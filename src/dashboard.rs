use azdaja::{
    DashboardSnapshot, SessionStatus,
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

fn total_state_bytes(snapshot: &DashboardSnapshot) -> u64 {
    snapshot
        .sessions
        .iter()
        .map(|session| session.state_bytes)
        .sum()
}

fn status_line(snapshot: &DashboardSnapshot) -> (&'static str, &'static str) {
    if snapshot.observability_degraded {
        ("● awake · local metrics need attention", RED)
    } else {
        ("● awake · source stays local", GREEN)
    }
}

fn nest_line(snapshot: &DashboardSnapshot) -> String {
    let constellation = memory_constellation(snapshot);
    let trace_count = constellation.as_ref().map_or(0, |value| value.trace_count);
    if snapshot.sessions.is_empty() {
        return if trace_count == 0 {
            format!("empty · cold · 0/{} slots", snapshot.max_sessions)
        } else {
            let history = history_count_label(constellation.as_ref().expect("checked history"));
            format!(
                "0 resident · cold · 0/{} slots · {} · {} observed",
                snapshot.max_sessions,
                history,
                human_bytes(
                    constellation
                        .as_ref()
                        .map_or(0, |value| value.total_source_bytes)
                )
            )
        };
    }
    let pressure = if snapshot.sessions.len() >= snapshot.max_sessions {
        "full"
    } else if active_sessions(snapshot) > 0 {
        "warm"
    } else {
        "resting"
    };
    let mut line = format!(
        "{} resident state · {pressure} · {}/{} slots",
        human_bytes(total_state_bytes(snapshot)),
        snapshot.sessions.len(),
        snapshot.max_sessions
    );
    if trace_count > 0 {
        line.push_str(&format!(
            " · {}",
            history_count_label(constellation.as_ref().expect("checked history"))
        ));
    }
    line
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

fn memory_line(snapshot: &DashboardSnapshot) -> String {
    match memory_constellation(snapshot) {
        Some(constellation) => format!(
            "H→ {} · {}",
            constellation.render_strip(18),
            history_count_label(&constellation)
        ),
        None => "H→ ·················· · no traces yet".to_owned(),
    }
}

fn trace_count_label(count: usize) -> String {
    if count == 1 {
        "1 trace".to_owned()
    } else {
        format!("{count} traces")
    }
}

fn memory_count_label(count: usize) -> String {
    if count == 1 {
        "1 memory".to_owned()
    } else {
        format!("{count} memories")
    }
}

fn history_count_label(constellation: &MemoryConstellation) -> String {
    if constellation.completed_count == 0 {
        return trace_count_label(constellation.trace_count);
    }
    let loads = constellation
        .trace_count
        .saturating_sub(constellation.completed_count);
    if loads == 0 {
        memory_count_label(constellation.completed_count)
    } else {
        format!(
            "{} · {}",
            memory_count_label(constellation.completed_count),
            trace_count_label(loads)
        )
    }
}

fn percent(millipercent: u16) -> u32 {
    (u32::from(millipercent.min(1000)) * 100 + 500) / 1000
}

fn texture_line(snapshot: &DashboardSnapshot) -> String {
    match memory_constellation(snapshot) {
        Some(constellation) => format!(
            "H₀ {:.1}/8 · redundancy {}% · lines {}% nonempty",
            constellation.weighted_byte_entropy_bits(),
            percent(constellation.zero_order_redundancy_millipercent()),
            percent(constellation.nonempty_line_millipercent)
        ),
        None => "unmeasured · load one source".to_owned(),
    }
}

fn recent_trace_line(snapshot: &DashboardSnapshot, timestamp: u64) -> Option<String> {
    let run = snapshot.recent_observability.runs.first()?;
    let kind = match run.kind {
        RunKind::SessionLoad => "session load",
        RunKind::SoloLoad => "solo load",
        RunKind::SessionFinal => "session memory",
        RunKind::SoloFinal => "solo memory",
    };
    Some(format!(
        "{kind} · {} · {} lines · {} ago",
        human_bytes(run.source.source_bytes),
        run.source.physical_lines,
        human_duration(timestamp.saturating_sub(run.observed_unix))
    ))
}

fn session_line(session: &SessionStatus, default_model: &str, timestamp: u64) -> String {
    let marker = if session.busy { "●" } else { "○" };
    let state = if session.busy { "running" } else { "idle" };
    let model = session.sub_model.as_deref().unwrap_or(default_model);
    format!(
        "{marker} {} {state} {} · {}",
        clean(&session.id[..session.id.len().min(8)]),
        human_duration(timestamp.saturating_sub(session.updated)),
        clean(model)
    )
}

fn compact_texture_line(snapshot: &DashboardSnapshot) -> String {
    match memory_constellation(snapshot) {
        Some(constellation) => format!(
            "H₀ {:.1}/8 · R₀ {}% · lines {}%",
            constellation.weighted_byte_entropy_bits(),
            percent(constellation.zero_order_redundancy_millipercent()),
            percent(constellation.nonempty_line_millipercent)
        ),
        None => "unmeasured · load one source".to_owned(),
    }
}

fn compact_nest_line(snapshot: &DashboardSnapshot) -> String {
    let constellation = memory_constellation(snapshot);
    let traces = constellation.as_ref().map_or(0, |value| value.trace_count);
    if snapshot.sessions.is_empty() {
        return match constellation {
            Some(value) => format!(
                "0 resident · {} · {} observed",
                history_count_label(&value),
                human_bytes(value.total_source_bytes)
            ),
            None => format!("empty · 0/{} slots", snapshot.max_sessions),
        };
    }
    let mut line = format!(
        "{} resident · {}/{} slots",
        human_bytes(total_state_bytes(snapshot)),
        snapshot.sessions.len(),
        snapshot.max_sessions
    );
    if traces > 0 {
        line.push_str(&format!(
            " · {}",
            history_count_label(constellation.as_ref().expect("checked history"))
        ));
    }
    line
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
        "{} {}\n",
        paint(color, BOLD, "azdaja"),
        paint(color, status_style, status)
    ));
    output.push_str(&format!(
        "{}\n",
        truncate(
            &format!(
                "route {} · {} · {}",
                clean(&snapshot.default_model),
                clean(&snapshot.provider),
                clean(&snapshot.reasoning)
            ),
            width
        )
    ));
    output.push_str(&format!(
        "{}\n",
        truncate(&format!("nest  {}", compact_nest_line(snapshot)), width)
    ));
    let compact_memory = match memory_constellation(snapshot) {
        Some(constellation) => format!(
            "memory H→ {} · {}",
            constellation.render_strip(12),
            history_count_label(&constellation)
        ),
        None => "memory H→ ············ · no traces".to_owned(),
    };
    output.push_str(&format!("{}\n", truncate(&compact_memory, width)));
    output.push_str(&format!(
        "{}\n",
        truncate(
            &format!("texture {}", compact_texture_line(snapshot)),
            width
        )
    ));
    if let Some(session) = snapshot.sessions.first() {
        output.push_str(&format!(
            "{}\n",
            truncate(
                &format!(
                    "recent {}",
                    session_line(session, &snapshot.default_model, timestamp)
                ),
                width
            )
        ));
    } else if let Some(trace) = recent_trace_line(snapshot, timestamp) {
        output.push_str(&format!(
            "{}\n",
            truncate(&format!("recent {trace}"), width)
        ));
    } else {
        output.push_str("recent no memory trace yet\n");
    }
    output.push_str(&format!(
        "{}\n",
        truncate("next  map · solo · list · doctor · help", width)
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
    let resident = if snapshot.sessions.is_empty() {
        "empty".to_owned()
    } else {
        format!("{} resident", human_bytes(total_state_bytes(snapshot)))
    };
    let title = if width < 54 {
        "azdaja nest"
    } else {
        "azdaja memory nest"
    };
    let header = truncate(
        &format!(
            "{title} · {}/{} slots · {resident}",
            snapshot.sessions.len(),
            snapshot.max_sessions
        ),
        width,
    );
    let mut output = format!("{}\n\n", paint(color, BOLD, &header));

    if snapshot.sessions.is_empty() {
        output.push_str("no resident sessions\n\n");
        if snapshot.observability_degraded {
            output.push_str(&format!(
                "{}\n\n",
                paint(
                    color,
                    RED,
                    &truncate("note  local metrics need attention", width)
                )
            ));
        }
        output.push_str(&format!(
            "{}\n",
            paint(color, CYAN, &truncate("next  start · solo · help", width))
        ));
        return output;
    }

    for session in &snapshot.sessions {
        let marker = if session.busy { "●" } else { "○" };
        let state = if session.busy { "running" } else { "idle" };
        let age = human_duration(timestamp.saturating_sub(session.updated));
        let model = clean(
            session
                .sub_model
                .as_deref()
                .unwrap_or(&snapshot.default_model),
        );
        let id = clean(&session.id);
        let style = if session.busy { GREEN } else { "" };
        if width < 64 {
            let identity = truncate(&format!("{marker} {id} {state} {age}"), width);
            let details = truncate(
                &format!("  {} · {model}", human_bytes(session.state_bytes)),
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
            &truncate("commands  final <id> · kill <id> · help", width)
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
    output.push_str(&row(
        total,
        "route",
        &format!(
            "{} · {} · {}",
            snapshot.default_model, snapshot.provider, snapshot.reasoning
        ),
        CYAN,
        color,
    ));
    output.push_str(&row(total, "nest", &nest_line(snapshot), "", color));
    output.push_str(&row(total, "memory", &memory_line(snapshot), "", color));
    output.push_str(&row(total, "texture", &texture_line(snapshot), DIM, color));
    if snapshot.sessions.is_empty() {
        output.push_str(&row(
            total,
            "recent",
            recent_trace_line(snapshot, timestamp)
                .as_deref()
                .unwrap_or("no memory trace yet"),
            DIM,
            color,
        ));
    } else {
        for (index, session) in snapshot.sessions.iter().take(2).enumerate() {
            output.push_str(&row(
                total,
                if index == 0 { "recent" } else { "" },
                &session_line(session, &snapshot.default_model, timestamp),
                if session.busy { GREEN } else { "" },
                color,
            ));
        }
        if snapshot.sessions.len() > 2 {
            output.push_str(&row(
                total,
                "",
                &format!("+{} tucked away", snapshot.sessions.len() - 2),
                DIM,
                color,
            ));
        }
    }
    output.push_str(&bottom_border(total));
    output.push_str(&format!(
        "{}  {}\n",
        paint(color, DIM, "next"),
        paint(
            color,
            CYAN,
            "map · solo \"question\" -f ./document.txt · list · doctor · help"
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
                kind: RunKind::SoloLoad,
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
            default_model: "gpt-5.6-sol".into(),
            provider: "openai".into(),
            reasoning: "medium".into(),
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

    #[test]
    fn dashboard_card_shows_a_minimal_truthful_memory_constellation() {
        let rendered = render_at(&snapshot(), false, 72, 1000);
        assert!(rendered.starts_with("╭─ azdaja · memory constellation"));
        assert!(rendered.contains("● awake · source stays local"));
        assert!(rendered.contains("gpt-5.6-sol · openai · medium"));
        assert!(rendered.contains("1.5 MiB resident state · warm · 2/4 slots · 2 traces"));
        assert!(rendered.contains("H→"));
        assert!(rendered.contains('●'));
        assert!(rendered.contains('○'));
        assert!(rendered.contains("H₀"));
        assert!(rendered.contains("redundancy"));
        assert!(rendered.contains("lines"));
        assert!(rendered.contains("01234567 running"));
        assert!(rendered.contains("fedcba98 idle"));
        assert!(rendered.contains("next"));
        assert!(!rendered.contains("\x1b["));
    }

    #[test]
    fn dashboard_sanitizes_control_sequences_and_has_a_static_narrow_fallback() {
        let mut data = snapshot();
        data.default_model = "bad\x1b[31m\nmodel".into();
        let rendered = render_at(&data, true, 40, 1000);
        assert!(rendered.contains("bad[31mmodel"));
        assert!(!rendered.contains("bad\x1b[31m"));
        assert!(rendered.contains("next  map · solo · list · doctor · help"));
        assert!(!rendered.contains("q quit"));
    }

    #[test]
    fn dashboard_discloses_degraded_optional_metrics() {
        let mut data = snapshot();
        data.observability_degraded = true;
        let rendered = render_at(&data, false, 72, 1000);
        assert!(rendered.contains("local metrics need attention"));
        assert!(rendered.contains("1.5 MiB resident state"));
    }

    #[test]
    fn dashboard_error_is_terminal_safe() {
        let rendered = render_error("bad\x1b[2J\nconfig", false, 72);
        assert!(rendered.contains("bad[2Jconfig"));
        assert!(!rendered.contains("\x1b"));
        assert!(rendered.contains("needs attention"));
    }

    #[test]
    fn list_view_is_an_actionable_details_on_demand_layer() {
        let rendered = render_list_at(&snapshot(), false, 78, 1000);
        assert!(rendered.starts_with("azdaja memory nest · 2/4 slots · 1.5 MiB resident\n"));
        assert!(rendered.contains("● 0123456789abcdef"));
        assert!(rendered.contains("running"));
        assert!(rendered.contains("1.0 MiB"));
        assert!(rendered.contains("gpt-5.6-sol"));
        assert!(rendered.contains("○ fedcba9876543210"));
        assert!(rendered.contains("512.0 KiB"));
        assert!(rendered.contains("small-model"));
        assert!(rendered.contains("commands  final <id> · kill <id> · help"));
        assert!(!rendered.contains("\x1b["));
    }

    #[test]
    fn list_view_has_useful_empty_and_narrow_states() {
        let mut data = snapshot();
        data.sessions.truncate(1);
        let narrow = render_list_at(&data, false, 45, 1000);
        assert!(narrow.contains("azdaja nest · 1/4 slots · 1.0 MiB resident"));
        assert!(narrow.contains("● 0123456789abcdef running 10s"));
        assert!(narrow.contains("1.0 MiB · gpt-5.6-sol"));
        assert!(narrow.contains("commands  final <id>"));

        data.sessions.clear();
        data.observability_degraded = true;
        let empty = render_list_at(&data, false, 72, 1000);
        assert!(empty.contains("0/4 slots · empty"));
        assert!(empty.contains("no resident sessions"));
        assert!(empty.contains("local metrics need attention"));
        assert!(empty.contains("next  start · solo · help"));
        assert!(!empty.contains("kill <id>"));
    }
}
