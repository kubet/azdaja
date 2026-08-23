use azdaja::{DashboardSnapshot, SessionStatus, VERSION};
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

fn top_border(total: usize, color: bool) -> String {
    let title = format!(" AZDAJA v{VERSION} ");
    let fill = total.saturating_sub(title.chars().count() + 3);
    format!(
        "╭─{}{}╮\n",
        paint(color, BOLD, &paint(color, RED, &title)),
        "─".repeat(fill)
    )
}

fn bottom_border(total: usize) -> String {
    format!("╰{}╯\n", "─".repeat(total.saturating_sub(2)))
}

fn separator(total: usize, label: &str, color: bool) -> String {
    let label = format!(" {label} ");
    let fill = total.saturating_sub(label.chars().count() + 3);
    format!("├─{}{}┤\n", paint(color, DIM, &label), "─".repeat(fill))
}

fn row(total: usize, label: &str, value: &str, value_style: &str, color: bool) -> String {
    let capacity = total.saturating_sub(4);
    let label_width = 11.min(capacity);
    let value_width = capacity.saturating_sub(label_width);
    let label = truncate(&clean(label), label_width);
    let value = truncate(&clean(value), value_width);
    let plain_width = label_width + value.chars().count();
    let padding = capacity.saturating_sub(plain_width);
    format!(
        "│ {}{}{}{} │\n",
        paint(color, DIM, &format!("{label:<label_width$}")),
        paint(color, value_style, &value),
        " ".repeat(padding),
        ""
    )
}

