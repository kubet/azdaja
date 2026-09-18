//! Source-bound, checkpointed native judgments. No automatic retries.
use crate::judge::{JudgeConfig, JudgeEngine};
use anyhow::{Result, anyhow, ensure};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::{
    collections::BTreeSet,
    fs::{self, File},
    io::{Read, Write},
    path::{Path, PathBuf},
    sync::atomic::{AtomicU64, Ordering},
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

const MAX_PLAN: u64 = 64 * 1024 * 1024;
static NEXT: AtomicU64 = AtomicU64::new(0);

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub struct BatchLimits {
    pub max_requests: usize,
    pub max_input_tokens: u64,
    pub max_seconds: u64,
}
#[derive(Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct Entry {
    id: String,
    state: Value,
    questions: Value,
}
struct Plan {
    entries: Vec<Entry>,
    hashes: Vec<String>,
    binding: Value,
    bytes: usize,
    questions: usize,
}
fn decode<T: serde::de::DeserializeOwned>(bytes: &[u8]) -> Result<T> {
    let value: crate::UniqueJsonValue =
        serde_json::from_slice(bytes).map_err(|_| anyhow!("batch: malformed or duplicate JSON"))?;
    serde_json::from_value(value.0).map_err(|_| anyhow!("batch: invalid artifact schema"))
}
fn parse(input: &Path, config: &JudgeConfig, limits: &BatchLimits) -> Result<Plan> {
    ensure!(
        (1..=10_000).contains(&limits.max_requests),
        "batch: invalid request limit"
    );
    ensure!(
        (1..=(1u64 << 53)).contains(&limits.max_input_tokens),
        "batch: invalid token limit"
    );
    ensure!(
        (1..=604_800).contains(&limits.max_seconds),
        "batch: invalid wall limit"
    );
    config.validate()?;
    let file = crate::open_regular_nofollow(input, false)
        .map_err(|_| anyhow!("batch: input must be a regular non-symlink file"))?;
    ensure!(
        file.metadata()?.len() <= MAX_PLAN,
        "batch: plan exceeds 64 MiB"
    );
    let mut bytes = Vec::new();
    (&file).take(MAX_PLAN + 1).read_to_end(&mut bytes)?;
    crate::bound_metadata(&file, input)?;
    ensure!(bytes.len() as u64 <= MAX_PLAN, "batch: plan exceeds 64 MiB");
    let text = std::str::from_utf8(&bytes).map_err(|_| anyhow!("batch: input is not UTF-8"))?;
    let mut ids = BTreeSet::new();
    let mut entries = Vec::new();
    let mut hashes = Vec::new();
    let mut questions = 0;
    for line in text.lines().filter(|line| !line.trim().is_empty()) {
        ensure!(
            entries.len() < limits.max_requests,
            "batch: request limit exceeded"
        );
        let entry: Entry = decode(line.as_bytes())?;
        ensure!(
            !entry.id.trim().is_empty()
                && entry.id.len() <= 256
                && !entry.id.chars().any(char::is_control)
                && crate::judge::redact_typesafe_keys(&entry.id) == entry.id
                && ids.insert(entry.id.clone()),
            "batch: duplicate or invalid id"
        );
        let request = crate::judge::prepare_request(config, &entry.state, &entry.questions)?;
        let count = entry
            .questions
            .as_object()
            .expect("validated questions")
            .len();
        ensure!(
            count <= config.max_questions_per_cell.min(255),
            "batch: question limit exceeded"
        );
        questions += count;
        hashes.push(crate::sha256_hex(&request));
        entries.push(entry);
    }
    ensure!(!entries.is_empty(), "batch: empty plan");
    let binding = json!({"schema":"azdaja.judge_batch.plan.v1",
        "input_sha256":crate::sha256_hex(&bytes), "config":config, "limits":limits,
        "requests":entries.iter().zip(&hashes).map(|(e,h)|json!({"id":e.id,"request_sha256":h})).collect::<Vec<_>>()});
    Ok(Plan {
        entries,
        hashes,
        binding,
        bytes: bytes.len(),
        questions,
    })
}
pub fn inspect(input: &Path, config: &JudgeConfig, limits: &BatchLimits) -> Result<Value> {
    let plan = parse(input, config, limits)?;
    Ok(
        json!({"status":"valid","records":plan.entries.len(),"questions":plan.questions,
        "plan_bytes":plan.bytes,"input_sha256":plan.binding["input_sha256"],
        "provider_requests":0,"credentials_checked":false,"execution_enabled":false,
        "typesafe_compiled":cfg!(feature="typesafe"),"limits":limits}),
    )
}
fn now_ms() -> Result<u64> {
    Ok(SystemTime::now()
        .duration_since(UNIX_EPOCH)?
        .as_millis()
        .try_into()?)
}

