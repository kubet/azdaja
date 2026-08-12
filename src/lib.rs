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
    io::{Read, Write},
    path::{Path, PathBuf},
    process::{Command, Stdio},
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const MONTY_VERSION: &str = "0.0.21";
pub const SKILL: &str = include_str!("../assets/SKILL.md");
pub const DEFAULT_CONFIG: &str = include_str!("../assets/config.toml");
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
}
impl Default for Config {
    fn default() -> Self {
        Self {
        sub_llm_cmd: "jcode run --no-update --quiet --model {model} Read_the_complete_UTF-8_prompt_at_{prompt_file}_and_return_only_its_answer".into(),
        default_model: "claude-haiku-4-5".into(), output_cap:8192, max_depth:1,
        sub_timeout:300, max_sessions:4, cell_timeout:30, idle_timeout:1800,
        clean_patterns:vec![r"(?m)^\[(?:read|write|bash|grep|glob|edit)\].*\n?".into(),r"(?m)^\[Tokens\].*\n?".into(),r"(?m)^\s*→.*\n?".into()],
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
        if self.max_sessions == 0 {
            bail!("max_sessions must be positive")
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
    let model = kw(kwargs, "model").or(args.get(1)).and_then(|o| {
        if let MontyObject::String(s) = o {
            Some(s.clone())
        } else {
            None
        }
    });
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
    let workers = kw(kwargs, "workers")
        .or(args.get(2))
        .and_then(|o| {
            if let MontyObject::Int(n) = o {
                usize::try_from(*n).ok()
            } else {
                None
            }
        })
        .unwrap_or(8)
        .clamp(1, 32);
    Ok((prompts, model, workers))
}
fn external(
    name: &str,
    args: &[MontyObject],
    kwargs: &[(MontyObject, MontyObject)],
    cfg: &Config,
    default_model: &str,
    final_out: &mut Option<Final>,
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
        "llm" | "llm_batch" => {
            let batch = name == "llm_batch";
            let (prompts, model, workers) = parse_call(args, kwargs, batch)?;
            let model = model
                .as_deref()
                .filter(|s| !s.is_empty())
                .unwrap_or(default_model);
            let values = call_many(&prompts, model, workers, cfg)?;
            if batch {
                Ok(MontyObject::List(
                    values.into_iter().map(MontyObject::String).collect(),
                ))
            } else {
                Ok(MontyObject::String(
                    values.into_iter().next().unwrap_or_default(),
                ))
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
    let inputs = ["llm", "llm_batch", "FINAL", "FINAL_VAR"]
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

pub fn exec(sid: &str, code: &str, cfg: &Config) -> Result<ExecResult> {
    let dir = session_dir(sid)?;
    let _guard = lock(&dir)?;
    let meta = read_meta(&dir)?;
    let model = meta.sub_model.as_deref().unwrap_or(&cfg.default_model);
    let repl = load_repl(&dir)?;
    let (mut repl, mut output, success, mut final_out) = run_cell(repl, code, cfg, model);
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
    if let Some(final_value) = final_out {
        let value = match final_value {
            Final::Value(v) => Some(v),
            Final::Var(name) => match repl.feed_run(&name, vec![], PrintWriter::Disabled) {
                Ok(v) => Some(v),
                Err(e) => {
                    output.push_str(&format!("\n{e}"));
                    None
                }
            },
        };
        if let Some(v) = value {
            atomic_write(&dir.join("final"), v.to_string().as_bytes())?;
            finalized = true;
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

pub fn call_many(
    prompts: &[String],
    model: &str,
    workers: usize,
    cfg: &Config,
) -> Result<Vec<String>> {
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
    let slots = std::sync::Mutex::new((0usize, vec![None; prompts.len()]));
    let error = std::sync::Mutex::new(None);
    thread::scope(|scope| {
        for _ in 0..workers.min(prompts.len()) {
            scope.spawn(|| {
                loop {
                    let i = {
                        let mut s = slots.lock().unwrap();
                        if s.0 >= prompts.len() {
                            break;
                        }
                        s.0 += 1;
                        s.0 - 1
                    };
                    match call_model(&prompts[i], model, cfg, depth + 1) {
                        Ok(v) => slots.lock().unwrap().1[i] = Some(v),
                        Err(e) => {
                            *error.lock().unwrap() = Some(e);
                            break;
                        }
                    }
                }
            });
        }
    });
    if let Some(e) = error.into_inner().unwrap() {
        return Err(e);
    }
    Ok(slots
        .into_inner()
        .unwrap()
        .1
        .into_iter()
        .map(Option::unwrap)
        .collect())
}
pub fn call_model(prompt: &str, model: &str, cfg: &Config, depth: u32) -> Result<String> {
    let wire = if depth > 0 {
        format!(
            "[azdaja recursion depth {depth}/{}: do not invoke azdaja recursively.]\n\n{prompt}",
            cfg.max_depth
        )
    } else {
        prompt.to_owned()
    };
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
                file.write_all(wire.as_bytes())?;
                made = Some(path);
                break;
            }
        }
        Some(made.ok_or_else(|| anyhow!("could not allocate prompt file"))?)
    } else {
        None
    };
    let result = call_model_inner(&wire, prompt_path.as_deref(), model, cfg, depth);
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
