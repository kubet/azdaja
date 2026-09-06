//! Transfer acceptance through the existing HTTP installer's verified executable.
//! Never builds, copies, installs, or substitutes an executable.
use serde_json::Value;
use std::cell::Cell;
use std::collections::BTreeMap;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, ExitStatus, Stdio};
use std::thread;
use std::time::{Duration, Instant};

struct Running(Option<Child>);
impl Drop for Running {
    fn drop(&mut self) {
        if let Some(child) = &mut self.0 {
            let _ = child.kill();
            let _ = child.wait();
        }
    }
}

struct Reply {
    status: ExitStatus,
    out: Vec<u8>,
    err: Vec<u8>,
}
impl Reply {
    fn success(self) -> Vec<u8> {
        assert!(
            self.status.success(),
            "command failed: {}",
            String::from_utf8_lossy(&self.err)
        );
        self.out
    }
    fn refused(self) {
        assert_eq!(
            self.status.code(),
            Some(2),
            "not a clean CLI refusal: {}",
            String::from_utf8_lossy(&self.err)
        );
        assert!(self.out.is_empty(), "refusal emitted partial data");
        assert!(!self.err.is_empty(), "refusal lacked a diagnostic");
        let diagnostic = String::from_utf8_lossy(&self.err);
        assert!(
            !diagnostic.contains("Unicode 🦀"),
            "refusal exposed note text"
        );
        assert!(
            !diagnostic.contains("contrary evidence without the search word"),
            "refusal exposed context text"
        );
    }
}

struct Harness<'a> {
    binary: &'a Path,
    captures: PathBuf,
    sequence: Cell<usize>,
}
impl Harness<'_> {
    fn run(&self, mut command: Command) -> Reply {
        const CAP: u64 = 2 * 1024 * 1024;
        let index = self.sequence.get();
        self.sequence.set(index + 1);
        let out = self.captures.join(format!("{index}.out"));
        let err = self.captures.join(format!("{index}.err"));
        command
            .stdin(Stdio::null())
            .stdout(fs::File::create(&out).unwrap())
            .stderr(fs::File::create(&err).unwrap());
        let mut running = Running(Some(command.spawn().expect("spawn fixture command")));
        let deadline = Instant::now() + Duration::from_secs(30);
        let status = loop {
            assert!(
                fs::metadata(&out).unwrap().len() <= CAP,
                "stdout exceeded capture cap"
            );
            assert!(
                fs::metadata(&err).unwrap().len() <= CAP,
                "stderr exceeded capture cap"
            );
            if let Some(status) = running.0.as_mut().unwrap().try_wait().unwrap() {
                running.0.take();
                break status;
            }
            assert!(
                Instant::now() < deadline,
                "installed command exceeded deadline"
            );
            thread::sleep(Duration::from_millis(10));
        };
        assert!(fs::metadata(&out).unwrap().len() <= CAP);
        assert!(fs::metadata(&err).unwrap().len() <= CAP);
        Reply {
            status,
            out: fs::read(out).unwrap(),
            err: fs::read(err).unwrap(),
        }
    }

    fn cli(&self, cwd: &Path, home: &Path, mode: &str, args: &[&str]) -> Reply {
        let mut command = Command::new(self.binary);
        command
            .env_clear()
            .env("PATH", std::env::var_os("PATH").expect("test runner PATH"));
        command
            .args(args)
            .current_dir(cwd)
            .env("HOME", home)
            .env("USERPROFILE", home)
            .env("AZDAJA_PROJECT_MEMORY", mode)
            .env_remove("AZDAJA_HOME")
            .env_remove("XDG_STATE_HOME");
        self.run(command)
    }

    fn git(&self, cwd: &Path, home: &Path, args: &[&str]) {
        let mut command = Command::new("git");
        command
            .env_clear()
            .env("PATH", std::env::var_os("PATH").expect("test runner PATH"));
        command
            .args([
                "-c",
                "core.hooksPath=/dev/null",
                "-c",
                "commit.gpgsign=false",
                "-c",
                "user.name=Transfer Fixture",
                "-c",
                "user.email=fixture@example.invalid",
            ])
            .args(args)
            .current_dir(cwd)
            .env("HOME", home)
            .env("GIT_CONFIG_NOSYSTEM", "1")
            .env("GIT_CONFIG_GLOBAL", "/dev/null")
            .env("GIT_TERMINAL_PROMPT", "0");
        self.run(command).success();
    }

    fn recall(&self, cwd: &Path, home: &Path, global: bool) -> Value {
        let mut args = vec!["memory", "recall", "transferanchor"];
        if global {
            args.push("--global");
        }
        let bytes = self.cli(cwd, home, "on", &args).success();
        assert!(bytes.len() <= 64 * 1024);
        serde_json::from_slice(&bytes).unwrap()
    }
}

