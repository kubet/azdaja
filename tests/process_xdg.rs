#![cfg(unix)]

use std::{
    fs,
    os::unix::fs::PermissionsExt,
    path::{Path, PathBuf},
    process::{Command, Output, Stdio},
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

fn temp(name: &str) -> PathBuf {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let path = std::env::temp_dir().join(format!(
        "azdaja-process-xdg-{name}-{}-{nonce}",
        std::process::id()
    ));
    fs::create_dir_all(&path).unwrap();
    path
}

fn write_executable(path: &Path, body: &str) {
    fs::write(path, body).unwrap();
    fs::set_permissions(path, fs::Permissions::from_mode(0o755)).unwrap();
}

fn write_config(path: &Path, command: &str, timeout: u64) {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).unwrap();
    }
    fs::write(
        path,
        format!(
            r#"sub_llm_cmd = {command:?}
default_model = "test"
output_cap = 8192
max_depth = 1
sub_timeout = {timeout}
max_sessions = 4
cell_timeout = 2
idle_timeout = 60
clean_patterns = []
jcode_provider = "openai"
jcode_reasoning = "medium"
max_calls_per_cell = 8
"#,
        ),
    )
    .unwrap();
}

fn doctor(root: &Path, config: &Path) -> Output {
    Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .arg("doctor")
        .current_dir(root)
        .env("HOME", root.join("home"))
        .env("AZDAJA_HOME", root.join("state"))
        .env("AZDAJA_CONFIG", config)
        .output()
        .unwrap()
}

fn wait_file(path: &Path) {
    let deadline = Instant::now() + Duration::from_secs(3);
    while !path.exists() && Instant::now() < deadline {
        thread::sleep(Duration::from_millis(10));
    }
    assert!(path.exists(), "timed out waiting for {}", path.display());
}

fn wait_pid_gone(pid: i32) {
    let deadline = Instant::now() + Duration::from_secs(3);
    loop {
        let result = unsafe { libc::kill(pid, 0) };
        if result != 0 && std::io::Error::last_os_error().raw_os_error() == Some(libc::ESRCH) {
            return;
        }
        assert!(Instant::now() < deadline, "process {pid} survived custody");
        thread::sleep(Duration::from_millis(10));
    }
}

fn pids(path: &Path) -> (i32, i32) {
    let text = fs::read_to_string(path).unwrap();
    let mut parts = text.split_whitespace().map(|part| part.parse().unwrap());
    (parts.next().unwrap(), parts.next().unwrap())
}

#[test]
fn direct_success_and_error_cannot_leave_background_descendants_or_orphan_writes() {
    for exit_code in [0, 1] {
        let root = temp(&format!("direct-{exit_code}"));
        fs::create_dir_all(root.join("home")).unwrap();
        let provider = root.join("provider.py");
        let pid_file = root.join("pids");
        let orphan = root.join("ORPHAN");
        write_executable(
            &provider,
            r#"#!/usr/bin/env python3
import os, pathlib, subprocess, sys
child = subprocess.Popen([sys.executable, "-c", "import pathlib,sys,time; time.sleep(.4); pathlib.Path(sys.argv[1]).touch()", sys.argv[2]])
pathlib.Path(sys.argv[1]).write_text(f"{os.getpid()} {child.pid}")
print("AZDAJA", flush=True)
raise SystemExit(int(sys.argv[3]))
"#,
        );
        let config = root.join("config.toml");
        write_config(
            &config,
            &format!(
                "python3 {} {} {} {exit_code}",
                provider.display(),
                pid_file.display(),
                orphan.display()
            ),
            3,
        );
        let started = Instant::now();
        let output = doctor(&root, &config);
        assert!(started.elapsed() < Duration::from_secs(2), "{output:?}");
        assert_eq!(output.status.success(), exit_code == 0, "{output:?}");
        let (parent, descendant) = pids(&pid_file);
        wait_pid_gone(parent);
        wait_pid_gone(descendant);
        thread::sleep(Duration::from_millis(550));
        assert!(!orphan.exists(), "exit={exit_code} left an orphan write");
    }
}

#[test]
fn timeout_is_an_overall_pipe_deadline_and_removes_the_process_group() {
    let root = temp("timeout");
    fs::create_dir_all(root.join("home")).unwrap();
    let provider = root.join("provider.py");
    let pid_file = root.join("pids");
    write_executable(
        &provider,
        r#"#!/usr/bin/env python3
import os, pathlib, subprocess, sys, time
child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
pathlib.Path(sys.argv[1]).write_text(f"{os.getpid()} {child.pid}")
time.sleep(30)
"#,
    );
    let config = root.join("config.toml");
    write_config(
        &config,
        &format!("python3 {} {}", provider.display(), pid_file.display()),
        1,
    );
    let started = Instant::now();
    let output = doctor(&root, &config);
    assert!(!output.status.success());
    assert!(started.elapsed() < Duration::from_secs(3), "{output:?}");
    assert!(
        String::from_utf8_lossy(&output.stdout).contains("model connection failed"),
        "{output:?}"
    );
    let (group, descendant) = pids(&pid_file);
    wait_pid_gone(group);
    wait_pid_gone(descendant);
    let group_probe = unsafe { libc::kill(-group, 0) };
    assert_eq!(group_probe, -1);
    assert_eq!(
        std::io::Error::last_os_error().raw_os_error(),
        Some(libc::ESRCH)
    );
}

