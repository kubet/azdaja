//! Acceptance contract for the proposed default-on, repo-local memory store.
//! These tests must fail until the product routes project memory into .azdaja.
use serde_json::Value;
use std::fs;
use std::io::Read;
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::thread;
use std::time::{Duration, Instant};

static NEXT: AtomicU64 = AtomicU64::new(0);

#[cfg(unix)]
#[test]
fn existing_invalid_project_ledger_entries_are_refused_without_exposure_or_repair() {
    use std::os::unix::fs::{PermissionsExt, symlink};
    for shape in ["symlink", "directory", "public-file"] {
        let f = Fixture::new();
        let added = f.run(
            "home-a",
            &f.repo(),
            false,
            &[
                "memory",
                "add",
                "hypothesis",
                "projectwisdom private fixture evidence",
            ],
        );
        assert!(added.status.success(), "fixture add failed: {:?}", added);
        let expected = f.recall("home-a", &f.repo(), false);
        let id = expected["matches"][0]["record"]["id"].as_str().unwrap();
        let ledger = f.repo().join(".azdaja/memory/global.jsonl");
        let original = fs::read(&ledger).unwrap();
        let victim = f.repo().join("victim.jsonl");
        fs::write(&victim, &original).unwrap();
        fs::set_permissions(&victim, fs::Permissions::from_mode(0o600)).unwrap();
        fs::remove_file(&ledger).unwrap();
        match shape {
            "symlink" => symlink(&victim, &ledger).unwrap(),
            "directory" => fs::create_dir(&ledger).unwrap(),
            "public-file" => {
                fs::write(&ledger, &original).unwrap();
                fs::set_permissions(&ledger, fs::Permissions::from_mode(0o644)).unwrap();
            }
            _ => unreachable!(),
        }
        for args in [
            vec!["memory", "list"],
            vec!["memory", "list", "--kind", "hypothesis"],
            vec!["memory", "show", id],
            vec!["memory", "recall", "projectwisdom"],
        ] {
            let output = f.run("home-b", &f.repo().join("src"), false, &args);
            assert_eq!(
                output.status.code(),
                Some(2),
                "{shape} {args:?}: {:?}",
                output
            );
            assert!(output.stdout.is_empty(), "{shape} exposed record output");
            assert!(
                !output.stderr.is_empty(),
                "{shape} lacked a refusal diagnostic"
            );
            assert!(!String::from_utf8_lossy(&output.stderr).contains("private fixture evidence"));
            assert_eq!(fs::read(&victim).unwrap(), original);
            let metadata = fs::symlink_metadata(&ledger).unwrap();
            match shape {
                "symlink" => {
                    assert!(metadata.file_type().is_symlink());
                    assert_eq!(fs::read_link(&ledger).unwrap(), victim);
                }
                "directory" => {
                    assert!(metadata.is_dir());
                    assert_eq!(fs::read_dir(&ledger).unwrap().count(), 0);
                }
                "public-file" => {
                    assert_eq!(metadata.permissions().mode() & 0o777, 0o644);
                    assert_eq!(fs::read(&ledger).unwrap(), original);
                }
                _ => unreachable!(),
            }
        }
        if shape == "directory" {
            fs::remove_dir(&ledger).unwrap();
        } else {
            fs::remove_file(&ledger).unwrap();
        }
        fs::write(&ledger, &original).unwrap();
        fs::set_permissions(&ledger, fs::Permissions::from_mode(0o600)).unwrap();
        assert_eq!(f.recall("home-b", &f.repo().join("src"), false), expected);
    }
}

#[test]
fn preexisting_empty_project_directories_are_not_initialized_by_read_commands() {
    for with_memory_dir in [false, true] {
        let f = Fixture::new();
        let root = f.repo().join(".azdaja");
        fs::create_dir(&root).unwrap();
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            fs::set_permissions(&root, fs::Permissions::from_mode(0o700)).unwrap();
        }
        fs::write(root.join("keep"), b"existing unrelated local bytes").unwrap();
        if with_memory_dir {
            fs::create_dir(root.join("memory")).unwrap();
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                fs::set_permissions(root.join("memory"), fs::Permissions::from_mode(0o700))
                    .unwrap();
            }
        }
        let before = snapshot(&root);
        for args in [
            vec!["memory", "list"],
            vec!["memory", "list", "--kind", "hypothesis"],
            vec!["memory", "recall", "projectwisdom"],
        ] {
            let output = f.run("home-a", &f.repo(), false, &args);
            assert!(output.status.success(), "read failed: {:?}", output);
            assert_eq!(snapshot(&root), before);
        }
        let output = f.run(
            "home-a",
            &f.repo(),
            false,
            &["memory", "show", "m0000000000000000"],
        );
        assert!(!output.status.success());
        assert!(output.stdout.is_empty());
        assert_eq!(snapshot(&root), before);
        assert!(!f.0.join("home-a/state").exists());
    }
}

