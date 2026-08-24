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
use std::io::{self, BufRead, BufReader, Read, Write};
use std::path::{Path, PathBuf};
use std::sync::mpsc::{self, Receiver, RecvTimeoutError, Sender};
use std::thread::{self, JoinHandle};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

#[cfg(unix)]
use std::os::unix::fs::{DirBuilderExt, FileTypeExt, MetadataExt, OpenOptionsExt, PermissionsExt};

/// Environment variable passed to a successful Azdaja `solo` process.
pub const CHALLENGE_ENV: &str = "AZDAJA_JCODE_CHALLENGE";
/// A challenge may be completed for ten minutes after it is issued.
pub const CHALLENGE_TTL_SECONDS: u64 = 10 * 60;
/// Aggregate allowance for bounded reads in one Jcode session.
pub const NARROW_SESSION_BUDGET: u64 = 512;
/// Interval between persisted claim heartbeat updates.
#[cfg(not(test))]
pub const CLAIM_HEARTBEAT_INTERVAL: Duration = Duration::from_secs(5);
/// Short heartbeat interval used by the in-module lease tests.
#[cfg(test)]
pub const CLAIM_HEARTBEAT_INTERVAL: Duration = Duration::from_millis(50);
/// A claim without a heartbeat newer than this threshold is recoverable.
#[cfg(not(test))]
pub const CLAIM_STALE_THRESHOLD: Duration = Duration::from_secs(30);
/// Short stale threshold used by the in-module lease tests.
#[cfg(test)]
pub const CLAIM_STALE_THRESHOLD: Duration = Duration::from_millis(300);

const GATE_DIRECTORY: &str = "jcode-gate";
const CHALLENGE_DIRECTORY: &str = "challenges";
const LOCK_FILE: &str = "gate.lock";
const MAX_STATE_BYTES: u64 = 64 * 1024;
const MAX_NARROW_READ_LINES: u64 = 256;
const MAX_NARROW_READ_BYTES: u64 = 64 * 1024;
const MAX_NARROW_READ_SCAN_BYTES: u64 = 4 * 1024 * 1024;
const MAX_BLOCK_MESSAGE_BYTES: usize = 1_900;
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
    #[serde(default)]
    claim_hash: Option<String>,
    #[serde(default)]
    heartbeat_at_ms: Option<u64>,
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

/// Input scope presented before challenged work begins.
pub enum ChallengeInputScope<'a> {
    /// A repository pass rooted at this path.
    Repository(&'a Path),
    /// Any file-scoped `solo -f` work, which cannot satisfy a repository challenge.
    Files,
}

/// An atomically claimed challenge. Dropping an incomplete lease releases the claim so a failed
/// provider run can be retried while the issuance window remains open.
#[derive(Debug)]
pub struct ChallengeLease {
    state_root: PathBuf,
    challenge_hash: String,
    claim_hash: String,
    completed: bool,
    heartbeat: Option<ClaimHeartbeat>,
}

impl Drop for ChallengeLease {
    fn drop(&mut self) {
        self.stop_heartbeat();
        if !self.completed {
            let _ = release_claim(&self.state_root, &self.challenge_hash, &self.claim_hash);
        }
    }
}

#[derive(Debug)]
struct ClaimHeartbeat {
    stop: Sender<()>,
    join: Option<JoinHandle<()>>,
}

impl ClaimHeartbeat {
    fn shutdown(&mut self) {
        let _ = self.stop.send(());
        if let Some(join) = self.join.take() {
            let _ = join.join();
        }
    }
}

impl Drop for ClaimHeartbeat {
    fn drop(&mut self) {
        self.shutdown();
    }
}

impl ChallengeLease {
    fn stop_heartbeat(&mut self) {
        if let Some(mut heartbeat) = self.heartbeat.take() {
            heartbeat.shutdown();
        }
    }

    #[cfg(test)]
    fn abandon_without_releasing_for_test(&mut self) {
        self.stop_heartbeat();
        self.completed = true;
    }
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

    fn try_open(state_root: &Path) -> GateResult<Option<Self>> {
        ensure_private_directory(state_root)?;
        let root = state_root.join(GATE_DIRECTORY);
        ensure_private_directory(&root)?;
        let challenges = root.join(CHALLENGE_DIRECTORY);
        ensure_private_directory(&challenges)?;
        let lock = open_private_lock(&root.join(LOCK_FILE))?;
        match FileExt::try_lock_exclusive(&lock) {
            Ok(()) => Ok(Some(Self {
                root,
                challenges,
                _lock: lock,
            })),
            Err(error) if error.kind() == io::ErrorKind::WouldBlock => Ok(None),
            Err(error) => Err(error.into()),
        }
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
        validate_challenge_record(challenge_hash, &record)?;
        Ok(Some(record))
    }

    fn save_challenge(&self, challenge_hash: &str, record: &ChallengeRecord) -> GateResult<()> {
        validate_challenge_record(challenge_hash, record)?;
        atomic_private_write(
            &self.challenge_path(challenge_hash),
            &serde_json::to_vec(record)?,
        )
    }

    fn remove_challenge(&self, challenge_hash: &str) -> GateResult<()> {
        remove_private_file_if_present(&self.challenge_path(challenge_hash))
    }
}

