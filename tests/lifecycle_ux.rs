#![cfg(unix)]

use std::{
    fs,
    io::Write,
    os::unix::fs::{MetadataExt, PermissionsExt, symlink},
    path::{Path, PathBuf},
    process::{Command, Output, Stdio},
    sync::{Arc, Barrier},
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

struct Scratch(PathBuf);
impl Scratch {
    fn new(label: &str) -> Self {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "azdaja-lifecycle-{label}-{}-{nonce}",
            std::process::id()
        ));
        fs::create_dir(&path).unwrap();
        Self(path)
    }
}
impl Drop for Scratch {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn run(binary: &Path, home: &Path, args: &[&str]) -> Output {
    Command::new(binary)
        .args(args)
        .env("HOME", home)
        .env("XDG_CONFIG_HOME", home.join("xdg"))
        .env("AZDAJA_HOME", home.join("state"))
        .env_remove("AZDAJA_CONFIG")
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap()
}
fn run_with_jcode_home(binary: &Path, home: &Path, jcode_home: &Path, args: &[&str]) -> Output {
    Command::new(binary)
        .args(args)
        .env("HOME", home)
        .env("JCODE_HOME", jcode_home)
        .env("XDG_CONFIG_HOME", home.join("xdg"))
        .env("AZDAJA_HOME", home.join("state"))
        .env("PATH", "/usr/bin:/bin")
        .env_remove("AZDAJA_CONFIG")
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap()
}
fn text(output: &Output) -> (&str, &str) {
    (
        std::str::from_utf8(&output.stdout).unwrap(),
        std::str::from_utf8(&output.stderr).unwrap(),
    )
}
fn assert_success(output: &Output) -> &str {
    let (stdout, stderr) = text(output);
    assert!(output.status.success(), "stdout={stdout} stderr={stderr}");
    assert!(stderr.is_empty(), "{stderr}");
    stdout
}
fn targets(home: &Path) -> [PathBuf; 5] {
    [
        home.join(".jcode/skills/azdaja"),
        home.join(".claude/skills/azdaja"),
        home.join(".agents/skills/azdaja"),
        home.join(".gemini/skills/azdaja"),
        home.join("xdg/opencode/skills/azdaja"),
    ]
}
fn install_all(home: &Path) -> String {
    let output = run(
        Path::new(env!("CARGO_BIN_EXE_azdaja")),
        home,
        &["install", "--harness", "all"],
    );
    assert_success(&output).to_owned()
}

#[test]
fn all_harness_install_and_custody_doctor_are_provider_free_and_session_honest() {
    let scratch = Scratch::new("custody-all");
    let provider = scratch.0.join("provider-must-not-run");
    fs::write(
        &provider,
        format!(
            "#!/bin/sh\nprintf called > {:?}\nexit 91\n",
            scratch.0.join("provider-called").to_str().unwrap()
        ),
    )
    .unwrap();
    fs::set_permissions(&provider, fs::Permissions::from_mode(0o755)).unwrap();

    let stdout = install_all(&scratch.0);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    assert!(
        stdout
            .lines()
            .last()
            .unwrap()
            .contains("reload/restart all five harnesses")
    );
    for target in targets(&scratch.0) {
        assert!(target.join(".azdaja-managed").is_file());
    }

    // Even replacing every adapter string with a sentinel would be harmless:
    // the custody route only parses the managed files.
    for target in targets(&scratch.0) {
        let config = target.join("config.toml");
        let original = fs::read_to_string(&config).unwrap();
        fs::write(
            &config,
            original.replace(
                original
                    .lines()
                    .find(|line| line.starts_with("sub_llm_cmd = "))
                    .unwrap(),
                &format!("sub_llm_cmd = {:?}", provider.to_str().unwrap()),
            ),
        )
        .unwrap();
        // Reinstall records the deliberately customized configuration in the marker.
    }
    install_all(&scratch.0);
    let output = run(
        Path::new(env!("CARGO_BIN_EXE_azdaja")),
        &scratch.0,
        &["doctor", "--harness", "all"],
    );
    let stdout = assert_success(&output);
    assert_eq!(stdout.lines().count(), 10, "{stdout}");
    assert_eq!(
        stdout
            .lines()
            .filter(|line| line.starts_with("PASS ") && line.contains("installed on disk"))
            .count(),
        5
    );
    assert!(stdout.contains("already-open Jcode session"));
    assert!(stdout.contains("skill_manage reload_all"));
    assert!(stdout.contains("/skills -> Reload all"));
    assert!(stdout.contains("fresh Jcode session"));
    assert!(!scratch.0.join("provider-called").exists());
}

#[test]
fn custom_jcode_home_is_authoritative_and_next_command_is_shell_quoted() {
    let scratch = Scratch::new("jcode-home");
    let binary = Path::new(env!("CARGO_BIN_EXE_azdaja"));
    let custom = scratch.0.join("custom Jcode ☃ ' registry");
    fs::create_dir_all(&custom).unwrap();

    // No explicit selector: detection must honor JCODE_HOME rather than HOME/.jcode.
    let output = run_with_jcode_home(binary, &scratch.0, &custom, &["install"]);
    let stdout = assert_success(&output);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    assert!(stdout.lines().next().unwrap().contains("jcode (directory)"));
    let target = custom.join("skills/azdaja");
    assert!(target.join("azdaja").is_file());
    assert!(!scratch.0.join(".jcode/skills/azdaja").exists());

    let managed = target.join("azdaja");
    let quoted = format!("'{}'", managed.to_string_lossy().replace('\'', "'\\''"));
    let next = stdout.lines().last().unwrap();
    assert!(
        next.contains(&format!("run {quoted} doctor; then")),
        "{next}"
    );
    let command = next
        .strip_prefix("Next: run ")
        .unwrap()
        .split_once("; then")
        .unwrap()
        .0;
    let syntax = Command::new("sh")
        .args(["-n", "-c", command])
        .output()
        .unwrap();
    assert!(syntax.status.success(), "command={command}");

    let doctor = run_with_jcode_home(
        binary,
        &scratch.0,
        &custom,
        &["doctor", "--harness", "jcode"],
    );
    assert!(assert_success(&doctor).contains("installed on disk"));
    let uninstall = run_with_jcode_home(
        binary,
        &scratch.0,
        &custom,
        &["uninstall", "--harness", "jcode"],
    );
    let stdout = assert_success(&uninstall);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    assert!(stdout.contains("skill only (standalone and documents kept)"));
    assert!(!target.exists());
}

#[test]
fn install_and_uninstall_are_exactly_three_lines_with_harness_reload_guidance() {
    let scratch = Scratch::new("three-lines");
    let binary = Path::new(env!("CARGO_BIN_EXE_azdaja"));
    let install = run(binary, &scratch.0, &["install", "--harness", "jcode"]);
    let stdout = assert_success(&install);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    let next = stdout.lines().last().unwrap();
    let managed = scratch.0.join(".jcode/skills/azdaja/azdaja");
    assert!(next.contains(&format!("'{}' doctor", managed.display())));
    assert!(next.contains("skill_manage reload_all"));

    for _ in 0..2 {
        let uninstall = run(binary, &scratch.0, &["uninstall", "--harness", "jcode"]);
        let stdout = assert_success(&uninstall);
        assert_eq!(stdout.lines().count(), 3, "{stdout}");
        assert!(stdout.lines().last().unwrap().contains("restart Jcode"));
    }

    install_all(&scratch.0);
    let uninstall_all = run(binary, &scratch.0, &["uninstall", "--harness", "all"]);
    let stdout = assert_success(&uninstall_all);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    assert!(
        stdout
            .lines()
            .next()
            .unwrap()
            .contains("all five harness skills only (standalone and documents kept)")
    );
    assert!(
        stdout
            .lines()
            .last()
            .unwrap()
            .contains("all five harnesses")
    );
    assert!(targets(&scratch.0).iter().all(|path| !path.exists()));
}

#[test]
fn all_harness_uninstall_preflights_unknown_changed_and_symlink_targets() {
    let scratch = Scratch::new("preflight");
    let binary = Path::new(env!("CARGO_BIN_EXE_azdaja"));
    install_all(&scratch.0);
    let all = targets(&scratch.0);

    fs::write(all[1].join("unknown"), "foreign").unwrap();
    let refused = run(binary, &scratch.0, &["uninstall", "--harness", "all"]);
    assert!(!refused.status.success());
    assert!(all.iter().all(|path| path.exists()));
    fs::remove_file(all[1].join("unknown")).unwrap();

    let original_skill = fs::read(all[2].join("SKILL.md")).unwrap();
    fs::write(all[2].join("SKILL.md"), "changed").unwrap();
    let refused = run(binary, &scratch.0, &["uninstall", "--harness", "all"]);
    assert!(!refused.status.success());
    assert!(all[0].exists(), "an earlier target was partially removed");
    fs::write(all[2].join("SKILL.md"), original_skill).unwrap();

    let victim = scratch.0.join("victim");
    fs::create_dir(&victim).unwrap();
    fs::write(victim.join("sentinel"), "unchanged").unwrap();
    fs::remove_dir_all(&all[3]).unwrap();
    symlink(&victim, &all[3]).unwrap();
    let refused = run(binary, &scratch.0, &["uninstall", "--harness", "all"]);
    assert!(!refused.status.success());
    assert_eq!(fs::read(victim.join("sentinel")).unwrap(), b"unchanged");
    assert!(all[0].exists(), "symlink refusal happened after mutation");
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

fn standalone(home: &Path, name: &str) -> PathBuf {
    let directory = home.join(name);
    fs::create_dir_all(&directory).unwrap();
    let binary = directory.join("azdaja");
    fs::copy(env!("CARGO_BIN_EXE_azdaja"), &binary).unwrap();
    fs::set_permissions(&binary, fs::Permissions::from_mode(0o755)).unwrap();
    fs::write(
        directory.join("azdaja-config.toml"),
        include_str!("../assets/config.toml"),
    )
    .unwrap();
    fs::write(
        directory.join("azdaja-config.toml.managed"),
        "azdaja-installer-owned-config-v1\n",
    )
    .unwrap();
    let documents = home.join(".local/share/azdaja");
    fs::create_dir_all(&documents).unwrap();
    fs::write(documents.join("LICENSE"), include_bytes!("../LICENSE")).unwrap();
    fs::write(
        documents.join("THIRD-PARTY-NOTICES.md"),
        include_bytes!("../THIRD-PARTY-NOTICES.md"),
    )
    .unwrap();
    fs::write(documents.join(".azdaja-managed"), DOCUMENT_OWNER_V2).unwrap();
    binary
}

fn legacy_standalone(home: &Path, name: &str) -> Option<PathBuf> {
    let notices = legacy_notices()?;
    let binary = standalone(home, name);
    let documents = home.join(".local/share/azdaja");
    fs::write(documents.join("THIRD-PARTY-NOTICES.md"), notices).unwrap();
    fs::write(documents.join(".azdaja-managed"), DOCUMENT_OWNER_V1).unwrap();
    Some(binary)
}

#[test]
fn unmanaged_standalone_uninstall_points_to_original_installer_or_cargo() {
    let scratch = Scratch::new("unmanaged-standalone");
    let directory = scratch.0.join("cargo bin");
    fs::create_dir_all(&directory).unwrap();
    let binary = directory.join("azdaja");
    fs::copy(env!("CARGO_BIN_EXE_azdaja"), &binary).unwrap();
    fs::set_permissions(&binary, fs::Permissions::from_mode(0o755)).unwrap();

    let output = run(&binary, &scratch.0, &["uninstall", "--standalone"]);
    let stdout = assert_success(&output);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    assert!(stdout.contains("standalone not installer-managed (left untouched)"));
    let next = stdout.lines().last().unwrap();
    assert!(next.contains("THIRD-PARTY-NOTICES.md"), "{next}");
    assert!(next.contains("cargo uninstall azdaja"), "{next}");
    assert!(
        binary.is_file(),
        "unmanaged executable must remain untouched"
    );
}

#[test]
fn standalone_and_full_all_self_uninstall_preserve_foreign_neighbors() {
    let scratch = Scratch::new("standalone");
    let binary = standalone(&scratch.0, "custom bin");
    let directory = binary.parent().unwrap();
    symlink("foreign-az", directory.join("az")).unwrap();
    fs::write(directory.join("foreign-az"), "victim").unwrap();
    fs::write(directory.join("neighbor"), "keep").unwrap();
    let output = run(&binary, &scratch.0, &["uninstall", "--standalone"]);
    let stdout = assert_success(&output);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    assert!(
        stdout
            .lines()
            .next()
            .unwrap()
            .contains("standalone and documents only (harness skills kept)")
    );
    assert!(!binary.exists());
    assert!(!directory.join("azdaja-config.toml").exists());
    assert!(!directory.join("azdaja-config.toml.managed").exists());
    assert!(!scratch.0.join(".local/share/azdaja").exists());
    assert_eq!(
        fs::read_link(directory.join("az")).unwrap(),
        PathBuf::from("foreign-az")
    );
    assert_eq!(fs::read(directory.join("neighbor")).unwrap(), b"keep");

    let full = standalone(&scratch.0, "full bin");
    symlink("azdaja", full.parent().unwrap().join("az")).unwrap();
    install_all_with(&full, &scratch.0);
    let output = run(&full, &scratch.0, &["uninstall", "--all"]);
    let stdout = assert_success(&output);
    assert_eq!(stdout.lines().count(), 3, "{stdout}");
    assert!(
        stdout
            .lines()
            .next()
            .unwrap()
            .contains("all five harness skills, standalone, and documents")
    );
    assert!(
        stdout
            .lines()
            .last()
            .unwrap()
            .contains("all five harnesses")
    );
    assert!(targets(&scratch.0).iter().all(|path| !path.exists()));
    assert!(
        fs::read_dir(full.parent().unwrap())
            .unwrap()
            .next()
            .is_none()
    );
}

#[test]
fn exact_legacy_v1_standalone_documents_are_safely_removable() {
    let scratch = Scratch::new("legacy-standalone");
    let Some(binary) = legacy_standalone(&scratch.0, "bin") else {
        return;
    };
    let output = run(&binary, &scratch.0, &["uninstall", "--standalone"]);
    assert_success(&output);
    assert!(!binary.exists());
    assert!(!scratch.0.join(".local/share/azdaja").exists());
}

#[test]
fn fake_v2_and_mutated_legacy_standalone_documents_refuse_before_mutation() {
    for state in ["fake-v2", "mutated-legacy"] {
        if state == "mutated-legacy" && legacy_notices().is_none() {
            continue;
        }
        let scratch = Scratch::new(state);
        let binary = if state == "fake-v2" {
            standalone(&scratch.0, "bin")
        } else {
            legacy_standalone(&scratch.0, "bin").unwrap()
        };
        let documents = scratch.0.join(".local/share/azdaja");
        if state == "fake-v2" {
            fs::write(
                documents.join(".azdaja-managed"),
                b"azdaja-installer-owned-docs-v2\nschema=azdaja-managed-documents-v2\nLICENSE.sha256=ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff\nTHIRD-PARTY-NOTICES.md.sha256=eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee\n",
            )
            .unwrap();
        } else {
            let mut notices = legacy_notices().unwrap();
            notices.extend_from_slice(b"mutated");
            fs::write(documents.join("THIRD-PARTY-NOTICES.md"), notices).unwrap();
        }
        let binary_before = surface_snapshot(binary.parent().unwrap());
        let documents_before = surface_snapshot(&documents);
        let output = run(&binary, &scratch.0, &["uninstall", "--standalone"]);
        assert!(!output.status.success(), "state={state}");
        assert_eq!(surface_snapshot(binary.parent().unwrap()), binary_before);
        assert_eq!(surface_snapshot(&documents), documents_before);
    }
}

#[test]
fn standalone_document_quarantine_rolls_back_v2_and_legacy_at_every_injected_step() {
    for legacy in [false, true] {
        if legacy && legacy_notices().is_none() {
            continue;
        }
        let scratch = Scratch::new(if legacy { "rollback-v1" } else { "rollback-v2" });
        let binary = if legacy {
            legacy_standalone(&scratch.0, "bin").unwrap()
        } else {
            standalone(&scratch.0, "bin")
        };
        let documents = scratch.0.join(".local/share/azdaja");
        let binary_before = surface_snapshot(binary.parent().unwrap());
        let documents_before = surface_snapshot(&documents);
        for fail_at in 1..=4 {
            let fail_at = fail_at.to_string();
            let output = run_with_lifecycle_env(
                &binary,
                &scratch.0,
                &["uninstall", "--standalone"],
                &[("AZDAJA_LIFECYCLE_TEST_FAIL_AT", &fail_at)],
            );
            assert!(
                !output.status.success(),
                "legacy={legacy} fail_at={fail_at}"
            );
            assert!(text(&output).1.contains("injected lifecycle failure"));
            assert_eq!(surface_snapshot(binary.parent().unwrap()), binary_before);
            assert_eq!(surface_snapshot(&documents), documents_before);
            assert!(fs::read_dir(&scratch.0).unwrap().all(|entry| {
                !entry
                    .unwrap()
                    .file_name()
                    .to_string_lossy()
                    .contains("uninstall")
            }));
        }
    }
}

#[test]
fn concurrent_standalone_document_lifecycle_has_one_owner_and_no_quarantine_leak() {
    let scratch = Scratch::new("concurrent-standalone");
    let first = standalone(&scratch.0, "first-bin");
    let second = standalone(&scratch.0, "second-bin");
    let barrier = Arc::new(Barrier::new(3));
    let mut workers = Vec::new();
    for binary in [first.clone(), second.clone()] {
        let barrier = Arc::clone(&barrier);
        let home = scratch.0.clone();
        workers.push(thread::spawn(move || {
            barrier.wait();
            run(&binary, &home, &["uninstall", "--standalone"])
        }));
    }
    barrier.wait();
    let outputs = workers
        .into_iter()
        .map(|worker| worker.join().unwrap())
        .collect::<Vec<_>>();
    assert_eq!(
        outputs
            .iter()
            .filter(|output| output.status.success())
            .count(),
        1
    );
    assert!(!scratch.0.join(".local/share/azdaja").exists());
    assert_eq!(
        [first.exists(), second.exists()]
            .into_iter()
            .filter(|exists| *exists)
            .count(),
        1
    );
    for parent in [scratch.0.clone(), scratch.0.join(".local/share")] {
        if let Ok(entries) = fs::read_dir(parent) {
            assert!(
                entries
                    .map(|entry| entry.unwrap().file_name().to_string_lossy().into_owned())
                    .all(|name| !name.contains("docs-uninstall")
                        && !name.contains("azdaja-uninstall"))
            );
        }
    }
}

fn install_all_with(binary: &Path, home: &Path) {
    let output = run(binary, home, &["install", "--harness", "all"]);
    assert_success(&output);
}

#[test]
fn foreign_standalone_config_refuses_full_all_before_harness_mutation() {
    let scratch = Scratch::new("foreign-config");
    let directory = scratch.0.join("foreign bin");
    fs::create_dir(&directory).unwrap();
    let binary = directory.join("azdaja");
    fs::copy(env!("CARGO_BIN_EXE_azdaja"), &binary).unwrap();
    fs::set_permissions(&binary, fs::Permissions::from_mode(0o755)).unwrap();
    fs::write(
        directory.join("azdaja-config.toml"),
        include_str!("../assets/config.toml"),
    )
    .unwrap();
    install_all_with(&binary, &scratch.0);
    let output = run(&binary, &scratch.0, &["uninstall", "--all"]);
    assert!(!output.status.success());
    assert!(text(&output).1.contains("incomplete standalone ownership"));
    assert!(binary.exists());
    assert!(targets(&scratch.0).iter().all(|path| path.exists()));
}

#[derive(Debug, Eq, PartialEq)]
struct SurfaceEntry {
    relative: PathBuf,
    directory: bool,
    bytes: Vec<u8>,
    mode: u32,
    dev: u64,
    ino: u64,
}

fn surface_snapshot(root: &Path) -> Vec<SurfaceEntry> {
    fn visit(root: &Path, path: &Path, entries: &mut Vec<SurfaceEntry>) {
        let metadata = fs::symlink_metadata(path).unwrap();
        let relative = path.strip_prefix(root).unwrap().to_path_buf();
        let directory = metadata.file_type().is_dir();
        entries.push(SurfaceEntry {
            relative,
            directory,
            bytes: if directory {
                Vec::new()
            } else {
                fs::read(path).unwrap()
            },
            mode: metadata.mode(),
            dev: metadata.dev(),
            ino: metadata.ino(),
        });
        if directory {
            let mut children = fs::read_dir(path)
                .unwrap()
                .map(|entry| entry.unwrap().path())
                .collect::<Vec<_>>();
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

fn selected_snapshots(home: &Path) -> Vec<Vec<SurfaceEntry>> {
    targets(home)
        .iter()
        .map(|target| surface_snapshot(target))
        .collect()
}

fn lifecycle_artifacts(home: &Path) -> Vec<PathBuf> {
    let mut artifacts = Vec::new();
    for target in targets(home) {
        if let Some(parent) = target.parent()
            && let Ok(entries) = fs::read_dir(parent)
        {
            for entry in entries {
                let path = entry.unwrap().path();
                let name = path.file_name().unwrap().to_string_lossy();
                if name.starts_with(".azdaja-stage-") || name.starts_with(".azdaja-backup-") {
                    artifacts.push(path);
                }
            }
        }
    }
    artifacts
}

fn run_with_lifecycle_env(
    binary: &Path,
    home: &Path,
    args: &[&str],
    extra: &[(&str, &str)],
) -> Output {
    let mut command = Command::new(binary);
    command
        .args(args)
        .env("HOME", home)
        .env("XDG_CONFIG_HOME", home.join("xdg"))
        .env("AZDAJA_HOME", home.join("state"))
        .env_remove("AZDAJA_CONFIG")
        .env_remove("RLM_DEPTH");
    for (name, value) in extra {
        command.env(name, value);
    }
    command.output().unwrap()
}

#[test]
fn concurrent_reinstall_barrier_two_workers_twenty_reinstalls_never_loses_target_or_leaks() {
    let scratch = Scratch::new("concurrent-reinstall");
    let binary = PathBuf::from(env!("CARGO_BIN_EXE_azdaja"));
    assert_success(&run(
        &binary,
        &scratch.0,
        &["install", "--harness", "jcode"],
    ));

    for _round in 0..10 {
        let barrier = Arc::new(Barrier::new(3));
        let mut workers = Vec::new();
        for _ in 0..2 {
            let barrier = Arc::clone(&barrier);
            let binary = binary.clone();
            let home = scratch.0.clone();
            workers.push(thread::spawn(move || {
                barrier.wait();
                run(&binary, &home, &["install", "--harness", "jcode"])
            }));
        }
        barrier.wait();
        for worker in workers {
            let output = worker.join().unwrap();
            assert_success(&output);
        }
        let target = scratch.0.join(".jcode/skills/azdaja");
        assert!(target.is_dir());
        assert!(lifecycle_artifacts(&scratch.0).is_empty());
        let doctor = run(&binary, &scratch.0, &["doctor", "--harness", "jcode"]);
        assert!(assert_success(&doctor).contains("PASS jcode"));
    }
}

#[test]
fn all_harness_install_and_uninstall_roll_back_every_injected_target_failure() {
    let scratch = Scratch::new("all-failpoints");
    let binary = Path::new(env!("CARGO_BIN_EXE_azdaja"));
    install_all(&scratch.0);

    // A deliberately customized managed config remains supported and must be
    // preserved byte-for-byte (and by inode) through every rollback.
    let config = targets(&scratch.0)[2].join("config.toml");
    let original = fs::read_to_string(&config).unwrap();
    let model_line = original
        .lines()
        .find(|line| line.starts_with("default_model = "))
        .unwrap();
    fs::write(
        &config,
        original.replace(model_line, "default_model = \"custom-rollback-model\""),
    )
    .unwrap();
    let expected = selected_snapshots(&scratch.0);

    for command_name in ["install", "uninstall"] {
        for fail_at in 1..=5 {
            let fail_at = fail_at.to_string();
            let output = run_with_lifecycle_env(
                binary,
                &scratch.0,
                &[command_name, "--harness", "all"],
                &[("AZDAJA_LIFECYCLE_TEST_FAIL_AT", &fail_at)],
            );
            assert!(!output.status.success(), "{command_name} step {fail_at}");
            assert!(
                text(&output).1.contains("injected lifecycle failure"),
                "{}",
                text(&output).1
            );
            assert_eq!(selected_snapshots(&scratch.0), expected);
            assert!(lifecycle_artifacts(&scratch.0).is_empty());
        }
    }
}

fn wait_for_barrier(path: &Path) {
    let deadline = Instant::now() + Duration::from_secs(60);
    while !path.exists() {
        assert!(
            Instant::now() < deadline,
            "lifecycle barrier did not become ready"
        );
        thread::sleep(Duration::from_millis(2));
    }
}

#[test]
fn late_unknown_and_changed_targets_abort_without_touching_other_selected_surfaces() {
    let scratch = Scratch::new("late-selected-change");
    let binary = PathBuf::from(env!("CARGO_BIN_EXE_azdaja"));
    install_all(&scratch.0);
    let all = targets(&scratch.0);

    let barrier = scratch.0.join("install-late");
    let barrier_value = barrier.to_string_lossy().into_owned();
    let ready = PathBuf::from(format!("{barrier_value}.ready"));
    let go = PathBuf::from(format!("{barrier_value}.go"));
    let home = scratch.0.clone();
    let install_binary = binary.clone();
    let install = thread::spawn(move || {
        run_with_lifecycle_env(
            &install_binary,
            &home,
            &["install", "--harness", "all"],
            &[("AZDAJA_LIFECYCLE_TEST_BARRIER", &barrier_value)],
        )
    });
    wait_for_barrier(&ready);
    fs::write(all[4].join("late-unknown"), b"foreign").unwrap();
    let expected = selected_snapshots(&scratch.0);
    fs::write(&go, b"go").unwrap();
    let output = install.join().unwrap();
    assert!(!output.status.success());
    assert!(text(&output).1.contains("unknown files"));
    assert_eq!(selected_snapshots(&scratch.0), expected);
    assert!(lifecycle_artifacts(&scratch.0).is_empty());
    fs::remove_file(all[4].join("late-unknown")).unwrap();

    let barrier = scratch.0.join("uninstall-late");
    let barrier_value = barrier.to_string_lossy().into_owned();
    let ready = PathBuf::from(format!("{barrier_value}.ready"));
    let go = PathBuf::from(format!("{barrier_value}.go"));
    let home = scratch.0.clone();
    let uninstall_binary = binary.clone();
    let uninstall = thread::spawn(move || {
        run_with_lifecycle_env(
            &uninstall_binary,
            &home,
            &["uninstall", "--harness", "all"],
            &[("AZDAJA_LIFECYCLE_TEST_BARRIER", &barrier_value)],
        )
    });
    wait_for_barrier(&ready);
    fs::write(all[4].join("SKILL.md"), b"late changed bytes").unwrap();
    let expected = selected_snapshots(&scratch.0);
    fs::write(&go, b"go").unwrap();
    let output = uninstall.join().unwrap();
    assert!(!output.status.success());
    assert!(text(&output).1.contains("changed file"));
    assert_eq!(selected_snapshots(&scratch.0), expected);
    assert!(lifecycle_artifacts(&scratch.0).is_empty());
}

#[test]
fn all_harness_staging_permission_failure_occurs_before_any_commit() {
    let scratch = Scratch::new("stage-permission");
    let binary = Path::new(env!("CARGO_BIN_EXE_azdaja"));
    install_all(&scratch.0);
    let expected = selected_snapshots(&scratch.0);
    let late_parent = targets(&scratch.0)[4].parent().unwrap().to_path_buf();
    let prior_mode = fs::metadata(&late_parent).unwrap().permissions().mode();
    fs::set_permissions(&late_parent, fs::Permissions::from_mode(0o500)).unwrap();
    let output = run(binary, &scratch.0, &["install", "--harness", "all"]);
    fs::set_permissions(&late_parent, fs::Permissions::from_mode(prior_mode)).unwrap();
    assert!(!output.status.success());
    assert_eq!(selected_snapshots(&scratch.0), expected);
    assert!(lifecycle_artifacts(&scratch.0).is_empty());
}

#[test]
fn harness_only_uninstall_keeps_exact_owned_documents() {
    let scratch = Scratch::new("harness-keeps-docs");
    let binary = standalone(&scratch.0, "bin");
    install_all_with(&binary, &scratch.0);
    let documents = scratch.0.join(".local/share/azdaja");
    let before = surface_snapshot(&documents);
    let output = run(&binary, &scratch.0, &["uninstall", "--harness", "all"]);
    let stdout = assert_success(&output);
    assert!(stdout.contains("standalone and documents kept"));
    assert_eq!(surface_snapshot(&documents), before);
    assert!(binary.exists());
    assert!(targets(&scratch.0).iter().all(|path| !path.exists()));
}

#[test]
fn changed_foreign_symlink_and_hardlinked_documents_refuse_all_before_mutation() {
    for state in ["changed", "foreign", "symlink", "hardlink"] {
        let scratch = Scratch::new(state);
        let binary = standalone(&scratch.0, "bin");
        install_all_with(&binary, &scratch.0);
        let docs = scratch.0.join(".local/share/azdaja");
        match state {
            "changed" => fs::write(docs.join("THIRD-PARTY-NOTICES.md"), b"changed").unwrap(),
            "foreign" => fs::write(docs.join("foreign"), b"keep").unwrap(),
            "symlink" => {
                let notice = docs.join("THIRD-PARTY-NOTICES.md");
                fs::remove_file(&notice).unwrap();
                symlink("LICENSE", notice).unwrap();
            }
            "hardlink" => {
                let license = docs.join("LICENSE");
                fs::hard_link(&license, scratch.0.join("license-second-link")).unwrap();
            }
            _ => unreachable!(),
        }
        let before = surface_snapshot(&scratch.0);
        let output = run(&binary, &scratch.0, &["uninstall", "--all"]);
        assert!(!output.status.success(), "state={state}");
        assert_eq!(surface_snapshot(&scratch.0), before, "state={state}");
        assert!(binary.exists());
        assert!(targets(&scratch.0).iter().all(|path| path.exists()));
    }
}
