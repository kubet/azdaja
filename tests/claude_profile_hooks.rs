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
        self.raw_event(value, activation, deny);
    }
    /// One hook event payload exactly as Claude Code 2.1.273 emits it (captured
    /// from a live session on 2026-09-16). Field names are the host contract.
    fn captured(&self, name: &str, tool: Option<&str>, input: Value, extra: Value) -> Value {
        let mut value = json!({
            "session_id": "0d3f1c3e-captured",
            "transcript_path": self.root.join("transcript.jsonl"),
            "cwd": self.root,
            "hook_event_name": name,
        });
        if name != "SessionEnd" {
            value["prompt_id"] = json!("550e8400-e29b-41d4-a716-446655440000");
            value["permission_mode"] = json!("default");
        }
        if let Some(tool) = tool {
            value["tool_name"] = json!(tool);
            value["tool_input"] = input;
            value["tool_use_id"] = json!("toolu_01CapturedToolUse");
        } else if name == "UserPromptSubmit" {
            value["prompt"] = input;
        } else {
            value["reason"] = json!("other");
        }
        if let Some(extra) = extra.as_object() {
            for (key, item) in extra {
                value[key] = item.clone();
            }
        }
        value
    }
    /// Run the wrapper exactly as Claude's Bash tool would, against the installed binary.
    fn run_wrapper(&self, wrapper: &str) -> std::process::Output {
        Command::new("bash")
            .args(["-c", wrapper])
            .current_dir(&self.root)
            .env("HOME", &self.home)
            .env("AZDAJA_HOME", &self.state)
            .env_remove("AZDAJA_CONFIG")
            .output()
            .unwrap()
    }
    fn raw_event(&self, value: Value, activation: Option<&str>, deny: bool) {
        let name = value["hook_event_name"].as_str().unwrap().to_owned();
        let mut command = Command::new("sh");
        command
            .args(["-c", &self.commands[&name]])
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
    /// The managed wrapper exactly as the installed SKILL.md instructs Claude to
    /// run it, with only `<input-path>` and the Python cell substituted.
    fn installed_wrapper(&self, input: &Path) -> String {
        let skill = fs::read_to_string(self.plugin.join("SKILL.md")).unwrap();
        let fence = "```bash\nset -euo pipefail\n";
        let start = skill
            .find(fence)
            .expect("installed SKILL.md carries the managed wrapper")
            + "```bash\n".len();
        let end = start + skill[start..].find("\n```").unwrap();
        let wrapper = &skill[start..end];
        assert!(wrapper.contains("'<input-path>'"), "{wrapper}");
        assert!(
            wrapper.contains("<one compact Python cell ending in FINAL(...)>"),
            "{wrapper}"
        );
        let quoted = format!("'{}'", input.to_string_lossy().replace('\'', "'\\''"));
        wrapper
            .replace("'<input-path>'", &quoted)
            .replace("<one compact Python cell ending in FINAL(...)>", "FINAL(1)")
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

#[test]
fn installed_claude_skill_wrapper_is_recognized_by_installed_hook() {
    let profile = Profile::new();
    let wrapper = profile.installed_wrapper(&profile.root.join("large.jsonl"));
    let binary = profile.plugin.join("azdaja").to_string_lossy().into_owned();
    assert!(wrapper.contains(&binary), "{wrapper}");
    let foreign = wrapper.replace(&binary, "/different/azdaja");
    for activation in ["request", "session", "repository"] {
        profile.event(
            "UserPromptSubmit",
            "",
            json!({"prompt":"Classify every record in large.jsonl."}),
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
        // Negative control: the same wrapper naming another binary is broad access.
        profile.event(
            "PreToolUse",
            "Bash",
            json!({"command":foreign.clone()}),
            Some(activation),
            true,
        );
        // The wrapper the skill dictates must pass and claim the transaction lease.
        profile.event(
            "PreToolUse",
            "Bash",
            json!({"command":wrapper.clone()}),
            Some(activation),
            false,
        );
        assert!(
            profile
                .markers()
                .keys()
                .any(|name| name.ends_with(".transaction")),
            "{:?}",
            profile.markers().keys().collect::<Vec<_>>()
        );
        // A second lifecycle inside the same prompt is refused as in flight.
        profile.event(
            "PreToolUse",
            "Bash",
            json!({"command":wrapper.clone()}),
            Some(activation),
            true,
        );
        // Success releases the prompt for ordinary follow-up work.
        profile.event(
            "PostToolUse",
            "Bash",
            json!({"command":wrapper.clone()}),
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
        profile.event("SessionEnd", "", json!({}), Some(activation), false);
    }
}

/// Claude Code emits PreToolUse for the Skill tool and never PostToolUse for it.
/// The installed hook must route the exact captured sequence: deny the large
/// read, accept the skill invocation as activation, admit the dictated wrapper,
/// let it really run, and release the prompt on the captured success event.
#[test]
fn installed_hook_routes_the_captured_claude_code_sequence_without_post_tool_use_skill() {
    let profile = Profile::new();
    let large = profile.root.join("large.jsonl");
    let wrapper = profile
        .installed_wrapper(&large)
        .replace("FINAL(1)", "FINAL(len(source))");
    let bash =
        |command: &str| json!({"command": command, "description": "Run the Azdaja lifecycle"});
    for activation in ["request", "session", "repository"] {
        let on = Some(activation);
        profile.raw_event(
            profile.captured(
                "UserPromptSubmit",
                None,
                json!("Classify every record in large.jsonl by sentiment."),
                json!({}),
            ),
            on,
            false,
        );
        profile.raw_event(
            profile.captured(
                "PreToolUse",
                Some("Read"),
                json!({"file_path": large}),
                json!({}),
            ),
            on,
            true,
        );
        profile.raw_event(
            profile.captured(
                "PreToolUse",
                Some("Skill"),
                json!({"skill": "azdaja"}),
                json!({}),
            ),
            on,
            false,
        );
        assert!(
            profile
                .markers()
                .keys()
                .any(|name| name.ends_with(".active")),
            "{:?}",
            profile.markers().keys().collect::<Vec<_>>()
        );
        profile.raw_event(
            profile.captured("PreToolUse", Some("Bash"), bash(&wrapper), json!({})),
            on,
            false,
        );
        assert!(
            profile
                .markers()
                .keys()
                .any(|name| name.ends_with(".transaction"))
        );
        let output = profile.run_wrapper(&wrapper);
        assert!(
            output.status.success(),
            "dictated wrapper failed: {}",
            String::from_utf8_lossy(&output.stderr)
        );
        assert_eq!(
            String::from_utf8_lossy(&output.stdout).trim(),
            (2 * 1024 * 1024).to_string(),
            "wrapper must answer from the loaded input"
        );
        profile.raw_event(
            profile.captured(
                "PostToolUse",
                Some("Bash"),
                bash(&wrapper),
                json!({"tool_response": {"stdout": "2097152", "stderr": "", "interrupted": false,
                    "isImage": false, "noOutputExpected": false}}),
            ),
            on,
            false,
        );
        assert!(
            profile.markers().is_empty(),
            "success must release the prompt"
        );
        profile.raw_event(
            profile.captured(
                "PreToolUse",
                Some("Read"),
                json!({"file_path": large}),
                json!({}),
            ),
            on,
            false,
        );
        profile.raw_event(
            profile.captured("SessionEnd", None, json!(null), json!({})),
            on,
            false,
        );
    }
}

/// A lifecycle that really fails must release the prompt on the captured
/// PostToolUseFailure event so ordinary tools come back without another wrapper.
#[test]
fn installed_hook_releases_the_prompt_after_a_captured_failed_lifecycle() {
    let profile = Profile::new();
    let large = profile.root.join("large.jsonl");
    let wrapper = profile
        .installed_wrapper(&large)
        .replace("FINAL(1)", "FINAL(undefined_name)");
    let bash =
        |command: &str| json!({"command": command, "description": "Run the Azdaja lifecycle"});
    let on = Some("session");
    profile.raw_event(
        profile.captured(
            "UserPromptSubmit",
            None,
            json!("Label every record in large.jsonl."),
            json!({}),
        ),
        on,
        false,
    );
    profile.raw_event(
        profile.captured(
            "PreToolUse",
            Some("Skill"),
            json!({"skill": "azdaja"}),
            json!({}),
        ),
        on,
        false,
    );
    profile.raw_event(
        profile.captured("PreToolUse", Some("Bash"), bash(&wrapper), json!({})),
        on,
        false,
    );
    let output = profile.run_wrapper(&wrapper);
    assert!(
        !output.status.success(),
        "the broken cell must fail the lifecycle"
    );
    profile.raw_event(
        profile.captured(
            "PostToolUseFailure",
            Some("Bash"),
            bash(&wrapper),
            json!({"error": String::from_utf8_lossy(&output.stderr), "is_interrupt": false,
                "duration_ms": 12}),
        ),
        on,
        false,
    );
    assert!(
        profile.markers().is_empty(),
        "failure must release the prompt"
    );
    profile.raw_event(
        profile.captured(
            "PreToolUse",
            Some("Read"),
            json!({"file_path": large}),
            json!({}),
        ),
        on,
        false,
    );
    profile.raw_event(
        profile.captured(
            "PreToolUse",
            Some("Bash"),
            bash("wc -l large.jsonl"),
            json!({}),
        ),
        on,
        false,
    );
    profile.raw_event(
        profile.captured("SessionEnd", None, json!(null), json!({})),
        on,
        false,
    );
}