fn validate_challenge_record(challenge_hash: &str, record: &ChallengeRecord) -> GateResult<()> {
    let claim_is_valid = record
        .claim_hash
        .as_deref()
        .is_none_or(|claim_hash| is_lower_hex(claim_hash, 64));
    if !is_lower_hex(challenge_hash, 64)
        || !is_lower_hex(&record.token, 32)
        || sha256_hex(record.token.as_bytes()) != challenge_hash
        || !is_lower_hex(&record.session_hash, 64)
        || !is_lower_hex(&record.workspace_hash, 64)
        || !claim_is_valid
        || (record.claim_hash.is_none() && record.heartbeat_at_ms.is_some())
    {
        return Err(contract("private challenge state binding is invalid"));
    }
    Ok(())
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

/// Atomically claim the challenge named by [`CHALLENGE_ENV`] before repository loading or provider
/// work begins. Dropping an incomplete lease releases the claim so a failed run may be retried
/// while the original issuance window remains open.
pub fn claim_challenge(
    state_root: &Path,
    scope: ChallengeInputScope<'_>,
) -> GateResult<Option<ChallengeLease>> {
    let Some(token) = env::var(CHALLENGE_ENV)
        .ok()
        .filter(|value| !value.is_empty())
    else {
        return Ok(None);
    };
    claim_at(state_root, &token, scope, unix_time_seconds()?).map(Some)
}

/// Claim a challenge using the crate state root.
pub fn claim_challenge_in_crate_state(
    scope: ChallengeInputScope<'_>,
) -> GateResult<Option<ChallengeLease>> {
    claim_challenge(&crate_state_root()?, scope)
}

/// Complete work under a previously claimed lease. Expiry is checked when the lease is claimed,
/// not after a potentially long provider run.
pub fn complete_claimed_challenge(
    lease: &mut ChallengeLease,
    work: SuccessfulAzdajaWork<'_>,
) -> GateResult<()> {
    complete_claimed_at(lease, &work, unix_time_seconds()?)?;
    lease.completed = true;
    lease.stop_heartbeat();
    Ok(())
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
        "turn_end" | "session_start" | "session_end" | "post_tool" => Ok(Decision::Allow),
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
    let requirement = classify_tool(tool_name, &input, 0, &context.canonical_cwd);
    let storage = Storage::open(state_root)?;
    let heartbeat_now_ms = unix_time_millis()?;
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
        let claimed = storage
            .load_challenge(&active.challenge_hash)?
            .is_some_and(|record| {
                record.session_hash == context.session_hash
                    && record.workspace_hash == context.workspace_hash
                    && record.expires_at == active.expires_at
                    && claim_is_live(&record, heartbeat_now_ms)
            });
        if !claimed {
            let hash = active.challenge_hash.clone();
            state.active_challenge = None;
            storage.remove_challenge(&hash)?;
            storage.save_session(&state)?;
        }
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
                block_with_challenge(
                    &storage,
                    &mut state,
                    &context,
                    now,
                    heartbeat_now_ms,
                    binary,
                )
            }
        }
        Requirement::Memory => block_with_challenge(
            &storage,
            &mut state,
            &context,
            now,
            heartbeat_now_ms,
            binary,
        ),
    }
}

