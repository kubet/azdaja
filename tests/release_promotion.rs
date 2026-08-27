#![cfg(unix)]

use std::{
    fs,
    os::unix::fs::{PermissionsExt, symlink},
    path::{Path, PathBuf},
    process::{Command, Output},
    sync::atomic::{AtomicU64, Ordering},
};

static NEXT_ID: AtomicU64 = AtomicU64::new(0);
const RUN_ID: &str = "645";
const RUN_ATTEMPT: &str = "2";
const VERSION: &str = "0.1.14";
const TARGETS: [(&str, &str); 3] = [
    ("aarch64-apple-darwin", "azdaja-v0.1.14-darwin-arm64"),
    ("x86_64-apple-darwin", "azdaja-v0.1.14-darwin-x86_64"),
    ("x86_64-unknown-linux-gnu", "azdaja-v0.1.14-linux-x86_64"),
];

struct Scratch(PathBuf);
impl Scratch {
    fn new(label: &str) -> Self {
        let id = NEXT_ID.fetch_add(1, Ordering::Relaxed);
        let path = std::env::temp_dir().join(format!(
            "azdaja-release-promotion-{label}-{}-{id}",
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
    root: PathBuf,
    candidates: PathBuf,
    source_sha: String,
}

fn run(mut command: Command) -> Output {
    command.output().unwrap()
}

fn git(root: &Path, args: &[&str]) -> Output {
    let mut command = Command::new("git");
    command.args(args).current_dir(root);
    run(command)
}

fn sha256(path: &Path) -> String {
    let output = run({
        let mut command = Command::new("shasum");
        command.args(["-a", "256"]).arg(path);
        command
    });
    assert!(output.status.success());
    String::from_utf8(output.stdout)
        .unwrap()
        .split_whitespace()
        .next()
        .unwrap()
        .to_owned()
}

fn binary(target: &str) -> Vec<u8> {
    let mut data = vec![0_u8; 64];
    match target {
        "aarch64-apple-darwin" => {
            data[..8].copy_from_slice(&[0xcf, 0xfa, 0xed, 0xfe, 0x0c, 0x00, 0x00, 0x01]);
        }
        "x86_64-apple-darwin" => {
            data[..8].copy_from_slice(&[0xcf, 0xfa, 0xed, 0xfe, 0x07, 0x00, 0x00, 0x01]);
        }
        "x86_64-unknown-linux-gnu" => {
            data[..7].copy_from_slice(b"\x7fELF\x02\x01\x01");
            data[18..20].copy_from_slice(&[0x3e, 0x00]);
        }
        _ => unreachable!(),
    }
    data.extend_from_slice(target.as_bytes());
    data
}

fn write_receipt(dir: &Path, source_sha: &str, target: &str, asset: &str) {
    let binary = dir.join(asset);
    let receipt = format!(
        concat!(
            "{{\"architecture_validation\":true,\"asset_name\":\"{}\",",
            "\"bytes\":{},\"publication_authorized\":false,\"run_attempt\":{},",
            "\"run_id\":{},\"schema_version\":1,\"sha256\":\"{}\",",
            "\"source_sha\":\"{}\",\"target\":\"{}\",\"version\":\"{}\"}}\n"
        ),
        asset,
        fs::metadata(&binary).unwrap().len(),
        RUN_ATTEMPT,
        RUN_ID,
        sha256(&binary),
        source_sha,
        target,
        VERSION,
    );
    fs::write(dir.join("candidate-receipt.json"), receipt).unwrap();
}

fn fixture(label: &str) -> (Scratch, Fixture) {
    let scratch = Scratch::new(label);
    let root = scratch.0.join("repo");
    fs::create_dir_all(root.join("release")).unwrap();
    fs::copy(
        Path::new(env!("CARGO_MANIFEST_DIR")).join("release/promote-standalone-assets.sh"),
        root.join("release/promote-standalone-assets.sh"),
    )
    .unwrap();
    fs::write(root.join("LICENSE"), "reviewed license\n").unwrap();
    fs::write(root.join("THIRD-PARTY-NOTICES.md"), "reviewed notices\n").unwrap();
    assert!(git(&root, &["init", "-q"]).status.success());
    assert!(
        git(&root, &["config", "user.email", "test@example.invalid"])
            .status
            .success()
    );
    assert!(
        git(&root, &["config", "user.name", "Release Test"])
            .status
            .success()
    );
    assert!(git(&root, &["add", "."]).status.success());
    assert!(git(&root, &["commit", "-qm", "source A"]).status.success());
    let source_sha = String::from_utf8(git(&root, &["rev-parse", "HEAD"]).stdout)
        .unwrap()
        .trim()
        .to_owned();
    let candidates = scratch.0.join("candidates");
    fs::create_dir(&candidates).unwrap();
    for (target, asset) in TARGETS {
        let dir = candidates.join(format!("azdaja-candidate-{target}"));
        fs::create_dir(&dir).unwrap();
        fs::write(dir.join(asset), binary(target)).unwrap();
        write_receipt(&dir, &source_sha, target, asset);
    }
    (
        scratch,
        Fixture {
            root,
            candidates,
            source_sha,
        },
    )
}

fn promote(fixture: &Fixture, output: &Path) -> Output {
    run({
        let mut command = Command::new("sh");
        command
            .arg(fixture.root.join("release/promote-standalone-assets.sh"))
            .args([
                &fixture.source_sha,
                RUN_ID,
                RUN_ATTEMPT,
                fixture.candidates.to_str().unwrap(),
                output.to_str().unwrap(),
            ])
            .current_dir(&fixture.root);
        command
    })
}

fn assert_rejected_atomically(fixture: &Fixture, label: &str) -> String {
    let output_dir = fixture.root.parent().unwrap().join(format!("out-{label}"));
    let output = promote(fixture, &output_dir);
    assert!(!output.status.success(), "promotion unexpectedly succeeded");
    assert!(!output_dir.exists(), "partial output was left behind");
    String::from_utf8_lossy(&output.stderr).into_owned()
}

#[test]
fn promotion_succeeds_with_exact_payloads_and_is_deterministic() {
    let (_scratch, fixture) = fixture("success");
    let output_one = fixture.root.parent().unwrap().join("out-one");
    let first = promote(&fixture, &output_one);
    assert!(
        first.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&first.stderr)
    );
    let mut names = fs::read_dir(&output_one)
        .unwrap()
        .map(|entry| entry.unwrap().file_name().into_string().unwrap())
        .collect::<Vec<_>>();
    names.sort();
    assert_eq!(
        names,
        vec![
            "LICENSE",
            "PROVENANCE.json",
            "SHA256SUMS",
            "THIRD-PARTY-NOTICES.md",
            "azdaja-v0.1.14-darwin-arm64",
            "azdaja-v0.1.14-darwin-x86_64",
            "azdaja-v0.1.14-linux-x86_64",
        ]
    );
    assert_eq!(
        fs::read_to_string(output_one.join("SHA256SUMS"))
            .unwrap()
            .lines()
            .count(),
        5
    );
    for (_, asset) in TARGETS {
        assert_eq!(
            fs::metadata(output_one.join(asset))
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o755
        );
    }
    let provenance_one = fs::read(output_one.join("PROVENANCE.json")).unwrap();
    assert!(String::from_utf8_lossy(&provenance_one).contains("REVIEWED_FOR_PUBLICATION"));
    let output_two = fixture.root.parent().unwrap().join("out-two");
    assert!(promote(&fixture, &output_two).status.success());
    assert_eq!(
        provenance_one,
        fs::read(output_two.join("PROVENANCE.json")).unwrap()
    );
}

#[test]
fn promotion_accepts_a_logical_symlink_alias_of_the_source_repository() {
    let (scratch, fixture) = fixture("source-alias");
    let alias = scratch.0.join("repo-alias");
    symlink(&fixture.root, &alias).unwrap();
    let output_dir = scratch.0.join("out-alias");
    let output = run({
        let mut command = Command::new("sh");
        command
            .arg(alias.join("release/promote-standalone-assets.sh"))
            .args([
                &fixture.source_sha,
                RUN_ID,
                RUN_ATTEMPT,
                fixture.candidates.to_str().unwrap(),
                output_dir.to_str().unwrap(),
            ])
            .current_dir(&alias);
        command
    });
    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(output_dir.join("PROVENANCE.json").is_file());
}

#[test]
fn promotion_rejects_omission_extra_symlink_and_tamper_atomically() {
    let (_scratch, fixture) = fixture("structural");
    let omitted = fixture
        .candidates
        .join("azdaja-candidate-aarch64-apple-darwin/candidate-receipt.json");
    fs::remove_file(&omitted).unwrap();
    assert!(assert_rejected_atomically(&fixture, "omission").contains("must contain exactly"));
    write_receipt(
        omitted.parent().unwrap(),
        &fixture.source_sha,
        TARGETS[0].0,
        TARGETS[0].1,
    );
    fs::write(fixture.candidates.join("extra"), "no").unwrap();
    assert!(assert_rejected_atomically(&fixture, "extra").contains("must contain exactly"));
    fs::remove_file(fixture.candidates.join("extra")).unwrap();
    let receipt = fixture
        .candidates
        .join("azdaja-candidate-aarch64-apple-darwin/candidate-receipt.json");
    fs::remove_file(&receipt).unwrap();
    symlink("../missing", &receipt).unwrap();
    assert!(assert_rejected_atomically(&fixture, "symlink").contains("symlinked"));
    fs::remove_file(&receipt).unwrap();
    write_receipt(
        receipt.parent().unwrap(),
        &fixture.source_sha,
        TARGETS[0].0,
        TARGETS[0].1,
    );
    fs::write(receipt.parent().unwrap().join(TARGETS[0].1), b"tampered").unwrap();
    assert!(assert_rejected_atomically(&fixture, "tamper").contains("receipt mismatch"));
}

#[test]
fn promotion_rejects_receipt_identity_and_wrong_magic_atomically() {
    for (label, needle, replacement, expected) in [
        (
            "sha",
            "source_sha\":\"",
            "source_sha\":\"0000000000000000000000000000000000000000",
            "receipt mismatch for source_sha",
        ),
        (
            "run",
            "\"run_id\":645",
            "\"run_id\":646",
            "receipt mismatch for run_id",
        ),
        (
            "target",
            "aarch64-apple-darwin",
            "x86_64-apple-darwin",
            "receipt mismatch for target",
        ),
        (
            "version",
            "\"version\":\"0.1.14\"",
            "\"version\":\"0.1.13\"",
            "receipt mismatch for version",
        ),
    ] {
        let (_scratch, fixture) = fixture(label);
        let receipt = fixture
            .candidates
            .join("azdaja-candidate-aarch64-apple-darwin/candidate-receipt.json");
        let text = fs::read_to_string(&receipt).unwrap();
        let changed = if label == "sha" {
            let start = text.find(needle).unwrap() + needle.len();
            let mut value = text.clone();
            value.replace_range(
                start..start + 40,
                "0000000000000000000000000000000000000000",
            );
            value
        } else {
            text.replace(needle, replacement)
        };
        fs::write(receipt, changed).unwrap();
        assert!(assert_rejected_atomically(&fixture, label).contains(expected));
    }
    let (_scratch, fixture) = fixture("magic");
    let binary = fixture
        .candidates
        .join("azdaja-candidate-aarch64-apple-darwin")
        .join(TARGETS[0].1);
    let mut bytes = fs::read(&binary).unwrap();
    bytes[0] = 0;
    fs::write(&binary, bytes).unwrap();
    write_receipt(
        binary.parent().unwrap(),
        &fixture.source_sha,
        TARGETS[0].0,
        TARGETS[0].1,
    );
    assert!(assert_rejected_atomically(&fixture, "magic").contains("wrong architecture"));
}

#[test]
fn promotion_rejects_dirty_or_mismatched_source_commit() {
    let (_scratch, fixture) = fixture("source");
    fs::write(fixture.root.join("dirty"), "dirty").unwrap();
    assert!(assert_rejected_atomically(&fixture, "dirty").contains("not clean"));
    fs::remove_file(fixture.root.join("dirty")).unwrap();
    let output_dir = fixture.root.parent().unwrap().join("out-mismatch");
    let output = run({
        let mut command = Command::new("sh");
        command
            .arg(fixture.root.join("release/promote-standalone-assets.sh"))
            .args([
                "0000000000000000000000000000000000000000",
                RUN_ID,
                RUN_ATTEMPT,
                fixture.candidates.to_str().unwrap(),
                output_dir.to_str().unwrap(),
            ])
            .current_dir(&fixture.root);
        command
    });
    assert!(!output.status.success());
    assert!(String::from_utf8_lossy(&output.stderr).contains("does not equal SOURCE_SHA"));
    assert!(!output_dir.exists());
}
