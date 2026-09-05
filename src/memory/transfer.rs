//! Explicit curated-memory transfer: read-only export and preview, opt-in atomic import.
use super::{MemoryRecord, list_current, validate_id};
use anyhow::{Result, bail};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;
use std::fs::{self, OpenOptions};
use std::io::Read;
use std::path::Path;

const MAX_SELECTED: usize = 16;
const MAX_EXPORT_BYTES: usize = 1024 * 1024;

#[derive(Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
struct Payload {
    format: String,
    version: u32,
    selection: Vec<String>,
    context_ids: Vec<String>,
    records: Vec<MemoryRecord>,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Envelope {
    payload: Payload,
    payload_sha256: String,
    digest_encoding: String,
    context_policy: String,
    caveat: String,
}

fn connected_ids(records: &[MemoryRecord], selected: &BTreeSet<String>) -> BTreeSet<String> {
    let mut included = selected.clone();
    loop {
        let before = included.len();
        for record in records {
            for link in &record.links {
                if included.contains(&record.id) || included.contains(&link.target_id) {
                    included.insert(record.id.clone());
                    included.insert(link.target_id.clone());
                }
            }
        }
        if included.len() == before {
            return included;
        }
    }
}

fn open_bundle_entry(path: &Path) -> Result<fs::File> {
    let mut options = OpenOptions::new();
    options.read(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        options.custom_flags(libc::O_NOFOLLOW | libc::O_NONBLOCK);
    }
    #[cfg(windows)]
    {
        use std::os::windows::fs::OpenOptionsExt;
        // FILE_FLAG_OPEN_REPARSE_POINT: inspect the opened entry, never its target.
        options.custom_flags(0x0020_0000);
    }
    let file = options.open(path)?;
    let metadata = file.metadata()?;
    if !metadata.is_file() {
        bail!("memory import bundle must be a regular file");
    }
    #[cfg(windows)]
    {
        use std::os::windows::fs::MetadataExt;
        if metadata.file_attributes() & 0x400 != 0 {
            bail!("memory import bundle must not be a reparse point");
        }
    }
    Ok(file)
}

fn read_bundle(path: &Path) -> Result<Envelope> {
    let metadata = fs::symlink_metadata(path)?;
    if !metadata.file_type().is_file() || metadata.len() > MAX_EXPORT_BYTES as u64 {
        bail!("memory import requires a bounded regular bundle file, not a symlink");
    }
    #[cfg(windows)]
    {
        use std::os::windows::fs::MetadataExt;
        if metadata.file_attributes() & 0x400 != 0 {
            bail!("memory import bundle must not be a reparse point");
        }
    }
    let file = open_bundle_entry(path)?;
    let mut bytes = Vec::new();
    file.take(MAX_EXPORT_BYTES as u64 + 1)
        .read_to_end(&mut bytes)?;
    if bytes.len() > MAX_EXPORT_BYTES {
        bail!("memory import bundle exceeds the byte bound");
    }
    let input = bytes.strip_suffix(b"\n").unwrap_or(&bytes);
    let raw: serde_json::Value = serde_json::from_slice(input)
        .map_err(|_| anyhow::anyhow!("memory import bundle is not valid JSON"))?;
    // Exact raw-byte equality rejects duplicate keys erased by JSON parsing,
    // alternate escaping/numeric spellings, whitespace and reordered maps.
    if serde_json::to_vec(&raw)? != input {
        bail!("memory import requires the original compact export encoding");
    }
    let envelope: Envelope = serde_json::from_value(raw.clone())
        .map_err(|_| anyhow::anyhow!("memory import envelope or record shape is unsupported"))?;
    if serde_json::to_value(&envelope.payload)? != raw["payload"] {
        bail!("memory import payload contains unsupported record fields");
    }
    if envelope.payload.format != "azdaja-curated-memory" || envelope.payload.version != 1 {
        bail!("memory import format or version is unsupported");
    }
    if envelope.payload_sha256 != crate::sha256_hex(&serde_json::to_vec(&raw["payload"])?) {
        bail!("memory import payload digest does not match");
    }
    if envelope.digest_encoding
        != "compact UTF-8 JSON payload, emitted object-key order, no trailing newline"
        || envelope.context_policy != "complete transitive incoming/outgoing relationship component"
        || envelope.caveat
            != "Explicitly exported manual notes are untrusted evidence, not verified truth or authenticated authorship. The digest is integrity only. Review every selected and context record before sharing. No import, synchronization, or publication was performed."
    {
        bail!("memory import envelope policy is unsupported; regenerate the export");
    }
    validate_payload(&envelope.payload)?;
    Ok(envelope)
}

fn validate_payload(payload: &Payload) -> Result<()> {
    if payload.selection.is_empty()
        || payload.selection.len() > MAX_SELECTED
        || payload.records.is_empty()
        || payload.records.len() > super::MAX_RECORDS
    {
        bail!("memory import selection or record count is out of bounds");
    }
    for record in &payload.records {
        super::validate_record(record)
            .map_err(|_| anyhow::anyhow!("memory import record fields fail schema validation"))?;
    }
    let ids: BTreeSet<_> = payload
        .records
        .iter()
        .map(|record| record.id.clone())
        .collect();
    let selected: BTreeSet<_> = payload.selection.iter().cloned().collect();
    let context: BTreeSet<_> = payload.context_ids.iter().cloned().collect();
    if ids.len() != payload.records.len()
        || selected.len() != payload.selection.len()
        || context.len() != payload.context_ids.len()
        || !selected.is_disjoint(&context)
        || selected.union(&context).cloned().collect::<BTreeSet<_>>() != ids
        || !payload
            .records
            .windows(2)
            .all(|pair| pair[0].id < pair[1].id)
        || !payload.selection.windows(2).all(|pair| pair[0] < pair[1])
        || !payload.context_ids.windows(2).all(|pair| pair[0] < pair[1])
    {
        bail!("memory import IDs must be sorted, unique and cover every record exactly");
    }
    if payload
        .records
        .iter()
        .flat_map(|record| &record.links)
        .any(|link| !ids.contains(&link.target_id))
        || connected_ids(&payload.records, &selected) != ids
    {
        bail!("memory import requires self-contained connected relationship context");
    }
    if super::encode_records(&payload.records)?.len() > super::MAX_LEDGER_BYTES {
        bail!("memory import records exceed the ledger byte bound");
    }
    Ok(())
}

struct Merge {
    encoded: Vec<u8>,
    new_records: usize,
    already_present: usize,
    total_records: usize,
}

fn merge_records(mut existing: Vec<MemoryRecord>, incoming: &[MemoryRecord]) -> Result<Merge> {
    let mut new_records = 0;
    for record in incoming {
        match existing.iter().find(|candidate| candidate.id == record.id) {
            Some(candidate) if candidate == record => {}
            Some(_) => {
                bail!("memory import conflicts with an existing record; no records were replaced")
            }
            None => {
                existing.push(record.clone());
                new_records += 1;
            }
        }
    }
    if existing.len() > super::MAX_RECORDS {
        bail!("memory import would exceed the ledger record bound");
    }
    // This is exactly the persisted UTF-8 JSONL, including every newline.
    let encoded = super::encode_records(&existing)?;
    if encoded.len() > super::MAX_LEDGER_BYTES {
        bail!("memory import would exceed the ledger byte bound");
    }
    Ok(Merge {
        encoded,
        new_records,
        already_present: incoming.len() - new_records,
        total_records: existing.len(),
    })
}

/// Validate an explicitly chosen bundle and preview its merge by default.
/// Apply rechecks under the ordinary writer lock and publishes one snapshot.
/// Stored provenance is preserved as untrusted source data, never authenticated
/// or relabeled as locally authored. No model is invoked.
pub fn import_current(global: bool, source: &Path, apply: bool) -> Result<String> {
    let envelope = read_bundle(source)?;
    let (root, scope_key, project) = match super::project::current_root(global, false)? {
        Some(root) => (root, None, true),
        None => (
            super::recall::state_root_for_read()?,
            super::current_scope_key(global)?,
            false,
        ),
    };
    let mut merged = merge_records(
        super::list_at(&root, scope_key.as_deref())?,
        &envelope.payload.records,
    )?;
    if apply && merged.new_records != 0 {
        let writable_root = if project {
            super::project::current_root(global, true)?
                .ok_or_else(|| anyhow::anyhow!("memory import destination changed"))?
        } else {
            crate::state_home()?
        };
        if writable_root != root || (!project && super::current_scope_key(global)? != scope_key) {
            bail!("memory import destination changed before apply");
        }
        super::prepare_parent(&root, scope_key.as_deref())?;
        let path = super::ledger_path(&root, scope_key.as_deref())?;
        let _lock = crate::lock_path(&path.with_extension("lock"))?;
        let current_project = super::project::current_root(global, false)?;
        let same_destination = if project {
            current_project.as_ref() == Some(&root)
        } else {
            current_project.is_none()
                && super::recall::state_root_for_read()? == root
                && super::current_scope_key(global)? == scope_key
        };
        if !same_destination {
            bail!("memory import destination changed while acquiring custody");
        }
        merged = merge_records(super::load_path(&path)?, &envelope.payload.records)?;
        if merged.new_records != 0 {
            crate::atomic_write(&path, &merged.encoded)?;
            let _ = crate::open_private_file(&path, false)?;
        }
    }
    Ok(serde_json::to_string(&serde_json::json!({
        "action": if apply { "apply" } else { "dry-run" },
        "scope": if project { "project" } else if global { "global" } else { "legacy" },
        "new_records": merged.new_records,
        "already_present": merged.already_present,
        "total_records": merged.total_records,
        "source_payload_sha256": envelope.payload_sha256,
        "caveat": "Imported record provenance is an untrusted source assertion, not verified truth, authenticated authorship, local authorship, or independent confirmation. A digest is not a signature. Dry-run writes nothing; apply may initialize custody even if a later write fails."
    }))?)
}

/// Export explicitly selected records from one validated snapshot. Additional
/// connected records require separate consent; incomplete evidence is refused.
/// The returned compact JSON has no trailing newline. Its byte bound reserves
/// that newline for CLI rendering. Digests provide integrity, not authenticity.
pub fn export_current(global: bool, ids: &[String], with_context: bool) -> Result<String> {
    if ids.is_empty() || ids.len() > MAX_SELECTED {
        bail!("memory export requires 1 through {MAX_SELECTED} selected IDs");
    }
    let mut selected = BTreeSet::new();
    for id in ids {
        validate_id(id)?;
        if !selected.insert(id.clone()) {
            bail!("memory export selected IDs must be unique");
        }
    }
    let records = list_current(global)?;
    if selected
        .iter()
        .any(|id| !records.iter().any(|record| &record.id == id))
    {
        bail!("memory export selection contains an ID absent from the selected store");
    }
    let included = connected_ids(&records, &selected);
    let context_ids: Vec<_> = included.difference(&selected).cloned().collect();
    if !context_ids.is_empty() && !with_context {
        bail!(
            "memory export requires {} additional connected records; review them locally and explicitly use --with-context to include the complete component. No bundle was emitted",
            context_ids.len()
        );
    }
    let mut records: Vec<_> = records
        .into_iter()
        .filter(|record| included.contains(&record.id))
        .collect();
    records.sort_by(|a, b| a.id.cmp(&b.id));
    let payload = serde_json::to_value(Payload {
        format: "azdaja-curated-memory".to_owned(),
        version: 1,
        selection: selected.into_iter().collect(),
        context_ids,
        records,
    })?;
    // Hash precisely the compact UTF-8 payload serialization also embedded in
    // the envelope. Consumers must preserve its emitted object-key order.
    let payload_bytes = serde_json::to_vec(&payload)?;
    let report = serde_json::json!({
        "payload": payload,
        "payload_sha256": crate::sha256_hex(&payload_bytes),
        "digest_encoding": "compact UTF-8 JSON payload, emitted object-key order, no trailing newline",
        "context_policy": "complete transitive incoming/outgoing relationship component",
        "caveat": "Explicitly exported manual notes are untrusted evidence, not verified truth or authenticated authorship. The digest is integrity only. Review every selected and context record before sharing. No import, synchronization, or publication was performed."
    });
    let encoded = serde_json::to_string(&report)?;
    if encoded.len() + 1 > MAX_EXPORT_BYTES {
        bail!("memory export exceeds the {MAX_EXPORT_BYTES}-byte output bound");
    }
    Ok(encoded)
}

#[cfg(all(test, any(unix, windows)))]
mod opened_entry_tests {
    use super::*;
    use std::path::PathBuf;
    use std::sync::atomic::{AtomicU64, Ordering};

