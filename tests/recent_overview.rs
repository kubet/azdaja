#![cfg(unix)]

use regex::Regex;
use std::{
    fs,
    io::Write,
    os::unix::fs::PermissionsExt,
    path::{Path, PathBuf},
    process::{Command, Output, Stdio},
    thread,
    time::{Duration, SystemTime, UNIX_EPOCH},
};

struct Scratch(PathBuf);
impl Scratch {
    fn new(label: &str) -> Self {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path = std::env::temp_dir().join(format!(
            "azdaja-recent-overview-{label}-{}-{nonce}",
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

fn command(home: &Path, cwd: &Path) -> Command {
    let mut command = Command::new(binary());
    command
        .current_dir(cwd)
        .env("HOME", home)
        .env("XDG_CONFIG_HOME", home.join("xdg"))
        .env("AZDAJA_HOME", home.join("state"))
        .env_remove("RLM_DEPTH");
    let config = home.join("config.toml");
    if config.exists() {
        command.env("AZDAJA_CONFIG", config);
    } else {
        command.env_remove("AZDAJA_CONFIG");
    }
    command
}

fn run(home: &Path, cwd: &Path, args: &[&str], input: &str) -> Output {
    let mut command = command(home, cwd);
    command
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(input.as_bytes())
        .unwrap();
    child.wait_with_output().unwrap()
}

fn assert_success(output: Output) -> String {
    assert!(
        output.status.success(),
        "status={} stdout={} stderr={}",
        output.status,
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).unwrap()
}

fn add_memory(home: &Path, project: &Path, text: &str) {
    assert_success(run(home, project, &["memory", "add", "decision", text], ""));
}

fn add_source_summary(home: &Path, project: &Path) {
    let provider = home.join("mock-provider.sh");
    fs::write(
        &provider,
        "#!/bin/sh\ncat >/dev/null\nprintf '%s\\n' \"\\`\\`\\`python\" \"FINAL({'result': 'deterministic'})\" \"\\`\\`\\`\"\n",
    )
    .unwrap();
    fs::set_permissions(&provider, fs::Permissions::from_mode(0o700)).unwrap();
    fs::write(
        home.join("config.toml"),
        format!(
            r#"sub_llm_cmd = {:?}
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
"#,
            provider.to_string_lossy()
        ),
    )
    .unwrap();
    let source = project.join("source.txt");
    fs::write(&source, "deterministic source\n").unwrap();
    assert_success(run(
        home,
        project,
        &[
            "solo",
            "summarize the deterministic source",
            "-f",
            source.to_str().unwrap(),
        ],
        "",
    ));
}

#[cfg(target_os = "macos")]
fn run_bare_pty(home: &Path, cwd: &Path) -> Output {
    Command::new("script")
        .args([
            "-q",
            "/dev/null",
            "/bin/sh",
            "-c",
            "stty cols 160 rows 40; exec \"$@\"",
            "sh",
            binary(),
        ])
        .current_dir(cwd)
        .env("HOME", home)
        .env("XDG_CONFIG_HOME", home.join("xdg"))
        .env("AZDAJA_HOME", home.join("state"))
        .env_remove("AZDAJA_CONFIG")
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap()
}

#[cfg(not(target_os = "macos"))]
fn run_bare_pty(home: &Path, cwd: &Path) -> Output {
    let quoted = format!(
        "stty cols 160 rows 40; exec {}",
        shlex::try_quote(binary()).unwrap()
    );
    Command::new("script")
        .args(["-q", "-e", "-c", &quoted, "/dev/null"])
        .current_dir(cwd)
        .env("HOME", home)
        .env("XDG_CONFIG_HOME", home.join("xdg"))
        .env("AZDAJA_HOME", home.join("state"))
        .env_remove("AZDAJA_CONFIG")
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap()
}

fn pty_text(output: Output) -> String {
    assert!(
        output.status.success(),
        "status={} stdout={} stderr={}",
        output.status,
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(strip_ansi_escapes::strip(output.stdout))
        .unwrap()
        .replace('\r', "")
}

fn recent_rows(text: &str) -> Vec<(String, usize, usize)> {
    let row = Regex::new(
        r"(?m)([0-9a-f]{8}) · ([0-9]+) memor(?:y|ies) · ([0-9]+) source summar(?:y|ies) · [^\n│]+",
    )
    .unwrap();
    row.captures_iter(text)
        .map(|capture| {
            (
                capture[1].to_owned(),
                capture[2].parse().unwrap(),
                capture[3].parse().unwrap(),
            )
        })
        .collect()
}

fn state_snapshot(root: &Path) -> Vec<(PathBuf, bool, u128, Vec<u8>)> {
    fn visit(root: &Path, path: &Path, entries: &mut Vec<(PathBuf, bool, u128, Vec<u8>)>) {
        let metadata = fs::symlink_metadata(path).unwrap();
        let modified = metadata
            .modified()
            .unwrap()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let relative = path.strip_prefix(root).unwrap().to_owned();
        if metadata.is_dir() {
            entries.push((relative, true, modified, Vec::new()));
            let mut children: Vec<_> = fs::read_dir(path)
                .unwrap()
                .map(|entry| entry.unwrap().path())
                .collect();
            children.sort();
            for child in children {
                visit(root, &child, entries);
            }
        } else {
            entries.push((relative, false, modified, fs::read(path).unwrap()));
        }
    }

    let mut entries = Vec::new();
    visit(root, root, &mut entries);
    entries
}

#[test]
fn bare_tty_shows_private_bounded_recent_projects_in_recency_order() {
    let scratch = Scratch::new("tty");
    let home = scratch.0.join("home");
    fs::create_dir(&home).unwrap();
    let projects: Vec<PathBuf> = (0..5)
        .map(|index| {
            let path = scratch.0.join(format!("private-project-{index}"));
            fs::create_dir(&path).unwrap();
            fs::canonicalize(path).unwrap()
        })
        .collect();

    for (index, project) in projects.iter().enumerate() {
        add_memory(&home, project, &format!("memory-only scope {index}"));
    }
    add_source_summary(&home, &projects[3]);

    let first = pty_text(run_bare_pty(&home, &projects[4]));
    let first_rows = recent_rows(&first);
    assert_eq!(first_rows.len(), 3, "{first}");
    assert!(first.contains("scope"), "{first}");
    assert!(
        first.contains("projects") || first.contains("project"),
        "{first}"
    );
    assert!(
        first_rows
            .iter()
            .any(|(_, memories, summaries)| *memories == 1 && *summaries == 1),
        "{first}"
    );
    assert!(
        first_rows
            .iter()
            .any(|(_, memories, summaries)| *memories == 1 && *summaries == 0),
        "{first}"
    );

    let stable = pty_text(run_bare_pty(&home, &projects[4]));
    assert_eq!(
        recent_rows(&stable),
        first_rows,
        "overview must not touch recency"
    );

    add_memory(
        &home,
        &projects[4],
        "current scope changes stay in current detail",
    );
    let current_changed = pty_text(run_bare_pty(&home, &projects[4]));
    assert_eq!(
        recent_rows(&current_changed),
        first_rows,
        "the current project must be excluded from recent projects"
    );

    thread::sleep(Duration::from_millis(1_100));
    add_memory(&home, &projects[0], "make the oldest other scope newest");
    let reordered = pty_text(run_bare_pty(&home, &projects[4]));
    let reordered_rows = recent_rows(&reordered);
    assert_eq!(reordered_rows.len(), 3, "{reordered}");
    assert_eq!(reordered_rows[0].1, 2, "{reordered}");

    assert!(
        !reordered.contains(home.to_string_lossy().as_ref()),
        "leaked isolated home: {reordered}"
    );
    for path in projects.iter().take(4) {
        let absolute = path.to_string_lossy();
        assert!(
            !reordered.contains(absolute.as_ref()),
            "leaked {absolute}: {reordered}"
        );
        if let Some(name) = path.file_name().and_then(|name| name.to_str()) {
            assert!(!reordered.contains(name), "leaked {name}: {reordered}");
        }
    }
    assert!(
        reordered.contains(projects[4].file_name().unwrap().to_str().unwrap()),
        "current-folder detail disappeared: {reordered}"
    );
}

#[test]
fn non_tty_and_explicit_commands_remain_help_or_command_output_without_state() {
    let scratch = Scratch::new("non-tty");
    let home = scratch.0.join("home");
    let project = scratch.0.join("project");
    fs::create_dir(&home).unwrap();
    fs::create_dir(&project).unwrap();
    let state = home.join("state");
    let row =
        Regex::new(r"[0-9a-f]{8} · [0-9]+ memor(?:y|ies) · [0-9]+ source summar(?:y|ies)").unwrap();

    let bare = run(&home, &project, &[], "");
    assert!(bare.status.success());
    let bare = String::from_utf8(bare.stdout).unwrap();
    assert!(bare.contains("Usage: az <command>"), "{bare}");
    assert!(!bare.contains("projects"), "{bare}");
    assert!(!row.is_match(&bare), "{bare}");
    assert!(!state.exists(), "bare non-TTY created state");

    add_memory(&home, &project, "explicit-command state sentinel");
    let commands: [&[&str]; 6] = [
        &["list"],
        &["list", "--global"],
        &["map"],
        &["map", "--global"],
        &["--help"],
        &["--version"],
    ];
    for args in commands {
        let _ = run(&home, &project, args, "");
    }
    let before = state_snapshot(&state);
    for args in commands {
        let output = run(&home, &project, args, "");
        let combined = format!(
            "{}{}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        assert!(!combined.contains("projects"), "args={args:?}: {combined}");
        assert!(!row.is_match(&combined), "args={args:?}: {combined}");
        assert_eq!(
            state_snapshot(&state),
            before,
            "args={args:?} touched existing state"
        );
    }
}
