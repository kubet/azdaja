use anyhow::{Context, Result, anyhow, bail};
use fs2::FileExt;
use monty::{Dump, MontyRepl, ReplProgress, Session, SessionRef, dump};
use monty_types::{
    CompileOptions, ExcType, MontyException, MontyObject, NameLookupResult, PrintWriter,
    PrintWriterCallback, ResourceLimits, ResourceTracker,
};
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::{
    borrow::Cow,
    collections::{BTreeMap, BTreeSet, HashSet, VecDeque},
    env,
    fs::{self, File, OpenOptions},
    io::{BufRead, BufReader, Read, Seek, SeekFrom, Write},
    path::{Path, PathBuf},
    process::{Command, Stdio},
    sync::{
        Arc, OnceLock,
        atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering},
        mpsc,
    },
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

#[cfg(unix)]
use std::os::unix::{
    fs::OpenOptionsExt,
    io::{AsRawFd, FromRawFd},
    net::UnixStream,
};
#[cfg(windows)]
use std::os::windows::fs::OpenOptionsExt as WindowsOpenOptionsExt;

#[cfg(windows)]
const FILE_FLAG_OPEN_REPARSE_POINT: u32 = 0x0020_0000;
#[cfg(windows)]
const FILE_FLAG_BACKUP_SEMANTICS: u32 = 0x0200_0000;

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const MONTY_VERSION: &str = "0.0.21";
pub const SKILL: &str = include_str!("../assets/SKILL.md");
pub const DEFAULT_CONFIG: &str = include_str!("../assets/config.toml");
pub const SEMANTIC_MANIFEST_PROMPT_ENVELOPE_CHARS: usize = 360_000;
pub const SEMANTIC_MANIFEST_RESPONSE_ENVELOPE_CHARS: usize = 8_192;
pub const MAX_CALLS_PER_CELL: usize = 150;
pub const SEMANTIC_MANIFEST_MAX_CALLS: usize = 16_158;
pub const SEMANTIC_MANIFEST_WORKERS: usize = 8;
pub const SEMANTIC_PER_CALL_P95_SECONDS: u64 = 27;
pub const SEMANTIC_WALL_SAFETY_SECONDS: u64 = 60;
pub const SEMANTIC_MIN_WALL_SECONDS: u64 = 240;

static PROVIDER_INTERRUPTED: AtomicBool = AtomicBool::new(false);
#[cfg(unix)]
static INTERRUPT_SIGNAL: std::sync::atomic::AtomicI32 = std::sync::atomic::AtomicI32::new(0);
#[cfg(unix)]
static INTERRUPT_HANDLER_INSTALL: OnceLock<std::result::Result<(), i32>> = OnceLock::new();

#[cfg(unix)]
extern "C" fn record_interrupt(signal: libc::c_int) {
    // Only async-signal-safe atomics are touched here. Preserve the first signal so the
    // command can return the conventional 128 + signal status after process-tree cleanup.
    let _ = INTERRUPT_SIGNAL.compare_exchange(0, signal, Ordering::SeqCst, Ordering::SeqCst);
}

fn install_provider_interrupt_handler() -> Result<()> {
    #[cfg(unix)]
    {
        let installed = INTERRUPT_HANDLER_INSTALL.get_or_init(|| {
            let mut action: libc::sigaction = unsafe { std::mem::zeroed() };
            action.sa_sigaction = record_interrupt as *const () as usize;
            action.sa_flags = 0;
            unsafe {
                libc::sigemptyset(&mut action.sa_mask);
            }
            for signal in [libc::SIGINT, libc::SIGTERM, libc::SIGHUP] {
                if unsafe { libc::sigaction(signal, &action, std::ptr::null_mut()) } != 0 {
                    return Err(std::io::Error::last_os_error()
                        .raw_os_error()
                        .unwrap_or(libc::EINVAL));
                }
            }
            Ok(())
        });
        if let Err(code) = installed {
            return Err(std::io::Error::from_raw_os_error(*code).into());
        }
    }
    Ok(())
}

pub fn provider_interrupted() -> bool {
    PROVIDER_INTERRUPTED.load(Ordering::SeqCst)
}

/// Conventional shell status for the Unix signal that interrupted provider custody.
///
/// Windows does not expose the POSIX INT/TERM/HUP contract used by this supervisor.
pub fn provider_interrupt_exit_status() -> u8 {
    #[cfg(unix)]
    {
        let signal = INTERRUPT_SIGNAL.load(Ordering::SeqCst);
        u8::try_from(128_i32.saturating_add(signal)).unwrap_or(130)
    }
    #[cfg(not(unix))]
    {
        130
    }
}

fn interrupt_requested() -> bool {
    #[cfg(unix)]
    {
        INTERRUPT_SIGNAL.load(Ordering::SeqCst) != 0
    }
    #[cfg(not(unix))]
    {
        false
    }
}

fn mark_provider_interrupted() {
    PROVIDER_INTERRUPTED.store(true, Ordering::SeqCst);
}

#[cfg(test)]
mod managed_skill_tests {
    use super::{SKILL, VERSION};

    #[test]
    fn frontmatter_and_rendering_preserve_awareness_and_binary_path_custody() {
        let source = SKILL
            .strip_prefix("---\n")
            .expect("skill starts with YAML frontmatter");
        let (frontmatter, _) = source
            .split_once("\n---\n")
            .expect("skill closes YAML frontmatter");
        assert!(frontmatter.lines().any(|line| line == "name: azdaja"));
        let description = frontmatter
            .lines()
            .find_map(|line| line.strip_prefix("description: "))
            .expect("skill frontmatter description");
        for trigger in [
            "complete semantic classification",
            "large file",
            "over 1 MiB",
            "over 200 records",
            "too large for one Read",
            "Azdaja",
            "az virtual-memory tool",
            "installed",
            "available",
            "Invoke before reading or solving natively",
        ] {
            assert!(description.contains(trigger), "missing trigger {trigger:?}");
        }

        let embedded_binary = "'/managed harness/skills/azdaja/azdaja'";
        let rendered = SKILL
            .replace("{{VERSION}}", VERSION)
            .replace("{{BIN}}", embedded_binary);
        assert!(rendered.contains(&format!("# Azdaja {VERSION}")));
        assert!(rendered.contains("## Managed-skill awareness"));
        assert!(rendered.contains("answer **yes**"));
        assert!(rendered.contains("local `az` virtual-memory tool"));
        assert!(rendered.contains("A matching task means invoke this skill now"));
        assert!(rendered.contains("OpenCode must not solve a matching task natively"));
        assert!(rendered.contains("Never claim ignorance of Azdaja"));
        assert!(!rendered.contains("{{VERSION}}"));
        assert!(!rendered.contains("{{BIN}}"));

        let internal_commands = rendered
            .split_once("```bash\n")
            .and_then(|(_, rest)| rest.split_once("\n```").map(|(block, _)| block))
            .expect("skill includes its internal command block");
        assert!(
            !internal_commands
                .lines()
                .any(|line| line.trim_start().starts_with("az "))
        );
        for command in ["start", "load", "exec", "final", "kill"] {
            assert!(
                internal_commands.lines().any(|line| {
                    line.contains(embedded_binary)
                        && line
                            .split(|character: char| {
                                !character.is_ascii_alphanumeric() && character != '-'
                            })
                            .any(|word| word == command)
                }),
                "internal {command} command did not retain the embedded binary path"
            );
        }
    }
}

const PRELUDE: &str = "import os, re, json, math, collections, datetime";

#[derive(Debug)]
struct ConfigFileIssue {
    path: String,
    cause: String,
}

impl std::fmt::Display for ConfigFileIssue {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(formatter, "{}: {}", self.path, self.cause)
    }
}

impl std::error::Error for ConfigFileIssue {}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ConfigErrorReport {
    pub path: String,
    pub cause: String,
}

fn terminal_safe(text: &str) -> String {
    text.chars()
        .flat_map(|character| character.escape_default())
        .take(2048)
        .collect()
}

fn config_path(path: &Path) -> String {
    terminal_safe(&path.to_string_lossy())
}

fn config_issue(path: &Path, cause: impl AsRef<str>) -> anyhow::Error {
    ConfigFileIssue {
        path: config_path(path),
        cause: terminal_safe(cause.as_ref()),
    }
    .into()
}

fn config_read_cause(error: &anyhow::Error) -> String {
    let rendered = format!("{error:#}");
    if rendered.contains("not a regular non-symlink file") {
        return "not a regular non-symlink file".into();
    }
    if let Some(io) = error
        .chain()
        .find_map(|cause| cause.downcast_ref::<std::io::Error>())
    {
        return format!("could not be read: {io}");
    }
    format!("could not be read: {}", error.root_cause())
}

fn config_validation_cause(error: &anyhow::Error) -> String {
    if let Some(regex) = error
        .chain()
        .find_map(|cause| cause.downcast_ref::<regex::Error>())
    {
        let rendered = regex.to_string();
        let terminal = rendered
            .lines()
            .rev()
            .find(|line| !line.trim().is_empty())
            .unwrap_or("invalid regular expression")
            .trim();
        let terminal = terminal
            .strip_prefix("error: ")
            .unwrap_or("invalid regular expression");
        return format!("invalid clean pattern: {terminal}");
    }
    error.root_cause().to_string()
}

fn sanitized_toml_message(message: &str) -> String {
    for prefix in ["invalid type: ", "invalid value: "] {
        if let Some(detail) = message.strip_prefix(prefix)
            && let Some((observed, expected)) = detail.split_once(", expected ")
        {
            let kind = observed.split_ascii_whitespace().next().unwrap_or("value");
            return format!("{prefix}{kind}, expected {expected}");
        }
    }
    if message.starts_with("unknown variant ")
        && let Some((_, expected)) = message.split_once(", expected ")
    {
        return format!("unknown value; expected {expected}");
    }
    message.to_owned()
}

fn toml_position(text: &str, offset: usize) -> (usize, usize) {
    let offset = offset.min(text.len());
    let before = &text.as_bytes()[..offset];
    let line = before.iter().filter(|byte| **byte == b'\n').count() + 1;
    let line_start = before
        .iter()
        .rposition(|byte| *byte == b'\n')
        .map_or(0, |index| index + 1);
    let column = text[line_start..offset].chars().count() + 1;
    (line, column)
}

pub fn config_error_report(error: &anyhow::Error) -> ConfigErrorReport {
    if let Some(issue) = error.downcast_ref::<ConfigFileIssue>() {
        return ConfigErrorReport {
            path: issue.path.clone(),
            cause: issue.cause.clone(),
        };
    }
    ConfigErrorReport {
        path: "configuration source".into(),
        cause: terminal_safe(&error.root_cause().to_string()),
    }
}

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
            cell_timeout: 60,
            idle_timeout: 1800,
            clean_patterns: Vec::new(),
            jcode_provider: "openai".into(),
            jcode_reasoning: "medium".into(),
            max_calls_per_cell: MAX_CALLS_PER_CELL,
        }
    }
}
impl Config {
    pub fn load() -> Result<Self> {
        // Validate both authoritative overrides before any configuration can select a provider.
        // This also makes an invalid AZDAJA_HOME fail closed for stdin-based adapters that do not
        // otherwise need to allocate state before spawning.
        let _ = strict_absolute_override("AZDAJA_HOME")?;
        if let Some(path) = strict_absolute_override("AZDAJA_CONFIG")? {
            return load_config_file(&path)?.ok_or_else(|| config_issue(&path, "file is missing"));
        }

        if let Ok(executable) = env::current_exe()
            && let Some(directory) = executable.parent()
        {
            let standalone = directory.join("azdaja-config.toml");
            if let Some(config) = load_config_file(&standalone)? {
                return Ok(config);
            }

            let marker = directory.join(".azdaja-managed");
            if let Some(bytes) = read_regular_nofollow(&marker)? {
                #[derive(Deserialize)]
                struct ManagedMarker {
                    files: Vec<(String, u64)>,
                }
                let marker: ManagedMarker = serde_json::from_slice(&bytes)
                    .with_context(|| format!("invalid managed marker {}", marker.display()))?;
                let has = |expected: &str| marker.files.iter().any(|(name, _)| name == expected);
                let binary_is_managed = executable
                    .file_name()
                    .and_then(|name| name.to_str())
                    .is_some_and(&has);
                if has("config.toml") && has("SKILL.md") && binary_is_managed {
                    let config_path = directory.join("config.toml");
                    return load_config_file(&config_path)?
                        .ok_or_else(|| config_issue(&config_path, "managed config is missing"));
                }
            }
        }

        if let Some(path) = config_home().map(|p| p.join("azdaja/config.toml"))
            && let Some(config) = load_config_file(&path)?
        {
            return Ok(config);
        }
        Self::default().validate()
    }
    pub fn validate(self) -> Result<Self> {
        if self.sub_llm_cmd.trim().is_empty() {
            bail!("sub_llm_cmd cannot be empty")
        }
        if self.default_model.trim().is_empty() {
            bail!("default_model cannot be empty")
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
        if self.max_calls_per_cell > MAX_CALLS_PER_CELL {
            bail!("max_calls_per_cell cannot exceed {MAX_CALLS_PER_CELL}")
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
fn absolute_home() -> Option<PathBuf> {
    ["HOME", "USERPROFILE"].into_iter().find_map(|name| {
        let path = PathBuf::from(env::var_os(name)?);
        (!path.as_os_str().is_empty() && path.is_absolute()).then_some(path)
    })
}

fn strict_absolute_override_value(name: &str, value: Option<PathBuf>) -> Result<Option<PathBuf>> {
    let Some(path) = value else {
        return Ok(None);
    };
    if path.as_os_str().is_empty() || !path.is_absolute() {
        bail!("{name} must be set to a non-empty absolute path")
    }
    Ok(Some(path))
}

fn strict_absolute_override(name: &str) -> Result<Option<PathBuf>> {
    strict_absolute_override_value(name, env::var_os(name).map(PathBuf::from))
}

fn xdg_absolute(name: &str) -> Option<PathBuf> {
    let path = PathBuf::from(env::var_os(name)?);
    (!path.as_os_str().is_empty() && path.is_absolute()).then_some(path)
}

fn config_home() -> Option<PathBuf> {
    xdg_absolute("XDG_CONFIG_HOME").or_else(|| absolute_home().map(|p| p.join(".config")))
}
fn load_config_file(path: &Path) -> Result<Option<Config>> {
    let Some(bytes) = read_regular_nofollow(path)
        .map_err(|error| config_issue(path, config_read_cause(&error)))?
    else {
        return Ok(None);
    };
    let text = String::from_utf8(bytes).map_err(|_| config_issue(path, "config is not UTF-8"))?;
    let parsed = toml::from_str::<Config>(&text).map_err(|error| {
        let location = error.span().map(|span| toml_position(&text, span.start));
        let message = sanitized_toml_message(error.message());
        let cause = match location {
            Some((line, column)) => {
                format!("TOML error at line {line}, column {column}: {message}")
            }
            None => format!("TOML error: {message}"),
        };
        config_issue(path, cause)
    })?;
    parsed
        .validate()
        .map(Some)
        .map_err(|error| config_issue(path, config_validation_cause(&error)))
}
pub fn state_home() -> Result<PathBuf> {
    let p = strict_absolute_override("AZDAJA_HOME")?
        .or_else(|| xdg_absolute("XDG_STATE_HOME").map(|p| p.join("azdaja")))
        .or_else(|| absolute_home().map(|p| p.join(".local/state/azdaja")))
        .ok_or_else(|| anyhow!("no absolute home directory; set AZDAJA_HOME"))?;
    debug_assert!(p.is_absolute());
    secure_dir(&p)?;
    Ok(p)
}
#[cfg(unix)]
fn metadata_matches(open: &fs::Metadata, path: &fs::Metadata) -> bool {
    use std::os::unix::fs::MetadataExt;
    open.dev() == path.dev() && open.ino() == path.ino()
}
#[cfg(windows)]
fn metadata_matches(open: &fs::Metadata, path: &fs::Metadata) -> bool {
    use std::os::windows::fs::MetadataExt;
    open.volume_serial_number().is_some()
        && open.volume_serial_number() == path.volume_serial_number()
        && open.file_index().is_some()
        && open.file_index() == path.file_index()
}
#[cfg(not(any(unix, windows)))]
fn metadata_matches(_: &fs::Metadata, _: &fs::Metadata) -> bool {
    false
}

#[cfg(unix)]
fn metadata_is_link_or_reparse(metadata: &fs::Metadata) -> bool {
    metadata.file_type().is_symlink()
}
#[cfg(windows)]
fn metadata_is_link_or_reparse(metadata: &fs::Metadata) -> bool {
    use std::os::windows::fs::MetadataExt;
    metadata.file_attributes() & 0x0400 != 0
}
#[cfg(not(any(unix, windows)))]
fn metadata_is_link_or_reparse(_: &fs::Metadata) -> bool {
    true
}

fn bound_metadata(file: &File, path: &Path) -> Result<fs::Metadata> {
    let open = file.metadata()?;
    let current = fs::symlink_metadata(path)
        .with_context(|| format!("path binding changed: {}", path.display()))?;
    if metadata_is_link_or_reparse(&current) || !metadata_matches(&open, &current) {
        bail!("path binding changed: {}", path.display())
    }
    Ok(open)
}

fn open_regular_nofollow(path: &Path, write: bool) -> Result<File> {
    let mut options = OpenOptions::new();
    options.read(true).write(write);
    #[cfg(unix)]
    options.custom_flags(libc::O_NOFOLLOW | libc::O_NONBLOCK | libc::O_CLOEXEC);
    #[cfg(windows)]
    options.custom_flags(FILE_FLAG_OPEN_REPARSE_POINT);
    let file = options
        .open(path)
        .with_context(|| format!("open regular file {}", path.display()))?;
    let metadata = bound_metadata(&file, path)?;
    if !metadata.file_type().is_file() {
        bail!("not a regular file: {}", path.display())
    }
    Ok(file)
}

fn read_regular_nofollow(path: &Path) -> Result<Option<Vec<u8>>> {
    match fs::symlink_metadata(path) {
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(error) => return Err(error.into()),
        Ok(metadata)
            if metadata_is_link_or_reparse(&metadata) || !metadata.file_type().is_file() =>
        {
            bail!("not a regular non-symlink file: {}", path.display())
        }
        Ok(_) => {}
    }
    let mut file = open_regular_nofollow(path, false)?;
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes)?;
    bound_metadata(&file, path)?;
    Ok(Some(bytes))
}

#[cfg(unix)]
fn validate_private_file_identity(file: &File, path: &Path) -> Result<fs::Metadata> {
    use std::os::unix::fs::MetadataExt;
    let metadata = bound_metadata(file, path)?;
    if !metadata.file_type().is_file()
        || metadata.uid() != unsafe { libc::geteuid() }
        || metadata.nlink() != 1
    {
        bail!("unsafe private file: {}", path.display())
    }
    Ok(metadata)
}
#[cfg(windows)]
fn validate_private_file_identity(file: &File, path: &Path) -> Result<fs::Metadata> {
    use std::os::windows::fs::MetadataExt;
    let metadata = bound_metadata(file, path)?;
    if !metadata.file_type().is_file() || metadata.number_of_links() != Some(1) {
        bail!("unsafe private file: {}", path.display())
    }
    Ok(metadata)
}
#[cfg(not(any(unix, windows)))]
fn validate_private_file_identity(_: &File, path: &Path) -> Result<fs::Metadata> {
    bail!(
        "private file validation is unavailable on this platform: {}",
        path.display()
    )
}

#[cfg(unix)]
fn validate_private_file(file: &File, path: &Path) -> Result<fs::Metadata> {
    use std::os::unix::fs::PermissionsExt;
    let metadata = validate_private_file_identity(file, path)?;
    if metadata.permissions().mode() & 0o077 != 0 {
        bail!("unsafe private file mode: {}", path.display())
    }
    Ok(metadata)
}
#[cfg(windows)]
fn validate_private_file(file: &File, path: &Path) -> Result<fs::Metadata> {
    validate_private_file_identity(file, path)
}
#[cfg(not(any(unix, windows)))]
fn validate_private_file(_: &File, path: &Path) -> Result<fs::Metadata> {
    bail!(
        "private file validation is unavailable on this platform: {}",
        path.display()
    )
}

fn open_private_file(path: &Path, write: bool) -> Result<File> {
    let file = open_regular_nofollow(path, write)?;
    validate_private_file(&file, path)?;
    Ok(file)
}

fn create_private_file(path: &Path) -> Result<File> {
    let mut options = OpenOptions::new();
    options.read(true).write(true).create_new(true);
    #[cfg(unix)]
    options
        .mode(0o600)
        .custom_flags(libc::O_NOFOLLOW | libc::O_NONBLOCK | libc::O_CLOEXEC);
    #[cfg(windows)]
    options.custom_flags(FILE_FLAG_OPEN_REPARSE_POINT);
    let file = options.open(path)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let metadata = bound_metadata(&file, path)?;
        use std::os::unix::fs::MetadataExt;
        if !metadata.file_type().is_file()
            || metadata.uid() != unsafe { libc::geteuid() }
            || metadata.nlink() != 1
        {
            bail!("unsafe newly-created private file: {}", path.display())
        }
        file.set_permissions(fs::Permissions::from_mode(0o600))?;
    }
    validate_private_file(&file, path)?;
    Ok(file)
}

fn open_private_directory(path: &Path) -> Result<File> {
    let mut options = OpenOptions::new();
    options.read(true);
    #[cfg(unix)]
    options.custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC);
    #[cfg(windows)]
    options.custom_flags(FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS);
    let file = options
        .open(path)
        .with_context(|| format!("open private directory {}", path.display()))?;
    let metadata = bound_metadata(&file, path)?;
    if !metadata.file_type().is_dir() {
        bail!("not a private directory: {}", path.display())
    }
    #[cfg(unix)]
    {
        use std::os::unix::fs::MetadataExt;
        if metadata.uid() != unsafe { libc::geteuid() } {
            bail!(
                "private directory is not owned by the current user: {}",
                path.display()
            )
        }
    }
    Ok(file)
}

fn validate_private_directory(file: &File, path: &Path) -> Result<()> {
    let metadata = bound_metadata(file, path)?;
    if !metadata.file_type().is_dir() {
        bail!("not a private directory: {}", path.display())
    }
    #[cfg(unix)]
    {
        use std::os::unix::fs::{MetadataExt, PermissionsExt};
        if metadata.uid() != unsafe { libc::geteuid() }
            || metadata.permissions().mode() & 0o777 != 0o700
        {
            bail!("unsafe private directory: {}", path.display())
        }
    }
    Ok(())
}

#[cfg(unix)]
fn chmod(path: &Path, mode: u32) -> Result<()> {
    use std::os::unix::fs::{MetadataExt, PermissionsExt};
    let metadata = fs::symlink_metadata(path)?;
    if metadata.file_type().is_symlink() || metadata.uid() != unsafe { libc::geteuid() } {
        bail!("refusing to chmod unsafe path: {}", path.display())
    }
    let mut options = OpenOptions::new();
    options.read(true);
    if metadata.file_type().is_dir() {
        options.custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC);
    } else {
        options.custom_flags(libc::O_NOFOLLOW | libc::O_NONBLOCK | libc::O_CLOEXEC);
    }
    let file = options.open(path)?;
    let open = bound_metadata(&file, path)?;
    if open.file_type().is_file() && open.nlink() != 1 {
        bail!("refusing to chmod hard-linked path: {}", path.display())
    }
    file.set_permissions(fs::Permissions::from_mode(mode))?;
    bound_metadata(&file, path)?;
    Ok(())
}
#[cfg(not(unix))]
fn chmod(_: &Path, _: u32) -> Result<()> {
    Ok(())
}

fn secure_dir(path: &Path) -> Result<()> {
    fs::create_dir_all(path)?;
    let file = open_private_directory(path)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        file.set_permissions(fs::Permissions::from_mode(0o700))?;
    }
    validate_private_directory(&file, path)
}

fn create_new_private_directory(path: &Path) -> Result<File> {
    #[cfg(unix)]
    {
        use std::os::unix::fs::DirBuilderExt;
        let mut builder = fs::DirBuilder::new();
        builder.mode(0o700);
        builder.create(path)?;
    }
    #[cfg(not(unix))]
    fs::create_dir(path)?;
    let directory = open_private_directory(path)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        directory.set_permissions(fs::Permissions::from_mode(0o700))?;
    }
    validate_private_directory(&directory, path)?;
    Ok(directory)
}

fn cleanup_owned_directory(path: &Path, directory: &File) {
    if validate_private_directory(directory, path).is_ok() {
        let _ = fs::remove_dir_all(path);
    }
}

#[cfg(any(target_os = "linux", target_os = "android"))]
fn rename_noreplace(from: &Path, to: &Path) -> Result<()> {
    use std::ffi::CString;
    use std::os::unix::ffi::OsStrExt;
    let from = CString::new(from.as_os_str().as_bytes())?;
    let to = CString::new(to.as_os_str().as_bytes())?;
    let result = unsafe {
        libc::renameat2(
            libc::AT_FDCWD,
            from.as_ptr(),
            libc::AT_FDCWD,
            to.as_ptr(),
            libc::RENAME_NOREPLACE,
        )
    };
    if result == 0 {
        Ok(())
    } else {
        Err(std::io::Error::last_os_error().into())
    }
}
#[cfg(target_vendor = "apple")]
fn rename_noreplace(from: &Path, to: &Path) -> Result<()> {
    use std::ffi::CString;
    use std::os::unix::ffi::OsStrExt;
    let from = CString::new(from.as_os_str().as_bytes())?;
    let to = CString::new(to.as_os_str().as_bytes())?;
    let result = unsafe {
        libc::renameatx_np(
            libc::AT_FDCWD,
            from.as_ptr(),
            libc::AT_FDCWD,
            to.as_ptr(),
            libc::RENAME_EXCL,
        )
    };
    if result == 0 {
        Ok(())
    } else {
        Err(std::io::Error::last_os_error().into())
    }
}
#[cfg(windows)]
fn rename_noreplace(from: &Path, to: &Path) -> Result<()> {
    fs::rename(from, to)?;
    Ok(())
}
#[cfg(not(any(
    target_os = "linux",
    target_os = "android",
    target_vendor = "apple",
    windows
)))]
fn rename_noreplace(_: &Path, _: &Path) -> Result<()> {
    bail!("atomic no-replace rename is unavailable on this platform")
}

fn remove_bound_file(path: &Path, file: &File) {
    if bound_metadata(file, path).is_ok() {
        let _ = fs::remove_file(path);
    }
}