#[test]
fn kind_filtered_list_and_show_use_the_project_store_across_homes() {
    let f = Fixture::new();
    for (kind, text) in [
        ("hypothesis", "projectwisdom primary hypothesis"),
        ("disagreement", "projectwisdom contrary evidence"),
    ] {
        let output = f.run("home-a", &f.repo(), false, &["memory", "add", kind, text]);
        assert!(output.status.success());
    }
    let filtered = f.run(
        "home-b",
        &f.repo().join("src"),
        false,
        &["memory", "list", "--kind", "hypothesis"],
    );
    assert!(
        filtered.status.success(),
        "filtered list failed: {:?}",
        filtered
    );
    let text = String::from_utf8(filtered.stdout).unwrap();
    assert!(text.contains("projectwisdom primary hypothesis"));
    assert!(!text.contains("projectwisdom contrary evidence"));
    let report = f.recall("home-b", &f.repo(), false);
    let record = report["matches"]
        .as_array()
        .unwrap()
        .iter()
        .find(|item| item["record"]["kind"] == "hypothesis")
        .unwrap();
    let id = record["record"]["id"].as_str().unwrap();
    let shown = f.run(
        "home-b",
        &f.repo().join("src"),
        false,
        &["memory", "show", id],
    );
    assert!(shown.status.success(), "project show failed: {:?}", shown);
    assert!(String::from_utf8_lossy(&shown.stdout).contains("projectwisdom primary hypothesis"));
    assert!(!f.0.join("home-b/state").exists());
}

#[test]
#[ignore = "explicit preparation of frozen Luna pilot inputs, not an inference-quality test"]
fn emit_luna_handoff_pilot_receipts() {
    let f = Fixture::new();
    for (query, kind, text, contrary) in [
        (
            "corruptrecord",
            "observation",
            "corruptrecord: The focused regression is cargo +1.95.0 test --locked --release --test memory_recall_reliability global_parseable_invalid_record_shapes_are_refused_without_rewriting_history -- --exact. A clean malformed-record CLI refusal uses exit code 2, not 1. Verify the current case before relying on this note.",
            "A panic or signal is not ordinary refusal. Check empty stdout, unchanged damaged-ledger bytes and successful recovery after valid bytes are restored. Notes alone do not prove these properties.",
        ),
        (
            "recallbound",
            "hypothesis",
            "recallbound: An earlier review claimed memory recall has no output-byte bound and only limits record counts.",
            "That earlier claim was contradicted by MAX_OUTPUT_BYTES = 64 * 1024 and a serialized report-size check. Verify current source and cargo +1.95.0 test --locked --release --test memory_recall_review. Long Unicode and linked context belong in the check. This does not prove agent usefulness.",
        ),
    ] {
        let add = f.run("home-a", &f.repo(), false, &["memory", "add", kind, text]);
        assert!(add.status.success(), "pilot seed failed: {:?}", add);
        let lookup = f.run("home-a", &f.repo(), false, &["memory", "recall", query]);
        assert!(lookup.status.success());
        let selected: Value = serde_json::from_slice(&lookup.stdout).unwrap();
        assert_eq!(selected["total_matches"], 1);
        let link = format!(
            "related-to:{}",
            selected["matches"][0]["record"]["id"].as_str().unwrap()
        );
        let add = f.run(
            "home-a",
            &f.repo(),
            false,
            &["memory", "add", "disagreement", contrary, "--link", &link],
        );
        assert!(add.status.success());
        let receipt = f.run(
            "home-b",
            &f.repo().join("src"),
            false,
            &["memory", "recall", query],
        );
        assert!(receipt.status.success());
        assert!(receipt.stdout.len() <= 64 * 1024);
        let report: Value = serde_json::from_slice(&receipt.stdout).unwrap();
        assert_eq!(report["scope"], "project");
        assert_eq!(report["total_matches"], 1);
        assert_eq!(report["context"].as_array().unwrap().len(), 1);
        assert_eq!(report["context"][0]["record"]["kind"], "disagreement");
        eprintln!(
            "LUNA_PILOT_RECEIPT {query} {}",
            serde_json::to_string(&report).unwrap()
        );
    }
}

