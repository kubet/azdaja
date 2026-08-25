use azdaja::{
    DashboardSnapshot, RecentScopeStatus, SessionStatus,
    observability::{MemoryConstellation, RecentRunAggregate, RunKind},
};
use std::time::{SystemTime, UNIX_EPOCH};

const RED: &str = "\x1b[31m";
const GREEN: &str = "\x1b[32m";
const CYAN: &str = "\x1b[36m";
const DIM: &str = "\x1b[2m";
const BOLD: &str = "\x1b[1m";
const RESET: &str = "\x1b[0m";

pub fn terminal_width() -> usize {
    if let Ok(columns) = std::env::var("COLUMNS")
        && let Ok(columns) = columns.parse::<usize>()
        && columns > 0
    {
        return columns;
    }
    #[cfg(unix)]
    {
        let mut size: libc::winsize = unsafe { std::mem::zeroed() };
        if unsafe { libc::ioctl(libc::STDOUT_FILENO, libc::TIOCGWINSZ, &mut size) } == 0
            && size.ws_col > 0
        {
            return usize::from(size.ws_col);
        }
    }
    72
}

fn now() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
}

fn clean(value: &str) -> String {
    value
        .chars()
        .filter_map(|character| {
            if character == '\t' {
                Some(' ')
            } else if character.is_control() {
                None
            } else {
                Some(character)
            }
        })
        .collect()
}

fn truncate(value: &str, width: usize) -> String {
    if value.chars().count() <= width {
        return value.to_owned();
    }
    if width <= 1 {
        return "…".chars().take(width).collect();
    }
    let mut output = value.chars().take(width - 1).collect::<String>();
    output.push('…');
    output
}

fn paint(enabled: bool, style: &str, value: &str) -> String {
    if enabled {
        format!("{style}{value}{RESET}")
    } else {
        value.to_owned()
    }
}

fn top_border(total: usize, title: &str, color: bool) -> String {
    let title = format!(" {title} ");
    let fill = total.saturating_sub(title.chars().count() + 3);
    format!(
        "╭─{}{}╮\n",
        paint(color, BOLD, &paint(color, CYAN, &title)),
        "─".repeat(fill)
    )
}

fn bottom_border(total: usize) -> String {
    format!("╰{}╯\n", "─".repeat(total.saturating_sub(2)))
}

fn row(total: usize, label: &str, value: &str, value_style: &str, color: bool) -> String {
    let capacity = total.saturating_sub(4);
    let label_width = 9.min(capacity);
    let value_width = capacity.saturating_sub(label_width);
    let label = truncate(&clean(label), label_width);
    let value = truncate(&clean(value), value_width);
    let plain_width = label_width + value.chars().count();
    let padding = capacity.saturating_sub(plain_width);
    format!(
        "│ {}{}{} │\n",
        paint(color, DIM, &format!("{label:<label_width$}")),
        paint(color, value_style, &value),
        " ".repeat(padding),
    )
}

fn human_bytes(bytes: u64) -> String {
    const KIB: u64 = 1024;
    const MIB: u64 = 1024 * KIB;
    const GIB: u64 = 1024 * MIB;
    if bytes >= GIB {
        format!("{:.1} GiB", bytes as f64 / GIB as f64)
    } else if bytes >= MIB {
        format!("{:.1} MiB", bytes as f64 / MIB as f64)
    } else if bytes >= KIB {
        format!("{:.1} KiB", bytes as f64 / KIB as f64)
    } else {
        format!("{bytes} B")
    }
}

fn human_duration(seconds: u64) -> String {
    match seconds {
        0..=59 => format!("{seconds}s"),
        60..=3599 => format!("{}m", seconds / 60),
        3600..=86_399 => format!("{}h", seconds / 3600),
        _ => format!("{}d", seconds / 86_400),
    }
}

fn active_sessions(snapshot: &DashboardSnapshot) -> usize {
    snapshot
        .sessions
        .iter()
        .filter(|session| session.busy)
        .count()
}

