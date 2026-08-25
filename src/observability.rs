use anyhow::{Context, Result, bail};
use serde::{Deserialize, Serialize};
use std::{
    fs,
    io::Read,
    path::{Path, PathBuf},
    time::UNIX_EPOCH,
};

const SCHEMA_VERSION: u32 = 1;
const RECENT_LIMIT: usize = 24;
const RECENT_DIR: &str = "observability";
const RECENT_FILE: &str = "recent.json";
const SCOPES_DIR: &str = "scopes";
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
    SessionFinal,
    SoloFinal,
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

    pub fn compact_memory_constellation(&self) -> Option<MemoryConstellation> {
        MemoryConstellation::from_recent_summary(self)
    }
}

const CONSTELLATION_COLUMNS: usize = 24;
const CONSTELLATION_ROWS: usize = 4;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MemoryTracePoint {
    /// Zero is the newest retained aggregate trace.
    pub run_index: usize,
    /// Horizontal source-texture position. Zero is 0 bits/byte; 23 is 8 bits/byte.
    pub entropy_column: usize,
    /// Vertical absolute source-mass band. Zero is the largest band.
    pub mass_row: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MemoryConstellation {
    pub trace_count: usize,
    pub completed_count: usize,
    pub total_source_bytes: u64,
    pub newest_unix: u64,
    pub weighted_byte_entropy_millibits: u16,
    pub nonempty_line_millipercent: u16,
    pub points: Vec<MemoryTracePoint>,
}

impl MemoryConstellation {
    fn from_recent_summary(summary: &RecentAggregateSummary) -> Option<Self> {
        let newest_unix = summary.runs.first()?.observed_unix;
        let mut total_source_bytes = 0u64;
        let mut total_physical_lines = 0u64;
        let mut total_nonempty_lines = 0u64;
        let mut weighted_entropy = 0u128;
        let mut completed_count = 0usize;
        let mut points = Vec::with_capacity(summary.runs.len());
        for (run_index, run) in summary.runs.iter().enumerate() {
            if matches!(run.kind, RunKind::SessionFinal | RunKind::SoloFinal) {
                completed_count += 1;
            }
            let source = &run.source;
            total_source_bytes = total_source_bytes.saturating_add(source.source_bytes);
            total_physical_lines = total_physical_lines.saturating_add(source.physical_lines);
            total_nonempty_lines = total_nonempty_lines.saturating_add(source.nonempty_lines);
            weighted_entropy = weighted_entropy.saturating_add(
                u128::from(source.byte_entropy_millibits) * u128::from(source.source_bytes.max(1)),
            );
            points.push(MemoryTracePoint {
                run_index,
                entropy_column: entropy_column(source.byte_entropy_millibits),
                mass_row: source_mass_row(source.source_bytes),
            });
        }
        let entropy_weight = total_source_bytes.max(summary.runs.len() as u64);
        let weighted_byte_entropy_millibits = ((weighted_entropy + u128::from(entropy_weight / 2))
            / u128::from(entropy_weight))
        .min(8000) as u16;
        Some(Self {
            trace_count: summary.runs.len(),
            completed_count,
            total_source_bytes,
            newest_unix,
            weighted_byte_entropy_millibits,
            nonempty_line_millipercent: ratio_millipercent(
                total_nonempty_lines,
                total_physical_lines,
            ),
            points,
        })
    }

    pub fn weighted_byte_entropy_bits(&self) -> f64 {
        f64::from(self.weighted_byte_entropy_millibits) / 1000.0
    }

    /// Zero-order byte redundancy, `1 - H_byte / 8`. This is not a measured
    /// compressor ratio and must not be labelled as compression.
    pub fn zero_order_redundancy_millipercent(&self) -> u16 {
        zero_order_redundancy_millipercent(self.weighted_byte_entropy_millibits)
    }

    pub fn effective_byte_alphabet(&self) -> f64 {
        2.0f64.powf(self.weighted_byte_entropy_bits())
    }

    pub fn render_strip(&self, width: usize) -> String {
        let width = width.clamp(8, CONSTELLATION_COLUMNS);
        let mut cells = vec![Vec::<usize>::new(); width];
        for point in &self.points {
            let column = point.entropy_column * (width - 1) / (CONSTELLATION_COLUMNS - 1);
            cells[column].push(point.run_index);
        }
        cells
            .into_iter()
            .map(|indices| trace_cell(indices, 0))
            .collect()
    }

    pub fn render_grid(&self, width: usize) -> Vec<String> {
        self.render_grid_selected(width, 0)
    }

    pub fn render_grid_selected(&self, width: usize, selected_run: usize) -> Vec<String> {
        let width = width.clamp(12, CONSTELLATION_COLUMNS);
        let mut cells = vec![vec![Vec::<usize>::new(); width]; CONSTELLATION_ROWS];
        for point in &self.points {
            let column = point.entropy_column * (width - 1) / (CONSTELLATION_COLUMNS - 1);
            cells[point.mass_row][column].push(point.run_index);
        }
        cells
            .into_iter()
            .map(|row| {
                row.into_iter()
                    .map(|indices| trace_cell(indices, selected_run))
                    .collect()
            })
            .collect()
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SessionAggregateSummary {
    pub schema_version: u32,
    pub updated_unix: u64,
    pub privacy: ObservabilityPrivacyContract,
    pub loaded_sources: u64,
    #[serde(default)]
    pub completed_loaded_sources: u64,
    pub current_source: Option<SourceLocalAggregate>,
}

impl SessionAggregateSummary {
    fn empty() -> Self {
        Self {
            schema_version: SCHEMA_VERSION,
            updated_unix: unix_now(),
            privacy: ObservabilityPrivacyContract::default(),
            loaded_sources: 0,
            completed_loaded_sources: 0,
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

fn ratio_millipercent(numerator: u64, denominator: u64) -> u16 {
    if denominator == 0 {
        return 0;
    }
    ((u128::from(numerator.min(denominator)) * 1000 + u128::from(denominator / 2))
        / u128::from(denominator))
    .min(1000) as u16
}

fn zero_order_redundancy_millipercent(entropy_millibits: u16) -> u16 {
    1000u16.saturating_sub(((u32::from(entropy_millibits.min(8000)) * 1000 + 4000) / 8000) as u16)
}

fn entropy_column(entropy_millibits: u16) -> usize {
    (usize::from(entropy_millibits.min(8000)) * (CONSTELLATION_COLUMNS - 1) + 4000) / 8000
}

fn source_mass_row(source_bytes: u64) -> usize {
    const KIB: u64 = 1024;
    const MIB: u64 = 1024 * KIB;
    if source_bytes >= 16 * MIB {
        0
    } else if source_bytes >= MIB {
        1
    } else if source_bytes >= 64 * KIB {
        2
    } else {
        3
    }
}

fn trace_cell(indices: Vec<usize>, selected_run: usize) -> char {
    match indices.as_slice() {
        [] => '·',
        many if many.contains(&selected_run) => '●',
        [_] => '○',
        many if many.len() < 10 => char::from_digit(many.len() as u32, 10).unwrap_or('+'),
        _ => '+',
    }
}

pub(crate) fn record_session_source_load(
    session_dir: &Path,
    source: &SourceLocalAggregate,
) -> Result<()> {
    let _guard = crate::global_lock()?;
    let session_summary =
        load_session_summary_at(session_dir)?.unwrap_or_else(SessionAggregateSummary::empty);
    let session_summary = SessionAggregateSummary {
        schema_version: SCHEMA_VERSION,
        updated_unix: unix_now(),
        privacy: ObservabilityPrivacyContract::default(),
        loaded_sources: session_summary.loaded_sources.saturating_add(1),
        completed_loaded_sources: session_summary.completed_loaded_sources,
        current_source: Some(source.clone()),
    };
    write_session_summary_at(session_dir, &session_summary)?;
    Ok(())
}

pub(crate) fn record_session_completion(session_dir: &Path, scope: Option<&Path>) -> Result<()> {
    let root = crate::state_home()?;
    let _guard = crate::global_lock()?;
    let scope_key = scope.and_then(|path| scope_key_for_path(path).ok());
    record_session_completion_at_with_scope(&root, session_dir, scope_key.as_deref())
}

#[cfg(test)]
fn record_session_completion_at(root: &Path, session_dir: &Path) -> Result<()> {
    record_session_completion_at_with_scope(root, session_dir, None)
}

fn record_session_completion_at_with_scope(
    root: &Path,
    session_dir: &Path,
    scope_key: Option<&str>,
) -> Result<()> {
    let Some(mut summary) = load_session_summary_at(session_dir)? else {
        return Ok(());
    };
    if summary.loaded_sources == 0
        || summary.completed_loaded_sources >= summary.loaded_sources
        || summary.current_source.is_none()
    {
        return Ok(());
    }
    let source = summary.current_source.clone().expect("checked source");
    summary.completed_loaded_sources = summary.loaded_sources;
    summary.updated_unix = unix_now();
    write_session_summary_at(session_dir, &summary)?;
    append_recent_at(root, RunKind::SessionFinal, &source)?;
    if let Some(scope_key) = scope_key {
        append_scoped_at(root, scope_key, RunKind::SessionFinal, &source)?;
    }
    Ok(())
}

pub fn record_solo_completion(source: &SourceLocalAggregate) -> Result<()> {
    let root = crate::state_home()?;
    let _guard = crate::global_lock()?;
    append_recent_at(&root, RunKind::SoloFinal, source)?;
    let cwd = std::env::current_dir()?;
    let scope_key = scope_key_for_path(&cwd)?;
    append_scoped_at(&root, &scope_key, RunKind::SoloFinal, source)
}

pub fn load_recent_summary() -> Result<RecentAggregateSummary> {
    let root = crate::state_home()?;
    load_recent_summary_at(&root)
}

/// Return the stable private key used for aggregate state belonging to one canonical working
/// directory. The path itself is never written into observability JSON.
pub fn scope_key_for_path(path: &Path) -> Result<String> {
    let canonical = fs::canonicalize(path)
        .with_context(|| format!("canonicalize observability scope {}", path.display()))?;
    Ok(crate::sha256_hex(&scope_key_material(&canonical)))
}

fn scope_key_material(path: &Path) -> Vec<u8> {
    let mut material = b"azdaja-observability-scope-v1\0".to_vec();
    #[cfg(unix)]
    {
        use std::os::unix::ffi::OsStrExt;
        material.extend_from_slice(path.as_os_str().as_bytes());
    }
    #[cfg(windows)]
    {
        use std::os::windows::ffi::OsStrExt;
        for unit in path.as_os_str().encode_wide() {
            material.extend_from_slice(&unit.to_le_bytes());
        }
    }
    #[cfg(not(any(unix, windows)))]
    material.extend_from_slice(path.to_string_lossy().as_bytes());
    material
}

/// Load the numeric source-summary history for one working-directory scope.
pub fn load_scoped_summary(path: &Path) -> Result<RecentAggregateSummary> {
    let root = crate::state_home()?;
    let key = scope_key_for_path(path)?;
    load_scoped_summary_at(&root, &key)
}

pub(crate) fn load_session_summary(session_dir: &Path) -> Result<Option<SessionAggregateSummary>> {
    load_session_summary_at(session_dir)
}

fn recent_path(root: &Path) -> std::path::PathBuf {
    root.join(RECENT_DIR).join(RECENT_FILE)
}

fn scopes_path(root: &Path) -> PathBuf {
    root.join(RECENT_DIR).join(SCOPES_DIR)
}

fn scoped_path(root: &Path, key: &str) -> PathBuf {
    scopes_path(root).join(format!("{key}.json"))
}

fn session_path(session_dir: &Path) -> std::path::PathBuf {
    session_dir.join(SESSION_FILE)
}

fn append_recent_at(root: &Path, kind: RunKind, source: &SourceLocalAggregate) -> Result<()> {
    let dir = root.join(RECENT_DIR);
    crate::secure_dir(&dir)?;
    append_recent_file(&recent_path(root), kind, source)
}

fn append_scoped_at(
    root: &Path,
    scope_key: &str,
    kind: RunKind,
    source: &SourceLocalAggregate,
) -> Result<()> {
    crate::secure_dir(&scopes_path(root))?;
    append_recent_file(&scoped_path(root, scope_key), kind, source)
}

fn append_recent_file(path: &Path, kind: RunKind, source: &SourceLocalAggregate) -> Result<()> {
    let mut summary = load_summary_path(path)?;
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
    crate::atomic_write(path, &bytes)
}

fn load_recent_summary_at(root: &Path) -> Result<RecentAggregateSummary> {
    load_summary_path(&recent_path(root))
}

fn load_scoped_summary_at(root: &Path, scope_key: &str) -> Result<RecentAggregateSummary> {
    load_summary_path(&scoped_path(root, scope_key))
}

fn load_summary_path(path: &Path) -> Result<RecentAggregateSummary> {
    if !summary_path_exists(path)? {
        return Ok(RecentAggregateSummary::empty());
    }
    let bytes = read_private_summary_file(path)
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
        assert!(!json.contains("memory_observations"));
        let loaded = load_recent_summary_at(&root).expect("load recent");
        assert_eq!(loaded.runs.len(), RECENT_LIMIT);
    }

    #[test]
    fn successful_session_completion_is_persisted_once_per_loaded_source() {
        let root = unique_temp_dir("completed-session");
        let session_dir = root.join("session");
        crate::secure_dir(&session_dir).expect("create session dir");
        let source = SourceLocalAggregate::from_text("private source\nalpha beta\n");
        let mut session = SessionAggregateSummary::empty();
        session.loaded_sources = 1;
        session.current_source = Some(source.clone());
        write_session_summary_at(&session_dir, &session).expect("write session source summary");

        assert!(load_recent_summary_at(&root).unwrap().runs.is_empty());
        record_session_completion_at(&root, &session_dir).expect("record completion");
        record_session_completion_at(&root, &session_dir).expect("idempotent completion");

        let recent = load_recent_summary_at(&root).expect("load completed history");
        assert_eq!(recent.runs.len(), 1);
        assert_eq!(recent.runs[0].kind, RunKind::SessionFinal);
        assert_eq!(recent.runs[0].source, source);
        let session = load_session_summary_at(&session_dir)
            .expect("load session summary")
            .expect("session summary exists");
        assert_eq!(session.completed_loaded_sources, 1);
    }

    #[test]
    fn recent_aggregates_render_a_truthful_memory_constellation() {
        let root = unique_temp_dir("constellation");
        let repetitive = SourceLocalAggregate::from_text("aaaaaaaaaaaaaaaa");
        let sensitive = "vault note [[private/person]]\nsecret-token 0123456789\n";
        let varied = SourceLocalAggregate::from_text(sensitive);
        append_recent_at(&root, RunKind::SessionLoad, &repetitive).expect("append old trace");
        append_recent_at(&root, RunKind::SoloFinal, &varied).expect("append completed memory");

        let json = fs::read_to_string(recent_path(&root)).expect("recent json");
        assert!(!json.contains("memory_observations"));
        for forbidden in [
            "vault note",
            "private/person",
            "secret-token",
            "[[private/person]]",
        ] {
            assert!(!json.contains(forbidden), "leaked {forbidden:?} in {json}");
        }

        let loaded = load_recent_summary_at(&root).expect("load recent");
        let constellation = loaded
            .compact_memory_constellation()
            .expect("constellation from retained traces");
        assert_eq!(constellation.trace_count, 2);
        assert_eq!(constellation.completed_count, 1);
        assert_eq!(constellation.points.len(), 2);
        assert_eq!(
            constellation.total_source_bytes,
            (sensitive.len() + 16) as u64
        );
        assert!(constellation.weighted_byte_entropy_bits() > 0.0);
        assert!(constellation.zero_order_redundancy_millipercent() <= 1000);
        assert!(constellation.effective_byte_alphabet() > 1.0);
        assert_eq!(constellation.nonempty_line_millipercent, 1000);
        let strip = constellation.render_strip(16);
        assert_eq!(strip.chars().count(), 16);
        assert!(strip.contains('●'));
        assert!(strip.contains('○'));
        let grid = constellation.render_grid(24);
        assert_eq!(grid.len(), CONSTELLATION_ROWS);
        assert!(grid.iter().all(|row| row.chars().count() == 24));
    }

    #[test]
    fn scoped_histories_are_isolated_deterministic_and_path_free() {
        let root = unique_temp_dir("scoped-root");
        let first = unique_temp_dir("scoped-first");
        let second = unique_temp_dir("scoped-second");
        let first_key = scope_key_for_path(&first).expect("first scope key");
        let second_key = scope_key_for_path(&second).expect("second scope key");
        assert_ne!(first_key, second_key);
        assert_eq!(
            first_key,
            scope_key_for_path(&first.join(".")).expect("canonical scope key")
        );

        let first_source = SourceLocalAggregate::from_text("first project source\n");
        let second_source = SourceLocalAggregate::from_text("second project source\n");
        append_scoped_at(&root, &first_key, RunKind::SoloFinal, &first_source)
            .expect("write first scope");
        append_scoped_at(&root, &second_key, RunKind::SoloFinal, &second_source)
            .expect("write second scope");

        let first_summary = load_scoped_summary_at(&root, &first_key).expect("read first scope");
        let second_summary = load_scoped_summary_at(&root, &second_key).expect("read second scope");
        assert_eq!(first_summary.runs.len(), 1);
        assert_eq!(first_summary.runs[0].source, first_source);
        assert_eq!(second_summary.runs.len(), 1);
        assert_eq!(second_summary.runs[0].source, second_source);
        assert!(load_recent_summary_at(&root).unwrap().runs.is_empty());

        let first_json = fs::read_to_string(scoped_path(&root, &first_key)).unwrap();
        assert!(!first_json.contains(first.to_string_lossy().as_ref()));
        assert!(!first_json.contains("first project source"));
    }

    #[cfg(unix)]
    #[test]
    fn scope_keys_distinguish_non_utf8_directory_names() {
        use std::ffi::OsString;
        use std::os::unix::ffi::OsStringExt;

        let first = PathBuf::from(OsString::from_vec(
            [b"project".as_slice(), &[0x80]].concat(),
        ));
        let second = PathBuf::from(OsString::from_vec(
            [b"project".as_slice(), &[0x81]].concat(),
        ));
        assert_ne!(
            crate::sha256_hex(&scope_key_material(&first)),
            crate::sha256_hex(&scope_key_material(&second))
        );
    }

    #[test]
    fn obsolete_derived_observation_fields_are_ignored_on_load() {
        let root = unique_temp_dir("legacy");
        crate::secure_dir(&root.join(RECENT_DIR)).expect("create observability dir");
        let aggregate = SourceLocalAggregate::from_text("aaaa\n");
        let legacy = serde_json::json!({
            "schema_version": 1,
            "updated_unix": 1,
            "max_recent_runs": 24,
            "privacy": ObservabilityPrivacyContract::default(),
            "runs": [{
                "kind": "solo-load",
                "observed_unix": 1,
                "source": aggregate,
            }],
            "memory_observations": [{"obsolete": true}]
        });
        crate::atomic_write(
            &recent_path(&root),
            serde_json::to_string_pretty(&legacy).unwrap().as_bytes(),
        )
        .expect("write legacy");
        let loaded = load_recent_summary_at(&root).expect("load legacy");
        assert!(loaded.compact_memory_constellation().is_some());
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