struct Store {
    path: PathBuf,
    directory: File,
    _lock: File,
}
impl Store {
    fn open(path: &Path, resume: bool) -> Result<Self> {
        ensure!(
            crate::credentials::storage_available(),
            "batch: private job storage unavailable on this platform"
        );
        // Resolve parent aliases once, but never follow the job directory itself.
        let parent = path
            .parent()
            .filter(|p| !p.as_os_str().is_empty())
            .unwrap_or(Path::new("."));
        let name = path
            .file_name()
            .ok_or_else(|| anyhow!("batch: invalid job path"))?;
        let path = parent.canonicalize()?.join(name);
        let directory = if resume {
            crate::open_private_directory(&path)?
        } else {
            crate::create_new_private_directory(&path)?
        };
        crate::validate_private_directory(&directory, &path)?;
        let lock_path = path.join(".lock");
        let lock = match fs::symlink_metadata(&lock_path) {
            Ok(_) => crate::open_private_file(&lock_path, true)?,
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
                crate::create_private_file(&lock_path)?
            }
            Err(e) => return Err(e.into()),
        };
        fs2::FileExt::try_lock_exclusive(&lock).map_err(|_| anyhow!("batch: job is busy"))?;
        crate::validate_private_directory(&directory, &path)?;
        Ok(Self {
            path,
            directory,
            _lock: lock,
        })
    }
    fn check(&self) -> Result<()> {
        crate::validate_private_directory(&self.directory, &self.path)
    }
    fn read(&self, name: &str, max: u64) -> Result<Option<Vec<u8>>> {
        self.check()?;
        let path = self.path.join(name);
        match fs::symlink_metadata(&path) {
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(None),
            Err(e) => return Err(e.into()),
            Ok(_) => {}
        }
        let file = crate::open_private_file(&path, false)?;
        ensure!(file.metadata()?.len() <= max, "batch: oversized artifact");
        let mut bytes = Vec::new();
        (&file).take(max + 1).read_to_end(&mut bytes)?;
        crate::validate_private_file(&file, &path)?;
        self.check()?;
        ensure!(bytes.len() as u64 <= max, "batch: oversized artifact");
        Ok(Some(bytes))
    }
    fn write_new<T: Serialize>(&self, name: &str, value: &T) -> Result<()> {
        self.check()?;
        let target = self.path.join(name);
        let staging = self.path.join(format!(
            ".pending-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        let mut file = crate::create_private_file(&staging)?;
        let result = (|| {
            serde_json::to_writer(&mut file, value)?;
            file.write_all(b"\n")?;
            file.sync_all()?;
            crate::validate_private_file(&file, &staging)?;
            self.check()?;
            crate::rename_noreplace(&staging, &target)?;
            self.directory.sync_all()?;
            self.check()
        })();
        if result.is_err() {
            crate::remove_bound_file(&staging, &file);
        }
        result
    }
    fn inventory(&self, size: usize) -> Result<()> {
        let mut allowed = BTreeSet::from(["manifest.json".to_string(), ".lock".to_string()]);
        for i in 0..size {
            allowed.insert(format!("{i:06}.intent.json"));
            allowed.insert(format!("{i:06}.result.json"));
        }
        for (n, entry) in fs::read_dir(&self.path)?.enumerate() {
            ensure!(n < size * 3 + 20, "batch: artifact count exceeded");
            let name = entry?
                .file_name()
                .into_string()
                .map_err(|_| anyhow!("batch: invalid artifact name"))?;
            // Interrupted atomic writes are never treated as observations.
            ensure!(
                allowed.contains(&name) || name.starts_with(".pending-"),
                "batch: unexpected artifact"
            );
        }
        self.check()
    }
}
#[derive(Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Manifest {
    schema: String,
    binding: Value,
    started_unix_ms: u64,
    deadline_unix_ms: u64,
}
#[derive(Serialize, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
struct Intent {
    schema: String,
    index: usize,
    id: String,
    request_sha256: String,
}
#[derive(Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Record {
    schema: String,
    intent: Intent,
    status: String,
    observation: Option<Value>,
    stats: Value,
    finished_unix_ms: u64,
}
fn expected_intent(plan: &Plan, index: usize) -> Intent {
    Intent {
        schema: "azdaja.judge_batch.intent.v1".into(),
        index,
        id: plan.entries[index].id.clone(),
        request_sha256: plan.hashes[index].clone(),
    }
}
fn number(value: &Value, name: &str) -> Result<u64> {
    value
        .get(name)
        .and_then(Value::as_u64)
        .ok_or_else(|| anyhow!("batch: invalid accounting"))
}
#[derive(Default, Serialize)]
struct Totals {
    attempts: u64,
    successful_requests: u64,
    failed_attempts: u64,
    questions: u64,
    known_input_tokens: u64,
    known_output_tokens: u64,
    unknown_input_usage_requests: u64,
    unknown_output_usage_requests: u64,
    total_wall_ns: u64,
}
impl Totals {
    fn add(&mut self, stats: &Value) -> Result<()> {
        macro_rules! add { ($($field:ident),*) => { $(self.$field = self.$field.checked_add(number(stats,stringify!($field))?).ok_or_else(||anyhow!("batch: accounting overflow"))?;)* }; }
        add!(
            attempts,
            successful_requests,
            failed_attempts,
            questions,
            known_input_tokens,
            known_output_tokens,
            unknown_input_usage_requests,
            unknown_output_usage_requests,
            total_wall_ns
        );
        Ok(())
    }
}
fn validate_record(
    record: &Record,
    plan: &Plan,
    index: usize,
    config: &JudgeConfig,
    manifest: &Manifest,
) -> Result<()> {
    ensure!(
        record.schema == "azdaja.judge_batch.result.v1"
            && record.intent == expected_intent(plan, index),
        "batch: result binding mismatch"
    );
    ensure!(
        record.finished_unix_ms >= manifest.started_unix_ms,
        "batch: invalid completion time"
    );
    let s = &record.stats;
    let attempts = number(s, "attempts")?;
    let success = number(s, "successful_requests")?;
    ensure!(
        attempts <= 1
            && success <= attempts
            && number(s, "provider_requests")? == attempts
            && number(s, "failed_attempts")? == attempts - success
            && number(s, "cache_hits")? == 0
            && number(s, "cached_requests")? == success
            && number(s, "questions")?
                == attempts * plan.entries[index].questions.as_object().unwrap().len() as u64
            && number(s, "unknown_input_usage_requests")? <= attempts
            && number(s, "unknown_output_usage_requests")? <= attempts,
        "batch: invalid per-request accounting"
    );
    ensure!(
        s["input_usage_complete"] == json!(number(s, "unknown_input_usage_requests")? == 0)
            && s["output_usage_complete"]
                == json!(number(s, "unknown_output_usage_requests")? == 0)
            && s["enabled"] == true
            && s["transport_available"] == true,
        "batch: invalid usage or transport state"
    );
    let mut checked = Totals::default();
    checked.add(s)?;
    if record.status == "completed" {
        ensure!(
            attempts == 1 && success == 1 && s["poisoned"] == false,
            "batch: incomplete success accounting"
        );
        let mut body = record
            .observation
            .clone()
            .ok_or_else(|| anyhow!("batch: missing observation"))?;
        let obj = body
            .as_object_mut()
            .ok_or_else(|| anyhow!("batch: invalid observation"))?;
        let meta = obj
            .remove("_azdaja")
            .ok_or_else(|| anyhow!("batch: missing native binding"))?;
        ensure!(
            meta["request_sha256"] == record.intent.request_sha256
                && meta["cache_hit"] == false
                && meta["provider_requests_this_call"] == 1,
            "batch: observation request mismatch"
        );
        crate::judge::validate_response(&body, &plan.entries[index].questions, config)?;
        for (usage, known, unknown) in [
            (
                "input_tokens",
                "known_input_tokens",
                "unknown_input_usage_requests",
            ),
            (
                "output_tokens",
                "known_output_tokens",
                "unknown_output_usage_requests",
            ),
        ] {
            let value = body
                .get("usage")
                .and_then(|u| u.get(usage))
                .filter(|v| !v.is_null());
            let tokens = value
                .map(|v| v.as_u64().ok_or_else(|| anyhow!("batch: invalid usage")))
                .transpose()?;
            ensure!(
                number(s, known)? == tokens.unwrap_or(0)
                    && number(s, unknown)? == u64::from(tokens.is_none()),
                "batch: usage differs from observation"
            );
        }
    } else {
        ensure!(
            record.status == "failed" && success == 0 && record.observation.is_none(),
            "batch: invalid failed result"
        );
    }
    Ok(())
}
fn summary(
    plan: &Plan,
    totals: &Totals,
    completed: usize,
    new_attempts: u64,
    reason: Option<&str>,
    ambiguous: bool,
) -> Value {
    json!({"schema":"azdaja.judge_batch.summary.v1",
        "status":if reason.is_none(){"completed"}else{"stopped"},"stop_reason":reason,
        "input_sha256":plan.binding["input_sha256"],
        "records":{"total":plan.entries.len(),"completed":completed,"pending":plan.entries.len()-completed},
        "calls":totals.attempts,"new_requests":new_attempts,"usage":totals,
        "unresolved_inflight_requests":u64::from(ambiguous),
        "input_usage_complete":!ambiguous && totals.unknown_input_usage_requests==0,
        "output_usage_complete":!ambiguous && totals.unknown_output_usage_requests==0,
        "billing":"not_inferred"})
}

