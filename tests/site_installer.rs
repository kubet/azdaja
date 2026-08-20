#![cfg(unix)]

use std::{
    ffi::OsStr,
    fs,
    io::Write,
    os::unix::fs::{MetadataExt, PermissionsExt},
    path::{Path, PathBuf},
    process::{Child, Command, Output, Stdio},
    sync::atomic::{AtomicU64, Ordering},
    thread,
    time::{Duration, SystemTime, UNIX_EPOCH},
};

struct Scratch(PathBuf);
impl Scratch {
    fn new() -> Self {
        static NEXT: AtomicU64 = AtomicU64::new(0);
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "azdaja-site-installer-{}-{nonce}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
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
            if let Ok(port_text) = fs::read_to_string(&port_file)
                && let Ok(port) = port_text.trim().parse::<u16>()
                && port != 0
            {
                return Self {
                    child,
                    base: format!("http://127.0.0.1:{port}"),
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

const DOCUMENT_OWNER_V1: &[u8] = b"azdaja-installer-owned-docs-v1\n";
const DOCUMENT_OWNER_V2: &[u8] = b"azdaja-installer-owned-docs-v2\n\
schema=azdaja-managed-documents-v2\n\
LICENSE.sha256=45dd135e23e0e915b3dd61095d46eb45a8f59bbc53dadface6affbd1c76d7096\n\
THIRD-PARTY-NOTICES.md.sha256=ee908558c8d5f0d2080400558db351d8f24fb7ad3ca902c904822d97d7b5eac6\n";

fn sha256_bytes(bytes: &[u8]) -> String {
    for (tool, args) in [("shasum", vec!["-a", "256"]), ("sha256sum", vec![])] {
        let mut child = match Command::new(tool)
            .args(args)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .spawn()
        {
            Ok(child) => child,
            Err(_) => continue,
        };
        child.stdin.take().unwrap().write_all(bytes).unwrap();
        let output = child.wait_with_output().unwrap();
        if output.status.success() {
            return String::from_utf8(output.stdout)
                .unwrap()
                .split_whitespace()
                .next()
                .unwrap()
                .to_owned();
        }
    }
    panic!("no SHA-256 utility available")
}

fn legacy_notices() -> Option<Vec<u8>> {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let revisions = Command::new("git")
        .current_dir(root)
        .args([
            "log",
            "--all",
            "--format=%H",
            "--",
            "THIRD-PARTY-NOTICES.md",
        ])
        .output()
        .ok()?;
    if !revisions.status.success() {
        return None;
    }
    for revision in String::from_utf8(revisions.stdout).ok()?.lines() {
        let object = format!("{revision}:THIRD-PARTY-NOTICES.md");
        let candidate = Command::new("git")
            .current_dir(root)
            .args(["show", &object])
            .output()
            .ok()?;
        if candidate.status.success()
            && sha256_bytes(&candidate.stdout)
                == "dde4b0d189ff4fbc79748212bc0fc90bbf75dd27a4f23aaddbb24624e6e8cabb"
        {
            return Some(candidate.stdout);
        }
    }
    // Parentless public snapshots intentionally have no predecessor object history.
    None
}

fn write_managed_documents(directory: &Path, marker: &[u8], notices: &[u8]) {
    fs::create_dir_all(directory).unwrap();
    fs::write(directory.join("LICENSE"), include_bytes!("../LICENSE")).unwrap();
    fs::write(directory.join("THIRD-PARTY-NOTICES.md"), notices).unwrap();
    fs::write(directory.join(".azdaja-managed"), marker).unwrap();
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
    let source = Path::new(env!("CARGO_MANIFEST_DIR"));
    fs::copy(source.join("LICENSE"), release.join("LICENSE")).unwrap();
    fs::copy(
        source.join("THIRD-PARTY-NOTICES.md"),
        release.join("THIRD-PARTY-NOTICES.md"),
    )
    .unwrap();
    let license_digest = sha256(&release.join("LICENSE"));
    let notices_digest = sha256(&release.join("THIRD-PARTY-NOTICES.md"));
    fs::write(
        release.join("SHA256SUMS"),
        format!(
            "{digest}  azdaja-v0.1.2-darwin-arm64\n{digest}  azdaja-v0.1.2-linux-x86_64\n{license_digest}  LICENSE\n{notices_digest}  THIRD-PARTY-NOTICES.md\n"
        ),
    )
    .unwrap();
}

struct InstallRun<'a> {
    home: &'a Path,
    base: &'a str,
    os: &'a str,
    arch: &'a str,
    glibc_version: Option<&'a str>,
    harness: Option<&'a str>,
    bin_dir: Option<&'a Path>,
    path: &'a str,
}
fn run_installer_with_jcode_home(run: InstallRun<'_>, jcode_home: Option<&Path>) -> Output {
    let script = Path::new(env!("CARGO_MANIFEST_DIR")).join("site/install");
    let mut command = Command::new("sh");
    command
        .arg(script)
        .env("HOME", run.home)
        .env("XDG_CONFIG_HOME", run.home.join(".config"))
        .env_remove("XDG_DATA_HOME")
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
    if let Some(glibc_version) = run.glibc_version {
        command.env("AZDAJA_INSTALL_GLIBC_VERSION", glibc_version);
    } else {
        command.env_remove("AZDAJA_INSTALL_GLIBC_VERSION");
    }
    if let Some(jcode_home) = jcode_home {
        command.env("JCODE_HOME", jcode_home);
    } else {
        command.env_remove("JCODE_HOME");
    }
    if let Some(harness) = run.harness {
        command.args(["--harness", harness]);
    }
    if let Some(bin_dir) = run.bin_dir {
        command.arg("--bin-dir").arg(bin_dir);
    }
    command.output().unwrap()
}
fn run_installer(run: InstallRun<'_>) -> Output {
    run_installer_with_jcode_home(run, None)
}

fn run_installer_with_extra(run: InstallRun<'_>, extra: &[(&str, &OsStr)]) -> Output {
    let script = Path::new(env!("CARGO_MANIFEST_DIR")).join("site/install");
    let mut command = Command::new("sh");
    command
        .arg(script)
        .env("HOME", run.home)
        .env("XDG_CONFIG_HOME", run.home.join(".config"))
        .env_remove("XDG_DATA_HOME")
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
    if let Some(glibc_version) = run.glibc_version {
        command.env("AZDAJA_INSTALL_GLIBC_VERSION", glibc_version);
    } else {
        command.env_remove("AZDAJA_INSTALL_GLIBC_VERSION");
    }
    if let Some(harness) = run.harness {
        command.args(["--harness", harness]);
    }
    if let Some(bin_dir) = run.bin_dir {
        command.arg("--bin-dir").arg(bin_dir);
    }
    for (name, value) in extra {
        command.env(name, value);
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

fn write_executable(path: &Path, contents: &str) {
    fs::write(path, contents).unwrap();
    fs::set_permissions(path, fs::Permissions::from_mode(0o755)).unwrap();
}

#[derive(Debug, Eq, PartialEq)]
struct PathIdentity {
    relative: PathBuf,
    kind: &'static str,
    device: u64,
    inode: u64,
    links: u64,
    mode: u32,
    bytes_or_target: Vec<u8>,
}

fn tree_identity(root: &Path) -> Vec<PathIdentity> {
    fn visit(root: &Path, path: &Path, entries: &mut Vec<PathIdentity>) {
        let metadata = fs::symlink_metadata(path).unwrap();
        let file_type = metadata.file_type();
        let (kind, bytes_or_target) = if file_type.is_symlink() {
            (
                "symlink",
                fs::read_link(path)
                    .unwrap()
                    .as_os_str()
                    .to_string_lossy()
                    .as_bytes()
                    .to_vec(),
            )
        } else if file_type.is_file() {
            ("file", fs::read(path).unwrap())
        } else {
            ("directory", Vec::new())
        };
        entries.push(PathIdentity {
            relative: path.strip_prefix(root).unwrap().to_path_buf(),
            kind,
            device: metadata.dev(),
            inode: metadata.ino(),
            links: metadata.nlink(),
            mode: metadata.mode(),
            bytes_or_target,
        });
        if file_type.is_dir() {
            let mut children: Vec<_> = fs::read_dir(path)
                .unwrap()
                .map(|entry| entry.unwrap().path())
                .collect();
            children.sort();
            for child in children {
                visit(root, &child, entries);
            }
        }
    }

    let mut entries = Vec::new();
    visit(root, root, &mut entries);
    entries
}

fn installed_output(binary: &Path, home: &Path, path: &str, args: &[&str]) -> Output {
    Command::new(binary)
        .args(args)
        .env("HOME", home)
        .env("PATH", path)
        .env("AZDAJA_HOME", home.join("state"))
        .env(
            "AZDAJA_CONFIG",
            binary.parent().unwrap().join("azdaja-config.toml"),
        )
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap()
}

fn assert_owned_adjacent_config(bin: &Path) {
    assert!(bin.join("azdaja-config.toml").is_file());
    assert_eq!(
        fs::read(bin.join("azdaja-config.toml.managed")).unwrap(),
        b"azdaja-installer-owned-config-v1\n"
    );
}

fn shell_quoted(path: &Path) -> String {
    format!("'{}'", path.to_string_lossy().replace('\'', "'\\''"))
}

fn assert_off_path_doctor(next: &str, bin: &Path) {
    let literal = bin.join("azdaja");
    let canonical = fs::canonicalize(bin).unwrap().join("azdaja");
    assert!(
        [literal, canonical]
            .iter()
            .any(|absolute| next.starts_with(&format!(
                "Next: run {} doctor, then ",
                shell_quoted(absolute)
            ))),
        "{next}"
    );
    assert!(
        next.contains("; add ") && next.contains(" to PATH"),
        "{next}"
    );
}

fn assert_alias_identity_and_local_caps(home: &Path, bin: &Path, path: &str) {
    assert_owned_adjacent_config(bin);
    let long = bin.join("azdaja");
    let short = bin.join("az");
    assert_eq!(fs::read_link(&short).unwrap(), PathBuf::from("azdaja"));
    for args in [vec!["--version"], Vec::new(), vec!["doctor", "--caps"]] {
        let long_output = installed_output(&long, home, path, &args);
        let short_output = installed_output(&short, home, path, &args);
        assert_eq!(short_output.status, long_output.status, "args={args:?}");
        assert_eq!(short_output.stdout, long_output.stdout, "args={args:?}");
        assert_eq!(short_output.stderr, long_output.stderr, "args={args:?}");
        assert!(short_output.status.success(), "args={args:?}");
        if args.is_empty() {
            let help = String::from_utf8(short_output.stdout).unwrap();
            assert_eq!(
                help,
                "AZDAJA v0.1.2 — virtual memory for language models\nUsage: az <command> [options]  (azdaja also works)\nCommands: start load exec final list kill solo install doctor uninstall\nSetup: az install --harness <jcode|claude|codex|gemini|opencode|all>\nExample: az solo \"summarize this file\" -f ./document.txt\n"
            );
        }
    }
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
    assert!(text.contains("GLIBC_MIN=2.35"));
    assert!(text.contains("getconf GNU_LIBC_VERSION"));
    assert!(text.contains("AZDAJA_INSTALL_GLIBC_VERSION is required"));
    assert!(!text.contains("v0.1.1"));
    assert!(text.contains("mv -f \"$STAGED\" \"$DEST\""));
    assert!(text.contains("ln -s azdaja \"$ALIAS\""));
    assert!(text.contains("PATH_AZ=$PATH_ENTRY/az"));
    assert!(text.contains("short alias skipped"));
    assert!(text.contains("azdaja-config.toml.managed"));
    assert!(!text.contains("\"$BIN_DIR/config.toml\""));
    assert!(text.contains("run az doctor"));
    assert!(text.contains("run azdaja doctor"));
}

#[test]
fn linux_glibc_floor_refuses_below_and_accepts_exact_boundary_and_above() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);

    let curl_log = scratch.0.join("refusal-curl.log");
    let tools = scratch.0.join("refusal-tools");
    fs::create_dir(&tools).unwrap();
    write_executable(
        &tools.join("curl"),
        &format!(
            "#!/bin/sh\nprintf '%s\\n' invoked >> '{}'\nexit 97\n",
            curl_log.display()
        ),
    );
    let refusal_path = format!("{}:/usr/bin:/bin", tools.display());
    let below_home = scratch.0.join("glibc-below");
    fs::create_dir(&below_home).unwrap();
    let before = tree_identity(&below_home);
    let below = run_installer(InstallRun {
        home: &below_home,
        base: &format!("{}/good", server.base),
        os: "Linux",
        arch: "x86_64",
        glibc_version: Some("2.34"),
        harness: Some("claude"),
        bin_dir: Some(&below_home.join("bin")),
        path: &refusal_path,
    });
    assert_eq!(below.status.code(), Some(1));
    assert!(below.stdout.is_empty());
    let stderr = String::from_utf8_lossy(&below.stderr);
    assert!(stderr.contains("requires glibc 2.35 or newer"), "{stderr}");
    assert!(stderr.contains("found glibc 2.34"), "{stderr}");
    assert!(
        stderr.contains("build from source with Rust 1.95"),
        "{stderr}"
    );
    assert_eq!(tree_identity(&below_home), before);
    assert!(!curl_log.exists(), "curl was invoked before libc refusal");
    assert!(
        !server.log.exists(),
        "a download was requested before libc refusal"
    );

    for version in ["2.35", "2.36"] {
        let home = scratch
            .0
            .join(format!("glibc-{}", version.replace('.', "-")));
        let bin = home.join("bin");
        fs::create_dir(&home).unwrap();
        let output = run_installer(InstallRun {
            home: &home,
            base: &format!("{}/good", server.base),
            os: "Linux",
            arch: "x86_64",
            glibc_version: Some(version),
            harness: Some("claude"),
            bin_dir: Some(&bin),
            path: "/usr/bin:/bin",
        });
        let stdout = assert_success(&output);
        assert_eq!(stdout.lines().count(), 3, "version={version} {stdout}");
        assert!(bin.join("azdaja").is_file());
    }
}

#[test]
fn linux_local_selector_requires_fake_glibc_instead_of_reading_the_host() {
    let scratch = Scratch::new();
    let home = scratch.0.join("home");
    fs::create_dir(&home).unwrap();
    let before = tree_identity(&home);
    let output = run_installer(InstallRun {
        home: &home,
        base: "http://127.0.0.1:9",
        os: "Linux",
        arch: "x86_64",
        glibc_version: None,
        harness: Some("claude"),
        bin_dir: Some(&home.join("bin")),
        path: "/usr/bin:/bin",
    });
    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("AZDAJA_INSTALL_GLIBC_VERSION is required")
    );
    assert_eq!(tree_identity(&home), before);
}

#[test]
fn native_linux_musl_and_missing_getconf_refuse_without_curl_or_home_mutation() {
    let scratch = Scratch::new();
    let installer = Path::new(env!("CARGO_MANIFEST_DIR")).join("site/install");

    for libc in ["musl", "missing-getconf"] {
        let tools = scratch.0.join(format!("{libc}-tools"));
        let home = scratch.0.join(format!("{libc}-home"));
        let curl_log = scratch.0.join(format!("{libc}-curl.log"));
        fs::create_dir(&tools).unwrap();
        fs::create_dir(&home).unwrap();
        write_executable(
            &tools.join("uname"),
            "#!/bin/sh\ncase \"${1-}\" in\n  -s) printf '%s\\n' Linux ;;\n  -m) printf '%s\\n' x86_64 ;;\n  *) exit 2 ;;\nesac\n",
        );
        write_executable(
            &tools.join("curl"),
            &format!(
                "#!/bin/sh\nprintf '%s\\n' invoked >> '{}'\nexit 97\n",
                curl_log.display()
            ),
        );
        if libc == "musl" {
            write_executable(
                &tools.join("getconf"),
                "#!/bin/sh\nprintf '%s\\n' 'musl 1.2.5'\n",
            );
        }
        let before = tree_identity(&home);
        let output = Command::new("/bin/sh")
            .arg(&installer)
            .args(["--harness", "claude", "--bin-dir"])
            .arg(home.join("bin"))
            .env("HOME", &home)
            .env("PATH", &tools)
            .env_remove("AZDAJA_INSTALL_TEST_MODE")
            .env_remove("AZDAJA_INSTALL_BASE_URL")
            .env_remove("AZDAJA_INSTALL_OS")
            .env_remove("AZDAJA_INSTALL_ARCH")
            .env_remove("AZDAJA_INSTALL_GLIBC_VERSION")
            .output()
            .unwrap();
        assert_eq!(output.status.code(), Some(1), "libc={libc}");
        assert!(output.stdout.is_empty(), "libc={libc}");
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert!(stderr.contains("requires glibc 2.35 or newer"), "{stderr}");
        assert!(stderr.contains("getconf GNU_LIBC_VERSION"), "{stderr}");
        assert!(stderr.contains("musl is not supported"), "{stderr}");
        assert!(
            stderr.contains("build from source with Rust 1.95"),
            "{stderr}"
        );
        assert_eq!(tree_identity(&home), before, "libc={libc}");
        assert!(!curl_log.exists(), "libc={libc}: curl was invoked");
    }
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
            glibc_version: (os == "Linux").then_some("2.35"),
            harness: Some("claude"),
            bin_dir: Some(&bin),
            path: system_path,
        });
        let stdout = assert_success(&output);
        assert_eq!(stdout.lines().count(), 3, "{stdout}");
        assert!(stdout.contains(asset));
        assert!(stdout.contains("add ") && stdout.contains(" to PATH"));
        assert_eq!(sha256(&bin.join("azdaja")), digest);
        let active = fs::read_to_string(bin.join("azdaja-config.toml")).unwrap();
        assert!(active.contains("claude -p --model {model}"));
        assert!(target(&home, "claude").join("azdaja").is_file());
        assert!(stdout.contains("azdaja ->") && stdout.contains("az ->"));
        let next = stdout.lines().last().unwrap();
        assert_off_path_doctor(next, &bin);
        assert!(next.contains("restart Claude to reload its skills"));
        assert_alias_identity_and_local_caps(&home, &bin, system_path);
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
        glibc_version: None,
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
        glibc_version: None,
        harness: Some("claude"),
        bin_dir: Some(&bin),
        path: system_path,
    });
    assert_success(&good);
    let version = Command::new(&existing).arg("--version").output().unwrap();
    assert!(String::from_utf8_lossy(&version.stdout).starts_with("azdaja 0.1.2 "));
    assert_alias_identity_and_local_caps(&home, &bin, system_path);

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
        glibc_version: None,
        harness: Some("claude"),
        bin_dir: None,
        path: &path,
    });
    let stdout = assert_success(&good);
    assert!(path_bin.join("azdaja").is_file());
    assert!(stdout.contains("is on PATH"));
    assert!(
        stdout
            .lines()
            .last()
            .unwrap()
            .contains("az doctor, then restart Claude to reload its skills")
    );
    assert_alias_identity_and_local_caps(&home, &path_bin, &path);
    assert!(
        fs::read_to_string(path_bin.join("azdaja-config.toml"))
            .unwrap()
            .contains("claude -p --model {model}")
    );
    let doctor = Command::new(path_bin.join("azdaja"))
        .arg("doctor")
        .env("HOME", &home)
        .env("PATH", &path)
        .env("AZDAJA_HOME", home.join("state"))
        .env("AZDAJA_CONFIG", path_bin.join("azdaja-config.toml"))
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap();
    let stdout = assert_success(&doctor);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    assert!(stdout.lines().all(|line| line.starts_with("PASS ")));
}

