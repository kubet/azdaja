use anyhow::{Context, Result, anyhow, bail};
use azdaja::{
    Config, DEFAULT_CONFIG, MONTY_VERSION, SKILL, VERSION, call_model, capability_check, exec,
    final_answer, kill, list, load, start,
};
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::{
    env, fs,
    io::{self, Read},
    path::{Path, PathBuf},
    process::ExitCode,
};

const CANARY_PROMPT: &str = "Reverse the six-letter ASCII string AJADZA. Reply with the reversed string only, no punctuation.";
const CANARY_ANSWER: &str = "AZDAJA";

fn help() {
    println!(
        "azdaja {VERSION}\n\nUSAGE:\n  azdaja start\n  azdaja load <sid> <path> <var>\n  azdaja exec <sid>             # Python on stdin\n  azdaja final <sid>\n  azdaja list | kill <sid>\n  azdaja solo <question> -f <file> [--model X] [--sub-model Y]\n  azdaja install [--harness jcode|claude|codex|gemini|opencode|all]\n  azdaja doctor [--caps]\n  azdaja uninstall [--harness ...]"
    );
}
fn main() -> ExitCode {
    match run() {
        Ok(ok) => {
            if ok {
                ExitCode::SUCCESS
            } else {
                ExitCode::from(1)
            }
        }
        Err(e) => {
            eprintln!("error: {e:#}");
            ExitCode::from(2)
        }
    }
}
fn run() -> Result<bool> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.is_empty() || matches!(args[0].as_str(), "-h" | "--help") {
        help();
        return Ok(true);
    }
    if args[0] == "--version" {
        println!("azdaja {VERSION} (monty {MONTY_VERSION})");
        return Ok(true);
    }
    match args[0].as_str() {
        "start" => {
            exact(&args, 1)?;
            println!("{}", start(&Config::load()?, None)?)
        }
        "load" => {
            exact(&args, 4)?;
            println!(
                "{}",
                load(&args[1], Path::new(&args[2]), &args[3], &Config::load()?)?
            )
        }
        "exec" => {
            exact(&args, 2)?;
            let mut code = String::new();
            io::stdin().read_to_string(&mut code)?;
            let r = exec(&args[1], &code, &Config::load()?)?;
            print!("{}", r.output);
            return Ok(r.success);
        }
        "final" => {
            exact(&args, 2)?;
            print!("{}", final_answer(&args[1], &Config::load()?)?)
        }
        "list" => {
            exact(&args, 1)?;
            for id in list(&Config::load()?)? {
                println!("{id}")
            }
        }
        "kill" => {
            exact(&args, 2)?;
            kill(&args[1])?;
            println!("killed {}", args[1])
        }
        "doctor" => doctor(&args)?,
        "install" => install_cmd(&args, false)?,
        "uninstall" => install_cmd(&args, true)?,
        "solo" => solo(&args, &Config::load()?)?,
        x => bail!("unknown command '{x}' (run --help)"),
    }
    Ok(true)
}
fn exact(args: &[String], n: usize) -> Result<()> {
    if args.len() != n {
        bail!("wrong number of arguments (run --help)")
    }
    Ok(())
}
fn doctor(args: &[String]) -> Result<()> {
    if args.get(1).is_some_and(|s| s == "--caps") {
        exact(args, 2)?;
        println!(
            "{}",
            serde_json::json!({"azdaja":VERSION,"monty":MONTY_VERSION,"dump_version":monty::DUMP_VERSION,"capabilities":["persistent-repl","snapshots","external-functions","re","json","datetime","monty-os-calls-denied"]})
        );
        return Ok(());
    }
    exact(args, 1)?;
    let cfg = Config::load()?;
    capability_check(&cfg)?;
    let reply = call_model(CANARY_PROMPT, &cfg.default_model, &cfg, 1)?;
    if reply.trim() != CANARY_ANSWER {
        bail!("sub_llm_cmd canary mismatch: {reply}")
    }
    println!("ok: azdaja {VERSION}, monty {MONTY_VERSION}, sub-LLM reachable");
    Ok(())
}

