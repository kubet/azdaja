use anyhow::Result;
use azdaja::{DashboardSnapshot, SessionStatus, VERSION, observability::SourceLocalAggregate};
use crossterm::{
    cursor::{Hide, Show},
    event::{self, Event, KeyCode, KeyEvent, KeyEventKind, KeyModifiers},
    execute,
    terminal::{
        self, EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode,
    },
};
use ratatui::{
    Frame, Terminal,
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, BorderType, Borders, Paragraph, Wrap},
};
use std::{
    io::{self, Write},
    panic::{self, AssertUnwindSafe},
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

use crate::dashboard;

const MIN_INTERACTIVE_WIDTH: u16 = 54;
const MIN_INTERACTIVE_HEIGHT: u16 = 9;
const REFRESH_INTERVAL: Duration = Duration::from_secs(2);
const POLL_INTERVAL: Duration = Duration::from_millis(200);

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ConsoleView {
    Overview,
    Details,
    Install,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct VisualRow {
    label: &'static str,
    value: String,
    tier: &'static str,
}

#[derive(Debug)]
struct AppState {
    snapshot: Option<DashboardSnapshot>,
    error: Option<String>,
    selected: usize,
    view: ConsoleView,
    details: bool,
    color: bool,
    last_refresh: Instant,
}

impl AppState {
    fn new(color: bool) -> Self {
        Self {
            snapshot: None,
            error: None,
            selected: 0,
            view: ConsoleView::Overview,
            details: false,
            color,
            last_refresh: Instant::now() - REFRESH_INTERVAL,
        }
    }

    fn refresh<F>(&mut self, load_snapshot: &mut F)
    where
        F: FnMut() -> Result<DashboardSnapshot>,
    {
        match load_snapshot() {
            Ok(snapshot) => {
                let len = snapshot.sessions.len();
                self.selected = self.selected.min(len.saturating_sub(1));
                self.snapshot = Some(snapshot);
                self.error = None;
            }
            Err(error) => {
                self.error = Some(format!("{error:#}"));
            }
        }
        self.last_refresh = Instant::now();
    }

    fn move_selection(&mut self, delta: isize) {
        let Some(snapshot) = self.snapshot.as_ref() else {
            return;
        };
        if snapshot.sessions.is_empty() {
            self.selected = 0;
            return;
        }
        let last = snapshot.sessions.len() - 1;
        self.selected = if delta.is_negative() {
            self.selected.saturating_sub(delta.unsigned_abs())
        } else {
            self.selected.saturating_add(delta as usize).min(last)
        };
    }
}

struct TerminalGuard;

impl TerminalGuard {
    fn enter() -> Result<Self> {
        enable_raw_mode()?;
        let mut stdout = io::stdout();
        if let Err(error) = execute!(stdout, EnterAlternateScreen, Hide) {
            let _ = disable_raw_mode();
            return Err(error.into());
        }
        Ok(Self)
    }
}

impl Drop for TerminalGuard {
    fn drop(&mut self) {
        let _ = disable_raw_mode();
        let _ = execute!(io::stdout(), Show, LeaveAlternateScreen);
    }
}

/// Run the installed no-args observability console.
///
/// Non-TTY handling stays in `main`; this function keeps a line-oriented fallback for
/// terminals too narrow or short for a safe full-screen interface.
pub fn run<F>(mut load_snapshot: F, color: bool) -> Result<()>
where
    F: FnMut() -> Result<DashboardSnapshot>,
{
    let (columns, rows) = terminal::size().unwrap_or((dashboard::terminal_width() as u16, 24));
    if columns < MIN_INTERACTIVE_WIDTH || rows < MIN_INTERACTIVE_HEIGHT {
        match load_snapshot() {
            Ok(snapshot) => print!("{}", render_narrow_text(&snapshot, color)),
            Err(error) => print!(
                "{}",
                dashboard::render_error(&format!("{error:#}"), color, columns.into())
            ),
        }
        io::stdout().flush()?;
        return Ok(());
    }

    let guard = TerminalGuard::enter()?;
    let mut terminal = Terminal::new(CrosstermBackend::new(io::stdout()))?;
    let result = panic::catch_unwind(AssertUnwindSafe(|| {
        run_loop(&mut terminal, &mut load_snapshot, color)
    }));
    drop(terminal);
    drop(guard);
    match result {
        Ok(result) => result,
        Err(payload) => panic::resume_unwind(payload),
    }
}

fn run_loop<F>(
    terminal: &mut Terminal<CrosstermBackend<io::Stdout>>,
    load_snapshot: &mut F,
    color: bool,
) -> Result<()>
where
    F: FnMut() -> Result<DashboardSnapshot>,
{
    let mut state = AppState::new(color);
    state.refresh(load_snapshot);
    loop {
        terminal.draw(|frame| render(frame, &state))?;
        if event::poll(POLL_INTERVAL)? {
            match event::read()? {
                Event::Key(key) if should_handle_key(key) => {
                    if handle_key(key, &mut state, load_snapshot) {
                        break;
                    }
                }
                Event::Resize(_, 0) | Event::Resize(0, _) => break,
                _ => {}
            }
        }
        if state.last_refresh.elapsed() >= REFRESH_INTERVAL {
            state.refresh(load_snapshot);
        }
    }
    Ok(())
}

fn should_handle_key(key: KeyEvent) -> bool {
    matches!(key.kind, KeyEventKind::Press | KeyEventKind::Repeat)
}

fn handle_key<F>(key: KeyEvent, state: &mut AppState, load_snapshot: &mut F) -> bool
where
    F: FnMut() -> Result<DashboardSnapshot>,
{
    if key.modifiers.contains(KeyModifiers::CONTROL)
        && matches!(key.code, KeyCode::Char('c') | KeyCode::Char('C'))
    {
        return true;
    }
    match key.code {
        KeyCode::Char('q') | KeyCode::Char('Q') | KeyCode::Esc => true,
        KeyCode::Char('r') | KeyCode::Char('R') => {
            state.refresh(load_snapshot);
            false
        }
        KeyCode::Char('d') | KeyCode::Char('D') => {
            state.details = !state.details;
            state.view = if state.details {
                ConsoleView::Details
            } else {
                ConsoleView::Overview
            };
            false
        }
        KeyCode::Enter => {
            state.view = ConsoleView::Details;
            state.details = true;
            false
        }
        KeyCode::Char('i') | KeyCode::Char('I') => {
            state.view = if state.view == ConsoleView::Install {
                ConsoleView::Overview
            } else {
                ConsoleView::Install
            };
            false
        }
        KeyCode::Up | KeyCode::Char('k') | KeyCode::Char('K') => {
            state.move_selection(-1);
            false
        }
        KeyCode::Down | KeyCode::Char('j') | KeyCode::Char('J') => {
            state.move_selection(1);
            false
        }
        _ => false,
    }
}

fn render(frame: &mut Frame<'_>, state: &AppState) {
    let area = frame.area();
    if area.width < MIN_INTERACTIVE_WIDTH || area.height < MIN_INTERACTIVE_HEIGHT {
        render_narrow(frame, area, state);
        return;
    }
    let vertical = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(card_height(area.height)),
            Constraint::Min(1),
            Constraint::Length(1),
        ])
        .split(area);

    let card = match state.error.as_deref() {
        Some(error) => error_lines(error),
        None => state
            .snapshot
            .as_ref()
            .map_or_else(empty_lines, |snapshot| {
                overview_lines(snapshot, now_secs(), state.color)
            }),
    };
    frame.render_widget(
        Paragraph::new(card)
            .block(
                Block::default()
                    .borders(Borders::ALL)
                    .border_type(BorderType::Rounded)
                    .title(Line::from(vec![Span::styled(
                        format!(" azdaja · virtual memory · v{VERSION} "),
                        heading_style(state.color),
                    )])),
            )
            .wrap(Wrap { trim: true }),
        vertical[0],
    );

    let body = match (state.error.as_deref(), state.snapshot.as_ref(), state.view) {
        (Some(error), _, _) => detail_error_lines(error, state.color),
        (None, Some(snapshot), ConsoleView::Details) => {
            details_lines(snapshot, state.selected, state.color)
        }
        (None, Some(snapshot), ConsoleView::Install) => install_lines(snapshot, state.color),
        (None, Some(snapshot), ConsoleView::Overview) => {
            sessions_lines(snapshot, state.selected, state.color)
        }
        (None, None, _) => vec![Line::from("loading local state…")],
    };
    frame.render_widget(Paragraph::new(body).wrap(Wrap { trim: true }), vertical[1]);
    frame.render_widget(
        Paragraph::new(key_hint(state.view, state.color)),
        vertical[2],
    );
}

