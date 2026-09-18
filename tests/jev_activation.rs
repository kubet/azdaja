//! Actual CLI activation boundaries. Synthetic credentials only; never invoke judge_many.
#![cfg(unix)]
use serde_json::{Value, json};
use std::{
    ffi::OsString,
    fs,
    io::Write,
    os::unix::{
        ffi::OsStringExt,
        fs::{PermissionsExt, symlink},
    },
    path::PathBuf,
    process::{Command, Output, Stdio},
    sync::atomic::{AtomicU64, Ordering},
};

const KEY: &str = "apikey_SYNTHETICACTIVATION_0123456789abcdef0123456789abcdef";
const CUSTOM: &str = "AZDAJA_ACTIVATION_CUSTOM_KEY";
static NEXT: AtomicU64 = AtomicU64::new(0);
struct Case {
    root: PathBuf,
}
impl Case {
    fn new() -> Self {
        let base = std::env::var_os("JCODE_SCRATCH_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(std::env::temp_dir);
        let root = base.join(format!(
            "az-activation-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir_all(&root).unwrap();
        fs::set_permissions(&root, fs::Permissions::from_mode(0o700)).unwrap();
        let case = Self { root };
        case.configure(None, "TYPESAFE_API_KEY");
        case
    }
    fn state(&self) -> PathBuf {
        self.root.join("state")
    }
    fn configure(&self, enabled: Option<bool>, name: &str) {
        let enabled = enabled
            .map(|v| format!("enabled = {v}\n"))
            .unwrap_or_default();
        fs::write(self.root.join("config.toml"), format!("sub_llm_cmd = \"/usr/bin/false\"\ncell_timeout = 5\n[judge]\n{enabled}key_env = {name:?}\n")).unwrap();
    }
    fn run(&self, args: &[&str], input: &str, vars: &[(&str, OsString)]) -> Output {
        let binary = std::env::var_os("AZDAJA_ACTIVATION_BINARY")
            .unwrap_or_else(|| env!("CARGO_BIN_EXE_azdaja").into());
        let mut cmd = Command::new(binary);
        cmd.args(args)
            .current_dir(&self.root)
            .env_clear()
            .env("PATH", "/usr/bin:/bin")
            .env("HOME", &self.root)
            .env("AZDAJA_HOME", self.state())
            .env("AZDAJA_CONFIG", self.root.join("config.toml"))
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        for (name, value) in vars {
            cmd.env(name, value);
        }
        let mut child = cmd.spawn().unwrap();
        child
            .stdin
            .take()
            .unwrap()
            .write_all(input.as_bytes())
            .unwrap();
        let out = child.wait_with_output().unwrap();
        assert!(!text(&out).contains(KEY), "credential disclosed by CLI");
        out
    }
    fn ok(&self, args: &[&str], input: &str, vars: &[(&str, OsString)]) -> Output {
        let out = self.run(args, input, vars);
        assert!(out.status.success(), "{args:?}: {}", text(&out));
        out
    }
    fn json(&self, args: &[&str], vars: &[(&str, OsString)]) -> Value {
        serde_json::from_slice(&self.ok(args, "", vars).stdout).unwrap()
    }
    fn attach(&self, name: &str) {
        self.ok(&["jev", "attach", "--stdin", "--key-env", name], KEY, &[]);
    }
    fn stats(&self, vars: &[(&str, OsString)], expected: bool) {
        // Start is deliberately credential-free. Only the exec subprocess receives the environment.
        let start = self.ok(&["start"], "", &[]);
        let id = String::from_utf8(start.stdout).unwrap().trim().to_owned();
        let out = self.run(&["exec", &id], "FINAL(judge_stats())\n", vars);
        let result = self.run(&["final", &id], "", &[]);
        let killed = self.run(&["kill", &id], "", &[]);
        assert!(out.status.success(), "{}", text(&out));
        assert!(result.status.success(), "{}", text(&result));
        assert!(killed.status.success(), "{}", text(&killed));
        let stats: Value = serde_json::from_slice(&result.stdout).unwrap();
        assert_eq!(stats["enabled"], expected, "{stats}");
        assert_eq!(stats["provider_requests"], 0);
        assert_eq!(stats["poisoned"], false);
    }
}
impl Drop for Case {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.root);
    }
}
fn text(out: &Output) -> String {
    format!(
        "{}{}",
        String::from_utf8_lossy(&out.stdout),
        String::from_utf8_lossy(&out.stderr)
    )
}
fn env<'a>(name: &'a str, value: &str) -> Vec<(&'a str, OsString)> {
    vec![(name, value.into())]
}

