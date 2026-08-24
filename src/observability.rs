use anyhow::{Context, Result, bail};
use serde::{Deserialize, Serialize};
use std::{fs, io::Read, path::Path, time::UNIX_EPOCH};

const SCHEMA_VERSION: u32 = 1;
const RECENT_LIMIT: usize = 24;
const RECENT_DIR: &str = "observability";
const RECENT_FILE: &str = "recent.json";
const SESSION_FILE: &str = "observability.json";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum EvidenceTier {
    ExactLocal,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SourceLocalAggregate {
    pub evidence_tier: EvidenceTier,
    pub source_bytes: u64,
    pub utf8_chars: u64,
    pub physical_lines: u64,
    pub nonempty_lines: u64,
    /// Shannon byte entropy in thousandths of a bit per byte. Range: 0..=8000.
    pub byte_entropy_millibits: u16,
}

impl SourceLocalAggregate {
    pub fn from_text(text: &str) -> Self {
        let bytes = text.as_bytes();
        let mut counts = [0u64; 256];
        for byte in bytes {
            counts[usize::from(*byte)] += 1;
        }
        let entropy = if bytes.is_empty() {
            0.0
        } else {
            let len = bytes.len() as f64;
            counts
                .iter()
                .filter(|count| **count > 0)
                .map(|count| {
                    let probability = *count as f64 / len;
                    -probability * probability.log2()
                })
                .sum::<f64>()
        };
        let physical_lines = physical_line_count(text);
        let nonempty_lines = nonempty_physical_line_count(text);
        Self {
            evidence_tier: EvidenceTier::ExactLocal,
            source_bytes: bytes.len() as u64,
            utf8_chars: text.chars().count() as u64,
            physical_lines,
            nonempty_lines,
            byte_entropy_millibits: (entropy * 1000.0).round().clamp(0.0, 8000.0) as u16,
        }
    }

    pub fn byte_entropy_bits(&self) -> f64 {
        f64::from(self.byte_entropy_millibits) / 1000.0
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ObservabilityPrivacyContract {
    pub aggregate_only: bool,
    pub excludes_source_text: bool,
    pub excludes_paths: bool,
    pub excludes_hashes: bool,
    pub excludes_prompts: bool,
    pub excludes_responses: bool,
}

impl Default for ObservabilityPrivacyContract {
    fn default() -> Self {
        Self {
            aggregate_only: true,
            excludes_source_text: true,
            excludes_paths: true,
            excludes_hashes: true,
            excludes_prompts: true,
            excludes_responses: true,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum RunKind {
    SessionLoad,
    SoloLoad,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct RecentRunAggregate {
    pub kind: RunKind,
    pub observed_unix: u64,
    pub source: SourceLocalAggregate,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct RecentAggregateSummary {
    pub schema_version: u32,
    pub updated_unix: u64,
    pub max_recent_runs: usize,
    pub privacy: ObservabilityPrivacyContract,
    pub runs: Vec<RecentRunAggregate>,
}

impl RecentAggregateSummary {
    pub fn empty() -> Self {
        Self {
            schema_version: SCHEMA_VERSION,
            updated_unix: unix_now(),
            max_recent_runs: RECENT_LIMIT,
            privacy: ObservabilityPrivacyContract::default(),
            runs: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SessionAggregateSummary {
    pub schema_version: u32,
    pub updated_unix: u64,
    pub privacy: ObservabilityPrivacyContract,
    pub loaded_sources: u64,
    pub current_source: Option<SourceLocalAggregate>,
}

impl SessionAggregateSummary {
    fn empty() -> Self {
        Self {
            schema_version: SCHEMA_VERSION,
            updated_unix: unix_now(),
            privacy: ObservabilityPrivacyContract::default(),
            loaded_sources: 0,
            current_source: None,
        }
    }
}

fn unix_now() -> u64 {
    std::time::SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

fn physical_line_count(text: &str) -> u64 {
    if text.is_empty() {
        return 0;
    }
    let newline_count = text
        .as_bytes()
        .iter()
        .filter(|byte| **byte == b'\n')
        .count() as u64;
    if text.ends_with('\n') {
        newline_count
    } else {
        newline_count + 1
    }
}

fn nonempty_physical_line_count(text: &str) -> u64 {
    if text.is_empty() {
        return 0;
    }
    let mut count = 0u64;
    let mut start = 0usize;
    for (index, byte) in text.bytes().enumerate() {
        if byte == b'\n' {
            if physical_line_has_content(&text[start..index]) {
                count += 1;
            }
            start = index + 1;
        }
    }
    if start < text.len() && physical_line_has_content(&text[start..]) {
        count += 1;
    }
    count
}

fn physical_line_has_content(line: &str) -> bool {
    let line = line.strip_suffix('\r').unwrap_or(line);
    !line.trim().is_empty()
}

pub(crate) fn record_session_source_load(
    session_dir: &Path,
    source: &SourceLocalAggregate,
) -> Result<()> {
    let root = crate::state_home()?;
    let _guard = crate::global_lock()?;
    let session_summary =
        load_session_summary_at(session_dir)?.unwrap_or_else(SessionAggregateSummary::empty);
    let session_summary = SessionAggregateSummary {
        schema_version: SCHEMA_VERSION,
        updated_unix: unix_now(),
        privacy: ObservabilityPrivacyContract::default(),
        loaded_sources: session_summary.loaded_sources.saturating_add(1),
        current_source: Some(source.clone()),
    };
    write_session_summary_at(session_dir, &session_summary)?;
    append_recent_at(&root, RunKind::SessionLoad, source)
}

pub fn record_solo_source_load(source: &SourceLocalAggregate) -> Result<()> {
    let root = crate::state_home()?;
    let _guard = crate::global_lock()?;
    append_recent_at(&root, RunKind::SoloLoad, source)
}

pub fn load_recent_summary() -> Result<RecentAggregateSummary> {
    let root = crate::state_home()?;
    load_recent_summary_at(&root)
}

pub(crate) fn load_session_summary(session_dir: &Path) -> Result<Option<SessionAggregateSummary>> {
    load_session_summary_at(session_dir)
}

fn recent_path(root: &Path) -> std::path::PathBuf {
    root.join(RECENT_DIR).join(RECENT_FILE)
}

fn session_path(session_dir: &Path) -> std::path::PathBuf {
    session_dir.join(SESSION_FILE)
}

fn append_recent_at(root: &Path, kind: RunKind, source: &SourceLocalAggregate) -> Result<()> {
    let dir = root.join(RECENT_DIR);
    crate::secure_dir(&dir)?;
    let mut summary = load_recent_summary_at(root)?;
    summary.schema_version = SCHEMA_VERSION;
    summary.updated_unix = unix_now();
    summary.max_recent_runs = RECENT_LIMIT;
    summary.privacy = ObservabilityPrivacyContract::default();
    summary.runs.insert(
        0,
        RecentRunAggregate {
            kind,
            observed_unix: summary.updated_unix,
            source: source.clone(),
        },
    );
    summary.runs.truncate(RECENT_LIMIT);
    let bytes = serde_json::to_vec_pretty(&summary)?;
    crate::atomic_write(&recent_path(root), &bytes)
}

fn load_recent_summary_at(root: &Path) -> Result<RecentAggregateSummary> {
    let path = recent_path(root);
    if !summary_path_exists(&path)? {
        return Ok(RecentAggregateSummary::empty());
    }
    let bytes = read_private_summary_file(&path)
        .with_context(|| format!("read private observability summary {}", path.display()))?;
    let mut summary: RecentAggregateSummary = serde_json::from_slice(&bytes)
        .with_context(|| format!("parse aggregate observability summary {}", path.display()))?;
    normalize_recent_summary(&mut summary);
    Ok(summary)
}

fn normalize_recent_summary(summary: &mut RecentAggregateSummary) {
    summary.schema_version = SCHEMA_VERSION;
    summary.max_recent_runs = RECENT_LIMIT;
    summary.privacy = ObservabilityPrivacyContract::default();
    summary.runs.truncate(RECENT_LIMIT);
}

fn write_session_summary_at(session_dir: &Path, summary: &SessionAggregateSummary) -> Result<()> {
    let bytes = serde_json::to_vec_pretty(summary)?;
    crate::atomic_write(&session_path(session_dir), &bytes)
}

fn read_private_summary_file(path: &Path) -> Result<Vec<u8>> {
    let mut file = crate::open_private_file(path, false)?;
    crate::validate_private_file(&file, path)?;
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes)?;
    crate::validate_private_file(&file, path)?;
    Ok(bytes)
}

fn summary_path_exists(path: &Path) -> Result<bool> {
    match fs::symlink_metadata(path) {
        Ok(metadata) => {
            if !metadata.file_type().is_file() {
                bail!(
                    "observability summary is not a regular file: {}",
                    path.display()
                )
            }
            Ok(true)
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(false),
        Err(error) => Err(error.into()),
    }
}

fn load_session_summary_at(session_dir: &Path) -> Result<Option<SessionAggregateSummary>> {
    let path = session_path(session_dir);
    if !summary_path_exists(&path)? {
        return Ok(None);
    }
    let bytes = read_private_summary_file(&path).with_context(|| {
        format!(
            "read private session observability summary {}",
            path.display()
        )
    })?;
    let mut summary: SessionAggregateSummary = serde_json::from_slice(&bytes)
        .with_context(|| format!("parse session observability summary {}", path.display()))?;
    summary.schema_version = SCHEMA_VERSION;
    summary.privacy = ObservabilityPrivacyContract::default();
    Ok(Some(summary))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::io::Write;
    use std::path::PathBuf;

    fn unique_temp_dir(name: &str) -> PathBuf {
        let mut path = std::env::temp_dir();
        path.push(format!(
            "azdaja-observability-{name}-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_nanos()
        ));
        let _ = fs::remove_dir_all(&path);
        crate::secure_dir(&path).expect("create private temp dir");
        path
    }

    #[test]
    fn source_aggregate_counts_utf8_lines_and_byte_entropy_without_text() {
        let aggregate = SourceLocalAggregate::from_text("a\n\né");
        assert_eq!(aggregate.evidence_tier, EvidenceTier::ExactLocal);
        assert_eq!(aggregate.source_bytes, 5);
        assert_eq!(aggregate.utf8_chars, 4);
        assert_eq!(aggregate.physical_lines, 3);
        assert_eq!(aggregate.nonempty_lines, 2);
        assert_eq!(aggregate.byte_entropy_millibits, 1922);
        assert!((aggregate.byte_entropy_bits() - 1.922).abs() < f64::EPSILON);

        let serialized = serde_json::to_string(&aggregate).unwrap();
        assert!(!serialized.contains("a\\n"));
        assert!(!serialized.contains('é'));

        let whitespace = SourceLocalAggregate::from_text("alpha\n \t\r\n beta ");
        assert_eq!(whitespace.physical_lines, 3);
        assert_eq!(whitespace.nonempty_lines, 2);
    }

    #[test]
    fn aggregate_persistence_keeps_only_counts_and_privacy_flags() {
        let root = unique_temp_dir("privacy");
        let session_dir = root.join("session");
        crate::secure_dir(&session_dir).expect("create session dir");
        let sensitive = "prompt /Users/alice/project secret-token response deadbeef";
        let aggregate = SourceLocalAggregate::from_text(sensitive);

        append_recent_at(&root, RunKind::SoloLoad, &aggregate).expect("write recent summary");
        let mut session = SessionAggregateSummary::empty();
        session.loaded_sources = 1;
        session.current_source = Some(aggregate);
        write_session_summary_at(&session_dir, &session).expect("write session summary");

        let recent_json = fs::read_to_string(recent_path(&root)).expect("recent json");
        let session_json = fs::read_to_string(session_path(&session_dir)).expect("session json");
        for json in [&recent_json, &session_json] {
            assert!(json.contains("aggregate_only"));
            assert!(json.contains("excludes_source_text"));
            for forbidden in [
                sensitive,
                "/Users/alice/project",
                "secret-token",
                "deadbeef",
                "response deadbeef",
            ] {
                assert!(!json.contains(forbidden), "leaked {forbidden:?} in {json}");
            }
        }

        let loaded_recent = load_recent_summary_at(&root).expect("read recent");
        assert_eq!(loaded_recent.runs.len(), 1);
        assert_eq!(loaded_recent.runs[0].kind, RunKind::SoloLoad);
        let loaded_session = load_session_summary_at(&session_dir)
            .expect("read session")
            .expect("session summary exists");
        assert_eq!(loaded_session.loaded_sources, 1);
        assert_eq!(
            loaded_session.current_source.as_ref().unwrap().source_bytes,
            sensitive.len() as u64
        );
    }

    #[test]
    fn recent_runs_are_bounded_without_identifiers() {
        let root = unique_temp_dir("recent-bound");
        let aggregate = SourceLocalAggregate::from_text("x");
        for _ in 0..(RECENT_LIMIT + 3) {
            append_recent_at(&root, RunKind::SessionLoad, &aggregate).expect("append recent");
        }
        let json = fs::read_to_string(recent_path(&root)).expect("recent json");
        assert!(!json.contains("session_id"));
        assert!(!json.contains("source_path"));
        assert!(!json.contains("path\""));
        assert!(!json.contains("hash\""));
        let loaded = load_recent_summary_at(&root).expect("load recent");
        assert_eq!(loaded.runs.len(), RECENT_LIMIT);
    }

    #[test]
    fn summary_loaders_reject_non_regular_summary_paths() {
        let root = unique_temp_dir("nonregular");
        crate::secure_dir(&root.join(RECENT_DIR)).expect("create observability dir");
        fs::create_dir(recent_path(&root)).expect("create nonregular recent path");
        assert!(load_recent_summary_at(&root).is_err());

        let session_dir = root.join("session");
        crate::secure_dir(&session_dir).expect("create session dir");
        fs::create_dir(session_path(&session_dir)).expect("create nonregular session path");
        assert!(load_session_summary_at(&session_dir).is_err());
    }

    #[cfg(unix)]
    #[test]
    fn summary_loaders_reject_symlink_summary_paths() {
        let root = unique_temp_dir("symlink");
        crate::secure_dir(&root.join(RECENT_DIR)).expect("create observability dir");
        let target = root.join("target.json");
        let mut target_file = crate::create_private_file(&target).expect("create private target");
        target_file
            .write_all(br#"{"schema_version":1,"updated_unix":0,"max_recent_runs":24,"privacy":{"aggregate_only":true,"excludes_source_text":true,"excludes_paths":true,"excludes_hashes":true,"excludes_prompts":true,"excludes_responses":true},"runs":[]}"#)
            .expect("write target");
        std::os::unix::fs::symlink(&target, recent_path(&root)).expect("create recent symlink");
        assert!(load_recent_summary_at(&root).is_err());

        let session_dir = root.join("session");
        crate::secure_dir(&session_dir).expect("create session dir");
        std::os::unix::fs::symlink(&target, session_path(&session_dir))
            .expect("create session symlink");
        assert!(load_session_summary_at(&session_dir).is_err());
    }
}
