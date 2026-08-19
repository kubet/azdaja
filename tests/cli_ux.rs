#![cfg(unix)]

use std::{
    fs,
    os::unix::fs::PermissionsExt,
    path::{Path, PathBuf},
    process::{Command, Output},
    time::{SystemTime, UNIX_EPOCH},
};

struct Scratch(PathBuf);
impl Scratch {
    fn new(name: &str) -> Self {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "azdaja-cli-ux-{name}-{}-{nonce}",
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

fn binary() -> &'static str {
    env!("CARGO_BIN_EXE_azdaja")
}
fn config(path: &Path, command: &str) -> PathBuf {
    let config = path.join("config.toml");
    fs::write(
        &config,
        format!(
            r#"sub_llm_cmd = {command:?}
default_model = "mock"
output_cap = 512
max_depth = 1
sub_timeout = 3
max_sessions = 4
cell_timeout = 2
idle_timeout = 1800
clean_patterns = []
jcode_provider = "openai"
jcode_reasoning = "medium"
max_calls_per_cell = 64
"#
        ),
    )
    .unwrap();
    config
}
fn command(home: &Path) -> Command {
    let mut command = Command::new(binary());
    command
        .env("HOME", home)
        .env("AZDAJA_HOME", home.join("state"))
        .env_remove("RLM_DEPTH");
    command
}
fn utf8(output: &Output) -> (&str, &str) {
    (
        std::str::from_utf8(&output.stdout).unwrap(),
        std::str::from_utf8(&output.stderr).unwrap(),
    )
}

#[test]
fn bare_command_is_exactly_five_useful_lines() {
    let output = Command::new(binary()).output().unwrap();
    assert!(output.status.success());
    let (stdout, stderr) = utf8(&output);
    assert!(stderr.is_empty());
    assert_eq!(
        stdout,
        format!(
            "          __====-_  _-====__\n    _--^^^#####//      \\\\#####^^^--_\n  _-^##########// (    ) \\\\##########^-_  AZDAJA v{}\nUsage: azdaja <start|load|exec|final|list|kill|solo|install|doctor|uninstall> [options]\nExample: azdaja solo \"summarize this file\" -f ./document.txt\n",
            env!("CARGO_PKG_VERSION")
        )
    );
    assert_eq!(stdout.lines().count(), 5);
}

#[test]
fn doctor_prints_one_pass_or_fail_per_check_and_every_fail_has_a_fix() {
    let scratch = Scratch::new("doctor");
    let oracle = scratch.0.join("oracle.sh");
    fs::write(&oracle, "#!/bin/sh\ncat >/dev/null\nprintf 'AZDAJA\\n'\n").unwrap();
    fs::set_permissions(&oracle, fs::Permissions::from_mode(0o755)).unwrap();
    let good_config = config(&scratch.0, oracle.to_str().unwrap());
    let good = command(&scratch.0)
        .env("AZDAJA_CONFIG", &good_config)
        .arg("doctor")
        .output()
        .unwrap();
    assert!(good.status.success());
    let (stdout, stderr) = utf8(&good);
    assert!(stderr.is_empty());
    let lines: Vec<_> = stdout.lines().collect();
    assert_eq!(lines.len(), 3, "{stdout}");
    assert!(lines.iter().all(|line| line.starts_with("PASS ")));
    assert!(lines[0].starts_with("PASS config:"));
    assert!(lines[1].starts_with("PASS evaluator:"));
    assert!(lines[2].starts_with("PASS harness:"));

    fs::write(&oracle, "#!/bin/sh\ncat >/dev/null\nprintf 'WRONG\\n'\n").unwrap();
    let bad = command(&scratch.0)
        .env("AZDAJA_CONFIG", &good_config)
        .arg("doctor")
        .output()
        .unwrap();
    assert_eq!(bad.status.code(), Some(1));
    let (stdout, stderr) = utf8(&bad);
    assert!(stderr.is_empty());
    let lines: Vec<_> = stdout.lines().collect();
    assert_eq!(lines.len(), 3, "{stdout}");
    assert_eq!(
        lines
            .iter()
            .filter(|line| line.starts_with("FAIL "))
            .count(),
        1
    );
    assert!(lines[2].starts_with("FAIL harness:") && lines[2].contains("; Fix: "));

    let invalid = scratch.0.join("invalid.toml");
    fs::write(&invalid, "not valid toml = [").unwrap();
    let bad = command(&scratch.0)
        .env("AZDAJA_CONFIG", invalid)
        .arg("doctor")
        .output()
        .unwrap();
    assert_eq!(bad.status.code(), Some(1));
    let (stdout, stderr) = utf8(&bad);
    assert!(stderr.is_empty());
    let lines: Vec<_> = stdout.lines().collect();
    assert_eq!(lines.len(), 3, "{stdout}");
    assert!(lines.iter().all(|line| line.starts_with("FAIL ")));
    assert!(lines.iter().all(|line| line.contains("; Fix: ")));
}

#[test]
fn install_is_three_human_lines_and_detects_directories_and_clis() {
    let scratch = Scratch::new("install");
    fs::create_dir_all(scratch.0.join(".claude")).unwrap();
    let tools = scratch.0.join("tools");
    fs::create_dir(&tools).unwrap();
    let gemini = tools.join("gemini");
    fs::write(&gemini, "#!/bin/sh\nexit 99\n").unwrap();
    fs::set_permissions(&gemini, fs::Permissions::from_mode(0o755)).unwrap();
    let cfg = config(&scratch.0, "cat");
    let output = command(&scratch.0)
        .env("AZDAJA_CONFIG", cfg)
        .env("PATH", format!("{}:/usr/bin:/bin", tools.display()))
        .arg("install")
        .output()
        .unwrap();
    assert!(output.status.success(), "{}", utf8(&output).1);
    let (stdout, stderr) = utf8(&output);
    assert!(stderr.is_empty());
    let lines: Vec<_> = stdout.lines().collect();
    assert_eq!(lines.len(), 3, "{stdout}");
    assert!(lines[0].starts_with("Detected: "));
    assert!(lines[0].contains("claude (directory)"));
    assert!(lines[0].contains("gemini (CLI)"));
    assert!(lines[1].starts_with("Written: "));
    assert!(lines[1].contains(".claude/skills/azdaja"));
    assert!(lines[1].contains(".gemini/skills/azdaja"));
    assert!(lines[2].starts_with("Next: run ") && lines[2].ends_with(" doctor"));
    assert!(
        !stdout
            .split_whitespace()
            .any(|word| { word.len() == 64 && word.bytes().all(|byte| byte.is_ascii_hexdigit()) })
    );
}

#[test]
fn no_harness_refuses_cleanly_before_writing_anything() {
    let scratch = Scratch::new("no-harness");
    let output = command(&scratch.0)
        .env("PATH", "/usr/bin:/bin")
        .arg("install")
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    let (stdout, stderr) = utf8(&output);
    assert!(stdout.is_empty());
    assert!(stderr.contains("no supported harness found"));
    assert!(!stderr.contains("stack backtrace"));
    assert!(fs::read_dir(&scratch.0).unwrap().next().is_none());
}
