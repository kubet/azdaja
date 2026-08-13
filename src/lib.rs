use anyhow::{Context, Result, anyhow, bail};
use fs2::FileExt;
use monty::{Dump, MontyRepl, ReplProgress, Session, SessionRef, dump};
use monty_types::{
    CompileOptions, MontyException, MontyObject, NameLookupResult, PrintWriter,
    PrintWriterCallback, ResourceLimits, ResourceTracker,
};
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::{
    borrow::Cow,
    collections::VecDeque,
    env,
    fs::{self, File, OpenOptions},
    io::{BufRead, BufReader, Read, Write},
    path::{Path, PathBuf},
    process::{Command, Stdio},
    sync::{
        Arc, OnceLock,
        atomic::{AtomicU32, AtomicU64, Ordering},
    },
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

#[cfg(unix)]
use std::os::unix::{fs::OpenOptionsExt, net::UnixStream};

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const MONTY_VERSION: &str = "0.0.21";
pub const SKILL: &str = include_str!("../assets/SKILL.md");
pub const DEFAULT_CONFIG: &str = include_str!("../assets/config.toml");
pub const SEMANTIC_MANIFEST_PROMPT_ENVELOPE_CHARS: usize = 45_000;
const PRELUDE: &str = "import os, re, json, math, collections, datetime";

#[derive(Clone, Deserialize, Serialize)]
#[serde(default, deny_unknown_fields)]
pub struct Config {
    pub sub_llm_cmd: String,
    pub default_model: String,
    pub output_cap: usize,
    pub max_depth: u32,
    pub sub_timeout: u64,
    pub max_sessions: usize,
    pub cell_timeout: u64,
    pub idle_timeout: u64,
    pub clean_patterns: Vec<String>,
    pub jcode_provider: String,
    pub jcode_reasoning: String,
    pub max_calls_per_cell: usize,
}
impl Default for Config {
    fn default() -> Self {
        Self {
            sub_llm_cmd: "jcode-api".into(),
            default_model: "gpt-5.6-luna".into(),
            output_cap: 8192,
            max_depth: 1,
            sub_timeout: 300,
            max_sessions: 4,
            cell_timeout: 30,
            idle_timeout: 1800,
            clean_patterns: Vec::new(),
            jcode_provider: "openai".into(),
            jcode_reasoning: "medium".into(),
            max_calls_per_cell: 64,
        }
    }
}
impl Config {
    pub fn load() -> Result<Self> {
        let candidates = [
            env::var_os("AZDAJA_CONFIG").map(PathBuf::from),
            env::current_exe()
                .ok()
                .and_then(|p| p.parent().map(|p| p.join("config.toml"))),
            config_home().map(|p| p.join("azdaja/config.toml")),
        ];
        for p in candidates.into_iter().flatten() {
            if p.is_file() {
                return toml::from_str::<Self>(&fs::read_to_string(&p)?)
                    .with_context(|| format!("invalid config {}", p.display()))?
                    .validate();
            }
        }
        Self::default().validate()
    }
    pub fn validate(self) -> Result<Self> {
        if self.sub_llm_cmd.trim().is_empty() {
            bail!("sub_llm_cmd cannot be empty")
        }
        if self.output_cap < 256 {
            bail!("output_cap must be at least 256")
        }
        if self.sub_timeout == 0 || self.cell_timeout == 0 || self.idle_timeout == 0 {
            bail!("timeouts must be positive")
        }
        if self.max_sessions == 0 || self.max_calls_per_cell == 0 {
            bail!("session and call limits must be positive")
        }
        for p in &self.clean_patterns {
            Regex::new(p).with_context(|| format!("invalid clean pattern: {p}"))?;
        }
        Ok(self)
    }
}

#[derive(Serialize, Deserialize)]
struct Meta {
    version: String,
    monty: String,
    created: u64,
    sub_model: Option<String>,
}
fn now() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}
fn now_ms() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
}
fn home() -> Option<PathBuf> {
    env::var_os("HOME")
        .or_else(|| env::var_os("USERPROFILE"))
        .map(PathBuf::from)
}
fn config_home() -> Option<PathBuf> {
    env::var_os("XDG_CONFIG_HOME")
        .map(PathBuf::from)
        .or_else(|| home().map(|p| p.join(".config")))
}
pub fn state_home() -> Result<PathBuf> {
    let p = env::var_os("AZDAJA_HOME")
        .map(PathBuf::from)
        .or_else(|| env::var_os("XDG_STATE_HOME").map(|p| PathBuf::from(p).join("azdaja")))
        .or_else(|| home().map(|p| p.join(".local/state/azdaja")))
        .ok_or_else(|| anyhow!("no home directory; set AZDAJA_HOME"))?;
    secure_dir(&p)?;
    Ok(p)
}
#[cfg(unix)]
fn chmod(path: &Path, mode: u32) -> Result<()> {
    use std::os::unix::fs::PermissionsExt;
    fs::set_permissions(path, fs::Permissions::from_mode(mode))?;
    Ok(())
}
#[cfg(not(unix))]
fn chmod(_: &Path, _: u32) -> Result<()> {
    Ok(())
}
fn secure_dir(p: &Path) -> Result<()> {
    fs::create_dir_all(p)?;
    chmod(p, 0o700)
}
fn atomic_write(path: &Path, data: &[u8]) -> Result<()> {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    let tmp = path.with_extension(format!("tmp-{}-{nonce}", std::process::id()));
    {
        let mut f = OpenOptions::new().write(true).create_new(true).open(&tmp)?;
        chmod(&tmp, 0o600)?;
        f.write_all(data)?;
    }
    #[cfg(windows)]
    if path.exists() {
        fs::remove_file(path)?;
    }
    fs::rename(tmp, path)?;
    Ok(())
}
fn valid_sid(s: &str) -> bool {
    s.len() == 16
        && s.bytes()
            .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
}
fn session_dir(sid: &str) -> Result<PathBuf> {
    if !valid_sid(sid) {
        bail!("invalid session id");
    }
    let p = state_home()?.join(sid);
    let m = fs::symlink_metadata(&p).with_context(|| format!("session not found: {sid}"))?;
    if !m.file_type().is_dir() || m.file_type().is_symlink() {
        bail!("unsafe session path");
    }
    Ok(p)
}
fn lock_path(path: &Path) -> Result<File> {
    if let Some(parent) = path.parent() {
        secure_dir(parent)?
    }
    let f = OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .open(path)?;
    chmod(path, 0o600)?;
    FileExt::lock_exclusive(&f)?;
    Ok(f)
}
fn lock(dir: &Path) -> Result<File> {
    let sid = dir
        .file_name()
        .ok_or_else(|| anyhow!("invalid session path"))?;
    lock_path(&state_home()?.join("locks").join(sid).with_extension("lock"))
}
fn global_lock() -> Result<File> {
    lock_path(&state_home()?.join("global.lock"))
}
fn load_repl(dir: &Path) -> Result<MontyRepl> {
    let p = dir.join("state.monty");
    if fs::symlink_metadata(&p)?.file_type().is_symlink() {
        bail!("unsafe snapshot path");
    }
    let file = File::open(p)?;
    // Writers replace the snapshot inode under the session lock, so this mapping is never mutated.
    let bytes = unsafe { memmap2::MmapOptions::new().map(&file)? };
    let restored = Dump::load(&bytes)?;
    drop(bytes);
    match restored.state {
        Session::Idle(r) => Ok(*r),
        _ => bail!("session snapshot is suspended"),
    }
}
fn save_repl(dir: &Path, repl: &MontyRepl) -> Result<()> {
    atomic_write(
        &dir.join("state.monty"),
        &dump("azdaja", None, SessionRef::Idle(repl))?,
    )
}
fn read_meta(dir: &Path) -> Result<Meta> {
    Ok(serde_json::from_slice(&fs::read(dir.join("meta.json"))?)?)
}

pub fn reap(cfg: &Config) -> Result<()> {
    let base = state_home()?;
    secure_dir(&base.join("locks"))?;
    let prompt_dir = base.join("prompts");
    secure_dir(&prompt_dir)?;
    let prompt_age = cfg.idle_timeout.max(cfg.sub_timeout.saturating_mul(2));
    if let Some(cutoff) = SystemTime::now().checked_sub(Duration::from_secs(prompt_age)) {
        for e in fs::read_dir(&prompt_dir)? {
            let e = e?;
            if e.file_type()?.is_file() && e.metadata()?.modified().is_ok_and(|t| t < cutoff) {
                let _ = fs::remove_file(e.path());
            }
        }
    }
    let cutoff = SystemTime::now().checked_sub(Duration::from_secs(cfg.idle_timeout));
    for e in fs::read_dir(&base)? {
        let e = e?;
        let name = e.file_name().to_string_lossy().into_owned();
        if !valid_sid(&name) || e.file_type()?.is_symlink() {
            continue;
        }
        if !cutoff.is_some_and(|c| e.metadata().and_then(|m| m.modified()).is_ok_and(|t| t < c)) {
            continue;
        }
        let lockfile = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(false)
            .open(base.join("locks").join(&name).with_extension("lock"));
        let Ok(lockfile) = lockfile else { continue };
        if FileExt::try_lock_exclusive(&lockfile).is_err() {
            continue;
        }
        if cutoff.is_some_and(|c| e.metadata().and_then(|m| m.modified()).is_ok_and(|t| t < c)) {
            let _ = fs::remove_dir_all(e.path());
        }
    }
    Ok(())
}
pub fn list(cfg: &Config) -> Result<Vec<String>> {
    reap(cfg)?;
    let mut v = Vec::new();
    for e in fs::read_dir(state_home()?)? {
        let e = e?;
        let n = e.file_name().to_string_lossy().into_owned();
        if valid_sid(&n) && e.file_type()?.is_dir() {
            v.push(n);
        }
    }
    v.sort();
    Ok(v)
}

pub fn start(cfg: &Config, sub_model: Option<String>) -> Result<String> {
    let _global = global_lock()?;
    reap(cfg)?;
    if list(cfg)?.len() >= cfg.max_sessions {
        bail!("session limit reached ({})", cfg.max_sessions)
    }
    let base = state_home()?;
    for salt in 0..100u64 {
        let raw = format!("{:?}:{}:{salt}", SystemTime::now(), std::process::id());
        let id = format!("{:016x}", fnv1a(raw.as_bytes()));
        let dir = base.join(&id);
        if dir.exists() {
            continue;
        }
        let stage = base.join(format!(".start-{}-{id}", std::process::id()));
        if stage.exists() {
            let _ = fs::remove_dir_all(&stage);
        }
        fs::create_dir(&stage)?;
        chmod(&stage, 0o700)?;
        let setup = (|| -> Result<()> {
            let tracker = ResourceTracker::new(
                ResourceLimits::default().max_duration(Duration::from_secs(cfg.cell_timeout)),
            );
            let mut repl = MontyRepl::new("azdaja", tracker, CompileOptions::default());
            repl.feed_run(PRELUDE, vec![], PrintWriter::Disabled)
                .context("Monty capability canary failed")?;
            save_repl(&stage, &repl)?;
            let meta = Meta {
                version: VERSION.into(),
                monty: MONTY_VERSION.into(),
                created: now(),
                sub_model: sub_model.clone(),
            };
            atomic_write(&stage.join("meta.json"), &serde_json::to_vec(&meta)?)?;
            Ok(())
        })();
        if let Err(e) = setup {
            let _ = fs::remove_dir_all(&stage);
            return Err(e);
        }
        match fs::rename(&stage, &dir) {
            Ok(()) => return Ok(id),
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => {
                let _ = fs::remove_dir_all(&stage);
            }
            Err(e) => {
                let _ = fs::remove_dir_all(&stage);
                return Err(e.into());
            }
        }
    }
    bail!("could not allocate session")
}

