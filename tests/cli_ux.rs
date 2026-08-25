#![cfg(unix)]

use std::{
    fs,
    io::Write,
    os::unix::fs::PermissionsExt,
    path::{Path, PathBuf},
    process::{Command, Output, Stdio},
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
fn non_tty_bare_command_is_exactly_five_line_help_without_sprite() {
    let output = Command::new(binary()).output().unwrap();
    assert!(output.status.success());
    let (stdout, stderr) = utf8(&output);
    assert!(stderr.is_empty());
    assert_eq!(
        stdout,
        format!(
            "AZDAJA v{} — virtual memory for language models\nUsage: az <command>\nCommands: help solo map install doctor start load exec final list kill uninstall memory\nInstall: az install  (auto-detects supported tools)\nExample: az solo \"summarize this file\" -f ./document.txt\n",
            env!("CARGO_PKG_VERSION")
        )
    );
    assert_eq!(stdout.lines().count(), 5);
    assert!(!stdout.contains('\u{1b}'));
    assert!(!stdout.contains('▀'));
    assert!(!stdout.contains('▄'));
}

#[test]
fn help_alias_is_concise_and_command_help_uses_plain_targets() {
    let bare = Command::new(binary()).output().unwrap();
    let help = Command::new(binary()).arg("help").output().unwrap();
    let long = Command::new(binary()).arg("--help").output().unwrap();
    assert!(help.status.success() && long.status.success());
    assert_eq!(help.stdout, bare.stdout);
    assert_eq!(long.stdout, bare.stdout);
    assert!(help.stderr.is_empty() && long.stderr.is_empty());

    let help_help = Command::new(binary())
        .args(["help", "help"])
        .output()
        .unwrap();
    let (stdout, stderr) = utf8(&help_help);
    assert!(help_help.status.success());
    assert_eq!(stdout, "Usage: az help [command]\n");
    assert!(stderr.is_empty());

    let install = Command::new(binary())
        .args(["help", "install"])
        .output()
        .unwrap();
    let (stdout, stderr) = utf8(&install);
    assert!(install.status.success());
    assert!(stderr.is_empty());
    assert!(stdout.starts_with("Usage: az install [TARGET[,TARGET...]|all]\n"));
    assert!(stdout.contains("az install\n"));
    assert!(stdout.contains("az install jcode\n"));
    assert!(!stdout.contains("--harness"));

    let unknown = Command::new(binary())
        .args(["help", "spaceship"])
        .output()
        .unwrap();
    let (stdout, stderr) = utf8(&unknown);
    assert_eq!(unknown.status.code(), Some(2));
    assert!(stdout.is_empty());
    assert_eq!(
        stderr,
        "error: unknown command 'spaceship' (run 'az help')\n"
    );

    let memory_help = Command::new(binary())
        .args(["help", "memory"])
        .output()
        .unwrap();
    assert!(memory_help.status.success());
    let memory_help = String::from_utf8(memory_help.stdout).unwrap();
    assert!(memory_help.contains("Usage: az memory <add|list|show>"));
    assert!(memory_help.contains("explicit, local-first, bounded"));
}

#[test]
fn memory_cli_is_scope_first_linked_and_global_only_when_explicit() {
    let scratch = Scratch::new("memory-ledger");
    let first = scratch.0.join("first");
    let second = scratch.0.join("second");
    fs::create_dir_all(&first).unwrap();
    fs::create_dir_all(&second).unwrap();

    let add = |cwd: &Path, args: &[&str]| {
        let output = command(&scratch.0)
            .current_dir(cwd)
            .args(args)
            .output()
            .unwrap();
        assert!(
            output.status.success(),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        String::from_utf8(output.stdout).unwrap()
    };

    let first_record = add(
        &first,
        &[
            "memory",
            "add",
            "decision",
            "keep the evaluator core unchanged",
            "--tag",
            "architecture",
        ],
    );
    let id = first_record
        .split_whitespace()
        .find(|part| part.starts_with('m'))
        .unwrap()
        .to_owned();
    assert_eq!(id.len(), 17);

    let linked = add(
        &first,
        &[
            "memory",
            "add",
            "disagreement",
            "retain the minority view for later review",
            "--link",
            &format!("supports:{id}"),
        ],
    );
    assert!(linked.contains("disagreement"));

    let listed = add(&first, &["memory", "list"]);
    assert!(listed.contains("memory scope  current folder"));
    assert!(listed.contains("decision"));
    assert!(listed.contains("disagreement"));
    assert!(listed.contains(&id));
    assert!(!listed.contains(first.to_string_lossy().as_ref()));

    let shown = add(&first, &["memory", "show", &id]);
    assert!(shown.contains("provenance manual"));
    assert!(shown.contains("backlink"));
    assert!(shown.contains("supports"));

    let isolated = add(&second, &["memory", "list"]);
    assert!(isolated.contains("current folder · 0 records"));
    assert!(!isolated.contains(&id));

    let global = add(
        &first,
        &[
            "memory",
            "add",
            "observation",
            "global is an explicit escape hatch",
            "--global",
        ],
    );
    assert!(global.contains("global"));
    let global_list = add(&second, &["memory", "list", "--global"]);
    assert!(global_list.contains("global · 1 records"));
    assert!(global_list.contains("explicit escape hatch"));
}

#[test]
fn map_keeps_a_private_numeric_source_summary_after_the_session_is_killed() {
    let scratch = Scratch::new("memory-map");
    let cfg = config(&scratch.0, "cat");
    let source = scratch.0.join("private source.txt");
    let secret = "private constellation source\nalpha beta gamma\n\n";
    fs::write(&source, secret).unwrap();

    let started = command(&scratch.0)
        .env("AZDAJA_CONFIG", &cfg)
        .arg("start")
        .output()
        .unwrap();
    assert!(started.status.success());
    let session = std::str::from_utf8(&started.stdout).unwrap().trim();

    let loaded = command(&scratch.0)
        .env("AZDAJA_CONFIG", &cfg)
        .args(["load", session, source.to_str().unwrap(), "source"])
        .output()
        .unwrap();
    assert!(
        loaded.status.success(),
        "{}",
        String::from_utf8_lossy(&loaded.stderr)
    );

    let live_map = command(&scratch.0)
        .env("AZDAJA_CONFIG", &cfg)
        .env("NO_COLOR", "1")
        .arg("map")
        .output()
        .unwrap();
    assert!(live_map.status.success());
    let live_map = String::from_utf8(live_map.stdout).unwrap();
    assert!(live_map.contains("1 source summary"));
    assert!(live_map.contains("numbers only"));
    assert!(!live_map.contains("session memory"));

    let mut executed = command(&scratch.0)
        .env("AZDAJA_CONFIG", &cfg)
        .args(["exec", session])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    executed
        .stdin
        .as_mut()
        .unwrap()
        .write_all(b"FINAL(\"done\")\n")
        .unwrap();
    let executed = executed.wait_with_output().unwrap();
    assert!(
        executed.status.success(),
        "{}",
        String::from_utf8_lossy(&executed.stderr)
    );

    let killed = command(&scratch.0)
        .env("AZDAJA_CONFIG", &cfg)
        .args(["kill", session])
        .output()
        .unwrap();
    assert!(killed.status.success());

    let mapped = command(&scratch.0)
        .env("AZDAJA_CONFIG", &cfg)
        .env("NO_COLOR", "1")
        .arg("map")
        .output()
        .unwrap();
    assert!(mapped.status.success());
    let (stdout, stderr) = utf8(&mapped);
    assert!(stderr.is_empty());
    assert!(stdout.starts_with("╭─ azdaja · memory constellation"));
    assert!(stdout.contains("live     none · 4 slots free"));
    assert!(stdout.contains("memory   1 source summary"));
    assert!(stdout.contains("numbers only"));
    assert!(stdout.contains("pattern  repeated ←"));
    assert!(stdout.contains("→ varied · avg variety"));
    assert!(stdout.contains("recent   finished"));
    for rejected in [
        "resident",
        "cold",
        "trace",
        "H→",
        "texture",
        "H₀",
        "redundancy",
        "session memory",
    ] {
        assert!(
            !stdout.contains(rejected),
            "unexpected {rejected:?}: {stdout}"
        );
    }
    assert!(!stdout.contains(secret));
    assert!(!stdout.contains("private constellation source"));
    assert!(!stdout.contains('\u{1b}'));
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
    assert!(lines[2].starts_with("PASS model:"));

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
    assert!(lines[2].starts_with("FAIL model:") && lines[2].contains("; Fix: "));

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
fn doctor_config_failures_name_adjacent_and_xdg_paths_before_provider_work() {
    let scratch = Scratch::new("doctor-config-paths");
    let adjacent_dir = scratch.0.join("adjacent bin");
    fs::create_dir_all(&adjacent_dir).unwrap();
    let adjacent_binary = adjacent_dir.join("azdaja");
    fs::copy(binary(), &adjacent_binary).unwrap();
    fs::set_permissions(&adjacent_binary, fs::Permissions::from_mode(0o755)).unwrap();
    let adjacent_config = adjacent_dir.join("azdaja-config.toml");
    fs::write(&adjacent_config, "not valid toml = [").unwrap();

    let adjacent = Command::new(&adjacent_binary)
        .arg("doctor")
        .env("HOME", &scratch.0)
        .env("AZDAJA_HOME", scratch.0.join("adjacent-state"))
        .env_remove("AZDAJA_CONFIG")
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap();
    assert_eq!(adjacent.status.code(), Some(1));
    let (stdout, stderr) = utf8(&adjacent);
    assert!(stderr.is_empty());
    assert!(
        stdout
            .lines()
            .next()
            .unwrap()
            .starts_with(&format!("FAIL config: {}:", adjacent_config.display())),
        "{stdout}"
    );

    fs::remove_file(&adjacent_config).unwrap();
    let xdg_home = scratch.0.join("xdg");
    let xdg_config = xdg_home.join("azdaja/config.toml");
    fs::create_dir_all(xdg_config.parent().unwrap()).unwrap();
    fs::write(&xdg_config, "not valid toml = [").unwrap();
    let xdg = command(&scratch.0)
        .env("XDG_CONFIG_HOME", &xdg_home)
        .env_remove("AZDAJA_CONFIG")
        .arg("doctor")
        .output()
        .unwrap();
    assert_eq!(xdg.status.code(), Some(1));
    let (stdout, stderr) = utf8(&xdg);
    assert!(stderr.is_empty());
    assert!(
        stdout
            .lines()
            .next()
            .unwrap()
            .starts_with(&format!("FAIL config: {}:", xdg_config.display())),
        "{stdout}"
    );
}

#[test]
fn install_is_three_human_lines_and_detects_only_tool_executables() {
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
    assert!(!lines[0].contains("claude"));
    assert!(lines[0].contains("gemini (CLI)"));
    assert!(lines[1].starts_with("Written: "));
    assert!(!lines[1].contains(".claude/skills/azdaja"));
    assert!(lines[1].contains(".gemini/skills/azdaja"));
    assert!(lines[2].starts_with("Next: run "));
    assert!(lines[2].contains("/.gemini/skills/azdaja/azdaja' doctor; then "));
    assert!(lines[2].contains("restart Gemini to reload its skills"));
    assert!(
        !stdout
            .split_whitespace()
            .any(|word| { word.len() == 64 && word.bytes().all(|byte| byte.is_ascii_hexdigit()) })
    );
}

#[test]
fn no_supported_tool_refuses_cleanly_before_writing_anything() {
    let scratch = Scratch::new("no-supported-tool");
    for directory in [
        ".jcode",
        ".claude",
        ".agents/skills",
        ".gemini",
        ".config/opencode",
    ] {
        fs::create_dir_all(scratch.0.join(directory)).unwrap();
    }
    let output = command(&scratch.0)
        .env("PATH", "/usr/bin:/bin")
        .arg("install")
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    let (stdout, stderr) = utf8(&output);
    assert!(stdout.is_empty());
    assert!(stderr.contains("no supported tool executable found"));
    assert!(!stderr.contains("stack backtrace"));
    for target in [
        ".jcode/skills/azdaja",
        ".claude/skills/azdaja",
        ".agents/skills/azdaja",
        ".gemini/skills/azdaja",
        ".config/opencode/skills/azdaja",
    ] {
        assert!(!scratch.0.join(target).exists());
    }

    for directory in [".jcode", ".claude", ".agents", ".gemini", ".config"] {
        fs::remove_dir_all(scratch.0.join(directory)).unwrap();
    }

    let output = command(&scratch.0)
        .env("PATH", "/usr/bin:/bin")
        .arg("uninstall")
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    let (stdout, stderr) = utf8(&output);
    assert!(stdout.is_empty());
    assert!(stderr.contains("no managed tool integration detected"));
    assert!(stderr.contains("az uninstall jcode"));
    assert!(!stderr.contains("az install"));
    for target in [
        ".jcode/skills/azdaja",
        ".claude/skills/azdaja",
        ".agents/skills/azdaja",
        ".gemini/skills/azdaja",
        ".config/opencode/skills/azdaja",
    ] {
        assert!(!scratch.0.join(target).exists());
    }
}