pub fn run(
    input: &Path,
    output: &Path,
    config: &JudgeConfig,
    limits: &BatchLimits,
    resume: bool,
) -> Result<Value> {
    run_with(
        input,
        output,
        config,
        limits,
        resume,
        |plan| {
            ensure!(config.enabled, "batch: judge disabled");
            ensure!(
                cfg!(feature = "typesafe"),
                "batch: typesafe feature is not enabled in this build"
            );
            let key = crate::credentials::resolve(&config.key_env)
                .map_err(|_| anyhow!("batch: credential unavailable"))?;
            ensure!(
                crate::judge::safe_token(&key),
                "batch: invalid credential syntax"
            );
            ensure!(
                !crate::judge::contains_secret(&plan.binding, &key),
                "batch: credential leakage refused"
            );
            for e in &plan.entries {
                ensure!(
                    !e.id.contains(&key)
                        && !crate::judge::contains_secret(&e.state, &key)
                        && !crate::judge::contains_secret(&e.questions, &key),
                    "batch: credential leakage refused"
                );
            }
            Ok(())
        },
        |entry, cfg, deadline| {
            let mut engine = JudgeEngine::new(cfg);
            engine.set_deadline(deadline);
            let result = engine.evaluate(entry.state.clone(), entry.questions.clone());
            (result, engine.stats())
        },
    )
}
// The injected closures are private and never selectable by a CLI, endpoint or environment.
fn run_with<P, E>(
    input: &Path,
    output: &Path,
    config: &JudgeConfig,
    limits: &BatchLimits,
    resume: bool,
    mut preflight: P,
    mut evaluate: E,
) -> Result<Value>
where
    P: FnMut(&Plan) -> Result<()>,
    E: FnMut(&Entry, &JudgeConfig, Instant) -> (Result<Value>, Value),
{
    let plan = parse(input, config, limits)?;
    if !resume {
        preflight(&plan)?;
    }
    let store = Store::open(output, resume)?;
    store.inventory(plan.entries.len())?;
    let manifest = if resume {
        let raw = store
            .read("manifest.json", MAX_PLAN)?
            .ok_or_else(|| anyhow!("batch: missing manifest"))?;
        let m: Manifest = decode(&raw)?;
        ensure!(
            m.schema == "azdaja.judge_batch.job.v1" && m.binding == plan.binding,
            "batch: plan, configuration or limits changed"
        );
        ensure!(
            m.started_unix_ms.checked_add(limits.max_seconds * 1000) == Some(m.deadline_unix_ms),
            "batch: invalid original deadline"
        );
        m
    } else {
        let start = now_ms()?;
        let m = Manifest {
            schema: "azdaja.judge_batch.job.v1".into(),
            binding: plan.binding.clone(),
            started_unix_ms: start,
            deadline_unix_ms: start
                .checked_add(limits.max_seconds * 1000)
                .ok_or_else(|| anyhow!("batch: invalid deadline"))?,
        };
        store.write_new("manifest.json", &m)?;
        m
    };
    let mut totals = Totals::default();
    let mut completed = 0;
    let mut reason = None;
    let mut ambiguous = false;
    let mut next = plan.entries.len();
    let mut gap = false;
    for index in 0..plan.entries.len() {
        let intent = store.read(&format!("{index:06}.intent.json"), 16384)?;
        let result = store.read(
            &format!("{index:06}.result.json"),
            config.max_response_bytes as u64 + 65536,
        )?;
        if let Some(bytes) = intent.as_ref() {
            ensure!(!gap, "batch: non-contiguous request journal");
            let actual: Intent = decode(bytes)?;
            ensure!(
                actual == expected_intent(&plan, index),
                "batch: intent binding mismatch"
            );
        }
        if let Some(bytes) = result {
            ensure!(intent.is_some() && !gap, "batch: orphan result");
            let record: Record = decode(&bytes)?;
            validate_record(&record, &plan, index, config, &manifest)?;
            totals.add(&record.stats)?;
            if record.status == "completed" {
                completed += 1;
            } else {
                reason = Some("previous_request_failed");
                gap = true;
            }
            if record.finished_unix_ms > manifest.deadline_unix_ms {
                reason = Some("original_deadline_exceeded");
            }
        } else if intent.is_some() {
            reason = Some("ambiguous_inflight_request");
            ambiguous = true;
            gap = true;
        } else {
            if next == plan.entries.len() {
                next = index;
            }
            gap = true;
        }
    }
    if totals.known_input_tokens > limits.max_input_tokens {
        reason = Some("input_token_limit_exceeded");
    }
    if totals.unknown_input_usage_requests > 0 {
        reason = Some("unknown_input_usage");
    }
    if reason.is_some() {
        return Ok(summary(&plan, &totals, completed, 0, reason, ambiguous));
    }
    if completed == plan.entries.len() {
        return Ok(summary(&plan, &totals, completed, 0, None, false));
    }
    let now = now_ms()?;
    ensure!(
        now >= manifest.started_unix_ms,
        "batch: clock moved backwards"
    );
    if now >= manifest.deadline_unix_ms {
        return Ok(summary(
            &plan,
            &totals,
            completed,
            0,
            Some("original_deadline_exceeded"),
            false,
        ));
    }
    if resume {
        preflight(&plan)?;
    }
    let invocation_deadline =
        Instant::now() + Duration::from_millis(manifest.deadline_unix_ms.saturating_sub(now_ms()?));
    let mut new_attempts = 0;
    for index in next..plan.entries.len() {
        if crate::provider_interrupted() {
            reason = Some("interrupted");
            break;
        }
        let remaining = manifest.deadline_unix_ms.saturating_sub(now_ms()?).min(
            invocation_deadline
                .saturating_duration_since(Instant::now())
                .as_millis() as u64,
        );
        if remaining == 0 {
            reason = Some("original_deadline_exceeded");
            break;
        }
        if totals.known_input_tokens >= limits.max_input_tokens {
            reason = Some("input_token_limit_exhausted");
            break;
        }
        let entry = &plan.entries[index];
        let mut cfg = config.clone();
        cfg.max_requests_per_cell = 1;
        cfg.max_questions_per_cell = entry.questions.as_object().unwrap().len();
        cfg.max_input_tokens_per_cell = config
            .max_input_tokens_per_cell
            .min(limits.max_input_tokens - totals.known_input_tokens);
        let intent = expected_intent(&plan, index);
        let deadline = Instant::now() + Duration::from_millis(remaining);
        store.write_new(&format!("{index:06}.intent.json"), &intent)?;
        let (result, stats) = evaluate(entry, &cfg, deadline);
        let ok = result.is_ok();
        let record = Record {
            schema: "azdaja.judge_batch.result.v1".into(),
            intent,
            status: if ok { "completed" } else { "failed" }.into(),
            observation: result.ok(),
            stats,
            finished_unix_ms: now_ms()?,
        };
        validate_record(&record, &plan, index, config, &manifest)?;
        store.write_new(&format!("{index:06}.result.json"), &record)?;
        new_attempts += number(&record.stats, "attempts")?;
        totals.add(&record.stats)?;
        if ok {
            completed += 1;
        }
        eprintln!(
            "{}",
            json!({"event":"batch_progress","completed":completed,"total":plan.entries.len(),"attempts":totals.attempts})
        );
        if !ok {
            reason = Some("request_failed");
            break;
        }
        if totals.unknown_input_usage_requests > 0 {
            reason = Some("unknown_input_usage");
            break;
        }
        if record.finished_unix_ms > manifest.deadline_unix_ms {
            reason = Some("original_deadline_exceeded");
            break;
        }
    }
    Ok(summary(
        &plan,
        &totals,
        completed,
        new_attempts,
        reason,
        false,
    ))
}