fn fnv1a(bytes: &[u8]) -> u64 {
    let mut h = 0xcbf29ce484222325u64;
    for b in bytes {
        h ^= u64::from(*b);
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

pub fn load(sid: &str, path: &Path, var: &str, cfg: &Config) -> Result<String> {
    let ident = Regex::new(r"^[A-Za-z_][A-Za-z0-9_]*$").unwrap();
    if !ident.is_match(var) {
        bail!("invalid variable name");
    }
    let dir = session_dir(sid)?;
    let _guard = lock(&dir)?;
    let text = fs::read_to_string(path)
        .with_context(|| format!("input is not UTF-8: {}", path.display()))?;
    let chars = text.chars().count();
    let lines = text.lines().count();
    let mut repl = load_repl(&dir)?;
    repl.tracker_mut()
        .set_max_duration(Duration::from_secs(cfg.cell_timeout));
    let code = format!("{var} = __azdaja_loaded");
    repl.feed_run(
        &code,
        vec![("__azdaja_loaded".into(), MontyObject::String(text))],
        PrintWriter::Disabled,
    )?;
    save_repl(&dir, &repl)?;
    Ok(format!(
        "loaded '{var}' : str, {chars} chars, {lines} lines"
    ))
}

#[derive(Clone)]
enum Final {
    Value(MontyObject),
    Var(String),
}
pub struct ExecResult {
    pub output: String,
    pub success: bool,
    pub finalized: bool,
}
fn as_string(o: &MontyObject, name: &str) -> Result<String> {
    if let MontyObject::String(s) = o {
        Ok(s.clone())
    } else {
        bail!("{name} must be a string")
    }
}
fn kw<'a>(kwargs: &'a [(MontyObject, MontyObject)], name: &str) -> Option<&'a MontyObject> {
    kwargs
        .iter()
        .find_map(|(k, v)| matches!(k,MontyObject::String(s) if s==name).then_some(v))
}
fn parse_call(
    args: &[MontyObject],
    kwargs: &[(MontyObject, MontyObject)],
    batch: bool,
) -> Result<(Vec<String>, Option<String>, usize)> {
    let first = args.first().ok_or_else(|| anyhow!("missing prompt"))?;
    let prompts = if batch {
        if let MontyObject::List(v) = first {
            v.iter()
                .map(|o| as_string(o, "prompt"))
                .collect::<Result<_>>()?
        } else {
            bail!("prompts must be a list")
        }
    } else {
        vec![as_string(first, "prompt")?]
    };
    let model = match kw(kwargs, "model").or(args.get(1)) {
        None | Some(MontyObject::None) => None,
        Some(MontyObject::String(s)) => Some(s.clone()),
        Some(_) => bail!("model must be a string or None"),
    };
    let ctx = if batch {
        String::new()
    } else {
        kw(kwargs, "ctx")
            .or(args.get(2))
            .map(|o| as_string(o, "ctx"))
            .transpose()?
            .unwrap_or_default()
    };
    let prompts = prompts
        .into_iter()
        .map(|p| {
            if ctx.is_empty() {
                p
            } else {
                format!("{p}\n\n{ctx}")
            }
        })
        .collect();
    let workers = match kw(kwargs, "workers").or(args.get(2)) {
        None => 2,
        Some(MontyObject::Int(n)) => {
            let n = usize::try_from(*n).map_err(|_| anyhow!("workers must be between 1 and 32"))?;
            if !(1..=32).contains(&n) {
                bail!("workers must be between 1 and 32")
            }
            n
        }
        Some(_) => bail!("workers must be an integer"),
    };
    Ok((prompts, model, workers))
}
fn external(
    name: &str,
    args: &[MontyObject],
    kwargs: &[(MontyObject, MontyObject)],
    cfg: &Config,
    default_model: &str,
    final_out: &mut Option<Final>,
    call_count: &mut usize,
) -> Result<MontyObject> {
    match name {
        "FINAL" => {
            let v = args
                .first()
                .ok_or_else(|| anyhow!("FINAL requires an answer"))?
                .clone();
            *final_out = Some(Final::Value(v));
            Ok(MontyObject::None)
        }
        "FINAL_VAR" => {
            let name = as_string(
                args.first()
                    .ok_or_else(|| anyhow!("FINAL_VAR requires a name"))?,
                "variable name",
            )?;
            if !Regex::new(r"^[A-Za-z_][A-Za-z0-9_]*$")
                .unwrap()
                .is_match(&name)
            {
                bail!("FINAL_VAR requires an identifier")
            }
            *final_out = Some(Final::Var(name));
            Ok(MontyObject::None)
        }
        "llm" | "llm_batch" | "llm_batch_fresh" => {
            let batch = name != "llm";
            let use_shared = name != "llm_batch_fresh";
            let (prompts, model, workers) = parse_call(args, kwargs, batch)?;
            let model = model
                .as_deref()
                .filter(|s| !s.is_empty())
                .unwrap_or(default_model);
            *call_count = call_count.saturating_add(prompts.len());
            if *call_count > cfg.max_calls_per_cell {
                bail!(
                    "llm call budget exceeded: {} > {}",
                    *call_count,
                    cfg.max_calls_per_cell
                )
            }
            let values = call_many_items(&prompts, model, workers, cfg, batch, use_shared)?;
            if batch {
                Ok(MontyObject::List(
                    values
                        .into_iter()
                        .map(|result| MontyObject::String(batch_item_value(result)))
                        .collect(),
                ))
            } else {
                match values.into_iter().next() {
                    Some(Ok(value)) => Ok(MontyObject::String(value)),
                    Some(Err(error)) => bail!("{error}"),
                    None => Ok(MontyObject::String(String::new())),
                }
            }
        }
        _ => bail!("unknown external function: {name}"),
    }
}
struct BoundedOutput {
    limit: usize,
    head: String,
    head_chars: usize,
    tail: VecDeque<char>,
    total: usize,
}
impl BoundedOutput {
    fn new(limit: usize) -> Self {
        Self {
            limit,
            head: String::new(),
            head_chars: 0,
            tail: VecDeque::new(),
            total: 0,
        }
    }
    fn push_str(&mut self, s: &str) {
        for c in s.chars() {
            self.push(c)
        }
    }
    fn push(&mut self, c: char) {
        self.total += 1;
        let h = self.limit / 2;
        if self.head_chars < h {
            self.head.push(c);
            self.head_chars += 1
        } else {
            self.tail.push_back(c);
            while self.tail.len() > self.limit - h {
                self.tail.pop_front();
            }
        }
    }
    fn finish(self) -> String {
        if self.total <= self.limit {
            return self.head + self.tail.iter().collect::<String>().as_str();
        }
        let mut marker = String::new();
        let mut keep = self.limit;
        for _ in 0..4 {
            marker = format!(
                "[... {} chars elided — assign to a variable and inspect slices, or FINAL_VAR it ...]",
                self.total.saturating_sub(keep)
            );
            keep = self.limit.saturating_sub(marker.chars().count())
        }
        if marker.chars().count() >= self.limit {
            return marker.chars().take(self.limit).collect();
        }
        let front = keep / 2;
        let back = keep - front;
        let a: String = self.head.chars().take(front).collect();
        let b: String = self
            .tail
            .iter()
            .skip(self.tail.len().saturating_sub(back))
            .collect();
        format!("{a}{marker}{b}")
    }
}
impl PrintWriterCallback for BoundedOutput {
    fn stdout_write(&mut self, output: Cow<'_, str>) -> Result<(), MontyException> {
        self.push_str(&output);
        Ok(())
    }
    fn stdout_push(&mut self, end: char) -> Result<(), MontyException> {
        self.push(end);
        Ok(())
    }
}
fn run_cell(
    mut repl: MontyRepl,
    code: &str,
    cfg: &Config,
    default_model: &str,
) -> (MontyRepl, String, bool, Option<Final>) {
    repl.tracker_mut()
        .set_max_duration(Duration::from_secs(cfg.cell_timeout));
    let inputs = ["llm", "llm_batch", "llm_batch_fresh", "FINAL", "FINAL_VAR"]
        .into_iter()
        .map(|n| {
            (
                n.into(),
                MontyObject::Function {
                    name: n.into(),
                    docstring: None,
                },
            )
        })
        .collect();
    let mut printed = BoundedOutput::new(cfg.output_cap);
    let mut final_out = None;
    let mut call_count = 0usize;
    let mut progress = match repl.feed_start(code, inputs, PrintWriter::Callback(&mut printed)) {
        Ok(p) => p,
        Err(e) => {
            let e = *e;
            printed.push_str(&e.error.to_string());
            return (e.repl, printed.finish(), false, final_out);
        }
    };
    loop {
        progress = match progress {
            ReplProgress::Complete { repl, value } => {
                if !matches!(value, MontyObject::None) {
                    match value {
                        MontyObject::String(s) => {
                            printed.push('\'');
                            printed.push_str(&s);
                            printed.push('\'')
                        }
                        v => printed.push_str(&v.py_repr()),
                    }
                    printed.push('\n')
                }
                return (repl, printed.finish(), true, final_out);
            }
            ReplProgress::FunctionCall(call) => {
                let result = external(
                    &call.function_name,
                    &call.args,
                    &call.kwargs,
                    cfg,
                    default_model,
                    &mut final_out,
                    &mut call_count,
                )
                .map_err(MontyException::runtime_error);
                let resumed = match result {
                    Ok(v) => call.resume(v, PrintWriter::Callback(&mut printed)),
                    Err(e) => call.resume(e, PrintWriter::Callback(&mut printed)),
                };
                match resumed {
                    Ok(p) => p,
                    Err(e) => {
                        let e = *e;
                        printed.push_str(&e.error.to_string());
                        return (e.repl, printed.finish(), false, final_out);
                    }
                }
            }
            ReplProgress::NameLookup(call) => match call.resume(
                NameLookupResult::Undefined,
                PrintWriter::Callback(&mut printed),
            ) {
                Ok(p) => p,
                Err(e) => {
                    let e = *e;
                    printed.push_str(&e.error.to_string());
                    return (e.repl, printed.finish(), false, final_out);
                }
            },
            ReplProgress::OsCall(call) => match call.resume(
                MontyException::runtime_error("OS access is disabled"),
                PrintWriter::Callback(&mut printed),
            ) {
                Ok(p) => p,
                Err(e) => {
                    let e = *e;
                    printed.push_str(&e.error.to_string());
                    return (e.repl, printed.finish(), false, final_out);
                }
            },
            ReplProgress::ResolveFutures(p) => {
                printed.push_str("RuntimeError: unresolved async call");
                return (p.into_repl(), printed.finish(), false, final_out);
            }
        }
    }
}

const SOLO_STRUCTURAL_SAMPLE_BYTES: usize = 4096;
const SOLO_SAMPLE_SIDE_BYTES: usize = 1700;

fn escaped_sample_side(
    chars: impl Iterator<Item = char>,
    reverse: bool,
) -> Result<(String, usize)> {
    let mut fragments = Vec::new();
    let mut escaped_bytes = 0usize;
    let mut source_chars = 0usize;
    for ch in chars {
        let encoded = serde_json::to_string(&ch.to_string())?;
        let mut fragment = encoded[1..encoded.len() - 1].to_owned();
        // JSON permits these scalars literally, but JavaScript-like prompt consumers also treat
        // them as line boundaries. Escape them explicitly so untrusted data cannot create framing.
        fragment = fragment
            .replace('\u{0085}', "\\u0085")
            .replace('\u{2028}', "\\u2028")
            .replace('\u{2029}', "\\u2029");
        let width = fragment.len();
        if escaped_bytes + width > SOLO_SAMPLE_SIDE_BYTES {
            break;
        }
        escaped_bytes += width;
        source_chars += 1;
        fragments.push(fragment);
    }
    if reverse {
        fragments.reverse();
    }
    Ok((fragments.concat(), source_chars))
}

/// A deterministic, escaped structural view that exposes bounded head and tail context without
/// copying the complete input into a model prompt. The release-time byte check is authoritative;
/// labels, escapes, and multibyte UTF-8 all count toward the same serialized envelope.
fn structural_sample(text: &str, total: usize) -> Result<String> {
    let (head, head_source_chars) = escaped_sample_side(text.chars(), false)?;
    let sample = if head_source_chars == total {
        format!("[chars 0..{total} of {total}; JSON-string contents]\n{head}")
    } else {
        let (tail, tail_source_chars) =
            escaped_sample_side(text.chars().rev().take(total - head_source_chars), true)?;
        let tail_start = total.saturating_sub(tail_source_chars);
        format!(
            "[HEAD chars 0..{head_source_chars} of {total}; JSON-string contents]\n{head}\n\
[... {gap} source chars omitted ...]\n\
[TAIL chars {tail_start}..{total} of {total}; JSON-string contents]\n{tail}",
            gap = total.saturating_sub(head_source_chars + tail_source_chars),
        )
    };
    if sample.len() > SOLO_STRUCTURAL_SAMPLE_BYTES {
        bail!(
            "solo structural sample exceeds {} serialized UTF-8 bytes",
            SOLO_STRUCTURAL_SAMPLE_BYTES
        )
    }
    Ok(sample)
}

