//! Real Git worktree/clone acceptance. Unix process-group cleanup and provider
//! tripwires are intentional here; this target does not claim Windows runtime proof.
#![cfg(unix)]

use serde_json::Value;
use std::collections::BTreeMap;
use std::fs;
use std::io::Read;
use std::os::unix::fs::PermissionsExt;
use std::os::unix::process::CommandExt;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Output, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant};

static NEXT: AtomicU64 = AtomicU64::new(0);

struct Fixture {
    root: PathBuf,
    path: std::ffi::OsString,
}

struct Running(Option<Child>);
impl Drop for Running {
    fn drop(&mut self) {
        if let Some(mut child) = self.0.take() {
            if let Ok(pid) = libc::pid_t::try_from(child.id())
                && pid > 0
            {
                // The child creates its own process group and has not been reaped.
                unsafe {
                    libc::kill(-pid, libc::SIGKILL);
                }
            }
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

impl Fixture {
    fn new() -> Self {
        let root = loop {
            let sequence = NEXT.fetch_add(1, Ordering::Relaxed);
            let candidate =
                std::env::temp_dir().join(format!("az-wt-{}-{sequence}", std::process::id()));
            match fs::create_dir(&candidate) {
                Ok(()) => break candidate,
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
                Err(error) => panic!("cannot create exclusive fixture: {error}"),
            }
        };
        for directory in ["home-a", "home-b", "guard", "empty-hooks", "repo"] {
            fs::create_dir(root.join(directory)).unwrap();
        }
        fs::write(root.join("gitconfig"), b"").unwrap();
        for provider in ["jcode", "claude", "codex", "gemini", "opencode"] {
            let executable = root.join("guard").join(provider);
            fs::write(&executable, b"#!/bin/sh\nprintf 'unexpected provider\n' >> \"$AZ_TEST_PROVIDER_MARKER\"\nexit 93\n").unwrap();
            fs::set_permissions(executable, fs::Permissions::from_mode(0o755)).unwrap();
        }
        let mut paths = vec![root.join("guard")];
        paths.extend(std::env::split_paths(
            &std::env::var_os("PATH").expect("Git requires PATH"),
        ));
        Self {
            root,
            path: std::env::join_paths(paths).unwrap(),
        }
    }

    fn output(&self, program: &str, home: &str, cwd: &Path, args: &[&str]) -> Output {
        let sequence = NEXT.fetch_add(1, Ordering::Relaxed);
        let stdout_path = self.root.join(format!("stdout-{sequence}"));
        let stderr_path = self.root.join(format!("stderr-{sequence}"));
        let mut command = Command::new(program);
        for (key, _) in std::env::vars_os() {
            if ["AZDAJA_", "JCODE_", "GIT_", "RLM_"]
                .iter()
                .any(|prefix| key.to_string_lossy().starts_with(prefix))
            {
                command.env_remove(key);
            }
        }
        let home = self.root.join(home);
        command
            .args(args)
            .current_dir(cwd)
            .env("HOME", &home)
            .env("USERPROFILE", &home)
            .env("XDG_CONFIG_HOME", home.join("config"))
            .env("XDG_STATE_HOME", home.join("state"))
            .env("PATH", &self.path)
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .env("GIT_CONFIG_GLOBAL", self.root.join("gitconfig"))
            .env("GIT_TERMINAL_PROMPT", "0")
            .env("AZ_TEST_PROVIDER_MARKER", self.root.join("provider-called"))
            .stdin(Stdio::null())
            .stdout(fs::File::create(&stdout_path).unwrap())
            .stderr(fs::File::create(&stderr_path).unwrap())
            .process_group(0);
        let deadline = Instant::now() + Duration::from_secs(15);
        let mut running =
            Running(Some(command.spawn().unwrap_or_else(|error| {
                panic!("cannot spawn {program} {args:?}: {error}")
            })));
        let status = loop {
            if let Some(status) = running.0.as_mut().unwrap().try_wait().unwrap() {
                running.0.take();
                break status;
            }
            assert!(
                Instant::now() < deadline,
                "{program} {args:?} exceeded fixture deadline"
            );
            std::thread::sleep(Duration::from_millis(5));
        };
        let capture = |path: &Path| {
            let mut bytes = Vec::new();
            fs::File::open(path)
                .unwrap()
                .take(64 * 1024 + 1)
                .read_to_end(&mut bytes)
                .unwrap();
            assert!(
                bytes.len() <= 64 * 1024,
                "fixture command output exceeded 64 KiB"
            );
            bytes
        };
        let output = Output {
            status,
            stdout: capture(&stdout_path),
            stderr: capture(&stderr_path),
        };
        assert!(
            !self.root.join("provider-called").exists(),
            "memory workflow invoked a provider"
        );
        output
    }

    fn run(&self, program: &str, home: &str, cwd: &Path, args: &[&str]) -> Output {
        let output = self.output(program, home, cwd, args);
        assert!(
            output.status.success(),
            "{program} {args:?}: {}",
            String::from_utf8_lossy(&output.stderr)
        );
        output
    }

    fn git(&self, cwd: &Path, args: &[&str]) -> Output {
        let hooks = format!("core.hooksPath={}", self.root.join("empty-hooks").display());
        let mut configured = vec![
            "-c",
            &hooks,
            "-c",
            "commit.gpgsign=false",
            "-c",
            "user.name=Memory Fixture",
            "-c",
            "user.email=fixture@example.invalid",
        ];
        configured.extend_from_slice(args);
        self.run("git", "home-a", cwd, &configured)
    }

    fn seed(&self) -> PathBuf {
        let repo = self.root.join("repo");
        self.git(
            &repo,
            &["init", "--quiet", "--template=", "--initial-branch=main"],
        );
        fs::create_dir(repo.join("src")).unwrap();
        fs::write(repo.join("src/lib.rs"), b"pub fn answer() -> u32 { 42 }\n").unwrap();
        self.git(&repo, &["add", "src/lib.rs"]);
        self.git(&repo, &["commit", "--quiet", "-m", "fixture source"]);
        repo
    }

    fn az(&self, home: &str, cwd: &Path, args: &[&str]) -> Output {
        self.run(env!("CARGO_BIN_EXE_azdaja"), home, cwd, args)
    }

    fn recall(&self, home: &str, cwd: &Path, query: &str) -> Value {
        let output = self.az(home, cwd, &["memory", "recall", query]);
        let report: Value = serde_json::from_slice(&output.stdout).unwrap();
        assert_eq!(report["scope"], "project");
        assert_eq!(report["method"], "lexical");
        assert!(
            report["caveat"]
                .as_str()
                .unwrap()
                .contains("not verified truth")
        );
        report
    }
}

impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.root);
    }
}

