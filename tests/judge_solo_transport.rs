//! Actual public solo failure boundaries, with macOS enforcing no network.
//! This does not simulate a successful TypeSafe response or use a real credential.
#![cfg(target_os = "macos")]

use std::{
    fs,
    os::unix::fs::PermissionsExt,
    path::PathBuf,
    process::{Command, Output},
    sync::{
        OnceLock,
        atomic::{AtomicUsize, Ordering},
    },
    time::{SystemTime, UNIX_EPOCH},
};

const PROFILE: &str = "(version 1) (allow default) (deny network*)";
const KEY_NAME: &str = "AZDAJA_SOLO_TRANSPORT_SYNTHETIC";
const SYNTHETIC: &str = "synthetic-not-a-provider-credential";
#[cfg(feature = "typesafe")]
const QUESTION: &str =
    "{'q':{'type':'noul','instructions':'Does the supplied text describe an observation?'}}";

fn assert_network_is_denied() {
    static VERIFIED: OnceLock<()> = OnceLock::new();
    VERIFIED.get_or_init(|| {
        let output = Command::new("/usr/bin/sandbox-exec")
            .args([
                "-p",
                PROFILE,
                "/usr/bin/python3",
                "-c",
                r#"
import errno, socket
for kind in (socket.SOCK_STREAM, socket.SOCK_DGRAM):
    try:
        s = socket.socket(socket.AF_INET, kind)
        s.settimeout(1)
        if kind == socket.SOCK_STREAM:
            s.connect(('127.0.0.1', 9))
        else:
            s.sendto(b'network-denial-canary', ('127.0.0.1', 9))
    except OSError as error:
        assert error.errno == errno.EPERM, repr(error)
    else:
        raise AssertionError('OS network denial was not enforced')
print('tcp-and-udp-denied')
"#,
            ])
            .env_clear()
            .env("PATH", "/usr/bin:/bin")
            .output()
            .unwrap();
        assert!(
            output.status.success(),
            "network-denial admission failed: {:?}",
            output
        );
        assert_eq!(
            String::from_utf8_lossy(&output.stdout).trim(),
            "tcp-and-udp-denied"
        );
    });
}

struct Case {
    root: PathBuf,
}
impl Case {
    fn new() -> Self {
        assert_network_is_denied(); // Must pass before any typed-call program is admitted.
        static NEXT: AtomicUsize = AtomicUsize::new(0);
        let base = std::env::var_os("JCODE_SCRATCH_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(std::env::temp_dir);
        let root = base.join(format!(
            "az-solo-denial-{}-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&root).unwrap();
        fs::set_permissions(&root, fs::Permissions::from_mode(0o700)).unwrap();
        fs::write(root.join("source.txt"), "One public observation.\n").unwrap();
        fs::write(
            root.join("provider.py"),
            r#"import os, pathlib, sys
prompt = sys.stdin.buffer.read()
root = pathlib.Path(__file__).parent
assert 'AZDAJA_SOLO_TRANSPORT_SYNTHETIC' not in os.environ, 'typed credential reached generator'
# Feature-off classification preserves the legacy three strategy probes before
# root execution. These are local fixture calls, not semantic evidence.
if b'Choose only the root strategy, never answer the task. Reply with exactly DELEGATE or DETERMINISTIC.' in prompt:
    assert os.environ.get('RLM_DEPTH') != '0'
    roles = [b'Neutral audit.', b'Act as a delegation advocate,', b'Act as a deterministic-computation advocate,']
    matches = [i for i, role in enumerate(roles) if role in prompt]
    assert len(matches) == 1, 'unknown planner probe'
    with (root / ('planner-' + str(matches[0]))).open('x') as marker:
        marker.write('local strategy probe')
    print('DELEGATE')
    sys.exit(0)
kind = 'root' if os.environ.get('RLM_DEPTH') == '0' else 'child'
p = root / (kind + '.count')
p.write_text(str((int(p.read_text()) if p.exists() else 0) + 1))
assert kind == 'root', 'unexpected generative child'
print('```python\n' + (root / 'program.py').read_text() + '\n```')
"#,
        )
        .unwrap();
        Self { root }
    }
    fn run(&self, enabled: bool, question: &str, code: &str) -> Output {
        fs::write(self.root.join("program.py"), code).unwrap();
        let provider = format!(
            "/usr/bin/python3 {}",
            shlex::try_quote(self.root.join("provider.py").to_str().unwrap()).unwrap()
        );
        let cfg = format!(
            "sub_llm_cmd = {}\ncell_timeout = 10\nsub_timeout = 10\n[judge]\nenabled = {enabled}\nkey_env = \"{KEY_NAME}\"\ntimeout_secs = 2\n",
            serde_json::to_string(&provider).unwrap()
        );
        fs::write(self.root.join("config.toml"), cfg).unwrap();
        Command::new("/usr/bin/sandbox-exec")
            .args(["-p", PROFILE])
            .arg(env!("CARGO_BIN_EXE_azdaja"))
            .args(["solo", question, "-f"])
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
            .env(KEY_NAME, SYNTHETIC)
            .output()
            .unwrap()
    }
    fn count(&self, kind: &str) -> usize {
        fs::read_to_string(self.root.join(format!("{kind}.count")))
            .map(|s| s.parse().unwrap())
            .unwrap_or(0)
    }
    fn planner_probes(&self) -> usize {
        fs::read_dir(&self.root)
            .unwrap()
            .filter(|entry| {
                entry
                    .as_ref()
                    .unwrap()
                    .file_name()
                    .to_string_lossy()
                    .starts_with("planner-")
            })
            .count()
    }
    fn runtime(&self) -> serde_json::Value {
        fs::read_to_string(self.root.join("solo.trace"))
            .unwrap()
            .lines()
            .filter_map(|s| serde_json::from_str::<serde_json::Value>(s).ok())
            .find(|v| v["event"] == "solo_runtime")
            .expect("actual public runtime footer")
    }
    fn assert_no_secret(&self, output: &Output) {
        for bytes in [&output.stdout, &output.stderr] {
            assert!(!String::from_utf8_lossy(bytes).contains(SYNTHETIC));
        }
        for name in ["solo.trace", "model.jsonl"] {
            if let Ok(text) = fs::read_to_string(self.root.join(name)) {
                assert!(!text.contains(SYNTHETIC));
            }
        }
    }
}
impl Drop for Case {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.root);
    }
}

#[test]
fn disabled_solo_stats_stay_off_despite_a_present_synthetic_credential() {
    let case = Case::new();
    let output = case.run(false, "Return the setup status.", "FINAL(judge_stats())");
    assert!(output.status.success(), "{:?}", output);
    let value: serde_json::Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(value["enabled"], false);
    assert_eq!(value["attempts"], 0);
    assert_eq!(case.count("root"), 1);
    assert_eq!(case.count("child"), 0);
    assert_eq!(case.planner_probes(), 0);
    case.assert_no_secret(&output);
}

#[test]
fn model_mutated_stats_cannot_forge_semantic_evidence() {
    let case = Case::new();
    let output = case.run(
        true,
        "Classify this source and return a count.",
        "s = judge_stats()\ns['successful_requests'] = 99\ns['attempts'] = 99\nFINAL(1)",
    );
    assert!(!output.status.success(), "{:?}", output);
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("semantic_call_count=0"),
        "{:?}\ntrace={}",
        output,
        fs::read_to_string(case.root.join("solo.trace")).unwrap_or_default()
    );
    assert_eq!(case.count("root"), 4);
    assert_eq!(case.count("child"), 0);
    assert_eq!(
        case.planner_probes(),
        if cfg!(feature = "typesafe") { 0 } else { 3 }
    );
    let runtime = case.runtime();
    assert_eq!(runtime["outcome"], "failed");
    let cells = runtime["judge_cells"].as_array().unwrap();
    assert_eq!(cells.len(), 4);
    for cell in cells {
        assert_eq!(cell["attempts"], 0);
        assert_eq!(cell["successful_requests"], 0);
    }
    case.assert_no_secret(&output);
}

