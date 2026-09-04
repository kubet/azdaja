use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
    process::Command,
    sync::atomic::{AtomicU64, Ordering},
    time::{SystemTime, UNIX_EPOCH},
};

static FIXTURE_SEQUENCE: AtomicU64 = AtomicU64::new(0);

fn fixture() -> (PathBuf, PathBuf, PathBuf, PathBuf, PathBuf) {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let sequence = FIXTURE_SEQUENCE.fetch_add(1, Ordering::Relaxed);
    let root = std::env::temp_dir().join(format!(
        "azdaja-memory-recall-review-{}-{nonce}-{sequence}",
        std::process::id()
    ));
    let home = root.join("home");
    let config = root.join("config");
    let state = root.join("state");
    let scope = root.join("scope");
    fs::create_dir_all(&home).unwrap();
    fs::create_dir_all(&config).unwrap();
    fs::create_dir_all(&scope).unwrap();
    (root, home, config, state, scope)
}

fn run(
    scope: &PathBuf,
    home: &PathBuf,
    config: &PathBuf,
    state: &PathBuf,
    args: &[String],
) -> std::process::Output {
    Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .current_dir(scope)
        .env("HOME", home)
        .env("XDG_CONFIG_HOME", config)
        .env("XDG_STATE_HOME", state)
        .env_remove("AZDAJA_HOME")
        .args(args)
        .output()
        .unwrap()
}

fn snapshot(path: &Path, root: &Path, out: &mut BTreeMap<String, Option<Vec<u8>>>) {
    if path.is_dir() {
        out.insert(path.strip_prefix(root).unwrap().display().to_string(), None);
        for entry in fs::read_dir(path).unwrap() {
            snapshot(&entry.unwrap().path(), root, out);
        }
    } else {
        out.insert(
            path.strip_prefix(root).unwrap().display().to_string(),
            Some(fs::read(path).unwrap()),
        );
    }
}

fn fixture_snapshot(root: &Path) -> BTreeMap<String, Option<Vec<u8>>> {
    let mut out = BTreeMap::new();
    snapshot(root, root, &mut out);
    out
}

#[test]
fn recall_bounds_long_unicode_records_and_reports_omissions() {
    let (root, home, config, state, scope) = fixture();
    let text = "needle ".to_owned() + &"界é🙂".repeat(900);
    let add = run(
        &scope,
        &home,
        &config,
        &state,
        &["memory".into(), "add".into(), "decision".into(), text],
    );
    assert!(
        add.status.success(),
        "{}",
        String::from_utf8_lossy(&add.stderr)
    );
    let seed = run(
        &scope,
        &home,
        &config,
        &state,
        &["memory".into(), "recall".into(), "needle".into()],
    );
    let seed_report: serde_json::Value = serde_json::from_slice(&seed.stdout).unwrap();
    let id = seed_report["matches"][0]["record"]["id"]
        .as_str()
        .unwrap()
        .to_owned();
    for index in 0..12 {
        let linked = run(
            &scope,
            &home,
            &config,
            &state,
            &[
                "memory".into(),
                "add".into(),
                "disagreement".into(),
                format!("contrary context {index}"),
                "--link".into(),
                format!("related-to:{id}"),
            ],
        );
        assert!(
            linked.status.success(),
            "{}",
            String::from_utf8_lossy(&linked.stderr)
        );
    }
    let recall = run(
        &scope,
        &home,
        &config,
        &state,
        &["memory".into(), "recall".into(), "needle".into()],
    );
    assert!(
        recall.status.success(),
        "{}",
        String::from_utf8_lossy(&recall.stderr)
    );
    let line = String::from_utf8(recall.stdout).unwrap();
    assert!(line.len() <= 64 * 1024, "{} bytes", line.len());
    let report: serde_json::Value = serde_json::from_str(line.trim()).unwrap();
    assert_eq!(report["method"], "lexical");
    assert!(
        report["caveat"]
            .as_str()
            .is_some_and(|value| value.contains("not verified truth"))
    );
    assert!(!report["matches"].as_array().unwrap().is_empty());
    assert!(report["matches"].as_array().unwrap().len() <= 4);
    assert!(report["context"].as_array().unwrap().len() <= 8);
    assert!(report["omitted_matches"].is_number());
    assert!(report["omitted_context"].as_u64().unwrap() > 0);
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn recall_missing_state_is_read_only_and_returns_empty_matches() {
    let (root, home, config, state, scope) = fixture();
    let before = fixture_snapshot(&root);
    let recall = run(
        &scope,
        &home,
        &config,
        &state,
        &["memory".into(), "recall".into(), "needle".into()],
    );
    assert!(
        recall.status.success(),
        "{}",
        String::from_utf8_lossy(&recall.stderr)
    );
    let report: serde_json::Value = serde_json::from_slice(&recall.stdout).unwrap();
    assert!(report["matches"].as_array().unwrap().is_empty());
    assert!(report["context"].as_array().unwrap().is_empty());
    assert_eq!(before, fixture_snapshot(&root));
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn recall_existing_store_without_lock_or_observability_is_read_only() {
    let (root, home, config, state, scope) = fixture();
    let add = run(
        &scope,
        &home,
        &config,
        &state,
        &[
            "memory".into(),
            "add".into(),
            "decision".into(),
            "missing-lock needle".into(),
        ],
    );
    assert!(
        add.status.success(),
        "{}",
        String::from_utf8_lossy(&add.stderr)
    );
    let state_files = fs::read_dir(&state)
        .unwrap()
        .map(|entry| entry.unwrap().path())
        .collect::<Vec<_>>();
    let mut lock = None;
    let mut observability = None;
    for path in state_files {
        if path.file_name().is_some_and(|name| name == ".lock") {
            lock = Some(path.clone());
        }
        if path.file_name().is_some_and(|name| name == "observability") && path.is_dir() {
            observability = Some(path);
        }
    }
    if let Some(path) = lock {
        fs::remove_file(path).unwrap();
    }
    if let Some(path) = observability {
        fs::remove_dir_all(path).unwrap();
    }
    let before = fixture_snapshot(&root);
    let recall = run(
        &scope,
        &home,
        &config,
        &state,
        &["memory".into(), "recall".into(), "needle".into()],
    );
    let after = fixture_snapshot(&root);
    assert_eq!(
        before, after,
        "recall mutated fixture after lock/observability removal"
    );
    if recall.status.success() {
        let report: serde_json::Value = serde_json::from_slice(&recall.stdout).unwrap();
        assert!(!report["matches"].as_array().unwrap().is_empty());
    } else {
        assert!(
            !recall.stderr.is_empty(),
            "safe refusal must explain the failure"
        );
    }
    fs::remove_dir_all(root).unwrap();
}
