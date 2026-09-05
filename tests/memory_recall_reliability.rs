use serde_json::Value;
use std::collections::BTreeSet;
use std::fs;
use std::io::Read;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Output, Stdio};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, mpsc};
use std::thread;
use std::time::{Duration, Instant};

static NEXT: AtomicU64 = AtomicU64::new(0);

struct Fixture(PathBuf);
struct Running(Option<Child>);

fn drain<R: Read + Send + 'static>(mut stream: R) -> thread::JoinHandle<Vec<u8>> {
    thread::spawn(move || {
        let mut captured = Vec::new();
        stream
            .by_ref()
            .take(2 * 1024 * 1024)
            .read_to_end(&mut captured)
            .unwrap();
        std::io::copy(&mut stream, &mut std::io::sink()).unwrap();
        captured
    })
}

impl Running {
    fn finish(mut self) -> Output {
        let stdout = drain(self.0.as_mut().unwrap().stdout.take().unwrap());
        let stderr = drain(self.0.as_mut().unwrap().stderr.take().unwrap());
        let deadline = Instant::now() + Duration::from_secs(15);
        loop {
            if self.0.as_mut().unwrap().try_wait().unwrap().is_some() {
                let status = self.0.as_mut().unwrap().wait().unwrap();
                return Output {
                    status,
                    stdout: stdout.join().unwrap(),
                    stderr: stderr.join().unwrap(),
                };
            }
            if Instant::now() >= deadline {
                let child = self.0.as_mut().unwrap();
                let _ = child.kill();
                let _ = child.wait();
                let _ = stdout.join();
                let _ = stderr.join();
                panic!("memory CLI exceeded 15-second deadline");
            }
            thread::sleep(Duration::from_millis(1));
        }
    }

    fn interrupt(mut self) -> (Output, bool) {
        let kill_sent = self.0.as_mut().unwrap().kill().is_ok();
        (self.finish(), kill_sent)
    }
}

impl Drop for Running {
    fn drop(&mut self) {
        if let Some(child) = self.0.as_mut() {
            if child.try_wait().ok().flatten().is_none() {
                let _ = child.kill();
            }
            let _ = child.wait();
        }
    }
}