fn block_with_challenge(
    storage: &Storage,
    state: &mut SessionState,
    context: &BoundContext,
    now: u64,
    heartbeat_now_ms: u64,
    binary: &Path,
) -> GateResult<Decision> {
    let token = match state.active_challenge.as_ref() {
        Some(active) => match storage
            .load_challenge(&active.challenge_hash)?
            .filter(|record| {
                record.session_hash == context.session_hash
                    && record.workspace_hash == context.workspace_hash
                    && record.expires_at == active.expires_at
            }) {
            Some(mut record) => {
                if record.claim_hash.is_some() {
                    if claim_is_live(&record, heartbeat_now_ms) {
                        return Ok(Decision::Block(
                            "Azdaja is already carrying the challenged repository pass. Wait for its answer and do not retry the broad read."
                                .into(),
                        ));
                    }
                    record.claim_hash = None;
                    record.heartbeat_at_ms = None;
                    storage.save_challenge(&active.challenge_hash, &record)?;
                }
                (active.expires_at > now).then_some(record.token)
            }
            None => None,
        },
        None => None,
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
                    claim_hash: None,
                    heartbeat_at_ms: None,
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

    let message = format!(
        "Azdaja should carry this broad read.\nRun one challenged repository pass now. Replace <user task> with the current user request; keep the challenge and binary unchanged:\n  {CHALLENGE_ENV}={token} {} solo \"<user task>\" --repo .\nContinue from its answer. Do not retry the blocked broad read. Narrow reads, Git control, builds, and tests remain available.",
        shell_quote(binary)
    );
    if message.len() > MAX_BLOCK_MESSAGE_BYTES {
        return Err(contract("Jcode memory-handoff block message is too long"));
    }
    Ok(Decision::Block(message))
}

fn claim_at(
    state_root: &Path,
    token: &str,
    scope: ChallengeInputScope<'_>,
    now: u64,
) -> GateResult<ChallengeLease> {
    if !is_lower_hex(token, 32) {
        return Err(contract(
            "AZDAJA_JCODE_CHALLENGE is not a 128-bit challenge",
        ));
    }
    let challenge_hash = sha256_hex(token.as_bytes());
    let storage = Storage::open(state_root)?;
    let mut record = storage
        .load_challenge(&challenge_hash)?
        .ok_or_else(|| contract("unknown or already completed AZDAJA_JCODE_CHALLENGE"))?;
    if record.token != token {
        return Err(contract(
            "AZDAJA_JCODE_CHALLENGE does not match private state",
        ));
    }
    let heartbeat_now_ms = unix_time_millis()?;
    if record.claim_hash.is_some() {
        if claim_is_live(&record, heartbeat_now_ms) {
            return Err(contract(
                "AZDAJA_JCODE_CHALLENGE is already claimed by another Azdaja run",
            ));
        }
        record.claim_hash = None;
        record.heartbeat_at_ms = None;
        storage.save_challenge(&challenge_hash, &record)?;
    }
    if now >= record.expires_at {
        expire_challenge(&storage, &record, &challenge_hash)?;
        return Err(contract("AZDAJA_JCODE_CHALLENGE has expired"));
    }
    let supplied_workspace_hash = match (&record.required_scope, scope) {
        (RequiredScope::RepositoryBundle, ChallengeInputScope::Repository(root)) => {
            let canonical_root = fs::canonicalize(root)?;
            sha256_hex(path_bytes(&canonical_root).as_ref())
        }
        (RequiredScope::RepositoryBundle, ChallengeInputScope::Files) => {
            return Err(contract(
                "file-scoped Azdaja work cannot claim a repository challenge",
            ));
        }
    };
    if record.workspace_hash != supplied_workspace_hash {
        return Err(contract(
            "AZDAJA_JCODE_CHALLENGE repository does not match --repo",
        ));
    }
    validate_active_challenge(&storage, &record, &challenge_hash)?;

    let claim_hash = sha256_hex(&os_random_128()?);
    record.claim_hash = Some(claim_hash.clone());
    record.heartbeat_at_ms = Some(heartbeat_now_ms);
    storage.save_challenge(&challenge_hash, &record)?;
    let heartbeat = match start_claim_heartbeat(state_root, &challenge_hash, &claim_hash) {
        Ok(heartbeat) => heartbeat,
        Err(error) => {
            record.claim_hash = None;
            record.heartbeat_at_ms = None;
            storage.save_challenge(&challenge_hash, &record)?;
            return Err(error);
        }
    };
    Ok(ChallengeLease {
        state_root: state_root.to_path_buf(),
        challenge_hash,
        claim_hash,
        completed: false,
        heartbeat: Some(heartbeat),
    })
}

fn claim_is_live(record: &ChallengeRecord, now_ms: u64) -> bool {
    if record.claim_hash.is_none() {
        return false;
    }
    let Some(heartbeat_at_ms) = record.heartbeat_at_ms else {
        return false;
    };
    let stale_after_ms = u64::try_from(CLAIM_STALE_THRESHOLD.as_millis()).unwrap_or(u64::MAX);
    now_ms.saturating_sub(heartbeat_at_ms) <= stale_after_ms
}

fn start_claim_heartbeat(
    state_root: &Path,
    challenge_hash: &str,
    claim_hash: &str,
) -> GateResult<ClaimHeartbeat> {
    let (stop, receiver) = mpsc::channel();
    let state_root = state_root.to_path_buf();
    let challenge_hash = challenge_hash.to_owned();
    let claim_hash = claim_hash.to_owned();
    let join = thread::Builder::new()
        .name("azdaja-jcode-claim-heartbeat".into())
        .spawn(move || claim_heartbeat_loop(&state_root, &challenge_hash, &claim_hash, receiver))?;
    Ok(ClaimHeartbeat {
        stop,
        join: Some(join),
    })
}

fn claim_heartbeat_loop(
    state_root: &Path,
    challenge_hash: &str,
    claim_hash: &str,
    stop: Receiver<()>,
) {
    loop {
        match stop.recv_timeout(CLAIM_HEARTBEAT_INTERVAL) {
            Ok(()) | Err(RecvTimeoutError::Disconnected) => break,
            Err(RecvTimeoutError::Timeout) => {}
        }
        match refresh_claim_heartbeat(state_root, challenge_hash, claim_hash) {
            Ok(true) => {}
            Ok(false) | Err(_) => break,
        }
    }
}

fn refresh_claim_heartbeat(
    state_root: &Path,
    challenge_hash: &str,
    claim_hash: &str,
) -> GateResult<bool> {
    let Some(storage) = Storage::try_open(state_root)? else {
        return Ok(true);
    };
    let Some(mut record) = storage.load_challenge(challenge_hash)? else {
        return Ok(false);
    };
    if record.claim_hash.as_deref() != Some(claim_hash) {
        return Ok(false);
    }
    record.heartbeat_at_ms = Some(unix_time_millis()?);
    storage.save_challenge(challenge_hash, &record)?;
    Ok(true)
}

fn complete_claimed_at(
    lease: &ChallengeLease,
    work: &SuccessfulAzdajaWork<'_>,
    _now: u64,
) -> GateResult<()> {
    if work.final_output.trim().is_empty() {
        return Err(contract(
            "empty Azdaja work cannot complete a Jcode challenge",
        ));
    }
    let storage = Storage::open(&lease.state_root)?;
    let record = storage
        .load_challenge(&lease.challenge_hash)?
        .ok_or_else(|| contract("unknown or already completed AZDAJA_JCODE_CHALLENGE"))?;
    if record.claim_hash.as_deref() != Some(lease.claim_hash.as_str()) {
        return Err(contract("AZDAJA_JCODE_CHALLENGE claim is no longer active"));
    }
    let supplied_workspace_hash = completion_workspace_hash(&record, work)?;
    if record.workspace_hash != supplied_workspace_hash {
        return Err(contract(
            "AZDAJA_JCODE_CHALLENGE repository bundle does not match --repo",
        ));
    }
    consume_challenge(&storage, &record, &lease.challenge_hash)
}

fn release_claim(state_root: &Path, challenge_hash: &str, claim_hash: &str) -> GateResult<()> {
    if !state_root.join(GATE_DIRECTORY).is_dir() {
        return Ok(());
    }
    let storage = Storage::open(state_root)?;
    let Some(mut record) = storage.load_challenge(challenge_hash)? else {
        return Ok(());
    };
    if record.claim_hash.as_deref() == Some(claim_hash) {
        record.claim_hash = None;
        record.heartbeat_at_ms = None;
        storage.save_challenge(challenge_hash, &record)?;
    }
    Ok(())
}

#[cfg(test)]
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
    if record.claim_hash.is_some() {
        return Err(contract(
            "AZDAJA_JCODE_CHALLENGE is claimed by another Azdaja run",
        ));
    }
    if now >= record.expires_at {
        expire_challenge(&storage, &record, &challenge_hash)?;
        return Err(contract("AZDAJA_JCODE_CHALLENGE has expired"));
    }
    let supplied_workspace_hash = completion_workspace_hash(&record, work)?;
    if record.workspace_hash != supplied_workspace_hash {
        return Err(contract(
            "AZDAJA_JCODE_CHALLENGE repository bundle does not match --repo",
        ));
    }
    consume_challenge(&storage, &record, &challenge_hash)
}