fn session_bar(used: usize, maximum: usize) -> String {
    let width = 12usize;
    let filled = if maximum == 0 {
        0
    } else {
        used.saturating_mul(width).div_ceil(maximum).min(width)
    };
    format!("{}{}", "■".repeat(filled), "·".repeat(width - filled))
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

fn session_line(session: &SessionStatus, default_model: &str, timestamp: u64) -> String {
    let marker = if session.busy { "●" } else { "○" };
    let state = if session.busy { "running" } else { "idle" };
    let age = timestamp.saturating_sub(session.updated);
    let model = session.sub_model.as_deref().unwrap_or(default_model);
    format!(
        "{marker} {}  {state:<7}  {:>4}  {}",
        &session.id[..session.id.len().min(8)],
        human_duration(age),
        clean(model)
    )
}

fn render_compact(snapshot: &DashboardSnapshot, color: bool, timestamp: u64) -> String {
    let active = snapshot
        .sessions
        .iter()
        .filter(|session| session.busy)
        .count();
    let bytes = snapshot
        .sessions
        .iter()
        .map(|session| session.state_bytes)
        .sum();
    let mut output = String::new();
    output.push_str(&format!(
        "{} {}\n",
        paint(color, BOLD, &format!("AZDAJA v{VERSION}")),
        paint(color, GREEN, "● ready")
    ));
    output.push_str(&format!(
        "{} · {} · {} reasoning\n",
        clean(&snapshot.default_model),
        clean(&snapshot.provider),
        clean(&snapshot.reasoning)
    ));
    output.push_str(&format!(
        "sessions {}/{} · {active} active · {} state\n",
        snapshot.sessions.len(),
        snapshot.max_sessions,
        human_bytes(bytes)
    ));
    if let Some(session) = snapshot.sessions.first() {
        output.push_str(&format!(
            "recent {}\n",
            session_line(session, &snapshot.default_model, timestamp)
        ));
    }
    output.push_str("commands  solo · list · doctor · help\n");
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
    let active = snapshot
        .sessions
        .iter()
        .filter(|session| session.busy)
        .count();
    let state_bytes: u64 = snapshot
        .sessions
        .iter()
        .map(|session| session.state_bytes)
        .sum();
    let mut output = top_border(total, color);
    output.push_str(&row(
        total,
        "Status",
        "● ready · local provider-free view",
        GREEN,
        color,
    ));
    output.push_str(&row(total, "Model", &snapshot.default_model, CYAN, color));
    output.push_str(&row(
        total,
        "Route",
        &format!("{} · {} reasoning", snapshot.provider, snapshot.reasoning),
        "",
        color,
    ));
    output.push_str(&row(
        total,
        "Sessions",
        &format!(
            "{}/{} {} · {active} active",
            snapshot.sessions.len(),
            snapshot.max_sessions,
            session_bar(snapshot.sessions.len(), snapshot.max_sessions)
        ),
        if active > 0 { GREEN } else { "" },
        color,
    ));
    output.push_str(&row(
        total,
        "State",
        &format!(
            "{} · {} idle expiry",
            human_bytes(state_bytes),
            human_duration(snapshot.idle_timeout)
        ),
        "",
        color,
    ));
    output.push_str(&separator(total, "recent sessions", color));
    if snapshot.sessions.is_empty() {
        output.push_str(&row(
            total,
            "Recent",
            "No sessions yet · az start creates one",
            DIM,
            color,
        ));
    } else {
        for (index, session) in snapshot.sessions.iter().take(3).enumerate() {
            output.push_str(&row(
                total,
                if index == 0 { "Recent" } else { "" },
                &session_line(session, &snapshot.default_model, timestamp),
                if session.busy { GREEN } else { "" },
                color,
            ));
        }
    }
    output.push_str(&bottom_border(total));
    output.push_str(&format!(
        "  {}  {}\n",
        paint(color, DIM, "Commands"),
        paint(color, CYAN, "solo · list · doctor · help")
    ));
    output.push_str(&format!(
        "  {}\n",
        paint(color, DIM, "az solo \"question\" -f ./document.txt")
    ));
    output
}

pub fn render_error(message: &str, color: bool, terminal_columns: usize) -> String {
    let message = clean(message);
    if terminal_columns < 54 {
        return format!(
            "{} {}\n{}\ncommands  doctor · install · help\n",
            paint(color, BOLD, &format!("AZDAJA v{VERSION}")),
            paint(color, RED, "● needs attention"),
            truncate(&message, terminal_columns.max(20))
        );
    }
    let total = terminal_columns.clamp(58, 78);
    let mut output = top_border(total, color);
    output.push_str(&row(total, "Status", "● needs attention", RED, color));
    output.push_str(&row(total, "Issue", &message, "", color));
    output.push_str(&row(total, "Fix", "az doctor · az help", CYAN, color));
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
                },
                SessionStatus {
                    id: "fedcba9876543210".into(),
                    created: 800,
                    updated: 880,
                    sub_model: Some("small-model".into()),
                    busy: false,
                    state_bytes: 512 * 1024,
                },
            ],
        }
    }

    #[test]
    fn dashboard_card_reports_real_snapshot_fields_without_color() {
        let rendered = render_at(&snapshot(), false, 72, 1000);
        assert!(rendered.starts_with("╭─ AZDAJA v"));
        assert!(rendered.contains("● ready · local provider-free view"));
        assert!(rendered.contains("gpt-5.6-luna"));
        assert!(rendered.contains("openai · medium reasoning"));
        assert!(rendered.contains("2/4"));
        assert!(rendered.contains("1 active"));
        assert!(rendered.contains("01234567  running"));
        assert!(rendered.contains("fedcba98  idle"));
        assert!(rendered.contains("1.5 MiB"));
        assert!(!rendered.contains("\x1b["));
    }

    #[test]
    fn dashboard_sanitizes_control_sequences_and_has_a_narrow_fallback() {
        let mut data = snapshot();
        data.default_model = "bad\x1b[31m\nmodel".into();
        let rendered = render_at(&data, true, 40, 1000);
        assert!(rendered.contains("bad[31mmodel"));
        assert!(!rendered.contains("bad\x1b[31m"));
        assert!(rendered.contains("commands  solo · list · doctor · help"));
    }

    #[test]
    fn dashboard_error_is_terminal_safe() {
        let rendered = render_error("bad\x1b[2J\nconfig", false, 72);
        assert!(rendered.contains("bad[2Jconfig"));
        assert!(!rendered.contains("\x1b"));
        assert!(rendered.contains("needs attention"));
    }
}
