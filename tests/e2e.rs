use std::{
    fs,
    io::Write,
    path::{Path, PathBuf},
    process::{Command, Output, Stdio},
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

fn temp(name: &str) -> PathBuf {
    let n = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let p = std::env::temp_dir().join(format!("azdaja-{name}-{}-{n}", std::process::id()));
    fs::create_dir_all(&p).unwrap();
    p
}
fn fnv(bytes: &[u8]) -> u64 {
    let mut h = 0xcbf29ce484222325u64;
    for b in bytes {
        h ^= u64::from(*b);
        h = h.wrapping_mul(0x100000001b3)
    }
    h
}
fn config(dir: &Path, cmd: &str, cap: usize, depth: u32, timeout: u64, max: usize) -> PathBuf {
    let p = dir.join("config.toml");
    fs::write(
        &p,
        format!(
            r#"sub_llm_cmd = {cmd:?}
default_model = "mock"
output_cap = {cap}
max_depth = {depth}
sub_timeout = {timeout}
max_sessions = {max}
cell_timeout = 2
idle_timeout = 1800
clean_patterns = []
jcode_provider = "openai"
jcode_reasoning = "medium"
max_calls_per_cell = 64
"#
        ),
    )
    .unwrap();
    p
}
fn run(home: &Path, cfg: &Path, args: &[&str], input: &str) -> Output {
    let mut c = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    c.env_remove("RLM_DEPTH")
        .args(args)
        .env("AZDAJA_HOME", home.join("state"))
        .env("AZDAJA_CONFIG", cfg)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = c.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(input.as_bytes())
        .unwrap();
    child.wait_with_output().unwrap()
}
fn ok(o: Output) -> String {
    assert!(
        o.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&o.stderr),
        String::from_utf8_lossy(&o.stdout)
    );
    String::from_utf8(o.stdout).unwrap()
}
fn sid(home: &Path, cfg: &Path) -> String {
    ok(run(home, cfg, &["start"], "")).trim().into()
}

// Local scripted transport only: these synthetic classes are unrelated to benchmark gold, and
// every semantic response is produced by the temporary Python oracle without inference/network I/O.
fn write_semantic_metamorphic_oracle(dir: &Path) -> (PathBuf, PathBuf) {
    let logs = dir.join("semantic-logs");
    fs::create_dir(&logs).unwrap();
    let script = dir.join("semantic-oracle.py");
    fs::write(
        &script,
        r#"import json, os, pathlib, re, sys

logs = pathlib.Path(sys.argv[1])
prompt = sys.stdin.read()
cases = (
    "id-original", "id-renamed", "records-forward", "records-reversed",
    "labels-forward", "labels-reversed", "evidence-plain", "evidence-noisy",
    "duplicates-one", "duplicates-three",
)
case = [name for name in cases if ("metamorphic/" + name) in prompt]
assert len(case) == 1, case
case = case[0]

root_code = {
    "id-original": '''items=[{"id":"caller-left","evidence":"semantic-alpha review-me"},{"id":"caller-right","evidence":"semantic-beta stable"}]
labels=semantic_manifest(items,"synthetic scripted-oracle framing",["class-a","class-b"])
FINAL(labels["caller-left"]+":"+labels["caller-right"])''',
    "id-renamed": '''items=[{"id":"renamed-red","evidence":"semantic-alpha review-me"},{"id":"renamed-blue","evidence":"semantic-beta stable"}]
labels=semantic_manifest(items,"synthetic scripted-oracle framing",["class-a","class-b"])
FINAL(labels["renamed-red"]+":"+labels["renamed-blue"])''',
    "records-forward": '''items=[{"id":"forward-alpha-0","evidence":"semantic-alpha review-me"},{"id":"forward-alpha-1","evidence":"semantic-alpha review-me"},{"id":"forward-beta-0","evidence":"semantic-beta stable"}]
labels=semantic_manifest(items,"synthetic scripted-oracle framing",["class-a","class-b"])
counts={"class-a":0,"class-b":0}
for item in items:
    counts[labels[item["id"]]]+=1
FINAL(str(counts["class-a"])+":"+str(counts["class-b"]))''',
    "records-reversed": '''items=[{"id":"forward-beta-0","evidence":"semantic-beta stable"},{"id":"forward-alpha-1","evidence":"semantic-alpha review-me"},{"id":"forward-alpha-0","evidence":"semantic-alpha review-me"}]
labels=semantic_manifest(items,"synthetic scripted-oracle framing",["class-a","class-b"])
counts={"class-a":0,"class-b":0}
for item in items:
    counts[labels[item["id"]]]+=1
FINAL(str(counts["class-a"])+":"+str(counts["class-b"]))''',
    "labels-forward": '''items=[{"id":"label-alpha","evidence":"semantic-alpha review-me"},{"id":"label-beta","evidence":"semantic-beta stable"}]
labels=semantic_manifest(items,"synthetic scripted-oracle framing",["class-a","class-b"])
FINAL(labels["label-alpha"]+":"+labels["label-beta"])''',
    "labels-reversed": '''items=[{"id":"label-alpha","evidence":"semantic-alpha review-me"},{"id":"label-beta","evidence":"semantic-beta stable"}]
labels=semantic_manifest(items,"synthetic scripted-oracle framing",["class-b","class-a"])
FINAL(labels["label-alpha"]+":"+labels["label-beta"])''',
    "evidence-plain": '''items=[{"id":"plain-alpha","evidence":"semantic-alpha review-me"},{"id":"plain-beta","evidence":"semantic-beta stable"}]
labels=semantic_manifest(items,"synthetic scripted-oracle framing",["class-a","class-b"])
FINAL(labels["plain-alpha"]+":"+labels["plain-beta"])''',
    "evidence-noisy": '''items=[{"id":"noisy-alpha","evidence":"meta=semantic-beta semantic-alpha   review-me\\nmeta=trace-77"},{"id":"noisy-beta","evidence":"meta=noop\\nsemantic-beta\\tstable meta=semantic-alpha"}]
labels=semantic_manifest(items,"synthetic scripted-oracle framing",["class-a","class-b"])
FINAL(labels["noisy-alpha"]+":"+labels["noisy-beta"])''',
    "duplicates-one": '''items=[{"id":"occ-alpha-0","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-1","evidence":"semantic-alpha review-me"},{"id":"occ-beta-0","evidence":"semantic-beta stable"}]
labels=semantic_manifest(items,"synthetic scripted-oracle framing",["class-a","class-b"])
counts={"class-a":0,"class-b":0}
expanded=[]
for item in items:
    value=labels[item["id"]]
    counts[value]+=1
    expanded.append(item["id"]+"="+value)
FINAL(str(len(labels))+":"+str(counts["class-a"])+":"+str(counts["class-b"])+"|"+",".join(expanded))''',
    "duplicates-three": '''items=[{"id":"occ-alpha-0","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-1","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-2","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-3","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-4","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-5","evidence":"semantic-alpha review-me"},{"id":"occ-beta-0","evidence":"semantic-beta stable"},{"id":"occ-beta-1","evidence":"semantic-beta stable"},{"id":"occ-beta-2","evidence":"semantic-beta stable"}]
labels=semantic_manifest(items,"synthetic scripted-oracle framing",["class-a","class-b"])
counts={"class-a":0,"class-b":0}
expanded=[]
for item in items:
    value=labels[item["id"]]
    counts[value]+=1
    expanded.append(item["id"]+"="+value)
FINAL(str(len(labels))+":"+str(counts["class-a"])+":"+str(counts["class-b"])+"|"+",".join(expanded))''',
}

if os.getenv("RLM_DEPTH") == "0":
    print("```python\n" + root_code[case] + "\n```")
    raise SystemExit(0)

if "annotator A" in prompt:
    role = "a"
elif "annotator B" in prompt:
    role = "b"
elif "final blind source-annotation adjudicator" in prompt:
    role = "j"
else:
    raise AssertionError("unexpected semantic prompt")
allowed_match = re.search(r"^Allowed labels: (.+)$", prompt, re.MULTILINE)
assert allowed_match is not None
allowed = allowed_match.group(1).split(", ")
assert set(allowed) == {"class-a", "class-b"}
rows = []
for line in prompt.splitlines():
    if re.match(r"^R[0-9]{8} \|\| ", line):
        rid, evidence = line.split(" || ", 1)
        rows.append([rid, evidence])
assert rows

def canonical_label(evidence):
    without_metadata = re.sub(r"\bmeta=[^ ]+", "", evidence)
    semantic = " ".join(without_metadata.split())
    has_alpha = "semantic-alpha" in semantic
    has_beta = "semantic-beta" in semantic
    assert has_alpha != has_beta, semantic
    return "class-a" if has_alpha else "class-b"

manifest = []
for rid, evidence in rows:
    label = canonical_label(evidence)
    if role == "b" and label == "class-a":
        label = "class-b"  # Script one blind disagreement; the judge must see only its wire ID.
    manifest.append([rid, label])
record = {"allowed": allowed, "manifest": manifest, "prompt": prompt, "rows": rows}
path = logs / (case + "-" + role + ".json")
assert not path.exists(), "unexpected retry or duplicate semantic call"
path.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
print("\n".join(rid + "|" + label for rid, label in manifest))
"#,
    )
    .unwrap();
    (script, logs)
}

fn semantic_metamorphic_config(dir: &Path, script: &Path, logs: &Path) -> PathBuf {
    let cfg = config(
        dir,
        &format!("python3 {} {}", script.display(), logs.display()),
        4096,
        1,
        3,
        4,
    );
    let text = fs::read_to_string(&cfg)
        .unwrap()
        .replace("max_calls_per_cell = 64", "max_calls_per_cell = 5");
    fs::write(&cfg, text).unwrap();
    cfg
}