fn completion_workspace_hash(
    record: &ChallengeRecord,
    work: &SuccessfulAzdajaWork<'_>,
) -> GateResult<String> {
    match (&record.required_scope, &work.scope) {
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
            Ok(sha256_hex(path_bytes(&canonical_root).as_ref()))
        }
        (RequiredScope::RepositoryBundle, CompletionScope::Files { .. }) => Err(contract(
            "file-scoped Azdaja work cannot complete a repository challenge",
        )),
        (RequiredScope::RepositoryBundle, CompletionScope::IngestionOnly) => Err(contract(
            "Azdaja ingestion without completed repository work cannot complete a challenge",
        )),
    }
}

fn validate_active_challenge(
    storage: &Storage,
    record: &ChallengeRecord,
    challenge_hash: &str,
) -> GateResult<SessionState> {
    let state = storage
        .load_session(&record.session_hash)?
        .ok_or_else(|| contract("AZDAJA_JCODE_CHALLENGE session is no longer active"))?;
    if state.workspace_hash != record.workspace_hash
        || !state.active_challenge.as_ref().is_some_and(|active| {
            active.challenge_hash == challenge_hash && active.expires_at == record.expires_at
        })
    {
        return Err(contract("AZDAJA_JCODE_CHALLENGE is revoked or not active"));
    }
    Ok(state)
}

fn consume_challenge(
    storage: &Storage,
    record: &ChallengeRecord,
    challenge_hash: &str,
) -> GateResult<()> {
    let mut state = validate_active_challenge(storage, record, challenge_hash)?;
    state.active_challenge = None;
    storage.save_session(&state)?;
    storage.remove_challenge(challenge_hash)?;
    Ok(())
}