#[derive(Debug, PartialEq, Eq)]
struct Entry {
    directory: bool,
    mode: u32,
    bytes: Vec<u8>,
}
fn snapshot(root: &Path) -> BTreeMap<PathBuf, Entry> {
    fn visit(root: &Path, path: &Path, entries: &mut BTreeMap<PathBuf, Entry>) {
        use std::os::unix::fs::PermissionsExt;
        let metadata = fs::symlink_metadata(path).unwrap();
        assert!(
            !metadata.file_type().is_symlink(),
            "unexpected fixture symlink"
        );
        assert!(
            metadata.is_dir() || metadata.is_file(),
            "unexpected fixture special file"
        );
        entries.insert(
            path.strip_prefix(root).unwrap().to_path_buf(),
            Entry {
                directory: metadata.is_dir(),
                mode: metadata.permissions().mode(),
                bytes: if metadata.is_file() {
                    fs::read(path).unwrap()
                } else {
                    Vec::new()
                },
            },
        );
        if metadata.is_dir() {
            for entry in fs::read_dir(path).unwrap() {
                visit(root, &entry.unwrap().path(), entries);
            }
        }
    }
    let mut entries = BTreeMap::new();
    match fs::symlink_metadata(root) {
        Ok(_) => visit(root, root, &mut entries),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {}
        Err(error) => panic!("cannot inspect fixture: {error}"),
    }
    entries
}

fn records(report: &Value) -> BTreeMap<String, Value> {
    let mut seen = std::collections::BTreeSet::new();
    report["matches"]
        .as_array()
        .unwrap()
        .iter()
        .chain(report["context"].as_array().unwrap())
        .map(|item| {
            let record = item["record"].clone();
            assert!(
                seen.insert(record["id"].as_str().unwrap().to_owned()),
                "recall duplicated a record"
            );
            (record["id"].as_str().unwrap().to_owned(), record)
        })
        .collect()
}

#[test]
#[should_panic(expected = "recall duplicated a record")]
fn duplicate_context_cannot_be_hidden_by_record_map_collection() {
    let report = serde_json::json!({
        "matches": [{"record": {"id": "duplicate-fixture-id"}}],
        "context": [{"record": {"id": "duplicate-fixture-id"}}]
    });
    records(&report);
}