#[test]
fn standalone_installer_honors_authoritative_custom_jcode_home() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let home = scratch.0.join("custom-jcode-home");
    let custom = scratch.0.join("Jcode root ☃ ' with spaces");
    let bin = home.join("custom bin ☃ ' path");
    fs::create_dir_all(&custom).unwrap();
    let output = run_installer_with_jcode_home(
        InstallRun {
            home: &home,
            base: &format!("{}/good", server.base),
            os: "Linux",
            arch: "x86_64",
            glibc_version: Some("2.35"),
            harness: None,
            bin_dir: Some(&bin),
            path: "/usr/bin:/bin",
        },
        Some(&custom),
    );
    let stdout = assert_success(&output);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    assert!(stdout.lines().next().unwrap().contains("jcode"));
    assert!(custom.join("skills/azdaja/azdaja").is_file());
    assert!(!home.join(".jcode/skills/azdaja").exists());
    let next = stdout.lines().last().unwrap();
    assert_off_path_doctor(next, &bin);
    assert!(next.contains("skill_manage reload_all"), "{next}");

    // Extract the advertised command exactly as a user would. A deliberately
    // missing config makes doctor stop before evaluator/provider work while
    // still proving the spaces/Unicode/apostrophe shell quoting is executable.
    let command = next
        .strip_prefix("Next: run ")
        .unwrap()
        .split_once(", then ")
        .unwrap()
        .0;
    let missing_config = home.join("missing-provider-free-config.toml");
    let executed = Command::new("sh")
        .args(["-c", command])
        .env("HOME", &home)
        .env("JCODE_HOME", &custom)
        .env("XDG_CONFIG_HOME", home.join(".config"))
        .env("AZDAJA_HOME", home.join("quoted-command-state"))
        .env("AZDAJA_CONFIG", &missing_config)
        .env("PATH", "/usr/bin:/bin")
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap();
    assert_eq!(executed.status.code(), Some(1));
    assert!(executed.stderr.is_empty());
    assert!(
        String::from_utf8(executed.stdout)
            .unwrap()
            .starts_with(&format!(
                "FAIL config: {}: file is missing",
                missing_config.display()
            ))
    );

    let doctor = Command::new(bin.join("azdaja"))
        .args(["doctor", "--harness", "jcode"])
        .env("HOME", &home)
        .env("JCODE_HOME", &custom)
        .env("XDG_CONFIG_HOME", home.join(".config"))
        .env("AZDAJA_HOME", home.join("state"))
        .env("PATH", "/usr/bin:/bin")
        .env_remove("AZDAJA_CONFIG")
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap();
    assert!(assert_success(&doctor).contains("installed on disk"));
}