pub struct SoloSession {
    repl: Option<MontyRepl>,
    sub_model: String,
    answer: Option<String>,
    structural_sample: Option<String>,
}
impl SoloSession {
    pub fn new(cfg: &Config, sub_model: Option<String>) -> Result<Self> {
        let tracker = ResourceTracker::new(
            ResourceLimits::default().max_duration(Duration::from_secs(cfg.cell_timeout)),
        );
        let mut repl = MontyRepl::new("azdaja", tracker, CompileOptions::default());
        repl.feed_run(PRELUDE, vec![], PrintWriter::Disabled)
            .context("Monty capability canary failed")?;
        Ok(Self {
            repl: Some(repl),
            sub_model: sub_model.unwrap_or_else(|| cfg.default_model.clone()),
            answer: None,
            structural_sample: None,
        })
    }
    pub fn load(&mut self, path: &Path, var: &str, cfg: &Config) -> Result<String> {
        // Every load attempt invalidates prior prompt evidence before validation or I/O.
        self.structural_sample = None;
        if !Regex::new(r"^[A-Za-z_][A-Za-z0-9_]*$")
            .unwrap()
            .is_match(var)
        {
            bail!("invalid variable name")
        }
        let text = fs::read_to_string(path)
            .with_context(|| format!("input is not UTF-8: {}", path.display()))?;
        let chars = text.chars().count();
        let lines = text.lines().count();
        let sample = structural_sample(&text, chars)?;
        let repl = self
            .repl
            .as_mut()
            .ok_or_else(|| anyhow!("solo session is busy"))?;
        repl.tracker_mut()
            .set_max_duration(Duration::from_secs(cfg.cell_timeout));
        repl.feed_run(
            &format!("{var} = __azdaja_loaded"),
            vec![("__azdaja_loaded".into(), MontyObject::String(text))],
            PrintWriter::Disabled,
        )?;
        self.structural_sample = Some(sample);
        Ok(format!(
            "loaded '{var}' : str, {chars} chars, {lines} lines"
        ))
    }
    pub fn structural_sample(&self) -> Result<&str> {
        self.structural_sample
            .as_deref()
            .ok_or_else(|| anyhow!("solo session has no structural sample"))
    }
    pub fn exec(&mut self, code: &str, cfg: &Config) -> Result<ExecResult> {
        let repl = self
            .repl
            .take()
            .ok_or_else(|| anyhow!("solo session is busy"))?;
        let (mut repl, mut output, success, mut final_out) =
            run_cell(repl, code, cfg, &self.sub_model);
        let mut success = success;
        if success
            && final_out.is_none()
            && Regex::new(r"(?m)^\s*FINAL\s*=").unwrap().is_match(code)
            && let Ok(value) = repl.feed_run("FINAL", vec![], PrintWriter::Disabled)
            && !matches!(value, MontyObject::None | MontyObject::Function { .. })
        {
            final_out = Some(Final::Value(value))
        }
        let mut finalized = false;
        if success && let Some(final_value) = final_out {
            let value = match final_value {
                Final::Value(v) => Some(v),
                Final::Var(name) => match repl.feed_run(&name, vec![], PrintWriter::Disabled) {
                    Ok(v) => Some(v),
                    Err(e) => {
                        output.push_str(&format!("\n{e}"));
                        success = false;
                        None
                    }
                },
            };
            if let Some(v) = value {
                self.answer = Some(v.to_string());
                finalized = true
            }
        }
        self.repl = Some(repl);
        Ok(ExecResult {
            output: cap(&output, cfg.output_cap),
            success,
            finalized,
        })
    }
    pub fn final_answer(&self, cfg: &Config) -> Result<String> {
        self.answer
            .as_deref()
            .map(|s| cap(s, cfg.output_cap))
            .ok_or_else(|| anyhow!("session has no final answer"))
    }
}

pub fn exec(sid: &str, code: &str, cfg: &Config) -> Result<ExecResult> {
    let dir = session_dir(sid)?;
    let _guard = lock(&dir)?;
    let meta = read_meta(&dir)?;
    let model = meta.sub_model.as_deref().unwrap_or(&cfg.default_model);
    let repl = load_repl(&dir)?;
    let (mut repl, mut output, success, mut final_out) = run_cell(repl, code, cfg, model);
    let mut success = success;
    // Paper-style trajectories sometimes assign `FINAL = answer` instead of calling it.
    if success
        && final_out.is_none()
        && Regex::new(r"(?m)^\s*FINAL\s*=").unwrap().is_match(code)
        && let Ok(value) = repl.feed_run("FINAL", vec![], PrintWriter::Disabled)
        && !matches!(value, MontyObject::None | MontyObject::Function { .. })
    {
        final_out = Some(Final::Value(value));
    }
    let mut finalized = false;
    if success && let Some(final_value) = final_out {
        let value = match final_value {
            Final::Value(v) => Some(v),
            Final::Var(name) => match repl.feed_run(&name, vec![], PrintWriter::Disabled) {
                Ok(v) => Some(v),
                Err(e) => {
                    output.push_str(&format!("\n{e}"));
                    success = false;
                    None
                }
            },
        };
        if let Some(v) = value {
            atomic_write(&dir.join("final"), v.to_string().as_bytes())?;
            finalized = true
        }
    }
    save_repl(&dir, &repl)?;
    Ok(ExecResult {
        output: cap(&output, cfg.output_cap),
        success,
        finalized,
    })
}
pub fn final_answer(sid: &str, cfg: &Config) -> Result<String> {
    let dir = session_dir(sid)?;
    let _guard = lock(&dir)?;
    let b = fs::read(dir.join("final")).context("session has no final answer")?;
    Ok(cap(&String::from_utf8(b)?, cfg.output_cap))
}
pub fn kill(sid: &str) -> Result<()> {
    let dir = session_dir(sid)?;
    let _guard = lock(&dir)?;
    fs::remove_dir_all(dir)?;
    Ok(())
}

pub fn cap(s: &str, limit: usize) -> String {
    let n = s.chars().count();
    if n <= limit {
        return s.into();
    }
    if limit == 0 {
        return String::new();
    }
    let mut marker = String::new();
    let mut keep = limit;
    for _ in 0..4 {
        let elided = n.saturating_sub(keep);
        marker = format!(
            "[... {elided} chars elided — assign to a variable and inspect slices, or FINAL_VAR it ...]"
        );
        keep = limit.saturating_sub(marker.chars().count());
    }
    if marker.chars().count() >= limit {
        return marker.chars().take(limit).collect();
    }
    let front = keep / 2;
    let back = keep - front;
    let a: String = s.chars().take(front).collect();
    let b: String = s.chars().skip(n - back).collect();
    format!("{a}{marker}{b}")
}

pub const LLM_BATCH_ERROR_KIND: &str = "provider_call_failed_retry_item";

type CallItemResult = std::result::Result<String, String>;

fn batch_item_value(result: CallItemResult) -> String {
    match result {
        Ok(value) => value,
        Err(error) => {
            let compact = error.split_whitespace().collect::<Vec<_>>().join(" ");
            let message: String = compact.chars().take(1024).collect();
            serde_json::json!({
                "azdaja_error": LLM_BATCH_ERROR_KIND,
                "message": message,
            })
            .to_string()
        }
    }
}