pub(super) fn verify(root: &Path, installed: &Path) {
    let fixture = root.join("http-installed-transfer");
    fs::create_dir(&fixture).unwrap();
    let home_a = fixture.join("home-a");
    let home_b = fixture.join("home-b");
    let source = fixture.join("source");
    let destination = fixture.join("clone");
    let captures = fixture.join("captures");
    for directory in [&home_a, &home_b, &source, &captures] {
        fs::create_dir(directory).unwrap();
    }
    let h = Harness {
        binary: installed,
        captures,
        sequence: Cell::new(0),
    };
    let help = h
        .cli(&source, &home_a, "on", &["memory", "--help"])
        .success();
    let help = String::from_utf8(help).unwrap();
    assert!(help.contains("Import defaults to a no-write dry-run"));
    assert!(help.contains("--with-context"));
    h.git(&source, &home_a, &["init", "--quiet"]);
    fs::write(
        source.join("README.md"),
        "Synthetic installed-transfer fixture\n",
    )
    .unwrap();
    h.git(&source, &home_a, &["add", "README.md"]);
    h.git(&source, &home_a, &["commit", "--quiet", "-m", "fixture"]);
    h.cli(
        &source,
        &home_a,
        "on",
        &[
            "memory",
            "add",
            "observation",
            "transferanchor Unicode 🦀\n$(this is inert note text)",
            "--tag",
            "file:src/lib.rs",
        ],
    )
    .success();
    let initial = h.recall(&source, &home_a, false);
    let anchor = initial["matches"][0]["record"]["id"]
        .as_str()
        .unwrap()
        .to_owned();
    let link = format!("related-to:{anchor}");
    h.cli(
        &source,
        &home_a,
        "on",
        &[
            "memory",
            "add",
            "disagreement",
            "contrary evidence without the search word",
            "--link",
            &link,
        ],
    )
    .success();
    h.cli(
        &source,
        &home_a,
        "on",
        &[
            "memory",
            "add",
            "observation",
            "personalglobal private unrelated note",
            "--global",
        ],
    )
    .success();
    let expected_report = h.recall(&source, &home_a, false);
    let expected_records = records(&expected_report);
    assert_eq!(expected_records.len(), 2);
    let source_before = snapshot(&source.join(".azdaja"));
    let personal_before = snapshot(&home_a);
    h.cli(&source, &home_a, "on", &["memory", "export", &anchor])
        .refused();
    let bundle = h
        .cli(
            &source,
            &home_a,
            "on",
            &["memory", "export", &anchor, "--with-context"],
        )
        .success();
    assert!(bundle.len() <= 1024 * 1024);
    let _: Value = serde_json::from_slice(&bundle).unwrap();
    assert!(!String::from_utf8_lossy(&bundle).contains("personalglobal"));
    assert_eq!(
        bundle,
        h.cli(
            &source,
            &home_a,
            "on",
            &["memory", "export", &anchor, "--with-context"]
        )
        .success()
    );
    assert_eq!(snapshot(&source.join(".azdaja")), source_before);
    assert_eq!(snapshot(&home_a), personal_before);

    h.git(
        &fixture,
        &home_b,
        &[
            "clone",
            "--quiet",
            source.to_str().unwrap(),
            destination.to_str().unwrap(),
        ],
    );
    assert!(
        !destination.join(".azdaja").exists(),
        "ordinary clone included private memories"
    );
    let bundle_path = fixture.join("reviewed-bundle.json");
    fs::write(&bundle_path, &bundle).unwrap();
    let bundle_arg = bundle_path.to_str().unwrap();
    let destination_before = snapshot(&destination);
    let home_before = snapshot(&home_b);
    let preview = h
        .cli(
            &destination,
            &home_b,
            "on",
            &["memory", "import", bundle_arg],
        )
        .success();
    let _: Value = serde_json::from_slice(&preview).unwrap();
    assert_eq!(
        snapshot(&destination),
        destination_before,
        "preview changed clone"
    );
    assert_eq!(
        snapshot(&home_b),
        home_before,
        "preview changed personal state"
    );
    for suffix in [vec![], vec!["--apply"]] {
        let mut args = vec!["memory", "import", bundle_arg];
        args.extend(suffix);
        h.cli(&destination, &home_b, "off", &args).refused();
    }
    assert_eq!(snapshot(&destination), destination_before);
    assert_eq!(snapshot(&home_b), home_before);

    h.cli(
        &destination,
        &home_b,
        "on",
        &["memory", "import", bundle_arg, "--apply"],
    )
    .success();
    let imported = h.recall(&destination, &home_b, false);
    assert_eq!(
        records(&imported),
        expected_records,
        "import changed complete records or lost contrary context"
    );
    assert!(imported["caveat"].as_str().unwrap().contains("untrusted"));
    assert_eq!(
        snapshot(&home_b),
        home_before,
        "project apply leaked into personal state"
    );
    let export_args = ["memory", "export", &anchor, "--with-context"];
    assert_eq!(
        h.cli(&destination, &home_b, "on", &export_args).success(),
        bundle
    );
    let imported_before = snapshot(&destination);
    h.cli(
        &destination,
        &home_b,
        "on",
        &["memory", "import", bundle_arg, "--apply"],
    )
    .success();
    assert_eq!(
        snapshot(&destination),
        imported_before,
        "idempotent apply rewrote state"
    );

    let mut tampered = bundle.clone();
    let offset = tampered
        .windows(b"transferanchor".len())
        .position(|bytes| bytes == b"transferanchor")
        .unwrap();
    tampered[offset] = b'T';
    let _: Value = serde_json::from_slice(&tampered).unwrap();
    let damaged_path = fixture.join("tampered-bundle.json");
    fs::write(&damaged_path, tampered).unwrap();
    for suffix in [vec![], vec!["--apply"]] {
        let mut args = vec!["memory", "import", damaged_path.to_str().unwrap()];
        args.extend(suffix);
        h.cli(&destination, &home_b, "on", &args).refused();
    }
    assert_eq!(
        snapshot(&destination),
        imported_before,
        "tampered import changed destination"
    );

    let ledger = destination.join(".azdaja/memory/global.jsonl");
    let original = fs::read(&ledger).expect("actual imported project ledger must exist");
    assert!(String::from_utf8_lossy(&original).contains(&anchor));
    fs::write(&ledger, b"{broken ledger\n").unwrap();
    let corrupt_before = snapshot(&destination);
    h.cli(
        &destination,
        &home_b,
        "on",
        &["memory", "import", bundle_arg, "--apply"],
    )
    .refused();
    h.cli(&destination, &home_b, "on", &export_args).refused();
    h.cli(
        &destination,
        &home_b,
        "on",
        &["memory", "recall", "transferanchor"],
    )
    .refused();
    assert_eq!(
        snapshot(&destination),
        corrupt_before,
        "corrupt history was repaired or rewritten"
    );
    fs::write(&ledger, original).unwrap();
    assert_eq!(
        h.cli(&destination, &home_b, "on", &export_args).success(),
        bundle
    );
    assert_eq!(
        records(&h.recall(&destination, &home_b, false)),
        expected_records
    );

    let project_before = snapshot(&destination);
    let global_preview = h
        .cli(
            &destination,
            &home_b,
            "off",
            &["memory", "import", bundle_arg, "--global"],
        )
        .success();
    let _: Value = serde_json::from_slice(&global_preview).unwrap();
    assert_eq!(
        snapshot(&home_b),
        home_before,
        "global preview initialized personal state"
    );
    h.cli(
        &destination,
        &home_b,
        "off",
        &["memory", "import", bundle_arg, "--global", "--apply"],
    )
    .success();
    assert_eq!(
        records(&h.recall(&destination, &home_b, true)),
        expected_records
    );
    assert_eq!(
        snapshot(&destination),
        project_before,
        "explicit global import changed project state"
    );
    assert_eq!(snapshot(&source.join(".azdaja")), source_before);
    assert_eq!(snapshot(&home_a), personal_before);
    assert_eq!(
        fs::read(&bundle_path).unwrap(),
        bundle,
        "import rewrote the supplied bundle"
    );
    eprintln!(
        "http_installed_transfer clone=passed export_consent=passed preview_no_write=passed exact_records=2 idempotent=passed tamper_refusal=passed corrupt_recovery=passed off_global_isolation=passed"
    );
}