fn card_height(screen_height: u16) -> u16 {
    if screen_height < 14 { 8 } else { 10 }
}

fn render_narrow(frame: &mut Frame<'_>, area: Rect, state: &AppState) {
    let lines = match state.error.as_deref() {
        Some(error) => vec![
            Line::from(styled(
                "azdaja · virtual memory",
                heading_style(state.color),
            )),
            Line::from(styled("needs attention", bad_style(state.color))),
            Line::from(clean(error)),
            key_hint(state.view, state.color),
        ],
        None => state
            .snapshot
            .as_ref()
            .map_or_else(empty_lines, |snapshot| narrow_lines(snapshot, state.color)),
    };
    frame.render_widget(Paragraph::new(lines).wrap(Wrap { trim: true }), area);
}

fn overview_lines(snapshot: &DashboardSnapshot, timestamp: u64, color: bool) -> Vec<Line<'static>> {
    overview_rows(snapshot, timestamp)
        .into_iter()
        .map(|row| row_line(row, color))
        .collect()
}

fn empty_lines() -> Vec<Line<'static>> {
    vec![
        Line::from("status    ○ dormant · source stays local"),
        Line::from("resident  no session state loaded"),
        Line::from(format!("map       {}", "·".repeat(24))),
        Line::from("next      ask your agent about one large input"),
    ]
}