#[test]
fn auto_environment_is_resolved_at_execution_only() {
    let c = Case::new();
    c.stats(&[], false);
    c.stats(&env("TYPESAFE_API_KEY", KEY), cfg!(feature = "typesafe"));
    for value in ["", "invalid token!", "apikey_bad\nvalue"] {
        c.stats(&env("TYPESAFE_API_KEY", value), false);
    }
    c.stats(
        &[("TYPESAFE_API_KEY", OsString::from_vec(vec![0xff]))],
        false,
    );
}

#[test]
fn attachment_is_detected_after_restart_and_detach_without_config_mutation() {
    let c = Case::new();
    let before = fs::read(c.root.join("config.toml")).unwrap();
    c.stats(&[], false);
    c.attach("TYPESAFE_API_KEY");
    assert_eq!(fs::read(c.root.join("config.toml")).unwrap(), before);
    c.stats(&[], cfg!(feature = "typesafe"));
    c.stats(&[], cfg!(feature = "typesafe"));
    c.ok(&["jev", "detach"], "", &[]);
    c.stats(&[], false);
    assert_eq!(fs::read(c.root.join("config.toml")).unwrap(), before);
}

#[test]
fn invalid_environment_shadows_valid_attachment_including_non_unicode() {
    let c = Case::new();
    c.attach("TYPESAFE_API_KEY");
    for value in [
        OsString::from(""),
        OsString::from("invalid token!"),
        OsString::from_vec(vec![0xff]),
    ] {
        c.stats(&[("TYPESAFE_API_KEY", value)], false);
    }
}

#[test]
fn explicit_false_overrides_environment_and_attachment_and_true_preserves_opt_in() {
    let c = Case::new();
    c.attach("TYPESAFE_API_KEY");
    c.configure(Some(false), "TYPESAFE_API_KEY");
    c.stats(&[], false);
    c.stats(&env("TYPESAFE_API_KEY", KEY), false);
    c.configure(Some(true), "TYPESAFE_API_KEY");
    // Explicit true historically exposes enabled stats even in feature-off builds.
    c.stats(&env("TYPESAFE_API_KEY", ""), true);
}

#[test]
fn custom_key_has_no_default_environment_or_attachment_fallback() {
    let c = Case::new();
    c.attach("TYPESAFE_API_KEY");
    c.configure(None, CUSTOM);
    c.stats(&env("TYPESAFE_API_KEY", KEY), false);
    c.stats(&env(CUSTOM, KEY), cfg!(feature = "typesafe"));
    c.attach(CUSTOM);
    c.stats(&[], cfg!(feature = "typesafe"));
    c.stats(&env(CUSTOM, "invalid token!"), false);
}

#[test]
fn doctor_reports_tristate_and_effective_build_gating_without_network() {
    for (configured, mode) in [
        (None, "auto"),
        (Some(false), "disabled"),
        (Some(true), "enabled"),
    ] {
        let c = Case::new();
        c.configure(configured, CUSTOM);
        for present in [false, true] {
            let vars = if present { env(CUSTOM, KEY) } else { vec![] };
            let report = c.json(&["doctor", "jev"], &vars);
            assert_eq!(report["configured_enabled"], json!(configured));
            assert_eq!(report["activation_mode"], mode);
            assert_eq!(
                report["effective_enabled"],
                cfg!(feature = "typesafe") && configured.unwrap_or(present)
            );
            assert_eq!(
                report["solo_effective_enabled"],
                cfg!(feature = "typesafe") && configured == Some(true)
            );
            assert_eq!(report["provider_readiness_checked"], false);
            assert!(!c.state().exists(), "readiness must not initialize state");
        }
    }
}