#[test]
fn local_fixture_alias_delta_matrix_covers_platform_routes_and_update_states() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let base = format!("{}/good", server.base);
    let system_path = "/usr/bin:/bin";
    let mut positive_cells = 0;
    let mut expected_refusals = 0;

    for (os, arch) in [("Darwin", "arm64"), ("Linux", "x86_64")] {
        for harness in ["jcode", "claude", "codex", "gemini", "opencode"] {
            let home = scratch.0.join(format!("matrix-{os}-detected-{harness}"));
            let bin = home.join("bin");
            fs::create_dir_all(&home).unwrap();
            mark_detected(&home, harness);
            let output = run_installer(InstallRun {
                home: &home,
                base: &base,
                os,
                arch,
                glibc_version: (os == "Linux").then_some("2.35"),
                harness: None,
                bin_dir: Some(&bin),
                path: system_path,
            });
            let stdout = assert_success(&output);
            assert_eq!(stdout.lines().count(), 3, "{stdout}");
            assert!(stdout.lines().next().unwrap().contains(harness));
            assert!(stdout.contains("azdaja ->") && stdout.contains("az ->"));
            let reload = match harness {
                "jcode" => "skill_manage reload_all or /skills -> Reload all",
                "claude" => "restart Claude to reload its skills",
                "codex" => "restart Codex to reload its skills",
                "gemini" => "restart Gemini to reload its skills",
                _ => "restart OpenCode to reload its skills",
            };
            let next = stdout.lines().last().unwrap();
            assert_off_path_doctor(next, &bin);
            assert!(next.contains(reload), "harness={harness} next={next}");
            assert!(target(&home, harness).join("azdaja").is_file());
            assert_eq!(
                fs::read(bin.join("azdaja-config.toml")).unwrap(),
                fs::read(target(&home, harness).join("config.toml")).unwrap(),
                "PATH binary must bind the selected {harness} route"
            );
            assert_alias_identity_and_local_caps(&home, &bin, system_path);
            positive_cells += 1;
        }

        let home = scratch.0.join(format!("matrix-{os}-all"));
        let bin = home.join("bin");
        fs::create_dir_all(&home).unwrap();
        let output = run_installer(InstallRun {
            home: &home,
            base: &base,
            os,
            arch,
            glibc_version: (os == "Linux").then_some("2.35"),
            harness: Some("all"),
            bin_dir: Some(&bin),
            path: system_path,
        });
        let stdout = assert_success(&output);
        assert_eq!(stdout.lines().count(), 3, "{stdout}");
        let next = stdout.lines().last().unwrap();
        assert_off_path_doctor(next, &bin);
        assert!(next.contains("reload/restart all five harnesses"));
        for harness in ["jcode", "claude", "codex", "gemini", "opencode"] {
            assert!(target(&home, harness).join("azdaja").is_file());
        }
        assert!(
            fs::read_to_string(bin.join("azdaja-config.toml"))
                .unwrap()
                .contains("jcode-api")
        );
        assert_alias_identity_and_local_caps(&home, &bin, system_path);
        positive_cells += 1;

        let before = fs::read_to_string(&server.log).unwrap_or_default();
        let home = scratch.0.join(format!("matrix-{os}-none"));
        fs::create_dir(&home).unwrap();
        let output = run_installer(InstallRun {
            home: &home,
            base: &base,
            os,
            arch,
            glibc_version: (os == "Linux").then_some("2.35"),
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
        expected_refusals += 1;

        let home = scratch.0.join(format!("matrix-{os}-already-installed"));
        let bin = home.join("bin");
        fs::create_dir_all(&bin).unwrap();
        fs::write(bin.join("azdaja"), b"old-managed-binary").unwrap();
        std::os::unix::fs::symlink("azdaja", bin.join("az")).unwrap();
        let output = run_installer(InstallRun {
            home: &home,
            base: &base,
            os,
            arch,
            glibc_version: (os == "Linux").then_some("2.35"),
            harness: Some("claude"),
            bin_dir: Some(&bin),
            path: system_path,
        });
        assert_success(&output);
        assert_alias_identity_and_local_caps(&home, &bin, system_path);
        assert_ne!(fs::read(bin.join("azdaja")).unwrap(), b"old-managed-binary");
        // A second update proves the exact managed link is accepted idempotently.
        let output = run_installer(InstallRun {
            home: &home,
            base: &base,
            os,
            arch,
            glibc_version: (os == "Linux").then_some("2.35"),
            harness: Some("claude"),
            bin_dir: Some(&bin),
            path: system_path,
        });
        assert_success(&output);
        assert_alias_identity_and_local_caps(&home, &bin, system_path);
        positive_cells += 1;
    }

    assert_eq!(positive_cells, 14);
    assert_eq!(expected_refusals, 2);
}

#[test]
fn alias_safety_failures_leave_home_and_foreign_paths_unchanged() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    let digest = sha256(&candidate);
    write_release(&fixture_root, "good", &candidate, &digest);
    write_release(&fixture_root, "bad", &candidate, &"0".repeat(64));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let system_path = "/usr/bin:/bin";

    let home = scratch.0.join("checksum-home");
    fs::create_dir(&home).unwrap();
    let output = run_installer(InstallRun {
        home: &home,
        base: &format!("{}/bad", server.base),
        os: "Darwin",
        arch: "arm64",
        glibc_version: None,
        harness: Some("claude"),
        bin_dir: Some(&home.join("bin")),
        path: system_path,
    });
    assert_eq!(output.status.code(), Some(1));
    assert!(String::from_utf8_lossy(&output.stderr).contains("SHA-256 mismatch"));
    assert!(fs::read_dir(&home).unwrap().next().is_none());

    let before_requests = fs::read_to_string(&server.log).unwrap_or_default();
    let home = scratch.0.join("unsupported-home");
    fs::create_dir(&home).unwrap();
    let output = run_installer(InstallRun {
        home: &home,
        base: &format!("{}/good", server.base),
        os: "Plan9",
        arch: "mips",
        glibc_version: None,
        harness: Some("claude"),
        bin_dir: Some(&home.join("bin")),
        path: system_path,
    });
    assert_eq!(output.status.code(), Some(1));
    assert!(String::from_utf8_lossy(&output.stderr).contains("unsupported platform"));
    assert!(fs::read_dir(&home).unwrap().next().is_none());
    assert_eq!(
        fs::read_to_string(&server.log).unwrap_or_default(),
        before_requests
    );

    for kind in ["regular", "symlink"] {
        let home = scratch.0.join(format!("foreign-{kind}-home"));
        let bin = home.join("bin");
        fs::create_dir_all(&bin).unwrap();
        let alias = bin.join("az");
        if kind == "regular" {
            fs::write(&alias, b"foreign-command").unwrap();
        } else {
            std::os::unix::fs::symlink("foreign-command", &alias).unwrap();
        }
        let output = run_installer(InstallRun {
            home: &home,
            base: &format!("{}/good", server.base),
            os: "Linux",
            arch: "x86_64",
            glibc_version: Some("2.35"),
            harness: Some("claude"),
            bin_dir: Some(&bin),
            path: system_path,
        });
        let stdout = assert_success(&output);
        assert_eq!(stdout.lines().count(), 3, "{stdout}");
        assert!(
            stdout
                .lines()
                .nth(1)
                .unwrap()
                .contains("short alias skipped")
        );
        let next = stdout.lines().last().unwrap();
        assert_off_path_doctor(next, &bin);
        assert!(next.contains("short alias skipped"));
        assert!(!stdout.contains("; az ->"));
        assert!(bin.join("azdaja").is_file());
        assert_owned_adjacent_config(&bin);
        assert_eq!(fs::read_dir(&bin).unwrap().count(), 4);
        if kind == "regular" {
            assert_eq!(fs::read(&alias).unwrap(), b"foreign-command");
        } else {
            assert_eq!(
                fs::read_link(&alias).unwrap(),
                PathBuf::from("foreign-command")
            );
        }
    }
}

