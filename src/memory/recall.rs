//! Explicit, provider-free retrieval of curated notes, never a truth judgment.

use super::{MemoryKind, MemoryRecord, MemoryRelation, list_at};
use anyhow::{Result, bail};
use serde::Serialize;
use std::{
    collections::BTreeSet,
    env, fs,
    path::{Path, PathBuf},
};

const MAX_QUERY_CHARS: usize = 256;
const MAX_TERMS: usize = 32;
const MAX_MATCHES: usize = 4;
const MAX_CONTEXT: usize = 8;
const MAX_OUTPUT_BYTES: usize = 64 * 1024;
// Reserve room for the escaped query, keys, counters, caveat, and separators.
const ITEM_BUDGET_BYTES: usize = MAX_OUTPUT_BYTES - 4096;

#[derive(Debug, Clone, Serialize)]
pub struct RecallBacklink {
    pub relation: MemoryRelation,
    pub source_id: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct RecallItem {
    pub record: MemoryRecord,
    pub backlinks: Vec<RecallBacklink>,
}

#[derive(Debug, Clone, Serialize)]
pub struct MemoryRecallReport {
    pub schema_version: u32,
    pub method: &'static str,
    pub scope: &'static str,
    pub query: String,
    pub matches: Vec<RecallItem>,
    pub context: Vec<RecallItem>,
    pub total_matches: usize,
    /// Matching records absent from both returned arrays.
    pub omitted_matches: usize,
    /// One-hop context records absent from the returned context array.
    pub omitted_context: usize,
    pub caveat: &'static str,
}

pub fn recall_current(global: bool, query: &str) -> Result<MemoryRecallReport> {
    query_terms(query)?;
    if let Some(root) = super::project::current_root(global, false)? {
        let mut report = recall_at(&root, None, query)?;
        report.scope = "project";
        if serde_json::to_vec(&report)?.len() + 1 > MAX_OUTPUT_BYTES {
            bail!("project memory recall exceeds the output byte budget");
        }
        return Ok(report);
    }
    let root = state_root_for_read()?;
    let scope_key = if global {
        None
    } else {
        Some(crate::observability::scope_key_for_path(
            &env::current_dir()?.canonicalize()?,
        ))
    };
    let scope_key = scope_key.transpose()?;
    recall_at(&root, scope_key.as_deref(), query)
}

// `state_home` initializes runtime directories. Recall must honor the same
// documented path precedence without initializing or repairing any state.
// Existing-ledger CLI tests exercise parity with the ordinary write path.
pub(super) fn state_root_for_read() -> Result<PathBuf> {
    let home = env::var_os("HOME").map(PathBuf::from);
    #[cfg(windows)]
    let home = home.or_else(|| env::var_os("USERPROFILE").map(PathBuf::from));
    let root = resolve_state_root(
        env::var_os("AZDAJA_HOME").map(PathBuf::from),
        env::var_os("XDG_STATE_HOME").map(PathBuf::from),
        home,
    )?;
    match fs::symlink_metadata(&root) {
        Ok(metadata) => {
            if !metadata.is_dir() || metadata.file_type().is_symlink() {
                bail!("memory recall state root must be a real directory")
            }
            #[cfg(unix)]
            {
                use std::os::unix::fs::{MetadataExt, PermissionsExt};
                if metadata.uid() != unsafe { libc::geteuid() }
                    || metadata.permissions().mode() & 0o077 != 0
                {
                    bail!("memory recall state root must be private and owned by the current user")
                }
            }
            #[cfg(windows)]
            {
                use std::os::windows::fs::MetadataExt;
                if metadata.file_attributes() & 0x400 != 0 {
                    bail!("memory recall state root must not be a reparse point")
                }
            }
        }
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
        Err(error) => return Err(error.into()),
    }
    Ok(root)
}

fn resolve_state_root(
    explicit: Option<PathBuf>,
    xdg: Option<PathBuf>,
    home: Option<PathBuf>,
) -> Result<PathBuf> {
    if let Some(root) = explicit {
        if !root.is_absolute() {
            bail!("AZDAJA_HOME must be an absolute, nonempty path")
        }
        return Ok(root);
    }
    if let Some(root) = xdg.filter(|root| root.is_absolute()) {
        return Ok(root.join("azdaja"));
    }
    let Some(home) = home.filter(|home| home.is_absolute()) else {
        bail!("memory recall requires an absolute home or state path")
    };
    Ok(home.join(".local").join("state").join("azdaja"))
}

/// Recall from one validated ledger snapshot. No provider calls or writes.
///
/// Match distinct, case-insensitive Unicode alphanumeric words in text and tags.
/// Ties prefer newer notes, then ascending IDs. Incoming and outgoing one-hop
/// relationships remain inspectable without treating links as endorsements.
pub fn recall_at(root: &Path, scope_key: Option<&str>, query: &str) -> Result<MemoryRecallReport> {
    let terms = query_terms(query)?;
    let records = if ledger_present(root, scope_key)? {
        list_at(root, scope_key)?
    } else {
        Vec::new()
    };
    let mut ranked: Vec<_> = records
        .iter()
        .filter_map(|record| {
            let words = words(&format!("{} {}", record.text, record.tags.join(" ")));
            let score = words.intersection(&terms).count();
            (score > 0).then_some((score, record))
        })
        .collect();
    ranked.sort_by(|(score_a, a), (score_b, b)| {
        score_b
            .cmp(score_a)
            .then_with(|| b.created_unix.cmp(&a.created_unix))
            .then_with(|| a.id.cmp(&b.id))
    });

    let mut report = MemoryRecallReport {
        schema_version: 1,
        method: "lexical",
        scope: if scope_key.is_some() {
            "current"
        } else {
            "global"
        },
        query: query.to_owned(),
        matches: Vec::new(),
        context: Vec::new(),
        total_matches: ranked.len(),
        omitted_matches: 0,
        omitted_context: 0,
        caveat: "Manual notes and links are untrusted evidence, not verified truth, agent consensus, or semantic confidence. Context is one hop only.",
    };
    let mut remaining = ITEM_BUDGET_BYTES;
    for (_, record) in &ranked {
        if report.matches.len() == MAX_MATCHES {
            break;
        }
        let item = item_from_snapshot(record, &records);
        if reserve_item(&item, &mut remaining)? {
            report.matches.push(item);
        }
    }
    let selected: BTreeSet<_> = report
        .matches
        .iter()
        .map(|item| item.record.id.as_str())
        .collect();
    let outgoing: BTreeSet<_> = report
        .matches
        .iter()
        .flat_map(|item| item.record.links.iter().map(|link| link.target_id.as_str()))
        .collect();
    let mut context: Vec<_> = records
        .iter()
        .filter(|record| {
            !selected.contains(record.id.as_str())
                && (outgoing.contains(record.id.as_str())
                    || record
                        .links
                        .iter()
                        .any(|link| selected.contains(link.target_id.as_str())))
        })
        .collect();
    // Prefer contrary notes and incoming supersession when context is bounded.
    // This prioritizes inspection, not credibility, and never deletes history.
    let priority = |record: &MemoryRecord| {
        if record.kind == MemoryKind::Disagreement {
            0
        } else if record.links.iter().any(|link| {
            link.relation == MemoryRelation::Supersedes
                && selected.contains(link.target_id.as_str())
        }) {
            1
        } else {
            2
        }
    };
    context.sort_by(|a, b| {
        priority(a)
            .cmp(&priority(b))
            .then_with(|| b.created_unix.cmp(&a.created_unix))
            .then_with(|| a.id.cmp(&b.id))
    });
    let context_count = context.len();
    for record in context {
        if report.context.len() == MAX_CONTEXT {
            break;
        }
        let item = item_from_snapshot(record, &records);
        if reserve_item(&item, &mut remaining)? {
            report.context.push(item);
        }
    }
    report.omitted_context = context_count - report.context.len();
    let shown: BTreeSet<_> = report
        .matches
        .iter()
        .chain(&report.context)
        .map(|item| item.record.id.as_str())
        .collect();
    report.omitted_matches = ranked
        .iter()
        .filter(|(_, record)| !shown.contains(record.id.as_str()))
        .count();
    // Fail closed if a future schema change invalidates the reserved envelope.
    // Account for the CLI's trailing newline too.
    if serde_json::to_vec(&report)?.len() + 1 > MAX_OUTPUT_BYTES {
        bail!("memory recall output exceeds its byte envelope")
    }
    Ok(report)
}

// The ordinary list path can initialize storage directories. A missing ledger
// is an empty read, not a reason to initialize that infrastructure.
pub(super) fn ledger_present(root: &Path, scope_key: Option<&str>) -> Result<bool> {
    if scope_key.is_some_and(|scope| {
        scope.is_empty()
            || scope.len() > 128
            || !scope
                .bytes()
                .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-' || byte == b'_')
    }) {
        bail!("memory recall scope must be a bounded safe identifier")
    }
    let memory = root.join(super::MEMORY_DIR);
    let mut directories = vec![memory.clone()];
    let ledger = if let Some(scope) = scope_key {
        let scopes = memory.join(super::SCOPES_DIR);
        directories.push(scopes.clone());
        scopes.join(format!("{scope}.jsonl"))
    } else {
        memory.join(super::GLOBAL_LEDGER)
    };
    for directory in directories {
        match fs::symlink_metadata(directory) {
            Ok(metadata) if metadata.is_dir() && !metadata.file_type().is_symlink() => {
                #[cfg(unix)]
                {
                    use std::os::unix::fs::{MetadataExt, PermissionsExt};
                    if metadata.uid() != unsafe { libc::geteuid() }
                        || metadata.permissions().mode() & 0o077 != 0
                    {
                        bail!("memory ledger parent must be private and owned by the current user");
                    }
                }
                #[cfg(windows)]
                {
                    use std::os::windows::fs::MetadataExt;
                    if metadata.file_attributes() & 0x400 != 0 {
                        bail!("memory ledger parent must not be a reparse point");
                    }
                }
            }
            Ok(_) => bail!("memory recall ledger parent must be a real directory"),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false),
            Err(error) => return Err(error.into()),
        }
    }
    match fs::symlink_metadata(ledger) {
        Ok(_) => Ok(true), // Existing loader validates contents and file custody.
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(false),
        Err(error) => Err(error.into()),
    }
}