    static NEXT: AtomicU64 = AtomicU64::new(0);

    struct Scratch(PathBuf);
    impl Drop for Scratch {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    #[test]
    fn changed_bundle_entry_is_refused_after_a_successful_regular_file_precheck() {
        let root = (0..1000)
            .find_map(|_| {
                let path = std::env::temp_dir().join(format!(
                    "az-import-handle-{}-{}",
                    std::process::id(),
                    NEXT.fetch_add(1, Ordering::Relaxed)
                ));
                match fs::create_dir(&path) {
                    Ok(()) => Some(Scratch(path)),
                    Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => None,
                    Err(error) => panic!("cannot create exclusive fixture: {error}"),
                }
            })
            .expect("exclusive fixture paths exhausted");
        let source = root.0.join("bundle");
        let victim = root.0.join("unrelated");
        fs::write(&source, b"approved source").unwrap();
        fs::write(&victim, b"unrelated private contents").unwrap();
        let mut original = Vec::new();
        open_bundle_entry(&source)
            .unwrap()
            .read_to_end(&mut original)
            .unwrap();
        assert_eq!(original, b"approved source");
        assert!(fs::symlink_metadata(&source).unwrap().is_file());
        // Deterministically replace the entry in the gap after the precheck.
        fs::remove_file(&source).unwrap();
        #[cfg(unix)]
        std::os::unix::fs::symlink(&victim, &source).unwrap();
        #[cfg(windows)]
        std::os::windows::fs::symlink_file(&victim, &source).unwrap();
        assert!(open_bundle_entry(&source).is_err());
        assert!(
            fs::symlink_metadata(&source)
                .unwrap()
                .file_type()
                .is_symlink()
        );
        assert_eq!(fs::read(&victim).unwrap(), b"unrelated private contents");
        fs::remove_file(&source).unwrap();
        fs::create_dir(&source).unwrap();
        assert!(open_bundle_entry(&source).is_err());
        fs::remove_dir(&source).unwrap();
        fs::write(&source, b"recovered source").unwrap();
        let mut recovered = Vec::new();
        open_bundle_entry(&source)
            .unwrap()
            .read_to_end(&mut recovered)
            .unwrap();
        assert_eq!(recovered, b"recovered source");
    }
}