fn status_line(snapshot: &DashboardSnapshot) -> (&'static str, &'static str) {
    if snapshot.observability_degraded {
        ("● awake · local metrics need attention", RED)
    } else {
        ("● awake · source stays local", GREEN)
    }
}

fn scope_line(snapshot: &DashboardSnapshot) -> String {
    clean(&snapshot.scope)
}

fn memory_constellation(snapshot: &DashboardSnapshot) -> Option<MemoryConstellation> {
    let mut summary = snapshot.recent_observability.clone();
    for session in snapshot.sessions.iter().rev() {
        if session.loaded_sources > session.completed_sources
            && let Some(source) = session.source.as_ref()
        {
            summary.runs.insert(
                0,
                RecentRunAggregate {
                    kind: RunKind::SessionLoad,
                    observed_unix: session.updated,
                    source: source.clone(),
                },
            );
        }
    }
    summary.runs.truncate(summary.max_recent_runs);
    summary.compact_memory_constellation()
}

fn percent(millipercent: u16) -> u32 {
    (u32::from(millipercent.min(1000)) * 100 + 500) / 1000
}

fn new_work_line(snapshot: &DashboardSnapshot) -> String {
    let model = clean(snapshot.default_model.trim());
    let model = if model.is_empty() {
        "model unknown".to_owned()
    } else {
        model
    };
    let provider = clean(snapshot.provider.trim());
    let provider = if provider.is_empty() {
        "provider unknown".to_owned()
    } else {
        provider
    };
    let mut line = format!("{model} via {provider}");
    let reasoning = clean(snapshot.reasoning.trim());
    match reasoning.to_ascii_lowercase().as_str() {
        "" | "unknown" => {}
        "none" | "off" => line.push_str(" · thinking off"),
        _ => line.push_str(&format!(" · {reasoning} thinking")),
    }
    line
}

fn live_line(snapshot: &DashboardSnapshot) -> String {
    let used = snapshot.sessions.len();
    if used == 0 {
        let free = snapshot.max_sessions;
        return format!(
            "none · {free} {} free",
            if free == 1 { "slot" } else { "slots" }
        );
    }
    let running = active_sessions(snapshot);
    let idle = used.saturating_sub(running);
    format!(
        "{running} running · {idle} idle · {used}/{} slots used",
        snapshot.max_sessions
    )
}

fn summary_count(count: usize) -> String {
    format!(
        "{count} source {}",
        if count == 1 { "summary" } else { "summaries" }
    )
}

fn memory_line(snapshot: &DashboardSnapshot) -> String {
    match memory_constellation(snapshot) {
        Some(constellation) => {
            format!(
                "{} · {} measured · numbers only",
                summary_count(constellation.trace_count),
                human_bytes(constellation.total_source_bytes)
            )
        }
        None => "none yet · summaries keep numbers, not source text".to_owned(),
    }
}

fn variety_percent_from_entropy(byte_entropy_millibits: u16) -> u32 {
    (u32::from(byte_entropy_millibits.min(8000)) * 100 + 4000) / 8000
}

fn pattern_line(snapshot: &DashboardSnapshot, strip_width: usize) -> String {
    match memory_constellation(snapshot) {
        Some(constellation) => format!(
            "repeated ← {} → varied · avg variety {}%",
            constellation.render_strip(strip_width),
            100 - percent(constellation.zero_order_redundancy_millipercent())
        ),
        None => "appears after the first source".to_owned(),
    }
}

fn run_kind_label(kind: RunKind) -> &'static str {
    match kind {
        RunKind::SessionLoad | RunKind::SoloLoad => "loaded",
        RunKind::SessionFinal | RunKind::SoloFinal => "finished",
    }
}

fn recent_summary_line(snapshot: &DashboardSnapshot, timestamp: u64) -> Option<String> {
    let run = snapshot.recent_observability.runs.first()?;
    let kind = run_kind_label(run.kind);
    Some(format!(
        "{kind} · {} · {} lines · {} ago",
        human_bytes(run.source.source_bytes),
        run.source.physical_lines,
        human_duration(timestamp.saturating_sub(run.observed_unix))
    ))
}

