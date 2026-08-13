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
    begin = '--- BEGIN UNTRUSTED SCHEMA SAMPLE ---'
    end = '--- END UNTRUSTED SCHEMA SAMPLE ---'
    sample = p.split(begin, 1)[1].split(end, 1)[0].strip('\n') if begin in p and end in p else ''
    required = ('parse only the observed schema', 'every source occurrence', 'integer multiplicity',
                'semantic_manifest(items, task, labels)', 'two blind independent full manifests',
                'strictly validates both', 'blindly adjudicates every disagreement',
                'two-key dicts named id and evidence', 'nonempty unique string',
                'call the helper exactly once iff semantic judgments are required',
                'never call llm, llm_batch, or llm_batch_fresh directly',
                'os, re, json, math, collections, datetime',
                'globals/locals/callable', 'keep code under 50 nonblank lines')
    sample_ok = 'schema-canary' in sample and len(sample) <= 4096 and 'TAIL_NOT_IN_SAMPLE' not in p
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
fn solo_fails_closed_after_one_root_turn() {
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
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
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
                    "create_session" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"attached",
                        "session":{"session_id":&sid,"status":"idle"}
                    })],
                    "get_runtime_info" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"runtime_info","session_id":&sid,
                        "provider":"OpenAI","model":"gpt-5.4"
                    })],
                    "set_model" => {
                        assert_eq!(f["model"], "openai-oauth:gpt-5.4");
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "set_reasoning_effort" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "send_message" => {
                        turn_count += 1;
                        assert_eq!(turn_count, 1, "batch session received a second turn");
                        let (suffix, text) = if session_number == 1 {
                            ("direct secret prompt", "DIRECT_OK")
                        } else {
                            ("second", "SECOND_OK")
                        };
                        assert!(f["content"].as_str().unwrap().ends_with(suffix));
                        vec![
                            serde_json::json!({
                                "v":1,"ev":"message_accepted","session_id":&sid
                            }),
                            serde_json::json!({
                                "v":1,"ev":"model_info","session_id":&sid,
                                "provider":"OpenAI","model":"gpt-5.4"
                            }),
                            serde_json::json!({
                                "v":1,"ev":"text_delta","session_id":&sid,"text":text
                            }),
                            serde_json::json!({
                                "v":1,"ev":"token_usage","session_id":&sid,
                                "input":11,"output":2,"cache_read_input":3
                            }),
                            serde_json::json!({"v":1,"ev":"turn_done","session_id":&sid}),
                        ]
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
            b"print(llm_batch_fresh(['direct secret prompt','second'],model='gpt-5.4',workers=1))\n",
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
    let usage = &usages[0];
    assert_eq!(usage["provider"], "OpenAI");
    assert_eq!(usage["model"], "gpt-5.4");
    assert_eq!(usage["input_tokens"], 11);
    assert_eq!(usage["output_tokens"], 2);
    assert_eq!(usage["cache_read_tokens"], 3);
    assert!(usage["latency_ms"].as_u64().is_some());
    assert_eq!(server.join().unwrap(), [1, 1]);
    fs::remove_dir_all(t).unwrap();
}

#[cfg(unix)]
#[test]
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
                    "create_session" => vec![serde_json::json!({
                        "v": 1, "reply_to": id, "ev": "attached",
                        "session": {"session_id": &sid, "status": "idle"}
                    })],
                    "set_model" => {
                        assert_eq!(request["model"], "openai-oauth:gpt-5.4");
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "get_runtime_info" => vec![serde_json::json!({
                        "v": 1, "reply_to": id, "ev": "runtime_info",
                        "session_id": &sid, "provider": "OpenAI", "model": "gpt-5.4"
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
                                "message": "injected provider failure"
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
