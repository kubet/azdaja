use std::{
    fs,
    path::{Path, PathBuf},
    process::Command,
    time::{SystemTime, UNIX_EPOCH},
};

fn root() -> PathBuf {
    static NEXT_ID: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let nonce = format!(
        "{nonce}-{}",
        NEXT_ID.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
    );
    std::env::temp_dir().join(format!(
        "azdaja-memory-recall-{}-{nonce}",
        std::process::id()
    ))
}

fn run(root: &Path, args: &[&str]) -> std::process::Output {
    Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args(args)
        .env("HOME", root)
        .env("XDG_CONFIG_HOME", root.join("config"))
        .env("XDG_STATE_HOME", root.join("state"))
        .env_remove("AZDAJA_HOME")
        .current_dir(root)
        .output()
        .expect("run azdaja")
}

fn add(root: &Path, kind: &str, text: &str) -> String {
    let output = run(root, &["memory", "add", kind, text]);
    assert!(
        output.status.success(),
        "add failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    output
        .stdout
        .split(|b| b.is_ascii_whitespace())
        .filter_map(|part| std::str::from_utf8(part).ok())
        .find(|part| {
            part.len() == 17
                && part.starts_with('m')
                && part[1..].chars().all(|c| c.is_ascii_hexdigit())
        })
        .expect("record id in add output")
        .to_owned()
}

fn add_linked(root: &Path, kind: &str, text: &str, link: &str) {
    let output = run(root, &["memory", "add", kind, text, "--link", link]);
    assert!(
        output.status.success(),
        "linked add failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
}

fn add_global(root: &Path, kind: &str, text: &str) {
    let output = run(root, &["memory", "add", kind, text, "--global"]);
    assert!(
        output.status.success(),
        "global add failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
}

fn recall(root: &Path, query: &str, global: bool) -> serde_json::Value {
    let mut args = vec!["memory", "recall", query];
    if global {
        args.push("--global");
    }
    let output = run(root, &args);
    assert!(
        output.status.success(),
        "recall failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).expect("recall JSON")
}

fn ledger_files(root: &Path) -> Vec<PathBuf> {
    let mut pending = vec![root.to_owned()];
    let mut found = Vec::new();
    while let Some(path) = pending.pop() {
        for entry in fs::read_dir(path).into_iter().flatten().flatten() {
            let path = entry.path();
            if path.is_dir() {
                pending.push(path);
            } else if path.file_name().is_some_and(|n| n == "global.jsonl") {
                found.push(path);
            }
        }
    }
    found
}

fn state_snapshot(root: &Path) -> Vec<(PathBuf, Vec<u8>)> {
    let mut pending = vec![root.to_owned()];
    let mut found = Vec::new();
    while let Some(path) = pending.pop() {
        for entry in fs::read_dir(path).into_iter().flatten().flatten() {
            let path = entry.path();
            if path.is_dir() {
                pending.push(path);
            } else if let Ok(bytes) = fs::read(&path) {
                found.push((path.strip_prefix(root).unwrap().to_owned(), bytes));
            }
        }
    }
    found.sort_by(|a, b| a.0.cmp(&b.0));
    found
}

#[test]
fn recall_is_fresh_process_bounded_and_read_only() {
    let root = root();
    fs::create_dir_all(&root).unwrap();
    add(&root, "decision", "alpha rollout chosen");
    add(&root, "observation", "alpha rollout observed");
    let before = ledger_files(&root)
        .into_iter()
        .map(|p| fs::read(p).unwrap())
        .collect::<Vec<_>>();
    let report = recall(&root, "alpha", false);
    assert_eq!(report["method"], "lexical");
    assert_eq!(report["scope"], "current");
    assert_eq!(report["total_matches"], 2);
    assert_eq!(report["omitted_matches"], 0);
    assert_eq!(report["matches"].as_array().unwrap().len(), 2);
    assert!(
        report["caveat"]
            .as_str()
            .unwrap()
            .contains("not verified truth")
    );
    let after = ledger_files(&root)
        .into_iter()
        .map(|p| fs::read(p).unwrap())
        .collect::<Vec<_>>();
    assert_eq!(before, after);
    fs::remove_dir_all(root).ok();
}

#[test]
fn recall_rejects_empty_and_oversized_queries_without_mutation() {
    let root = root();
    fs::create_dir_all(&root).unwrap();
    assert!(!run(&root, &["memory", "recall", "   "]).status.success());
    let oversized = (0..33)
        .map(|i| format!("term{i}"))
        .collect::<Vec<_>>()
        .join(" ");
    assert!(
        !run(&root, &["memory", "recall", &oversized])
            .status
            .success()
    );
    fs::remove_dir_all(root).ok();
}

#[test]
fn recall_reports_no_match_and_global_isolation() {
    let root = root();
    fs::create_dir_all(&root).unwrap();
    add(&root, "decision", "local-only wisdom");
    let none = recall(&root, "absent", false);
    assert_eq!(none["total_matches"], 0);
    assert!(none["matches"].as_array().unwrap().is_empty());
    let global = recall(&root, "local", true);
    assert_eq!(global["scope"], "global");
    assert_eq!(global["total_matches"], 0);
    fs::remove_dir_all(root).ok();
}

#[test]
fn recall_refuses_corrupt_ledger() {
    let root = root();
    fs::create_dir_all(&root).unwrap();
    add_global(&root, "decision", "corruption fixture");
    let files = ledger_files(&root);
    assert_eq!(files.len(), 1, "global ledger discovery");
    fs::write(&files[0], b"not-json\n").unwrap();
    assert!(
        !run(&root, &["memory", "recall", "anything", "--global"])
            .status
            .success()
    );
    fs::remove_dir_all(root).ok();
}

#[test]
fn recall_preserves_nonmatching_incoming_context() {
    let root = root();
    fs::create_dir_all(&root).unwrap();
    let id = add(&root, "decision", "deploy alpha");
    add_linked(
        &root,
        "disagreement",
        "contrary evidence",
        &format!("related-to:{id}"),
    );
    let report = recall(&root, "alpha", false);
    assert_eq!(report["matches"].as_array().unwrap().len(), 1);
    assert!(
        report["context"]
            .as_array()
            .unwrap()
            .iter()
            .any(|v| v["record"]["text"] == "contrary evidence")
    );
    fs::remove_dir_all(root).ok();
}

#[test]
fn recall_reports_primary_and_context_omissions_and_relationship_context() {
    let root = root();
    fs::create_dir_all(&root).unwrap();
    let anchor = add(&root, "decision", "shared anchor beacon");
    for index in 0..4 {
        add(&root, "decision", &format!("shared primary {index}"));
    }
    for index in 0..9 {
        add_linked(
            &root,
            "disagreement",
            &format!("contrary note {index}"),
            &format!("related-to:{anchor}"),
        );
    }
    add_linked(
        &root,
        "observation",
        "superseding evidence",
        &format!("supersedes:{anchor}"),
    );
    let before = state_snapshot(&root);
    let report = recall(&root, "shared beacon", false);
    assert_eq!(report["total_matches"], 5);
    assert_eq!(report["matches"].as_array().unwrap().len(), 4);
    assert_eq!(report["omitted_matches"], 1);
    assert_eq!(report["context"].as_array().unwrap().len(), 8);
    assert_eq!(report["omitted_context"], 2);
    let after = state_snapshot(&root);
    assert_eq!(before, after);
    fs::remove_dir_all(root).ok();
}

#[test]
fn recall_includes_supersedes_context_for_selected_primary() {
    let root = root();
    fs::create_dir_all(&root).unwrap();
    let anchor = add(&root, "decision", "unique anchor phrase");
    add_linked(
        &root,
        "observation",
        "superseding evidence",
        &format!("supersedes:{anchor}"),
    );
    let report = recall(&root, "unique anchor phrase", false);
    assert!(
        report["context"]
            .as_array()
            .unwrap()
            .iter()
            .any(|v| v["record"]["text"] == "superseding evidence")
    );
    fs::remove_dir_all(root).ok();
}

#[test]
fn invalid_recall_is_read_only_for_complete_isolated_state() {
    let root = root();
    fs::create_dir_all(&root).unwrap();
    add(&root, "decision", "invalid query fixture");
    let before = state_snapshot(&root);
    assert!(!run(&root, &["memory", "recall", "   "]).status.success());
    assert_eq!(before, state_snapshot(&root));
    fs::remove_dir_all(root).ok();
}
