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
    let binary = Path::new(env!("CARGO_BIN_EXE_azdaja"));
    let digest = sha256(binary);
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
    assert!(String::from_utf8_lossy(&bad.stderr).contains("SHA-256 mismatch"));
    assert!(fs::read_dir(&bad_home).unwrap().next().is_none());

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
    assert!(String::from_utf8_lossy(&version.stdout).starts_with("azdaja 0.1.0 "));
}
