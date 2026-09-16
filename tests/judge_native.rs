//! Public CLI boundary tests. Never provide a credential or enter a provider.
use std::{
    fs,
    io::Write,
    path::PathBuf,
    process::{Command, Output, Stdio},
    time::{SystemTime, UNIX_EPOCH},
};

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
            "az-judge-cli-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
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
    assert!(!cfg.judge.enabled);
    cfg.judge.enabled = true;
    cfg.judge.max_requests_per_cell = 2;
    let encoded = toml::to_string(&cfg).unwrap();
    assert!(encoded.contains("[judge]"));
    let decoded: azdaja::Config = toml::from_str(&encoded).unwrap();
    assert_eq!(decoded.judge.max_requests_per_cell, 2);
    decoded.validate().unwrap();
    cfg.judge.timeout_secs = 0;
    assert!(cfg.validate().is_err());
}

#[cfg(unix)]
#[test]
fn native_judgment_key_is_not_forwarded_to_custom_generative_provider() {
    let s = Session::new("enabled = true");
    let mut cfg = azdaja::Config::default();
    cfg.sub_llm_cmd = "/bin/sh -c 'if [ -n \"$TYPESAFE_API_KEY$AZDAJA_CUSTOM_JUDGE_TEST\" ]; then printf leaked; else printf isolated; fi'".into();
    cfg.judge.key_env = "AZDAJA_CUSTOM_JUDGE_TEST".into();
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
        .write_all(b"FINAL(llm('return environment isolation status'))\n")
        .unwrap();
    let result = child.wait_with_output().unwrap();
    assert!(
        result.status.success(),
        "{}",
        String::from_utf8_lossy(&result.stderr)
    );
    assert_eq!(s.ok(&["final", &s.id], "").trim(), "isolated");
}