fn run_semantic_metamorphic_case(dir: &Path, cfg: &Path, case: &str) -> String {
    let input = dir.join(format!("{case}.txt"));
    fs::write(&input, "synthetic schema; no benchmark rows or gold").unwrap();
    let question = format!("metamorphic/{case}");
    let output = run(
        dir,
        cfg,
        &["solo", &question, "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "case={case} stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

fn semantic_log(logs: &Path, case: &str, role: &str) -> serde_json::Value {
    serde_json::from_slice(&fs::read(logs.join(format!("{case}-{role}.json"))).unwrap()).unwrap()
}

fn string_pairs(value: &serde_json::Value, key: &str) -> Vec<Vec<String>> {
    serde_json::from_value(value[key].clone()).unwrap()
}

fn string_list(value: &serde_json::Value, key: &str) -> Vec<String> {
    serde_json::from_value(value[key].clone()).unwrap()
}

fn assert_exact_semantic_trace(
    logs: &Path,
    case: &str,
    rows: &[(&str, &str)],
    caller_labels: &[&str],
    forbidden_caller_ids: &[&str],
) {
    let mut call_roles = fs::read_dir(logs)
        .unwrap()
        .filter_map(Result::ok)
        .filter_map(|entry| entry.file_name().into_string().ok())
        .filter(|name| name.starts_with(&format!("{case}-")))
        .collect::<Vec<_>>();
    call_roles.sort();
    assert_eq!(
        call_roles,
        [
            format!("{case}-a.json"),
            format!("{case}-b.json"),
            format!("{case}-j.json")
        ],
        "exact child-call budget is two blind manifests plus one adjudication"
    );

    let a = semantic_log(logs, case, "a");
    let b = semantic_log(logs, case, "b");
    let j = semantic_log(logs, case, "j");
    let expected_a = rows
        .iter()
        .map(|(rid, evidence)| vec![(*rid).to_string(), (*evidence).to_string()])
        .collect::<Vec<_>>();
    let scripted_class_is_a = |evidence: &str| {
        evidence
            .split_whitespace()
            .filter(|word| !word.starts_with("meta="))
            .any(|word| word == "semantic-alpha")
    };
    let expected_a_manifest = rows
        .iter()
        .map(|(rid, evidence)| {
            vec![
                (*rid).to_string(),
                if scripted_class_is_a(evidence) {
                    "class-a".to_string()
                } else {
                    "class-b".to_string()
                },
            ]
        })
        .collect::<Vec<_>>();
    let mut expected_b = expected_a.clone();
    expected_b.reverse();
    let expected_b_manifest = expected_b
        .iter()
        .map(|row| vec![row[0].clone(), "class-b".to_string()])
        .collect::<Vec<_>>();
    let expected_j = expected_a
        .iter()
        .filter(|row| scripted_class_is_a(&row[1]))
        .cloned()
        .collect::<Vec<_>>();
    let expected_j_manifest = expected_j
        .iter()
        .map(|row| vec![row[0].clone(), "class-a".to_string()])
        .collect::<Vec<_>>();

    assert_eq!(string_pairs(&a, "rows"), expected_a);
    assert_eq!(string_pairs(&a, "manifest"), expected_a_manifest);
    assert_eq!(string_list(&a, "allowed"), caller_labels);
    assert_eq!(string_pairs(&b, "rows"), expected_b);
    assert_eq!(string_pairs(&b, "manifest"), expected_b_manifest);
    assert_eq!(
        string_list(&b, "allowed"),
        caller_labels.iter().rev().copied().collect::<Vec<_>>()
    );
    assert_eq!(string_pairs(&j, "rows"), expected_j);
    assert_eq!(string_pairs(&j, "manifest"), expected_j_manifest);
    assert_eq!(string_list(&j, "allowed"), caller_labels);
    for call in [&a, &b, &j] {
        let prompt = call["prompt"].as_str().unwrap();
        for caller_id in forbidden_caller_ids {
            assert!(
                !prompt.contains(caller_id),
                "caller ID leaked into provider manifest: {caller_id}"
            );
        }
    }
}

#[test]
fn lifecycle_is_persistent_and_load_is_metadata_only() {
    let t = temp("life");
    let cfg = config(&t, "cat", 512, 1, 2, 4);
    let secret = "CANARY-7fa9".repeat(40);
    let input = t.join("input.txt");
    fs::write(&input, format!("{secret}\nsecond line\n")).unwrap();
    let id = sid(&t, &cfg);
    let loaded = ok(run(
        &t,
        &cfg,
        &["load", &id, input.to_str().unwrap(), "ctx"],
        "",
    ));
    assert!(loaded.contains("loaded 'ctx' : str"));
    assert!(!loaded.contains("CANARY-7fa9"));
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        assert_eq!(
            fs::metadata(t.join("state").join(&id).join("state.monty"))
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o600
        );
    }
    assert_eq!(ok(run(&t, &cfg, &["exec", &id], "n=len(ctx)\n")).trim(), "");
    assert_eq!(
        ok(run(&t, &cfg, &["exec", &id], "n\n")).trim(),
        (secret.len() + 13).to_string()
    );
    ok(run(
        &t,
        &cfg,
        &["exec", &id],
        "FINAL = 'assignment-compatible'\n",
    ));
    assert_eq!(
        ok(run(&t, &cfg, &["final", &id], "")).trim(),
        "assignment-compatible"
    );
    ok(run(
        &t,
        &cfg,
        &["exec", &id],
        "answer={'chars': n}\nFINAL_VAR('answer')\n",
    ));
    assert_eq!(
        ok(run(&t, &cfg, &["final", &id], "")).trim(),
        format!("{{'chars': {}}}", secret.len() + 13)
    );
    assert!(ok(run(&t, &cfg, &["list"], "")).contains(&id));
    ok(run(&t, &cfg, &["kill", &id], ""));
    assert!(!ok(run(&t, &cfg, &["list"], "")).contains(&id));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn output_cap_is_unicode_exact_and_errors_preserve_state() {
    let t = temp("cap");
    let cfg = config(&t, "cat", 256, 1, 2, 4);
    let id = sid(&t, &cfg);
    let out = ok(run(&t, &cfg, &["exec", &id], "print('λ'*100000)\n"));
    assert!(out.chars().count() <= 256);
    assert!(out.contains("chars elided"));
    assert!(out.starts_with('λ') && out.trim_end().ends_with('λ'));
    let bad = run(&t, &cfg, &["exec", &id], "x=73\n1/0\n");
    assert_eq!(bad.status.code(), Some(1));
    assert!(String::from_utf8_lossy(&bad.stdout).contains("ZeroDivisionError"));
    assert_eq!(ok(run(&t, &cfg, &["exec", &id], "x\n")).trim(), "73");
    let failed_final = run(&t, &cfg, &["exec", &id], "FINAL('wrong')\n1/0\n");
    assert_eq!(failed_final.status.code(), Some(1));
    let absent = run(&t, &cfg, &["final", &id], "");
    assert_eq!(absent.status.code(), Some(2));
    ok(run(&t, &cfg, &["exec", &id], "FINAL('λ'*10000)\n"));
    let final_out = ok(run(&t, &cfg, &["final", &id], ""));
    assert!(final_out.chars().count() <= 256 && final_out.contains("chars elided"));
    ok(run(&t, &cfg, &["kill", &id], ""));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn batch_preserves_ordered_successes_across_timeout_but_single_call_fails_closed() {
    let t = temp("partial-batch");
    let script = t.join("selective.sh");
    fs::write(
        &script,
        r#"#!/bin/sh
input=$(cat)
case "$input" in
  *timeout*) sleep 5;;
  *first*) sleep 0.2; printf FIRST_OK;;
  *third*) printf THIRD_OK;;
  *fail*) echo intentional >&2; exit 9;;
esac
"#,
    )
    .unwrap();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&script, fs::Permissions::from_mode(0o755)).unwrap();
    }
    let cfg = config(&t, script.to_str().unwrap(), 2048, 1, 1, 4);
    let id = sid(&t, &cfg);
    let started = Instant::now();
    let out = ok(run(
        &t,
        &cfg,
        &["exec", &id],
        "print(llm_batch(['first','timeout','third'],None,2))\n",
    ));
    assert!(started.elapsed() < Duration::from_secs(3));
    let first = out.find("FIRST_OK").unwrap();
    let failed = out
        .find(r#"{"azdaja_error":"provider_call_failed_retry_item""#)
        .unwrap();
    let third = out.find("THIRD_OK").unwrap();
    assert!(first < failed && failed < third, "{out}");
    assert!(out.contains("timed out after 1s"), "{out}");

    let single = run(&t, &cfg, &["exec", &id], "llm('fail')\n");
    assert_eq!(single.status.code(), Some(1));
    assert!(
        String::from_utf8_lossy(&single.stdout).contains("intentional"),
        "{}",
        String::from_utf8_lossy(&single.stdout)
    );
    ok(run(&t, &cfg, &["kill", &id], ""));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn callbacks_batch_depth_and_timeout() {
    let t = temp("callbacks");
    let cfg = config(&t, "cat", 1024, 1, 1, 4);
    let id = sid(&t, &cfg);
    let out = ok(run(
        &t,
        &cfg,
        &["exec", &id],
        "llm_batch(['first','second'], None, 2)\n",
    ));
    assert!(out.find("first").unwrap() < out.find("second").unwrap());
    let marker = t.join("spawned");
    let script = t.join("mark.sh");
    fs::write(
        &script,
        format!("#!/bin/sh\ntouch {}\ncat\n", marker.display()),
    )
    .unwrap();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&script, fs::Permissions::from_mode(0o755)).unwrap();
    }
    let cfg2 = config(&t, script.to_str().unwrap(), 1024, 1, 1, 4);
    let mut c = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    let mut depth = c
        .args(["exec", &id])
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg2)
        .env("RLM_DEPTH", "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    depth
        .stdin
        .take()
        .unwrap()
        .write_all(b"llm('no')\n")
        .unwrap();
    let o = depth.wait_with_output().unwrap();
    assert_eq!(o.status.code(), Some(1));
    assert!(!marker.exists());
    let orphan = t.join("orphan");
    let sleeper = t.join("sleeper.sh");
    fs::write(
        &sleeper,
        format!("(sleep 2; touch {}) &\nsleep 5\n", orphan.display()),
    )
    .unwrap();
    let slow = config(&t, &format!("sh {}", sleeper.display()), 1024, 1, 1, 4);
    let started = Instant::now();
    let o = run(&t, &slow, &["exec", &id], "llm('x')\n");
    assert_eq!(o.status.code(), Some(1));
    assert!(started.elapsed() < Duration::from_secs(3));
    assert!(String::from_utf8_lossy(&o.stdout).contains("timed out"));
    std::thread::sleep(Duration::from_millis(2200));
    assert!(!orphan.exists(), "timed-out descendant survived");
    ok(run(&t, &cfg, &["kill", &id], ""));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn prompt_file_beats_arg_max_and_model_is_one_argument() {
    let t = temp("prompt");
    let mock = t.join("mock.py");
    fs::write(
        &mock,
        r#"import sys,stat,os
p=sys.argv[2]
data=open(p,'rb').read(); stdin=sys.stdin.buffer.read(); h=0xcbf29ce484222325
for b in data: h=((h^b)*0x100000001b3)&0xffffffffffffffff
print(f'argc={len(sys.argv)} model={sys.argv[1]} bytes={len(data)} fnv={h:016x} mode={stat.S_IMODE(os.stat(p).st_mode):o} stdin={len(stdin)}')
"#,
    )
    .unwrap();
    let cmd = format!("python3 {} {{model}} {{prompt_file}}", mock.display());
    let cfg = config(&t, &cmd, 1024, 1, 5, 4);
    let big = t.join("big.txt");
    fs::write(&big, "x".repeat(1_100_000)).unwrap();
    let id = sid(&t, &cfg);
    ok(run(
        &t,
        &cfg,
        &["load", &id, big.to_str().unwrap(), "ctx"],
        "",
    ));
    let out = ok(run(
        &t,
        &cfg,
        &["exec", &id],
        "llm(ctx, model='safe --not-an-option')\n",
    ));
    let wire = format!(
        "[azdaja recursion depth 1/1: do not invoke azdaja recursively.]\n\n{}",
        "x".repeat(1_100_000)
    );
    assert!(out.contains("argc=3 model=safe --not-an-option"), "{out}");
    assert!(
        out.contains(&format!(
            "bytes={} fnv={:016x} mode=600 stdin=0",
            wire.len(),
            fnv(wire.as_bytes())
        )),
        "{out}"
    );
    assert_eq!(fs::read_dir(t.join("state/prompts")).unwrap().count(), 0);
    ok(run(&t, &cfg, &["kill", &id], ""));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn sandbox_and_path_validation_fail_closed() {
    let t = temp("safe");
    let cfg = config(&t, "cat", 1024, 1, 2, 4);
    let id = sid(&t, &cfg);
    let o = run(&t, &cfg, &["exec", &id], "open('/etc/passwd').read()\n");
    assert_eq!(o.status.code(), Some(1));
    let s = String::from_utf8_lossy(&o.stdout);
    assert!(s.contains("OS access is disabled"));
    assert!(!s.contains("root:"));
    for code in [
        "os.getenv('HOME')\n",
        "import subprocess\n",
        "import socket\n",
    ] {
        let denied = run(&t, &cfg, &["exec", &id], code);
        assert_eq!(denied.status.code(), Some(1), "{code}");
    }
    let timeout_cfg = t.join("timeout.toml");
    fs::write(
        &timeout_cfg,
        fs::read_to_string(&cfg)
            .unwrap()
            .replace("cell_timeout = 2", "cell_timeout = 1"),
    )
    .unwrap();
    let began = Instant::now();
    let spin = run(&t, &timeout_cfg, &["exec", &id], "while True:\n    pass\n");
    assert_eq!(spin.status.code(), Some(1));
    assert!(began.elapsed() < Duration::from_secs(3));
    assert!(String::from_utf8_lossy(&spin.stdout).contains("time limit exceeded"));
    let o = run(&t, &cfg, &["final", "../escape"], "");
    assert!(!o.status.success());
    assert!(String::from_utf8_lossy(&o.stderr).contains("invalid session id"));
    #[cfg(unix)]
    {
        std::os::unix::fs::symlink("/tmp", t.join("state/0000000000000000")).unwrap();
        let o = run(&t, &cfg, &["final", "0000000000000000"], "");
        assert!(!o.status.success());
        assert!(String::from_utf8_lossy(&o.stderr).contains("unsafe session path"));
    }
    ok(run(&t, &cfg, &["kill", &id], ""));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn concurrent_starts_respect_limit() {
    let t = temp("limit");
    let cfg = config(&t, "cat", 512, 1, 2, 4);
    let mut children = Vec::new();
    for _ in 0..8 {
        children.push(
            Command::new(env!("CARGO_BIN_EXE_azdaja"))
                .env_remove("RLM_DEPTH")
                .arg("start")
                .env("AZDAJA_HOME", t.join("state"))
                .env("AZDAJA_CONFIG", &cfg)
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn()
                .unwrap(),
        )
    }
    let mut ids = Vec::new();
    for c in children {
        let o = c.wait_with_output().unwrap();
        if o.status.success() {
            ids.push(String::from_utf8(o.stdout).unwrap().trim().to_string())
        }
    }
    assert_eq!(ids.len(), 4);
    for id in ids {
        ok(run(&t, &cfg, &["kill", &id], ""));
    }
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_fixed_manifest_prelude_owns_dual_provider_plumbing() {
    let t = temp("solo-manifest");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        r#"import os,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{"id":"R1","evidence":"ordinary note"},{"id":"R2","evidence":"ambiguous service"}]\nlabels=semantic_manifest(items,"binary annotation",["ham","spam"])\nFINAL(labels["R1"]+":"+labels["R2"])\n```')
else:
    print('R00000000|ham\nR00000001|spam')
"#,
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "schema row").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "binary annotation", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "ham:spam");
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_dual_manifest_blindly_adjudicates_every_disagreement() {
    let t = temp("solo-dual-adjudicate");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        r#"import os,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{"id":"x","evidence":"first raw"},{"id":"y","evidence":"second raw"}]\nlabels=semantic_manifest(items,"official binary task",["ham","spam"])\nFINAL(labels["x"]+":"+labels["y"])\n```')
elif 'annotator A' in p:
    print('R00000000|ham\nR00000001|ham')
elif 'annotator B' in p:
    assert 'Allowed labels: spam, ham' in p
    print('R00000000|ham\nR00000001|spam')
elif 'final blind source-annotation adjudicator' in p:
    assert 'R00000001 || second raw' in p
    assert 'R00000000 || first raw' not in p
    assert 'annotator A' not in p and 'annotator B' not in p
    print('R00000001|spam')
else:
    raise SystemExit('unexpected prompt')
"#,
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "schema row").unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "official binary task",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
    );
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "ham:spam");
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_is_invariant_to_caller_item_id_renaming() {
    let t = temp("semantic-id-metamorphism");
    let (script, logs) = write_semantic_metamorphic_oracle(&t);
    let cfg = semantic_metamorphic_config(&t, &script, &logs);
    let original = run_semantic_metamorphic_case(&t, &cfg, "id-original");
    let renamed = run_semantic_metamorphic_case(&t, &cfg, "id-renamed");
    assert_eq!(original, "class-a:class-b");
    assert_eq!(renamed, original);
    let rows = [
        ("R00000000", "semantic-alpha review-me"),
        ("R00000001", "semantic-beta stable"),
    ];
    assert_exact_semantic_trace(
        &logs,
        "id-original",
        &rows,
        &["class-a", "class-b"],
        &["caller-left", "caller-right"],
    );
    assert_exact_semantic_trace(
        &logs,
        "id-renamed",
        &rows,
        &["class-a", "class-b"],
        &["renamed-red", "renamed-blue"],
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "id-original", "a"), "manifest"),
        string_pairs(&semantic_log(&logs, "id-renamed", "a"), "manifest")
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "id-original", "j"), "rows"),
        vec![vec![
            "R00000000".to_string(),
            "semantic-alpha review-me".to_string()
        ]]
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_reversal_preserves_order_invariant_reduction() {
    let t = temp("semantic-order-metamorphism");
    let (script, logs) = write_semantic_metamorphic_oracle(&t);
    let cfg = semantic_metamorphic_config(&t, &script, &logs);
    let forward = run_semantic_metamorphic_case(&t, &cfg, "records-forward");
    let reversed = run_semantic_metamorphic_case(&t, &cfg, "records-reversed");
    assert_eq!(forward, "2:1");
    assert_eq!(reversed, forward);
    assert_exact_semantic_trace(
        &logs,
        "records-forward",
        &[
            ("R00000000", "semantic-alpha review-me"),
            ("R00000001", "semantic-beta stable"),
        ],
        &["class-a", "class-b"],
        &["forward-alpha-0", "forward-alpha-1", "forward-beta-0"],
    );
    assert_exact_semantic_trace(
        &logs,
        "records-reversed",
        &[
            ("R00000000", "semantic-beta stable"),
            ("R00000001", "semantic-alpha review-me"),
        ],
        &["class-a", "class-b"],
        &["forward-alpha-0", "forward-alpha-1", "forward-beta-0"],
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "records-forward", "j"), "manifest"),
        vec![vec!["R00000000".to_string(), "class-a".to_string()]]
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "records-reversed", "j"), "manifest"),
        vec![vec!["R00000001".to_string(), "class-a".to_string()]]
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_is_invariant_to_caller_allowed_label_order() {
    let t = temp("semantic-label-metamorphism");
    let (script, logs) = write_semantic_metamorphic_oracle(&t);
    let cfg = semantic_metamorphic_config(&t, &script, &logs);
    let forward = run_semantic_metamorphic_case(&t, &cfg, "labels-forward");
    let reversed = run_semantic_metamorphic_case(&t, &cfg, "labels-reversed");
    assert_eq!(forward, "class-a:class-b");
    assert_eq!(reversed, forward);
    let rows = [
        ("R00000000", "semantic-alpha review-me"),
        ("R00000001", "semantic-beta stable"),
    ];
    assert_exact_semantic_trace(
        &logs,
        "labels-forward",
        &rows,
        &["class-a", "class-b"],
        &["label-alpha", "label-beta"],
    );
    assert_exact_semantic_trace(
        &logs,
        "labels-reversed",
        &rows,
        &["class-b", "class-a"],
        &["label-alpha", "label-beta"],
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "labels-forward", "j"), "manifest"),
        string_pairs(&semantic_log(&logs, "labels-reversed", "j"), "manifest")
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_scripted_oracle_ignores_harmless_metadata_and_whitespace() {
    let t = temp("semantic-evidence-metamorphism");
    let (script, logs) = write_semantic_metamorphic_oracle(&t);
    let cfg = semantic_metamorphic_config(&t, &script, &logs);
    let plain = run_semantic_metamorphic_case(&t, &cfg, "evidence-plain");
    let noisy = run_semantic_metamorphic_case(&t, &cfg, "evidence-noisy");
    assert_eq!(plain, "class-a:class-b");
    assert_eq!(noisy, plain);
    assert_exact_semantic_trace(
        &logs,
        "evidence-plain",
        &[
            ("R00000000", "semantic-alpha review-me"),
            ("R00000001", "semantic-beta stable"),
        ],
        &["class-a", "class-b"],
        &["plain-alpha", "plain-beta"],
    );
    assert_exact_semantic_trace(
        &logs,
        "evidence-noisy",
        &[
            (
                "R00000000",
                "meta=semantic-beta semantic-alpha   review-me meta=trace-77",
            ),
            (
                "R00000001",
                "meta=noop semantic-beta\tstable meta=semantic-alpha",
            ),
        ],
        &["class-a", "class-b"],
        &["noisy-alpha", "noisy-beta"],
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "evidence-plain", "j"), "manifest"),
        string_pairs(&semantic_log(&logs, "evidence-noisy", "j"), "manifest")
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_scales_duplicate_multiplicity_and_expands_every_occurrence() {
    let t = temp("semantic-duplicate-metamorphism");
    let (script, logs) = write_semantic_metamorphic_oracle(&t);
    let cfg = semantic_metamorphic_config(&t, &script, &logs);
    let one = run_semantic_metamorphic_case(&t, &cfg, "duplicates-one");
    let three = run_semantic_metamorphic_case(&t, &cfg, "duplicates-three");
    assert_eq!(
        one,
        "3:2:1|occ-alpha-0=class-a,occ-alpha-1=class-a,occ-beta-0=class-b"
    );
    assert_eq!(
        three,
        "9:6:3|occ-alpha-0=class-a,occ-alpha-1=class-a,occ-alpha-2=class-a,occ-alpha-3=class-a,occ-alpha-4=class-a,occ-alpha-5=class-a,occ-beta-0=class-b,occ-beta-1=class-b,occ-beta-2=class-b"
    );
    let unique_rows = [
        ("R00000000", "semantic-alpha review-me"),
        ("R00000001", "semantic-beta stable"),
    ];
    assert_exact_semantic_trace(
        &logs,
        "duplicates-one",
        &unique_rows,
        &["class-a", "class-b"],
        &["occ-alpha-0", "occ-alpha-1", "occ-beta-0"],
    );
    assert_exact_semantic_trace(
        &logs,
        "duplicates-three",
        &unique_rows,
        &["class-a", "class-b"],
        &[
            "occ-alpha-0",
            "occ-alpha-1",
            "occ-alpha-2",
            "occ-alpha-3",
            "occ-alpha-4",
            "occ-alpha-5",
            "occ-beta-0",
            "occ-beta-1",
            "occ-beta-2",
        ],
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "duplicates-one", "a"), "manifest"),
        string_pairs(&semantic_log(&logs, "duplicates-three", "a"), "manifest")
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_normalizes_integer_ids_and_singleton_labels_without_child_call() {
    let t = temp("solo-manifest-ids");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        r#"import os,sys
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{"id":7,"evidence":"one"},{"id":8,"evidence":"one"}]\nlabels=semantic_manifest(items,"deterministic inclusion",["include","include"])\nFINAL(str(labels[7])+":"+str(labels[8]))\n```')
else:
    print('UNEXPECTED_CHILD_CALL')
"#,
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "schema row").unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "deterministic inclusion",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
    );
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(
        String::from_utf8_lossy(&output.stdout).trim(),
        "include:include"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_dual_manifest_retries_only_malformed_primary_shard() {
    let t = temp("solo-dual-contract-retry");
    let a_seen = t.join("a-seen");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import os,sys,pathlib
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{{"id":"x","evidence":"raw"}}]\nlabels=semantic_manifest(items,"official binary task",["ham","spam"])\nFINAL(labels["x"])\n```')
else:
    with open({calls:?}, 'a') as f: f.write('x')
    if 'annotator A' in p and not pathlib.Path({a_seen:?}).exists():
        pathlib.Path({a_seen:?}).write_text('seen')
        print('malformed')
    else:
        print('R00000000|ham')
