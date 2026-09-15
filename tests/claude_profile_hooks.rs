#![cfg(unix)]

use serde_json::{Value, json};
use std::{
    collections::BTreeMap,
    fs,
    io::Write,
    path::{Path, PathBuf},
    process::{Command, Stdio},
    time::{SystemTime, UNIX_EPOCH},
};

struct Profile {
    root: PathBuf,
    home: PathBuf,
    state: PathBuf,
    plugin: PathBuf,
    commands: BTreeMap<String, String>,
}
impl Profile {
    fn new() -> Self {
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let root = std::env::temp_dir().join(format!(
            "azdaja-claude-profile-{}-{stamp}",
            std::process::id()
        ));
        let home = root.join("home with spaces");
        let state = root.join("state");
        fs::create_dir_all(&home).unwrap();
        let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .args(["install", "claude"])
            .env("HOME", &home)
            .env("AZDAJA_HOME", &state)
            .env_remove("AZDAJA_CONFIG")
            .env_remove("AZDAJA_CLAUDE_ACTIVATION")
            .output()
            .unwrap();
        assert!(
            output.status.success(),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        let plugin = home.join(".claude/skills/azdaja");
        let hooks: Value =
            serde_json::from_slice(&fs::read(plugin.join("hooks/hooks.json")).unwrap()).unwrap();
        let mut commands = BTreeMap::new();
        for (name, groups) in hooks["hooks"].as_object().unwrap() {
            let entries: Vec<_> = groups
                .as_array()
                .unwrap()
                .iter()
                .flat_map(|g| g["hooks"].as_array().unwrap())
                .collect();
            assert_eq!(entries.len(), 1);
            assert!(
                entries[0].get("args").is_none(),
                "Claude executes the command string, not an args array"
            );
            let command = entries[0]["command"].as_str().unwrap();
            assert_eq!(command, "\"${CLAUDE_PLUGIN_ROOT}/azdaja\" claude-hook");
            commands.insert(name.clone(), command.to_owned());
        }
        assert_eq!(commands.len(), 5);
        fs::write(root.join("large.jsonl"), vec![b'x'; 2 * 1024 * 1024]).unwrap();
        fs::write(root.join("small.ts"), "export const value = 1;\n").unwrap();
        Self {
            root,
            home,
            state,
            plugin,
            commands,
        }
    }
    fn event(&self, name: &str, tool: &str, input: Value, activation: Option<&str>, deny: bool) {
        let mut value = json!({"session_id":"profile", "hook_event_name":name, "cwd":self.root,
            "tool_name":tool, "tool_input":input});
        if name == "UserPromptSubmit" {
            value["prompt"] = value["tool_input"]["prompt"].clone();
        }
        let mut command = Command::new("sh");
        command
            .args(["-c", &self.commands[name]])
            .current_dir(&self.root)
            .env("CLAUDE_PLUGIN_ROOT", &self.plugin)
            .env("HOME", &self.home)
            .env("AZDAJA_HOME", &self.state)
            .env_remove("AZDAJA_CONFIG")
            .env_remove("AZDAJA_CLAUDE_ACTIVATION")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        if let Some(activation) = activation {
            command.env("AZDAJA_CLAUDE_ACTIVATION", activation);
        }
        let mut child = command.spawn().unwrap();
        child
            .stdin
            .take()
            .unwrap()
            .write_all(value.to_string().as_bytes())
            .unwrap();
        let output = child.wait_with_output().unwrap();
        assert!(
            output.status.success(),
            "{value}: {}",
            String::from_utf8_lossy(&output.stderr)
        );
        assert!(output.stderr.is_empty(), "{value}: {:?}", output.stderr);
        if deny {
            let response: Value = serde_json::from_slice(&output.stdout).unwrap();
            assert_eq!(response["hookSpecificOutput"]["permissionDecision"], "deny");
        } else {
            assert!(
                output.stdout.is_empty(),
                "{value}: {}",
                String::from_utf8_lossy(&output.stdout)
            );
        }
    }
    fn markers(&self) -> BTreeMap<String, Vec<u8>> {
        let directory = self.state.join("claude-hook-markers");
        if !directory.exists() {
            return BTreeMap::new();
        }
        fs::read_dir(directory)
            .unwrap()
            .map(|entry| {
                let path = entry.unwrap().path();
                (
                    path.file_name().unwrap().to_string_lossy().into_owned(),
                    fs::read(path).unwrap(),
                )
            })
            .collect()
    }
}
impl Drop for Profile {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.root);
    }
}

