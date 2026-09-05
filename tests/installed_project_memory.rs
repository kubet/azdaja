//! Run explicitly against a separately installed release artifact:
//! AZDAJA_INSTALLED_TEST_BINARY=/absolute/install/root/bin/azdaja \
//! cargo +1.95.0 test --locked --test installed_project_memory -- --ignored
//! The caller must retain installation/provenance evidence. A path alone does
//! not prove where the binary came from. Normal test runs do not claim this gate.

use serde_json::Value;
use std::collections::BTreeMap;
use std::fs;
use std::io::Read;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Output, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::mpsc;
use std::thread;
use std::time::{Duration, Instant};

static NEXT: AtomicU64 = AtomicU64::new(0);

struct Fixture {
    root: PathBuf,
    binary: PathBuf,
}

struct Running(Option<Child>);

impl Drop for Running {
    fn drop(&mut self) {
        if let Some(mut child) = self.0.take() {
            // The child remains unreaped until its pipes close. Its PID cannot
            // be reused while this guard may still terminate its private group.
            #[cfg(unix)]
            if let Ok(pid) = libc::pid_t::try_from(child.id())
                && pid > 0
            {
                unsafe {
                    libc::kill(-pid, libc::SIGKILL);
                }
            }
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

fn capture<R: Read + Send + 'static>(mut stream: R) -> mpsc::Receiver<Vec<u8>> {
    let (sender, receiver) = mpsc::channel();
    thread::spawn(move || {
        let mut bytes = Vec::new();
        stream
            .by_ref()
            .take(1024 * 1024)
            .read_to_end(&mut bytes)
            .unwrap();
        std::io::copy(&mut stream, &mut std::io::sink()).unwrap();
        let _ = sender.send(bytes);
    });
    receiver
}

fn finish(command: Command) -> Output {
    finish_with_timeout(command, Duration::from_secs(30))
}

fn finish_with_timeout(mut command: Command, timeout: Duration) -> Output {
    #[cfg(unix)]
    {
        use std::os::unix::process::CommandExt;
        command.process_group(0);
    }
    let child = command
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    let mut running = Running(Some(child));
    let stdout_reader = capture(running.0.as_mut().unwrap().stdout.take().unwrap());
    let stderr_reader = capture(running.0.as_mut().unwrap().stderr.take().unwrap());
    let deadline = Instant::now() + timeout;
    // Do not reap the direct child before EOF: a descendant may hold a pipe.
    // Both collection waits and the final child wait share one deadline.
    let stdout = stdout_reader
        .recv_timeout(deadline.saturating_duration_since(Instant::now()))
        .expect("stdout capture exceeded the deadline or failed");
    let stderr = stderr_reader
        .recv_timeout(deadline.saturating_duration_since(Instant::now()))
        .expect("stderr capture exceeded the deadline or failed");
    let status = loop {
        if let Some(status) = running.0.as_mut().unwrap().try_wait().unwrap() {
            running.0.take();
            break status;
        }
        assert!(
            Instant::now() < deadline,
            "installed-artifact child exceeded its deadline"
        );
        thread::sleep(Duration::from_millis(5));
    };
    Output {
        status,
        stdout,
        stderr,
    }
}

impl Fixture {
    fn new() -> Self {
        let supplied = PathBuf::from(
            std::env::var_os("AZDAJA_INSTALLED_TEST_BINARY")
                .expect("this explicit gate requires AZDAJA_INSTALLED_TEST_BINARY"),
        );
        assert!(
            supplied.is_absolute(),
            "supply the installed binary's absolute path"
        );
        let binary = supplied
            .canonicalize()
            .expect("installed binary must exist");
        assert!(binary.is_file());
        let root = loop {
            let root = std::env::temp_dir().join(format!(
                "az-installed-memory-{}-{}",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            match fs::create_dir(&root) {
                Ok(()) => break root,
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
                Err(error) => panic!("cannot create exclusive fixture: {error}"),
            }
        };
        let fixture = Self { root, binary };
        for name in ["home-a", "home-b", "outside"] {
            fs::create_dir(fixture.root.join(name)).unwrap();
        }
        fs::write(fixture.root.join("gitconfig"), b"").unwrap();
        fixture.init_repo(&fixture.repo());
        fs::create_dir(fixture.repo().join("src")).unwrap();
        let version = fixture.run(
            "home-a",
            &fixture.root.join("outside"),
            None,
            &["--version"],
        );
        assert!(version.status.success(), "version failed: {version:?}");
        let text = std::str::from_utf8(&version.stdout).unwrap();
        assert!(
            text.starts_with("azdaja"),
            "wrong installed product: {text:?}"
        );
        assert!(
            text.split_whitespace()
                .any(|part| part == env!("CARGO_PKG_VERSION")),
            "installed version differs from candidate package: {text:?}"
        );
        fixture
    }

    fn repo(&self) -> PathBuf {
        self.root.join("repo")
    }

    fn init_repo(&self, path: &Path) {
        let mut command = Command::new("git");
        for (key, _) in std::env::vars_os() {
            if key.to_string_lossy().starts_with("GIT_") {
                command.env_remove(key);
            }
        }
        command
            .current_dir(&self.root)
            .env_remove("GIT_DIR")
            .env_remove("GIT_WORK_TREE")
            .env_remove("GIT_INDEX_FILE")
            .env_remove("GIT_COMMON_DIR")
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .env("GIT_CONFIG_GLOBAL", self.root.join("gitconfig"))
            .args(["init", "--quiet", "--template="])
            .arg(path);
        let output = finish(command);
        assert!(
            output.status.success(),
            "fixture Git init failed: {output:?}"
        );
    }

    fn run(&self, home: &str, cwd: &Path, mode: Option<&str>, args: &[&str]) -> Output {
        let mut command = Command::new(&self.binary);
        for (key, _) in std::env::vars_os() {
            if key.to_string_lossy().starts_with("AZDAJA_")
                || key.to_string_lossy().starts_with("GIT_")
            {
                command.env_remove(key);
            }
        }
        command
            .current_dir(cwd)
            .env("HOME", self.root.join(home))
            .env("USERPROFILE", self.root.join(home))
            .env("XDG_CONFIG_HOME", self.root.join(format!("config-{home}")))
            .env("XDG_STATE_HOME", self.root.join(format!("state-{home}")))
            .args(args);
        if let Some(mode) = mode {
            command.env("AZDAJA_PROJECT_MEMORY", mode);
        }
        finish(command)
    }

    fn recall(&self, home: &str, cwd: &Path, global: bool) -> Value {
        let mut args = vec!["memory", "recall", "artifactlesson"];
        if global {
            args.push("--global");
        }
        let output = self.run(home, cwd, None, &args);
        assert!(output.status.success(), "recall failed: {output:?}");
        assert!(output.stdout.len() <= 64 * 1024);
        let report: Value = serde_json::from_slice(&output.stdout).unwrap();
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

fn snapshot(root: &Path) -> BTreeMap<PathBuf, (bool, Vec<u8>)> {
    let mut result = BTreeMap::new();
    let mut pending = vec![root.to_owned()];
    while let Some(directory) = pending.pop() {
        for entry in fs::read_dir(directory).unwrap() {
            let path = entry.unwrap().path();
            let kind = fs::symlink_metadata(&path).unwrap().file_type();
            assert!(!kind.is_symlink(), "unexpected link in owned store fixture");
            let bytes = if kind.is_dir() {
                pending.push(path.clone());
                Vec::new()
            } else {
                assert!(
                    kind.is_file(),
                    "unexpected nonregular entry in owned store fixture"
                );
                fs::read(&path).unwrap()
            };
            result.insert(
                path.strip_prefix(root).unwrap().to_owned(),
                (kind.is_dir(), bytes),
            );
        }
    }
    result
}

#[cfg(unix)]
#[test]
fn capture_deadline_covers_inherited_pipes() {
    const PHASE: &str = "AZDAJA_ARTIFACT_CAPTURE_PROBE";
    const MARKER: &str = "AZDAJA_ARTIFACT_CAPTURE_MARKER";
    if let Ok(phase) = std::env::var(PHASE) {
        if phase == "descendant" {
            fs::write(
                std::env::var_os(MARKER).unwrap(),
                std::process::id().to_string(),
            )
            .unwrap();
            thread::sleep(Duration::from_secs(8));
        } else {
            assert_eq!(phase, "parent");
            #[allow(
                clippy::zombie_processes,
                reason = "Fault probe must exit before its descendant; the outer harness owns timeout group cleanup"
            )]
            let _descendant = Command::new(std::env::current_exe().unwrap())
                .args([
                    "--exact",
                    "capture_deadline_covers_inherited_pipes",
                    "--nocapture",
                ])
                .env(PHASE, "descendant")
                .stdin(Stdio::null())
                .stdout(Stdio::inherit())
                .stderr(Stdio::inherit())
                .spawn()
                .unwrap();
        }
        return;
    }
    let root = loop {
        let path = std::env::temp_dir().join(format!(
            "az-capture-probe-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        match fs::create_dir(&path) {
            Ok(()) => break path,
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(error) => panic!("cannot create exclusive probe: {error}"),
        }
    };
    let owned = Fixture {
        root,
        binary: std::env::current_exe().unwrap(),
    };
    let marker = owned.root.join("descendant-ready");
    let mut command = Command::new(&owned.binary);
    command
        .args([
            "--exact",
            "capture_deadline_covers_inherited_pipes",
            "--nocapture",
        ])
        .env(PHASE, "parent")
        .env(MARKER, &marker);
    let started = Instant::now();
    let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        finish_with_timeout(command, Duration::from_secs(2))
    }));
    assert!(
        marker.is_file(),
        "descendant did not reach the inherited-pipe probe"
    );
    assert!(
        result.is_err(),
        "helper accepted a descendant-held pipe after its deadline"
    );
    assert!(
        started.elapsed() < Duration::from_secs(6),
        "pipe cleanup exceeded the bounded allowance"
    );
}

#[test]
#[ignore = "requires a separately installed candidate via AZDAJA_INSTALLED_TEST_BINARY"]
fn installed_artifact_preserves_cross_home_handoff_and_relocation() {
    let f = Fixture::new();
    let cold = f.recall("home-a", &f.repo(), false);
    assert_eq!(cold["scope"], "project");
    assert_eq!(cold["total_matches"], 0);
    assert!(!f.repo().join(".azdaja").exists());
    assert!(!f.root.join("state-home-a").exists());

    let text = "artifactlesson verify the candidate before promotion";
    let output = f.run(
        "home-a",
        &f.repo(),
        None,
        &[
            "memory",
            "add",
            "decision",
            text,
            "--tag",
            "file:src/cache.rs",
        ],
    );
    assert!(output.status.success(), "project add failed: {output:?}");
    let primary = f.recall("home-a", &f.repo(), false);
    let id = primary["matches"][0]["record"]["id"].as_str().unwrap();
    assert_eq!(primary["matches"][0]["record"]["text"], text);
    assert_eq!(
        primary["matches"][0]["record"]["tags"],
        serde_json::json!(["file:src/cache.rs"])
    );
    assert_eq!(
        primary["matches"][0]["record"]["provenance"]["origin"],
        "manual"
    );
    let contrary = "New evidence contradicts the initial premise.";
    let link = format!("related-to:{id}");
    let output = f.run(
        "home-b",
        &f.repo().join("src"),
        None,
        &["memory", "add", "disagreement", contrary, "--link", &link],
    );
    assert!(output.status.success(), "linked add failed: {output:?}");
    let report = f.recall("home-b", &f.repo().join("src"), false);
    assert_eq!(report["total_matches"], 1);
    assert_eq!(
        report["matches"][0]["record"],
        primary["matches"][0]["record"]
    );
    assert!(
        report["context"]
            .as_array()
            .unwrap()
            .iter()
            .any(|item| item["record"]["kind"] == "disagreement"
                && item["record"]["text"] == contrary)
    );
    assert_eq!(f.recall("home-b", &f.repo(), true)["total_matches"], 0);
    let peer = f.root.join("peer");
    f.init_repo(&peer);
    assert_eq!(f.recall("home-a", &peer, false)["total_matches"], 0);
    assert!(!peer.join(".azdaja").exists());

    let before = snapshot(&f.repo().join(".azdaja"));
    for args in [
        vec!["memory", "list", "--kind", "decision"],
        vec!["memory", "show", id],
    ] {
        let output = f.run("home-b", &f.repo().join("src"), None, &args);
        assert!(output.status.success(), "project read failed: {output:?}");
        assert!(String::from_utf8_lossy(&output.stdout).contains(text));
    }
    assert_eq!(snapshot(&f.repo().join(".azdaja")), before);
    assert_eq!(
        fs::read(f.repo().join(".azdaja/.gitignore")).unwrap(),
        b"*\n"
    );
    let moved = f.root.join("relocated");
    fs::rename(f.repo(), &moved).unwrap();
    assert_eq!(f.recall("home-b", &moved.join("src"), false), report);
    assert_eq!(snapshot(&moved.join(".azdaja")), before);
}

#[test]
#[ignore = "requires a separately installed candidate via AZDAJA_INSTALLED_TEST_BINARY"]
fn installed_artifact_refuses_disabled_writes_and_corrupt_reads_without_fallback() {
    let f = Fixture::new();
    let refused = f.run(
        "home-a",
        &f.repo(),
        Some("off"),
        &["memory", "add", "observation", "artifactlesson disabled"],
    );
    assert_eq!(refused.status.code(), Some(2));
    assert!(refused.stdout.is_empty());
    assert!(!f.repo().join(".azdaja").exists());
    assert!(!f.root.join("state-home-a").exists());
    let output = f.run(
        "home-a",
        &f.repo(),
        Some("off"),
        &[
            "memory",
            "add",
            "observation",
            "artifactlesson personal-only",
            "--global",
        ],
    );
    assert!(
        output.status.success(),
        "explicit global add failed: {output:?}"
    );
    assert_eq!(f.recall("home-a", &f.repo(), true)["total_matches"], 1);
    assert_eq!(f.recall("home-a", &f.repo(), false)["total_matches"], 0);

    let output = f.run(
        "home-a",
        &f.repo(),
        None,
        &["memory", "add", "hypothesis", "artifactlesson project-only"],
    );
    assert!(output.status.success(), "project add failed: {output:?}");
    let expected = f.recall("home-b", &f.repo(), false);
    let id = expected["matches"][0]["record"]["id"].as_str().unwrap();
    let ledger = f.repo().join(".azdaja/memory/global.jsonl");
    let original = fs::read(&ledger).unwrap();
    fs::write(&ledger, b"{invalid-json\n").unwrap();
    let damaged = snapshot(&f.repo().join(".azdaja"));
    for args in [
        vec!["memory", "recall", "artifactlesson"],
        vec!["memory", "list"],
        vec!["memory", "show", id],
    ] {
        let output = f.run("home-a", &f.repo(), None, &args);
        assert_eq!(
            output.status.code(),
            Some(2),
            "not a clean refusal: {output:?}"
        );
        assert!(
            output.stdout.is_empty(),
            "corrupt project fell back to personal output"
        );
        assert!(!output.stderr.is_empty());
        assert_eq!(snapshot(&f.repo().join(".azdaja")), damaged);
    }
    fs::write(&ledger, &original).unwrap();
    assert_eq!(f.recall("home-b", &f.repo().join("src"), false), expected);
    assert_eq!(f.recall("home-a", &f.repo(), true)["total_matches"], 1);
}