#[cfg(feature = "typesafe")]
#[test]
fn actual_transport_failure_is_retained_and_never_automatically_repaired() {
    for caught in [false, true] {
        let case = Case::new();
        let call = format!("judge_many(ctx, {QUESTION})");
        let code = if caught {
            format!("try:\n    {call}\nexcept Exception:\n    pass\nFINAL(1)")
        } else {
            format!("{call}\nFINAL(1)")
        };
        let output = case.run(true, "Classify this source and return a count.", &code);
        assert!(!output.status.success(), "caught={caught} {:?}", output);
        assert!(output.stdout.is_empty());
        let error = String::from_utf8_lossy(&output.stderr);
        assert!(
            error.contains(if caught {
                "semantic_call_count=0"
            } else {
                "judge: transport failed"
            }),
            "{error}"
        );
        assert_eq!(case.count("root"), 1, "no repair after transport attempt");
        assert_eq!(case.count("child"), 0);
        assert_eq!(case.planner_probes(), 0);
        assert_failed_attempt(&case.runtime());
        case.assert_no_secret(&output);
    }
}

#[cfg(feature = "typesafe")]
#[test]
fn catching_transport_failure_does_not_allow_a_second_attempt_in_the_cell() {
    let case = Case::new();
    let code = format!(
        "for ignored in range(2):\n    try:\n        judge_many(ctx, {QUESTION})\n    except Exception:\n        pass\nFINAL(1)"
    );
    let output = case.run(true, "Classify this source and return a count.", &code);
    assert!(!output.status.success());
    assert!(String::from_utf8_lossy(&output.stderr).contains("semantic_call_count=0"));
    assert_eq!(case.count("root"), 1);
    assert_eq!(case.count("child"), 0);
    assert_eq!(case.planner_probes(), 0);
    assert_failed_attempt(&case.runtime());
    case.assert_no_secret(&output);
}

#[cfg(feature = "typesafe")]
fn assert_failed_attempt(runtime: &serde_json::Value) {
    assert_eq!(runtime["outcome"], "failed");
    assert_eq!(runtime["exec_invocation_count"], 1);
    assert_eq!(runtime["semantic_call_count"], 0);
    let cells = runtime["judge_cells"].as_array().unwrap();
    assert_eq!(cells.len(), 1);
    let cell = &cells[0];
    for key in [
        "attempts",
        "provider_requests",
        "questions",
        "failed_attempts",
        "unknown_input_usage_requests",
        "unknown_output_usage_requests",
    ] {
        assert_eq!(cell[key], 1, "{key}");
    }
    for key in [
        "successful_requests",
        "known_input_tokens",
        "known_output_tokens",
        "cache_hits",
        "cached_requests",
    ] {
        assert_eq!(cell[key], 0, "{key}");
    }
    assert_eq!(cell["poisoned"], true);
    assert_eq!(cell["input_usage_complete"], false);
    assert_eq!(cell["output_usage_complete"], false);
    assert!(cell["total_wall_ns"].as_u64().unwrap() > 0);
}