#[test]
fn term_and_hup_clean_prompt_and_descendants_with_conventional_status() {
    for signal in [libc::SIGTERM, libc::SIGHUP] {
        let root = temp(&format!("signal-{signal}"));
        fs::create_dir_all(root.join("home")).unwrap();
        let provider = root.join("provider.py");
        let pid_file = root.join("pids");
        write_executable(
            &provider,
            r#"#!/usr/bin/env python3
import os, pathlib, subprocess, sys, time
child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
pathlib.Path(sys.argv[2]).write_text(f"{os.getpid()} {child.pid}")
time.sleep(30)
"#,
        );
        let config = root.join("config.toml");
        write_config(
            &config,
            &format!(
                "python3 {} {{prompt_file}} {}",
                provider.display(),
                pid_file.display()
            ),
            20,
        );
        let input = root.join("input.txt");
        fs::write(&input, "context").unwrap();
        let child = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .args(["solo", "question", "-f"])
            .arg(&input)
            .current_dir(&root)
            .env("HOME", root.join("home"))
            .env("AZDAJA_HOME", root.join("state"))
            .env("AZDAJA_CONFIG", &config)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap();
        wait_file(&pid_file);
        assert_eq!(unsafe { libc::kill(child.id() as i32, signal) }, 0);
        let output = child.wait_with_output().unwrap();
        assert_eq!(output.status.code(), Some(128 + signal), "{output:?}");
        assert_eq!(
            String::from_utf8_lossy(&output.stderr),
            "Interrupted: provider stopped; temporary prompt removed.\n"
        );
        assert!(
            fs::read_dir(root.join("state/prompts"))
                .unwrap()
                .next()
                .is_none()
        );
        let (parent, descendant) = pids(&pid_file);
        wait_pid_gone(parent);
        wait_pid_gone(descendant);
    }
}

#[test]
fn empty_and_relative_xdg_roots_fall_back_to_home_not_cwd() {
    for (index, xdg) in ["", "relative-xdg"].into_iter().enumerate() {
        let root = temp(&format!("xdg-{index}"));
        let home = root.join("home");
        fs::create_dir_all(&home).unwrap();
        let safe = root.join("safe.py");
        write_executable(&safe, "#!/usr/bin/env python3\nprint('AZDAJA')\n");
        write_config(
            &home.join(".config/azdaja/config.toml"),
            &format!("python3 {}", safe.display()),
            2,
        );
        let marker = root.join("MALICIOUS_PROVIDER");
        let malicious = root.join("malicious.py");
        write_executable(
            &malicious,
            "#!/usr/bin/env python3\nimport pathlib,sys\npathlib.Path(sys.argv[1]).touch()\nprint('AZDAJA')\n",
        );
        let cwd_config = if xdg.is_empty() {
            root.join("azdaja/config.toml")
        } else {
            root.join(xdg).join("azdaja/config.toml")
        };
        write_config(
            &cwd_config,
            &format!("python3 {} {}", malicious.display(), marker.display()),
            2,
        );
        let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .arg("doctor")
            .current_dir(&root)
            .env("HOME", &home)
            .env("XDG_CONFIG_HOME", xdg)
            .env("XDG_STATE_HOME", xdg)
            .env_remove("AZDAJA_HOME")
            .env_remove("AZDAJA_CONFIG")
            .output()
            .unwrap();
        assert!(output.status.success(), "{output:?}");
        assert!(!marker.exists());
        assert!(home.join(".local/state/azdaja").is_dir());
        assert!(!root.join(xdg).join("azdaja/sessions").exists());
    }
}