#[cfg(all(
    test,
    any(target_vendor = "apple", target_os = "linux", target_os = "android")
))]
mod tests {
    use super::*;
    use std::{cell::Cell, rc::Rc};
    struct Fixture {
        root: PathBuf,
        input: PathBuf,
        job: PathBuf,
    }
    impl Fixture {
        fn new() -> Self {
            let base = std::env::var_os("JCODE_SCRATCH_DIR")
                .map(PathBuf::from)
                .unwrap_or_else(std::env::temp_dir);
            let root = base.join(format!(
                "az-batch-unit-{}-{}-{}",
                std::process::id(),
                now_ms().unwrap(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            fs::create_dir(&root).unwrap();
            let input = root.join("plan.jsonl");
            let rows = (0..3).map(|i|json!({"id":format!("record-{i}"),"state":"public source","questions":{"q":{"type":"noul","instructions":"Present?"}}}).to_string()).collect::<Vec<_>>().join("\n");
            fs::write(&input, rows).unwrap();
            Self {
                job: root.join("job"),
                root,
                input,
            }
        }
    }
    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.root);
        }
    }
    fn config() -> JudgeConfig {
        JudgeConfig {
            enabled: true,
            ..JudgeConfig::default()
        }
    }
    fn limits() -> BatchLimits {
        BatchLimits {
            max_requests: 3,
            max_input_tokens: 100,
            max_seconds: 60,
        }
    }
    fn evaluator(
        calls: Rc<Cell<u64>>,
        fail_at: Option<u64>,
        unknown: bool,
    ) -> impl FnMut(&Entry, &JudgeConfig, Instant) -> (Result<Value>, Value) {
        move |entry, cfg, deadline| {
            let calls = calls.clone();
            let questions = entry.questions.clone();
            let mut engine = JudgeEngine::with_dependencies(
                cfg,
                Box::new(|_| Ok("synthetic-token".into())),
                Box::new(move |_, _, _, _| {
                    let n = calls.get();
                    calls.set(n + 1);
                    if fail_at == Some(n) {
                        anyhow::bail!("synthetic transport failure");
                    }
                    let answers = questions
                        .as_object()
                        .unwrap()
                        .keys()
                        .map(|k| (k.clone(), json!({"type":"noul","noul":0.8})))
                        .collect::<serde_json::Map<_, _>>();
                    Ok(serde_json::to_vec(
                        &json!({"model":"jev-test","answers":answers,"usage":if unknown{Value::Null}else{json!({"input_tokens":5,"output_tokens":2})}}),
                    )?)
                }),
            );
            engine.set_deadline(deadline);
            let result = engine.evaluate(entry.state.clone(), entry.questions.clone());
            (result, engine.stats())
        }
    }
    #[test]
    fn native_success_resume_does_not_resolve_credentials_or_call_again() {
        let f = Fixture::new();
        let calls = Rc::new(Cell::new(0));
        let r = run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            false,
            |_| Ok(()),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        assert_eq!(r["status"], "completed");
        assert_eq!(calls.get(), 3);
        assert_eq!(r["usage"]["known_output_tokens"], 6);
        let r = run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            true,
            |_| panic!("credential read"),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        assert_eq!(r["status"], "completed");
        assert_eq!(r["new_requests"], 0);
        assert_eq!(r["calls"], 3);
        assert_eq!(calls.get(), 3);
    }
    #[test]
    fn failed_request_retains_usage_and_is_never_counted_completed_on_resume() {
        let f = Fixture::new();
        let calls = Rc::new(Cell::new(0));
        let r = run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            false,
            |_| Ok(()),
            evaluator(calls.clone(), Some(1), false),
        )
        .unwrap();
        assert_eq!(r["status"], "stopped");
        assert_eq!(r["records"]["completed"], 1);
        assert_eq!(r["usage"]["unknown_input_usage_requests"], 1);
        let r = run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            true,
            |_| panic!("preflight"),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        assert_eq!(r["status"], "stopped");
        assert_eq!(calls.get(), 2);
        assert_eq!(r["new_requests"], 0);
    }
    #[test]
    fn unknown_usage_stops_before_next_request() {
        let f = Fixture::new();
        let calls = Rc::new(Cell::new(0));
        let r = run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            false,
            |_| Ok(()),
            evaluator(calls.clone(), None, true),
        )
        .unwrap();
        assert_eq!(r["stop_reason"], "unknown_input_usage");
        assert_eq!(calls.get(), 1);
        assert_eq!(r["input_usage_complete"], false);
    }
    #[test]
    fn crossing_token_budget_preserves_paid_failure_and_usage() {
        let f = Fixture::new();
        let calls = Rc::new(Cell::new(0));
        let mut cap = limits();
        cap.max_input_tokens = 7;
        let r = run_with(
            &f.input,
            &f.job,
            &config(),
            &cap,
            false,
            |_| Ok(()),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        assert_eq!(r["status"], "stopped");
        assert_eq!(r["records"]["completed"], 1);
        assert_eq!(r["usage"]["known_input_tokens"], 10);
        assert_eq!(calls.get(), 2);
    }
    #[test]
    fn interrupted_intent_prevents_automatic_paid_reentry() {
        let f = Fixture::new();
        let calls = Rc::new(Cell::new(0));
        let mut eval = evaluator(calls.clone(), None, false);
        let aborted = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            run_with(
                &f.input,
                &f.job,
                &config(),
                &limits(),
                false,
                |_| Ok(()),
                |e, c, d| {
                    if calls.get() == 1 {
                        panic!("simulated kill after durable intent")
                    };
                    eval(e, c, d)
                },
            )
        }));
        assert!(aborted.is_err());
        let r = run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            true,
            |_| panic!("preflight"),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        assert_eq!(r["stop_reason"], "ambiguous_inflight_request");
        assert_eq!(r["unresolved_inflight_requests"], 1);
        assert_eq!(calls.get(), 1);
    }
    #[test]
    fn changed_source_configuration_and_limits_are_refused() {
        let f = Fixture::new();
        let calls = Rc::new(Cell::new(0));
        run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            false,
            |_| Ok(()),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        let mut cfg = config();
        cfg.model = "different".into();
        assert!(
            run_with(
                &f.input,
                &f.job,
                &cfg,
                &limits(),
                true,
                |_| panic!(),
                evaluator(calls.clone(), None, false)
            )
            .is_err()
        );
        let mut cap = limits();
        cap.max_input_tokens += 1;
        assert!(
            run_with(
                &f.input,
                &f.job,
                &config(),
                &cap,
                true,
                |_| panic!(),
                evaluator(calls.clone(), None, false)
            )
            .is_err()
        );
        let text = fs::read_to_string(&f.input)
            .unwrap()
            .replace("public source", "changed source");
        fs::write(&f.input, text).unwrap();
        assert!(
            run_with(
                &f.input,
                &f.job,
                &config(),
                &limits(),
                true,
                |_| panic!(),
                evaluator(calls.clone(), None, false)
            )
            .is_err()
        );
        assert_eq!(calls.get(), 3);
    }
    #[test]
    fn expired_deadline_can_only_replay_already_completed_work() {
        let f = Fixture::new();
        let calls = Rc::new(Cell::new(0));
        run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            false,
            |_| Ok(()),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        let path = f.job.join("manifest.json");
        let mut m: Manifest = decode(&fs::read(&path).unwrap()).unwrap();
        let delta = 120_000;
        m.started_unix_ms -= delta;
        m.deadline_unix_ms -= delta;
        fs::write(&path, serde_json::to_vec(&m).unwrap()).unwrap();
        for i in 0..3 {
            let p = f.job.join(format!("{i:06}.result.json"));
            let mut r: Record = decode(&fs::read(&p).unwrap()).unwrap();
            r.finished_unix_ms -= delta;
            fs::write(p, serde_json::to_vec(&r).unwrap()).unwrap();
        }
        let r = run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            true,
            |_| panic!(),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        assert_eq!(r["status"], "completed");
        fs::remove_file(f.job.join("000002.result.json")).unwrap();
        fs::remove_file(f.job.join("000002.intent.json")).unwrap();
        let r = run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            true,
            |_| panic!(),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        assert_eq!(r["stop_reason"], "original_deadline_exceeded");
        assert_eq!(calls.get(), 3);
    }
    #[test]
    fn journal_lock_and_corrupt_result_refuse_before_transport() {
        let f = Fixture::new();
        let calls = Rc::new(Cell::new(0));
        run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            false,
            |_| Ok(()),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        {
            let _held = Store::open(&f.job, true).unwrap();
            assert!(
                run_with(
                    &f.input,
                    &f.job,
                    &config(),
                    &limits(),
                    true,
                    |_| panic!(),
                    evaluator(calls.clone(), None, false)
                )
                .is_err()
            );
        }
        let p = f.job.join("000001.result.json");
        let mut r: Value = decode(&fs::read(&p).unwrap()).unwrap();
        r["stats"]["known_input_tokens"] = json!(0);
        fs::write(p, serde_json::to_vec(&r).unwrap()).unwrap();
        assert!(
            run_with(
                &f.input,
                &f.job,
                &config(),
                &limits(),
                true,
                |_| panic!(),
                evaluator(calls.clone(), None, false)
            )
            .is_err()
        );
        assert_eq!(calls.get(), 3);
    }
    #[cfg(unix)]
    #[test]
    fn private_paths_reject_symlinks_hardlinks_and_unsafe_modes() {
        use std::os::unix::fs::{PermissionsExt, symlink};
        let f = Fixture::new();
        let calls = Rc::new(Cell::new(0));
        run_with(
            &f.input,
            &f.job,
            &config(),
            &limits(),
            false,
            |_| Ok(()),
            evaluator(calls.clone(), None, false),
        )
        .unwrap();
        assert_eq!(
            fs::metadata(&f.job).unwrap().permissions().mode() & 0o777,
            0o700
        );
        let p = f.job.join("000000.result.json");
        assert_eq!(
            fs::metadata(&p).unwrap().permissions().mode() & 0o777,
            0o600
        );
        fs::hard_link(&p, f.root.join("hard")).unwrap();
        assert!(
            Store::open(&f.job, true)
                .unwrap()
                .read("000000.result.json", MAX_PLAN)
                .is_err()
        );
        fs::remove_file(f.root.join("hard")).unwrap();
        fs::set_permissions(&p, fs::Permissions::from_mode(0o644)).unwrap();
        assert!(
            Store::open(&f.job, true)
                .unwrap()
                .read("000000.result.json", MAX_PLAN)
                .is_err()
        );
        let link = f.root.join("link");
        symlink(&f.job, &link).unwrap();
        assert!(Store::open(&link, true).is_err());
        assert_eq!(calls.get(), 3);
    }
}
