use anyhow::Result;
use azdaja::{
    DashboardSnapshot, SessionStatus,
    observability::{MemoryConstellation, RecentRunAggregate, RunKind, SourceLocalAggregate},
};
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
const RECENT_ROWS: usize = 1;

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
    Accent,
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
                let selectable = if snapshot.sessions.is_empty() {
                    snapshot.recent_observability.runs.len()
                } else {
                    snapshot.sessions.len()
                };
                self.selected = self.selected.min(selectable.saturating_sub(1));
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
        let selectable = if snapshot.sessions.is_empty() {
            snapshot.recent_observability.runs.len()
        } else {
            snapshot.sessions.len()
        };
        if selectable == 0 {
            self.selected = 0;
            return;
        }
        let last = selectable - 1;
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
                Event::Key(key)
                    if should_handle_key(key)
                        && handle_key(key, &mut state, load_snapshot, load_integrations) =>
                {
                    break;
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
        Paragraph::new(key_hint(
            state.view,
            history_is_selected(state),
            state.color,
        )),
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
            " azdaja · memory constellation ".to_string(),
            vec![Line::from("status   ○ waking local state")],
        );
    };
    let rows = if state.view == ConsoleView::Overview {
        overview_rows(snapshot, now_secs(), state.selected)
    } else {
        summary_rows(snapshot)
    };
    (
        " azdaja · memory constellation ".to_string(),
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
        ConsoleView::Overview => constellation_lines(snapshot, state.selected, state.color),
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
            key_hint(state.view, history_is_selected(state), state.color),
        ]
    } else if let Some(snapshot) = state.snapshot.as_ref() {
        let mut lines = vec![Line::from(styled(
            "azdaja · memory constellation",
            heading_style(state.color),
        ))];
        for row in summary_rows(snapshot) {
            lines.push(row_line(row, state.color));
        }
        lines.push(key_hint(
            state.view,
            history_is_selected(state),
            state.color,
        ));
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
            label: "scope",
            value: clean(&snapshot.scope),
            tone: Tone::Dim,
        },
        VisualRow {
            label: "new work",
            value: new_work_line(snapshot),
            tone: Tone::Accent,
        },
        VisualRow {
            label: "live",
            value: live_line(snapshot),
            tone: Tone::Normal,
        },
        VisualRow {
            label: "memory",
            value: memory_line(snapshot),
            tone: Tone::Normal,
        },
        VisualRow {
            label: "pattern",
            value: pattern_line(snapshot),
            tone: Tone::Dim,
        },
    ]
}

