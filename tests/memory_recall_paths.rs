use serde_json::Value;
use std::{
    fs,
    path::PathBuf,
    process::{Command, Output},
    time::{SystemTime, UNIX_EPOCH},
};

struct Fixture(PathBuf);

impl Fixture {
    fn new() -> Self {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let nonce = format!("{nonce}-{}", {
            static NEXT: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
            NEXT.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
        });
        let root =
            std::env::temp_dir().join(format!("az-recall-paths-{}-{nonce}", std::process::id()));
        fs::create_dir_all(root.join("home")).unwrap();
        fs::create_dir_all(root.join("scope")).unwrap();
        Self(root)
    }

    fn command(&self, route: usize) -> Command {
        let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
        command
            .current_dir(self.0.join("scope"))
            .env("HOME", self.0.join("home"))
            .env("XDG_CONFIG_HOME", self.0.join("config"))
            .env_remove("AZDAJA_HOME")
            .env_remove("XDG_STATE_HOME");
        match route {
            0 => {
                command.env("AZDAJA_HOME", self.root(route));
            }
            1 => {
                command.env("XDG_STATE_HOME", self.0.join("state Ž's"));
            }
            2 => {
                command.env("XDG_STATE_HOME", "relative-state");
            }
            3 => {
                command.env("XDG_STATE_HOME", "");
            }
            4 => {}
            _ => unreachable!(),
        }
        command
    }

    fn root(&self, route: usize) -> PathBuf {
        match route {
            0 => self.0.join("explicit Ž's"),
            1 => self.0.join("state Ž's/azdaja"),
            _ => self.0.join("home/.local/state/azdaja"),
        }
    }

    fn recall(&self, route: usize) -> Output {
        self.command(route)
            .args(["memory", "recall", "needle"])
            .output()
            .unwrap()
    }
}

impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn success(output: &Output) -> Value {
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(output.stderr.is_empty());
    serde_json::from_slice(&output.stdout).unwrap()
}

#[test]
fn recall_matches_writer_path_policy_without_initializing_empty_roots() {
    for route in 0..5 {
        let fixture = Fixture::new();
        let before = success(&fixture.recall(route));
        assert_eq!(before["matches"], serde_json::json!([]));
        assert!(
            !fixture.root(route).exists(),
            "route {route} initialized state"
        );
        assert!(!fixture.0.join("home/.local").exists());
        assert!(!fixture.0.join("state Ž's").exists());
        assert!(!fixture.0.join("config").exists());
        let added = fixture
            .command(route)
            .args(["memory", "add", "decision", "needle route parity"])
            .output()
            .unwrap();
        assert!(
            added.status.success(),
            "route {route}: {}",
            String::from_utf8_lossy(&added.stderr)
        );
        assert!(
            fixture.root(route).is_dir(),
            "writer route {route} differs from documented path"
        );
        let after = success(&fixture.recall(route));
        assert_eq!(after["schema_version"], 1);
        assert_eq!(after["matches"][0]["record"]["text"], "needle route parity");
    }
}

#[test]
fn invalid_authoritative_state_paths_fail_without_creating_fallback_state() {
    for invalid in ["", "relative-state"] {
        let fixture = Fixture::new();
        let output = fixture
            .command(1)
            .env("AZDAJA_HOME", invalid)
            .args(["memory", "recall", "needle"])
            .output()
            .unwrap();
        assert!(!output.status.success());
        assert!(output.stdout.is_empty());
        assert!(!fixture.0.join("state Ž's").exists());
        assert!(!fixture.0.join("scope/relative-state").exists());
        assert!(!fixture.0.join("home/.local").exists());
    }
}

