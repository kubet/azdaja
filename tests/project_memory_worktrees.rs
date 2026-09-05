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

    fn run(&self, program: &str, home: &str, cwd: &Path, args: &[&str]) -> Output {
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
            output.status.success(),
            "{program} {args:?}: {}",
            String::from_utf8_lossy(&output.stderr)
        );
        assert!(
            !self.root.join("provider-called").exists(),
            "memory workflow invoked a provider"
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