#[test]
fn foreign_az_anywhere_on_path_skips_alias_without_changing_resolution() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);

    for position in ["earlier", "later"] {
        let home = scratch.0.join(format!("foreign-path-{position}"));
        let bin = home.join("bin");
        let foreign = home.join("azure-cli/bin");
        fs::create_dir_all(&bin).unwrap();
        fs::create_dir_all(&foreign).unwrap();
        if position == "later" {
            std::os::unix::fs::symlink("azdaja", bin.join("az")).unwrap();
        }
        let foreign_az = foreign.join("az");
        fs::write(&foreign_az, "#!/bin/sh\nprintf 'FOREIGN_AZ\\n'\n").unwrap();
        fs::set_permissions(&foreign_az, fs::Permissions::from_mode(0o755)).unwrap();
        let path = if position == "earlier" {
            format!("{}:{}:/usr/bin:/bin", foreign.display(), bin.display())
        } else {
            format!("{}:{}:/usr/bin:/bin", bin.display(), foreign.display())
        };
        let output = run_installer(InstallRun {
            home: &home,
            base: &format!("{}/good", server.base),
            os: "Darwin",
            arch: "arm64",
            glibc_version: None,
            harness: Some("claude"),
            bin_dir: Some(&bin),
            path: &path,
        });
        let stdout = assert_success(&output);
        assert_eq!(stdout.lines().count(), 3, "{stdout}");
        let written = stdout.lines().nth(1).unwrap();
        assert!(written.contains("short alias skipped"), "{written}");
        assert!(!written.contains("; az ->"), "{written}");
        assert!(stdout.lines().last().unwrap().contains("azdaja doctor"));
        assert!(!bin.join("az").exists());
        assert_owned_adjacent_config(&bin);

        let resolved = Command::new("sh")
            .args(["-c", "command -v az; az; command -v azdaja"])
            .env("PATH", &path)
            .output()
            .unwrap();
        let resolved = assert_success(&resolved);
        assert_eq!(
            resolved,
            format!(
                "{}\nFOREIGN_AZ\n{}\n",
                foreign_az.display(),
                bin.join("azdaja").display()
            )
        );
    }
}

