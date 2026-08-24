//! Cooperative Jcode hook gate for requiring Azdaja virtual-memory work before broad reads.
//!
//! This module is deliberately a cooperative workflow guard. It does not claim, and must not be
//! presented as providing, security against a malicious same-user process with arbitrary shell or
//! filesystem access. State is nevertheless kept private, validated, and updated atomically so
//! ordinary concurrent hook processes cannot accidentally bypass or corrupt the workflow.

use fs2::FileExt;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::env;
use std::fmt;
use std::fs::{self, File, OpenOptions};
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

#[cfg(unix)]
use std::os::unix::fs::{DirBuilderExt, FileTypeExt, MetadataExt, OpenOptionsExt, PermissionsExt};

/// Environment variable passed to a successful Azdaja `solo` process.
pub const CHALLENGE_ENV: &str = "AZDAJA_JCODE_CHALLENGE";
/// Optional absolute path to the managed Azdaja binary used in block instructions.
pub const MANAGED_BINARY_ENV: &str = "AZDAJA_JCODE_BINARY";
/// A challenge may be completed for ten minutes after it is issued.
pub const CHALLENGE_TTL_SECONDS: u64 = 10 * 60;
/// Aggregate allowance for bounded reads in one Jcode session.
pub const NARROW_SESSION_BUDGET: u64 = 512;

const GATE_DIRECTORY: &str = "jcode-gate";
const CHALLENGE_DIRECTORY: &str = "challenges";
const LOCK_FILE: &str = "gate.lock";
const MAX_STATE_BYTES: u64 = 64 * 1024;
const MAX_NARROW_READ_LINES: u64 = 256;
const MAX_NARROW_GREP_REGIONS: u64 = 8;
const MAX_NARROW_GREP_FILES: u64 = 4;

/// Result of evaluating a hook event.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Decision {
    /// Permit the tool call, or acknowledge an observer event.
    Allow,
    /// Block a `pre_tool` call and return this text on stderr with exit status 2.
    Block(String),
}

impl Decision {
    /// Exit status required by Jcode's lifecycle-hook contract.
    pub fn exit_code(&self) -> u8 {
        match self {
            Self::Allow => 0,
            Self::Block(_) => 2,
        }
    }

    /// Text to write to stderr when the decision blocks a tool call.
    pub fn block_message(&self) -> Option<&str> {
        match self {
            Self::Allow => None,
            Self::Block(message) => Some(message),
        }
    }
}

/// Errors mean the hook implementation itself could not make a decision. Jcode's documented
/// behavior for a nonzero status other than 2 is fail-open.
#[derive(Debug)]
pub enum GateError {
    Io(io::Error),
    Json(serde_json::Error),
    Contract(String),
}

impl fmt::Display for GateError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(error) => write!(f, "{error}"),
            Self::Json(error) => write!(f, "{error}"),
            Self::Contract(message) => f.write_str(message),
        }
    }
}

impl std::error::Error for GateError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::Io(error) => Some(error),
            Self::Json(error) => Some(error),
            Self::Contract(_) => None,
        }
    }
}

impl From<io::Error> for GateError {
    fn from(error: io::Error) -> Self {
        Self::Io(error)
    }
}

impl From<serde_json::Error> for GateError {
    fn from(error: serde_json::Error) -> Self {
        Self::Json(error)
    }
}

pub type GateResult<T> = Result<T, GateError>;

#[derive(Debug)]
struct HookInvocation {
    event: String,
    session_id: Option<String>,
    cwd: Option<PathBuf>,
    tool_name: Option<String>,
}

impl HookInvocation {
    fn from_env() -> GateResult<Self> {
        let event = env::var("JCODE_HOOK_EVENT")
            .map_err(|_| contract("JCODE_HOOK_EVENT is required for a Jcode hook"))?;
        Ok(Self {
            event,
            session_id: env::var("JCODE_HOOK_SESSION_ID").ok(),
            cwd: env::var_os("JCODE_HOOK_CWD").map(PathBuf::from),
            tool_name: env::var("JCODE_HOOK_TOOL_NAME").ok(),
        })
    }

    fn bound_context(&self) -> GateResult<BoundContext> {
        let session_id = self
            .session_id
            .as_deref()
            .filter(|value| !value.is_empty())
            .ok_or_else(|| contract("JCODE_HOOK_SESSION_ID is required for this hook event"))?;
        let cwd = self
            .cwd
            .as_deref()
            .ok_or_else(|| contract("JCODE_HOOK_CWD is required for this hook event"))?;
        BoundContext::new(session_id, cwd)
    }
}

#[derive(Debug, Clone)]
struct BoundContext {
    session_hash: String,
    workspace_hash: String,
    canonical_cwd: PathBuf,
}

impl BoundContext {
    fn new(session_id: &str, cwd: &Path) -> GateResult<Self> {
        let canonical_cwd = fs::canonicalize(cwd).map_err(|error| {
            GateError::Io(io::Error::new(
                error.kind(),
                format!(
                    "cannot canonicalize JCODE_HOOK_CWD {}: {error}",
                    cwd.display()
                ),
            ))
        })?;
        Ok(Self {
            session_hash: sha256_hex(session_id.as_bytes()),
            workspace_hash: sha256_hex(path_bytes(&canonical_cwd).as_ref()),
            canonical_cwd,
        })
    }
}

#[derive(Debug, Default, Serialize, Deserialize)]
struct SessionState {
    session_hash: String,
    workspace_hash: String,
    narrow_units: u64,
    active_challenge: Option<ActiveChallenge>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ActiveChallenge {
    challenge_hash: String,
    expires_at: u64,
}

#[derive(Debug, Serialize, Deserialize)]
struct ChallengeRecord {
    token: String,
    session_hash: String,
    workspace_hash: String,
    required_scope: RequiredScope,
    expires_at: u64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
enum RequiredScope {
    RepositoryBundle,
}

/// Evidence supplied by main from the successful Azdaja execution path.
///
/// The variants intentionally distinguish a complete `--repo` bundle from `-f` and ingestion-only
/// work. A caller must describe the input actually processed, not merely pass the hook workspace.
pub enum CompletionScope<'a> {
    /// A successful `solo ... --repo <root>` bundle over this repository root.
    RepositoryBundle {
        root: &'a Path,
        included_files: usize,
        raw_source_bytes: usize,
    },
    /// A successful file-scoped run such as `solo ... -f <path>`.
    Files { paths: &'a [PathBuf] },
    /// Loading or ingesting inputs without completed semantic work.
    IngestionOnly,
}

/// Evidence for successful, nonempty Azdaja work. Main should construct this only on the final
/// success path, after the final output has been produced.
pub struct SuccessfulAzdajaWork<'a> {
    pub final_output: &'a str,
    pub scope: CompletionScope<'a>,
}

struct Storage {
    root: PathBuf,
    challenges: PathBuf,
    _lock: File,
}

impl Storage {
    fn open(state_root: &Path) -> GateResult<Self> {
        ensure_private_directory(state_root)?;
        let root = state_root.join(GATE_DIRECTORY);
        ensure_private_directory(&root)?;
        let challenges = root.join(CHALLENGE_DIRECTORY);
        ensure_private_directory(&challenges)?;
        let lock = open_private_lock(&root.join(LOCK_FILE))?;
        FileExt::lock_exclusive(&lock)?;
        Ok(Self {
            root,
            challenges,
            _lock: lock,
        })
    }