#[test]
fn authoritative_home_and_explicit_modes_have_consistent_precedence() {
    let f = Fixture::new();
    let authoritative = f.0.join("authoritative");
    let run = |mode: Option<&str>, args: &[&str]| {
        let mut command = f.command("home-a", &f.repo(), mode, args);
        command.env("AZDAJA_HOME", &authoritative);
        finish(command)
    };
    let legacy = run(
        None,
        &[
            "memory",
            "add",
            "decision",
            "projectwisdom authoritative legacy",
        ],
    );
    assert!(
        legacy.status.success(),
        "authoritative add failed: {:?}",
        legacy
    );
    assert!(!f.repo().join(".azdaja").exists());
    let original = snapshot(&authoritative);
    assert!(!original.is_empty());
    let local = run(
        Some("on"),
        &[
            "memory",
            "add",
            "observation",
            "projectwisdom explicit local",
        ],
    );
    assert!(
        local.status.success(),
        "explicit project add failed: {:?}",
        local
    );
    assert!(f.repo().join(".azdaja").is_dir());
    assert_eq!(snapshot(&authoritative), original);
    let query = ["memory", "recall", "projectwisdom"];
    for (mode, text) in [
        (None, "projectwisdom authoritative legacy"),
        (Some("legacy"), "projectwisdom authoritative legacy"),
        (Some("on"), "projectwisdom explicit local"),
    ] {
        let output = run(mode, &query);
        assert!(output.status.success());
        let report: Value = serde_json::from_slice(&output.stdout).unwrap();
        assert_eq!(report["total_matches"], 1);
        assert_eq!(report["matches"][0]["record"]["text"], text);
    }
    let project_before = snapshot(&f.repo().join(".azdaja"));
    for mode in ["off", "typo", ""] {
        let output = run(
            Some(mode),
            &[
                "memory",
                "add",
                "observation",
                "projectwisdom must not be written",
            ],
        );
        assert!(!output.status.success());
        assert!(output.stdout.is_empty());
        assert_eq!(snapshot(&authoritative), original);
        assert_eq!(snapshot(&f.repo().join(".azdaja")), project_before);
    }
    let global = run(
        Some("off"),
        &[
            "memory",
            "add",
            "observation",
            "projectwisdom personal global",
            "--global",
        ],
    );
    assert!(global.status.success());
    let after_global = snapshot(&authoritative);
    for mode in [None, Some("on"), Some("off"), Some("legacy"), Some("typo")] {
        let output = run(mode, &["memory", "recall", "projectwisdom", "--global"]);
        assert!(output.status.success());
        let report: Value = serde_json::from_slice(&output.stdout).unwrap();
        assert_eq!(report["scope"], "global");
        assert_eq!(report["total_matches"], 1);
        assert_eq!(
            report["matches"][0]["record"]["text"],
            "projectwisdom personal global"
        );
    }
    assert_eq!(snapshot(&authoritative), after_global);
    assert_eq!(snapshot(&f.repo().join(".azdaja")), project_before);
}

#[test]
fn invalid_authoritative_home_and_forced_project_outside_git_fail_without_fallback() {
    let f = Fixture::new();
    for value in ["", "relative-state"] {
        let mut command = f.command(
            "home-a",
            &f.repo(),
            None,
            &["memory", "recall", "projectwisdom"],
        );
        command.env("AZDAJA_HOME", value);
        let output = finish(command);
        assert!(
            !output.status.success(),
            "invalid authoritative root was silently ignored: {:?}",
            output
        );
        assert!(output.stdout.is_empty());
        assert!(!f.repo().join(".azdaja").exists());
        assert!(!f.repo().join("relative-state").exists());
        assert!(!f.0.join("home-a/state").exists());
    }
    let output = f.run_mode(
        "home-a",
        &f.0.join("outside"),
        Some("on"),
        &["memory", "add", "observation", "projectwisdom refused"],
    );
    assert!(!output.status.success());
    assert!(output.stdout.is_empty());
    assert!(String::from_utf8_lossy(&output.stderr).contains("Git worktree"));
    assert!(!f.0.join("outside/.azdaja").exists());
    assert!(!f.0.join("home-a/state").exists());
}

