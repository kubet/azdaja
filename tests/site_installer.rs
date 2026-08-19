#![cfg(unix)]

use std::{
    fs,
    os::unix::fs::PermissionsExt,
    path::{Path, PathBuf},
    process::{Child, Command, Output, Stdio},
    thread,
    time::{Duration, SystemTime, UNIX_EPOCH},
};

struct Scratch(PathBuf);
impl Scratch {
    fn new() -> Self {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "azdaja-site-installer-{}-{nonce}",
            std::process::id()
        ));
        fs::create_dir_all(&path).unwrap();
        Self(path)
    }
}
impl Drop for Scratch {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

struct FixtureServer {
    child: Child,
    base: String,
    log: PathBuf,
}
impl FixtureServer {
    fn start(scratch: &Path, root: &Path) -> Self {
        let script = scratch.join("fixture-server.py");
        let port_file = scratch.join("fixture-port");
        let log = scratch.join("fixture-http.log");
        fs::write(
            &script,
            r#"import functools
import http.server
import pathlib
import sys

root, port_file, log_file = map(pathlib.Path, sys.argv[1:])
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        with log_file.open("a", encoding="utf-8") as stream:
            stream.write(self.path + "\n")
handler = functools.partial(Handler, directory=str(root))
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
port_file.write_text(str(server.server_address[1]), encoding="ascii")
server.serve_forever()
"#,
        )
        .unwrap();
        let mut child = Command::new("python3")
            .arg(&script)
            .arg(root)
            .arg(&port_file)
            .arg(&log)
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .unwrap();
        for _ in 0..200 {
            if let Ok(port) = fs::read_to_string(&port_file) {
                return Self {
                    child,
                    base: format!("http://127.0.0.1:{}", port.trim()),
                    log,
                };
            }
            thread::sleep(Duration::from_millis(10));
        }
        let _ = child.kill();
        let _ = child.wait();
        panic!("fixture HTTP server did not start")
    }
}
impl Drop for FixtureServer {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

fn sha256(path: &Path) -> String {
    for (tool, args) in [("shasum", vec!["-a", "256"]), ("sha256sum", vec![])] {
        let output = Command::new(tool).args(args).arg(path).output();
        if let Ok(output) = output
            && output.status.success()
        {
            return String::from_utf8(output.stdout)
                .unwrap()
                .split_whitespace()
                .next()
                .unwrap()
                .to_string();
        }
    }
    panic!("no SHA-256 utility available");
}

fn local_candidate(scratch: &Path) -> PathBuf {
    const DOWNLOAD_CAP: u64 = 64 * 1024 * 1024;
    let candidate = scratch.join("fixture-azdaja");
    fs::copy(env!("CARGO_BIN_EXE_azdaja"), &candidate).unwrap();
    fs::set_permissions(&candidate, fs::Permissions::from_mode(0o755)).unwrap();
    if fs::metadata(&candidate).unwrap().len() > DOWNLOAD_CAP {
        let status = Command::new("strip").arg(&candidate).status().unwrap();
        assert!(
            status.success(),
            "strip failed for oversized fixture binary"
        );
    }
    assert!(fs::metadata(&candidate).unwrap().len() <= DOWNLOAD_CAP);
    candidate
}

fn write_release(root: &Path, name: &str, candidate: &Path, digest: &str) {
    let release = root.join(name);
    fs::create_dir_all(&release).unwrap();
    for asset in ["azdaja-v0.1.2-darwin-arm64", "azdaja-v0.1.2-linux-x86_64"] {
        fs::copy(candidate, release.join(asset)).unwrap();
    }
    fs::write(
        release.join("SHA256SUMS"),
        format!("{digest}  azdaja-v0.1.2-darwin-arm64\n{digest}  azdaja-v0.1.2-linux-x86_64\n"),
    )
    .unwrap();
}

struct InstallRun<'a> {
    home: &'a Path,
    base: &'a str,
    os: &'a str,
    arch: &'a str,
    harness: Option<&'a str>,
    bin_dir: Option<&'a Path>,
    path: &'a str,
}
fn run_installer(run: InstallRun<'_>) -> Output {
    let script = Path::new(env!("CARGO_MANIFEST_DIR")).join("site/install");
    let mut command = Command::new("sh");
    command
        .arg(script)
        .env("HOME", run.home)
        .env("XDG_CONFIG_HOME", run.home.join(".config"))
        .env("PATH", run.path)
        .env("AZDAJA_INSTALL_TEST_MODE", "local")
        .env("AZDAJA_INSTALL_BASE_URL", run.base)
        .env("AZDAJA_INSTALL_OS", run.os)
        .env("AZDAJA_INSTALL_ARCH", run.arch)
        .env_remove("AZDAJA_CONFIG")
        .env_remove("AZDAJA_HOME")
        .env_remove("RLM_DEPTH")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    if let Some(harness) = run.harness {
        command.args(["--harness", harness]);
    }
    if let Some(bin_dir) = run.bin_dir {
        command.arg("--bin-dir").arg(bin_dir);
    }
    command.output().unwrap()
}
fn assert_success(output: &Output) -> String {
    assert!(
        output.status.success(),
        "status={} stdout={} stderr={}",
        output.status,
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(output.stderr.is_empty());
    String::from_utf8(output.stdout.clone()).unwrap()
}
fn target(home: &Path, harness: &str) -> PathBuf {
    match harness {
        "jcode" => home.join(".jcode/skills/azdaja"),
        "claude" => home.join(".claude/skills/azdaja"),
        "codex" => home.join(".agents/skills/azdaja"),
        "gemini" => home.join(".gemini/skills/azdaja"),
        _ => home.join(".config/opencode/skills/azdaja"),
    }
}
fn mark_detected(home: &Path, harness: &str) {
    let path = match harness {
        "jcode" => home.join(".jcode"),
        "claude" => home.join(".claude"),
        "codex" => home.join(".codex"),
        "gemini" => home.join(".gemini"),
        _ => home.join(".config/opencode"),
    };
    fs::create_dir_all(path).unwrap();
}

#[test]
fn installers_are_identical_and_bind_fresh_v012_assets_and_sums() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let site = fs::read(root.join("site/install")).unwrap();
    let top = fs::read(root.join("install.sh")).unwrap();
    assert_eq!(top, site);
    let text = String::from_utf8(site).unwrap();
    assert_eq!(text.matches("VERSION=0.1.2").count(), 1);
    assert!(text.contains("$BASE_URL/SHA256SUMS"));
    assert!(text.contains("azdaja-v$VERSION-darwin-arm64"));
    assert!(text.contains("azdaja-v$VERSION-linux-x86_64"));
    assert!(text.contains("Darwin-arm64)"));
    assert!(text.contains("Linux-x86_64)"));
    assert!(!text.contains("v0.1.1"));
    assert!(text.contains("mv -f \"$STAGED\" \"$DEST\""));
}

#[test]
fn local_http_fixture_covers_platform_checksum_atomic_path_and_selected_route() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    let digest = sha256(&candidate);
    write_release(&fixture_root, "good", &candidate, &digest);
    write_release(&fixture_root, "bad", &candidate, &"0".repeat(64));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let system_path = "/usr/bin:/bin";