fn error_lines(error: &str) -> Vec<Line<'static>> {
    vec![
        Line::from("status    ● needs attention"),
        Line::from(format!("issue     {}", clean(error))),
        Line::from("fix       az doctor · az help"),
    ]
}

fn detail_error_lines(error: &str, color: bool) -> Vec<Line<'static>> {
    vec![
        Line::from(styled("configuration/state error", bad_style(color))),
        Line::from(clean(error)),
        Line::from("No provider call was made while rendering this console."),
    ]
}

fn details_lines(snapshot: &DashboardSnapshot, selected: usize, color: bool) -> Vec<Line<'static>> {
    let source = current_source(snapshot, selected);
    let mut lines = vec![
        Line::from(styled("measured details", heading_style(color))),
        Line::from(format!(
            "state root       {}",
            clean(&snapshot.state_root.display().to_string())
        )),
        Line::from(format!("session limit    {}", snapshot.max_sessions)),
        Line::from(format!(
            "idle expiry      {}",
            human_duration(snapshot.idle_timeout)
        )),
        Line::from(source_exposure_line(source)),
        Line::from("coverage         n/a · no coverage contract observed"),
    ];
    if let Some(source) = source {
        lines.push(Line::from(format!(
            "resident source  {}",
            source_line(source)
        )));
        lines.push(Line::from(format!(
            "source texture  H0 byte {:.1} / 8",
            source.byte_entropy_bits()
        )));
    }
    if let Some(session) = snapshot.sessions.get(selected) {
        lines.push(Line::from(""));
        lines.push(Line::from(styled("selected session", heading_style(color))));
        lines.push(Line::from(format!(
            "id               {}",
            clean(&session.id)
        )));
        lines.push(Line::from(format!(
            "status           {}",
            if session.busy { "running" } else { "idle" }
        )));
        lines.push(Line::from(format!(
            "updated          {} ago",
            human_duration(now_secs().saturating_sub(session.updated))
        )));
        lines.push(Line::from(format!(
            "state bytes      {}",
            human_bytes(session.state_bytes)
        )));
        lines.push(Line::from(format!(
            "loaded sources   {} aggregate-only record(s)",
            session.loaded_sources
        )));
        lines.push(Line::from(format!(
            "model            {}",
            clean(
                session
                    .sub_model
                    .as_deref()
                    .unwrap_or(&snapshot.default_model)
            )
        )));
    } else {
        lines.push(Line::from(""));
        lines.push(Line::from("no sessions yet"));
    }
    lines
}

fn install_lines(_snapshot: &DashboardSnapshot, color: bool) -> Vec<Line<'static>> {
    vec![
        Line::from(styled("installations", heading_style(color))),
        Line::from("Install custody is not in DashboardSnapshot yet."),
        Line::from("Run az doctor [jcode|claude|codex|gemini|opencode] for validated state."),
        Line::from("This console does not infer active/available/absent from missing data."),
    ]
}

fn sessions_lines(
    snapshot: &DashboardSnapshot,
    selected: usize,
    color: bool,
) -> Vec<Line<'static>> {
    let mut lines = vec![Line::from(styled("recent sessions", heading_style(color)))];
    if snapshot.sessions.is_empty() {
        lines.push(Line::from(
            "No sessions yet. az solo can inspect a large UTF-8 file.",
        ));
        return lines;
    }
    for (index, session) in snapshot.sessions.iter().take(6).enumerate() {
        let marker = if index == selected { "›" } else { " " };
        lines.push(Line::from(vec![
            Span::raw(marker),
            Span::raw(" "),
            Span::styled(
                session_summary(session, &snapshot.default_model, now_secs()),
                session_style(session, color),
            ),
        ]));
    }
    lines
}

