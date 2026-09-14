use std::{
    fs,
    io::Write,
    path::Path,
    process::{Command, Stdio},
};

fn collect_strings(value: &serde_json::Value, out: &mut Vec<String>) {
    match value {
        serde_json::Value::String(s) if s.contains("claude-hook") => out.push(s.clone()),
        serde_json::Value::Array(a) => a.iter().for_each(|v| collect_strings(v, out)),
        serde_json::Value::Object(o) => o.values().for_each(|v| collect_strings(v, out)),
        _ => {}
    }
}

#[test]
fn installed_claude_hooks_execute_actual_registered_commands() {
    let root = std::env::temp_dir().join(format!("azdaja-claude-profile-{}", std::process::id()));
    let home = root.join("home with spaces");
    fs::create_dir_all(&home).unwrap();
    let state = root.join("state");
    let install = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args(["install", "claude"])
        .env("HOME", &home)
        .env("AZDAJA_HOME", &state)
        .output()
        .unwrap();
    assert!(
        install.status.success(),
        "{}",
        String::from_utf8_lossy(&install.stderr)
    );
    let profile = home.join(".claude/skills/azdaja");
    let hooks: serde_json::Value =
        serde_json::from_slice(&fs::read(profile.join("hooks/hooks.json")).unwrap()).unwrap();
    let mut commands = Vec::new();
    collect_strings(&hooks, &mut commands);
    assert!(!commands.is_empty());
    let event =
        br#"{"session_id":"profile","hook_event_name":"SessionEnd","cwd":".","tool_input":{}}"#;
    for command in commands {
        let mut child = Command::new("sh")
            .arg("-c")
            .arg(command)
            .env("CLAUDE_PLUGIN_ROOT", &profile)
            .env("HOME", &home)
            .env("AZDAJA_HOME", &state)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap();
        child.stdin.take().unwrap().write_all(event).unwrap();
        let output = child.wait_with_output().unwrap();
        assert!(
            output.status.success(),
            "registered hook failed: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
    fs::remove_dir_all(root).unwrap();
}