"#,
            calls = calls,
            a_seen = a_seen,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "schema row").unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "official binary task",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
    );
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "ham");
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 3);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_dual_manifest_never_contract_retries_provider_errors() {
    let t = temp("solo-dual-provider-error");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import os,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{{"id":"x","evidence":"raw"}}]\nsemantic_manifest(items,"official binary task",["ham","spam"])\nFINAL("unreachable")\n```')
else:
    with open({calls:?}, 'a') as f: f.write('x')
    if 'annotator A' in p:
        print('{{"azdaja_error":"provider_call_failed_retry_item"}}')
    else:
        print('R00000000|ham')
"#,
            calls = calls,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "schema row").unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "official binary task",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
    );
    assert!(!output.status.success());
    assert!(String::from_utf8_lossy(&output.stderr).contains("semantic provider failure"));
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 2);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_dual_manifest_preflights_worst_case_call_budget() {
    let t = temp("solo-dual-budget");
    let marker = t.join("child-called");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import os,sys,pathlib
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{{"id":"x","evidence":"raw"}}]\nsemantic_manifest(items,"official binary task",["ham","spam"])\nFINAL("unreachable")\n```')
else:
    pathlib.Path({marker:?}).write_text('called')
    print('R00000000|ham')
"#,
            marker = marker,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let text = fs::read_to_string(&cfg)
        .unwrap()
        .replace("max_calls_per_cell = 64", "max_calls_per_cell = 4");
    fs::write(&cfg, text).unwrap();
    let input = t.join("input.txt");
    fs::write(&input, "schema row").unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "official binary task",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
    );
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("semantic dual/adjudication call envelope")
    );
    assert!(!marker.exists(), "preflight must precede every child call");
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_prompt_guides_exact_aggregation_in_one_root_turn() {
    let t = temp("solo");
    let mock = t.join("solo.py");
    fs::write(
        &mock,
        r#"import os,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    begin = '--- BEGIN UNTRUSTED OFFSET-LABELLED STRUCTURAL SAMPLE ---'
    end = '--- END UNTRUSTED OFFSET-LABELLED STRUCTURAL SAMPLE ---'
    sample = p.split(begin, 1)[1].split(end, 1)[0].strip('\n') if begin in p and end in p else ''
    required = ('inspect and parse complete ctx', 'preserve source occurrences',
                'semantic_manifest(items, task, labels) exactly once',
                'nonempty list of exactly two-key dicts named id and evidence',
                'nonempty unique string', 'complete faithful nonempty item evidence',
                'never silently truncated', 'source occurrences and weights preserved',
                'task concisely frames', 'at least two distinct actual labels',
                'leave conservative room below the 45000-character envelope',
                'complete id-to-label mapping', 'two blind validated manifests',
                'blind disagreement adjudication', 'every source item has exactly one result',
                'reduce with preserved multiplicity',
                'never infer semantic labels by searching evidence for label words',
                'do not call llm, llm_batch, or llm_batch_fresh directly',
                'os, re, json, math, collections, datetime',
                'globals/locals/callable', 'dict.get', 'below 50 nonblank lines')
    sample_ok = ('schema-canary' in sample and 'TAIL_NOT_IN_SAMPLE' in sample
                 and '[HEAD chars 0..' in sample and '[TAIL chars ' in sample
                 and len(sample.encode('utf-8')) <= 4096)
    if not sample_ok or not all(x in p.lower() for x in required): print('```python\nFINAL("missing bounded sample or exact aggregation playbook")\n```')
    else: print('```python\nFINAL("done:" + llm("classify"))\n```')
else: print('SUB_OK')
"#,
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 1024, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(
        &input,
        format!(
            "schema-canary\n{{\"id\":1,\"body\":\"hello\"}}\n{}TAIL_NOT_IN_SAMPLE",
            "x".repeat(8000)
        ),
    )
    .unwrap();
    let o = run(
        &t,
        &cfg,
        &["solo", "question", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        o.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&o.stdout),
        String::from_utf8_lossy(&o.stderr)
    );
    assert!(
        String::from_utf8_lossy(&o.stdout).contains("done:SUB_OK"),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&o.stdout),
        String::from_utf8_lossy(&o.stderr)
    );
    let sessions = fs::read_dir(t.join("state"))
        .ok()
        .into_iter()
        .flatten()
        .filter_map(Result::ok)
        .filter(|e| {
            e.file_name().to_string_lossy().len() == 16 && e.file_type().is_ok_and(|t| t.is_dir())
        })
        .count();
    assert_eq!(sessions, 0, "solo should retain Monty only in-process");
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_handles_synthetic_final_section_and_prefix_formats_without_gold() {
    let t = temp("solo-final-structure");
    let mock = t.join("root.py");
    fs::write(
        &mock,
        r#"import os,sys
p=sys.stdin.read()
assert os.getenv('RLM_DEPTH') == '0'
required = ('inspect and parse complete ctx',
            'demonstrations or multiple sections',
            'select the requested section', 'preserve source occurrences', '[chars 0..')
assert all(value in p.lower() for value in required), p
if 'CASE_FWE' in p:
    code = '''qpos=ctx.rfind("\\nQuestion:")
assert qpos>=0
body=ctx[:qpos]
start=body.rfind("Data:")
assert start>=0
tokens=body[start+len("Data:"):].split()
counts={}
for token in tokens:
    if token!="...":
        counts[token]=counts[token]+1 if token in counts else 1
words=[]
for token in counts:
    words.append(token)
words.sort(key=lambda token: counts[token],reverse=True)
FINAL(", ".join(words[:3]))'''
    print('```python\n' + code + '\n```')
elif 'CASE_VT' in p:
    first = '''qpos=ctx.rfind("\\nQuestion:")
assert qpos>=0
start=ctx.rfind("Assignments:",0,qpos)
assert start>=0
question=ctx[qpos:]
match=re.search(r"value ([0-9]+)",question)
assert match is not None
target=match.group(1)
mapping={}
order=[]
for line in ctx[start:qpos].splitlines():
    if line.startswith("VAR "):
        parts=line.split()
        mapping[parts[1]]=parts[3]
        order.append(parts[1])'''
    second = '''names=[]
for name in order:
    current=name
    seen=[]
    while not mapping[current].isdigit():
        assert current not in seen
        seen.append(current)
        current=mapping[current]
    if mapping[current]==target:
        names.append(name)
FINAL(" ".join(names))'''
    print('```python\n' + first + '\n' + second + '\n```')
elif 'CASE_KEY' in p:
    code = '''qpos=ctx.rfind("\\nQuestion:")
assert qpos>=0
question=ctx[qpos:]
question_only=question.split(" Answer:",1)[0]
mentions=re.findall(r"key-[a-z]+",question_only)
unique=[]
for key in mentions:
    if key not in unique:
        unique.append(key)
assert len(unique)==1
records={}
for line in ctx[:qpos].splitlines():
    if " = " in line:
        parts=line.split(" = ",1)
        records[parts[0]]=parts[1]
assert unique[0] in records
FINAL(records[unique[0]])'''
    print('```python\n' + code + '\n```')
elif 'CASE_CSV' in p:
    code = '''rows=ctx.splitlines()
total=0
for line in rows[2:]:
    parts=line.split(",")
    total+=int(parts[1])
FINAL(str(total))'''
    print('```python\n' + code + '\n```')
elif 'CASE_LOG' in p:
    code = '''count=0
for line in ctx.splitlines():
    if line.startswith("ERROR "):
        count+=1
FINAL(str(count))'''
    print('```python\n' + code + '\n```')
elif 'CASE_CODE' in p:
    code = '''count=0
for line in ctx.splitlines():
    if "TODO" in line:
        count+=1
FINAL(str(count))'''
    print('```python\n' + code + '\n```')
else:
    raise AssertionError('missing synthetic case marker')
"#,
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 1024, 1, 3, 4);
    let cases = [
        (
            "CASE_FWE Read and count coded tokens. Data: red red red blue blue green ...\nQuestion: Return the three tokens in order. Answer:",
            "red, blue, green",
        ),
        (
            "CASE_VT demo\nAssignments:\nVAR OLD = 111\nQuestion: Find variables assigned value 111. Answer: OLD\nCASE_VT actual\nAssignments:\nVAR END = 777\nVAR MID = END\nVAR TOP = MID\nQuestion: Find variables assigned value 777. Answer:",
            "END MID TOP",
        ),
        (
            "CASE_KEY pairs\nkey-z = value-old\nkey-x = value-final\nQuestion: What is stored for key-x? Answer: continuation for key-x is",
            "value-final",
        ),
        ("CASE_CSV\nname,value\na,2\nb,3", "5"),
        ("CASE_LOG\nINFO boot\nERROR one\nWARN mid\nERROR two", "2"),
        ("CASE_CODE\nfn main() {} // TODO first\n// TODO second", "2"),
    ];
    for (index, (input_text, expected)) in cases.iter().enumerate() {
        let input = t.join(format!("case-{index}.txt"));
        fs::write(&input, input_text).unwrap();
        let output = run(
            &t,
            &cfg,
            &[
                "solo",
                "synthetic format regression",
                "-f",
                input.to_str().unwrap(),
            ],
            "",
        );
        assert!(
            output.status.success(),
            "case={index} stdout={} stderr={}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), *expected);
    }
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_repairs_each_observed_root_failure_class_once_and_uses_fresh_monty() {
    let t = temp("solo-root-repair-classes");
    let mock = t.join("repair.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1])
kind = sys.argv[2]
count = len(calls.read_text().splitlines()) if calls.exists() else 0
calls.open("a").write("root\n")
if count:
    print('```python\nassert ctx == "generic synthetic context"\nFINAL("repaired")\n```')
elif kind == "assertion":
    print('```python\nctx = "poison"\nassert False\n```')
elif kind == "value":
    print('```python\nraise ValueError("sentinel-secret")\n```')
elif kind == "regex":
    print('```python\nre.compile("[z-a]")\nFINAL("bad")\n```')
elif kind == "line":
    print('```python\n' + '\n'.join('x = 1' for _ in range(51)) + '\n```')
elif kind == "key":
    print('```python\nx = {}\nx["missing"]\n```')
elif kind == "index":
    print('```python\nx = []\nx[0]\n```')
else:
    print('invalid prose')
"#,
    )
    .unwrap();
    let input = t.join("input.txt");
    fs::write(&input, "generic synthetic context").unwrap();
    for kind in [
        "assertion",
        "value",
        "regex",
        "line",
        "key",
        "index",
        "prose",
    ] {
        let calls = t.join(format!("{kind}.calls"));
        let trace = t.join(format!("{kind}.trace"));
        let cfg = config(
            &t,
            &format!("python3 {} {} {kind}", mock.display(), calls.display()),
            4096,
            1,
            3,
            4,
        );
        let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .env_remove("RLM_DEPTH")
            .env("AZDAJA_HOME", t.join(format!("{kind}-state")))
            .env("AZDAJA_CONFIG", &cfg)
            .env("AZDAJA_SOLO_TRACE", &trace)
            .args([
                "solo",
                "answer the generic question",
                "-f",
                input.to_str().unwrap(),
            ])
            .output()
            .unwrap();
        assert!(
            output.status.success(),
            "{kind}: {}",
            String::from_utf8_lossy(&output.stderr)
        );
        assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "repaired");
        assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 2);
        let retained = fs::read_to_string(&trace).unwrap();
        assert!(
            retained.contains("category=repair outcome=succeeded"),
            "{kind}: {retained}"
        );
        let repair_request = retained
            .split("=== repair request begin")
            .nth(1)
            .unwrap()
            .split("=== repair request end")
            .next()
            .unwrap();
        assert!(
            !repair_request.contains("sentinel-secret"),
            "repair prompt leaked raw diagnostic"
        );
    }
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_does_not_repair_monty_timeouts() {
    let t = temp("solo-no-timeout-repair");
    let calls = t.join("calls");
    let mock = t.join("timeout.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write("root\n")
print('```python\nwhile True:\n    pass\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let cfg_text = fs::read_to_string(&cfg)
        .unwrap()
        .replace("cell_timeout = 2", "cell_timeout = 1");
    fs::write(&cfg, cfg_text).unwrap();
    let input = t.join("input.txt");
    fs::write(&input, "generic").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("TimeoutError"),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_does_not_repair_unknown_runtime_failures() {
    let t = temp("solo-no-unknown-repair");
    let calls = t.join("calls");
    let mock = t.join("unknown.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write("root\n")
print('```python\nprint("AssertionError: spoof")\nraise RuntimeError("unknown")\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_does_not_repair_after_a_child_call_consumes_evidence() {
    let t = temp("solo-no-repair-after-child");
    let calls = t.join("calls");
    let mock = t.join("child.py");
    fs::write(
        &mock,
        r#"import os, pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write(os.environ.get("RLM_DEPTH", "?") + "\n")
if os.environ.get("RLM_DEPTH") == "0":
    print('```python\nllm("child")\nassert False\n```')
else:
    print("child result")
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic context").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(
        fs::read_to_string(&calls)
            .unwrap()
            .lines()
            .collect::<Vec<_>>(),
        ["0", "1"]
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_repair_model_trace_preflight_failure_prevents_second_turn() {
    let t = temp("repair-model-trace-preflight");
    let calls = t.join("calls");
    let trace = t.join("model.jsonl");
    let mock = t.join("break-model-trace.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1]); trace = pathlib.Path(sys.argv[2])
calls.open("a").write("root\n")
trace.unlink(); trace.mkdir()
print("invalid prose")
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!(
            "python3 {} {} {}",
            mock.display(),
            calls.display(),
            trace.display()
        ),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .args(["solo", "generic question", "-f", input.to_str().unwrap()])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn solo_repair_trace_rename_replacement_prevents_second_turn() {
    let t = temp("repair-trace-binding");
    let calls = t.join("calls");
    let trace = t.join("solo.trace");
    let hidden = t.join("solo.hidden");
    let mock = t.join("replace-trace.py");
    fs::write(&mock, r#"import os, pathlib, sys
calls = pathlib.Path(sys.argv[1]); trace = pathlib.Path(sys.argv[2]); hidden = pathlib.Path(sys.argv[3])
calls.open("a").write("root\n")
trace.rename(hidden)
trace.write_text("")
os.chmod(trace, 0o600)
print("invalid prose")
"#).unwrap();
    let cfg = config(
        &t,
        &format!(
            "python3 {} {} {} {}",
            mock.display(),
            calls.display(),
            trace.display(),
            hidden.display()
        ),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_SOLO_TRACE", &trace)
        .args(["solo", "generic question", "-f", input.to_str().unwrap()])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
    assert_eq!(fs::metadata(&trace).unwrap().len(), 0);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_repair_trace_preflight_failure_prevents_second_turn() {
    let t = temp("solo-repair-trace-preflight");
    let calls = t.join("calls");
    let trace = t.join("solo.trace");
    let mock = t.join("break-trace.py");
    fs::write(
        &mock,
        r#"import pathlib, shutil, sys
calls = pathlib.Path(sys.argv[1]); trace = pathlib.Path(sys.argv[2])
calls.open("a").write("root\n")
trace.unlink(); trace.mkdir()
print("invalid prose")
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!(
            "python3 {} {} {}",
            mock.display(),
            calls.display(),
            trace.display()
        ),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_SOLO_TRACE", &trace)
        .args(["solo", "generic question", "-f", input.to_str().unwrap()])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_repairs_deferred_final_var_lookup_failure() {
    let t = temp("solo-final-var-repair");
    let calls = t.join("calls");
    let mock = t.join("final-var.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1]); count = len(calls.read_text().splitlines()) if calls.exists() else 0
calls.open("a").write("root\n")
if count == 0:
    print('```python\nFINAL_VAR("missing")\n```')
else:
    print('```python\nFINAL("RECOVERED")\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "RECOVERED");
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 2);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_rejects_long_whitespace_final_before_output_capping() {
    let t = temp("solo-long-blank-final");
    let calls = t.join("calls");
    let mock = t.join("long-blank-final.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write("root\n")
print('```python\nFINAL(" " * 1000)\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        256,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "return a nonempty answer",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 3);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_second_repair_rejects_empty_final_and_recovers() {
    let t = temp("solo-empty-final-repair");
    let calls = t.join("calls");
    let mock = t.join("empty-final.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1]); count = len(calls.read_text().splitlines()) if calls.exists() else 0
calls.open("a").write("root\n")
if count == 0:
    print('```python\nassert False\n```')
elif count == 1:
    print('```python\nFINAL("")\n```')
else:
    print('```python\nassert ctx == "original"\nFINAL("RECOVERED")\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "RECOVERED");
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 3);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_second_repair_recovers_a_failed_first_repair_once() {
    let t = temp("solo-second-repair");
    let calls = t.join("calls");
    let mock = t.join("repair-twice.py");
    fs::write(&mock, r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1]); count = len(calls.read_text().splitlines()) if calls.exists() else 0
calls.open("a").write("root\n")
if count == 0:
    print("invalid prose")
elif count == 1:
    print('```python\n' + '\n'.join('x = 1' for _ in range(51)) + '\n```')
else:
    print('```python\nassert ctx == "original"\nFINAL("RECOVERED")\n```')
"#).unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let trace = t.join("solo.trace");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_SOLO_TRACE", &trace)
        .args(["solo", "generic question", "-f", input.to_str().unwrap()])
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "RECOVERED");
    assert_eq!(fs::read_to_string(calls).unwrap().lines().count(), 3);
    let retained = fs::read_to_string(trace).unwrap();
    assert!(retained.contains("repair_index=2"));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_repair_fails_closed_after_exactly_three_root_turns() {
    let t = temp("solo-root-repair-fail-closed");
    let calls = t.join("calls");
    let mock = t.join("bad.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write("root\n")
print("invalid prose")
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic synthetic context").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 3);
    assert!(String::from_utf8_lossy(&output.stderr).contains("repair failed"));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_reports_typed_compile_and_regex_diagnostics_after_one_repair() {
    let t = temp("solo-typed-diagnostics");
    let calls = t.join("calls");
    let mock = t.join("invalid.py");
    fs::write(
        &mock,
        r#"import sys
with open(sys.argv[1], 'a') as f: f.write('root\n')
p=sys.stdin.read()
if 'compile-case' in p:
    print('```python\nx = (\n```')
else:
    print('```python\nre.compile("[z-a]")\nFINAL("unreachable")\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        2048,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "synthetic no-gold data").unwrap();
    for (question, expected) in [
        ("compile-case", "solo root Python compile error"),
        ("regex-case", "solo solve invalid regular expression"),
    ] {
        let output = run(
            &t,
            &cfg,
            &["solo", question, "-f", input.to_str().unwrap()],
            "",
        );
        assert_eq!(output.status.code(), Some(2));
        assert!(
            String::from_utf8_lossy(&output.stderr).contains(expected),
            "stderr={}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 6);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_fails_closed_after_two_repair_turns() {
    let t = temp("solo-turn-limit");
    let calls = t.join("root-calls");
    let mock = t.join("never-final.py");
    fs::write(
        &mock,
        r#"import os,sys
if os.getenv('RLM_DEPTH') == '0':
    with open(sys.argv[1], 'a') as f: f.write('root\n')
    print('```python\nx = 1\n```')
else:
    print('unexpected child call')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        1024,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "raw context").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert!(String::from_utf8_lossy(&output.stderr).contains("did not call FINAL"));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 3);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn shipped_cleaners_strip_jcode_banners_and_ansi() {
    let t = temp("clean");
    let mock = t.join("clean.sh");
    fs::write(&mock,"#!/bin/sh\nprintf '\\033[31m[read] /tmp/p\\033[0m\\n[Tokens] upload: 1 download: 1\\n  → preview\\nANSWER\\n'\n").unwrap();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&mock, fs::Permissions::from_mode(0o755)).unwrap();
    }
    let cfg = t.join("config.toml");
    let text=include_str!("../assets/config.toml").replace("sub_llm_cmd = \"jcode-api\"",&format!("sub_llm_cmd = {:?}",mock.to_str().unwrap())).replace("clean_patterns = []","clean_patterns = ['(?m)^\\[(?:read|write|bash|grep|glob|edit)\\].*\\n?', '(?m)^\\[Tokens\\].*\\n?', '(?m)^\\s*→.*\\n?']");
    fs::write(&cfg, text).unwrap();
    let id = sid(&t, &cfg);
    let out = ok(run(&t, &cfg, &["exec", &id], "llm('x')\n"));
    assert!(out.contains("ANSWER"));
    assert!(
        !out.contains("read")
            && !out.contains("Tokens")
            && !out.contains('→')
            && !out.contains('\u{1b}')
    );
    ok(run(&t, &cfg, &["kill", &id], ""));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn install_is_verified_idempotent_and_owned() {
    let t = temp("install");
    let bin = t.join("bin");
    fs::create_dir(&bin).unwrap();
    let mock = bin.join("claude");
    fs::write(&mock,r#"#!/bin/sh
for a in "$@"; do case "$a" in Read_the_complete_UTF-8_prompt_at_*_and_return_only_its_answer) p=${a#*_at_}; p=${p%_and_return*}; cat "$p";; esac; done
"#).unwrap();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&mock, fs::Permissions::from_mode(0o755)).unwrap();
    }
    let cfg = config(&t, "cat", 512, 1, 3, 4);
    let dst = t.join(".claude/skills/azdaja");
    let bad = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["install", "--harness", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env(
            "PATH",
            format!("{}:{}", bin.display(), std::env::var("PATH").unwrap()),
        )
        .output()
        .unwrap();
    assert!(!bad.status.success());
    assert!(!dst.exists(), "failed verification left a partial install");
    fs::write(&mock, "#!/bin/sh\necho AZDAJA\n").unwrap();
    let mut cmd = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    let o = cmd
        .env_remove("RLM_DEPTH")
        .args(["install", "--harness", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env(
            "PATH",
            format!("{}:{}", bin.display(), std::env::var("PATH").unwrap()),
        )
        .output()
        .unwrap();
    assert!(o.status.success(), "{}", String::from_utf8_lossy(&o.stderr));
    assert!(dst.join("azdaja").is_file());
    let skill = fs::read_to_string(dst.join("SKILL.md")).unwrap();
    assert!(skill.contains("azdaja 0.1.0") && skill.contains(dst.join("azdaja").to_str().unwrap()));
    assert!(skill.contains("Each source occurrence is an aggregation unit"));
    assert!(skill.contains("retaining every source ID or an integer multiplicity"));
    assert!(skill.contains("actual rendered character length"));
    assert!(skill.contains("complete manifest"));
    assert!(skill.contains("Omission is unresolved"));
    assert!(skill.contains("two independent complete manifests"));
    assert!(skill.contains("Blindly adjudicate every A/B disagreement"));
    assert!(skill.contains("`yield`/generators"));
    assert!(skill.contains("`FINAL(answer)` is always defined"));
    assert!(skill.contains("`csv` and other imports are unavailable"));
    let edited_config = fs::read_to_string(&cfg).unwrap().replace(
        "sub_llm_cmd = \"cat\"",
        &format!("sub_llm_cmd = {:?}", mock.to_str().unwrap()),
    );
    fs::write(dst.join("config.toml"), &edited_config).unwrap();
    let o = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["install", "--harness", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env(
            "PATH",
            format!("{}:{}", bin.display(), std::env::var("PATH").unwrap()),
        )
        .output()
        .unwrap();
    assert!(o.status.success(), "{}", String::from_utf8_lossy(&o.stderr));
    assert_eq!(
        fs::read_to_string(dst.join("config.toml")).unwrap(),
        edited_config
    );
    fs::write(dst.join("unknown"), "x").unwrap();
    let refused = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["uninstall", "--harness", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .output()
        .unwrap();
    assert!(!refused.status.success() && dst.exists());
    fs::remove_file(dst.join("unknown")).unwrap();
    let original_skill = fs::read(dst.join("SKILL.md")).unwrap();
    fs::write(dst.join("SKILL.md"), "changed").unwrap();
    let refused = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["uninstall", "--harness", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .output()
        .unwrap();
    assert!(!refused.status.success() && dst.exists());
    fs::write(dst.join("SKILL.md"), original_skill).unwrap();
    let o = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["uninstall", "--harness", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .output()
        .unwrap();
    assert!(o.status.success(), "{}", String::from_utf8_lossy(&o.stderr));
    assert!(!dst.exists());
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn cumulative_llm_budget_stops_repeated_calls_in_one_cell() {
    let t = temp("call-budget");
    let cfg = config(&t, "cat", 1024, 1, 3, 4);
    let id = sid(&t, &cfg);
    let result = run(
        &t,
        &cfg,
        &["exec", &id],
        "for i in range(65):\n    x = llm('x')\n",
    );
    assert!(!result.status.success());
    let out = String::from_utf8(result.stdout).unwrap();
    assert!(out.contains("llm call budget exceeded: 65 > 64"), "{out}");
    ok(run(&t, &cfg, &["kill", &id], ""));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn command_transport_trace_keeps_unknown_route_and_usage_null() {
    let t = temp("unknown-trace");
    let cfg = config(&t, "cat", 2048, 1, 3, 4);
    let id = sid(&t, &cfg);
    let trace = t.join("model.jsonl");
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args(["exec", &id])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(b"print(llm('synthetic'))\n")
        .unwrap();
    ok(child.wait_with_output().unwrap());
    let rows: Vec<serde_json::Value> = fs::read_to_string(trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 1, "{rows:?}");
    let row = &rows[0];
    assert_eq!(row["outcome"], "succeeded");
    assert_eq!(row["entered_turn"], 1);
    assert!(row.get("provider").is_none());
    assert!(row.get("model").is_none());
    assert!(row.get("input_tokens").is_none());
    assert!(row.get("output_tokens").is_none());
    assert!(row.get("cache_read_tokens").is_none());
    fs::remove_dir_all(t).unwrap();
}

#[cfg(unix)]
#[test]
fn jcode_api_fresh_batch_uses_one_session_per_item_and_streams_usage() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;
    let t = temp("jcode-api");
    let socket = t.join("api.sock");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let mut turns_per_session = Vec::new();
        for session_number in 1..=2 {
            // JcodeSession::open first probes bridge liveness, then opens the protocol stream.
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let sid = format!("s{session_number}");
            let mut turn_count = 0;
            let mut runtime_count = 0;
            let mut active_model = if session_number == 1 {
                "gpt-5.3"
            } else {
                "gpt-5.4"
            };
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).unwrap() == 0 {
                    break;
                }
                let f: serde_json::Value = serde_json::from_str(&line).unwrap();
                let id = f["id"].as_u64().unwrap();
                let req = f["req"].as_str().unwrap();
                let frames: Vec<serde_json::Value> = match req {
                    "hello" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                    })],
                    "create_session" if session_number == 1 => vec![
                        serde_json::json!({
                            "v":1,"ev":"session_status","status":"attached","session_id":&sid
                        }),
                        serde_json::json!({
                            "v":1,"reply_to":id,"ev":"attached",
                            "session":{"session_id":&sid,"status":"idle"}
                        }),
                        serde_json::json!({
                            "v":1,"ev":"model_info","session_id":&sid,
                            "provider":"OpenAI","model":active_model
                        }),
                    ],
                    // A correlated attached reply is the completion barrier. The
                    // unsolicited initial model_info event is optional; runtime_info
                    // below is the authoritative route check.
                    "create_session" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"attached",
                        "session":{"session_id":&sid,"status":"idle"}
                    })],
                    "set_model" => {
                        assert_eq!(
                            session_number, 1,
                            "transient empty routes must be re-queried"
                        );
                        assert_eq!(f["model"], "openai-oauth:gpt-5.4");
                        active_model = "gpt-5.4";
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "get_runtime_info" => {
                        runtime_count += 1;
                        let routes = if session_number == 2 && runtime_count == 1 {
                            Vec::<serde_json::Value>::new()
                        } else {
                            vec![serde_json::json!({
                                "provider":"OpenAI","model":active_model,
                                "api_method":"openai-oauth","available":true
                            })]
                        };
                        vec![serde_json::json!({
                            "v":1,"reply_to":id,"ev":"runtime_info","session_id":&sid,
                            "provider":"OpenAI","model":active_model,"routes":routes
                        })]
                    }
                    "set_reasoning_effort" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "send_message" => {
                        turn_count += 1;
                        assert_eq!(turn_count, 1, "batch session received a second turn");
                        let content = f["content"].as_str().unwrap();
                        let text = if content.ends_with("direct secret prompt") {
                            "DIRECT_OK"
                        } else {
                            assert!(content.ends_with("second"));
                            "SECOND_OK"
                        };
                        let mut frames = vec![
                            serde_json::json!({
                                "v":1,"ev":"message_accepted","session_id":&sid
                            }),
                            serde_json::json!({
                                "v":1,"ev":"model_info","session_id":&sid,
                                "provider":"OpenAI","model":active_model
                            }),
                            serde_json::json!({
                                "v":1,"ev":"text_delta","session_id":&sid,"text":text
                            }),
                        ];
                        if session_number == 1 {
                            frames.push(serde_json::json!({
                                "v":1,"ev":"token_usage","session_id":&sid,
                                "input":11,"output":2,"cache_read_input":3
                            }));
                        }
                        frames.push(serde_json::json!({
                            "v":1,"ev":"turn_done","session_id":&sid
                        }));
                        frames
                    }
                    "archive_session" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    x => panic!("unexpected {x}; batch sessions must never be cleared"),
                };
                for frame in frames {
                    serde_json::to_writer(&mut stream, &frame).unwrap();
                    stream.write_all(b"\n").unwrap();
                    stream.flush().unwrap()
                }
            }
            turns_per_session.push(turn_count);
        }
        turns_per_session
    });
    let cfg = config(&t, "jcode-api", 1024, 1, 3, 4);
    let id = sid(&t, &cfg);
    let mut c = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    c.args(["exec", &id])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", t.join("usage.jsonl"))
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = c.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(
            b"print(llm_batch_fresh(['direct secret prompt','second'],model='gpt-5.4',workers=2))\n",
        )
        .unwrap();
    let out = child.wait_with_output().unwrap();
    assert!(
        out.status.success(),
        "{}",
        String::from_utf8_lossy(&out.stderr)
    );
    let stdout = String::from_utf8_lossy(&out.stdout);
    assert!(stdout.contains("DIRECT_OK") && stdout.contains("SECOND_OK"));
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        assert_eq!(
            fs::metadata(t.join("usage.jsonl"))
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o600
        );
    }
    let usage_rows = fs::read_to_string(t.join("usage.jsonl")).unwrap();
    let usages: Vec<serde_json::Value> = usage_rows
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(usages.len(), 2);
    let request_ids: std::collections::HashSet<_> = usages
        .iter()
        .map(|row| row["request_id"].as_str().unwrap())
        .collect();
    assert_eq!(request_ids.len(), 2, "one logical request per batch item");
    let session_ids: std::collections::HashSet<_> = usages
        .iter()
        .map(|row| row["session_id"].as_str().unwrap())
        .collect();
    assert_eq!(session_ids, std::collections::HashSet::from(["s1", "s2"]));
    for usage in &usages {
        assert_eq!(usage["schema_version"], 2);
        assert_eq!(usage["event"], "model_attempt");
        assert_eq!(usage["attempt"], 1);
        assert_eq!(usage["category"], "turn");
        assert_eq!(usage["outcome"], "succeeded");
        assert_eq!(usage["degraded_transport"], false);
        assert_eq!(usage["failed_attempts_before_success"], 0);
        assert_eq!(usage["provider"], "OpenAI");
        assert_eq!(usage["model"], "gpt-5.4");
        if usage["session_id"] == "s1" {
            assert_eq!(usage["input_tokens"], 11);
            assert_eq!(usage["output_tokens"], 2);
            assert_eq!(usage["cache_read_tokens"], 3);
        } else {
            assert_eq!(usage["session_id"], "s2");
            assert!(usage.get("input_tokens").is_none());
            assert!(usage.get("output_tokens").is_none());
            assert!(usage.get("cache_read_tokens").is_none());
        }
        assert!(usage["latency_ms"].as_u64().is_some());
        assert!(usage.get("error").is_none());
    }
    assert_eq!(server.join().unwrap(), [1, 1]);
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn jcode_fresh_batch_retries_setup_without_repeating_model_turn() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("jsr");
    let socket = t.join("api.sock");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let mut messages = Vec::new();
        for session_number in 1..=3 {
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let sid = format!("s{session_number}");
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).unwrap() == 0 {
                    break;
                }
                let request: serde_json::Value = serde_json::from_str(&line).unwrap();
                let id = request["id"].as_u64().unwrap();
                let req = request["req"].as_str().unwrap();
                let frames = match req {
                    "hello" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                    })],
                    "create_session" if session_number < 3 => vec![serde_json::json!({
                        "v":1,"ev":"error","code":"service_unavailable","message":"injected setup failure"
                    })],
                    "create_session" => vec![
                        serde_json::json!({
                            "v":1,"reply_to":id,"ev":"attached",
                            "session":{"session_id":&sid,"status":"idle"}
                        }),
                        serde_json::json!({
                            "v":1,"ev":"model_info","session_id":&sid,
                            "provider":"OpenAI","model":"gpt-5.4"
                        }),
                    ],
                    "get_runtime_info" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"runtime_info","session_id":&sid,
                        "provider":"OpenAI","model":"gpt-5.4",
                        "routes":[{"provider":"OpenAI","model":"gpt-5.4",
                            "api_method":"openai-oauth","available":true}]
                    })],
                    "set_reasoning_effort" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "send_message" => {
                        messages.push(request["content"].as_str().unwrap().to_owned());
                        vec![
                            serde_json::json!({
                                "v":1,"ev":"model_info","session_id":&sid,
                                "provider":"OpenAI","model":"gpt-5.4"
                            }),
                            serde_json::json!({
                                "v":1,"ev":"text_delta","session_id":&sid,"text":"ONLY_OK"
                            }),
                            serde_json::json!({
                                "v":1,"ev":"token_usage","session_id":&sid,
                                "input":7,"output":1,"cache_read_input":0
                            }),
                            serde_json::json!({"v":1,"ev":"turn_done","session_id":&sid}),
                        ]
                    }
                    "archive_session" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    other => panic!("unexpected {other}"),
                };
                for frame in frames {
                    serde_json::to_writer(&mut stream, &frame).unwrap();
                    stream.write_all(b"\n").unwrap();
                    stream.flush().unwrap();
                }
            }
        }
        messages
    });

    let cfg = config(&t, "jcode-api", 1024, 1, 3, 4);
    let id = sid(&t, &cfg);
    let trace = t.join("usage.jsonl");
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args(["exec", &id])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(b"print(llm_batch_fresh(['once'],model='gpt-5.4',workers=1))\n")
        .unwrap();
    let output = child.wait_with_output().unwrap();
    let out = ok(output);
    assert!(out.contains("ONLY_OK"), "{out}");
    assert_eq!(server.join().unwrap().len(), 1);

    let rows: Vec<serde_json::Value> = fs::read_to_string(trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 3, "{rows:?}");
    assert!(rows.iter().all(|row| row["schema_version"] == 2));
    assert!(rows.iter().all(|row| row["event"] == "model_attempt"));
    assert!(
        rows.windows(2)
            .all(|pair| pair[0]["request_id"] == pair[1]["request_id"])
    );
    assert_eq!(
        rows.iter()
            .map(|row| row["attempt"].as_u64().unwrap())
            .collect::<Vec<_>>(),
        [1, 2, 3]
    );
    let failures = &rows[..2];
    assert!(
        failures
            .iter()
            .all(|row| row["category"] == "session_setup")
    );
    assert!(failures.iter().all(|row| row["outcome"] == "failed"));
    assert!(failures.iter().all(|row| row["stage"] == "session_setup"));
    assert!(failures.iter().all(|row| row["setup_substage"] == "attach"));
    assert!(
        failures
            .iter()
            .all(|row| row["error"] == "provider_call_failed")
    );
    assert!(
        failures
            .iter()
            .all(|row| row["error_category"] == "provider")
    );
    assert!(failures.iter().all(|row| row["session_id"].is_null()));
    assert!(failures.iter().all(|row| row.get("input_tokens").is_none()));

    let success = &rows[2];
    assert_eq!(success["category"], "turn");
    assert_eq!(success["outcome"], "succeeded");
    assert_eq!(success["session_id"], "s3");
    assert_eq!(success["degraded_transport"], true);
    assert_eq!(success["failed_attempts_before_success"], 2);
    assert_eq!(success["input_tokens"], 7);
    assert_eq!(success["output_tokens"], 1);
    assert_eq!(
        rows.iter().filter(|row| row["category"] == "turn").count(),
        1,
        "setup retries must not consume entered-turn budget"
    );
}

#[test]
#[cfg(unix)]
fn jcode_fresh_batch_stops_after_four_failed_setups() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("jsb");
    let socket = t.join("api.sock");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let mut messages = Vec::new();
        let mut archives = Vec::new();
        for session_number in 1..=4 {
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let sid = format!("s{session_number}");
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).unwrap() == 0 {
                    break;
                }
                let request: serde_json::Value = serde_json::from_str(&line).unwrap();
                let id = request["id"].as_u64().unwrap();
                let req = request["req"].as_str().unwrap();
                let frames = match req {
                    "hello" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                    })],
                    "create_session" => vec![
                        serde_json::json!({
                            "v":1,"reply_to":id,"ev":"attached",
                            "session":{"session_id":&sid,"status":"idle"}
                        }),
                        serde_json::json!({
                            "v":1,"ev":"model_info","session_id":&sid,
                            "provider":"OpenAI","model":"gpt-5.4"
                        }),
                    ],
                    "get_runtime_info" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"runtime_info","session_id":&sid,
                        "provider":"OpenAI","model":"gpt-5.4",
                        "routes":[{"provider":"OpenAI","model":"gpt-5.4",
                            "api_method":"openai-oauth","available":true}]
                    })],
                    "set_reasoning_effort" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"error","code":"service_unavailable","message":"injected setup failure"
                    })],
                    "send_message" => {
                        messages.push(request["content"].as_str().unwrap().to_owned());
                        vec![
                            serde_json::json!({
                                "v":1,"ev":"model_info","session_id":&sid,
                                "provider":"OpenAI","model":"gpt-5.4"
                            }),
                            serde_json::json!({
                                "v":1,"ev":"text_delta","session_id":&sid,"text":"ONLY_OK"
                            }),
                            serde_json::json!({
                                "v":1,"ev":"token_usage","session_id":&sid,
                                "input":7,"output":1,"cache_read_input":0
                            }),
                            serde_json::json!({"v":1,"ev":"turn_done","session_id":&sid}),
                        ]
                    }
                    "cancel" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "archive_session" => {
                        archives.push(sid.clone());
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    other => panic!("unexpected {other}"),
                };
                for frame in frames {
                    serde_json::to_writer(&mut stream, &frame).unwrap();
                    stream.write_all(b"\n").unwrap();
                    stream.flush().unwrap();
                }
            }
        }
        (messages, archives)
    });

    let cfg = config(&t, "jcode-api", 1024, 1, 3, 4);
    let id = sid(&t, &cfg);
    let trace = t.join("usage.jsonl");
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args(["exec", &id])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(b"print(llm_batch_fresh(['once'],model='gpt-5.4',workers=1))\n")
        .unwrap();
    let output = child.wait_with_output().unwrap();
    let out = ok(output);
    assert!(out.contains("provider_call_failed_retry_item"), "{out}");
    let (messages, archives) = server.join().unwrap();
    assert!(messages.is_empty());
    assert_eq!(archives, vec!["s1", "s2", "s3", "s4"]);

    let rows: Vec<serde_json::Value> = fs::read_to_string(trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 4, "{rows:?}");
    assert!(
        rows.windows(2)
            .all(|pair| pair[0]["request_id"] == pair[1]["request_id"])
    );
    assert_eq!(
        rows.iter()
            .map(|row| row["attempt"].as_u64().unwrap())
            .collect::<Vec<_>>(),
        [1, 2, 3, 4]
    );
    assert!(rows.iter().all(|row| row["category"] == "session_setup"));
    assert!(rows.iter().all(|row| row["outcome"] == "failed"));
    assert!(rows.iter().all(|row| row["stage"] == "session_setup"));
    assert!(rows.iter().all(|row| row["setup_substage"] == "reasoning"));
    assert_eq!(
        rows.iter()
            .map(|row| row["session_id"].as_str().unwrap())
            .collect::<Vec<_>>(),
        ["s1", "s2", "s3", "s4"]
    );
    assert!(rows.iter().all(|row| row.get("input_tokens").is_none()));
}

