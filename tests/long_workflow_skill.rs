use std::{
    fs,
    io::Write,
    path::{Path, PathBuf},
    process::{Command, Stdio},
    time::{SystemTime, UNIX_EPOCH},
};

fn root() -> PathBuf {
    let base = std::env::var_os("JCODE_SCRATCH_DIR")
        .map(PathBuf::from)
        .unwrap_or_else(std::env::temp_dir);
    let path = base.join(format!(
        "long-workflow-skill-{}-{}",
        std::process::id(),
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    ));
    fs::create_dir_all(&path).unwrap();
    path
}

fn run(home: &Path, config: &Path, args: &[&str], input: &str) -> std::process::Output {
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args(args)
        .env("AZDAJA_HOME", home.join("state"))
        .env("AZDAJA_CONFIG", config)
        .env_remove("TYPESAFE_API_KEY")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(input.as_bytes())
        .unwrap();
    child.wait_with_output().unwrap()
}

struct SessionGuard {
    home: PathBuf,
    config: PathBuf,
    sid: String,
    root: PathBuf,
}

impl Drop for SessionGuard {
    fn drop(&mut self) {
        let _ = run(&self.home, &self.config, &["kill", &self.sid], "");
        let _ = fs::remove_dir_all(&self.root);
    }
}

fn ok(output: std::process::Output) -> String {
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).unwrap()
}

#[test]
fn skill_routes_long_workflow_and_preserves_one_shot_lane() {
    let template = fs::read_to_string("assets/template/SKILL.md").unwrap();
    let installed = fs::read_to_string("skills/azdaja/SKILL.md").unwrap();
    for skill in [&template, &installed] {
        assert!(skill.contains("Choose exactly one workflow"));
        assert!(skill.contains("General persistent/artifact workflow"));
        assert!(skill.contains("exec"));
        assert!(skill.contains("persistent"));
        assert!(skill.contains("Historical one-shot exact-panel workflow"));
        assert!(skill.contains("llm_batch"));
        assert!(skill.contains("scripts, data, or reports"));
        assert!(skill.contains("native `sha256(text)`"));
    }

    let dir = root();
    let home = dir.join("home");
    fs::create_dir_all(&home).unwrap();
    let config = dir.join("config.toml");
    fs::write(
        &config,
        "sub_llm_cmd = \"/bin/false\"\ncell_timeout = 5\n[judge]\nenabled = false\n",
    )
    .unwrap();
    let source = dir.join("packed-source.bin");
    let bytes = b"head\xF0\x9F\xA7\xAA\ntail";
    fs::write(&source, bytes).unwrap();

    let sid = ok(run(&home, &config, &["start"], "")).trim().to_owned();
    let _guard = SessionGuard {
        home: home.clone(),
        config: config.clone(),
        sid: sid.clone(),
        root: dir.clone(),
    };
    assert!(
        run(
            &home,
            &config,
            &["load", &sid, source.to_str().unwrap(), "source"],
            ""
        )
        .status
        .success()
    );
    assert!(
        run(&home, &config, &["exec", &sid], "count = 1\n")
            .status
            .success()
    );
    let second = ok(run(
        &home,
        &config,
        &["exec", &sid],
        "count = count + 1\nFINAL({\"count\": count, \"source\": source})\n",
    ));
    assert!(
        second.is_empty(),
        "exec should defer the final value to final: {second:?}"
    );
    let exported = ok(run(&home, &config, &["final", &sid], ""));
    let artifact = dir.join("data.json");
    fs::write(&artifact, &exported).unwrap();
    let parsed: serde_json::Value = serde_json::from_str(exported.trim()).unwrap();
    assert_eq!(parsed["count"], 2);
    assert_eq!(parsed["source"], String::from_utf8_lossy(bytes).as_ref());
    let host_slice = &bytes[4..8];
    assert_eq!(host_slice, "🧪".as_bytes());
    assert!(artifact.exists());
}
