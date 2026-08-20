#![cfg(unix)]

use std::{
    fs,
    os::unix::fs::{MetadataExt, PermissionsExt, symlink},
    path::{Path, PathBuf},
    process::{Command, Output},
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
    assert!(stdout.contains("skill only (standalone kept)"));
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
            .contains("all five harness skills only (standalone kept)")
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
    binary
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
    assert!(next.contains("original installer"), "{next}");
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
            .contains("standalone only (harness skills kept)")
    );
    assert!(!binary.exists());
    assert!(!directory.join("azdaja-config.toml").exists());
    assert!(!directory.join("azdaja-config.toml.managed").exists());
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
            .contains("all five harness skills and standalone")
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
