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

impl Fixture {
    fn import_bytes(&self, bytes: &[u8], apply: bool, global: bool) -> Output {
        let source = self.0.join(format!(
            "bundle-{}.json",
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::write(&source, bytes).unwrap();
        let mut args = vec!["memory", "import", source.to_str().unwrap()];
        if apply {
            args.push("--apply");
        }
        if global {
            args.push("--global");
        }
        let result = self.run(&args);
        assert_eq!(
            fs::read(source).unwrap(),
            bytes,
            "import must not alter its input"
        );
        result
    }
    fn clone_from(source: &Self) -> Self {
        fs::write(
            source.0.join("repo/README.md"),
            "Disposable handoff fixture\n",
        )
        .unwrap();
        let mut add = source.command("git");
        add.args(["add", "README.md"]);
        assert!(source.finish(add).status.success());
        let mut commit = source.command("git");
        commit.args([
            "-c",
            "user.name=Memory Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            "commit.gpgSign=false",
            "commit",
            "-m",
            "Seed handoff fixture",
        ]);
        assert!(source.finish(commit).status.success());
        let destination = Self::new();
        fs::remove_dir_all(destination.0.join("repo")).unwrap();
        let mut clone = destination.command("git");
        clone
            .current_dir(&destination.0)
            .args(["clone", "--no-local", "--template="])
            .arg(source.0.join("repo"))
            .arg(destination.0.join("repo"));
        assert!(destination.finish(clone).status.success());
        assert!(!destination.0.join("repo/.azdaja").exists());
        destination
    }
}

fn import_receipt(output: &Output) -> Value {
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    let value: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert!(
        value["caveat"]
            .as_str()
            .unwrap()
            .contains("untrusted source assertion")
    );
    assert!(
        value["caveat"]
            .as_str()
            .unwrap()
            .contains("not verified truth")
    );
    value
}

fn rehash(mut value: Value) -> Vec<u8> {
    value["payload_sha256"] =
        Value::from(sha256_hex(&serde_json::to_vec(&value["payload"]).unwrap()));
    serde_json::to_vec(&value).unwrap()
}

#[test]
fn actual_clone_import_previews_without_writes_then_preserves_exact_handoff_idempotently() {
    let source = Fixture::new();
    let anchor = source.add("verified-by-tests handoff anchor", &[], false);
    source.add(
        "contrary context must survive the handoff",
        &[format!("related-to:{anchor}")],
        false,
    );
    let exported = source.export(&[&anchor], true, false);
    let original = bundle(&exported);
    let destination = Fixture::clone_from(&source);
    let source_before = source.snapshot();
    let before = destination.snapshot();
    let preview = import_receipt(&destination.import_bytes(&exported.stdout, false, false));
    assert_eq!(preview["action"], "dry-run");
    assert_eq!(preview["scope"], "project");
    assert_eq!(preview["new_records"], 2);
    assert_eq!(preview["already_present"], 0);
    assert_eq!(preview["total_records"], 2);
    assert_eq!(preview["source_payload_sha256"], original["payload_sha256"]);
    assert_eq!(before, destination.snapshot());
    let applied = import_receipt(&destination.import_bytes(&exported.stdout, true, false));
    assert_eq!(applied["action"], "apply");
    assert_eq!(applied["new_records"], 2);
    assert_eq!(applied["source_payload_sha256"], original["payload_sha256"]);
    let after = destination.snapshot();
    let second = import_receipt(&destination.import_bytes(&exported.stdout, true, false));
    assert_eq!(second["new_records"], 0);
    assert_eq!(second["already_present"], 2);
    assert_eq!(after, destination.snapshot());
    assert_eq!(
        exported.stdout,
        destination.export(&[&anchor], true, false).stdout
    );
    let home = destination.0.join("fresh-agent-home");
    fs::create_dir(&home).unwrap();
    let mut recall = destination.command(env!("CARGO_BIN_EXE_azdaja"));
    recall
        .env("HOME", &home)
        .env("USERPROFILE", &home)
        .args(["memory", "recall", "anchor"]);
    let output = destination.finish(recall);
    assert!(output.status.success());
    let report: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(report["matches"][0]["record"]["id"], anchor);
    assert_eq!(
        report["context"][0]["record"]["text"],
        "contrary context must survive the handoff"
    );
    assert_eq!(source_before, source.snapshot());
    assert_eq!(after, destination.snapshot());
}

#[test]
fn malformed_tampered_duplicate_and_unknown_import_data_never_initializes_destination() {
    let source = Fixture::new();
    let id = source.add("private body must not enter diagnostics", &[], false);
    let output = source.export(&[&id], false, false);
    let original = bundle(&output);
    let destination = Fixture::new();
    let before = destination.snapshot();
    let raw = String::from_utf8(output.stdout.clone()).unwrap();
    let duplicate = raw.replacen("\"version\":1", "\"version\":1,\"version\":1", 1);
    assert_ne!(raw, duplicate);
    let mut cases = vec![
        b"not JSON".to_vec(),
        duplicate.into_bytes(),
        format!(" {raw}").into_bytes(),
        vec![b' '; 1024 * 1024 + 1],
    ];
    let mut wrong_digest = original.clone();
    wrong_digest["payload"]["records"][0]["text"] = Value::from("changed");
    cases.push(serde_json::to_vec(&wrong_digest).unwrap());
    for (field, value) in [
        ("unexpected", Value::from(true)),
        ("id", Value::from("bad\nINJECTED_DIAGNOSTIC")),
        ("provenance", serde_json::json!({"origin":"verified"})),
        (
            "links",
            serde_json::json!([{"relation":"related-to","target_id":"m0000000000000000"}]),
        ),
    ] {
        let mut changed = original.clone();
        changed["payload"]["records"][0][field] = value;
        cases.push(rehash(changed));
    }
    let mut version = original.clone();
    version["payload"]["version"] = Value::from(2);
    cases.push(rehash(version));
    let mut policy = original.clone();
    policy["caveat"] = Value::from("authenticated consensus");
    cases.push(rehash(policy));
    for bytes in cases {
        for apply in [false, true] {
            let result = destination.import_bytes(&bytes, apply, false);
            refused(&result);
            let error = String::from_utf8_lossy(&result.stderr);
            assert!(!error.contains("private body"));
            assert!(!error.contains("INJECTED_DIAGNOSTIC"));
            assert_eq!(before, destination.snapshot());
        }
    }
    assert_eq!(
        import_receipt(&destination.import_bytes(&output.stdout, true, false))["new_records"],
        1
    );
}

#[test]
fn conflicting_import_preserves_existing_records_and_does_not_recreate_missing_custody() {
    let f = Fixture::new();
    let id = f.add("original history", &[], false);
    let exported = f.export(&[&id], false, false);
    let mut changed = bundle(&exported);
    changed["payload"]["records"][0]["text"] = Value::from("conflicting history");
    let bytes = rehash(changed);
    fs::remove_file(f.0.join("repo/.azdaja/memory/global.lock")).unwrap();
    let before = f.snapshot();
    for apply in [false, true] {
        refused(&f.import_bytes(&bytes, apply, false));
        assert_eq!(before, f.snapshot());
    }
    let same = import_receipt(&f.import_bytes(&exported.stdout, true, false));
    assert_eq!(same["new_records"], 0);
    assert_eq!(same["already_present"], 1);
    assert_eq!(before, f.snapshot());
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
fn public_help_explains_context_consent_and_no_write_import_default() {
    let f = Fixture::new();
    let before = f.snapshot();
    let output = f.run(&["memory", "--help"]);
    assert!(output.status.success());
    let help = String::from_utf8(output.stdout).unwrap();
    assert!(help.contains("Export: az memory export <id>... [--with-context] [--global]"));
    assert!(help.contains("review all records before sharing"));
    assert!(help.contains("Import: az memory import <bundle-file> [--apply] [--global]"));
    assert!(help.contains("Import defaults to a no-write dry-run"));
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
#[test]
fn import_at_record_capacity_refuses_without_losing_existing_history() {
    let source = Fixture::new();
    let id = source.add("incoming capacity evidence", &[], false);
    let exported = source.run(&["memory", "export", &id]);
    assert!(exported.status.success());
    let destination = Fixture::new();
    for index in 0..256 {
        destination.add(&format!("retained capacity record {index}"), &[], false);
    }
    let ledger = destination.0.join("repo/.azdaja/memory/global.jsonl");
    let original = fs::read(&ledger).unwrap();
    assert_eq!(
        original
            .split(|byte| *byte == b'\n')
            .filter(|line| !line.is_empty())
            .count(),
        256
    );
    let before = destination.snapshot();
    for apply in [false, true] {
        let output = destination.import_bytes(&exported.stdout, apply, false);
        assert_eq!(output.status.code(), Some(2));
        assert!(output.stdout.is_empty());
        assert_eq!(fs::read(&ledger).unwrap(), original);
        assert_eq!(destination.snapshot(), before);
    }
    let output = destination.run(&["memory", "recall", "retained"]);
    assert!(output.status.success());
    let report: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(report["total_matches"], 256);
    assert_eq!(destination.snapshot(), before);
    let first: Value =
        serde_json::from_slice(original.split(|byte| *byte == b'\n').next().unwrap()).unwrap();
    let existing = destination.run(&["memory", "export", first["id"].as_str().unwrap()]);
    assert!(existing.status.success());
    let unchanged = destination.import_bytes(&existing.stdout, true, false);
    assert!(unchanged.status.success());
    let report: Value = serde_json::from_slice(&unchanged.stdout).unwrap();
    assert_eq!(report["new_records"], 0);
    assert_eq!(report["already_present"], 1);
    assert_eq!(report["total_records"], 256);
    assert_eq!(destination.snapshot(), before);
}

#[test]
fn valid_import_refuses_corrupt_destination_without_repair_then_recovers() {
    let source = Fixture::new();
    let id = source.add("incoming recovery note", &[], false);
    let exported = source.run(&["memory", "export", &id]);
    assert!(exported.status.success());
    let destination = Fixture::new();
    destination.add("original retained note", &[], false);
    let ledger = destination.0.join("repo/.azdaja/memory/global.jsonl");
    let original = fs::read(&ledger).unwrap();
    let damaged = b"{broken private note\n";
    fs::write(&ledger, damaged).unwrap();
    let before = destination.snapshot();
    for apply in [false, true] {
        let output = destination.import_bytes(&exported.stdout, apply, false);
        assert_eq!(output.status.code(), Some(2));
        assert!(output.stdout.is_empty());
        assert!(!String::from_utf8_lossy(&output.stderr).contains("broken private note"));
        assert_eq!(fs::read(&ledger).unwrap(), damaged);
        assert_eq!(destination.snapshot(), before);
    }
    fs::write(&ledger, &original).unwrap();
    let applied = destination.import_bytes(&exported.stdout, true, false);
    assert!(applied.status.success());
    let report: Value = serde_json::from_slice(&applied.stdout).unwrap();
    assert_eq!(report["new_records"], 1);
    assert_eq!(report["total_records"], 2);
    assert!(fs::read(&ledger).unwrap().starts_with(&original));
    let recovered = destination.run(&["memory", "export", &id]);
    assert!(recovered.status.success());
    assert_eq!(recovered.stdout, exported.stdout);
}

#[test]
fn import_byte_capacity_accounts_for_utf8_metadata_and_newlines_then_recovers() {
    let source = Fixture::new();
    let text = "🦀".repeat(4096);
    let id = source.add(&text, &[], false);
    let exported = source.run(&["memory", "export", &id]);
    assert!(exported.status.success());
    let envelope: Value = serde_json::from_slice(&exported.stdout).unwrap();
    let incoming_record_bytes = serde_json::to_vec(&envelope["payload"]["records"][0])
        .unwrap()
        .len()
        + 1;
    let destination = Fixture::new();
    let ledger = destination.0.join("repo/.azdaja/memory/global.jsonl");
    let mut refused = false;
    for _ in 0..40 {
        let previous = fs::read(&ledger).unwrap_or_default();
        let output = destination.run(&[
            "memory",
            "add",
            "observation",
            &text,
            "--tag",
            "file:src/lib.rs",
        ]);
        if output.status.success() {
            continue;
        }
        assert_eq!(output.status.code(), Some(2));
        assert!(output.stdout.is_empty());
        assert_eq!(fs::read(&ledger).unwrap(), previous);
        refused = true;
        break;
    }
    assert!(
        refused,
        "fixture must reach the actual serialized byte boundary"
    );
    let original = fs::read(&ledger).unwrap();
    let count = original
        .split(|byte| *byte == b'\n')
        .filter(|line| !line.is_empty())
        .count();
    assert!(count < 256, "this must exercise bytes, not record capacity");
    assert!(original.len() <= 512 * 1024);
    assert!(original.len() + incoming_record_bytes > 512 * 1024);
    let before = destination.snapshot();
    for apply in [false, true] {
        let output = destination.import_bytes(&exported.stdout, apply, false);
        assert_eq!(output.status.code(), Some(2));
        assert!(output.stdout.is_empty());
        assert_eq!(destination.snapshot(), before);
        assert_eq!(fs::read(&ledger).unwrap(), original);
    }
    let small = Fixture::new();
    let small_id = small.add("small recovery evidence", &[], false);
    let small_export = small.run(&["memory", "export", &small_id]);
    assert!(small_export.status.success());
    let small_envelope: Value = serde_json::from_slice(&small_export.stdout).unwrap();
    let small_record_bytes = serde_json::to_vec(&small_envelope["payload"]["records"][0])
        .unwrap()
        .len()
        + 1;
    assert!(original.len() + small_record_bytes <= 512 * 1024);
    let applied = destination.import_bytes(&small_export.stdout, true, false);
    assert!(
        applied.status.success(),
        "{}",
        String::from_utf8_lossy(&applied.stderr)
    );
    let report: Value = serde_json::from_slice(&applied.stdout).unwrap();
    assert_eq!(report["new_records"], 1);
    let after = fs::read(&ledger).unwrap();
    assert!(after.starts_with(&original));
    assert_eq!(after.len(), original.len() + small_record_bytes);
    eprintln!(
        "import_byte_capacity retained={count} old_bytes={} rejected_record_bytes={incoming_record_bytes} accepted_record_bytes={small_record_bytes} recovery=passed",
        original.len()
    );
}
// Concurrent children use ordinary files, not reader threads whose inherited
// pipe descriptors could outlive the child. Every child remains owned until reaped.
struct PendingMemoryChild {
    child: Option<std::process::Child>,
    stdout: PathBuf,
    stderr: PathBuf,
}

impl PendingMemoryChild {
    fn start(fixture: &Fixture, args: &[&str], sequence: usize) -> Self {
        Self::start_in_mode(fixture, args, sequence, "on")
    }

    fn start_in_mode(fixture: &Fixture, args: &[&str], sequence: usize, mode: &str) -> Self {
        Self::start_configured(fixture, args, sequence, mode, |_| {})
    }

    fn start_configured(
        fixture: &Fixture,
        args: &[&str],
        sequence: usize,
        mode: &str,
        configure: impl FnOnce(&mut Command),
    ) -> Self {
        let stdout = fixture.0.join(format!("race-{sequence}.stdout"));
        let stderr = fixture.0.join(format!("race-{sequence}.stderr"));
        let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
        command.env_clear();
        for key in ["PATH", "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "TEMP", "TMP"] {
            if let Some(value) = std::env::var_os(key) {
                command.env(key, value);
            }
        }
        command
            .current_dir(fixture.0.join("repo"))
            .env("HOME", fixture.0.join("home"))
            .env("USERPROFILE", fixture.0.join("home"))
            .env("XDG_CONFIG_HOME", fixture.0.join("config"))
            .env("XDG_STATE_HOME", fixture.0.join("xdg"))
            .env("AZDAJA_HOME", fixture.0.join("personal"))
            .env("AZDAJA_PROJECT_MEMORY", mode)
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .env("GIT_CONFIG_GLOBAL", fixture.0.join("absent-git-config"))
            .args(args)
            .stdin(Stdio::null())
            .stdout(fs::File::create(&stdout).unwrap())
            .stderr(fs::File::create(&stderr).unwrap());
        configure(&mut command);
        Self {
            child: Some(command.spawn().unwrap()),
            stdout,
            stderr,
        }
    }

    fn finish(mut self, deadline: std::time::Instant) -> std::process::Output {
        let status = loop {
            if let Some(status) = self.child.as_mut().unwrap().try_wait().unwrap() {
                self.child.take();
                break status;
            }
            assert!(
                std::time::Instant::now() < deadline,
                "concurrent memory child exceeded shared deadline"
            );
            std::thread::sleep(std::time::Duration::from_millis(5));
        };
        assert!(fs::metadata(&self.stdout).unwrap().len() <= 1024 * 1024);
        assert!(fs::metadata(&self.stderr).unwrap().len() <= 64 * 1024);
        std::process::Output {
            status,
            stdout: fs::read(&self.stdout).unwrap(),
            stderr: fs::read(&self.stderr).unwrap(),
        }
    }
}

impl Drop for PendingMemoryChild {
    fn drop(&mut self) {
        if let Some(mut child) = self.child.take() {
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

#[test]
fn overlapping_imports_and_normal_writers_preserve_every_acknowledged_record() {
    let source = Fixture::new();
    let imported_id = source.add("imported concurrent evidence", &[], false);
    let exported = source.run(&["memory", "export", &imported_id]);
    assert!(exported.status.success());
    let destination = Fixture::new();
    let original_id = destination.add("preexisting concurrent evidence", &[], false);
    let original_export = destination.run(&["memory", "export", &original_id]);
    assert!(original_export.status.success());
    let input = destination.0.join("reviewed-race-bundle.json");
    fs::write(&input, &exported.stdout).unwrap();
    let custody = fs::OpenOptions::new()
        .read(true)
        .write(true)
        .open(destination.0.join("repo/.azdaja/memory/global.lock"))
        .unwrap();
    fs2::FileExt::lock_exclusive(&custody).unwrap();
    let mut children = Vec::new();
    for index in 0..8 {
        children.push((
            true,
            PendingMemoryChild::start(
                &destination,
                &["memory", "import", input.to_str().unwrap(), "--apply"],
                index * 2,
            ),
        ));
        children.push((
            false,
            PendingMemoryChild::start(
                &destination,
                &[
                    "memory",
                    "add",
                    "observation",
                    &format!("normal concurrent writer {index}"),
                ],
                index * 2 + 1,
            ),
        ));
    }
    for (_, child) in &mut children {
        assert!(
            child.child.as_mut().unwrap().try_wait().unwrap().is_none(),
            "all 16 children must overlap while actual writer custody is held"
        );
    }
    drop(custody);
    let deadline = std::time::Instant::now() + std::time::Duration::from_secs(15);
    let mut imported = 0;
    let mut acknowledged_writers = 0;
    for (is_import, child) in children {
        let output = child.finish(deadline);
        assert!(
            output.status.success(),
            "{}",
            String::from_utf8_lossy(&output.stderr)
        );
        if is_import {
            let report: Value = serde_json::from_slice(&output.stdout).unwrap();
            assert_eq!(report["scope"], "project");
            imported += report["new_records"].as_u64().unwrap();
        } else {
            acknowledged_writers += 1;
        }
    }
    assert_eq!(imported, 1);
    assert_eq!(acknowledged_writers, 8);
    let ledger =
        fs::read_to_string(destination.0.join("repo/.azdaja/memory/global.jsonl")).unwrap();
    let records: Vec<Value> = ledger
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(records.len(), 10);
    assert_eq!(
        records
            .iter()
            .filter(|record| record["id"] == imported_id)
            .count(),
        1
    );
    for index in 0..8 {
        assert_eq!(
            records
                .iter()
                .filter(|record| record["text"] == format!("normal concurrent writer {index}"))
                .count(),
            1
        );
    }
    let after_export = destination.run(&["memory", "export", &original_id]);
    assert!(after_export.status.success());
    assert_eq!(after_export.stdout, original_export.stdout);
    assert_eq!(fs::read(&input).unwrap(), exported.stdout);
    let recalled = destination.run(&["memory", "recall", "concurrent"]);
    assert!(recalled.status.success());
    let report: Value = serde_json::from_slice(&recalled.stdout).unwrap();
    assert_eq!(report["total_matches"], 10);
    eprintln!(
        "import_race overlapping_children=16 import_calls=8 unique_imports={imported} acknowledged_normal_writers={acknowledged_writers} final_records=10"
    );
}
#[test]
fn import_routing_matrix_keeps_project_global_and_legacy_stores_separate() {
    let source = Fixture::new();
    let id = source.add("routingproof import evidence", &[], false);
    let exported = source.run(&["memory", "export", &id]);
    assert!(exported.status.success());
    for mode in ["on", "off", "legacy"] {
        for global in [false, true] {
            let destination = Fixture::new();
            let input = destination.0.join("routing-bundle.json");
            fs::write(&input, &exported.stdout).unwrap();
            let invoke = |args: &[&str], selected_mode: &str| {
                PendingMemoryChild::start_in_mode(&destination, args, 0, selected_mode)
                    .finish(std::time::Instant::now() + std::time::Duration::from_secs(15))
            };
            let mut args = vec!["memory", "import", input.to_str().unwrap()];
            if global {
                args.push("--global");
            }
            let before = destination.snapshot();
            let preview = invoke(&args, mode);
            assert_eq!(
                destination.snapshot(),
                before,
                "preview mode={mode} global={global}"
            );
            args.push("--apply");
            let applied = invoke(&args, mode);
            if mode == "off" && !global {
                for output in [preview, applied] {
                    assert_eq!(output.status.code(), Some(2));
                    assert!(output.stdout.is_empty());
                }
                assert_eq!(destination.snapshot(), before);
                continue;
            }
            let expected_scope = if global {
                "global"
            } else if mode == "on" {
                "project"
            } else {
                "legacy"
            };
            for (output, action) in [(preview, "dry-run"), (applied, "apply")] {
                assert!(
                    output.status.success(),
                    "mode={mode} global={global}: {}",
                    String::from_utf8_lossy(&output.stderr)
                );
                let report: Value = serde_json::from_slice(&output.stdout).unwrap();
                assert_eq!(
                    report
                        .as_object()
                        .unwrap()
                        .keys()
                        .map(String::as_str)
                        .collect::<std::collections::BTreeSet<_>>(),
                    std::collections::BTreeSet::from([
                        "action",
                        "scope",
                        "new_records",
                        "already_present",
                        "total_records",
                        "source_payload_sha256",
                        "caveat"
                    ])
                );
                let source_envelope: Value = serde_json::from_slice(&exported.stdout).unwrap();
                assert_eq!(
                    report["source_payload_sha256"],
                    source_envelope["payload_sha256"]
                );
                assert!(
                    report["caveat"]
                        .as_str()
                        .unwrap()
                        .contains("not verified truth")
                );
                assert_eq!(report["scope"], expected_scope);
                assert_eq!(report["action"], action);
                assert_eq!(report["new_records"], 1);
                assert_eq!(report["already_present"], 0);
                assert_eq!(report["total_records"], 1);
            }
            let after = destination.snapshot();
            for (read_mode, read_global, read_scope) in [
                ("on", false, "project"),
                ("legacy", false, "legacy"),
                ("off", true, "global"),
            ] {
                let mut read_args = vec!["memory", "recall", "routingproof"];
                if read_global {
                    read_args.push("--global");
                }
                let output = invoke(&read_args, read_mode);
                assert!(
                    output.status.success(),
                    "{}",
                    String::from_utf8_lossy(&output.stderr)
                );
                let report: Value = serde_json::from_slice(&output.stdout).unwrap();
                let expected = usize::from(read_scope == expected_scope);
                assert_eq!(report["total_matches"], expected);
                if expected == 1 {
                    assert_eq!(report["matches"][0]["record"]["id"], id);
                }
                assert_eq!(destination.snapshot(), after);
            }
            assert_eq!(fs::read(&input).unwrap(), exported.stdout);
        }
    }
}

#[test]
fn import_invalid_flags_and_nonregular_sources_refuse_without_initialization() {
    let source = Fixture::new();
    let id = source.add("source remains unchanged", &[], false);
    let exported = source.run(&["memory", "export", &id]);
    assert!(exported.status.success());
    let destination = Fixture::new();
    let input = destination.0.join("valid-source.json");
    fs::write(&input, &exported.stdout).unwrap();
    let before = destination.snapshot();
    for suffix in [
        vec!["--apply", "--apply"],
        vec!["--global", "--global"],
        vec!["--unknown"],
    ] {
        let mut args = vec!["memory", "import", input.to_str().unwrap()];
        args.extend(suffix);
        let output = destination.run(&args);
        assert_eq!(output.status.code(), Some(2));
        assert!(output.stdout.is_empty());
        assert_eq!(destination.snapshot(), before);
    }
    let directory = destination.0.join("source-directory");
    fs::create_dir(&directory).unwrap();
    let missing = destination.0.join("missing-source");
    let paths = vec![directory, missing];
    #[cfg(unix)]
    let paths = {
        let mut paths = paths;
        let link = destination.0.join("source-link");
        std::os::unix::fs::symlink(&input, &link).unwrap();
        paths.push(link);
        paths
    };
    for path in paths {
        for apply in [false, true] {
            let mut args = vec!["memory", "import", path.to_str().unwrap()];
            if apply {
                args.push("--apply");
            }
            let output = destination.run(&args);
            assert_eq!(output.status.code(), Some(2));
            assert!(output.stdout.is_empty());
            assert_eq!(destination.snapshot(), before);
            assert_eq!(fs::read(&input).unwrap(), exported.stdout);
        }
    }
}
#[cfg(unix)]
#[test]
fn import_write_failure_preserves_history_and_releases_custody_for_recovery() {
    use std::os::unix::process::CommandExt;
    let source = Fixture::new();
    let id = source.add(&"🦀".repeat(4096), &[], false);
    let exported = source.run(&["memory", "export", &id]);
    assert!(exported.status.success());
    let destination = Fixture::new();
    for index in 0..20 {
        destination.add(
            &format!("retained fault record {index} {}", "x".repeat(300)),
            &[],
            false,
        );
    }
    let ledger = destination.0.join("repo/.azdaja/memory/global.jsonl");
    let original = fs::read(&ledger).unwrap();
    assert!(original.len() > 8192);
    let input = destination.0.join("fault-bundle.json");
    fs::write(&input, &exported.stdout).unwrap();
    let output = PendingMemoryChild::start_configured(
        &destination,
        &["memory", "import", input.to_str().unwrap(), "--apply"],
        0,
        "on",
        |command| {
            // Only async-signal-safe libc calls run between fork and exec.
            unsafe {
                command.pre_exec(|| {
                    if libc::signal(libc::SIGXFSZ, libc::SIG_IGN) == libc::SIG_ERR {
                        return Err(std::io::Error::last_os_error());
                    }
                    let limit = libc::rlimit {
                        rlim_cur: 8192,
                        rlim_max: 8192,
                    };
                    if libc::setrlimit(libc::RLIMIT_FSIZE, &limit) != 0 {
                        return Err(std::io::Error::last_os_error());
                    }
                    Ok(())
                });
            }
        },
    )
    .finish(std::time::Instant::now() + std::time::Duration::from_secs(15));
    assert_eq!(
        output.status.code(),
        Some(2),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read(&ledger).unwrap(), original);
    assert_eq!(fs::read(&input).unwrap(), exported.stdout);
    let recalled = destination.run(&["memory", "recall", "retained fault"]);
    assert!(recalled.status.success());
    let report: Value = serde_json::from_slice(&recalled.stdout).unwrap();
    assert_eq!(report["total_matches"], 20);
    let recovered = destination.import_bytes(&exported.stdout, true, false);
    assert!(
        recovered.status.success(),
        "{}",
        String::from_utf8_lossy(&recovered.stderr)
    );
    let report: Value = serde_json::from_slice(&recovered.stdout).unwrap();
    assert_eq!(report["new_records"], 1);
    assert_eq!(report["total_records"], 21);
    assert!(fs::read(&ledger).unwrap().starts_with(&original));
    let reexported = destination.run(&["memory", "export", &id]);
    assert!(reexported.status.success());
    assert_eq!(reexported.stdout, exported.stdout);
    eprintln!(
        "import_io_fault old_bytes={} failure_exit=2 rollback=exact recovery=passed",
        original.len()
    );
}