impl Fixture {
    fn new() -> Self {
        loop {
            let root = std::env::temp_dir().join(format!(
                "azdaja-recall-reliability-{}-{}",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            match fs::create_dir(&root) {
                Ok(()) => {
                    for name in ["home", "config", "scope"] {
                        fs::create_dir(root.join(name)).unwrap();
                    }
                    return Self(root);
                }
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
                Err(error) => panic!("cannot create private test fixture: {error}"),
            }
        }
    }

    fn spawn(&self, args: &[&str]) -> Running {
        self.spawn_program(env!("CARGO_BIN_EXE_azdaja"), args)
    }

    fn spawn_program(&self, program: &str, args: &[&str]) -> Running {
        Running(Some(
            Command::new(program)
                .args(args)
                .current_dir(self.0.join("scope"))
                .env("HOME", self.0.join("home"))
                .env("USERPROFILE", self.0.join("home"))
                .env("XDG_CONFIG_HOME", self.0.join("config"))
                .env("XDG_STATE_HOME", self.0.join("state"))
                .env_remove("AZDAJA_HOME")
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn()
                .unwrap(),
        ))
    }

    fn run(&self, args: &[&str]) -> Output {
        self.spawn(args).finish()
    }

    fn add(&self, text: &str) {
        let output = self.run(&["memory", "add", "observation", text, "--global"]);
        assert!(
            output.status.success(),
            "add failed: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }

    fn recall(&self, query: &str) -> Value {
        let output = self.run(&["memory", "recall", query, "--global"]);
        assert!(
            output.status.success(),
            "recall failed: {}",
            String::from_utf8_lossy(&output.stderr)
        );
        assert!(output.stdout.len() <= 64 * 1024);
        assert_eq!(
            output.stdout.iter().filter(|byte| **byte == b'\n').count(),
            1
        );
        let report: Value = serde_json::from_slice(&output.stdout).unwrap();
        assert_eq!(report["method"], "lexical");
        assert_eq!(report["scope"], "global");
        assert_eq!(report["query"], query);
        report
    }

    fn ledger(&self) -> PathBuf {
        self.state_file("global.jsonl")
    }

    fn state_file(&self, name: &str) -> PathBuf {
        fn find(root: &Path, name: &str, found: &mut Vec<PathBuf>) {
            for entry in fs::read_dir(root).unwrap() {
                let entry = entry.unwrap();
                let kind = entry.file_type().unwrap();
                if kind.is_dir() {
                    find(&entry.path(), name, found);
                } else if kind.is_file() && entry.file_name() == name {
                    found.push(entry.path());
                }
            }
        }
        let mut paths = Vec::new();
        find(&self.0.join("state"), name, &mut paths);
        assert_eq!(
            paths.len(),
            1,
            "expected one fixture state file named {name}"
        );
        paths.remove(0)
    }
}

impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

struct StopOnDrop(Arc<AtomicBool>);
impl Drop for StopOnDrop {
    fn drop(&mut self) {
        self.0.store(true, Ordering::Release);
    }
}

#[test]
fn live_readers_observe_coherent_snapshots_during_concurrent_writes() {
    const WRITERS: usize = 4;
    const NOTES: usize = 12;
    let fixture = Fixture::new();
    fixture.add("streamprobe anchor");
    let allowed = std::iter::once("streamprobe anchor".to_owned())
        .chain((0..WRITERS).flat_map(|writer| {
            (0..NOTES).map(move |note| format!("streamprobe writer{writer}note{note}"))
        }))
        .collect::<BTreeSet<_>>();
    let stop = Arc::new(AtomicBool::new(false));
    let (ready_tx, ready_rx) = mpsc::channel();
    let read_count = thread::scope(|scope| {
        let stop_guard = StopOnDrop(stop.clone());
        let readers = (0..4)
            .map(|_| {
                let stop = stop.clone();
                let fixture = &fixture;
                let allowed = &allowed;
                scope.spawn(move || {
                    let mut last_total = 1_u64;
                    let mut reads = 0;
                    while !stop.load(Ordering::Acquire) && reads < 256 {
                        let report = fixture.recall("streamprobe");
                        let total = report["total_matches"].as_u64().unwrap();
                        assert!(
                            total >= last_total,
                            "a fresh reader lost acknowledged history"
                        );
                        assert!(total <= allowed.len() as u64);
                        let matches = report["matches"].as_array().unwrap();
                        assert_eq!(matches.len(), total.min(4) as usize);
                        assert_eq!(report["omitted_matches"], total - matches.len() as u64);
                        assert_eq!(report["omitted_context"], 0);
                        assert!(report["context"].as_array().unwrap().is_empty());
                        let mut ids = BTreeSet::new();
                        for view in matches {
                            assert!(allowed.contains(view["record"]["text"].as_str().unwrap()));
                            assert!(ids.insert(view["record"]["id"].as_str().unwrap()));
                        }
                        last_total = total;
                        reads += 1;
                    }
                    reads
                })
            })
            .collect::<Vec<_>>();
        let mut resume = Vec::new();
        let writers = (0..WRITERS)
            .map(|writer| {
                let (tx, rx) = mpsc::channel();
                resume.push(tx);
                let ready = ready_tx.clone();
                let fixture = &fixture;
                scope.spawn(move || {
                    for note in 0..NOTES {
                        if note == NOTES / 2 {
                            ready.send(writer).unwrap();
                            rx.recv_timeout(Duration::from_secs(30))
                                .expect("coordinator did not release writer");
                        }
                        fixture.add(&format!("streamprobe writer{writer}note{note}"));
                    }
                })
            })
            .collect::<Vec<_>>();
        for _ in 0..WRITERS {
            ready_rx
                .recv_timeout(Duration::from_secs(30))
                .expect("writer failed before midpoint");
        }
        // Writers remain alive with half their work pending. This guarantees a
        // genuine intermediate persisted state instead of only post-join reads.
        let checkpoint = fixture.recall("streamprobe");
        assert_eq!(checkpoint["total_matches"], 1 + WRITERS * (NOTES / 2));
        for tx in resume {
            tx.send(()).unwrap();
        }
        for writer in writers {
            writer.join().unwrap();
        }
        drop(stop_guard);
        readers
            .into_iter()
            .map(|reader| reader.join().unwrap())
            .sum::<usize>()
    });
    assert!(read_count >= 4);
    for text in &allowed {
        let query = text.split_whitespace().last().unwrap();
        let report = fixture.recall(query);
        assert_eq!(report["total_matches"], 1);
        assert_eq!(report["matches"][0]["record"]["text"], text.as_str());
    }
    eprintln!(
        "live_recall readers=4 writers={WRITERS} acknowledged_writes={} coherent_reads={read_count} midpoint_records=25 final_records=49",
        WRITERS * NOTES
    );
}

#[test]
fn timed_writer_termination_attempts_preserve_acknowledged_records_and_allow_recovery() {
    let fixture = Fixture::new();
    let mut committed = BTreeSet::new();
    let mut permitted = BTreeSet::new();
    for index in 0..24 {
        let text = format!("stable{index:03} {}", "x".repeat(3000));
        fixture.add(&text);
        committed.insert(text.clone());
        permitted.insert(text);
    }
    let mut interrupted = 0;
    let delays = [0, 50, 200, 1000, 3000, 5000];
    for attempt in 0..24 {
        let text = format!("interrupted{attempt:03} {}", "y".repeat(3900));
        permitted.insert(text.clone());
        let child = fixture.spawn(&["memory", "add", "observation", &text, "--global"]);
        thread::sleep(Duration::from_micros(delays[attempt % delays.len()]));
        let (output, kill_sent) = child.interrupt();
        if output.status.success() {
            committed.insert(text);
        } else {
            assert!(kill_sent, "writer failed without a successful kill request");
            #[cfg(unix)]
            {
                use std::os::unix::process::ExitStatusExt;
                assert_eq!(
                    output.status.signal(),
                    Some(9),
                    "writer failure was not the intended SIGKILL"
                );
            }
            interrupted += 1;
        }
        let before = fixture.recall("stable000");
        assert_eq!(before["total_matches"], 1);
        let recovery = format!("recovery{attempt:03}");
        fixture.add(&recovery);
        committed.insert(recovery.clone());
        permitted.insert(recovery);
    }
    // The mandatory lock-wait interruption test below guarantees a real kill.
    // These timing probes additionally explore the write lifecycle, without
    // turning scheduler speed into a flaky requirement that at least one wins.
    let raw = fs::read_to_string(fixture.ledger()).unwrap();
    assert!(raw.ends_with('\n'));
    let mut actual = BTreeSet::new();
    let mut ids = BTreeSet::new();
    for line in raw.lines() {
        let record: Value =
            serde_json::from_str(line).expect("interrupted writer left partial JSON");
        assert!(ids.insert(record["id"].as_str().unwrap().to_owned()));
        let text = record["text"].as_str().unwrap().to_owned();
        assert!(
            permitted.contains(&text),
            "ledger contains a partial or unknown record"
        );
        assert!(actual.insert(text), "ledger duplicated a note");
    }
    assert!(
        committed.is_subset(&actual),
        "an acknowledged note was lost"
    );
    for text in &committed {
        let report = fixture.recall(text.split_whitespace().next().unwrap());
        assert_eq!(report["total_matches"], 1);
        assert_eq!(report["matches"][0]["record"]["text"], text.as_str());
    }
    eprintln!(
        "writer_recovery attempts=24 interrupted={interrupted} acknowledged={} final_records={}",
        committed.len(),
        actual.len()
    );
}

#[cfg(unix)]
#[test]
fn symlinked_ledger_is_refused_without_exposing_or_modifying_victim() {
    use std::os::unix::fs::symlink;
    let fixture = Fixture::new();
    fixture.add("privatevictim secret fixture note");
    let ledger = fixture.ledger();
    let victim = fixture.0.join("victim.jsonl");
    fs::rename(&ledger, &victim).unwrap();
    let before = fs::read(&victim).unwrap();
    symlink(&victim, &ledger).unwrap();
    let output = fixture.run(&["memory", "recall", "privatevictim", "--global"]);
    assert!(!output.status.success(), "recall followed a ledger symlink");
    assert!(output.stdout.is_empty());
    assert!(!String::from_utf8_lossy(&output.stderr).contains("secret fixture note"));
    assert_eq!(fs::read(&victim).unwrap(), before);
    assert!(
        fs::symlink_metadata(&ledger)
            .unwrap()
            .file_type()
            .is_symlink()
    );
}

#[cfg(unix)]
#[test]
fn hardlinked_ledger_is_refused_without_mutating_either_name() {
    use std::os::unix::fs::MetadataExt;
    let fixture = Fixture::new();
    fixture.add("hardlinkvictim retained fixture note");
    let ledger = fixture.ledger();
    let victim = fixture.0.join("victim.jsonl");
    fs::hard_link(&ledger, &victim).unwrap();
    let before = fs::read(&victim).unwrap();
    let output = fixture.run(&["memory", "recall", "hardlinkvictim", "--global"]);
    assert!(
        !output.status.success(),
        "recall accepted a multiply linked private ledger"
    );
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read(&victim).unwrap(), before);
    assert_eq!(fs::read(&ledger).unwrap(), before);
    assert_eq!(fs::metadata(&ledger).unwrap().nlink(), 2);
}

#[cfg(unix)]
#[test]
fn world_readable_ledger_is_refused_without_permission_repair() {
    use std::os::unix::fs::PermissionsExt;
    let fixture = Fixture::new();
    fixture.add("permissionprobe retained fixture note");
    let ledger = fixture.ledger();
    fs::set_permissions(&ledger, fs::Permissions::from_mode(0o644)).unwrap();
    let before = fs::read(&ledger).unwrap();
    let output = fixture.run(&["memory", "recall", "permissionprobe", "--global"]);
    assert!(
        !output.status.success(),
        "recall accepted a world-readable private ledger"
    );
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read(&ledger).unwrap(), before);
    assert_eq!(
        fs::metadata(&ledger).unwrap().permissions().mode() & 0o777,
        0o644
    );
}

#[cfg(unix)]
#[test]
fn file_size_limit_failure_keeps_the_old_ledger_and_releases_writer_custody() {
    let fixture = Fixture::new();
    for index in 0..12 {
        fixture.add(&format!("fsize{index:03} {}", "z".repeat(3000)));
    }
    let ledger = fixture.ledger();
    let before = fs::read(&ledger).unwrap();
    assert!(before.len() > 16 * 1024);
    let output = fixture.spawn_program("/bin/sh", &[
        "-c",
        "ulimit -c 0 || exit 96; ulimit -f 1 || exit 97; printf 'FSIZE_LIMIT_SET\\n' >&2; exec \"$@\"",
        "azdaja-fsize-probe",
        env!("CARGO_BIN_EXE_azdaja"),
        "memory", "add", "observation", "fsize_failed_transaction", "--global",
    ]).finish();
    assert!(String::from_utf8_lossy(&output.stderr).starts_with("FSIZE_LIMIT_SET\n"));
    assert!(
        !output.status.success(),
        "writer ignored the enforced file-size limit"
    );
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read(&ledger).unwrap(), before);
    let missing = fixture.recall("fsize_failed_transaction");
    assert_eq!(missing["total_matches"], 0);
    fixture.add("fsize_recovery");
    assert_eq!(fixture.recall("fsize_recovery")["total_matches"], 1);
    for index in 0..12 {
        assert_eq!(
            fixture.recall(&format!("fsize{index:03}"))["total_matches"],
            1
        );
    }
    eprintln!(
        "fsize_fault old_ledger_bytes={} rollback=exact recovery=passed",
        before.len()
    );
}

#[test]
fn full_record_capacity_refuses_new_notes_without_evicting_acknowledged_history() {
    let fixture = Fixture::new();
    for index in 0..256 {
        fixture.add(&format!("capacity{index:03}"));
    }
    let ledger = fixture.ledger();
    let before = fs::read(&ledger).unwrap();
    let output = fixture.run(&[
        "memory",
        "add",
        "observation",
        "capacity_overflow",
        "--global",
    ]);
    assert!(
        !output.status.success(),
        "full store silently accepted another note"
    );
    assert!(output.stdout.is_empty());
    assert_eq!(
        fs::read(&ledger).unwrap(),
        before,
        "rejected write changed existing history"
    );
    assert_eq!(fixture.recall("capacity_overflow")["total_matches"], 0);
    for index in [0, 127, 255] {
        let text = format!("capacity{index:03}");
        let report = fixture.recall(&text);
        assert_eq!(report["total_matches"], 1);
        assert_eq!(report["matches"][0]["record"]["text"], text);
    }
    eprintln!("record_capacity accepted=256 overflow=refused prior_history=byte_identical");
}

#[test]
fn utf8_byte_capacity_refusal_preserves_history_and_allows_a_smaller_write() {
    const LIMIT: usize = 512 * 1024;
    let fixture = Fixture::new();
    fixture.add("bytecapacityanchor");
    let ledger = fixture.ledger();
    let mut accepted = Vec::new();
    let mut rejected = false;
    for index in 0..40 {
        let text = format!("unicode{index:03} {}", "🦀".repeat(4080));
        assert!(text.chars().count() <= 4096);
        let before = fs::read(&ledger).unwrap();
        let output = fixture.run(&["memory", "add", "observation", &text, "--global"]);
        if output.status.success() {
            assert!(fs::metadata(&ledger).unwrap().len() <= LIMIT as u64);
            accepted.push(text);
        } else {
            assert!(output.stdout.is_empty());
            assert_eq!(fs::read(&ledger).unwrap(), before);
            rejected = true;
            break;
        }
    }
    assert!(
        rejected,
        "byte cap was not reached before 40 valid Unicode notes"
    );
    assert!(!accepted.is_empty());
    let remaining = LIMIT - fs::metadata(&ledger).unwrap().len() as usize;
    assert!(
        remaining > 1024,
        "fixture must leave room for a small recovery note"
    );
    fixture.add("bytecapacityrecovery");
    assert_eq!(fixture.recall("bytecapacityrecovery")["total_matches"], 1);
    assert_eq!(fixture.recall("bytecapacityanchor")["total_matches"], 1);
    for text in &accepted {
        let report = fixture.recall(text.split_whitespace().next().unwrap());
        assert_eq!(report["total_matches"], 1);
        assert_eq!(report["matches"][0]["record"]["text"], text.as_str());
    }
    eprintln!(
        "byte_capacity unicode_notes={} free_bytes_before_recovery={remaining} oversized_write=refused history=preserved",
        accepted.len()
    );
}

#[test]
fn killed_writer_while_store_lock_is_held_preserves_history_and_recovery() {
    let fixture = Fixture::new();
    fixture.add("lockwaitanchor");
    let ledger = fixture.ledger();
    let before = fs::read(&ledger).unwrap();
    let lock = fs::OpenOptions::new()
        .read(true)
        .write(true)
        .open(fixture.state_file("global.lock"))
        .unwrap();
    lock.lock().unwrap();
    let mut child = fixture.spawn(&[
        "memory",
        "add",
        "observation",
        "lockwaitunacknowledged",
        "--global",
    ]);
    // Liveness does not prove the child has reached its lock syscall.
    // This case guarantees a kill while custody is held, not a crash mid-write.
    thread::sleep(Duration::from_millis(20));
    assert!(
        child.0.as_mut().unwrap().try_wait().unwrap().is_none(),
        "writer exited while the fixture held the store lock"
    );
    let (output, kill_sent) = child.interrupt();
    assert!(kill_sent);
    assert!(!output.status.success());
    #[cfg(unix)]
    {
        use std::os::unix::process::ExitStatusExt;
        assert_eq!(output.status.signal(), Some(9));
    }
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read(&ledger).unwrap(), before);
    drop(lock);
    assert_eq!(fixture.recall("lockwaitunacknowledged")["total_matches"], 0);
    fixture.add("lockwaitrecovery");
    assert_eq!(fixture.recall("lockwaitanchor")["total_matches"], 1);
    assert_eq!(fixture.recall("lockwaitrecovery")["total_matches"], 1);
    eprintln!(
        "held_lock_fault deliberate_kill=confirmed prior_history=byte_identical recovery=passed"
    );
}