#[test]
fn static_help_and_caps_ignore_symlinked_invalid_configuration_and_storage() {
    let c = Case::new();
    fs::remove_file(c.root.join("config.toml")).unwrap();
    fs::write(c.root.join("config-marker"), "invalid TOML [[").unwrap();
    symlink(c.root.join("config-marker"), c.root.join("config.toml")).unwrap();
    let marker = c.root.join("unsafe-state-marker");
    fs::create_dir(&marker).unwrap();
    fs::set_permissions(&marker, fs::Permissions::from_mode(0o777)).unwrap();
    symlink(&marker, c.state()).unwrap();
    for args in [
        vec!["--help"],
        vec!["jev", "--help"],
        vec!["jev", "batch", "--help"],
        vec!["doctor", "--caps"],
    ] {
        let out = c.ok(&args, "", &env("TYPESAFE_API_KEY", KEY));
        if args == ["doctor", "--caps"] {
            let caps: Value = serde_json::from_slice(&out.stdout).unwrap();
            assert_eq!(caps["typed_judgments"]["credentials_checked"], false);
            assert_eq!(caps["typed_batches"]["credentials_checked"], false);
        }
    }
    assert_eq!(
        fs::read_to_string(c.root.join("config-marker")).unwrap(),
        "invalid TOML [["
    );
    assert_eq!(fs::read_dir(marker).unwrap().count(), 0);
    assert!(c.state().is_symlink());
}

#[test]
fn offline_batch_validation_does_not_resolve_attached_key_or_create_output() {
    let c = Case::new();
    let marker = c.root.join("unsafe-storage");
    fs::create_dir(&marker).unwrap();
    fs::set_permissions(&marker, fs::Permissions::from_mode(0o777)).unwrap();
    symlink(&marker, c.state()).unwrap();
    let row = json!({"id":"one", "state":"Local synthetic source", "questions":{"q":{"type":"noul","instructions":"Is this local?"}}});
    fs::write(c.root.join("plan.jsonl"), format!("{row}\n")).unwrap();
    let report = c.json(
        &["jev", "batch", "--input", "plan.jsonl"],
        &env("TYPESAFE_API_KEY", KEY),
    );
    assert_eq!(report["provider_requests"], 0);
    assert_eq!(report["credentials_checked"], false);
    assert_eq!(report["execution_enabled"], false);
    assert!(!c.root.join("job").exists());
    assert_eq!(fs::read_dir(marker).unwrap().count(), 0);
}

#[test]
fn solo_local_generator_requires_explicit_opt_in_and_never_receives_credentials() {
    for (configured, active) in [
        (None, false),
        (None, true),
        (Some(false), true),
        (Some(true), true),
    ] {
        let c = Case::new();
        // POSIX shell drains all stdin and returns only a local program, with no judge callback.
        fs::write(c.root.join("generator.sh"), "#!/bin/sh\ncat > prompt.txt\nenv > generator.env\nprintf '```python\\nFINAL(42)\\n```\\n'\n").unwrap();
        let generator = format!(
            "/bin/sh {}",
            shlex::try_quote(c.root.join("generator.sh").to_str().unwrap()).unwrap()
        );
        let enabled = configured
            .map(|v| format!("enabled = {v}\n"))
            .unwrap_or_default();
        fs::write(c.root.join("config.toml"), format!("sub_llm_cmd = {}\ncell_timeout = 5\nsub_timeout = 5\n[judge]\n{enabled}key_env = {CUSTOM:?}\n", serde_json::to_string(&generator).unwrap())).unwrap();
        let mut vars = if active { env(CUSTOM, KEY) } else { vec![] };
        vars.push((
            "AZDAJA_SOLO_TRACE",
            c.root.join("solo.trace").into_os_string(),
        ));
        let out = c.ok(
            &["solo", "Return 42 locally.", "-f", "-"],
            "Local source.",
            &vars,
        );
        assert_eq!(String::from_utf8_lossy(&out.stdout).trim(), "42");
        let prompt = fs::read_to_string(c.root.join("prompt.txt")).unwrap();
        let typed_ready = configured == Some(true) && cfg!(feature = "typesafe");
        assert_eq!(prompt.contains("Optional engines:"), typed_ready);
        assert_eq!(
            prompt.contains("judge_many(state, questions):"),
            typed_ready
        );
        assert_eq!(
            prompt.contains("TypeSafe transport is unavailable in this build."),
            configured == Some(true) && !cfg!(feature = "typesafe")
        );
        if configured != Some(true) {
            assert!(
                !prompt.contains("judge_many"),
                "auto and disabled solo keep the old prompt"
            );
        }
        let trace = fs::read_to_string(c.root.join("solo.trace")).unwrap();
        let runtime = trace
            .lines()
            .filter_map(|line| serde_json::from_str::<Value>(line).ok())
            .find(|row| row["event"] == "solo_runtime")
            .expect("solo runtime footer");
        let cells = runtime["judge_cells"]
            .as_array()
            .map(Vec::as_slice)
            .unwrap_or(&[]);
        if configured != Some(true) {
            assert!(
                cells.is_empty(),
                "non-opted-in solo must not use optional runtime"
            );
        }
        for cell in cells {
            assert_eq!(cell["provider_requests"], 0);
        }
        assert!(!prompt.contains(KEY));
        let child_env = fs::read_to_string(c.root.join("generator.env")).unwrap();
        assert!(
            !child_env.contains(KEY),
            "typed credential leaked to custom generator"
        );
    }
}