#[test]
fn adjacent_config_ownership_preserves_custom_state_and_generic_config() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let home = scratch.0.join("owned-config-home");
    let bin = home.join("bin");
    fs::create_dir_all(&bin).unwrap();
    fs::write(bin.join("config.toml"), b"unrelated = 'keep-me'\n").unwrap();
    let run = || {
        run_installer(InstallRun {
            home: &home,
            base: &format!("{}/good", server.base),
            os: "Linux",
            arch: "x86_64",
            glibc_version: Some("2.35"),
            harness: Some("claude"),
            bin_dir: Some(&bin),
            path: "/usr/bin:/bin",
        })
    };

    assert_success(&run());
    assert_owned_adjacent_config(&bin);
    assert_eq!(
        fs::read(bin.join("config.toml")).unwrap(),
        b"unrelated = 'keep-me'\n"
    );
    let custom = format!(
        "# user-owned customization\n{}",
        fs::read_to_string(bin.join("azdaja-config.toml")).unwrap()
    );
    fs::write(bin.join("azdaja-config.toml"), custom.as_bytes()).unwrap();
    let stdout = assert_success(&run());
    assert!(
        stdout
            .lines()
            .nth(1)
            .unwrap()
            .contains("config preserved ->")
    );
    assert_eq!(
        fs::read(bin.join("azdaja-config.toml")).unwrap(),
        custom.as_bytes()
    );
    assert_eq!(
        fs::read(bin.join("config.toml")).unwrap(),
        b"unrelated = 'keep-me'\n"
    );
    assert_alias_identity_and_local_caps(&home, &bin, "/usr/bin:/bin");
}