fn snapshot(root: &Path) -> std::collections::BTreeMap<PathBuf, Vec<u8>> {
    fn walk(root: &Path, path: &Path, result: &mut std::collections::BTreeMap<PathBuf, Vec<u8>>) {
        if !path.exists() {
            return;
        }
        for entry in fs::read_dir(path).unwrap() {
            let entry = entry.unwrap();
            let path = entry.path();
            assert!(!entry.file_type().unwrap().is_symlink());
            let key = path.strip_prefix(root).unwrap().to_owned();
            if entry.file_type().unwrap().is_dir() {
                result.insert(key, Vec::new());
                walk(root, &path, result);
            } else {
                result.insert(key, fs::read(path).unwrap());
            }
        }
    }
    let mut result = std::collections::BTreeMap::new();
    walk(root, root, &mut result);
    result
}

#[test]
fn legacy_memory_is_explicitly_accessible_not_silently_merged_or_migrated() {
    let f = Fixture::new();
    let seed = f.run_mode(
        "home-a",
        &f.repo(),
        Some("legacy"),
        &["memory", "add", "decision", "projectwisdom legacy evidence"],
    );
    assert!(seed.status.success(), "legacy seed failed: {:?}", seed);
    let args = ["memory", "recall", "projectwisdom"];
    let legacy = f.run_mode("home-a", &f.repo(), Some("legacy"), &args);
    assert!(legacy.status.success());
    let original: Value = serde_json::from_slice(&legacy.stdout).unwrap();
    assert_eq!(original["total_matches"], 1);
    let state = f.0.join("home-a/state");
    let before = snapshot(&state);
    assert!(!before.is_empty());
    let project = f.run("home-a", &f.repo(), false, &args);
    assert!(
        project.status.success(),
        "project recall failed: {:?}",
        project
    );
    let empty: Value = serde_json::from_slice(&project.stdout).unwrap();
    assert_eq!(empty["scope"], "project");
    assert_eq!(empty["total_matches"], 0);
    assert!(String::from_utf8_lossy(&project.stderr).contains("AZDAJA_PROJECT_MEMORY=legacy"));
    assert!(!f.repo().join(".azdaja").exists());
    assert_eq!(snapshot(&state), before);
    let new = f.run(
        "home-a",
        &f.repo(),
        false,
        &[
            "memory",
            "add",
            "observation",
            "projectwisdom new local evidence",
        ],
    );
    assert!(new.status.success());
    let local = f.recall("home-a", &f.repo(), false);
    assert_eq!(local["total_matches"], 1);
    assert_eq!(
        local["matches"][0]["record"]["text"],
        "projectwisdom new local evidence"
    );
    assert_eq!(
        snapshot(&state),
        before,
        "project writes must not modify old personal state"
    );
    let recovered = f.run_mode("home-a", &f.repo(), Some("legacy"), &args);
    assert!(recovered.status.success());
    assert_eq!(
        serde_json::from_slice::<Value>(&recovered.stdout).unwrap(),
        original
    );
    assert_eq!(snapshot(&state), before);
}

#[test]
fn explicit_global_memory_remains_separate_when_project_memory_is_off() {
    let f = Fixture::new();
    let output = f.run(
        "home-a",
        &f.repo(),
        true,
        &[
            "memory",
            "add",
            "observation",
            "projectwisdom personal global",
            "--global",
        ],
    );
    assert!(
        output.status.success(),
        "explicit global add failed: {:?}",
        output
    );
    assert!(!f.repo().join(".azdaja").exists());
    let output = f.run(
        "home-a",
        &f.repo(),
        true,
        &["memory", "recall", "projectwisdom", "--global"],
    );
    assert!(output.status.success());
    let report: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(report["scope"], "global");
    assert_eq!(report["total_matches"], 1);
    assert_eq!(f.recall("home-a", &f.repo(), false)["total_matches"], 0);
    assert!(!f.repo().join(".azdaja").exists());
}