#[test]
fn fresh_batch_preflight_rejects_auto_off_and_explicit_disabled_without_job_files() {
    for configured in [None, Some(false)] {
        let c = Case::new();
        c.configure(configured, CUSTOM);
        let row = json!({"id":"one", "state":"Synthetic local source", "questions":{"q":{"type":"noul","instructions":"Is this local?"}}});
        fs::write(c.root.join("plan.jsonl"), format!("{row}\n")).unwrap();
        // A valid key is supplied only with explicit false, so no branch can enter transport.
        let vars = if configured == Some(false) {
            env(CUSTOM, KEY)
        } else {
            vec![]
        };
        let out = c.run(
            &[
                "jev",
                "batch",
                "--input",
                "plan.jsonl",
                "--execute",
                "--output",
                "job",
                "--max-requests",
                "1",
                "--max-input-tokens",
                "10000",
                "--max-seconds",
                "5",
            ],
            "",
            &vars,
        );
        assert!(!out.status.success(), "{}", text(&out));
        assert!(
            !c.root.join("job").exists(),
            "rejected preflight must not create job files"
        );
        assert!(!c.state().exists());
    }
}

#[test]
fn auto_batch_with_matching_synthetic_secret_reaches_leakage_guard_before_intent() {
    let c = Case::new();
    c.configure(None, CUSTOM);
    // Exact key in source guarantees local leakage refusal before any transport.
    let row = json!({"id":"one", "state":KEY, "questions":{"q":{"type":"noul","instructions":"Is this local?"}}});
    fs::write(c.root.join("plan.jsonl"), format!("{row}\n")).unwrap();
    let vars = env(CUSTOM, KEY);
    let report = c.json(&["jev", "batch", "--input", "plan.jsonl"], &vars);
    assert_eq!(report["provider_requests"], 0);
    assert_eq!(report["credentials_checked"], false);
    assert_eq!(report["execution_enabled"], false);
    assert!(!c.state().exists());
    assert!(!c.root.join("job").exists());
    let out = c.run(
        &[
            "jev",
            "batch",
            "--input",
            "plan.jsonl",
            "--execute",
            "--output",
            "job",
            "--max-requests",
            "1",
            "--max-input-tokens",
            "10000",
            "--max-seconds",
            "5",
        ],
        "",
        &vars,
    );
    assert!(!out.status.success(), "{}", text(&out));
    if cfg!(feature = "typesafe") {
        assert!(
            text(&out).contains("credential leakage refused"),
            "{}",
            text(&out)
        );
        assert!(
            !text(&out).contains("judge disabled"),
            "auto must resolve before preflight"
        );
    } else {
        assert!(text(&out).contains("judge disabled"), "{}", text(&out));
    }
    assert!(!c.state().exists());
    assert!(
        !c.root.join("job").exists(),
        "no durable intent or output before leakage guard"
    );
}