fn overview_rows(snapshot: &DashboardSnapshot, timestamp: u64, selected: usize) -> Vec<VisualRow> {
    let mut rows = summary_rows(snapshot);
    rows.push(VisualRow {
        label: "recent",
        value: recent_summary_line(
            snapshot,
            timestamp,
            if snapshot.sessions.is_empty() {
                selected
            } else {
                0
            },
        )
        .unwrap_or_else(|| "no source summary yet".to_owned()),
        tone: Tone::Dim,
    });
    if snapshot.sessions.is_empty() {
        return rows;
    }

    let visible = visible_session_range(snapshot.sessions.len(), selected);
    for (offset, session) in snapshot.sessions[visible.clone()].iter().enumerate() {
        let index = visible.start + offset;
        rows.push(VisualRow {
            label: "",
            value: session_summary(session, timestamp, index == selected),
            tone: if session.busy {
                Tone::Good
            } else {
                Tone::Normal
            },
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

fn new_work_line(snapshot: &DashboardSnapshot) -> String {
    let model = clean(snapshot.default_model.trim());
    let model = if model.is_empty() {
        "model unknown".to_owned()
    } else {
        model
    };
    let runner = clean(snapshot.provider.trim());
    let runner = if runner.is_empty() {
        "runner unknown".to_owned()
    } else {
        runner
    };
    let mut line = format!("{model} via {runner}");
    let reasoning = clean(snapshot.reasoning.trim());
    match reasoning.to_ascii_lowercase().as_str() {
        "" | "unknown" => {}
        "none" | "off" => line.push_str(" · thinking off"),
        _ => line.push_str(&format!(" · {reasoning} thinking")),
    }
    line
}

fn known_value(value: &str) -> Option<&str> {
    let value = value.trim();
    if value.is_empty()
        || matches!(
            value.to_ascii_lowercase().as_str(),
            "unknown" | "unset" | "none" | "n/a"
        )
    {
        None
    } else {
        Some(value)
    }
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
    let active = active_sessions(snapshot);
    let idle = used.saturating_sub(active);
    format!(
        "{active} running · {idle} idle · {used}/{} slots used",
        snapshot.max_sessions
    )
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
    let Some(constellation) = memory_constellation(snapshot) else {
        return "none yet · summaries keep numbers, not source text".to_owned();
    };
    format!(
        "{} · {} measured · numbers only",
        summary_count(constellation.trace_count),
        human_bytes(constellation.total_source_bytes)
    )
}

fn summary_count(count: usize) -> String {
    format!(
        "{count} source {}",
        if count == 1 { "summary" } else { "summaries" }
    )
}

fn percent(millipercent: u16) -> u32 {
    (u32::from(millipercent.min(1000)) * 100 + 500) / 1000
}

fn pattern_line(snapshot: &DashboardSnapshot) -> String {
    match memory_constellation(snapshot) {
        Some(constellation) => format!(
            "repeated ← {} → varied · avg variety {}%",
            constellation.render_strip(18),
            100 - percent(constellation.zero_order_redundancy_millipercent())
        ),
        None => "appears after the first source".to_owned(),
    }
}

fn variety_percent_from_entropy(byte_entropy_millibits: u16) -> u32 {
    (u32::from(byte_entropy_millibits.min(8000)) * 100 + 4000) / 8000
}

fn constellation_lines(
    snapshot: &DashboardSnapshot,
    selected: usize,
    color: bool,
) -> Vec<Line<'static>> {
    let mut lines = Vec::new();
    if let Some(constellation) = memory_constellation(snapshot) {
        lines.push(Line::from(styled(
            "source size ↑ · local numeric summaries",
            heading_style(color),
        )));
        let labels = ["≥16 MiB", "≥1 MiB", "≥64 KiB", "<64 KiB"];
        let selected_trace = if snapshot.sessions.is_empty() {
            selected
        } else {
            0
        };
        for (label, row) in labels
            .into_iter()
            .zip(constellation.render_grid_selected(24, selected_trace))
        {
            lines.push(Line::from(vec![
                Span::styled(format!("{label:<9} "), subtle_style(color)),
                Span::raw(row),
            ]));
        }
        lines.push(Line::from("          repeated ← source variety → varied"));
        lines.push(Line::from(
            "          ● selected/newest · ○ earlier · 2 overlap",
        ));
        lines.push(Line::from("each point is one local numeric source summary"));
    } else {
        lines.push(Line::from(styled(
            "no local numeric source summaries yet",
            subtle_style(color),
        )));
    }
    lines.push(Line::from(
        "summaries contain no source text, paths, prompts, or answers",
    ));
    lines.push(Line::from(vec![
        Span::styled("next  ", subtle_style(color)),
        Span::styled("solo \"question\" -f ./document.txt", accent_style(color)),
        Span::raw(" · list · memory · doctor · help"),
    ]));
    lines
}

fn recent_summary_line(
    snapshot: &DashboardSnapshot,
    timestamp: u64,
    selected: usize,
) -> Option<String> {
    let run = snapshot.recent_observability.runs.get(selected)?;
    let kind = match run.kind {
        RunKind::SessionLoad | RunKind::SoloLoad => "loaded",
        RunKind::SessionFinal | RunKind::SoloFinal => "finished",
    };
    Some(format!(
        "{kind} · {} · {} lines · {} ago",
        human_bytes(run.source.source_bytes),
        run.source.physical_lines,
        human_duration(timestamp.saturating_sub(run.observed_unix))
    ))
}

fn details_lines(snapshot: &DashboardSnapshot, selected: usize, color: bool) -> Vec<Line<'static>> {
    let mut lines = vec![
        Line::from(styled(
            "measured details · local numeric summaries",
            heading_style(color),
        )),
        Line::from(format!(
            "telemetry       {}",
            if snapshot.observability_degraded {
                "degraded · live work remains available"
            } else {
                "healthy · numeric summaries available"
            }
        )),
        Line::from("privacy         summaries contain no source text, paths, prompts, or answers"),
        Line::from("model boundary  unmeasured · no boundary telemetry recorded"),
        Line::from("coverage        n/a · no evidence-selection contract recorded"),
    ];

    if let Some(session) = snapshot.sessions.get(selected) {
        if let Some(source) = session.source.as_ref() {
            lines.push(Line::from(format!(
                "source summary   {}",
                source_line(source)
            )));
            lines.push(Line::from(entropy_line(source)));
            lines.push(Line::from(variety_line(source)));
            lines.push(Line::from(repetition_line(source)));
            lines.push(Line::from(line_density_line(source)));
        } else {
            lines.push(Line::from("source summary   unmeasured for this live work"));
        }
        lines.push(Line::from(""));
        lines.push(Line::from(styled(
            "selected live work",
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
            session_model(session)
        )));
    } else if let Some(run) = snapshot.recent_observability.runs.get(selected) {
        let source = &run.source;
        let state = if matches!(run.kind, RunKind::SessionFinal | RunKind::SoloFinal) {
            "finished"
        } else {
            "loaded"
        };
        lines.push(Line::from(format!(
            "recent summary  {} · {state}",
            source_line(source),
        )));
        lines.push(Line::from(entropy_line(source)));
        lines.push(Line::from(variety_line(source)));
        lines.push(Line::from(repetition_line(source)));
        lines.push(Line::from(line_density_line(source)));
    } else {
        lines.push(Line::from("source summary   none measured yet"));
    }
    lines
}

fn entropy_line(source: &SourceLocalAggregate) -> String {
    format!(
        "entropy         {:.1} / 8 bits · higher means more byte variety",
        source.byte_entropy_bits(),
    )
}

fn variety_line(source: &SourceLocalAggregate) -> String {
    format!(
        "variety         {}% · distribution only, not quality",
        variety_percent_from_entropy(source.byte_entropy_millibits)
    )
}

fn repetition_line(source: &SourceLocalAggregate) -> String {
    format!(
        "repetition      {}% · estimate, not file compression",
        100u32.saturating_sub(variety_percent_from_entropy(source.byte_entropy_millibits))
    )
}

fn line_density_line(source: &SourceLocalAggregate) -> String {
    let density = if source.physical_lines == 0 {
        0
    } else {
        ((u128::from(source.nonempty_lines.min(source.physical_lines)) * 100
            + u128::from(source.physical_lines / 2))
            / u128::from(source.physical_lines)) as u32
    };
    let mean = if source.physical_lines == 0 {
        0.0
    } else {
        source.utf8_chars as f64 / source.physical_lines as f64
    };
    format!(
        "line density    {}% nonempty · {mean:.1} chars per line",
        density
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

fn history_is_selected(state: &AppState) -> bool {
    state.snapshot.as_ref().is_some_and(|snapshot| {
        snapshot.sessions.is_empty() && !snapshot.recent_observability.runs.is_empty()
    })
}

fn key_hint(view: ConsoleView, history_selected: bool, color: bool) -> Line<'static> {
    let text = match view {
        ConsoleView::Overview => {
            "↑/↓ select · Enter inspect · d details · i integrations · r refresh · q quit"
        }
        ConsoleView::Details if history_selected => {
            "↑/↓ summary · d overview · i integrations · r refresh · q quit"
        }
        ConsoleView::Details => "↑/↓ work · d overview · i integrations · r refresh · q quit",
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

fn source_line(source: &SourceLocalAggregate) -> String {
    format!(
        "{} · {} chars · {} lines · {} nonempty",
        human_bytes(source.source_bytes),
        source.utf8_chars,
        source.physical_lines,
        source.nonempty_lines
    )
}

fn session_summary(session: &SessionStatus, timestamp: u64, selected: bool) -> String {
    let pointer = if selected { "›" } else { " " };
    let marker = if session.busy { "●" } else { "○" };
    let state = if session.busy { "running" } else { "idle" };
    format!(
        "{pointer} {marker} {} {state} {} · {}",
        clean(&session.id[..session.id.len().min(8)]),
        human_duration(timestamp.saturating_sub(session.updated)),
        session_model(session),
    )
}

fn session_model(session: &SessionStatus) -> String {
    session
        .sub_model
        .as_deref()
        .and_then(known_value)
        .map(|model| format!("default {}", clean(model)))
        .unwrap_or_else(|| "default model unknown".to_owned())
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

fn accent_style(color: bool) -> Style {
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
        Tone::Accent => accent_style(color),
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
    use ratatui::{Terminal, backend::TestBackend};
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
        let mut recent_observability = RecentAggregateSummary::empty();
        recent_observability.updated_unix = 990;
        recent_observability.runs = vec![RecentRunAggregate {
            kind: RunKind::SoloFinal,
            observed_unix: 980,
            source: SourceLocalAggregate {
                evidence_tier: EvidenceTier::ExactLocal,
                source_bytes: 64_000,
                utf8_chars: 60_000,
                physical_lines: 1_000,
                nonempty_lines: 800,
                byte_entropy_millibits: 3_000,
            },
        }];
        DashboardSnapshot {
            scope: "azdaja · current folder".into(),
            default_model: "gpt-5.6-sol".into(),
            provider: "Jcode/OpenAI".into(),
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
            recent_scopes: Vec::new(),
        }
    }

    fn rows_text(rows: Vec<VisualRow>) -> String {
        rows.into_iter()
            .map(|row| format!("{} {}", row.label, row.value))
            .collect::<Vec<_>>()
            .join("\n")
    }

    fn lines_text(lines: Vec<Line<'static>>) -> String {
        lines
            .into_iter()
            .map(|line| line.to_string())
            .collect::<Vec<_>>()
            .join("\n")
    }

    fn rendered_text(data: DashboardSnapshot, width: u16, height: u16) -> String {
        let backend = TestBackend::new(width, height);
        let mut terminal = Terminal::new(backend).unwrap();
        let mut state = AppState::new(false);
        state.snapshot = Some(data);
        terminal.draw(|frame| render(frame, &state)).unwrap();
        let buffer = terminal.backend().buffer();
        (0..height)
            .map(|y| {
                let mut line = String::new();
                for x in 0..width {
                    line.push_str(buffer[(x, y)].symbol());
                }
                line.trim_end().to_owned()
            })
            .collect::<Vec<_>>()
            .join("\n")
    }

    #[test]
    fn truly_empty_overview_has_plain_rows_without_fake_measurements() {
        let mut data = snapshot();
        data.sessions.clear();
        data.recent_observability = RecentAggregateSummary::empty();
        let rows = overview_rows(&data, 1000, 0);
        assert_eq!(
            rows.iter().map(|row| row.label).collect::<Vec<_>>(),
            [
                "status", "scope", "new work", "live", "memory", "pattern", "recent",
            ]
        );
        let text = rows_text(rows);
        assert!(text.contains("new work gpt-5.6-sol via Jcode/OpenAI · medium thinking"));
        assert!(text.contains("live none · 4 slots free"));
        assert!(text.contains("memory none yet · summaries keep numbers, not source text"));
        assert!(text.contains("pattern appears after the first source"));
        assert!(text.contains("recent no source summary yet"));
        assert!(!text.contains("avg variety 0%"));
    }

    #[test]
    fn history_only_overview_reports_finished_and_loaded_summaries_plainly() {
        let mut data = snapshot();
        data.sessions.clear();
        let finished = rows_text(overview_rows(&data, 1000, 0));
        assert!(finished.contains("1 source summary · 62.5 KiB measured · numbers only"));
        assert!(finished.contains("recent finished · 62.5 KiB · 1000 lines · 20s ago"));

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
        let loaded = rows_text(overview_rows(&data, 1000, 0));
        assert!(loaded.contains("1 source summary · 2.3 MiB measured · numbers only"));
        assert!(loaded.contains("recent loaded · 2.3 MiB · 9421 lines · 0s ago"));
    }

    #[test]
    fn active_mixed_model_sessions_show_persisted_defaults_without_fallback() {
        let data = snapshot();
        let first = rows_text(overview_rows(&data, 1000, 0));
        assert!(first.contains("live 1 running · 1 idle · 2/4 slots used"));
        assert!(first.contains("01234567 running 10s · default model unknown"));
        assert!(!first.contains("01234567 running 10s · default gpt-5.6-sol"));

        let second = rows_text(overview_rows(&data, 1000, 1));
        assert!(second.contains("fedcba98 idle 2m · default small-model"));
        let details = lines_text(details_lines(&data, 1, false));
        assert!(details.contains("default small-model"));
    }

    #[test]
    fn new_work_uses_the_authoritative_runner_label_and_known_thinking_only() {
        let mut data = snapshot();
        data.provider = "Claude CLI".into();
        assert_eq!(
            new_work_line(&data),
            "gpt-5.6-sol via Claude CLI · medium thinking"
        );
        data.reasoning = "unknown".into();
        assert_eq!(new_work_line(&data), "gpt-5.6-sol via Claude CLI");
        data.reasoning = "off".into();
        assert_eq!(
            new_work_line(&data),
            "gpt-5.6-sol via Claude CLI · thinking off"
        );
    }

    #[test]
    fn narrow_runtime_keeps_the_title_and_plain_summary_rows() {
        let text = rendered_text(snapshot(), 48, 16);
        assert!(text.contains("azdaja · memory constellation"));
        assert!(text.contains("new work"));
        assert!(text.contains("live"));
        assert!(text.contains("memory"));
        assert!(text.contains("pattern"));
        assert!(!text.contains("route"));
    }

    #[test]
    fn constellation_is_a_minimal_labeled_source_summary_graph() {
        let text = lines_text(constellation_lines(&snapshot(), 0, false));
        assert!(text.contains("source size ↑ · local numeric summaries"));
        for label in ["≥16 MiB", "≥1 MiB", "≥64 KiB", "<64 KiB"] {
            assert!(text.contains(label));
        }
        assert!(text.contains("repeated ← source variety → varied"));
        assert!(text.contains("● selected/newest · ○ earlier · 2 overlap"));
        assert!(text.contains("each point is one local numeric source summary"));
        assert!(text.contains("summaries contain no source text, paths, prompts, or answers"));
    }

    #[test]
    fn details_translate_entropy_and_scope_privacy_to_summaries() {
        let text = lines_text(details_lines(&snapshot(), 0, false));
        assert!(text.contains("entropy         4.8 / 8 bits · higher means more byte variety"));
        assert!(text.contains("variety         60% · distribution only, not quality"));
        assert!(text.contains("repetition      40% · estimate, not file compression"));
        assert!(text.contains("line density"));
        assert!(
            text.contains("94% nonempty · 19.3 chars per line"),
            "{text}"
        );
        assert!(text.contains("summaries contain no source text, paths, prompts, or answers"));
        assert!(text.contains("selected live work"));
        assert!(text.contains("default model unknown"));
        assert!(!text.contains("effective"));
        assert!(!text.contains("2^"));
        assert!(!text.contains("/private/state"));
        assert!(!text.contains("live session state contains no source"));
    }

    #[test]
    fn overview_has_no_forbidden_jargon_or_metric_headlines() {
        let text = rows_text(overview_rows(&snapshot(), 1000, 0)).to_lowercase();
        for forbidden in [
            "route",
            "nest",
            "resident",
            "cold",
            "warm",
            "trace",
            "observed",
            "h₀",
            "entropy",
            "redundancy",
        ] {
            assert!(
                !text.contains(forbidden),
                "overview contained {forbidden:?}: {text}"
            );
        }
    }

    #[test]
    fn selection_moves_across_history_and_live_work() {
        let mut history = snapshot();
        history.sessions.clear();
        history.recent_observability.runs.push(RecentRunAggregate {
            kind: RunKind::SessionLoad,
            observed_unix: 900,
            source: source(),
        });
        let mut state = AppState::new(false);
        state.snapshot = Some(history);
        state.move_selection(1);
        assert_eq!(state.selected, 1);

        state.snapshot = Some(snapshot());
        state.selected = 0;
        state.move_selection(1);
        assert_eq!(state.selected, 1);
    }

    #[test]
    fn degraded_telemetry_is_visible_without_claiming_live_work_failed() {
        let mut data = snapshot();
        data.observability_degraded = true;
        let rows = summary_rows(&data);
        assert!(rows[0].value.contains("local metrics need attention"));
        let details = lines_text(details_lines(&data, 0, false));
        assert!(details.contains("degraded · live work remains available"));
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
        let text = lines_text(integration_lines(Some(&statuses), None, false));
        assert!(text.contains("jcode     found · ready"));
        assert!(text.contains("gemini    not found · not integrated"));
        assert!(text.contains("codex     found · needs repair"));
    }

    #[test]
    fn centered_card_preserves_wide_and_narrow_width_behavior() {
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
        data.provider = "custom\x1b[31m\nrunner".into();
        let text = rows_text(summary_rows(&data));
        assert!(text.contains("bad[2Jmodel via custom[31mrunner"));
        assert!(!text.contains('\x1b'));
    }
}