#[test]
fn ambiguous_adjacent_config_states_refuse_before_install_mutation() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);

    for scenario in [
        "config-only",
        "marker-only",
        "unknown-marker",
        "config-symlink",
        "marker-symlink",
    ] {
        let home = scratch.0.join(format!("config-collision-{scenario}"));
        let bin = home.join("bin");
        fs::create_dir_all(&bin).unwrap();
        let config = bin.join("azdaja-config.toml");
        let marker = bin.join("azdaja-config.toml.managed");
        match scenario {
            "config-only" => fs::write(&config, b"foreign\n").unwrap(),
            "marker-only" => fs::write(&marker, b"azdaja-installer-owned-config-v1\n").unwrap(),
            "unknown-marker" => {
                fs::write(&config, b"foreign\n").unwrap();
                fs::write(&marker, b"some-other-owner\n").unwrap();
            }
            "config-symlink" => {
                std::os::unix::fs::symlink("foreign-config", &config).unwrap();
                fs::write(&marker, b"azdaja-installer-owned-config-v1\n").unwrap();
            }
            _ => {
                fs::write(&config, b"foreign\n").unwrap();
                std::os::unix::fs::symlink("foreign-owner", &marker).unwrap();
            }
        }
        let before_config = fs::symlink_metadata(&config).ok().map(|m| m.file_type());
        let before_marker = fs::symlink_metadata(&marker).ok().map(|m| m.file_type());
        let output = run_installer(InstallRun {
            home: &home,
            base: &format!("{}/good", server.base),
            os: "Linux",
            arch: "x86_64",
            glibc_version: Some("2.35"),
            harness: Some("claude"),
            bin_dir: Some(&bin),
            path: "/usr/bin:/bin",
        });
        assert_eq!(output.status.code(), Some(1), "scenario={scenario}");
        assert!(output.stdout.is_empty(), "scenario={scenario}");
        assert!(
            String::from_utf8_lossy(&output.stderr).contains("refusing"),
            "scenario={scenario} stderr={}",
            String::from_utf8_lossy(&output.stderr)
        );
        assert!(!bin.join("azdaja").exists());
        assert!(!bin.join("az").exists());
        assert!(!target(&home, "claude").exists());
        assert_eq!(
            fs::symlink_metadata(&config).ok().map(|m| m.file_type()),
            before_config,
            "scenario={scenario}"
        );
        assert_eq!(
            fs::symlink_metadata(&marker).ok().map(|m| m.file_type()),
            before_marker,
            "scenario={scenario}"
        );
    }
}

#[test]
fn unowned_hardlinked_harness_refuses_without_inode_link_or_mode_mutation() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let home = scratch.0.join("hardlink-refusal-home");
    let bin = home.join("bin");
    fs::create_dir_all(&bin).unwrap();
    let prior_binary = bin.join("azdaja");
    fs::write(&prior_binary, b"old-binary-must-not-move").unwrap();
    fs::set_permissions(&prior_binary, fs::Permissions::from_mode(0o740)).unwrap();
    std::os::unix::fs::symlink("azdaja", bin.join("az")).unwrap();

    let harness = target(&home, "claude");
    fs::create_dir_all(&harness).unwrap();
    fs::set_permissions(&harness, fs::Permissions::from_mode(0o750)).unwrap();
    let outside = home.join("outside-hardlink-victim");
    fs::write(&outside, b"outside-inode-must-survive").unwrap();
    fs::set_permissions(&outside, fs::Permissions::from_mode(0o640)).unwrap();
    fs::hard_link(&outside, harness.join("foreign-hardlink")).unwrap();
    let before = tree_identity(&home);
    assert_eq!(fs::metadata(&outside).unwrap().nlink(), 2);

    let output = run_installer(InstallRun {
        home: &home,
        base: &format!("{}/good", server.base),
        os: "Darwin",
        arch: "arm64",
        glibc_version: None,
        harness: Some("claude"),
        bin_dir: Some(&bin),
        path: "/usr/bin:/bin",
    });
    assert!(!output.status.success());
    assert!(output.stdout.is_empty());
    assert!(String::from_utf8_lossy(&output.stderr).contains("refusing"));
    assert_eq!(tree_identity(&home), before);
    assert_eq!(fs::metadata(&outside).unwrap().nlink(), 2);
    assert!(!bin.join("azdaja-config.toml").exists());
    assert!(!bin.join("azdaja-config.toml.managed").exists());
}

#[test]
fn symlinked_harness_target_refuses_without_touching_link_or_target() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let home = scratch.0.join("symlink-refusal-home");
    let bin = home.join("bin");
    let skills = home.join(".claude/skills");
    let outside = home.join("outside-directory");
    fs::create_dir_all(&bin).unwrap();
    fs::create_dir_all(&skills).unwrap();
    fs::create_dir_all(&outside).unwrap();
    fs::write(outside.join("unknown"), b"preserve").unwrap();
    fs::set_permissions(&outside, fs::Permissions::from_mode(0o750)).unwrap();
    std::os::unix::fs::symlink(&outside, skills.join("azdaja")).unwrap();
    let before = tree_identity(&home);

    let output = run_installer(InstallRun {
        home: &home,
        base: &format!("{}/good", server.base),
        os: "Linux",
        arch: "x86_64",
        glibc_version: Some("2.35"),
        harness: Some("claude"),
        bin_dir: Some(&bin),
        path: "/usr/bin:/bin",
    });
    assert!(!output.status.success());
    assert!(output.stdout.is_empty());
    assert!(String::from_utf8_lossy(&output.stderr).contains("refusing"));
    assert_eq!(tree_identity(&home), before);
}

#[test]
fn all_harness_preflight_refuses_unknown_late_target_before_valid_first_target_changes() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let home = scratch.0.join("multi-target-refusal-home");
    let bin = home.join("bin");
    fs::create_dir_all(&home).unwrap();

    let initial = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args(["install", "--harness", "jcode"])
        .env("HOME", &home)
        .env("XDG_CONFIG_HOME", home.join(".config"))
        .env_remove("AZDAJA_CONFIG")
        .env_remove("AZDAJA_HOME")
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap();
    assert_success(&initial);
    let claude = target(&home, "claude");
    fs::create_dir_all(&claude).unwrap();
    fs::write(claude.join("unknown"), b"unowned-late-target").unwrap();
    fs::set_permissions(&claude, fs::Permissions::from_mode(0o550)).unwrap();
    let before = tree_identity(&home);

    let output = run_installer(InstallRun {
        home: &home,
        base: &format!("{}/good", server.base),
        os: "Linux",
        arch: "x86_64",
        glibc_version: Some("2.35"),
        harness: Some("all"),
        bin_dir: Some(&bin),
        path: "/usr/bin:/bin",
    });
    assert!(!output.status.success());
    assert!(output.stdout.is_empty());
    assert!(String::from_utf8_lossy(&output.stderr).contains("refusing"));
    assert_eq!(tree_identity(&home), before);
    assert!(
        !bin.exists(),
        "standalone bin directory was created before refusal"
    );
}

