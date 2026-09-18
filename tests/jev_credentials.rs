//! Real CLI acceptance with synthetic keys. No test permits a provider request.
#![cfg(unix)]
use serde_json::Value;
use std::fs;
use std::io::Write;
use std::os::unix::fs::{PermissionsExt, symlink};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Output, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant};

static NEXT: AtomicU64 = AtomicU64::new(0);
const KEY: &str = "apikey_SYNTHETICATTACH_0123456789abcdef0123456789abcdef";
const OTHER: &str = "apikey_SYNTHETICREPLACE_fedcba9876543210fedcba9876543210";
const NAME: &str = "Jev_test_credential";

struct Fixture(PathBuf);
impl Fixture {
    fn new() -> Self {
        let base = std::env::var_os("JCODE_SCRATCH_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(std::env::temp_dir);
        let root = base.join(format!(
            "azdaja-credentials-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&root).unwrap();
        fs::set_permissions(&root, fs::Permissions::from_mode(0o700)).unwrap();
        Self(root)
    }
    fn state(&self) -> PathBuf {
        self.0.join("state")
    }
    fn command(&self, args: &[&str], vars: &[(&str, &str)]) -> Command {
        let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
        command
            .args(args)
            .current_dir(&self.0)
            .env_clear()
            .env("PATH", "/usr/bin:/bin")
            .env("HOME", &self.0)
            .env("AZDAJA_HOME", self.state())
            .env("AZDAJA_CONFIG", self.0.join("config.toml"))
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        for (name, value) in vars {
            command.env(name, value);
        }
        command
    }
    fn run(&self, args: &[&str], input: Option<&[u8]>, vars: &[(&str, &str)]) -> Output {
        Self::finish_child(self.command(args, vars).spawn().unwrap(), input)
    }
    fn finish_child(mut child: Child, input: Option<&[u8]>) -> Output {
        let write_result = if let Some(bytes) = input {
            child.stdin.take().unwrap().write_all(bytes)
        } else {
            drop(child.stdin.take());
            Ok(())
        };
        let output = child.wait_with_output().unwrap();
        // A refusal may close stdin first. Preserve its output for the caller's
        // assertions, but never hide an incomplete write to a successful child.
        match write_result {
            Ok(()) => {}
            Err(error)
                if error.kind() == std::io::ErrorKind::BrokenPipe && !output.status.success() => {}
            Err(error) => panic!("writing child stdin failed: {error}"),
        }
        output
    }
    fn run_after_exit(&self, args: &[&str], input: &[u8], vars: &[(&str, &str)]) -> Output {
        let mut child = self.command(args, vars).spawn().unwrap();
        let deadline = Instant::now() + Duration::from_secs(5);
        while child.try_wait().unwrap().is_none() {
            if Instant::now() >= deadline {
                let _ = child.kill();
                let _ = child.wait();
                panic!("CLI did not exit before the bounded stdin-write witness");
            }
            std::thread::yield_now();
        }
        Self::finish_child(child, Some(input))
    }
    fn ok(&self, args: &[&str], input: Option<&[u8]>, vars: &[(&str, &str)]) -> Value {
        let output = self.run(args, input, vars);
        assert!(
            output.status.success(),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        serde_json::from_slice(&output.stdout).unwrap()
    }
    fn attach(&self, key: &str) {
        self.ok(
            &["jev", "attach", "--stdin", "--key-env", NAME],
            Some(key.as_bytes()),
            &[],
        );
    }
    fn key_file(&self) -> PathBuf {
        let files: Vec<_> = fs::read_dir(self.state().join("credentials"))
            .unwrap()
            .map(|e| e.unwrap().path())
            .filter(|p| p.extension().is_some_and(|v| v == "key"))
            .collect();
        assert_eq!(files.len(), 1);
        files[0].clone()
    }
    fn configure(&self, enabled: bool) {
        fs::write(
            self.0.join("config.toml"),
            format!(
                "sub_llm_cmd=\"/usr/bin/false\"\n[judge]\nenabled={enabled}\nkey_env=\"{NAME}\"\n"
            ),
        )
        .unwrap();
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn mode(path: &Path) -> u32 {
    fs::symlink_metadata(path).unwrap().permissions().mode() & 0o777
}

#[test]
fn invalid_args_refuse_before_stdin_write_without_losing_output() {
    let f = Fixture::new();
    let args = ["jev", "attach", "--stdin", "--stdin"];
    let expected = f.run(&args, None, &[]);
    let actual = f.run_after_exit(&args, KEY.as_bytes(), &[]);
    assert_eq!(actual.status, expected.status);
    assert_eq!(actual.stdout, expected.stdout);
    assert_eq!(actual.stderr, expected.stderr);
}

#[test]
fn unsafe_status_refuses_before_stdin_write_without_changing_storage() {
    let f = Fixture::new();
    f.attach(KEY);
    let path = f.key_file();
    fs::set_permissions(&path, fs::Permissions::from_mode(0o644)).unwrap();
    let args = ["jev", "status", "--key-env", NAME];
    let expected = f.run(&args, None, &[]);
    let actual = f.run_after_exit(&args, OTHER.as_bytes(), &[]);
    assert!(!actual.status.success());
    assert_eq!(actual.status, expected.status);
    assert_eq!(actual.stdout, expected.stdout);
    assert_eq!(actual.stderr, expected.stderr);
    assert_eq!(fs::read_to_string(&path).unwrap(), KEY);
    assert_eq!(mode(&path), 0o644);
}

#[test]
#[should_panic(expected = "writing child stdin failed")]
fn successful_exit_does_not_hide_incomplete_stdin() {
    Fixture::new().run_after_exit(&["--version"], KEY.as_bytes(), &[]);
}

#[test]
fn public_attachment_survives_restart_replacement_and_detach_without_config_or_network() {
    let f = Fixture::new();
    fs::write(f.0.join("config.toml"), "broken = [").unwrap();
    let absent = f.ok(&["jev", "status", "--key-env", NAME], None, &[]);
    assert_eq!(absent["source"], "absent");
    assert!(!f.state().exists(), "status must not initialize state");
    f.attach(KEY);
    let path = f.key_file();
    assert_eq!(fs::read_to_string(&path).unwrap(), KEY);
    assert_eq!(mode(&path), 0o600);
    assert_eq!(mode(&f.state()), 0o700);
    assert_eq!(mode(&f.state().join("credentials")), 0o700);
    let attached = f.ok(&["jev", "status", "--key-env", NAME], None, &[]);
    assert_eq!(attached["source"], "attached_file");
    assert_eq!(attached["fingerprint"].as_str().unwrap().len(), 12);
    assert!(!attached.to_string().contains(KEY));
    let refused = f.run(
        &["jev", "attach", "--stdin", "--key-env", NAME],
        Some(OTHER.as_bytes()),
        &[],
    );
    assert!(!refused.status.success());
    assert_eq!(fs::read_to_string(&path).unwrap(), KEY);
    f.ok(
        &["jev", "attach", "--stdin", "--replace", "--key-env", NAME],
        Some(OTHER.as_bytes()),
        &[],
    );
    assert_eq!(fs::read_to_string(&path).unwrap(), OTHER);
    let env = f.ok(&["jev", "status", "--key-env", NAME], None, &[(NAME, KEY)]);
    assert_eq!(env["source"], "environment");
    let removed = f.ok(&["jev", "detach", "--key-env", NAME], None, &[]);
    assert_eq!(removed["removed"], true);
    assert!(!path.exists());
    assert_eq!(
        f.ok(&["jev", "detach", "--key-env", NAME], None, &[])["removed"],
        false
    );
}

#[test]
fn public_attachment_refuses_unsafe_paths_without_changing_existing_bytes_or_modes() {
    let f = Fixture::new();
    fs::create_dir(f.state()).unwrap();
    fs::set_permissions(f.state(), fs::Permissions::from_mode(0o755)).unwrap();
    assert!(
        !f.run(&["jev", "attach", "--stdin"], Some(KEY.as_bytes()), &[])
            .status
            .success()
    );
    assert_eq!(
        mode(&f.state()),
        0o755,
        "must not silently repair unsafe storage"
    );
    fs::set_permissions(f.state(), fs::Permissions::from_mode(0o700)).unwrap();
    f.attach(KEY);
    let path = f.key_file();
    fs::set_permissions(&path, fs::Permissions::from_mode(0o644)).unwrap();
    for args in [
        vec!["jev", "status", "--key-env", NAME],
        vec!["jev", "detach", "--key-env", NAME],
        vec!["jev", "attach", "--stdin", "--replace", "--key-env", NAME],
    ] {
        assert!(!f.run(&args, Some(OTHER.as_bytes()), &[]).status.success());
    }
    assert_eq!(fs::read_to_string(&path).unwrap(), KEY);
    fs::set_permissions(&path, fs::Permissions::from_mode(0o600)).unwrap();
    let target = f.0.join("unrelated-owned-test-file");
    fs::rename(&path, &target).unwrap();
    symlink(&target, &path).unwrap();
    assert!(
        !f.run(
            &["jev", "attach", "--stdin", "--replace", "--key-env", NAME],
            Some(OTHER.as_bytes()),
            &[]
        )
        .status
        .success()
    );
    assert!(
        fs::symlink_metadata(&path)
            .unwrap()
            .file_type()
            .is_symlink()
    );
    assert_eq!(fs::read_to_string(&target).unwrap(), KEY);
}

#[test]
fn attachment_rejects_argv_secrets_and_bounded_stdin_without_disclosure() {
    let f = Fixture::new();
    for args in [
        vec!["jev", "attach", KEY],
        vec!["jev", "attach", "--stdin", "--key-env", "../bad"],
        vec!["jev", "status", "--stdin"],
        vec!["jev", "attach", "--stdin", "--stdin"],
    ] {
        let output = f.run(&args, Some(KEY.as_bytes()), &[]);
        assert!(!output.status.success());
        assert!(!String::from_utf8_lossy(&output.stdout).contains(KEY));
        assert!(!String::from_utf8_lossy(&output.stderr).contains(KEY));
    }
    for bytes in [
        Vec::new(),
        vec![b'A'; 8196],
        b"two\nlines".to_vec(),
        vec![0xff],
    ] {
        assert!(
            !f.run(&["jev", "attach", "--stdin"], Some(&bytes), &[])
                .status
                .success()
        );
    }
    assert!(!f.state().exists());
}

#[test]
fn doctor_jev_is_explicit_local_status_and_caps_remains_non_probing() {
    let f = Fixture::new();
    f.configure(false);
    let caps = f.ok(&["doctor", "--caps"], None, &[]);
    assert_eq!(caps["typed_judgments"]["credentials_checked"], false);
    assert!(!f.state().exists());
    f.attach(KEY);
    let report = f.ok(&["doctor", "jev"], None, &[]);
    assert_eq!(report["configured_enabled"], false);
    assert_eq!(report["source"], "attached_file");
    assert_eq!(report["provider_readiness_checked"], false);
}

#[test]
fn interrupted_attachment_is_visible_and_detach_recovers_only_that_key() {
    let f = Fixture::new();
    f.attach(KEY);
    f.ok(&["jev", "detach", "--key-env", NAME], None, &[]);
    let directory = f.state().join("credentials");
    let pending = directory.join(format!(
        ".pending-{}-900000-0",
        azdaja::sha256_hex(NAME.as_bytes())
    ));
    let unrelated = directory.join(format!(
        ".pending-{}-900000-0",
        azdaja::sha256_hex(b"OTHER_KEY")
    ));
    for path in [&pending, &unrelated] {
        fs::write(path, KEY).unwrap();
        fs::set_permissions(path, fs::Permissions::from_mode(0o600)).unwrap();
    }
    let status = f.ok(&["jev", "status", "--key-env", NAME], None, &[]);
    assert_eq!(status["source"], "absent");
    assert_eq!(status["incomplete_attachment"], true);
    assert_eq!(
        f.ok(&["jev", "detach", "--key-env", NAME], None, &[])["removed"],
        true
    );
    assert!(!pending.exists());
    assert_eq!(fs::read(&unrelated).unwrap(), KEY.as_bytes());
    assert_eq!(
        f.ok(&["jev", "status", "--key-env", NAME], None, &[])["incomplete_attachment"],
        false
    );
    fs::write(&pending, KEY).unwrap();
    fs::set_permissions(&pending, fs::Permissions::from_mode(0o600)).unwrap();
    f.attach(KEY);
    assert!(!pending.exists());
}

#[test]
fn unsafe_staging_is_not_followed_or_deleted() {
    let f = Fixture::new();
    f.attach(KEY);
    let pending = f.state().join("credentials").join(format!(
        ".pending-{}-900000-0",
        azdaja::sha256_hex(NAME.as_bytes())
    ));
    let target = f.0.join("unrelated");
    fs::write(&target, "keep").unwrap();
    std::os::unix::fs::symlink(&target, &pending).unwrap();
    assert!(
        !f.run(&["jev", "detach", "--key-env", NAME], None, &[])
            .status
            .success()
    );
    assert!(pending.is_symlink());
    assert_eq!(fs::read(&target).unwrap(), b"keep");
}

#[test]
fn native_resolution_uses_attachment_but_disabled_and_invalid_overrides_never_enter_transport() {
    let f = Fixture::new();
    f.attach(KEY);
    f.configure(false);
    let start = f.run(&["start"], None, &[]);
    assert!(start.status.success());
    let sid = String::from_utf8(start.stdout).unwrap().trim().to_owned();
    // The state contains every possible valid synthetic key. Even a precedence
    // regression therefore hits the leakage guard instead of contacting a provider.
    let code = format!(
        "error = None\ntry:\n    judge_many({KEY:?}, {{\"q\":{{\"type\":\"noul\",\"instructions\":\"Is it present?\"}}}})\nexcept Exception as e:\n    error = str(e)\nFINAL({{\"error\":error,\"stats\":judge_stats()}})\n"
    );
    for (enabled, vars, expected) in [
        (
            false,
            vec![],
            "judge_many is disabled; the host must explicitly enable [judge]",
        ),
        (
            true,
            vec![],
            if cfg!(feature = "typesafe") {
                "judge: credential leakage refused"
            } else {
                "judge: typesafe feature is not enabled in this build"
            },
        ),
        (
            true,
            vec![(NAME, "invalid value")],
            if cfg!(feature = "typesafe") {
                "judge: invalid credential syntax"
            } else {
                "judge: typesafe feature is not enabled in this build"
            },
        ),
    ] {
        f.configure(enabled);
        let output = f.run(&["exec", &sid], Some(code.as_bytes()), &vars);
        assert!(
            output.status.success(),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        let report = f.ok(&["final", &sid], None, &[]);
        assert!(
            report["error"].as_str().unwrap().contains(expected),
            "{report}"
        );
        assert_eq!(report["stats"]["attempts"], 0);
    }
    assert!(f.run(&["kill", &sid], None, &[]).status.success());
}