#[test]
fn outgoing_evidence_is_returned_even_without_query_words() {
    let fixture = Fixture::new();
    let added = fixture
        .command(0)
        .args(["memory", "add", "observation", "antecedent detail"])
        .output()
        .unwrap();
    assert!(added.status.success());
    let previous = fixture
        .command(0)
        .args(["memory", "recall", "antecedent"])
        .output()
        .unwrap();
    let previous = success(&previous);
    let evidence_id = previous["matches"][0]["record"]["id"].as_str().unwrap();
    let added = fixture
        .command(0)
        .args([
            "memory",
            "add",
            "decision",
            "needle choice",
            "--link",
            &format!("derived-from:{evidence_id}"),
        ])
        .output()
        .unwrap();
    assert!(
        added.status.success(),
        "{}",
        String::from_utf8_lossy(&added.stderr)
    );
    let report = success(&fixture.recall(0));
    assert_eq!(report["matches"].as_array().unwrap().len(), 1);
    assert_eq!(report["context"].as_array().unwrap().len(), 1);
    assert_eq!(report["context"][0]["record"]["id"], evidence_id);
    assert_eq!(report["context"][0]["record"]["text"], "antecedent detail");
    assert_eq!(
        report["context"][0]["backlinks"][0]["source_id"],
        report["matches"][0]["record"]["id"]
    );
}

fn snapshot(root: &std::path::Path) -> Vec<(PathBuf, Option<Vec<u8>>)> {
    let mut pending = vec![root.to_owned()];
    let mut result = Vec::new();
    while let Some(directory) = pending.pop() {
        for entry in fs::read_dir(&directory).unwrap() {
            let entry = entry.unwrap();
            let path = entry.path();
            let metadata = fs::symlink_metadata(&path).unwrap();
            if metadata.is_dir() {
                result.push((path.strip_prefix(root).unwrap().to_owned(), None));
                pending.push(path);
            } else {
                assert!(metadata.is_file() && !metadata.file_type().is_symlink());
                result.push((
                    path.strip_prefix(root).unwrap().to_owned(),
                    Some(fs::read(path).unwrap()),
                ));
            }
        }
    }
    result.sort_by(|a, b| a.0.cmp(&b.0));
    result
}

#[test]
fn global_only_store_and_foreign_folder_recall_do_not_initialize_scope_state() {
    let fixture = Fixture::new();
    let added = fixture
        .command(0)
        .args(["memory", "add", "decision", "needle global", "--global"])
        .output()
        .unwrap();
    assert!(added.status.success());
    let other = fixture.0.join("other");
    fs::create_dir(&other).unwrap();
    let before = snapshot(&fixture.0);
    assert!(
        success(&fixture.recall(0))["matches"]
            .as_array()
            .unwrap()
            .is_empty()
    );
    let output = fixture
        .command(0)
        .current_dir(&other)
        .args(["memory", "recall", "needle"])
        .output()
        .unwrap();
    assert!(success(&output)["matches"].as_array().unwrap().is_empty());
    assert_eq!(before, snapshot(&fixture.0));
}

#[test]
fn empty_private_state_root_is_not_initialized_by_recall() {
    let fixture = Fixture::new();
    let root = fixture.root(0);
    fs::create_dir(&root).unwrap();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&root, fs::Permissions::from_mode(0o700)).unwrap();
    }
    let before = snapshot(&fixture.0);
    assert!(
        success(&fixture.recall(0))["matches"]
            .as_array()
            .unwrap()
            .is_empty()
    );
    let output = fixture
        .command(0)
        .args(["memory", "recall", "needle", "--global"])
        .output()
        .unwrap();
    assert!(success(&output)["matches"].as_array().unwrap().is_empty());
    assert_eq!(before, snapshot(&fixture.0));
}

#[cfg(unix)]
#[test]
fn unsafe_state_roots_are_refused_without_chmod_or_link_mutation() {
    use std::os::unix::fs::{PermissionsExt, symlink};
    let fixture = Fixture::new();
    let added = fixture
        .command(0)
        .args(["memory", "add", "decision", "needle private"])
        .output()
        .unwrap();
    assert!(added.status.success());
    let root = fixture.root(0);
    let alias = fixture.0.join("alias");
    symlink(&root, &alias).unwrap();
    let output = fixture
        .command(0)
        .env("AZDAJA_HOME", &alias)
        .args(["memory", "recall", "needle"])
        .output()
        .unwrap();
    assert!(!output.status.success());
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read_link(&alias).unwrap(), root);
    fs::set_permissions(&root, fs::Permissions::from_mode(0o755)).unwrap();
    let output = fixture.recall(0);
    assert!(!output.status.success());
    assert!(output.stdout.is_empty());
    assert_eq!(
        fs::metadata(&root).unwrap().permissions().mode() & 0o777,
        0o755
    );
}