#[test]
fn empty_project_recall_is_read_only_and_reports_project_scope() {
    let f = Fixture::new();
    let report = f.recall("home-a", &f.repo().join("src"), false);
    assert_eq!(report["scope"], "project");
    assert_eq!(report["total_matches"], 0);
    let listed = f.run("home-a", &f.repo(), false, &["memory", "list"]);
    assert!(listed.status.success());
    let missing = f.run(
        "home-a",
        &f.repo(),
        false,
        &["memory", "show", "m0000000000000000"],
    );
    assert!(!missing.status.success());
    assert!(missing.stdout.is_empty());
    assert!(!f.repo().join(".azdaja").exists());
    assert!(!f.0.join("home-a/state").exists());
}

#[test]
fn corrupt_project_ledger_is_refused_without_rewriting_or_personal_fallback() {
    let f = Fixture::new();
    let add = f.run(
        "home-a",
        &f.repo(),
        false,
        &["memory", "add", "observation", "projectwisdom original"],
    );
    assert!(add.status.success());
    let ledger = f.repo().join(".azdaja/memory/global.jsonl");
    let original = fs::read(&ledger).unwrap();
    fs::write(&ledger, b"{bad-json}\n").unwrap();
    let before = snapshot(&f.repo().join(".azdaja"));
    for args in [
        vec!["memory", "recall", "projectwisdom"],
        vec!["memory", "list"],
    ] {
        let output = f.run("home-b", &f.repo().join("src"), false, &args);
        assert!(!output.status.success());
        assert!(output.stdout.is_empty());
        assert!(!output.stderr.is_empty());
        assert_eq!(snapshot(&f.repo().join(".azdaja")), before);
        assert!(!f.0.join("home-b/state").exists());
    }
    fs::write(&ledger, original).unwrap();
    assert_eq!(f.recall("home-b", &f.repo(), false)["total_matches"], 1);
}

#[test]
fn project_notes_keep_file_tags_after_repository_relocation_and_stay_git_ignored() {
    let f = Fixture::new();
    let output = f.run(
        "home-a",
        &f.repo(),
        false,
        &[
            "memory",
            "add",
            "decision",
            "projectwisdom spans implementation and tests",
            "--tag",
            "file:src/cache.rs",
            "--tag",
            "file:tests/cache.rs",
        ],
    );
    assert!(output.status.success(), "tagged add failed: {:?}", output);
    let before = f.recall("home-a", &f.repo(), false);
    assert_eq!(
        before["matches"][0]["record"]["tags"],
        serde_json::json!(["file:src/cache.rs", "file:tests/cache.rs"])
    );
    let mut git = Command::new("git");
    git.current_dir(f.repo())
        .args(["status", "--porcelain", "--untracked-files=all"]);
    let status = finish(git);
    assert!(status.status.success());
    assert!(
        status.stdout.is_empty(),
        "private memory leaked into ordinary Git status: {:?}",
        status
    );
    let moved = f.0.join("relocated");
    fs::rename(f.repo(), &moved).unwrap();
    let after = f.recall("home-b", &moved.join("src"), false);
    assert_eq!(
        before, after,
        "repo-local recall must not depend on absolute checkout path or HOME"
    );
}

#[test]
fn concurrent_first_use_keeps_every_acknowledged_project_note() {
    use std::sync::atomic::AtomicBool;
    use std::sync::mpsc;
    let f = Fixture::new();
    let release = AtomicBool::new(false);
    let (ready_tx, ready_rx) = mpsc::channel();
    thread::scope(|scope| {
        let handles = (0..12)
            .map(|index| {
                let ready = ready_tx.clone();
                let f = &f;
                let release = &release;
                scope.spawn(move || {
                    ready.send(()).unwrap();
                    let deadline = Instant::now() + Duration::from_secs(15);
                    while !release.load(Ordering::Acquire) {
                        assert!(
                            Instant::now() < deadline,
                            "project writer start gate timed out"
                        );
                        thread::sleep(Duration::from_millis(1));
                    }
                    let text = format!("projectwisdom concurrent note {index}");
                    f.run(
                        "home-a",
                        &f.repo(),
                        false,
                        &["memory", "add", "observation", &text],
                    )
                })
            })
            .collect::<Vec<_>>();
        for _ in 0..12 {
            ready_rx.recv_timeout(Duration::from_secs(15)).unwrap();
        }
        release.store(true, Ordering::Release);
        for handle in handles {
            let output = handle.join().unwrap();
            assert!(
                output.status.success(),
                "cold project writer failed: {:?}",
                output
            );
        }
    });
    let output = f.run("home-b", &f.repo().join("src"), false, &["memory", "list"]);
    assert!(
        output.status.success(),
        "cross-home list failed: {:?}",
        output
    );
    let report = f.recall("home-b", &f.repo(), false);
    assert_eq!(report["total_matches"], 12);
    assert_eq!(report["omitted_matches"], 8);
    let mut ids = std::collections::BTreeSet::new();
    for index in 0..12 {
        let query = index.to_string();
        let output = f.run(
            "home-b",
            &f.repo().join("src"),
            false,
            &["memory", "recall", &query],
        );
        assert!(output.status.success());
        let found: Value = serde_json::from_slice(&output.stdout).unwrap();
        assert_eq!(found["total_matches"], 1);
        assert_eq!(
            found["matches"][0]["record"]["text"],
            format!("projectwisdom concurrent note {index}")
        );
        assert!(
            ids.insert(
                found["matches"][0]["record"]["id"]
                    .as_str()
                    .unwrap()
                    .to_owned()
            )
        );
    }
    assert_eq!(
        fs::read(f.repo().join(".azdaja/.gitignore")).unwrap(),
        b"*\n"
    );
    assert!(
        !fs::read_dir(f.repo().join(".azdaja"))
            .unwrap()
            .any(|entry| entry
                .unwrap()
                .file_name()
                .to_string_lossy()
                .starts_with(".ignore-init-"))
    );
}