    fn session_path(&self, session_hash: &str) -> PathBuf {
        debug_assert!(is_lower_hex(session_hash, 64));
        self.root.join(format!("{session_hash}.json"))
    }

    fn challenge_path(&self, challenge_hash: &str) -> PathBuf {
        debug_assert!(is_lower_hex(challenge_hash, 64));
        self.challenges.join(format!("{challenge_hash}.json"))
    }

    fn load_session(&self, session_hash: &str) -> GateResult<Option<SessionState>> {
        let path = self.session_path(session_hash);
        let Some(bytes) = read_private_file(&path)? else {
            return Ok(None);
        };
        let state: SessionState = serde_json::from_slice(&bytes)?;
        if state.session_hash != session_hash
            || !is_lower_hex(&state.workspace_hash, 64)
            || state
                .active_challenge
                .as_ref()
                .is_some_and(|active| !is_lower_hex(&active.challenge_hash, 64))
        {
            return Err(contract("Jcode gate session state binding is invalid"));
        }
        Ok(Some(state))
    }

    fn save_session(&self, state: &SessionState) -> GateResult<()> {
        if !is_lower_hex(&state.session_hash, 64) || !is_lower_hex(&state.workspace_hash, 64) {
            return Err(contract(
                "refusing to save invalid Jcode gate state binding",
            ));
        }
        atomic_private_write(
            &self.session_path(&state.session_hash),
            &serde_json::to_vec(state)?,
        )
    }

    fn load_challenge(&self, challenge_hash: &str) -> GateResult<Option<ChallengeRecord>> {
        if !is_lower_hex(challenge_hash, 64) {
            return Err(contract("invalid private challenge-state key"));
        }
        let path = self.challenge_path(challenge_hash);
        let Some(bytes) = read_private_file(&path)? else {
            return Ok(None);
        };
        let record: ChallengeRecord = serde_json::from_slice(&bytes)?;
        if !is_lower_hex(&record.token, 32)
            || sha256_hex(record.token.as_bytes()) != challenge_hash
            || !is_lower_hex(&record.session_hash, 64)
            || !is_lower_hex(&record.workspace_hash, 64)
        {
            return Err(contract("private challenge state binding is invalid"));
        }
        Ok(Some(record))
    }

    fn save_challenge(&self, challenge_hash: &str, record: &ChallengeRecord) -> GateResult<()> {
        atomic_private_write(
            &self.challenge_path(challenge_hash),
            &serde_json::to_vec(record)?,
        )
    }

    fn remove_challenge(&self, challenge_hash: &str) -> GateResult<()> {
        remove_private_file_if_present(&self.challenge_path(challenge_hash))
    }

