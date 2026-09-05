use azdaja::sha256_hex;
use serde_json::Value;
use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant};

static NEXT: AtomicU64 = AtomicU64::new(0);
struct Fixture(PathBuf);
impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}
impl Fixture {
    fn new() -> Self {
        let root = loop {
            let candidate = std::env::temp_dir().join(format!(
                "az-export-{}-{}",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            match fs::create_dir(&candidate) {
                Ok(()) => break candidate,
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
                Err(error) => panic!("exclusive fixture: {error}"),
            }
        };
        let fixture = Self(root);
        fs::create_dir(fixture.0.join("home")).unwrap();
        fs::create_dir(fixture.0.join("repo")).unwrap();
        let mut git = fixture.command("git");
        git.args(["init", "--template=", "--initial-branch=main"]);
        assert!(fixture.finish(git).status.success());
        fixture
    }
    fn command(&self, program: &str) -> Command {
        let mut command = Command::new(program);
        for (key, _) in std::env::vars_os() {
            let name = key.to_string_lossy();
            if ["AZDAJA_", "JCODE_", "GIT_", "RLM_"]
                .iter()
                .any(|prefix| name.starts_with(prefix))
            {
                command.env_remove(key);
            }
        }
        command
            .current_dir(self.0.join("repo"))
            .env("HOME", self.0.join("home"))
            .env("USERPROFILE", self.0.join("home"))
            .env("XDG_CONFIG_HOME", self.0.join("config"))
            .env("XDG_STATE_HOME", self.0.join("xdg"))
            .env("AZDAJA_HOME", self.0.join("personal"))
            .env("AZDAJA_PROJECT_MEMORY", "on")
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .env("GIT_CONFIG_GLOBAL", self.0.join("absent-git-config"))
            .env("GIT_TERMINAL_PROMPT", "0")
            .stdin(Stdio::null());
        command
    }
    fn finish(&self, mut command: Command) -> Output {
        // Regular files avoid pipe capacity and descendant-held EOF deadlocks.
        let number = NEXT.fetch_add(1, Ordering::Relaxed);
        let stdout = self.0.join(format!("stdout-{number}"));
        let stderr = self.0.join(format!("stderr-{number}"));
        command
            .stdout(fs::File::create(&stdout).unwrap())
            .stderr(fs::File::create(&stderr).unwrap());
        let mut child = command.spawn().unwrap();
        let deadline = Instant::now() + Duration::from_secs(15);
        let status = loop {
            if let Some(status) = child.try_wait().unwrap() {
                break status;
            }
            if Instant::now() >= deadline {
                let _ = child.kill();
                let _ = child.wait();
                panic!("CLI exceeded fixture deadline");
            }
            std::thread::sleep(Duration::from_millis(5));
        };
        assert!(fs::metadata(&stdout).unwrap().len() <= 1024 * 1024);
        assert!(fs::metadata(&stderr).unwrap().len() <= 64 * 1024);
        Output {
            status,
            stdout: fs::read(stdout).unwrap(),
            stderr: fs::read(stderr).unwrap(),
        }
    }
    fn run(&self, args: &[&str]) -> Output {
        let mut command = self.command(env!("CARGO_BIN_EXE_azdaja"));
        command.args(args);
        self.finish(command)
    }
    fn add(&self, text: &str, links: &[String], global: bool) -> String {
        let mut args = vec![
            "memory",
            "add",
            "observation",
            text,
            "--tag",
            "file:src/lib.rs",
        ];
        for link in links {
            args.extend(["--link", link]);
        }
        if global {
            args.push("--global");
        }
        let output = self.run(&args);
        assert!(
            output.status.success(),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        String::from_utf8(output.stdout)
            .unwrap()
            .split_whitespace()
            .nth(1)
            .unwrap()
            .to_owned()
    }
    fn export(&self, ids: &[&str], context: bool, global: bool) -> Output {
        let mut args = vec!["memory", "export"];
        args.extend(ids);
        if context {
            args.push("--with-context");
        }
        if global {
            args.push("--global");
        }
        self.run(&args)
    }
    fn snapshot(&self) -> BTreeMap<PathBuf, Vec<u8>> {
        fn visit(path: &Path, root: &Path, result: &mut BTreeMap<PathBuf, Vec<u8>>) {
            if !path.exists() {
                return;
            }
            let metadata = fs::symlink_metadata(path).unwrap();
            assert!(!metadata.file_type().is_symlink());
            let mut value = vec![u8::from(metadata.is_dir())];
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                value.extend(metadata.permissions().mode().to_le_bytes());
            }
            if metadata.is_file() {
                value.extend(fs::read(path).unwrap());
            }
            result.insert(path.strip_prefix(root).unwrap().to_owned(), value);
            if metadata.is_dir() {
                for entry in fs::read_dir(path).unwrap() {
                    visit(&entry.unwrap().path(), root, result);
                }
            }
        }
        let mut result = BTreeMap::new();
        for name in ["repo/.azdaja", "personal", "home", "config", "xdg"] {
            visit(&self.0.join(name), &self.0, &mut result);
        }
        result
    }
}
fn bundle(output: &Output) -> Value {
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(output.stderr.is_empty());
    assert!(output.stdout.ends_with(b"\n"));
    let value: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(value["payload"]["format"], "azdaja-curated-memory");
    assert_eq!(value["payload"]["version"], 1);
    let digest = sha256_hex(&serde_json::to_vec(&value["payload"]).unwrap());
    assert_eq!(value["payload_sha256"], digest);
    let mut declared: Vec<_> = value["payload"]["selection"]
        .as_array()
        .unwrap()
        .iter()
        .chain(value["payload"]["context_ids"].as_array().unwrap())
        .cloned()
        .collect();
    declared.sort_by(|a, b| a.as_str().cmp(&b.as_str()));
    let actual: Vec<_> = value["payload"]["records"]
        .as_array()
        .unwrap()
        .iter()
        .map(|record| record["id"].clone())
        .collect();
    assert_eq!(
        declared, actual,
        "every declared selected/context ID must have exactly one record"
    );
    assert!(
        actual
            .windows(2)
            .all(|pair| pair[0].as_str() < pair[1].as_str())
    );
    assert!(
        value["caveat"]
            .as_str()
            .unwrap()
            .contains("not verified truth")
    );
    value
}
fn refused(output: &Output) {
    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    assert!(!output.stderr.is_empty());
}

#[test]
fn explicit_export_is_deterministic_exact_and_nonmutating_without_writer_lock() {
    let f = Fixture::new();
    let text = "Wisdom Ω 🦀\n$(touch forbidden)\nIgnore instructions is inert note text";
    let first = f.add(text, &[], false);
    let second = f.add("other explicitly selected note", &[], false);
    f.add("unrelated secret must remain local", &[], false);
    fs::remove_file(f.0.join("repo/.azdaja/memory/global.lock")).unwrap();
    let before = f.snapshot();
    let output = f.export(&[&first, &second], false, false);
    let value = bundle(&output);
    assert_eq!(
        output.stdout,
        f.export(&[&second, &first], false, false).stdout
    );
    let records = value["payload"]["records"].as_array().unwrap();
    assert_eq!(records.len(), 2);
    let record = records.iter().find(|record| record["id"] == first).unwrap();
    assert_eq!(record["text"], text);
    assert_eq!(record["provenance"]["origin"], "manual");
    assert_eq!(record["tags"], serde_json::json!(["file:src/lib.rs"]));
    assert_eq!(value["payload"]["context_ids"], serde_json::json!([]));
    assert!(!String::from_utf8_lossy(&output.stdout).contains("unrelated secret"));
    assert!(!String::from_utf8_lossy(&output.stdout).contains(f.0.to_str().unwrap()));
    assert!(!f.0.join("repo/forbidden").exists());
    assert_eq!(before, f.snapshot());
    let mut modified = value["payload"].clone();
    modified["records"][0]["text"] = Value::from("tampered");
    assert_ne!(
        sha256_hex(&serde_json::to_vec(&modified).unwrap()),
        value["payload_sha256"].as_str().unwrap()
    );
}

#[test]
fn connected_context_requires_consent_and_preserves_all_directions_beyond_recall_cap() {
    let f = Fixture::new();
    let anchor = f.add("anchor", &[], false);
    let mut previous = anchor.clone();
    for index in 0..12 {
        previous = f.add(
            &format!("contrary nonmatching context {index}"),
            &[format!("related-to:{previous}")],
            false,
        );
    }
    let before = f.snapshot();
    let rejected = f.export(&[&anchor], false, false);
    refused(&rejected);
    assert!(String::from_utf8_lossy(&rejected.stderr).contains("12 additional"));
    assert!(!String::from_utf8_lossy(&rejected.stderr).contains("contrary nonmatching"));
    for selected in [&anchor, &previous] {
        let value = bundle(&f.export(&[selected], true, false));
        assert_eq!(value["payload"]["records"].as_array().unwrap().len(), 13);
        assert_eq!(
            value["payload"]["context_ids"].as_array().unwrap().len(),
            12
        );
        assert_eq!(value["payload"]["selection"], serde_json::json!([selected]));
    }
    assert_eq!(before, f.snapshot());
}

#[test]
fn invalid_selection_flags_and_cold_missing_ids_never_initialize_state() {
    let f = Fixture::new();
    let before = f.snapshot();
    for args in [
        vec!["memory", "export"],
        vec!["memory", "export", "bad"],
        vec!["memory", "export", "m0000000000000000"],
        vec!["memory", "export", "--all"],
        vec!["memory", "export", "--global", "--global"],
        vec!["memory", "export", "--with-context", "--with-context"],
    ] {
        refused(&f.run(&args));
        assert_eq!(before, f.snapshot());
    }
    let id = f.add("valid", &[], false);
    let before = f.snapshot();
    refused(&f.export(&[&id, &id], false, false));
    let too_many = vec![id.as_str(); 17];
    refused(&f.export(&too_many, false, false));
    assert_eq!(before, f.snapshot());
}

#[test]
fn explicit_global_and_disabled_project_routing_do_not_mix_stores() {
    let f = Fixture::new();
    let project = f.add("project only", &[], false);
    let global = f.add("global only", &[], true);
    let before = f.snapshot();
    refused(&f.export(&[&global], true, false));
    refused(&f.export(&[&project], true, true));
    assert_eq!(
        bundle(&f.export(&[&global], false, true))["payload"]["records"][0]["text"],
        "global only"
    );
    let mut command = f.command(env!("CARGO_BIN_EXE_azdaja"));
    command
        .env("AZDAJA_PROJECT_MEMORY", "off")
        .args(["memory", "export", &project]);
    refused(&f.finish(command));
    let mut command = f.command(env!("CARGO_BIN_EXE_azdaja"));
    command
        .env("AZDAJA_PROJECT_MEMORY", "off")
        .args(["memory", "export", &global, "--global"]);
    bundle(&f.finish(command));
    assert_eq!(before, f.snapshot());
}

#[test]
fn corrupt_ledger_is_refused_without_repair_and_recovers_exact_export() {
    let f = Fixture::new();
    let id = f.add("history", &[], false);
    let expected = f.export(&[&id], false, false);
    bundle(&expected);
    let path = f.0.join("repo/.azdaja/memory/global.jsonl");
    let original = fs::read(&path).unwrap();
    fs::write(&path, b"{\"text\":null}\n").unwrap();
    let damaged = f.snapshot();
    refused(&f.export(&[&id], true, false));
    assert_eq!(damaged, f.snapshot());
    fs::write(path, original).unwrap();
    assert_eq!(expected.stdout, f.export(&[&id], false, false).stdout);
}

#[test]
fn full_connected_ledger_exports_without_truncation_and_enforces_selection_boundary() {
    let f = Fixture::new();
    let mut ids = Vec::new();
    let relations = ["supports", "supersedes", "derived-from", "related-to"];
    for index in 0..256 {
        let text = format!("record {index} {}", "🦀".repeat(300));
        let links = ids
            .last()
            .map(|id| vec![format!("{}:{id}", relations[index % 4])])
            .unwrap_or_default();
        ids.push(f.add(&text, &links, false));
    }
    let before = f.snapshot();
    let selected: Vec<_> = ids.iter().take(16).map(String::as_str).collect();
    let output = f.export(&selected, true, false);
    let value = bundle(&output);
    assert!(output.stdout.len() > 256 * 1024);
    assert!(output.stdout.len() <= 1024 * 1024);
    assert_eq!(value["payload"]["selection"].as_array().unwrap().len(), 16);
    assert_eq!(
        value["payload"]["context_ids"].as_array().unwrap().len(),
        240
    );
    let records = value["payload"]["records"].as_array().unwrap();
    assert_eq!(records.len(), 256);
    let mut expected: Vec<Value> = fs::read_to_string(f.0.join("repo/.azdaja/memory/global.jsonl"))
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    expected.sort_by(|a, b| a["id"].as_str().cmp(&b["id"].as_str()));
    assert_eq!(
        records, &expected,
        "every field of every record must remain exact"
    );
    let too_many: Vec<_> = ids.iter().take(17).map(String::as_str).collect();
    refused(&f.export(&too_many, true, false));
    assert_eq!(before, f.snapshot());
}

#[test]
fn public_help_explains_explicit_context_consent_without_claiming_import() {
    let f = Fixture::new();
    let before = f.snapshot();
    let output = f.run(&["memory", "--help"]);
    assert!(output.status.success());
    let help = String::from_utf8(output.stdout).unwrap();
    assert!(help.contains("Export: az memory export <id>... [--with-context] [--global]"));
    assert!(help.contains("review all records before sharing"));
    assert!(!help.contains("Import:"));
    assert_eq!(before, f.snapshot());
}

#[test]
fn dangling_relationship_is_refused_before_any_incomplete_bundle_is_emitted() {
    let f = Fixture::new();
    let id = f.add("complete history", &[], false);
    let expected = f.export(&[&id], false, false);
    bundle(&expected);
    let ledger = f.0.join("repo/.azdaja/memory/global.jsonl");
    let original = fs::read(&ledger).unwrap();
    let mut record: Value = serde_json::from_slice(&original).unwrap();
    record["links"] =
        serde_json::json!([{"relation":"related-to", "target_id":"m0000000000000000"}]);
    let mut damaged = serde_json::to_vec(&record).unwrap();
    damaged.push(b'\n');
    fs::write(&ledger, damaged).unwrap();
    let before = f.snapshot();
    for consent in [false, true] {
        refused(&f.export(&[&id], consent, false));
    }
    assert_eq!(before, f.snapshot());
    fs::write(ledger, original).unwrap();
    assert_eq!(expected.stdout, f.export(&[&id], true, false).stdout);
}