fn narrow_lines(snapshot: &DashboardSnapshot, color: bool) -> Vec<Line<'static>> {
    let mut lines = vec![Line::from(styled(
        format!("azdaja · virtual memory · v{VERSION}"),
        heading_style(color),
    ))];
    for row in overview_rows(snapshot, now_secs()).into_iter().take(6) {
        lines.push(row_line(row, color));
    }
    lines.push(key_hint(ConsoleView::Overview, color));
    lines
}

fn render_narrow_text(snapshot: &DashboardSnapshot, color: bool) -> String {
    let mut output = String::new();
    output.push_str(&format!("azdaja · virtual memory · v{VERSION}\n"));
    for row in overview_rows(snapshot, now_secs()) {
        output.push_str(&format!("{:<9} {}\n", row.label, clean(&row.value)));
    }
    output.push_str("keys      r refresh · d details · i install · q quit\n");
    if color { output } else { output }
}

fn overview_rows(snapshot: &DashboardSnapshot, timestamp: u64) -> Vec<VisualRow> {
    let active = active_sessions(snapshot);
    let state_bytes = total_state_bytes(snapshot);
    let source = current_source(snapshot, 0);
    let status = if snapshot.sessions.is_empty() {
        "○ dormant · source stays local".to_string()
    } else if active > 0 {
        "● active · source stays local".to_string()
    } else {
        "○ idle · source stays local".to_string()
    };
    let mut rows = vec![
        VisualRow {
            label: "status",
            value: status,
            tier: "exact-local",
        },
        VisualRow {
            label: "route",
            value: format!(
                "{} · {} · {}",
                clean(&snapshot.default_model),
                clean(&snapshot.provider),
                clean(&snapshot.reasoning)
            ),
            tier: "exact-local",
        },
        VisualRow {
            label: "sessions",
            value: format!(
                "{}/{} · {active} active",
                snapshot.sessions.len(),
                snapshot.max_sessions
            ),
            tier: "exact-local",
        },
        VisualRow {
            label: "state",
            value: if state_bytes == 0 {
                format!(
                    "no session state · {} idle expiry",
                    human_duration(snapshot.idle_timeout)
                )
            } else {
                format!(
                    "{} session state · {} idle expiry",
                    human_bytes(state_bytes),
                    human_duration(snapshot.idle_timeout)
                )
            },
            tier: "exact-local",
        },
    ];
    if let Some(source) = source {
        rows.push(VisualRow {
            label: "resident",
            value: source_line(source),
            tier: "exact-local",
        });
    }
    rows.extend([
        VisualRow {
            label: "map",
            value: memory_map(snapshot),
            tier: if source.is_some() {
                "exact-local"
            } else {
                "exact-structural"
            },
        },
        VisualRow {
            label: "coverage",
            value: "n/a · no coverage contract observed".to_string(),
            tier: "exact-local",
        },
        VisualRow {
            label: "last",
            value: last_line(snapshot, timestamp),
            tier: "exact-local",
        },
        VisualRow {
            label: "next",
            value: "az solo \"question\" -f ./document.txt".to_string(),
            tier: "exact-local",
        },
    ]);
    rows
}

fn row_line(row: VisualRow, color: bool) -> Line<'static> {
    let label_style = Style::default().fg(if color { Color::DarkGray } else { Color::Reset });
    Line::from(vec![
        Span::styled(format!("{:<9} ", row.label), label_style),
        Span::raw(row.value),
        Span::styled(
            format!("  [{}]", row.tier),
            Style::default().fg(if color { Color::DarkGray } else { Color::Reset }),
        ),
    ])
}

fn key_hint(view: ConsoleView, color: bool) -> Line<'static> {
    let view = match view {
        ConsoleView::Overview => "overview",
        ConsoleView::Details => "details",
        ConsoleView::Install => "install",
    };
    Line::from(vec![
        Span::styled(format!("{view} · "), subtle_style(color)),
        Span::raw("↑/↓ j/k select · Enter inspect · d details · i install · r refresh · q quit"),
    ])
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

