use std::{
    fs,
    path::{Path, PathBuf},
    process::{Command, Output},
    sync::atomic::{AtomicU64, Ordering},
};

static NEXT_SCRATCH: AtomicU64 = AtomicU64::new(0);

struct Scratch(PathBuf);

impl Scratch {
    fn new(label: &str) -> Self {
        let nonce = NEXT_SCRATCH.fetch_add(1, Ordering::Relaxed);
        let path = std::env::temp_dir().join(format!(
            "azdaja-publication-verifier-{label}-{}-{nonce}",
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&path);
        fs::create_dir_all(&path).unwrap();
        Self(path)
    }
}

impl Drop for Scratch {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

struct Fixture {
    version: &'static str,
    expected: PathBuf,
    site: PathBuf,
    github: PathBuf,
    tag: PathBuf,
}

fn sha256(path: &Path) -> String {
    let attempts = [
        ("shasum", vec!["-a", "256", path.to_str().unwrap()]),
        ("sha256sum", vec![path.to_str().unwrap()]),
    ];
    for (program, args) in attempts {
        if let Ok(output) = Command::new(program).args(args).output()
            && output.status.success()
        {
            return String::from_utf8(output.stdout)
                .unwrap()
                .split_whitespace()
                .next()
                .unwrap()
                .to_owned();
        }
    }
    panic!("shasum or sha256sum is required for publication verifier tests");
}

fn copy_release(source: &Path, destination: &Path, payloads: &[String]) {
    fs::create_dir_all(destination).unwrap();
    for payload in payloads {
        fs::copy(source.join(payload), destination.join(payload)).unwrap();
    }
    fs::copy(source.join("SHA256SUMS"), destination.join("SHA256SUMS")).unwrap();
}

fn fixture(scratch: &Scratch) -> Fixture {
    let version = "9.9.9";
    let expected = scratch.0.join("expected");
    let site = scratch.0.join("site");
    let github = scratch.0.join("github");
    let tag = scratch.0.join("tag");
    fs::create_dir_all(&expected).unwrap();

    let payloads = vec![
        format!("azdaja-v{version}-darwin-arm64"),
        format!("azdaja-v{version}-darwin-x86_64"),
        format!("azdaja-v{version}-linux-x86_64"),
        "LICENSE".to_owned(),
        "THIRD-PARTY-NOTICES.md".to_owned(),
    ];
    for (index, payload) in payloads.iter().enumerate() {
        fs::write(
            expected.join(payload),
            format!("fixture payload {index}: {payload}\n"),
        )
        .unwrap();
    }
    let manifest = payloads
        .iter()
        .map(|payload| format!("{}  {payload}\n", sha256(&expected.join(payload))))
        .collect::<String>();
    fs::write(expected.join("SHA256SUMS"), manifest).unwrap();
    let provenance = format!(
        concat!(
            "{{\"allowed_promotion_delta_paths\":[",
            "\"site/releases/v{version}/LICENSE\",",
            "\"site/releases/v{version}/PROVENANCE.json\",",
            "\"site/releases/v{version}/SHA256SUMS\",",
            "\"site/releases/v{version}/THIRD-PARTY-NOTICES.md\",",
            "\"site/releases/v{version}/azdaja-v{version}-darwin-arm64\",",
            "\"site/releases/v{version}/azdaja-v{version}-darwin-x86_64\",",
            "\"site/releases/v{version}/azdaja-v{version}-linux-x86_64\"],",
            "\"release_version\":\"{version}\",\"schema_version\":1,",
            "\"source_artifacts\":[",
            "{{\"artifact_name\":\"azdaja-candidate-aarch64-apple-darwin\",\"asset_name\":\"azdaja-v{version}-darwin-arm64\",\"bytes\":17,\"sha256\":\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\",\"target\":\"aarch64-apple-darwin\"}},",
            "{{\"artifact_name\":\"azdaja-candidate-x86_64-apple-darwin\",\"asset_name\":\"azdaja-v{version}-darwin-x86_64\",\"bytes\":18,\"sha256\":\"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\",\"target\":\"x86_64-apple-darwin\"}},",
            "{{\"artifact_name\":\"azdaja-candidate-x86_64-unknown-linux-gnu\",\"asset_name\":\"azdaja-v{version}-linux-x86_64\",\"bytes\":19,\"sha256\":\"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc\",\"target\":\"x86_64-unknown-linux-gnu\"}}],",
            "\"source_commit\":\"1111111111111111111111111111111111111111\",",
            "\"status\":\"REVIEWED_FOR_PUBLICATION\",",
            "\"workflow_run_attempt\":2,\"workflow_run_id\":645}}\n"
        ),
        version = version
    );
    fs::write(expected.join("PROVENANCE.json"), provenance).unwrap();

    copy_release(
        &expected,
        &site.join(format!("releases/v{version}")),
        &payloads,
    );
    copy_release(&expected, &github, &payloads);
    copy_release(&expected, &tag, &payloads);
    for destination in [
        site.join(format!("releases/v{version}/PROVENANCE.json")),
        github.join("PROVENANCE.json"),
        tag.join("PROVENANCE.json"),
    ] {
        fs::copy(expected.join("PROVENANCE.json"), destination).unwrap();
    }
    fs::write(
        site.join("install"),
        format!(
            "#!/bin/sh\nVERSION={version}\ncase \"$OS-$ARCH\" in\n  Darwin-x86_64)\n    ASSET=azdaja-v$VERSION-darwin-x86_64\n    ;;\nesac\n"
        ),
    )
    .unwrap();

    Fixture {
        version,
        expected,
        site,
        github,
        tag,
    }
}

fn run_verifier(fixture: &Fixture) -> Output {
    Command::new("sh")
        .arg(Path::new(env!("CARGO_MANIFEST_DIR")).join("release/verify-published-release.sh"))
        .arg(fixture.version)
        .env("AZDAJA_VERIFY_TEST_MODE", "local")
        .env(
            "AZDAJA_SITE_BASE",
            format!("file://{}", fixture.site.display()),
        )
        .env(
            "AZDAJA_GITHUB_RELEASE_BASE",
            format!("file://{}", fixture.github.display()),
        )
        .env(
            "AZDAJA_GITHUB_TAG_BASE",
            format!("file://{}", fixture.tag.display()),
        )
        .env("AZDAJA_EXPECTED_DIR", &fixture.expected)
        .output()
        .unwrap()
}

#[test]
fn release_note_requires_the_post_publication_verifier() {
    let release_note =
        fs::read_to_string(Path::new(env!("CARGO_MANIFEST_DIR")).join("release/v0.1.14.md"))
            .unwrap();
    assert!(release_note.contains("release/verify-published-release.sh 0.1.14"));
    assert!(release_note.contains("downloads and verifies all five payloads"));
}

#[test]
fn workflow_dispatch_runs_the_read_only_publication_verifier() {
    let workflow = fs::read_to_string(
        Path::new(env!("CARGO_MANIFEST_DIR"))
            .join(".github/workflows/verify-published-release.yml"),
    )
    .unwrap();
    assert!(workflow.contains("workflow_dispatch:"));
    assert!(workflow.contains("contents: read"));
    assert!(workflow.contains("release/verify-published-release.sh \"$VERSION\""));
    assert!(!workflow.contains("default: 0.1.14"));
    assert!(!workflow.contains("contents: write"));
    assert!(!workflow.contains("gh release upload"));
}

#[test]
fn publication_verifier_rejects_a_non_semver_release_selector() {
    let scratch = Scratch::new("invalid-version");
    let fixture = fixture(&scratch);
    let output = Command::new("sh")
        .arg(Path::new(env!("CARGO_MANIFEST_DIR")).join("release/verify-published-release.sh"))
        .arg("9..9")
        .env("AZDAJA_VERIFY_TEST_MODE", "local")
        .env(
            "AZDAJA_SITE_BASE",
            format!("file://{}", fixture.site.display()),
        )
        .env(
            "AZDAJA_GITHUB_RELEASE_BASE",
            format!("file://{}", fixture.github.display()),
        )
        .env("AZDAJA_EXPECTED_DIR", &fixture.expected)
        .output()
        .unwrap();
    assert!(!output.status.success());
    assert!(String::from_utf8_lossy(&output.stderr).contains("invalid version '9..9'"));
}

#[test]
fn publication_verifier_requires_an_explicit_version() {
    let output = Command::new("sh")
        .arg(Path::new(env!("CARGO_MANIFEST_DIR")).join("release/verify-published-release.sh"))
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("Usage: release/verify-published-release.sh VERSION")
    );
}

#[test]
fn publication_verifier_accepts_complete_matching_boundaries() {
    let scratch = Scratch::new("complete");
    let fixture = fixture(&scratch);
    let output = run_verifier(&fixture);
    assert!(
        output.status.success(),
        "stdout:\n{}\nstderr:\n{}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("verified published v9.9.9"));
    assert!(stdout.contains(&fixture.site.display().to_string()));
    assert!(stdout.contains(&fixture.github.display().to_string()));
    assert!(stdout.contains(&fixture.tag.display().to_string()));
}

#[test]
fn publication_verifier_rejects_mismatched_provenance() {
    let scratch = Scratch::new("provenance-mismatch");
    let fixture = fixture(&scratch);
    let provenance = fixture.github.join("PROVENANCE.json");
    let changed = fs::read_to_string(&provenance)
        .unwrap()
        .replace("\"workflow_run_id\":645", "\"workflow_run_id\":646");
    fs::write(provenance, changed).unwrap();

    let output = run_verifier(&fixture);
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("GitHub release PROVENANCE.json differs from the reviewed local provenance")
    );
}

#[test]
fn publication_verifier_rejects_an_installer_without_the_intel_route() {
    let scratch = Scratch::new("installer-route");
    let fixture = fixture(&scratch);
    fs::write(
        fixture.site.join("install"),
        "#!/bin/sh\nVERSION=9.9.9\ncase \"$OS-$ARCH\" in\n  Darwin-arm64) ;;\nesac\n",
    )
    .unwrap();

    let output = run_verifier(&fixture);
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("deployed installer does not route Darwin-x86_64")
    );
}