fn expire_challenge(
    storage: &Storage,
    record: &ChallengeRecord,
    challenge_hash: &str,
) -> GateResult<()> {
    storage.remove_challenge(challenge_hash)?;
    if let Some(mut state) = storage.load_session(&record.session_hash)?
        && state
            .active_challenge
            .as_ref()
            .is_some_and(|active| active.challenge_hash == challenge_hash)
    {
        state.active_challenge = None;
        storage.save_session(&state)?;
    }
    Ok(())
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

fn classify_tool(tool_name: &str, input: &Value, depth: usize, cwd: &Path) -> Requirement {
    if depth > 16 {
        return Requirement::Memory;
    }
    match normalized_tool_name(tool_name) {
        "read" => classify_read(input, cwd),
        "agentgrep" => classify_agentgrep(input),
        "bash" => classify_bash(input),
        "batch" => classify_batch(input, depth + 1, cwd),
        _ => Requirement::Free,
    }
}

fn normalized_tool_name(name: &str) -> &str {
    name.rsplit(['.', ':', '/']).next().unwrap_or(name)
}

fn classify_read(input: &Value, cwd: &Path) -> Requirement {
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
    let start_line = match object.get("start_line") {
        Some(value) => match value.as_u64() {
            Some(line) if line > 0 => line,
            _ => return Requirement::Memory,
        },
        None => 1,
    };
    if !narrow_read_is_byte_bounded(cwd, path, start_line, limit) {
        return Requirement::Memory;
    }
    Requirement::Narrow(limit.max(1))
}

fn narrow_read_is_byte_bounded(cwd: &Path, path: &str, start_line: u64, limit: u64) -> bool {
    let requested = Path::new(path);
    let joined = if requested.is_absolute() {
        requested.to_path_buf()
    } else {
        cwd.join(requested)
    };
    let Ok(named) = fs::symlink_metadata(&joined) else {
        return false;
    };
    if named.file_type().is_symlink() || !named.file_type().is_file() {
        return false;
    }
    let Ok(canonical) = fs::canonicalize(&joined) else {
        return false;
    };
    if !canonical.starts_with(cwd) {
        return false;
    }
    if named.len() <= MAX_NARROW_READ_BYTES {
        return true;
    }
    let Ok(file) = File::open(&canonical) else {
        return false;
    };
    let mut reader = BufReader::new(file);
    let end_line = start_line.saturating_add(limit.saturating_sub(1));
    let mut current_line = 1u64;
    let mut scanned = 0u64;
    let mut selected = 0u64;
    loop {
        let Ok(buffer) = reader.fill_buf() else {
            return false;
        };
        if buffer.is_empty() {
            return true;
        }
        let mut consumed = 0usize;
        for byte in buffer {
            consumed += 1;
            scanned = scanned.saturating_add(1);
            if scanned > MAX_NARROW_READ_SCAN_BYTES {
                return false;
            }
            if (start_line..=end_line).contains(&current_line) {
                selected = selected.saturating_add(1);
                if selected > MAX_NARROW_READ_BYTES {
                    return false;
                }
            }
            if *byte == b'\n' {
                current_line = current_line.saturating_add(1);
                if current_line > end_line {
                    return true;
                }
            }
        }
        reader.consume(consumed);
    }
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

fn classify_batch(input: &Value, depth: usize, cwd: &Path) -> Requirement {
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
        match classify_tool(tool, nested_input, depth, cwd) {
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
    if git_workflow_requires_memory(command) {
        return Requirement::Memory;
    }
    if is_git_build_test_lint_or_format(command) {
        return Requirement::Free;
    }
    Requirement::Memory
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
            let Some(parsed) = shlex::split(segment) else {
                return false;
            };
            let words = parsed.iter().map(String::as_str).collect::<Vec<_>>();
            let Some((program, arguments)) = command_words(&words) else {
                continue;
            };
            saw_command = true;
            let program = program.rsplit('/').next().unwrap_or(program);
            let first = arguments.first().copied().unwrap_or("");
            let allowed = match program {
                "git" => git_command_is_safe(arguments),
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

fn git_workflow_requires_memory(command: &str) -> bool {
    let has_shell_expansion = command.contains("$(") || command.contains('`');
    for segment in command.split(['\n', ';']).flat_map(|part| part.split("&&")) {
        for alternative in segment.split("||") {
            let segment = alternative.trim();
            if segment.is_empty() {
                continue;
            }
            let Some(parsed) = shlex::split(segment) else {
                return true;
            };
            let words = parsed.iter().map(String::as_str).collect::<Vec<_>>();
            for (index, program) in words.iter().enumerate() {
                let program = *program;
                if program.rsplit('/').next().unwrap_or(program) != "git" {
                    continue;
                }
                if has_shell_expansion
                    || segment.contains('|')
                    || segment.contains('>')
                    || segment.contains('<')
                    || !git_command_is_safe(&words[index + 1..])
                {
                    return true;
                }
            }
        }
    }
    false
}

fn git_command_is_safe(arguments: &[&str]) -> bool {
    let Some((subcommand, arguments)) = git_subcommand(arguments) else {
        return arguments.is_empty();
    };
    match subcommand {
        "--help" | "--version" | "help" | "version" => true,
        "status" => !arguments.iter().any(|argument| git_verbose_flag(argument)),
        "add" | "checkout" | "switch" | "restore" | "reset" => !arguments.iter().any(|argument| {
            matches!(*argument, "-p" | "--patch" | "-i" | "--interactive")
                || argument.starts_with("--patch=")
        }),
        "commit" => !arguments.iter().any(|argument| git_verbose_flag(argument)),
        "rebase" => !arguments.iter().any(|argument| {
            matches!(*argument, "-x" | "--exec" | "--show-current-patch")
                || argument.starts_with("-x")
                || argument.starts_with("--exec=")
        }),
        "diff" => git_diff_is_metadata_only(arguments),
        "log" => git_log_is_bounded_or_metadata_only(arguments),
        "branch" | "rev-parse" | "fetch" | "pull" | "push" | "merge" | "worktree" | "tag"
        | "clean" | "init" | "clone" | "remote" | "rm" | "mv" | "cherry-pick" | "revert"
        | "describe" | "ls-files" | "ls-tree" | "show-ref" | "for-each-ref" | "symbolic-ref"
        | "update-ref" | "gc" | "maintenance" => true,
        _ => false,
    }
}

fn git_verbose_flag(argument: &str) -> bool {
    argument == "--verbose"
        || argument.starts_with("--verbose=")
        || (argument.starts_with('-') && !argument.starts_with("--") && argument[1..].contains('v'))
}

fn git_subcommand<'a>(arguments: &'a [&'a str]) -> Option<(&'a str, &'a [&'a str])> {
    let mut index = 0;
    while let Some(argument) = arguments.get(index).copied() {
        match argument {
            "-C" | "--git-dir" | "--work-tree" => {
                index += 2;
                if index > arguments.len() {
                    return None;
                }
            }
            "--no-pager"
            | "--paginate"
            | "--literal-pathspecs"
            | "--glob-pathspecs"
            | "--noglob-pathspecs"
            | "--icase-pathspecs" => index += 1,
            "--help" | "--version" => return Some((argument, &arguments[index + 1..])),
            _ if argument.starts_with("--git-dir=") || argument.starts_with("--work-tree=") => {
                index += 1;
            }
            _ if argument.starts_with('-') => return None,
            _ => return Some((argument, &arguments[index + 1..])),
        }
    }
    None
}

fn git_diff_is_metadata_only(arguments: &[&str]) -> bool {
    let mut metadata_output = false;
    let mut paths_only = false;
    for argument in arguments {
        if paths_only || *argument == "--" {
            paths_only = true;
            continue;
        }
        if !argument.starts_with('-') {
            continue;
        }
        if matches!(
            *argument,
            "--stat"
                | "--shortstat"
                | "--numstat"
                | "--dirstat"
                | "--dirstat-by-file"
                | "--summary"
                | "--name-only"
                | "--name-status"
                | "--raw"
                | "--quiet"
                | "--exit-code"
                | "--no-patch"
                | "-s"
        ) || argument.starts_with("--stat=")
            || argument.starts_with("--dirstat=")
            || argument.starts_with("--dirstat-by-file=")
        {
            metadata_output = true;
            continue;
        }
        if matches!(
            *argument,
            "--cached"
                | "--staged"
                | "--merge-base"
                | "--no-index"
                | "--relative"
                | "--no-renames"
                | "--find-renames"
                | "--ignore-space-at-eol"
                | "--ignore-space-change"
                | "--ignore-all-space"
                | "--ignore-blank-lines"
                | "--ignore-submodules"
                | "-z"
        ) || argument.starts_with("--relative=")
            || argument.starts_with("--find-renames=")
            || argument.starts_with("--diff-filter=")
            || argument.starts_with("--ignore-submodules=")
            || argument.starts_with("--color=")
        {
            continue;
        }
        return false;
    }
    metadata_output
}

fn git_log_is_bounded_or_metadata_only(arguments: &[&str]) -> bool {
    let mut bounded_or_metadata = false;
    let mut expect_count = false;
    for argument in arguments {
        if expect_count {
            if argument.parse::<u64>().is_err() {
                return false;
            }
            bounded_or_metadata = true;
            expect_count = false;
            continue;
        }
        if matches!(*argument, "-n" | "--max-count") {
            expect_count = true;
            continue;
        }
        if argument
            .strip_prefix("--max-count=")
            .is_some_and(|count| count.parse::<u64>().is_ok())
            || (argument.starts_with("-n")
                && argument.len() > 2
                && argument[2..].parse::<u64>().is_ok())
            || (argument.starts_with('-')
                && argument.len() > 1
                && argument[1..].bytes().all(|byte| byte.is_ascii_digit()))
        {
            bounded_or_metadata = true;
            continue;
        }
        if matches!(
            *argument,
            "--stat"
                | "--shortstat"
                | "--numstat"
                | "--summary"
                | "--name-only"
                | "--name-status"
                | "--raw"
        ) {
            bounded_or_metadata = true;
            continue;
        }
        if matches!(
            *argument,
            "-p" | "-u"
                | "--patch"
                | "--full-diff"
                | "--binary"
                | "--patch-with-stat"
                | "--patch-with-raw"
                | "--cc"
                | "-c"
                | "--remerge-diff"
                | "-L"
        ) || argument.starts_with("--unified")
            || argument.starts_with("--word-diff")
            || argument.starts_with("--color-words")
            || argument.starts_with("-L")
        {
            return false;
        }
    }
    !expect_count && bounded_or_metadata
}

fn command_words<'a>(words: &'a [&'a str]) -> Option<(&'a str, &'a [&'a str])> {
    let mut index = 0;
    loop {
        while words
            .get(index)
            .is_some_and(|word| is_environment_assignment(word))
        {
            index += 1;
        }
        let program = words.get(index).copied()?;
        match program.rsplit('/').next().unwrap_or(program) {
            "env" => {
                index += 1;
                loop {
                    match words.get(index).copied() {
                        Some("-i" | "--ignore-environment") => index += 1,
                        Some("-u" | "--unset" | "-C" | "--chdir") => {
                            index += 2;
                            if index > words.len() {
                                return None;
                            }
                        }
                        Some("--") => {
                            index += 1;
                            break;
                        }
                        Some(argument)
                            if argument.starts_with("--unset=")
                                || argument.starts_with("--chdir=") =>
                        {
                            index += 1;
                        }
                        Some(argument) if argument.starts_with('-') => return None,
                        _ => break,
                    }
                }
            }
            "command" | "exec" => {
                index += 1;
                if words.get(index).copied() == Some("--") {
                    index += 1;
                }
            }
            _ => return Some((program, &words[index + 1..])),
        }
    }
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

fn managed_binary_path() -> GateResult<PathBuf> {
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

fn unix_time_millis() -> GateResult<u64> {
    let millis = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|_| contract("system clock is before the Unix epoch"))?
        .as_millis();
    u64::try_from(millis).map_err(|_| contract("system clock exceeds supported range"))
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
            fs::create_dir(cwd.join("src")).unwrap();
            fs::write(cwd.join("src/lib.rs"), "bounded line\n".repeat(600)).unwrap();
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
            "Azdaja should carry this broad read.\nRun one challenged repository pass now. Replace <user task> with the current user request; keep the challenge and binary unchanged:\n  {CHALLENGE_ENV}={challenge} /managed/azdaja solo \"<user task>\" --repo .\nContinue from its answer. Do not retry the blocked broad read. Narrow reads, Git control, builds, and tests remain available."
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
    fn one_requested_minified_line_cannot_bypass_the_byte_bound() {
        let scratch = Scratch::new();
        let state = scratch.state();
        fs::write(scratch.cwd.join("minified.js"), vec![b'x'; 1024 * 1024]).unwrap();
        assert!(matches!(
            call(
                &state,
                &scratch.cwd,
                "read",
                json!({"file_path":"minified.js","start_line":1,"limit":1}),
                NOW,
            )
            .unwrap(),
            Decision::Block(_)
        ));
    }

    #[test]
    fn narrow_read_fails_closed_when_reaching_the_range_requires_a_large_scan() {
        let scratch = Scratch::new();
        let state = scratch.state();
        fs::write(
            scratch.cwd.join("deep.txt"),
            format!(
                "{}tail\n",
                "x\n".repeat((MAX_NARROW_READ_SCAN_BYTES / 2) as usize)
            ),
        )
        .unwrap();
        assert!(matches!(
            call(
                &state,
                &scratch.cwd,
                "read",
                json!({
                    "file_path":"deep.txt",
                    "start_line":MAX_NARROW_READ_SCAN_BYTES,
                    "limit":1
                }),
                NOW,
            )
            .unwrap(),
            Decision::Block(_)
        ));
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
    fn ordinary_git_build_test_lint_and_format_commands_are_allowed() {
        let scratch = Scratch::new();
        let state = scratch.state();
        for command in [
            "git status --short",
            "env -i git status --short",
            "command git status --short",
            "/usr/bin/env -i git diff --stat",
            "git -C . status --short",
            "git branch --show-current",
            "git rev-parse --show-toplevel",
            "git add README.md",
            "git commit --dry-run",
            "git checkout main",
            "git switch main",
            "git restore README.md",
            "git fetch --dry-run",
            "git pull --ff-only",
            "git push --dry-run",
            "git merge --no-commit topic",
            "git rebase --onto main base topic",
            "git worktree list",
            "git tag --list",
            "git clean -nd",
            "git diff --stat",
            "git diff --name-only HEAD~1",
            "git log -10 --oneline",
            "git --no-pager log -1 --oneline",
            "git log --stat",
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
    fn broad_content_reading_and_git_source_extraction_are_blocked() {
        let scratch = Scratch::new();
        let state = scratch.state();
        for command in [
            "cat src/lib.rs",
            "cp src/lib.rs /dev/stdout",
            "dd if=src/lib.rs bs=4096 count=1",
            "printf '%s' \"$(<src/lib.rs)\"",
            "git show HEAD:src/lib.rs",
            "git cat-file -p HEAD:src/lib.rs",
            "git grep receipt",
            "git archive HEAD",
            "git blame src/lib.rs",
            "git diff",
            "git diff --cached",
            "git diff -p",
            "git diff --stat -p",
            "git diff --check",
            "git log",
            "git log -p -1",
            "git status -vv",
            "git status -sbv",
            "env -i git show HEAD:src/lib.rs",
            "git add -p",
            "git commit -vv --dry-run",
            "git commit -anv --dry-run",
            "git checkout -p -- src/lib.rs",
            "git restore -p src/lib.rs",
            "git rebase --show-current-patch",
            "command git show HEAD:src/lib.rs",
            "/usr/bin/env -i git show HEAD:src/lib.rs",
            "sudo git cat-file -p HEAD:src/lib.rs",
            "xargs git show HEAD:src/lib.rs",
            "command g\\it show HEAD:src/lib.rs",
            "command 'git' show HEAD:src/lib.rs",
        ] {
            assert!(
                matches!(
                    call(
                        &state,
                        &scratch.cwd,
                        "bash",
                        json!({"command":command}),
                        NOW,
                    )
                    .unwrap(),
                    Decision::Block(_)
                ),
                "{command}"
            );
        }
    }

    #[test]
    fn challenge_command_uses_the_running_executable() {
        assert_eq!(managed_binary_path().unwrap(), env::current_exe().unwrap());
    }

    #[test]
    fn overlong_managed_binary_cannot_overflow_jcode_hook_stderr() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let binary = PathBuf::from(format!("/{}", "a".repeat(MAX_BLOCK_MESSAGE_BYTES)));
        let error = handle_at(
            &state,
            &invocation("pre_tool", &scratch.cwd, Some("read")),
            &serde_json::to_vec(&broad_read()).unwrap(),
            NOW,
            &binary,
        )
        .unwrap_err();
        assert!(error.to_string().contains("block message is too long"));
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
    fn challenge_claimed_before_expiry_can_finish_after_a_long_provider_run() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let mut lease = claim_at(
            &state,
            &token(&blocked),
            ChallengeInputScope::Repository(&scratch.cwd),
            NOW + 1,
        )
        .unwrap();
        let in_flight = call(
            &state,
            &scratch.cwd,
            "read",
            broad_read(),
            NOW + CHALLENGE_TTL_SECONDS + 30,
        )
        .unwrap();
        assert!(matches!(
            in_flight,
            Decision::Block(message) if message.contains("already carrying")
        ));
        complete_claimed_at(
            &lease,
            &completed_repo(&scratch.cwd, "answer"),
            NOW + CHALLENGE_TTL_SECONDS + 60,
        )
        .unwrap();
        lease.completed = true;
        assert!(matches!(
            call(
                &state,
                &scratch.cwd,
                "read",
                broad_read(),
                NOW + CHALLENGE_TTL_SECONDS + 61
            )
            .unwrap(),
            Decision::Block(_)
        ));
    }

    #[test]
    fn live_claim_remains_exclusive_after_the_issuance_window_expires() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let challenge = token(&blocked);
        let lease = claim_at(
            &state,
            &challenge,
            ChallengeInputScope::Repository(&scratch.cwd),
            NOW + 1,
        )
        .unwrap();
        let duplicate = claim_at(
            &state,
            &challenge,
            ChallengeInputScope::Repository(&scratch.cwd),
            NOW + CHALLENGE_TTL_SECONDS + 30,
        )
        .unwrap_err();
        assert!(duplicate.to_string().contains("already claimed"));
        drop(lease);
    }

    #[test]
    fn stale_claim_is_recovered_after_the_claimant_disappears() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let challenge = token(&blocked);
        let mut abandoned = claim_at(
            &state,
            &challenge,
            ChallengeInputScope::Repository(&scratch.cwd),
            NOW + 1,
        )
        .unwrap();
        abandoned.abandon_without_releasing_for_test();
        drop(abandoned);
        thread::sleep(CLAIM_STALE_THRESHOLD + CLAIM_HEARTBEAT_INTERVAL);
        let recovered = claim_at(
            &state,
            &challenge,
            ChallengeInputScope::Repository(&scratch.cwd),
            NOW + 2,
        )
        .unwrap();
        drop(recovered);
    }

    #[test]
    fn challenge_claim_is_exclusive_and_drop_releases_it_for_retry() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let challenge = token(&blocked);
        let lease = claim_at(
            &state,
            &challenge,
            ChallengeInputScope::Repository(&scratch.cwd),
            NOW + 1,
        )
        .unwrap();
        let duplicate = claim_at(
            &state,
            &challenge,
            ChallengeInputScope::Repository(&scratch.cwd),
            NOW + 2,
        )
        .unwrap_err();
        assert!(duplicate.to_string().contains("already claimed"));
        drop(lease);
        let mut retry = claim_at(
            &state,
            &challenge,
            ChallengeInputScope::Repository(&scratch.cwd),
            NOW + 3,
        )
        .unwrap();
        complete_claimed_at(&retry, &completed_repo(&scratch.cwd, "answer"), NOW + 4).unwrap();
        retry.completed = true;
    }

    #[test]
    fn file_scoped_work_is_rejected_when_claiming_before_provider_entry() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let error = claim_at(
            &state,
            &token(&blocked),
            ChallengeInputScope::Files,
            NOW + 1,
        )
        .unwrap_err();
        assert!(error.to_string().contains("file-scoped"));
    }

    #[test]
    fn detached_observer_events_never_mutate_challenge_state() {
        let scratch = Scratch::new();
        let state = scratch.state();
        let blocked = call(&state, &scratch.cwd, "read", broad_read(), NOW).unwrap();
        let challenge = token(&blocked);
        for (offset, event) in ["turn_end", "session_start", "session_end", "post_tool"]
            .into_iter()
            .enumerate()
        {
            assert_eq!(
                handle_at(
                    &state,
                    &invocation(event, &scratch.cwd, None),
                    b"{}",
                    NOW + offset as u64 + 1,
                    Path::new("/managed/azdaja"),
                )
                .unwrap(),
                Decision::Allow
            );
            let still_blocked = call(
                &state,
                &scratch.cwd,
                "read",
                broad_read(),
                NOW + offset as u64 + 2,
            )
            .unwrap();
            assert_eq!(token(&still_blocked), challenge);
        }
        complete_at(
            &state,
            &challenge,
            &completed_repo(&scratch.cwd, "answer"),
            NOW + 10,
        )
        .unwrap();
        assert!(matches!(
            call(&state, &scratch.cwd, "read", broad_read(), NOW + 11).unwrap(),
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
