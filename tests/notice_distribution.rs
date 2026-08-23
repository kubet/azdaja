use std::{
    fs,
    path::Path,
    process::Command,
    time::{SystemTime, UNIX_EPOCH},
};

fn sha256(path: &Path) -> String {
    for (tool, args) in [("shasum", vec!["-a", "256"]), ("sha256sum", vec![])] {
        if let Ok(output) = Command::new(tool).args(args).arg(path).output()
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

#[test]
fn reviewed_notice_license_and_font_ofl_bytes_are_preserved() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    assert_eq!(
        sha256(&root.join("THIRD-PARTY-NOTICES.md")),
        "ee908558c8d5f0d2080400558db351d8f24fb7ad3ca902c904822d97d7b5eac6"
    );
    assert_eq!(
        sha256(&root.join("LICENSE")),
        "45dd135e23e0e915b3dd61095d46eb45a8f59bbc53dadface6affbd1c76d7096"
    );
    assert_eq!(
        sha256(&root.join("site/fonts/Cormorant-Garamond-OFL.txt")),
        "60700d351cac4650c51f3f9db318d2a420f8b45052dba2715eb5fec41f0f6956"
    );
}

#[test]
fn cargo_package_list_is_the_exact_twelve_file_allowlist() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let output = Command::new("cargo")
        .args(["package", "--list", "--allow-dirty"])
        .current_dir(root)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    let files: Vec<_> = String::from_utf8(output.stdout)
        .unwrap()
        .lines()
        .map(str::to_owned)
        .collect();
    assert_eq!(
        files,
        vec![
            ".cargo_vcs_info.json",
            "Cargo.lock",
            "Cargo.toml",
            "Cargo.toml.orig",
            "LICENSE",
            "README.md",
            "THIRD-PARTY-NOTICES.md",
            "assets/SKILL.md",
            "assets/config.toml",
            "src/banner.rs",
            "src/lib.rs",
            "src/main.rs",
        ]
    );
}

#[test]
fn readme_has_exactly_three_install_blocks_and_readme_site_link_notices() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let readme = fs::read_to_string(root.join("README.md")).unwrap();
    let install = readme
        .split_once("## Install")
        .unwrap()
        .1
        .split_once("## Use")
        .unwrap()
        .0;
    assert_eq!(install.matches("```bash\n").count(), 3);
    assert!(install.contains("[supported-target third-party notices](THIRD-PARTY-NOTICES.md)"));
    let site = fs::read_to_string(root.join("site/index.html")).unwrap();
    assert!(site.contains("THIRD-PARTY-NOTICES.md\">third-party notices</a>"));
    assert!(site.contains("LICENSE\">license</a>"));
}

#[test]
fn standalone_release_assembler_keeps_raw_binaries_and_checksums_four_payloads() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let dist = std::env::temp_dir().join(format!(
        "azdaja-notice-assets-{}-{nonce}",
        std::process::id()
    ));
    fs::create_dir(&dist).unwrap();
    let darwin = dist.join("azdaja-v0.1.3-darwin-arm64");
    let linux = dist.join("azdaja-v0.1.3-linux-x86_64");
    fs::write(&darwin, b"raw darwin binary").unwrap();
    fs::write(&linux, b"raw linux binary").unwrap();
    let output = Command::new("sh")
        .arg(root.join("release/assemble-standalone-assets.sh"))
        .arg(&dist)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(fs::read(&darwin).unwrap(), b"raw darwin binary");
    assert_eq!(fs::read(&linux).unwrap(), b"raw linux binary");
    assert_eq!(
        fs::read(dist.join("LICENSE")).unwrap(),
        fs::read(root.join("LICENSE")).unwrap()
    );
    assert_eq!(
        fs::read(dist.join("THIRD-PARTY-NOTICES.md")).unwrap(),
        fs::read(root.join("THIRD-PARTY-NOTICES.md")).unwrap()
    );
    let sums = fs::read_to_string(dist.join("SHA256SUMS")).unwrap();
    let lines: Vec<_> = sums.lines().collect();
    assert_eq!(lines.len(), 4);
    for name in [
        "azdaja-v0.1.3-darwin-arm64",
        "azdaja-v0.1.3-linux-x86_64",
        "LICENSE",
        "THIRD-PARTY-NOTICES.md",
    ] {
        assert_eq!(
            lines
                .iter()
                .filter(|line| line.ends_with(&format!("  {name}")))
                .count(),
            1
        );
    }
    fs::remove_dir_all(dist).unwrap();
}