fn call_many_items(
    prompts: &[String],
    model: &str,
    workers: usize,
    cfg: &Config,
    batch: bool,
    use_shared: bool,
) -> Result<Vec<CallItemResult>> {
    let depth = env::var("RLM_DEPTH")
        .ok()
        .and_then(|s| s.parse::<u32>().ok())
        .unwrap_or(0);
    if depth >= cfg.max_depth {
        bail!("maximum RLM depth {} reached", cfg.max_depth);
    }
    if prompts.is_empty() {
        return Ok(Vec::new());
    }
    if prompts.len() > cfg.max_calls_per_cell {
        bail!(
            "llm call budget exceeded: {} > {}",
            prompts.len(),
            cfg.max_calls_per_cell
        )
    }
    if !(1..=32).contains(&workers) {
        bail!("workers must be between 1 and 32")
    }
    preflight_model_trace_sink()?;
    #[cfg(unix)]
    if batch && !use_shared && cfg.sub_llm_cmd == "jcode-api" {
        // A fresh/independent batch must not leave the root subscription session occupying
        // provider capacity or accidentally reuse its conversation. Archive it before any
        // annotator setup begins.
        drop(SOLO_SHARED_JCODE.lock().unwrap().take());
    }
    let results = std::sync::Mutex::new((
        0usize,
        std::iter::repeat_with(|| None)
            .take(prompts.len())
            .collect::<Vec<Option<CallItemResult>>>(),
    ));
    thread::scope(|scope| {
        for _ in 0..workers.min(prompts.len()) {
            scope.spawn(|| {
                loop {
                    let i = {
                        let mut state = results.lock().unwrap();
                        if state.0 >= prompts.len() {
                            break;
                        }
                        let i = state.0;
                        state.0 += 1;
                        i
                    };
                    let request_id = model_trace_request_id();
                    let entered_turn_budget = Arc::new(EnteredTurnBudget::new(2));
                    #[cfg(unix)]
                    let result: Result<String> = (|| {
                        if batch && cfg.sub_llm_cmd == "jcode-api" {
                        let wire = format!(
                            "[azdaja recursion depth {}/{}: do not invoke azdaja recursively.]\n\n{}",
                            depth + 1,
                            cfg.max_depth,
                            prompts[i]
                        );
                        let shared = if use_shared {
                            SOLO_SHARED_JCODE.lock().unwrap().take()
                        } else {
                            None
                        };
                        if let Some(mut api) = shared {
                            let entered_turn = entered_turn_budget.try_enter()?;
                            let first_started = Instant::now();
                            match api.turn(&wire) {
                                Ok(reply) => {
                                    trace_model_reply_attempt(
                                        &reply,
                                        depth + 1,
                                        &request_id,
                                        1,
                                        entered_turn,
                                        Some(&api.session),
                                        api.usage_observed,
                                    );
                                    Ok(reply.text)
                                }
                                Err(error) => {
                                    api.discard();
                                    let first_session = api.session.clone();
                                    record_model_trace_result(trace_model_turn_failure(
                                        depth + 1,
                                        &request_id,
                                        1,
                                        entered_turn,
                                        Some(&first_session),
                                        &error,
                                        Some(first_started.elapsed().as_millis()),
                                    ));
                                    drop(api);
                                    if !model_transport_error_is_transient(&error) {
                                        Err(error)
                                    } else {
                                        thread::sleep(Duration::from_secs(2));
                                        let second_started = Instant::now();
                                        let mut observation = JcodeSetupObservation::default();
                                        match JcodeSession::open_for_batch_serialized(
                                            cfg,
                                            model,
                                            prompts[i].chars().count(),
                                            &mut observation,
                                        ) {
                                            Err(retry_error) => {
                                                record_model_trace_result(trace_model_setup_failure_attempt(
                                                    depth + 1,
                                                    &request_id,
                                                    2,
                                                    &observation,
                                                    &retry_error,
                                                    Some(second_started.elapsed().as_millis()),
                                                ));
                                                Err(anyhow!(
                                                    "shared turn failed: {error:#}; retry failed: {retry_error:#}"
                                                ))
                                            }
                                            Ok(mut fresh) => {
                                                let retry_entered_turn =
                                                    entered_turn_budget.try_enter()?;
                                                let retry_started = Instant::now();
                                                match fresh.turn(&wire) {
                                                    Ok(reply) => {
                                                        trace_model_reply_attempt(
                                                            &reply,
                                                            depth + 1,
                                                            &request_id,
                                                            2,
                                                            retry_entered_turn,
                                                            Some(&fresh.session),
                                                            fresh.usage_observed,
                                                        );
                                                        Ok(reply.text)
                                                    }
                                                    Err(retry_error) => {
                                                        fresh.discard();
                                                        record_model_trace_result(trace_model_turn_failure(
                                                            depth + 1,
                                                            &request_id,
                                                            2,
                                                            retry_entered_turn,
                                                            Some(&fresh.session),
                                                            &retry_error,
                                                            Some(retry_started.elapsed().as_millis()),
                                                        ));
                                                        Err(anyhow!(
                                                            "shared turn failed: {error:#}; retry failed: {retry_error:#}"
                                                        ))
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        } else {
                            // Setup and entered-turn budgets are independent: up to four setup
                            // failures, but never more than two physical provider turns.
                            let mut result = None;
                            let mut physical_attempt = 0u32;
                            let mut setup_attempts = 0u32;
                            let mut setup_elapsed = Duration::ZERO;
                            let mut retry_delay = Duration::ZERO;
                            while setup_attempts < 4 && entered_turn_budget.entered() < 2 {
                                physical_attempt += 1;
                                if physical_attempt > 1 {
                                    thread::sleep(retry_delay);
                                }
                                let attempt_started = Instant::now();
                                let mut observation = JcodeSetupObservation::default();
                                let mut api = match JcodeSession::open_for_batch_serialized(
                                    cfg,
                                    model,
                                    prompts[i].chars().count(),
                                    &mut observation,
                                ) {
                                    Ok(api) => api,
                                    Err(error) => {
                                        setup_attempts += 1;
                                        setup_elapsed += attempt_started.elapsed();
                                        retry_delay = Duration::from_millis(50);
                                        let transient = model_setup_error_is_transient(
                                            &error,
                                            observation.substage,
                                        );
                                        record_model_trace_result(trace_model_setup_failure_attempt(
                                            depth + 1,
                                            &request_id,
                                            physical_attempt,
                                            &observation,
                                            &error,
                                            Some(attempt_started.elapsed().as_millis()),
                                        ));
                                        result = Some(Err(error));
                                        if !transient
                                            || setup_elapsed >= Duration::from_secs(30)
                                        {
                                            break;
                                        }
                                        continue;
                                    }
                                };
                                let entered_turn = entered_turn_budget.try_enter()?;
                                let turn_started = Instant::now();
                                match api.turn(&wire) {
                                    Ok(reply) => {
                                        trace_model_reply_attempt(
                                            &reply,
                                            depth + 1,
                                            &request_id,
                                            physical_attempt,
                                            entered_turn,
                                            Some(&api.session),
                                            api.usage_observed,
                                        );
                                        result = Some(Ok(reply.text));
                                        break;
                                    }
                                    Err(error) => {
                                        api.discard();
                                        retry_delay = Duration::from_secs(2);
                                        let transient = model_transport_error_is_transient(&error);
                                        record_model_trace_result(trace_model_turn_failure(
                                            depth + 1,
                                            &request_id,
                                            physical_attempt,
                                            entered_turn,
                                            Some(&api.session),
                                            &error,
                                            Some(turn_started.elapsed().as_millis()),
                                        ));
                                        result = Some(Err(error));
                                        if !transient {
                                            break;
                                        }
                                    }
                                }
                            }
                            result.unwrap_or_else(|| Err(anyhow!("provider call did not run")))
                        }
                    } else {
                        call_model_reply_with_attempt(
                            &prompts[i],
                            model,
                            cfg,
                            depth + 1,
                            &request_id,
                            1,
                            &entered_turn_budget,
                        )
                        .map(|reply| reply.text)
                        }
                    })();
                    #[cfg(not(unix))]
                    let result = call_model_reply_with_attempt(
                        &prompts[i],
                        model,
                        cfg,
                        depth + 1,
                        &request_id,
                        1,
                        &entered_turn_budget,
                    )
                    .map(|reply| reply.text);
                    results.lock().unwrap().1[i] =
                        Some(result.map_err(|error| format!("{error:#}")));
                }
            });
        }
    });
    Ok(results
        .into_inner()
        .unwrap()
        .1
        .into_iter()
        .map(|result| {
            result.unwrap_or_else(|| Err("llm_batch worker did not produce a result".into()))
        })
        .collect())
}

pub fn call_many(
    prompts: &[String],
    model: &str,
    workers: usize,
    cfg: &Config,
) -> Result<Vec<String>> {
    Ok(call_many_items(prompts, model, workers, cfg, true, true)?
        .into_iter()
        .map(batch_item_value)
        .collect())
}

#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct ModelUsage {
    pub input: u64,
    pub output: u64,
    pub cache_read: u64,
}
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelReply {
    pub text: String,
    pub usage: ModelUsage,
    pub provider: String,
    pub model: String,
    pub latency_ms: u128,
}

pub const MODEL_TRACE_SCHEMA_VERSION: u8 = 2;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ModelTraceEvent {
    ModelAttempt,
}

/// The phase reached by one physical provider attempt.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ModelAttemptCategory {
    SessionSetup,
    Turn,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ModelAttemptOutcome {
    Failed,
    Succeeded,
}

/// Coarse, finite failure classification suitable for aggregate reliability reports.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ModelTransportErrorCategory {
    BridgeIo,
    BridgeProtocol,
    Provider,
    Timeout,
    SetupRoute,
    Unknown,
}

impl ModelTransportErrorCategory {
    /// Only explicitly transient transport classes are eligible for an automatic retry.
    pub fn is_transient(self) -> bool {
        matches!(self, Self::BridgeIo | Self::BridgeProtocol | Self::Timeout)
    }
}

/// An atomically enforced physical entered-turn budget shared by every retry of one
/// logical call. Setup attempts do not consume it.
#[derive(Debug)]
pub struct EnteredTurnBudget {
    limit: u32,
    entered: AtomicU32,
}

impl EnteredTurnBudget {
    pub fn new(limit: u32) -> Self {
        Self {
            limit,
            entered: AtomicU32::new(0),
        }
    }

    fn try_enter(&self) -> Result<u32> {
        let mut current = self.entered.load(Ordering::Acquire);
        loop {
            if current >= self.limit {
                bail!(
                    "physical entered-turn budget exhausted ({}/{})",
                    current,
                    self.limit
                )
            }
            match self.entered.compare_exchange_weak(
                current,
                current + 1,
                Ordering::AcqRel,
                Ordering::Acquire,
            ) {
                Ok(_) => return Ok(current + 1),
                Err(observed) => current = observed,
            }
        }
    }

    pub fn entered(&self) -> u32 {
        self.entered.load(Ordering::Acquire)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ModelSetupSubstage {
    Connect,
    Hello,
    Attach,
    RuntimeInfo,
    SetModel,
    Reasoning,
}

impl ModelSetupSubstage {
    fn as_str(self) -> &'static str {
        match self {
            Self::Connect => "connect",
            Self::Hello => "hello",
            Self::Attach => "attach",
            Self::RuntimeInfo => "runtime_info",
            Self::SetModel => "set_model",
            Self::Reasoning => "reasoning",
        }
    }
}

#[derive(Debug, Clone)]
struct JcodeSetupObservation {
    session_id: Option<String>,
    substage: ModelSetupSubstage,
}

impl Default for JcodeSetupObservation {
    fn default() -> Self {
        Self {
            session_id: None,
            substage: ModelSetupSubstage::Connect,
        }
    }
}

#[derive(Debug)]
struct JcodeApiError {
    message: String,
    code: Option<String>,
    transient: bool,
}

impl std::fmt::Display for JcodeApiError {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if let Some(code) = &self.code {
            write!(formatter, "jcode API error code={code:?}: {}", self.message)
        } else {
            write!(formatter, "jcode API error: {}", self.message)
        }
    }
}

impl std::error::Error for JcodeApiError {}

fn jcode_frame_error(frame: &serde_json::Value) -> anyhow::Error {
    let message = frame
        .get("message")
        .and_then(serde_json::Value::as_str)
        .unwrap_or("error")
        .to_owned();
    let code = frame
        .get("code")
        .or_else(|| frame.get("class"))
        .and_then(serde_json::Value::as_str)
        .map(str::to_owned);
    // Provider text is never retry authority. Only these protocol-supplied typed values are.
    let transient = code.as_deref().is_some_and(|value| {
        matches!(
            value,
            "rate_limited"
                | "overloaded"
                | "service_unavailable"
                | "temporarily_unavailable"
                | "connection_reset"
                | "server_timeout"
        )
    });
    anyhow::Error::new(JcodeApiError {
        message,
        code,
        transient,
    })
}

/// One JSONL row in `AZDAJA_MODEL_TRACE`.
///
/// The legacy route/usage/error fields remain additive for readers of the original
/// schema.  Version-aware readers must validate the typed attempt fields rather than
/// guessing whether an error happened during setup or after a model turn was entered.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ModelTrace {
    pub schema_version: u8,
    pub event: ModelTraceEvent,
    pub timestamp_ms: u128,
    pub depth: u32,
    /// Stable correlation key shared by every retry of one logical provider call.
    pub request_id: String,
    /// One-based physical attempt number for this logical provider call.
    pub attempt: u32,
    /// One-based entered-turn ordinal within the separately enforced logical budget.
    /// Setup failures have no ordinal because no provider turn was entered.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub entered_turn: Option<u32>,
    /// Provider session ID, or null when setup failed before an ID was observed.
    pub session_id: Option<String>,
    pub category: ModelAttemptCategory,
    pub outcome: ModelAttemptOutcome,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error_category: Option<ModelTransportErrorCategory>,
    /// Additive legacy alias for `category`.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stage: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub setup_substage: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub provider: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub model: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub input_tokens: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub output_tokens: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cache_read_tokens: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub latency_ms: Option<u128>,
    /// Explicitly prevents a successful retry from being presented as a clean call.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub degraded_transport: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub failed_attempts_before_success: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub response: Option<String>,
}

#[cfg(unix)]
#[derive(Debug)]
struct BridgePaths {
    socket: PathBuf,
    pidfile: PathBuf,
    home: PathBuf,
    run: PathBuf,
    marker: PathBuf,
}
#[cfg(unix)]
fn stable_path_hash(path: &Path) -> u64 {
    use std::os::unix::ffi::OsStrExt;
    let mut hash = 0xcbf29ce484222325u64;
    for byte in path.as_os_str().as_bytes() {
        hash ^= u64::from(*byte);
        hash = hash.wrapping_mul(0x100000001b3);
    }
    hash
}
#[cfg(unix)]
fn short_runtime_dir(state: &Path, uid: u32) -> PathBuf {
    PathBuf::from("/tmp")
        .join(format!("azdaja-{uid}"))
        .join(format!("r-{:016x}", stable_path_hash(state)))
}
#[cfg(unix)]
fn secure_owned_runtime_dir(path: &Path) -> Result<()> {
    use std::os::unix::fs::MetadataExt;
    match fs::symlink_metadata(path) {
        Ok(meta) => {
            if !meta.file_type().is_dir()
                || meta.file_type().is_symlink()
                || meta.uid() != unsafe { libc::geteuid() }
            {
                bail!("unsafe private runtime directory: {}", path.display())
            }
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => fs::create_dir(path)?,
        Err(error) => return Err(error.into()),
    }
    chmod(path, 0o700)
}
#[cfg(unix)]
fn bridge_paths() -> Result<BridgePaths> {
    use std::os::unix::ffi::OsStrExt;
    let state = state_home()?;
    let private = state.join("jcode-api");
    secure_dir(&private)?;
    let runtime = short_runtime_dir(&state, unsafe { libc::geteuid() });
    let runtime_root = runtime
        .parent()
        .ok_or_else(|| anyhow!("invalid private runtime path"))?;
    secure_owned_runtime_dir(runtime_root)?;
    secure_owned_runtime_dir(&runtime)?;
    let run = runtime.join("run");
    secure_owned_runtime_dir(&run)?;
    let socket = runtime.join("api.sock");
    if socket.as_os_str().as_bytes().len() >= 100 {
        bail!("private Jcode API socket path is unexpectedly long")
    }
    let marker = private.join("runtime-dir");
    atomic_write(&marker, runtime.as_os_str().as_bytes())?;
    let home = private.join("home");
    secure_dir(&home)?;
    Ok(BridgePaths {
        socket,
        pidfile: private.join("bridge.pid"),
        home,
        run,
        marker,
    })
}
#[cfg(unix)]
fn socket_alive(path: &Path) -> bool {
    UnixStream::connect(path).is_ok()
}
#[cfg(unix)]
fn ensure_jcode_bridge(cfg: &Config) -> Result<PathBuf> {
    if let Some(path) = env::var_os("AZDAJA_JCODE_API_SOCKET") {
        let path = PathBuf::from(path);
        if socket_alive(&path) {
            return Ok(path);
        }
        bail!("AZDAJA_JCODE_API_SOCKET is not accepting connections")
    }
    if cfg.jcode_provider != "openai" {
        bail!("jcode-api currently requires subscription provider 'openai'")
    }
    let paths = bridge_paths()?;
    if socket_alive(&paths.socket) {
        return Ok(paths.socket);
    }
    let _guard = lock_path(&state_home()?.join("jcode-api.lock"))?;
    if socket_alive(&paths.socket) {
        return Ok(paths.socket);
    }
    let _ = fs::remove_file(&paths.socket);
    let user_home = env::var_os("HOME")
        .map(PathBuf::from)
        .ok_or_else(|| anyhow!("HOME is required for subscription OAuth"))?;
    let auth = user_home.join(".jcode/openai-auth.json");
    if !auth.is_file() {
        bail!(
            "OpenAI subscription OAuth login missing: {}",
            auth.display()
        )
    }
    use std::os::unix::fs::MetadataExt;
    let auth_meta = fs::metadata(&auth)?;
    if auth_meta.mode() & 0o077 != 0 || auth_meta.uid() != unsafe { libc::geteuid() } {
        bail!("OpenAI OAuth credential must be owner-only and owned by the current user")
    }
    let auth_link = paths.home.join("openai-auth.json");
    if let Ok(meta) = fs::symlink_metadata(&auth_link) {
        if !meta.file_type().is_symlink() {
            bail!("refusing non-symlink credential in private Jcode home")
        }
        if fs::canonicalize(&auth_link)? != fs::canonicalize(&auth)? {
            bail!("private Jcode OAuth link targets a different credential")
        }
    } else {
        std::os::unix::fs::symlink(&auth, &auth_link)?
    }
    let mut cmd = Command::new("jcode");
    cmd.args(["api-bridge", "--api-socket"])
        .arg(&paths.socket)
        .args(["--no-update", "--quiet", "--provider", "openai", "--model"])
        .arg(&cfg.default_model)
        .arg("--disable-base-tools")
        .env_clear();
    for key in [
        "HOME",
        "PATH",
        "USER",
        "LOGNAME",
        "SHELL",
        "TMPDIR",
        "LANG",
        "LC_ALL",
        "TERM",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_CACHE_HOME",
    ] {
        if let Some(value) = env::var_os(key) {
            cmd.env(key, value);
        }
    }
    cmd.env("JCODE_HOME", &paths.home)
        .env("JCODE_RUNTIME_DIR", &paths.run)
        .env("JCODE_API_SOCKET", &paths.socket)
        .env("JCODE_SOCKET", paths.run.join("j.sock"))
        .env("JCODE_NO_TELEMETRY", "1")
        .env("JCODE_TOOL_PROFILE", "none")
        .env("JCODE_RUN_MCP", "0")
        .env("JCODE_RUN_AUTO_POKE", "0")
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    use std::os::unix::process::CommandExt;
    cmd.process_group(0);
    let mut child = cmd
        .spawn()
        .context("failed to start private Jcode API bridge")?;
    atomic_write(&paths.pidfile, child.id().to_string().as_bytes())?;
    let deadline = Instant::now() + Duration::from_secs(30);
    while Instant::now() < deadline {
        if socket_alive(&paths.socket) {
            return Ok(paths.socket);
        }
        if let Some(status) = child.try_wait()? {
            bail!(
                "private Jcode API bridge exited before readiness ({status}); inspect {}",
                paths.home.join("logs").display()
            )
        }
        thread::sleep(Duration::from_millis(25))
    }
    let _ = child.kill();
    let _ = child.wait();
    bail!(
        "private Jcode API bridge did not become ready; inspect {} (runtime marker {})",
        paths.home.join("logs").display(),
        paths.marker.display()
    )
}

#[cfg(unix)]
fn jcode_root_timeout(cfg: &Config) -> Duration {
    Duration::from_secs(cfg.sub_timeout.min(30))
}
#[cfg(unix)]
fn jcode_batch_timeout(cfg: &Config, prompt_chars: usize) -> Duration {
    let cap = if prompt_chars >= 8_000 { 90 } else { 45 };
    Duration::from_secs(cfg.sub_timeout.min(cap))
}

#[cfg(unix)]
struct JcodeSession {
    stream: UnixStream,
    reader: BufReader<UnixStream>,
    next_id: u64,
    session: String,
    usage: ModelUsage,
    usage_observed: bool,
    provider: String,
    model: String,
    requested_model: String,
    timeout: Duration,
    cancel_before_archive: bool,
}
#[cfg(unix)]
static SOLO_SHARED_JCODE: std::sync::Mutex<Option<JcodeSession>> = std::sync::Mutex::new(None);
#[cfg(unix)]
static JCODE_SETUP_LOCK: std::sync::Mutex<()> = std::sync::Mutex::new(());
#[cfg(unix)]
impl JcodeSession {
    fn send(&mut self, value: serde_json::Value) -> Result<u64> {
        let id = self.next_id;
        self.next_id += 1;
        let mut obj = value
            .as_object()
            .cloned()
            .ok_or_else(|| anyhow!("request must be object"))?;
        obj.insert("v".into(), 1.into());
        obj.insert("id".into(), id.into());
        serde_json::to_writer(&mut self.stream, &obj)?;
        self.stream.write_all(b"\n")?;
        self.stream.flush()?;
        Ok(id)
    }
    fn frame(&mut self) -> Result<serde_json::Value> {
        let mut line = String::new();
        const MAX_FRAME: u64 = 16 * 1024 * 1024;
        let read = self
            .reader
            .by_ref()
            .take(MAX_FRAME + 1)
            .read_line(&mut line);
        match read {
            Ok(0) => bail!("jcode API bridge closed"),
            Ok(n) if n as u64 > MAX_FRAME || !line.ends_with('\n') => {
                bail!("jcode API frame exceeds 16 MiB or is unterminated")
            }
            Ok(_) => {}
            Err(e)
                if matches!(
                    e.kind(),
                    std::io::ErrorKind::WouldBlock | std::io::ErrorKind::TimedOut
                ) =>
            {
                bail!("jcode subscription turn timed out")
            }
            Err(e) => return Err(e).context("reading jcode API frame"),
        };
        serde_json::from_str(&line).context("invalid jcode API frame")
    }
    fn reply_with_timeout(
        &mut self,
        id: u64,
        kind: &str,
        timeout: Duration,
    ) -> Result<serde_json::Value> {
        let deadline = Instant::now() + timeout;
        loop {
            let remaining = deadline
                .checked_duration_since(Instant::now())
                .ok_or_else(|| anyhow!("jcode API request timed out"))?;
            self.stream.set_read_timeout(Some(remaining))?;
            let f = self.frame()?;
            // A flat error is connection-scoped in the bridge protocol. Requests on a
            // dedicated session connection are serialized, so waiting for a correlated
            // reply after such an error only converts an immediate failure into a timeout.
            if f.get("ev").and_then(serde_json::Value::as_str) == Some("error") {
                return Err(jcode_frame_error(&f));
            }
            if f.get("reply_to").and_then(serde_json::Value::as_u64) == Some(id)
                && f.get("ev").and_then(serde_json::Value::as_str) == Some(kind)
            {
                return Ok(f);
            }
        }
    }
    fn reply(&mut self, id: u64, kind: &str) -> Result<serde_json::Value> {
        self.reply_with_timeout(id, kind, self.timeout)
    }
    fn reply_before(
        &mut self,
        id: u64,
        kind: &str,
        deadline: Instant,
    ) -> Result<serde_json::Value> {
        let remaining = deadline
            .checked_duration_since(Instant::now())
            .ok_or_else(|| anyhow!("jcode session setup timed out"))?;
        self.reply_with_timeout(id, kind, remaining)
    }
    fn attached_before(&mut self, id: u64, deadline: Instant) -> Result<String> {
        loop {
            let remaining = deadline
                .checked_duration_since(Instant::now())
                .ok_or_else(|| anyhow!("jcode session attach timed out"))?;
            self.stream.set_read_timeout(Some(remaining))?;
            let f = self.frame()?;
            if f.get("ev").and_then(serde_json::Value::as_str) == Some("error") {
                return Err(jcode_frame_error(&f));
            }
            let correlated = f.get("reply_to").and_then(serde_json::Value::as_u64) == Some(id)
                && f.get("ev").and_then(serde_json::Value::as_str) == Some("attached");
            if correlated {
                let sid = f
                    .pointer("/session/session_id")
                    .or_else(|| f.get("session_id"))
                    .and_then(serde_json::Value::as_str)
                    .filter(|value| !value.is_empty())
                    .ok_or_else(|| anyhow!("jcode API omitted session id"))?;
                return Ok(sid.to_owned());
            }
        }
    }
    fn open(cfg: &Config, model: &str, observation: &mut JcodeSetupObservation) -> Result<Self> {
        Self::open_with_timeout(
            cfg,
            model,
            Duration::from_secs(cfg.sub_timeout),
            observation,
        )
    }
    fn open_for_root(
        cfg: &Config,
        model: &str,
        observation: &mut JcodeSetupObservation,
    ) -> Result<Self> {
        Self::open_with_timeout(cfg, model, jcode_root_timeout(cfg), observation)
    }
    fn open_for_batch(
        cfg: &Config,
        model: &str,
        prompt_chars: usize,
        observation: &mut JcodeSetupObservation,
    ) -> Result<Self> {
        Self::open_with_timeout(
            cfg,
            model,
            jcode_batch_timeout(cfg, prompt_chars),
            observation,
        )
    }
    fn open_for_batch_serialized(
        cfg: &Config,
        model: &str,
        prompt_chars: usize,
        observation: &mut JcodeSetupObservation,
    ) -> Result<Self> {
        // Independence requires one API connection and session per item. Conservatively order
        // their short setup handshakes, then release the lock before concurrent model turns.
        let _guard = JCODE_SETUP_LOCK.lock().unwrap();
        Self::open_for_batch(cfg, model, prompt_chars, observation)
    }
    fn runtime_is_subscription_route(rt: &serde_json::Value, model: &str) -> bool {
        rt.get("provider").and_then(serde_json::Value::as_str) == Some("OpenAI")
            && rt.get("model").and_then(serde_json::Value::as_str) == Some(model)
            && rt
                .get("routes")
                .and_then(serde_json::Value::as_array)
                .is_some_and(|routes| {
                    routes.iter().any(|route| {
                        route.get("provider").and_then(serde_json::Value::as_str) == Some("OpenAI")
                            && route.get("model").and_then(serde_json::Value::as_str) == Some(model)
                            && route.get("api_method").and_then(serde_json::Value::as_str)
                                == Some("openai-oauth")
                            && route.get("available").and_then(serde_json::Value::as_bool)
                                == Some(true)
                    })
                })
    }
    fn open_with_timeout(
        cfg: &Config,
        model: &str,
        timeout: Duration,
        observation: &mut JcodeSetupObservation,
    ) -> Result<Self> {
        observation.substage = ModelSetupSubstage::Connect;
        let socket = ensure_jcode_bridge(cfg)?;
        let stream = UnixStream::connect(&socket)?;
        stream.set_read_timeout(Some(timeout))?;
        stream.set_write_timeout(Some(Duration::from_secs(10)))?;
        let reader = BufReader::new(stream.try_clone()?);
        let mut this = Self {
            stream,
            reader,
            next_id: 1,
            session: String::new(),
            usage: ModelUsage::default(),
            usage_observed: false,
            provider: String::new(),
            model: String::new(),
            requested_model: model.to_owned(),
            timeout,
            cancel_before_archive: true,
        };
        let setup_deadline = Instant::now() + Duration::from_secs(12);
        observation.substage = ModelSetupSubstage::Hello;
        let id=this.send(serde_json::json!({"req":"hello","min_version":1,"max_version":1,"client":format!("azdaja/{VERSION}")}))?;
        this.reply_before(id, "hello_ok", setup_deadline)
            .context("jcode hello setup")?;
        observation.substage = ModelSetupSubstage::Attach;
        let id = this
            .send(serde_json::json!({"req":"create_session","working_dir":env::current_dir()?}))?;
        let session_id = this
            .attached_before(id, setup_deadline)
            .context("jcode attach setup")?;
        this.session = session_id;
        observation.session_id = Some(this.session.clone());
        // Pace consecutive bridge control frames. The released bridge can otherwise emit a
        // connection-scoped JSON parser error or a transient empty route catalog when queried
        // in the same scheduler tick as attachment.
        thread::sleep(Duration::from_millis(50));
        // Runtime info is the authoritative post-attach route barrier. An uncorrelated
        // model_info may arrive before or after the correlated attached reply, so do not
        // make its timing part of session setup.
        let runtime_info = |session: &mut Self| -> Result<serde_json::Value> {
            let id = session
                .send(serde_json::json!({"req":"get_runtime_info","session_id":session.session}))?;
            session
                .reply_before(id, "runtime_info", setup_deadline)
                .context("jcode route setup")
        };
        observation.substage = ModelSetupSubstage::RuntimeInfo;
        let mut rt = runtime_info(&mut this)?;
        for delay_ms in [50, 150] {
            if Self::runtime_is_subscription_route(&rt, model) {
                break;
            }
            let top_matches = rt.get("provider").and_then(serde_json::Value::as_str)
                == Some("OpenAI")
                && rt.get("model").and_then(serde_json::Value::as_str) == Some(model);
            if !top_matches {
                break;
            }
            // A newly attached Jcode session can briefly expose the selected top-level
            // route before its route catalog is populated. Re-query the correlated runtime
            // snapshot instead of needlessly churning the selected model.
            thread::sleep(Duration::from_millis(delay_ms));
            rt = runtime_info(&mut this)?;
        }
        if !Self::runtime_is_subscription_route(&rt, model) {
            thread::sleep(Duration::from_millis(50));
            observation.substage = ModelSetupSubstage::SetModel;
            let id=this.send(serde_json::json!({"req":"set_model","session_id":this.session,"model":format!("openai-oauth:{model}")}))?;
            this.reply_before(id, "ok", setup_deadline)
                .context("jcode model setup")?;
            thread::sleep(Duration::from_millis(50));
            observation.substage = ModelSetupSubstage::RuntimeInfo;
            rt = runtime_info(&mut this)?;
        }
        if !Self::runtime_is_subscription_route(&rt, model) {
            let provider = rt
                .get("provider")
                .and_then(serde_json::Value::as_str)
                .unwrap_or("");
            let resolved = rt
                .get("model")
                .and_then(serde_json::Value::as_str)
                .unwrap_or("");
            bail!("subscription OAuth route mismatch: provider={provider:?} model={resolved:?}")
        }
        this.provider = "OpenAI OAuth".into();
        this.model = model.into();
        thread::sleep(Duration::from_millis(50));
        observation.substage = ModelSetupSubstage::Reasoning;
        let id=this.send(serde_json::json!({"req":"set_reasoning_effort","session_id":this.session,"effort":cfg.jcode_reasoning}))?;
        this.reply_before(id, "ok", setup_deadline)
            .context("jcode reasoning setup")?;
        this.cancel_before_archive = false;
        Ok(this)
    }
    fn discard(&mut self) {
        // A failed turn can leave unread frames on the stream. Mark it for an ordered, bounded
        // cancel-before-archive cleanup rather than trying to reuse the poisoned protocol state.
        self.cancel_before_archive = true;
    }
    fn turn(&mut self, prompt: &str) -> Result<ModelReply> {
        let result = self.turn_inner(prompt);
        if result.is_err() {
            self.discard();
        }
        result
    }
    fn turn_inner(&mut self, prompt: &str) -> Result<ModelReply> {
        let started = Instant::now();
        self.usage = ModelUsage::default();
        self.usage_observed = false;
        let sid = self.session.clone();
        self.send(
            serde_json::json!({"req":"send_message","session_id":sid,"content":prompt,"images":[]}),
        )?;
        let mut text = String::new();
        let deadline = started + self.timeout;
        loop {
            let remaining = deadline
                .checked_duration_since(Instant::now())
                .ok_or_else(|| anyhow!("jcode subscription turn timed out"))?;
            self.stream.set_read_timeout(Some(remaining))?;
            let f = self.frame()?;
            if f.get("session_id").and_then(serde_json::Value::as_str) != Some(&self.session) {
                continue;
            }
            match f.get("ev").and_then(serde_json::Value::as_str) {
                Some("text_delta") => {
                    let delta = f
                        .get("text")
                        .and_then(serde_json::Value::as_str)
                        .unwrap_or("");
                    if text.len().saturating_add(delta.len()) > 16 * 1024 * 1024 {
                        bail!("jcode model response exceeds 16 MiB")
                    }
                    text.push_str(delta)
                }
                Some("token_usage") => {
                    self.usage_observed = true;
                    self.usage.input = f
                        .get("input")
                        .and_then(serde_json::Value::as_u64)
                        .unwrap_or(0);
                    self.usage.output = f
                        .get("output")
                        .and_then(serde_json::Value::as_u64)
                        .unwrap_or(0);
                    self.usage.cache_read = f
                        .get("cache_read_input")
                        .and_then(serde_json::Value::as_u64)
                        .unwrap_or(0)
                }
                Some("permission_request") => {
                    let rid = f
                        .get("request_id")
                        .and_then(serde_json::Value::as_str)
                        .unwrap_or("");
                    let id=self.send(serde_json::json!({"req":"permission_response","session_id":self.session,"request_id":rid,"decision":"deny"}))?;
                    self.reply(id, "ok")?;
                }
                Some("model_info") => {
                    self.provider = f
                        .get("provider")
                        .and_then(serde_json::Value::as_str)
                        .unwrap_or("")
                        .into();
                    self.model = f
                        .get("model")
                        .and_then(serde_json::Value::as_str)
                        .unwrap_or("")
                        .into()
                }
                Some("error") => return Err(jcode_frame_error(&f)),
                Some("turn_done") => {
                    if (self.provider != "OpenAI" && self.provider != "OpenAI OAuth")
                        || self.model != self.requested_model
                    {
                        bail!(
                            "subscription turn reported unexpected route provider={:?} model={:?}, expected OpenAI OAuth/{:?}",
                            self.provider,
                            self.model,
                            self.requested_model
                        )
                    }
                    return Ok(ModelReply {
                        text: text.trim().into(),
                        usage: self.usage.clone(),
                        provider: self.provider.clone(),
                        model: self.model.clone(),
                        latency_ms: started.elapsed().as_millis(),
                    });
                }
                _ => {}
            }
        }
    }
}
#[cfg(unix)]
impl Drop for JcodeSession {
    fn drop(&mut self) {
        let sid = self.session.clone();
        if sid.is_empty() {
            return;
        }
        // Cleanup is control-plane work, not another model turn. In particular, never reuse the
        // prompt-sized turn timeout here: a missing archive acknowledgement used to add 15--55
        // seconds to an otherwise completed batch item. A failed/poisoned stream still gets an
        // ordered best-effort cancel + archive before it is closed so the bridge does not retain an
        // active subscription session indefinitely.
        const CLEANUP_TIMEOUT: Duration = Duration::from_secs(1);
        let _ = self.stream.set_write_timeout(Some(CLEANUP_TIMEOUT));
        if self.cancel_before_archive {
            let _ = self.send(serde_json::json!({"req":"cancel","session_id":sid}));
        }
        if let Ok(id) = self.send(serde_json::json!({"req":"archive_session","session_id":sid})) {
            let _ = self.reply_with_timeout(id, "ok", CLEANUP_TIMEOUT);
        }
    }
}

pub struct RootDriver {
    cfg: Config,
    model: String,
    request_id: String,
    attempt: u32,
    entered_turn_budget: Arc<EnteredTurnBudget>,
    #[cfg(unix)]
    api: Option<JcodeSession>,
    history: String,
}
impl RootDriver {
    pub fn start(cfg: &Config, model: &str) -> Result<Self> {
        Self::start_attempt_with_budget(
            cfg,
            model,
            model_trace_request_id(),
            1,
            Arc::new(EnteredTurnBudget::new(2)),
        )
    }

    /// Start one physical root attempt with the atomic entered-turn budget shared by
    /// every setup and turn retry of the logical call.
    pub fn start_attempt_with_budget(
        cfg: &Config,
        model: &str,
        request_id: String,
        attempt: u32,
        entered_turn_budget: Arc<EnteredTurnBudget>,
    ) -> Result<Self> {
        preflight_model_trace_sink()?;
        #[cfg(unix)]
        let api = if cfg.sub_llm_cmd == "jcode-api" {
            let started = Instant::now();
            let mut observation = JcodeSetupObservation::default();
            match JcodeSession::open_for_root(cfg, model, &mut observation) {
                Ok(api) => Some(api),
                Err(error) => {
                    record_model_trace_result(trace_model_setup_failure_attempt(
                        0,
                        &request_id,
                        attempt,
                        &observation,
                        &error,
                        Some(started.elapsed().as_millis()),
                    ));
                    return Err(error);
                }
            }
        } else {
            None
        };
        Ok(Self {
            cfg: cfg.clone(),
            model: model.into(),
            request_id,
            attempt,
            entered_turn_budget,
            #[cfg(unix)]
            api,
            history: String::new(),
        })
    }

    pub fn turn(&mut self, prompt: &str) -> Result<ModelReply> {
        #[cfg(unix)]
        if let Some(api) = &mut self.api {
            let entered_turn = self.entered_turn_budget.try_enter()?;
            let started = Instant::now();
            let reply = match api.turn(prompt) {
                Ok(reply) => reply,
                Err(error) => {
                    api.discard();
                    record_model_trace_result(trace_model_turn_failure(
                        0,
                        &self.request_id,
                        self.attempt,
                        entered_turn,
                        Some(&api.session),
                        &error,
                        Some(started.elapsed().as_millis()),
                    ));
                    return Err(error);
                }
            };
            trace_model_reply_attempt(
                &reply,
                0,
                &self.request_id,
                self.attempt,
                entered_turn,
                Some(&api.session),
                api.usage_observed,
            );
            return Ok(reply);
        }
        self.history.push_str(prompt);
        let r = call_model_reply_with_attempt(
            &self.history,
            &self.model,
            &self.cfg,
            0,
            &self.request_id,
            self.attempt,
            &self.entered_turn_budget,
        )?;
        self.history.push_str("\n\nAssistant:\n");
        self.history.push_str(&r.text);
        self.history.push_str("\n\nUser:\n");
        Ok(r)
    }

    pub fn session_id(&self) -> Option<&str> {
        #[cfg(unix)]
        if let Some(api) = &self.api {
            return Some(&api.session);
        }
        None
    }

    pub fn lend_to_solo(&mut self) -> Result<()> {
        #[cfg(unix)]
        if self.cfg.sub_llm_cmd == "jcode-api" {
            let mut api = self
                .api
                .take()
                .ok_or_else(|| anyhow!("root subscription session unavailable"))?;
            api.timeout = Duration::from_secs(self.cfg.sub_timeout.min(90));
            let mut slot = SOLO_SHARED_JCODE.lock().unwrap();
            if slot.is_some() {
                bail!("solo subscription session already lent")
            }
            *slot = Some(api);
        }
        Ok(())
    }
}

static MODEL_TRACE_REQUEST_SEQUENCE: AtomicU64 = AtomicU64::new(1);
static MODEL_TRACE_PROCESS_NONCE: OnceLock<u128> = OnceLock::new();

/// Return a process-unique correlation key for one logical model call.
pub fn model_trace_request_id() -> String {
    let nonce = *MODEL_TRACE_PROCESS_NONCE.get_or_init(|| {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_nanos()
    });
    let sequence = MODEL_TRACE_REQUEST_SEQUENCE.fetch_add(1, Ordering::Relaxed);
    format!("{}-{nonce}-{sequence}", std::process::id())
}

pub fn model_transport_error_category(error: &anyhow::Error) -> ModelTransportErrorCategory {
    if error.downcast_ref::<JcodeApiError>().is_some() {
        return ModelTransportErrorCategory::Provider;
    }
    let message = format!("{error:#}").to_ascii_lowercase();
    if message.contains("timed out") || message.contains("timeout") {
        ModelTransportErrorCategory::Timeout
    } else if message.contains("subscription oauth route mismatch")
        || message.contains("unexpected route")
    {
        ModelTransportErrorCategory::SetupRoute
    } else if message.contains("invalid jcode api frame")
        || message.contains("frame exceeds")
        || message.contains("omitted session id")
        || message.contains("request must be object")
    {
        ModelTransportErrorCategory::BridgeProtocol
    } else if message.contains("bridge closed")
        || message.contains("reading jcode api frame")
        || message.contains("failed to start private jcode api bridge")
        || message.contains("bridge exited before readiness")
        || message.contains("bridge did not become ready")
        || message.contains("connection refused")
        || message.contains("broken pipe")
        || message.contains("os error")
    {
        ModelTransportErrorCategory::BridgeIo
    } else {
        ModelTransportErrorCategory::Unknown
    }
}

pub fn model_transport_error_is_transient(error: &anyhow::Error) -> bool {
    if let Some(provider) = error.downcast_ref::<JcodeApiError>() {
        return provider.transient;
    }
    model_transport_error_category(error).is_transient()
}

fn model_setup_error_category(
    error: &anyhow::Error,
    substage: ModelSetupSubstage,
) -> ModelTransportErrorCategory {
    let category = model_transport_error_category(error);
    if category != ModelTransportErrorCategory::Unknown {
        return category;
    }
    match substage {
        ModelSetupSubstage::RuntimeInfo | ModelSetupSubstage::SetModel => {
            ModelTransportErrorCategory::SetupRoute
        }
        _ => ModelTransportErrorCategory::Unknown,
    }
}

fn model_setup_error_is_transient(error: &anyhow::Error, substage: ModelSetupSubstage) -> bool {
    if let Some(provider) = error.downcast_ref::<JcodeApiError>() {
        return provider.transient;
    }
    model_setup_error_category(error, substage).is_transient()
}

fn open_model_trace_sink() -> Result<Option<File>> {
    let Some(path) = env::var_os("AZDAJA_MODEL_TRACE") else {
        return Ok(None);
    };
    let mut options = OpenOptions::new();
    options.create(true).append(true);
    #[cfg(unix)]
    options.mode(0o600);
    let file = options.open(&path)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        if file.metadata()?.permissions().mode() & 0o077 != 0 {
            file.set_permissions(fs::Permissions::from_mode(0o600))?;
        }
    }
    Ok(Some(file))
}

/// Validate and durably synchronize the optional trace sink before provider work begins.
/// A sink which cannot be opened must fail before an entered model turn, never after a
/// valid provider response in a way that could trigger duplicate work.
pub fn preflight_model_trace_sink() -> Result<()> {
    let Some(file) = open_model_trace_sink()? else {
        return Ok(());
    };
    FileExt::lock_exclusive(&file)?;
    let result = file.sync_data();
    let unlock = FileExt::unlock(&file);
    result?;
    unlock?;
    Ok(())
}

fn append_model_trace(row: &ModelTrace) -> Result<()> {
    let mut bytes = serde_json::to_vec(row)?;
    bytes.push(b'\n');
    let Some(mut file) = open_model_trace_sink()? else {
        return Ok(());
    };
    FileExt::lock_exclusive(&file)?;
    let result = (|| -> Result<()> {
        file.write_all(&bytes)?;
        file.sync_data()?;
        Ok(())
    })();
    let unlock = FileExt::unlock(&file);
    result?;
    unlock?;
    Ok(())
}

fn record_model_trace_result(result: Result<()>) {
    if let Err(error) = result {
        eprintln!("azdaja: model trace write failed: {error:#}");
    }
}

fn record_model_trace(row: &ModelTrace) {
    record_model_trace_result(append_model_trace(row));
}

#[derive(Debug, Clone, Copy)]
struct ModelAttemptContext<'a> {
    depth: u32,
    request_id: &'a str,
    attempt: u32,
    entered_turn: Option<u32>,
    session_id: Option<&'a str>,
    latency_ms: Option<u128>,
}

fn trace_model_failure_attempt(
    context: ModelAttemptContext<'_>,
    category: ModelAttemptCategory,
    setup_substage: Option<ModelSetupSubstage>,
    error_category: ModelTransportErrorCategory,
) -> Result<()> {
    append_model_trace(&ModelTrace {
        schema_version: MODEL_TRACE_SCHEMA_VERSION,
        event: ModelTraceEvent::ModelAttempt,
        timestamp_ms: now_ms(),
        depth: context.depth,
        request_id: context.request_id.to_owned(),
        attempt: context.attempt,
        entered_turn: context.entered_turn,
        session_id: context.session_id.map(str::to_owned),
        category,
        outcome: ModelAttemptOutcome::Failed,
        error: Some("provider_call_failed".into()),
        error_category: Some(error_category),
        stage: Some(
            match category {
                ModelAttemptCategory::SessionSetup => "session_setup",
                ModelAttemptCategory::Turn => "turn",
            }
            .into(),
        ),
        setup_substage: setup_substage.map(|value| value.as_str().to_owned()),
        provider: None,
        model: None,
        input_tokens: None,
        output_tokens: None,
        cache_read_tokens: None,
        latency_ms: context.latency_ms,
        degraded_transport: None,
        failed_attempts_before_success: None,
        response: None,
    })
}

fn trace_model_turn_failure(
    depth: u32,
    request_id: &str,
    attempt: u32,
    entered_turn: u32,
    session_id: Option<&str>,
    error: &anyhow::Error,
    latency_ms: Option<u128>,
) -> Result<()> {
    trace_model_failure_attempt(
        ModelAttemptContext {
            depth,
            request_id,
            attempt,
            entered_turn: Some(entered_turn),
            session_id,
            latency_ms,
        },
        ModelAttemptCategory::Turn,
        None,
        model_transport_error_category(error),
    )
}

fn trace_model_setup_failure_attempt(
    depth: u32,
    request_id: &str,
    attempt: u32,
    observation: &JcodeSetupObservation,
    error: &anyhow::Error,
    latency_ms: Option<u128>,
) -> Result<()> {
    trace_model_failure_attempt(
        ModelAttemptContext {
            depth,
            request_id,
            attempt,
            entered_turn: None,
            session_id: observation.session_id.as_deref(),
            latency_ms,
        },
        ModelAttemptCategory::SessionSetup,
        Some(observation.substage),
        model_setup_error_category(error, observation.substage),
    )
}

/// Compatibility entry point for callers which do not manage retries. The emitted
/// v2 row is a single, fail-closed setup attempt with no claimed provider session.
pub fn trace_model_setup_failure(depth: u32, error: &anyhow::Error) -> Result<()> {
    trace_model_setup_failure_attempt(
        depth,
        &model_trace_request_id(),
        1,
        &JcodeSetupObservation::default(),
        error,
        None,
    )
}

fn trace_model_reply_attempt(
    reply: &ModelReply,
    depth: u32,
    request_id: &str,
    attempt: u32,
    entered_turn: u32,
    session_id: Option<&str>,
    usage_observed: bool,
) {
    let known_provider = !reply.provider.trim().is_empty();
    let known_usage = known_provider && usage_observed;
    record_model_trace(&ModelTrace {
        schema_version: MODEL_TRACE_SCHEMA_VERSION,
        event: ModelTraceEvent::ModelAttempt,
        timestamp_ms: now_ms(),
        depth,
        request_id: request_id.to_owned(),
        attempt,
        entered_turn: Some(entered_turn),
        session_id: session_id.map(str::to_owned),
        category: ModelAttemptCategory::Turn,
        outcome: ModelAttemptOutcome::Succeeded,
        error: None,
        error_category: None,
        stage: None,
        setup_substage: None,
        provider: known_provider.then(|| reply.provider.clone()),
        model: known_provider.then(|| reply.model.clone()),
        input_tokens: known_usage.then_some(reply.usage.input),
        output_tokens: known_usage.then_some(reply.usage.output),
        cache_read_tokens: known_usage.then_some(reply.usage.cache_read),
        latency_ms: Some(reply.latency_ms),
        degraded_transport: Some(attempt > 1),
        failed_attempts_before_success: Some(attempt.saturating_sub(1)),
        response: (depth > 0 && env::var("AZDAJA_TRACE_RESPONSES").as_deref() == Ok("1"))
            .then(|| reply.text.clone()),
    });
}

pub fn call_model_reply(prompt: &str, model: &str, cfg: &Config, depth: u32) -> Result<ModelReply> {
    preflight_model_trace_sink()?;
    call_model_reply_with_attempt(
        prompt,
        model,
        cfg,
        depth,
        &model_trace_request_id(),
        1,
        &EnteredTurnBudget::new(1),
    )
}

fn call_model_reply_with_attempt(
    prompt: &str,
    model: &str,
    cfg: &Config,
    depth: u32,
    request_id: &str,
    attempt: u32,
    entered_turn_budget: &EnteredTurnBudget,
) -> Result<ModelReply> {
    let wire = if depth > 0 {
        format!(
            "[azdaja recursion depth {depth}/{}: do not invoke azdaja recursively.]

{prompt}",
            cfg.max_depth
        )
    } else {
        prompt.to_owned()
    };
    if cfg.sub_llm_cmd == "jcode-api" {
        #[cfg(unix)]
        {
            let setup_started = Instant::now();
            let mut observation = JcodeSetupObservation::default();
            let mut api = match JcodeSession::open(cfg, model, &mut observation) {
                Ok(api) => api,
                Err(error) => {
                    record_model_trace_result(trace_model_setup_failure_attempt(
                        depth,
                        request_id,
                        attempt,
                        &observation,
                        &error,
                        Some(setup_started.elapsed().as_millis()),
                    ));
                    return Err(error);
                }
            };
            let entered_turn = entered_turn_budget.try_enter()?;
            let turn_started = Instant::now();
            let reply = match api.turn(&wire) {
                Ok(reply) => reply,
                Err(error) => {
                    record_model_trace_result(trace_model_turn_failure(
                        depth,
                        request_id,
                        attempt,
                        entered_turn,
                        Some(&api.session),
                        &error,
                        Some(turn_started.elapsed().as_millis()),
                    ));
                    return Err(error);
                }
            };
            trace_model_reply_attempt(
                &reply,
                depth,
                request_id,
                attempt,
                entered_turn,
                Some(&api.session),
                api.usage_observed,
            );
            return Ok(reply);
        }
        #[cfg(not(unix))]
        bail!("jcode-api transport requires Unix")
    }
    let entered_turn = entered_turn_budget.try_enter()?;
    let started = Instant::now();
    let text = match call_model_command(&wire, model, cfg, depth) {
        Ok(text) => text,
        Err(error) => {
            record_model_trace_result(trace_model_turn_failure(
                depth,
                request_id,
                attempt,
                entered_turn,
                None,
                &error,
                Some(started.elapsed().as_millis()),
            ));
            return Err(error);
        }
    };
    let reply = ModelReply {
        text,
        usage: ModelUsage::default(),
        provider: String::new(),
        model: model.into(),
        latency_ms: started.elapsed().as_millis(),
    };
    trace_model_reply_attempt(
        &reply,
        depth,
        request_id,
        attempt,
        entered_turn,
        None,
        false,
    );
    Ok(reply)
}
pub fn call_model(prompt: &str, model: &str, cfg: &Config, depth: u32) -> Result<String> {
    Ok(call_model_reply(prompt, model, cfg, depth)?.text)
}
fn call_model_command(prompt: &str, model: &str, cfg: &Config, depth: u32) -> Result<String> {
    let prompt_path = if cfg.sub_llm_cmd.contains("{prompt_file}") {
        let dir = state_home()?.join("prompts");
        secure_dir(&dir)?;
        let nanos = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_nanos();
        let mut made = None;
        for salt in 0..100u8 {
            let path = dir.join(format!("{}-{nanos}-{salt}.txt", std::process::id()));
            if let Ok(mut file) = OpenOptions::new().write(true).create_new(true).open(&path) {
                chmod(&path, 0o600)?;
                file.write_all(prompt.as_bytes())?;
                made = Some(path);
                break;
            }
        }
        Some(made.ok_or_else(|| anyhow!("could not allocate prompt file"))?)
    } else {
        None
    };
    let result = call_model_inner(prompt, prompt_path.as_deref(), model, cfg, depth);
    if let Some(path) = prompt_path {
        let _ = fs::remove_file(path);
    }
    result
}
fn call_model_inner(
    prompt: &str,
    prompt_path: Option<&Path>,
    model: &str,
    cfg: &Config,
    depth: u32,
) -> Result<String> {
    let mut argv =
        shlex::split(&cfg.sub_llm_cmd).ok_or_else(|| anyhow!("invalid sub_llm_cmd quoting"))?;
    let path = prompt_path
        .map(|p| p.to_string_lossy().into_owned())
        .unwrap_or_default();
    for arg in &mut argv {
        *arg = arg
            .replace("{model}", model)
            .replace("{prompt_file}", &path)
    }
    let (program, args) = argv
        .split_first()
        .ok_or_else(|| anyhow!("empty sub_llm_cmd"))?;
    let stdin = if prompt_path.is_some() {
        Stdio::null()
    } else {
        Stdio::piped()
    };
    let mut command = Command::new(program);
    command
        .args(args)
        .env("RLM_DEPTH", depth.to_string())
        .stdin(stdin)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    #[cfg(unix)]
    {
        use std::os::unix::process::CommandExt;
        command.process_group(0);
    }
    let mut child = command
        .spawn()
        .with_context(|| format!("failed to start {program}"))?;
    let out = child.stdout.take().unwrap();
    let err = child.stderr.take().unwrap();
    let out_thread = thread::spawn(move || drain_limited(out, 16 * 1024 * 1024));
    let err_thread = thread::spawn(move || drain_limited(err, 1024 * 1024));
    let input_thread = child.stdin.take().map(|mut input| {
        let bytes = prompt.as_bytes().to_vec();
        thread::spawn(move || input.write_all(&bytes))
    });
    let deadline = Instant::now() + Duration::from_secs(cfg.sub_timeout);
    let mut timed_out = false;
    let status = loop {
        if let Some(status) = child.try_wait()? {
            break status;
        } else if Instant::now() >= deadline {
            timed_out = true;
            #[cfg(unix)]
            unsafe {
                libc::kill(-(child.id() as i32), libc::SIGKILL);
            }
            #[cfg(not(unix))]
            let _ = child.kill();
            break child.wait()?;
        }
        thread::sleep(Duration::from_millis(10));
    };
    let input_result = input_thread
        .map(|t| t.join().map_err(|_| anyhow!("stdin writer panicked")))
        .transpose()?;
    let (stdout, out_over) = out_thread
        .join()
        .map_err(|_| anyhow!("stdout reader panicked"))??;
    let (stderr, err_over) = err_thread
        .join()
        .map_err(|_| anyhow!("stderr reader panicked"))??;
    if timed_out {
        bail!("sub-LLM timed out after {}s", cfg.sub_timeout)
    }
    if let Some(result) = input_result {
        result?
    }
    if out_over || err_over {
        bail!("sub-LLM output exceeded capture limit")
    }
    if !status.success() {
        bail!(
            "sub-LLM exited {status}: {}",
            String::from_utf8_lossy(&stderr).trim()
        )
    }
    let mut text = String::from_utf8_lossy(&strip_ansi_escapes::strip(stdout)).into_owned();
    for pattern in &cfg.clean_patterns {
        text = Regex::new(pattern)?.replace_all(&text, "").into_owned()
    }
    Ok(text.trim().to_owned())
}

fn drain_limited(mut r: impl Read, limit: usize) -> std::io::Result<(Vec<u8>, bool)> {
    let mut kept = Vec::new();
    let mut over = false;
    let mut chunk = [0u8; 8192];
    loop {
        let n = r.read(&mut chunk)?;
        if n == 0 {
            break;
        }
        let room = limit.saturating_sub(kept.len());
        kept.extend_from_slice(&chunk[..n.min(room)]);
        over |= n > room;
    }
    Ok((kept, over))
}

pub fn capability_check(cfg: &Config) -> Result<()> {
    let sid = start(cfg, None)?;
    let result = exec(
        &sid,
        r#"assert re.findall(r"\d+", "a12b") == ["12"]
assert json.loads('{"x": 1}')["x"] == 1
assert datetime.date(2026, 1, 2).isoformat() == "2026-01-02"
"ok""#,
        cfg,
    );
    let _ = kill(&sid);
    let result = result?;
    if !result.success || !result.output.contains("ok") {
        bail!("Monty canary failed: {}", result.output)
    }
    Ok(())
}

#[cfg(all(test, unix))]
mod unit_tests {
    use super::*;

    #[test]
    fn private_bridge_socket_is_short_and_state_specific() {
        let long_a = PathBuf::from("/very/long").join("a".repeat(1_000));
        let long_b = PathBuf::from("/very/long").join("b".repeat(1_000));
        let a = short_runtime_dir(&long_a, 501).join("api.sock");
        let b = short_runtime_dir(&long_b, 501).join("api.sock");
        use std::os::unix::ffi::OsStrExt;
        assert!(a.as_os_str().as_bytes().len() < 100, "{}", a.display());
        assert_ne!(a, b);
        assert!(a.starts_with("/tmp/azdaja-501"));
    }
    #[test]
    fn root_and_batch_timeouts_are_capped_without_changing_config() {
        let mut cfg = Config {
            sub_timeout: 300,
            ..Config::default()
        };
        assert_eq!(jcode_batch_timeout(&cfg, 20_000), Duration::from_secs(90));
        assert_eq!(jcode_batch_timeout(&cfg, 2_000), Duration::from_secs(45));
        assert_eq!(jcode_root_timeout(&cfg), Duration::from_secs(30));
        assert_eq!(cfg.sub_timeout, 300);
        cfg.sub_timeout = 12;
        assert_eq!(jcode_batch_timeout(&cfg, 20_000), Duration::from_secs(12));
        assert_eq!(jcode_batch_timeout(&cfg, 2_000), Duration::from_secs(12));
        assert_eq!(jcode_root_timeout(&cfg), Duration::from_secs(12));
    }

    #[test]
    fn jcode_drop_uses_cleanup_deadline_not_turn_deadline() {
        let (stream, peer) = UnixStream::pair().unwrap();
        let reader = BufReader::new(stream.try_clone().unwrap());
        let server = thread::spawn(move || {
            let mut peer = BufReader::new(peer);
            let mut request = String::new();
            peer.read_line(&mut request).unwrap();
            assert!(request.contains("archive_session"));
            // Keep the socket open without acknowledging the archive. The client's cleanup
            // deadline, rather than EOF, must release Drop.
            request.clear();
            assert_eq!(peer.read_line(&mut request).unwrap(), 0);
        });
        let api = JcodeSession {
            stream,
            reader,
            next_id: 1,
            session: "slow-archive".into(),
            usage: ModelUsage::default(),
            usage_observed: false,
            provider: "OpenAI OAuth".into(),
            model: "mock".into(),
            requested_model: "mock".into(),
            timeout: Duration::from_secs(55),
            cancel_before_archive: false,
        };
        let started = Instant::now();
        drop(api);
        let elapsed = started.elapsed();
        assert!(elapsed < Duration::from_secs(3), "{elapsed:?}");
        server.join().unwrap();
    }

    #[test]
    fn solo_structural_sample_is_bounded_escaped_and_offset_labelled() {
        let text = format!(
            "HEAD\n{}\nTAIL Question: final? Answer:",
            "x".repeat(10_000)
        );
        let sample = structural_sample(&text, text.chars().count()).unwrap();
        assert!(sample.len() <= SOLO_STRUCTURAL_SAMPLE_BYTES);
        assert!(sample.starts_with("[HEAD chars 0.."));
        assert!(sample.contains("[TAIL chars "));
        assert!(sample.contains(r"HEAD\n"));
        assert!(sample.ends_with(r"TAIL Question: final? Answer:"));
        assert!(!sample.contains("xxxxx\nTAIL"));

        let hostile_text = "first\n\"```python\nFINAL('leak')";
        let hostile = structural_sample(hostile_text, hostile_text.chars().count()).unwrap();
        assert!(hostile.contains(r#"first\n\"```python"#));
        assert!(!hostile.contains("first\n\"```python"));

        let multibyte = format!(
            "\u{0085}\u{2028}{}{}\u{2029}",
            "🦀é".repeat(3000),
            "界".repeat(3000)
        );
        let multibyte_sample = structural_sample(&multibyte, multibyte.chars().count()).unwrap();
        assert!(multibyte_sample.len() <= SOLO_STRUCTURAL_SAMPLE_BYTES);
        assert!(multibyte_sample.contains(r"\u0085") || multibyte_sample.contains(r"\u2029"));
        assert!(!multibyte_sample.contains('\u{0085}'));
        assert!(!multibyte_sample.contains('\u{2028}'));
        assert!(!multibyte_sample.contains('\u{2029}'));
    }

    #[test]
    fn entered_turn_budget_is_atomic_and_transport_retry_classes_are_explicit() {
        let budget = Arc::new(EnteredTurnBudget::new(2));
        let successes = AtomicU32::new(0);
        thread::scope(|scope| {
            for _ in 0..16 {
                let budget = Arc::clone(&budget);
                let successes = &successes;
                scope.spawn(move || {
                    if budget.try_enter().is_ok() {
                        successes.fetch_add(1, Ordering::AcqRel);
                    }
                });
            }
        });
        assert_eq!(successes.load(Ordering::Acquire), 2);
        assert_eq!(budget.entered(), 2);
        assert!(!ModelTransportErrorCategory::Provider.is_transient());
        assert!(ModelTransportErrorCategory::Timeout.is_transient());
        assert!(!ModelTransportErrorCategory::SetupRoute.is_transient());
        assert!(!ModelTransportErrorCategory::Unknown.is_transient());
        let untyped = jcode_frame_error(&serde_json::json!({
            "ev":"error", "message":"provider says please retry"
        }));
        assert!(!model_transport_error_is_transient(&untyped));
        assert_eq!(
            model_transport_error_category(&untyped),
            ModelTransportErrorCategory::Provider
        );
        let explicit_transient = jcode_frame_error(&serde_json::json!({
            "ev":"error", "code":"service_unavailable", "message":"try later"
        }));
        assert!(model_transport_error_is_transient(&explicit_transient));
        let typed_permanent = jcode_frame_error(&serde_json::json!({
            "ev":"error", "code":"invalid_request", "message":"bad request"
        }));
        assert!(!model_transport_error_is_transient(&typed_permanent));
        // Keep the original public struct-literal surface source-compatible.
        let _reply = ModelReply {
            text: String::new(),
            usage: ModelUsage::default(),
            provider: String::new(),
            model: String::new(),
            latency_ms: 0,
        };
    }

    #[test]
    fn failed_reload_invalidates_prior_structural_sample() {
        let dir = env::temp_dir().join(format!(
            "azdaja-stale-sample-{}-{}",
            std::process::id(),
            now_ms()
        ));
        fs::create_dir_all(&dir).unwrap();
        let valid = dir.join("valid.txt");
        let invalid = dir.join("invalid.txt");
        fs::write(&valid, "prior valid sample").unwrap();
        fs::write(&invalid, [0xff, 0xfe]).unwrap();
        let cfg = Config::default();
        let mut session = SoloSession::new(&cfg, None).unwrap();
        session.load(&valid, "ctx", &cfg).unwrap();
        assert!(session.structural_sample().unwrap().contains("prior valid"));
        assert!(session.load(&invalid, "ctx", &cfg).is_err());
        assert!(session.structural_sample().is_err());
        fs::remove_dir_all(dir).unwrap();
    }

    #[test]
    fn failed_solo_cell_cannot_publish_final() {
        let cfg = Config::default();
        let mut session = SoloSession::new(&cfg, None).unwrap();
        let result = session.exec("FINAL('wrong')\n1/0", &cfg).unwrap();
        assert!(!result.success && !result.finalized);
        assert!(session.final_answer(&cfg).is_err());
    }
}
