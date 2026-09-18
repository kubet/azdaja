#![cfg(unix)]

use std::{
    fs,
    path::PathBuf,
    process::{Command, Output},
    sync::atomic::{AtomicUsize, Ordering},
    time::{SystemTime, UNIX_EPOCH},
};

struct Case {
    root: PathBuf,
    source: String,
}

// Independently computed with Python hashlib over exact UTF-8 bytes, including CRLF.
const SOURCE_SHA256: &str = "6f8b8183090997bba9cfae687decbfbb52d3d18c12f45da2484f505a9cdf83cb";

impl Case {
    fn new() -> Self {
        static NEXT_CASE: AtomicUsize = AtomicUsize::new(0);
        let base = std::env::var_os("JCODE_SCRATCH_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(std::env::temp_dir);
        let root = base.join(format!(
            "azdaja-hash-preflight-{}-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos(),
            NEXT_CASE.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&root).unwrap();
        let source = "Public source with Unicode 🦀 and exact CRLF.\r\n".repeat(32_768);
        assert_eq!(source.len(), 1_605_632);
        assert_eq!(source.chars().count(), 1_507_328);
        fs::write(root.join("source.txt"), &source).unwrap();
        fs::write(
            root.join("provider.py"),
            r#"import os, pathlib, sys
prompt = sys.stdin.buffer.read()  # Always drain the complete pipe.
root = pathlib.Path(__file__).parent
kind = 'root' if os.environ.get('RLM_DEPTH') == '0' else 'child'
log = root / (kind + '.count')
count = int(log.read_text()) + 1 if log.exists() else 1
log.write_text(str(count))
if kind == 'root':
    name = 'first.py' if count == 1 else 'repair.py'
    print('```python\n' + (root / name).read_text() + '\n```')
else:
    print('observed-local-child')
"#,
        )
        .unwrap();
        Self { root, source }
    }

    fn run(&self, enabled: bool, first: &str, repair: &str) -> Output {
        fs::write(self.root.join("first.py"), first).unwrap();
        fs::write(self.root.join("repair.py"), repair).unwrap();
        let provider = format!(
            "python3 {}",
            shlex::try_quote(self.root.join("provider.py").to_str().unwrap()).unwrap()
        );
        let config = format!(
            "sub_llm_cmd = {}\ncell_timeout = 20\nsub_timeout = 20\n[judge]\nenabled = {enabled}\nkey_env = \"AZDAJA_PREFLIGHT_TEST_ABSENT\"\n",
            serde_json::to_string(&provider).unwrap()
        );
        fs::write(self.root.join("config.toml"), config).unwrap();
        Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .args([
                "solo",
                "Return the exact source hash, length and the verification note.",
                "-f",
            ])
            .arg(self.root.join("source.txt"))
            .current_dir(&self.root)
            .env_clear()
            .env("PATH", "/usr/bin:/bin")
            .env("HOME", &self.root)
            .env("LANG", "C.UTF-8")
            .env("PYTHONUTF8", "1")
            .env("AZDAJA_HOME", self.root.join("state"))
            .env("AZDAJA_CONFIG", self.root.join("config.toml"))
            .env("AZDAJA_SOLO_TRACE", self.root.join("solo.trace"))
            .env("AZDAJA_MODEL_TRACE", self.root.join("model.jsonl"))
            .output()
            .unwrap()
    }

    fn count(&self, kind: &str) -> usize {
        fs::read_to_string(self.root.join(format!("{kind}.count")))
            .map(|s| s.parse().unwrap())
            .unwrap_or(0)
    }

    fn runtime(&self) -> serde_json::Value {
        fs::read_to_string(self.root.join("solo.trace"))
            .unwrap()
            .lines()
            .filter_map(|line| serde_json::from_str::<serde_json::Value>(line).ok())
            .find(|row| row["event"] == "solo_runtime")
            .expect("public runtime footer")
    }

    fn assert_answer(&self, output: &Output) {
        assert!(
            output.status.success(),
            "status={} roots={} children={} stdout={} stderr={}",
            output.status,
            self.count("root"),
            self.count("child"),
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        let answer: serde_json::Value =
            serde_json::from_slice(&output.stdout).expect("public FINAL is JSON");
        assert_eq!(answer["source_sha256"], SOURCE_SHA256);
        assert_eq!(answer["characters"], self.source.chars().count());
        assert_eq!(answer["note"], "observed-local-child");
        assert_eq!(self.runtime()["outcome"], "succeeded");
    }
}

impl Drop for Case {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.root);
    }
}

const BAD: &str = "note=llm('local-child-probe')\nFINAL({'source_sha256':sha256(ctx.encode('utf-8')).hexdigest(),'characters':len(ctx),'note':note})";
const GOOD: &str = "note=llm('local-child-probe')\nFINAL({'source_sha256':sha256(ctx),'characters':len(ctx),'note':note})";

#[cfg(feature = "typesafe")]
#[test]
fn optional_hash_contract_is_repaired_before_any_child_read() {
    let case = Case::new();
    let output = case.run(true, BAD, GOOD);
    case.assert_answer(&output);
    assert_eq!(case.count("root"), 2);
    assert_eq!(
        case.count("child"),
        1,
        "no preflight child and no paid replay"
    );
    assert_eq!(case.runtime()["exec_invocation_count"], 1);
    assert_eq!(case.runtime()["semantic_call_count"], 1);
    let runtime = case.runtime();
    let cells = runtime["judge_cells"].as_array().unwrap();
    assert_eq!(cells.len(), 1);
    assert_eq!(cells[0]["attempts"], 0);
    assert_eq!(cells[0]["total_wall_ns"], 0);
}

#[test]
fn valid_hash_and_source_like_literals_work_in_both_modes() {
    let code =
        format!("literal = '''sha256(ctx.encode()).hexdigest()'''\n# sha256(ctx).digest()\n{GOOD}");
    for enabled in [false, true] {
        let case = Case::new();
        let output = case.run(enabled, &code, &code);
        case.assert_answer(&output);
        assert_eq!(case.count("root"), 1);
        assert_eq!(case.count("child"), 1);
    }
}

#[test]
fn disabled_and_feature_off_preserve_legacy_execution() {
    let modes = if cfg!(feature = "typesafe") {
        vec![false]
    } else {
        vec![false, true]
    };
    for enabled in modes {
        let case = Case::new();
        let output = case.run(enabled, BAD, GOOD);
        assert!(!output.status.success());
        assert!(
            !String::from_utf8_lossy(&output.stderr).contains("optional solo native hash contract")
        );
        assert_eq!(case.count("root"), 1);
        assert_eq!(case.count("child"), 1);
        assert_eq!(case.runtime()["outcome"], "failed");
        assert_eq!(case.runtime()["exec_invocation_count"], 1);
    }
}

#[test]
fn unrelated_failure_after_a_child_is_not_automatically_replayed() {
    let case = Case::new();
    let code = "note=llm('local-child-probe')\nFINAL(1/0)";
    let output = case.run(true, code, GOOD);
    assert!(!output.status.success());
    assert_eq!(case.count("root"), 1);
    assert_eq!(case.count("child"), 1);
    assert_eq!(case.runtime()["outcome"], "failed");
    assert_eq!(case.runtime()["exec_invocation_count"], 1);
}

#[cfg(feature = "typesafe")]
#[test]
fn persistent_bad_program_stops_at_existing_root_limit_without_children() {
    let case = Case::new();
    let output = case.run(true, BAD, BAD);
    assert!(!output.status.success());
    assert_eq!(case.count("root"), 4);
    assert_eq!(case.count("child"), 0);
    assert_eq!(case.runtime()["outcome"], "failed");
    assert_eq!(case.runtime()["exec_invocation_count"], 0);
    assert_eq!(case.runtime()["semantic_call_count"], 0);
}

#[cfg(feature = "typesafe")]
#[test]
fn known_hash_failure_never_enters_prior_typed_callback() {
    let case = Case::new();
    let bad = "judge_many(ctx, {})\nFINAL(sha256(ctx).hexdigest())";
    let output = case.run(true, bad, GOOD);
    case.assert_answer(&output);
    assert_eq!(case.count("root"), 2);
    assert_eq!(case.count("child"), 1);
    let runtime = case.runtime();
    assert_eq!(runtime["exec_invocation_count"], 1);
    let cells = runtime["judge_cells"].as_array().unwrap();
    assert_eq!(cells.len(), 1);
    assert_eq!(cells[0]["attempts"], 0);
    assert_eq!(cells[0]["total_wall_ns"], 0);
}