#[test]
fn installed_alias_matches_solo_through_a_provider_free_fixture() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let home = scratch.0.join("solo-home");
    let bin = home.join("bin");
    let tools = home.join("tools");
    fs::create_dir_all(&tools).unwrap();
    let claude = tools.join("claude");
    fs::write(
        &claude,
        "#!/bin/sh\ncat >/dev/null\nif [ \"${RLM_DEPTH:-}\" = 0 ]; then\n  printf '%s\\n' '```python' 'FINAL(\"ALIAS_SOLO_OK\")' '```'\nelse\n  printf 'AZDAJA\\n'\nfi\n",
    )
    .unwrap();
    fs::set_permissions(&claude, fs::Permissions::from_mode(0o755)).unwrap();
    let path = format!("{}:/usr/bin:/bin", tools.display());
    let output = run_installer(InstallRun {
        home: &home,
        base: &format!("{}/good", server.base),
        os: "Darwin",
        arch: "arm64",
        glibc_version: None,
        harness: Some("claude"),
        bin_dir: Some(&bin),
        path: &path,
    });
    assert_success(&output);
    let input = home.join("input.txt");
    fs::write(&input, "synthetic alias parity input").unwrap();
    let args = [
        "solo",
        "return the fixture answer",
        "-f",
        input.to_str().unwrap(),
    ];
    let long = installed_output(&bin.join("azdaja"), &home, &path, &args);
    let short = installed_output(&bin.join("az"), &home, &path, &args);
    assert_success(&long);
    assert_success(&short);
    assert_eq!(short.stdout, long.stdout);
    assert_eq!(short.stderr, long.stderr);
    assert_eq!(String::from_utf8(short.stdout).unwrap(), "ALIAS_SOLO_OK\n");
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
        .env("AZDAJA_INSTALL_GLIBC_VERSION", "2.35")
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

#[test]
fn license_and_notice_checksum_missing_or_mismatch_is_zero_home_mutation() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    let digest = sha256(&candidate);
    for name in [
        "missing-license",
        "missing-notice",
        "bad-license",
        "bad-notice",
    ] {
        write_release(&fixture_root, name, &candidate, &digest);
    }
    for (name, needle) in [
        ("missing-license", "  LICENSE"),
        ("missing-notice", "  THIRD-PARTY-NOTICES.md"),
    ] {
        let sums = fixture_root.join(name).join("SHA256SUMS");
        let filtered = fs::read_to_string(&sums)
            .unwrap()
            .lines()
            .filter(|line| !line.ends_with(needle))
            .collect::<Vec<_>>()
            .join("\n")
            + "\n";
        fs::write(sums, filtered).unwrap();
    }
    fs::write(fixture_root.join("bad-license/LICENSE"), b"changed license").unwrap();
    fs::write(
        fixture_root.join("bad-notice/THIRD-PARTY-NOTICES.md"),
        b"changed notices",
    )
    .unwrap();
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    for name in [
        "missing-license",
        "missing-notice",
        "bad-license",
        "bad-notice",
    ] {
        let home = scratch.0.join(format!("home-{name}"));
        fs::create_dir(&home).unwrap();
        mark_detected(&home, "claude");
        let before = tree_identity(&home);
        let base = format!("{}/{name}", server.base);
        let output = run_installer(InstallRun {
            home: &home,
            base: &base,
            os: "Darwin",
            arch: "arm64",
            glibc_version: None,
            harness: Some("claude"),
            bin_dir: Some(&home.join("bin")),
            path: "/usr/bin:/bin",
        });
        assert!(!output.status.success(), "case={name}");
        assert_eq!(tree_identity(&home), before, "case={name}");
        assert!(!target(&home, "claude").exists(), "case={name}");
        assert!(!home.join(".local/share/azdaja").exists(), "case={name}");
    }
}

#[test]
fn foreign_document_directory_file_symlink_and_hardlink_refuse_without_mutation() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let base = format!("{}/good", server.base);
    for state in [
        "empty-directory",
        "foreign-entry",
        "regular-path",
        "symlink",
        "hardlink",
    ] {
        let home = scratch.0.join(format!("foreign-doc-{state}"));
        fs::create_dir(&home).unwrap();
        mark_detected(&home, "claude");
        let docs = home.join(".local/share/azdaja");
        fs::create_dir_all(docs.parent().unwrap()).unwrap();
        match state {
            "empty-directory" => fs::create_dir(&docs).unwrap(),
            "foreign-entry" => {
                fs::create_dir(&docs).unwrap();
                fs::write(docs.join("foreign"), b"keep").unwrap();
            }
            "regular-path" => fs::write(&docs, b"keep").unwrap(),
            "symlink" => {
                let victim = home.join("victim-docs");
                fs::create_dir(&victim).unwrap();
                fs::write(victim.join("keep"), b"keep").unwrap();
                std::os::unix::fs::symlink(&victim, &docs).unwrap();
            }
            "hardlink" => {
                fs::create_dir(&docs).unwrap();
                let source = home.join("license-hardlink-source");
                fs::write(&source, include_bytes!("../LICENSE")).unwrap();
                fs::hard_link(&source, docs.join("LICENSE")).unwrap();
                fs::write(
                    docs.join("THIRD-PARTY-NOTICES.md"),
                    include_bytes!("../THIRD-PARTY-NOTICES.md"),
                )
                .unwrap();
                fs::write(
                    docs.join(".azdaja-managed"),
                    b"azdaja-installer-owned-docs-v1\n",
                )
                .unwrap();
            }
            _ => unreachable!(),
        }
        let before = tree_identity(&home);
        let output = run_installer(InstallRun {
            home: &home,
            base: &base,
            os: "Darwin",
            arch: "arm64",
            glibc_version: None,
            harness: Some("claude"),
            bin_dir: Some(&home.join("bin")),
            path: "/usr/bin:/bin",
        });
        assert!(!output.status.success(), "state={state}");
        assert_eq!(tree_identity(&home), before, "state={state}");
    }
}

