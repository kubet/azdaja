use std::{
    fs,
    io::Write,
    path::{Path, PathBuf},
    process::{Command, Output, Stdio},
    time::{SystemTime, UNIX_EPOCH},
};
fn temp() -> PathBuf {
    let p = std::env::temp_dir().join(format!(
        "azdaja-compat-{}-{}",
        std::process::id(),
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos()
    ));
    fs::create_dir_all(&p).unwrap();
    p
}
fn run(home: &Path, cfg: &Path, args: &[&str], input: &str) -> Output {
    let mut c = Command::new(env!("CARGO_BIN_EXE_azdaja"));
    let mut child = c
        .args(args)
        .env("AZDAJA_HOME", home.join("state"))
        .env("AZDAJA_CONFIG", cfg)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(input.as_bytes())
        .unwrap();
    child.wait_with_output().unwrap()
}
#[test]
fn rlm_idioms_and_regex_flavor_execute_unmodified() {
    let t = temp();
    let cfg = t.join("config.toml");
    fs::write(
        &cfg,
        r#"sub_llm_cmd="cat"
default_model="mock"
output_cap=8192
max_depth=1
sub_timeout=2
max_sessions=2
cell_timeout=5
idle_timeout=1800
clean_patterns=[]
jcode_provider="openai"
jcode_reasoning="medium"
max_calls_per_cell=64
"#,
    )
    .unwrap();
    let s = run(&t, &cfg, &["start"], "");
    assert!(s.status.success());
    let id = String::from_utf8(s.stdout).unwrap().trim().to_string();
    let code = r#"
# slicing/peeking, loops, accumulators, comprehensions
text = "alpha=12 beta=34 alpha=56"
peek = text[:8]
acc = {}
for word in text.split():
    key = word.split("=")[0]
    acc[key] = acc.get(key, 0) + 1
assert acc == {"alpha": 2, "beta": 1}
assert [x*x for x in range(4)] == [0, 1, 4, 9]
# sorting, nested functions, f-strings
def outer(scale):
    def inner(x): return x * scale
    return inner
assert sorted([3, 1, 2], key=lambda x: -x) == [3, 2, 1]
mapping = {"low": 2, "high": 9, "middle": 4}
assert max(mapping, key=lambda k: mapping[k]) == "high"
matched = False
predicate_count = 0
for word in text.split():
    if word == "beta=34":
        matched = True
    if word.startswith("alpha="):
        predicate_count += 1
assert matched
assert predicate_count == 2
bounded_matches = []
for match in re.finditer(r"\d+", text):
    bounded_matches.append(match.group(0))
    if len(bounded_matches) >= 2:
        break
assert bounded_matches == ["12", "34"]
ranking_words = re.findall(r"[a-z]+", "red blue red green blue red")
ranking_counts = collections.Counter(ranking_words)
ranking_top = ranking_counts.most_common(2)
ranking_answer = ", ".join([item[0] for item in ranking_top])
assert ranking_answer == "red, blue"
assert f"v={outer(2)(4)}" == "v=8"
# json/datetime
obj = json.loads('{"b": 2, "a": [1, null]}')
assert json.loads(json.dumps(obj))["a"][1] is None
assert datetime.date(2026, 8, 12).isoformat() == "2026-08-12"
# regex flavor probes
assert re.findall(r"\d+(?= beta)", text) == ["12"]
assert re.findall(r"(?<=alpha=)\d+", text) == ["12", "56"]
assert re.findall(r"(\w+) \1", "go go stop") == ["go"]
assert [m.group(0) for m in re.finditer(r"\d+", text)] == ["12", "34", "56"]
assert re.findall(r"(?i)ALPHA", text) == ["alpha", "alpha"]
# host error is a catchable Python error
caught = False
try:
    llm(123)
except RuntimeError:
    caught = True
assert caught
answer = {"peek": peek, "counts": acc, "regex": 5}
FINAL_VAR("answer")
"#;
    let o = run(&t, &cfg, &["exec", &id], code);
    assert!(
        o.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&o.stdout),
        String::from_utf8_lossy(&o.stderr)
    );
    let f = run(&t, &cfg, &["final", &id], "");
    assert!(f.status.success());
    let out = String::from_utf8(f.stdout).unwrap();
    assert!(out.contains("'regex': 5") && out.contains("'alpha': 2"));
    run(&t, &cfg, &["kill", &id], "");
    fs::remove_dir_all(t).unwrap();
}