fn atomic_write(path: &Path, data: &[u8]) -> Result<()> {
    if let Some(parent) = path.parent() {
        let parent = open_private_directory(parent)?;
        validate_private_directory(&parent, path.parent().expect("checked parent"))?;
    }
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    for salt in 0..100u8 {
        let tmp = path.with_extension(format!("tmp-{}-{nonce}-{salt}", std::process::id()));
        let mut file = match create_private_file(&tmp) {
            Ok(file) => file,
            Err(error)
                if error
                    .downcast_ref::<std::io::Error>()
                    .is_some_and(|error| error.kind() == std::io::ErrorKind::AlreadyExists) =>
            {
                continue;
            }
            Err(error) => return Err(error),
        };
        if let Err(error) = file.write_all(data) {
            remove_bound_file(&tmp, &file);
            return Err(error.into());
        }
        validate_private_file(&file, &tmp)?;
        drop(file);
        #[cfg(windows)]
        match fs::symlink_metadata(path) {
            Ok(metadata) if metadata_is_link_or_reparse(&metadata) => {
                let _ = fs::remove_file(&tmp);
                bail!("refusing to replace symlink: {}", path.display())
            }
            Ok(_) => fs::remove_file(path)?,
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
            Err(error) => return Err(error.into()),
        }
        match fs::rename(&tmp, path) {
            Ok(()) => return Ok(()),
            Err(error) => {
                if let Ok(file) = open_private_file(&tmp, false) {
                    remove_bound_file(&tmp, &file);
                }
                return Err(error.into());
            }
        }
    }
    bail!("could not allocate private temporary file")
}
fn valid_sid(s: &str) -> bool {
    s.len() == 16
        && s.bytes()
            .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
}
fn session_dir(sid: &str) -> Result<(PathBuf, File)> {
    if !valid_sid(sid) {
        bail!("invalid session id");
    }
    let path = state_home()?.join(sid);
    let directory =
        open_private_directory(&path).with_context(|| format!("unsafe session path: {sid}"))?;
    validate_private_directory(&directory, &path)?;
    Ok((path, directory))
}
fn open_lock_file(path: &Path) -> Result<File> {
    if let Some(parent) = path.parent() {
        secure_dir(parent)?
    }
    let mut create = OpenOptions::new();
    create.read(true).write(true).create_new(true);
    #[cfg(unix)]
    create
        .mode(0o600)
        .custom_flags(libc::O_NOFOLLOW | libc::O_NONBLOCK | libc::O_CLOEXEC);
    #[cfg(windows)]
    create.custom_flags(FILE_FLAG_OPEN_REPARSE_POINT);
    let file = match create.open(path) {
        Ok(file) => file,
        Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
            open_regular_nofollow(path, true)?
        }
        Err(error) => return Err(error.into()),
    };
    validate_private_file_identity(&file, path)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        file.set_permissions(fs::Permissions::from_mode(0o600))?;
    }
    validate_private_file(&file, path)?;
    Ok(file)
}
fn lock_path(path: &Path) -> Result<File> {
    let file = open_lock_file(path)?;
    FileExt::lock_exclusive(&file)?;
    validate_private_file(&file, path)?;
    Ok(file)
}
fn try_lock_path(path: &Path) -> Result<Option<File>> {
    let file = open_lock_file(path)?;
    match FileExt::try_lock_exclusive(&file) {
        Ok(()) => {
            validate_private_file(&file, path)?;
            Ok(Some(file))
        }
        Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => Ok(None),
        Err(error) => Err(error.into()),
    }
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
    let path = dir.join("state.monty");
    let file = open_private_file(&path, false)?;
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
    let path = dir.join("meta.json");
    let mut file = open_private_file(&path, false)?;
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes)?;
    validate_private_file(&file, &path)?;
    Ok(serde_json::from_slice(&bytes)?)
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
        let entry_path = e.path();
        let Ok(directory) = open_private_directory(&entry_path) else {
            continue;
        };
        if validate_private_directory(&directory, &entry_path).is_err()
            || !cutoff.is_some_and(|c| e.metadata().and_then(|m| m.modified()).is_ok_and(|t| t < c))
        {
            continue;
        }
        let lock_path = base.join("locks").join(&name).with_extension("lock");
        let Ok(Some(_lockfile)) = try_lock_path(&lock_path) else {
            continue;
        };
        if cutoff.is_some_and(|c| e.metadata().and_then(|m| m.modified()).is_ok_and(|t| t < c))
            && validate_private_directory(&directory, &entry_path).is_ok()
        {
            let _ = fs::remove_dir_all(entry_path);
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
        let stage_directory = match create_new_private_directory(&stage) {
            Ok(directory) => directory,
            Err(error)
                if error
                    .downcast_ref::<std::io::Error>()
                    .is_some_and(|error| error.kind() == std::io::ErrorKind::AlreadyExists) =>
            {
                continue;
            }
            Err(error) => return Err(error),
        };
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
        if let Err(error) = setup {
            cleanup_owned_directory(&stage, &stage_directory);
            return Err(error);
        }
        validate_private_directory(&stage_directory, &stage)?;
        match rename_noreplace(&stage, &dir) {
            Ok(()) => return Ok(id),
            Err(error)
                if error
                    .downcast_ref::<std::io::Error>()
                    .is_some_and(|error| error.kind() == std::io::ErrorKind::AlreadyExists) =>
            {
                cleanup_owned_directory(&stage, &stage_directory);
            }
            Err(error) => {
                cleanup_owned_directory(&stage, &stage_directory);
                return Err(error);
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

fn sha256_hex(bytes: &[u8]) -> String {
    const K: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4,
        0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe,
        0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f,
        0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
        0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116,
        0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
        0xc67178f2,
    ];
    let mut state = [
        0x6a09e667u32,
        0xbb67ae85,
        0x3c6ef372,
        0xa54ff53a,
        0x510e527f,
        0x9b05688c,
        0x1f83d9ab,
        0x5be0cd19,
    ];
    let bit_length = (bytes.len() as u64).wrapping_mul(8);
    let mut padded = Vec::with_capacity((bytes.len() + 72) & !63);
    padded.extend_from_slice(bytes);
    padded.push(0x80);
    while padded.len() % 64 != 56 {
        padded.push(0);
    }
    padded.extend_from_slice(&bit_length.to_be_bytes());
    for chunk in padded.chunks_exact(64) {
        let mut words = [0u32; 64];
        for (index, word) in words[..16].iter_mut().enumerate() {
            *word = u32::from_be_bytes(chunk[index * 4..index * 4 + 4].try_into().unwrap());
        }
        for index in 16..64 {
            let s0 = words[index - 15].rotate_right(7)
                ^ words[index - 15].rotate_right(18)
                ^ (words[index - 15] >> 3);
            let s1 = words[index - 2].rotate_right(17)
                ^ words[index - 2].rotate_right(19)
                ^ (words[index - 2] >> 10);
            words[index] = words[index - 16]
                .wrapping_add(s0)
                .wrapping_add(words[index - 7])
                .wrapping_add(s1);
        }
        let [mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut h] = state;
        for index in 0..64 {
            let sum1 = e.rotate_right(6) ^ e.rotate_right(11) ^ e.rotate_right(25);
            let choose = (e & f) ^ ((!e) & g);
            let temp1 = h
                .wrapping_add(sum1)
                .wrapping_add(choose)
                .wrapping_add(K[index])
                .wrapping_add(words[index]);
            let sum0 = a.rotate_right(2) ^ a.rotate_right(13) ^ a.rotate_right(22);
            let majority = (a & b) ^ (a & c) ^ (b & c);
            let temp2 = sum0.wrapping_add(majority);
            h = g;
            g = f;
            f = e;
            e = d.wrapping_add(temp1);
            d = c;
            c = b;
            b = a;
            a = temp1.wrapping_add(temp2);
        }
        for (value, addition) in state.iter_mut().zip([a, b, c, d, e, f, g, h]) {
            *value = value.wrapping_add(addition);
        }
    }
    let mut out = String::with_capacity(64);
    for word in state {
        out.push_str(&format!("{word:08x}"));
    }
    out
}

const CLAUDE_HOOK_LARGE_BYTES: u64 = 1_000_000;
const CLAUDE_HOOK_SAMPLE_BYTES: usize = 64 * 1024;
const CLAUDE_HOOK_MARKER: &[u8] = b"azdaja-claude-hook-v1\n";

fn claude_hook_paths(root: &Path, session_id: &str) -> (PathBuf, PathBuf, PathBuf, PathBuf) {
    let stem = sha256_hex(session_id.as_bytes());
    (
        root.join(format!("{stem}.coverage")),
        root.join(format!("{stem}.active")),
        root.join(format!("{stem}.sample")),
        root.join(format!("{stem}.transaction")),
    )
}

fn claude_hook_marker_present(path: &Path) -> Result<bool> {
    match fs::symlink_metadata(path) {
        Ok(metadata) => {
            if !metadata.file_type().is_file() {
                bail!("unsafe Claude hook marker: {}", path.display())
            }
            let mut file = open_private_file(path, false)?;
            let mut bytes = Vec::new();
            file.read_to_end(&mut bytes)?;
            if bytes != CLAUDE_HOOK_MARKER {
                bail!("invalid Claude hook marker: {}", path.display())
            }
            Ok(true)
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(false),
        Err(error) => Err(error.into()),
    }
}

fn claude_hook_write_marker(path: &Path) -> Result<()> {
    atomic_write(path, CLAUDE_HOOK_MARKER)
}

fn claude_hook_claim_sample(path: &Path) -> Result<bool> {
    let mut options = OpenOptions::new();
    options.write(true).create_new(true);
    #[cfg(unix)]
    options.mode(0o600).custom_flags(libc::O_NOFOLLOW);
    #[cfg(windows)]
    options.custom_flags(FILE_FLAG_OPEN_REPARSE_POINT);
    let mut file = match options.open(path) {
        Ok(file) => file,
        Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
            claude_hook_marker_present(path)?;
            return Ok(false);
        }
        Err(error) => return Err(error.into()),
    };
    if let Err(error) = file
        .write_all(CLAUDE_HOOK_MARKER)
        .and_then(|()| file.sync_all())
    {
        let _ = fs::remove_file(path);
        return Err(error.into());
    }
    Ok(true)
}

fn claude_hook_remove_marker(path: &Path) -> Result<()> {
    match fs::remove_file(path) {
        Ok(()) => Ok(()),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error.into()),
    }
}

fn claude_hook_coverage_prompt(prompt: &str) -> bool {
    let lower = prompt.to_lowercase();
    let bounded_substep = [
        "only the first",
        "only first",
        "only the last",
        "only last",
        "small excerpt",
        "bounded excerpt",
        "sample of",
    ]
    .iter()
    .any(|needle| lower.contains(needle));
    let words = lower
        .split(|character: char| !character.is_alphanumeric())
        .filter(|word| !word.is_empty())
        .collect::<HashSet<_>>();
    let data_noun = [
        "row",
        "rows",
        "record",
        "records",
        "line",
        "lines",
        "entry",
        "entries",
        "observation",
        "observations",
        "value",
        "values",
        "file",
        "files",
        "input",
        "inputs",
        "dataset",
        "datasets",
        "log",
        "logs",
        "event",
        "events",
        "item",
        "items",
    ]
    .iter()
    .any(|word| words.contains(word));
    let coverage_quantifier = ["all", "every", "full", "complete", "whole", "entire"]
        .iter()
        .any(|word| words.contains(word));
    let explicit_coverage = ["complete coverage", "machine-graded", "clean dataset"]
        .iter()
        .any(|needle| lower.contains(needle))
        || words.contains("aggregate")
        || (coverage_quantifier && data_noun);
    let strong_reduction = [
        "count",
        "total",
        "number",
        "maximum",
        "minimum",
        "max",
        "min",
        "highest",
        "lowest",
        "earliest",
        "latest",
        "unique",
        "distinct",
        "sum",
        "average",
        "median",
        "frequency",
        "distribution",
    ]
    .iter()
    .any(|word| words.contains(word))
        || lower.contains("how many");
    let positional_reduction = ["first", "last"].iter().any(|word| words.contains(word));
    let whole_input_digest =
        words.contains("checksum") || words.contains("sha256") || lower.contains("sha-256");
    let complete_intent =
        explicit_coverage || (strong_reduction && data_noun) || whole_input_digest;
    complete_intent || (!bounded_substep && positional_reduction && data_noun)
}

fn claude_hook_path_is_large(path: &Path, remaining: &mut usize, depth: usize) -> Result<bool> {
    let mut total = 0u64;
    claude_hook_path_is_large_inner(path, remaining, depth, &mut total)
}

fn claude_hook_path_is_large_inner(
    path: &Path,
    remaining: &mut usize,
    depth: usize,
    total: &mut u64,
) -> Result<bool> {
    if *remaining == 0 || depth > 12 {
        return Ok(true);
    }
    *remaining -= 1;
    let metadata = match fs::symlink_metadata(path) {
        Ok(metadata) => metadata,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false),
        Err(_) => return Ok(true),
    };
    if metadata.file_type().is_symlink() {
        let target = match fs::metadata(path) {
            Ok(target) => target,
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false),
            Err(_) => return Ok(true),
        };
        if target.file_type().is_file() {
            *total = total.saturating_add(target.len());
            return Ok(*total > CLAUDE_HOOK_LARGE_BYTES);
        }
        return Ok(true);
    }
    if metadata.file_type().is_file() {
        *total = total.saturating_add(metadata.len());
        return Ok(*total > CLAUDE_HOOK_LARGE_BYTES);
    }
    if !metadata.file_type().is_dir() {
        return Ok(true);
    }
    let entries = match fs::read_dir(path) {
        Ok(entries) => entries,
        Err(_) => return Ok(true),
    };
    for entry in entries {
        if *remaining == 0 {
            return Ok(true);
        }
        let entry = match entry {
            Ok(entry) => entry,
            Err(_) => return Ok(true),
        };
        if claude_hook_path_is_large_inner(&entry.path(), remaining, depth + 1, total)? {
            return Ok(true);
        }
    }
    Ok(*total > CLAUDE_HOOK_LARGE_BYTES)
}

fn claude_hook_resolve(cwd: &Path, raw: &str) -> PathBuf {
    let path = PathBuf::from(raw);
    if path.is_absolute() {
        path
    } else {
        cwd.join(path)
    }
}

fn claude_hook_path_or_scope_is_large(path: &Path, cwd: &Path) -> Result<bool> {
    let path_within_cwd = fs::canonicalize(path)
        .ok()
        .zip(fs::canonicalize(cwd).ok())
        .is_some_and(|(path, cwd)| path.starts_with(cwd));
    if !path_within_cwd {
        return Ok(true);
    }
    for candidate in [Some(path), Some(cwd), path.parent()].into_iter().flatten() {
        let mut budget = 10_000usize;
        if claude_hook_path_is_large(candidate, &mut budget, 0)? {
            return Ok(true);
        }
    }
    Ok(false)
}

fn claude_hook_find_large_basename(
    path: &Path,
    basename: &str,
    remaining: &mut usize,
    depth: usize,
) -> Result<bool> {
    if *remaining == 0 || depth > 12 {
        return Ok(true);
    }
    *remaining -= 1;
    let metadata = match fs::symlink_metadata(path) {
        Ok(metadata) => metadata,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false),
        Err(_) => return Ok(true),
    };
    if metadata.file_type().is_symlink() {
        if path.file_name().and_then(|name| name.to_str()) != Some(basename) {
            return Ok(false);
        }
        let target = match fs::metadata(path) {
            Ok(target) => target,
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false),
            Err(_) => return Ok(true),
        };
        return Ok(
            (target.file_type().is_file() && target.len() > CLAUDE_HOOK_LARGE_BYTES)
                || !target.file_type().is_file(),
        );
    }
    if metadata.file_type().is_file() {
        return Ok(metadata.len() > CLAUDE_HOOK_LARGE_BYTES
            && path.file_name().and_then(|name| name.to_str()) == Some(basename));
    }
    if !metadata.file_type().is_dir() {
        return Ok(true);
    }
    let entries = match fs::read_dir(path) {
        Ok(entries) => entries,
        Err(_) => return Ok(true),
    };
    for entry in entries {
        if *remaining == 0 {
            return Ok(true);
        }
        let entry = match entry {
            Ok(entry) => entry,
            Err(_) => return Ok(true),
        };
        if claude_hook_find_large_basename(&entry.path(), basename, remaining, depth + 1)? {
            return Ok(true);
        }
    }
    Ok(false)
}

fn claude_hook_has_shell_expansion(value: &str) -> bool {
    value.chars().any(|character| {
        matches!(
            character,
            '$' | '~' | '{' | '}' | '*' | '?' | '[' | ']' | '!'
        )
    })
}

fn claude_hook_literal_path_operand(value: &str) -> bool {
    !value.is_empty()
        && !value.starts_with('-')
        && !claude_hook_has_shell_expansion(value)
        && !value.contains(['\n', '\r', '\0'])
}

fn claude_hook_trusted_system_program(token: &str, expected: &str) -> bool {
    token == format!("/usr/bin/{expected}") || token == format!("/bin/{expected}")
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ClaudeHookBashAccess {
    None,
    Sample,
    Broad,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct ClaudeHookSample {
    program: String,
    count: usize,
    path: String,
}

fn claude_hook_bounded_sample(command: &str) -> Option<Vec<ClaudeHookSample>> {
    if command.contains("$(")
        || command.contains('`')
        || command.contains('<')
        || command.contains('>')
        || command.contains('|')
        || command.contains('&')
    {
        return None;
    }
    let mut total = 0usize;
    let mut samples = Vec::new();
    for segment in command.split([';', '\n']) {
        let segment = segment.trim();
        if segment.is_empty() {
            continue;
        }
        let tokens = shlex::split(segment)?;
        let program_token = tokens.first()?;
        let program = Path::new(program_token)
            .file_name()
            .and_then(|name| name.to_str())
            .unwrap_or(program_token)
            .to_ascii_lowercase();
        if !matches!(program.as_str(), "head" | "tail")
            || !claude_hook_trusted_system_program(program_token, &program)
        {
            return None;
        }
        let mut count = 10usize;
        let mut operands = Vec::new();
        let mut index = 1usize;
        let mut options_done = false;
        while index < tokens.len() {
            let token = &tokens[index];
            if !options_done && token == "--" {
                options_done = true;
                index += 1;
                continue;
            }
            if !options_done && matches!(token.as_str(), "-n" | "--lines") {
                let value = tokens.get(index + 1)?;
                if value.is_empty() || !value.bytes().all(|byte| byte.is_ascii_digit()) {
                    return None;
                }
                count = value.parse().ok()?;
                index += 2;
                continue;
            }
            if !options_done {
                if let Some(value) = token.strip_prefix("--lines=") {
                    if value.is_empty() || !value.bytes().all(|byte| byte.is_ascii_digit()) {
                        return None;
                    }
                    count = value.parse().ok()?;
                    index += 1;
                    continue;
                }
                if let Some(value) = token.strip_prefix('-') {
                    if value.is_empty() || !value.bytes().all(|byte| byte.is_ascii_digit()) {
                        return None;
                    }
                    count = value.parse().ok()?;
                    index += 1;
                    continue;
                }
            }
            options_done = true;
            operands.push(token.clone());
            index += 1;
        }
        if operands.len() != 1 || !claude_hook_literal_path_operand(&operands[0]) {
            return None;
        }
        total = total.checked_add(count)?;
        if total > 10 {
            return None;
        }
        samples.push(ClaudeHookSample {
            program,
            count,
            path: operands.remove(0),
        });
    }
    if samples.is_empty() {
        None
    } else {
        Some(samples)
    }
}

fn claude_hook_open_sample_file(path: &Path) -> Option<File> {
    let mut options = OpenOptions::new();
    options.read(true);
    #[cfg(unix)]
    options.custom_flags(libc::O_NOFOLLOW | libc::O_NONBLOCK);
    #[cfg(windows)]
    options.custom_flags(FILE_FLAG_OPEN_REPARSE_POINT);
    let file = options.open(path).ok()?;
    file.metadata().ok()?.is_file().then_some(file)
}

fn claude_hook_head_sample_bytes(path: &Path, count: usize, limit: usize) -> Result<Option<usize>> {
    if count == 0 {
        return Ok(Some(0));
    }
    let Some(file) = claude_hook_open_sample_file(path) else {
        return Ok(None);
    };
    let mut bytes = Vec::new();
    file.take((limit + 1) as u64).read_to_end(&mut bytes)?;
    let mut lines = 0usize;
    for (index, byte) in bytes.iter().enumerate() {
        if *byte == b'\n' {
            lines += 1;
            if lines == count {
                return Ok((index < limit).then_some(index + 1));
            }
        }
    }
    if bytes.len() <= limit {
        Ok(Some(bytes.len()))
    } else {
        Ok(None)
    }
}

fn claude_hook_tail_sample_bytes(path: &Path, count: usize, limit: usize) -> Result<Option<usize>> {
    if count == 0 {
        return Ok(Some(0));
    }
    let Some(mut file) = claude_hook_open_sample_file(path) else {
        return Ok(None);
    };
    let metadata = file.metadata()?;
    let size = metadata.len();
    if size <= limit as u64 {
        return Ok(Some(size as usize));
    }
    let window = (limit + 1) as u64;
    file.seek(SeekFrom::End(-(window as i64)))?;
    let mut bytes = Vec::with_capacity(window as usize);
    file.take(window).read_to_end(&mut bytes)?;
    let search_end = if bytes.last() == Some(&b'\n') {
        bytes.len().saturating_sub(1)
    } else {
        bytes.len()
    };
    let mut lines = 0usize;
    for index in (0..search_end).rev() {
        if bytes[index] == b'\n' {
            lines += 1;
            if lines == count {
                let output = bytes.len() - index - 1;
                return Ok((output <= limit).then_some(output));
            }
        }
    }
    Ok(None)
}

fn claude_hook_is_line_text(path: &Path) -> bool {
    let rejected_extension = path
        .extension()
        .and_then(|extension| extension.to_str())
        .is_some_and(|extension| {
            matches!(
                extension.to_ascii_lowercase().as_str(),
                "pdf"
                    | "ipynb"
                    | "png"
                    | "jpg"
                    | "jpeg"
                    | "gif"
                    | "webp"
                    | "bmp"
                    | "ico"
                    | "tif"
                    | "tiff"
                    | "zip"
                    | "gz"
                    | "bz2"
                    | "xz"
                    | "7z"
                    | "tar"
                    | "doc"
                    | "docx"
                    | "xls"
                    | "xlsx"
                    | "ppt"
                    | "pptx"
                    | "parquet"
                    | "arrow"
                    | "sqlite"
                    | "db"
                    | "wasm"
            )
        });
    if rejected_extension {
        return false;
    }
    let Some(file) = claude_hook_open_sample_file(path) else {
        return false;
    };
    let mut prefix = Vec::new();
    if file.take(8 * 1024).read_to_end(&mut prefix).is_err()
        || prefix.contains(&0)
        || std::str::from_utf8(&prefix).is_err()
    {
        return false;
    }
    !prefix.starts_with(b"%PDF-")
        && !prefix.starts_with(b"\x89PNG\r\n\x1a\n")
        && !prefix.starts_with(b"GIF87a")
        && !prefix.starts_with(b"GIF89a")
        && !prefix.starts_with(b"RIFF")
        && !prefix.starts_with(b"PK\x03\x04")
}

fn claude_hook_samples_are_byte_bounded(samples: &[ClaudeHookSample], cwd: &Path) -> Result<bool> {
    let mut remaining = CLAUDE_HOOK_SAMPLE_BYTES;
    for sample in samples {
        let path = claude_hook_resolve(cwd, &sample.path);
        let bytes = match sample.program.as_str() {
            "head" => claude_hook_head_sample_bytes(&path, sample.count, remaining)?,
            "tail" => claude_hook_tail_sample_bytes(&path, sample.count, remaining)?,
            _ => None,
        };
        let Some(bytes) = bytes else {
            return Ok(false);
        };
        remaining = remaining.saturating_sub(bytes);
    }
    Ok(true)
}

fn claude_hook_bash_metadata_only(command: &str) -> bool {
    if command.contains("$(")
        || command.contains('`')
        || command.contains('<')
        || command.contains('>')
        || command.contains('|')
        || command.contains('&')
    {
        return false;
    }
    let mut commands = 0usize;
    for segment in command.split([';', '\n']) {
        let segment = segment.trim();
        if segment.is_empty() {
            continue;
        }
        commands += 1;
        let Some(tokens) = shlex::split(segment) else {
            return false;
        };
        let Some(program_token) = tokens.first() else {
            return false;
        };
        let program = Path::new(program_token)
            .file_name()
            .and_then(|name| name.to_str())
            .unwrap_or(program_token)
            .to_ascii_lowercase();
        if !claude_hook_trusted_system_program(program_token, &program) {
            return false;
        }
        let arguments = &tokens[1..];
        if arguments
            .iter()
            .any(|argument| claude_hook_has_shell_expansion(argument))
        {
            return false;
        }
        let safe = match program.as_str() {
            "pwd" | "true" => arguments.is_empty(),
            "wc" => {
                let mut operands = Vec::new();
                let options_safe = arguments.iter().all(|argument| {
                    if matches!(
                        argument.as_str(),
                        "-l" | "-c"
                            | "-w"
                            | "-m"
                            | "--lines"
                            | "--bytes"
                            | "--words"
                            | "--chars"
                            | "--"
                    ) {
                        true
                    } else if argument.starts_with('-') {
                        false
                    } else {
                        operands.push(argument);
                        operands.len() <= 1
                    }
                });
                options_safe && operands.len() == 1 && claude_hook_literal_path_operand(operands[0])
            }
            "stat" | "file" => {
                arguments.len() == 1 && claude_hook_literal_path_operand(&arguments[0])
            }
            "du" => {
                let mut operands = Vec::new();
                let options_safe = arguments.iter().all(|argument| {
                    if matches!(argument.as_str(), "-h" | "-s" | "-sh" | "-hs" | "--") {
                        true
                    } else if argument.starts_with('-') {
                        false
                    } else {
                        operands.push(argument);
                        operands.len() <= 1
                    }
                });
                options_safe && operands.len() == 1 && claude_hook_literal_path_operand(operands[0])
            }
            "ls" => {
                let mut operands = Vec::new();
                let options_safe = arguments.iter().all(|argument| {
                    if matches!(
                        argument.as_str(),
                        "-l" | "-a" | "-la" | "-al" | "-d" | "-ld" | "-dl" | "--"
                    ) {
                        true
                    } else if argument.starts_with('-') {
                        false
                    } else {
                        operands.push(argument);
                        operands.len() <= 1
                    }
                });
                options_safe
                    && operands
                        .first()
                        .is_none_or(|operand| claude_hook_literal_path_operand(operand))
            }
            _ => false,
        };
        if !safe {
            return false;
        }
    }
    commands > 0
}

fn claude_hook_argument_is_large(raw: &str, cwd: &Path) -> Result<bool> {
    let raw = raw.trim_matches(|character: char| matches!(character, ';' | ',' | '(' | ')'));
    if raw.is_empty() {
        return Ok(false);
    }
    if claude_hook_has_shell_expansion(raw) {
        return Ok(true);
    }
    if raw.starts_with('-') {
        return Ok(false);
    }
    let path = claude_hook_resolve(cwd, raw);
    if claude_hook_path_or_scope_is_large(&path, cwd)? {
        return Ok(true);
    }
    if !raw.contains('/') {
        let mut budget = 10_000usize;
        return claude_hook_find_large_basename(cwd, raw, &mut budget, 0);
    }
    Ok(false)
}

fn claude_hook_bash_access(command: &str, cwd: &Path) -> Result<ClaudeHookBashAccess> {
    if claude_hook_bash_metadata_only(command) {
        return Ok(ClaudeHookBashAccess::None);
    }
    if let Some(samples) = claude_hook_bounded_sample(command) {
        let mut samples_large = false;
        for sample in &samples {
            if claude_hook_argument_is_large(&sample.path, cwd)? {
                samples_large = true;
            }
        }
        if samples_large {
            return if claude_hook_samples_are_byte_bounded(&samples, cwd)? {
                Ok(ClaudeHookBashAccess::Sample)
            } else {
                Ok(ClaudeHookBashAccess::Broad)
            };
        }
        return Ok(ClaudeHookBashAccess::None);
    }
    Ok(ClaudeHookBashAccess::Broad)
}

fn claude_hook_denial() -> String {
    serde_json::json!({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Azdaja is required before broad access to this large input. Call the Skill tool with azdaja, then retry through its managed binary."
        }
    })
    .to_string()
}

fn claude_hook_lifecycle_denial() -> String {
    serde_json::json!({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "After Azdaja activation, use exactly one managed Bash transaction containing start/load/exec/final/kill. Do not inspect, stage, validate, or retry with another tool."
        }
    })
    .to_string()
}

fn claude_hook_is_managed_transaction(command: &str) -> bool {
    [
        "set -euo pipefail",
        "sid=",
        "cleanup()",
        "trap cleanup EXIT",
        " start",
        " load",
        " exec",
        " final",
        " kill",
        "cat <<",
        "FINAL(",
    ]
    .iter()
    .all(|part| command.contains(part))
        && !Regex::new(r"(?i)\bsolo\b").unwrap().is_match(command)
        && (command.contains("/azdaja") || command.contains("$AZ"))
}

fn claude_hook_with_root(input: &str, root: &Path) -> Result<Option<String>> {
    let event: serde_json::Value =
        serde_json::from_str(input).context("invalid Claude hook JSON")?;
    let session_id = event
        .get("session_id")
        .and_then(serde_json::Value::as_str)
        .ok_or_else(|| anyhow!("Claude hook input lacks session_id"))?;
    secure_dir(root)?;
    let (coverage, active, sample, transaction) = claude_hook_paths(root, session_id);
    match event
        .get("hook_event_name")
        .and_then(serde_json::Value::as_str)
        .unwrap_or_default()
    {
        "UserPromptSubmit"
            if event
                .get("user_prompt")
                .or_else(|| event.get("prompt"))
                .and_then(serde_json::Value::as_str)
                .is_some_and(claude_hook_coverage_prompt) =>
        {
            for path in [&coverage, &active, &sample, &transaction] {
                claude_hook_remove_marker(path)?;
            }
            claude_hook_write_marker(&coverage)?;
        }
        "UserPromptSubmit" => {
            for path in [&coverage, &active, &sample, &transaction] {
                claude_hook_remove_marker(path)?;
            }
        }
        "PostToolUse" => {
            let skill = event
                .get("tool_input")
                .and_then(|input| input.get("skill").or_else(|| input.get("name")))
                .and_then(serde_json::Value::as_str);
            if event.get("tool_name").and_then(serde_json::Value::as_str) == Some("Skill")
                && skill == Some("azdaja")
            {
                // Activation is idempotent: a repeated delivery must never reopen
                // an already claimed one-transaction lease.
                claude_hook_write_marker(&active)?;
            }
        }
        "PreToolUse" => {
            if !claude_hook_marker_present(&coverage)? {
                return Ok(None);
            }
            let tool = event
                .get("tool_name")
                .and_then(serde_json::Value::as_str)
                .unwrap_or_default();
            let tool_input = event.get("tool_input").unwrap_or(&serde_json::Value::Null);
            if claude_hook_marker_present(&active)? {
                if tool == "StructuredOutput" {
                    return Ok(None);
                }
                if tool == "Bash" {
                    let command = tool_input
                        .get("command")
                        .and_then(serde_json::Value::as_str)
                        .unwrap_or_default();
                    if claude_hook_is_managed_transaction(command)
                        && claude_hook_claim_sample(&transaction)?
                    {
                        return Ok(None);
                    }
                }
                return Ok(Some(claude_hook_lifecycle_denial()));
            }
            let cwd = event
                .get("cwd")
                .and_then(serde_json::Value::as_str)
                .map(PathBuf::from)
                .unwrap_or_else(|| PathBuf::from("."));
            let access = match tool {
                "Read" => {
                    let object = tool_input.as_object();
                    let path = tool_input
                        .get("file_path")
                        .or_else(|| tool_input.get("path"))
                        .and_then(serde_json::Value::as_str);
                    let fields_safe = object.is_some_and(|object| {
                        object.keys().all(|key| {
                            matches!(key.as_str(), "file_path" | "path" | "offset" | "limit")
                        }) && !(object.contains_key("file_path") && object.contains_key("path"))
                    });
                    if let Some(path) = path {
                        if claude_hook_has_shell_expansion(path) {
                            ClaudeHookBashAccess::Broad
                        } else {
                            let resolved = claude_hook_resolve(&cwd, path);
                            if claude_hook_path_or_scope_is_large(&resolved, &cwd)? {
                                let limit =
                                    tool_input.get("limit").and_then(serde_json::Value::as_u64);
                                let offset_safe = match tool_input.get("offset") {
                                    None => true,
                                    Some(offset) => offset.as_u64() == Some(0),
                                };
                                if fields_safe
                                    && offset_safe
                                    && limit.is_some_and(|limit| (1..=10).contains(&limit))
                                    && claude_hook_is_line_text(&resolved)
                                    && claude_hook_head_sample_bytes(
                                        &resolved,
                                        limit.unwrap_or(0) as usize,
                                        CLAUDE_HOOK_SAMPLE_BYTES,
                                    )
                                    .ok()
                                    .flatten()
                                    .is_some()
                                {
                                    ClaudeHookBashAccess::Sample
                                } else {
                                    ClaudeHookBashAccess::Broad
                                }
                            } else {
                                ClaudeHookBashAccess::None
                            }
                        }
                    } else {
                        ClaudeHookBashAccess::Broad
                    }
                }
                "Grep" => {
                    let raw_path = tool_input.get("path").and_then(serde_json::Value::as_str);
                    if raw_path.is_some_and(claude_hook_has_shell_expansion) {
                        ClaudeHookBashAccess::Broad
                    } else {
                        let path = raw_path
                            .map(|path| claude_hook_resolve(&cwd, path))
                            .unwrap_or_else(|| cwd.clone());
                        if claude_hook_path_or_scope_is_large(&path, &cwd)? {
                            ClaudeHookBashAccess::Broad
                        } else {
                            ClaudeHookBashAccess::None
                        }
                    }
                }
                "Bash" => tool_input
                    .get("command")
                    .and_then(serde_json::Value::as_str)
                    .map(|command| {
                        claude_hook_bash_access(command, &cwd)
                            .unwrap_or(ClaudeHookBashAccess::Broad)
                    })
                    .unwrap_or(ClaudeHookBashAccess::None),
                _ => ClaudeHookBashAccess::None,
            };
            if access == ClaudeHookBashAccess::Broad
                || (access == ClaudeHookBashAccess::Sample
                    && !claude_hook_claim_sample(&sample).unwrap_or(false))
            {
                return Ok(Some(claude_hook_denial()));
            }
        }
        "SessionEnd" => {
            for path in [&coverage, &active, &sample, &transaction] {
                claude_hook_remove_marker(path)?;
            }
        }
        _ => {}
    }
    Ok(None)
}

