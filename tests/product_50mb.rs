//! Offline scripted-transport acceptance for the product's real CLI path.
//!
//! The three deterministic inputs use real-world record formats and are each exactly 50 MiB.
//! The scripted harness never returns an answer constant: it returns a short program that must
//! inspect the complete `ctx`. This proves distribution-independent load, bounded prompt sampling,
//! root transport, Monty execution, exact finalization, cleanup, and death-free operation. It does
//! not claim that a live model will synthesize the same program; that remains an opt-in smoke gate.

use std::{
    collections::HashMap,
    fs::{self, File},
    io::{BufWriter, Write},
    path::{Path, PathBuf},
    process::{Command, Output, Stdio},
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

const FIFTY_MIB: usize = 50 * 1024 * 1024;
const BLOCK_BYTES: usize = 4096;
const BLOCKS: usize = FIFTY_MIB / BLOCK_BYTES;
const RAW_OVERLAP_BYTES: usize = 100;
const ROLLING_BASE: u64 = 1_000_003;

struct Scratch(PathBuf);

impl Scratch {
    fn new() -> Self {
        let nonce = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path =
            std::env::temp_dir().join(format!("azdaja-product-50m-{}-{nonce}", std::process::id()));
        fs::create_dir_all(&path).unwrap();
        Self(path)
    }
}

impl Drop for Scratch {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn write_records(path: &Path, mut record: impl FnMut(usize) -> String) {
    let file = File::create(path).unwrap();
    let mut writer = BufWriter::new(file);
    for index in 0..BLOCKS {
        let text = record(index);
        assert!(text.is_ascii());
        assert!(text.len() < BLOCK_BYTES, "record {index} is too large");
        writer.write_all(text.as_bytes()).unwrap();
        writer
            .write_all(&vec![b' '; BLOCK_BYTES - text.len() - 1])
            .unwrap();
        writer.write_all(b"\n").unwrap();
    }
    writer.flush().unwrap();
    assert_eq!(fs::metadata(path).unwrap().len(), FIFTY_MIB as u64);
}

fn config(dir: &Path, transport: &Path, prompt_dir: &Path) -> PathBuf {
    let path = dir.join("config.toml");
    fs::write(
        &path,
        format!(
            r#"sub_llm_cmd = "python3 {} {}"
default_model = "scripted-product-e2e"
output_cap = 512
max_depth = 1
sub_timeout = 10
max_sessions = 1
cell_timeout = 30
idle_timeout = 1800
clean_patterns = []
jcode_provider = "openai"
jcode_reasoning = "medium"
max_calls_per_cell = 1
"#,
            transport.display(),
            prompt_dir.display()
        ),
    )
    .unwrap();
    path
}

#[cfg(any(target_os = "linux", target_os = "macos"))]
fn reaped_child_high_water_rss_bytes() -> Option<u64> {
    let mut usage = std::mem::MaybeUninit::<libc::rusage>::zeroed();
    // SAFETY: getrusage initializes the provided rusage on success.
    if unsafe { libc::getrusage(libc::RUSAGE_CHILDREN, usage.as_mut_ptr()) } != 0 {
        return None;
    }
    // SAFETY: the successful getrusage call initialized usage.
    let raw = u64::try_from(unsafe { usage.assume_init() }.ru_maxrss).ok()?;
    #[cfg(target_os = "linux")]
    return Some(raw.saturating_mul(1024));
    #[cfg(target_os = "macos")]
    return Some(raw);
}

#[cfg(not(any(target_os = "linux", target_os = "macos")))]
fn reaped_child_high_water_rss_bytes() -> Option<u64> {
    None
}

fn run(home: &Path, cfg: &Path, trace: &Path, args: &[&str]) -> (Output, Option<u64>) {
    let binary = std::env::var_os("AZDAJA_PRODUCT_BINARY")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(env!("CARGO_BIN_EXE_azdaja")));
    let mut child = Command::new(binary)
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", home.join("state"))
        .env("AZDAJA_CONFIG", cfg)
        .env("AZDAJA_SOLO_TRACE", trace)
        .args(args)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    let deadline = Instant::now() + Duration::from_secs(90);
    loop {
        if child.try_wait().unwrap().is_some() {
            let output = child.wait_with_output().unwrap();
            return (output, reaped_child_high_water_rss_bytes());
        }
        if Instant::now() >= deadline {
            child.kill().unwrap();
            let output = child.wait_with_output().unwrap();
            let rss = reaped_child_high_water_rss_bytes();
            panic!(
                "50 MiB product path exceeded its 90-second outer deadline: reaped_child_high_water_rss_bytes={rss:?} stdout={} stderr={}",
                String::from_utf8_lossy(&output.stdout),
                String::from_utf8_lossy(&output.stderr)
            );
        }
        thread::sleep(Duration::from_millis(25));
    }
}

fn assert_runtime_trace(path: &Path) {
    let retained = fs::read_to_string(path).unwrap();
    let runtime = retained
        .lines()
        .filter_map(|line| serde_json::from_str::<serde_json::Value>(line).ok())
        .find(|row| row["event"] == "solo_runtime")
        .expect("missing solo runtime record");
    assert_eq!(runtime["outcome"], "succeeded");
    assert_eq!(runtime["exec_invocation_count"], 1);
    assert_eq!(runtime["snapshot_save_count"], 1);
    assert_eq!(runtime["snapshot_load_count"], 0);
    assert_eq!(runtime["sub_call_count"], 0);
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        assert_eq!(fs::metadata(path).unwrap().permissions().mode() & 0o077, 0);
    }
}