#[test]
fn installed_claude_hooks_execute_actual_commands_and_recover_without_tool_monopoly() {
    let profile = Profile::new();
    let semantic = json!({"prompt":"Classify every record in large.jsonl."});
    // Positive control first: prove the installed hook really routes, not just exits zero.
    profile.event(
        "UserPromptSubmit",
        "",
        semantic.clone(),
        Some("session"),
        false,
    );
    profile.event(
        "PostToolUse",
        "Skill",
        json!({"skill":"azdaja"}),
        Some("session"),
        false,
    );
    profile.event(
        "PreToolUse",
        "Read",
        json!({"file_path":profile.root.join("large.jsonl")}),
        Some("session"),
        true,
    );
    assert_eq!(profile.markers().len(), 2);
    let stale = profile.markers();
    for activation in [None, Some("invalid"), Some("")] {
        profile.event("UserPromptSubmit", "", semantic.clone(), activation, false);
        profile.event(
            "PostToolUse",
            "Skill",
            json!({"skill":"azdaja"}),
            activation,
            false,
        );
        profile.event(
            "PreToolUse",
            "Read",
            json!({"file_path":profile.root.join("large.jsonl")}),
            activation,
            false,
        );
        profile.event(
            "PreToolUse",
            "Agent",
            json!({"prompt":"copy artwork"}),
            activation,
            false,
        );
        profile.event(
            "PostToolUseFailure",
            "Bash",
            json!({"command":"broken wrapper"}),
            activation,
            false,
        );
        profile.event("SessionEnd", "", json!({}), activation, false);
        assert_eq!(
            profile.markers(),
            stale,
            "inactive events must preserve stale state"
        );
    }
    for activation in ["request", "session", "repository"] {
        profile.event(
            "UserPromptSubmit",
            "",
            semantic.clone(),
            Some(activation),
            false,
        );
        profile.event(
            "PostToolUse",
            "Skill",
            json!({"skill":"azdaja"}),
            Some(activation),
            false,
        );
        for command in ["cp large.jsonl copied.jsonl", "cp absent.txt failed.txt"] {
            profile.event(
                "PreToolUse",
                "Bash",
                json!({"command":command}),
                Some(activation),
                false,
            );
        }
        profile.event(
            "PreToolUse",
            "Bash",
            json!({"command":"cp large.jsonl /dev/stdout"}),
            Some(activation),
            true,
        );
        profile.event(
            "PreToolUse",
            "Agent",
            json!({"prompt":"inspect artwork"}),
            Some(activation),
            false,
        );
        let failed = Command::new("cp")
            .args(["absent.txt", "failed.txt"])
            .current_dir(&profile.root)
            .output()
            .unwrap();
        assert!(!failed.status.success());
        profile.event(
            "PostToolUseFailure",
            "Bash",
            json!({"command":"cp absent.txt failed.txt"}),
            Some(activation),
            false,
        );
        assert!(profile.markers().is_empty());
        profile.event(
            "PreToolUse",
            "Read",
            json!({"file_path":profile.root.join("large.jsonl")}),
            Some(activation),
            false,
        );
        assert!(
            Command::new("cp")
                .args(["small.ts", "copied.ts"])
                .current_dir(&profile.root)
                .status()
                .unwrap()
                .success()
        );
        assert_eq!(
            fs::read(profile.root.join("small.ts")).unwrap(),
            fs::read(profile.root.join("copied.ts")).unwrap()
        );
        profile.event(
            "UserPromptSubmit",
            "",
            semantic.clone(),
            Some(activation),
            false,
        );
        profile.event(
            "PostToolUse",
            "Skill",
            json!({"skill":"azdaja"}),
            Some(activation),
            false,
        );
        profile.event(
            "UserPromptSubmit",
            "",
            json!({"prompt":"Continue ordinary code navigation."}),
            Some(activation),
            false,
        );
        assert!(profile.markers().is_empty());
        profile.event("SessionEnd", "", json!({}), Some(activation), false);
    }
    assert!(Path::new(&profile.plugin).join("SKILL.md").exists());
}