    for (os, arch, asset) in [
        ("Darwin", "arm64", "azdaja-v0.1.2-darwin-arm64"),
        ("Linux", "x86_64", "azdaja-v0.1.2-linux-x86_64"),
    ] {
        let home = scratch.0.join(format!("platform-{os}"));
        let bin = home.join("bin");
        fs::create_dir_all(&home).unwrap();
        let output = run_installer(InstallRun {
            home: &home,
            base: &format!("{}/good", server.base),
            os,
            arch,
            harness: Some("claude"),
            bin_dir: Some(&bin),
            path: system_path,
        });
        let stdout = assert_success(&output);
        assert_eq!(stdout.lines().count(), 3, "{stdout}");
        assert!(stdout.contains(asset));
        assert!(stdout.contains("add ") && stdout.contains(" to PATH"));
        assert_eq!(sha256(&bin.join("azdaja")), digest);
        let active = fs::read_to_string(bin.join("config.toml")).unwrap();
        assert!(active.contains("claude -p --model {model}"));
        assert!(target(&home, "claude").join("azdaja").is_file());
    }
    let requests = fs::read_to_string(&server.log).unwrap();
    assert!(requests.contains("/good/SHA256SUMS"));
    assert!(requests.contains("/good/azdaja-v0.1.2-darwin-arm64"));
    assert!(requests.contains("/good/azdaja-v0.1.2-linux-x86_64"));

    let home = scratch.0.join("atomic-home");
    let bin = home.join("bin");
    fs::create_dir_all(&bin).unwrap();
    let existing = bin.join("azdaja");
    fs::write(&existing, b"existing-install-must-survive").unwrap();
    let bad = run_installer(InstallRun {
        home: &home,
        base: &format!("{}/bad", server.base),
        os: "Darwin",
        arch: "arm64",
        harness: Some("claude"),
        bin_dir: Some(&bin),
        path: system_path,
    });
    assert_eq!(bad.status.code(), Some(1));
    assert!(String::from_utf8_lossy(&bad.stderr).contains("SHA-256 mismatch"));
    assert_eq!(
        fs::read(&existing).unwrap(),
        b"existing-install-must-survive"
    );

    let good = run_installer(InstallRun {
        home: &home,
        base: &format!("{}/good", server.base),
        os: "Darwin",
        arch: "arm64",
        harness: Some("claude"),
        bin_dir: Some(&bin),
        path: system_path,
    });
    assert_success(&good);
    let version = Command::new(&existing).arg("--version").output().unwrap();
    assert!(String::from_utf8_lossy(&version.stdout).starts_with("azdaja 0.1.2 "));