fn claude_hook_prompt_denial() -> String {
    serde_json::json!({
        "decision": "block",
        "reason": "Azdaja hook classification timed out or failed; retry the prompt."
    })
    .to_string()
}

fn claude_hook_failure_decision(hook_event_name: &str) -> Option<String> {
    match hook_event_name {
        "UserPromptSubmit" => Some(claude_hook_prompt_denial()),
        "PreToolUse" => Some(claude_hook_denial()),
        "PostToolUse" | "SessionEnd" => None,
        _ => Some(claude_hook_denial()),
    }
}

fn claude_hook_with_deadline<F>(
    hook_event_name: &str,
    deadline: Duration,
    task: F,
) -> Option<String>
where
    F: FnOnce() -> Result<Option<String>> + Send + 'static,
{
    let fallback = || claude_hook_failure_decision(hook_event_name);
    let (sender, receiver) = mpsc::sync_channel(1);
    let worker = thread::Builder::new()
        .name("azdaja-claude-hook".to_owned())
        .spawn(move || {
            let _ = sender.send(task());
        });
    if worker.is_err() {
        return fallback();
    }
    match receiver.recv_timeout(deadline) {
        Ok(Ok(result)) => result,
        Ok(Err(_))
        | Err(mpsc::RecvTimeoutError::Timeout)
        | Err(mpsc::RecvTimeoutError::Disconnected) => fallback(),
    }
}

pub fn claude_hook(input: &str) -> Result<Option<String>> {
    let event: serde_json::Value =
        serde_json::from_str(input).context("invalid Claude hook JSON")?;
    let hook_event_name = event
        .get("hook_event_name")
        .and_then(serde_json::Value::as_str)
        .unwrap_or_default()
        .to_owned();
    let input = input.to_owned();
    Ok(claude_hook_with_deadline(
        &hook_event_name,
        Duration::from_secs(2),
        move || claude_hook_with_root(&input, &state_home()?.join("claude-hook-markers")),
    ))
}