fn current_source(snapshot: &DashboardSnapshot, selected: usize) -> Option<&SourceLocalAggregate> {
    snapshot
        .sessions
        .get(selected)
        .and_then(|session| session.source.as_ref())
        .or_else(|| {
            snapshot
                .sessions
                .iter()
                .find_map(|session| session.source.as_ref())
        })
        .or_else(|| {
            snapshot
                .recent_observability
                .runs
                .first()
                .map(|run| &run.source)
        })
}

fn source_line(source: &SourceLocalAggregate) -> String {
    format!(
        "{} · {} chars · {} lines · {} nonempty",
        human_bytes(source.source_bytes),
        source.utf8_chars,
        source.physical_lines,
        source.nonempty_lines
    )
}

fn source_exposure_line(source: Option<&SourceLocalAggregate>) -> String {
    if source.is_some() {
        "source exposure  unmeasured · aggregate resident counts only".to_string()
    } else {
        "source exposure  unmeasured by current snapshot".to_string()
    }
}

fn memory_map(snapshot: &DashboardSnapshot) -> String {
    if current_source(snapshot, 0).is_some() {
        format!("{} · resident held local", "░".repeat(24))
    } else if snapshot.sessions.is_empty() || total_state_bytes(snapshot) == 0 {
        format!("{} · no session state loaded", "·".repeat(24))
    } else {
        format!("{} · source exposure unmeasured", "?".repeat(24))
    }
}

fn last_line(snapshot: &DashboardSnapshot, timestamp: u64) -> String {
    match snapshot.sessions.first() {
        Some(session) => format!(
            "{} · updated {} ago",
            clean(&session.id[..session.id.len().min(8)]),
            human_duration(timestamp.saturating_sub(session.updated))
        ),
        None => "no sessions yet".to_string(),
    }
}

fn session_summary(session: &SessionStatus, default_model: &str, timestamp: u64) -> String {
    let marker = if session.busy { "●" } else { "○" };
    let state = if session.busy { "running" } else { "idle" };
    let model = session.sub_model.as_deref().unwrap_or(default_model);
    format!(
        "{marker} {}  {state:<7}  {:>4}  {} state  {}",
        clean(&session.id[..session.id.len().min(8)]),
        human_duration(timestamp.saturating_sub(session.updated)),
        human_bytes(session.state_bytes),
        clean(model),
    )
}

fn now_secs() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs()
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

fn styled(value: impl Into<String>, style: Style) -> Span<'static> {
    Span::styled(value.into(), style)
}

fn heading_style(color: bool) -> Style {
    if color {
        Style::default()
            .fg(Color::Cyan)
            .add_modifier(Modifier::BOLD)
    } else {
        Style::default().add_modifier(Modifier::BOLD)
    }
}

fn subtle_style(color: bool) -> Style {
    Style::default().fg(if color { Color::DarkGray } else { Color::Reset })
}

fn bad_style(color: bool) -> Style {
    if color {
        Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)
    } else {
        Style::default().add_modifier(Modifier::BOLD)
    }
}

fn session_style(session: &SessionStatus, color: bool) -> Style {
    if !color {
        return Style::default();
    }
    if session.busy {
        Style::default().fg(Color::Green)
    } else {
        Style::default()
    }
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
        }
    }

    #[test]
    fn overview_uses_only_snapshot_fields_and_labels_unknowns() {
        let rows = overview_rows(&snapshot(), 1000);
        let text = rows
            .iter()
            .map(|row| format!("{} {}", row.label, row.value))
            .collect::<Vec<_>>()
            .join("\n");
        assert!(text.contains("gpt-5.6-luna · openai · medium"));
        assert!(text.contains("2/4 · 1 active"));
        assert!(text.contains("1.5 MiB session state"));
        assert!(text.contains("source exposure unmeasured"));
        assert!(text.contains("n/a · no coverage contract observed"));
        assert!(!text.contains("boundary"));
        assert!(!text.contains("verified 100%"));
    }

    #[test]
    fn empty_map_is_plain_and_does_not_claim_source_loaded() {
        let mut empty = snapshot();
        empty.sessions.clear();
        let rows = overview_rows(&empty, 1000);
        let map = rows.iter().find(|row| row.label == "map").unwrap();
        assert!(map.value.contains("········"));
        assert!(map.value.contains("no session state loaded"));
    }

    #[test]
    fn narrow_text_has_no_border_and_keeps_key_hints() {
        let rendered = render_narrow_text(&snapshot(), false);
        assert!(rendered.starts_with("azdaja · virtual memory"));
        assert!(rendered.contains("keys"));
        assert!(!rendered.contains('╭'));
        assert!(rendered.contains("source exposure unmeasured"));
    }
}