fn recent_scope_line(scope: &RecentScopeStatus, timestamp: u64) -> String {
    let memories = if scope.memory_records == 1 {
        "memory"
    } else {
        "memories"
    };
    let summaries = if scope.source_summaries == 1 {
        "source summary"
    } else {
        "source summaries"
    };
    format!(
        "{} · {} {memories} · {} {summaries} · {} ago",
        clean(&scope.token),
        scope.memory_records,
        scope.source_summaries,
        human_duration(timestamp.saturating_sub(scope.updated_unix))
    )
}

fn session_line(session: &SessionStatus, timestamp: u64) -> String {
    let marker = if session.busy { "●" } else { "○" };
    let state = if session.busy { "running" } else { "idle" };
    let model = session.sub_model.as_deref().map_or_else(
        || "default model unknown".to_owned(),
        |model| format!("default {}", clean(model)),
    );
    format!(
        "{marker} {} {state} {} · {}",
        clean(&session.id[..session.id.len().min(8)]),
        human_duration(timestamp.saturating_sub(session.updated)),
        model
    )
}

fn render_compact(
    snapshot: &DashboardSnapshot,
    color: bool,
    timestamp: u64,
    terminal_columns: usize,
) -> String {
    let width = terminal_columns.max(20);
    let (status, status_style) = status_line(snapshot);
    let mut output = String::new();
    output.push_str(&format!(
        "{}\n",
        paint(
            color,
            BOLD,
            &truncate("azdaja · memory constellation", width)
        )
    ));
    output.push_str(&format!(
        "{}\n",
        truncate(&format!("scope     {}", scope_line(snapshot)), width)
    ));
    output.push_str(&format!(
        "{}\n",
        paint(
            color,
            status_style,
            &truncate(&format!("status    {status}"), width)
        )
    ));
    output.push_str(&format!(
        "{}\n",
        truncate(&format!("new work  {}", new_work_line(snapshot)), width)
    ));
    output.push_str(&format!(
        "{}\n",
        truncate(&format!("live      {}", live_line(snapshot)), width)
    ));
    output.push_str(&format!(
        "{}\n",
        truncate(&format!("memory    {}", memory_line(snapshot)), width)
    ));
    output.push_str(&format!(
        "{}\n",
        truncate(&format!("pattern   {}", pattern_line(snapshot, 8)), width)
    ));
    if let Some(summary) = recent_summary_line(snapshot, timestamp) {
        output.push_str(&format!(
            "{}\n",
            truncate(&format!("recent    {summary}"), width)
        ));
    } else {
        output.push_str(&format!(
            "{}\n",
            truncate("recent    no source summary yet", width)
        ));
    }
    for scope in snapshot.recent_scopes.iter().take(3) {
        output.push_str(&format!(
            "{}\n",
            truncate(
                &format!("project   {}", recent_scope_line(scope, timestamp)),
                width
            )
        ));
    }
    for session in snapshot.sessions.iter().take(3) {
        output.push_str(&format!(
            "{}\n",
            truncate(
                &format!("session   {}", session_line(session, timestamp)),
                width
            )
        ));
    }
    output.push_str(&format!(
        "{}\n",
        truncate("next  map · list · memory · list --global · help", width)
    ));
    output
}

pub fn render(snapshot: &DashboardSnapshot, color: bool, terminal_columns: usize) -> String {
    render_at(snapshot, color, terminal_columns, now())
}

pub fn render_list(snapshot: &DashboardSnapshot, color: bool, terminal_columns: usize) -> String {
    render_list_at(snapshot, color, terminal_columns, now())
}

