use azdaja::{DashboardSnapshot, SessionStatus};
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
    if snapshot.sessions.is_empty() {
        return format!("empty · cold · 0/{} slots", snapshot.max_sessions);
    }
    let pressure = if snapshot.sessions.len() >= snapshot.max_sessions {
        "full"
    } else if active_sessions(snapshot) > 0 {
        "warm"
    } else {
        "resting"
    };
    format!(
        "{} resident state · {pressure} · {}/{} slots",
        human_bytes(total_state_bytes(snapshot)),
        snapshot.sessions.len(),
        snapshot.max_sessions
    )
}

fn memory_map(snapshot: &DashboardSnapshot) -> String {
    let capacity = snapshot.max_sessions.max(1);
    let shown = capacity.min(8);
    let mut slots = String::new();
    for index in 0..shown {
        slots.push(match snapshot.sessions.get(index) {
            Some(session) if session.busy => '●',
            Some(_) => '○',
            None => '·',
        });
    }
    if capacity > shown {
        slots.push_str(&format!("+{}", capacity - shown));
    }
    let mut mass = String::with_capacity(20);
    for unit in 0..20usize {
        let slot = unit.saturating_mul(capacity) / 20;
        mass.push(match snapshot.sessions.get(slot) {
            Some(session) if session.busy => '█',
            Some(_) => '▒',
            None => '░',
        });
    }
    format!("{slots}  {mass}")
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

fn render_compact(snapshot: &DashboardSnapshot, color: bool, timestamp: u64) -> String {
    let (status, status_style) = status_line(snapshot);
    let mut output = String::new();
    output.push_str(&format!(
        "{} {}\n",
        paint(color, BOLD, "azdaja"),
        paint(color, status_style, status)
    ));
    output.push_str(&format!(
        "route {} · {} · {}\n",
        clean(&snapshot.default_model),
        clean(&snapshot.provider),
        clean(&snapshot.reasoning)
    ));
    output.push_str(&format!("nest  {}\n", nest_line(snapshot)));
    output.push_str(&format!("map   {}\n", memory_map(snapshot)));
    if let Some(session) = snapshot.sessions.first() {
        output.push_str(&format!(
            "recent {}\n",
            session_line(session, &snapshot.default_model, timestamp)
        ));
    } else {
        output.push_str("recent no resident session\n");
    }
    output.push_str("next  solo · list · doctor · help\n");
    output
}

pub fn render(snapshot: &DashboardSnapshot, color: bool, terminal_columns: usize) -> String {
    render_at(snapshot, color, terminal_columns, now())
}

fn render_at(
    snapshot: &DashboardSnapshot,
    color: bool,
    terminal_columns: usize,
    timestamp: u64,
) -> String {
    if terminal_columns < 54 {
        return render_compact(snapshot, color, timestamp);
    }
    let total = terminal_columns.clamp(58, 78);
    let (status, status_style) = status_line(snapshot);
    let mut output = top_border(total, "azdaja · little memory", color);
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
    output.push_str(&row(total, "map", &memory_map(snapshot), "", color));
    if snapshot.sessions.is_empty() {
        output.push_str(&row(total, "recent", "no resident session", DIM, color));
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
            "solo \"question\" -f ./document.txt · list · doctor · help"
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
    use std::path::PathBuf;

    fn snapshot() -> DashboardSnapshot {
        DashboardSnapshot {
            default_model: "gpt-5.6-luna".into(),
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
                },
            ],
            recent_observability: azdaja::observability::RecentAggregateSummary::empty(),
            observability_degraded: false,
        }
    }

    #[test]
    fn dashboard_card_matches_the_minimal_memory_nest() {
        let rendered = render_at(&snapshot(), false, 72, 1000);
        assert!(rendered.starts_with("╭─ azdaja · little memory"));
        assert!(rendered.contains("● awake · source stays local"));
        assert!(rendered.contains("gpt-5.6-luna · openai · medium"));
        assert!(rendered.contains("1.5 MiB resident state · warm · 2/4 slots"));
        assert!(rendered.contains("●○··"));
        assert!(rendered.contains("█████"));
        assert!(rendered.contains("▒▒▒▒▒"));
        assert!(rendered.contains("░░░░░"));
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
        assert!(rendered.contains("next  solo · list · doctor · help"));
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
}