fn harness_arg(args: &[String]) -> Result<String> {
    match args {
        [_] => Ok("detected".into()),
        [_, flag, h] if flag == "--harness" => Ok(h.clone()),
        _ => bail!("usage: {} [--harness NAME]", args[0]),
    }
}
fn harnesses(which: &str) -> Result<Vec<&'static str>> {
    let all = ["jcode", "claude", "codex", "gemini", "opencode"];
    if which == "all" {
        return Ok(all.into());
    }
    if which == "detected" {
        let home = home()?;
        let v = all
            .into_iter()
            .filter(|h| target(&home, h).parent().is_some_and(Path::exists))
            .collect::<Vec<_>>();
        return if v.is_empty() {
            Ok(vec!["jcode"])
        } else {
            Ok(v)
        };
    }
    all.into_iter()
        .find(|h| *h == which)
        .map(|h| vec![h])
        .ok_or_else(|| anyhow!("unknown harness '{which}'"))
}
fn home() -> Result<PathBuf> {
    env::var_os("HOME")
        .or_else(|| env::var_os("USERPROFILE"))
        .map(PathBuf::from)
        .ok_or_else(|| anyhow!("no home directory"))
}
fn target(home: &Path, h: &str) -> PathBuf {
    match h {
        "jcode" => home.join(".jcode/skills/azdaja"),
        "claude" => home.join(".claude/skills/azdaja"),
        "codex" => home.join(".agents/skills/azdaja"),
        "gemini" => home.join(".gemini/skills/azdaja"),
        _ => home.join(".config/opencode/skills/azdaja"),
    }
}
fn adapter(h: &str) -> (&'static str, &'static str) {
    match h {
        "claude" => ("claude -p --model {model}", "haiku"),
        "codex" => (
            "codex exec --ephemeral --skip-git-repo-check --model {model} -",
            "gpt-5.4-mini",
        ),
        "gemini" => ("gemini --model {model} -p \"\"", "gemini-2.5-flash"),
        "opencode" => ("opencode --pure run --model {model}", "openai/gpt-5.4-mini"),
        _ => (
            "jcode run --no-update --quiet --model {model} Read_the_complete_UTF-8_prompt_at_{prompt_file}_and_return_only_its_answer",
            "claude-haiku-4-5",
        ),
    }
}
#[derive(Serialize, Deserialize)]
struct Manifest {
    files: Vec<(String, u64)>,
}
fn hash(b: &[u8]) -> u64 {
    let mut h = 0xcbf29ce484222325u64;
    for x in b {
        h ^= u64::from(*x);
        h = h.wrapping_mul(0x100000001b3)
    }
    h
}
fn install_cmd(args: &[String], remove: bool) -> Result<()> {
    let hs = harnesses(&harness_arg(args)?)?;
    let home = home()?;
    if remove {
        for h in hs {
            uninstall(&target(&home, h), false)?
        }
        return Ok(());
    }
    let exe = env::current_exe()?.canonicalize()?;
    for h in hs {
        let dst = target(&home, h);
        let (cmd, model) = adapter(h);
        let preserved = if dst.exists() {
            validate_install(&dst, true)?;
            Some(fs::read(dst.join("config.toml"))?)
        } else {
            None
        };
        let cfg = if let Some(bytes) = &preserved {
            toml::from_str::<Config>(&String::from_utf8(bytes.clone())?)?.validate()?
        } else {
            let mut c: Config = toml::from_str(DEFAULT_CONFIG)?;
            c.sub_llm_cmd = cmd.into();
            c.default_model = model.into();
            c.validate()?
        };
        let model = cfg.default_model.as_str();
        capability_check(&cfg)?;
        let reply = call_model(CANARY_PROMPT, model, &cfg, 1)
            .with_context(|| format!("{h} adapter verification failed"))?;
        if reply.trim() != CANARY_ANSWER {
            bail!("{h} adapter canary mismatch")
        }
        let parent = dst.parent().unwrap();
        fs::create_dir_all(parent)?;
        let stage = parent.join(format!(".azdaja-stage-{}", std::process::id()));
        if stage.exists() {
            fs::remove_dir_all(&stage)?
        }
        fs::create_dir(&stage)?;
        let bin = stage.join(if cfg!(windows) {
            "azdaja.exe"
        } else {
            "azdaja"
        });
        fs::copy(&exe, &bin)?;
        executable(&bin)?;
        let final_bin = dst.join(bin.file_name().unwrap());
        let skill = SKILL
            .replace("{{VERSION}}", VERSION)
            .replace("{{BIN}}", &shell_quote(&final_bin));
        fs::write(stage.join("SKILL.md"), skill)?;
        fs::write(
            stage.join("config.toml"),
            preserved.unwrap_or(toml::to_string_pretty(&cfg)?.into_bytes()),
        )?;
        let files = [
            bin.file_name().unwrap().to_string_lossy().into_owned(),
            "SKILL.md".into(),
            "config.toml".into(),
        ];
        let manifest = Manifest {
            files: files
                .iter()
                .map(|n| (n.clone(), hash(&fs::read(stage.join(n)).unwrap())))
                .collect(),
        };
        fs::write(
            stage.join(".azdaja-managed"),
            serde_json::to_vec(&manifest)?,
        )?;
        if dst.exists() {
            let backup = parent.join(format!(".azdaja-backup-{}", std::process::id()));
            if backup.exists() {
                fs::remove_dir_all(&backup)?
            }
            fs::rename(&dst, &backup)?;
            if let Err(e) = fs::rename(&stage, &dst) {
                let _ = fs::rename(&backup, &dst);
                return Err(e.into());
            }
            fs::remove_dir_all(backup)?
        } else {
            fs::rename(&stage, &dst)?
        }
        println!("installed {h}: {}", dst.display());
    }
    Ok(())
}
#[cfg(unix)]
fn executable(p: &Path) -> Result<()> {
    use std::os::unix::fs::PermissionsExt;
    fs::set_permissions(p, fs::Permissions::from_mode(0o755))?;
    Ok(())
}
#[cfg(not(unix))]
fn executable(_: &Path) -> Result<()> {
    Ok(())
}
fn shell_quote(p: &Path) -> String {
    let s = p.to_string_lossy();
    format!("'{}'", s.replace('\'', "'\\''"))
}
fn validate_install(dst: &Path, allow_config_change: bool) -> Result<()> {
    let manifest: Manifest = serde_json::from_slice(
        &fs::read(dst.join(".azdaja-managed"))
            .context("refusing to modify unowned skill directory")?,
    )?;
    for (n, want) in &manifest.files {
        let p = dst.join(n);
        let got =
            hash(&fs::read(&p).with_context(|| format!("managed file missing: {}", p.display()))?);
        if got != *want && !(allow_config_change && n == "config.toml") {
            bail!("refusing to modify changed file: {}", p.display())
        }
    }
    if fs::read_dir(dst)?.count() != manifest.files.len() + 1 {
        bail!(
            "refusing to modify directory with unknown files: {}",
            dst.display()
        )
    }
    Ok(())
}
fn uninstall(dst: &Path, allow_config_change: bool) -> Result<()> {
    if !dst.exists() {
        println!("not installed: {}", dst.display());
        return Ok(());
    }
    validate_install(dst, allow_config_change)?;
    fs::remove_dir_all(dst)?;
    println!("uninstalled {}", dst.display());
    Ok(())
}

