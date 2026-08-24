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
fn run_with_solo_trace(
    home: &Path,
    cfg: &Path,
    args: &[&str],
    input: &str,
    trace: &Path,
) -> Output {
    let mut c = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    c.env_remove("RLM_DEPTH")
        .args(args)
        .env("AZDAJA_HOME", home.join("state"))
        .env("AZDAJA_CONFIG", cfg)
        .env("AZDAJA_SOLO_TRACE", trace)
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

// Local scripted transport only: these synthetic classes are unrelated to benchmark gold, and
// every semantic response is produced by the temporary Python oracle without inference/network I/O.
fn write_semantic_metamorphic_oracle(dir: &Path) -> (PathBuf, PathBuf) {
    let logs = dir.join("semantic-logs");
    fs::create_dir(&logs).unwrap();
    let script = dir.join("semantic-oracle.py");
    fs::write(
        &script,
        r#"import json, os, pathlib, re, sys

logs = pathlib.Path(sys.argv[1])
prompt = sys.stdin.read()
cases = (
    "id-original", "id-renamed", "records-forward", "records-reversed",
    "labels-forward", "labels-reversed", "evidence-plain", "evidence-noisy",
    "duplicates-one", "duplicates-three",
)
case = [name for name in cases if ("metamorphic/" + name) in prompt]
assert len(case) == 1, case
case = case[0]

root_code = {
    "id-original": '''items=[{"id":"caller-left","evidence":"semantic-alpha review-me"},{"id":"caller-right","evidence":"semantic-beta stable"}]
labels=semantic_manifest_records(items,"synthetic scripted-oracle framing",["class-a","class-b"])
FINAL(labels["caller-left"]+":"+labels["caller-right"])''',
    "id-renamed": '''items=[{"id":"renamed-red","evidence":"semantic-alpha review-me"},{"id":"renamed-blue","evidence":"semantic-beta stable"}]
labels=semantic_manifest_records(items,"synthetic scripted-oracle framing",["class-a","class-b"])
FINAL(labels["renamed-red"]+":"+labels["renamed-blue"])''',
    "records-forward": '''items=[{"id":"forward-alpha-0","evidence":"semantic-alpha review-me"},{"id":"forward-alpha-1","evidence":"semantic-alpha review-me"},{"id":"forward-beta-0","evidence":"semantic-beta stable"}]
labels=semantic_manifest_records(items,"synthetic scripted-oracle framing",["class-a","class-b"])
counts={"class-a":0,"class-b":0}
for item in items:
    counts[labels[item["id"]]]+=1
FINAL(str(counts["class-a"])+":"+str(counts["class-b"]))''',
    "records-reversed": '''items=[{"id":"forward-beta-0","evidence":"semantic-beta stable"},{"id":"forward-alpha-1","evidence":"semantic-alpha review-me"},{"id":"forward-alpha-0","evidence":"semantic-alpha review-me"}]
labels=semantic_manifest_records(items,"synthetic scripted-oracle framing",["class-a","class-b"])
counts={"class-a":0,"class-b":0}
for item in items:
    counts[labels[item["id"]]]+=1
FINAL(str(counts["class-a"])+":"+str(counts["class-b"]))''',
    "labels-forward": '''items=[{"id":"label-alpha","evidence":"semantic-alpha review-me"},{"id":"label-beta","evidence":"semantic-beta stable"}]
labels=semantic_manifest_records(items,"synthetic scripted-oracle framing",["class-a","class-b"])
FINAL(labels["label-alpha"]+":"+labels["label-beta"])''',
    "labels-reversed": '''items=[{"id":"label-alpha","evidence":"semantic-alpha review-me"},{"id":"label-beta","evidence":"semantic-beta stable"}]
labels=semantic_manifest_records(items,"synthetic scripted-oracle framing",["class-b","class-a"])
FINAL(labels["label-alpha"]+":"+labels["label-beta"])''',
    "evidence-plain": '''items=[{"id":"plain-alpha","evidence":"semantic-alpha review-me"},{"id":"plain-beta","evidence":"semantic-beta stable"}]
labels=semantic_manifest_records(items,"synthetic scripted-oracle framing",["class-a","class-b"])
FINAL(labels["plain-alpha"]+":"+labels["plain-beta"])''',
    "evidence-noisy": '''items=[{"id":"noisy-alpha","evidence":"meta=semantic-beta semantic-alpha   review-me\\nmeta=trace-77"},{"id":"noisy-beta","evidence":"meta=noop\\nsemantic-beta\\tstable meta=semantic-alpha"}]
labels=semantic_manifest_records(items,"synthetic scripted-oracle framing",["class-a","class-b"])
FINAL(labels["noisy-alpha"]+":"+labels["noisy-beta"])''',
    "duplicates-one": '''items=[{"id":"occ-alpha-0","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-1","evidence":"semantic-alpha review-me"},{"id":"occ-beta-0","evidence":"semantic-beta stable"}]
labels=semantic_manifest_records(items,"synthetic scripted-oracle framing",["class-a","class-b"])
counts={"class-a":0,"class-b":0}
expanded=[]
for item in items:
    value=labels[item["id"]]
    counts[value]+=1
    expanded.append(item["id"]+"="+value)
FINAL(str(len(labels))+":"+str(counts["class-a"])+":"+str(counts["class-b"])+"|"+",".join(expanded))''',
    "duplicates-three": '''items=[{"id":"occ-alpha-0","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-1","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-2","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-3","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-4","evidence":"semantic-alpha review-me"},{"id":"occ-alpha-5","evidence":"semantic-alpha review-me"},{"id":"occ-beta-0","evidence":"semantic-beta stable"},{"id":"occ-beta-1","evidence":"semantic-beta stable"},{"id":"occ-beta-2","evidence":"semantic-beta stable"}]
labels=semantic_manifest_records(items,"synthetic scripted-oracle framing",["class-a","class-b"])
counts={"class-a":0,"class-b":0}
expanded=[]
for item in items:
    value=labels[item["id"]]
    counts[value]+=1
    expanded.append(item["id"]+"="+value)
FINAL(str(len(labels))+":"+str(counts["class-a"])+":"+str(counts["class-b"])+"|"+",".join(expanded))''',
}

if os.getenv("RLM_DEPTH") == "0":
    print("```python\n" + root_code[case] + "\n```")
    raise SystemExit(0)

if "annotator A" in prompt:
    role = "a"
elif "annotator B" in prompt:
    role = "b"
elif "Blind final source-annotation adjudicator" in prompt:
    role = "j"
else:
    raise AssertionError("unexpected semantic prompt")
tag_match = re.search(r"return only (AZM1-[ABJ]-[0-9]+-[0-9]+-[0-9]+:) followed", prompt)
assert tag_match is not None
response_prefix = tag_match.group(1)
legend_text = prompt.split("LABEL CODES", 1)[1].split("ROWS are", 1)[0]
legend = []
for line in legend_text.splitlines()[1:]:
    code, value = line.split("\t", 1)
    legend.append([code, json.loads(value)])
allowed = [row[1] for row in legend]
assert set(allowed) == {"class-a", "class-b"}
rows_text = prompt.split("no whitespace, prose, markdown, omission, or extra character.\n", 1)[1]
rows = []
for line in rows_text.splitlines():
    rid, evidence = line.split("\t", 1)
    rows.append([rid, json.loads(evidence)])
assert rows

def canonical_label(evidence):
    without_metadata = " ".join(word for word in evidence.split() if not word.startswith("meta="))
    semantic = " ".join(without_metadata.split())
    has_alpha = "semantic-alpha" in semantic
    has_beta = "semantic-beta" in semantic
    assert has_alpha != has_beta, semantic
    return "class-a" if has_alpha else "class-b"

manifest = []
for rid, evidence in rows:
    label = canonical_label(evidence)
    if role == "b" and label == "class-a":
        label = "class-b"  # Script one blind disagreement; the judge must see only its wire ID.
    manifest.append([rid, label])
record = {"allowed": allowed, "manifest": manifest, "prompt": prompt, "rows": rows}
path = logs / (case + "-" + role + ".json")
assert not path.exists(), "unexpected retry or duplicate semantic call"
path.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
code_by_label = {label: code for code, label in legend}
print(response_prefix + "".join(code_by_label[label] for rid, label in manifest))
"#,
    )
    .unwrap();
    (script, logs)
}

fn semantic_metamorphic_config(dir: &Path, script: &Path, logs: &Path) -> PathBuf {
    let cfg = config(
        dir,
        &format!("python3 {} {}", script.display(), logs.display()),
        4096,
        1,
        3,
        4,
    );
    let text = fs::read_to_string(&cfg)
        .unwrap()
        .replace("max_calls_per_cell = 64", "max_calls_per_cell = 6");
    fs::write(&cfg, text).unwrap();
    cfg
}

fn run_semantic_metamorphic_case(dir: &Path, cfg: &Path, case: &str) -> String {
    let input = dir.join(format!("{case}.txt"));
    fs::write(&input, "synthetic schema; no benchmark rows or gold").unwrap();
    let question = format!("metamorphic/{case}");
    let output = run(
        dir,
        cfg,
        &["solo", &question, "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "case={case} stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).unwrap().trim().to_string()
}

fn semantic_log(logs: &Path, case: &str, role: &str) -> serde_json::Value {
    serde_json::from_slice(&fs::read(logs.join(format!("{case}-{role}.json"))).unwrap()).unwrap()
}

fn string_pairs(value: &serde_json::Value, key: &str) -> Vec<Vec<String>> {
    serde_json::from_value(value[key].clone()).unwrap()
}

fn string_list(value: &serde_json::Value, key: &str) -> Vec<String> {
    serde_json::from_value(value[key].clone()).unwrap()
}

fn assert_exact_semantic_trace(
    logs: &Path,
    case: &str,
    rows: &[(&str, &str)],
    caller_labels: &[&str],
    forbidden_caller_ids: &[&str],
) {
    let mut call_roles = fs::read_dir(logs)
        .unwrap()
        .filter_map(Result::ok)
        .filter_map(|entry| entry.file_name().into_string().ok())
        .filter(|name| name.starts_with(&format!("{case}-")))
        .collect::<Vec<_>>();
    call_roles.sort();
    assert_eq!(
        call_roles,
        [
            format!("{case}-a.json"),
            format!("{case}-b.json"),
            format!("{case}-j.json")
        ],
        "exact child-call budget is two blind manifests plus one adjudication"
    );

    let a = semantic_log(logs, case, "a");
    let b = semantic_log(logs, case, "b");
    let j = semantic_log(logs, case, "j");
    let expected_a = rows
        .iter()
        .enumerate()
        .map(|(index, (_, evidence))| vec![index.to_string(), (*evidence).to_string()])
        .collect::<Vec<_>>();
    let scripted_class_is_a = |evidence: &str| {
        evidence
            .split_whitespace()
            .filter(|word| !word.starts_with("meta="))
            .any(|word| word == "semantic-alpha")
    };
    let expected_a_manifest = expected_a
        .iter()
        .map(|row| {
            vec![
                row[0].clone(),
                if scripted_class_is_a(&row[1]) {
                    "class-a".to_string()
                } else {
                    "class-b".to_string()
                },
            ]
        })
        .collect::<Vec<_>>();
    let expected_b = rows
        .iter()
        .rev()
        .enumerate()
        .map(|(index, (_, evidence))| vec![index.to_string(), (*evidence).to_string()])
        .collect::<Vec<_>>();
    let expected_b_manifest = expected_b
        .iter()
        .map(|row| vec![row[0].clone(), "class-b".to_string()])
        .collect::<Vec<_>>();
    let expected_j = rows
        .iter()
        .filter(|(_, evidence)| scripted_class_is_a(evidence))
        .enumerate()
        .map(|(index, (_, evidence))| vec![index.to_string(), (*evidence).to_string()])
        .collect::<Vec<_>>();
    let expected_j_manifest = expected_j
        .iter()
        .map(|row| vec![row[0].clone(), "class-a".to_string()])
        .collect::<Vec<_>>();

    assert_eq!(string_pairs(&a, "rows"), expected_a);
    assert_eq!(string_pairs(&a, "manifest"), expected_a_manifest);
    assert_eq!(string_list(&a, "allowed"), caller_labels);
    assert_eq!(string_pairs(&b, "rows"), expected_b);
    assert_eq!(string_pairs(&b, "manifest"), expected_b_manifest);
    assert_eq!(
        string_list(&b, "allowed"),
        caller_labels.iter().rev().copied().collect::<Vec<_>>()
    );
    assert_eq!(string_pairs(&j, "rows"), expected_j);
    assert_eq!(string_pairs(&j, "manifest"), expected_j_manifest);
    assert_eq!(string_list(&j, "allowed"), caller_labels);
    for call in [&a, &b, &j] {
        let prompt = call["prompt"].as_str().unwrap();
        for caller_id in forbidden_caller_ids {
            assert!(
                !prompt.contains(caller_id),
                "caller ID leaked into provider manifest: {caller_id}"
            );
        }
    }
}

// Offline scripted transport for the count-derived semantic budget. It never opens benchmark
// material or a network connection; the generated evidence only matches the measured row lengths.
fn write_semantic_scale_oracle(dir: &Path) -> (PathBuf, PathBuf) {
    let logs = dir.join("scale-logs");
    fs::create_dir(&logs).unwrap();
    let script = dir.join("scale-oracle.py");
    fs::write(
        &script,
        r####"import json, os, pathlib, re, sys, time

logs = pathlib.Path(sys.argv[1])
prompt = sys.stdin.read()
cases = (
    "semantic-scale/102158", "semantic-scale/100000",
    "semantic-projection/102158",
)
matched = [value for value in cases if value in prompt]
assert len(matched) == 1, matched
case = matched[0]
count = 102158 if case.endswith("102158") else 100000
projected = case.startswith("semantic-projection/")

if os.getenv("RLM_DEPTH") == "0":
    if projected:
        root = (
            "ledger=exact_line_ledger(ctx,\"Row: \")\n"
            "assert len(ledger.entries)==" + str(count) + "\n"
            "selected=[]\n"
            "for entry in ledger.entries:\n"
            "    selected.append(entry.id)\n"
            "labels=semantic_manifest(ledger,selected,\" || Target: \",\"classify every final Target under the two-label ontology; metadata is aggregation-only\",[\"class-a\",\"class-b\"])\n"
            "FINAL(str(len(labels))+\":\"+labels[\"O0\"]+\":\"+labels[\"O" + str(count - 1) + "\"])"
        )
    else:
        root = (
            "items=[]\n"
            "i=0\n"
            "while i<" + str(count) + ":\n"
            "    items.append({\"id\":\"i\"+str(i),\"evidence\":\"Instance: synthetic semantic row \"+str(i)+\" \"+(\"x\"*55)})\n"
            "    i+=1\n"
            "labels=semantic_manifest_records(items,\"classify every synthetic instance under the two-label ontology\",[\"class-a\",\"class-b\"])\n"
            "FINAL(str(len(labels))+\":\"+labels[\"i0\"]+\":\"+labels[\"i\"+str(" + str(count - 1) + ")])"
        )
    print("```python\n" + root + "\n```")
    raise SystemExit(0)

tag_match = re.search(r"return only (AZM1-([ABJ])-([0-9]+)-([0-9]+)-([0-9]+):) followed", prompt)
assert tag_match is not None
prefix, role, shard, item_count, code_width = tag_match.groups()
item_count = int(item_count)
code_width = int(code_width)
legend_text = prompt.split("LABEL CODES", 1)[1].split("ROWS are", 1)[0]
legend = []
for line in legend_text.splitlines()[1:]:
    code, value = line.split("\t", 1)
    legend.append((code, json.loads(value)))
code_by_label = {label: code for code, label in legend}
rows_text = prompt.split("no whitespace, prose, markdown, omission, or extra character.\n", 1)[1]
rows = []
for line in rows_text.splitlines():
    local_id, evidence = line.split("\t", 1)
    rows.append((local_id, json.loads(evidence)))
assert len(rows) == item_count
assert len(prefix) + item_count * code_width <= 8192
# These values are compared across separate provider processes. macOS Python 3.9
# exposes a process-relative monotonic epoch, so use the shared wall-clock epoch here.
started_ns = time.time_ns()
time.sleep(0.05)
ended_ns = time.time_ns()
record = {
    "case": case,
    "role": role,
    "shard": int(shard),
    "item_count": item_count,
    "prompt_chars": len(prompt),
    "first_local": rows[0][0],
    "last_local": rows[-1][0],
    "first_evidence": rows[0][1],
    "last_evidence": rows[-1][1],
    "started_ns": started_ns,
    "ended_ns": ended_ns,
}
marker = logs / (case.rsplit("/", 1)[1] + "-" + prefix[:-1] + ".first")
malformed = False
if malformed:
    marker.write_text("first", encoding="utf-8")
    record["phase"] = "malformed"
else:
    record["phase"] = "valid"
line = (json.dumps(record, sort_keys=True) + "\n").encode()
fd = os.open(logs / (case.rsplit("/", 1)[1] + ".jsonl"), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
os.write(fd, line)
os.close(fd)
if malformed:
    print("malformed")
    raise SystemExit(0)
label = "class-a"
print(prefix + code_by_label[label] * item_count)
"####,
    )
    .unwrap();
    (script, logs)
}

fn semantic_scale_config(dir: &Path, script: &Path, logs: &Path) -> PathBuf {
    let cfg = config(
        dir,
        &format!("python3 {} {}", script.display(), logs.display()),
        8192,
        1,
        30,
        4,
    );
    let text = fs::read_to_string(&cfg)
        .unwrap()
        .replace("cell_timeout = 2", "cell_timeout = 120");
    fs::write(&cfg, text).unwrap();
    cfg
}

fn read_json_lines(path: &Path) -> Vec<serde_json::Value> {
    fs::read_to_string(path)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect()
}

fn peak_logged_concurrency(calls: &[serde_json::Value]) -> usize {
    let mut events = Vec::new();
    for call in calls {
        events.push((call["started_ns"].as_u64().unwrap(), 1_i32));
        events.push((call["ended_ns"].as_u64().unwrap(), -1_i32));
    }
    events.sort_by_key(|(at, delta)| (*at, -*delta));
    let mut active = 0_i32;
    let mut peak = 0_i32;
    for (_, delta) in events {
        active += delta;
        peak = peak.max(active);
    }
    usize::try_from(peak).unwrap()
}

#[test]
fn semantic_manifest_102158_rows_uses_fixed_39_item_shards() {
    let t = temp("semantic-scale-102158");
    let (script, logs) = write_semantic_scale_oracle(&t);
    let cfg = semantic_scale_config(&t, &script, &logs);
    let input = t.join("input.txt");
    fs::write(&input, "synthetic classification scale fixture; no gold").unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "semantic-scale/102158 classification",
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
        "102158:class-a:class-a"
    );
    let calls = read_json_lines(&logs.join("102158.jsonl"));
    let shards = 2_620;
    assert_eq!(calls.len(), 2 * shards);
    assert_eq!(peak_logged_concurrency(&calls), 8);
    for role in ["A", "B"] {
        let role_calls = calls
            .iter()
            .filter(|value| value["role"] == role)
            .collect::<Vec<_>>();
        assert_eq!(role_calls.len(), shards);
        assert_eq!(
            role_calls
                .iter()
                .map(|value| value["shard"].as_u64().unwrap())
                .collect::<std::collections::BTreeSet<_>>()
                .len(),
            shards
        );
    }
    assert_eq!(calls.iter().filter(|value| value["role"] == "J").count(), 0);
    assert!(calls.iter().all(
        |value| matches!(value["item_count"].as_u64(), Some(38 | 39))
            && value["prompt_chars"].as_u64().unwrap() + 128 <= 81_920
    ));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn semantic_manifest_exact_target_projection_preserves_102158_occurrences() {
    let t = temp("semantic-projection-102158");
    let (script, logs) = write_semantic_scale_oracle(&t);
    let cfg = semantic_scale_config(&t, &script, &logs);
    let input = t.join("input.txt");
    let mut source = String::from(
        "The allowed labels are \"class-a\" and \"class-b\". Each Row is one complete physical line; after deterministic metadata selection, its label is solely a function of the final Target field.\n",
    );
    for index in 0..102_158usize {
        source.push_str(&format!(
            "Row: occurrence={index} || Target: exact designated target payload {}\n",
            index % 4_151
        ));
    }
    fs::write(&input, source).unwrap();
    let trace_path = t.join("solo.trace");
    let output = run_with_solo_trace(
        &t,
        &cfg,
        &[
            "solo",
            "semantic-projection/102158 classification",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
        &trace_path,
    );
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(
        String::from_utf8_lossy(&output.stdout).trim(),
        "102158:class-a:class-a"
    );
    let calls = read_json_lines(&logs.join("102158.jsonl"));
    let unique_targets = 4_151_u64;
    let shards = 107;
    assert_eq!(calls.len(), 2 * shards);
    assert_eq!(peak_logged_concurrency(&calls), 8);
    for role in ["A", "B"] {
        let role_calls = calls
            .iter()
            .filter(|value| value["role"] == role)
            .collect::<Vec<_>>();
        assert_eq!(role_calls.len(), shards);
        assert_eq!(
            role_calls
                .iter()
                .map(|value| value["item_count"].as_u64().unwrap())
                .sum::<u64>(),
            unique_targets
        );
        assert_eq!(
            role_calls
                .iter()
                .map(|value| value["shard"].as_u64().unwrap())
                .collect::<std::collections::BTreeSet<_>>()
                .len(),
            shards
        );
    }
    assert_eq!(calls.iter().filter(|value| value["role"] == "J").count(), 0);
    assert!(calls.iter().all(
        |value| matches!(value["item_count"].as_u64(), Some(38 | 39))
            && value["prompt_chars"].as_u64().unwrap() + 128 <= 81_920
    ));
    let trace = fs::read_to_string(trace_path).unwrap();
    let runtime: serde_json::Value = trace
        .lines()
        .filter_map(|line| serde_json::from_str(line).ok())
        .next_back()
        .unwrap();
    assert_eq!(runtime["projection_ledger_calls"], 1);
    assert_eq!(runtime["projection_calls"], 1);
    assert_eq!(runtime["projection_ledger_occurrences"], 102_158);
    assert_eq!(runtime["projection_selected_occurrences"], 102_158);
    assert_eq!(runtime["projection_unique_targets"], 4_151);
    assert_eq!(runtime["projection_manifest_callers"], 102_158);
    assert_eq!(runtime["projection_expanded_outputs"], 102_158);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn semantic_manifest_100000_rows_uses_fixed_39_item_shards() {
    let t = temp("semantic-scale-100000");
    let (script, logs) = write_semantic_scale_oracle(&t);
    let cfg = semantic_scale_config(&t, &script, &logs);
    let input = t.join("input.txt");
    fs::write(&input, "synthetic classification scale fixture; no gold").unwrap();
    let started = std::time::Instant::now();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "semantic-scale/100000 classification",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
    );
    let elapsed = started.elapsed();
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(
        String::from_utf8_lossy(&output.stdout).trim(),
        "100000:class-a:class-a"
    );
    let calls = read_json_lines(&logs.join("100000.jsonl"));
    let shards = 2_565;
    assert_eq!(calls.len(), 2 * shards);
    assert_eq!(peak_logged_concurrency(&calls), 8);
    for role in ["A", "B"] {
        let role_calls = calls
            .iter()
            .filter(|value| value["role"] == role)
            .collect::<Vec<_>>();
        assert_eq!(role_calls.len(), shards);
        assert_eq!(
            role_calls
                .iter()
                .map(|value| value["shard"].as_u64().unwrap())
                .collect::<std::collections::BTreeSet<_>>()
                .len(),
            shards
        );
    }
    assert_eq!(calls.iter().filter(|value| value["role"] == "J").count(), 0);
    assert!(calls.iter().all(
        |value| matches!(value["item_count"].as_u64(), Some(38 | 39))
            && value["prompt_chars"].as_u64().unwrap() + 128 <= 81_920
    ));
    assert!(
        elapsed < Duration::from_secs(1_800),
        "100K fixed-shard run took {elapsed:?}"
    );
    fs::remove_dir_all(t).unwrap();
}

fn run_semantic_zero_call_rejection(case: &str, root: &str) {
    let t = temp(case);
    let calls = t.join("depth-one-calls");
    let mock = t.join("preflight.py");
    fs::write(
        &mock,
        format!(
            r####"import os, pathlib, sys
prompt=sys.stdin.read()
if os.getenv("RLM_DEPTH") == "0":
    print("```python\n" + {root:?} + "\n```")
else:
    pathlib.Path({calls:?}).write_text("unexpected semantic call", encoding="utf-8")
    print("unexpected")
"####,
            root = root,
            calls = calls.to_string_lossy(),
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 8192, 1, 30, 4);
    let text = fs::read_to_string(&cfg)
        .unwrap()
        .replace("cell_timeout = 2", "cell_timeout = 120")
        .replace("max_calls_per_cell = 64", "max_calls_per_cell = 150");
    fs::write(&cfg, text).unwrap();
    let input = t.join("input.txt");
    fs::write(&input, "synthetic classification preflight; no gold").unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "synthetic classification preflight",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
    );
    assert!(!output.status.success());
    assert!(
        !calls.exists(),
        "preflight rejection launched a semantic child"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn semantic_manifest_105001_occurrences_reject_before_child_calls() {
    run_semantic_zero_call_rejection(
        "semantic-over-count",
        "items=[]\ni=0\nwhile i<105001:\n    items.append({\"id\":str(i),\"evidence\":\"synthetic row\"})\n    i+=1\nlabels=semantic_manifest_records(items,\"binary synthetic classification\",[\"a\",\"b\"])\nFINAL(str(len(labels)))",
    );
}

#[test]
fn exact_line_records_external_boundary_accepts_105000_and_rejects_105001() {
    use std::fmt::Write as _;
    for (count, succeeds) in [(105_000usize, true), (105_001usize, false)] {
        let t = temp(&format!("exact-line-boundary-{count}"));
        let child_marker = t.join("child-called");
        let mock = t.join("mock.py");
        fs::write(
            &mock,
            format!(
                r#"import os,pathlib
if os.getenv("RLM_DEPTH") == "0":
    print('```python\nrecords=exact_line_records(ctx,"Row: ")\nFINAL(str(len(records)))\n```')
else:
    pathlib.Path({child_marker:?}).write_text("unexpected child",encoding="utf-8")
    print("unexpected")
"#,
                child_marker = child_marker,
            ),
        )
        .unwrap();
        let cfg = config(&t, &format!("python3 {}", mock.display()), 8192, 1, 30, 4);
        let text = fs::read_to_string(&cfg)
            .unwrap()
            .replace("cell_timeout = 2", "cell_timeout = 120");
        fs::write(&cfg, text).unwrap();
        let input = t.join("input.txt");
        let mut source = String::with_capacity(count * 16);
        for i in 0..count {
            writeln!(&mut source, "Row: {i}").unwrap();
        }
        fs::write(&input, source).unwrap();
        let output = run(
            &t,
            &cfg,
            &[
                "solo",
                "Count every exact Row record.",
                "-f",
                input.to_str().unwrap(),
            ],
            "",
        );
        if succeeds {
            assert!(
                output.status.success(),
                "{}",
                String::from_utf8_lossy(&output.stderr)
            );
            assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "105000");
        } else {
            assert!(!output.status.success());
            assert!(
                String::from_utf8_lossy(&output.stderr)
                    .contains("exact_line_records record limit exceeded"),
                "{}",
                String::from_utf8_lossy(&output.stderr)
            );
        }
        assert!(
            !child_marker.exists(),
            "boundary path launched a child call"
        );
        fs::remove_dir_all(t).unwrap();
    }
}

#[test]
fn semantic_manifest_oversized_evidence_rejects_before_child_calls() {
    run_semantic_zero_call_rejection(
        "semantic-over-prompt",
        "items=[{\"id\":\"x\",\"evidence\":\"z\"*360000}]\nlabels=semantic_manifest_records(items,\"binary synthetic classification\",[\"a\",\"b\"])\nFINAL(labels[\"x\"])",
    );
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
        format!(r#"{{"chars":{}}}"#, secret.len() + 13)
    );
    ok(run(
        &t,
        &cfg,
        &["exec", &id],
        "answer={'ok': True, 'items': [1, None, 'x'], 'nested': {'f': False}}\nFINAL(answer)\n",
    ));
    assert_eq!(
        ok(run(&t, &cfg, &["final", &id], "")).trim(),
        r#"{"items":[1,null,"x"],"nested":{"f":false},"ok":true}"#
    );
    assert!(ok(run(&t, &cfg, &["list"], "")).contains(&id));
    ok(run(&t, &cfg, &["kill", &id], ""));
    assert!(!ok(run(&t, &cfg, &["list"], "")).contains(&id));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn corrupt_observability_sidecars_do_not_block_authoritative_loads() {
    let t = temp("observability-degrades");
    let cfg = config(&t, "cat", 512, 1, 2, 4);
    let first = t.join("first.txt");
    let second = t.join("second.txt");
    fs::write(&first, "first source\n").unwrap();
    fs::write(&second, "second authoritative source\n").unwrap();
    let id = sid(&t, &cfg);

    ok(run(
        &t,
        &cfg,
        &["load", &id, first.to_str().unwrap(), "ctx"],
        "",
    ));
    fs::write(t.join("state").join(&id).join("observability.json"), "{").unwrap();
    fs::create_dir_all(t.join("state/observability")).unwrap();
    fs::write(t.join("state/observability/recent.json"), "{").unwrap();

    let loaded = ok(run(
        &t,
        &cfg,
        &["load", &id, second.to_str().unwrap(), "ctx"],
        "",
    ));
    assert!(loaded.contains("loaded 'ctx' : str"));
    assert_eq!(
        ok(run(&t, &cfg, &["exec", &id], "len(ctx)\n")).trim(),
        "second authoritative source\n".len().to_string()
    );

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
fn cell_timeout_excludes_suspended_host_call_wall() {
    let t = temp("cell-host-wall");
    let script = t.join("slow-success.sh");
    fs::write(
        &script,
        "#!/bin/sh
sleep 1.1
cat
",
    )
    .unwrap();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&script, fs::Permissions::from_mode(0o755)).unwrap();
    }
    let cfg = config(&t, script.to_str().unwrap(), 2048, 1, 3, 4);
    let text = fs::read_to_string(&cfg)
        .unwrap()
        .replace("cell_timeout = 2", "cell_timeout = 1");
    fs::write(&cfg, text).unwrap();
    let id = sid(&t, &cfg);
    let started = Instant::now();
    let output = run(
        &t,
        &cfg,
        &["exec", &id],
        "first=llm('first')
second=llm('second')
FINAL(first+second)
",
    );
    let elapsed = started.elapsed();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stdout)
    );
    assert!(
        elapsed >= Duration::from_secs(2),
        "host wait was not exercised: {elapsed:?}"
    );
    assert!(
        elapsed < Duration::from_secs(5),
        "unexpected host wall: {elapsed:?}"
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
        r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{"id":"R1","evidence":"ordinary note"},{"id":"R2","evidence":"ambiguous service"}]\nlabels=semantic_manifest_records(items,"binary annotation",["ham","spam"])\nFINAL(labels["R1"]+":"+labels["R2"])\n```')
else:
    prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-[0-9]+-[0-9]+:) followed',p).group(1)
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    codes={json.loads(line.split('\t',1)[1]):line.split('\t',1)[0] for line in legend}
    rows=p.split('extra character.\n',1)[1].splitlines()
    evidence=[json.loads(line.split('\t',1)[1]) for line in rows]
    labels=['spam' if 'ambiguous' in value else 'ham' for value in evidence]
    print(prefix+''.join(codes[label] for label in labels))
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
        r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{"id":"x","evidence":"first raw"},{"id":"y","evidence":"second raw"}]\nlabels=semantic_manifest_records(items,"official binary task",["ham","spam"])\nFINAL(labels["x"]+":"+labels["y"])\n```')
else:
    prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-[0-9]+-[0-9]+:) followed',p).group(1)
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    codes={json.loads(line.split('\t',1)[1]):line.split('\t',1)[0] for line in legend}
    rows=p.split('extra character.\n',1)[1].splitlines()
    evidence=[json.loads(line.split('\t',1)[1]) for line in rows]
    if 'annotator A' in p:
        labels=['ham' for value in evidence]
    elif 'annotator B' in p:
        assert [json.loads(line.split('\t',1)[1]) for line in legend] == ['spam','ham']
        labels=['spam' if value == 'second raw' else 'ham' for value in evidence]
    elif 'Blind final source-annotation adjudicator' in p:
        assert evidence == ['second raw']
        assert 'annotator A' not in p and 'annotator B' not in p
        labels=['spam']
    else:
        raise SystemExit('unexpected prompt')
    print(prefix+''.join(codes[label] for label in labels))
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
fn solo_dual_manifest_retries_malformed_adjudication_once_within_envelope() {
    let t = temp("solo-judge-contract-retry");
    let marker = t.join("judge-seen");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,pathlib,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{{"id":"x","evidence":"complete raw"}}]\nlabels=semantic_manifest_records(items,"official binary task",["ham","spam"])\nFINAL(labels["x"])\n```')
else:
    with open({calls:?}, 'a') as f: f.write('x')
    prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-[0-9]+-[0-9]+:) followed',p).group(1)
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    codes={{json.loads(line.split('\t',1)[1]):line.split('\t',1)[0] for line in legend}}
    if 'annotator A' in p: label='ham'
    elif 'annotator B' in p: label='spam'
    elif not pathlib.Path({marker:?}).exists():
        pathlib.Path({marker:?}).write_text('seen');print('malformed');raise SystemExit
    else: label='ham'
    print(prefix+codes[label])
"#,
            calls = calls,
            marker = marker,
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
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 4);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_is_invariant_to_caller_item_id_renaming() {
    let t = temp("semantic-id-metamorphism");
    let (script, logs) = write_semantic_metamorphic_oracle(&t);
    let cfg = semantic_metamorphic_config(&t, &script, &logs);
    let original = run_semantic_metamorphic_case(&t, &cfg, "id-original");
    let renamed = run_semantic_metamorphic_case(&t, &cfg, "id-renamed");
    assert_eq!(original, "class-a:class-b");
    assert_eq!(renamed, original);
    let rows = [
        ("R00000000", "semantic-alpha review-me"),
        ("R00000001", "semantic-beta stable"),
    ];
    assert_exact_semantic_trace(
        &logs,
        "id-original",
        &rows,
        &["class-a", "class-b"],
        &["caller-left", "caller-right"],
    );
    assert_exact_semantic_trace(
        &logs,
        "id-renamed",
        &rows,
        &["class-a", "class-b"],
        &["renamed-red", "renamed-blue"],
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "id-original", "a"), "manifest"),
        string_pairs(&semantic_log(&logs, "id-renamed", "a"), "manifest")
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "id-original", "j"), "rows"),
        vec![vec![
            "0".to_string(),
            "semantic-alpha review-me".to_string()
        ]]
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_reversal_preserves_order_invariant_reduction() {
    let t = temp("semantic-order-metamorphism");
    let (script, logs) = write_semantic_metamorphic_oracle(&t);
    let cfg = semantic_metamorphic_config(&t, &script, &logs);
    let forward = run_semantic_metamorphic_case(&t, &cfg, "records-forward");
    let reversed = run_semantic_metamorphic_case(&t, &cfg, "records-reversed");
    assert_eq!(forward, "2:1");
    assert_eq!(reversed, forward);
    assert_exact_semantic_trace(
        &logs,
        "records-forward",
        &[
            ("R00000000", "semantic-alpha review-me"),
            ("R00000001", "semantic-beta stable"),
        ],
        &["class-a", "class-b"],
        &["forward-alpha-0", "forward-alpha-1", "forward-beta-0"],
    );
    assert_exact_semantic_trace(
        &logs,
        "records-reversed",
        &[
            ("R00000000", "semantic-beta stable"),
            ("R00000001", "semantic-alpha review-me"),
        ],
        &["class-a", "class-b"],
        &["forward-alpha-0", "forward-alpha-1", "forward-beta-0"],
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "records-forward", "j"), "manifest"),
        vec![vec!["0".to_string(), "class-a".to_string()]]
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "records-reversed", "j"), "manifest"),
        vec![vec!["0".to_string(), "class-a".to_string()]]
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_is_invariant_to_caller_allowed_label_order() {
    let t = temp("semantic-label-metamorphism");
    let (script, logs) = write_semantic_metamorphic_oracle(&t);
    let cfg = semantic_metamorphic_config(&t, &script, &logs);
    let forward = run_semantic_metamorphic_case(&t, &cfg, "labels-forward");
    let reversed = run_semantic_metamorphic_case(&t, &cfg, "labels-reversed");
    assert_eq!(forward, "class-a:class-b");
    assert_eq!(reversed, forward);
    let rows = [
        ("R00000000", "semantic-alpha review-me"),
        ("R00000001", "semantic-beta stable"),
    ];
    assert_exact_semantic_trace(
        &logs,
        "labels-forward",
        &rows,
        &["class-a", "class-b"],
        &["label-alpha", "label-beta"],
    );
    assert_exact_semantic_trace(
        &logs,
        "labels-reversed",
        &rows,
        &["class-b", "class-a"],
        &["label-alpha", "label-beta"],
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "labels-forward", "j"), "manifest"),
        string_pairs(&semantic_log(&logs, "labels-reversed", "j"), "manifest")
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_scripted_oracle_ignores_harmless_metadata_and_whitespace() {
    let t = temp("semantic-evidence-metamorphism");
    let (script, logs) = write_semantic_metamorphic_oracle(&t);
    let cfg = semantic_metamorphic_config(&t, &script, &logs);
    let plain = run_semantic_metamorphic_case(&t, &cfg, "evidence-plain");
    let noisy = run_semantic_metamorphic_case(&t, &cfg, "evidence-noisy");
    assert_eq!(plain, "class-a:class-b");
    assert_eq!(noisy, plain);
    assert_exact_semantic_trace(
        &logs,
        "evidence-plain",
        &[
            ("R00000000", "semantic-alpha review-me"),
            ("R00000001", "semantic-beta stable"),
        ],
        &["class-a", "class-b"],
        &["plain-alpha", "plain-beta"],
    );
    assert_exact_semantic_trace(
        &logs,
        "evidence-noisy",
        &[
            (
                "R00000000",
                "meta=semantic-beta semantic-alpha   review-me\nmeta=trace-77",
            ),
            (
                "R00000001",
                "meta=noop\nsemantic-beta\tstable meta=semantic-alpha",
            ),
        ],
        &["class-a", "class-b"],
        &["noisy-alpha", "noisy-beta"],
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "evidence-plain", "j"), "manifest"),
        string_pairs(&semantic_log(&logs, "evidence-noisy", "j"), "manifest")
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_scales_duplicate_multiplicity_and_expands_every_occurrence() {
    let t = temp("semantic-duplicate-metamorphism");
    let (script, logs) = write_semantic_metamorphic_oracle(&t);
    let cfg = semantic_metamorphic_config(&t, &script, &logs);
    let one = run_semantic_metamorphic_case(&t, &cfg, "duplicates-one");
    let three = run_semantic_metamorphic_case(&t, &cfg, "duplicates-three");
    assert_eq!(
        one,
        "3:2:1|occ-alpha-0=class-a,occ-alpha-1=class-a,occ-beta-0=class-b"
    );
    assert_eq!(
        three,
        "9:6:3|occ-alpha-0=class-a,occ-alpha-1=class-a,occ-alpha-2=class-a,occ-alpha-3=class-a,occ-alpha-4=class-a,occ-alpha-5=class-a,occ-beta-0=class-b,occ-beta-1=class-b,occ-beta-2=class-b"
    );
    let unique_rows = [
        ("R00000000", "semantic-alpha review-me"),
        ("R00000001", "semantic-beta stable"),
    ];
    assert_exact_semantic_trace(
        &logs,
        "duplicates-one",
        &unique_rows,
        &["class-a", "class-b"],
        &["occ-alpha-0", "occ-alpha-1", "occ-beta-0"],
    );
    assert_exact_semantic_trace(
        &logs,
        "duplicates-three",
        &unique_rows,
        &["class-a", "class-b"],
        &[
            "occ-alpha-0",
            "occ-alpha-1",
            "occ-alpha-2",
            "occ-alpha-3",
            "occ-alpha-4",
            "occ-alpha-5",
            "occ-beta-0",
            "occ-beta-1",
            "occ-beta-2",
        ],
    );
    assert_eq!(
        string_pairs(&semantic_log(&logs, "duplicates-one", "a"), "manifest"),
        string_pairs(&semantic_log(&logs, "duplicates-three", "a"), "manifest")
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_rejects_duplicate_singleton_labels_before_child_call() {
    let t = temp("solo-manifest-duplicate-labels");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        r#"import os
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{"id":7,"evidence":"one"},{"id":8,"evidence":"one"}]\nlabels=semantic_manifest_records(items,"deterministic inclusion",["include","include"])\nFINAL(str(labels[7])+":"+str(labels[8]))\n```')
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
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("duplicate semantic label"),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(!String::from_utf8_lossy(&output.stdout).contains("UNEXPECTED_CHILD_CALL"));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_rejects_one_unique_label_before_child_call() {
    let t = temp("solo-manifest-one-label");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        r#"import os
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{"id":"x","evidence":"one"}]\nlabels=semantic_manifest_records(items,"deterministic inclusion",["include"])\nFINAL(labels["x"])\n```')
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
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("semantic_manifest requires at least two distinct labels"),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(!String::from_utf8_lossy(&output.stdout).contains("UNEXPECTED_CHILD_CALL"));
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
            r#"import json,os,re,sys,pathlib
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{{"id":"x","evidence":"raw"}}]\nlabels=semantic_manifest_records(items,"official binary task",["ham","spam"])\nFINAL(labels["x"])\n```')
else:
    with open({calls:?}, 'a') as f: f.write('x')
    if 'annotator A' in p and not pathlib.Path({a_seen:?}).exists():
        pathlib.Path({a_seen:?}).write_text('seen')
        print('malformed')
    else:
        prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-[0-9]+-[0-9]+:) followed',p).group(1)
        legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
        code=next(line.split('\t',1)[0] for line in legend if json.loads(line.split('\t',1)[1]) == 'ham')
        print(prefix+code)
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
fn solo_manifest_adjudicates_malformed_primary_after_bounded_retry() {
    let t = temp("solo-malformed-primary-adjudication");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{{"id":"x","evidence":"raw"}}]\nlabels=semantic_manifest_records(items,"official binary task",["ham","spam"])\nFINAL(labels["x"])\n```')
else:
    with open({calls:?}, 'a') as f: f.write('x')
    role=re.search(r'return only AZM1-([ABJ])-',p).group(1)
    if role == 'A':
        print('malformed-after-bounded-retry')
    else:
        prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-[0-9]+-[0-9]+:) followed',p).group(1)
        legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
        code=next(line.split('\t',1)[0] for line in legend if json.loads(line.split('\t',1)[1]) == 'ham')
        print(prefix+code)
"#,
            calls = calls,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 6, 4);
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
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 4);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_continues_a_valid_short_positional_prefix() {
    let t = temp("solo-positional-prefix-continuation");
    let a_seen = t.join("a-seen");
    let counts = t.join("counts");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,pathlib,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[]\ni=0\nwhile i<39:\n    items.append({{"id":str(i),"evidence":"row "+str(i)}})\n    i+=1\nlabels=semantic_manifest_records(items,"binary task",["ham","spam"])\nFINAL(labels["0"]+":"+labels["38"])\n```')
else:
    prefix=re.search(r'return only (AZM1-([ABJ])-[0-9]+-([0-9]+)-[0-9]+:) followed',p).group(1)
    role=re.search(r'return only AZM1-([ABJ])-',p).group(1)
    count=int(prefix[:-1].split('-')[3])
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    code=next(line.split('\t',1)[0] for line in legend if json.loads(line.split('\t',1)[1]) == 'ham')
    with open({counts:?},'a') as f:f.write(str(count)+'\n')
    if role == 'A' and count == 39 and not pathlib.Path({a_seen:?}).exists():
        pathlib.Path({a_seen:?}).write_text('seen');print(prefix+code*38)
    else: print(prefix+code*count)
"#,
            a_seen = a_seen,
            counts = counts,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "schema row").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "binary task", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "ham:ham");
    let observed = fs::read_to_string(&counts).unwrap();
    assert_eq!(observed.lines().filter(|line| *line == "39").count(), 2);
    assert_eq!(observed.lines().filter(|line| *line == "1").count(), 1);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_normalizes_only_unambiguous_positional_frames() {
    let t = temp("solo-positional-frame-normalization");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nlabels=[]\ni=0\nwhile i<63:\n    labels.append("l"+str(i))\n    i+=1\nitems=[]\ni=0\nwhile i<4:\n    items.append({{"id":str(i),"evidence":"row "+str(i)}})\n    i+=1\nmapping=semantic_manifest_records(items,"multi label task",labels)\nFINAL(mapping["0"]+":"+mapping["3"])\n```')
else:
    with open({calls:?},'a') as f:f.write('x')
    prefix=re.search(r'return only (AZM1-([ABJ])-[0-9]+-([0-9]+)-[0-9]+:) followed',p).group(1)
    role=re.search(r'return only AZM1-([ABJ])-',p).group(1)
    count=int(prefix[:-1].split('-')[3])
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    code=next(line.split('\t',1)[0] for line in legend if json.loads(line.split('\t',1)[1]) == 'l62')
    if role == 'A':
        print(prefix+' '.join([code]*count)+' provider-tail')
    else:
        print(prefix[:-1]+code*count)
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
        &["solo", "multi label task", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "l62:l62");
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 2);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_rejects_ambiguous_short_frame_before_retry() {
    let t = temp("solo-ambiguous-short-frame");
    let a_seen = t.join("a-seen");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,pathlib,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[]\ni=0\nwhile i<4:\n    items.append({{"id":str(i),"evidence":"row "+str(i)}})\n    i+=1\nlabels=semantic_manifest_records(items,"binary task",["ham","spam"])\nFINAL(labels["0"]+":"+labels["3"])\n```')
else:
    with open({calls:?},'a') as f:f.write('x')
    prefix=re.search(r'return only (AZM1-([ABJ])-[0-9]+-([0-9]+)-[0-9]+:) followed',p).group(1)
    role=re.search(r'return only AZM1-([ABJ])-',p).group(1)
    count=int(prefix[:-1].split('-')[3])
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    code=next(line.split('\t',1)[0] for line in legend if json.loads(line.split('\t',1)[1]) == 'spam')
    if role == 'A' and not pathlib.Path({a_seen:?}).exists():
        pathlib.Path({a_seen:?}).write_text('seen')
        short=prefix.rsplit('-',1)[0]+'-'
        print(short+code*count)
    else:
        print(prefix+code*count)
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
        &["solo", "binary task", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "spam:spam");
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 3);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_uses_leftover_primary_reserve_for_one_second_suffix_retry() {
    let t = temp("solo-primary-second-suffix-retry");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[]\ni=0\nwhile i<313:\n    items.append({{"id":str(i),"evidence":"row "+str(i)}})\n    i+=1\nlabels=semantic_manifest_records(items,"binary task",["ham","spam"])\nFINAL(labels["0"]+":"+labels["312"])\n```')
else:
    with open({calls:?},'a') as f:f.write('x')
    prefix=re.search(r'return only (AZM1-([ABJ])-([0-9]+)-([0-9]+)-[0-9]+:) followed',p).group(1)
    role=re.search(r'return only AZM1-([ABJ])-',p).group(1)
    shard=int(prefix[:-1].split('-')[2]);count=int(prefix[:-1].split('-')[3])
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    code=next(line.split('\t',1)[0] for line in legend if json.loads(line.split('\t',1)[1]) == 'ham')
    if role == 'A' and shard == 0 and count == 35:
        print(prefix+code*(count-3))
    elif role == 'A' and shard == 0 and count == 3:
        print(prefix+code*(count-1))
    else:
        print(prefix+code*count)
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
        &["solo", "binary task", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "ham:ham");
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 20);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_uses_leftover_adjudication_reserve_for_one_second_suffix_retry() {
    let t = temp("solo-adjudication-second-suffix-retry");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[]\ni=0\nwhile i<313:\n    items.append({{"id":str(i),"evidence":"row "+str(i)}})\n    i+=1\nlabels=semantic_manifest_records(items,"binary task",["ham","spam"])\nFINAL(labels["0"]+":"+labels["1"]+":"+labels["2"]+":"+labels["312"])\n```')
else:
    with open({calls:?},'a') as f:f.write('x')
    prefix=re.search(r'return only (AZM1-([ABJ])-([0-9]+)-([0-9]+)-[0-9]+:) followed',p).group(1)
    role=re.search(r'return only AZM1-([ABJ])-',p).group(1)
    count=int(prefix[:-1].split('-')[3])
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    codes={{json.loads(line.split('\t',1)[1]):line.split('\t',1)[0] for line in legend}}
    rows=p.rsplit('extra character.\n',1)[1].splitlines()
    evidence=[json.loads(line.split('\t',1)[1]) for line in rows]
    if role == 'B':
        labels=['spam' if value in ['row 0','row 1','row 2'] else 'ham' for value in evidence]
        print(prefix+''.join(codes[label] for label in labels))
    elif role == 'J' and count == 3:
        print(prefix+codes['ham'])
    elif role == 'J' and count == 2:
        print(prefix+codes['ham'])
    else:
        print(prefix+codes['ham']*count)
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
        &["solo", "binary task", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(
        String::from_utf8_lossy(&output.stdout).trim(),
        "ham:ham:ham:ham"
    );
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 21);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_uses_adjudication_instead_of_a_third_primary_retry_round() {
    let t = temp("solo-no-third-primary-retry");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[]\ni=0\nwhile i<313:\n    items.append({{"id":str(i),"evidence":"row "+str(i)}})\n    i+=1\nsemantic_manifest_records(items,"binary task",["ham","spam"])\nFINAL("unreachable")\n```')
else:
    with open({calls:?},'a') as f:f.write('x')
    prefix=re.search(r'return only (AZM1-([ABJ])-([0-9]+)-([0-9]+)-[0-9]+:) followed',p).group(1)
    role=re.search(r'return only AZM1-([ABJ])-',p).group(1)
    shard=int(prefix[:-1].split('-')[2]);count=int(prefix[:-1].split('-')[3])
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    code=next(line.split('\t',1)[0] for line in legend if json.loads(line.split('\t',1)[1]) == 'ham')
    if role == 'A' and shard == 0 and count == 35:
        print(prefix+code*(count-3))
    elif role == 'A' and shard == 0 and count == 3:
        print(prefix+code*(count-1))
    elif role == 'A' and shard == 0 and count == 1:
        print(prefix)
    else:
        print(prefix+code*count)
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
        &["solo", "binary task", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(
        String::from_utf8_lossy(&output.stdout).trim(),
        "unreachable"
    );
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 21);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_blocks_fragmented_second_judge_retry_before_provider_entry() {
    let t = temp("solo-fragmented-judge-retry-block");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[]\ni=0\nwhile i<157:\n    items.append({{"id":str(i),"evidence":"row "+str(i)}})\n    i+=1\nsemantic_manifest_records(items,"binary task",["ham","spam"])\nFINAL("unreachable")\n```')
else:
    with open({calls:?},'a') as f:f.write('x')
    prefix=re.search(r'return only (AZM1-([ABJ])-([0-9]+)-([0-9]+)-[0-9]+:) followed',p).group(1)
    role=re.search(r'return only AZM1-([ABJ])-',p).group(1)
    count=int(prefix[:-1].split('-')[3])
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    codes={{json.loads(line.split('\t',1)[1]):line.split('\t',1)[0] for line in legend}}
    if role == 'J':
        print(prefix)
    elif role == 'B':
        rows=p.rsplit('extra character.\n',1)[1].splitlines()
        evidence=[json.loads(line.split('\t',1)[1]) for line in rows]
        labels=['spam' if value == 'row 0' else 'ham' for value in evidence]
        print(prefix+''.join(codes[label] for label in labels))
    else:
        print(prefix+codes['ham']*count)
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
        &["solo", "binary task", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("semantic adjudication retry reserve envelope"),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 12);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn semantic_phase_reserves_are_host_enforced_before_provider_entry() {
    for (phase, calls, expected) in [
        (
            "classification",
            5,
            "semantic classification call budget exceeded",
        ),
        (
            "adjudication",
            3,
            "semantic adjudication call budget exceeded",
        ),
    ] {
        let t = temp(&format!("semantic-host-phase-{phase}"));
        let marker = t.join("provider-entered");
        let mock = t.join("mock.py");
        fs::write(
            &mock,
            format!(
                r#"import os,pathlib
if os.getenv('RLM_DEPTH') == '0':
 print('```python\n_az_llm_batch_fresh_once(["x"]*{calls},None,8,6,"{phase}")\nFINAL("bad")\n```')
else:
 pathlib.Path({marker:?}).write_text('entered')
 print('unexpected')
"#,
                calls = calls,
                phase = phase,
                marker = marker,
            ),
        )
        .unwrap();
        let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 10, 4);
        let input = t.join("input.txt");
        fs::write(&input, "phase test").unwrap();
        let output = run(
            &t,
            &cfg,
            &["solo", "phase budget", "-f", input.to_str().unwrap()],
            "",
        );
        assert!(!output.status.success());
        assert!(String::from_utf8_lossy(&output.stderr).contains(expected));
        assert!(!marker.exists());
        fs::remove_dir_all(t).unwrap();
    }
}

#[test]
fn solo_manifest_reserves_all_six_primary_and_adjudication_phases() {
    let t = temp("semantic-six-phase-reserve");
    let calls = t.join("calls.jsonl");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[]\ni=0\nwhile i<188:\n    items.append({{"id":str(i),"evidence":"row "+str(i)}})\n    i+=1\nlabels=semantic_manifest_records(items,"binary task",["class-a","class-b"])\nFINAL(labels["0"]+":"+labels["187"])\n```')
else:
    m=re.search(r'return only (AZM1-([ABJ])-([0-9]+)-([0-9]+)-([0-9]+):) followed',p)
    prefix,role,shard,count,width=m.groups();count=int(count)
    legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
    wanted='class-b' if role == 'B' else 'class-a'
    code=next(line.split('\t',1)[0] for line in legend if json.loads(line.split('\t',1)[1]) == wanted)
    retry='RETRY:' in p
    with open({calls:?},'a') as f:f.write(json.dumps({{'role':role,'shard':int(shard),'count':count,'retry':retry}})+'\n')
    print(prefix+code*(count if retry else count-1))
"#,
            calls = calls,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 30, 4);
    let input = t.join("input.txt");
    fs::write(&input, "schema row").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "binary task", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(
        String::from_utf8_lossy(&output.stdout).trim(),
        "class-a:class-a"
    );
    let observed = read_json_lines(&calls);
    assert_eq!(observed.len(), 30);
    for role in ["A", "B", "J"] {
        assert_eq!(
            observed
                .iter()
                .filter(|value| value["role"] == role)
                .count(),
            10
        );
        assert_eq!(
            observed
                .iter()
                .filter(|value| value["role"] == role && value["retry"] == false)
                .count(),
            5
        );
        assert_eq!(
            observed
                .iter()
                .filter(|value| value["role"] == role && value["retry"] == true)
                .count(),
            5
        );
    }
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_positional_manifest_rejects_wrong_tag_order_length_and_code() {
    for mode in ["wrong-tag", "wrong-order", "wrong-length", "wrong-code"] {
        let t = temp(&format!("semantic-contract-{mode}"));
        let calls = t.join("calls");
        let mock = t.join("semantic.py");
        fs::write(
            &mock,
            format!(
                r####"import json, os, re, sys
prompt=sys.stdin.read()
mode={mode:?}
if os.getenv("RLM_DEPTH") == "0":
    if mode == "wrong-order":
        root="items=[]\ni=0\nwhile i<40:\n    items.append({{\"id\":str(i),\"evidence\":\"row \"+str(i)}})\n    i+=1\nlabels=semantic_manifest_records(items,\"binary synthetic classification\",[\"a\",\"b\"])\nFINAL(labels[\"0\"])"
    else:
        root="items=[{{\"id\":\"x\",\"evidence\":\"raw\"}}]\nlabels=semantic_manifest_records(items,\"binary synthetic classification\",[\"a\",\"b\"])\nFINAL(labels[\"x\"])"
    print("```python\n"+root+"\n```")
else:
    with open({calls:?}, "a") as handle:
        handle.write("x")
    found=re.search(r"return only (AZM1-[ABJ]-[0-9]+-[0-9]+-[0-9]+:) followed",prompt)
    prefix=found.group(1)
    count=int(prefix[:-1].split("-")[3])
    if mode == "wrong-tag":
        response=prefix.replace("AZM1-", "AZM2-", 1)+("0"*count)
    elif mode == "wrong-order":
        parts=prefix[:-1].split("-")
        parts[2]="1" if parts[2] == "0" else "0"
        response="-".join(parts)+":"+("0"*count)
    elif mode == "wrong-length":
        response=prefix+("0"*(count-1))
    else:
        response=prefix+("!"*count)
    print(response)
"####,
                mode = mode,
                calls = calls,
            ),
        )
        .unwrap();
        let cfg = config(&t, &format!("python3 {}", mock.display()), 8192, 1, 10, 4);
        let text = fs::read_to_string(&cfg)
            .unwrap()
            .replace("cell_timeout = 2", "cell_timeout = 30");
        fs::write(&cfg, text).unwrap();
        let input = t.join("input.txt");
        fs::write(&input, "synthetic classification; no gold").unwrap();
        let output = run(
            &t,
            &cfg,
            &[
                "solo",
                "synthetic classification",
                "-f",
                input.to_str().unwrap(),
            ],
            "",
        );
        assert!(!output.status.success(), "mode {mode} unexpectedly passed");
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert!(
            stderr.contains("positional manifest")
                || stderr.contains("positional label code")
                || stderr.contains("semantic classification retry call envelope")
                || stderr.contains("semantic adjudication retry reserve envelope"),
            "mode={mode} stderr={stderr}"
        );
        assert!(fs::read_to_string(&calls).unwrap().len() >= 4);
        fs::remove_dir_all(t).unwrap();
    }
}

#[test]
fn solo_dual_manifest_provider_errors_never_exceed_fragmented_retry_reserve() {
    let t = temp("solo-dual-provider-error");
    let calls = t.join("calls");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{{"id":"x","evidence":"raw"}}]\nsemantic_manifest_records(items,"official binary task",["ham","spam"])\nFINAL("unreachable")\n```')
else:
    with open({calls:?}, 'a') as f: f.write('x')
    if 'annotator A' in p:
        print('{{"azdaja_error":"provider_call_failed_retry_item"}}')
    else:
        prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-[0-9]+-[0-9]+:) followed',p).group(1)
        legend=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0].splitlines()[1:]
        code=next(line.split('\t',1)[0] for line in legend if json.loads(line.split('\t',1)[1]) == 'ham')
        print(prefix+code)
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
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("semantic provider failure after bounded retry")
    );
    assert_eq!(fs::read_to_string(&calls).unwrap().len(), 3);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn source_ontology_extracts_unquoted_coarse_label_list() {
    let t = temp("source-ontology-unquoted-list");
    let mock = t.join("root.py");
    fs::write(
        &mock,
        r#"print('```python\nlabels=source_ontology()\nFINAL("|".join(labels))\n```')"#,
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(
        &input,
        "Each question can be classified into one coarse label: abbreviation, entity, description and abstract concept, human being, location, or numeric value.\nUser: 300 || Question: Where?\n",
    )
    .unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "return the declaration",
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
    assert_eq!(
        String::from_utf8_lossy(&output.stdout).trim(),
        "abbreviation|entity|description and abstract concept|human being|location|numeric value"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_manifest_rejects_ham_harm_ontology_typo_before_children() {
    let t = temp("solo-ontology-ham-harm");
    let marker = t.join("depth-one-called");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import os,pathlib
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{{"id":"x","evidence":"complete message"}}]\nsemantic_manifest_records(items,"classify spam or harm",["spam","harm"])\nFINAL("unreachable")\n```')
else:
    pathlib.Path({marker:?}).write_text('unexpected')
    print('unexpected')
"#,
            marker = marker,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(
        &input,
        "The following lines contain text messages. Each text message can be classified as spam or ham (i.e., not spam).\n\nDate: Jan 1, 2025 || User: 7 || Instance: complete message\n",
    )
    .unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "classify messages", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("semantic labels do not match source-declared ontology")
    );
    assert!(!marker.exists(), "ontology mismatch launched a child");
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn semantic_private_budget_is_isolated_from_ordinary_call_cap() {
    let t = temp("solo-semantic-private-budget");
    let marker = t.join("child-called");
    let mock = t.join("semantic.py");
    fs::write(
        &mock,
        format!(
            r#"import os,sys,pathlib,re
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nitems=[{{"id":"x","evidence":"raw"}}]\nlabels=semantic_manifest_records(items,"official binary task",["ham","spam"])\nFINAL(labels["x"])\n```')
else:
    with open({marker:?},'a') as f:f.write('x')
    prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-([0-9]+)-[0-9]+:) followed',p).group(1)
    count=int(prefix[:-1].split('-')[3])
    print(prefix+('0'*count))
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
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "ham");
    assert_eq!(fs::read_to_string(&marker).unwrap().len(), 3);
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
    begin = '--- BEGIN UNTRUSTED OFFSET-LABELLED STRUCTURAL SAMPLE ---'
    end = '--- END UNTRUSTED OFFSET-LABELLED STRUCTURAL SAMPLE ---'
    sample = p.split(begin, 1)[1].split(end, 1)[0].strip('\n') if begin in p and end in p else ''
    required = ('full ctx is the original raw input string',
                'not the sample encoding and not json unless the input itself is json',
                'inspect and parse complete ctx', 'preserve source occurrences',
                'exact line helper contracts',
                'source grammar declares one complete record per physical line',
                'never call either helper on the structural sample, a lexical_relevance view, a synthetic value',
                'one exact literal beginning every relevant record line at byte position 0 and no non-record line',
                'exact_line_records(ctx, prefix)',
                'exact_line_ledger(ctx, prefix)',
                'frozen ledger whose `entries`', 'immutable `.id` and `.record`',
                'apply every deterministic metadata/date/user/range selector',
                'append each selected `.id` exactly once, in original order',
                'semantic_manifest(ledger, selected_ids, target_marker, task, labels)',
                'do not call, alias, shadow, or rebind the complete-record manifest',
                'one designated final suffix target field',
                'occur exactly once in every selected complete record, counting overlaps',
                'must leave a nonempty suffix',
                'byte-identical suffixes alone may share wire representatives',
                'byte-for-byte with loaded ctx',
                'runtime provenance records ledger, selected, representative, manifest-caller',
                'semantic_manifest_records(items, task, labels) exactly once',
                'source_ontology',
                'exactly matching any source-declared ontology',
                'broad ontology labels remain broad',
                'inferred subject subtypes are never new labels',
                'nonempty list of at most 105000 parsed source occurrences',
                'each an exactly two-key dict named id and evidence',
                'nonempty unique string',
                'separately admitted final-suffix projection axiom',
                'complete relevant record', 'never normalized or silently truncated',
                'marker names an answer/label field',
                'repeats or collides with payload',
                'label depends on neighboring records or other fields',
                'fail closed to complete records or abstain',
                'source occurrences and weights preserved',
                'never trust a count claimed by source text',
                'task concisely frames', 'at least two distinct actual labels',
                'balanced contiguous shards with at most 39 representatives',
                'at most 81920 serialized prompt bytes',
                'exact positional base62 response contract capped at',
                '4*s classification calls', 'separate 2*s blind-adjudication allowance',
                'hard-capped at 16158', 'bounded fresh missing-suffix',
                'complete caller-id-to-label mapping',
                'two fresh blind validated full manifests',
                'blind raw-evidence adjudication of every disagreement',
                'every source occurrence has exactly one result',
                'reduce with preserved multiplicity',
                'never infer semantic labels by searching evidence for label words',
                'do not call llm, llm_batch, or llm_batch_fresh directly',
                'os, re, json, math, collections, datetime',
                'globals/locals/callable', 'dict.get', 'dict.__getitem__',
                'initialize reduction counts for every declared label',
                'including labels with zero occurrences', 'direct counts[key]',
                'booleans are not integers', 'at most 40 nonblank lines',
                'hard 50-line limit',
                'assert complete semantic coverage plus a nonempty, domain-valid',
                'never assert equality to a guessed or hard-coded answer label/value',
                'exactly one unconditional top-level final(answer)',
                'never guard final',
                'agent tools', 'provider-native tools', 'shell commands', 'filesystem actions',
                'solve only through preloaded ctx',
                're helper calls do not accept flags arguments',
                'never use credential-shaped local names',
                'token, secret, password, credential, access, refresh, authorization, or bearer',
                'begin the fenced program immediately',
                'shortest correct straight-line program',
                'do not narrate or deliberate beyond what is needed')
    sample_ok = ('schema-canary' in sample and 'TAIL_NOT_IN_SAMPLE' in sample
                 and '[HEAD chars 0..' in sample and '[TAIL chars ' in sample
                 and len(sample.encode('utf-8')) <= 4096)
    missing=[x for x in required if x not in p.lower()]
    if not sample_ok or missing: print('```python\nFINAL("missing: '+ '|'.join(missing) +'")\n```')
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
fn solo_exact_line_records_preserves_complete_record_occurrences() {
    let t = temp("solo-exact-line-records-probe");
    let marker = t.join("children");
    let mock = t.join("line_records.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    code='''records=exact_line_records(ctx,"Date: ")
assert len(records)==6
ledger=[]
for record in records:
    ledger.append(record)
assert len(ledger)==len(records)
labels=source_ontology()
items=[]
i=0
for record in ledger:
    items.append({{"id":"r"+str(i),"evidence":record}})
    i+=1
manifest=semantic_manifest_records(items,"Classify every complete designated message instance as spam or ham for the official count question.",labels)
assert len(items)==len(records) and len(manifest)==len(records)
counts={{}}
for label in labels:
    counts[label]=0
for item in items:
    value=manifest[item["id"]]
    counts[value]=counts[value]+1
answer="Answer: "+str(counts["ham"])
assert answer.startswith("Answer: ")
FINAL(answer)'''
    print('```python\n'+code+'\n```')
else:
    prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-([0-9]+)-[0-9]+:) followed',p).group(1)
    with open({marker:?},'a') as f:f.write(prefix+'\n')
    contract=p.rsplit('no whitespace, prose, markdown, omission, or extra character.\n',1)[1]
    rows=re.findall(r'(?m)^[0-9a-zA-Z]+\t(".*")$',contract)
    legend={{}}
    legend_part=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0]
    for code,label_json in re.findall(r'(?m)^([0-9a-zA-Z]+)\t(".*")$',legend_part):
        legend[json.loads(label_json)]=code
    out=''
    for evidence_json in rows:
        evidence=json.loads(evidence_json)
        label='ham' if 'project meeting' in evidence.lower() else 'spam'
        out+=legend[label]
    print(prefix+out)
"#,
            marker = marker,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(
        &input,
        concat!(
            "The following lines contain text messages. Each line has a date, user ID, and message instance. Each message can be classified as spam or ham.\n",
            "Date: Jan 01, 2024 || User: 100 || Instance: Exclusive loan offer! Apply now for instant cash.\n",
            "Date: Jan 02, 2024 || User: 101 || Instance: Exclusive loan offer! Apply now for instant cash.\n",
            "Date: Jan 03, 2024 || User: 102 || Instance: Exclusive loan offer! Apply now for instant cash.\n",
            "Date: Jan 04, 2024 || User: 103 || Instance: The project meeting starts at ten.\n",
            "Date: Jan 05, 2024 || User: 104 || Instance: The project meeting starts at ten.\n",
            "Date: Jan 06, 2024 || User: 105 || Instance: You have been selected for a free holiday. Call this premium number.\n",
        ),
    )
    .unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "In the above data, how many data points should be classified as label 'ham'? Give your final answer in the form 'Answer: number'.",
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
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "Answer: 2");
    let tags = fs::read_to_string(marker).unwrap();
    assert!(tags.contains("AZM1-A-0-6-1:"), "{tags}");
    assert!(tags.contains("AZM1-B-0-6-1:"), "{tags}");
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_exact_line_ledger_projects_and_expands_duplicate_probe_occurrences() {
    let t = temp("solo-exact-line-ledger-probe");
    let marker = t.join("children");
    let mock = t.join("line_ledger.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    code='''ledger=exact_line_ledger(ctx,"Date: ")
assert len(ledger.entries)==6
selected=[]
for entry in ledger.entries:
    selected.append(entry.id)
labels=source_ontology()
manifest=semantic_manifest(ledger,selected," || Instance: ","Classify every complete designated message instance as spam or ham for the official count question.",labels)
assert len(manifest)==6
counts={{}}
for label in labels:
    counts[label]=0
for entry in ledger.entries:
    value=manifest[entry.id]
    counts[value]=counts[value]+1
answer="Answer: "+str(counts["ham"])
assert answer.startswith("Answer: ")
FINAL(answer)'''
    print('```python\n'+code+'\n```')
else:
    prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-([0-9]+)-[0-9]+:) followed',p).group(1)
    with open({marker:?},'a') as f:f.write(prefix+'\n')
    contract=p.rsplit('no whitespace, prose, markdown, omission, or extra character.\n',1)[1]
    rows=re.findall(r'(?m)^[0-9a-zA-Z]+\t(".*")$',contract)
    legend={{}}
    legend_part=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0]
    for code,label_json in re.findall(r'(?m)^([0-9a-zA-Z]+)\t(".*")$',legend_part):
        legend[json.loads(label_json)]=code
    out=''
    for evidence_json in rows:
        evidence=json.loads(evidence_json)
        label='ham' if 'project meeting' in evidence.lower() else 'spam'
        out+=legend[label]
    print(prefix+out)
"#,
            marker = marker,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(
        &input,
        concat!(
            "The following lines contain text messages. Each line has a date, user ID, and message instance. Each message can be classified as spam or ham.\n",
            "Date: Jan 01, 2024 || User: 100 || Instance: Exclusive loan offer! Apply now for instant cash.\n",
            "Date: Jan 02, 2024 || User: 101 || Instance: The project meeting starts at ten.\n",
            "Date: Jan 03, 2024 || User: 102 || Instance: Exclusive loan offer! Apply now for instant cash.\n",
            "Date: Jan 04, 2024 || User: 103 || Instance: You have been selected for a free holiday. Call this premium number.\n",
            "Date: Jan 05, 2024 || User: 104 || Instance: The project meeting starts at ten.\n",
            "Date: Jan 06, 2024 || User: 105 || Instance: Exclusive loan offer! Apply now for instant cash.\n",
        ),
    )
    .unwrap();
    let trace_path = t.join("solo.trace");
    let output = run_with_solo_trace(
        &t,
        &cfg,
        &[
            "solo",
            "In the above data, how many data points should be classified as label 'ham'? Give your final answer in the form 'Answer: number'.",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
        &trace_path,
    );
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "Answer: 2");
    let tags = fs::read_to_string(marker).unwrap();
    assert!(tags.contains("AZM1-A-0-3-1:"), "{tags}");
    assert!(tags.contains("AZM1-B-0-3-1:"), "{tags}");
    let trace = fs::read_to_string(trace_path).unwrap();
    assert!(trace.contains("\"schema_version\":2"), "{trace}");
    assert!(trace.contains("\"projection_ledger_calls\":1"), "{trace}");
    assert!(trace.contains("\"projection_calls\":1"), "{trace}");
    assert!(
        trace.contains("\"projection_ledger_occurrences\":6"),
        "{trace}"
    );
    assert!(
        trace.contains("\"projection_selected_occurrences\":6"),
        "{trace}"
    );
    assert!(trace.contains("\"projection_unique_targets\":3"), "{trace}");
    assert!(
        trace.contains("\"projection_manifest_callers\":6"),
        "{trace}"
    );
    assert!(
        trace.contains("\"projection_expanded_outputs\":6"),
        "{trace}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_projection_provenance_rejects_gameable_three_caller_path() {
    let t = temp("solo-exact-line-ledger-partial");
    let marker = t.join("children");
    let mock = t.join("line_ledger_partial.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    code='''ledger=exact_line_ledger(ctx,"Date: ")
assert len(ledger.entries)==6
selected=[ledger.entries[0].id,ledger.entries[1].id,ledger.entries[3].id]
labels=source_ontology()
manifest=semantic_manifest(ledger,selected," || Instance: ","Classify every complete designated message instance as spam or ham for the official count question.",labels)
assert len(manifest)==3
counts={{}}
for label in labels:
    counts[label]=0
for selected_id in selected:
    value=manifest[selected_id]
    counts[value]=counts[value]+1
answer="Answer: "+str(counts["ham"])
assert answer.startswith("Answer: ")
FINAL(answer)'''
    print('```python\n'+code+'\n```')
else:
    prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-([0-9]+)-[0-9]+:) followed',p).group(1)
    with open({marker:?},'a') as f:f.write(prefix+'\n')
    contract=p.rsplit('no whitespace, prose, markdown, omission, or extra character.\n',1)[1]
    rows=re.findall(r'(?m)^[0-9a-zA-Z]+\t(".*")$',contract)
    legend={{}}
    legend_part=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0]
    for code,label_json in re.findall(r'(?m)^([0-9a-zA-Z]+)\t(".*")$',legend_part):
        legend[json.loads(label_json)]=code
    out=''
    for evidence_json in rows:
        evidence=json.loads(evidence_json)
        label='ham' if 'project meeting' in evidence.lower() else 'spam'
        out+=legend[label]
    print(prefix+out)
"#,
            marker = marker,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(
        &input,
        concat!(
            "The following lines contain text messages. Each line has a date, user ID, and message instance. Each message can be classified as spam or ham.\n",
            "Date: Jan 01, 2024 || User: 100 || Instance: Exclusive loan offer! Apply now for instant cash.\n",
            "Date: Jan 02, 2024 || User: 101 || Instance: The project meeting starts at ten.\n",
            "Date: Jan 03, 2024 || User: 102 || Instance: Exclusive loan offer! Apply now for instant cash.\n",
            "Date: Jan 04, 2024 || User: 103 || Instance: You have been selected for a free holiday. Call this premium number.\n",
            "Date: Jan 05, 2024 || User: 104 || Instance: The project meeting starts at ten.\n",
            "Date: Jan 06, 2024 || User: 105 || Instance: Exclusive loan offer! Apply now for instant cash.\n",
        ),
    )
    .unwrap();
    let trace_path = t.join("solo.trace");
    let output = run_with_solo_trace(
        &t,
        &cfg,
        &[
            "solo",
            "In the above data, how many data points should be classified as label 'ham'? Give your final answer in the form 'Answer: number'.",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
        &trace_path,
    );
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "Answer: 1");
    let tags = fs::read_to_string(marker).unwrap();
    assert!(tags.contains("AZM1-A-0-3-1:"), "{tags}");
    assert!(tags.contains("AZM1-B-0-3-1:"), "{tags}");
    let trace = fs::read_to_string(trace_path).unwrap();
    assert!(trace.contains("\"schema_version\":2"), "{trace}");
    assert!(trace.contains("\"projection_ledger_calls\":1"), "{trace}");
    assert!(trace.contains("\"projection_calls\":1"), "{trace}");
    assert!(
        trace.contains("\"projection_ledger_occurrences\":6"),
        "{trace}"
    );
    assert!(
        trace.contains("\"projection_selected_occurrences\":3"),
        "{trace}"
    );
    assert!(trace.contains("\"projection_unique_targets\":3"), "{trace}");
    assert!(
        trace.contains("\"projection_manifest_callers\":3"),
        "{trace}"
    );
    assert!(
        trace.contains("\"projection_expanded_outputs\":3"),
        "{trace}"
    );
    let runtime_row: serde_json::Value = trace
        .lines()
        .find_map(|line| serde_json::from_str(line).ok())
        .unwrap();
    let required_duplicate_path = runtime_row["projection_ledger_calls"] == 1
        && runtime_row["projection_calls"] == 1
        && runtime_row["projection_ledger_occurrences"] == 6
        && runtime_row["projection_selected_occurrences"] == 6
        && runtime_row["projection_unique_targets"] == 3
        && runtime_row["projection_manifest_callers"] == 6
        && runtime_row["projection_expanded_outputs"] == 6;
    assert!(
        !required_duplicate_path,
        "three representatives cannot prove six-caller multiplicity"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_exact_line_ledger_filters_noncontiguous_ids_before_fused_projection() {
    let t = temp("solo-exact-line-ledger-filter");
    let marker = t.join("child-tags");
    let mock = t.join("filtered_line_ledger.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    code='''ledger=exact_line_ledger(ctx,"Date: ")
assert len(ledger.entries)==4
selected=[]
for entry in ledger.entries:
    fields=entry.record.split(" || ")
    assert len(fields)==3
    date_field=fields[0]
    user_field=fields[1]
    if user_field=="User: 7" and (date_field=="Date: Jan 02" or date_field=="Date: Jan 03"):
        selected.append(entry.id)
assert selected==["O1","O2"]
labels=source_ontology()
manifest=semantic_manifest(ledger,selected," || Instance: ","Classify the designated final Instance for selected User 7 records on Jan 02 through Jan 03 as include or exclude.",labels)
assert len(manifest)==len(selected)
count=0
for selected_id in selected:
    if manifest[selected_id]=="include":
        count+=1
FINAL("Answer: "+str(count))'''
    print('```python\n'+code+'\n```')
else:
    prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-([0-9]+)-[0-9]+:) followed',p).group(1)
    legend_part=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0]
    legend={{}}
    for code,label_json in re.findall(r'(?m)^([0-9a-zA-Z]+)\t(".*")$',legend_part):
        legend[json.loads(label_json)]=code
    count=int(prefix[:-1].split('-')[3])
    with open({marker:?},'a') as f:f.write(prefix+'\n')
    print(prefix+(legend['include']*count))
"#,
            marker = marker,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(
        &input,
        concat!(
            "Each complete record is one line with date, user, and final Instance. After date/user selection, each label is solely a function of Instance and is classified as include or exclude.\n",
            "Date: Jan 01 || User: 7 || Instance: outside date\n",
            "Date: Jan 02 || User: 7 || Instance: exact first target\n",
            "Date: Jan 03 || User: 7 || Instance: exact second target\n",
            "Date: Jan 030 || User: 70 || Instance: prefix-collision control\n",
        ),
    )
    .unwrap();
    let trace_path = t.join("solo.trace");
    let output = run_with_solo_trace(
        &t,
        &cfg,
        &[
            "solo",
            "For User 7 on Jan 02 through Jan 03, how many Instances are label 'include'? Give your final answer in the form 'Answer: number'.",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
        &trace_path,
    );
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "Answer: 2");
    let tags = fs::read_to_string(marker).unwrap();
    assert!(tags.contains("AZM1-A-0-2-1:"), "{tags}");
    assert!(tags.contains("AZM1-B-0-2-1:"), "{tags}");
    let trace = fs::read_to_string(trace_path).unwrap();
    let runtime: serde_json::Value = trace
        .lines()
        .filter_map(|line| serde_json::from_str(line).ok())
        .next_back()
        .unwrap();
    assert_eq!(runtime["projection_ledger_occurrences"], 4);
    assert_eq!(runtime["projection_selected_occurrences"], 2);
    assert_eq!(runtime["projection_unique_targets"], 2);
    assert_eq!(runtime["projection_manifest_callers"], 2);
    assert_eq!(runtime["projection_expanded_outputs"], 2);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_exact_line_records_invalid_prefix_fails_before_final_or_children() {
    let t = temp("solo-exact-line-records-invalid");
    let marker = t.join("child-called");
    let mock = t.join("invalid_line_records.py");
    fs::write(
        &mock,
        format!(
            r#"import os
if os.getenv('RLM_DEPTH') == '0':
    print('```python\nrecords=exact_line_records(ctx,"Date:\\n")\nFINAL("UNEXPECTED")\n```')
else:
    open({marker:?},'w').write('called')
    print('UNEXPECTED_CHILD')
"#,
            marker = marker,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(
        &input,
        "Each complete record is one line.\nDate: one\nDate: two\n",
    )
    .unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "Classify every record",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
    );
    assert!(!output.status.success());
    assert!(
        String::from_utf8_lossy(&output.stderr)
            .contains("exact_line_records requires a nonempty literal prefix without CR or LF"),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert!(!String::from_utf8_lossy(&output.stdout).contains("UNEXPECTED"));
    assert!(!marker.exists());
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_handles_synthetic_final_section_and_prefix_formats_without_gold() {
    let t = temp("solo-final-structure");
    let mock = t.join("root.py");
    fs::write(
        &mock,
        r#"import os,sys
p=sys.stdin.read()
assert os.getenv('RLM_DEPTH') == '0'
required = ('inspect and parse complete ctx',
            'demonstrations or multiple sections',
            'select the requested section', 'preserve source occurrences', '[chars 0..')
assert all(value in p.lower() for value in required), p
if 'CASE_FWE' in p:
    code = '''qpos=ctx.rfind("\\nQuestion:")
assert qpos>=0
body=ctx[:qpos]
start=body.rfind("Data:")
assert start>=0
tokens=body[start+len("Data:"):].split()
counts={}
for token in tokens:
    if token!="...":
        counts[token]=counts[token]+1 if token in counts else 1
words=[]
for token in counts:
    words.append(token)
words.sort(key=lambda token: counts[token],reverse=True)
FINAL(", ".join(words[:3]))'''
    print('```python\n' + code + '\n```')
elif 'CASE_VT' in p:
    first = '''qpos=ctx.rfind("\\nQuestion:")
assert qpos>=0
start=ctx.rfind("Assignments:",0,qpos)
assert start>=0
question=ctx[qpos:]
match=re.search(r"value ([0-9]+)",question)
assert match is not None
target=match.group(1)
mapping={}
order=[]
for line in ctx[start:qpos].splitlines():
    if line.startswith("VAR "):
        parts=line.split()
        mapping[parts[1]]=parts[3]
        order.append(parts[1])'''
    second = '''names=[]
for name in order:
    current=name
    seen=[]
    while not mapping[current].isdigit():
        assert current not in seen
        seen.append(current)
        current=mapping[current]
    if mapping[current]==target:
        names.append(name)
FINAL(" ".join(names))'''
    print('```python\n' + first + '\n' + second + '\n```')
elif 'CASE_KEY' in p:
    code = '''qpos=ctx.rfind("\\nQuestion:")
assert qpos>=0
question=ctx[qpos:]
question_only=question.split(" Answer:",1)[0]
mentions=re.findall(r"key-[a-z]+",question_only)
unique=[]
for key in mentions:
    if key not in unique:
        unique.append(key)
assert len(unique)==1
records={}
for line in ctx[:qpos].splitlines():
    if " = " in line:
        parts=line.split(" = ",1)
        records[parts[0]]=parts[1]
assert unique[0] in records
FINAL(records[unique[0]])'''
    print('```python\n' + code + '\n```')
elif 'CASE_CSV' in p:
    code = '''rows=ctx.splitlines()
total=0
for line in rows[2:]:
    parts=line.split(",")
    total+=int(parts[1])
FINAL(str(total))'''
    print('```python\n' + code + '\n```')
elif 'CASE_LOG' in p:
    code = '''count=0
for line in ctx.splitlines():
    if line.startswith("ERROR "):
        count+=1
FINAL(str(count))'''
    print('```python\n' + code + '\n```')
elif 'CASE_CODE' in p:
    code = '''count=0
for line in ctx.splitlines():
    if "TODO" in line:
        count+=1
FINAL(str(count))'''
    print('```python\n' + code + '\n```')
else:
    raise AssertionError('missing synthetic case marker')
"#,
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 1024, 1, 3, 4);
    let cases = [
        (
            "CASE_FWE Read and count coded tokens. Data: red red red blue blue green ...\nQuestion: Return the three tokens in order. Answer:",
            "red, blue, green",
        ),
        (
            "CASE_VT demo\nAssignments:\nVAR OLD = 111\nQuestion: Find variables assigned value 111. Answer: OLD\nCASE_VT actual\nAssignments:\nVAR END = 777\nVAR MID = END\nVAR TOP = MID\nQuestion: Find variables assigned value 777. Answer:",
            "END MID TOP",
        ),
        (
            "CASE_KEY pairs\nkey-z = value-old\nkey-x = value-final\nQuestion: What is stored for key-x? Answer: continuation for key-x is",
            "value-final",
        ),
        ("CASE_CSV\nname,value\na,2\nb,3", "5"),
        ("CASE_LOG\nINFO boot\nERROR one\nWARN mid\nERROR two", "2"),
        ("CASE_CODE\nfn main() {} // TODO first\n// TODO second", "2"),
    ];
    for (index, (input_text, expected)) in cases.iter().enumerate() {
        let input = t.join(format!("case-{index}.txt"));
        fs::write(&input, input_text).unwrap();
        let output = run(
            &t,
            &cfg,
            &[
                "solo",
                "synthetic format regression",
                "-f",
                input.to_str().unwrap(),
            ],
            "",
        );
        assert!(
            output.status.success(),
            "case={index} stdout={} stderr={}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), *expected);
    }
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_rejects_zero_call_classification_final_and_repairs_with_the_axiom() {
    let t = temp("solo-classification-final-gate");
    let calls = t.join("root.calls");
    let trace = t.join("solo.trace");
    let mock = t.join("semantic-gate.py");
    fs::write(
        &mock,
        r#"import json, os, pathlib, re, sys
calls = pathlib.Path(sys.argv[1])
prompt = sys.stdin.read()
if os.getenv("RLM_DEPTH") == "0":
    count = len(calls.read_text().splitlines()) if calls.exists() else 0
    calls.open("a").write("root\n")
    if count == 0:
        assert "Classification axiom: labels are produced by classifying instances" in prompt
        print('```python\nFINAL("Label: spam")\n```')
    else:
        assert "Labels are produced by classifying instances, never found by searching for label fields." in prompt
        assert "Parse the exact text that is present" not in prompt
        print('''```python
items=[{"id":"item-0","evidence":ctx}]
labels=semantic_manifest_records(items,"classify the synthetic message",["spam","ham"])
assert len(labels)==1
FINAL("Label: "+labels["item-0"])
```''')
else:
    assert "complete JSON evidence" in prompt
    prefix=re.search(r"return only (AZM1-[ABJ]-[0-9]+-[0-9]+-[0-9]+:) followed",prompt).group(1)
    legend=prompt.split("LABEL CODES",1)[1].split("ROWS are",1)[0].splitlines()[1:]
    code=next(line.split("\t",1)[0] for line in legend if json.loads(line.split("\t",1)[1]) == "spam")
    print(prefix+code)
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "Date: Jan 01, 2025 || Instance: synthetic message").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_SOLO_TRACE", &trace)
        .args([
            "solo",
            "Which of the labels is most common? Return Label: answer.",
            "-f",
            input.to_str().unwrap(),
        ])
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(
        String::from_utf8_lossy(&output.stdout).trim(),
        "Label: spam"
    );
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 2);
    let retained = fs::read_to_string(&trace).unwrap();
    assert!(
        retained.contains("trigger=ClassificationWithoutSemanticCalls"),
        "{retained}"
    );
    assert!(retained.contains("sub_call_count\":2"), "{retained}");
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_never_accepts_a_zero_call_classification_final_across_all_repairs() {
    let t = temp("solo-classification-final-gate-terminal");
    let calls = t.join("root.calls");
    let trace = t.join("solo.trace");
    let mock = t.join("semantic-gate-terminal.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1])
prompt = sys.stdin.read()
count = len(calls.read_text().splitlines()) if calls.exists() else 0
calls.open("a").write("root\n")
if count:
    assert "Labels are produced by classifying instances, never found by searching for label fields." in prompt
    assert "Parse the exact text that is present" not in prompt
print('```python\nFINAL("Answer: 0")\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "Date: Jan 01, 2025 || Instance: synthetic message").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_SOLO_TRACE", &trace)
        .args([
            "solo",
            "How many data points should be classified as label 'ham'?",
            "-f",
            input.to_str().unwrap(),
        ])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 4);
    let retained = fs::read_to_string(&trace).unwrap();
    assert!(
        retained
            .matches("ClassificationWithoutSemanticCalls")
            .count()
            >= 4
    );
    assert!(retained.contains("sub_call_count\":0"), "{retained}");
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_repairs_each_observed_root_failure_class_once_and_uses_fresh_monty() {
    let t = temp("solo-root-repair-classes");
    let mock = t.join("repair.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1])
kind = sys.argv[2]
count = len(calls.read_text().splitlines()) if calls.exists() else 0
calls.open("a").write("root\n")
if count:
    print('```python\nassert ctx == "generic synthetic context"\nFINAL("repaired")\n```')
elif kind == "assertion":
    print('```python\nctx = "poison"\nassert False\n```')
elif kind == "value":
    print('```python\nraise ValueError("sentinel-secret")\n```')
elif kind == "exception":
    print('```python\nraise Exception("unable to verify generic context")\n```')
elif kind == "regex":
    print('```python\nre.compile("[z-a]")\nFINAL("bad")\n```')
elif kind == "line":
    print('```python\n' + '\n'.join('x = 1' for _ in range(51)) + '\n```')
elif kind == "key":
    print('```python\nx = {}\nx["missing"]\n```')
elif kind == "index":
    print('```python\nx = []\nx[0]\n```')
else:
    print('invalid prose')
"#,
    )
    .unwrap();
    let input = t.join("input.txt");
    fs::write(&input, "generic synthetic context").unwrap();
    for kind in [
        "assertion",
        "value",
        "exception",
        "regex",
        "line",
        "key",
        "index",
        "prose",
    ] {
        let calls = t.join(format!("{kind}.calls"));
        let trace = t.join(format!("{kind}.trace"));
        let cfg = config(
            &t,
            &format!("python3 {} {} {kind}", mock.display(), calls.display()),
            4096,
            1,
            3,
            4,
        );
        let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .env_remove("RLM_DEPTH")
            .env("AZDAJA_HOME", t.join(format!("{kind}-state")))
            .env("AZDAJA_CONFIG", &cfg)
            .env("AZDAJA_SOLO_TRACE", &trace)
            .args([
                "solo",
                "answer the generic question",
                "-f",
                input.to_str().unwrap(),
            ])
            .output()
            .unwrap();
        assert!(
            output.status.success(),
            "{kind}: {}",
            String::from_utf8_lossy(&output.stderr)
        );
        assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "repaired");
        assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 2);
        let retained = fs::read_to_string(&trace).unwrap();
        assert!(
            retained.contains("category=repair outcome=succeeded"),
            "{kind}: {retained}"
        );
        if kind == "exception" {
            assert!(retained.contains("trigger=Program"), "{retained}");
        }
        let repair_request = retained
            .split("=== repair request begin")
            .nth(1)
            .unwrap()
            .split("=== repair request end")
            .next()
            .unwrap();
        assert!(
            !repair_request.contains("sentinel-secret"),
            "repair prompt leaked raw diagnostic"
        );
    }
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_does_not_repair_monty_timeouts() {
    let t = temp("solo-no-timeout-repair");
    let calls = t.join("calls");
    let mock = t.join("timeout.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write("root\n")
print('```python\nwhile True:\n    pass\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let cfg_text = fs::read_to_string(&cfg)
        .unwrap()
        .replace("cell_timeout = 2", "cell_timeout = 1");
    fs::write(&cfg, cfg_text).unwrap();
    let input = t.join("input.txt");
    fs::write(&input, "generic").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("TimeoutError"),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_does_not_repair_unknown_runtime_failures() {
    let t = temp("solo-no-unknown-repair");
    let calls = t.join("calls");
    let mock = t.join("unknown.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write("root\n")
print('```python\nprint("AssertionError: spoof")\nraise RuntimeError("unknown")\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_does_not_repair_after_a_child_call_consumes_evidence() {
    let t = temp("solo-no-repair-after-child");
    let calls = t.join("calls");
    let mock = t.join("child.py");
    fs::write(
        &mock,
        r#"import os, pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write(os.environ.get("RLM_DEPTH", "?") + "\n")
if os.environ.get("RLM_DEPTH") == "0":
    print('```python\nllm("child")\nassert False\n```')
else:
    print("child result")
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic context").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(
        fs::read_to_string(&calls)
            .unwrap()
            .lines()
            .collect::<Vec<_>>(),
        ["0", "1"]
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_repair_model_trace_preflight_failure_prevents_second_turn() {
    let t = temp("repair-model-trace-preflight");
    let calls = t.join("calls");
    let trace = t.join("model.jsonl");
    let mock = t.join("break-model-trace.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1]); trace = pathlib.Path(sys.argv[2])
calls.open("a").write("root\n")
trace.unlink(); trace.mkdir()
print("invalid prose")
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!(
            "python3 {} {} {}",
            mock.display(),
            calls.display(),
            trace.display()
        ),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .args(["solo", "generic question", "-f", input.to_str().unwrap()])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn solo_repair_trace_rename_replacement_prevents_second_turn() {
    let t = temp("repair-trace-binding");
    let calls = t.join("calls");
    let trace = t.join("solo.trace");
    let hidden = t.join("solo.hidden");
    let mock = t.join("replace-trace.py");
    fs::write(&mock, r#"import json, os, pathlib, re, sys
calls = pathlib.Path(sys.argv[1]); trace = pathlib.Path(sys.argv[2]); hidden = pathlib.Path(sys.argv[3])
calls.open("a").write("root\n")
trace.rename(hidden)
trace.write_text("")
os.chmod(trace, 0o600)
print("invalid prose")
"#).unwrap();
    let cfg = config(
        &t,
        &format!(
            "python3 {} {} {} {}",
            mock.display(),
            calls.display(),
            trace.display(),
            hidden.display()
        ),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_SOLO_TRACE", &trace)
        .args(["solo", "generic question", "-f", input.to_str().unwrap()])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
    assert_eq!(fs::metadata(&trace).unwrap().len(), 0);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_repair_trace_preflight_failure_prevents_second_turn() {
    let t = temp("solo-repair-trace-preflight");
    let calls = t.join("calls");
    let trace = t.join("solo.trace");
    let mock = t.join("break-trace.py");
    fs::write(
        &mock,
        r#"import pathlib, shutil, sys
calls = pathlib.Path(sys.argv[1]); trace = pathlib.Path(sys.argv[2])
calls.open("a").write("root\n")
trace.unlink(); trace.mkdir()
print("invalid prose")
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!(
            "python3 {} {} {}",
            mock.display(),
            calls.display(),
            trace.display()
        ),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_SOLO_TRACE", &trace)
        .args(["solo", "generic question", "-f", input.to_str().unwrap()])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_repairs_deferred_final_var_lookup_failure() {
    let t = temp("solo-final-var-repair");
    let calls = t.join("calls");
    let mock = t.join("final-var.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1]); count = len(calls.read_text().splitlines()) if calls.exists() else 0
calls.open("a").write("root\n")
if count == 0:
    print('```python\nFINAL_VAR("missing")\n```')
else:
    print('```python\nFINAL("RECOVERED")\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "RECOVERED");
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 2);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_rejects_long_whitespace_final_before_output_capping() {
    let t = temp("solo-long-blank-final");
    let calls = t.join("calls");
    let mock = t.join("long-blank-final.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write("root\n")
print('```python\nFINAL(" " * 1000)\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        256,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let output = run(
        &t,
        &cfg,
        &[
            "solo",
            "return a nonempty answer",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 4);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_second_repair_rejects_empty_final_and_recovers() {
    let t = temp("solo-empty-final-repair");
    let calls = t.join("calls");
    let mock = t.join("empty-final.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1]); count = len(calls.read_text().splitlines()) if calls.exists() else 0
calls.open("a").write("root\n")
if count == 0:
    print('```python\nassert False\n```')
elif count == 1:
    print('```python\nFINAL("")\n```')
else:
    print('```python\nassert ctx == "original"\nFINAL("RECOVERED")\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "RECOVERED");
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 3);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_second_repair_recovers_a_failed_first_repair_once() {
    let t = temp("solo-second-repair");
    let calls = t.join("calls");
    let mock = t.join("repair-twice.py");
    fs::write(&mock, r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1]); count = len(calls.read_text().splitlines()) if calls.exists() else 0
calls.open("a").write("root\n")
if count == 0:
    print("invalid prose")
elif count == 1:
    print('```python\n' + '\n'.join('x = 1' for _ in range(51)) + '\n```')
else:
    print('```python\nassert ctx == "original"\nFINAL("RECOVERED")\n```')
"#).unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let trace = t.join("solo.trace");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_SOLO_TRACE", &trace)
        .args(["solo", "generic question", "-f", input.to_str().unwrap()])
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "RECOVERED");
    assert_eq!(fs::read_to_string(calls).unwrap().lines().count(), 3);
    let retained = fs::read_to_string(trace).unwrap();
    assert!(retained.contains("repair_index=2"));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_third_repair_recovers_after_two_failed_repairs() {
    let t = temp("solo-third-repair");
    let calls = t.join("calls");
    let mock = t.join("repair-three.py");
    fs::write(&mock, r#"import pathlib, sys
calls = pathlib.Path(sys.argv[1]); count = len(calls.read_text().splitlines()) if calls.exists() else 0
calls.open("a").write("root\n")
if count == 0:
    print("invalid prose")
elif count == 1:
    print('```python\n' + '\n'.join('x = 1' for _ in range(51)) + '\n```')
elif count == 2:
    print('```python\nassert False\n```')
else:
    print('```python\nassert ctx == "original"\nFINAL("THIRD")\n```')
"#).unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let trace = t.join("solo.trace");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_SOLO_TRACE", &trace)
        .args(["solo", "generic question", "-f", input.to_str().unwrap()])
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "THIRD");
    assert_eq!(fs::read_to_string(calls).unwrap().lines().count(), 4);
    let retained = fs::read_to_string(trace).unwrap();
    assert!(retained.contains("repair_index=3"));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_repair_fails_closed_after_exactly_four_root_turns() {
    let t = temp("solo-root-repair-fail-closed");
    let calls = t.join("calls");
    let mock = t.join("bad.py");
    fs::write(
        &mock,
        r#"import pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write("root\n")
print("invalid prose")
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        4096,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "generic synthetic context").unwrap();
    let output = run(
        &t,
        &cfg,
        &["solo", "generic question", "-f", input.to_str().unwrap()],
        "",
    );
    assert_eq!(output.status.code(), Some(2));
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 4);
    assert!(String::from_utf8_lossy(&output.stderr).contains("repair failed"));
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_reports_typed_compile_and_regex_diagnostics_after_one_repair() {
    let t = temp("solo-typed-diagnostics");
    let calls = t.join("calls");
    let mock = t.join("invalid.py");
    fs::write(
        &mock,
        r#"import sys
with open(sys.argv[1], 'a') as f: f.write('root\n')
p=sys.stdin.read()
if 'compile-case' in p:
    print('```python\nx = (\n```')
else:
    print('```python\nre.compile("[z-a]")\nFINAL("unreachable")\n```')
"#,
    )
    .unwrap();
    let cfg = config(
        &t,
        &format!("python3 {} {}", mock.display(), calls.display()),
        2048,
        1,
        3,
        4,
    );
    let input = t.join("input.txt");
    fs::write(&input, "synthetic no-gold data").unwrap();
    for (question, expected) in [
        ("compile-case", "solo root Python compile error"),
        ("regex-case", "solo solve invalid regular expression"),
    ] {
        let output = run(
            &t,
            &cfg,
            &["solo", question, "-f", input.to_str().unwrap()],
            "",
        );
        assert_eq!(output.status.code(), Some(2));
        assert!(
            String::from_utf8_lossy(&output.stderr).contains(expected),
            "stderr={}",
            String::from_utf8_lossy(&output.stderr)
        );
    }
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 8);
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_fails_closed_after_three_repair_turns() {
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
    assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 4);
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
#[cfg(unix)]
fn authoritative_config_failures_never_enter_fallback_provider() {
    let t = temp("authoritative-config");
    let xdg = t.join("xdg/azdaja");
    fs::create_dir_all(&xdg).unwrap();
    let calls = t.join("provider-calls");
    let provider = t.join("provider.py");
    fs::write(
        &provider,
        r#"import pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write("entered\n")
sys.stdin.read()
print("AZDAJA")
"#,
    )
    .unwrap();
    config(
        &xdg,
        &format!("python3 {} {}", provider.display(), calls.display()),
        512,
        1,
        3,
        4,
    );

    let missing = t.join("missing.toml");
    let directory = t.join("directory.toml");
    fs::create_dir(&directory).unwrap();
    let dangling = t.join("dangling.toml");
    std::os::unix::fs::symlink(t.join("absent-target"), &dangling).unwrap();
    let malformed = t.join("malformed.toml");
    fs::write(&malformed, "this is not = valid toml [").unwrap();

    for (index, invalid) in [missing, directory, dangling, malformed].iter().enumerate() {
        let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .arg("doctor")
            .env("HOME", &t)
            .env("XDG_CONFIG_HOME", t.join("xdg"))
            .env("AZDAJA_HOME", t.join(format!("state-{index}")))
            .env("AZDAJA_CONFIG", invalid)
            .env_remove("RLM_DEPTH")
            .output()
            .unwrap();
        assert_eq!(
            output.status.code(),
            Some(1),
            "invalid={}",
            invalid.display()
        );
        assert!(String::from_utf8_lossy(&output.stdout).starts_with("FAIL config:"));
        assert!(output.stderr.is_empty());
    }
    assert!(
        !calls.exists(),
        "an authoritative config failure must stop before fallback provider entry"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn adjacent_config_requires_standalone_name_or_managed_marker() {
    let t = temp("adjacent-config");
    let xdg = t.join("xdg/azdaja");
    fs::create_dir_all(&xdg).unwrap();
    let provider = t.join("provider.py");
    fs::write(
        &provider,
        r#"import pathlib, sys
pathlib.Path(sys.argv[1]).open("a").write("entered\n")
sys.stdin.read()
print("AZDAJA")
"#,
    )
    .unwrap();

    let run_copy = |name: &str, adjacent_name: &str, managed: bool| {
        let root = t.join(name);
        let bin = root.join("bin");
        fs::create_dir_all(&bin).unwrap();
        let executable = bin.join("azdaja");
        fs::copy(env!("CARGO_BIN_EXE_azdaja"), &executable).unwrap();
        let adjacent_calls = root.join("adjacent-calls");
        let xdg_calls = root.join("xdg-calls");
        config(
            &bin,
            &format!(
                "python3 {} {}",
                provider.display(),
                adjacent_calls.display()
            ),
            512,
            1,
            3,
            4,
        );
        if adjacent_name != "config.toml" {
            fs::rename(bin.join("config.toml"), bin.join(adjacent_name)).unwrap();
        }
        if managed {
            fs::write(
                bin.join(".azdaja-managed"),
                r#"{"files":[["azdaja",0],["SKILL.md",0],["config.toml",0]]}"#,
            )
            .unwrap();
        }
        let xdg_dir = root.join("xdg/azdaja");
        fs::create_dir_all(&xdg_dir).unwrap();
        config(
            &xdg_dir,
            &format!("python3 {} {}", provider.display(), xdg_calls.display()),
            512,
            1,
            3,
            4,
        );
        let output = Command::new(&executable)
            .arg("doctor")
            .env("HOME", &root)
            .env("XDG_CONFIG_HOME", root.join("xdg"))
            .env("AZDAJA_HOME", root.join("state"))
            .env_remove("AZDAJA_CONFIG")
            .env_remove("RLM_DEPTH")
            .output()
            .unwrap();
        assert!(
            output.status.success(),
            "stdout={} stderr={}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        (adjacent_calls.exists(), xdg_calls.exists())
    };

    assert_eq!(run_copy("generic", "config.toml", false), (false, true));
    assert_eq!(
        run_copy("standalone", "azdaja-config.toml", false),
        (true, false)
    );
    assert_eq!(run_copy("managed", "config.toml", true), (true, false));
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn global_lock_symlink_and_hardlink_victims_are_unchanged() {
    use std::os::unix::fs::{MetadataExt, PermissionsExt};

    for kind in ["symlink", "hardlink"] {
        let t = temp(&format!("global-lock-{kind}"));
        let state = t.join("state");
        fs::create_dir(&state).unwrap();
        fs::set_permissions(&state, fs::Permissions::from_mode(0o700)).unwrap();
        let victim = t.join("DO_NOT_CHANGE");
        fs::write(&victim, b"victim-content").unwrap();
        fs::set_permissions(&victim, fs::Permissions::from_mode(0o644)).unwrap();
        let before = fs::metadata(&victim).unwrap();
        if kind == "symlink" {
            std::os::unix::fs::symlink(&victim, state.join("global.lock")).unwrap();
        } else {
            fs::hard_link(&victim, state.join("global.lock")).unwrap();
        }
        let cfg = config(&t, "cat", 512, 1, 3, 4);
        let output = run(&t, &cfg, &["start"], "");
        assert!(!output.status.success(), "kind={kind}");
        let after = fs::metadata(&victim).unwrap();
        assert_eq!(fs::read(&victim).unwrap(), b"victim-content");
        assert_eq!(after.permissions().mode() & 0o777, 0o644);
        assert_eq!(after.ino(), before.ino());
        fs::remove_dir_all(t).unwrap();
    }
}

#[test]
#[cfg(unix)]
fn global_lock_path_replacement_is_detected_after_waiting() {
    use fs2::FileExt;
    use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};

    let t = temp("global-lock-replacement");
    let state = t.join("state");
    fs::create_dir(&state).unwrap();
    fs::set_permissions(&state, fs::Permissions::from_mode(0o700)).unwrap();
    let lock_path = state.join("global.lock");
    let original = fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create_new(true)
        .mode(0o600)
        .open(&lock_path)
        .unwrap();
    FileExt::lock_exclusive(&original).unwrap();
    let cfg = config(&t, "cat", 512, 1, 3, 4);
    let mut child = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .arg("start")
        .env("HOME", &t)
        .env("AZDAJA_HOME", &state)
        .env("AZDAJA_CONFIG", &cfg)
        .env_remove("RLM_DEPTH")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    std::thread::sleep(Duration::from_millis(150));
    assert!(
        child.try_wait().unwrap().is_none(),
        "child did not wait on the opened lock inode"
    );

    let moved = state.join("original.lock");
    fs::rename(&lock_path, &moved).unwrap();
    fs::write(&lock_path, b"DO_NOT_CHANGE").unwrap();
    fs::set_permissions(&lock_path, fs::Permissions::from_mode(0o600)).unwrap();
    FileExt::unlock(&original).unwrap();
    let output = child.wait_with_output().unwrap();
    assert!(!output.status.success());
    assert!(String::from_utf8_lossy(&output.stderr).contains("path binding changed"));
    assert_eq!(fs::read(&lock_path).unwrap(), b"DO_NOT_CHANGE");
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn symlinked_state_locks_and_prompts_directories_fail_closed() {
    use std::os::unix::fs::PermissionsExt;

    for kind in ["state", "locks", "prompts"] {
        let t = temp(&format!("symlinked-{kind}"));
        let victim = t.join("DO_NOT_CHANGE");
        fs::create_dir(&victim).unwrap();
        fs::set_permissions(&victim, fs::Permissions::from_mode(0o755)).unwrap();
        fs::write(victim.join("sentinel"), b"unchanged").unwrap();
        let state = t.join("state");
        if kind == "state" {
            std::os::unix::fs::symlink(&victim, &state).unwrap();
        } else {
            fs::create_dir(&state).unwrap();
            fs::set_permissions(&state, fs::Permissions::from_mode(0o700)).unwrap();
            std::os::unix::fs::symlink(&victim, state.join(kind)).unwrap();
        }
        let calls = t.join("provider-calls");
        let provider = t.join("provider.py");
        fs::write(
            &provider,
            format!(
                "import pathlib,sys\npathlib.Path({:?}).write_text('entered')\nprint('AZDAJA')\n",
                calls.to_str().unwrap()
            ),
        )
        .unwrap();
        let command = if kind == "prompts" {
            format!("python3 {} {{prompt_file}}", provider.display())
        } else {
            "cat".to_owned()
        };
        let cfg = config(&t, &command, 512, 1, 3, 4);
        let output = run(&t, &cfg, &["doctor"], "");
        assert!(!output.status.success(), "kind={kind}");
        let after = fs::metadata(&victim).unwrap();
        assert_eq!(after.permissions().mode() & 0o777, 0o755);
        assert_eq!(fs::read(victim.join("sentinel")).unwrap(), b"unchanged");
        assert!(!calls.exists(), "kind={kind} entered provider");
        fs::remove_dir_all(t).unwrap();
    }
}

#[test]
fn install_is_provider_free_idempotent_and_owned() {
    let t = temp("install");
    let bin = t.join("bin");
    fs::create_dir(&bin).unwrap();
    let mock = bin.join("claude");
    let provider_called = t.join("provider-called");
    fs::write(
        &mock,
        format!(
            "#!/bin/sh
printf called > {:?}
exit 9
",
            provider_called.to_str().unwrap()
        ),
    )
    .unwrap();
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&mock, fs::Permissions::from_mode(0o755)).unwrap();
    }
    let cfg = config(&t, "cat", 512, 1, 3, 4);
    let dst = t.join(".claude/skills/azdaja");
    let installed = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["install", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env(
            "PATH",
            format!("{}:{}", bin.display(), std::env::var("PATH").unwrap()),
        )
        .output()
        .unwrap();
    assert!(
        installed.status.success(),
        "{}",
        String::from_utf8_lossy(&installed.stderr)
    );
    assert!(
        !provider_called.exists(),
        "install must not execute a live provider adapter"
    );
    assert!(dst.join("azdaja").is_file());
    let skill = fs::read_to_string(dst.join("SKILL.md")).unwrap();
    assert!(skill.contains("Azdaja 0.1.8") && skill.contains(dst.join("azdaja").to_str().unwrap()));
    assert!(skill.contains("one explicit `start`/`load`/`exec`/`final`/`kill` lifecycle"));
    assert!(skill.contains("llm_batch(prompts, workers=4)"));
    assert!(skill.contains("Scan the complete loaded source"));
    assert!(skill.contains("Preserve source order, duplicates, and stable occurrence IDs"));
    assert!(skill.contains("create blind A/B prompts"));
    assert!(
        skill.contains("never use keyword, regex, substring, label-name, or hand-written rules")
    );
    assert!(skill.contains("Validate JSON, exact ID coverage, and label domain"));
    assert!(skill.contains("Use native `sha256(text)`"));
    assert!(skill.contains("End with `FINAL(answer_dict)` exactly once"));
    assert!(!skill.contains("workers=16"));
    assert!(skill.len() < 8_000);
    let edited_config = fs::read_to_string(&cfg).unwrap().replace(
        "sub_llm_cmd = \"cat\"",
        &format!("sub_llm_cmd = {:?}", mock.to_str().unwrap()),
    );
    fs::write(dst.join("config.toml"), &edited_config).unwrap();

    // A user-editable config must not make the managed installation impossible to remove.
    let removed = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["uninstall", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .output()
        .unwrap();
    assert!(
        removed.status.success(),
        "{}",
        String::from_utf8_lossy(&removed.stderr)
    );
    assert!(!dst.exists());

    let reinstalled = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["install", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env(
            "PATH",
            format!("{}:{}", bin.display(), std::env::var("PATH").unwrap()),
        )
        .output()
        .unwrap();
    assert!(
        reinstalled.status.success(),
        "{}",
        String::from_utf8_lossy(&reinstalled.stderr)
    );
    fs::write(dst.join("config.toml"), &edited_config).unwrap();

    // Upgrade remains idempotent and re-hashes the preserved customized config.
    let o = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["install", "claude"])
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
        .args(["uninstall", "claude"])
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
        .args(["uninstall", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .output()
        .unwrap();
    assert!(!refused.status.success() && dst.exists());
    fs::write(dst.join("SKILL.md"), original_skill).unwrap();
    let o = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["uninstall", "claude"])
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
#[cfg(unix)]
fn managed_install_never_removes_stopped_pid_or_symlink_collisions() {
    let t = temp("install-collisions");
    let wrapper = t.join("install-wrapper.sh");
    fs::write(
        &wrapper,
        r#"#!/bin/sh
set -eu
parent="$HOME/.claude/skills"
mkdir -p "$parent" "$HOME/collision-victim"
if [ "$MODE" = first ]; then
  stage="$parent/.azdaja-stage-$$"
  backup="$parent/.azdaja-backup-$$"
  mkdir "$stage"
  printf DO_NOT_DELETE > "$stage/DO_NOT_DELETE"
  ln -s "$HOME/collision-victim" "$backup"
else
  stage="$parent/.azdaja-stage-$$"
  backup="$parent/.azdaja-backup-$$"
  ln -s "$HOME/collision-victim" "$stage"
  mkdir "$backup"
  printf DO_NOT_DELETE > "$backup/DO_NOT_DELETE"
fi
printf '%s\n%s\n' "$stage" "$backup" > "$HOME/collision-paths-$MODE"
exec "$AZDAJA_TEST_BIN" install claude
"#,
    )
    .unwrap();
    use std::os::unix::fs::PermissionsExt;
    fs::set_permissions(&wrapper, fs::Permissions::from_mode(0o755)).unwrap();

    for mode in ["first", "upgrade"] {
        let output = Command::new(&wrapper)
            .env("MODE", mode)
            .env("HOME", &t)
            .env("AZDAJA_TEST_BIN", env!("CARGO_BIN_EXE_azdaja"))
            .env("AZDAJA_HOME", t.join("state"))
            .env_remove("AZDAJA_CONFIG")
            .env_remove("RLM_DEPTH")
            .output()
            .unwrap();
        assert!(
            output.status.success(),
            "mode={mode} stdout={} stderr={}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        let paths = fs::read_to_string(t.join(format!("collision-paths-{mode}"))).unwrap();
        let paths: Vec<_> = paths.lines().map(PathBuf::from).collect();
        assert_eq!(paths.len(), 2);
        if mode == "first" {
            assert_eq!(
                fs::read(paths[0].join("DO_NOT_DELETE")).unwrap(),
                b"DO_NOT_DELETE"
            );
            assert_eq!(
                fs::read_link(&paths[1]).unwrap(),
                t.join("collision-victim")
            );
        } else {
            assert_eq!(
                fs::read_link(&paths[0]).unwrap(),
                t.join("collision-victim")
            );
            assert_eq!(
                fs::read(paths[1].join("DO_NOT_DELETE")).unwrap(),
                b"DO_NOT_DELETE"
            );
        }
    }

    let dst = t.join(".claude/skills/azdaja");
    assert!(dst.join(".azdaja-managed").is_file());
    let uninstall = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args(["uninstall", "claude"])
        .env("HOME", &t)
        .env("AZDAJA_HOME", t.join("state"))
        .env_remove("AZDAJA_CONFIG")
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap();
    assert!(
        uninstall.status.success(),
        "{}",
        String::from_utf8_lossy(&uninstall.stderr)
    );
    assert!(!dst.exists());
    for mode in ["first", "upgrade"] {
        for path in fs::read_to_string(t.join(format!("collision-paths-{mode}")))
            .unwrap()
            .lines()
        {
            assert!(
                fs::symlink_metadata(path).is_ok(),
                "collision was deleted: {path}"
            );
        }
    }
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn managed_skill_is_rendered_consistently_for_every_harness() {
    let t = temp("skill-all-harnesses");
    let xdg = t.join("xdg");
    let installed = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["install", "all"])
        .env("HOME", &t)
        .env("XDG_CONFIG_HOME", &xdg)
        .env("AZDAJA_HOME", t.join("state"))
        .output()
        .unwrap();
    assert!(
        installed.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&installed.stderr),
        String::from_utf8_lossy(&installed.stdout)
    );
    let doctor = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["doctor", "all"])
        .env("HOME", &t)
        .env("XDG_CONFIG_HOME", &xdg)
        .env("AZDAJA_HOME", t.join("state"))
        .output()
        .unwrap();
    assert!(
        doctor.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&doctor.stderr),
        String::from_utf8_lossy(&doctor.stdout)
    );

    let targets = [
        (
            "jcode",
            "Jcode",
            "reload all skills",
            t.join(".jcode/skills/azdaja"),
        ),
        (
            "claude",
            "Claude Code",
            "<execution_state>",
            t.join(".claude/skills/azdaja"),
        ),
        ("codex", "Codex", "$azdaja", t.join(".agents/skills/azdaja")),
        (
            "gemini",
            "Gemini",
            "In Gemini",
            t.join(".gemini/skills/azdaja"),
        ),
        (
            "opencode",
            "OpenCode",
            "session-sticky",
            xdg.join("opencode/skills/azdaja"),
        ),
    ];
    let binary_name = if cfg!(windows) {
        "azdaja.exe"
    } else {
        "azdaja"
    };
    for (harness, display, marker, target) in targets {
        let binary = target.join(binary_name);
        let skill = fs::read_to_string(target.join("SKILL.md")).unwrap();
        let binary_text = binary.to_str().unwrap();
        assert!(binary.is_file(), "{harness} managed binary is missing");
        assert!(skill.contains(&format!("# Azdaja {}", env!("CARGO_PKG_VERSION"))));
        assert!(
            skill.contains(binary_text),
            "{harness} path was not embedded"
        );
        assert!(!skill.contains("{{VERSION}}"));
        assert!(!skill.contains("{{BIN}}"));
        assert!(
            skill.contains(&format!("## Harness activation: {display}")),
            "{harness} did not receive its harness activation section"
        );
        assert!(
            skill.contains(marker),
            "{harness} did not receive its harness-specific activation guidance"
        );

        let frontmatter = skill
            .strip_prefix("---\n")
            .and_then(|rest| {
                rest.split_once("\n---\n")
                    .map(|(frontmatter, _)| frontmatter)
            })
            .expect("installed skill YAML frontmatter");
        let description = frontmatter
            .lines()
            .find_map(|line| line.strip_prefix("description: "))
            .expect("installed skill description");
        let size_trigger = match harness {
            "claude" => "exhaustive semantic judgment or classification over one input",
            "codex" | "opencode" => "exhaustive semantic judgment or classification over one input",
            _ => "inputs too large",
        };
        let mut triggers = vec![
            size_trigger,
            "Azdaja",
            "az virtual-memory tool",
            "installed",
            "available",
        ];
        if !matches!(harness, "claude" | "codex" | "opencode") {
            triggers.push("how to use");
        }
        for trigger in triggers {
            assert!(
                description.contains(trigger),
                "{harness} description is missing trigger {trigger:?}"
            );
        }
        if matches!(harness, "codex" | "opencode") {
            for nontrigger in [
                "repository audits",
                "code navigation",
                "structural searches",
                "bounded excerpts",
                "a mere mention of Azdaja",
            ] {
                assert!(
                    description.contains(nontrigger),
                    "{harness} description is missing OpenCode-safe nontrigger {nontrigger:?}"
                );
            }
            assert!(!description.starts_with("Mandatory:"));
            assert!(!skill.contains("before Read, Grep, or Bash inspection"));
            assert!(skill.contains("Passive discovery"));
            assert!(skill.contains("an explicit Azdaja request is"));
            assert!(skill.contains("### Standard cell contract"));
            assert!(skill.contains("at most 256 unique items and 64 KiB each"));
            assert!(skill.contains(r#"{"labels":"TFT..."}"#));
            assert!(skill.contains("evaluations get no retry"));
            assert!(!skill.lines().any(|line| line.starts_with("        ")));
            if harness == "codex" {
                assert!(skill.contains("Codex coworker lane (default)"));
                assert!(skill.contains("Codex skill activation is per-turn"));
                assert!(skill.contains(
                    "OpenCode may also discover this Agent Skills compatibility profile"
                ));
                assert!(skill.contains("Strict benchmark/audit lane (explicit only)"));
                let metadata = fs::read_to_string(target.join("agents/openai.yaml")).unwrap();
                assert!(metadata.contains("interface:"));
                assert!(metadata.contains("display_name: \"Azdaja\""));
                assert!(metadata.contains("short_description:"));
                assert!(metadata.contains("repository audits"));
                assert!(metadata.contains("default_prompt: \"$azdaja Use"));
                assert!(metadata.contains("policy:"));
                assert!(metadata.contains("allow_implicit_invocation: true"));
            } else {
                assert!(skill.contains("### Strict benchmark lane (explicit only)"));
            }
        }
        for awareness in [
            "## Managed-skill awareness",
            "answer **yes**",
            "local `az` virtual-memory tool",
            "Never claim ignorance of Azdaja",
        ] {
            assert!(
                skill.contains(awareness),
                "{harness} skill is missing awareness text {awareness:?}"
            );
        }
        let internal_commands = skill
            .split_once("```bash\n")
            .and_then(|(_, rest)| rest.split_once("\n```").map(|(block, _)| block))
            .expect("installed skill internal commands");
        assert!(
            !internal_commands
                .lines()
                .any(|line| line.trim_start().starts_with("az ")),
            "{harness} internal commands must not use a bare az executable"
        );
        for command in ["start", "load", "exec", "final", "kill"] {
            assert!(
                internal_commands.lines().any(|line| {
                    line.contains(binary_text)
                        && line
                            .split(|character: char| {
                                !character.is_ascii_alphanumeric() && character != '-'
                            })
                            .any(|word| word == command)
                }),
                "{harness} internal {command} command does not use its managed binary"
            );
        }
    }
    let activation = t.join(".claude/skills/azdaja/ACTIVATION.md");
    let activation_text = fs::read_to_string(&activation).unwrap();
    assert!(activation_text.len() <= 500);
    assert!(activation_text.contains("exhaustive semantic judgment or classification"));
    assert!(activation_text.contains("repository audits"));
    assert!(activation_text.contains("deterministic count, tail, and checksum work"));
    let plugin =
        fs::read_to_string(t.join(".claude/skills/azdaja/.claude-plugin/plugin.json")).unwrap();
    let hooks = fs::read_to_string(t.join(".claude/skills/azdaja/hooks/hooks.json")).unwrap();
    assert!(plugin.contains("\"name\": \"azdaja\""));
    assert!(hooks.contains("UserPromptSubmit"));
    assert!(hooks.contains("PreToolUse"));
    assert!(hooks.contains("PostToolUse"));
    assert!(hooks.contains("PostToolUseFailure"));
    assert!(hooks.contains("\"matcher\": \"Skill|Bash\""));
    assert!(hooks.contains("SessionEnd"));
    #[cfg(unix)]
    assert_eq!(
        fs::read_link(t.join(".claude/rules/azdaja.md")).unwrap(),
        activation
    );
    fs::remove_dir_all(t).unwrap();
}

fn install_codex_for_doctor_fixture(t: &Path, codex_home: &Path) {
    let installed = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["install", "codex"])
        .env("HOME", t)
        .env("CODEX_HOME", codex_home)
        .env("AZDAJA_HOME", t.join("state"))
        .output()
        .unwrap();
    assert!(
        installed.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&installed.stderr),
        String::from_utf8_lossy(&installed.stdout)
    );
}

fn doctor_codex_fixture(t: &Path, codex_home: &Path, cwd: &Path) -> Output {
    Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .current_dir(cwd)
        .env_remove("RLM_DEPTH")
        .args(["doctor", "codex"])
        .env("HOME", t)
        .env("CODEX_HOME", codex_home)
        .env("AZDAJA_HOME", t.join("state"))
        .output()
        .unwrap()
}

#[test]
fn codex_doctor_rejects_relative_codex_home_without_provider_calls() {
    let t = temp("codex-relative-home");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["doctor", "codex"])
        .env("HOME", &t)
        .env("CODEX_HOME", "relative-codex-home")
        .env("AZDAJA_HOME", t.join("state"))
        .output()
        .unwrap();
    assert!(!output.status.success());
    let stderr = String::from_utf8_lossy(&output.stderr);
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stderr.contains("CODEX_HOME must be set to a non-empty absolute path")
            || stdout.contains("CODEX_HOME must be set to a non-empty absolute path"),
        "stderr={stderr} stdout={stdout}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_rejects_disabled_managed_skill() {
    let t = temp("codex-disabled-managed");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    fs::write(
        codex_home.join("config.toml"),
        "[[skills.config]]\nname = \"azdaja\"\nenabled = false\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("managed Codex Azdaja skill is disabled"),
        "{stdout}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_honors_name_disable_and_later_path_reenable_for_managed_skill() {
    let t = temp("codex-managed-reenable");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let managed_skill_md = t.join(".agents/skills/azdaja/SKILL.md");
    fs::write(
        codex_home.join("config.toml"),
        format!(
            "[[skills.config]]\nname = \"azdaja\"\nenabled = false\n\n[[skills.config]]\npath = {:?}\nenabled = true\n",
            managed_skill_md.to_str().unwrap()
        ),
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(
        output.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_rejects_include_instructions_false() {
    let t = temp("codex-include-instructions");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    fs::write(
        codex_home.join("config.toml"),
        "[skills]\ninclude_instructions = false\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("include_instructions=false"), "{stdout}");
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_accepts_valid_bundled_skills_config() {
    let t = temp("codex-valid-bundled-config");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    fs::write(
        codex_home.join("config.toml"),
        "[skills]\ninclude_instructions = true\nmax_context_tokens = 1\n[skills.bundled]\nenabled = false\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(
        output.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    fs::remove_dir_all(t).unwrap();
}

#[cfg(unix)]
#[test]
fn codex_doctor_refuses_symlinked_user_config() {
    let t = temp("codex-config-symlink");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let real_config = t.join("real-config.toml");
    fs::write(&real_config, "project_root_markers = []\n").unwrap();
    std::os::unix::fs::symlink(&real_config, codex_home.join("config.toml")).unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("managed path is not a regular file")
            || stdout.contains("Too many levels of symbolic links"),
        "{stdout}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_rejects_zero_max_context_tokens() {
    let t = temp("codex-zero-max-context");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    fs::write(
        codex_home.join("config.toml"),
        "[skills]\nmax_context_tokens = 0\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("greater than zero"), "{stdout}");
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_rejects_visible_codex_home_duplicate_unless_exact_skill_disabled() {
    let t = temp("codex-home-duplicate");
    let codex_home = t.join("codex-home");
    let duplicate = codex_home.join("skills/azdaja");
    fs::create_dir_all(&duplicate).unwrap();
    fs::write(
        duplicate.join("SKILL.md"),
        "---\nname: azdaja\ndescription: foreign duplicate\n---\nforeign\n",
    )
    .unwrap();
    #[cfg(unix)]
    std::os::unix::fs::symlink(&duplicate, codex_home.join("skills/link-to-azdaja")).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);

    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("Codex can discover an enabled same-name Azdaja skill"),
        "{stdout}"
    );

    fs::write(
        codex_home.join("config.toml"),
        format!(
            "[[skills.config]]\npath = {:?}\nenabled = false\n",
            duplicate.join("SKILL.md").to_str().unwrap()
        ),
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(
        output.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_duplicate_exception_uses_final_path_or_name_selector_state() {
    let t = temp("codex-duplicate-selector-order");
    let codex_home = t.join("codex-home");
    let duplicate = codex_home.join("skills/azdaja");
    fs::create_dir_all(&duplicate).unwrap();
    fs::write(
        duplicate.join("SKILL.md"),
        "---\nname: azdaja\ndescription: foreign duplicate\n---\nforeign\n",
    )
    .unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let duplicate_skill = duplicate.join("SKILL.md");

    fs::write(
        codex_home.join("config.toml"),
        format!(
            "[[skills.config]]\npath = {:?}\nenabled = false\n\n[[skills.config]]\nname = \"azdaja\"\nenabled = true\n",
            duplicate_skill.to_str().unwrap()
        ),
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("Codex can discover an enabled same-name Azdaja skill"),
        "{stdout}"
    );

    fs::write(
        codex_home.join("config.toml"),
        format!(
            "[[skills.config]]\nname = \"azdaja\"\nenabled = true\n\n[[skills.config]]\npath = {:?}\nenabled = false\n",
            duplicate_skill.to_str().unwrap()
        ),
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(
        output.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_rejects_malformed_skills_config_shapes() {
    for (case, config, expected) in [
        (
            "unknown-skills-key",
            "[skills]\nunknown = true\n",
            "unknown key",
        ),
        (
            "config-not-array",
            "[skills]\nconfig = true\n",
            "skills.config must be an array",
        ),
        (
            "entry-not-table",
            "[skills]\nconfig = [1]\n",
            "entries must be tables",
        ),
        (
            "missing-enabled",
            "[[skills.config]]\nname = \"azdaja\"\n",
            "enabled is required",
        ),
        (
            "unknown-entry-key",
            "[[skills.config]]\nname = \"azdaja\"\nenabled = true\nextra = true\n",
            "unknown key",
        ),
        (
            "bundled-wrong-type",
            "[skills]\nbundled = true\n",
            "bundled must be a table",
        ),
        (
            "bundled-unknown-key",
            "[skills.bundled]\nenabled = false\nextra = true\n",
            "bundled has unknown key",
        ),
        (
            "bundled-enabled-wrong-type",
            "[skills.bundled]\nenabled = 1\n",
            "bundled.enabled must be a boolean",
        ),
    ] {
        let t = temp(&format!("codex-malformed-{case}"));
        let codex_home = t.join("codex-home");
        fs::create_dir_all(&codex_home).unwrap();
        install_codex_for_doctor_fixture(&t, &codex_home);
        fs::write(codex_home.join("config.toml"), config).unwrap();
        let output = doctor_codex_fixture(&t, &codex_home, &t);
        assert!(!output.status.success(), "case={case}");
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(stdout.contains(expected), "case={case} stdout={stdout}");
        fs::remove_dir_all(t).unwrap();
    }
}

#[test]
fn codex_doctor_scans_project_codex_and_agents_duplicates_even_when_untrusted() {
    let t = temp("codex-project-duplicates");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let project = t.join("project");
    let nested = project.join("a/b");
    fs::create_dir_all(&nested).unwrap();
    fs::create_dir(project.join(".git")).unwrap();

    let codex_duplicate = project.join(".codex/skills/azdaja");
    fs::create_dir_all(&codex_duplicate).unwrap();
    fs::write(
        codex_duplicate.join("SKILL.md"),
        "---\nname: azdaja\ndescription: foreign duplicate\n---\nforeign\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &nested);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("Codex can discover an enabled same-name Azdaja skill"),
        "{stdout}"
    );

    fs::write(
        codex_home.join("config.toml"),
        format!(
            "[projects.{:?}]\ntrust_level = \"untrusted\"\n",
            project.to_str().unwrap()
        ),
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &nested);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("Codex can discover an enabled same-name Azdaja skill"),
        "{stdout}"
    );
    fs::remove_dir_all(&codex_duplicate).unwrap();

    for duplicate in [
        project.join(".agents/skills/azdaja"),
        project.join(".codex/skills/group/not-azdaja"),
    ] {
        fs::create_dir_all(&duplicate).unwrap();
        fs::write(
            duplicate.join("SKILL.md"),
            "---\nname: azdaja\ndescription: foreign duplicate\n---\nforeign\n",
        )
        .unwrap();
        let output = doctor_codex_fixture(&t, &codex_home, &nested);
        assert!(!output.status.success());
        let stdout = String::from_utf8_lossy(&output.stdout);
        assert!(
            stdout.contains("Codex can discover an enabled same-name Azdaja skill"),
            "{stdout}"
        );
        fs::remove_dir_all(&duplicate).unwrap();
    }

    let default_name_duplicate = project.join(".agents/skills/group/azdaja");
    fs::create_dir_all(&default_name_duplicate).unwrap();
    fs::write(
        default_name_duplicate.join("SKILL.md"),
        "---\ndescription: fallback name\n---\nforeign\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &nested);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("Codex can discover an enabled same-name Azdaja skill"),
        "{stdout}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_honors_custom_project_root_markers() {
    let t = temp("codex-custom-root-marker");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let project = t.join("project");
    let nested = project.join("src/deep");
    fs::create_dir_all(&nested).unwrap();
    fs::write(project.join(".codex-root"), "").unwrap();
    fs::write(
        codex_home.join("config.toml"),
        "project_root_markers = [\".codex-root\"]\n",
    )
    .unwrap();
    let duplicate = project.join(".codex/skills/not-named-azdaja");
    fs::create_dir_all(&duplicate).unwrap();
    fs::write(
        duplicate.join("SKILL.md"),
        " ---  \nname: azdaja\ndescription: Build for AWS: ECS\n --- \nforeign\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &nested);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("Codex can discover an enabled same-name Azdaja skill"),
        "{stdout}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_matches_codex_scalar_repair_for_unrelated_frontmatter_keys() {
    let t = temp("codex-frontmatter-scalar-repair");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let project = t.join("project");
    fs::create_dir_all(project.join(".git")).unwrap();
    let duplicate = project.join(".codex/skills/foreign");
    fs::create_dir_all(&duplicate).unwrap();
    fs::write(
        duplicate.join("SKILL.md"),
        "---\nname: azdaja\ndescription: foreign duplicate\nargument-hint: <duration: e.g. 7d>\n---\nforeign\n",
    )
    .unwrap();

    let output = doctor_codex_fixture(&t, &codex_home, &project);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("Codex can discover an enabled same-name Azdaja skill"),
        "{stdout}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_honors_empty_project_root_markers_as_cwd_only() {
    let t = temp("codex-empty-root-markers");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    fs::write(
        codex_home.join("config.toml"),
        "project_root_markers = []\n",
    )
    .unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let project = t.join("project");
    let nested = project.join("src/deep");
    fs::create_dir_all(&nested).unwrap();
    fs::create_dir(project.join(".git")).unwrap();
    let ignored_duplicate = project.join(".codex/skills/azdaja");
    fs::create_dir_all(&ignored_duplicate).unwrap();
    fs::write(
        ignored_duplicate.join("SKILL.md"),
        "---\nname: azdaja\ndescription: foreign duplicate\n---\nforeign\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &nested);
    assert!(
        output.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );

    let cwd_duplicate = nested.join(".agents/skills/azdaja");
    fs::create_dir_all(&cwd_duplicate).unwrap();
    fs::write(
        cwd_duplicate.join("SKILL.md"),
        "---\nname: azdaja\ndescription: cwd duplicate\n---\nforeign\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &nested);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("Codex can discover an enabled same-name Azdaja skill"),
        "{stdout}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_rejects_invalid_project_root_markers() {
    let t = temp("codex-invalid-root-marker");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    fs::write(
        codex_home.join("config.toml"),
        "project_root_markers = [1]\n",
    )
    .unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("project_root_markers must be an array of strings"),
        "{stdout}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_doctor_matches_codex_validation_for_missing_description_and_repairable_yaml() {
    let t = temp("codex-invalid-same-name");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let invalid = codex_home.join("skills/azdaja");
    fs::create_dir_all(&invalid).unwrap();
    fs::write(
        invalid.join("SKILL.md"),
        "---\nname: azdaja\n---\nnot loaded\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(
        output.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );

    fs::write(
        invalid.join("SKILL.md"),
        "---\nname: [not valid yaml\ndescription: bad\n---\nnot loaded\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(
        output.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&output.stderr),
        String::from_utf8_lossy(&output.stdout)
    );

    fs::write(
        invalid.join("SKILL.md"),
        "---\nname: azdaja\ndescription: foreign duplicate\ninvalid: [\n---\nnot loaded\n",
    )
    .unwrap();
    let output = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(!output.status.success());
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("Codex can discover an enabled same-name Azdaja skill"),
        "{stdout}"
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_metadata_is_manifested_and_removed_by_uninstall() {
    let t = temp("codex-metadata-custody");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let target = t.join(".agents/skills/azdaja");
    assert!(target.join("agents/openai.yaml").is_file());
    let manifest = fs::read_to_string(target.join(".azdaja-managed")).unwrap();
    assert!(manifest.contains("agents/openai.yaml"), "{manifest}");

    let removed = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["uninstall", "codex"])
        .env("HOME", &t)
        .env("CODEX_HOME", &codex_home)
        .env("AZDAJA_HOME", t.join("state"))
        .output()
        .unwrap();
    assert!(
        removed.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&removed.stderr),
        String::from_utf8_lossy(&removed.stdout)
    );
    assert!(!target.exists());
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn codex_reinstall_migrates_byte_exact_legacy_adapter_to_isolated_workers() {
    let t = temp("codex-adapter-migration");
    let codex_home = t.join("codex-home");
    fs::create_dir_all(&codex_home).unwrap();
    install_codex_for_doctor_fixture(&t, &codex_home);
    let target = t.join(".agents/skills/azdaja");
    let config_path = target.join("config.toml");
    let current = fs::read_to_string(&config_path).unwrap();
    let current_command = "codex exec --ephemeral --skip-git-repo-check --ignore-user-config --ignore-rules --sandbox read-only {isolated_env} -c model_reasoning_effort=low -c skills.include_instructions=false -c features.shell_tool=false -c features.view_image=false -c features.multi_agent=false -c features.multi_agent_v2=false -c agents.enabled=false -c web_search=disabled --json --model {model} -C {sandbox_dir} -";
    assert!(current.contains(current_command), "{current}");
    let legacy_configs: [&[u8]; 4] = [
        include_bytes!("../assets/legacy/codex-config-a9da6615.toml"),
        include_bytes!("../assets/legacy/codex-config-41f19430.toml"),
        include_bytes!("../assets/legacy/codex-config-ae85a189.toml"),
        include_bytes!("../assets/legacy/codex-config-e6467dc6.toml"),
    ];
    for legacy in legacy_configs {
        assert_ne!(legacy, current.as_bytes());
        fs::write(&config_path, legacy).unwrap();

        let reinstalled = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .env_remove("RLM_DEPTH")
            .args(["install", "codex"])
            .env("HOME", &t)
            .env("CODEX_HOME", &codex_home)
            .env("AZDAJA_HOME", t.join("state"))
            .output()
            .unwrap();
        assert!(
            reinstalled.status.success(),
            "stderr={} stdout={}",
            String::from_utf8_lossy(&reinstalled.stderr),
            String::from_utf8_lossy(&reinstalled.stdout)
        );
        let migrated = fs::read_to_string(&config_path).unwrap();
        assert!(migrated.contains(current_command), "{migrated}");
        assert!(
            migrated.contains("default_model = \"gpt-5.6-sol\""),
            "{migrated}"
        );
    }

    let doctor = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(
        doctor.status.success(),
        "stderr={} stdout={}",
        String::from_utf8_lossy(&doctor.stderr),
        String::from_utf8_lossy(&doctor.stdout)
    );

    let mut customized_legacy = legacy_configs[1].to_vec();
    customized_legacy.extend_from_slice(b"# user customization\n");
    fs::write(&config_path, &customized_legacy).unwrap();
    let reinstalled = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .env_remove("RLM_DEPTH")
        .args(["install", "codex"])
        .env("HOME", &t)
        .env("CODEX_HOME", &codex_home)
        .env("AZDAJA_HOME", t.join("state"))
        .output()
        .unwrap();
    assert!(reinstalled.status.success());
    assert_eq!(fs::read(&config_path).unwrap(), customized_legacy);
    let doctor = doctor_codex_fixture(&t, &codex_home, &t);
    assert!(!doctor.status.success());
    assert!(String::from_utf8_lossy(&doctor.stdout).contains(
        "managed Codex sub_llm_cmd does not exactly match the isolated adapter contract"
    ));
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

#[test]
fn command_transport_trace_keeps_requested_model_and_unknown_provider_usage() {
    let t = temp("unknown-trace");
    let cfg = config(&t, "cat", 2048, 1, 3, 4);
    let id = sid(&t, &cfg);
    let trace = t.join("model.jsonl");
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args(["exec", &id])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(b"print(llm('synthetic'))\n")
        .unwrap();
    ok(child.wait_with_output().unwrap());
    let rows: Vec<serde_json::Value> = fs::read_to_string(trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 1, "{rows:?}");
    let row = &rows[0];
    assert_eq!(row["outcome"], "succeeded");
    assert_eq!(row["entered_turn"], 1);
    assert!(row.get("provider").is_none());
    assert_eq!(row["model"], "mock");
    assert!(row.get("input_tokens").is_none());
    assert!(row.get("output_tokens").is_none());
    assert!(row.get("cache_read_tokens").is_none());
    fs::remove_dir_all(t).unwrap();
}

#[cfg(unix)]
#[test]
fn jcode_api_fresh_batch_uses_one_session_per_item_and_streams_usage() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::{fs::MetadataExt, net::UnixListener};
    use std::thread;
    let t = temp("jcode-api");
    let task_cwd = std::env::current_dir().unwrap();
    let socket = t.join("api.sock");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let mut turns_per_session = Vec::new();
        let mut workspaces = Vec::new();
        for session_number in 1..=2 {
            // JcodeSession::open first probes bridge liveness, then opens the protocol stream.
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let sid = format!("s{session_number}");
            let mut turn_count = 0;
            let mut runtime_count = 0;
            let mut active_model = if session_number == 1 {
                "gpt-5.3"
            } else {
                "gpt-5.4"
            };
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).unwrap() == 0 {
                    break;
                }
                let f: serde_json::Value = serde_json::from_str(&line).unwrap();
                let id = f["id"].as_u64().unwrap();
                let req = f["req"].as_str().unwrap();
                if req == "create_session" {
                    let workspace = PathBuf::from(f["working_dir"].as_str().unwrap());
                    assert!(workspace.is_absolute());
                    let canonical_workspace = fs::canonicalize(&workspace).unwrap();
                    let canonical_task_cwd = fs::canonicalize(&task_cwd).unwrap();
                    assert!(!canonical_workspace.starts_with(canonical_task_cwd));
                    let meta = fs::symlink_metadata(&workspace).unwrap();
                    assert!(meta.file_type().is_dir());
                    assert!(!meta.file_type().is_symlink());
                    assert_eq!(meta.uid(), unsafe { libc::geteuid() });
                    assert_eq!(meta.mode() & 0o777, 0o700);
                    assert!(fs::read_dir(&workspace).unwrap().next().is_none());
                    if session_number == 1 {
                        fs::write(workspace.join("provider-side-effect"), b"retained").unwrap();
                    }
                    workspaces.push(workspace);
                }
                let frames: Vec<serde_json::Value> = match req {
                    "hello" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                    })],
                    "create_session" if session_number == 1 => vec![
                        serde_json::json!({
                            "v":1,"ev":"session_status","status":"attached","session_id":&sid
                        }),
                        serde_json::json!({
                            "v":1,"reply_to":id,"ev":"attached",
                            "session":{"session_id":&sid,"status":"idle"}
                        }),
                        serde_json::json!({
                            "v":1,"ev":"model_info","session_id":&sid,
                            "provider":"OpenAI","model":active_model
                        }),
                    ],
                    // A correlated attached reply is the completion barrier. The
                    // unsolicited initial model_info event is optional; runtime_info
                    // below is the authoritative route check.
                    "create_session" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"attached",
                        "session":{"session_id":&sid,"status":"idle"}
                    })],
                    "set_model" => {
                        assert_eq!(
                            session_number, 1,
                            "transient empty routes must be re-queried"
                        );
                        assert_eq!(f["model"], "openai-oauth:gpt-5.4");
                        active_model = "gpt-5.4";
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "get_runtime_info" => {
                        runtime_count += 1;
                        let routes = if session_number == 2 && runtime_count == 1 {
                            Vec::<serde_json::Value>::new()
                        } else {
                            vec![serde_json::json!({
                                "provider":"OpenAI","model":active_model,
                                "api_method":"openai-oauth","available":true
                            })]
                        };
                        vec![serde_json::json!({
                            "v":1,"reply_to":id,"ev":"runtime_info","session_id":&sid,
                            "provider":"OpenAI","model":active_model,"routes":routes
                        })]
                    }
                    "set_reasoning_effort" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "send_message" => {
                        turn_count += 1;
                        assert_eq!(turn_count, 1, "batch session received a second turn");
                        let content = f["content"].as_str().unwrap();
                        let text = if content.ends_with("direct secret prompt") {
                            "DIRECT_OK"
                        } else {
                            assert!(content.ends_with("second"));
                            "SECOND_OK"
                        };
                        let mut frames = vec![
                            serde_json::json!({
                                "v":1,"ev":"message_accepted","session_id":&sid
                            }),
                            serde_json::json!({
                                "v":1,"ev":"model_info","session_id":&sid,
                                "provider":"OpenAI","model":active_model
                            }),
                            serde_json::json!({
                                "v":1,"ev":"text_delta","session_id":&sid,"text":text
                            }),
                        ];
                        if session_number == 1 {
                            frames.push(serde_json::json!({
                                "v":1,"ev":"token_usage","session_id":&sid,
                                "input":11,"output":2,"cache_read_input":3
                            }));
                        }
                        frames.push(serde_json::json!({
                            "v":1,"ev":"turn_done","session_id":&sid
                        }));
                        frames
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
        (turns_per_session, workspaces)
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
            b"print(llm_batch_fresh(['direct secret prompt','second'],model='gpt-5.4',workers=2))\n",
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
    let request_ids: std::collections::HashSet<_> = usages
        .iter()
        .map(|row| row["request_id"].as_str().unwrap())
        .collect();
    assert_eq!(request_ids.len(), 2, "one logical request per batch item");
    let session_ids: std::collections::HashSet<_> = usages
        .iter()
        .map(|row| row["session_id"].as_str().unwrap())
        .collect();
    assert_eq!(session_ids, std::collections::HashSet::from(["s1", "s2"]));
    for usage in &usages {
        assert_eq!(usage["schema_version"], 2);
        assert_eq!(usage["event"], "model_attempt");
        assert_eq!(usage["attempt"], 1);
        assert_eq!(usage["category"], "turn");
        assert_eq!(usage["outcome"], "succeeded");
        assert_eq!(usage["degraded_transport"], false);
        assert_eq!(usage["failed_attempts_before_success"], 0);
        assert_eq!(usage["provider"], "OpenAI");
        assert_eq!(usage["model"], "gpt-5.4");
        if usage["session_id"] == "s1" {
            assert_eq!(usage["input_tokens"], 11);
            assert_eq!(usage["output_tokens"], 2);
            assert_eq!(usage["cache_read_tokens"], 3);
        } else {
            assert_eq!(usage["session_id"], "s2");
            assert!(usage.get("input_tokens").is_none());
            assert!(usage.get("output_tokens").is_none());
            assert!(usage.get("cache_read_tokens").is_none());
        }
        assert!(usage["latency_ms"].as_u64().is_some());
        assert!(usage.get("error").is_none());
    }
    let (turns, workspaces) = server.join().unwrap();
    assert_eq!(turns, [1, 1]);
    assert_eq!(workspaces.len(), 2);
    assert_ne!(workspaces[0], workspaces[1]);
    assert_eq!(
        fs::read(workspaces[0].join("provider-side-effect")).unwrap(),
        b"retained"
    );
    assert!(!workspaces[1].exists());
    fs::remove_file(workspaces[0].join("provider-side-effect")).unwrap();
    fs::remove_dir(&workspaces[0]).unwrap();
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn jcode_fresh_batch_retries_setup_without_repeating_model_turn() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("jsr");
    let socket = t.join("api.sock");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let mut messages = Vec::new();
        let mut workspaces = Vec::new();
        for session_number in 1..=3 {
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let sid = format!("s{session_number}");
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).unwrap() == 0 {
                    break;
                }
                let request: serde_json::Value = serde_json::from_str(&line).unwrap();
                let id = request["id"].as_u64().unwrap();
                let req = request["req"].as_str().unwrap();
                if req == "create_session" {
                    workspaces.push(PathBuf::from(request["working_dir"].as_str().unwrap()));
                }
                let frames = match req {
                    "hello" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                    })],
                    "create_session" if session_number < 3 => vec![serde_json::json!({
                        "v":1,"ev":"error","code":"service_unavailable","message":"injected setup failure"
                    })],
                    "create_session" => vec![
                        serde_json::json!({
                            "v":1,"reply_to":id,"ev":"attached",
                            "session":{"session_id":&sid,"status":"idle"}
                        }),
                        serde_json::json!({
                            "v":1,"ev":"model_info","session_id":&sid,
                            "provider":"OpenAI","model":"gpt-5.4"
                        }),
                    ],
                    "get_runtime_info" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"runtime_info","session_id":&sid,
                        "provider":"OpenAI","model":"gpt-5.4",
                        "routes":[{"provider":"OpenAI","model":"gpt-5.4",
                            "api_method":"openai-oauth","available":true}]
                    })],
                    "set_reasoning_effort" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "send_message" => {
                        messages.push(request["content"].as_str().unwrap().to_owned());
                        vec![
                            serde_json::json!({
                                "v":1,"ev":"model_info","session_id":&sid,
                                "provider":"OpenAI","model":"gpt-5.4"
                            }),
                            serde_json::json!({
                                "v":1,"ev":"text_delta","session_id":&sid,"text":"ONLY_OK"
                            }),
                            serde_json::json!({
                                "v":1,"ev":"token_usage","session_id":&sid,
                                "input":7,"output":1,"cache_read_input":0
                            }),
                            serde_json::json!({"v":1,"ev":"turn_done","session_id":&sid}),
                        ]
                    }
                    "archive_session" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    other => panic!("unexpected {other}"),
                };
                for frame in frames {
                    serde_json::to_writer(&mut stream, &frame).unwrap();
                    stream.write_all(b"\n").unwrap();
                    stream.flush().unwrap();
                }
            }
        }
        (messages, workspaces)
    });

    let cfg = config(&t, "jcode-api", 1024, 1, 3, 4);
    let id = sid(&t, &cfg);
    let trace = t.join("usage.jsonl");
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args(["exec", &id])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(b"print(llm_batch_fresh(['once'],model='gpt-5.4',workers=1))\n")
        .unwrap();
    let output = child.wait_with_output().unwrap();
    let out = ok(output);
    assert!(out.contains("ONLY_OK"), "{out}");
    let (messages, workspaces) = server.join().unwrap();
    assert_eq!(messages.len(), 1);
    assert_eq!(workspaces.len(), 3);
    for workspace in workspaces {
        if workspace.exists() {
            assert!(fs::read_dir(&workspace).unwrap().next().is_none());
            fs::remove_dir(workspace).unwrap();
        }
    }

    let rows: Vec<serde_json::Value> = fs::read_to_string(trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 3, "{rows:?}");
    assert!(rows.iter().all(|row| row["schema_version"] == 2));
    assert!(rows.iter().all(|row| row["event"] == "model_attempt"));
    assert!(
        rows.windows(2)
            .all(|pair| pair[0]["request_id"] == pair[1]["request_id"])
    );
    assert_eq!(
        rows.iter()
            .map(|row| row["attempt"].as_u64().unwrap())
            .collect::<Vec<_>>(),
        [1, 2, 3]
    );
    let failures = &rows[..2];
    assert!(
        failures
            .iter()
            .all(|row| row["category"] == "session_setup")
    );
    assert!(failures.iter().all(|row| row["outcome"] == "failed"));
    assert!(failures.iter().all(|row| row["stage"] == "session_setup"));
    assert!(failures.iter().all(|row| row["setup_substage"] == "attach"));
    assert!(
        failures
            .iter()
            .all(|row| row["error"] == "provider_call_failed")
    );
    assert!(
        failures
            .iter()
            .all(|row| row["error_category"] == "provider")
    );
    assert!(failures.iter().all(|row| row["session_id"].is_null()));
    assert!(failures.iter().all(|row| row.get("input_tokens").is_none()));

    let success = &rows[2];
    assert_eq!(success["category"], "turn");
    assert_eq!(success["outcome"], "succeeded");
    assert_eq!(success["session_id"], "s3");
    assert_eq!(success["degraded_transport"], true);
    assert_eq!(success["failed_attempts_before_success"], 2);
    assert_eq!(success["input_tokens"], 7);
    assert_eq!(success["output_tokens"], 1);
    assert_eq!(
        rows.iter().filter(|row| row["category"] == "turn").count(),
        1,
        "setup retries must not consume entered-turn budget"
    );
}

#[test]
#[cfg(unix)]
fn jcode_fresh_batch_stops_after_four_failed_setups() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("jsb");
    let socket = t.join("api.sock");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let mut messages = Vec::new();
        let mut archives = Vec::new();
        for session_number in 1..=4 {
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let sid = format!("s{session_number}");
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
                        "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                    })],
                    "create_session" => vec![
                        serde_json::json!({
                            "v":1,"reply_to":id,"ev":"attached",
                            "session":{"session_id":&sid,"status":"idle"}
                        }),
                        serde_json::json!({
                            "v":1,"ev":"model_info","session_id":&sid,
                            "provider":"OpenAI","model":"gpt-5.4"
                        }),
                    ],
                    "get_runtime_info" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"runtime_info","session_id":&sid,
                        "provider":"OpenAI","model":"gpt-5.4",
                        "routes":[{"provider":"OpenAI","model":"gpt-5.4",
                            "api_method":"openai-oauth","available":true}]
                    })],
                    "set_reasoning_effort" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"error","code":"service_unavailable","message":"injected setup failure"
                    })],
                    "send_message" => {
                        messages.push(request["content"].as_str().unwrap().to_owned());
                        vec![
                            serde_json::json!({
                                "v":1,"ev":"model_info","session_id":&sid,
                                "provider":"OpenAI","model":"gpt-5.4"
                            }),
                            serde_json::json!({
                                "v":1,"ev":"text_delta","session_id":&sid,"text":"ONLY_OK"
                            }),
                            serde_json::json!({
                                "v":1,"ev":"token_usage","session_id":&sid,
                                "input":7,"output":1,"cache_read_input":0
                            }),
                            serde_json::json!({"v":1,"ev":"turn_done","session_id":&sid}),
                        ]
                    }
                    "cancel" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "archive_session" => {
                        archives.push(sid.clone());
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    other => panic!("unexpected {other}"),
                };
                for frame in frames {
                    serde_json::to_writer(&mut stream, &frame).unwrap();
                    stream.write_all(b"\n").unwrap();
                    stream.flush().unwrap();
                }
            }
        }
        (messages, archives)
    });

    let cfg = config(&t, "jcode-api", 1024, 1, 3, 4);
    let id = sid(&t, &cfg);
    let trace = t.join("usage.jsonl");
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args(["exec", &id])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(b"print(llm_batch_fresh(['once'],model='gpt-5.4',workers=1))\n")
        .unwrap();
    let output = child.wait_with_output().unwrap();
    let out = ok(output);
    assert!(out.contains("provider_call_failed_retry_item"), "{out}");
    let (messages, archives) = server.join().unwrap();
    assert!(messages.is_empty());
    assert_eq!(archives, vec!["s1", "s2", "s3", "s4"]);

    let rows: Vec<serde_json::Value> = fs::read_to_string(trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 4, "{rows:?}");
    assert!(
        rows.windows(2)
            .all(|pair| pair[0]["request_id"] == pair[1]["request_id"])
    );
    assert_eq!(
        rows.iter()
            .map(|row| row["attempt"].as_u64().unwrap())
            .collect::<Vec<_>>(),
        [1, 2, 3, 4]
    );
    assert!(rows.iter().all(|row| row["category"] == "session_setup"));
    assert!(rows.iter().all(|row| row["outcome"] == "failed"));
    assert!(rows.iter().all(|row| row["stage"] == "session_setup"));
    assert!(rows.iter().all(|row| row["setup_substage"] == "reasoning"));
    assert_eq!(
        rows.iter()
            .map(|row| row["session_id"].as_str().unwrap())
            .collect::<Vec<_>>(),
        ["s1", "s2", "s3", "s4"]
    );
    assert!(rows.iter().all(|row| row.get("input_tokens").is_none()));
}

#[test]
#[cfg(unix)]
fn solo_root_does_not_retry_typed_permanent_invalid_request() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("pir");
    let socket = t.join("a");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let (probe, _) = listener.accept().unwrap();
        drop(probe);
        let (mut stream, _) = listener.accept().unwrap();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        let mut entered_turns = 0;
        let mut archive_requests = 0;
        let mut workspace = None;
        loop {
            let mut line = String::new();
            if reader.read_line(&mut line).unwrap() == 0 {
                break;
            }
            let request: serde_json::Value = serde_json::from_str(&line).unwrap();
            let id = request["id"].as_u64().unwrap();
            if request["req"] == "create_session" {
                workspace = Some(PathBuf::from(request["working_dir"].as_str().unwrap()));
            }
            let frames = match request["req"].as_str().unwrap() {
                "hello" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                })],
                "create_session" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"attached",
                    "session":{"session_id":"s1","status":"idle"}
                })],
                "get_runtime_info" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"runtime_info","session_id":"s1",
                    "provider":"OpenAI","model":"gpt-5.4",
                    "routes":[{"provider":"OpenAI","model":"gpt-5.4",
                        "api_method":"openai-oauth","available":true}]
                })],
                "set_reasoning_effort" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"ok"
                })],
                "send_message" => {
                    entered_turns += 1;
                    vec![serde_json::json!({
                        "v":1,"ev":"error","session_id":"s1",
                        "code":"invalid_request","message":"permanent invalid request"
                    })]
                }
                "cancel" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"ok"
                })],
                "archive_session" => {
                    archive_requests += 1;
                    Vec::new()
                }
                other => panic!("unexpected request {other}"),
            };
            for frame in frames {
                serde_json::to_writer(&mut stream, &frame).unwrap();
                stream.write_all(b"\n").unwrap();
                stream.flush().unwrap();
            }
        }
        (entered_turns, archive_requests, workspace.unwrap())
    });

    let cfg = config(&t, "jcode-api", 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "synthetic row").unwrap();
    let trace = t.join("model.jsonl");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args([
            "solo",
            "return scripted result",
            "-f",
            input.to_str().unwrap(),
            "--model",
            "gpt-5.4",
        ])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .output()
        .unwrap();
    assert!(!output.status.success());
    let (entered_turns, archive_requests, workspace) = server.join().unwrap();
    assert_eq!(entered_turns, 1, "permanent error must not retry");
    assert_eq!(archive_requests, 1);
    assert!(workspace.is_dir());
    assert!(fs::read_dir(&workspace).unwrap().next().is_none());
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert_eq!(
        stderr.matches("reason=archive_unconfirmed").count(),
        1,
        "{stderr}"
    );
    let rows: Vec<serde_json::Value> = fs::read_to_string(trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 1, "{rows:?}");
    assert_eq!(rows[0]["category"], "turn");
    assert_eq!(rows[0]["entered_turn"], 1);
    assert_eq!(rows[0]["error_category"], "provider");
    fs::remove_dir(workspace).unwrap();
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn solo_root_retries_explicit_typed_transient_errors_with_separate_budgets() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("rtr");
    let socket = t.join("a");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let mut entered_turns = Vec::new();
        let mut workspaces = Vec::new();
        for session_number in 1..=3 {
            // Each open probes bridge liveness before creating its protocol connection.
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let sid = format!("s{session_number}");
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).unwrap() == 0 {
                    break;
                }
                let request: serde_json::Value = serde_json::from_str(&line).unwrap();
                let id = request["id"].as_u64().unwrap();
                let req = request["req"].as_str().unwrap();
                if req == "create_session" {
                    workspaces.push(PathBuf::from(request["working_dir"].as_str().unwrap()));
                }
                let frames = match req {
                    "hello" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                    })],
                    "create_session" if session_number == 1 => vec![serde_json::json!({
                        "v":1,"ev":"error","code":"service_unavailable","message":"injected transient setup provider failure"
                    })],
                    "create_session" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"attached",
                        "session":{"session_id":&sid,"status":"idle"}
                    })],
                    "get_runtime_info" => vec![serde_json::json!({
                        "v":1,"reply_to":id,"ev":"runtime_info","session_id":&sid,
                        "provider":"OpenAI","model":"gpt-5.4",
                        "routes":[{"provider":"OpenAI","model":"gpt-5.4",
                            "api_method":"openai-oauth","available":true}]
                    })],
                    "set_reasoning_effort" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "send_message" => {
                        entered_turns.push(sid.clone());
                        if session_number == 2 {
                            vec![serde_json::json!({
                                "v":1,"ev":"error","session_id":&sid,"code":"service_unavailable",
                                "message":"injected transient provider failure"
                            })]
                        } else {
                            vec![
                                serde_json::json!({
                                    "v":1,"ev":"model_info","session_id":&sid,
                                    "provider":"OpenAI","model":"gpt-5.4"
                                }),
                                serde_json::json!({
                                    "v":1,"ev":"text_delta","session_id":&sid,
                                    "text":"```python\nFINAL(\"ROUTE_OK\")\n```"
                                }),
                                serde_json::json!({
                                    "v":1,"ev":"token_usage","session_id":&sid,
                                    "input":13,"output":2,"cache_read_input":5
                                }),
                                serde_json::json!({"v":1,"ev":"turn_done","session_id":&sid}),
                            ]
                        }
                    }
                    "cancel" | "archive_session" => {
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    other => panic!("unexpected root request {other}"),
                };
                for frame in frames {
                    serde_json::to_writer(&mut stream, &frame).unwrap();
                    stream.write_all(b"\n").unwrap();
                    stream.flush().unwrap();
                }
            }
        }
        (entered_turns, workspaces)
    });

    let cfg = config(&t, "jcode-api", 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "synthetic row").unwrap();
    let model_trace = t.join("model.jsonl");
    let solo_trace = t.join("solo.log");
    let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    command
        .args([
            "solo",
            "return the scripted result",
            "-f",
            input.to_str().unwrap(),
            "--model",
            "gpt-5.4",
        ])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &model_trace)
        .env("AZDAJA_SOLO_TRACE", &solo_trace)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let output = command.output().unwrap();
    let out = ok(output);
    assert_eq!(out.trim(), "ROUTE_OK");
    let (entered_turns, workspaces) = server.join().unwrap();
    assert_eq!(entered_turns, ["s2", "s3"]);
    assert_eq!(workspaces.len(), 3);
    for workspace in workspaces {
        if workspace.exists() {
            assert!(fs::read_dir(&workspace).unwrap().next().is_none());
            fs::remove_dir(workspace).unwrap();
        }
    }

    let rows: Vec<serde_json::Value> = fs::read_to_string(&model_trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 3, "{rows:?}");
    assert!(
        rows.windows(2)
            .all(|pair| pair[0]["request_id"] == pair[1]["request_id"])
    );
    assert_eq!(
        rows.iter()
            .map(|row| row["attempt"].as_u64().unwrap())
            .collect::<Vec<_>>(),
        [1, 2, 3]
    );

    let setup_failure = &rows[0];
    assert_eq!(setup_failure["category"], "session_setup");
    assert_eq!(setup_failure["outcome"], "failed");
    assert_eq!(setup_failure["setup_substage"], "attach");
    assert_eq!(setup_failure["error_category"], "provider");
    assert!(setup_failure["session_id"].is_null());
    assert!(setup_failure.get("entered_turn").is_none());

    let turn_failure = &rows[1];
    assert_eq!(turn_failure["category"], "turn");
    assert_eq!(turn_failure["outcome"], "failed");
    assert_eq!(turn_failure["session_id"], "s2");
    assert_eq!(turn_failure["entered_turn"], 1);
    assert_eq!(turn_failure["error_category"], "provider");
    assert!(turn_failure.get("input_tokens").is_none());

    let success = &rows[2];
    assert_eq!(success["category"], "turn");
    assert_eq!(success["outcome"], "succeeded");
    assert_eq!(success["session_id"], "s3");
    assert_eq!(success["entered_turn"], 2);
    assert_eq!(success["provider"], "OpenAI");
    assert_eq!(success["model"], "gpt-5.4");
    assert_eq!(success["degraded_transport"], true);
    assert_eq!(success["failed_attempts_before_success"], 2);

    let successful_usage = rows
        .iter()
        .filter(|row| row["outcome"] == "succeeded")
        .fold((0, 0, 0), |sum, row| {
            (
                sum.0 + row["input_tokens"].as_u64().unwrap(),
                sum.1 + row["output_tokens"].as_u64().unwrap(),
                sum.2 + row["cache_read_tokens"].as_u64().unwrap(),
            )
        });
    assert_eq!(successful_usage, (13, 2, 5));
    assert_eq!(
        rows.iter().filter(|row| row["outcome"] == "failed").count(),
        2
    );
    assert_eq!(
        rows.iter().filter(|row| row["category"] == "turn").count(),
        2,
        "setup failure must not spend either physical entered turn"
    );

    let solo = fs::read_to_string(solo_trace).unwrap();
    assert!(solo.contains("attempt=3"), "{solo}");
    assert!(solo.contains("session_id=Some(\"s3\")"), "{solo}");
    assert!(solo.contains("degraded_transport=true"), "{solo}");
    assert!(solo.contains("failed_attempts_before_success=2"), "{solo}");
    assert!(
        solo.contains("provider=\"OpenAI\" model=\"gpt-5.4\""),
        "{solo}"
    );
    let traced_request_id = success["request_id"].as_str().unwrap();
    let solo_lines: Vec<&str> = solo.lines().collect();
    assert_eq!(
        solo_lines[solo_lines.len() - 3],
        format!("=== solo runtime trace begin request_id={traced_request_id:?} ===")
    );
    assert_eq!(
        solo_lines[solo_lines.len() - 1],
        format!("=== solo runtime trace end request_id={traced_request_id:?} ===")
    );
    let runtime: serde_json::Value =
        serde_json::from_str(solo_lines[solo_lines.len() - 2]).unwrap();
    assert_eq!(runtime["schema_version"], 2);
    assert_eq!(runtime["event"], "solo_runtime");
    assert_eq!(runtime["request_id"], traced_request_id);
    assert_eq!(runtime["outcome"], "succeeded");
    assert_eq!(runtime["exec_invocation_count"], 1);
    assert_eq!(runtime["snapshot_save_count"], 1);
    assert_eq!(runtime["snapshot_load_count"], 0);
    assert_eq!(runtime["sub_call_count"], 0);
    assert!(runtime["exec_wall_ns"].as_u64().is_some());
    assert!(runtime["snapshot_save_wall_ns"].as_u64().is_some());
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn solo_root_stops_after_four_setup_attempts_without_entering_turn() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("rsa");
    let socket = t.join("a");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let mut workspaces = Vec::new();
        for _ in 0..4 {
            let (probe, _) = listener.accept().unwrap();
            drop(probe);
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).unwrap() == 0 {
                    break;
                }
                let request: serde_json::Value = serde_json::from_str(&line).unwrap();
                let id = request["id"].as_u64().unwrap();
                if request["req"] == "create_session" {
                    let workspace = PathBuf::from(request["working_dir"].as_str().unwrap());
                    assert!(workspace.is_dir());
                    assert!(fs::read_dir(&workspace).unwrap().next().is_none());
                    workspaces.push(workspace);
                }
                let frame = match request["req"].as_str().unwrap() {
                    "hello" => serde_json::json!({
                        "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                    }),
                    "create_session" => serde_json::json!({
                        "v":1,"ev":"error","code":"service_unavailable","message":"transient provider setup failure"
                    }),
                    other => panic!("setup failure must not reach {other}"),
                };
                serde_json::to_writer(&mut stream, &frame).unwrap();
                stream.write_all(b"\n").unwrap();
                stream.flush().unwrap();
            }
        }
        workspaces
    });

    let cfg = config(&t, "jcode-api", 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "synthetic row").unwrap();
    let trace = t.join("model.jsonl");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args([
            "solo",
            "return scripted result",
            "-f",
            input.to_str().unwrap(),
            "--model",
            "gpt-5.4",
        ])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &trace)
        .output()
        .unwrap();
    assert!(!output.status.success());
    let workspaces = server.join().unwrap();
    assert_eq!(workspaces.len(), 4);
    for workspace in &workspaces {
        assert!(workspace.is_dir(), "{}", workspace.display());
        assert!(fs::read_dir(workspace).unwrap().next().is_none());
    }
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert_eq!(
        stderr.matches("reason=archive_unconfirmed").count(),
        4,
        "{stderr}"
    );
    let rows: Vec<serde_json::Value> = fs::read_to_string(trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 4, "{rows:?}");
    assert_eq!(
        rows.iter()
            .map(|row| row["attempt"].as_u64().unwrap())
            .collect::<Vec<_>>(),
        [1, 2, 3, 4]
    );
    assert!(rows.iter().all(|row| row["category"] == "session_setup"));
    assert!(rows.iter().all(|row| row.get("entered_turn").is_none()));
    for workspace in workspaces {
        fs::remove_dir(workspace).unwrap();
    }
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn solo_jcode_runtime_repair_reuses_one_session_and_archives_once() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("jrs");
    let socket = t.join("a");
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let (probe, _) = listener.accept().unwrap();
        drop(probe);
        let (mut stream, _) = listener.accept().unwrap();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        let mut messages = Vec::new();
        let mut archives = 0;
        loop {
            let mut line = String::new();
            if reader.read_line(&mut line).unwrap() == 0 {
                break;
            }
            let request: serde_json::Value = serde_json::from_str(&line).unwrap();
            let id = request["id"].as_u64().unwrap();
            let frames = match request["req"].as_str().unwrap() {
                "hello" => vec![
                    serde_json::json!({"v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"}),
                ],
                "create_session" => vec![
                    serde_json::json!({"v":1,"reply_to":id,"ev":"attached","session":{"session_id":"same","status":"idle"}}),
                ],
                "get_runtime_info" => vec![
                    serde_json::json!({"v":1,"reply_to":id,"ev":"runtime_info","session_id":"same","provider":"OpenAI","model":"gpt-5.4","routes":[{"provider":"OpenAI","model":"gpt-5.4","api_method":"openai-oauth","available":true}]}),
                ],
                "set_reasoning_effort" => vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})],
                "send_message" => {
                    let content = request["content"].as_str().unwrap();
                    if messages.is_empty() {
                        assert!(content.contains("agent tools"));
                        assert!(content.contains("provider-native tools"));
                        assert!(content.contains("filesystem actions"));
                        assert!(content.contains("solve only through preloaded ctx"));
                    }
                    messages.push(content.to_owned());
                    let text = match messages.len() {
                        1 => "```python\nctx = \"poison\"\nassert False\n```".to_owned(),
                        2 => format!("```python\n{}\n```", "x = 1\n".repeat(51)),
                        _ => "```python\nassert ctx == \"original\"\nFINAL(\"REPAIRED\")\n```"
                            .to_owned(),
                    };
                    vec![
                        serde_json::json!({"v":1,"ev":"model_info","session_id":"same","provider":"OpenAI","model":"gpt-5.4"}),
                        serde_json::json!({"v":1,"ev":"text_delta","session_id":"same","text":text}),
                        serde_json::json!({"v":1,"ev":"token_usage","session_id":"same","input":4,"output":1,"cache_read_input":0}),
                        serde_json::json!({"v":1,"ev":"turn_done","session_id":"same"}),
                    ]
                }
                "archive_session" => {
                    archives += 1;
                    vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                }
                other => panic!("unexpected root request {other}"),
            };
            for frame in frames {
                serde_json::to_writer(&mut stream, &frame).unwrap();
                stream.write_all(b"\n").unwrap();
                stream.flush().unwrap();
            }
        }
        (messages, archives)
    });
    let cfg = config(&t, "jcode-api", 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "original").unwrap();
    let model_trace = t.join("model.jsonl");
    let solo_trace = t.join("solo.log");
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args([
            "solo",
            "generic question",
            "-f",
            input.to_str().unwrap(),
            "--model",
            "gpt-5.4",
        ])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &model_trace)
        .env("AZDAJA_SOLO_TRACE", &solo_trace)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "REPAIRED");
    let (messages, archives) = server.join().unwrap();
    assert_eq!(messages.len(), 3);
    assert!(messages[1].contains("typed category Assertion"));
    assert!(messages[2].contains("typed category LineLimit"));
    assert_eq!(archives, 1);
    let rows: Vec<serde_json::Value> = fs::read_to_string(model_trace)
        .unwrap()
        .lines()
        .map(|line| serde_json::from_str(line).unwrap())
        .collect();
    assert_eq!(rows.len(), 3);
    assert_eq!(rows[0]["session_id"], "same");
    assert_eq!(rows[1]["session_id"], "same");
    assert_eq!(rows[1]["category"], "repair");
    assert_eq!(rows[2]["session_id"], "same");
    assert_eq!(rows[2]["category"], "repair");
    assert!(
        rows[1]["request_id"]
            .as_str()
            .unwrap()
            .ends_with("-repair-1")
    );
    assert!(
        rows[2]["request_id"]
            .as_str()
            .unwrap()
            .ends_with("-repair-2")
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn valid_root_response_is_not_retried_when_trace_append_fails() {
    use std::io::{BufRead, BufReader, Write as _};
    use std::os::unix::net::UnixListener;
    use std::thread;

    let t = temp("tio");
    let socket = t.join("a");
    let model_trace = t.join("model.jsonl");
    let server_trace = model_trace.clone();
    let listener = UnixListener::bind(&socket).unwrap();
    let server = thread::spawn(move || {
        let (probe, _) = listener.accept().unwrap();
        drop(probe);
        let (mut stream, _) = listener.accept().unwrap();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        let mut entered_turns = 0;
        loop {
            let mut line = String::new();
            if reader.read_line(&mut line).unwrap() == 0 {
                break;
            }
            let request: serde_json::Value = serde_json::from_str(&line).unwrap();
            let id = request["id"].as_u64().unwrap();
            let frames = match request["req"].as_str().unwrap() {
                "hello" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"hello_ok","version":1,"server":"fake"
                })],
                "create_session" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"attached",
                    "session":{"session_id":"s1","status":"idle"}
                })],
                "get_runtime_info" => vec![serde_json::json!({
                    "v":1,"reply_to":id,"ev":"runtime_info","session_id":"s1",
                    "provider":"OpenAI","model":"gpt-5.4",
                    "routes":[{"provider":"OpenAI","model":"gpt-5.4",
                        "api_method":"openai-oauth","available":true}]
                })],
                "set_reasoning_effort" => {
                    vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                }
                "send_message" => {
                    entered_turns += 1;
                    // Preflight already succeeded. Break only the later append to prove a
                    // diagnostic failure cannot turn this valid response into another call.
                    fs::remove_file(&server_trace).unwrap();
                    fs::create_dir(&server_trace).unwrap();
                    vec![
                        serde_json::json!({
                            "v":1,"ev":"model_info","session_id":"s1",
                            "provider":"OpenAI","model":"gpt-5.4"
                        }),
                        serde_json::json!({
                            "v":1,"ev":"text_delta","session_id":"s1",
                            "text":"```python\nFINAL(\"TRACE_OK\")\n```"
                        }),
                        serde_json::json!({
                            "v":1,"ev":"token_usage","session_id":"s1",
                            "input":4,"output":1,"cache_read_input":0
                        }),
                        serde_json::json!({"v":1,"ev":"turn_done","session_id":"s1"}),
                    ]
                }
                "archive_session" => {
                    vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                }
                other => panic!("unexpected root request {other}"),
            };
            for frame in frames {
                serde_json::to_writer(&mut stream, &frame).unwrap();
                stream.write_all(b"\n").unwrap();
                stream.flush().unwrap();
            }
        }
        entered_turns
    });

    let cfg = config(&t, "jcode-api", 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(&input, "synthetic row").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args([
            "solo",
            "return scripted result",
            "-f",
            input.to_str().unwrap(),
            "--model",
            "gpt-5.4",
        ])
        .env_remove("RLM_DEPTH")
        .env("AZDAJA_HOME", t.join("state"))
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_JCODE_API_SOCKET", &socket)
        .env("AZDAJA_MODEL_TRACE", &model_trace)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "TRACE_OK");
    assert_eq!(
        server.join().unwrap(),
        1,
        "valid response must not be retried"
    );
    assert!(
        String::from_utf8_lossy(&output.stderr).contains("model trace write failed"),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
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
                    "create_session" => vec![
                        serde_json::json!({
                            "v": 1, "reply_to": id, "ev": "attached",
                            "session": {"session_id": &sid, "status": "idle"}
                        }),
                        serde_json::json!({
                            "v":1,"ev":"model_info","session_id":&sid,
                            "provider":"OpenAI","model":"gpt-5.4"
                        }),
                    ],
                    "set_model" => {
                        assert_eq!(request["model"], "openai-oauth:gpt-5.4");
                        vec![serde_json::json!({"v":1,"reply_to":id,"ev":"ok"})]
                    }
                    "get_runtime_info" => vec![serde_json::json!({
                        "v": 1, "reply_to": id, "ev": "runtime_info",
                        "session_id": &sid, "provider": "OpenAI", "model": "gpt-5.4",
                        "routes":[{
                            "provider":"OpenAI","model":"gpt-5.4",
                            "api_method":"openai-oauth","available":true
                        }]
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
                                "code": "service_unavailable", "message": "injected provider failure"
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

#[test]
#[cfg(unix)]
fn command_help_usage_and_bare_text_are_identical_through_both_names() {
    let t = temp("command-help");
    let expected = [
        ("start", "Usage: az start"),
        ("load", "Usage: az load <session-id> <path> <variable>"),
        ("exec", "Usage: az exec <session-id>"),
        ("final", "Usage: az final <session-id>"),
        ("list", "Usage: az list"),
        ("map", "Usage: az map"),
        ("kill", "Usage: az kill <session-id>"),
        (
            "solo",
            "Usage: az solo <question> -f <path> [--model <model>] [--sub-model <model>]",
        ),
        (
            "doctor",
            "Usage: az doctor [jcode|claude|codex|gemini|opencode|all|--caps]",
        ),
        ("install", "Usage: az install [TARGET[,TARGET...]|all]"),
        (
            "uninstall",
            "Usage: az uninstall [jcode|claude|codex|gemini|opencode|standalone|all]",
        ),
        ("help", "Usage: az help [command]"),
    ];
    let bare = format!(
        "AZDAJA v{} — virtual memory for language models\nUsage: az <command>\nCommands: help solo map install doctor start load exec final list kill uninstall\nInstall: az install  (auto-detects supported tools)\nExample: az solo \"summarize this file\" -f ./document.txt\n",
        env!("CARGO_PKG_VERSION")
    );
    for name in ["az", "azdaja"] {
        let executable = t.join(name);
        fs::copy(env!("CARGO_BIN_EXE_azdaja"), &executable).unwrap();
        let output = Command::new(&executable)
            .env("TERM", "dumb")
            .env("NO_COLOR", "1")
            .output()
            .unwrap();
        assert_eq!(output.status.code(), Some(0));
        assert_eq!(String::from_utf8(output.stdout).unwrap(), bare);
        assert!(output.stderr.is_empty());

        for args in [["--help"].as_slice(), ["help"].as_slice()] {
            let top = Command::new(&executable).args(args).output().unwrap();
            assert_eq!(top.status.code(), Some(0));
            assert!(top.stderr.is_empty());
            assert_eq!(String::from_utf8(top.stdout).unwrap(), bare);
        }

        for (command, usage) in expected {
            let output = Command::new(&executable)
                .args([command, "--help"])
                .output()
                .unwrap();
            assert_eq!(output.status.code(), Some(0), "{name} {command}");
            let stdout = String::from_utf8(output.stdout).unwrap();
            match command {
                "doctor" => assert_eq!(
                    stdout,
                    format!(
                        "{usage}\nNo name: check the configured connection. A tool name checks installed files only.\nExamples:\n  az doctor\n  az doctor jcode\n"
                    )
                ),
                "install" => assert_eq!(
                    stdout,
                    format!(
                        "{usage}\nNo name: detect and install every supported tool found on this computer.\nExamples:\n  az install\n  az install jcode\n  az install jcode,codex\n  az install all\n"
                    )
                ),
                "uninstall" => assert_eq!(
                    stdout,
                    format!(
                        "{usage}\nNo name: remove detected Azdaja tool integrations only.\n'standalone' removes the curl-installed command and documents. 'all' removes both.\nExamples:\n  az uninstall jcode\n  az uninstall standalone\n  az uninstall all\n"
                    )
                ),
                _ => assert_eq!(stdout, format!("{usage}\n")),
            }
            assert!(output.stderr.is_empty());
        }

        let invalid: [(&[&str], &str); 12] = [
            (&["start", "extra"], expected[0].1),
            (&["load", "only-one"], expected[1].1),
            (&["exec", "session", "extra"], expected[2].1),
            (&["final"], expected[3].1),
            (&["list", "extra"], expected[4].1),
            (&["map", "extra"], expected[5].1),
            (&["kill"], expected[6].1),
            (&["solo", "question", "--bogus", "value"], expected[7].1),
            (&["doctor", "--bogus"], expected[8].1),
            (&["install", "--bogus"], expected[9].1),
            (&["uninstall", "--harness"], expected[10].1),
            (&["help", "start", "extra"], expected[11].1),
        ];
        for (args, usage) in invalid {
            let output = Command::new(&executable).args(args).output().unwrap();
            assert_eq!(output.status.code(), Some(2), "{name} {args:?}");
            assert!(output.stdout.is_empty());
            assert_eq!(
                String::from_utf8(output.stderr).unwrap(),
                format!("{usage}\n")
            );
        }
    }
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_empty_values_fail_before_config_or_input_loading() {
    let t = temp("solo-empty-preflight");
    let marker = t.join("provider-entered");
    let provider = t.join("provider.py");
    fs::write(
        &provider,
        format!(
            "import pathlib\npathlib.Path({:?}).write_text('entered')\nprint('unexpected')\n",
            marker.to_str().unwrap()
        ),
    )
    .unwrap();
    let malformed = t.join("malformed-config.toml");
    fs::write(&malformed, "this config must not be loaded = [").unwrap();
    let absent_input = t.join("absent-input");

    let cases: [(&[&str], &str); 3] = [
        (
            &["solo", "   ", "-f", absent_input.to_str().unwrap()],
            "error: solo question cannot be empty\n",
        ),
        (
            &[
                "solo",
                "question",
                "-f",
                absent_input.to_str().unwrap(),
                "--model",
                "",
            ],
            "error: --model cannot be empty\n",
        ),
        (
            &[
                "solo",
                "question",
                "-f",
                absent_input.to_str().unwrap(),
                "--sub-model",
                "   ",
            ],
            "error: --sub-model cannot be empty\n",
        ),
    ];
    for (args, expected) in cases {
        let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .args(args)
            .env("AZDAJA_CONFIG", &malformed)
            .env("AZDAJA_HOME", t.join("state-args"))
            .env_remove("RLM_DEPTH")
            .output()
            .unwrap();
        assert_eq!(output.status.code(), Some(2));
        assert!(output.stdout.is_empty());
        assert_eq!(String::from_utf8(output.stderr).unwrap(), expected);
    }

    let cfg = config(&t, &format!("python3 {}", provider.display()), 512, 1, 3, 4);
    let invalid_default = fs::read_to_string(&cfg)
        .unwrap()
        .replace("default_model = \"mock\"", "default_model = \"   \"");
    fs::write(&cfg, invalid_default).unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
        .args(["solo", "question", "-f", absent_input.to_str().unwrap()])
        .env("AZDAJA_CONFIG", &cfg)
        .env("AZDAJA_HOME", t.join("state-default"))
        .env_remove("RLM_DEPTH")
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(2));
    assert!(output.stdout.is_empty());
    assert_eq!(
        String::from_utf8(output.stderr).unwrap(),
        "error: default_model cannot be empty\n"
    );
    assert!(!marker.exists(), "provider entered during solo preflight");
    fs::remove_dir_all(t).unwrap();
}

#[test]
#[cfg(unix)]
fn doctor_reports_sanitized_config_path_and_terminal_cause() {
    let t = temp("doctor-config-diagnostics");
    let provider_called = t.join("provider-called");
    let provider = t.join("provider.py");
    fs::write(
        &provider,
        format!(
            "import pathlib\npathlib.Path({:?}).write_text('entered')\nprint('AZDAJA')\n",
            provider_called.to_str().unwrap()
        ),
    )
    .unwrap();
    let provider_command = format!("python3 {}", provider.display());

    let missing = t.join("missing.toml");
    let nonregular = t.join("nonregular.toml");
    fs::create_dir(&nonregular).unwrap();
    let syntax = t.join("syntax.toml");
    fs::write(
        &syntax,
        "sub_llm_cmd = \"DO_NOT_DISCLOSE_SYNTAX_VALUE\"\ndefault_model = \"mock\"\nclean_patterns = [",
    )
    .unwrap();
    let unknown = t.join("unknown.toml");
    fs::write(
        &unknown,
        format!(
            "sub_llm_cmd = {:?}\ndefault_model = \"mock\"\nunknown_field = \"DO_NOT_DISCLOSE_UNKNOWN_VALUE\"\n",
            provider_command
        ),
    )
    .unwrap();
    let secret_type = t.join("secret-type.toml");
    fs::write(
        &secret_type,
        format!(
            "sub_llm_cmd = {:?}\ndefault_model = \"mock\"\noutput_cap = \"DO_NOT_DISCLOSE_TYPE_VALUE\"\n",
            provider_command
        ),
    )
    .unwrap();
    let validation = config(&t, &provider_command, 512, 1, 3, 4);
    let validation_path = t.join("validation.toml");
    fs::rename(&validation, &validation_path).unwrap();
    let text = fs::read_to_string(&validation_path)
        .unwrap()
        .replace("output_cap = 512", "output_cap = 1");
    fs::write(&validation_path, text).unwrap();
    let regex_path = t.join("regex.toml");
    config(&t, &provider_command, 512, 1, 3, 4);
    fs::rename(t.join("config.toml"), &regex_path).unwrap();
    let text = fs::read_to_string(&regex_path).unwrap().replace(
        "clean_patterns = []",
        "clean_patterns = [\"DO_NOT_DISCLOSE_REGEX_VALUE(\"]",
    );
    fs::write(&regex_path, text).unwrap();

    let cases = [
        (&missing, "file is missing"),
        (&nonregular, "not a regular non-symlink file"),
        (&syntax, "unclosed array"),
        (&unknown, "unknown field `unknown_field`"),
        (&secret_type, "invalid type: string, expected usize"),
        (&validation_path, "output_cap must be at least 256"),
        (&regex_path, "invalid clean pattern: unclosed group"),
    ];
    for (index, (path, terminal)) in cases.into_iter().enumerate() {
        let output = Command::new(env!("CARGO_BIN_EXE_azdaja"))
            .arg("doctor")
            .env("AZDAJA_CONFIG", path)
            .env("AZDAJA_HOME", t.join(format!("state-{index}")))
            .env_remove("RLM_DEPTH")
            .output()
            .unwrap();
        assert_eq!(output.status.code(), Some(1), "{}", path.display());
        assert!(output.stderr.is_empty());
        let stdout = String::from_utf8(output.stdout).unwrap();
        let first = stdout.lines().next().unwrap();
        assert!(
            first.starts_with(&format!("FAIL config: {}:", path.display())),
            "{first}"
        );
        assert!(first.contains(terminal), "{first}");
        assert!(
            first.ends_with(&format!(
                "; Fix: repair {}, then rerun azdaja doctor",
                path.display()
            )),
            "{first}"
        );
        assert!(!stdout.contains("DO_NOT_DISCLOSE"), "{stdout}");
    }
    assert!(!provider_called.exists());
    fs::remove_dir_all(t).unwrap();
}

#[cfg(unix)]
fn wait_for_file(path: &Path) {
    let deadline = Instant::now() + Duration::from_secs(2);
    while Instant::now() < deadline {
        if fs::read_to_string(path).is_ok_and(|contents| !contents.trim().is_empty()) {
            return;
        }
        std::thread::sleep(Duration::from_millis(10));
    }
    panic!("provider did not populate {}", path.display());
}

#[cfg(unix)]
fn process_exists(pid: i32) -> bool {
    let result = unsafe { libc::kill(pid, 0) };
    result == 0 || std::io::Error::last_os_error().raw_os_error() != Some(libc::ESRCH)
}

#[cfg(unix)]
fn assert_processes_gone(pids: &Path) {
    let values: Vec<i32> = fs::read_to_string(pids)
        .unwrap()
        .split_whitespace()
        .map(|value| value.parse().unwrap())
        .collect();
    assert_eq!(values.len(), 2);
    let deadline = Instant::now() + Duration::from_secs(1);
    while values.iter().copied().any(process_exists) && Instant::now() < deadline {
        std::thread::sleep(Duration::from_millis(10));
    }
    for pid in values {
        assert!(
            !process_exists(pid),
            "provider process {pid} survived SIGINT"
        );
    }
}

#[test]
#[cfg(unix)]
fn sigint_stops_provider_group_cleans_prompt_and_preserves_exec_snapshot() {
    for prompt_file in [false, true] {
        let t = temp(if prompt_file {
            "interrupt-exec-prompt-file"
        } else {
            "interrupt-exec-stdin"
        });
        let calls = t.join("calls");
        let pids = t.join("pids");
        let provider = t.join("provider.py");
        fs::write(
            &provider,
            r#"import os, pathlib, subprocess, sys, time
calls = pathlib.Path(sys.argv[1])
calls.open("a").write("call\n")
if len(sys.argv) == 4:
    assert pathlib.Path(sys.argv[3]).read_text()
else:
    assert sys.stdin.read()
child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
pathlib.Path(sys.argv[2]).write_text(f"{os.getpid()} {child.pid}")
time.sleep(60)
"#,
        )
        .unwrap();
        let command = if prompt_file {
            format!(
                "python3 {} {} {} {{prompt_file}}",
                provider.display(),
                calls.display(),
                pids.display()
            )
        } else {
            format!(
                "python3 {} {} {}",
                provider.display(),
                calls.display(),
                pids.display()
            )
        };
        let cfg = config(&t, &command, 1024, 1, 60, 4);
        let id = sid(&t, &cfg);
        ok(run(&t, &cfg, &["exec", &id], "x = 1\n"));

        let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
        command
            .args(["exec", &id])
            .env_remove("RLM_DEPTH")
            .env("AZDAJA_HOME", t.join("state"))
            .env("AZDAJA_CONFIG", &cfg)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        let mut child = command.spawn().unwrap();
        child
            .stdin
            .take()
            .unwrap()
            .write_all(b"x = 99\nllm('sensitive interrupt prompt')\n")
            .unwrap();
        wait_for_file(&pids);
        let interrupted_at = Instant::now();
        assert_eq!(unsafe { libc::kill(child.id() as i32, libc::SIGINT) }, 0);
        let output = child.wait_with_output().unwrap();
        assert!(interrupted_at.elapsed() < Duration::from_secs(1));
        assert_eq!(output.status.code(), Some(130));
        assert!(output.stdout.is_empty());
        assert_eq!(
            String::from_utf8(output.stderr).unwrap(),
            format!(
                "Interrupted: provider stopped; temporary prompt removed; session {id} preserved.\n"
            )
        );
        assert_processes_gone(&pids);
        assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
        let prompt_dir = t.join("state/prompts");
        assert_eq!(fs::read_dir(prompt_dir).unwrap().count(), 0);

        ok(run(&t, &cfg, &["exec", &id], "FINAL(x)\n"));
        assert_eq!(ok(run(&t, &cfg, &["final", &id], "")), "1");
        ok(run(&t, &cfg, &["kill", &id], ""));
        fs::remove_dir_all(t).unwrap();
    }
}

#[test]
#[cfg(unix)]
fn sigint_stops_solo_provider_without_retry_and_cleans_prompt() {
    for prompt_file in [false, true] {
        let t = temp(if prompt_file {
            "interrupt-solo-prompt-file"
        } else {
            "interrupt-solo-stdin"
        });
        let calls = t.join("calls");
        let pids = t.join("pids");
        let provider = t.join("provider.py");
        fs::write(
            &provider,
            r#"import os, pathlib, subprocess, sys, time
pathlib.Path(sys.argv[1]).open("a").write("call\n")
if len(sys.argv) == 4:
    assert pathlib.Path(sys.argv[3]).read_text()
else:
    assert sys.stdin.read()
child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
pathlib.Path(sys.argv[2]).write_text(f"{os.getpid()} {child.pid}")
time.sleep(60)
"#,
        )
        .unwrap();
        let command = if prompt_file {
            format!(
                "python3 {} {} {} {{prompt_file}}",
                provider.display(),
                calls.display(),
                pids.display()
            )
        } else {
            format!(
                "python3 {} {} {}",
                provider.display(),
                calls.display(),
                pids.display()
            )
        };
        let cfg = config(&t, &command, 4096, 1, 60, 4);
        let input = t.join("input.txt");
        fs::write(&input, "private solo input").unwrap();
        let mut command = Command::new(env!("CARGO_BIN_EXE_azdaja"));
        command
            .args(["solo", "summarize the input", "-f", input.to_str().unwrap()])
            .env_remove("RLM_DEPTH")
            .env("AZDAJA_HOME", t.join("state"))
            .env("AZDAJA_CONFIG", &cfg)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        let child = command.spawn().unwrap();
        wait_for_file(&pids);
        let interrupted_at = Instant::now();
        assert_eq!(unsafe { libc::kill(child.id() as i32, libc::SIGINT) }, 0);
        let output = child.wait_with_output().unwrap();
        assert!(interrupted_at.elapsed() < Duration::from_secs(1));
        assert_eq!(output.status.code(), Some(130));
        assert!(output.stdout.is_empty());
        assert_eq!(
            String::from_utf8(output.stderr).unwrap(),
            "Interrupted: provider stopped; temporary prompt removed.\n"
        );
        assert_processes_gone(&pids);
        assert_eq!(fs::read_to_string(&calls).unwrap().lines().count(), 1);
        let prompt_dir = t.join("state/prompts");
        if prompt_dir.exists() {
            assert_eq!(fs::read_dir(prompt_dir).unwrap().count(), 0);
        }
        fs::remove_dir_all(t).unwrap();
    }
}

#[test]
fn claude_hook_worker_errors_fail_open_for_interactive_events() {
    let root = temp("claude-hook-fail-open");
    let blocked_state = root.join("state-is-a-file");
    fs::write(&blocked_state, b"not a directory").unwrap();
    let invoke = |event: serde_json::Value| {
        let mut child = Command::new(env!("CARGO_BIN_EXE_azdaja"));
        child
            .arg("claude-hook")
            .env("AZDAJA_HOME", &blocked_state)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        let mut child = child.spawn().unwrap();
        child
            .stdin
            .take()
            .unwrap()
            .write_all(event.to_string().as_bytes())
            .unwrap();
        child.wait_with_output().unwrap()
    };
    let base = serde_json::json!({
        "session_id": "fail-open-session",
        "cwd": root,
        "tool_input": {}
    });

    let mut prompt = base.clone();
    prompt["hook_event_name"] = serde_json::json!("UserPromptSubmit");
    prompt["user_prompt"] = serde_json::json!("Classify every record in the full input.");
    let output = invoke(prompt);
    assert!(output.status.success(), "{:?}", output);
    assert!(output.stdout.is_empty());

    let mut pretool = base.clone();
    pretool["hook_event_name"] = serde_json::json!("PreToolUse");
    pretool["tool_name"] = serde_json::json!("Read");
    let output = invoke(pretool);
    assert!(output.status.success(), "{:?}", output);
    assert!(output.stdout.is_empty());

    let mut posttool = base;
    posttool["hook_event_name"] = serde_json::json!("PostToolUse");
    posttool["tool_name"] = serde_json::json!("Skill");
    posttool["tool_input"] = serde_json::json!({"skill": "azdaja"});
    let output = invoke(posttool);
    assert!(output.status.success(), "{:?}", output);
    assert!(output.stdout.is_empty());
    assert!(blocked_state.is_file());
    fs::remove_dir_all(root).unwrap();
}
#[test]
fn solo_projected_manifest_rejects_invalid_capability_paths_before_children() {
    let t = temp("solo-projected-negative-paths");
    let marker = t.join("unexpected-child");
    let mock = t.join("projection_negative.py");
    fs::write(
        &mock,
        format!(
            r#"import os,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    if 'case-cropped' in p:
        code='ledger=exact_line_ledger(ctx[:-1],"Row: ")'
    elif 'case-synthetic' in p:
        code='ledger=exact_line_ledger("Row: meta=0 target=alpha\\n","Row: ")'
    elif 'case-duplicate-id' in p:
        code='''ledger=exact_line_ledger(ctx,"Row: ")
semantic_manifest(ledger,["O0","O0"]," target=","task",["a","b"])'''
    elif 'case-wrapper-arity' in p:
        code='''ledger=exact_line_ledger(ctx,"Row: ")
semantic_manifest(ledger,["O0"]," target=","task")'''
    elif 'case-second-ledger' in p:
        code='''exact_line_ledger(ctx,"Row: ")
exact_line_ledger(ctx,"Row: ")'''
    elif 'case-private' in p:
        code='_az_project_selected(None,[],"x")'
    elif 'case-shadow' in p:
        code='semantic_manifest = semantic_manifest_records'
    else:
        raise AssertionError('missing case')
    print('```python\n'+code+'\n```')
else:
    with open({marker:?},'a') as f:f.write('child\n')
    print('unexpected')
"#,
            marker = marker,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 2, 2);
    let input = t.join("input.txt");
    fs::write(
        &input,
        concat!(
            "Each record is classified as a or b solely from its final target field.\n",
            "Row: meta=0 target=alpha\n",
            "Row: meta=1 target=beta\n",
        ),
    )
    .unwrap();
    for case in [
        "case-cropped",
        "case-synthetic",
        "case-duplicate-id",
        "case-wrapper-arity",
        "case-second-ledger",
        "case-private",
        "case-shadow",
    ] {
        let output = run(&t, &cfg, &["solo", case, "-f", input.to_str().unwrap()], "");
        assert!(
            !output.status.success(),
            "case={case} stdout={} stderr={}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
        assert!(!marker.exists(), "case={case}");
    }
    fs::remove_dir_all(t).unwrap();
}

#[test]
fn solo_cross_field_labels_keep_complete_records_and_emit_no_projection_provenance() {
    let t = temp("solo-cross-field-no-projection");
    let marker = t.join("evidence");
    let mock = t.join("cross_field.py");
    fs::write(
        &mock,
        format!(
            r#"import json,os,re,sys
p=sys.stdin.read()
if os.getenv('RLM_DEPTH') == '0':
    code='''records=exact_line_records(ctx,"Row: ")
items=[]
i=0
for record in records:
    items.append({{"id":"r"+str(i),"evidence":record}})
    i+=1
labels=["allow","deny"]
manifest=semantic_manifest_records(items,"Classify each complete record as allow or deny using its User field; the repeated final Message field alone is insufficient.",labels)
counts={{"allow":0,"deny":0}}
for item in items:
    value=manifest[item["id"]]
    counts[value]=counts[value]+1
FINAL("Answer: "+str(counts["allow"]))'''
    print('```python\n'+code+'\n```')
else:
    prefix=re.search(r'return only (AZM1-[ABJ]-[0-9]+-([0-9]+)-[0-9]+:) followed',p).group(1)
    contract=p.rsplit('no whitespace, prose, markdown, omission, or extra character.\n',1)[1]
    rows=re.findall(r'(?m)^[0-9a-zA-Z]+\t(".*")$',contract)
    legend={{}}
    legend_part=p.split('LABEL CODES',1)[1].split('ROWS are',1)[0]
    for code,label_json in re.findall(r'(?m)^([0-9a-zA-Z]+)\t(".*")$',legend_part):
        legend[json.loads(label_json)]=code
    out=''
    with open({marker:?},'a') as f:
        for evidence_json in rows:
            evidence=json.loads(evidence_json)
            assert 'User: ' in evidence and ' || Message: repeated' in evidence
            f.write(evidence+'\n')
            out+=legend['allow' if 'User: privileged' in evidence else 'deny']
    print(prefix+out)
"#,
            marker = marker,
        ),
    )
    .unwrap();
    let cfg = config(&t, &format!("python3 {}", mock.display()), 4096, 1, 3, 4);
    let input = t.join("input.txt");
    fs::write(
        &input,
        concat!(
            "Each complete record is classified as 'allow' or 'deny'. The label depends on User; Message alone is insufficient.\n",
            "Row: User: privileged || Message: repeated\n",
            "Row: User: ordinary || Message: repeated\n",
            "Row: User: privileged || Message: repeated\n",
            "Row: User: ordinary || Message: repeated\n",
        ),
    )
    .unwrap();
    let trace_path = t.join("solo.trace");
    let output = run_with_solo_trace(
        &t,
        &cfg,
        &[
            "solo",
            "How many complete records should be classified as allow? Give Answer: number.",
            "-f",
            input.to_str().unwrap(),
        ],
        "",
        &trace_path,
    );
    assert!(
        output.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    assert_eq!(String::from_utf8_lossy(&output.stdout).trim(), "Answer: 2");
    assert_eq!(fs::read_to_string(marker).unwrap().lines().count(), 4);
    let trace = fs::read_to_string(trace_path).unwrap();
    let runtime: serde_json::Value = trace
        .lines()
        .find_map(|line| serde_json::from_str(line).ok())
        .unwrap();
    assert!(runtime["projection_ledger_calls"].is_null());
    assert!(runtime["projection_calls"].is_null());
    assert!(runtime["projection_ledger_occurrences"].is_null());
    assert!(runtime["projection_expanded_outputs"].is_null());
    fs::remove_dir_all(t).unwrap();
}