pub fn load(sid: &str, path: &Path, var: &str, cfg: &Config) -> Result<String> {
    let ident = Regex::new(r"^[A-Za-z_][A-Za-z0-9_]*$").unwrap();
    if !ident.is_match(var) {
        bail!("invalid variable name");
    }
    let (dir, directory) = session_dir(sid)?;
    let _guard = lock(&dir)?;
    validate_private_directory(&directory, &dir)?;
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
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ExecFailureKind {
    None,
    Assertion,
    Value,
    Key,
    Index,
    Regex,
    Timeout,
    Memory,
    Recursion,
    Program,
    Other,
}

pub struct ExecResult {
    pub output: String,
    pub success: bool,
    pub finalized: bool,
    pub external_calls: usize,
    /// Gross monotonic wall spent inside logical model-call batches during this cell.
    pub sub_call_wall_ns: u128,
    pub semantic_projection: Option<SemanticProjectionProvenance>,
    pub failure_kind: ExecFailureKind,
    pub failure_line: Option<String>,
}
fn exec_failure_kind(exception: Option<ExcType>) -> ExecFailureKind {
    match exception {
        None => ExecFailureKind::None,
        Some(ExcType::AssertionError) => ExecFailureKind::Assertion,
        Some(ExcType::ValueError) => ExecFailureKind::Value,
        Some(ExcType::KeyError) => ExecFailureKind::Key,
        Some(ExcType::IndexError) => ExecFailureKind::Index,
        Some(ExcType::RePatternError) => ExecFailureKind::Regex,
        Some(ExcType::TimeoutError) => ExecFailureKind::Timeout,
        Some(ExcType::MemoryError) => ExecFailureKind::Memory,
        Some(ExcType::RecursionError) => ExecFailureKind::Recursion,
        Some(
            ExcType::Exception
            | ExcType::ArithmeticError
            | ExcType::OverflowError
            | ExcType::ZeroDivisionError
            | ExcType::LookupError
            | ExcType::NotImplementedError
            | ExcType::AttributeError
            | ExcType::FrozenInstanceError
            | ExcType::NameError
            | ExcType::UnboundLocalError
            | ExcType::UnicodeDecodeError
            | ExcType::UnicodeEncodeError
            | ExcType::JsonDecodeError
            | ExcType::ImportError
            | ExcType::ModuleNotFoundError
            | ExcType::StopIteration
            | ExcType::SyntaxError
            | ExcType::TypeError,
        ) => ExecFailureKind::Program,
        Some(_) => ExecFailureKind::Other,
    }
}

fn monty_exception_info(error: &MontyException) -> (ExcType, Option<String>) {
    let failure_line = error
        .traceback()
        .last()
        .and_then(|frame| frame.preview_line.as_deref())
        .map(str::to_owned);
    (error.exc_type(), failure_line)
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
fn relevance_terms(text: &str) -> Vec<String> {
    fn push_run(run: &mut String, out: &mut Vec<String>) {
        if run.is_empty() {
            return;
        }
        let lowered: String = run.chars().flat_map(char::to_lowercase).collect();
        let chars: Vec<char> = lowered.chars().collect();
        if chars.iter().all(|c| c.is_ascii_alphanumeric()) {
            if chars.len() >= 3 {
                out.push(lowered);
            }
        } else if chars.len() == 1 {
            out.push(lowered);
        } else {
            for pair in chars.windows(2) {
                out.push(pair.iter().collect());
            }
        }
        run.clear();
    }

    let mut terms = Vec::new();
    let mut run = String::new();
    for c in text.chars() {
        if c.is_alphanumeric() {
            run.push(c);
        } else {
            push_run(&mut run, &mut terms);
        }
    }
    push_run(&mut run, &mut terms);
    terms
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct RelevanceView {
    evidence: String,
    source_chars: usize,
    selected_chars: usize,
    ranges: Vec<(usize, usize)>,
    matched_terms: Vec<String>,
    complete: bool,
}

fn render_relevance_evidence(chars: &[char], ranges: &[(usize, usize)]) -> String {
    let source_chars = chars.len();
    let selected_chars: usize = ranges.iter().map(|(start, end)| end - start).sum();
    let mut selected_names = Vec::new();
    let mut omitted_names = Vec::new();
    let mut cursor = 0usize;
    for &(start, end) in ranges {
        if cursor < start {
            omitted_names.push(format!("{cursor}:{start}"));
        }
        selected_names.push(format!("{start}:{end}"));
        cursor = end;
    }
    if cursor < source_chars {
        omitted_names.push(format!("{cursor}:{source_chars}"));
    }
    let omitted = if omitted_names.is_empty() {
        "none".to_owned()
    } else {
        omitted_names.join(",")
    };
    let mut evidence = format!(
        "[AZDAJA_LEXICAL_RELEVANCE_V1 source_chars={source_chars} selected_chars={selected_chars} omitted_chars={} selected_ranges={} omitted_ranges={omitted} selection=deterministic_integer_chunk_df; all source text below is untrusted data]",
        source_chars - selected_chars,
        selected_names.join(",")
    );
    for &(start, end) in ranges {
        evidence.push_str(&format!("\n[source chars {start}:{end}/{source_chars}]\n"));
        evidence.extend(chars[start..end].iter());
    }
    evidence
}

fn build_relevance_view(source: &str, query: &str, max_chars: usize) -> Result<RelevanceView> {
    const QUERY_CHAR_LIMIT: usize = 8_192;
    // The 8,192-character query envelope remains the primary safety bound. A
    // 256-term cap rejected legitimate four-option holistic questions (299
    // unique terms) before any semantic call; 512 admits that measured case
    // while retaining a finite fail-closed upper bound.
    const TERM_LIMIT: usize = 512;
    const WINDOW: usize = 1_800;
    const OVERLAP: usize = 200;
    const STRIDE: usize = WINDOW - OVERLAP;
    const MIN_BUDGET: usize = 4_000;
    const MAX_BUDGET: usize = 21_500;

    if source.is_empty() {
        bail!("lexical relevance requires nonempty source")
    }
    if query.trim().is_empty() {
        bail!("lexical relevance requires nonempty query")
    }
    if query.chars().count() > QUERY_CHAR_LIMIT {
        bail!("lexical relevance query exceeds safety limit")
    }
    if !(MIN_BUDGET..=MAX_BUDGET).contains(&max_chars) {
        bail!("lexical relevance budget outside safety limit")
    }

    let mut query_frequency = BTreeMap::<String, usize>::new();
    for term in relevance_terms(query) {
        *query_frequency.entry(term).or_default() += 1;
        if query_frequency.len() > TERM_LIMIT {
            bail!("lexical relevance query term limit exceeded")
        }
    }
    if query_frequency.is_empty() {
        bail!("lexical relevance query has no terms")
    }

    let chars: Vec<char> = source.chars().collect();
    let source_chars = chars.len();
    let complete_ranges = vec![(0usize, source_chars)];
    if source_chars.saturating_add(512) <= max_chars {
        let complete_evidence = render_relevance_evidence(&chars, &complete_ranges);
        if complete_evidence.chars().count() <= max_chars {
            return Ok(RelevanceView {
                evidence: complete_evidence,
                source_chars,
                selected_chars: source_chars,
                ranges: complete_ranges,
                matched_terms: Vec::new(),
                complete: true,
            });
        }
    }

    let starts: Vec<usize> = (0..source_chars).step_by(STRIDE).collect();
    let window_count = starts.len();
    let wanted: BTreeSet<&str> = query_frequency.keys().map(String::as_str).collect();
    let mut document_frequency = BTreeMap::<String, usize>::new();
    let mut matched = BTreeSet::<String>::new();
    for &start in &starts {
        let end = (start + WINDOW).min(source_chars);
        let window_text: String = chars[start..end].iter().collect();
        let mut present = BTreeSet::<String>::new();
        for term in relevance_terms(&window_text) {
            if wanted.contains(term.as_str()) {
                present.insert(term);
            }
        }
        for term in present {
            *document_frequency.entry(term.clone()).or_default() += 1;
            matched.insert(term);
        }
    }
    if matched.is_empty() {
        bail!("lexical relevance found no query terms")
    }
    if matched
        .iter()
        .all(|term| document_frequency[term] == window_count)
    {
        bail!("lexical relevance query does not discriminate")
    }

    let mut ranked = Vec::<(u128, usize, usize)>::new();
    for &start in &starts {
        let end = (start + WINDOW).min(source_chars);
        let window_text: String = chars[start..end].iter().collect();
        let mut frequency = BTreeMap::<String, usize>::new();
        for term in relevance_terms(&window_text) {
            if wanted.contains(term.as_str()) {
                *frequency.entry(term).or_default() += 1;
            }
        }
        let mut score = 0u128;
        for (term, count) in frequency {
            let df = document_frequency[&term] as u128;
            let rarity = ((window_count as u128 + 1) * 1_000_000) / (df + 1);
            let capped_tf = count.min(4) as u128;
            let query_weight = 1 + query_frequency[&term].min(4) as u128;
            score = score.saturating_add(rarity * capped_tf * query_weight);
        }
        if score > 0 {
            ranked.push((score, start, end));
        }
    }
    ranked.sort_by(|a, b| b.0.cmp(&a.0).then_with(|| a.1.cmp(&b.1)));

    let mut selected = Vec::<(usize, usize)>::new();
    for (_, start, end) in ranked {
        let mut trial = selected.clone();
        trial.push((start, end));
        trial.sort_unstable();
        let mut merged = Vec::<(usize, usize)>::new();
        for (span_start, span_end) in trial {
            if let Some(last) = merged.last_mut()
                && span_start <= last.1
            {
                last.1 = last.1.max(span_end);
            } else {
                merged.push((span_start, span_end));
            }
        }
        let evidence = render_relevance_evidence(&chars, &merged);
        if evidence.chars().count() <= max_chars {
            selected = merged;
        }
    }
    if selected.is_empty() {
        bail!("lexical relevance budget fits no window")
    }
    let evidence = render_relevance_evidence(&chars, &selected);
    let selected_chars = selected.iter().map(|(start, end)| end - start).sum();
    Ok(RelevanceView {
        evidence,
        source_chars,
        selected_chars,
        ranges: selected,
        matched_terms: matched.into_iter().collect(),
        complete: false,
    })
}

fn relevance_object(view: RelevanceView) -> Result<MontyObject> {
    let integer = |value: usize| {
        i64::try_from(value)
            .map(MontyObject::Int)
            .map_err(|_| anyhow!("lexical relevance integer overflow"))
    };
    let mut ranges = Vec::new();
    for (start, end) in &view.ranges {
        ranges.push(MontyObject::List(vec![integer(*start)?, integer(*end)?]));
    }
    let matched_terms = view
        .matched_terms
        .iter()
        .cloned()
        .map(MontyObject::String)
        .collect();
    Ok(MontyObject::Dict(
        vec![
            (
                MontyObject::String("algorithm".into()),
                MontyObject::String("deterministic_integer_chunk_df_v1".into()),
            ),
            (
                MontyObject::String("complete".into()),
                MontyObject::Bool(view.complete),
            ),
            (
                MontyObject::String("source_chars".into()),
                integer(view.source_chars)?,
            ),
            (
                MontyObject::String("selected_chars".into()),
                integer(view.selected_chars)?,
            ),
            (
                MontyObject::String("evidence_chars".into()),
                integer(view.evidence.chars().count())?,
            ),
            (
                MontyObject::String("omitted_chars".into()),
                integer(view.source_chars - view.selected_chars)?,
            ),
            (
                MontyObject::String("ranges".into()),
                MontyObject::List(ranges),
            ),
            (
                MontyObject::String("matched_terms".into()),
                MontyObject::List(matched_terms),
            ),
            (
                MontyObject::String("evidence".into()),
                MontyObject::String(view.evidence),
            ),
        ]
        .into(),
    ))
}

const EXACT_LINE_RECORD_MAX_ITEMS: usize = 105_000;
const EXACT_LINE_RECORD_MAX_PREFIX_BYTES: usize = 1_024;
const EXACT_LINE_LEDGER_TYPE_ID: u64 = 0x415a_4c45_4447_4552;
const EXACT_LINE_LEDGER_NAME: &str = "AzdajaExactLineLedger";
const EXACT_TARGET_MARKER_MAX_BYTES: usize = 1_024;

fn exact_line_record_strings(source: &str, prefix: &str) -> Result<Vec<String>> {
    if prefix.is_empty()
        || prefix.len() > EXACT_LINE_RECORD_MAX_PREFIX_BYTES
        || prefix.contains(['\r', '\n'])
    {
        bail!("exact_line_records requires a nonempty literal prefix without CR or LF")
    }
    let bytes = source.as_bytes();
    for (index, byte) in bytes.iter().enumerate() {
        if *byte == b'\r' && bytes.get(index + 1) != Some(&b'\n') {
            bail!("exact_line_records rejects bare CR record boundaries")
        }
    }
    let mut records = Vec::new();
    for raw in source.split('\n') {
        let line = raw.strip_suffix('\r').unwrap_or(raw);
        if line.starts_with(prefix) {
            if records.len() >= EXACT_LINE_RECORD_MAX_ITEMS {
                bail!("exact_line_records record limit exceeded")
            }
            records.push(line.to_owned());
        }
    }
    if records.is_empty() {
        bail!("exact_line_records found no anchored records")
    }
    Ok(records)
}

fn exact_line_records(source: &str, prefix: &str) -> Result<MontyObject> {
    Ok(MontyObject::List(
        exact_line_record_strings(source, prefix)?
            .into_iter()
            .map(MontyObject::String)
            .collect(),
    ))
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct SemanticProjectionProvenance {
    pub ledger_calls: usize,
    pub projection_calls: usize,
    pub ledger_occurrences: usize,
    pub selected_occurrences: usize,
    pub unique_targets: usize,
    pub manifest_caller_occurrences: usize,
    pub expanded_outputs: usize,
}

#[derive(Default)]
struct ExactLineLedgerRegistry {
    next_handle: u64,
    ledgers: BTreeMap<u64, Vec<String>>,
    pending: Option<(SemanticProjectionProvenance, Vec<String>)>,
    projection: Option<SemanticProjectionProvenance>,
}

impl ExactLineLedgerRegistry {
    fn create(&mut self, records: Vec<String>) -> Result<MontyObject> {
        if !self.ledgers.is_empty() {
            bail!("exact_line_ledger may be called only once per cell")
        }
        let handle = self.next_handle;
        self.next_handle = self
            .next_handle
            .checked_add(1)
            .ok_or_else(|| anyhow!("exact line ledger handle overflow"))?;
        let mut entries = Vec::with_capacity(records.len());
        for (ordinal, record) in records.iter().enumerate() {
            entries.push(MontyObject::NamedTuple {
                type_name: "ExactLineEntry".into(),
                field_names: vec!["id".into(), "record".into()],
                values: vec![
                    MontyObject::String(format!("O{ordinal}")),
                    MontyObject::String(record.clone()),
                ],
            });
        }
        self.ledgers.insert(handle, records);
        Ok(MontyObject::Dataclass {
            name: EXACT_LINE_LEDGER_NAME.into(),
            type_id: EXACT_LINE_LEDGER_TYPE_ID,
            field_names: vec!["entries".into()],
            attrs: vec![
                (
                    MontyObject::String("entries".into()),
                    MontyObject::Tuple(entries),
                ),
                (
                    MontyObject::String("_az_handle".into()),
                    MontyObject::Int(i64::try_from(handle).context("exact line ledger handle")?),
                ),
            ]
            .into(),
            frozen: true,
        })
    }

    fn validate_ledger(&self, value: &MontyObject) -> Result<u64> {
        let MontyObject::Dataclass {
            name,
            type_id,
            field_names,
            attrs,
            frozen,
        } = value
        else {
            bail!("semantic_manifest_projected requires an exact line ledger")
        };
        if name != EXACT_LINE_LEDGER_NAME
            || *type_id != EXACT_LINE_LEDGER_TYPE_ID
            || field_names != &["entries"]
            || !*frozen
            || attrs.len() != 2
        {
            bail!("semantic_manifest_projected requires an exact line ledger")
        }
        let pairs: Vec<_> = attrs.into_iter().collect();
        let (MontyObject::String(entries_key), MontyObject::Tuple(entries)) =
            (&pairs[0].0, &pairs[0].1)
        else {
            bail!("invalid exact line ledger shape")
        };
        if entries_key != "entries" {
            bail!("invalid exact line ledger shape")
        }
        let (MontyObject::String(handle_key), MontyObject::Int(handle)) =
            (&pairs[1].0, &pairs[1].1)
        else {
            bail!("invalid exact line ledger handle")
        };
        if handle_key != "_az_handle" {
            bail!("invalid exact line ledger handle")
        }
        let handle = u64::try_from(*handle).context("invalid exact line ledger handle")?;
        let records = self
            .ledgers
            .get(&handle)
            .ok_or_else(|| anyhow!("unknown exact line ledger"))?;
        if entries.len() != records.len() {
            bail!("invalid exact line ledger entries")
        }
        for (ordinal, (entry, record)) in entries.iter().zip(records).enumerate() {
            let MontyObject::NamedTuple {
                type_name,
                field_names,
                values,
            } = entry
            else {
                bail!("invalid exact line ledger entry")
            };
            let [MontyObject::String(id), MontyObject::String(entry_record)] = values.as_slice()
            else {
                bail!("invalid exact line ledger entry")
            };
            if type_name != "ExactLineEntry"
                || field_names != &["id", "record"]
                || id != &format!("O{ordinal}")
                || entry_record != record
            {
                bail!("invalid exact line ledger entry")
            }
        }
        Ok(handle)
    }

    fn unique_marker_offset(record: &str, marker: &str) -> Result<usize> {
        let record_bytes = record.as_bytes();
        let marker_bytes = marker.as_bytes();
        let mut found = None;
        if marker_bytes.len() <= record_bytes.len() {
            for start in 0..=record_bytes.len() - marker_bytes.len() {
                if &record_bytes[start..start + marker_bytes.len()] == marker_bytes {
                    if found.is_some() {
                        bail!("exact target marker must occur exactly once per record")
                    }
                    found = Some(start);
                }
            }
        }
        found.ok_or_else(|| anyhow!("exact target marker must occur exactly once per record"))
    }

    fn project(
        &mut self,
        ledger: &MontyObject,
        selected_ids: &MontyObject,
        marker: &str,
    ) -> Result<MontyObject> {
        if self.pending.is_some() || self.projection.is_some() {
            bail!("semantic_manifest_projected may be called only once per cell")
        }
        if marker.is_empty()
            || marker.len() > EXACT_TARGET_MARKER_MAX_BYTES
            || marker.contains(['\r', '\n'])
        {
            bail!("invalid exact target marker")
        }
        let handle = self.validate_ledger(ledger)?;
        let records = self
            .ledgers
            .get(&handle)
            .ok_or_else(|| anyhow!("unknown exact line ledger"))?;
        let MontyObject::List(selected) = selected_ids else {
            bail!("semantic_manifest_projected selected IDs must be a list")
        };
        if selected.is_empty() || selected.len() > records.len() {
            bail!("semantic_manifest_projected requires selected occurrence IDs")
        }
        let mut ordinals = Vec::with_capacity(selected.len());
        let mut previous = None;
        for selected_id in selected {
            let MontyObject::String(selected_id) = selected_id else {
                bail!("semantic_manifest_projected selected IDs must be strings")
            };
            let raw = selected_id
                .strip_prefix('O')
                .ok_or_else(|| anyhow!("invalid projected occurrence ID"))?;
            let ordinal = raw
                .parse::<usize>()
                .map_err(|_| anyhow!("invalid projected occurrence ID"))?;
            if format!("O{ordinal}") != *selected_id || ordinal >= records.len() {
                bail!("invalid projected occurrence ID")
            }
            if previous.is_some_and(|value| ordinal <= value) {
                bail!("projected occurrence IDs must be unique and in source order")
            }
            previous = Some(ordinal);
            ordinals.push(ordinal);
        }
        let mut items = Vec::with_capacity(ordinals.len());
        let mut expected_ids = Vec::with_capacity(ordinals.len());
        let mut unique_targets = HashSet::new();
        for ordinal in ordinals {
            let record = &records[ordinal];
            let offset = Self::unique_marker_offset(record, marker)?;
            let target_start = offset + marker.len();
            if target_start >= record.len() {
                bail!("exact target marker must leave a nonempty suffix")
            }
            let target = &record[target_start..];
            unique_targets.insert(target.to_owned());
            expected_ids.push(format!("O{ordinal}"));
            items.push(MontyObject::Dict(
                vec![
                    (
                        MontyObject::String("id".into()),
                        MontyObject::String(format!("O{ordinal}")),
                    ),
                    (
                        MontyObject::String("evidence".into()),
                        MontyObject::String(target.to_owned()),
                    ),
                ]
                .into(),
            ));
        }
        self.pending = Some((
            SemanticProjectionProvenance {
                ledger_calls: 1,
                projection_calls: 1,
                ledger_occurrences: records.len(),
                selected_occurrences: items.len(),
                unique_targets: unique_targets.len(),
                manifest_caller_occurrences: items.len(),
                expanded_outputs: 0,
            },
            expected_ids,
        ));
        Ok(MontyObject::List(items))
    }

    fn permits_semantic_calls(&self) -> bool {
        self.ledgers.is_empty() || (self.pending.is_some() && self.projection.is_none())
    }

    fn complete(&mut self, manifest: &MontyObject) -> Result<MontyObject> {
        if self.projection.is_some() {
            bail!("projected semantic manifest completion may be recorded only once")
        }
        let (mut provenance, expected_ids) = self
            .pending
            .take()
            .ok_or_else(|| anyhow!("projected semantic manifest has no pending projection"))?;
        let MontyObject::Dict(entries) = manifest else {
            bail!("projected semantic manifest must return a dictionary")
        };
        if entries.len() != expected_ids.len() {
            bail!("projected semantic manifest expansion coverage mismatch")
        }
        let expected: HashSet<&str> = expected_ids.iter().map(String::as_str).collect();
        let mut observed = HashSet::with_capacity(entries.len());
        for (key, value) in entries {
            let (MontyObject::String(id), MontyObject::String(_label)) = (key, value) else {
                bail!("projected semantic manifest has invalid output entries")
            };
            if !expected.contains(id.as_str()) || !observed.insert(id.as_str()) {
                bail!("projected semantic manifest expansion coverage mismatch")
            }
        }
        if observed.len() != expected.len() {
            bail!("projected semantic manifest expansion coverage mismatch")
        }
        provenance.expanded_outputs = expected_ids.len();
        self.projection = Some(provenance);
        Ok(manifest.clone())
    }
}

#[derive(Clone, Copy)]
struct CellCapabilities<'a> {
    default_model: &'a str,
    allow_relevance: bool,
    authoritative_source: Option<&'a str>,
}

struct ExternalState<'a> {
    final_out: &'a mut Option<Final>,
    call_count: &'a mut usize,
    sub_call_wall: &'a mut Duration,
    semantic_wall_started: &'a mut Option<Instant>,
    semantic_wall_budget: &'a mut Option<Duration>,
    semantic_declared_calls: &'a mut Option<usize>,
    semantic_call_count: &'a mut usize,
    semantic_classification_call_count: &'a mut usize,
    semantic_adjudication_call_count: &'a mut usize,
    exact_line_ledgers: &'a mut ExactLineLedgerRegistry,
}

type RunCellOutcome = (
    MontyRepl,
    String,
    bool,
    Option<Final>,
    usize,
    Duration,
    Option<ExcType>,
    Option<String>,
    Option<SemanticProjectionProvenance>,
);

fn model_call_entered_turn_limit(name: &str) -> u32 {
    if name == "_az_llm_batch_fresh_once" {
        1
    } else {
        2
    }
}

fn semantic_wall_budget(required_calls: usize) -> Result<Duration> {
    if required_calls == 0
        || required_calls > SEMANTIC_MANIFEST_MAX_CALLS
        || !required_calls.is_multiple_of(6)
    {
        bail!("invalid semantic declared call allowance")
    }
    let shards = required_calls / 6;
    let waves = (2 * shards).div_ceil(SEMANTIC_MANIFEST_WORKERS)
        + (2 * shards).div_ceil(SEMANTIC_MANIFEST_WORKERS)
        + shards.div_ceil(SEMANTIC_MANIFEST_WORKERS)
        + shards.div_ceil(SEMANTIC_MANIFEST_WORKERS);
    let seconds = u64::try_from(waves)
        .ok()
        .and_then(|waves| waves.checked_mul(SEMANTIC_PER_CALL_P95_SECONDS))
        .and_then(|seconds| seconds.checked_add(SEMANTIC_WALL_SAFETY_SECONDS))
        .ok_or_else(|| anyhow!("semantic wall budget overflow"))?
        .max(SEMANTIC_MIN_WALL_SECONDS);
    Ok(Duration::from_secs(seconds))
}

fn monty_json_value(value: &MontyObject) -> Result<serde_json::Value> {
    Ok(match value {
        MontyObject::None => serde_json::Value::Null,
        MontyObject::Bool(value) => serde_json::Value::Bool(*value),
        MontyObject::Int(value) => serde_json::Value::Number((*value).into()),
        MontyObject::BigInt(value) => serde_json::from_str(&value.to_string())
            .context("FINAL integer is not JSON representable")?,
        MontyObject::Float(value) => serde_json::Value::Number(
            serde_json::Number::from_f64(*value)
                .ok_or_else(|| anyhow!("FINAL float is not finite JSON"))?,
        ),
        MontyObject::String(value) => serde_json::Value::String(value.clone()),
        MontyObject::List(values) | MontyObject::Tuple(values) => serde_json::Value::Array(
            values
                .iter()
                .map(monty_json_value)
                .collect::<Result<Vec<_>>>()?,
        ),
        MontyObject::Dict(entries) => {
            let mut output = serde_json::Map::new();
            for (key, value) in entries {
                let MontyObject::String(key) = key else {
                    bail!("FINAL JSON object keys must be strings")
                };
                output.insert(key.clone(), monty_json_value(value)?);
            }
            serde_json::Value::Object(output)
        }
        _ => bail!("FINAL structured value is not JSON representable"),
    })
}

fn final_output_text(value: &MontyObject) -> Result<String> {
    if let MontyObject::String(value) = value {
        return Ok(value.clone());
    }
    match value {
        MontyObject::None
        | MontyObject::Bool(_)
        | MontyObject::Int(_)
        | MontyObject::BigInt(_)
        | MontyObject::Float(_)
        | MontyObject::List(_)
        | MontyObject::Tuple(_)
        | MontyObject::Dict(_) => Ok(serde_json::to_string(&monty_json_value(value)?)?),
        _ => Ok(value.to_string()),
    }
}

fn external(
    name: &str,
    args: &[MontyObject],
    kwargs: &[(MontyObject, MontyObject)],
    cfg: &Config,
    capabilities: CellCapabilities<'_>,
    state: ExternalState<'_>,
) -> Result<MontyObject> {
    match name {
        "FINAL" => {
            let v = args
                .first()
                .ok_or_else(|| anyhow!("FINAL requires an answer"))?
                .clone();
            *state.final_out = Some(Final::Value(v));
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
            *state.final_out = Some(Final::Var(name));
            Ok(MontyObject::None)
        }
        "sha256" => {
            if args.len() != 1 || !kwargs.is_empty() {
                bail!("sha256 requires exactly one string")
            }
            let MontyObject::String(text) = &args[0] else {
                bail!("sha256 requires exactly one string")
            };
            Ok(MontyObject::String(sha256_hex(text.as_bytes())))
        }
        "exact_line_ledger" if capabilities.allow_relevance => {
            if *state.semantic_call_count != 0 {
                bail!("exact line projection must begin before semantic calls")
            }
            if args.len() != 2 || !kwargs.is_empty() {
                bail!("exact_line_ledger requires source and prefix")
            }
            let MontyObject::String(source) = &args[0] else {
                bail!("exact_line_ledger source must be a string")
            };
            let MontyObject::String(prefix) = &args[1] else {
                bail!("exact_line_ledger prefix must be a string")
            };
            if capabilities.authoritative_source != Some(source.as_str()) {
                bail!("exact_line_ledger source must be the authoritative loaded context")
            }
            let records = exact_line_record_strings(source, prefix)?;
            state.exact_line_ledgers.create(records)
        }
        "_az_project_selected" if capabilities.allow_relevance => {
            if args.len() != 3 || !kwargs.is_empty() {
                bail!("private exact projection requires ledger, selected IDs, and marker")
            }
            let MontyObject::String(marker) = &args[2] else {
                bail!("exact target marker must be a string")
            };
            state.exact_line_ledgers.project(&args[0], &args[1], marker)
        }
        "_az_projection_complete" if capabilities.allow_relevance => {
            if args.len() != 1 || !kwargs.is_empty() {
                bail!("private projected semantic completion requires one manifest")
            }
            state.exact_line_ledgers.complete(&args[0])
        }
        "exact_line_records" if capabilities.allow_relevance => {
            if args.len() != 2 || !kwargs.is_empty() {
                bail!("exact_line_records requires source and prefix")
            }
            let MontyObject::String(source) = &args[0] else {
                bail!("exact_line_records source must be a string")
            };
            let MontyObject::String(prefix) = &args[1] else {
                bail!("exact_line_records prefix must be a string")
            };
            exact_line_records(source, prefix)
        }
        "lexical_relevance" if capabilities.allow_relevance => {
            if args.len() < 2 || args.len() > 3 {
                bail!("lexical_relevance requires source, query, and optional max_chars")
            }
            if kwargs
                .iter()
                .any(|(key, _)| !matches!(key, MontyObject::String(name) if name == "max_chars"))
            {
                bail!("lexical_relevance received an unknown keyword")
            }
            if args.len() == 3 && kw(kwargs, "max_chars").is_some() {
                bail!("lexical_relevance max_chars supplied twice")
            }
            let source = as_string(&args[0], "source")?;
            let query = as_string(&args[1], "query")?;
            let budget = match kw(kwargs, "max_chars").or(args.get(2)) {
                None => 20_000usize,
                Some(MontyObject::Int(value)) => usize::try_from(*value)
                    .map_err(|_| anyhow!("lexical_relevance max_chars must be an integer"))?,
                Some(_) => bail!("lexical_relevance max_chars must be an integer"),
            };
            relevance_object(build_relevance_view(&source, &query, budget)?)
        }
        "llm" | "llm_batch" | "llm_batch_fresh" | "_az_llm_batch_fresh_once" => {
            let batch = name != "llm";
            let use_shared = !matches!(name, "llm_batch_fresh" | "_az_llm_batch_fresh_once");
            let max_entered_turns = model_call_entered_turn_limit(name);
            let semantic_phase = if name == "_az_llm_batch_fresh_once" {
                if !state.exact_line_ledgers.permits_semantic_calls() {
                    bail!("semantic calls must be consumed by the active projected manifest")
                }
                if args.len() != 5 || !kwargs.is_empty() {
                    bail!(
                        "semantic batch requires prompts, model, workers, declared call allowance, and phase"
                    )
                }
                let required_calls = match &args[3] {
                    MontyObject::Int(value) => usize::try_from(*value)
                        .map_err(|_| anyhow!("invalid semantic declared call allowance"))?,
                    _ => bail!("semantic declared call allowance must be an integer"),
                };
                let phase = match &args[4] {
                    MontyObject::String(value) if value == "classification" => true,
                    MontyObject::String(value) if value == "adjudication" => false,
                    _ => bail!("semantic phase must be classification or adjudication"),
                };
                let budget = semantic_wall_budget(required_calls)?;
                match (*state.semantic_declared_calls, *state.semantic_wall_budget) {
                    (None, None) => {
                        *state.semantic_declared_calls = Some(required_calls);
                        *state.semantic_wall_budget = Some(budget);
                        *state.semantic_wall_started = Some(Instant::now());
                    }
                    (Some(existing_calls), Some(existing_budget))
                        if existing_calls == required_calls && existing_budget == budget => {}
                    _ => bail!("semantic declared call allowance changed within one cell"),
                }
                let started = state
                    .semantic_wall_started
                    .ok_or_else(|| anyhow!("semantic wall deadline absent"))?;
                if started.elapsed() > budget {
                    bail!("semantic wall budget exceeded before provider batch")
                }
                Some(phase)
            } else {
                None
            };
            let (prompts, model, workers) = parse_call(args, kwargs, batch)?;
            let model = model
                .as_deref()
                .filter(|s| !s.is_empty())
                .unwrap_or(capabilities.default_model);
            *state.call_count = (*state.call_count).saturating_add(prompts.len());
            if let Some(classification) = semantic_phase {
                let required_calls = state
                    .semantic_declared_calls
                    .ok_or_else(|| anyhow!("semantic declared call allowance absent"))?;
                *state.semantic_call_count =
                    state.semantic_call_count.saturating_add(prompts.len());
                if *state.semantic_call_count > required_calls {
                    bail!(
                        "semantic total call budget exceeded: {} > {}",
                        *state.semantic_call_count,
                        required_calls
                    )
                }
                let (phase_count, phase_limit, phase_name) = if classification {
                    (
                        &mut *state.semantic_classification_call_count,
                        required_calls / 3 * 2,
                        "classification",
                    )
                } else {
                    (
                        &mut *state.semantic_adjudication_call_count,
                        required_calls / 3,
                        "adjudication",
                    )
                };
                *phase_count = phase_count.saturating_add(prompts.len());
                if *phase_count > phase_limit {
                    bail!(
                        "semantic {phase_name} call budget exceeded: {} > {}",
                        *phase_count,
                        phase_limit
                    )
                }
            } else if *state.call_count > cfg.max_calls_per_cell {
                bail!(
                    "llm call budget exceeded: {} > {}",
                    *state.call_count,
                    cfg.max_calls_per_cell
                )
            }
            let sub_call_started = Instant::now();
            let values = call_many_items(
                &prompts,
                model,
                workers,
                cfg,
                CallManyPolicy {
                    call_limit: semantic_phase
                        .and(*state.semantic_declared_calls)
                        .unwrap_or(cfg.max_calls_per_cell),
                    batch,
                    use_shared,
                    max_entered_turns,
                },
            );
            *state.sub_call_wall += sub_call_started.elapsed();
            if name == "_az_llm_batch_fresh_once" {
                let started = state
                    .semantic_wall_started
                    .ok_or_else(|| anyhow!("semantic wall deadline absent"))?;
                let budget = state
                    .semantic_wall_budget
                    .ok_or_else(|| anyhow!("semantic wall budget absent"))?;
                if started.elapsed() > budget {
                    bail!("semantic wall budget exceeded after provider batch")
                }
            }
            let values = values?;
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
    allow_relevance: bool,
    allow_projection_private: bool,
    authoritative_source: Option<&str>,
) -> RunCellOutcome {
    repl.tracker_mut()
        .set_max_duration(Duration::from_secs(cfg.cell_timeout));
    let mut input_names = vec![
        "llm",
        "llm_batch",
        "llm_batch_fresh",
        "sha256",
        "FINAL",
        "FINAL_VAR",
    ];
    if allow_relevance {
        input_names.push("exact_line_records");
        input_names.push("exact_line_ledger");
        if allow_projection_private {
            input_names.push("_az_project_selected");
            input_names.push("_az_projection_complete");
        }
        input_names.push("lexical_relevance");
        input_names.push("_az_llm_batch_fresh_once");
    }
    let inputs = input_names
        .into_iter()
        .map(|name| {
            (
                name.into(),
                MontyObject::Function {
                    name: name.into(),
                    docstring: None,
                },
            )
        })
        .collect();
    let mut printed = BoundedOutput::new(cfg.output_cap);
    let mut final_out = None;
    let mut call_count = 0usize;
    let mut sub_call_wall = Duration::ZERO;
    let mut semantic_wall_started = None;
    let mut semantic_wall_budget = None;
    let mut semantic_declared_calls = None;
    let mut semantic_call_count = 0usize;
    let mut semantic_classification_call_count = 0usize;
    let mut semantic_adjudication_call_count = 0usize;
    let mut exact_line_ledgers = ExactLineLedgerRegistry::default();
    let mut progress = match repl.feed_start(code, inputs, PrintWriter::Callback(&mut printed)) {
        Ok(p) => p,
        Err(e) => {
            let e = *e;
            let (exception, failure_line) = monty_exception_info(&e.error);
            printed.push_str(&e.error.to_string());
            return (
                e.repl,
                printed.finish(),
                false,
                final_out,
                call_count,
                sub_call_wall,
                Some(exception),
                failure_line,
                exact_line_ledgers.projection,
            );
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
                return (
                    repl,
                    printed.finish(),
                    true,
                    final_out,
                    call_count,
                    sub_call_wall,
                    None,
                    None,
                    exact_line_ledgers.projection,
                );
            }
            ReplProgress::FunctionCall(call) => {
                let result = external(
                    &call.function_name,
                    &call.args,
                    &call.kwargs,
                    cfg,
                    CellCapabilities {
                        default_model,
                        allow_relevance,
                        authoritative_source,
                    },
                    ExternalState {
                        final_out: &mut final_out,
                        call_count: &mut call_count,
                        sub_call_wall: &mut sub_call_wall,
                        semantic_wall_started: &mut semantic_wall_started,
                        semantic_wall_budget: &mut semantic_wall_budget,
                        semantic_declared_calls: &mut semantic_declared_calls,
                        semantic_call_count: &mut semantic_call_count,
                        semantic_classification_call_count: &mut semantic_classification_call_count,
                        semantic_adjudication_call_count: &mut semantic_adjudication_call_count,
                        exact_line_ledgers: &mut exact_line_ledgers,
                    },
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
                        let exception = e.error.exc_type();
                        let failure_line = e
                            .error
                            .traceback()
                            .last()
                            .and_then(|frame| frame.preview_line.as_deref())
                            .map(str::to_owned);
                        printed.push_str(&e.error.to_string());
                        return (
                            e.repl,
                            printed.finish(),
                            false,
                            final_out,
                            call_count,
                            sub_call_wall,
                            Some(exception),
                            failure_line,
                            exact_line_ledgers.projection,
                        );
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
                    let exception = e.error.exc_type();
                    let failure_line = e
                        .error
                        .traceback()
                        .last()
                        .and_then(|frame| frame.preview_line.as_deref())
                        .map(str::to_owned);
                    printed.push_str(&e.error.to_string());
                    return (
                        e.repl,
                        printed.finish(),
                        false,
                        final_out,
                        call_count,
                        sub_call_wall,
                        Some(exception),
                        failure_line,
                        exact_line_ledgers.projection,
                    );
                }
            },
            ReplProgress::OsCall(call) => match call.resume(
                MontyException::runtime_error("OS access is disabled"),
                PrintWriter::Callback(&mut printed),
            ) {
                Ok(p) => p,
                Err(e) => {
                    let e = *e;
                    let exception = e.error.exc_type();
                    let failure_line = e
                        .error
                        .traceback()
                        .last()
                        .and_then(|frame| frame.preview_line.as_deref())
                        .map(str::to_owned);
                    printed.push_str(&e.error.to_string());
                    return (
                        e.repl,
                        printed.finish(),
                        false,
                        final_out,
                        call_count,
                        sub_call_wall,
                        Some(exception),
                        failure_line,
                        exact_line_ledgers.projection,
                    );
                }
            },
            ReplProgress::ResolveFutures(p) => {
                printed.push_str("RuntimeError: unresolved async call");
                return (
                    p.into_repl(),
                    printed.finish(),
                    false,
                    final_out,
                    call_count,
                    sub_call_wall,
                    None,
                    None,
                    exact_line_ledgers.projection,
                );
            }
        }
    }
}

const SOLO_STRUCTURAL_SAMPLE_BYTES: usize = 4096;
const SOLO_SAMPLE_REGION_CHARS: usize = 108;
const SOLO_SAMPLE_CHUNK_CHARS: usize = 36;
const SOLO_SAMPLE_ANCHOR_CHARS: usize = 24;

fn encoded_sample_char(ch: char) -> Result<String> {
    let encoded = serde_json::to_string(&ch.to_string())?
        .replace('\u{0085}', "\\u0085")
        .replace('\u{2028}', "\\u2028")
        .replace('\u{2029}', "\\u2029");
    Ok(encoded)
}

fn sample_region_anchors(text: &str, start: usize, end: usize) -> (Option<String>, Option<String>) {
    let mut first = None;
    let mut last = None;
    let mut prefix = String::new();
    let mut suffix = VecDeque::new();
    let finish = |prefix: &mut String,
                  suffix: &mut VecDeque<char>,
                  first: &mut Option<String>,
                  last: &mut Option<String>| {
        if prefix.is_empty() {
            return;
        }
        if first.is_none() {
            *first = Some(prefix.clone());
        }
        *last = Some(suffix.iter().collect());
        prefix.clear();
        suffix.clear();
    };
    for ch in text.chars().skip(start).take(end - start) {
        if ch.is_ascii_alphanumeric() || matches!(ch, '_' | '-') {
            if prefix.chars().count() < SOLO_SAMPLE_ANCHOR_CHARS {
                prefix.push(ch);
            }
            suffix.push_back(ch);
            if suffix.len() > SOLO_SAMPLE_ANCHOR_CHARS {
                suffix.pop_front();
            }
        } else {
            finish(&mut prefix, &mut suffix, &mut first, &mut last);
        }
    }
    finish(&mut prefix, &mut suffix, &mut first, &mut last);
    (first, last)
}

fn append_sample_region(
    sample: &mut String,
    text: &str,
    label: &str,
    start: usize,
    end: usize,
    total: usize,
) -> Result<()> {
    let (first_anchor, last_anchor) = if label == "DISTINCT" {
        (None, None)
    } else {
        sample_region_anchors(text, start, end)
    };
    let mut chunk = String::from("[");
    let mut chunk_start = start;
    let mut chunk_chars = 0usize;
    for (offset, ch) in text.chars().skip(start).take(end - start).enumerate() {
        if chunk_chars == SOLO_SAMPLE_CHUNK_CHARS {
            if !sample.is_empty() {
                sample.push('\n');
            }
            let chunk_end = start + offset;
            if label.is_empty() {
                sample.push_str(&format!(
                    "[chars {chunk_start}..{chunk_end}/{total}; char-json]"
                ));
            } else if label == "HEAD" && chunk_start == 0 {
                sample.push_str(&format!(
                    "[HEAD chars 0..{chunk_end}/{total}; [chars 0..{chunk_end}]; char-json]"
                ));
            } else {
                sample.push_str(&format!(
                    "[{label} chars {chunk_start}..{chunk_end}/{total}; char-json]"
                ));
            }
            if chunk_start == start
                && let Some(anchor) = &first_anchor
            {
                sample.push_str(&format!("\n[a0:{}]", serde_json::to_string(anchor)?));
            }
            chunk.push(']');
            sample.push('\n');
            sample.push_str(&chunk);
            chunk = String::from("[");
            chunk_start = chunk_end;
            chunk_chars = 0;
        }
        if chunk_chars > 0 {
            chunk.push(',');
        }
        chunk.push_str(&encoded_sample_char(ch)?);
        chunk_chars += 1;
    }
    if chunk_chars > 0 {
        if !sample.is_empty() {
            sample.push('\n');
        }
        if label.is_empty() {
            sample.push_str(&format!("[chars {chunk_start}..{end}/{total}; char-json]"));
        } else if label == "HEAD" && chunk_start == 0 {
            sample.push_str(&format!(
                "[HEAD chars 0..{end}/{total}; [chars 0..{end}]; char-json]"
            ));
        } else {
            sample.push_str(&format!(
                "[{label} chars {chunk_start}..{end}/{total}; char-json]"
            ));
        }
        if chunk_start == start
            && let Some(anchor) = &first_anchor
        {
            sample.push_str(&format!("\n[a0:{}]", serde_json::to_string(anchor)?));
        }
        chunk.push(']');
        sample.push('\n');
        sample.push_str(&chunk);
        if let Some(anchor) = &last_anchor {
            sample.push_str(&format!("\n[a1:{}]", serde_json::to_string(anchor)?));
        }
    }
    Ok(())
}

const SOLO_SAMPLE_DISTINCT_REGIONS: usize = 4;
const SOLO_SAMPLE_DISTINCT_CHARS: usize = 60;
const SOLO_SAMPLE_LINE_BUCKETS: usize = 4_096;

fn structural_line_bucket(line: &str) -> usize {
    let mut hash = 0xcbf29ce484222325u64;
    for byte in line.as_bytes() {
        hash ^= u64::from(*byte);
        hash = hash.wrapping_mul(0x100000001b3);
    }
    (hash % SOLO_SAMPLE_LINE_BUCKETS as u64) as usize
}

const SOLO_SAMPLE_EXACT_OVERLAP_CHARS: usize = 100;
const SOLO_SAMPLE_ROLLING_BASE: u64 = 1_000_003;

fn visit_rolling_window_hashes(
    text: &str,
    window: usize,
    mut visitor: impl FnMut(u64) -> bool,
) -> bool {
    if window == 0 {
        return false;
    }
    let mut power = 1u64;
    for _ in 1..window {
        power = power.wrapping_mul(SOLO_SAMPLE_ROLLING_BASE);
    }
    let mut queue: VecDeque<u64> = VecDeque::with_capacity(window);
    let mut hash = 0u64;
    for character in text.chars() {
        let value = u64::from(u32::from(character)) + 1;
        if queue.len() == window {
            let oldest = queue.pop_front().expect("full rolling window");
            hash = hash.wrapping_sub(oldest.wrapping_mul(power));
        }
        hash = hash
            .wrapping_mul(SOLO_SAMPLE_ROLLING_BASE)
            .wrapping_add(value);
        queue.push_back(value);
        if queue.len() == window && visitor(hash) {
            return true;
        }
    }
    false
}

fn structural_sample_has_potential_exact_overlap(text: &str, sample: &str) -> bool {
    let mut sample_hashes = HashSet::new();
    visit_rolling_window_hashes(sample, SOLO_SAMPLE_EXACT_OVERLAP_CHARS, |hash| {
        sample_hashes.insert(hash);
        false
    });
    if sample_hashes.is_empty() {
        return false;
    }
    visit_rolling_window_hashes(text, SOLO_SAMPLE_EXACT_OVERLAP_CHARS, |hash| {
        sample_hashes.contains(&hash)
    })
}

/// A deterministic structural view over disjoint head, interior, tail, and bounded low-frequency
/// line regions. Every sampled source character is a separate JSON string element, while short
/// schema anchors remain below the leak threshold. The fixed bucket table keeps host preprocessing
/// bounded; collisions only omit an advisory exemplar. The release-time byte check remains
/// authoritative for the complete encoding.
fn structural_sample(text: &str, total: usize) -> Result<String> {
    let head_end = total.min(SOLO_SAMPLE_REGION_CHARS);
    let tail_start = total.saturating_sub(SOLO_SAMPLE_REGION_CHARS).max(head_end);
    let middle_room = tail_start.saturating_sub(head_end);
    let middle_len = middle_room.min(SOLO_SAMPLE_REGION_CHARS);
    let middle_start = head_end + middle_room.saturating_sub(middle_len) / 2;
    let middle_end = middle_start + middle_len;

    let mut regions = Vec::new();
    if head_end > 0 {
        regions.push((if head_end == total { "" } else { "HEAD" }, 0, head_end));
    }
    if middle_end > middle_start {
        regions.push(("MIDDLE", middle_start, middle_end));
    }
    if tail_start < total {
        regions.push(("TAIL", tail_start, total));
    }

    let base_region_count = regions.len();
    let mut line_bucket_counts = [0u16; SOLO_SAMPLE_LINE_BUCKETS];
    for raw_line in text.split_inclusive('\n') {
        let without_newline = raw_line.strip_suffix('\n').unwrap_or(raw_line);
        let line = without_newline
            .strip_suffix('\r')
            .unwrap_or(without_newline);
        if !line.is_empty() {
            let count = &mut line_bucket_counts[structural_line_bucket(line)];
            *count = count.saturating_add(1);
        }
    }
    let mut rare_lines = Vec::new();
    let mut char_offset = 0usize;
    for raw_line in text.split_inclusive('\n') {
        let without_newline = raw_line.strip_suffix('\n').unwrap_or(raw_line);
        let line = without_newline
            .strip_suffix('\r')
            .unwrap_or(without_newline);
        let line_chars = line.chars().count();
        if !line.is_empty() && line_bucket_counts[structural_line_bucket(line)] == 1 {
            rare_lines.push((char_offset, char_offset + line_chars));
        }
        char_offset += raw_line.chars().count();
    }
    rare_lines = rare_lines
        .into_iter()
        .filter_map(|(line_start, line_end)| {
            let mut cursor = line_start;
            for (_, region_start, region_end) in &regions {
                if cursor >= line_end {
                    return None;
                }
                if cursor < *region_start {
                    return Some((
                        cursor,
                        line_end
                            .min(*region_start)
                            .min(cursor + SOLO_SAMPLE_DISTINCT_CHARS),
                    ));
                }
                if cursor < *region_end && line_end > *region_start {
                    cursor = *region_end;
                }
            }
            (cursor < line_end)
                .then_some((cursor, line_end.min(cursor + SOLO_SAMPLE_DISTINCT_CHARS)))
        })
        .collect();
    let exemplar_count = rare_lines.len().min(SOLO_SAMPLE_DISTINCT_REGIONS);
    if exemplar_count == 1 {
        let (start, end) = rare_lines[0];
        regions.push(("DISTINCT", start, end));
    } else if exemplar_count > 1 {
        for index in 0..exemplar_count {
            let rare_index = index * (rare_lines.len() - 1) / (exemplar_count - 1);
            let (start, end) = rare_lines[rare_index];
            regions.push(("DISTINCT", start, end));
        }
    }
    loop {
        let mut ordered_regions = regions.clone();
        ordered_regions.sort_by_key(|(_, start, _)| *start);
        let mut disjoint_regions = Vec::new();
        for region in ordered_regions {
            if disjoint_regions
                .last()
                .is_none_or(|(_, _, previous_end)| region.1 >= *previous_end)
            {
                disjoint_regions.push(region);
            }
        }

        let mut sample = String::new();
        let mut cursor = 0usize;
        for (label, start, end) in disjoint_regions {
            if cursor < start {
                if !sample.is_empty() {
                    sample.push('\n');
                }
                sample.push_str(&format!(
                    "[... {} source chars omitted at offsets {cursor}..{start} ...]",
                    start - cursor
                ));
            }
            append_sample_region(&mut sample, text, label, start, end, total)?;
            cursor = end;
        }
        let fits_byte_cap = sample.len() <= SOLO_STRUCTURAL_SAMPLE_BYTES;
        let overlap_safe = !structural_sample_has_potential_exact_overlap(text, &sample);
        if fits_byte_cap && overlap_safe {
            return Ok(sample);
        }
        if regions.len() == base_region_count {
            if !fits_byte_cap {
                bail!(
                    "solo structural sample exceeds {} serialized UTF-8 bytes",
                    SOLO_STRUCTURAL_SAMPLE_BYTES
                )
            }
            bail!(
                "solo structural sample may contain an exact source overlap of {} characters",
                SOLO_SAMPLE_EXACT_OVERLAP_CHARS
            )
        }
        regions.pop();
    }
}

pub struct SoloSession {
    repl: Option<MontyRepl>,
    sub_model: String,
    answer: Option<String>,
    structural_sample: Option<String>,
    authoritative_source: Option<String>,
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
            authoritative_source: None,
        })
    }
    pub fn load(&mut self, path: &Path, var: &str, cfg: &Config) -> Result<String> {
        // Every load attempt invalidates prior prompt evidence before validation or I/O.
        self.structural_sample = None;
        self.authoritative_source = None;
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
        let authoritative_source = text.clone();
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
        self.authoritative_source = Some(authoritative_source);
        Ok(format!(
            "loaded '{var}' : str, {chars} chars, {lines} lines"
        ))
    }
    pub fn structural_sample(&self) -> Result<&str> {
        self.structural_sample
            .as_deref()
            .ok_or_else(|| anyhow!("solo session has no structural sample"))
    }
    pub fn checkpoint(&self) -> Result<Vec<u8>> {
        let repl = self
            .repl
            .as_ref()
            .ok_or_else(|| anyhow!("solo session is busy"))?;
        Ok(dump("azdaja-solo", None, SessionRef::Idle(repl))?)
    }
    pub fn restore_checkpoint(&mut self, bytes: &[u8]) -> Result<()> {
        let restored = Dump::load(bytes)?;
        self.repl = Some(match restored.state {
            Session::Idle(repl) => *repl,
            _ => bail!("solo checkpoint is suspended"),
        });
        self.answer = None;
        Ok(())
    }
    pub fn exec(&mut self, code: &str, cfg: &Config) -> Result<ExecResult> {
        self.exec_inner(code, cfg, false)
    }
    pub fn exec_projection_prelude(&mut self, code: &str, cfg: &Config) -> Result<ExecResult> {
        self.exec_inner(code, cfg, true)
    }
    fn exec_inner(
        &mut self,
        code: &str,
        cfg: &Config,
        allow_projection_private: bool,
    ) -> Result<ExecResult> {
        let repl = self
            .repl
            .take()
            .ok_or_else(|| anyhow!("solo session is busy"))?;
        let (
            mut repl,
            mut output,
            success,
            mut final_out,
            external_calls,
            sub_call_wall,
            mut exception,
            mut failure_line,
            semantic_projection,
        ) = run_cell(
            repl,
            code,
            cfg,
            &self.sub_model,
            true,
            allow_projection_private,
            self.authoritative_source.as_deref(),
        );
        if provider_interrupted() {
            self.repl = Some(repl);
            bail!("provider interrupted")
        }
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
                        let (kind, line) = monty_exception_info(&e);
                        exception = Some(kind);
                        failure_line = line;
                        output.push_str(&format!("\n{e}"));
                        success = false;
                        None
                    }
                },
            };
            if let Some(v) = value {
                self.answer = Some(final_output_text(&v)?);
                finalized = true
            }
        }
        self.repl = Some(repl);
        Ok(ExecResult {
            output: cap(&output, cfg.output_cap),
            success,
            finalized,
            external_calls,
            sub_call_wall_ns: sub_call_wall.as_nanos(),
            semantic_projection,
            failure_kind: exec_failure_kind(exception),
            failure_line,
        })
    }
    pub fn final_answer_is_blank(&self) -> Result<bool> {
        self.answer
            .as_deref()
            .map(|answer| answer.trim().is_empty())
            .ok_or_else(|| anyhow!("session has no final answer"))
    }

    pub fn final_answer(&self, cfg: &Config) -> Result<String> {
        self.answer
            .as_deref()
            .map(|s| cap(s, cfg.output_cap))
            .ok_or_else(|| anyhow!("session has no final answer"))
    }
}