#[test]
fn invalid_authoritative_overrides_fail_before_provider_entry() {
    let root = temp("overrides");
    let home = root.join("home");
    fs::create_dir_all(&home).unwrap();
    let marker = root.join("PROVIDER_ENTERED");
    let provider = root.join("provider.py");
    write_executable(
        &provider,
        "#!/usr/bin/env python3\nimport pathlib,sys\npathlib.Path(sys.argv[1]).touch()\nprint('AZDAJA')\n",
    );
    let config = root.join("config.toml");
    write_config(
        &config,
        &format!("python3 {} {}", provider.display(), marker.display()),
        2,
    );

    for value in ["", "relative-state"] {
        let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .arg("doctor")
            .current_dir(&root)
            .env("HOME", &home)
            .env("AZDAJA_HOME", value)
            .env("AZDAJA_CONFIG", &config)
            .output()
            .unwrap();
        assert!(!output.status.success());
        assert!(
            String::from_utf8_lossy(&output.stdout)
                .contains("AZDAJA_HOME must be set to a non-empty absolute path")
        );
        assert!(!marker.exists());
    }

    let relative = root.join("relative-config");
    write_config(
        &relative,
        &format!("python3 {} {}", provider.display(), marker.display()),
        2,
    );
    for value in ["", "relative-config"] {
        let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .arg("doctor")
            .current_dir(&root)
            .env("HOME", &home)
            .env("AZDAJA_HOME", root.join("state"))
            .env("AZDAJA_CONFIG", value)
            .output()
            .unwrap();
        assert!(!output.status.success());
        assert!(
            String::from_utf8_lossy(&output.stdout)
                .contains("AZDAJA_CONFIG must be set to a non-empty absolute path")
        );
        assert!(!marker.exists());
    }
}

#[test]
fn rust_targets_use_absolute_xdg_fallback_and_unicode_paths_and_reject_bad_jcode_home() {
    let root = temp("targets");
    let home = root.join("home-雪 ' space");
    fs::create_dir_all(&home).unwrap();

    let fallback = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args(["install", "--harness", "opencode"])
        .current_dir(&root)
        .env("HOME", &home)
        .env("XDG_CONFIG_HOME", "relative-config")
        .env_remove("JCODE_HOME")
        .output()
        .unwrap();
    assert!(fallback.status.success(), "{fallback:?}");
    assert!(home.join(".config/opencode/skills/azdaja").is_dir());
    assert!(!root.join("relative-config/opencode/skills/azdaja").exists());

    let unicode_xdg = root.join("配置 💾");
    let unicode = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args(["install", "--harness", "opencode"])
        .current_dir(&root)
        .env("HOME", &home)
        .env("XDG_CONFIG_HOME", &unicode_xdg)
        .env_remove("JCODE_HOME")
        .output()
        .unwrap();
    assert!(unicode.status.success(), "{unicode:?}");
    assert!(unicode_xdg.join("opencode/skills/azdaja").is_dir());

    for value in ["", "relative-jcode"] {
        let invalid = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .args(["install", "--harness", "jcode"])
            .current_dir(&root)
            .env("HOME", &home)
            .env("JCODE_HOME", value)
            .output()
            .unwrap();
        assert!(!invalid.status.success());
        assert!(
            String::from_utf8_lossy(&invalid.stderr)
                .contains("JCODE_HOME must be set to a non-empty absolute path")
        );
    }

    let shell = Path::new(env!("CARGO_MANIFEST_DIR")).join("install.sh");
    let shell_invalid = Command::new("sh")
        .arg(shell)
        .args(["--harness", "jcode"])
        .env("HOME", &home)
        .env("JCODE_HOME", "relative-jcode")
        .output()
        .unwrap();
    assert!(!shell_invalid.status.success());
    assert!(
        String::from_utf8_lossy(&shell_invalid.stderr)
            .contains("JCODE_HOME must be set to a non-empty absolute path")
    );
}

#[test]
fn shell_ignores_empty_and_relative_xdg_config_during_detection() {
    let shell = Path::new(env!("CARGO_MANIFEST_DIR")).join("install.sh");
    for (index, value) in ["", "relative-xdg"].into_iter().enumerate() {
        let root = temp(&format!("shell-xdg-{index}"));
        let home = root.join("home");
        fs::create_dir_all(&home).unwrap();
        let malicious = if value.is_empty() {
            root.join("opencode")
        } else {
            root.join(value).join("opencode")
        };
        fs::create_dir_all(malicious).unwrap();
        let output = Command::new("sh")
            .arg(&shell)
            .current_dir(&root)
            .env("HOME", &home)
            .env("XDG_CONFIG_HOME", value)
            .env("PATH", "/usr/bin:/bin")
            .env("AZDAJA_INSTALL_BASE_URL", "must-not-reach-validation")
            .output()
            .unwrap();
        assert!(!output.status.success());
        assert!(
            String::from_utf8_lossy(&output.stderr).contains("no supported harness found"),
            "{output:?}"
        );
    }
}

#[test]
fn unicode_absolute_config_and_state_overrides_remain_supported() {
    let root = temp("unicode-overrides");
    let home = root.join("home");
    fs::create_dir_all(&home).unwrap();
    let provider = root.join("provider.py");
    write_executable(&provider, "#!/usr/bin/env python3\nprint('AZDAJA')\n");
    let config = root.join("設定 🐉/config.toml");
    write_config(&config, &format!("python3 {}", provider.display()), 2);
    let state = root.join("状態 💾");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .arg("doctor")
        .current_dir(&root)
        .env("HOME", &home)
        .env("AZDAJA_HOME", &state)
        .env("AZDAJA_CONFIG", &config)
        .output()
        .unwrap();
    assert!(output.status.success(), "{output:?}");
    assert!(state.is_dir());
}
