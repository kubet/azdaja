use std::{
    fs,
    io::Write,
    path::{Path, PathBuf},
    process::{Command, Stdio},
    time::{SystemTime, UNIX_EPOCH},
};

fn temp(name: &str) -> PathBuf {
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let path = std::env::temp_dir().join(format!("azdaja-{name}-{}-{stamp}", std::process::id()));
    fs::create_dir_all(&path).unwrap();
    path
}

fn hook(home: &Path, activation: Option<&str>, event: serde_json::Value) -> std::process::Output {
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args(["claude-hook"])
        .env("HOME", home.join("home"))
        .env("AZDAJA_HOME", home.join("state"))
        .env_remove("AZDAJA_CONFIG")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    if let Some(value) = activation {
        command.env("AZDAJA_CLAUDE_ACTIVATION", value);
    } else {
        command.env_remove("AZDAJA_CLAUDE_ACTIVATION");
    }
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(event.to_string().as_bytes())
        .unwrap();
    child.wait_with_output().unwrap()
}

fn event(
    session: &str,
    name: &str,
    cwd: &Path,
    tool: Option<&str>,
    input: serde_json::Value,
) -> serde_json::Value {
    let mut value = serde_json::json!({
        "session_id": session,
        "hook_event_name": name,
        "cwd": cwd,
    });
    if name == "UserPromptSubmit" {
        if let Some(prompt) = input.get("user_prompt").cloned() {
            value["user_prompt"] = prompt;
        }
        if let Some(prompt) = input.get("prompt").cloned() {
            value["prompt"] = prompt;
        }
        value["tool_input"] = serde_json::json!({});
    } else {
        value["tool_input"] = input;
    }
    if let Some(tool) = tool {
        value["tool_name"] = serde_json::json!(tool);
    }
    value
}

fn assert_denied(output: std::process::Output) {
    assert!(
        output.status.success(),
        "status={:?}, stderr={:?}",
        output.status,
        output.stderr
    );
    let decision: serde_json::Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(decision["hookSpecificOutput"]["permissionDecision"], "deny");
}

fn assert_open(output: std::process::Output) {
    assert!(
        output.status.success(),
        "status={:?}, stderr={:?}",
        output.status,
        output.stderr
    );
    assert!(
        output.stdout.is_empty(),
        "unexpected decision: {:?}",
        output.stdout
    );
}