#[test]
#[cfg(unix)]
fn solo_root_does_not_retry_typed_permanent_invalid_request() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("pir");
    let socket = t.join("a");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let (probe, _) = listener.accept().unwrap();
        drop(probe);
        let (mut stream, _) = listener.accept().unwrap();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        let mut entered_turns = 0;
        loop {
            let mut line = String::new();
            if reader.read_line(&mut line).unwrap() == 0 {
                break;
            }
            let request: serde_json::Value = serde_json::from_str(&line).unwrap();
            let id = request["id"].as_u64().unwrap();
            let frames = match request["req"].as_str().unwrap() {
                "hello" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                })],
                "create_session" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"attached",
                    "session":{"session_id":"s1","status":"idle"}
                })],
                "get_runtime_info" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"runtime_info","session_id":"s1",
                    "provider":"OpenAI","model":"gpt-5.4",
                    "routes":[{"provider":"OpenAI","model":"gpt-5.4",
                        "api_method":"openai-oauth","available":true}]
                })],
                "set_reasoning_effort" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"ok"
                })],
                "send_message" => {
                    entered_turns += 1;
                    vec![serde_json::json!({
                        "v":1,"ev":"error","session_id":"s1",
                        "code":"invalid_request","message":"permanent invalid request"
                    })]
                }
                "cancel" | "archive_session" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"ok"
                })],
                other => panic!("unexpected request {other}"),
            };
            for frame in frames {
                serde_json::to_writer(&mut stream, &frame).unwrap();
                stream.write_all(b"\n").unwrap();
                stream.flush().unwrap();
            }
        }
        entered_turns
    });

    let cfg = config(&t, "jcode-api", 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "synthetic row").unwrap();
    let trace = t.join("model.jsonl");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args([
            "solo",
            "return scripted result",
            "-f",
            input.to_str().unwrap(),
            "--model",
            "gpt-5.4",
        ])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .output()
        .unwrap();
    assert!(!output.status.success());
    assert_eq!(server.join().unwrap(), 1, "permanent error must not retry");
    let rows: Vec<serde_json::Value> = fs::read_to_string(trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 1, "{rows:?}");
    assert_eq!(rows[0]["category"], "turn");
    assert_eq!(rows[0]["entered_turn"], 1);
    assert_eq!(rows[0]["error_category"], "provider");
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn solo_root_retries_explicit_typed_transient_errors_with_separate_budgets() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("rtr");
    let socket = t.join("a");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let mut entered_turns = Vec::new();
        for session_number in 1..=3 {
            // Each open probes bridge liveness before creating its protocol connection.
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let sid = format!("s{session_number}");
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).unwrap() == 0 {
                    break;
                }
                let request: serde_json::Value = serde_json::from_str(&line).unwrap();
                let id = request["id"].as_u64().unwrap();
                let req = request["req"].as_str().unwrap();
                let frames = match req {
                    "hello" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                    })],
                    "create_session" if session_number == 1 => vec![serde_json::json!({
                        "v":1,"ev":"error","code":"service_unavailable","message":"injected transient setup provider failure"
                    })],
                    "create_session" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"attached",
                        "session":{"session_id":&sid,"status":"idle"}
                    })],
                    "get_runtime_info" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"runtime_info","session_id":&sid,
                        "provider":"OpenAI","model":"gpt-5.4",
                        "routes":[{"provider":"OpenAI","model":"gpt-5.4",
                            "api_method":"openai-oauth","available":true}]
                    })],
                    "set_reasoning_effort" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "send_message" => {
                        entered_turns.push(sid.clone());
                        if session_number == 2 {
                            vec![serde_json::json!({
                                "v":1,"ev":"error","session_id":&sid,"code":"service_unavailable",
                                "message":"injected transient provider failure"
                            })]
                        } else {
                            vec![
                                serde_json::json!({
                                    "v":1,"ev":"model_info","session_id":&sid,
                                    "provider":"OpenAI","model":"gpt-5.4"
                                }),
                                serde_json::json!({
                                    "v":1,"ev":"text_delta","session_id":&sid,
                                    "text":"```python\nFINAL(\"ROUTE_OK\")\n```"
                                }),
                                serde_json::json!({
                                    "v":1,"ev":"token_usage","session_id":&sid,
                                    "input":13,"output":2,"cache_read_input":5
                                }),
                                serde_json::json!({"v":1,"ev":"turn_done","session_id":&sid}),
                            ]
                        }
                    }
                    "cancel" | "archive_session" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    other => panic!("unexpected root request {other}"),
                };
                for frame in frames {
                    serde_json::to_writer(&mut stream, &frame).unwrap();
                    stream.write_all(b"\n").unwrap();
                    stream.flush().unwrap();
                }
            }
        }
        entered_turns
    });

    let cfg = config(&t, "jcode-api", 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "synthetic row").unwrap();
    let model_trace = t.join("model.jsonl");
    let solo_trace = t.join("solo.log");
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args([
            "solo",
            "return the scripted result",
            "-f",
            input.to_str().unwrap(),
            "--model",
            "gpt-5.4",
        ])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &model_trace)
        .env("AZDAJA_SOLO_TRACE", &solo_trace)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let output = command.output().unwrap();
    let out = ok(output);
    assert_eq!(out.trim(), "ROUTE_OK");
    assert_eq!(server.join().unwrap(), ["s2", "s3"]);

    let rows: Vec<serde_json::Value> = fs::read_to_string(&model_trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 3, "{rows:?}");
    assert!(
        rows.windows(2)
            .all(|pair| pair[0]["request_id"] == pair[1]["request_id"])
    );
    assert_eq!(
        rows.iter()
            .map(|row| row["attempt"].as_u64().unwrap())
            .collect::<Vec<_>>(),
        [1, 2, 3]
    );

    let setup_failure = &rows[0];
    assert_eq!(setup_failure["category"], "session_setup");
    assert_eq!(setup_failure["outcome"], "failed");
    assert_eq!(setup_failure["setup_substage"], "attach");
    assert_eq!(setup_failure["error_category"], "provider");
    assert!(setup_failure["session_id"].is_null());
    assert!(setup_failure.get("entered_turn").is_none());

    let turn_failure = &rows[1];
    assert_eq!(turn_failure["category"], "turn");
    assert_eq!(turn_failure["outcome"], "failed");
    assert_eq!(turn_failure["session_id"], "s2");
    assert_eq!(turn_failure["entered_turn"], 1);
    assert_eq!(turn_failure["error_category"], "provider");
    assert!(turn_failure.get("input_tokens").is_none());

    let success = &rows[2];
    assert_eq!(success["category"], "turn");
    assert_eq!(success["outcome"], "succeeded");
    assert_eq!(success["session_id"], "s3");
    assert_eq!(success["entered_turn"], 2);
    assert_eq!(success["provider"], "OpenAI");
    assert_eq!(success["model"], "gpt-5.4");
    assert_eq!(success["degraded_transport"], true);
    assert_eq!(success["failed_attempts_before_success"], 2);

    let successful_usage = rows
        .iter()
        .filter(|row| row["outcome"] == "succeeded")
        .fold((0, 0, 0), |sum, row| {
            (
                sum.0 + row["input_tokens"].as_u64().unwrap(),
                sum.1 + row["output_tokens"].as_u64().unwrap(),
                sum.2 + row["cache_read_tokens"].as_u64().unwrap(),
            )
        });
    assert_eq!(successful_usage, (13, 2, 5));
    assert_eq!(
        rows.iter().filter(|row| row["outcome"] == "failed").count(),
        2
    );
    assert_eq!(
        rows.iter().filter(|row| row["category"] == "turn").count(),
        2,
        "setup failure must not spend either physical entered turn"
    );

    let solo = fs::read_to_string(solo_trace).unwrap();
    assert!(solo.contains("attempt=3"), "{solo}");
    assert!(solo.contains("session_id=Some(\"s3\")"), "{solo}");
    assert!(solo.contains("degraded_transport=true"), "{solo}");
    assert!(solo.contains("failed_attempts_before_success=2"), "{solo}");
    assert!(
        solo.contains("provider=\"OpenAI\" model=\"gpt-5.4\""),
        "{solo}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn solo_root_stops_after_four_setup_attempts_without_entering_turn() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("rsa");
    let socket = t.join("a");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        for _ in 0..4 {
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).unwrap() == 0 {
                    break;
                }
                let request: serde_json::Value = serde_json::from_str(&line).unwrap();
                let id = request["id"].as_u64().unwrap();
                let frame = match request["req"].as_str().unwrap() {
                    "hello" => serde_json::json!({
                        "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                    }),
                    "create_session" => serde_json::json!({
                        "v":1,"ev":"error","code":"service_unavailable","message":"transient provider setup failure"
                    }),
                    other => panic!("setup failure must not reach {other}"),
                };
                serde_json::to_writer(&mut stream, &frame).unwrap();
                stream.write_all(b"\n").unwrap();
                stream.flush().unwrap();
            }
        }
    });

    let cfg = config(&t, "jcode-api", 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "synthetic row").unwrap();
    let trace = t.join("model.jsonl");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args([
            "solo",
            "return scripted result",
            "-f",
            input.to_str().unwrap(),
            "--model",
            "gpt-5.4",
        ])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .output()
        .unwrap();
    assert!(!output.status.success());
    server.join().unwrap();
    let rows: Vec<serde_json::Value> = fs::read_to_string(trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 4, "{rows:?}");
    assert_eq!(
        rows.iter()
            .map(|row| row["attempt"].as_u64().unwrap())
            .collect::<Vec<_>>(),
        [1, 2, 3, 4]
    );
    assert!(rows.iter().all(|row| row["category"] == "session_setup"));
    assert!(rows.iter().all(|row| row.get("entered_turn").is_none()));
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn solo_jcode_runtime_repair_reuses_one_session_and_archives_once() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("jrs");
    let socket = t.join("a");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let (probe, _) = listener.accept().unwrap();
        drop(probe);
        let (mut stream, _) = listener.accept().unwrap();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        let mut messages = Vec::new();
        let mut archives = 0;
        loop {
            let mut line = String::new();
            if reader.read_line(&mut line).unwrap() == 0 {
                break;
            }
            let request: serde_json::Value = serde_json::from_str(&line).unwrap();
            let id = request["id"].as_u64().unwrap();
            let frames = match request["req"].as_str().unwrap() {
                "hello" => vec![
                    serde_json::json!({"v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"}),
                ],
                "create_session" => vec![
                    serde_json::json!({"v":1,"reply_to":id,"ev":"attached","session":{"session_id":"same","status":"idle"}}),
                ],
                "get_runtime_info" => vec![
                    serde_json::json!({"v":1,"reply_to":id,"ev":"runtime_info","session_id":"same","provider":"OpenAI","model":"gpt-5.4","routes":[{"provider":"OpenAI","model":"gpt-5.4","api_method":"openai-oauth","available":true}]}),
                ],
                "set_reasoning_effort" => vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})],
                "send_message" => {
                    messages.push(request["content"].as_str().unwrap().to_owned());
                    let text = match messages.len() {
                        1 => "```python\nctx = \"poison\"\nassert False\n```".to_owned(),
                        2 => format!("```python\n{}\n```", "x = 1\n".repeat(51)),
                        _ => "```python\nassert ctx == \"original\"\nFINAL(\"REPAIRED\")\n```"
                            .to_owned(),
                    };
                    vec![
                        serde_json::json!({"v":1,"ev":"model_info","session_id":"same","provider":"OpenAI","model":"gpt-5.4"}),
                        serde_json::json!({"v":1,"ev":"text_delta","session_id":"same","text":text}),
                        serde_json::json!({"v":1,"ev":"token_usage","session_id":"same","input":4,"output":1,"cache_read_input":0}),
                        serde_json::json!({"v":1,"ev":"turn_done","session_id":"same"}),
                    ]
                }
                "archive_session" => {
                    archives += 1;
                    vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                }
                other => panic!("unexpected root request {other}"),
            };
            for frame in frames {
                serde_json::to_writer(&mut stream, &frame).unwrap();
                stream.write_all(b"\n").unwrap();
                stream.flush().unwrap();
            }
        }
        (messages, archives)
    });
    let cfg = config(&t, "jcode-api", 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let model_trace = t.join("model.jsonl");
    let solo_trace = t.join("solo.log");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args([
            "solo",
            "generic question",
            "-f",
            input.to_str().unwrap(),
            "--model",
            "gpt-5.4",
        ])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &model_trace)
        .env("AZDAJA_SOLO_TRACE", &solo_trace)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "REPAIRED");
    let (messages, archives) = server.join().unwrap();
    assert_eq!(messages.len(), 3);
    assert!(messages[1].contains("typed category Assertion"));
    assert!(messages[2].contains("typed category LineLimit"));
    assert_eq!(archives, 1);
    let rows: Vec<serde_json::Value> = fs::read_to_string(model_trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 3);
    assert_eq!(rows[0]["session_id"], "same");
    assert_eq!(rows[1]["session_id"], "same");
    assert_eq!(rows[1]["category"], "repair");
    assert_eq!(rows[2]["session_id"], "same");
    assert_eq!(rows[2]["category"], "repair");
    assert!(
        rows[1]["request_id"]
            .as_str()
            .unwrap()
            .ends_with("-repair-1")
    );
    assert!(
        rows[2]["request_id"]
            .as_str()
            .unwrap()
            .ends_with("-repair-2")
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn valid_root_response_is_not_retried_when_trace_append_fails() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("tio");
    let socket = t.join("a");
    let model_trace = t.join("model.jsonl");
    let server_trace = model_trace.clone();
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let (probe, _) = listener.accept().unwrap();
        drop(probe);
        let (mut stream, _) = listener.accept().unwrap();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        let mut entered_turns = 0;
        loop {
            let mut line = String::new();
            if reader.read_line(&mut line).unwrap() == 0 {
                break;
            }
            let request: serde_json::Value = serde_json::from_str(&line).unwrap();
            let id = request["id"].as_u64().unwrap();
            let frames = match request["req"].as_str().unwrap() {
                "hello" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                })],
                "create_session" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"attached",
                    "session":{"session_id":"s1","status":"idle"}
                })],
                "get_runtime_info" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"runtime_info","session_id":"s1",
                    "provider":"OpenAI","model":"gpt-5.4",
                    "routes":[{"provider":"OpenAI","model":"gpt-5.4",
                        "api_method":"openai-oauth","available":true}]
                })],
                "set_reasoning_effort" => {
                    vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                }
                "send_message" => {
                    entered_turns += 1;
                    // Preflight already succeeded. Break only the later append to prove a
                    // diagnostic failure cannot turn this valid response into another call.
                    fs::remove_file(&server_trace).unwrap();
                    fs::create_dir(&server_trace).unwrap();
                    vec![
                        serde_json::json!({
                            "v":1,"ev":"model_info","session_id":"s1",
                            "provider":"OpenAI","model":"gpt-5.4"
                        }),
                        serde_json::json!({
                            "v":1,"ev":"text_delta","session_id":"s1",
                            "text":"```python\nFINAL(\"TRACE_OK\")\n```"
                        }),
                        serde_json::json!({
                            "v":1,"ev":"token_usage","session_id":"s1",
                            "input":4,"output":1,"cache_read_input":0
                        }),
                        serde_json::json!({"v":1,"ev":"turn_done","session_id":"s1"}),
                    ]
                }
                "archive_session" => {
                    vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                }
                other => panic!("unexpected root request {other}"),
            };
            for frame in frames {
                serde_json::to_writer(&mut stream, &frame).unwrap();
                stream.write_all(b"\n").unwrap();
                stream.flush().unwrap();
            }
        }
        entered_turns
    });

    let cfg = config(&t, "jcode-api", 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "synthetic row").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args([
            "solo",
            "return scripted result",
            "-f",
            input.to_str().unwrap(),
            "--model",
            "gpt-5.4",
        ])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &model_trace)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "TRACE_OK");
    assert_eq!(
        server.join().unwrap(),
        1,
        "valid response must not be retried"
    );
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("model trace write failed"),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn jcode_batch_retries_provider_once_then_preserves_failure() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("jpb");
    let socket = t.join("api.sock");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let mut all_messages = Vec::new();
        let mut archives = Vec::new();
        for session_number in 1..=4 {
            // JcodeSession::open first probes bridge liveness, then opens the protocol stream.
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let sid = format!("s{session_number}");
            let mut session_messages = 0;
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).unwrap() == 0 {
                    break;
                }
                let request: serde_json::Value = serde_json::from_str(&line).unwrap();
                let id = request["id"].as_u64().unwrap();
                let req = request["req"].as_str().unwrap();
                let frames = match req {
                    "hello" => vec![serde_json::json!({
                        "v": 1, "reply_to": id, "ev": "hello_ok", "version": 1,
                        "server": "fake"
                    })],
                    "create_session" => vec![
                        serde_json::json!({
                            "v": 1, "reply_to": id, "ev": "attached",
                            "session": {"session_id": &sid, "status": "idle"}
                        }),
                        serde_json::json!({
                            "v":1,"ev":"model_info","session_id":&sid,
                            "provider":"OpenAI","model":"gpt-5.4"
                        }),
                    ],
                    "set_model" => {
                        assert_eq!(request["model"], "openai-oauth:gpt-5.4");
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "get_runtime_info" => vec![serde_json::json!({
                        "v": 1, "reply_to": id, "ev": "runtime_info",
                        "session_id": &sid, "provider": "OpenAI", "model": "gpt-5.4",
                        "routes":[{
                            "provider":"OpenAI","model":"gpt-5.4",
                            "api_method":"openai-oauth","available":true
                        }]
                    })],
                    "set_reasoning_effort" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "send_message" => {
                        session_messages += 1;
                        assert_eq!(session_messages, 1, "batch session received a second turn");
                        let content = request["content"].as_str().unwrap().to_owned();
                        all_messages.push(content.clone());
                        if session_number == 2 || session_number == 3 {
                            assert!(content.ends_with("bad"));
                            vec![serde_json::json!({
                                "v": 1, "ev": "error", "session_id": &sid,
                                "code": "service_unavailable", "message": "injected provider failure"
                            })]
                        } else {
                            let (suffix, answer) = if session_number == 1 {
                                ("first", "FIRST_OK")
                            } else {
                                assert_eq!(session_number, 4);
                                ("third", "THIRD_OK")
                            };
                            assert!(content.ends_with(suffix), "{content}");
                            vec![
                                serde_json::json!({
                                    "v":1,"ev":"model_info","session_id":&sid,
                                    "provider":"OpenAI","model":"gpt-5.4"
                                }),
                                serde_json::json!({
                                    "v":1,"ev":"text_delta","session_id":&sid,"text":answer
                                }),
                                serde_json::json!({"v":1,"ev":"turn_done","session_id":&sid}),
                            ]
                        }
                    }
                    "cancel" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "archive_session" => {
                        archives.push(sid.clone());
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    other => panic!(
                        "unexpected {other}; batch sessions must receive one turn and no clear"
                    ),
                };
                for frame in frames {
                    serde_json::to_writer(&mut stream, &frame).unwrap();
                    stream.write_all(b"\n").unwrap();
                    stream.flush().unwrap();
                }
            }
        }
        (all_messages, archives)
    });

    let cfg = config(&t, "jcode-api", 2048, 1, 2, 4);
    let id = sid(&t, &cfg);
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args(["exec", &id])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(b"print(llm_batch(['first','bad','third'],model='gpt-5.4',workers=1))\n")
        .unwrap();
    let output = child.wait_with_output().unwrap();
    let out = ok(output);
    let first = out.find("FIRST_OK").unwrap();
    let failed = out
        .find(r#"{"azdaja_error":"provider_call_failed_retry_item""#)
        .unwrap();
    let third = out.find("THIRD_OK").unwrap();
    assert!(first < failed && failed < third, "{out}");
    assert!(out.contains("injected provider failure"), "{out}");

    let (messages, archives) = server.join().unwrap();
    assert_eq!(messages.len(), 4);
    assert_eq!(archives, ["s1", "s2", "s3", "s4"]);
    fs::remove_dir_all(t).unwrap();
}
