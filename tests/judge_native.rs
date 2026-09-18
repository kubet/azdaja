//! Public CLI boundary tests. Never provide a credential or enter a provider.
use std::{
    fs,
    io::Write,
    path::PathBuf,
    process::{Command, Output, Stdio},
    sync::atomic::{AtomicU64, Ordering},
    time::{SystemTime, UNIX_EPOCH},
};

static NEXT_DIRECTORY: AtomicU64 = AtomicU64::new(0);

struct Session {
    dir: PathBuf,
    id: String,
}
impl Session {
    fn new(judge: &str) -> Self {
        let base = std::env::var_os("JCODE_SCRATCH_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(std::env::temp_dir);
        let dir = base.join(format!(
            "az-judge-cli-{}-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos(),
            NEXT_DIRECTORY.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join("config.toml"), format!("sub_llm_cmd = \"/usr/bin/false\"\ncell_timeout = 3\n[judge]\nkey_env = \"AZDAJA_TEST_MUST_NOT_HAVE_A_KEY\"\n{judge}\n")).unwrap();
        let mut session = Self {
            dir,
            id: String::new(),
        };
        session.id = session.ok(&["start"], "").trim().to_owned();
        session
    }
    fn run(&self, args: &[&str], code: &str) -> Output {
        let mut child = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .args(args)
            .env("AZDAJA_HOME", self.dir.join("state"))
            .env("AZDAJA_CONFIG", self.dir.join("config.toml"))
            .env_remove("TYPESAFE_API_KEY")
            .env_remove("AZDAJA_TEST_MUST_NOT_HAVE_A_KEY")
            .env_remove("RLM_DEPTH")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap();
        child
            .stdin
            .take()
            .unwrap()
            .write_all(code.as_bytes())
            .unwrap();
        child.wait_with_output().unwrap()
    }
    fn ok(&self, args: &[&str], code: &str) -> String {
        let out = self.run(args, code);
        assert!(
            out.status.success(),
            "stdout={} stderr={}",
            String::from_utf8_lossy(&out.stdout),
            String::from_utf8_lossy(&out.stderr)
        );
        String::from_utf8(out.stdout).unwrap()
    }
    fn fails(&self, code: &str, expected: &str) {
        let out = self.run(&["exec", &self.id], code);
        assert!(!out.status.success(), "unexpected success");
        let text = format!(
            "{}{}",
            String::from_utf8_lossy(&out.stdout),
            String::from_utf8_lossy(&out.stderr)
        );
        assert!(text.contains(expected), "expected {expected:?}: {text}");
    }
    fn final_json(&self, code: &str) -> serde_json::Value {
        self.ok(&["exec", &self.id], code);
        serde_json::from_str(self.ok(&["final", &self.id], "").trim()).unwrap()
    }
}
impl Drop for Session {
    fn drop(&mut self) {
        let _ = self.run(&["kill", &self.id], "");
        let _ = fs::remove_dir_all(&self.dir);
    }
}

#[test]
fn native_judgments_default_disabled_and_regular_repl_recovers() {
    let s = Session::new("");
    let stats = s.final_json("FINAL(judge_stats())\n");
    assert_eq!(stats["enabled"], false);
    assert_eq!(stats["provider_requests"], 0);
    s.fails("judge_many({}, {})\n", "judge_many is disabled");
    assert_eq!(
        s.final_json("x=41\nFINAL({'answer':x+1,'stats':judge_stats()})\n")["answer"],
        42
    );
    assert_eq!(s.final_json("FINAL(x+2)\n"), 43);
}

#[test]
fn native_judgment_argument_errors_do_not_enter_provider() {
    for (code, error) in [
        ("judge_many()", "requires state"),
        ("judge_many({}, {}, {})", "requires state and questions"),
        (
            "judge_many({}, {}, endpoint='elsewhere')",
            "accepts only state and questions",
        ),
        ("judge_many({}, {}, state={})", "duplicate argument"),
        (
            "judge_many({1:'wrong key'}, {})",
            "state must be JSON representable",
        ),
        ("judge_stats(1)", "takes no arguments"),
    ] {
        let s = Session::new("enabled = true");
        s.fails(code, error);
        let stats = s.final_json("FINAL(judge_stats())\n");
        assert_eq!(stats["provider_requests"], 0);
        assert_eq!(stats["poisoned"], false);
    }
}

#[test]
fn native_judgment_valid_named_arguments_fail_before_network_without_key() {
    let s = Session::new("enabled = true");
    let code = "judge_many(questions={'q':{'type':'noul','instructions':'Does the record state X?'}}, state='X')";
    let expected = if cfg!(feature = "typesafe") {
        "credential unavailable"
    } else {
        "typesafe feature"
    };
    s.fails(code, expected);
    assert_eq!(
        s.final_json("FINAL({'ok':True,'usage':judge_stats()})\n")["usage"]["provider_requests"],
        0
    );
}

#[test]
fn native_judgment_config_roundtrips_without_a_secret() {
    let mut cfg = azdaja::Config::default();
    assert_eq!(cfg.judge.enabled, None);
    assert_eq!(cfg.judge.activation_mode(), "auto");
    cfg.judge.enabled = Some(true);
    cfg.judge.max_requests_per_cell = 2;
    let encoded = toml::to_string(&cfg).unwrap();
    assert!(encoded.contains("[judge]"));
    let decoded: azdaja::Config = toml::from_str(&encoded).unwrap();
    assert_eq!(decoded.judge.enabled, Some(true));
    assert_eq!(decoded.judge.max_requests_per_cell, 2);
    decoded.validate().unwrap();
    cfg.judge.timeout_secs = 0;
    assert!(cfg.validate().is_err());
}

#[test]
fn native_judgment_capabilities_are_static_and_distinguish_transport_from_readiness() {
    let s = Session::new("");
    let home = s.dir.join("caps home must remain absent");
    let state = s.dir.join("caps state must remain absent");
    let bad_config = s.dir.join("unreadable-as-toml");
    fs::write(&bad_config, "this is intentionally invalid TOML [[").unwrap();
    let missing_config = s.dir.join("missing config");
    let synthetic = "capability-probe-synthetic-not-a-credential";
    let mut previous = None;
    for config in [&bad_config, &missing_config] {
        let out = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .args(["doctor", "--caps"])
            .env_clear()
            .env("HOME", &home)
            .env("AZDAJA_HOME", &state)
            .env("AZDAJA_CONFIG", config)
            .env("TYPESAFE_API_KEY", synthetic)
            .output()
            .unwrap();
        assert!(out.status.success(), "{:?}", out.stderr);
        assert!(out.stderr.is_empty());
        assert!(!String::from_utf8_lossy(&out.stdout).contains(synthetic));
        let caps: serde_json::Value = serde_json::from_slice(&out.stdout).unwrap();
        assert!(
            caps["capabilities"]
                .as_array()
                .unwrap()
                .contains(&serde_json::json!("native-typed-judgments"))
        );
        assert_eq!(
            caps["typed_judgments"],
            serde_json::json!({
                "functions": ["judge_many", "judge_stats"],
                "typesafe_compiled": cfg!(feature = "typesafe"),
                "enabled_by_default": false,
                "host_opt_in_required": true,
                "default_activation_mode": "auto_when_configured_credential_is_valid",
                "explicit_disable_supported": true,
                "runtime_configuration_checked": false,
                "credentials_checked": false,
                "cache_and_budget_scope": "cell"
            })
        );
        if let Some(previous) = &previous {
            assert_eq!(&out.stdout, previous);
        }
        previous = Some(out.stdout);
        assert!(!home.exists());
        assert!(!state.exists());
        assert!(!missing_config.exists());
    }
}

#[cfg(unix)]
#[test]
fn native_judgment_key_is_not_forwarded_to_custom_generative_provider() {
    assert_custom_generative_provider_isolates_key(
        "FINAL(llm('return environment isolation status'))\n",
    );
}

#[cfg(unix)]
#[test]
fn native_judgment_custom_provider_drains_prompt_before_exiting() {
    // Exceed pipe capacity so a fixture that exits without consuming stdin fails
    // reliably, rather than racing the production provider's stdin writer.
    assert_custom_generative_provider_isolates_key("FINAL(llm('x' * (1024 * 1024)))\n");
}

#[cfg(unix)]
fn assert_custom_generative_provider_isolates_key(code: &str) {
    let s = Session::new("enabled = true");
    let cfg = azdaja::Config {
        // The stdin writer runs concurrently with the provider. Drain its prompt
        // before exiting, otherwise even a successful shell can cause BrokenPipe.
        sub_llm_cmd: "/bin/sh -c '/bin/cat >/dev/null && if [ -n \"$TYPESAFE_API_KEY$AZDAJA_CUSTOM_JUDGE_TEST\" ]; then printf leaked; else printf isolated; fi'".into(),
        judge: azdaja::judge::JudgeConfig {
            key_env: "AZDAJA_CUSTOM_JUDGE_TEST".into(),
            ..Default::default()
        },
        ..Default::default()
    };
    fs::write(s.dir.join("config.toml"), toml::to_string(&cfg).unwrap()).unwrap();
    let mut child = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args(["exec", &s.id])
        .env("AZDAJA_HOME", s.dir.join("state"))
        .env("AZDAJA_CONFIG", s.dir.join("config.toml"))
        .env("TYPESAFE_API_KEY", "synthetic-default-not-a-credential")
        .env(
            "AZDAJA_CUSTOM_JUDGE_TEST",
            "synthetic-custom-not-a-credential",
        )
        .env_remove("RLM_DEPTH")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(code.as_bytes())
        .unwrap();
    let result = child.wait_with_output().unwrap();
    assert!(
        result.status.success(),
        "status={} stdout={} stderr={}",
        result.status,
        String::from_utf8_lossy(&result.stdout),
        String::from_utf8_lossy(&result.stderr)
    );
    assert_eq!(s.ok(&["final", &s.id], "").trim(), "isolated");
}
