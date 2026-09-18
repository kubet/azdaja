//! Public batch CLI boundary. All provider-capable tests deliberately lack a key.
use serde_json::{Value, json};
use std::{
    fs,
    path::PathBuf,
    process::{Command, Output},
    sync::atomic::{AtomicU64, Ordering},
    time::{SystemTime, UNIX_EPOCH},
};

static NEXT: AtomicU64 = AtomicU64::new(0);
struct Fixture {
    root: PathBuf,
}
impl Fixture {
    fn new(enabled: bool) -> Self {
        let base = std::env::var_os("JCODE_SCRATCH_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(std::env::temp_dir);
        let root = base.join(format!(
            "az-batch-cli-{}-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&root).unwrap();
        fs::write(
            root.join("config.toml"),
            format!("[judge]\nenabled = {enabled}\nkey_env = \"AZ_BATCH_NO_CREDENTIAL_IN_TEST\"\n"),
        )
        .unwrap();
        Self { root }
    }
    fn plan(&self, text: &str) {
        fs::write(self.root.join("plan.jsonl"), text).unwrap();
    }
    fn invoke(&self, args: &[&str]) -> Output {
        let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
        command
            .env_clear()
            .current_dir(&self.root)
            .env("HOME", self.root.join("home"))
            .env("AZDAJA_HOME", self.root.join("state"))
            .env("AZDAJA_CONFIG", self.root.join("config.toml"));
        #[cfg(windows)]
        if let Some(root) = std::env::var_os("SystemRoot") {
            command.env("SystemRoot", root);
        }
        command.args(args).output().unwrap()
    }
    fn batch(&self, flags: &[&str]) -> Output {
        let mut args = vec!["jev", "batch", "--input", "plan.jsonl"];
        args.extend_from_slice(flags);
        self.invoke(&args)
    }
    fn no_state(&self) {
        assert!(!self.root.join("state").exists());
        assert!(!self.root.join("job").exists());
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.root);
    }
}
fn row(id: &str) -> Value {
    json!({"id":id,"state":"The original signed clause.","questions":{"q":{"type":"noul","instructions":"Does the source describe a signed clause?"}}})
}
fn execute() -> Vec<&'static str> {
    vec![
        "--execute",
        "--output",
        "job",
        "--max-requests",
        "3",
        "--max-input-tokens",
        "10000",
        "--max-seconds",
        "30",
    ]
}
fn text(out: &Output) -> String {
    format!(
        "{}{}",
        String::from_utf8_lossy(&out.stdout),
        String::from_utf8_lossy(&out.stderr)
    )
}

#[test]
fn batch_help_is_discoverable_and_non_probing() {
    let f = Fixture::new(false);
    let parent = f.invoke(&["jev", "--help"]);
    assert!(parent.status.success());
    assert!(text(&parent).contains("jev batch"));
    let help = f.invoke(&["jev", "batch", "--help"]);
    assert!(help.status.success());
    assert!(text(&help).contains("--execute"));
    assert!(text(&help).contains("ambiguous"));
    let caps = f.invoke(&["doctor", "--caps"]);
    assert!(caps.status.success());
    let caps: Value = serde_json::from_slice(&caps.stdout).unwrap();
    assert_eq!(caps["typed_batches"]["command"], "jev batch");
    assert_eq!(caps["typed_batches"]["credentials_checked"], false);
    f.no_state();
}

#[test]
fn default_batch_validates_without_enabling_or_creating_state() {
    for enabled in [false, true] {
        let f = Fixture::new(enabled);
        f.plan(&format!("{}\n{}\n", row("a"), row("b")));
        let out = f.batch(&[]);
        assert!(out.status.success(), "{}", text(&out));
        let report: Value = serde_json::from_slice(&out.stdout).unwrap();
        assert!(report.is_object());
        f.no_state();
    }
}

#[test]
fn entire_plan_is_validated_before_any_output_or_provider() {
    for bad in [
        "{\"id\":\"b\",\"state\":\"x\",\"questions\":{}}".to_string(),
        row("a").to_string(),
        "{\"id\":\"b\",\"id\":\"c\",\"state\":\"x\",\"questions\":{}}".to_string(),
        "null".to_string(),
        "not-json".to_string(),
    ] {
        let f = Fixture::new(true);
        f.plan(&format!("{}\n{bad}\n", row("a")));
        let out = f.batch(&execute());
        assert!(!out.status.success(), "accepted bad plan {bad}");
        f.no_state();
    }
}

#[test]
fn live_admission_requires_all_limits_and_explicit_execute() {
    let f = Fixture::new(true);
    f.plan(&row("a").to_string());
    for flags in [
        vec!["--resume"],
        vec!["--execute"],
        vec!["--output", "job"],
        vec!["--execute", "--output", "job"],
        vec![
            "--execute",
            "--output",
            "job",
            "--max-requests",
            "1",
            "--max-seconds",
            "10",
        ],
    ] {
        let out = f.batch(&flags);
        assert_eq!(out.status.code(), Some(2), "{}", text(&out));
        f.no_state();
    }
}

#[test]
fn batch_refuses_invalid_duplicate_options_and_limits() {
    let f = Fixture::new(true);
    f.plan(&row("a").to_string());
    for flags in [
        vec!["--max-requests", "0"],
        vec!["--max-requests", "10001"],
        vec!["--max-input-tokens", "0"],
        vec!["--max-seconds", "0"],
        vec!["--max-requests", "true"],
        vec!["--input", "plan.jsonl"],
        vec!["--max-seconds", "10", "--max-seconds", "10"],
        vec!["--api-key", "not-a-key"],
    ] {
        let out = f.batch(&flags);
        assert_eq!(out.status.code(), Some(2), "{}", text(&out));
        f.no_state();
    }
}

#[test]
fn disabled_or_missing_credential_cannot_create_a_transport_intent() {
    for enabled in [false, true] {
        let f = Fixture::new(enabled);
        f.plan(&row("a").to_string());
        let out = f.batch(&execute());
        assert!(!out.status.success(), "{}", text(&out));
        assert!(
            !f.root.join("job/000000.intent.json").exists(),
            "credential preflight must precede transport admission"
        );
        let message = text(&out);
        assert!(
            message.contains("disabled")
                || message.contains("feature")
                || message.contains("credential"),
            "{message}"
        );
        assert!(!f.root.join("state").exists());
    }
}

#[test]
fn large_source_plan_is_checked_whole_without_a_model() {
    let f = Fixture::new(false);
    let mut source = String::new();
    for i in 0..64 {
        let mut record = row(&format!("source-{i}"));
        record["state"] = Value::String("Abc é .\n".repeat(5000));
        source.push_str(&record.to_string());
        source.push('\n');
    }
    assert!(source.len() > 2_000_000);
    f.plan(&source);
    let out = f.batch(&[]);
    assert!(out.status.success(), "{}", text(&out));
    f.no_state();
    let out = f.batch(&["--max-requests", "63"]);
    assert!(!out.status.success());
    f.no_state();
}

#[cfg(unix)]
#[test]
fn input_symlink_and_special_file_are_rejected_without_initialization() {
    use std::os::unix::fs::symlink;
    let f = Fixture::new(true);
    fs::write(f.root.join("source"), row("a").to_string()).unwrap();
    symlink("source", f.root.join("plan.jsonl")).unwrap();
    assert!(!f.batch(&[]).status.success());
    f.no_state();
    fs::remove_file(f.root.join("plan.jsonl")).unwrap();
    fs::create_dir(f.root.join("plan.jsonl")).unwrap();
    assert!(!f.batch(&[]).status.success());
    f.no_state();
}