#[test]
fn claude_hook_default_and_invalid_activation_are_fail_open_and_side_effect_free() {
    let root = temp("claude-nonblocking-default");
    let cwd = root.join("project");
    fs::create_dir_all(&cwd).unwrap();
    fs::write(cwd.join("records.jsonl"), vec![b'x'; 2 * 1024 * 1024]).unwrap();
    for activation in [None, Some("bogus")] {
        let session = format!("session-{activation:?}");
        assert_open(hook(
            &root,
            activation,
            event(
                &session,
                "UserPromptSubmit",
                &cwd,
                None,
                serde_json::json!({
                    "user_prompt": "Classify every record in the full input."
                }),
            ),
        ));
        assert_open(hook(
            &root,
            activation,
            event(
                &session,
                "PreToolUse",
                &cwd,
                Some("Read"),
                serde_json::json!({
                    "file_path": cwd.join("records.jsonl"),
                }),
            ),
        ));
        assert_open(hook(
            &root,
            activation,
            event(
                &session,
                "PostToolUse",
                &cwd,
                Some("Skill"),
                serde_json::json!({"skill":"azdaja"}),
            ),
        ));
    }
    let markers = root.join("state/claude-hook-markers");
    assert!(!markers.exists() || fs::read_dir(markers).unwrap().next().is_none());
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn claude_hook_opt_in_handles_stale_markers_and_releases_failed_transactions() {
    let root = temp("claude-nonblocking-recovery");
    let cwd = root.join("project");
    fs::create_dir_all(&cwd).unwrap();
    let large = cwd.join("records.jsonl");
    fs::write(&large, vec![b'x'; 2 * 1024 * 1024]).unwrap();
    let session = "recovery";
    assert_open(hook(
        &root,
        Some("session"),
        event(
            session,
            "PostToolUse",
            &cwd,
            Some("Skill"),
            serde_json::json!({"skill":"azdaja"}),
        ),
    ));
    let markers = root.join("state/claude-hook-markers");
    let coverage = fs::read_dir(&markers)
        .unwrap()
        .next()
        .unwrap()
        .unwrap()
        .path();
    let marker = b"azdaja-claude-hook-v1\n";
    for suffix in ["active", "transaction", "sample"] {
        let name = coverage.file_stem().unwrap().to_string_lossy();
        fs::write(markers.join(format!("{name}.{suffix}")), marker).unwrap();
    }
    assert_open(hook(
        &root,
        Some("session"),
        event(
            session,
            "UserPromptSubmit",
            &cwd,
            None,
            serde_json::json!({"user_prompt":"ordinary follow-up"}),
        ),
    ));
    assert!(fs::read_dir(&markers).unwrap().next().is_none());

    assert_open(hook(
        &root,
        Some("session"),
        event(
            session,
            "UserPromptSubmit",
            &cwd,
            None,
            serde_json::json!({"user_prompt":"Classify every record in the full input."}),
        ),
    ));
    assert_open(hook(
        &root,
        Some("session"),
        event(
            session,
            "PostToolUse",
            &cwd,
            Some("Skill"),
            serde_json::json!({"skill":"azdaja"}),
        ),
    ));
    let transaction = serde_json::json!({"command":format!("set -euo pipefail\nAZ={}\nsid=\ncleanup() {{\nif [[ -n \"$sid\" ]]; then\n\"$AZ\" kill \"$sid\" >/dev/null 2>&1 || true\nfi\n}}\ntrap cleanup EXIT\nsid=\"$(\"$AZ\" start)\"\n\"$AZ\" load \"$sid\" '{}' source >/dev/null\n\"$AZ\" exec \"$sid\" >/dev/null <<'PY'\nFINAL(1)\nPY\n\"$AZ\" final \"$sid\"", env!("CARGO_BIN_EXE_azdaja"), cwd.join("small.txt").display())});
    assert_open(hook(
        &root,
        Some("session"),
        event(
            session,
            "PreToolUse",
            &cwd,
            Some("Bash"),
            transaction.clone(),
        ),
    ));
    assert_open(hook(
        &root,
        Some("session"),
        event(
            session,
            "PostToolUseFailure",
            &cwd,
            Some("Bash"),
            transaction.clone(),
        ),
    ));
    assert_open(hook(
        &root,
        Some("session"),
        event(session, "PreToolUse", &cwd, Some("Bash"), transaction),
    ));
    assert_open(hook(
        &root,
        Some("session"),
        event(
            session,
            "PostToolUseFailure",
            &cwd,
            Some("Bash"),
            serde_json::json!({"command":"malformed wrapper"}),
        ),
    ));
    assert!(fs::read_dir(&markers).unwrap().next().is_none());
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn claude_hook_active_allows_ordinary_cp_read_grep_and_screenshot_workflow() {
    let root = temp("claude-nonblocking-screenshot");
    let cwd = root.join("project");
    fs::create_dir_all(&cwd).unwrap();
    let small = cwd.join("small.txt");
    fs::write(&small, "small\n").unwrap();
    let large = cwd.join("large.bin");
    fs::write(&large, vec![b'x'; 2 * 1024 * 1024]).unwrap();
    let copied = cwd.join("copied.bin");
    let session = "screenshot";
    assert_open(hook(
        &root,
        Some("request"),
        event(
            session,
            "UserPromptSubmit",
            &cwd,
            None,
            serde_json::json!({"user_prompt":"Classify every record in the full input."}),
        ),
    ));
    assert_open(hook(
        &root,
        Some("request"),
        event(
            session,
            "PostToolUse",
            &cwd,
            Some("Skill"),
            serde_json::json!({"skill":"azdaja"}),
        ),
    ));
    for (tool, input) in [
        (
            "Bash",
            serde_json::json!({"command":format!("cp {} {}", large.display(), copied.display())}),
        ),
        ("Read", serde_json::json!({"file_path":small})),
        ("Grep", serde_json::json!({"path":cwd,"pattern":"small"})),
        ("Agent", serde_json::json!({"description":"inspect"})),
        ("Task", serde_json::json!({"description":"inspect"})),
    ] {
        assert_open(hook(
            &root,
            Some("request"),
            event(session, "PreToolUse", &cwd, Some(tool), input),
        ));
    }
    let missing = cwd.join("absent.txt");
    let failed_copy = cwd.join("failed.bin");
    let missing_command = serde_json::json!({
        "command": format!("cp {} {}", missing.display(), failed_copy.display())
    });
    assert_open(hook(
        &root,
        Some("request"),
        event(
            session,
            "PreToolUse",
            &cwd,
            Some("Bash"),
            missing_command.clone(),
        ),
    ));
    assert_open(hook(
        &root,
        Some("request"),
        event(
            session,
            "PostToolUseFailure",
            &cwd,
            Some("Bash"),
            missing_command,
        ),
    ));
    assert_open(hook(
        &root,
        Some("request"),
        event(
            session,
            "PreToolUse",
            &cwd,
            Some("Read"),
            serde_json::json!({"file_path": small}),
        ),
    ));
    assert_open(hook(
        &root,
        Some("request"),
        event(
            session,
            "UserPromptSubmit",
            &cwd,
            None,
            serde_json::json!({"user_prompt":"Classify every record in the full input."}),
        ),
    ));
    assert_open(hook(
        &root,
        Some("request"),
        event(
            session,
            "PostToolUse",
            &cwd,
            Some("Skill"),
            serde_json::json!({"skill":"azdaja"}),
        ),
    ));
    for destination in [
        "/dev/stdout",
        "/dev/fd/1",
        "/proc/self/fd/1",
        "-",
        "alias.bin",
    ] {
        if destination == "alias.bin" {
            std::os::unix::fs::symlink(&large, cwd.join(destination)).unwrap();
        }
        let output = hook(
            &root,
            Some("request"),
            event(
                session,
                "PreToolUse",
                &cwd,
                Some("Bash"),
                serde_json::json!({"command":format!("cp {} {}", large.display(), destination)}),
            ),
        );
        assert_denied(output);
    }
    fs::remove_dir_all(root).unwrap();
}