#[cfg(unix)]
#[test]
fn unsafe_project_directory_is_refused_without_permission_repair() {
    use std::os::unix::fs::PermissionsExt;
    let f = Fixture::new();
    let store = f.repo().join(".azdaja");
    fs::create_dir(&store).unwrap();
    fs::set_permissions(&store, fs::Permissions::from_mode(0o755)).unwrap();
    let output = f.run(
        "home-a",
        &f.repo(),
        false,
        &["memory", "add", "observation", "projectwisdom refused"],
    );
    assert!(!output.status.success());
    assert!(output.stdout.is_empty());
    assert_eq!(
        fs::metadata(&store).unwrap().permissions().mode() & 0o777,
        0o755
    );
    assert_eq!(fs::read_dir(store).unwrap().count(), 0);
}

#[cfg(unix)]
#[test]
fn symlinked_project_store_is_refused_without_touching_the_target() {
    let f = Fixture::new();
    let victim = f.0.join("outside");
    fs::write(victim.join("keep"), b"private original bytes").unwrap();
    std::os::unix::fs::symlink(&victim, f.repo().join(".azdaja")).unwrap();
    let output = f.run(
        "home-a",
        &f.repo(),
        false,
        &["memory", "add", "observation", "projectwisdom refused"],
    );
    assert!(!output.status.success());
    assert!(output.stdout.is_empty());
    assert_eq!(
        fs::read(victim.join("keep")).unwrap(),
        b"private original bytes"
    );
    assert_eq!(fs::read_dir(victim).unwrap().count(), 1);
}

