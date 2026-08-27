use std::{
    collections::BTreeSet,
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

fn cargo_tree_packages(root: &Path, target: &str) -> BTreeSet<String> {
    let output = Command::new(env!("CARGO"))
        .args([
            "tree",
            "--locked",
            "--target",
            target,
            "--no-dedupe",
            "--prefix",
            "none",
            "--format",
            "{p}",
        ])
        .current_dir(root)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "cargo tree failed for {target}: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout)
        .unwrap()
        .lines()
        .map(|line| line.strip_suffix(" (proc-macro)").unwrap_or(line))
        .filter(|line| !line.starts_with("azdaja v"))
        .map(str::to_owned)
        .collect()
}

#[test]
fn reviewed_notice_license_and_font_ofl_bytes_are_preserved() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    assert_eq!(
        sha256(&root.join("THIRD-PARTY-NOTICES.md")),
        "0ca6a9e083b01cda3ac7017682f3b10b106f132c144a230436694e43d8f79bd3"
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
fn cargo_package_list_matches_the_reviewed_file_allowlist() {
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
            "assets/config.toml",
            "assets/legacy/codex-config-41f19430.toml",
            "assets/legacy/codex-config-a9da6615.toml",
            "assets/legacy/codex-config-ae85a189.toml",
            "assets/legacy/codex-config-e6467dc6.toml",
            "assets/legacy/jcode-config-bc956890.toml",
            "assets/legacy/jcode-config-d890a0fa.toml",
            "assets/legacy/opencode-config-f077082c.toml",
            "assets/template/SKILL.md",
            "src/banner.rs",
            "src/dashboard.rs",
            "src/jcode_config.rs",
            "src/jcode_gate.rs",
            "src/lib.rs",
            "src/main.rs",
            "src/memory.rs",
            "src/observability.rs",
            "src/repo_source.rs",
            "src/tui.rs",
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
fn public_platform_claims_include_every_installer_target() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let readme = fs::read_to_string(root.join("README.md")).unwrap();
    let install_doc = fs::read_to_string(root.join("docs/install.md")).unwrap();
    let site = fs::read_to_string(root.join("site/index.html")).unwrap();
    let installer = fs::read_to_string(root.join("site/install")).unwrap();

    assert!(readme.contains("macOS 11+ on Apple Silicon and Intel"));
    assert!(install_doc.contains("macOS 11 or newer on Apple Silicon and Intel"));
    assert!(site.contains("macOS 11+ on Apple Silicon and Intel"));
    for asset in [
        "azdaja-v$VERSION-darwin-arm64",
        "azdaja-v$VERSION-darwin-x86_64",
        "azdaja-v$VERSION-linux-x86_64",
    ] {
        assert!(installer.contains(asset), "installer is missing {asset}");
    }
}

#[test]
fn standalone_release_assembler_keeps_raw_binaries_and_checksums_five_payloads() {
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
    let darwin = dist.join("azdaja-v0.1.14-darwin-arm64");
    let darwin_x86_64 = dist.join("azdaja-v0.1.14-darwin-x86_64");
    let linux = dist.join("azdaja-v0.1.14-linux-x86_64");
    fs::write(&darwin, b"raw darwin binary").unwrap();
    fs::write(&darwin_x86_64, b"raw darwin x86-64 binary").unwrap();
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
    assert_eq!(
        fs::read(&darwin_x86_64).unwrap(),
        b"raw darwin x86-64 binary"
    );
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
    assert_eq!(lines.len(), 5);
    for name in [
        "azdaja-v0.1.14-darwin-arm64",
        "azdaja-v0.1.14-darwin-x86_64",
        "azdaja-v0.1.14-linux-x86_64",
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

#[test]
fn ci_builds_every_documented_standalone_target_explicitly() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let ci = fs::read_to_string(root.join(".github/workflows/ci.yml")).unwrap();
    let job = ci
        .split_once("\n  standalone-targets:\n")
        .expect("standalone target job must exist")
        .1
        .split_once("\n  windows-safety:\n")
        .expect("standalone target job must remain independently scoped")
        .0;

    for entry in [
        "          - os: macos-14\n            rust_target: aarch64-apple-darwin\n            asset: darwin-arm64",
        "          - os: macos-14\n            rust_target: x86_64-apple-darwin\n            asset: darwin-x86_64",
        "          - os: ubuntu-22.04\n            rust_target: x86_64-unknown-linux-gnu\n            asset: linux-x86_64",
    ] {
        assert!(
            job.contains(entry),
            "missing mandatory CI matrix entry: {entry}"
        );
    }
    assert!(job.contains("cargo build --release --locked --target \"${{ matrix.rust_target }}\""));
    assert!(job.contains("Verify standalone target architecture"));
    assert!(job.contains("unreviewed standalone target"));
}

#[test]
fn ci_windows_safety_is_strict_and_retains_exact_commit_candidates() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let ci = fs::read_to_string(root.join(".github/workflows/ci.yml")).unwrap();
    let job = ci
        .split_once("\n  windows-safety:\n")
        .expect("Windows safety job must exist")
        .1;

    assert!(job.contains("runs-on: windows-latest"));
    assert!(
        job.contains("cargo clippy --quiet --all-targets --all-features --locked -- -D warnings")
    );
    assert!(job.contains("cargo test --lib --bin azdaja --locked -- --test-threads=1"));
    assert!(job.contains(".\\target\\release\\azdaja.exe --version"));
    assert!(job.contains(".\\target\\release\\azdaja.exe doctor --caps"));
    assert!(job.contains("azdaja-v0.1.14-windows-x86_64.exe"));
    assert!(
        job.contains(
            "azdaja-standalone-windows-x86_64-${{ github.sha }}-${{ github.run_attempt }}"
        )
    );
}

#[test]
fn intel_darwin_dependency_delta_is_already_in_the_reviewed_notice_corpus() {
    if !cfg!(target_os = "macos") {
        return;
    }
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let arm = cargo_tree_packages(root, "aarch64-apple-darwin");
    let intel = cargo_tree_packages(root, "x86_64-apple-darwin");
    let linux = cargo_tree_packages(root, "x86_64-unknown-linux-gnu");

    assert_eq!(arm.len(), 189);
    assert_eq!(intel.len(), 190);
    assert_eq!(linux.len(), 190);
    assert_eq!(
        intel.difference(&arm).cloned().collect::<Vec<_>>(),
        ["spin v0.9.9"]
    );
    assert!(arm.difference(&intel).next().is_none());
    assert!(linux.contains("spin v0.9.9"));
    assert_eq!(
        arm.union(&intel)
            .cloned()
            .collect::<BTreeSet<_>>()
            .union(&linux)
            .count(),
        191
    );

    let notices = fs::read_to_string(root.join("THIRD-PARTY-NOTICES.md")).unwrap();
    assert!(notices.contains("| `spin` | `0.9.9` | `MIT` | `x86_64-unknown-linux-gnu` |"));
    assert!(notices.contains("pkg:cargo/spin@0.9.9 — `LICENSE` (archive_named_legal_file)"));
    assert!(
        notices.contains("pkg:cargo/spin@0.9.9 — `src/barrier.rs` (archive_legal_header_block)")
    );
}
