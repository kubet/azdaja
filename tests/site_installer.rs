#![cfg(unix)]

use std::{
    fs::{self, File},
    os::unix::fs::PermissionsExt,
    path::{Path, PathBuf},
    process::{Command, Output, Stdio},
    time::{SystemTime, UNIX_EPOCH},
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

fn local_install_candidate(scratch: &Path, built_binary: &Path) -> PathBuf {
    const DOWNLOAD_CAP: u64 = 64 * 1024 * 1024;
    let candidate = scratch.join("validation-candidate-azdaja");
    fs::copy(built_binary, &candidate).unwrap();
    fs::set_permissions(&candidate, fs::Permissions::from_mode(0o755)).unwrap();
    if fs::metadata(&candidate).unwrap().len() > DOWNLOAD_CAP {
        let stripped = Command::new("strip").arg(&candidate).status().unwrap();
        assert!(stripped.success(), "strip failed for oversized test binary");
    }
    assert!(
        fs::metadata(&candidate).unwrap().len() <= DOWNLOAD_CAP,
        "real validation candidate still exceeds installer download cap"
    );
    candidate
}

fn run_installer(
    script: &Path,
    home: &Path,
    path: &str,
    url: Option<&str>,
    digest: Option<&str>,
) -> Output {
    let mut command = Command::new("sh");
    command
        .args(["-s", "--", "--harness", "claude"])
        .env("HOME", home)
        .env("PATH", path)
        .env_remove("AZDAJA_CONFIG")
        .env_remove("AZDAJA_HOME")
        .env_remove("RLM_DEPTH")
        .env_remove("AZDAJA_INSTALL_URL")
        .env_remove("AZDAJA_INSTALL_SHA256")
        .env(
            "AZDAJA_INSTALL_TEST_MODE",
            if url.is_some() { "local" } else { "sealed" },
        )
        .stdin(Stdio::from(File::open(script).unwrap()))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    if let Some(url) = url {
        command.env("AZDAJA_INSTALL_URL", url);
    }
    if let Some(digest) = digest {
        command.env("AZDAJA_INSTALL_SHA256", digest);
    }
    command.output().unwrap()
}

#[test]
fn literal_site_installer_is_sealed_or_installs_verified_bytes_without_provider_calls() {
    let scratch = Scratch::new();
    let script = Path::new(env!("CARGO_MANIFEST_DIR")).join("site/install");
    let built_binary = Path::new(env!("CARGO_BIN_EXE_azdaja"));
    let binary = local_install_candidate(&scratch.0, built_binary);
    let digest = sha256(&binary);
    let url = format!("file://{}", binary.display());

    let tools = scratch.0.join("tools");
    fs::create_dir(&tools).unwrap();
    let provider_called = scratch.0.join("provider-called");
    let claude = tools.join("claude");
    fs::write(
        &claude,
        format!(
            "#!/bin/sh\nprintf called > {:?}\nexit 9\n",
            provider_called.to_str().unwrap()
        ),
    )
    .unwrap();
    fs::set_permissions(&claude, fs::Permissions::from_mode(0o755)).unwrap();
    let path = format!("{}:{}", tools.display(), std::env::var("PATH").unwrap());

    let sealed_home = scratch.0.join("sealed-home");
    fs::create_dir(&sealed_home).unwrap();
    let sealed = run_installer(&script, &sealed_home, &path, None, None);
    assert_eq!(sealed.status.code(), Some(1));
    assert!(fs::read_dir(&sealed_home).unwrap().next().is_none());

    let bad_home = scratch.0.join("bad-home");
    fs::create_dir(&bad_home).unwrap();
    let bad = run_installer(&script, &bad_home, &path, Some(&url), Some(&"0".repeat(64)));
    assert_eq!(bad.status.code(), Some(1));
    assert!(fs::read_dir(&bad_home).unwrap().next().is_none());
    assert!(
        String::from_utf8_lossy(&bad.stderr).contains("SHA-256 mismatch"),
        "unexpected bad-hash result: status={} stdout={} stderr={}",
        bad.status,
        String::from_utf8_lossy(&bad.stdout),
        String::from_utf8_lossy(&bad.stderr)
    );

    let good_home = scratch.0.join("good-home");
    fs::create_dir(&good_home).unwrap();
    let installed = run_installer(&script, &good_home, &path, Some(&url), Some(&digest));
    assert!(
        installed.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&installed.stdout),
        String::from_utf8_lossy(&installed.stderr)
    );
    assert!(
        !provider_called.exists(),
        "installer entered a provider turn"
    );
    let managed = good_home.join(".claude/skills/azdaja/azdaja");
    assert!(managed.is_file());
    assert_eq!(
        sha256(&managed),
        digest,
        "installed bytes changed after verification"
    );
    let version = Command::new(&managed).arg("--version").output().unwrap();
    assert!(version.status.success());
    assert!(String::from_utf8_lossy(&version.stdout).starts_with("azdaja 0.1.1 "));
}

#[test]
fn v011_installer_binds_exact_two_platform_assets_and_rejects_ordinary_overrides() {
    let script = Path::new(env!("CARGO_MANIFEST_DIR")).join("site/install");
    let text = fs::read_to_string(&script).unwrap();
    let darwin_url =
        "https://github.com/kubet/azdaja/releases/download/v0.1.1/azdaja-v0.1.1-darwin-arm64";
    let linux_url =
        "https://github.com/kubet/azdaja/releases/download/v0.1.1/azdaja-v0.1.1-linux-x86_64";
    let darwin_sha = "b58975de462e823adcf901e331acfd4e70c9e72b5db014de265c04e371d31883";
    let linux_sha = "b18775f0d3572b20804ff3c3af880ffc5fa3131017c566dc941c1dd743c00247";
    assert_eq!(text.matches(darwin_url).count(), 1);
    assert_eq!(text.matches(linux_url).count(), 1);
    assert_eq!(text.matches(darwin_sha).count(), 1);
    assert_eq!(text.matches(linux_sha).count(), 1);
    assert_eq!(text.matches("Darwin-arm64)").count(), 1);
    assert_eq!(text.matches("Linux-x86_64)").count(), 1);
    for unsupported in [
        "Darwin-x86_64)",
        "Linux-aarch64)",
        "Linux-arm64)",
        "Linux-amd64)",
    ] {
        assert!(
            !text.contains(unsupported),
            "unexpected platform arm: {unsupported}"
        );
    }
    assert!(text.contains("This platform has no published v0.1.1 binary"));

    let scratch = Scratch::new();
    let home = scratch.0.join("ordinary-override-home");
    fs::create_dir(&home).unwrap();
    let output = Command::new("sh")
        .arg(&script)
        .env("HOME", &home)
        .env("AZDAJA_INSTALL_URL", "https://example.invalid/azdaja")
        .env("AZDAJA_INSTALL_SHA256", "0".repeat(64))
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
