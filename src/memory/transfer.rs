//! Explicit, read-only export. This is not synchronization or an import API.
use super::{MemoryRecord, list_current, validate_id};
use anyhow::{Result, bail};
use serde::Serialize;
use std::collections::BTreeSet;

const MAX_SELECTED: usize = 16;
const MAX_EXPORT_BYTES: usize = 1024 * 1024;

#[derive(Serialize)]
struct Payload {
    format: &'static str,
    version: u32,
    selection: Vec<String>,
    context_ids: Vec<String>,
    records: Vec<MemoryRecord>,
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
    let mut included = selected.clone();
    loop {
        let before = included.len();
        for record in &records {
            for link in &record.links {
                if included.contains(&record.id) || included.contains(&link.target_id) {
                    included.insert(record.id.clone());
                    included.insert(link.target_id.clone());
                }
            }
        }
        if included.len() == before {
            break;
        }
    }
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
        format: "azdaja-curated-memory",
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