fn snapshot(root: &Path) -> BTreeMap<PathBuf, (bool, u32, Vec<u8>)> {
    fn visit(base: &Path, path: &Path, result: &mut BTreeMap<PathBuf, (bool, u32, Vec<u8>)>) {
        let metadata = fs::symlink_metadata(path).unwrap();
        assert!(!metadata.file_type().is_symlink());
        assert!(metadata.is_file() || metadata.is_dir());
        result.insert(
            path.strip_prefix(base).unwrap().to_owned(),
            (
                metadata.is_dir(),
                metadata.permissions().mode() & 0o777,
                if metadata.is_file() {
                    fs::read(path).unwrap()
                } else {
                    Vec::new()
                },
            ),
        );
        if metadata.is_dir() {
            for entry in fs::read_dir(path).unwrap() {
                visit(base, &entry.unwrap().path(), result);
            }
        }
    }
    let mut result = BTreeMap::new();
    visit(root, root, &mut result);
    result
}

#[test]
fn linked_worktrees_isolate_notes_but_share_handoffs_between_fresh_agents() {
    let fixture = Fixture::new();
    let main = fixture.seed();
    fixture.az(
        "home-a",
        &main,
        &[
            "memory",
            "add",
            "observation",
            "mainlesson stays in main worktree",
        ],
    );
    let main_before = snapshot(&main.join(".azdaja"));
    let linked = fixture.root.join("linked");
    fixture.git(
        &main,
        &[
            "worktree",
            "add",
            "--quiet",
            "-b",
            "agent-branch",
            linked.to_str().unwrap(),
        ],
    );
    assert!(
        linked.join(".git").is_file(),
        "must exercise a real linked worktree gitfile"
    );
    assert_eq!(
        fixture.recall("home-b", &linked.join("src"), "mainlesson")["total_matches"],
        0
    );
    assert!(!linked.join(".azdaja").exists());
    fixture.az(
        "home-b",
        &linked,
        &[
            "memory",
            "add",
            "decision",
            "branchlesson check the local source",
            "--tag",
            "file:src/lib.rs",
        ],
    );
    let first = fixture.recall("home-a", &linked.join("src"), "branchlesson");
    assert_eq!(first["total_matches"], 1);
    assert_eq!(
        first["matches"][0]["record"]["text"],
        "branchlesson check the local source"
    );
    assert_eq!(
        first["matches"][0]["record"]["tags"],
        serde_json::json!(["file:src/lib.rs"])
    );
    assert_eq!(
        first["matches"][0]["record"]["provenance"]["origin"],
        "manual"
    );
    let link = format!(
        "related-to:{}",
        first["matches"][0]["record"]["id"].as_str().unwrap()
    );
    fixture.az(
        "home-a",
        &linked,
        &[
            "memory",
            "add",
            "disagreement",
            "opposing evidence must remain visible",
            "--link",
            &link,
        ],
    );
    let linked_before = snapshot(&linked.join(".azdaja"));
    let report = fixture.recall("home-b", &linked.join("src"), "branchlesson");
    assert_eq!(report["total_matches"], 1);
    assert_eq!(
        report["context"][0]["record"]["text"],
        "opposing evidence must remain visible"
    );
    assert_eq!(report["context"][0]["record"]["kind"], "disagreement");
    assert_eq!(
        fixture.recall("home-b", &main, "branchlesson")["total_matches"],
        0
    );
    assert_eq!(
        fixture.recall("home-b", &main, "mainlesson")["total_matches"],
        1
    );
    assert_eq!(main_before, snapshot(&main.join(".azdaja")));
    assert_eq!(linked_before, snapshot(&linked.join(".azdaja")));
    fixture.git(&linked, &["add", "--all"]);
    assert!(
        fixture
            .git(&linked, &["ls-files", "--", ".azdaja"])
            .stdout
            .is_empty()
    );
    assert!(
        fixture
            .git(&linked, &["status", "--porcelain"])
            .stdout
            .is_empty()
    );
}