fn item_from_snapshot(record: &MemoryRecord, records: &[MemoryRecord]) -> RecallItem {
    let mut backlinks: Vec<_> = records
        .iter()
        .flat_map(|candidate| {
            candidate
                .links
                .iter()
                .filter(|link| link.target_id == record.id)
                .map(|link| RecallBacklink {
                    relation: link.relation,
                    source_id: candidate.id.clone(),
                })
        })
        .collect();
    backlinks.sort_by(|a, b| {
        a.source_id
            .cmp(&b.source_id)
            .then_with(|| a.relation.as_str().cmp(b.relation.as_str()))
    });
    RecallItem {
        record: record.clone(),
        backlinks,
    }
}

fn reserve_item(item: &RecallItem, remaining: &mut usize) -> Result<bool> {
    let bytes = serde_json::to_vec(item)?.len() + 1;
    if bytes > *remaining {
        return Ok(false);
    }
    *remaining -= bytes;
    Ok(true)
}

fn words(text: &str) -> BTreeSet<String> {
    text.split(|ch: char| !ch.is_alphanumeric())
        .filter(|word| !word.is_empty())
        .map(str::to_lowercase)
        .collect()
}

fn query_terms(query: &str) -> Result<BTreeSet<String>> {
    if query.chars().count() > MAX_QUERY_CHARS {
        bail!("memory recall query exceeds {MAX_QUERY_CHARS} characters")
    }
    let terms = words(query);
    if terms.is_empty() {
        bail!("memory recall query must contain at least one alphanumeric term")
    }
    if terms.len() > MAX_TERMS {
        bail!("memory recall query exceeds {MAX_TERMS} distinct terms")
    }
    Ok(terms)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn readonly_state_resolution_preserves_override_and_xdg_precedence() {
        let home = env::temp_dir().join("recall-home");
        let explicit = home.join("explicit");
        let xdg = home.join("xdg");
        assert_eq!(
            resolve_state_root(Some(explicit.clone()), Some(xdg.clone()), None).unwrap(),
            explicit
        );
        assert_eq!(
            resolve_state_root(None, Some(xdg.clone()), None).unwrap(),
            xdg.join("azdaja")
        );
        assert_eq!(
            resolve_state_root(None, Some(PathBuf::from("relative")), Some(home.clone())).unwrap(),
            home.join(".local/state/azdaja")
        );
        for root in [PathBuf::new(), PathBuf::from("relative")] {
            assert!(resolve_state_root(Some(root), Some(xdg.clone()), Some(home.clone())).is_err());
        }
        assert!(resolve_state_root(None, None, None).is_err());
    }

    #[test]
    fn query_is_unicode_case_insensitive_and_repetition_does_not_add_weight() {
        assert_eq!(
            query_terms("CACHE cache, ŽABA").unwrap(),
            words("cache žaba")
        );
        assert_eq!(query_terms("cache-cache").unwrap().len(), 1);
    }

    #[test]
    fn unsafe_scope_is_rejected_before_ledger_lookup() {
        let absent = env::temp_dir().join("az-recall-unsafe-scope-never-created");
        for scope in ["", "..", "../outside", "a/b", "a\\b", "C:outside"] {
            assert!(recall_at(&absent, Some(scope), "needle").is_err());
        }
    }

    #[test]
    fn query_bounds_reject_empty_punctuation_control_and_oversized_input() {
        for query in ["", "  ", "---?!", "\0\u{1b}"] {
            assert!(query_terms(query).is_err());
        }
        assert!(query_terms(&"é".repeat(256)).is_ok());
        assert!(query_terms(&"é".repeat(257)).is_err());
        let query = (0..33)
            .map(|i| format!("t{i}"))
            .collect::<Vec<_>>()
            .join(" ");
        assert!(query_terms(&query).is_err());
    }
}