    fn remove_session(&self, session_hash: &str) -> GateResult<()> {
        remove_private_file_if_present(&self.session_path(session_hash))
    }
}

/// Handle the current event from the documented `JCODE_HOOK_*` environment contract.
///
/// `tool_input` must be the complete `pre_tool` stdin JSON, not the truncated environment copy.
/// Observer events ignore it. The caller should map [`Decision::Allow`] to exit 0 and
/// [`Decision::Block`] to stderr plus exit 2.
pub fn handle_current_hook(state_root: &Path, tool_input: &[u8]) -> GateResult<Decision> {
    let invocation = HookInvocation::from_env()?;
    let binary = if invocation.event == "pre_tool" {
        managed_binary_path()?
    } else {
        PathBuf::new()
    };
    handle_at(
        state_root,
        &invocation,
        tool_input,
        unix_time_seconds()?,
        &binary,
    )
}

/// Read complete tool input from stdin and handle the current hook event.
pub fn handle_current_hook_from_stdin(state_root: &Path) -> GateResult<Decision> {
    let mut input = Vec::new();
    io::stdin().read_to_end(&mut input)?;
    handle_current_hook(state_root, &input)
}

/// Resolve the same state root as the crate: `AZDAJA_HOME`, then `XDG_STATE_HOME/azdaja`, then
/// `$HOME/.local/state/azdaja`. Overrides must be absolute.
pub fn crate_state_root() -> GateResult<PathBuf> {
    if let Some(value) = env::var_os("AZDAJA_HOME") {
        return absolute_override("AZDAJA_HOME", value);
    }
    if let Some(value) = env::var_os("XDG_STATE_HOME") {
        return Ok(absolute_override("XDG_STATE_HOME", value)?.join("azdaja"));
    }
    let home = env::var_os("HOME")
        .map(PathBuf::from)
        .filter(|path| path.is_absolute())
        .ok_or_else(|| contract("no absolute home directory; set AZDAJA_HOME"))?;
    Ok(home.join(".local/state/azdaja"))
}

/// Handle the current hook event using the crate state root.
pub fn handle_current_hook_in_crate_state(tool_input: &[u8]) -> GateResult<Decision> {
    handle_current_hook(&crate_state_root()?, tool_input)
}

/// Consume the challenge named by [`CHALLENGE_ENV`] after successful, nonempty Azdaja work.
///
/// Main must call this only after `solo` has produced its successful final output. Skill loading,
/// source ingestion, failed work, and intermediate output must never call this function. Empty
/// final output is rejected. The supplied scope must describe the inputs that the successful run
/// actually processed. Repository challenges accept only a canonical-root-matching `--repo` bundle.
/// Completion proves the memory pass and consumes the challenge, but never unlocks native broad
/// reads; callers must continue from the successful Azdaja answer.
pub fn complete_challenge(state_root: &Path, work: SuccessfulAzdajaWork<'_>) -> GateResult<bool> {
    if work.final_output.trim().is_empty() {
        return Err(contract(
            "empty Azdaja work cannot complete a Jcode challenge",
        ));
    }
    let Some(token) = env::var(CHALLENGE_ENV)
        .ok()
        .filter(|value| !value.is_empty())
    else {
        return Ok(false);
    };
    complete_at(state_root, &token, &work, unix_time_seconds()?)?;
    Ok(true)
}

/// Complete a challenge using the crate state root.
pub fn complete_challenge_in_crate_state(work: SuccessfulAzdajaWork<'_>) -> GateResult<bool> {
    complete_challenge(&crate_state_root()?, work)
}

fn handle_at(
    state_root: &Path,
    invocation: &HookInvocation,
    tool_input: &[u8],
    now: u64,
    binary: &Path,
) -> GateResult<Decision> {
    match invocation.event.as_str() {
        "pre_tool" => handle_pre_tool(state_root, invocation, tool_input, now, binary),
        "turn_end" | "session_start" => {
            let context = invocation.bound_context()?;
            revoke_turn(state_root, &context)?;
            Ok(Decision::Allow)
        }
        "session_end" => {
            let context = invocation.bound_context()?;
            revoke_session(state_root, &context)?;
            Ok(Decision::Allow)
        }
        "post_tool" => Ok(Decision::Allow),
        _ => Ok(Decision::Allow),
    }
}

fn handle_pre_tool(
    state_root: &Path,
    invocation: &HookInvocation,
    tool_input: &[u8],
    now: u64,
    binary: &Path,
) -> GateResult<Decision> {
    let context = invocation.bound_context()?;
    let tool_name = invocation
        .tool_name
        .as_deref()
        .filter(|value| !value.is_empty())
        .ok_or_else(|| contract("JCODE_HOOK_TOOL_NAME is required for pre_tool"))?;
    let input: Value = serde_json::from_slice(tool_input)?;
    let requirement = classify_tool(tool_name, &input, 0);
    let storage = Storage::open(state_root)?;
    let mut state = storage
        .load_session(&context.session_hash)?
        .unwrap_or_else(|| SessionState {
            session_hash: context.session_hash.clone(),
            workspace_hash: context.workspace_hash.clone(),
            ..SessionState::default()
        });

    if state.workspace_hash != context.workspace_hash {
        discard_active_challenge(&storage, &mut state)?;
        state.workspace_hash.clone_from(&context.workspace_hash);
        storage.save_session(&state)?;
    }

    if let Some(active) = state.active_challenge.as_ref()
        && now >= active.expires_at
    {
        let hash = active.challenge_hash.clone();
        state.active_challenge = None;
        storage.remove_challenge(&hash)?;
        storage.save_session(&state)?;
    }

    match requirement {
        Requirement::Free => Ok(Decision::Allow),
        Requirement::Narrow(units) => {
            let next = state.narrow_units.saturating_add(units);
            if next <= NARROW_SESSION_BUDGET {
                state.narrow_units = next;
                storage.save_session(&state)?;
                Ok(Decision::Allow)
            } else {
                block_with_challenge(&storage, &mut state, &context, now, binary)
            }
        }
        Requirement::Memory => block_with_challenge(&storage, &mut state, &context, now, binary),
    }
}

fn block_with_challenge(
    storage: &Storage,
    state: &mut SessionState,
    context: &BoundContext,
    now: u64,
    binary: &Path,
) -> GateResult<Decision> {
    let token = if let Some(active) = state.active_challenge.as_ref() {
        if active.expires_at > now {
            storage
                .load_challenge(&active.challenge_hash)?
                .filter(|record| {
                    record.session_hash == context.session_hash
                        && record.workspace_hash == context.workspace_hash
                        && record.expires_at == active.expires_at
                })
                .map(|record| record.token)
        } else {
            None
        }
    } else {
        None
    };

    let token = match token {
        Some(token) => token,
        None => {
            discard_active_challenge(storage, state)?;
            let token = hex(&os_random_128()?);
            let challenge_hash = sha256_hex(token.as_bytes());
            let expires_at = now.saturating_add(CHALLENGE_TTL_SECONDS);
            storage.save_challenge(
                &challenge_hash,
                &ChallengeRecord {
                    token: token.clone(),
                    session_hash: context.session_hash.clone(),
                    workspace_hash: context.workspace_hash.clone(),
                    required_scope: RequiredScope::RepositoryBundle,
                    expires_at,
                },
            )?;
            state.active_challenge = Some(ActiveChallenge {
                challenge_hash,
                expires_at,
            });
            storage.save_session(state)?;
            token
        }
    };

    Ok(Decision::Block(format!(
        "Azdaja should carry this broad read.\nRun the exact challenged command once and continue from its answer:\n  {CHALLENGE_ENV}={token} {} solo \"<user task>\" --repo {}\nDo not retry the blocked broad read. Narrow reads, Git, builds, and tests are still available.",
        shell_quote(binary),
        shell_quote(&context.canonical_cwd)
    )))
}

fn complete_at(
    state_root: &Path,
    token: &str,
    work: &SuccessfulAzdajaWork<'_>,
    now: u64,
) -> GateResult<()> {
    if work.final_output.trim().is_empty() {
        return Err(contract(
            "empty Azdaja work cannot complete a Jcode challenge",
        ));
    }
    if !is_lower_hex(token, 32) {
        return Err(contract(
            "AZDAJA_JCODE_CHALLENGE is not a 128-bit challenge",
        ));
    }
    let challenge_hash = sha256_hex(token.as_bytes());
    let storage = Storage::open(state_root)?;
    let record = storage
        .load_challenge(&challenge_hash)?
        .ok_or_else(|| contract("unknown or already completed AZDAJA_JCODE_CHALLENGE"))?;
    if record.token != token {
        return Err(contract(
            "AZDAJA_JCODE_CHALLENGE does not match private state",
        ));
    }
    if now >= record.expires_at {
        storage.remove_challenge(&challenge_hash)?;
        if let Some(mut state) = storage.load_session(&record.session_hash)?
            && state
                .active_challenge
                .as_ref()
                .is_some_and(|active| active.challenge_hash == challenge_hash)
        {
            state.active_challenge = None;
            storage.save_session(&state)?;
        }
        return Err(contract("AZDAJA_JCODE_CHALLENGE has expired"));
    }
    let supplied_workspace_hash = match (&record.required_scope, &work.scope) {
        (
            RequiredScope::RepositoryBundle,
            CompletionScope::RepositoryBundle {
                root,
                included_files,
                raw_source_bytes,
            },
        ) => {
            if *included_files == 0 || *raw_source_bytes == 0 {
                return Err(contract(
                    "empty repository evidence cannot complete a Jcode challenge",
                ));
            }
            let canonical_root = fs::canonicalize(root)?;
            sha256_hex(path_bytes(&canonical_root).as_ref())
        }
        (RequiredScope::RepositoryBundle, CompletionScope::Files { .. }) => {
            return Err(contract(
                "file-scoped Azdaja work cannot complete a repository challenge",
            ));
        }
        (RequiredScope::RepositoryBundle, CompletionScope::IngestionOnly) => {
            return Err(contract(
                "Azdaja ingestion without completed repository work cannot complete a challenge",
            ));
        }
    };
    if record.workspace_hash != supplied_workspace_hash {
        return Err(contract(
            "AZDAJA_JCODE_CHALLENGE repository bundle does not match --repo",
        ));
    }
    let mut state = storage
        .load_session(&record.session_hash)?
        .ok_or_else(|| contract("AZDAJA_JCODE_CHALLENGE session is no longer active"))?;
    if state.workspace_hash != record.workspace_hash
        || !state.active_challenge.as_ref().is_some_and(|active| {
            active.challenge_hash == challenge_hash && active.expires_at == record.expires_at
        })
    {
        return Err(contract("AZDAJA_JCODE_CHALLENGE is revoked or not active"));
    }
    state.active_challenge = None;
    storage.save_session(&state)?;
    storage.remove_challenge(&challenge_hash)?;
    Ok(())
}

fn revoke_turn(state_root: &Path, context: &BoundContext) -> GateResult<()> {
    let storage = Storage::open(state_root)?;
    let Some(mut state) = storage.load_session(&context.session_hash)? else {
        return Ok(());
    };
    if state.workspace_hash != context.workspace_hash {
        return Ok(());
    }
    discard_active_challenge(&storage, &mut state)?;
    storage.save_session(&state)
}

fn revoke_session(state_root: &Path, context: &BoundContext) -> GateResult<()> {
    let storage = Storage::open(state_root)?;
    let Some(mut state) = storage.load_session(&context.session_hash)? else {
        return Ok(());
    };
    discard_active_challenge(&storage, &mut state)?;
    storage.remove_session(&context.session_hash)
}

fn discard_active_challenge(storage: &Storage, state: &mut SessionState) -> GateResult<()> {
    if let Some(active) = state.active_challenge.take() {
        storage.remove_challenge(&active.challenge_hash)?;
    }
    Ok(())
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Requirement {
    Free,
    Narrow(u64),
    Memory,
}

fn classify_tool(tool_name: &str, input: &Value, depth: usize) -> Requirement {
    if depth > 16 {
        return Requirement::Memory;
    }
    match normalized_tool_name(tool_name) {
        "read" => classify_read(input),
        "agentgrep" => classify_agentgrep(input),
        "bash" => classify_bash(input),
        "batch" => classify_batch(input, depth + 1),
        _ => Requirement::Free,
    }
}

fn normalized_tool_name(name: &str) -> &str {
    name.rsplit(['.', ':', '/']).next().unwrap_or(name)
}

fn classify_read(input: &Value) -> Requirement {
    let Some(object) = input.as_object() else {
        return Requirement::Memory;
    };
    let Some(path) = object.get("file_path").and_then(Value::as_str) else {
        return Requirement::Memory;
    };
    if path.trim().is_empty() || path.contains(['*', '?', '[', ']']) {
        return Requirement::Memory;
    }
    let Some(limit) = object.get("limit").and_then(Value::as_u64) else {
        return Requirement::Memory;
    };
    if limit == 0 || limit > MAX_NARROW_READ_LINES {
        return Requirement::Memory;
    }
    if object
        .get("start_line")
        .is_some_and(|value| value.as_u64().is_none_or(|line| line == 0))
    {
        return Requirement::Memory;
    }
    Requirement::Narrow(limit.max(1))
}

fn classify_agentgrep(input: &Value) -> Requirement {
    let Some(object) = input.as_object() else {
        return Requirement::Memory;
    };
    let mode = object.get("mode").and_then(Value::as_str).unwrap_or("grep");
    let scoped_path = object
        .get("path")
        .and_then(Value::as_str)
        .is_some_and(is_narrow_scope);
    match mode {
        "outline" => {
            if object
                .get("file")
                .and_then(Value::as_str)
                .is_some_and(|file| !file.trim().is_empty())
            {
                Requirement::Narrow(192)
            } else {
                Requirement::Memory
            }
        }
        "grep" | "find" | "trace" => {
            let has_selector = match mode {
                "trace" => object
                    .get("terms")
                    .and_then(Value::as_array)
                    .is_some_and(|terms| !terms.is_empty()),
                _ => object
                    .get("query")
                    .and_then(Value::as_str)
                    .is_some_and(|query| !query.trim().is_empty()),
            };
            let files = object.get("max_files").and_then(Value::as_u64);
            let regions = object.get("max_regions").and_then(Value::as_u64);
            if scoped_path
                && has_selector
                && files.is_some_and(|value| (1..=MAX_NARROW_GREP_FILES).contains(&value))
                && regions.is_some_and(|value| (1..=MAX_NARROW_GREP_REGIONS).contains(&value))
            {
                Requirement::Narrow(
                    files.unwrap_or(1).saturating_mul(8) + regions.unwrap_or(1).saturating_mul(32),
                )
            } else {
                Requirement::Memory
            }
        }
        _ => Requirement::Memory,
    }
}

fn is_narrow_scope(path: &str) -> bool {
    let path = path.trim();
    !path.is_empty() && path != "." && path != ".." && path != "/"
}

fn classify_batch(input: &Value, depth: usize) -> Requirement {
    let Some(calls) = input.get("tool_calls").and_then(Value::as_array) else {
        return Requirement::Memory;
    };
    if calls.is_empty() {
        return Requirement::Free;
    }
    let mut units = 0u64;
    for call in calls {
        let Some(tool) = call.get("tool").and_then(Value::as_str) else {
            return Requirement::Memory;
        };
        let nested_input = call.get("input").unwrap_or(call);
        match classify_tool(tool, nested_input, depth) {
            Requirement::Free => {}
            Requirement::Narrow(value) => units = units.saturating_add(value),
            Requirement::Memory => return Requirement::Memory,
        }
    }
    if units == 0 {
        Requirement::Free
    } else {
        Requirement::Narrow(units)
    }
}

fn classify_bash(input: &Value) -> Requirement {
    let Some(command) = input.get("command").and_then(Value::as_str) else {
        return Requirement::Memory;
    };
    if is_git_build_test_lint_or_format(command) {
        return Requirement::Free;
    }
    if bash_reads_content(command) {
        Requirement::Memory
    } else {
        Requirement::Free
    }
}

fn is_git_build_test_lint_or_format(command: &str) -> bool {
    if command.contains("$('") || command.contains("$(") || command.contains('`') {
        return false;
    }
    let mut saw_command = false;
    for segment in command.split(['\n', ';']).flat_map(|part| part.split("&&")) {
        for alternative in segment.split("||") {
            let segment = alternative.trim();
            if segment.is_empty() {
                continue;
            }
            if segment.contains('|') || segment.contains('>') || segment.contains('<') {
                return false;
            }
            let words: Vec<&str> = segment.split_whitespace().collect();
            let Some((program, arguments)) = command_words(&words) else {
                continue;
            };
            saw_command = true;
            let program = program.rsplit('/').next().unwrap_or(program);
            let first = arguments.first().copied().unwrap_or("");
            let allowed = match program {
                "git" => true,
                "cargo" => matches!(
                    first,
                    "build" | "check" | "test" | "clippy" | "fmt" | "bench" | "doc"
                ),
                "rustc" | "rustfmt" | "make" | "gmake" | "ninja" | "pytest" | "ruff" | "black"
                | "eslint" | "prettier" => true,
                "go" => matches!(first, "build" | "test" | "vet" | "fmt"),
                "npm" | "pnpm" | "yarn" | "bun" => matches!(
                    first,
                    "test" | "build" | "lint" | "format" | "fmt" | "check" | "run"
                ),
                "mvn" | "mvnw" | "gradle" | "gradlew" => true,
                "cmake" => arguments.contains(&"--build") || arguments.contains(&"--check"),
                "cd" => true,
                _ => false,
            };
            if !allowed {
                return false;
            }
        }
    }
    saw_command
}

fn command_words<'a>(words: &'a [&'a str]) -> Option<(&'a str, &'a [&'a str])> {
    let mut index = 0;
    if words.first().copied() == Some("env") {
        index += 1;
    }
    while words
        .get(index)
        .is_some_and(|word| is_environment_assignment(word))
    {
        index += 1;
    }
    words
        .get(index)
        .map(|program| (*program, &words[index + 1..]))
}

fn is_environment_assignment(word: &str) -> bool {
    let Some((name, _)) = word.split_once('=') else {
        return false;
    };
    !name.is_empty()
        && name
            .bytes()
            .all(|byte| byte == b'_' || byte.is_ascii_alphanumeric())
}

fn bash_reads_content(command: &str) -> bool {
    let lower = command.to_ascii_lowercase();
    if lower.contains(".read(")
        || lower.contains("read_to_string")
        || lower.contains("fs::read")
        || lower.contains("path.read_text")
        || lower.contains("open(")
    {
        return true;
    }
    lower
        .split(|character: char| {
            character.is_whitespace()
                || matches!(
                    character,
                    ';' | '&' | '|' | '(' | ')' | '{' | '}' | '<' | '>'
                )
        })
        .filter(|token| !token.is_empty())
        .map(|token| token.rsplit('/').next().unwrap_or(token))
        .any(|program| {
            matches!(
                program,
                "cat"
                    | "tac"
                    | "sh"
                    | "bash"
                    | "zsh"
                    | "fish"
                    | "python"
                    | "python3"
                    | "perl"
                    | "ruby"
                    | "node"
                    | "deno"
                    | "php"
                    | "sed"
                    | "awk"
                    | "gawk"
                    | "grep"
                    | "egrep"
                    | "fgrep"
                    | "rg"
                    | "ripgrep"
                    | "head"
                    | "tail"
                    | "less"
                    | "more"
                    | "strings"
                    | "jq"
                    | "yq"
                    | "xxd"
                    | "od"
                    | "hexdump"
                    | "nl"
                    | "fold"
                    | "comm"
                    | "diff"
                    | "find"
                    | "wc"
                    | "cut"
                    | "paste"
                    | "sort"
                    | "uniq"
            )
        })
}

fn managed_binary_path() -> GateResult<PathBuf> {
    for name in [MANAGED_BINARY_ENV, "AZDAJA_BINARY"] {
        if let Some(value) = env::var_os(name) {
            return absolute_override(name, value);
        }
    }
    let binary = env::current_exe()?;
    if !binary.is_absolute() {
        return Err(contract(
            "current_exe did not return an absolute binary path",
        ));
    }
    Ok(binary)
}

fn absolute_override(name: &str, value: std::ffi::OsString) -> GateResult<PathBuf> {
    let path = PathBuf::from(value);
    if path.as_os_str().is_empty() || !path.is_absolute() {
        return Err(contract(format!(
            "{name} must be set to a non-empty absolute path"
        )));
    }
    Ok(path)
}

fn unix_time_seconds() -> GateResult<u64> {
    Ok(SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|_| contract("system clock is before the Unix epoch"))?
        .as_secs())
}

