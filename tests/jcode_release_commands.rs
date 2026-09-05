//! Fresh-process hook routing only. Commands below are inert event data, never executed.
use serde_json::json;
use std::collections::BTreeMap;
use std::fs;
use std::io::{Read, Write};
use std::path::PathBuf;
use std::process::{Child, Command, Output, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::thread;
use std::time::{Duration, Instant};

static NEXT: AtomicU64 = AtomicU64::new(0);
struct Fixture(PathBuf);
struct Running(Option<Child>);

impl Drop for Running {
    fn drop(&mut self) {
        if let Some(mut child) = self.0.take() {
            // Keep the direct child unreaped until output collection completes,
            // so its private Unix process-group ID cannot be reused on timeout.
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
impl Fixture {
    fn new() -> Self {
        let root = loop {
            let path = std::env::temp_dir().join(format!(
                "az-hook-release-{}-{}",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            match fs::create_dir(&path) {
                Ok(()) => break path,
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
                Err(error) => panic!("exclusive fixture creation failed: {error}"),
            }
        };
        let fixture = Self(root);
        fs::create_dir(fixture.0.join("home")).unwrap();
        fs::create_dir(fixture.0.join("repo")).unwrap();
        fs::write(fixture.0.join("repo/source.txt"), "fixture evidence\n").unwrap();
        fixture
    }

    fn event(&self, tool: &str, input: serde_json::Value) -> Output {
        let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
        for (key, _) in std::env::vars_os() {
            if ["AZDAJA_", "JCODE_", "GIT_"]
                .iter()
                .any(|prefix| key.to_string_lossy().starts_with(prefix))
            {
                command.env_remove(key);
            }
        }
        command
            .current_dir(self.0.join("repo"))
            .env("HOME", self.0.join("home"))
            .env("USERPROFILE", self.0.join("home"))
            .env("XDG_CONFIG_HOME", self.0.join("config"))
            .env("XDG_STATE_HOME", self.0.join("state"))
            .env("AZDAJA_HOME", self.0.join("az-state"))
            .env("AZDAJA_JCODE_ACTIVATION", "session")
            .env("JCODE_HOOK_EVENT", "pre_tool")
            .env("JCODE_HOOK_SESSION_ID", "release-command-fixture")
            .env("JCODE_HOOK_CWD", self.0.join("repo"))
            .env("JCODE_HOOK_TOOL_NAME", tool)
            .arg("jcode-hook")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        #[cfg(unix)]
        {
            use std::os::unix::process::CommandExt;
            command.process_group(0);
        }
        let mut running = Running(Some(command.spawn().unwrap()));
        let child = running.0.as_mut().unwrap();
        child
            .stdin
            .take()
            .unwrap()
            .write_all(serde_json::to_string(&input).unwrap().as_bytes())
            .unwrap();
        let mut stdout = child.stdout.take().unwrap();
        let mut stderr = child.stderr.take().unwrap();
        let (sender, receiver) = std::sync::mpsc::channel();
        let stdout_sender = sender.clone();
        thread::spawn(move || {
            let mut bytes = Vec::new();
            stdout
                .by_ref()
                .take(64 * 1024)
                .read_to_end(&mut bytes)
                .unwrap();
            std::io::copy(&mut stdout, &mut std::io::sink()).unwrap();
            let _ = stdout_sender.send((true, bytes));
        });
        thread::spawn(move || {
            let mut bytes = Vec::new();
            stderr
                .by_ref()
                .take(64 * 1024)
                .read_to_end(&mut bytes)
                .unwrap();
            std::io::copy(&mut stderr, &mut std::io::sink()).unwrap();
            let _ = sender.send((false, bytes));
        });
        let deadline = Instant::now() + Duration::from_secs(10);
        let mut captured_stdout = Vec::new();
        let mut captured_stderr = Vec::new();
        for _ in 0..2 {
            let (is_stdout, bytes) = receiver
                .recv_timeout(deadline.saturating_duration_since(Instant::now()))
                .expect("hook output capture did not finish");
            if is_stdout {
                captured_stdout = bytes;
            } else {
                captured_stderr = bytes;
            }
        }
        let status = loop {
            if let Some(status) = running.0.as_mut().unwrap().try_wait().unwrap() {
                running.0.take();
                break status;
            }
            assert!(Instant::now() < deadline, "hook decision exceeded timeout");
            thread::sleep(Duration::from_millis(5));
        };
        Output {
            status,
            stdout: captured_stdout,
            stderr: captured_stderr,
        }
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn snapshot(root: &std::path::Path) -> BTreeMap<PathBuf, (bool, Vec<u8>)> {
    let mut result = BTreeMap::new();
    let mut pending = vec![root.to_owned()];
    while let Some(directory) = pending.pop() {
        for entry in fs::read_dir(directory).unwrap() {
            let path = entry.unwrap().path();
            let kind = fs::symlink_metadata(&path).unwrap().file_type();
            assert!(kind.is_dir() || kind.is_file(), "unexpected fixture entry");
            let bytes = if kind.is_dir() {
                pending.push(path.clone());
                Vec::new()
            } else {
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

#[test]
fn active_hook_allows_release_build_events_without_unlocking_broad_reads() {
    let fixture = Fixture::new();
    let broad = json!({"file_path": fixture.0.join("repo/source.txt"), "limit": 5000});
    let blocked = fixture.event("read", broad.clone());
    assert_eq!(
        blocked.status.code(),
        Some(2),
        "activation control: {blocked:?}"
    );
    assert!(blocked.stdout.is_empty());
    assert!(String::from_utf8_lossy(&blocked.stderr).contains("AZDAJA_JCODE_CHALLENGE="));
    let before = snapshot(&fixture.0);
    for command in [
        "cargo +1.95.0 package --locked",
        "cargo +1.95.0 package --locked --no-verify",
        "cargo +1.95.0 package --list --allow-dirty --locked",
        "cargo +1.95.0 install --path . --root /fixture/candidate --locked",
    ] {
        let output = fixture.event("bash", json!({"command": command}));
        assert!(
            output.status.success(),
            "allowed event {command}: {output:?}"
        );
        assert!(output.stdout.is_empty());
        assert!(
            output.stderr.is_empty(),
            "allowed event emitted a diagnostic: {output:?}"
        );
    }
    assert_eq!(
        before,
        snapshot(&fixture.0),
        "build routing mutated fixture state"
    );
    for command in [
        "cargo publish --locked",
        "cargo install --path . --locked",
        "cargo install arbitrary-crate --root /fixture/candidate --locked",
        "cargo install --path . --root /fixture/candidate --locked --config build.rustc=cat",
        "cargo package --locked && cat source.txt",
    ] {
        let output = fixture.event("bash", json!({"command": command}));
        assert_eq!(
            output.status.code(),
            Some(2),
            "forbidden event {command}: {output:?}"
        );
        assert!(output.stdout.is_empty());
        assert!(String::from_utf8_lossy(&output.stderr).contains("AZDAJA_JCODE_CHALLENGE="));
    }
    let still_blocked = fixture.event("read", broad);
    assert_eq!(
        still_blocked.status.code(),
        Some(2),
        "allowing a build must not unlock reads: {still_blocked:?}"
    );
    assert!(still_blocked.stdout.is_empty());
    assert_eq!(
        blocked.stderr, still_blocked.stderr,
        "the pending challenge changed"
    );
}
