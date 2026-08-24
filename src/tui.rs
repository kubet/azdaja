use anyhow::Result;
use azdaja::{DashboardSnapshot, SessionStatus, observability::SourceLocalAggregate};
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
    layout::Rect,
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
const MIN_INTERACTIVE_HEIGHT: u16 = 20;
const MAX_CARD_WIDTH: u16 = 78;
const REFRESH_INTERVAL: Duration = Duration::from_secs(2);
const POLL_INTERVAL: Duration = Duration::from_millis(200);
const RECENT_ROWS: usize = 2;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum IntegrationHealth {
    Ready,
    Absent,
    NeedsAttention,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) struct IntegrationStatus {
    pub name: &'static str,
    pub host_found: bool,
    pub health: IntegrationHealth,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ConsoleView {
    Overview,
    Details,
    Integrations,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Tone {
    Normal,
    Good,
    Route,
    Attention,
    Dim,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct VisualRow {
    label: &'static str,
    value: String,
    tone: Tone,
}

#[derive(Debug)]
struct AppState {
    snapshot: Option<DashboardSnapshot>,
    snapshot_error: Option<String>,
    integrations: Option<Vec<IntegrationStatus>>,
    integration_error: Option<String>,
    selected: usize,
    view: ConsoleView,
    color: bool,
    last_refresh: Instant,
}

impl AppState {
    fn new(color: bool) -> Self {
        Self {
            snapshot: None,
            snapshot_error: None,
            integrations: None,
            integration_error: None,
            selected: 0,
            view: ConsoleView::Overview,
            color,
            last_refresh: Instant::now() - REFRESH_INTERVAL,
        }
    }

    fn refresh_snapshot<F>(&mut self, load_snapshot: &mut F)
    where
        F: FnMut() -> Result<DashboardSnapshot>,
    {
        match load_snapshot() {
            Ok(snapshot) => {
                self.selected = self.selected.min(snapshot.sessions.len().saturating_sub(1));
                self.snapshot = Some(snapshot);
                self.snapshot_error = None;
            }
            Err(error) => self.snapshot_error = Some(short_error(&error)),
        }
        self.last_refresh = Instant::now();
    }

    fn refresh_integrations<G>(&mut self, load_integrations: &mut G)
    where
        G: FnMut() -> Result<Vec<IntegrationStatus>>,
    {
        match load_integrations() {
            Ok(integrations) => {
                self.integrations = Some(integrations);
                self.integration_error = None;
            }
            Err(error) => self.integration_error = Some(short_error(&error)),
        }
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

/// Run the provider-free local virtual-memory console.
///
/// Very small or deliberately dumb terminals receive a static card and exit.
/// This avoids presenting keyboard controls that cannot be used safely.
pub fn run<F, G>(mut load_snapshot: F, mut load_integrations: G, color: bool) -> Result<()>
where
    F: FnMut() -> Result<DashboardSnapshot>,
    G: FnMut() -> Result<Vec<IntegrationStatus>>,
{
    let (columns, rows) = terminal::size().unwrap_or((dashboard::terminal_width() as u16, 24));
    let dumb = std::env::var("TERM").is_ok_and(|term| term == "dumb");
    if dumb || columns < MIN_INTERACTIVE_WIDTH || rows < MIN_INTERACTIVE_HEIGHT {
        match load_snapshot() {
            Ok(snapshot) => print!(
                "{}",
                dashboard::render(&snapshot, color, usize::from(columns))
            ),
            Err(error) => print!(
                "{}",
                dashboard::render_error(&short_error(&error), color, usize::from(columns))
            ),
        }
        io::stdout().flush()?;
        return Ok(());
    }

    let guard = TerminalGuard::enter()?;
    let mut terminal = Terminal::new(CrosstermBackend::new(io::stdout()))?;
    let result = panic::catch_unwind(AssertUnwindSafe(|| {
        run_loop(
            &mut terminal,
            &mut load_snapshot,
            &mut load_integrations,
            color,
        )
    }));
    drop(terminal);
    drop(guard);
    match result {
        Ok(result) => result,
        Err(payload) => panic::resume_unwind(payload),
    }
}

fn run_loop<F, G>(
    terminal: &mut Terminal<CrosstermBackend<io::Stdout>>,
    load_snapshot: &mut F,
    load_integrations: &mut G,
    color: bool,
) -> Result<()>
where
    F: FnMut() -> Result<DashboardSnapshot>,
    G: FnMut() -> Result<Vec<IntegrationStatus>>,
{
    let mut state = AppState::new(color);
    state.refresh_snapshot(load_snapshot);
    loop {
        terminal.draw(|frame| render(frame, &state))?;
        if event::poll(POLL_INTERVAL)? {
            match event::read()? {
                Event::Key(key) if should_handle_key(key) => {
                    if handle_key(key, &mut state, load_snapshot, load_integrations) {
                        break;
                    }
                }
                Event::Resize(_, 0) | Event::Resize(0, _) => break,
                _ => {}
            }
        }
        if state.last_refresh.elapsed() >= REFRESH_INTERVAL {
            state.refresh_snapshot(load_snapshot);
            if state.view == ConsoleView::Integrations {
                state.refresh_integrations(load_integrations);
            }
        }
    }
    Ok(())
}

fn should_handle_key(key: KeyEvent) -> bool {
    matches!(key.kind, KeyEventKind::Press | KeyEventKind::Repeat)
}

fn handle_key<F, G>(
    key: KeyEvent,
    state: &mut AppState,
    load_snapshot: &mut F,
    load_integrations: &mut G,
) -> bool
where
    F: FnMut() -> Result<DashboardSnapshot>,
    G: FnMut() -> Result<Vec<IntegrationStatus>>,
{
    if key.modifiers.contains(KeyModifiers::CONTROL)
        && matches!(key.code, KeyCode::Char('c') | KeyCode::Char('C'))
    {
        return true;
    }
    match key.code {
        KeyCode::Char('q') | KeyCode::Char('Q') | KeyCode::Esc => true,
        KeyCode::Char('r') | KeyCode::Char('R') => {
            state.refresh_snapshot(load_snapshot);
            if state.view == ConsoleView::Integrations {
                state.refresh_integrations(load_integrations);
            }
            false
        }
        KeyCode::Char('d') | KeyCode::Char('D') => {
            state.view = if state.view == ConsoleView::Details {
                ConsoleView::Overview
            } else {
                ConsoleView::Details
            };
            false
        }
        KeyCode::Enter => {
            state.view = ConsoleView::Details;
            false
        }
        KeyCode::Char('i') | KeyCode::Char('I') => {
            if state.view == ConsoleView::Integrations {
                state.view = ConsoleView::Overview;
            } else {
                state.view = ConsoleView::Integrations;
                state.refresh_integrations(load_integrations);
            }
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
    let full = frame.area();
    if full.width < MIN_INTERACTIVE_WIDTH || full.height < 9 {
        render_runtime_narrow(frame, full, state);
        return;
    }

    let area = centered_width(full);
    let top_margin = u16::from(area.height >= 14);
    let content = Rect {
        x: area.x,
        y: area.y.saturating_add(top_margin),
        width: area.width,
        height: area.height.saturating_sub(top_margin),
    };
    let footer_y = content.y + content.height.saturating_sub(1);

    let (title, card) = card_content(state);
    let wanted_card_height = u16::try_from(card.len().saturating_add(2)).unwrap_or(u16::MAX);
    let card_height = wanted_card_height.min(content.height.saturating_sub(2).max(1));
    let card_area = Rect {
        x: content.x,
        y: content.y,
        width: content.width,
        height: card_height,
    };
    frame.render_widget(
        Paragraph::new(card)
            .block(
                Block::default()
                    .borders(Borders::ALL)
                    .border_type(BorderType::Rounded)
                    .title(Line::from(Span::styled(title, heading_style(state.color)))),
            )
            .wrap(Wrap { trim: true }),
        card_area,
    );

    let body_y = card_area
        .y
        .saturating_add(card_area.height)
        .saturating_add(1);
    let body_area = Rect {
        x: content.x,
        y: body_y,
        width: content.width,
        height: footer_y.saturating_sub(body_y),
    };
    if body_area.height > 0 {
        frame.render_widget(
            Paragraph::new(body_lines(state)).wrap(Wrap { trim: true }),
            body_area,
        );
    }
    frame.render_widget(
        Paragraph::new(key_hint(state.view, state.color)),
        Rect {
            x: content.x,
            y: footer_y,
            width: content.width,
            height: 1,
        },
    );
}

fn centered_width(area: Rect) -> Rect {
    let width = if area.width >= 58 {
        area.width.min(MAX_CARD_WIDTH)
    } else {
        area.width
    };
    Rect {
        x: area.x + area.width.saturating_sub(width) / 2,
        y: area.y,
        width,
        height: area.height,
    }
}

fn card_content(state: &AppState) -> (String, Vec<Line<'static>>) {
    if let Some(error) = state.snapshot_error.as_deref() {
        return (
            " azdaja · needs attention ".to_string(),
            error_lines(error, state.color),
        );
    }
    let Some(snapshot) = state.snapshot.as_ref() else {
        return (
            " azdaja · little memory ".to_string(),
            vec![Line::from("status   ○ waking local state")],
        );
    };
    let rows = if state.view == ConsoleView::Overview {
        overview_rows(snapshot, now_secs(), state.selected)
    } else {
        summary_rows(snapshot)
    };
    (
        " azdaja · little memory ".to_string(),
        rows.into_iter()
            .map(|row| row_line(row, state.color))
            .collect(),
    )
}

fn body_lines(state: &AppState) -> Vec<Line<'static>> {
    if let Some(error) = state.snapshot_error.as_deref() {
        return vec![
            Line::from(styled(
                "local state could not be read",
                bad_style(state.color),
            )),
            Line::from(clean(error)),
            Line::from("No model provider was called. Run az doctor for the exact fix."),
        ];
    }
    let Some(snapshot) = state.snapshot.as_ref() else {
        return vec![Line::from("reading owner-only local state…")];
    };
    match state.view {
        ConsoleView::Overview => vec![Line::from(vec![
            Span::styled("next  ", subtle_style(state.color)),
            Span::styled(
                "solo \"question\" -f ./document.txt",
                route_style(state.color),
            ),
            Span::raw(" · list · doctor · help"),
        ])],
        ConsoleView::Details => details_lines(snapshot, state.selected, state.color),
        ConsoleView::Integrations => integration_lines(
            state.integrations.as_deref(),
            state.integration_error.as_deref(),
            state.color,
        ),
    }
}

fn render_runtime_narrow(frame: &mut Frame<'_>, area: Rect, state: &AppState) {
    let lines = if let Some(error) = state.snapshot_error.as_deref() {
        vec![
            Line::from(styled("azdaja ● needs attention", bad_style(state.color))),
            Line::from(clean(error)),
            key_hint(state.view, state.color),
        ]
    } else if let Some(snapshot) = state.snapshot.as_ref() {
        let mut lines = vec![Line::from(styled(
            "azdaja ● awake",
            heading_style(state.color),
        ))];
        for row in summary_rows(snapshot) {
            lines.push(row_line(row, state.color));
        }
        lines.push(key_hint(state.view, state.color));
        lines
    } else {
        vec![Line::from("azdaja ○ waking")]
    };
    frame.render_widget(Paragraph::new(lines).wrap(Wrap { trim: true }), area);
}

fn summary_rows(snapshot: &DashboardSnapshot) -> Vec<VisualRow> {
    let status = if snapshot.observability_degraded {
        VisualRow {
            label: "status",
            value: "● awake · local metrics need attention".to_string(),
            tone: Tone::Attention,
        }
    } else {
        VisualRow {
            label: "status",
            value: "● awake · source stays local".to_string(),
            tone: Tone::Good,
        }
    };
    vec![
        status,
        VisualRow {
            label: "route",
            value: format!(
                "{} · {} · {}",
                clean(&snapshot.default_model),
                clean(&snapshot.provider),
                clean(&snapshot.reasoning)
            ),
            tone: Tone::Route,
        },
        VisualRow {
            label: "nest",
            value: nest_line(snapshot),
            tone: Tone::Normal,
        },
        VisualRow {
            label: "map",
            value: memory_map(snapshot),
            tone: Tone::Normal,
        },
    ]
}

fn overview_rows(snapshot: &DashboardSnapshot, timestamp: u64, selected: usize) -> Vec<VisualRow> {
    let mut rows = summary_rows(snapshot);
    if snapshot.sessions.is_empty() {
        rows.push(VisualRow {
            label: "recent",
            value: "no resident session".to_string(),
            tone: Tone::Dim,
        });
        return rows;
    }

    let visible = visible_session_range(snapshot.sessions.len(), selected);
    for (offset, session) in snapshot.sessions[visible.clone()].iter().enumerate() {
        let index = visible.start + offset;
        rows.push(VisualRow {
            label: if offset == 0 { "recent" } else { "" },
            value: session_summary(
                session,
                &snapshot.default_model,
                timestamp,
                index == selected,
            ),
            tone: if session.busy {
                Tone::Good
            } else {
                Tone::Normal
            },
        });
    }
    let hidden = snapshot.sessions.len().saturating_sub(visible.len());
    if hidden > 0 {
        rows.push(VisualRow {
            label: "",
            value: format!("+{hidden} tucked away"),
            tone: Tone::Dim,
        });
    }
    rows
}

fn visible_session_range(len: usize, selected: usize) -> std::ops::Range<usize> {
    if len <= RECENT_ROWS {
        return 0..len;
    }
    let selected = selected.min(len - 1);
    let start = selected
        .saturating_sub(RECENT_ROWS - 1)
        .min(len - RECENT_ROWS);
    start..start + RECENT_ROWS
}

fn nest_line(snapshot: &DashboardSnapshot) -> String {
    if snapshot.sessions.is_empty() {
        return format!("empty · cold · 0/{} slots", snapshot.max_sessions);
    }
    let active = active_sessions(snapshot);
    let pressure = if snapshot.sessions.len() >= snapshot.max_sessions {
        "full"
    } else if active > 0 {
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

fn details_lines(snapshot: &DashboardSnapshot, selected: usize, color: bool) -> Vec<Line<'static>> {
    let mut lines = vec![
        Line::from(styled(
            "measured details · exact-local",
            heading_style(color),
        )),
        Line::from(format!(
            "telemetry       {}",
            if snapshot.observability_degraded {
                "degraded · core memory remains available"
            } else {
                "healthy · aggregate-only sidecars"
            }
        )),
        Line::from("model boundary  unmeasured · no boundary telemetry recorded"),
        Line::from("coverage        n/a · no evidence-selection contract recorded"),
    ];

    if let Some(session) = snapshot.sessions.get(selected) {
        if let Some(source) = session.source.as_ref() {
            lines.push(Line::from(format!(
                "resident source  {}",
                source_line(source)
            )));
            lines.push(Line::from(entropy_line(source)));
        } else {
            lines.push(Line::from("resident source  unmeasured for this session"));
        }
        lines.push(Line::from(""));
        lines.push(Line::from(styled(
            "selected resident",
            heading_style(color),
        )));
        lines.push(Line::from(format!(
            "{} · {} · updated {} ago",
            clean(&session.id[..session.id.len().min(8)]),
            if session.busy { "running" } else { "idle" },
            human_duration(now_secs().saturating_sub(session.updated))
        )));
        lines.push(Line::from(format!(
            "{} state · {} source load(s) · {}",
            human_bytes(session.state_bytes),
            session.loaded_sources,
            clean(
                session
                    .sub_model
                    .as_deref()
                    .unwrap_or(&snapshot.default_model)
            )
        )));
    } else if let Some(source) = recent_source(snapshot) {
        lines.push(Line::from(format!(
            "recent source    {} · completed run, not resident",
            source_line(source)
        )));
        lines.push(Line::from(entropy_line(source)));
    } else {
        lines.push(Line::from("resident source  none measured yet"));
    }
    lines
}

fn entropy_line(source: &SourceLocalAggregate) -> String {
    format!(
        "byte entropy     {:.1} / 8.0 bits/byte · distribution only, not quality",
        source.byte_entropy_bits()
    )
}

fn integration_lines(
    integrations: Option<&[IntegrationStatus]>,
    error: Option<&str>,
    color: bool,
) -> Vec<Line<'static>> {
    if let Some(error) = error {
        return vec![
            Line::from(styled("integrations need attention", bad_style(color))),
            Line::from(clean(error)),
            Line::from("Run az doctor or name a target with az install <tool>."),
        ];
    }
    let Some(integrations) = integrations else {
        return vec![Line::from("checking local integrations…")];
    };
    let mut lines = vec![Line::from(styled(
        "integrations · validated local state",
        heading_style(color),
    ))];
    for integration in integrations {
        let host = if integration.host_found {
            "found"
        } else {
            "not found"
        };
        let (marker, state, style) = match integration.health {
            IntegrationHealth::Ready => ("●", "ready", good_style(color)),
            IntegrationHealth::Absent => ("·", "not integrated", subtle_style(color)),
            IntegrationHealth::NeedsAttention => ("!", "needs repair", bad_style(color)),
        };
        lines.push(Line::from(vec![
            Span::styled(format!("{marker} {:<10}", integration.name), style),
            Span::raw(format!("{host} · {state}")),
        ]));
    }
    lines.push(Line::from(""));
    lines.push(Line::from(
        "doctor <tool> validates · install <tool> installs or repairs",
    ));
    lines
}

fn error_lines(error: &str, color: bool) -> Vec<Line<'static>> {
    vec![
        Line::from(styled("● needs attention", bad_style(color))),
        Line::from(format!("issue    {}", clean(error))),
        Line::from("fix      az doctor · az help"),
    ]
}

fn row_line(row: VisualRow, color: bool) -> Line<'static> {
    Line::from(vec![
        Span::styled(format!("{:<8} ", row.label), subtle_style(color)),
        Span::styled(row.value, tone_style(row.tone, color)),
    ])
}

fn key_hint(view: ConsoleView, color: bool) -> Line<'static> {
    let text = match view {
        ConsoleView::Overview => {
            "↑/↓ select · Enter inspect · d details · i integrations · r refresh · q quit"
        }
        ConsoleView::Details => "↑/↓ resident · d overview · i integrations · r refresh · q quit",
        ConsoleView::Integrations => "i overview · r refresh · d details · q quit",
    };
    Line::from(Span::styled(text, subtle_style(color)))
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

fn recent_source(snapshot: &DashboardSnapshot) -> Option<&SourceLocalAggregate> {
    snapshot
        .recent_observability
        .runs
        .first()
        .map(|run| &run.source)
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

fn session_summary(
    session: &SessionStatus,
    default_model: &str,
    timestamp: u64,
    selected: bool,
) -> String {
    let pointer = if selected { "›" } else { " " };
    let marker = if session.busy { "●" } else { "○" };
    let state = if session.busy { "running" } else { "idle" };
    let model = session.sub_model.as_deref().unwrap_or(default_model);
    format!(
        "{pointer} {marker} {} {state} {} · {}",
        clean(&session.id[..session.id.len().min(8)]),
        human_duration(timestamp.saturating_sub(session.updated)),
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

fn short_error(error: &anyhow::Error) -> String {
    let clean = clean(&format!("{error:#}"));
    if clean.chars().count() <= 180 {
        clean
    } else {
        let mut value = clean.chars().take(179).collect::<String>();
        value.push('…');
        value
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

fn route_style(color: bool) -> Style {
    Style::default().fg(if color { Color::Cyan } else { Color::Reset })
}

fn good_style(color: bool) -> Style {
    Style::default().fg(if color { Color::Green } else { Color::Reset })
}

fn bad_style(color: bool) -> Style {
    if color {
        Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)
    } else {
        Style::default().add_modifier(Modifier::BOLD)
    }
}

fn tone_style(tone: Tone, color: bool) -> Style {
    match tone {
        Tone::Normal => Style::default(),
        Tone::Good => good_style(color),
        Tone::Route => route_style(color),
        Tone::Attention => bad_style(color),
        Tone::Dim => subtle_style(color),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use azdaja::observability::{
        EvidenceTier, ObservabilityPrivacyContract, RecentAggregateSummary, RecentRunAggregate,
        RunKind,
    };
    use std::path::PathBuf;

    fn source() -> SourceLocalAggregate {
        SourceLocalAggregate {
            evidence_tier: EvidenceTier::ExactLocal,
            source_bytes: 2_400_000,
            utf8_chars: 182_000,
            physical_lines: 9_421,
            nonempty_lines: 8_900,
            byte_entropy_millibits: 4_812,
        }
    }

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
                    source: Some(source()),
                    loaded_sources: 1,
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
            recent_observability: RecentAggregateSummary::empty(),
            observability_degraded: false,
        }
    }

    #[test]
    fn overview_is_compact_cute_and_free_of_badge_clutter() {
        let rows = overview_rows(&snapshot(), 1000, 0);
        let text = rows
            .iter()
            .map(|row| format!("{} {}", row.label, row.value))
            .collect::<Vec<_>>()
            .join("\n");
        assert!(rows.len() <= 7);
        assert!(text.contains("status ● awake · source stays local"));
        assert!(text.contains("route gpt-5.6-luna · openai · medium"));
        assert!(text.contains("nest 1.5 MiB resident state · warm · 2/4 slots"));
        assert!(text.contains("map ●○··"));
        assert!(text.contains("█████"));
        assert!(text.contains("▒▒▒▒▒"));
        assert!(text.contains("░░░░░"));
        assert!(!text.contains("[exact-local]"));
        assert!(!text.contains("coverage"));
    }

    #[test]
    fn empty_state_teaches_one_action_without_claiming_resident_source() {
        let mut empty = snapshot();
        empty.sessions.clear();
        let rows = overview_rows(&empty, 1000, 0);
        let text = rows
            .iter()
            .map(|row| format!("{} {}", row.label, row.value))
            .collect::<Vec<_>>()
            .join("\n");
        assert!(text.contains("empty · cold · 0/4 slots"));
        assert!(text.contains("····"));
        assert!(text.contains("no resident session"));
        assert!(!text.contains("recent source"));
    }

    #[test]
    fn recent_completed_source_is_not_misrepresented_as_resident() {
        let mut data = snapshot();
        data.sessions.clear();
        data.recent_observability = RecentAggregateSummary {
            schema_version: 1,
            updated_unix: 1000,
            max_recent_runs: 24,
            privacy: ObservabilityPrivacyContract::default(),
            runs: vec![RecentRunAggregate {
                kind: RunKind::SoloLoad,
                observed_unix: 1000,
                source: source(),
            }],
        };
        assert!(nest_line(&data).starts_with("empty · cold"));
        let details = details_lines(&data, 0, false)
            .into_iter()
            .map(|line| line.to_string())
            .collect::<Vec<_>>()
            .join("\n");
        assert!(details.contains("completed run, not resident"));
    }

    #[test]
    fn details_put_entropy_behind_a_caveat_and_hide_internal_paths() {
        let text = details_lines(&snapshot(), 0, false)
            .into_iter()
            .map(|line| line.to_string())
            .collect::<Vec<_>>()
            .join("\n");
        assert!(text.contains("4.8 / 8.0 bits/byte"));
        assert!(text.contains("distribution only, not quality"));
        assert!(text.contains("model boundary  unmeasured"));
        assert!(!text.contains("/private/state"));
    }

    #[test]
    fn hidden_residents_are_disclosed_without_expanding_the_card() {
        let mut data = snapshot();
        data.sessions.extend([
            SessionStatus {
                id: "aaaaaaaaaaaaaaaa".into(),
                created: 700,
                updated: 700,
                sub_model: None,
                busy: false,
                state_bytes: 1,
                source: None,
                loaded_sources: 0,
            },
            SessionStatus {
                id: "bbbbbbbbbbbbbbbb".into(),
                created: 600,
                updated: 600,
                sub_model: None,
                busy: false,
                state_bytes: 1,
                source: None,
                loaded_sources: 0,
            },
        ]);
        let rows = overview_rows(&data, 1000, 3);
        assert!(rows.len() <= 7);
        assert!(rows.iter().any(|row| row.value == "+2 tucked away"));
        assert!(rows.iter().any(|row| row.value.contains("bbbbbbbb")));
    }

    #[test]
    fn degraded_telemetry_is_visible_but_does_not_claim_core_failure() {
        let mut data = snapshot();
        data.observability_degraded = true;
        let rows = summary_rows(&data);
        assert!(rows[0].value.contains("metrics need attention"));
        let details = details_lines(&data, 0, false)
            .into_iter()
            .map(|line| line.to_string())
            .collect::<Vec<_>>()
            .join("\n");
        assert!(details.contains("core memory remains available"));
    }

    #[test]
    fn integration_view_distinguishes_host_and_managed_state() {
        let statuses = [
            IntegrationStatus {
                name: "jcode",
                host_found: true,
                health: IntegrationHealth::Ready,
            },
            IntegrationStatus {
                name: "gemini",
                host_found: false,
                health: IntegrationHealth::Absent,
            },
            IntegrationStatus {
                name: "codex",
                host_found: true,
                health: IntegrationHealth::NeedsAttention,
            },
        ];
        let text = integration_lines(Some(&statuses), None, false)
            .into_iter()
            .map(|line| line.to_string())
            .collect::<Vec<_>>()
            .join("\n");
        assert!(text.contains("jcode     found · ready"));
        assert!(text.contains("gemini    not found · not integrated"));
        assert!(text.contains("codex     found · needs repair"));
    }

    #[test]
    fn centered_card_clamps_to_the_jcode_like_width() {
        let centered = centered_width(Rect::new(0, 0, 140, 30));
        assert_eq!(centered.width, 78);
        assert_eq!(centered.x, 31);
        let narrow = centered_width(Rect::new(0, 0, 56, 30));
        assert_eq!(narrow.width, 56);
        assert_eq!(narrow.x, 0);
    }

    #[test]
    fn control_sequences_are_removed_from_snapshot_strings() {
        let mut data = snapshot();
        data.default_model = "bad\x1b[2J\nmodel".into();
        let text = summary_rows(&data)
            .into_iter()
            .map(|row| row.value)
            .collect::<Vec<_>>()
            .join("\n");
        assert!(text.contains("bad[2Jmodel"));
        assert!(!text.contains("\x1b"));
    }
}