fn render_list_at(
    snapshot: &DashboardSnapshot,
    color: bool,
    terminal_columns: usize,
    timestamp: u64,
) -> String {
    let width = terminal_columns.max(20);
    let mut output = format!(
        "{}\n{}\n{}\n{}\n\n",
        paint(
            color,
            BOLD,
            &truncate("azdaja · memory constellation", width)
        ),
        truncate(&format!("scope         {}", scope_line(snapshot)), width),
        truncate(&format!("new work      {}", new_work_line(snapshot)), width),
        truncate(&format!("live sessions  {}", live_line(snapshot)), width)
    );

    output.push_str("live sessions\n");
    if snapshot.sessions.is_empty() {
        output.push_str("none\n");
    } else {
        for session in &snapshot.sessions {
            let marker = if session.busy { "●" } else { "○" };
            let state = if session.busy { "running" } else { "idle" };
            let age = human_duration(timestamp.saturating_sub(session.updated));
            let model = session.sub_model.as_deref().map_or_else(
                || "default model unknown".to_owned(),
                |model| format!("default {}", clean(model)),
            );
            let id = clean(&session.id);
            let style = if session.busy { GREEN } else { "" };
            if width < 64 {
                let identity = truncate(&format!("{marker} {id} {state} {age}"), width);
                let details = truncate(
                    &format!("  {} state · {model}", human_bytes(session.state_bytes)),
                    width,
                );
                output.push_str(&format!("{}\n{details}\n", paint(color, style, &identity)));
            } else {
                let line = truncate(
                    &format!(
                        "{marker} {id:<16}  {state:<7} {age:>4}  {:>9}  {model}",
                        human_bytes(session.state_bytes)
                    ),
                    width,
                );
                output.push_str(&format!("{}\n", paint(color, style, &line)));
            }
        }
    }

    output.push_str("\nsource summaries · local numbers only\n");
    if snapshot.recent_observability.runs.is_empty() {
        output.push_str("none yet\n");
    } else {
        for (index, run) in snapshot.recent_observability.runs.iter().enumerate() {
            let marker = if index == 0 { "●" } else { "○" };
            let age = human_duration(timestamp.saturating_sub(run.observed_unix));
            let kind = run_kind_label(run.kind);
            let variety = variety_percent_from_entropy(run.source.byte_entropy_millibits);
            let line = if width < 64 {
                format!(
                    "{marker} {kind} {age} · {} · variety {variety}%",
                    human_bytes(run.source.source_bytes),
                )
            } else {
                format!(
                    "{marker} {kind:<8} {age:>4}  {:>9}  {:>6} lines  variety {variety}%",
                    human_bytes(run.source.source_bytes),
                    run.source.physical_lines,
                )
            };
            output.push_str(&format!("{}\n", truncate(&line, width)));
        }
    }
    if snapshot.observability_degraded {
        output.push_str(&format!(
            "\n{}\n",
            paint(
                color,
                RED,
                &truncate("note  local metrics need attention", width)
            )
        ));
    }
    output.push_str(&format!(
        "\n{}\n",
        paint(
            color,
            CYAN,
            &truncate(
                if snapshot.sessions.is_empty() {
                    "next  map · start · solo · memory · list · list --global · doctor · help"
                } else {
                    "commands  final <id> · kill <id> · map · help"
                },
                width
            )
        )
    ));
    output
}