fn window_hash(window: &[u8]) -> u64 {
    window.iter().fold(0u64, |hash, byte| {
        hash.wrapping_mul(ROLLING_BASE)
            .wrapping_add(u64::from(*byte) + 1)
    })
}

fn assert_no_raw_source_span(input: &Path, provider_prompt: &[u8]) {
    assert!(provider_prompt.len() >= RAW_OVERLAP_BYTES);
    let mut prompt_windows: HashMap<u64, Vec<usize>> = HashMap::new();
    for (offset, window) in provider_prompt.windows(RAW_OVERLAP_BYTES).enumerate() {
        prompt_windows
            .entry(window_hash(window))
            .or_default()
            .push(offset);
    }

    let source = fs::read(input).unwrap();
    assert!(source.len() >= RAW_OVERLAP_BYTES);
    let mut power = 1u64;
    for _ in 1..RAW_OVERLAP_BYTES {
        power = power.wrapping_mul(ROLLING_BASE);
    }
    let mut hash = window_hash(&source[..RAW_OVERLAP_BYTES]);
    for offset in 0..=source.len() - RAW_OVERLAP_BYTES {
        if let Some(prompt_offsets) = prompt_windows.get(&hash) {
            for prompt_offset in prompt_offsets {
                assert_ne!(
                    &source[offset..offset + RAW_OVERLAP_BYTES],
                    &provider_prompt[*prompt_offset..*prompt_offset + RAW_OVERLAP_BYTES],
                    "provider prompt copied an exact {RAW_OVERLAP_BYTES}-byte source span at source offset {offset}"
                );
            }
        }
        if offset + RAW_OVERLAP_BYTES < source.len() {
            hash = hash.wrapping_sub((u64::from(source[offset]) + 1).wrapping_mul(power));
            hash = hash
                .wrapping_mul(ROLLING_BASE)
                .wrapping_add(u64::from(source[offset + RAW_OVERLAP_BYTES]) + 1);
        }
    }
}