fn contract(message: impl Into<String>) -> GateError {
    GateError::Contract(message.into())
}

fn is_lower_hex(value: &str, length: usize) -> bool {
    value.len() == length
        && value
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit() && !byte.is_ascii_uppercase())
}

fn hex(bytes: &[u8]) -> String {
    const DIGITS: &[u8; 16] = b"0123456789abcdef";
    let mut output = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        output.push(DIGITS[(byte >> 4) as usize] as char);
        output.push(DIGITS[(byte & 0x0f) as usize] as char);
    }
    output
}

#[cfg(unix)]
fn path_bytes(path: &Path) -> std::borrow::Cow<'_, [u8]> {
    use std::os::unix::ffi::OsStrExt;
    std::borrow::Cow::Borrowed(path.as_os_str().as_bytes())
}

#[cfg(not(unix))]
fn path_bytes(path: &Path) -> std::borrow::Cow<'_, [u8]> {
    std::borrow::Cow::Owned(path.as_os_str().to_string_lossy().as_bytes().to_vec())
}

fn shell_quote(path: &Path) -> String {
    let value = path.as_os_str().to_string_lossy();
    if !value.is_empty()
        && value.bytes().all(|byte| {
            byte.is_ascii_alphanumeric() || matches!(byte, b'/' | b'.' | b'_' | b'-' | b':' | b'+')
        })
    {
        return value.into_owned();
    }
    format!("'{}'", value.replace('\'', "'\\''"))
}