#[test]
fn exact_legacy_v1_documents_migrate_to_fixed_v2_and_reinstall_exactly() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let base = format!("{}/good", server.base);
    let home = scratch.0.join("legacy-home");
    fs::create_dir(&home).unwrap();
    mark_detected(&home, "claude");
    let docs = home.join(".local/share/azdaja");
    let Some(prior_notices) = legacy_notices() else {
        return;
    };
    write_managed_documents(&docs, DOCUMENT_OWNER_V1, &prior_notices);
    assert_eq!(
        sha256(&docs.join("THIRD-PARTY-NOTICES.md")),
        "dde4b0d189ff4fbc79748212bc0fc90bbf75dd27a4f23aaddbb24624e6e8cabb"
    );
    let run_once = || {
        run_installer(InstallRun {
            home: &home,
            base: &base,
            os: "Darwin",
            arch: "arm64",
            glibc_version: None,
            harness: Some("claude"),
            bin_dir: Some(&home.join("bin")),
            path: "/usr/bin:/bin",
        })
    };
    assert_success(&run_once());
    assert_eq!(
        fs::read(docs.join(".azdaja-managed")).unwrap(),
        DOCUMENT_OWNER_V2
    );
    assert_eq!(
        fs::read(docs.join("THIRD-PARTY-NOTICES.md")).unwrap(),
        include_bytes!("../THIRD-PARTY-NOTICES.md")
    );
    let migrated = tree_identity(&docs);
    assert_success(&run_once());
    assert_eq!(tree_identity(&docs), migrated);
    assert!(fs::read_dir(docs.parent().unwrap()).unwrap().all(|entry| {
        !entry
            .unwrap()
            .file_name()
            .to_string_lossy()
            .contains("azdaja-v1-previous")
    }));
}

#[test]
fn mutated_v1_and_marker_declared_fake_v2_refuse_before_home_mutation() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let base = format!("{}/good", server.base);
    for state in ["mutated-v1", "fake-v2"] {
        if state == "mutated-v1" && legacy_notices().is_none() {
            continue;
        }
        let home = scratch.0.join(state);
        fs::create_dir(&home).unwrap();
        mark_detected(&home, "claude");
        let docs = home.join(".local/share/azdaja");
        if state == "mutated-v1" {
            let mut notices = legacy_notices().unwrap();
            notices.extend_from_slice(b"mutated");
            write_managed_documents(&docs, DOCUMENT_OWNER_V1, &notices);
        } else {
            let fake = b"azdaja-installer-owned-docs-v2\nschema=azdaja-managed-documents-v2\nLICENSE.sha256=ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff\nTHIRD-PARTY-NOTICES.md.sha256=eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee\n";
            write_managed_documents(&docs, fake, b"foreign notices");
        }
        let before = tree_identity(&home);
        let output = run_installer(InstallRun {
            home: &home,
            base: &base,
            os: "Darwin",
            arch: "arm64",
            glibc_version: None,
            harness: Some("claude"),
            bin_dir: Some(&home.join("bin")),
            path: "/usr/bin:/bin",
        });
        assert!(!output.status.success(), "state={state}");
        assert_eq!(tree_identity(&home), before, "state={state}");
    }
}

#[test]
fn legacy_v1_migration_rolls_back_exactly_after_injected_harness_failure() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let base = format!("{}/good", server.base);
    let home = scratch.0.join("legacy-rollback-home");
    fs::create_dir(&home).unwrap();
    mark_detected(&home, "claude");
    let docs = home.join(".local/share/azdaja");
    let Some(prior_notices) = legacy_notices() else {
        return;
    };
    write_managed_documents(&docs, DOCUMENT_OWNER_V1, &prior_notices);
    let before = tree_identity(&home);
    let state = scratch.0.join("state-outside-home");
    let extra = [
        ("AZDAJA_LIFECYCLE_TEST_FAIL_AT", OsStr::new("1")),
        ("AZDAJA_HOME", state.as_os_str()),
    ];
    let output = run_installer_with_extra(
        InstallRun {
            home: &home,
            base: &base,
            os: "Darwin",
            arch: "arm64",
            glibc_version: None,
            harness: Some("claude"),
            bin_dir: Some(&home.join("bin")),
            path: "/usr/bin:/bin",
        },
        &extra,
    );
    assert!(!output.status.success());
    assert!(String::from_utf8_lossy(&output.stderr).contains("injected lifecycle failure"));
    assert_eq!(tree_identity(&home), before);
    assert_eq!(
        fs::read(docs.join(".azdaja-managed")).unwrap(),
        DOCUMENT_OWNER_V1
    );
}

#[test]
fn custom_xdg_unicode_space_apostrophe_reinstall_is_exact_and_idempotent() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let base = format!("{}/good", server.base);
    let home = scratch.0.join("home Ü space's");
    let xdg = scratch.0.join("data Ω space's");
    let bin = home.join("bin space's");
    fs::create_dir(&home).unwrap();
    mark_detected(&home, "claude");
    let extra = [("XDG_DATA_HOME", xdg.as_os_str())];
    let run_once = || {
        run_installer_with_extra(
            InstallRun {
                home: &home,
                base: &base,
                os: "Darwin",
                arch: "arm64",
                glibc_version: None,
                harness: Some("claude"),
                bin_dir: Some(&bin),
                path: "/usr/bin:/bin",
            },
            &extra,
        )
    };
    let first = assert_success(&run_once());
    assert_eq!(first.lines().count(), 3);
    assert!(
        first
            .lines()
            .nth(1)
            .unwrap()
            .contains(&format!("docs -> {}", xdg.join("azdaja").display()))
    );
    let docs = xdg.join("azdaja");
    assert_eq!(
        fs::read(docs.join("LICENSE")).unwrap(),
        include_bytes!("../LICENSE")
    );
    assert_eq!(
        fs::read(docs.join("THIRD-PARTY-NOTICES.md")).unwrap(),
        include_bytes!("../THIRD-PARTY-NOTICES.md")
    );
    assert_eq!(
        fs::read(docs.join(".azdaja-managed")).unwrap(),
        DOCUMENT_OWNER_V2
    );
    let before = tree_identity(&docs);
    let second = assert_success(&run_once());
    assert_eq!(second.lines().count(), 3);
    assert_eq!(tree_identity(&docs), before);
}

#[test]
fn late_harness_failure_rolls_back_fresh_documents_and_standalone_surfaces() {
    let scratch = Scratch::new();
    let fixture_root = scratch.0.join("releases");
    fs::create_dir(&fixture_root).unwrap();
    let candidate = local_candidate(&scratch.0);
    write_release(&fixture_root, "good", &candidate, &sha256(&candidate));
    let server = FixtureServer::start(&scratch.0, &fixture_root);
    let base = format!("{}/good", server.base);
    let home = scratch.0.join("late-failure-home");
    fs::create_dir(&home).unwrap();
    mark_detected(&home, "claude");
    let before = tree_identity(&home);
    let state = scratch.0.join("late-failure-state-outside-home");
    let extra = [
        ("AZDAJA_LIFECYCLE_TEST_FAIL_AT", OsStr::new("1")),
        ("AZDAJA_HOME", state.as_os_str()),
    ];
    let output = run_installer_with_extra(
        InstallRun {
            home: &home,
            base: &base,
            os: "Darwin",
            arch: "arm64",
            glibc_version: None,
            harness: Some("claude"),
            bin_dir: Some(&home.join("bin")),
            path: "/usr/bin:/bin",
        },
        &extra,
    );
    assert!(!output.status.success());
    assert_eq!(tree_identity(&home), before);
    assert!(!target(&home, "claude").exists());
    assert!(!home.join(".local/share/azdaja").exists());
}