#[test]
fn publication_verifier_rejects_a_two_binary_github_manifest() {
    let scratch = Scratch::new("github-manifest");
    let fixture = fixture(&scratch);
    let manifest_path = fixture.github.join("SHA256SUMS");
    let stale = fs::read_to_string(&manifest_path)
        .unwrap()
        .lines()
        .filter(|line| !line.contains("darwin-x86_64"))
        .map(|line| format!("{line}\n"))
        .collect::<String>();
    fs::write(manifest_path, stale).unwrap();

    let output = run_verifier(&fixture);
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("GitHub release SHA256SUMS must contain exactly five payload entries")
    );
}

#[test]
fn publication_verifier_rejects_a_tag_without_the_intel_payload() {
    let scratch = Scratch::new("tag-manifest");
    let fixture = fixture(&scratch);
    let manifest_path = fixture.tag.join("SHA256SUMS");
    let stale = fs::read_to_string(&manifest_path)
        .unwrap()
        .lines()
        .filter(|line| !line.contains("darwin-x86_64"))
        .map(|line| format!("{line}\n"))
        .collect::<String>();
    fs::write(manifest_path, stale).unwrap();

    let output = run_verifier(&fixture);
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("GitHub tag SHA256SUMS must contain exactly five payload entries")
    );
}