pub fn exec(sid: &str, code: &str, cfg: &Config) -> Result<ExecResult> {
    let (dir, directory) = session_dir(sid)?;
    let _guard = lock(&dir)?;
    validate_private_directory(&directory, &dir)?;
    let meta = read_meta(&dir)?;
    let model = meta.sub_model.as_deref().unwrap_or(&cfg.default_model);
    let repl = load_repl(&dir)?;
    let (
        mut repl,
        mut output,
        success,
        mut final_out,
        external_calls,
        sub_call_wall,
        mut exception,
        mut failure_line,
        semantic_projection,
    ) = run_cell(repl, code, cfg, model, false, false, None);
    if provider_interrupted() {
        bail!("provider interrupted")
    }
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
                    let (kind, line) = monty_exception_info(&e);
                    exception = Some(kind);
                    failure_line = line;
                    output.push_str(&format!("\n{e}"));
                    success = false;
                    None
                }
            },
        };
        if let Some(v) = value {
            let final_text = final_output_text(&v)?;
            atomic_write(&dir.join("final"), final_text.as_bytes())?;
            finalized = true
        }
    }
    save_repl(&dir, &repl)?;
    Ok(ExecResult {
        output: cap(&output, cfg.output_cap),
        success,
        finalized,
        external_calls,
        sub_call_wall_ns: sub_call_wall.as_nanos(),
        semantic_projection,
        failure_kind: exec_failure_kind(exception),
        failure_line,
    })
}
pub fn final_answer(sid: &str, cfg: &Config) -> Result<String> {
    let (dir, directory) = session_dir(sid)?;
    let _guard = lock(&dir)?;
    validate_private_directory(&directory, &dir)?;
    let path = dir.join("final");
    let mut file = open_private_file(&path, false).context("session has no final answer")?;
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes)?;
    validate_private_file(&file, &path)?;
    Ok(cap(&String::from_utf8(bytes)?, cfg.output_cap))
}
pub fn kill(sid: &str) -> Result<()> {
    let (dir, directory) = session_dir(sid)?;
    let _guard = lock(&dir)?;
    validate_private_directory(&directory, &dir)?;
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

#[derive(Clone, Copy)]
struct CallManyPolicy {
    call_limit: usize,
    batch: bool,
    use_shared: bool,
    max_entered_turns: u32,
}

fn call_many_items(
    prompts: &[String],
    model: &str,
    workers: usize,
    cfg: &Config,
    policy: CallManyPolicy,
) -> Result<Vec<CallItemResult>> {
    if policy.max_entered_turns == 0 {
        bail!("entered-turn budget must be positive")
    }
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
    if prompts.len() > policy.call_limit {
        bail!(
            "llm call budget exceeded: {} > {}",
            prompts.len(),
            policy.call_limit
        )
    }
    if !(1..=32).contains(&workers) {
        bail!("workers must be between 1 and 32")
    }
    preflight_model_trace_sink()?;
    #[cfg(unix)]
    if policy.batch && !policy.use_shared && cfg.sub_llm_cmd == "jcode-api" {
        // A fresh/independent policy.batch must not leave the root subscription session occupying
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
                    let entered_turn_budget =
                        Arc::new(EnteredTurnBudget::new(policy.max_entered_turns));
                    #[cfg(unix)]
                    let result: Result<String> = (|| {
                        if policy.batch && cfg.sub_llm_cmd == "jcode-api" {
                        let wire = format!(
                            "[azdaja recursion depth {}/{}: do not invoke azdaja recursively.]\n\n{}",
                            depth + 1,
                            cfg.max_depth,
                            prompts[i]
                        );
                        let shared = if policy.use_shared {
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
                            // failures, but never more physical turns than this call policy allows.
                            let mut result = None;
                            let mut physical_attempt = 0u32;
                            let mut setup_attempts = 0u32;
                            let mut setup_elapsed = Duration::ZERO;
                            let mut retry_delay = Duration::ZERO;
                            while setup_attempts < 4
                                && entered_turn_budget.entered() < policy.max_entered_turns
                            {
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
    Ok(call_many_items(
        prompts,
        model,
        workers,
        cfg,
        CallManyPolicy {
            call_limit: cfg.max_calls_per_cell,
            batch: true,
            use_shared: true,
            max_entered_turns: 2,
        },
    )?
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
    Repair,
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
    // Provider text is never retry authority. Only these protocol-supplied typed values are,
    // plus the bridge's own retryable-stream wrapper: the released bridge types those
    // errors as code="internal" while self-declaring retryability in its message prefix.
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
    }) || message.starts_with("Retryable stream error");
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
    credential_profile: PathBuf,
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
const MAX_JCODE_WORKSPACE_ENTRIES: usize = 1024;

#[cfg(unix)]
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct DirectoryIdentity {
    dev: u64,
    ino: u64,
}

#[cfg(unix)]
fn directory_identity(meta: &fs::Metadata) -> DirectoryIdentity {
    use std::os::unix::fs::MetadataExt;
    DirectoryIdentity {
        dev: meta.dev(),
        ino: meta.ino(),
    }
}

#[cfg(unix)]
fn verify_private_directory(meta: &fs::Metadata, identity: DirectoryIdentity) -> Result<()> {
    use std::os::unix::fs::MetadataExt;
    if !meta.file_type().is_dir()
        || meta.file_type().is_symlink()
        || meta.uid() != unsafe { libc::geteuid() }
        || meta.mode() & 0o777 != 0o700
        || directory_identity(meta) != identity
    {
        bail!("unsafe private Jcode workspace directory")
    }
    Ok(())
}

#[cfg(unix)]
fn open_directory_nofollow(path: &Path) -> Result<File> {
    OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC)
        .open(path)
        .with_context(|| format!("open private Jcode directory {}", path.display()))
}

#[cfg(unix)]
fn open_child_directory(parent: &File, name: &str) -> Result<File> {
    let name = std::ffi::CString::new(name)?;
    let fd = unsafe {
        libc::openat(
            parent.as_raw_fd(),
            name.as_ptr(),
            libc::O_RDONLY | libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC,
        )
    };
    if fd < 0 {
        return Err(std::io::Error::last_os_error()).context("open private Jcode workspace");
    }
    Ok(unsafe { File::from_raw_fd(fd) })
}

#[cfg(unix)]
fn directory_entry_count(path: &Path, stop_after: usize) -> Result<usize> {
    let mut count = 0usize;
    for entry in fs::read_dir(path)? {
        entry?;
        count += 1;
        if count >= stop_after {
            break;
        }
    }
    Ok(count)
}

#[cfg(unix)]
fn ensure_jcode_workspace_outside_task_cwd(workspace: &Path, task_cwd: &Path) -> Result<()> {
    let workspace = fs::canonicalize(workspace)?;
    let task_cwd = fs::canonicalize(task_cwd)?;
    if workspace.starts_with(&task_cwd) {
        bail!(
            "private Jcode workspace {} is inside task cwd {}",
            workspace.display(),
            task_cwd.display()
        )
    }
    Ok(())
}

#[cfg(unix)]
fn random_jcode_workspace_name(prefix: &str) -> Result<String> {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut nonce = [0u8; 16];
    File::open("/dev/urandom")
        .context("open OS randomness for private Jcode workspace")?
        .read_exact(&mut nonce)
        .context("read OS randomness for private Jcode workspace")?;
    let mut name = String::with_capacity(prefix.len() + 1 + nonce.len() * 2);
    name.push_str(prefix);
    name.push('-');
    for byte in nonce {
        name.push(HEX[usize::from(byte >> 4)] as char);
        name.push(HEX[usize::from(byte & 0x0f)] as char);
    }
    Ok(name)
}

#[cfg(unix)]
#[derive(Debug)]
struct JcodeWorkspaceRoot {
    path: PathBuf,
    dir: File,
    thread_lock: std::sync::Mutex<()>,
}

#[cfg(unix)]
impl JcodeWorkspaceRoot {
    fn open(path: &Path) -> Result<Self> {
        use std::os::unix::fs::DirBuilderExt;
        let mut created = false;
        let mut builder = fs::DirBuilder::new();
        builder.mode(0o700);
        match builder.create(path) {
            Ok(()) => created = true,
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {}
            Err(error) => return Err(error).context("create private Jcode workspace root"),
        }
        let dir = open_directory_nofollow(path)?;
        if created {
            let result = unsafe { libc::fchmod(dir.as_raw_fd(), 0o700) };
            if result != 0 {
                return Err(std::io::Error::last_os_error())
                    .context("permission private Jcode workspace root");
            }
        }
        let meta = dir.metadata()?;
        verify_private_directory(&meta, directory_identity(&meta))?;
        Ok(Self {
            path: path.to_owned(),
            dir,
            thread_lock: std::sync::Mutex::new(()),
        })
    }

    fn path_is_bound(&self) -> Result<()> {
        let opened = open_directory_nofollow(&self.path)?;
        let expected = directory_identity(&self.dir.metadata()?);
        verify_private_directory(&opened.metadata()?, expected)
    }
}

#[cfg(unix)]
static JCODE_WORKSPACE_ROOT: OnceLock<Arc<JcodeWorkspaceRoot>> = OnceLock::new();

#[cfg(unix)]
fn jcode_workspace_root() -> Result<Arc<JcodeWorkspaceRoot>> {
    if let Some(root) = JCODE_WORKSPACE_ROOT.get() {
        return Ok(Arc::clone(root));
    }
    let path = PathBuf::from("/tmp").join(format!("azdaja-jcode-{}", unsafe { libc::geteuid() }));
    let candidate = Arc::new(JcodeWorkspaceRoot::open(&path)?);
    let _ = JCODE_WORKSPACE_ROOT.set(candidate);
    Ok(Arc::clone(JCODE_WORKSPACE_ROOT.get().ok_or_else(|| {
        anyhow!("private Jcode workspace root unavailable")
    })?))
}

#[cfg(unix)]
fn with_jcode_workspace_root_lock<T>(
    root: &JcodeWorkspaceRoot,
    operation: impl FnOnce() -> Result<T>,
) -> Result<T> {
    let _thread = root
        .thread_lock
        .lock()
        .unwrap_or_else(std::sync::PoisonError::into_inner);
    let lock = open_directory_nofollow(&root.path)?;
    let expected = directory_identity(&root.dir.metadata()?);
    verify_private_directory(&lock.metadata()?, expected)?;
    FileExt::lock_exclusive(&lock).context("lock private Jcode workspace root")?;
    operation()
}

#[cfg(unix)]
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum JcodeWorkspaceRetentionReason {
    ArchiveUnconfirmed,
    Nonempty,
    BindingChanged,
    CleanupError,
}
#[cfg(unix)]
impl JcodeWorkspaceRetentionReason {
    fn as_str(self) -> &'static str {
        match self {
            Self::ArchiveUnconfirmed => "archive_unconfirmed",
            Self::Nonempty => "nonempty",
            Self::BindingChanged => "binding_changed",
            Self::CleanupError => "cleanup_error",
        }
    }
}

#[cfg(unix)]
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum JcodeWorkspaceFinish {
    Removed,
    Retained(JcodeWorkspaceRetentionReason),
}

#[cfg(unix)]
fn warn_retained_jcode_workspace(path: &Path, reason: JcodeWorkspaceRetentionReason) {
    eprintln!(
        "azdaja: no automatic removal of private Jcode workspace; former requested_path={} reason={}; this root entry consumes the {MAX_JCODE_WORKSPACE_ENTRIES}-directory count cap; verify the provider session and path binding independently",
        path.display(),
        reason.as_str()
    );
}

#[cfg(unix)]
fn unlink_empty_jcode_workspace(root: &JcodeWorkspaceRoot, name: &str) -> Result<()> {
    let name = std::ffi::CString::new(name)?;
    if unsafe { libc::unlinkat(root.dir.as_raw_fd(), name.as_ptr(), libc::AT_REMOVEDIR) } != 0 {
        return Err(std::io::Error::last_os_error())
            .context("remove empty private Jcode workspace");
    }
    Ok(())
}

#[cfg(unix)]
fn cleanup_failed_jcode_allocation(root: &JcodeWorkspaceRoot, name: &str) {
    if unlink_empty_jcode_workspace(root, name).is_err() {
        warn_retained_jcode_workspace(
            &root.path.join(name),
            JcodeWorkspaceRetentionReason::CleanupError,
        );
    }
}

#[cfg(unix)]
#[derive(Debug)]
struct JcodeWorkspace {
    root: Arc<JcodeWorkspaceRoot>,
    name: String,
    path: PathBuf,
    dir: File,
    identity: DirectoryIdentity,
    exposed: bool,
    finished: bool,
}

#[cfg(unix)]
impl JcodeWorkspace {
    fn create() -> Result<Self> {
        Self::create_in(jcode_workspace_root()?)
    }

    fn create_in(root: Arc<JcodeWorkspaceRoot>) -> Result<Self> {
        Self::create_in_with_cap(root, MAX_JCODE_WORKSPACE_ENTRIES)
    }

    fn create_in_with_cap(root: Arc<JcodeWorkspaceRoot>, cap: usize) -> Result<Self> {
        if cap == 0 {
            bail!("private Jcode workspace directory cap must be positive")
        }
        with_jcode_workspace_root_lock(&root, || {
            root.path_is_bound()?;
            let entry_count = directory_entry_count(&root.path, cap)?;
            root.path_is_bound()?;
            if entry_count >= cap {
                bail!(
                    "private Jcode workspace directory cap reached ({cap}); retained workspaces require manual review"
                )
            }
            for _ in 0..32 {
                let name = random_jcode_workspace_name("session")?;
                let name_c = std::ffi::CString::new(name.as_str())?;
                let made = unsafe { libc::mkdirat(root.dir.as_raw_fd(), name_c.as_ptr(), 0o700) };
                if made != 0 {
                    let error = std::io::Error::last_os_error();
                    if error.kind() == std::io::ErrorKind::AlreadyExists {
                        continue;
                    }
                    return Err(error).context("create private Jcode workspace");
                }
                let allocated = (|| -> Result<(File, DirectoryIdentity)> {
                    let dir = open_child_directory(&root.dir, &name)?;
                    if unsafe { libc::fchmod(dir.as_raw_fd(), 0o700) } != 0 {
                        return Err(std::io::Error::last_os_error())
                            .context("permission private Jcode workspace");
                    }
                    let meta = dir.metadata()?;
                    let identity = directory_identity(&meta);
                    verify_private_directory(&meta, identity)?;
                    Ok((dir, identity))
                })();
                match allocated {
                    Ok((dir, identity)) => {
                        return Ok(Self {
                            path: root.path.join(&name),
                            root: Arc::clone(&root),
                            name,
                            dir,
                            identity,
                            exposed: false,
                            finished: false,
                        });
                    }
                    Err(error) => {
                        cleanup_failed_jcode_allocation(&root, &name);
                        return Err(error);
                    }
                }
            }
            bail!("could not allocate exclusive private Jcode workspace")
        })
    }

    fn binding_is_current(&self) -> Result<bool> {
        let held = self.dir.metadata()?;
        if verify_private_directory(&held, self.identity).is_err() {
            return Ok(false);
        }
        let current = match open_child_directory(&self.root.dir, &self.name) {
            Ok(current) => current,
            Err(_) => return Ok(false),
        };
        if verify_private_directory(&current.metadata()?, self.identity).is_err() {
            return Ok(false);
        }
        let path = match open_directory_nofollow(&self.path) {
            Ok(path) => path,
            Err(_) => return Ok(false),
        };
        Ok(verify_private_directory(&path.metadata()?, self.identity).is_ok())
    }

    fn create_session_request(&self) -> Result<serde_json::Value> {
        self.create_session_request_for_cwd(&env::current_dir()?)
    }

    fn create_session_request_for_cwd(&self, task_cwd: &Path) -> Result<serde_json::Value> {
        let root = Arc::clone(&self.root);
        with_jcode_workspace_root_lock(&root, || {
            if !self.binding_is_current()? {
                bail!("private Jcode workspace binding changed before session creation")
            }
            if directory_entry_count(&self.path, 1)? != 0 {
                bail!("private Jcode workspace is not empty before session creation")
            }
            if !self.binding_is_current()? {
                bail!("private Jcode workspace binding changed during session creation")
            }
            ensure_jcode_workspace_outside_task_cwd(&self.path, task_cwd)?;
            if !self.binding_is_current()? {
                bail!("private Jcode workspace binding changed during cwd isolation check")
            }
            Ok(serde_json::json!({"req":"create_session","working_dir":self.path}))
        })
    }

    fn mark_exposed(&mut self) {
        self.exposed = true;
    }

    fn finish(&mut self, archive_confirmed: bool) -> JcodeWorkspaceFinish {
        if self.finished {
            return JcodeWorkspaceFinish::Retained(JcodeWorkspaceRetentionReason::CleanupError);
        }
        let root = Arc::clone(&self.root);
        let outcome = with_jcode_workspace_root_lock(&root, || {
            if self.exposed && !archive_confirmed {
                return Ok(JcodeWorkspaceFinish::Retained(
                    JcodeWorkspaceRetentionReason::ArchiveUnconfirmed,
                ));
            }
            if !self.binding_is_current()? {
                return Ok(JcodeWorkspaceFinish::Retained(
                    JcodeWorkspaceRetentionReason::BindingChanged,
                ));
            }
            if directory_entry_count(&self.path, 1)? != 0 {
                return Ok(JcodeWorkspaceFinish::Retained(
                    JcodeWorkspaceRetentionReason::Nonempty,
                ));
            }
            if !self.binding_is_current()? {
                return Ok(JcodeWorkspaceFinish::Retained(
                    JcodeWorkspaceRetentionReason::BindingChanged,
                ));
            }
            if unlink_empty_jcode_workspace(&self.root, &self.name).is_err() {
                return Ok(JcodeWorkspaceFinish::Retained(
                    JcodeWorkspaceRetentionReason::CleanupError,
                ));
            }
            Ok(JcodeWorkspaceFinish::Removed)
        })
        .unwrap_or(JcodeWorkspaceFinish::Retained(
            JcodeWorkspaceRetentionReason::CleanupError,
        ));
        self.finished = true;
        if let JcodeWorkspaceFinish::Retained(reason) = outcome {
            warn_retained_jcode_workspace(&self.path, reason);
        }
        outcome
    }
}

#[cfg(unix)]
impl Drop for JcodeWorkspace {
    fn drop(&mut self) {
        if !self.finished {
            let _ = self.finish(false);
        }
    }
}

/// A spawned adapter remains in custody until its entire process group has been killed and its
/// direct child has been waited. Dropping this guard is the unwind/error backstop.
struct CustodiedChild {
    child: std::process::Child,
    finished: bool,
}

impl CustodiedChild {
    fn new(child: std::process::Child) -> Self {
        Self {
            child,
            finished: false,
        }
    }

    fn child_mut(&mut self) -> &mut std::process::Child {
        &mut self.child
    }

    fn terminate_and_reap(&mut self) -> std::io::Result<std::process::ExitStatus> {
        if self.finished {
            return self.child.wait();
        }

        #[cfg(unix)]
        {
            // The child is the process-group leader. This is deliberately done even after the
            // direct child exited: background descendants can still own its stdout/stderr/stdin
            // pipe ends and would otherwise make reader/writer joins hang indefinitely.
            let result = unsafe { libc::kill(-(self.child.id() as i32), libc::SIGKILL) };
            if result != 0 {
                let error = std::io::Error::last_os_error();
                if error.raw_os_error() != Some(libc::ESRCH) {
                    self.finished = self.child.wait().is_ok();
                    return Err(error);
                }
            }
        }
        #[cfg(not(unix))]
        {
            // std does not provide a portable descendant-tree primitive. The direct child is
            // still terminated and reaped; the documented POSIX group guarantee is Unix-only.
            let _ = self.child.kill();
        }

        let status = self.child.wait();
        self.finished = status.is_ok();
        status
    }

    /// Release the long-lived private bridge only after its socket is ready.
    #[cfg(unix)]
    fn release(mut self) {
        self.finished = true;
    }
}

impl Drop for CustodiedChild {
    fn drop(&mut self) {
        if !self.finished {
            let _ = self.terminate_and_reap();
        }
    }
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
        credential_profile: home.join("credential-target"),
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
fn jcode_auth_path(user_home: &Path, explicit_home: Option<PathBuf>) -> Result<PathBuf> {
    let source_home = strict_absolute_override_value("JCODE_HOME", explicit_home)?
        .unwrap_or_else(|| user_home.join(".jcode"));
    Ok(source_home.join("openai-auth.json"))
}

#[cfg(unix)]
fn validate_jcode_auth(auth: &Path) -> Result<PathBuf> {
    if !auth.is_file() {
        bail!(
            "OpenAI subscription OAuth login missing: {}",
            auth.display()
        )
    }
    use std::os::unix::fs::MetadataExt;
    let auth_meta = fs::metadata(auth)?;
    if auth_meta.mode() & 0o077 != 0 || auth_meta.uid() != unsafe { libc::geteuid() } {
        bail!("OpenAI OAuth credential must be owner-only and owned by the current user")
    }
    fs::canonicalize(auth).context("could not canonicalize selected Jcode OAuth credential")
}

#[cfg(unix)]
fn jcode_bridge_profile_matches(paths: &BridgePaths, canonical_auth: &Path) -> Result<bool> {
    use std::os::unix::ffi::OsStrExt;
    let auth_link = paths.home.join("openai-auth.json");
    let metadata = match fs::symlink_metadata(&auth_link) {
        Ok(metadata) => metadata,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false),
        Err(error) => return Err(error.into()),
    };
    if !metadata.file_type().is_symlink() {
        bail!("refusing non-symlink credential in private Jcode home")
    }
    if fs::canonicalize(&auth_link)? != canonical_auth {
        return Ok(false);
    }
    let Some(profile) = read_regular_nofollow(&paths.credential_profile)? else {
        return Ok(false);
    };
    Ok(profile == canonical_auth.as_os_str().as_bytes())
}

#[cfg(unix)]
fn prepare_jcode_bridge_profile(
    paths: &BridgePaths,
    auth: &Path,
    canonical_auth: &Path,
) -> Result<()> {
    use std::os::unix::ffi::OsStrExt;
    let auth_link = paths.home.join("openai-auth.json");
    match fs::symlink_metadata(&auth_link) {
        Ok(metadata) => {
            if !metadata.file_type().is_symlink() {
                bail!("refusing non-symlink credential in private Jcode home")
            }
            if fs::canonicalize(&auth_link)? != canonical_auth {
                fs::remove_file(&auth_link)?;
                std::os::unix::fs::symlink(auth, &auth_link)?;
            }
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            std::os::unix::fs::symlink(auth, &auth_link)?;
        }
        Err(error) => return Err(error.into()),
    }
    if fs::canonicalize(&auth_link)? != canonical_auth {
        bail!("private Jcode OAuth link does not target the selected credential")
    }
    atomic_write(
        &paths.credential_profile,
        canonical_auth.as_os_str().as_bytes(),
    )?;
    Ok(())
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
    let user_home = env::var_os("HOME")
        .map(PathBuf::from)
        .ok_or_else(|| anyhow!("HOME is required for subscription OAuth"))?;
    let auth = jcode_auth_path(&user_home, env::var_os("JCODE_HOME").map(PathBuf::from))?;
    let canonical_auth = validate_jcode_auth(&auth)?;
    let paths = bridge_paths()?;
    if socket_alive(&paths.socket) {
        if jcode_bridge_profile_matches(&paths, &canonical_auth)? {
            return Ok(paths.socket);
        }
        bail!("live private Jcode API bridge belongs to a different credential profile")
    }
    let _guard = lock_path(&state_home()?.join("jcode-api.lock"))?;
    if socket_alive(&paths.socket) {
        if jcode_bridge_profile_matches(&paths, &canonical_auth)? {
            return Ok(paths.socket);
        }
        bail!("live private Jcode API bridge belongs to a different credential profile")
    }
    match fs::remove_file(&paths.socket) {
        Ok(()) => {}
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
        Err(error) => return Err(error.into()),
    }
    prepare_jcode_bridge_profile(&paths, &auth, &canonical_auth)?;
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
    let child = cmd
        .spawn()
        .context("failed to start private Jcode API bridge")?;
    let mut child = CustodiedChild::new(child);
    atomic_write(
        &paths.pidfile,
        child.child_mut().id().to_string().as_bytes(),
    )?;
    let deadline = Instant::now() + Duration::from_secs(cfg.sub_timeout.min(30));
    while Instant::now() < deadline {
        if socket_alive(&paths.socket) {
            child.release();
            return Ok(paths.socket);
        }
        if let Some(status) = child.child_mut().try_wait()? {
            // The custody guard kills any bridge descendants before this error unwinds.
            bail!(
                "private Jcode API bridge exited before readiness ({status}); inspect {}",
                paths.home.join("logs").display()
            )
        }
        thread::sleep(Duration::from_millis(25))
    }
    child.terminate_and_reap()?;
    bail!(
        "private Jcode API bridge did not become ready; inspect {} (runtime marker {})",
        paths.home.join("logs").display(),
        paths.marker.display()
    )
}

#[cfg(unix)]
fn jcode_root_timeout(cfg: &Config) -> Duration {
    Duration::from_secs(cfg.sub_timeout.min(120))
}
#[cfg(unix)]
fn jcode_root_idle_timeout(cfg: &Config) -> Duration {
    Duration::from_secs(cfg.sub_timeout.min(60))
}
#[cfg(unix)]
fn jcode_batch_timeout(cfg: &Config, prompt_chars: usize) -> Duration {
    let cap = if prompt_chars >= 8_000 { 90 } else { 45 };
    Duration::from_secs(cfg.sub_timeout.min(cap))
}

#[cfg(unix)]
fn rounded_socket_timeout(remaining: Duration) -> Duration {
    let millis = remaining.as_millis();
    let has_fractional_millisecond = !remaining.subsec_nanos().is_multiple_of(1_000_000);
    let rounded = millis.saturating_add(u128::from(has_fractional_millisecond));
    Duration::from_millis(rounded.min(u128::from(u64::MAX)) as u64)
}

#[cfg(unix)]
#[derive(Debug, Clone, Copy)]
struct TurnDeadline {
    hard_deadline: Instant,
    idle_deadline: Instant,
    idle_timeout: Duration,
}
#[cfg(unix)]
impl TurnDeadline {
    fn new(started: Instant, hard_timeout: Duration, idle_timeout: Duration) -> Result<Self> {
        let hard_deadline = started
            .checked_add(hard_timeout)
            .ok_or_else(|| anyhow!("jcode subscription hard timeout is too large"))?;
        let idle_deadline = started
            .checked_add(idle_timeout)
            .ok_or_else(|| anyhow!("jcode subscription idle timeout is too large"))?;
        Ok(Self {
            hard_deadline,
            idle_deadline,
            idle_timeout,
        })
    }

    fn remaining(&self, now: Instant) -> Result<Duration> {
        let hard = self
            .hard_deadline
            .checked_duration_since(now)
            .filter(|remaining| !remaining.is_zero())
            .ok_or_else(|| anyhow!("jcode subscription turn hard deadline timed out"))?;
        let idle = self
            .idle_deadline
            .checked_duration_since(now)
            .filter(|remaining| !remaining.is_zero())
            .ok_or_else(|| anyhow!("jcode subscription turn idle deadline timed out"))?;
        Ok(hard.min(idle))
    }

    fn progress(&mut self, now: Instant) -> Result<()> {
        self.idle_deadline = now
            .checked_add(self.idle_timeout)
            .ok_or_else(|| anyhow!("jcode subscription idle timeout is too large"))?;
        Ok(())
    }
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
    idle_timeout: Duration,
    cancel_before_archive: bool,
    workspace: Option<JcodeWorkspace>,
}
#[cfg(unix)]
static SOLO_SHARED_JCODE: std::sync::Mutex<Option<JcodeSession>> = std::sync::Mutex::new(None);
#[cfg(all(test, unix))]
static SOLO_SHARED_JCODE_DRAINS: AtomicU32 = AtomicU32::new(0);

pub struct SoloJcodeLeaseGuard {
    armed: bool,
    session_id: Option<String>,
}
impl Drop for SoloJcodeLeaseGuard {
    fn drop(&mut self) {
        #[cfg(unix)]
        if self.armed {
            let mut slot = SOLO_SHARED_JCODE
                .lock()
                .unwrap_or_else(std::sync::PoisonError::into_inner);
            let matches = slot
                .as_ref()
                .is_some_and(|api| self.session_id.as_deref() == Some(api.session.as_str()));
            let shared = if matches { slot.take() } else { None };
            #[cfg(test)]
            if shared.is_some() {
                SOLO_SHARED_JCODE_DRAINS.fetch_add(1, Ordering::AcqRel);
            }
            drop(shared);
        }
    }
}

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
        let timeout = Duration::from_secs(cfg.sub_timeout);
        Self::open_with_timeout(cfg, model, timeout, timeout, observation)
    }
    fn open_for_root(
        cfg: &Config,
        model: &str,
        observation: &mut JcodeSetupObservation,
    ) -> Result<Self> {
        Self::open_with_timeout(
            cfg,
            model,
            jcode_root_timeout(cfg),
            jcode_root_idle_timeout(cfg),
            observation,
        )
    }
    fn open_for_batch(
        cfg: &Config,
        model: &str,
        prompt_chars: usize,
        observation: &mut JcodeSetupObservation,
    ) -> Result<Self> {
        let timeout = jcode_batch_timeout(cfg, prompt_chars);
        Self::open_with_timeout(cfg, model, timeout, timeout, observation)
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
        idle_timeout: Duration,
        observation: &mut JcodeSetupObservation,
    ) -> Result<Self> {
        observation.substage = ModelSetupSubstage::Connect;
        let socket = ensure_jcode_bridge(cfg)?;
        let stream = UnixStream::connect(&socket)?;
        let workspace = JcodeWorkspace::create()?;
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
            idle_timeout,
            cancel_before_archive: true,
            workspace: Some(workspace),
        };
        let setup_deadline = Instant::now() + Duration::from_secs(12);
        observation.substage = ModelSetupSubstage::Hello;
        let id=this.send(serde_json::json!({"req":"hello","min_version":1,"max_version":1,"client":format!("azdaja/{VERSION}")}))?;
        this.reply_before(id, "hello_ok", setup_deadline)
            .context("jcode hello setup")?;
        observation.substage = ModelSetupSubstage::Attach;
        let create_session = this
            .workspace
            .as_ref()
            .ok_or_else(|| anyhow!("private Jcode workspace unavailable"))?
            .create_session_request()?;
        this.workspace
            .as_mut()
            .ok_or_else(|| anyhow!("private Jcode workspace unavailable"))?
            .mark_exposed();
        let id = this.send(create_session)?;
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
        const MAX_PENDING_PERMISSION_RESPONSES: usize = 64;

        let started = Instant::now();
        self.usage = ModelUsage::default();
        self.usage_observed = false;
        let sid = self.session.clone();
        self.send(
            serde_json::json!({"req":"send_message","session_id":sid,"content":prompt,"images":[]}),
        )?;
        let mut text = String::new();
        let mut pending_permission_responses = VecDeque::new();
        let mut turn_complete = false;
        let mut deadline = TurnDeadline::new(started, self.timeout, self.idle_timeout)?;
        loop {
            let remaining = deadline.remaining(Instant::now())?;
            // Darwin can reject fractional timeouts near a timeval boundary. Ceiling to an exact
            // millisecond preserves the deadline to within 1 ms and always keeps it nonzero.
            self.stream
                .set_read_timeout(Some(rounded_socket_timeout(remaining)))
                .with_context(|| format!("setting jcode turn read timeout {remaining:?}"))?;
            let f = self.frame()?;
            let event = f.get("ev").and_then(serde_json::Value::as_str);
            // Flat errors are connection-scoped. In particular, do not wait for a timeout merely
            // because a permission response error omitted the session ID.
            if event == Some("error") {
                return Err(jcode_frame_error(&f));
            }

            let reply_to = f.get("reply_to").and_then(serde_json::Value::as_u64);
            let permission_reply = reply_to.and_then(|id| {
                pending_permission_responses
                    .iter()
                    .position(|pending| *pending == id)
            });
            let mut made_progress = false;
            if let Some(position) = permission_reply {
                if event != Some("ok") {
                    bail!("jcode API returned an invalid permission response acknowledgement")
                }
                pending_permission_responses.remove(position);
                made_progress = true;
            } else if f.get("session_id").and_then(serde_json::Value::as_str) == Some(&self.session)
            {
                match event {
                    Some("text_delta") => {
                        let delta = f
                            .get("text")
                            .and_then(serde_json::Value::as_str)
                            .unwrap_or("");
                        if text.len().saturating_add(delta.len()) > 16 * 1024 * 1024 {
                            bail!("jcode model response exceeds 16 MiB")
                        }
                        text.push_str(delta);
                        made_progress = true;
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
                            .unwrap_or(0);
                        made_progress = true;
                    }
                    Some("permission_request") => {
                        if pending_permission_responses.len() >= MAX_PENDING_PERMISSION_RESPONSES {
                            bail!(
                                "jcode permission response limit exceeded ({MAX_PENDING_PERMISSION_RESPONSES})"
                            )
                        }
                        let request_id = f
                            .get("request_id")
                            .and_then(serde_json::Value::as_str)
                            .filter(|value| !value.is_empty())
                            .ok_or_else(|| {
                                anyhow!("jcode permission request omitted request id")
                            })?;
                        let id = self.send(serde_json::json!({
                            "req":"permission_response",
                            "session_id":self.session,
                            "request_id":request_id,
                            "decision":"deny"
                        }))?;
                        pending_permission_responses.push_back(id);
                        made_progress = true;
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
                            .into();
                        made_progress = true;
                    }
                    Some("turn_done") => {
                        turn_complete = true;
                        made_progress = true;
                    }
                    _ => {}
                }
            }

            if made_progress {
                deadline.progress(Instant::now())?;
            }
            // A turn_done may race ahead of the correlated permission acknowledgement. Keep
            // dispatching same-session deltas and usage until every explicit deny is confirmed.
            if turn_complete && pending_permission_responses.is_empty() {
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
        }
    }
}
#[cfg(unix)]
impl Drop for JcodeSession {
    fn drop(&mut self) {
        let sid = self.session.clone();
        let mut archive_confirmed = false;
        if !sid.is_empty() {
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
            if let Ok(id) = self.send(serde_json::json!({"req":"archive_session","session_id":sid}))
            {
                archive_confirmed = self.reply_with_timeout(id, "ok", CLEANUP_TIMEOUT).is_ok();
            }
        }
        if let Some(mut workspace) = self.workspace.take() {
            let _ = workspace.finish(archive_confirmed);
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

    pub fn repair_turn(&mut self, prompt: &str, repair_index: u32) -> Result<ModelReply> {
        preflight_model_trace_sink()?;
        if !(1..=3).contains(&repair_index) {
            bail!("root repair index must be between 1 and 3")
        }
        let repair_request_id = format!("{}-repair-{repair_index}", self.request_id);
        #[cfg(unix)]
        if let Some(api) = &mut self.api {
            let entered_turn = self.entered_turn_budget.try_enter()?;
            let started = Instant::now();
            let reply = match api.turn(prompt) {
                Ok(reply) => reply,
                Err(error) => {
                    api.discard();
                    record_model_trace_result(trace_model_repair_failure(
                        &repair_request_id,
                        entered_turn,
                        Some(&api.session),
                        &error,
                        Some(started.elapsed().as_millis()),
                    ));
                    return Err(error);
                }
            };
            trace_model_repair_reply(
                &reply,
                &repair_request_id,
                entered_turn,
                Some(&api.session),
                api.usage_observed,
            );
            return Ok(reply);
        }
        self.history.push_str(prompt);
        let entered_turn = self.entered_turn_budget.try_enter()?;
        let started = Instant::now();
        let text = match call_model_command(&self.history, &self.model, &self.cfg, 0) {
            Ok(text) => text,
            Err(error) => {
                record_model_trace_result(trace_model_repair_failure(
                    &repair_request_id,
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
            model: self.model.clone(),
            latency_ms: started.elapsed().as_millis(),
        };
        trace_model_repair_reply(&reply, &repair_request_id, entered_turn, None, false);
        self.history.push_str("\n\nAssistant:\n");
        self.history.push_str(&reply.text);
        self.history.push_str("\n\nUser:\n");
        Ok(reply)
    }

    pub fn session_id(&self) -> Option<&str> {
        #[cfg(unix)]
        if let Some(api) = &self.api {
            return Some(&api.session);
        }
        None
    }

    pub fn lend_to_solo(&mut self) -> Result<SoloJcodeLeaseGuard> {
        #[cfg(unix)]
        if self.cfg.sub_llm_cmd == "jcode-api" {
            let mut api = self
                .api
                .take()
                .ok_or_else(|| anyhow!("root subscription session unavailable"))?;
            api.timeout = Duration::from_secs(self.cfg.sub_timeout.min(90));
            api.idle_timeout = Duration::from_secs(self.cfg.sub_timeout.min(30));
            let session_id = api.session.clone();
            let mut slot = SOLO_SHARED_JCODE.lock().unwrap();
            if slot.is_some() {
                bail!("solo subscription session already lent")
            }
            *slot = Some(api);
            return Ok(SoloJcodeLeaseGuard {
                armed: true,
                session_id: Some(session_id),
            });
        }
        Ok(SoloJcodeLeaseGuard {
            armed: true,
            session_id: None,
        })
    }
    pub fn reclaim_from_solo(&mut self, mut guard: SoloJcodeLeaseGuard) -> Result<bool> {
        #[cfg(unix)]
        if self.cfg.sub_llm_cmd == "jcode-api" {
            let mut slot = SOLO_SHARED_JCODE.lock().unwrap();
            let matches = slot
                .as_ref()
                .is_some_and(|api| guard.session_id.as_deref() == Some(api.session.as_str()));
            if !matches {
                guard.armed = false;
                return Ok(false);
            }
            let mut api = slot
                .take()
                .ok_or_else(|| anyhow!("solo lease disappeared"))?;
            api.timeout = jcode_root_timeout(&self.cfg);
            api.idle_timeout = jcode_root_idle_timeout(&self.cfg);
            self.api = Some(api);
        }
        guard.armed = false;
        Ok(true)
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

fn ensure_private_model_trace_file(file: &File, path: &Path) -> Result<()> {
    let metadata = file.metadata()?;
    if !metadata.file_type().is_file() {
        bail!("model trace sink is not a regular file")
    }
    #[cfg(unix)]
    {
        use std::os::unix::fs::{MetadataExt, PermissionsExt};
        let path_metadata = fs::symlink_metadata(path)?;
        if path_metadata.file_type().is_symlink()
            || !path_metadata.file_type().is_file()
            || path_metadata.dev() != metadata.dev()
            || path_metadata.ino() != metadata.ino()
            || metadata.uid() != unsafe { libc::geteuid() }
            || metadata.nlink() != 1
            || metadata.permissions().mode() & 0o077 != 0
        {
            bail!("model trace sink is not a private bound file")
        }
    }
    Ok(())
}

fn open_model_trace_sink() -> Result<Option<File>> {
    let Some(path) = env::var_os("AZDAJA_MODEL_TRACE").map(PathBuf::from) else {
        return Ok(None);
    };
    let mut options = OpenOptions::new();
    options.create(true).append(true);
    #[cfg(unix)]
    options
        .mode(0o600)
        .custom_flags(libc::O_NOFOLLOW | libc::O_NONBLOCK);
    let file = options.open(&path)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        if file.metadata()?.permissions().mode() & 0o077 != 0 {
            file.set_permissions(fs::Permissions::from_mode(0o600))?;
        }
    }
    ensure_private_model_trace_file(&file, &path)?;
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
                ModelAttemptCategory::Repair => "repair",
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
    // Command transports cannot report a provider, but `reply.model` still holds the
    // exact requested model substituted into the managed command. Preserve it so
    // semantic-worker parity is auditable without claiming provider-side identity.
    let known_model = !reply.model.trim().is_empty();
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
        model: known_model.then(|| reply.model.clone()),
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

fn trace_model_repair_failure(
    request_id: &str,
    entered_turn: u32,
    session_id: Option<&str>,
    error: &anyhow::Error,
    latency_ms: Option<u128>,
) -> Result<()> {
    trace_model_failure_attempt(
        ModelAttemptContext {
            depth: 0,
            request_id,
            attempt: 1,
            entered_turn: Some(entered_turn),
            session_id,
            latency_ms,
        },
        ModelAttemptCategory::Repair,
        None,
        model_transport_error_category(error),
    )
}

fn trace_model_repair_reply(
    reply: &ModelReply,
    request_id: &str,
    entered_turn: u32,
    session_id: Option<&str>,
    usage_observed: bool,
) {
    let known_provider = !reply.provider.trim().is_empty();
    let known_model = !reply.model.trim().is_empty();
    let known_usage = known_provider && usage_observed;
    record_model_trace(&ModelTrace {
        schema_version: MODEL_TRACE_SCHEMA_VERSION,
        event: ModelTraceEvent::ModelAttempt,
        timestamp_ms: now_ms(),
        depth: 0,
        request_id: request_id.to_owned(),
        attempt: 1,
        entered_turn: Some(entered_turn),
        session_id: session_id.map(str::to_owned),
        category: ModelAttemptCategory::Repair,
        outcome: ModelAttemptOutcome::Succeeded,
        error: None,
        error_category: None,
        stage: Some("repair".into()),
        setup_substage: None,
        provider: known_provider.then(|| reply.provider.clone()),
        model: known_model.then(|| reply.model.clone()),
        input_tokens: known_usage.then_some(reply.usage.input),
        output_tokens: known_usage.then_some(reply.usage.output),
        cache_read_tokens: known_usage.then_some(reply.usage.cache_read),
        latency_ms: Some(reply.latency_ms),
        degraded_transport: Some(false),
        failed_attempts_before_success: Some(0),
        response: None,
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
    let prompt_file = if cfg.sub_llm_cmd.contains("{prompt_file}") {
        let dir = state_home()?.join("prompts");
        secure_dir(&dir)?;
        let nanos = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_nanos();
        let mut made = None;
        for salt in 0..100u8 {
            let path = dir.join(format!("{}-{nanos}-{salt}.txt", std::process::id()));
            match create_private_file(&path) {
                Ok(mut file) => {
                    file.write_all(prompt.as_bytes())?;
                    validate_private_file(&file, &path)?;
                    made = Some((path, file));
                    break;
                }
                Err(error)
                    if error
                        .downcast_ref::<std::io::Error>()
                        .is_some_and(|error| error.kind() == std::io::ErrorKind::AlreadyExists) =>
                {
                    continue;
                }
                Err(error) => return Err(error),
            }
        }
        Some(made.ok_or_else(|| anyhow!("could not allocate prompt file"))?)
    } else {
        None
    };
    let result = call_model_inner(
        prompt,
        prompt_file.as_ref().map(|(path, _)| path.as_path()),
        model,
        cfg,
        depth,
    );
    if let Some((path, file)) = prompt_file {
        remove_bound_file(&path, &file);
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
    install_provider_interrupt_handler()?;
    let child = command
        .spawn()
        .with_context(|| format!("failed to start {program}"))?;
    let mut child = CustodiedChild::new(child);
    let out = child.child_mut().stdout.take().unwrap();
    let err = child.child_mut().stderr.take().unwrap();
    let out_thread = thread::spawn(move || drain_limited(out, 16 * 1024 * 1024));
    let err_thread = thread::spawn(move || drain_limited(err, 1024 * 1024));
    let input_thread = child.child_mut().stdin.take().map(|mut input| {
        let bytes = prompt.as_bytes().to_vec();
        thread::spawn(move || input.write_all(&bytes))
    });
    let deadline = Instant::now() + Duration::from_secs(cfg.sub_timeout);
    let mut timed_out = false;
    let mut interrupted = false;
    let mut wait_error = None;
    loop {
        if interrupt_requested() {
            interrupted = true;
            break;
        }
        match child.child_mut().try_wait() {
            Ok(Some(_)) => break,
            Ok(None) if Instant::now() >= deadline => {
                timed_out = true;
                break;
            }
            Ok(None) => thread::sleep(Duration::from_millis(10)),
            Err(error) => {
                wait_error = Some(error);
                break;
            }
        }
    }

    // Always close custody before joining any pipe worker. In particular, a successful or failed
    // direct parent is not enough: its background descendants can inherit all three pipe ends.
    let custody_result = child.terminate_and_reap();
    let input_result = input_thread
        .map(|worker| worker.join().map_err(|_| anyhow!("stdin writer panicked")))
        .transpose();
    let stdout_result = out_thread
        .join()
        .map_err(|_| anyhow!("stdout reader panicked"));
    let stderr_result = err_thread
        .join()
        .map_err(|_| anyhow!("stderr reader panicked"));

    // Signal and deadline outcomes retain their exact public contract even when terminating the
    // provider caused the expected BrokenPipe in the input worker.
    if interrupted {
        mark_provider_interrupted();
        bail!("provider interrupted")
    }
    if timed_out {
        bail!("sub-LLM timed out after {}s", cfg.sub_timeout)
    }
    if let Some(error) = wait_error {
        return Err(error.into());
    }
    let status = custody_result?;
    let input_result = input_result?;
    let (stdout, out_over) = stdout_result??;
    let (stderr, err_over) = stderr_result??;
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
    fn shipped_default_config_matches_sixty_second_evaluator_cap() {
        let shipped: Config = toml::from_str(DEFAULT_CONFIG).unwrap();
        assert_eq!(Config::default().cell_timeout, 60);
        assert_eq!(shipped.cell_timeout, Config::default().cell_timeout);
    }

    #[cfg(unix)]
    #[test]
    fn explicit_absolute_jcode_home_is_authoritative_and_relative_values_fail_closed() {
        let user_home = Path::new("/private/test-home-a");
        let explicit = PathBuf::from("/private/test-home-b");
        assert_eq!(
            jcode_auth_path(user_home, Some(explicit.clone())).unwrap(),
            explicit.join("openai-auth.json")
        );
        assert_eq!(
            jcode_auth_path(user_home, None).unwrap(),
            user_home.join(".jcode/openai-auth.json")
        );
        for invalid in [PathBuf::new(), PathBuf::from("relative-jcode-home")] {
            let error = jcode_auth_path(user_home, Some(invalid)).unwrap_err();
            assert!(error.to_string().contains("non-empty absolute path"));
        }

        let root = env::temp_dir().join(format!(
            "azdaja-jcode-auth-routing-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let home_a = root.join("a");
        let home_b = root.join("b");
        fs::create_dir_all(home_a.join(".jcode")).unwrap();
        fs::create_dir_all(&home_b).unwrap();
        fs::write(home_a.join(".jcode/openai-auth.json"), b"owner-a").unwrap();
        let selected = jcode_auth_path(&home_a, Some(home_b.clone())).unwrap();
        assert_eq!(selected, home_b.join("openai-auth.json"));
        assert!(
            !selected.exists(),
            "must not fall back across Jcode profiles"
        );
        fs::write(&selected, b"owner-b").unwrap();
        assert_eq!(fs::read(&selected).unwrap(), b"owner-b");
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&selected, fs::Permissions::from_mode(0o600)).unwrap();
        let auth_a = home_a.join(".jcode/openai-auth.json");
        fs::set_permissions(&auth_a, fs::Permissions::from_mode(0o600)).unwrap();
        let canonical_a = validate_jcode_auth(&auth_a).unwrap();
        let canonical_b = validate_jcode_auth(&selected).unwrap();
        let bridge_home = root.join("bridge-home");
        fs::create_dir(&bridge_home).unwrap();
        fs::set_permissions(&bridge_home, fs::Permissions::from_mode(0o700)).unwrap();
        let paths = BridgePaths {
            socket: root.join("api.sock"),
            pidfile: root.join("bridge.pid"),
            home: bridge_home.clone(),
            run: root.join("run"),
            marker: root.join("runtime-dir"),
            credential_profile: bridge_home.join("credential-target"),
        };
        prepare_jcode_bridge_profile(&paths, &auth_a, &canonical_a).unwrap();
        assert!(jcode_bridge_profile_matches(&paths, &canonical_a).unwrap());
        assert!(!jcode_bridge_profile_matches(&paths, &canonical_b).unwrap());
        prepare_jcode_bridge_profile(&paths, &selected, &canonical_b).unwrap();
        assert!(jcode_bridge_profile_matches(&paths, &canonical_b).unwrap());
        assert!(!jcode_bridge_profile_matches(&paths, &canonical_a).unwrap());
        assert_eq!(
            fs::canonicalize(bridge_home.join("openai-auth.json")).unwrap(),
            canonical_b
        );
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn monty_failure_kinds_separate_program_bugs_from_resource_and_host_classes() {
        for ordinary in [
            ExcType::IndexError,
            ExcType::TypeError,
            ExcType::AttributeError,
            ExcType::NameError,
            ExcType::ZeroDivisionError,
            ExcType::JsonDecodeError,
            ExcType::SyntaxError,
        ] {
            assert!(matches!(
                exec_failure_kind(Some(ordinary)),
                ExecFailureKind::Index | ExecFailureKind::Program
            ));
        }
        assert_eq!(
            exec_failure_kind(Some(ExcType::Exception)),
            ExecFailureKind::Program
        );
        for (infrastructure, expected) in [
            (ExcType::BaseException, ExecFailureKind::Other),
            (ExcType::RuntimeError, ExecFailureKind::Other),
            (ExcType::OSError, ExecFailureKind::Other),
            (ExcType::PermissionError, ExecFailureKind::Other),
            (ExcType::TimeoutError, ExecFailureKind::Timeout),
            (ExcType::MemoryError, ExecFailureKind::Memory),
            (ExcType::RecursionError, ExecFailureKind::Recursion),
            (ExcType::SystemExit, ExecFailureKind::Other),
        ] {
            assert_eq!(exec_failure_kind(Some(infrastructure)), expected);
        }
    }

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
    fn jcode_workspace_test_root(label: &str) -> (PathBuf, Arc<JcodeWorkspaceRoot>) {
        let path = env::temp_dir().join(format!(
            "azdaja-jcode-{label}-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let root = Arc::new(JcodeWorkspaceRoot::open(&path).unwrap());
        (path, root)
    }

    #[test]
    fn create_session_cwd_is_bound_private_empty_and_not_task_cwd() {
        use std::os::unix::fs::MetadataExt;
        let (root_path, root) = jcode_workspace_test_root("wire");
        let mut workspace = JcodeWorkspace::create_in(root).unwrap();
        let request = workspace.create_session_request().unwrap();
        workspace.mark_exposed();
        assert_eq!(request["req"], "create_session");
        let cwd = PathBuf::from(request["working_dir"].as_str().unwrap());
        assert!(cwd.is_absolute());
        assert!(cwd.starts_with(&root_path));
        assert!(
            ensure_jcode_workspace_outside_task_cwd(&cwd, &env::current_dir().unwrap()).is_ok()
        );
        assert!(ensure_jcode_workspace_outside_task_cwd(&cwd, &env::temp_dir()).is_err());
        let meta = fs::symlink_metadata(&cwd).unwrap();
        assert!(meta.file_type().is_dir());
        assert!(!meta.file_type().is_symlink());
        assert_eq!(meta.uid(), unsafe { libc::geteuid() });
        assert_eq!(meta.mode() & 0o777, 0o700);
        assert!(fs::read_dir(&cwd).unwrap().next().is_none());
        assert_eq!(workspace.finish(true), JcodeWorkspaceFinish::Removed);
        assert!(!cwd.exists());
        fs::remove_dir(root_path).unwrap();
    }

    #[test]
    fn local_cwd_containment_rejection_removes_unexposed_workspace() {
        let (root_path, root) = jcode_workspace_test_root("cwd-reject");
        let mut workspace = JcodeWorkspace::create_in(root).unwrap();
        assert!(
            workspace
                .create_session_request_for_cwd(&env::temp_dir())
                .is_err()
        );
        assert!(!workspace.exposed);
        assert_eq!(workspace.finish(false), JcodeWorkspaceFinish::Removed);
        assert_eq!(directory_entry_count(&root_path, 1).unwrap(), 0);
        fs::remove_dir(root_path).unwrap();
    }

    #[test]
    fn jcode_workspace_retains_nonempty_and_archive_uncertain_evidence() {
        let (root_path, root) = jcode_workspace_test_root("retain");
        let mut nonempty = JcodeWorkspace::create_in(Arc::clone(&root)).unwrap();
        let nonempty_path = nonempty.path.clone();
        nonempty.create_session_request().unwrap();
        nonempty.mark_exposed();
        fs::write(nonempty_path.join("provider-side-effect"), b"retained").unwrap();
        assert_eq!(
            nonempty.finish(true),
            JcodeWorkspaceFinish::Retained(JcodeWorkspaceRetentionReason::Nonempty)
        );
        assert_eq!(
            fs::read(nonempty_path.join("provider-side-effect")).unwrap(),
            b"retained"
        );

        let mut uncertain = JcodeWorkspace::create_in(root).unwrap();
        let uncertain_path = uncertain.path.clone();
        uncertain.create_session_request().unwrap();
        uncertain.mark_exposed();
        assert_eq!(
            uncertain.finish(false),
            JcodeWorkspaceFinish::Retained(JcodeWorkspaceRetentionReason::ArchiveUnconfirmed)
        );
        assert!(uncertain_path.is_dir());

        fs::remove_file(nonempty_path.join("provider-side-effect")).unwrap();
        fs::remove_dir(nonempty_path).unwrap();
        fs::remove_dir(uncertain_path).unwrap();
        fs::remove_dir(root_path).unwrap();
    }

    #[test]
    fn jcode_workspace_same_owner_substitution_never_deletes_or_renames() {
        let (root_path, root) = jcode_workspace_test_root("substitution");
        let mut workspace = JcodeWorkspace::create_in(root).unwrap();
        workspace.create_session_request().unwrap();
        workspace.mark_exposed();
        let requested_path = workspace.path.clone();
        let moved_original = root_path.join("moved-original");
        fs::rename(&requested_path, &moved_original).unwrap();
        fs::write(moved_original.join("original-must-survive"), b"original").unwrap();
        fs::create_dir(&requested_path).unwrap();
        chmod(&requested_path, 0o700).unwrap();
        fs::write(requested_path.join("must-survive"), b"substitute").unwrap();

        assert_eq!(
            workspace.finish(true),
            JcodeWorkspaceFinish::Retained(JcodeWorkspaceRetentionReason::BindingChanged)
        );
        assert_eq!(
            fs::read(moved_original.join("original-must-survive")).unwrap(),
            b"original"
        );
        assert_eq!(
            fs::read(requested_path.join("must-survive")).unwrap(),
            b"substitute"
        );

        fs::remove_file(moved_original.join("original-must-survive")).unwrap();
        fs::remove_dir(moved_original).unwrap();
        fs::remove_file(requested_path.join("must-survive")).unwrap();
        fs::remove_dir(requested_path).unwrap();
        fs::remove_dir(root_path).unwrap();
    }

    #[test]
    fn jcode_workspace_cap_is_atomic_and_empty_cleanup_frees_slots() {
        let (root_path, root) = jcode_workspace_test_root("cap");
        let mut threads = Vec::new();
        for _ in 0..8 {
            let root = Arc::clone(&root);
            threads.push(thread::spawn(move || {
                JcodeWorkspace::create_in_with_cap(root, 8).unwrap()
            }));
        }
        let mut workspaces: Vec<_> = threads
            .into_iter()
            .map(|thread| thread.join().unwrap())
            .collect();
        let names: std::collections::HashSet<_> =
            workspaces.iter().map(|workspace| &workspace.name).collect();
        assert_eq!(names.len(), 8);
        assert!(JcodeWorkspace::create_in_with_cap(Arc::clone(&root), 8).is_err());
        assert_eq!(workspaces[0].finish(false), JcodeWorkspaceFinish::Removed);
        let mut replacement = JcodeWorkspace::create_in_with_cap(root, 8).unwrap();
        assert_eq!(replacement.finish(false), JcodeWorkspaceFinish::Removed);
        for workspace in &mut workspaces[1..] {
            assert_eq!(workspace.finish(false), JcodeWorkspaceFinish::Removed);
        }
        fs::remove_dir(root_path).unwrap();
    }

    #[test]
    fn failed_local_allocation_cleanup_never_removes_nonempty_data() {
        let (root_path, root) = jcode_workspace_test_root("partial");
        let name = "session-injected-post-mkdir-failure";
        let path = root_path.join(name);
        fs::create_dir(&path).unwrap();
        chmod(&path, 0o700).unwrap();
        fs::write(path.join("must-survive"), b"partial").unwrap();
        cleanup_failed_jcode_allocation(&root, name);
        assert_eq!(fs::read(path.join("must-survive")).unwrap(), b"partial");
        fs::remove_file(path.join("must-survive")).unwrap();
        fs::remove_dir(path).unwrap();
        fs::remove_dir(root_path).unwrap();
    }

    #[test]
    fn jcode_workspace_root_rejects_nonprivate_mode() {
        let path = env::temp_dir().join(format!(
            "azdaja-jcode-mode-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir(&path).unwrap();
        chmod(&path, 0o755).unwrap();
        assert!(JcodeWorkspaceRoot::open(&path).is_err());
        fs::remove_dir(path).unwrap();
    }

    #[test]
    fn root_and_batch_timeouts_are_capped_without_changing_config() {
        let mut cfg = Config {
            sub_timeout: 300,
            ..Config::default()
        };
        assert_eq!(jcode_batch_timeout(&cfg, 20_000), Duration::from_secs(90));
        assert_eq!(jcode_batch_timeout(&cfg, 2_000), Duration::from_secs(45));
        assert_eq!(jcode_root_timeout(&cfg), Duration::from_secs(120));
        assert_eq!(jcode_root_idle_timeout(&cfg), Duration::from_secs(60));
        assert_eq!(cfg.sub_timeout, 300);
        cfg.sub_timeout = 12;
        assert_eq!(jcode_batch_timeout(&cfg, 20_000), Duration::from_secs(12));
        assert_eq!(jcode_batch_timeout(&cfg, 2_000), Duration::from_secs(12));
        assert_eq!(jcode_root_timeout(&cfg), Duration::from_secs(12));
        assert_eq!(jcode_root_idle_timeout(&cfg), Duration::from_secs(12));
    }

    #[test]
    fn socket_timeout_rounding_ceilings_fractional_milliseconds() {
        assert_eq!(
            rounded_socket_timeout(Duration::from_nanos(1)),
            Duration::from_millis(1)
        );
        assert_eq!(
            rounded_socket_timeout(Duration::from_millis(1)),
            Duration::from_millis(1)
        );
        assert_eq!(
            rounded_socket_timeout(Duration::from_nanos(29_999_432_917)),
            Duration::from_secs(30)
        );
        assert_eq!(
            rounded_socket_timeout(Duration::from_nanos(30_000_000_001)),
            Duration::from_millis(30_001)
        );
    }

    #[test]
    fn turn_deadline_times_out_when_idle_without_reaching_hard_cap() {
        let started = Instant::now();
        let deadline =
            TurnDeadline::new(started, Duration::from_secs(120), Duration::from_secs(60)).unwrap();
        assert_eq!(
            deadline
                .remaining(started + Duration::from_secs(59))
                .unwrap(),
            Duration::from_secs(1)
        );
        let error = deadline
            .remaining(started + Duration::from_secs(60))
            .unwrap_err()
            .to_string();
        assert!(error.contains("idle deadline timed out"), "{error}");
    }

    #[test]
    fn turn_deadline_progress_extends_idle_but_not_hard_cap() {
        let started = Instant::now();
        let mut deadline =
            TurnDeadline::new(started, Duration::from_secs(120), Duration::from_secs(60)).unwrap();
        deadline
            .progress(started + Duration::from_secs(50))
            .unwrap();
        deadline
            .progress(started + Duration::from_secs(100))
            .unwrap();
        assert_eq!(
            deadline
                .remaining(started + Duration::from_secs(110))
                .unwrap(),
            Duration::from_secs(10)
        );
        deadline
            .progress(started + Duration::from_secs(110))
            .unwrap();
        assert_eq!(
            deadline
                .remaining(started + Duration::from_secs(119))
                .unwrap(),
            Duration::from_secs(1)
        );
        let error = deadline
            .remaining(started + Duration::from_secs(120))
            .unwrap_err()
            .to_string();
        assert!(error.contains("hard deadline timed out"), "{error}");
    }

    #[test]
    fn permission_ack_wait_dispatches_interleaved_turn_frames() {
        let (stream, peer) = UnixStream::pair().unwrap();
        let reader = BufReader::new(stream.try_clone().unwrap());
        let server = thread::spawn(move || {
            let mut peer = BufReader::new(peer);
            let mut request = String::new();
            peer.read_line(&mut request).unwrap();
            assert!(request.contains("send_message"));
            peer.get_mut()
                .write_all(
                    concat!(
                        "{\"ev\":\"permission_request\",\"session_id\":\"interleave\",\"request_id\":\"permission-1\"}\n",
                        "{\"ev\":\"text_delta\",\"session_id\":\"interleave\",\"text\":\"retained text\"}\n",
                        "{\"ev\":\"token_usage\",\"session_id\":\"interleave\",\"input\":11,\"output\":7,\"cache_read_input\":3}\n",
                        "{\"ev\":\"turn_done\",\"session_id\":\"interleave\"}\n"
                    )
                    .as_bytes(),
                )
                .unwrap();
            peer.get_mut().flush().unwrap();

            request.clear();
            peer.read_line(&mut request).unwrap();
            let deny: serde_json::Value = serde_json::from_str(&request).unwrap();
            assert_eq!(
                deny.get("decision").and_then(serde_json::Value::as_str),
                Some("deny")
            );
            let reply_to = deny.get("id").and_then(serde_json::Value::as_u64).unwrap();
            writeln!(peer.get_mut(), "{{\"ev\":\"ok\",\"reply_to\":{reply_to}}}").unwrap();
            peer.get_mut().flush().unwrap();
            request.clear();
            assert_eq!(peer.read_line(&mut request).unwrap(), 0);
        });
        let mut api = JcodeSession {
            stream,
            reader,
            next_id: 1,
            session: "interleave".into(),
            usage: ModelUsage::default(),
            usage_observed: false,
            provider: "OpenAI OAuth".into(),
            model: "mock".into(),
            requested_model: "mock".into(),
            timeout: Duration::from_secs(30),
            idle_timeout: Duration::from_secs(30),
            cancel_before_archive: false,
            workspace: None,
        };
        let reply = api.turn("prompt").unwrap();
        assert_eq!(reply.text, "retained text");
        assert_eq!(reply.usage.input, 11);
        assert_eq!(reply.usage.output, 7);
        assert_eq!(reply.usage.cache_read, 3);
        api.session.clear();
        drop(api);
        server.join().unwrap();
    }

    #[test]
    fn permission_request_flood_is_bounded_and_every_response_is_deny() {
        const LIMIT: usize = 64;
        let (stream, peer) = UnixStream::pair().unwrap();
        let reader = BufReader::new(stream.try_clone().unwrap());
        let server = thread::spawn(move || {
            let mut peer = BufReader::new(peer);
            let mut request = String::new();
            peer.read_line(&mut request).unwrap();
            assert!(request.contains("send_message"));
            for index in 0..=LIMIT {
                writeln!(
                    peer.get_mut(),
                    "{{\"ev\":\"permission_request\",\"session_id\":\"flood\",\"request_id\":\"p-{index}\"}}"
                )
                .unwrap();
            }
            peer.get_mut().flush().unwrap();
            for _ in 0..LIMIT {
                request.clear();
                peer.read_line(&mut request).unwrap();
                let deny: serde_json::Value = serde_json::from_str(&request).unwrap();
                assert_eq!(
                    deny.get("decision").and_then(serde_json::Value::as_str),
                    Some("deny")
                );
            }
            request.clear();
            assert_eq!(peer.read_line(&mut request).unwrap(), 0);
        });
        let mut api = JcodeSession {
            stream,
            reader,
            next_id: 1,
            session: "flood".into(),
            usage: ModelUsage::default(),
            usage_observed: false,
            provider: "OpenAI OAuth".into(),
            model: "mock".into(),
            requested_model: "mock".into(),
            timeout: Duration::from_secs(30),
            idle_timeout: Duration::from_secs(30),
            cancel_before_archive: false,
            workspace: None,
        };
        let error = api.turn("prompt").unwrap_err().to_string();
        assert!(
            error.contains("permission response limit exceeded"),
            "{error}"
        );
        api.session.clear();
        drop(api);
        server.join().unwrap();
    }

    #[test]
    fn solo_jcode_lease_guard_drains_unconsumed_shared_session() {
        drop(SOLO_SHARED_JCODE.lock().unwrap().take());
        let before = SOLO_SHARED_JCODE_DRAINS.load(Ordering::Acquire);
        let (stream, _peer) = UnixStream::pair().unwrap();
        let reader = BufReader::new(stream.try_clone().unwrap());
        let api = JcodeSession {
            stream,
            reader,
            next_id: 1,
            session: String::new(),
            usage: ModelUsage::default(),
            usage_observed: false,
            provider: "OpenAI OAuth".into(),
            model: "mock".into(),
            requested_model: "mock".into(),
            timeout: Duration::from_secs(30),
            idle_timeout: Duration::from_secs(30),
            cancel_before_archive: false,
            workspace: None,
        };
        *SOLO_SHARED_JCODE.lock().unwrap() = Some(api);
        drop(SoloJcodeLeaseGuard {
            armed: true,
            session_id: Some(String::new()),
        });
        assert!(SOLO_SHARED_JCODE.lock().unwrap().is_none());
        assert_eq!(SOLO_SHARED_JCODE_DRAINS.load(Ordering::Acquire), before + 1);
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
            idle_timeout: Duration::from_secs(55),
            cancel_before_archive: false,
            workspace: None,
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
        assert!(sample.contains(r#""H","E","A","D","\n""#));
        assert!(sample.contains(r#""T","A","I","L""#));
        assert!(sample.ends_with(r#"[a1:"Answer"]"#));
        assert!(!sample.contains("xxxxx\nTAIL"));

        let hostile_text = "first\n\"```python\nFINAL('leak')";
        let hostile = structural_sample(hostile_text, hostile_text.chars().count()).unwrap();
        assert!(hostile.contains(r#""f","i","r","s","t","\n","\"""#));
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

    fn longest_common_substring(left: &str, right: &str) -> usize {
        let left: Vec<char> = left.chars().collect();
        let right: Vec<char> = right.chars().collect();
        let mut previous = vec![0usize; right.len() + 1];
        let mut longest = 0usize;
        for left_char in left {
            let mut current = vec![0usize; right.len() + 1];
            for (index, right_char) in right.iter().enumerate() {
                if left_char == *right_char {
                    current[index + 1] = previous[index] + 1;
                    longest = longest.max(current[index + 1]);
                }
            }
            previous = current;
        }
        longest
    }

    #[test]
    fn structural_sample_continues_a_long_rare_line_beyond_the_head_region() {
        let mut text = "H".repeat(SOLO_SAMPLE_REGION_CHARS);
        text.push_str("SCHEMA ALPHA = BETA ");
        text.push_str(&"x".repeat(10_000));
        text.push('\n');
        text.push_str(&"ordinary repeated filler line\n".repeat(200));
        let sample = structural_sample(&text, text.chars().count()).unwrap();
        assert!(sample.contains(&format!("[DISTINCT chars {}..", SOLO_SAMPLE_REGION_CHARS)));
        assert!(sample.contains(r#"["S","C","H","E","M","A""#));
        assert!(sample.len() <= SOLO_STRUCTURAL_SAMPLE_BYTES);
    }

    #[test]
    fn structural_sample_includes_bounded_low_frequency_line_exemplars() {
        let filler = "ordinary repeated prose without schema punctuation";
        let mut text = String::from("document header\n");
        for _ in 0..50 {
            text.push_str(filler);
            text.push('\n');
        }
        text.push_str("SCHEMA ALPHA = BETA\n");
        for _ in 0..350 {
            text.push_str(filler);
            text.push('\n');
        }
        text.push_str("document question\n");
        let sample = structural_sample(&text, text.chars().count()).unwrap();
        assert!(sample.contains("[DISTINCT chars"));
        assert!(sample.contains(r#"["S","C","H","E","M","A""#));
        assert!(sample.len() <= SOLO_STRUCTURAL_SAMPLE_BYTES);

        let mut escape_heavy = String::new();
        for index in 0..12 {
            escape_heavy.push_str(&format!("line-{index}-{}\n", "\0".repeat(300)));
        }
        let escaped = structural_sample(&escape_heavy, escape_heavy.chars().count()).unwrap();
        assert!(escaped.len() <= SOLO_STRUCTURAL_SAMPLE_BYTES);

        let mut sensitive = format!("header\n{}", format!("{filler}\n").repeat(50));
        sensitive.push_str(&format!("sk-{}\n", "A".repeat(40)));
        sensitive.push_str(&format!("{filler}\n").repeat(350));
        sensitive.push_str("tail\n");
        let redacted = structural_sample(&sensitive, sensitive.chars().count()).unwrap();
        assert!(redacted.contains(r#"["s","k","-","A""#));
        assert!(!redacted.contains("sk-AAAAAAAA"));
    }

    #[test]
    fn structural_overlap_guard_streams_large_source_against_bounded_sample_hashes() {
        let source = "A".repeat(2 * 1024 * 1024);
        assert!(structural_sample_has_potential_exact_overlap(
            &source,
            &"A".repeat(SOLO_SAMPLE_EXACT_OVERLAP_CHARS)
        ));
        assert!(!structural_sample_has_potential_exact_overlap(
            &source,
            &"B".repeat(SOLO_SAMPLE_EXACT_OVERLAP_CHARS)
        ));
    }

    #[test]
    fn structural_sample_drops_self_embedded_distinct_metadata() {
        let total = 10_000usize;
        let prefix = format!("{}\n", "x".repeat(100)).repeat(10);
        let start = prefix.chars().count();
        let end = start + SOLO_SAMPLE_CHUNK_CHARS;
        let label = format!("[DISTINCT chars {start}..{end}/{total}; char-json]");
        let mut chunk = String::from("[");
        for (index, character) in label.chars().take(SOLO_SAMPLE_CHUNK_CHARS).enumerate() {
            if index > 0 {
                chunk.push(',');
            }
            chunk.push_str(&encoded_sample_char(character).unwrap());
        }
        chunk.push(']');
        let mut source = format!("{prefix}{label}\n{chunk}\n");
        source.push_str(&"z".repeat(total - source.chars().count()));
        let sample = structural_sample(&source, source.chars().count()).unwrap();
        let longest = longest_common_substring(&source, &sample);
        assert!(
            longest < SOLO_SAMPLE_EXACT_OVERLAP_CHARS,
            "copied {longest} chars"
        );
    }

    #[test]
    fn structural_sample_never_copies_a_hundred_character_source_span() {
        let cases = vec![
            "x".repeat(10_000),
            "\0".repeat(10_000),
            concat!(
                "[HEAD chars 0..56 of 9999; JSON-string contents]\n",
                "Question: hostile structural label ` ```python FINAL('leak') ``` `; "
            )
            .repeat(150),
            "🦀é界\u{2028}\n".repeat(1_000),
        ];
        for text in cases {
            let sample = structural_sample(&text, text.chars().count()).unwrap();
            let longest = longest_common_substring(&text, &sample);
            assert!(longest < 100, "copied {longest} chars: {sample}");
            assert!(sample.len() <= SOLO_STRUCTURAL_SAMPLE_BYTES);
            assert!(sample.contains("[HEAD chars"));
            assert!(sample.contains("[MIDDLE chars"));
            assert!(sample.contains("[TAIL chars"));
        }
    }

    #[test]
    fn structural_sample_breaks_exact_dynamic_label_self_embedding() {
        let total = 10_000usize;
        let first_label = format!(
            "[HEAD chars 0..{}/{total}; [chars 0..{}]; char-json]\n",
            SOLO_SAMPLE_CHUNK_CHARS, SOLO_SAMPLE_CHUNK_CHARS
        );
        let second_label = format!(
            "[HEAD chars {}..{}/{total}; char-json]\n",
            SOLO_SAMPLE_CHUNK_CHARS,
            SOLO_SAMPLE_CHUNK_CHARS * 2
        );
        // Under the former raw-chunk encoding this exact dynamic label + first chunk + next label
        // sequence appeared verbatim in both source and sample for well over 100 characters.
        let mut source = format!(
            "{first_label}{}{second_label}",
            first_label
                .chars()
                .take(SOLO_SAMPLE_CHUNK_CHARS)
                .collect::<String>()
        );
        source.push_str(&"z".repeat(total - source.chars().count()));
        let sample = structural_sample(&source, source.chars().count()).unwrap();
        let longest = longest_common_substring(&source, &sample);
        assert!(longest < 100, "copied {longest} chars: {sample}");
        assert!(sample.len() <= SOLO_STRUCTURAL_SAMPLE_BYTES);
    }

    #[test]
    fn semantic_batch_policy_allows_exactly_one_physical_provider_turn() {
        assert_eq!(model_call_entered_turn_limit("_az_llm_batch_fresh_once"), 1);
        assert_eq!(model_call_entered_turn_limit("llm_batch_fresh"), 2);
        assert_eq!(model_call_entered_turn_limit("llm_batch"), 2);
        let budget =
            EnteredTurnBudget::new(model_call_entered_turn_limit("_az_llm_batch_fresh_once"));
        assert_eq!(budget.try_enter().unwrap(), 1);
        assert!(budget.try_enter().is_err());
        assert_eq!(budget.entered(), 1);
    }

    #[test]
    fn semantic_wall_budget_scales_with_phase_waves_at_eight_workers() {
        assert_eq!(SEMANTIC_MANIFEST_WORKERS, 8);
        assert_eq!(semantic_wall_budget(6).unwrap(), Duration::from_secs(240));
        // The frozen latest scout's 3,182-item boundary uses 82 fixed shards.
        assert_eq!(
            semantic_wall_budget(492).unwrap(),
            Duration::from_secs(1_788)
        );
        // 105,000 / 39 rounds up to 2,693 shards and honestly reserves all six phases.
        assert_eq!(
            semantic_wall_budget(16_158).unwrap(),
            Duration::from_secs(54_654)
        );
        assert!(semantic_wall_budget(0).is_err());
        assert!(semantic_wall_budget(5).is_err());
        assert!(semantic_wall_budget(16_159).is_err());
        let s = 82_u64;
        let hypothetical_two_worker_seconds =
            ((2 * s).div_ceil(2) * 2 + s.div_ceil(2) * 2) * 27 + 60;
        assert_eq!(hypothetical_two_worker_seconds, 6_702);
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
        let retryable_stream = jcode_frame_error(&serde_json::json!({
            "ev": "error",
            "code": "internal",
            "message": "Retryable stream error: {\"type\":\"error\"}",
        }));
        assert!(model_transport_error_is_transient(&retryable_stream));
        let plain_internal = jcode_frame_error(&serde_json::json!({
            "ev": "error",
            "code": "internal",
            "message": "unrelated internal failure",
        }));
        assert!(!model_transport_error_is_transient(&plain_internal));
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
        assert!(
            session
                .structural_sample()
                .unwrap()
                .contains(r#""p","r","i","o","r""#)
        );
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

    #[test]
    fn reliability_two_default_call_cap_is_measured_headroom() {
        assert_eq!(Config::default().max_calls_per_cell, 150);
        assert_eq!(MAX_CALLS_PER_CELL, 150);
        assert_eq!(SEMANTIC_MANIFEST_MAX_CALLS, 16_158);
    }
}

#[cfg(test)]
mod claude_hook_tests {
    use super::*;

    fn event(
        session: &str,
        hook_event_name: &str,
        cwd: &Path,
        tool_name: Option<&str>,
        tool_input: serde_json::Value,
        prompt: Option<&str>,
    ) -> String {
        let mut value = serde_json::json!({
            "session_id": session,
            "hook_event_name": hook_event_name,
            "cwd": cwd,
            "tool_input": tool_input
        });
        if let Some(tool_name) = tool_name {
            value["tool_name"] = serde_json::Value::String(tool_name.to_owned());
        }
        if let Some(prompt) = prompt {
            value["user_prompt"] = serde_json::Value::String(prompt.to_owned());
        }
        value.to_string()
    }

    fn unique_temp_dir(label: &str) -> PathBuf {
        let path = env::temp_dir().join(format!(
            "{label}-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir_all(&path).unwrap();
        path
    }

    #[test]
    fn claude_hook_internal_deadline_fails_closed_before_the_worker_finishes() {
        let started = Instant::now();
        let prompt_block =
            claude_hook_with_deadline("UserPromptSubmit", Duration::from_millis(1), || {
                thread::sleep(Duration::from_millis(100));
                Ok(None)
            })
            .unwrap();
        let prompt_block: serde_json::Value = serde_json::from_str(&prompt_block).unwrap();
        assert_eq!(prompt_block["decision"], "block");
        assert!(prompt_block["reason"].as_str().unwrap().contains("retry"));
        assert!(started.elapsed() < Duration::from_secs(1));

        let pretool_denial =
            claude_hook_with_deadline("PreToolUse", Duration::from_secs(1), || {
                Err(anyhow!("forced worker error"))
            })
            .unwrap();
        let pretool_denial: serde_json::Value = serde_json::from_str(&pretool_denial).unwrap();
        assert_eq!(
            pretool_denial["hookSpecificOutput"]["permissionDecision"],
            "deny"
        );
        let panic_denial = claude_hook_with_deadline(
            "PreToolUse",
            Duration::from_secs(1),
            || -> Result<Option<String>> { panic!("forced worker panic") },
        )
        .unwrap();
        let panic_denial: serde_json::Value = serde_json::from_str(&panic_denial).unwrap();
        assert_eq!(
            panic_denial["hookSpecificOutput"]["permissionDecision"],
            "deny"
        );
        assert_eq!(
            claude_hook_with_deadline("PostToolUse", Duration::from_secs(1), || {
                Err(anyhow!("forced worker error"))
            }),
            None
        );
        assert_eq!(
            claude_hook_with_deadline("PreToolUse", Duration::from_secs(1), || {
                Ok(Some("decision".to_owned()))
            }),
            Some("decision".to_owned())
        );
    }

    #[test]
    fn claude_hook_coverage_terms_use_word_boundaries_and_common_reductions() {
        for prompt in [
            "Determine the total ERROR entries in observations.csv.",
            "What is the number of ERROR rows?",
            "Find the earliest event in the log.",
            "Compute the exact count for these records.",
            "Analyze the full dataset.",
            "Scan the entire log.",
            "List all events.",
            "Inspect only the first line to learn the schema, then compute the total number of rows across all records.",
        ] {
            assert!(claude_hook_coverage_prompt(prompt), "not routed: {prompt}");
        }
        for prompt in [
            "Update account settings.",
            "Apply the discount policy.",
            "Raise the minimum pipeline version.",
            "Make this exact small function change.",
            "Show only the first five records.",
        ] {
            assert!(
                !claude_hook_coverage_prompt(prompt),
                "false route: {prompt}"
            );
        }
    }

    #[test]
    fn claude_hook_blocks_only_broad_large_access_until_successful_activation() {
        let base = env::temp_dir().join(format!(
            "azdaja-claude-hook-test-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let root = base.join("markers");
        fs::create_dir(&base).unwrap();
        let large = base.join("observations.csv");
        let small = base.join("small.csv");
        let extensionless = base.join("observations");
        let spaced = base.join("space name.data");
        let unicode = base.join("観測資料");
        let long_line = base.join("one-line.blob");
        let short_lines = b"id,value\n".repeat(CLAUDE_HOOK_LARGE_BYTES as usize / 9 + 2);
        fs::write(&large, &short_lines).unwrap();
        fs::write(&extensionless, &short_lines).unwrap();
        fs::write(&spaced, &short_lines).unwrap();
        fs::write(&unicode, &short_lines).unwrap();
        fs::write(&long_line, vec![b'x'; CLAUDE_HOOK_LARGE_BYTES as usize + 1]).unwrap();
        fs::write(&small, b"id,value\n1,2\n").unwrap();
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            for name in ["head", "file"] {
                let executable = base.join(name);
                fs::write(&executable, b"#!/bin/sh\ncat observations.csv\n").unwrap();
                fs::set_permissions(&executable, fs::Permissions::from_mode(0o700)).unwrap();
            }
            std::os::unix::fs::symlink(&large, base.join("large-link.csv")).unwrap();
        }
        let session = "session-one";

        let prompt = event(
            session,
            "UserPromptSubmit",
            &base,
            None,
            serde_json::Value::Null,
            Some("Compute the exact aggregate over every record."),
        );
        assert_eq!(claude_hook_with_root(&prompt, &root).unwrap(), None);

        let metadata = event(
            session,
            "PreToolUse",
            &base,
            Some("Bash"),
            serde_json::json!({"command": "/usr/bin/wc -l observations.csv"}),
            None,
        );
        assert_eq!(claude_hook_with_root(&metadata, &root).unwrap(), None);
        let sample = event(
            session,
            "PreToolUse",
            &base,
            Some("Bash"),
            serde_json::json!({"command": "/usr/bin/head -6 observations.csv; /usr/bin/tail -3 observations.csv"}),
            None,
        );
        assert_eq!(claude_hook_with_root(&sample, &root).unwrap(), None);
        let oversized_sample = event(
            session,
            "PreToolUse",
            &base,
            Some("Bash"),
            serde_json::json!({"command": "/usr/bin/head -6 observations.csv; /usr/bin/tail -5 observations.csv"}),
            None,
        );
        assert!(
            claude_hook_with_root(&oversized_sample, &root)
                .unwrap()
                .is_some()
        );
        for command in [
            "/usr/bin/head -c 1000001 observations.csv",
            "cp observations.csv /dev/stdout",
            "/usr/bin/head -10 observations.csv observations.csv",
            "/usr/bin/head -1 observations.csv; nl observations.csv",
            "/usr/bin/head -1 observations.csv",
            "/usr/bin/head -1 one-line.blob",
            "/usr/bin/tail -1 one-line.blob",
            "cat observations",
            "cat 'space name.data'",
            "cat 観測資料",
            "/usr/bin/file -f observations.csv",
            "/usr/bin/head -1 {observations.csv,small.csv}",
            "/usr/bin/head -1 ~/outside-large",
            "/usr/bin/head -1 $TARGET",
            "/usr/bin/wc -l *.csv",
            "/usr/bin/file *",
            "/usr/bin/du -sh *",
            "head -1 observations.csv",
            "file observations.csv",
            "./head -1 observations.csv",
            "./file observations.csv",
            "./unknown-reader-with-hardcoded-path",
        ] {
            let bypass = event(
                session,
                "PreToolUse",
                &base,
                Some("Bash"),
                serde_json::json!({"command": command}),
                None,
            );
            assert!(
                claude_hook_with_root(&bypass, &root).unwrap().is_some(),
                "bypass was not denied: {command}"
            );
        }
        let small_scan = event(
            session,
            "PreToolUse",
            &base,
            Some("Bash"),
            serde_json::json!({"command": "python3 scan.py small.csv"}),
            None,
        );
        assert!(
            claude_hook_with_root(&small_scan, &root).unwrap().is_some(),
            "unknown broad Bash is fail-closed while a complete large-input task is pending"
        );

        let broad = event(
            session,
            "PreToolUse",
            &base,
            Some("Bash"),
            serde_json::json!({"command": "python3 scan.py observations.csv"}),
            None,
        );
        let denial = claude_hook_with_root(&broad, &root)
            .unwrap()
            .expect("broad large scan must be denied");
        assert!(denial.contains("permissionDecision"));
        assert!(denial.contains("Call the Skill tool with azdaja"));

        let bounded_read = event(
            session,
            "PreToolUse",
            &base,
            Some("Read"),
            serde_json::json!({"file_path": large, "limit": 5}),
            None,
        );
        assert!(
            claude_hook_with_root(&bounded_read, &root)
                .unwrap()
                .is_some(),
            "a second structural sample in one task must be denied"
        );
        let broad_read = event(
            session,
            "PreToolUse",
            &base,
            Some("Read"),
            serde_json::json!({"file_path": large}),
            None,
        );
        assert!(claude_hook_with_root(&broad_read, &root).unwrap().is_some());
        #[cfg(unix)]
        {
            let symlink_read = event(
                session,
                "PreToolUse",
                &base,
                Some("Read"),
                serde_json::json!({"file_path": base.join("large-link.csv")}),
                None,
            );
            assert!(
                claude_hook_with_root(&symlink_read, &root)
                    .unwrap()
                    .is_some()
            );
        }

        let unrelated_prompt = event(
            session,
            "UserPromptSubmit",
            &base,
            None,
            serde_json::Value::Null,
            Some("Summarize this small excerpt only."),
        );
        assert_eq!(
            claude_hook_with_root(&unrelated_prompt, &root).unwrap(),
            None
        );
        assert_eq!(claude_hook_with_root(&broad, &root).unwrap(), None);
        assert_eq!(claude_hook_with_root(&prompt, &root).unwrap(), None);

        let unrelated_skill = event(
            session,
            "PostToolUse",
            &base,
            Some("Skill"),
            serde_json::json!({"skill": "other"}),
            None,
        );
        assert_eq!(
            claude_hook_with_root(&unrelated_skill, &root).unwrap(),
            None
        );
        assert!(claude_hook_with_root(&broad, &root).unwrap().is_some());
        let activation = event(
            session,
            "PostToolUse",
            &base,
            Some("Skill"),
            serde_json::json!({"skill": "azdaja"}),
            None,
        );
        assert_eq!(claude_hook_with_root(&activation, &root).unwrap(), None);
        assert!(claude_hook_with_root(&broad, &root).unwrap().is_some());
        let transaction = event(
            session,
            "PreToolUse",
            &base,
            Some("Bash"),
            serde_json::json!({"command": r#"set -euo pipefail
AZ="/managed/azdaja"
sid=
cleanup() { "$AZ" kill "$sid"; }
trap cleanup EXIT
sid="$("$AZ" start)"
"$AZ" load "$sid" fixture.jsonl source
cat <<'PY' | "$AZ" exec "$sid"
FINAL({})
PY
"$AZ" final "$sid""#}),
            None,
        );
        assert_eq!(claude_hook_with_root(&transaction, &root).unwrap(), None);
        for denied_tool in ["Agent", "Task", "Skill"] {
            let event = event(
                session,
                "PreToolUse",
                &base,
                Some(denied_tool),
                serde_json::json!({"name": "azdaja"}),
                None,
            );
            assert!(claude_hook_with_root(&event, &root).unwrap().is_some());
        }
        // A repeated PostToolUse delivery is idempotent and cannot reopen
        // the already claimed transaction lease.
        assert_eq!(claude_hook_with_root(&activation, &root).unwrap(), None);
        assert!(
            claude_hook_with_root(&transaction, &root)
                .unwrap()
                .is_some()
        );
        let structured = event(
            session,
            "PreToolUse",
            &base,
            Some("StructuredOutput"),
            serde_json::json!({"code": "TF"}),
            None,
        );
        assert_eq!(claude_hook_with_root(&structured, &root).unwrap(), None);
        assert_eq!(
            claude_hook_with_root(&unrelated_prompt, &root).unwrap(),
            None
        );
        assert_eq!(claude_hook_with_root(&broad, &root).unwrap(), None);

        let end = event(
            session,
            "SessionEnd",
            &base,
            None,
            serde_json::Value::Null,
            None,
        );
        assert_eq!(claude_hook_with_root(&end, &root).unwrap(), None);
        assert_eq!(claude_hook_with_root(&broad, &root).unwrap(), None);
        fs::remove_dir_all(base).unwrap();
    }

    #[test]
    fn claude_hook_directories_accumulate_and_traversal_limits_fail_closed() {
        let base = env::temp_dir().join(format!(
            "azdaja-claude-hook-directory-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let cumulative = base.join("cumulative");
        let budgeted = base.join("budgeted");
        let leaf_scope = base.join("leaf-scope");
        fs::create_dir_all(&cumulative).unwrap();
        fs::create_dir_all(&budgeted).unwrap();
        fs::create_dir_all(&leaf_scope).unwrap();
        fs::write(leaf_scope.join("a"), vec![b'a'; 600_001]).unwrap();
        fs::write(leaf_scope.join("b"), vec![b'b'; 600_001]).unwrap();
        for index in 0..2_000 {
            fs::write(cumulative.join(format!("part-{index:04}")), vec![b'x'; 600]).unwrap();
        }
        for index in 0..10_001 {
            fs::write(budgeted.join(format!("empty-{index:05}")), b"").unwrap();
        }
        let mut deep = base.join("deep");
        fs::create_dir_all(&deep).unwrap();
        for index in 0..13 {
            deep = deep.join(format!("level-{index:02}"));
            fs::create_dir(&deep).unwrap();
        }
        let mut budget = 10_000usize;
        assert!(claude_hook_path_is_large(&cumulative, &mut budget, 0).unwrap());
        let mut budget = 10_000usize;
        assert!(claude_hook_path_is_large(&budgeted, &mut budget, 0).unwrap());
        let mut budget = 10_000usize;
        assert!(claude_hook_path_is_large(&base.join("deep"), &mut budget, 0).unwrap());

        let root = base.join("markers");
        let prompt = event(
            "session-directory",
            "UserPromptSubmit",
            &base,
            None,
            serde_json::Value::Null,
            Some("Compute the exact count for these records."),
        );
        assert_eq!(claude_hook_with_root(&prompt, &root).unwrap(), None);
        let grep = event(
            "session-directory",
            "PreToolUse",
            &base,
            Some("Grep"),
            serde_json::json!({"path": cumulative}),
            None,
        );
        assert!(claude_hook_with_root(&grep, &root).unwrap().is_some());
        for leaf in [leaf_scope.join("a"), leaf_scope.join("b")] {
            let read_leaf = event(
                "session-directory",
                "PreToolUse",
                &base,
                Some("Read"),
                serde_json::json!({"file_path": leaf, "limit": 1}),
                None,
            );
            assert!(claude_hook_with_root(&read_leaf, &root).unwrap().is_some());
            let grep_leaf = event(
                "session-directory",
                "PreToolUse",
                &base,
                Some("Grep"),
                serde_json::json!({"path": leaf}),
                None,
            );
            assert!(claude_hook_with_root(&grep_leaf, &root).unwrap().is_some());
        }
        let aggregate_head = event(
            "session-directory",
            "PreToolUse",
            &base,
            Some("Bash"),
            serde_json::json!({"command": "/usr/bin/head -5 leaf-scope/a; /usr/bin/head -5 leaf-scope/b"}),
            None,
        );
        assert!(
            claude_hook_with_root(&aggregate_head, &root)
                .unwrap()
                .is_some()
        );
        let expanding_grep = event(
            "session-directory",
            "PreToolUse",
            &base,
            Some("Grep"),
            serde_json::json!({"path": "~/outside-large"}),
            None,
        );
        assert!(
            claude_hook_with_root(&expanding_grep, &root)
                .unwrap()
                .is_some()
        );

        let small_cwd = unique_temp_dir("azdaja-claude-small-cwd");
        let external_a = unique_temp_dir("azdaja-claude-external-a");
        let external_b = unique_temp_dir("azdaja-claude-external-b");
        let disjoint_a = external_a.join("a");
        let disjoint_b = external_b.join("b");
        fs::write(&disjoint_a, vec![b'a'; 600_001]).unwrap();
        fs::write(&disjoint_b, vec![b'b'; 600_001]).unwrap();
        let disjoint_prompt = event(
            "session-disjoint",
            "UserPromptSubmit",
            &small_cwd,
            None,
            serde_json::Value::Null,
            Some("Aggregate all records from both inputs."),
        );
        assert_eq!(
            claude_hook_with_root(&disjoint_prompt, &root).unwrap(),
            None
        );
        for leaf in [&disjoint_a, &disjoint_b] {
            let read_leaf = event(
                "session-disjoint",
                "PreToolUse",
                &small_cwd,
                Some("Read"),
                serde_json::json!({"file_path": leaf, "limit": 1}),
                None,
            );
            assert!(claude_hook_with_root(&read_leaf, &root).unwrap().is_some());
            let grep_leaf = event(
                "session-disjoint",
                "PreToolUse",
                &small_cwd,
                Some("Grep"),
                serde_json::json!({"path": leaf}),
                None,
            );
            assert!(claude_hook_with_root(&grep_leaf, &root).unwrap().is_some());
        }
        let disjoint_head = event(
            "session-disjoint",
            "PreToolUse",
            &small_cwd,
            Some("Bash"),
            serde_json::json!({
                "command": format!(
                    "/usr/bin/head -5 '{}'; /usr/bin/head -5 '{}'",
                    disjoint_a.display(),
                    disjoint_b.display()
                )
            }),
            None,
        );
        assert!(
            claude_hook_with_root(&disjoint_head, &root)
                .unwrap()
                .is_some()
        );
        fs::remove_dir_all(small_cwd).unwrap();
        fs::remove_dir_all(external_a).unwrap();
        fs::remove_dir_all(external_b).unwrap();
        fs::remove_dir_all(base).unwrap();
    }

    #[test]
    fn claude_hook_allows_only_one_byte_bounded_read_sample_per_prompt() {
        let base = env::temp_dir().join(format!(
            "azdaja-claude-hook-read-sample-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let root = base.join("markers");
        fs::create_dir(&base).unwrap();
        let large = base.join("rows");
        let long_line = base.join("long-row");
        let pdf = base.join("large.pdf");
        let notebook = base.join("large.ipynb");
        let image = base.join("large.png");
        let inaccessible = base.join("inaccessible.txt");
        let short_text =
            b"short structural row\n".repeat(CLAUDE_HOOK_LARGE_BYTES as usize / 21 + 2);
        fs::write(&large, &short_text).unwrap();
        fs::write(&long_line, vec![b'x'; CLAUDE_HOOK_LARGE_BYTES as usize + 1]).unwrap();
        fs::write(
            &pdf,
            [
                b"%PDF-1.7\n".as_slice(),
                vec![b'x'; CLAUDE_HOOK_LARGE_BYTES as usize].as_slice(),
            ]
            .concat(),
        )
        .unwrap();
        fs::write(
            &notebook,
            b"{\"cells\":[]}\n".repeat(CLAUDE_HOOK_LARGE_BYTES as usize / 13 + 2),
        )
        .unwrap();
        fs::write(
            &image,
            [
                b"\x89PNG\r\n\x1a\n".as_slice(),
                vec![b'x'; CLAUDE_HOOK_LARGE_BYTES as usize].as_slice(),
            ]
            .concat(),
        )
        .unwrap();
        fs::write(&inaccessible, &short_text).unwrap();
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            fs::set_permissions(&inaccessible, fs::Permissions::from_mode(0o000)).unwrap();
        }
        let long_prompt = event(
            "session-long-read",
            "UserPromptSubmit",
            &base,
            None,
            serde_json::Value::Null,
            Some("Compute the exact aggregate over every row."),
        );
        assert_eq!(claude_hook_with_root(&long_prompt, &root).unwrap(), None);
        let long_sample = event(
            "session-long-read",
            "PreToolUse",
            &base,
            Some("Read"),
            serde_json::json!({"file_path": long_line, "limit": 1}),
            None,
        );
        assert!(
            claude_hook_with_root(&long_sample, &root)
                .unwrap()
                .is_some()
        );

        let session = "session-read-sample";
        let prompt = event(
            session,
            "UserPromptSubmit",
            &base,
            None,
            serde_json::Value::Null,
            Some("Compute the exact aggregate over every row."),
        );
        assert_eq!(claude_hook_with_root(&prompt, &root).unwrap(), None);
        for invalid_input in [
            serde_json::json!({"file_path": large, "limit": 0}),
            serde_json::json!({"file_path": large, "offset": -1, "limit": 5}),
            serde_json::json!({"file_path": large, "offset": "0", "limit": 5}),
            serde_json::json!({"file_path": large, "limit": 5, "pages": "1"}),
            serde_json::json!({"file_path": large, "path": large, "limit": 5}),
            serde_json::json!({"file_path": "~/outside-large", "limit": 5}),
            serde_json::json!({"file_path": pdf, "limit": 5}),
            serde_json::json!({"file_path": notebook, "limit": 5}),
            serde_json::json!({"file_path": image, "limit": 5}),
            serde_json::json!({"file_path": inaccessible, "limit": 5}),
        ] {
            let invalid = event(
                session,
                "PreToolUse",
                &base,
                Some("Read"),
                invalid_input,
                None,
            );
            assert!(claude_hook_with_root(&invalid, &root).unwrap().is_some());
        }
        let first = event(
            session,
            "PreToolUse",
            &base,
            Some("Read"),
            serde_json::json!({"file_path": large, "limit": 5}),
            None,
        );
        assert_eq!(claude_hook_with_root(&first, &root).unwrap(), None);
        let changed_offset = event(
            session,
            "PreToolUse",
            &base,
            Some("Read"),
            serde_json::json!({"file_path": large, "offset": 5, "limit": 5}),
            None,
        );
        assert!(
            claude_hook_with_root(&changed_offset, &root)
                .unwrap()
                .is_some()
        );
        assert!(claude_hook_with_root(&first, &root).unwrap().is_some());

        let unrelated = event(
            session,
            "UserPromptSubmit",
            &base,
            None,
            serde_json::Value::Null,
            Some("Summarize this small excerpt only."),
        );
        assert_eq!(claude_hook_with_root(&unrelated, &root).unwrap(), None);
        assert_eq!(claude_hook_with_root(&prompt, &root).unwrap(), None);
        assert_eq!(claude_hook_with_root(&first, &root).unwrap(), None);
        fs::remove_dir_all(base).unwrap();
    }

    #[test]
    fn claude_hook_does_not_force_large_bounded_or_noncoverage_work() {
        let base = env::temp_dir().join(format!(
            "azdaja-claude-hook-negative-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        let root = base.join("markers");
        fs::create_dir(&base).unwrap();
        fs::write(
            base.join("large.jsonl"),
            vec![b'x'; CLAUDE_HOOK_LARGE_BYTES as usize + 1],
        )
        .unwrap();
        let prompt = event(
            "session-negative",
            "UserPromptSubmit",
            &base,
            None,
            serde_json::Value::Null,
            Some("Show only the first five records."),
        );
        assert_eq!(claude_hook_with_root(&prompt, &root).unwrap(), None);
        let tool = event(
            "session-negative",
            "PreToolUse",
            &base,
            Some("Bash"),
            serde_json::json!({"command": "python3 scan.py large.jsonl"}),
            None,
        );
        assert_eq!(claude_hook_with_root(&tool, &root).unwrap(), None);
        let small_exact = event(
            "session-negative",
            "UserPromptSubmit",
            &base,
            None,
            serde_json::Value::Null,
            Some("Make this exact small function change."),
        );
        assert_eq!(claude_hook_with_root(&small_exact, &root).unwrap(), None);
        assert_eq!(claude_hook_with_root(&tool, &root).unwrap(), None);

        let installed_prompt = serde_json::json!({
            "session_id": "session-installed-prompt",
            "hook_event_name": "UserPromptSubmit",
            "cwd": base,
            "tool_input": {},
            "prompt": "Count every row in the full input."
        })
        .to_string();
        assert_eq!(
            claude_hook_with_root(&installed_prompt, &root).unwrap(),
            None
        );
        let installed_tool = event(
            "session-installed-prompt",
            "PreToolUse",
            &base,
            Some("Bash"),
            serde_json::json!({"command": "python3 scan.py large.jsonl"}),
            None,
        );
        assert!(
            claude_hook_with_root(&installed_tool, &root)
                .unwrap()
                .is_some()
        );
        fs::remove_dir_all(base).unwrap();
    }
}

#[cfg(test)]
mod native_hash_tests {
    use super::*;

    #[test]
    fn sha256_matches_standard_vectors() {
        assert_eq!(
            sha256_hex(b""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        );
        assert_eq!(
            sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
        assert_eq!(
            sha256_hex("🦀é".as_bytes()),
            "4fe0ad378bf371e07cf31e6a27beb70e31ccf4bff60ae9897e83ffdb9dcef354"
        );
    }
}

#[cfg(test)]
mod lexical_relevance_tests {
    use super::*;

    #[test]
    fn lexical_relevance_is_deterministic_and_byte_faithful() {
        let source = format!(
            "{}TARGET alpha βeta\r\n{}TARGET alpha ending",
            "ordinary filler. ".repeat(2_000),
            "other filler. ".repeat(2_000)
        );
        let one = build_relevance_view(&source, "TARGET alpha", 8_000).unwrap();
        let two = build_relevance_view(&source, "TARGET alpha", 8_000).unwrap();
        assert_eq!(one, two);
        assert!(!one.complete);
        assert!(one.evidence.chars().count() <= 8_000);
        assert!(one.evidence.contains("omitted_ranges="));
        let chars: Vec<char> = source.chars().collect();
        for &(start, end) in &one.ranges {
            let exact: String = chars[start..end].iter().collect();
            assert!(one.evidence.contains(&exact));
        }
        assert_eq!(
            one.source_chars,
            one.selected_chars + (one.source_chars - one.selected_chars)
        );
    }

    #[test]
    fn lexical_relevance_handles_non_ascii_runs_without_normalizing_evidence() {
        let source = format!(
            "{}目标句子含有稀有词麒麟。 emoji 👩‍💻 and e\u{301}.{}另一个麒麟线索。",
            "无关文本。".repeat(3_000),
            "普通内容。".repeat(3_000)
        );
        let view = build_relevance_view(&source, "请查找麒麟相关目标", 8_000).unwrap();
        assert!(view.evidence.contains("麒麟"));
        assert!(view.evidence.contains("👩‍💻") || view.evidence.contains("另一个麒麟"));
        assert!(view.matched_terms.iter().any(|term| term.contains('麒')));
    }

    #[test]
    fn lexical_relevance_fails_closed_without_discriminating_matches() {
        let no_match =
            build_relevance_view(&"ordinary source ".repeat(2_000), "absentneedle", 8_000)
                .unwrap_err();
        assert!(no_match.to_string().contains("found no query terms"));

        let repeated =
            build_relevance_view(&"sameword ".repeat(10_000), "sameword", 8_000).unwrap_err();
        assert!(repeated.to_string().contains("does not discriminate"));
    }

    #[test]
    fn lexical_relevance_accepts_measured_holistic_query_but_keeps_a_hard_term_cap() {
        let accepted_query = (0..299)
            .map(|index| format!("term{index:03}"))
            .collect::<Vec<_>>()
            .join(" ");
        let source = format!(
            "{} term298 decisive anchor {}",
            "ordinary filler. ".repeat(2_000),
            "other filler. ".repeat(2_000)
        );
        let view = build_relevance_view(&source, &accepted_query, 8_000).unwrap();
        assert!(view.evidence.contains("term298 decisive anchor"));

        let rejected_query = (0..513)
            .map(|index| format!("term{index:03}"))
            .collect::<Vec<_>>()
            .join(" ");
        let error = build_relevance_view(&source, &rejected_query, 8_000).unwrap_err();
        assert!(
            error
                .to_string()
                .contains("lexical relevance query term limit exceeded")
        );
    }

    #[test]
    fn lexical_relevance_is_available_to_solo_without_provider_calls() {
        let cfg = Config::default();
        let mut session = SoloSession::new(&cfg, None).unwrap();
        let result = session
            .exec(
                "view=lexical_relevance(('filler ' * 2000) + 'rare anchor', 'rare anchor', 8000)\nassert view['omitted_chars'] > 0\nassert view['evidence_chars'] <= 8000\nassert 'rare anchor' in view['evidence']\nFINAL('ok')",
                &cfg,
            )
            .unwrap();
        assert!(result.success);
        assert!(result.finalized);
        assert_eq!(result.external_calls, 0);
        assert_eq!(session.final_answer(&cfg).unwrap(), "ok");
    }

    #[test]
    fn lexical_relevance_is_absent_from_ordinary_cells() {
        let cfg = Config::default();
        let mut session = SoloSession::new(&cfg, None).unwrap();
        let repl = session.repl.take().unwrap();
        let (_, _, success, _, calls, _, failure, _, _) = run_cell(
            repl,
            "lexical_relevance('source', 'query', 4000)",
            &cfg,
            &cfg.default_model,
            false,
            false,
            None,
        );
        assert!(!success);
        assert_eq!(calls, 0);
        assert_eq!(failure, Some(ExcType::RuntimeError));
    }

    #[test]
    #[ignore = "release-only 16M-character stress"]
    fn lexical_relevance_release_stress_16m() {
        let mut source = "filler ".repeat(2_000_000);
        source.push_str(" rareanchor ending");
        let started = Instant::now();
        let view = build_relevance_view(&source, "rareanchor", 20_000).unwrap();
        assert!(view.evidence.contains("rareanchor"));
        assert!(started.elapsed() < Duration::from_secs(3));
    }

    #[test]
    fn lexical_relevance_returns_complete_small_source() {
        let source = "small exact source";
        let view = build_relevance_view(source, "exact", 4_000).unwrap();
        assert!(view.complete);
        assert_eq!(view.ranges, vec![(0, source.chars().count())]);
        assert!(view.evidence.contains(source));
    }
}

#[cfg(test)]
mod exact_line_record_tests {
    use super::*;

    fn strings(value: MontyObject) -> Vec<String> {
        let MontyObject::List(values) = value else {
            panic!("exact_line_records did not return a list")
        };
        values
            .into_iter()
            .map(|value| match value {
                MontyObject::String(value) => value,
                _ => panic!("exact_line_records returned a non-string"),
            })
            .collect()
    }

    #[test]
    fn exact_line_records_preserves_order_duplicates_and_all_nonseparator_bytes() {
        let source = concat!(
            "header\n",
            "Row: α\t  \0tail\n",
            "row: wrong-case\n",
            " Row: leading-space\n",
            "RowX: wrong-prefix\n",
            "Row: α\t  \0tail\n",
            "Row: unicode\u{2028}and\u{2029}payload",
        );
        assert_eq!(
            strings(exact_line_records(source, "Row: ").unwrap()),
            vec![
                "Row: α\t  \0tail",
                "Row: α\t  \0tail",
                "Row: unicode\u{2028}and\u{2029}payload",
            ]
        );
    }

    #[test]
    fn exact_line_records_defines_lf_crlf_mixed_and_terminal_behavior() {
        assert_eq!(
            strings(exact_line_records("Row: a\nRow: b\n", "Row: ").unwrap()),
            vec!["Row: a", "Row: b"]
        );
        assert_eq!(
            strings(exact_line_records("Row: a\r\nRow: b\r\n", "Row: ").unwrap()),
            vec!["Row: a", "Row: b"]
        );
        assert_eq!(
            strings(
                exact_line_records("head\nRow: lf\r\nRow: mixed\nRow:\nRow: terminal", "Row:")
                    .unwrap()
            ),
            vec!["Row: lf", "Row: mixed", "Row:", "Row: terminal"]
        );
    }

    #[test]
    fn exact_line_records_rejects_every_bare_cr_shape() {
        for source in ["\rRow: x", "Row: x\ry", "Row: x\r", "Row: x\r\r\n"] {
            let error = exact_line_records(source, "Row:").unwrap_err();
            assert!(
                error
                    .to_string()
                    .contains("rejects bare CR record boundaries"),
                "{source:?}: {error}"
            );
        }
    }

    #[test]
    fn exact_line_records_enforces_prefix_utf8_byte_contract() {
        let one_byte = "x";
        assert_eq!(
            strings(exact_line_records(one_byte, one_byte).unwrap()),
            vec![one_byte]
        );
        let multibyte = "é";
        assert_eq!(
            strings(exact_line_records(multibyte, multibyte).unwrap()),
            vec![multibyte]
        );
        let exact_ascii = "a".repeat(EXACT_LINE_RECORD_MAX_PREFIX_BYTES);
        assert_eq!(
            strings(exact_line_records(&exact_ascii, &exact_ascii).unwrap()),
            vec![exact_ascii.clone()]
        );
        let exact_multibyte = "é".repeat(EXACT_LINE_RECORD_MAX_PREFIX_BYTES / 2);
        assert_eq!(exact_multibyte.len(), EXACT_LINE_RECORD_MAX_PREFIX_BYTES);
        assert_eq!(
            strings(exact_line_records(&exact_multibyte, &exact_multibyte).unwrap()),
            vec![exact_multibyte]
        );
        for prefix in [
            String::new(),
            "x\n".to_owned(),
            "x\r".to_owned(),
            format!("{}é", "a".repeat(EXACT_LINE_RECORD_MAX_PREFIX_BYTES - 1)),
        ] {
            let error = exact_line_records("anything", &prefix).unwrap_err();
            assert!(
                error
                    .to_string()
                    .contains("requires a nonempty literal prefix"),
                "prefix bytes={}: {error}",
                prefix.len()
            );
        }
    }

    #[test]
    fn exact_line_records_fails_closed_on_missing_record() {
        let error = exact_line_records("header\nother", "Row:").unwrap_err();
        assert!(error.to_string().contains("found no anchored records"));
    }

    #[test]
    fn exact_line_records_supports_metadata_selection_after_full_ledger() {
        let cfg = Config::default();
        let mut session = SoloSession::new(&cfg, None).unwrap();
        let code = r#"rows=exact_line_records("header\nDate: Jan 01 || User: 1 || Instance: a\nDate: Jan 02 || User: 2 || Instance: b\nDate: Jan 03 || User: 1 || Instance: c","Date: ")
ledger=[]
for row in rows:
    ledger.append(row)
selected=[]
for row in ledger:
    if "User: 1" in row and "Jan 03" in row:
        selected.append(row)
assert len(ledger)==3
assert len(selected)==1
assert selected[0].endswith("Instance: c")
FINAL(len(selected))"#;
        let result = session.exec(code, &cfg).unwrap();
        assert!(result.success, "{}", result.output);
        assert_eq!(result.external_calls, 0);
        assert_eq!(session.final_answer(&cfg).unwrap(), "1");
    }

    #[test]
    fn exact_line_records_dispatch_rejects_arity_kwargs_and_types() {
        let cfg = Config::default();
        for (code, expected) in [
            ("exact_line_records()", "requires source and prefix"),
            ("exact_line_records('Row: x')", "requires source and prefix"),
            (
                "exact_line_records('Row: x','Row:',3)",
                "requires source and prefix",
            ),
            (
                "exact_line_records(source='Row: x',prefix='Row:')",
                "requires source and prefix",
            ),
            ("exact_line_records(3,'Row:')", "source must be a string"),
            ("exact_line_records('Row: x',3)", "prefix must be a string"),
        ] {
            let mut session = SoloSession::new(&cfg, None).unwrap();
            let result = session.exec(code, &cfg).unwrap();
            assert!(!result.success, "{code}");
            assert!(
                result.output.contains(expected),
                "{code}: {}",
                result.output
            );
            assert_eq!(result.external_calls, 0);
            assert!(!result.finalized);
        }
    }

    #[test]
    fn exact_line_records_enforces_occurrence_limit_boundaries() {
        let source = "Row: x\n".repeat(EXACT_LINE_RECORD_MAX_ITEMS);
        assert_eq!(
            strings(exact_line_records(&source, "Row: ").unwrap()).len(),
            EXACT_LINE_RECORD_MAX_ITEMS
        );
        let too_many = format!("{source}Row: x\n");
        let error = exact_line_records(&too_many, "Row: ").unwrap_err();
        assert!(error.to_string().contains("record limit exceeded"));
    }

    #[test]
    fn exact_line_records_is_absent_from_ordinary_cells() {
        let cfg = Config::default();
        let mut session = SoloSession::new(&cfg, None).unwrap();
        let repl = session.repl.take().unwrap();
        let (_, _, success, _, calls, _, failure, _, _) = run_cell(
            repl,
            "exact_line_records('Row: x', 'Row: ')",
            &cfg,
            &cfg.default_model,
            false,
            false,
            None,
        );
        assert!(!success);
        assert_eq!(calls, 0);
        assert_eq!(failure, Some(ExcType::RuntimeError));
    }
}

#[cfg(test)]
mod exact_line_ledger_projection_tests {
    use super::*;

    fn ids(values: &[&str]) -> MontyObject {
        MontyObject::List(
            values
                .iter()
                .map(|value| MontyObject::String((*value).to_owned()))
                .collect(),
        )
    }

    fn manifest(values: &[(&str, &str)]) -> MontyObject {
        MontyObject::Dict(
            values
                .iter()
                .map(|(id, label)| {
                    (
                        MontyObject::String((*id).to_owned()),
                        MontyObject::String((*label).to_owned()),
                    )
                })
                .collect::<Vec<_>>()
                .into(),
        )
    }

    #[test]
    fn projects_original_occurrences_and_completes_full_expansion() {
        let records = vec![
            "Row: meta=0 :: target=alpha".to_owned(),
            "Row: meta=1 :: target=alpha".to_owned(),
            "Row: meta=2 :: target=beta".to_owned(),
            "Row: meta=3 :: target=gamma".to_owned(),
            "Row: meta=4 :: target=beta".to_owned(),
            "Row: meta=5 :: target=alpha".to_owned(),
        ];
        let mut registry = ExactLineLedgerRegistry::default();
        let ledger = registry.create(records).unwrap();
        let items = registry
            .project(
                &ledger,
                &ids(&["O0", "O1", "O2", "O3", "O4", "O5"]),
                " :: target=",
            )
            .unwrap();
        assert!(matches!(items, MontyObject::List(ref values) if values.len() == 6));
        assert!(registry.projection.is_none());
        let complete = registry
            .complete(&manifest(&[
                ("O0", "left"),
                ("O1", "left"),
                ("O2", "right"),
                ("O3", "left"),
                ("O4", "right"),
                ("O5", "left"),
            ]))
            .unwrap();
        assert!(matches!(complete, MontyObject::Dict(ref values) if values.len() == 6));
        assert_eq!(
            registry.projection,
            Some(SemanticProjectionProvenance {
                ledger_calls: 1,
                projection_calls: 1,
                ledger_occurrences: 6,
                selected_occurrences: 6,
                unique_targets: 3,
                manifest_caller_occurrences: 6,
                expanded_outputs: 6,
            })
        );
        assert!(
            registry
                .complete(&manifest(&[("O0", "left")]))
                .unwrap_err()
                .to_string()
                .contains("only once")
        );
    }

    #[test]
    fn filters_by_canonical_ids_without_losing_source_order() {
        let mut registry = ExactLineLedgerRegistry::default();
        let ledger = registry
            .create(vec![
                "Row: keep=no :: target=zero".to_owned(),
                "Row: keep=yes :: target=one".to_owned(),
                "Row: keep=no :: target=two".to_owned(),
                "Row: keep=yes :: target=three".to_owned(),
            ])
            .unwrap();
        registry
            .project(&ledger, &ids(&["O1", "O3"]), " :: target=")
            .unwrap();
        registry
            .complete(&manifest(&[("O1", "a"), ("O3", "b")]))
            .unwrap();
        let provenance = registry.projection.unwrap();
        assert_eq!(provenance.ledger_occurrences, 4);
        assert_eq!(provenance.selected_occurrences, 2);
        assert_eq!(provenance.expanded_outputs, 2);
    }

    #[test]
    fn rejects_forged_ledgers_bad_selectors_and_ambiguous_markers() {
        let records = vec![
            "Row: n=0 :: target=alpha".to_owned(),
            "Row: n=1 :: target=beta".to_owned(),
        ];
        let mut registry = ExactLineLedgerRegistry::default();
        let ledger = registry.create(records).unwrap();

        let mut wrong_type = ledger.clone();
        if let MontyObject::Dataclass { type_id, .. } = &mut wrong_type {
            *type_id += 1;
        }
        for bad in [
            MontyObject::Tuple(vec![]),
            MontyObject::Dict(Vec::new().into()),
            wrong_type,
        ] {
            assert!(
                registry
                    .project(&bad, &ids(&["O0"]), " :: target=")
                    .is_err()
            );
        }
        let mut mutable = ledger.clone();
        if let MontyObject::Dataclass { frozen, .. } = &mut mutable {
            *frozen = false;
        }
        assert!(
            registry
                .project(&mutable, &ids(&["O0"]), " :: target=")
                .is_err()
        );

        for selected in [
            ids(&[]),
            ids(&["O0", "O0"]),
            ids(&["O1", "O0"]),
            ids(&["O2"]),
            ids(&["O00"]),
            MontyObject::Tuple(vec![MontyObject::String("O0".into())]),
            MontyObject::List(vec![MontyObject::Int(0)]),
        ] {
            assert!(registry.project(&ledger, &selected, " :: target=").is_err());
        }
        for marker in ["", "\n", "missing", "alpha", " :: target=alpha"] {
            assert!(registry.project(&ledger, &ids(&["O0"]), marker).is_err());
        }

        let mut overlap_registry = ExactLineLedgerRegistry::default();
        let overlap = overlap_registry
            .create(vec!["Row: aaaa-tail".to_owned()])
            .unwrap();
        assert!(
            overlap_registry
                .project(&overlap, &ids(&["O0"]), "aa")
                .unwrap_err()
                .to_string()
                .contains("exactly once")
        );

        let mut terminal_registry = ExactLineLedgerRegistry::default();
        let terminal = terminal_registry
            .create(vec!["Row: target=".to_owned()])
            .unwrap();
        assert!(
            terminal_registry
                .project(&terminal, &ids(&["O0"]), "target=")
                .unwrap_err()
                .to_string()
                .contains("nonempty suffix")
        );
    }

    #[test]
    fn validates_expansion_coverage_independent_of_dictionary_order() {
        for bad in [
            manifest(&[("O0", "a")]),
            manifest(&[("O0", "a"), ("O9", "b")]),
            MontyObject::List(vec![]),
        ] {
            let mut registry = ExactLineLedgerRegistry::default();
            let ledger = registry
                .create(vec![
                    "Row: 0 :: target=a".to_owned(),
                    "Row: 1 :: target=b".to_owned(),
                ])
                .unwrap();
            registry
                .project(&ledger, &ids(&["O0", "O1"]), " :: target=")
                .unwrap();
            assert!(registry.complete(&bad).is_err());
            assert!(registry.projection.is_none());
        }
        let mut registry = ExactLineLedgerRegistry::default();
        let ledger = registry
            .create(vec![
                "Row: 0 :: target=a".to_owned(),
                "Row: 1 :: target=b".to_owned(),
            ])
            .unwrap();
        registry
            .project(&ledger, &ids(&["O0", "O1"]), " :: target=")
            .unwrap();
        registry
            .complete(&manifest(&[("O1", "b"), ("O0", "a")]))
            .unwrap();
        assert_eq!(registry.projection.unwrap().expanded_outputs, 2);
    }

    #[test]
    fn exact_line_ledger_is_absent_from_ordinary_exec_cells() {
        let cfg = Config::default();
        let tracker = ResourceTracker::new(ResourceLimits::default());
        let mut repl = MontyRepl::new("ordinary", tracker, CompileOptions::default());
        repl.feed_run(PRELUDE, vec![], PrintWriter::Disabled)
            .unwrap();
        let (_, _, success, _, calls, _, failure, _, provenance) = run_cell(
            repl,
            "exact_line_ledger('Row: x', 'Row: ')",
            &cfg,
            &cfg.default_model,
            false,
            false,
            None,
        );
        assert!(!success);
        assert_eq!(calls, 0);
        assert_eq!(failure, Some(ExcType::RuntimeError));
        assert!(provenance.is_none());
    }

    #[test]
    fn authenticates_full_loaded_context_and_hides_private_callbacks() {
        let root = std::env::temp_dir().join(format!(
            "azdaja-ledger-auth-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir_all(&root).unwrap();
        let path = root.join("ctx.txt");
        fs::write(&path, "header\nRow: one\nRow: two\n").unwrap();
        let cfg = Config::default();

        let mut accepted = SoloSession::new(&cfg, None).unwrap();
        accepted.load(&path, "ctx", &cfg).unwrap();
        let result = accepted
            .exec(
                "ledger=exact_line_ledger(ctx, 'Row: ')\nassert len(ledger.entries)==2\nFINAL('ok')",
                &cfg,
            )
            .unwrap();
        assert!(result.success);
        assert_eq!(result.external_calls, 0);

        let mut cropped = SoloSession::new(&cfg, None).unwrap();
        cropped.load(&path, "ctx", &cfg).unwrap();
        let result = cropped
            .exec("exact_line_ledger('Row: one\\n', 'Row: ')", &cfg)
            .unwrap();
        assert!(!result.success);
        assert!(
            result
                .output
                .contains("source must be the authoritative loaded context")
        );
        assert_eq!(result.external_calls, 0);

        let mut private = SoloSession::new(&cfg, None).unwrap();
        private.load(&path, "ctx", &cfg).unwrap();
        let result = private
            .exec("_az_project_selected(None, [], 'x')", &cfg)
            .unwrap();
        assert!(!result.success);
        assert_eq!(result.external_calls, 0);
        fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn marker_byte_boundaries_and_suffix_bytes_are_exact() {
        let marker = "m".repeat(EXACT_TARGET_MARKER_MAX_BYTES);
        let mut boundary = ExactLineLedgerRegistry::default();
        let ledger = boundary
            .create(vec![format!("Row: {marker}payload")])
            .unwrap();
        boundary.project(&ledger, &ids(&["O0"]), &marker).unwrap();
        boundary.complete(&manifest(&[("O0", "label")])).unwrap();
        assert_eq!(boundary.projection.unwrap().unique_targets, 1);

        let mut oversized = ExactLineLedgerRegistry::default();
        let oversized_marker = "m".repeat(EXACT_TARGET_MARKER_MAX_BYTES + 1);
        let ledger = oversized
            .create(vec![format!("Row: {oversized_marker}payload")])
            .unwrap();
        assert!(
            oversized
                .project(&ledger, &ids(&["O0"]), &oversized_marker)
                .is_err()
        );

        let mut exact = ExactLineLedgerRegistry::default();
        let ledger = exact
            .create(vec![
                "Row: <T>e\u{301}\0 tail  ".to_owned(),
                "Row: <T>é\0 tail  ".to_owned(),
            ])
            .unwrap();
        let items = exact.project(&ledger, &ids(&["O0", "O1"]), "<T>").unwrap();
        let MontyObject::List(items) = items else {
            panic!("projected items must be a list")
        };
        let mut evidence = Vec::new();
        for item in items {
            let MontyObject::Dict(values) = item else {
                panic!("projected item must be a dictionary")
            };
            let (_, MontyObject::String(value)) = values.into_iter().nth(1).unwrap() else {
                panic!("projected evidence must be a string")
            };
            evidence.push(value);
        }
        assert_eq!(evidence, vec!["e\u{301}\0 tail  ", "é\0 tail  "]);
        assert_eq!(exact.pending.as_ref().unwrap().0.unique_targets, 2);
    }

    #[test]
    fn ledger_supports_exactly_one_hundred_five_thousand_records() {
        let records: Vec<_> = (0..EXACT_LINE_RECORD_MAX_ITEMS)
            .map(|index| format!("Row: {index} :: target=same"))
            .collect();
        let mut registry = ExactLineLedgerRegistry::default();
        let ledger = registry.create(records).unwrap();
        registry
            .project(&ledger, &ids(&["O104999"]), " :: target=")
            .unwrap();
        registry
            .complete(&manifest(&[("O104999", "label")]))
            .unwrap();
        let provenance = registry.projection.unwrap();
        assert_eq!(provenance.ledger_occurrences, 105_000);
        assert_eq!(provenance.unique_targets, 1);
    }
}