fn ensure_private_directory(path: &Path) -> GateResult<()> {
    if !path.exists() {
        #[cfg(unix)]
        {
            let mut builder = fs::DirBuilder::new();
            builder.recursive(true).mode(0o700).create(path)?;
        }
        #[cfg(not(unix))]
        fs::create_dir_all(path)?;
    }
    let metadata = fs::symlink_metadata(path)?;
    if metadata.file_type().is_symlink() || !metadata.file_type().is_dir() {
        return Err(contract(format!(
            "private state path is not a real directory: {}",
            path.display()
        )));
    }
    #[cfg(unix)]
    {
        if metadata.uid() != unsafe { libc::geteuid() } {
            return Err(contract(format!(
                "private state directory is not owned by the current user: {}",
                path.display()
            )));
        }
        if metadata.permissions().mode() & 0o077 != 0 {
            return Err(contract(format!(
                "private state directory is accessible by group or other users: {}",
                path.display()
            )));
        }
    }
    Ok(())
}

fn open_private_lock(path: &Path) -> GateResult<File> {
    let mut options = OpenOptions::new();
    options.read(true).write(true).create(true);
    #[cfg(unix)]
    options.mode(0o600).custom_flags(libc::O_NOFOLLOW);
    let file = options.open(path)?;
    validate_private_file(&file, path)?;
    Ok(file)
}