struct Fixture(PathBuf);
impl Fixture {
    fn new() -> Self {
        let base = std::env::temp_dir();
        let path = loop {
            let candidate = base.join(format!(
                "az-project-memory-{}-{}",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            match fs::create_dir(&candidate) {
                Ok(()) => break candidate,
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
                Err(error) => panic!("cannot create exclusive fixture: {error}"),
            }
        };
        let fixture = Self(path);
        for name in ["repo", "repo/src", "home-a", "home-b", "outside"] {
            fs::create_dir_all(fixture.0.join(name)).unwrap();
        }
        let mut git = Command::new("git");
        git.args(["init", "--quiet"]).arg(fixture.repo());
        let output = finish(git);
        assert!(
            output.status.success(),
            "private git init failed: {:?}",
            output
        );
        fixture
    }

    fn repo(&self) -> PathBuf {
        self.0.join("repo")
    }

    fn run(&self, home: &str, cwd: &Path, disabled: bool, args: &[&str]) -> Output {
        self.run_mode(home, cwd, if disabled { Some("off") } else { None }, args)
    }

    fn run_mode(&self, home: &str, cwd: &Path, mode: Option<&str>, args: &[&str]) -> Output {
        finish(self.command(home, cwd, mode, args))
    }

    fn command(&self, home: &str, cwd: &Path, mode: Option<&str>, args: &[&str]) -> Command {
        let home = self.0.join(home);
        let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
        command
            .current_dir(cwd)
            .args(args)
            .env("HOME", &home)
            .env("USERPROFILE", &home)
            .env("XDG_CONFIG_HOME", home.join("config"))
            .env("XDG_STATE_HOME", home.join("state"))
            .env_remove("AZDAJA_HOME")
            .env_remove("AZDAJA_PROJECT_MEMORY");
        if let Some(mode) = mode {
            command.env("AZDAJA_PROJECT_MEMORY", mode);
        }
        command
    }

    fn recall(&self, home: &str, cwd: &Path, global: bool) -> Value {
        let mut args = vec!["memory", "recall", "projectwisdom"];
        if global {
            args.push("--global");
        }
        let output = self.run(home, cwd, false, &args);
        assert!(output.status.success(), "recall failed: {:?}", output);
        assert!(output.stdout.len() <= 64 * 1024);
        serde_json::from_slice(&output.stdout).unwrap()
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn finish(mut command: Command) -> Output {
    let mut child = command
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    let stdout = child.stdout.take().unwrap();
    let stderr = child.stderr.take().unwrap();
    fn drain(mut stream: impl Read) -> Vec<u8> {
        let mut bytes = Vec::new();
        stream
            .by_ref()
            .take(2 * 1024 * 1024)
            .read_to_end(&mut bytes)
            .unwrap();
        std::io::copy(&mut stream, &mut std::io::sink()).unwrap();
        bytes
    }
    let out = thread::spawn(move || drain(stdout));
    let err = thread::spawn(move || drain(stderr));
    let deadline = Instant::now() + Duration::from_secs(15);
    let mut expired = false;
    let status = loop {
        if let Some(status) = child.try_wait().unwrap() {
            break status;
        }
        if Instant::now() >= deadline {
            expired = true;
            let _ = child.kill();
            break child.wait().unwrap();
        }
        thread::sleep(Duration::from_millis(5));
    };
    let output = Output {
        status,
        stdout: out.join().unwrap(),
        stderr: err.join().unwrap(),
    };
    assert!(!expired, "CLI exceeded fixture deadline: {:?}", output);
    output
}

#[test]
fn repo_local_handoff_crosses_homes_and_subdirectories_without_global_leakage() {
    let f = Fixture::new();
    let output = f.run(
        "home-a",
        &f.repo(),
        false,
        &[
            "memory",
            "add",
            "hypothesis",
            "projectwisdom: test a bounded cache before adopting it",
        ],
    );
    assert!(output.status.success(), "add failed: {:?}", output);
    assert!(
        f.repo().join(".azdaja").is_dir(),
        "default project memory must be repo-local, not only in one user's state directory"
    );
    let first = f.recall("home-a", &f.repo(), false);
    let id = first["matches"][0]["record"]["id"].as_str().unwrap();
    let link = format!("related-to:{id}");
    let output = f.run(
        "home-a",
        &f.repo(),
        false,
        &[
            "memory",
            "add",
            "disagreement",
            "The experiment used more memory. Benchmark before choosing this design.",
            "--link",
            &link,
        ],
    );
    assert!(output.status.success(), "linked add failed: {:?}", output);
    let second = f.recall("home-b", &f.repo().join("src"), false);
    assert_eq!(second["total_matches"], 1);
    assert_eq!(
        second["matches"][0]["record"],
        first["matches"][0]["record"]
    );
    assert!(second["context"].as_array().unwrap().iter().any(|item| {
        item["record"]["kind"] == "disagreement"
            && item["record"]["links"]
                .as_array()
                .unwrap()
                .iter()
                .any(|link| link["target_id"] == id)
    }));
    assert_eq!(f.recall("home-b", &f.repo(), true)["total_matches"], 0);
    assert_eq!(
        f.recall("home-a", &f.0.join("outside"), false)["total_matches"],
        0
    );
}

#[test]
fn explicit_project_memory_off_does_not_create_a_project_store() {
    let f = Fixture::new();
    let output = f.run(
        "home-a",
        &f.repo(),
        true,
        &[
            "memory",
            "add",
            "observation",
            "projectwisdom must not be recorded while disabled",
        ],
    );
    assert!(
        !output.status.success(),
        "disabled project memory unexpectedly accepted a write"
    );
    assert!(output.stdout.is_empty());
    assert!(String::from_utf8_lossy(&output.stderr).contains("disabled"));
    assert!(!f.repo().join(".azdaja").exists());
    assert!(
        !f.0.join("home-a/state").exists(),
        "disabled project memory must not silently redirect the write into personal state"
    );
}