#[test]
fn ordinary_clone_excludes_private_notes_and_requires_an_explicit_new_handoff() {
    let fixture = Fixture::new();
    let source = fixture.seed();
    let text = "clonelesson verify the source before trusting this note";
    fixture.az(
        "home-a",
        &source,
        &[
            "memory",
            "add",
            "observation",
            text,
            "--tag",
            "file:src/lib.rs",
        ],
    );
    let before = snapshot(&source.join(".azdaja"));
    fixture.git(&source, &["add", "--all"]);
    assert!(
        fixture
            .git(&source, &["ls-files", "--", ".azdaja"])
            .stdout
            .is_empty()
    );
    assert!(
        fixture
            .git(&source, &["status", "--porcelain"])
            .stdout
            .is_empty()
    );
    let clone = fixture.root.join("clone");
    fixture.git(
        &fixture.root,
        &[
            "clone",
            "--quiet",
            "--no-local",
            source.to_str().unwrap(),
            clone.to_str().unwrap(),
        ],
    );
    assert!(clone.join("src/lib.rs").is_file());
    assert!(!clone.join(".azdaja").exists());
    assert_eq!(
        fixture.recall("home-a", &clone.join("src"), "clonelesson")["total_matches"],
        0
    );
    assert!(
        !clone.join(".azdaja").exists(),
        "cold clone recall must remain read-only"
    );
    fixture.az(
        "home-b",
        &clone,
        &[
            "memory",
            "add",
            "observation",
            text,
            "--tag",
            "file:src/lib.rs",
        ],
    );
    let report = fixture.recall("home-a", &clone.join("src"), "clonelesson");
    assert_eq!(report["total_matches"], 1);
    assert_eq!(report["matches"][0]["record"]["text"], text);
    assert_eq!(
        report["matches"][0]["record"]["tags"],
        serde_json::json!(["file:src/lib.rs"])
    );
    assert_eq!(
        report["matches"][0]["record"]["provenance"]["origin"],
        "manual"
    );
    assert_eq!(before, snapshot(&source.join(".azdaja")));
}

#[test]
fn populated_project_reads_do_not_recreate_the_actual_writer_lock() {
    let fixture = Fixture::new();
    let repo = fixture.seed();
    let text = "locklesson committed evidence survives read-only access";
    fixture.az("home-a", &repo, &["memory", "add", "observation", text]);
    let initial = fixture.recall("home-b", &repo, "locklesson");
    assert_eq!(initial["total_matches"], 1);
    let id = initial["matches"][0]["record"]["id"].as_str().unwrap();
    let store = repo.join(".azdaja");
    let lock = store.join("memory/global.jsonl").with_extension("lock");
    assert!(
        lock.is_file(),
        "positive control: writer created its actual lock"
    );
    fs::remove_file(&lock).unwrap();
    assert!(!lock.exists());
    let before = snapshot(&store);
    let commands = [
        vec!["memory", "recall", "locklesson"],
        vec!["memory", "list"],
        vec!["memory", "list", "--kind", "observation"],
        vec!["memory", "show", id],
    ];
    for args in commands {
        let output = fixture.az("home-b", &repo.join("src"), &args);
        let stdout = String::from_utf8(output.stdout).unwrap();
        assert!(stdout.contains(text), "{args:?} lost the committed note");
        assert!(stdout.contains(id), "{args:?} lost its identity");
        assert_eq!(
            before,
            snapshot(&store),
            "{args:?} mutated the populated store"
        );
        assert!(!lock.exists(), "{args:?} recreated the writer lock");
    }
}