fn read_private_file(path: &Path) -> GateResult<Option<Vec<u8>>> {
    let mut options = OpenOptions::new();
    options.read(true);
    #[cfg(unix)]
    options.custom_flags(libc::O_NOFOLLOW);
    let file = match options.open(path) {
        Ok(file) => file,
        Err(error) if error.kind() == io::ErrorKind::NotFound => return Ok(None),
        Err(error) => return Err(error.into()),
    };
    validate_private_file(&file, path)?;
    let mut bytes = Vec::new();
    file.take(MAX_STATE_BYTES + 1).read_to_end(&mut bytes)?;
    if bytes.len() as u64 > MAX_STATE_BYTES {
        return Err(contract(format!(
            "private state file is too large: {}",
            path.display()
        )));
    }
    Ok(Some(bytes))
}

fn validate_private_file(file: &File, path: &Path) -> GateResult<()> {
    let opened = file.metadata()?;
    if !opened.file_type().is_file() {
        return Err(contract(format!(
            "private state path is not a regular file: {}",
            path.display()
        )));
    }
    #[cfg(unix)]
    {
        let named = fs::symlink_metadata(path)?;
        if named.file_type().is_symlink()
            || !named.file_type().is_file()
            || opened.dev() != named.dev()
            || opened.ino() != named.ino()
        {
            return Err(contract("private state path no longer names its open file"));
        }
        if opened.uid() != unsafe { libc::geteuid() }
            || opened.nlink() != 1
            || opened.permissions().mode() & 0o077 != 0
        {
            return Err(contract(format!(
                "private state file has unsafe ownership, links, or permissions: {}",
                path.display()
            )));
        }
    }
    Ok(())
}

fn atomic_private_write(path: &Path, bytes: &[u8]) -> GateResult<()> {
    let parent = path
        .parent()
        .ok_or_else(|| contract("private state file has no parent"))?;
    ensure_private_directory(parent)?;
    if let Some(existing) = read_private_file(path)? {
        drop(existing);
    }
    for _ in 0..32 {
        let suffix = hex(&os_random_128()?);
        let temporary = parent.join(format!(".tmp-{suffix}"));
        let mut options = OpenOptions::new();
        options.write(true).create_new(true);
        #[cfg(unix)]
        options.mode(0o600).custom_flags(libc::O_NOFOLLOW);
        let mut file = match options.open(&temporary) {
            Ok(file) => file,
            Err(error) if error.kind() == io::ErrorKind::AlreadyExists => continue,
            Err(error) => return Err(error.into()),
        };
        let result = (|| -> GateResult<()> {
            file.write_all(bytes)?;
            file.sync_all()?;
            validate_private_file(&file, &temporary)?;
            drop(file);
            fs::rename(&temporary, path)?;
            #[cfg(unix)]
            File::open(parent)?.sync_all()?;
            Ok(())
        })();
        if result.is_err() {
            let _ = fs::remove_file(&temporary);
        }
        return result;
    }
    Err(contract("could not allocate a private atomic state file"))
}

fn remove_private_file_if_present(path: &Path) -> GateResult<()> {
    let Some(bytes) = read_private_file(path)? else {
        return Ok(());
    };
    drop(bytes);
    match fs::remove_file(path) {
        Ok(()) => Ok(()),
        Err(error) if error.kind() == io::ErrorKind::NotFound => Ok(()),
        Err(error) => Err(error.into()),
    }
}

#[cfg(unix)]
fn os_random_128() -> GateResult<[u8; 16]> {
    let mut options = OpenOptions::new();
    options.read(true).custom_flags(libc::O_NOFOLLOW);
    let mut file = options.open("/dev/urandom")?;
    let metadata = file.metadata()?;
    if !metadata.file_type().is_char_device() {
        return Err(contract("/dev/urandom is not a character device"));
    }
    let mut bytes = [0u8; 16];
    file.read_exact(&mut bytes)?;
    Ok(bytes)
}