fn render_at(
    snapshot: &DashboardSnapshot,
    color: bool,
    terminal_columns: usize,
    timestamp: u64,
) -> String {
    if terminal_columns < 54 {
        return render_compact(snapshot, color, timestamp, terminal_columns);
    }
    let total = terminal_columns.clamp(58, 78);
    let (status, status_style) = status_line(snapshot);
    let mut output = top_border(total, "azdaja · memory constellation", color);
    output.push_str(&row(total, "status", status, status_style, color));
    output.push_str(&row(total, "scope", &scope_line(snapshot), DIM, color));
    output.push_str(&row(
        total,
        "new work",
        &new_work_line(snapshot),
        CYAN,
        color,
    ));
    output.push_str(&row(total, "live", &live_line(snapshot), "", color));
    output.push_str(&row(total, "memory", &memory_line(snapshot), "", color));
    output.push_str(&row(
        total,
        "pattern",
        &pattern_line(snapshot, 18),
        DIM,
        color,
    ));
    output.push_str(&row(
        total,
        "recent",
        recent_summary_line(snapshot, timestamp)
            .as_deref()
            .unwrap_or("no source summary yet"),
        DIM,
        color,
    ));
    for (index, scope) in snapshot.recent_scopes.iter().take(3).enumerate() {
        output.push_str(&row(
            total,
            if index == 0 { "projects" } else { "" },
            &recent_scope_line(scope, timestamp),
            "",
            color,
        ));
    }
    for session in snapshot.sessions.iter().take(3) {
        output.push_str(&row(
            total,
            "",
            &session_line(session, timestamp),
            if session.busy { GREEN } else { "" },
            color,
        ));
    }
    output.push_str(&bottom_border(total));
    output.push_str(&format!(
        "{}  {}\n",
        paint(color, DIM, "next"),
        paint(
            color,
            CYAN,
            "map · solo \"question\" -f ./document.txt · list · list --global · doctor · help"
        )
    ));
    output
}

pub fn render_error(message: &str, color: bool, terminal_columns: usize) -> String {
    let message = clean(message);
    if terminal_columns < 54 {
        return format!(
            "{} {}\n{}\nnext  doctor · install · help\n",
            paint(color, BOLD, "azdaja"),
            paint(color, RED, "● needs attention"),
            truncate(&message, terminal_columns.max(20))
        );
    }
    let total = terminal_columns.clamp(58, 78);
    let mut output = top_border(total, "azdaja · needs attention", color);
    output.push_str(&row(total, "status", "● needs attention", RED, color));
    output.push_str(&row(total, "issue", &message, "", color));
    output.push_str(&row(
        total,
        "fix",
        "az doctor · az install · az help",
        CYAN,
        color,
    ));
    output.push_str(&bottom_border(total));
    output
}

#[cfg(test)]
mod tests {
    use super::*;
    use azdaja::observability::{
        EvidenceTier, RecentAggregateSummary, RecentRunAggregate, SourceLocalAggregate,
    };
    use std::path::PathBuf;

    fn snapshot() -> DashboardSnapshot {
        let mut recent_observability = RecentAggregateSummary::empty();
        recent_observability.updated_unix = 990;
        recent_observability.runs = vec![
            RecentRunAggregate {
                kind: RunKind::SoloFinal,
                observed_unix: 980,
                source: SourceLocalAggregate {
                    evidence_tier: EvidenceTier::ExactLocal,
                    source_bytes: 2_400_000,
                    utf8_chars: 182_000,
                    physical_lines: 9_421,
                    nonempty_lines: 8_900,
                    byte_entropy_millibits: 4_812,
                },
            },
            RecentRunAggregate {
                kind: RunKind::SessionLoad,
                observed_unix: 900,
                source: SourceLocalAggregate {
                    evidence_tier: EvidenceTier::ExactLocal,
                    source_bytes: 64_000,
                    utf8_chars: 60_000,
                    physical_lines: 1_000,
                    nonempty_lines: 800,
                    byte_entropy_millibits: 3_000,
                },
            },
        ];
        DashboardSnapshot {
            scope: "azdaja · current folder".into(),
            default_model: "gpt-5.6-sol".into(),
            provider: "Jcode/OpenAI".into(),
            reasoning: "low".into(),
            max_sessions: 4,
            idle_timeout: 1800,
            state_root: PathBuf::from("/private/state"),
            sessions: vec![
                SessionStatus {
                    id: "0123456789abcdef".into(),
                    created: 900,
                    updated: 990,
                    sub_model: None,
                    busy: true,
                    state_bytes: 1024 * 1024,
                    source: None,
                    loaded_sources: 0,
                    completed_sources: 0,
                },
                SessionStatus {
                    id: "fedcba9876543210".into(),
                    created: 800,
                    updated: 880,
                    sub_model: Some("small-model".into()),
                    busy: false,
                    state_bytes: 512 * 1024,
                    source: None,
                    loaded_sources: 0,
                    completed_sources: 0,
                },
            ],
            recent_observability,
            observability_degraded: false,
        }
    }