    let home = scratch.0.join("path-home");
    let path_bin = home.join("path-bin");
    let tools = home.join("tools");
    fs::create_dir_all(&path_bin).unwrap();
    fs::create_dir_all(&tools).unwrap();
    let claude = tools.join("claude");
    fs::write(&claude, "#!/bin/sh\ncat >/dev/null\nprintf 'AZDAJA\\n'\n").unwrap();
    fs::set_permissions(&claude, fs::Permissions::from_mode(0o755)).unwrap();
    let path = format!("{}:{}:{system_path}", path_bin.display(), tools.display());
    let good = run_installer(InstallRun {
        home: &home,
        base: &format!("{}/good", server.base),
        os: "Darwin",
        arch: "arm64",
        harness: Some("claude"),
        bin_dir: None,
        path: &path,
    });
    let stdout = assert_success(&good);
    assert!(path_bin.join("azdaja").is_file());
    assert!(stdout.contains("is on PATH"));
    assert!(
        fs::read_to_string(path_bin.join("config.toml"))
            .unwrap()
            .contains("claude -p --model {model}")
    );
    let doctor = Command::new(path_bin.join("azdaja"))
        .arg("doctor")
        .env("HOME", &home)
        .env("PATH", &path)
        .env("AZDAJA_HOME", home.join("state"))
        .env_remove("AZDAJA_CONFIG")
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap();
    let stdout = assert_success(&doctor);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    assert!(stdout.lines().all(|line| line.starts_with("PASS ")));
}

#[test]
fn local_http_fixture_covers_each_detection_target_all_and_no_harness() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let base = format!("{}/good", server.base);
    let system_path = "/usr/bin:/bin";

    for harness in ["jcode", "claude", "codex", "gemini", "opencode"] {
        let home = scratch.0.join(format!("detected-{harness}"));
        let bin = home.join("bin");
        fs::create_dir_all(&home).unwrap();
        mark_detected(&home, harness);
        let output = run_installer(InstallRun {
            home: &home,
            base: &base,
            os: "Darwin",
            arch: "arm64",
            harness: None,
            bin_dir: Some(&bin),
            path: system_path,
        });
        let stdout = assert_success(&output);
        assert_eq!(stdout.lines().count(), 3, "{stdout}");
        assert!(stdout.lines().next().unwrap().contains(harness));
        assert!(target(&home, harness).join("azdaja").is_file());
        assert_eq!(
            fs::read(bin.join("config.toml")).unwrap(),
            fs::read(target(&home, harness).join("config.toml")).unwrap(),
            "PATH binary must bind the selected {harness} route"
        );
    }

    let home = scratch.0.join("all");
    let bin = home.join("bin");
    fs::create_dir_all(&home).unwrap();
    let output = run_installer(InstallRun {
        home: &home,
        base: &base,
        os: "Darwin",
        arch: "arm64",
        harness: Some("all"),
        bin_dir: Some(&bin),
        path: system_path,
    });
    let stdout = assert_success(&output);
    assert_eq!(stdout.lines().count(), 3);
    for harness in ["jcode", "claude", "codex", "gemini", "opencode"] {
        assert!(target(&home, harness).join("azdaja").is_file());
    }
    assert!(
        fs::read_to_string(bin.join("config.toml"))
            .unwrap()
            .contains("jcode-api")
    );

    let before = fs::read_to_string(&server.log).unwrap_or_default();
    let home = scratch.0.join("none");
    fs::create_dir(&home).unwrap();
    let output = run_installer(InstallRun {
        home: &home,
        base: &base,
        os: "Darwin",
        arch: "arm64",
        harness: None,
        bin_dir: Some(&home.join("bin")),
        path: system_path,
    });
    assert_eq!(output.status.code(), Some(1));
    assert!(output.stdout.is_empty());
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("no supported harness found"));
    assert!(!stderr.contains("stack"));
    assert!(fs::read_dir(&home).unwrap().next().is_none());
    assert_eq!(fs::read_to_string(&server.log).unwrap_or_default(), before);
}

#[test]
fn ordinary_installs_reject_validation_overrides_before_mutation() {
    let scratch = Scratch::new();
    let home = scratch.0.join("home");
    fs::create_dir(&home).unwrap();
    let output = Command::new("sh")
        .arg(Path::new(env!("CARGO_MANIFEST_DIR")).join("install.sh"))
        .args(["--harness", "claude"])
        .env("HOME", &home)
        .env("PATH", "/usr/bin:/bin")
        .env("AZDAJA_INSTALL_BASE_URL", "http://127.0.0.1:9")
        .env_remove("AZDAJA_INSTALL_TEST_MODE")
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("validation overrides require AZDAJA_INSTALL_TEST_MODE=local")
    );
    assert!(fs::read_dir(home).unwrap().next().is_none());
}