#[test]
fn cold_global_and_legacy_read_commands_do_not_initialize_personal_state() {
    let fixture = Fixture::new();
    let repo = fixture.seed();
    let outside = fixture.root.join("outside");
    fs::create_dir(&outside).unwrap();
    let home = fixture.root.join("home-b");
    let before = snapshot(&home);
    for (cwd, global) in [(&repo, true), (&outside, false)] {
        let commands = [
            vec!["memory", "list"],
            vec!["memory", "list", "--kind", "observation"],
            vec!["memory", "recall", "coldlesson"],
        ];
        for mut args in commands {
            if global {
                args.push("--global");
            }
            fixture.az("home-b", cwd, &args);
            assert_eq!(
                before,
                snapshot(&home),
                "{args:?} initialized personal state"
            );
        }
        let mut args = vec!["memory", "show", "m0000000000000000"];
        if global {
            args.push("--global");
        }
        let output = fixture.output(env!("CARGO_BIN_EXE_azdaja"), "home-b", cwd, &args);
        assert_eq!(output.status.code(), Some(2));
        assert!(output.stdout.is_empty() && !output.stderr.is_empty());
        assert_eq!(
            before,
            snapshot(&home),
            "missing show initialized personal state"
        );
    }
    assert!(!repo.join(".azdaja").exists());
    assert!(!outside.join(".azdaja").exists());
}

#[test]
fn unsafe_existing_reader_custody_is_refused_without_repair_or_exposure() {
    let fixture = Fixture::new();
    let repo = fixture.seed();
    let text = "custodylesson retained private fixture evidence";
    fixture.az("home-a", &repo, &["memory", "add", "observation", text]);
    let initial = fixture.recall("home-b", &repo, "custodylesson");
    let id = initial["matches"][0]["record"]["id"].as_str().unwrap();
    let store = repo.join(".azdaja");
    let original = snapshot(&store);
    let commands = [
        vec!["memory", "recall", "custodylesson"],
        vec!["memory", "list"],
        vec!["memory", "list", "--kind", "observation"],
        vec!["memory", "show", id],
    ];
    for (relative, bad_mode) in [("memory", 0o755), ("memory/global.lock", 0o644)] {
        let path = store.join(relative);
        let original_mode = fs::metadata(&path).unwrap().permissions().mode();
        fs::set_permissions(&path, fs::Permissions::from_mode(bad_mode)).unwrap();
        let damaged = snapshot(&store);
        for args in &commands {
            let output = fixture.output(env!("CARGO_BIN_EXE_azdaja"), "home-b", &repo, args);
            assert_eq!(output.status.code(), Some(2), "{relative}: {args:?}");
            assert!(output.stdout.is_empty() && !output.stderr.is_empty());
            assert!(!String::from_utf8_lossy(&output.stderr).contains(text));
            assert_eq!(
                damaged,
                snapshot(&store),
                "{relative}: {args:?} repaired custody"
            );
        }
        fs::set_permissions(&path, fs::Permissions::from_mode(original_mode)).unwrap();
        assert_eq!(initial, fixture.recall("home-b", &repo, "custodylesson"));
        assert_eq!(original, snapshot(&store));
    }
    let lock = store.join("memory/global.lock");
    let lock_bytes = fs::read(&lock).unwrap();
    fs::remove_file(&lock).unwrap();
    let victim = fixture.root.join("lock-victim");
    let victim_bytes = b"private fixture lock victim";
    fs::write(&victim, victim_bytes).unwrap();
    fs::set_permissions(&victim, fs::Permissions::from_mode(0o600)).unwrap();
    std::os::unix::fs::symlink(&victim, &lock).unwrap();
    let ledger_before = fs::read(store.join("memory/global.jsonl")).unwrap();
    for args in &commands {
        let output = fixture.output(env!("CARGO_BIN_EXE_azdaja"), "home-b", &repo, args);
        assert_eq!(output.status.code(), Some(2), "symlink lock: {args:?}");
        assert!(output.stdout.is_empty() && !output.stderr.is_empty());
        assert!(!String::from_utf8_lossy(&output.stderr).contains(text));
        assert!(!String::from_utf8_lossy(&output.stderr).contains("private fixture lock victim"));
        assert_eq!(fs::read_link(&lock).unwrap(), victim);
        assert_eq!(fs::read(&victim).unwrap(), victim_bytes);
        assert_eq!(
            fs::metadata(&victim).unwrap().permissions().mode() & 0o777,
            0o600
        );
        assert_eq!(
            fs::read(store.join("memory/global.jsonl")).unwrap(),
            ledger_before
        );
    }
    fs::remove_file(&lock).unwrap();
    fs::write(&lock, lock_bytes).unwrap();
    fs::set_permissions(&lock, fs::Permissions::from_mode(0o600)).unwrap();
    assert_eq!(initial, fixture.recall("home-b", &repo, "custodylesson"));
    assert_eq!(original, snapshot(&store));
}