    fn assert_plain_language(rendered: &str) {
        let rendered_lower = rendered.to_ascii_lowercase();
        for forbidden in [
            "route", "nest", "resident", "cold", "warm", "trace", "observed",
        ] {
            assert!(
                !rendered_lower.contains(forbidden),
                "unexpected legacy term {forbidden:?} in:\n{rendered}"
            );
        }
        assert!(!rendered.contains("H₀"), "unexpected H₀ in:\n{rendered}");
    }

    #[test]
    fn wide_dashboard_shows_active_mixed_model_work_plainly() {
        let rendered = render_at(&snapshot(), false, 72, 1000);
        assert!(rendered.starts_with("╭─ azdaja · memory constellation"));
        assert!(rendered.contains("● awake · source stays local"));
        assert!(rendered.contains("new work gpt-5.6-sol via Jcode/OpenAI · low thinking"));
        assert!(rendered.contains("1 running · 1 idle · 2/4 slots used"));
        assert!(rendered.contains("2 source summaries"));
        assert!(rendered.contains("2.3 MiB measured · numbers only"));
        assert!(rendered.contains("repeated ←"));
        assert!(rendered.contains("→ varied · avg variety 60%"));
        assert!(rendered.contains("recent   finished · 2.3 MiB · 9421 lines · 20s ago"));
        assert!(rendered.contains("01234567 running 10s · default model unknown"));
        assert!(rendered.contains("fedcba98 idle 2m · default small-model"));
        assert!(rendered.contains("next"));
        assert!(!rendered.contains("\x1b["));
        assert_plain_language(&rendered);
    }

    #[test]
    fn history_only_dashboard_keeps_summary_privacy_scoped() {
        let mut data = snapshot();
        data.sessions.clear();
        let rendered = render_at(&data, false, 72, 1000);
        assert!(rendered.contains("live     none · 4 slots free"));
        assert!(rendered.contains("2 source summaries"));
        assert!(rendered.contains("numbers only"));
        assert!(rendered.contains("recent   finished · 2.3 MiB · 9421 lines · 20s ago"));
        assert!(!rendered.contains("model unknown"));
        assert_plain_language(&rendered);
    }

    #[test]
    fn truly_empty_dashboard_explains_what_appears_next() {
        let mut data = snapshot();
        data.sessions.clear();
        data.recent_observability.runs.clear();
        data.reasoning = "unknown".into();
        data.provider = "Claude CLI".into();
        let rendered = render_at(&data, false, 72, 1000);
        assert!(rendered.contains("new work gpt-5.6-sol via Claude CLI"));
        assert!(!rendered.contains("thinking"));
        assert!(rendered.contains("live     none · 4 slots free"));
        assert!(rendered.contains("none yet · summaries keep numbers, not source text"));
        assert!(rendered.contains("pattern  appears after the first source"));
        assert!(rendered.contains("recent   no source summary yet"));
        assert_plain_language(&rendered);
    }

    #[test]
    fn narrow_dashboard_is_sanitized_and_keeps_the_same_meaning() {
        let mut data = snapshot();
        data.default_model = "bad\x1b[31m\nmodel".into();
        let rendered = render_at(&data, true, 45, 1000);
        assert!(rendered.contains("azdaja · memory constellation"));
        assert!(rendered.contains("new work  bad[31mmodel via Jcode/OpenAI"));
        assert!(rendered.contains("bad[31mmodel"));
        assert!(!rendered.contains("bad\x1b[31m"));
        assert!(rendered.contains("live      1 running · 1 idle"));
        assert!(rendered.contains("memory    2 source summaries"));
        assert!(rendered.contains("pattern   repeated ←"));
        assert!(rendered.contains("recent    finished"));
        assert!(rendered.contains("session   ● 01234567 running"));
        assert!(rendered.contains("next  map"));
        let wide = render_at(&data, false, 120, 1000);
        assert!(wide.contains(
            "next  map · solo \"question\" -f ./document.txt · list · list --global · doctor · help"
        ));
        assert!(!rendered.contains("q quit"));
        assert_plain_language(&rendered);
    }