#[test]
#[ignore = "release-only acceptance: run with AZDAJA_PRODUCT_BINARY=target/release/azdaja"]
fn offline_scripted_harness_answers_three_real_world_50_mib_files_without_a_death() {
    let scratch = Scratch::new();
    let prompt_dir = scratch.0.join("prompts");
    fs::create_dir(&prompt_dir).unwrap();
    let transport = scratch.0.join("harness.py");
    fs::write(
        &transport,
        r#"import os, pathlib, sys

assert os.environ.get("RLM_DEPTH") == "0"
prompt = sys.stdin.read()
out = pathlib.Path(sys.argv[1])
scenarios = {
    "PRODUCT_BUILD_LOG_50M": ("build", '''assert len(ctx)==52428800
needle=" level=ERROR target=payments::retry "
n=ctx.count(needle)
assert n>0
FINAL("Answer: "+str(n))'''),
    "PRODUCT_REPO_DUMP_50M": ("repo", '''assert len(ctx)==52428800
key="AZDAJA_RELEASE_BLOCKER="
p=ctx.find(key)
assert p>=0 and ctx.find(key,p+1)<0
b=ctx.rfind("===== BEGIN FILE ",0,p)
e=ctx.find(" =====",b)
z=ctx.find("\\n",p)
assert b>=0 and e>b and z>p
path=ctx[b+len("===== BEGIN FILE "):e]
ticket=ctx[p+len(key):z].strip()
assert path and ticket
FINAL(path+"|"+ticket)'''),
    "PRODUCT_TRANSCRIPT_50M": ("transcript", '''assert len(ctx)==52428800
tag="[ESCALATION incident=INC-4821]"
p=ctx.rfind(tag)
a=ctx.find("\\n",p)+1
b=ctx.find("\\n",a)
line=ctx[a:b]
prefix="[DECISION accepted] "
assert p>=0 and a>0 and b>a and line.startswith(prefix)
answer=line[len(prefix):]
assert answer
FINAL(answer)'''),
}
matched = [(key, value) for key, value in scenarios.items() if key in prompt]
assert len(matched) == 1, matched
_, (name, program) = matched[0]
(out / (name + ".prompt")).write_text(prompt)
with (out / (name + ".calls")).open("a") as calls:
    calls.write("root\n")
print("```python\n" + program + "\n```")
"#,
    )
    .unwrap();
    let cfg = config(&scratch.0, &transport, &prompt_dir);

    let build = scratch.0.join("build.log");
    let build_expected = (0..BLOCKS).filter(|index| index % 1000 == 17).count();
    write_records(&build, |index| {
        let (level, target) = if index % 1000 == 17 {
            ("ERROR", "payments::retry")
        } else if index % 137 == 9 {
            ("ERROR", "search::index")
        } else {
            ("INFO", "azdaja::worker")
        };
        format!(
            "[2026-08-17T08:{:02}:{:02}Z] job={index:05} level={level} target={target} duration_ms={} message=compile step completed\n",
            index % 60,
            (index * 17) % 60,
            20 + index % 300
        )
    });

    let repo = scratch.0.join("repo.dump");
    let repo_index = 7777;
    let repo_expected = format!("src/module_{repo_index:05}.rs|AZD-{repo_index}");
    write_records(&repo, |index| {
        let blocker = if index == repo_index {
            format!("AZDAJA_RELEASE_BLOCKER=AZD-{index}\n")
        } else {
            String::new()
        };
        format!(
            "===== BEGIN FILE src/module_{index:05}.rs =====\n// repository export generated from tracked source\n{blocker}pub fn module_{index:05}() -> usize {{ {index} }}\n===== END FILE =====\n"
        )
    });

    let transcript = scratch.0.join("transcript.txt");
    let transcript_expected = "ship-v0.1-after-doctor";
    write_records(&transcript, |index| {
        if [100, 5000, 12000].contains(&index) {
            let decision = if index == 12000 {
                transcript_expected
            } else {
                "continue-investigation"
            };
            format!(
                "2026-08-17T09:00:00Z speaker=operator [ESCALATION incident=INC-4821]\n[DECISION accepted] {decision}\n2026-08-17T09:00:01Z speaker=agent status=acknowledged\n"
            )
        } else {
            format!(
                "2026-08-17T09:{:02}:{:02}Z speaker=agent turn={index:05} status=observed detail=no-action\n",
                index % 60,
                (index * 11) % 60
            )
        }
    });

    let cases = [
        (
            build,
            "PRODUCT_BUILD_LOG_50M: How many ERROR records target payments::retry? Reply as Answer: N.",
            format!("Answer: {build_expected}"),
            "build",
        ),
        (
            repo,
            "PRODUCT_REPO_DUMP_50M: Return path|ticket for the unique release blocker in the complete repository dump.",
            repo_expected,
            "repo",
        ),
        (
            transcript,
            "PRODUCT_TRANSCRIPT_50M: Return the accepted decision immediately after the last INC-4821 escalation.",
            transcript_expected.to_string(),
            "transcript",
        ),
    ];

    let mut rss_high_water = Vec::new();
    for (input, question, expected, scenario) in cases {
        let name = input.file_name().unwrap().to_string_lossy();
        let trace = scratch.0.join(format!("{scenario}.trace"));
        let (output, rss) = run(
            &scratch.0,
            &cfg,
            &trace,
            &["solo", question, "-f", input.to_str().unwrap()],
        );
        if let Some(bytes) = rss {
            assert!(
                bytes > 0,
                "{name} reported a zero child RSS high-water mark"
            );
            eprintln!("product_50mb_rss scenario={scenario} reaped_child_high_water_bytes={bytes}");
            rss_high_water.push((scenario, bytes));
        }
        assert!(
            output.status.success(),
            "{name} died: status={:?} stdout={} stderr={}",
            output.status.code(),
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        assert_eq!(
            String::from_utf8(output.stdout).unwrap().trim(),
            expected,
            "{name} returned an incorrect answer"
        );
        let root_prompt = fs::read(prompt_dir.join(format!("{scenario}.prompt"))).unwrap();
        assert!(
            root_prompt.len() < 64 * 1024,
            "{name} sent an unbounded root prompt of {} bytes",
            root_prompt.len()
        );
        assert!(
            root_prompt.len() * 50 < FIFTY_MIB,
            "{name} root prompt was not bounded away from the complete input"
        );
        assert!(
            !String::from_utf8_lossy(&root_prompt).contains(input.to_string_lossy().as_ref()),
            "{name} leaked its host path to the provider prompt"
        );
        assert_no_raw_source_span(&input, &root_prompt);
        assert_eq!(
            fs::read_to_string(prompt_dir.join(format!("{scenario}.calls")))
                .unwrap()
                .lines()
                .count(),
            1,
            "{name} unexpectedly repaired or called a child"
        );
        assert_runtime_trace(&trace);
        fs::remove_file(input).unwrap();
    }

    #[cfg(any(target_os = "linux", target_os = "macos"))]
    {
        assert_eq!(
            rss_high_water.len(),
            3,
            "every product case must report the process-lifetime reaped-child RSS high-water mark"
        );
        let peak = rss_high_water
            .iter()
            .map(|(_, bytes)| *bytes)
            .max()
            .unwrap();
        eprintln!("product_50mb_rss maximum_reaped_child_high_water_bytes={peak}");
    }

    let surviving_sessions = fs::read_dir(scratch.0.join("state"))
        .ok()
        .into_iter()
        .flatten()
        .filter_map(Result::ok)
        .filter(|entry| {
            entry.file_name().to_string_lossy().len() == 16
                && entry.file_type().is_ok_and(|kind| kind.is_dir())
        })
        .count();
    assert_eq!(surviving_sessions, 0, "solo left a persistent session");
}