#[cfg(windows)]
fn os_random_128() -> GateResult<[u8; 16]> {
    #[link(name = "bcrypt")]
    unsafe extern "system" {
        fn BCryptGenRandom(
            algorithm: *mut std::ffi::c_void,
            buffer: *mut u8,
            length: u32,
            flags: u32,
        ) -> i32;
    }
    const BCRYPT_USE_SYSTEM_PREFERRED_RNG: u32 = 0x0000_0002;
    let mut bytes = [0u8; 16];
    let status = unsafe {
        BCryptGenRandom(
            std::ptr::null_mut(),
            bytes.as_mut_ptr(),
            bytes.len() as u32,
            BCRYPT_USE_SYSTEM_PREFERRED_RNG,
        )
    };
    if status < 0 {
        return Err(contract(format!(
            "BCryptGenRandom failed with status {status:#x}"
        )));
    }
    Ok(bytes)
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
    let mut output = String::with_capacity(64);
    for word in state {
        output.push_str(&format!("{word:08x}"));
    }
    output
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[cfg(unix)]
    use std::os::unix::fs::DirBuilderExt;
    use std::sync::atomic::{AtomicU64, Ordering};

    static TEMP_COUNTER: AtomicU64 = AtomicU64::new(0);
    const NOW: u64 = 1_800_000_000;

    struct Scratch {
        root: PathBuf,
        cwd: PathBuf,
        other: PathBuf,
    }

    impl Scratch {
        fn new() -> Self {
            let suffix = TEMP_COUNTER.fetch_add(1, Ordering::Relaxed);
            let root = env::temp_dir().join(format!(
                "azdaja-jcode-gate-test-{}-{suffix}",
                std::process::id()
            ));
            #[cfg(unix)]
            {
                let mut builder = fs::DirBuilder::new();
                builder.recursive(true).mode(0o700).create(&root).unwrap();
            }
            #[cfg(not(unix))]
            fs::create_dir_all(&root).unwrap();
            let cwd = root.join("repo");
            let other = root.join("other-repo");
            fs::create_dir(&cwd).unwrap();
            fs::create_dir(&other).unwrap();
            Self { root, cwd, other }
        }

        fn state(&self) -> PathBuf {
            let state = self.root.join("state");
            #[cfg(unix)]
            {
                let mut builder = fs::DirBuilder::new();
                builder.mode(0o700).create(&state).unwrap();
            }
            #[cfg(not(unix))]
            fs::create_dir(&state).unwrap();
            state
        }
    }

    impl Drop for Scratch {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.root);
        }
    }

    fn invocation(event: &str, cwd: &Path, tool: Option<&str>) -> HookInvocation {
        HookInvocation {
            event: event.to_owned(),
            session_id: Some("session/raw id".to_owned()),
            cwd: Some(cwd.to_path_buf()),
            tool_name: tool.map(str::to_owned),
        }
    }

    fn call(state: &Path, cwd: &Path, tool: &str, input: Value, now: u64) -> GateResult<Decision> {
        handle_at(
            state,
            &invocation("pre_tool", cwd, Some(tool)),
            &serde_json::to_vec(&input).unwrap(),
            now,
            Path::new("/managed/azdaja"),
        )
    }

    fn token(decision: &Decision) -> String {
        let Decision::Block(message) = decision else {
            panic!("expected block, got {decision:?}");
        };
        let prefix = format!("{CHALLENGE_ENV}=");
        message[message.find(&prefix).expect("challenge assignment") + prefix.len()..]
            .split_whitespace()
            .next()
            .unwrap()
            .to_owned()
    }

    fn completed_repo<'a>(root: &'a Path, output: &'a str) -> SuccessfulAzdajaWork<'a> {
        SuccessfulAzdajaWork {
            final_output: output,
            scope: CompletionScope::RepositoryBundle {
                root,
                included_files: 2,
                raw_source_bytes: 64,
            },
        }
    }

    fn broad_read() -> Value {
        json!({"file_path":"src/lib.rs","start_line":1,"limit":5000})
    }

    #[test]
    fn blocked_before_completion_uses_exact_managed_command_pattern() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let decision = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let challenge = token(&decision);
        assert!(is_lower_hex(&challenge, 32));
        let expected = format!(
            "Azdaja should carry this broad read.\nRun the exact challenged command once and continue from its answer:\n  {CHALLENGE_ENV}={challenge} /managed/azdaja solo \"<user task>\" --repo {}\nDo not retry the blocked broad read. Narrow reads, Git, builds, and tests are still available.",
            scratch.cwd.display()
        );
        assert_eq!(decision, Decision::Block(expected));
        assert_eq!(decision.exit_code(), 2);
    }

    #[test]
    fn narrow_explicit_read_is_allowed_and_charged() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let decision = call(
            &state,
            &scratch.cwd,
            "functions.read",
            json!({"file_path":"src/lib.rs","start_line":10,"limit":64}),
            NOW,
        )
        .unwrap();
        assert_eq!(decision, Decision::Allow);
        let context = BoundContext::new("session/raw id", &scratch.cwd).unwrap();
        let storage = Storage::open(&state).unwrap();
        assert_eq!(
            storage
                .load_session(&context.session_hash)
                .unwrap()
                .unwrap()
                .narrow_units,
            64
        );
    }

    #[test]
    fn recursive_batch_blocks_when_any_nested_call_is_broad() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let decision = call(
            &state,
            &scratch.cwd,
            "batch",
            json!({"tool_calls":[
                {"tool":"read","file_path":"README.md","start_line":1,"limit":20},
                {"tool":"batch","input":{"tool_calls":[
                    {"tool":"agentgrep","query":"thing","path":".","max_files":50,"max_regions":50}
                ]}}
            ]}),
            NOW,
        )
        .unwrap();
        assert!(matches!(decision, Decision::Block(_)));
    }

    #[test]
    fn git_build_test_lint_and_format_commands_are_allowed() {
        let scratch = Scratch::new();
        let state = scratch.state();
        for command in [
            "git diff --stat",
            "cargo build --locked",
            "cargo test --all-targets",
            "cargo clippy --all-targets",
            "cargo fmt --check",
        ] {
            assert_eq!(
                call(
                    &state,
                    &scratch.cwd,
                    "bash",
                    json!({"command":command}),
                    NOW,
                )
                .unwrap(),
                Decision::Allow,
                "{command}"
            );
        }
    }

    #[test]
    fn broad_content_reading_bash_is_blocked_but_git_inspection_is_allowed() {
        let scratch = Scratch::new();
        let state = scratch.state();
        assert!(matches!(
            call(
                &state,
                &scratch.cwd,
                "bash",
                json!({"command":"cat src/lib.rs"}),
                NOW,
            )
            .unwrap(),
            Decision::Block(_)
        ));
        assert_eq!(
            call(
                &state,
                &scratch.cwd,
                "bash",
                json!({"command":"git show HEAD:src/lib.rs"}),
                NOW,
            )
            .unwrap(),
            Decision::Allow
        );
    }

    #[test]
    fn repository_challenge_rejects_a_different_canonical_workspace() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let error = complete_at(
            &state,
            &token(&blocked),
            &completed_repo(&scratch.other, "answer"),
            NOW + 1,
        )
        .unwrap_err();
        assert!(error.to_string().contains("does not match --repo"));
        assert!(matches!(
            call(&state, &scratch.cwd, "read", broad_read(), NOW + 2).unwrap(),
            Decision::Block(_)
        ));
    }

    #[test]
    fn expired_challenge_cannot_complete() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let error = complete_at(
            &state,
            &token(&blocked),
            &completed_repo(&scratch.cwd, "answer"),
            NOW + CHALLENGE_TTL_SECONDS,
        )
        .unwrap_err();
        assert!(error.to_string().contains("expired"));
        assert!(matches!(
            call(
                &state,
                &scratch.cwd,
                "read",
                broad_read(),
                NOW + CHALLENGE_TTL_SECONDS
            )
            .unwrap(),
            Decision::Block(_)
        ));
    }

    #[test]
    fn completion_never_enables_broad_work_before_or_after_delayed_turn_end() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        complete_at(
            &state,
            &token(&blocked),
            &completed_repo(&scratch.cwd, "answer"),
            NOW + 1,
        )
        .unwrap();
        let blocked_before_turn_end =
            call(&state, &scratch.cwd, "read", broad_read(), NOW + 2).unwrap();
        assert!(matches!(blocked_before_turn_end, Decision::Block(_)));
        let outstanding = token(&blocked_before_turn_end);
        assert_eq!(
            handle_at(
                &state,
                &invocation("turn_end", &scratch.cwd, None),
                b"{}",
                NOW + 3,
                Path::new("/managed/azdaja"),
            )
            .unwrap(),
            Decision::Allow
        );
        assert!(matches!(
            call(&state, &scratch.cwd, "read", broad_read(), NOW + 4).unwrap(),
            Decision::Block(_)
        ));
        let error = complete_at(
            &state,
            &outstanding,
            &completed_repo(&scratch.cwd, "late answer"),
            NOW + 5,
        )
        .unwrap_err();
        assert!(error.to_string().contains("unknown or already completed"));
    }

    #[test]
    fn session_end_revokes_outstanding_challenge_and_session_state() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let challenge = token(&blocked);
        handle_at(
            &state,
            &invocation("session_end", &scratch.cwd, None),
            b"{}",
            NOW + 1,
            Path::new("/managed/azdaja"),
        )
        .unwrap();
        let error = complete_at(
            &state,
            &challenge,
            &completed_repo(&scratch.cwd, "late answer"),
            NOW + 2,
        )
        .unwrap_err();
        assert!(error.to_string().contains("unknown or already completed"));
        assert!(matches!(
            call(&state, &scratch.cwd, "read", broad_read(), NOW + 3).unwrap(),
            Decision::Block(_)
        ));
    }

    #[test]
    fn wrong_challenge_is_rejected_without_activation() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let _blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let error = complete_at(
            &state,
            "00000000000000000000000000000000",
            &completed_repo(&scratch.cwd, "answer"),
            NOW + 1,
        )
        .unwrap_err();
        assert!(error.to_string().contains("unknown"));
        assert!(matches!(
            call(&state, &scratch.cwd, "read", broad_read(), NOW + 2).unwrap(),
            Decision::Block(_)
        ));
    }

    #[test]
    fn tiny_file_scoped_work_cannot_unlock_repository_inspection() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "agentgrep", json!({}), NOW).unwrap();
        let file = scratch.cwd.join("one.txt");
        fs::write(&file, "tiny").unwrap();
        let files = [file];
        let work = SuccessfulAzdajaWork {
            final_output: "answer",
            scope: CompletionScope::Files { paths: &files },
        };
        let error = complete_at(&state, &token(&blocked), &work, NOW + 1).unwrap_err();
        assert!(error.to_string().contains("file-scoped"));
        assert!(matches!(
            call(&state, &scratch.cwd, "agentgrep", json!({}), NOW + 2).unwrap(),
            Decision::Block(_)
        ));
    }

    #[test]
    fn repeated_narrow_reads_exhaust_the_per_session_budget() {
        let scratch = Scratch::new();
        let state = scratch.state();
        for _ in 0..2 {
            assert_eq!(
                call(
                    &state,
                    &scratch.cwd,
                    "read",
                    json!({"file_path":"src/lib.rs","start_line":1,"limit":256}),
                    NOW,
                )
                .unwrap(),
                Decision::Allow
            );
        }
        assert!(matches!(
            call(
                &state,
                &scratch.cwd,
                "read",
                json!({"file_path":"src/lib.rs","start_line":1,"limit":1}),
                NOW,
            )
            .unwrap(),
            Decision::Block(_)
        ));
    }

    #[test]
    fn empty_work_is_not_completion_and_state_names_do_not_leak_bindings() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let challenge = token(&blocked);
        assert!(
            complete_at(
                &state,
                &challenge,
                &completed_repo(&scratch.cwd, "  "),
                NOW + 1
            )
            .is_err()
        );
        for entry in fs::read_dir(state.join(GATE_DIRECTORY)).unwrap() {
            let name = entry.unwrap().file_name().to_string_lossy().into_owned();
            assert!(!name.contains("session/raw id"));
            assert!(!name.contains("repo"));
        }
        #[cfg(unix)]
        {
            let metadata = fs::metadata(state.join(GATE_DIRECTORY)).unwrap();
            assert_eq!(metadata.permissions().mode() & 0o077, 0);
        }
    }

    #[test]
    fn empty_repository_evidence_cannot_unlock_broad_work() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let work = SuccessfulAzdajaWork {
            final_output: "answer",
            scope: CompletionScope::RepositoryBundle {
                root: &scratch.cwd,
                included_files: 0,
                raw_source_bytes: 0,
            },
        };
        let error = complete_at(&state, &token(&blocked), &work, NOW + 1).unwrap_err();
        assert!(error.to_string().contains("empty repository evidence"));
        assert!(matches!(
            call(&state, &scratch.cwd, "read", broad_read(), NOW + 2).unwrap(),
            Decision::Block(_)
        ));
    }

    #[test]
    fn sha256_binding_matches_standard_vector() {
        assert_eq!(
            sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
    }
}