    #[test]
    fn dashboard_discloses_degraded_optional_metrics() {
        let mut data = snapshot();
        data.observability_degraded = true;
        let rendered = render_at(&data, false, 72, 1000);
        assert!(rendered.contains("local metrics need attention"));
        assert!(rendered.contains("1 running · 1 idle · 2/4 slots used"));
        assert_plain_language(&rendered);
    }

    #[test]
    fn dashboard_error_is_terminal_safe() {
        let rendered = render_error("bad\x1b[2J\nconfig", false, 72);
        assert!(rendered.contains("bad[2Jconfig"));
        assert!(!rendered.contains("\x1b"));
        assert!(rendered.contains("needs attention"));
    }

    #[test]
    fn list_view_names_live_sessions_and_local_number_summaries() {
        let rendered = render_list_at(&snapshot(), false, 78, 1000);
        assert!(rendered.starts_with("azdaja · memory constellation"));
        assert!(rendered.contains("new work      gpt-5.6-sol via Jcode/OpenAI · low thinking"));
        assert!(rendered.contains("live sessions  1 running · 1 idle · 2/4 slots used"));
        assert!(rendered.contains("\nlive sessions\n"));
        assert!(rendered.contains("● 0123456789abcdef"));
        assert!(rendered.contains("running"));
        assert!(rendered.contains("1.0 MiB"));
        assert!(rendered.contains("default model unknown"));
        assert!(rendered.contains("○ fedcba9876543210"));
        assert!(rendered.contains("512.0 KiB"));
        assert!(rendered.contains("default small-model"));
        assert!(rendered.contains("source summaries · local numbers only"));
        assert!(rendered.contains("● finished"));
        assert!(rendered.contains("○ loaded"));
        assert!(rendered.contains("variety 60%"));
        assert!(rendered.contains("variety 38%"));
        assert!(rendered.contains("commands  final <id> · kill <id> · map · help"));
        assert!(!rendered.contains("\x1b["));
        assert_plain_language(&rendered);
    }

    #[test]
    fn list_view_has_useful_empty_and_narrow_states() {
        let mut data = snapshot();
        data.sessions.truncate(1);
        let narrow = render_list_at(&data, false, 45, 1000);
        assert!(narrow.starts_with("azdaja · memory constellation"));
        assert!(narrow.contains("new work      gpt-5.6-sol via Jcode/OpenAI"));
        assert!(narrow.contains("live sessions  1 running · 0 idle"));
        assert!(narrow.contains("● 0123456789abcdef running 10s"));
        assert!(narrow.contains("1.0 MiB state · default model unknown"));
        assert!(narrow.contains("source summaries · local numbers only"));
        assert!(narrow.contains("● finished 20s · 2.3 MiB · variety 60%"));
        assert!(narrow.contains("commands  final <id>"));
        assert_plain_language(&narrow);

        data.sessions.clear();
        data.observability_degraded = true;
        let empty = render_list_at(&data, false, 72, 1000);
        assert!(empty.contains("live sessions  none · 4 slots free"));
        assert!(empty.contains("live sessions\nnone"));
        assert!(empty.contains("source summaries · local numbers only"));
        assert!(empty.contains("● finished"));
        assert!(empty.contains("○ loaded"));
        assert!(empty.contains("variety 60%"));
        assert!(empty.contains("local metrics need attention"));
        assert!(
            empty.contains(
                "next  map · start · solo · memory · list · list --global · doctor · help"
            )
        );
        assert!(!empty.contains("kill <id>"));
        assert_plain_language(&empty);
    }
}
