use anyhow::{Context, Result, bail};
use serde::{Deserialize, Serialize};
use std::{
    collections::BTreeSet,
    env, fs,
    io::Read,
    path::{Path, PathBuf},
    time::{SystemTime, UNIX_EPOCH},
};

const SCHEMA_VERSION: u32 = 1;
const MEMORY_DIR: &str = "memory";
const SCOPES_DIR: &str = "scopes";
const GLOBAL_LEDGER: &str = "global.jsonl";
const MAX_RECORDS: usize = 256;
const MAX_LEDGER_BYTES: usize = 512 * 1024;
const MAX_TEXT_CHARS: usize = 4096;
const MAX_TAGS: usize = 16;
const MAX_TAG_CHARS: usize = 48;
const MAX_LINKS: usize = 16;
const ID_HEX_CHARS: usize = 16;

/// A deliberately small, explicit memory vocabulary. These are records, not
/// model confidence scores or automatic reflections.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum MemoryKind {
    Decision,
    Observation,
    Failure,
    Hypothesis,
    Disagreement,
}

impl MemoryKind {
    pub fn parse(value: &str) -> Result<Self> {
        match value {
            "decision" => Ok(Self::Decision),
            "observation" => Ok(Self::Observation),
            "failure" => Ok(Self::Failure),
            "hypothesis" => Ok(Self::Hypothesis),
            "disagreement" => Ok(Self::Disagreement),
            _ => bail!(
                "unknown memory kind {value:?}; use decision, observation, failure, hypothesis, or disagreement"
            ),
        }
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Decision => "decision",
            Self::Observation => "observation",
            Self::Failure => "failure",
            Self::Hypothesis => "hypothesis",
            Self::Disagreement => "disagreement",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum MemoryRelation {
    Supports,
    Supersedes,
    DerivedFrom,
    RelatedTo,
}

impl MemoryRelation {
    pub fn parse(value: &str) -> Result<Self> {
        match value {
            "supports" => Ok(Self::Supports),
            "supersedes" => Ok(Self::Supersedes),
            "derived-from" => Ok(Self::DerivedFrom),
            "related-to" => Ok(Self::RelatedTo),
            _ => bail!(
                "unknown memory relation {value:?}; use supports, supersedes, derived-from, or related-to"
            ),
        }
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Supports => "supports",
            Self::Supersedes => "supersedes",
            Self::DerivedFrom => "derived-from",
            Self::RelatedTo => "related-to",
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct MemoryLink {
    pub relation: MemoryRelation,
    pub target_id: String,
}

impl MemoryLink {
    pub fn parse(value: &str) -> Result<Self> {
        let (relation, target_id) = value
            .split_once(':')
            .ok_or_else(|| anyhow::anyhow!("memory link must be relation:id"))?;
        let relation = MemoryRelation::parse(relation)?;
        validate_id(target_id)?;
        Ok(Self {
            relation,
            target_id: target_id.to_owned(),
        })
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct MemoryProvenance {
    /// This first slice is intentionally user-authored only. Automatic model
    /// extraction is excluded to avoid silent memory poisoning.
    pub origin: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct MemoryRecord {
    pub schema_version: u32,
    pub id: String,
    pub created_unix: u64,
    pub kind: MemoryKind,
    pub text: String,
    pub tags: Vec<String>,
    pub links: Vec<MemoryLink>,
    pub provenance: MemoryProvenance,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct MemoryBacklink {
    pub source_id: String,
    pub relation: MemoryRelation,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct MemoryView {
    pub record: MemoryRecord,
    pub backlinks: Vec<MemoryBacklink>,
}

/// Add one explicitly authored record to the current working-directory ledger,
/// or to the separate global ledger when `global` is true.
pub fn add_current(
    global: bool,
    kind: MemoryKind,
    text: String,
    tags: Vec<String>,
    links: Vec<MemoryLink>,
) -> Result<MemoryRecord> {
    let root = crate::state_home()?;
    let scope_key = current_scope_key(global)?;
    append_at(&root, scope_key.as_deref(), kind, text, tags, links)
}

pub fn list_current(global: bool) -> Result<Vec<MemoryRecord>> {
    let root = crate::state_home()?;
    let scope_key = current_scope_key(global)?;
    list_at(&root, scope_key.as_deref())
}

pub fn show_current(global: bool, id: &str) -> Result<MemoryView> {
    let root = crate::state_home()?;
    let scope_key = current_scope_key(global)?;
    show_at(&root, scope_key.as_deref(), id)
}

pub fn append_at(
    root: &Path,
    scope_key: Option<&str>,
    kind: MemoryKind,
    text: String,
    tags: Vec<String>,
    links: Vec<MemoryLink>,
) -> Result<MemoryRecord> {
    validate_new_fields(&text, &tags, &links)?;
    let path = ledger_path(root, scope_key)?;
    prepare_parent(root, scope_key)?;
    if let Some(scope_key) = scope_key {
        crate::persist_current_scope_label_for_key_at(root, scope_key);
    }
    let _lock = crate::lock_path(&path.with_extension("lock"))?;
    let mut records = load_path(&path)?;
    if records.len() >= MAX_RECORDS {
        bail!(
            "memory ledger is full at {MAX_RECORDS} records; export or rotate it before adding more"
        )
    }
    let existing_ids = records
        .iter()
        .map(|record| record.id.as_str())
        .collect::<BTreeSet<_>>();
    for link in &links {
        if !existing_ids.contains(link.target_id.as_str()) {
            bail!("memory link target does not exist: {}", link.target_id)
        }
    }
    let now_ns = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    let scope_material = scope_key.unwrap_or("global");
    let id_material = format!(
        "azdaja-memory-v1\0{scope_material}\0{now_ns}\0{}\0{}",
        kind.as_str(),
        text
    );
    let id = format!(
        "m{}",
        &crate::sha256_hex(id_material.as_bytes())[..ID_HEX_CHARS]
    );
    if existing_ids.contains(id.as_str()) {
        bail!("memory record id collision; retry the operation")
    }
    let record = MemoryRecord {
        schema_version: SCHEMA_VERSION,
        id,
        created_unix: now_ns
            .checked_div(1_000_000_000)
            .and_then(|seconds| u64::try_from(seconds).ok())
            .unwrap_or(u64::MAX),
        kind,
        text,
        tags,
        links,
        provenance: MemoryProvenance {
            origin: "manual".to_owned(),
        },
    };
    records.push(record.clone());
    let encoded = encode_records(&records)?;
    if encoded.len() > MAX_LEDGER_BYTES {
        bail!("memory ledger exceeds the {MAX_LEDGER_BYTES}-byte bound")
    }
    crate::atomic_write(&path, &encoded)?;
    // Re-open through the hardened private-file path after replacement. This
    // protects the public command from accepting a swapped or linked victim.
    let _ = crate::open_private_file(&path, false)?;
    Ok(record)
}

pub fn list_at(root: &Path, scope_key: Option<&str>) -> Result<Vec<MemoryRecord>> {
    let path = ledger_path(root, scope_key)?;
    prepare_parent(root, scope_key)?;
    let _lock = crate::lock_path(&path.with_extension("lock"))?;
    load_path(&path)
}

pub fn show_at(root: &Path, scope_key: Option<&str>, id: &str) -> Result<MemoryView> {
    validate_id(id)?;
    let records = list_at(root, scope_key)?;
    let record = records
        .iter()
        .find(|record| record.id == id)
        .cloned()
        .ok_or_else(|| anyhow::anyhow!("memory record not found: {id}"))?;
    let backlinks = records
        .iter()
        .filter_map(|candidate| {
            candidate
                .links
                .iter()
                .find(|link| link.target_id == id)
                .map(|link| MemoryBacklink {
                    source_id: candidate.id.clone(),
                    relation: link.relation,
                })
        })
        .collect();
    Ok(MemoryView { record, backlinks })
}

pub fn single_line(text: &str) -> String {
    text.chars()
        .map(|character| {
            if character.is_control() {
                ' '
            } else {
                character
            }
        })
        .collect()
}

pub(crate) fn current_scope_key(global: bool) -> Result<Option<String>> {
    if global {
        return Ok(None);
    }
    Ok(Some(crate::observability::scope_key_for_path(
        &env::current_dir()?,
    )?))
}

fn ledger_path(root: &Path, scope_key: Option<&str>) -> Result<PathBuf> {
    if !root.is_absolute() {
        bail!("memory state root must be absolute")
    }
    let path = match scope_key {
        Some(key) => {
            validate_scope_key(key)?;
            root.join(MEMORY_DIR)
                .join(SCOPES_DIR)
                .join(format!("{key}.jsonl"))
        }
        None => root.join(MEMORY_DIR).join(GLOBAL_LEDGER),
    };
    Ok(path)
}

pub(crate) fn scoped_record_count_at(root: &Path, scope_key: &str) -> Result<usize> {
    let path = ledger_path(root, Some(scope_key))?;
    fs::symlink_metadata(&path)
        .with_context(|| format!("read memory scope metadata {}", path.display()))?;
    Ok(load_path(&path)?.len())
}

fn prepare_parent(root: &Path, scope_key: Option<&str>) -> Result<()> {
    crate::secure_dir(&root.join(MEMORY_DIR))?;
    if scope_key.is_some() {
        crate::secure_dir(&root.join(MEMORY_DIR).join(SCOPES_DIR))?;
    }
    Ok(())
}

fn load_path(path: &Path) -> Result<Vec<MemoryRecord>> {
    let metadata = match fs::symlink_metadata(path) {
        Ok(metadata) => metadata,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(Vec::new()),
        Err(error) => return Err(error.into()),
    };
    if !metadata.file_type().is_file() {
        bail!("memory ledger is not a regular file")
    }
    let file = crate::open_private_file(path, false)
        .with_context(|| "memory ledger is unsafe or not private")?;
    let mut bytes = Vec::new();
    file.take((MAX_LEDGER_BYTES + 1) as u64)
        .read_to_end(&mut bytes)?;
    if bytes.len() > MAX_LEDGER_BYTES {
        bail!("memory ledger exceeds the {MAX_LEDGER_BYTES}-byte bound")
    }
    let text = std::str::from_utf8(&bytes).context("memory ledger is not UTF-8")?;
    let mut records = Vec::new();
    let mut ids = BTreeSet::new();
    for (line_index, line) in text.lines().enumerate() {
        if line.trim().is_empty() {
            bail!("memory ledger contains an empty line at {}", line_index + 1)
        }
        let record: MemoryRecord = serde_json::from_str(line)
            .with_context(|| format!("memory ledger record {} is invalid", line_index + 1))?;
        validate_record(&record)?;
        if !ids.insert(record.id.clone()) {
            bail!("memory ledger repeats record id {}", record.id)
        }
        records.push(record);
        if records.len() > MAX_RECORDS {
            bail!("memory ledger contains more than {MAX_RECORDS} records")
        }
    }
    let all_ids = records
        .iter()
        .map(|record| record.id.as_str())
        .collect::<BTreeSet<_>>();
    for record in &records {
        for link in &record.links {
            if !all_ids.contains(link.target_id.as_str()) {
                bail!(
                    "memory ledger link target does not exist: {}",
                    link.target_id
                )
            }
        }
    }
    Ok(records)
}

fn encode_records(records: &[MemoryRecord]) -> Result<Vec<u8>> {
    let mut bytes = Vec::new();
    for record in records {
        serde_json::to_writer(&mut bytes, record)?;
        bytes.push(b'\n');
    }
    Ok(bytes)
}

fn validate_new_fields(text: &str, tags: &[String], links: &[MemoryLink]) -> Result<()> {
    if text.trim().is_empty() {
        bail!("memory text cannot be empty")
    }
    if text.chars().count() > MAX_TEXT_CHARS {
        bail!("memory text exceeds {MAX_TEXT_CHARS} characters")
    }
    if text.contains('\0') {
        bail!("memory text contains a NUL byte")
    }
    if tags.len() > MAX_TAGS {
        bail!("memory record has more than {MAX_TAGS} tags")
    }
    for tag in tags {
        if tag.is_empty() || tag.chars().count() > MAX_TAG_CHARS || tag.contains('\0') {
            bail!("memory tag is empty, too long, or contains a NUL byte")
        }
    }
    if links.len() > MAX_LINKS {
        bail!("memory record has more than {MAX_LINKS} links")
    }
    for link in links {
        validate_id(&link.target_id)?;
    }
    Ok(())
}

fn validate_record(record: &MemoryRecord) -> Result<()> {
    if record.schema_version != SCHEMA_VERSION {
        bail!(
            "unsupported memory schema version {}",
            record.schema_version
        )
    }
    validate_id(&record.id)?;
    if record.provenance.origin != "manual" {
        bail!("memory record provenance must be manual")
    }
    validate_new_fields(&record.text, &record.tags, &record.links)
}

fn validate_id(id: &str) -> Result<()> {
    if id.len() != 1 + ID_HEX_CHARS
        || !id.starts_with('m')
        || !id[1..]
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit() && !byte.is_ascii_uppercase())
    {
        bail!("invalid memory record id: {id}")
    }
    Ok(())
}

fn validate_scope_key(key: &str) -> Result<()> {
    if key.len() != 64 || !key.bytes().all(|byte| byte.is_ascii_hexdigit()) {
        bail!("invalid memory scope key")
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{
        sync::Arc,
        thread,
        time::{SystemTime, UNIX_EPOCH},
    };

    fn root(name: &str) -> PathBuf {
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let root = std::env::temp_dir().join(format!("azdaja-memory-{name}-{stamp}"));
        fs::create_dir_all(&root).unwrap();
        root
    }

    #[test]
    fn scope_ledgers_are_isolated_and_show_backlinks() {
        let root = root("isolated");
        let first_key = "a".repeat(64);
        let second_key = "b".repeat(64);
        let first = append_at(
            &root,
            Some(&first_key),
            MemoryKind::Decision,
            "keep scope-first retrieval".into(),
            vec!["memory".into()],
            Vec::new(),
        )
        .unwrap();
        let second = append_at(
            &root,
            Some(&first_key),
            MemoryKind::Disagreement,
            "retain the minority view".into(),
            Vec::new(),
            vec![MemoryLink {
                relation: MemoryRelation::RelatedTo,
                target_id: first.id.clone(),
            }],
        )
        .unwrap();
        append_at(
            &root,
            Some(&second_key),
            MemoryKind::Observation,
            "other project".into(),
            Vec::new(),
            Vec::new(),
        )
        .unwrap();
        assert_eq!(list_at(&root, Some(&first_key)).unwrap().len(), 2);
        assert_eq!(list_at(&root, Some(&second_key)).unwrap().len(), 1);
        let view = show_at(&root, Some(&first_key), &first.id).unwrap();
        assert_eq!(view.record.id, first.id);
        assert_eq!(view.backlinks[0].source_id, second.id);
        let bytes = fs::read_to_string(ledger_path(&root, Some(&first_key)).unwrap()).unwrap();
        assert!(!bytes.contains(root.to_string_lossy().as_ref()));
        assert!(!bytes.contains(&first_key));
    }

    #[test]
    fn corrupt_and_unsafe_ledgers_fail_closed() {
        let root = root("corrupt");
        let key = "c".repeat(64);
        let path = ledger_path(&root, Some(&key)).unwrap();
        prepare_parent(&root, Some(&key)).unwrap();
        fs::write(&path, b"not-json\n").unwrap();
        assert!(list_at(&root, Some(&key)).is_err());
        fs::remove_file(&path).unwrap();
        fs::write(&path, b"victim").unwrap();
        #[cfg(unix)]
        {
            use std::os::unix::fs::symlink;
            let victim = root.join("victim");
            fs::write(&victim, b"unchanged").unwrap();
            fs::remove_file(&path).unwrap();
            symlink(&victim, &path).unwrap();
            assert!(
                append_at(
                    &root,
                    Some(&key),
                    MemoryKind::Observation,
                    "must not follow links".into(),
                    Vec::new(),
                    Vec::new(),
                )
                .is_err()
            );
            assert_eq!(fs::read(&victim).unwrap(), b"unchanged");
        }
    }

    #[test]
    fn concurrent_appends_are_bounded_and_unique() {
        let root = Arc::new(root("concurrent"));
        let key = Arc::new("d".repeat(64));
        let mut workers = Vec::new();
        for index in 0..32 {
            let root = Arc::clone(&root);
            let key = Arc::clone(&key);
            workers.push(thread::spawn(move || {
                append_at(
                    &root,
                    Some(key.as_str()),
                    MemoryKind::Observation,
                    format!("observation-{index}"),
                    Vec::new(),
                    Vec::new(),
                )
                .unwrap();
            }));
        }
        for worker in workers {
            worker.join().unwrap();
        }
        let records = list_at(&root, Some(key.as_str())).unwrap();
        assert_eq!(records.len(), 32);
        let ids = records
            .iter()
            .map(|record| record.id.as_str())
            .collect::<BTreeSet<_>>();
        assert_eq!(ids.len(), 32);
        assert!(
            append_at(
                &root,
                Some(key.as_str()),
                MemoryKind::Observation,
                "x".repeat(MAX_TEXT_CHARS + 1),
                Vec::new(),
                Vec::new(),
            )
            .is_err()
        );
    }

    #[test]
    fn large_concurrent_append_stress_stops_at_the_256_record_bound() {
        let root = Arc::new(root("large-concurrent"));
        let key = Arc::new("e".repeat(64));
        let mut workers = Vec::new();
        for index in 0..300 {
            let root = Arc::clone(&root);
            let key = Arc::clone(&key);
            workers.push(thread::spawn(move || {
                append_at(
                    &root,
                    Some(key.as_str()),
                    MemoryKind::Observation,
                    format!("large-stress-observation-{index}"),
                    Vec::new(),
                    Vec::new(),
                )
            }));
        }
        let results = workers
            .into_iter()
            .map(|worker| worker.join().unwrap())
            .collect::<Vec<_>>();
        assert_eq!(
            results.iter().filter(|result| result.is_ok()).count(),
            MAX_RECORDS
        );
        assert_eq!(results.iter().filter(|result| result.is_err()).count(), 44);
        let records = list_at(&root, Some(key.as_str())).unwrap();
        assert_eq!(records.len(), MAX_RECORDS);
        let ids = records
            .iter()
            .map(|record| record.id.as_str())
            .collect::<BTreeSet<_>>();
        assert_eq!(ids.len(), MAX_RECORDS);
        let bytes = fs::metadata(ledger_path(&root, Some(key.as_str())).unwrap())
            .unwrap()
            .len();
        assert!(bytes <= MAX_LEDGER_BYTES as u64);
    }
}
