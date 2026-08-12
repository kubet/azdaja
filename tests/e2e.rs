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
    ok(run(&t, &cfg, &["exec", &id], "FINAL('λ'*10000)\n"));
    let final_out = ok(run(&t, &cfg, &["final", &id], ""));
    assert!(final_out.chars().count() <= 256 && final_out.contains("chars elided"));
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
fn solo_drives_root_and_recursive_subcall_end_to_end() {
    let t = temp("solo");
    let mock = t.join("solo.py");
    fs::write(
        &mock,
        r#"import os,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    if 'Capped result from the cell:' in p: print('```python\nFINAL("done:" + sub)\n```')
    else: print('```python\nsub = llm("classify")\n```')
else: print('SUB_OK')
"#,
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 1024, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "raw context").unwrap();
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
    assert!(String::from_utf8_lossy(&o.stdout).contains("done:SUB_OK"));
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
fn jcode_api_transport_reuses_worker_session_and_streams_usage() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;
    let t = temp("jcode-api");
    let socket = t.join("api.sock");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let _ = listener.accept().unwrap();
        let (mut stream, _) = listener.accept().unwrap();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        let mut send_count = 0;
        loop {
            let mut line = String::new();
            if reader.read_line(&mut line).unwrap() == 0 {
                break;
            }
            let f: serde_json::Value = serde_json::from_str(&line).unwrap();
            let id = f["id"].as_u64().unwrap();
            let req = f["req"].as_str().unwrap();
            let frames: Vec<serde_json::Value> = match req {
                "hello" => vec![
                    serde_json::json!({"v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"}),
                ],
                "create_session" => vec![
                    serde_json::json!({"v":1,"reply_to":id,"ev":"attached","session":{"session_id":"s1","status":"idle"}}),
                ],
                "get_runtime_info" => vec![
                    serde_json::json!({"v":1,"reply_to":id,"ev":"runtime_info","session_id":"s1","provider":"OpenAI","model":"gpt-5.4","routes":[{"model":"gpt-5.4","provider":"OpenAI","api_method":"openai-oauth","available":true,"detail":"OAuth"}]}),
                ],
                "set_model" => {
                    assert_eq!(f["model"], "openai-oauth:gpt-5.4");
                    vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                }
                "set_reasoning_effort" => vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})],
                "send_message" => {
                    send_count += 1;
                    let suffix = if send_count == 1 {
                        "direct secret prompt"
                    } else {
                        "second"
                    };
                    assert!(f["content"].as_str().unwrap().ends_with(suffix));
                    vec![
                        serde_json::json!({"v":1,"ev":"message_accepted","session_id":"s1"}),
                        serde_json::json!({"v":1,"ev":"model_info","session_id":"s1","provider":"OpenAI","model":"gpt-5.4"}),
                        serde_json::json!({"v":1,"ev":"text_delta","session_id":"s1","text":if send_count==1{"DIRECT_OK"}else{"SECOND_OK"}}),
                        serde_json::json!({"v":1,"ev":"token_usage","session_id":"s1","input":11,"output":2,"cache_read_input":3}),
                        serde_json::json!({"v":1,"ev":"turn_done","session_id":"s1"}),
                    ]
                }
                "clear" => vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})],
                "archive_session" => vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})],
                x => panic!("unexpected {x}"),
            };
            for frame in frames {
                serde_json::to_writer(&mut stream, &frame).unwrap();
                stream.write_all(b"\n").unwrap();
                stream.flush().unwrap()
            }
        }
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
            b"print(llm_batch(['direct secret prompt','second'],model='gpt-5.4',workers=1))\n",
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
    server.join().unwrap();
    fs::remove_dir_all(t).unwrap();
}