fn solo(args: &[String], cfg: &Config) -> Result<()> {
    if args.len() < 4 {
        bail!("usage: solo <question> -f <file> [--model X] [--sub-model Y]")
    }
    let question = &args[1];
    let mut file = None;
    let mut model = None;
    let mut sub = None;
    let mut i = 2;
    while i < args.len() {
        let v = args
            .get(i + 1)
            .ok_or_else(|| anyhow!("missing value for {}", args[i]))?
            .clone();
        match args[i].as_str() {
            "-f" => file = Some(v),
            "--model" => model = Some(v),
            "--sub-model" => sub = Some(v),
            x => bail!("unknown solo option {x}"),
        }
        i += 2
    }
    let file = PathBuf::from(file.ok_or_else(|| anyhow!("solo requires -f"))?);
    let sid = start(cfg, sub)?;
    let result = (|| {
        let metadata = load(&sid, &file, "ctx", cfg)?;
        let root_model = model.as_deref().unwrap_or(&cfg.default_model);
        let mut prompt = format!(
            "You are the root of a recursive language model. The raw input is stored only as variable ctx in a persistent Python session; you see metadata only. Question: {question}\n{metadata}\nReturn exactly one fenced Python cell. Use ordinary Python, llm/llm_batch, and finish with FINAL or FINAL_VAR. Never ask for the raw file."
        );
        let fence = Regex::new(r"(?s)```(?:python)?\s*(.*?)```").unwrap();
        let max_turns = env::var("AZDAJA_SOLO_MAX_TURNS")
            .ok()
            .and_then(|v| v.parse::<usize>().ok())
            .unwrap_or(12)
            .clamp(1, 24);
        let trace = env::var_os("AZDAJA_SOLO_TRACE").map(PathBuf::from);
        for turn in 0..max_turns {
            let reply = call_model(&prompt, root_model, cfg, 0)?;
            if let Some(path) = &trace {
                use std::io::Write;
                let mut f = fs::OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(path)?;
                writeln!(f, "\n=== turn {turn} reply ===\n{reply}")?;
            }
            let code = fence
                .captures(&reply)
                .map(|c| c[1].to_owned())
                .unwrap_or(reply);
            let r = exec(&sid, &code, cfg)?;
            if let Some(path) = &trace {
                use std::io::Write;
                let mut f = fs::OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(path)?;
                writeln!(f, "=== code ===\n{code}\n=== result ===\n{}", r.output)?;
            }
            if r.finalized {
                return final_answer(&sid, cfg);
            }
            prompt.push_str(&format!("\n\nYour cell:\n```python\n{code}\n```\nCapped result:\n{}\nReturn the next fenced Python cell; finish with FINAL.",r.output));
        }
        bail!("solo exceeded {max_turns} root turns")
    })();
    let _ = kill(&sid);
    println!("{}", result?);
    Ok(())
}
