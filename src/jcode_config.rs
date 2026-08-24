//! Pure, byte-preserving patch planning for Azdaja-managed Jcode hooks.
//!
//! This module does no filesystem I/O. Callers read `JCODE_HOME/config.toml`, pass its
//! bytes (or `None` when absent), and then apply the returned [`PatchPlan`].

use std::{error::Error, fmt};

const MANAGED_KEYS: [&str; 3] = ["pre_tool", "turn_end", "session_end"];
const BEGIN: &str = "# >>> azdaja managed Jcode hooks >>>";
const BEGIN_AFTER_UNTERMINATED: &str =
    "# >>> azdaja managed Jcode hooks; preceding newline is managed >>>";
const END: &str = "# <<< azdaja managed Jcode hooks <<<";
const MARKER_SIGNATURE: &str = "azdaja managed Jcode hooks";

/// The result of planning one config change.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct PatchPlan {
    /// Whether `config.toml` was absent when this plan was made.
    pub original_was_absent: bool,
    /// Whether applying the plan changes the filesystem state.
    pub changed: bool,
    /// Resulting file bytes. `None` means the caller should leave the file absent or remove it.
    pub result: Option<Vec<u8>>,
}

/// A refusal to guess at, overwrite, or remove configuration not owned byte-for-byte.
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum PatchError {
    InvalidManagedBinary(String),
    ConfigIsNotUtf8,
    InvalidToml {
        document: &'static str,
        message: String,
    },
    AmbiguousHooks(String),
    ForeignHook {
        key: &'static str,
        expected: String,
        found: String,
    },
    UnmanagedMatchingHook(&'static str),
    ModifiedManagedBlock(String),
}

impl fmt::Display for PatchError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidManagedBinary(reason) => {
                write!(f, "cannot manage Jcode hooks: {reason}")
            }
            Self::ConfigIsNotUtf8 => write!(
                f,
                "cannot edit Jcode config: config.toml is not valid UTF-8"
            ),
            Self::InvalidToml { document, message } => write!(
                f,
                "cannot edit Jcode config: {document} is not valid TOML: {message}"
            ),
            Self::AmbiguousHooks(reason) => write!(
                f,
                "cannot safely locate the top-level [hooks] table: {reason}; normalize it to one exact [hooks] header and retry"
            ),
            Self::ForeignHook {
                key,
                expected,
                found,
            } => write!(
                f,
                "refusing to overwrite foreign hooks.{key}: expected managed value {expected:?}, found {found:?}; remove or rename that setting and retry"
            ),
            Self::UnmanagedMatchingHook(key) => write!(
                f,
                "refusing to take ownership of hooks.{key}: its value matches, but it is not inside the exact Azdaja-managed block; remove the unmanaged setting and retry"
            ),
            Self::ModifiedManagedBlock(reason) => write!(
                f,
                "refusing to change a customized Azdaja-managed Jcode hook block: {reason}; restore the exact managed block or remove it manually"
            ),
        }
    }
}

impl Error for PatchError {}

/// Plan enabling `pre_tool`, `turn_end`, and `session_end` with one managed command.
///
/// `managed_binary` must be an absolute UTF-8 POSIX, drive-letter, or UNC-style path.
/// The command is shell-word quoted and receives the single argument `jcode-hook`.
pub fn plan_enable(original: Option<&[u8]>, managed_binary: &str) -> Result<PatchPlan, PatchError> {
    let command = managed_command(managed_binary)?;
    let original_was_absent = original.is_none();
    let bytes = original.unwrap_or_default();
    let text = input_text(bytes)?;
    let parsed = parse_toml(text, "input config.toml")?;
    let scan = scan_hooks_headers(text)?;
    let newline = preferred_newline(text);
    let blocks = Blocks::new(&command, newline);

    refuse_modified_markers(text, &blocks, &scan)?;

    if let Some(exact) = locate_exact_managed_block(text, &scan, &blocks)? {
        ensure_managed_values(&parsed, &command, true)?;
        if exact.start <= exact.end {
            return Ok(PatchPlan {
                original_was_absent,
                changed: false,
                result: original.map(ToOwned::to_owned),
            });
        }
    }

    match hooks_table(&parsed) {
        Some(_) => {
            require_one_exact_hooks_header(&scan)?;
            ensure_no_occupied_managed_keys(&parsed, &command)?;
        }
        None => {
            if hooks_entry(&parsed).is_some() {
                return Err(PatchError::AmbiguousHooks(
                    "top-level hooks exists but is not a table".into(),
                ));
            }
            if !scan.exact.is_empty() || !scan.ambiguous.is_empty() {
                return Err(PatchError::AmbiguousHooks(
                    "the textual hooks header does not agree with parsed TOML".into(),
                ));
            }
        }
    }

    let (offset, body) = if hooks_table(&parsed).is_some() {
        let offset = exact_hooks_table_end(&scan, text.len());
        (offset, blocks.keys_for_insertion(&text[..offset]))
    } else {
        (text.len(), blocks.table_for_insertion(text))
    };

    let mut result = Vec::with_capacity(bytes.len() + body.len());
    result.extend_from_slice(&bytes[..offset]);
    result.extend_from_slice(body.as_bytes());
    result.extend_from_slice(&bytes[offset..]);
    validate_output(&result)?;

    Ok(PatchPlan {
        original_was_absent,
        changed: true,
        result: Some(result),
    })
}

/// Plan disabling the exact managed block for `managed_binary`.
///
/// No individual key is removed. If the byte-exact delimited block is not present, foreign or
/// customized hook settings cause an actionable refusal. A config containing no managed keys is
/// an idempotent no-op. Removing a wholly managed file produces `result: None`.
pub fn plan_disable(
    original: Option<&[u8]>,
    managed_binary: &str,
) -> Result<PatchPlan, PatchError> {
    let command = managed_command(managed_binary)?;
    let original_was_absent = original.is_none();
    let Some(bytes) = original else {
        return Ok(PatchPlan {
            original_was_absent: true,
            changed: false,
            result: None,
        });
    };
    let text = input_text(bytes)?;
    let parsed = parse_toml(text, "input config.toml")?;
    let scan = scan_hooks_headers(text)?;
    let newline = preferred_newline(text);
    let blocks = Blocks::new(&command, newline);

    refuse_modified_markers(text, &blocks, &scan)?;

    if let Some(found) = locate_exact_managed_block(text, &scan, &blocks)? {
        ensure_managed_values(&parsed, &command, true)?;
        let mut result = Vec::with_capacity(bytes.len() - (found.end - found.start));
        result.extend_from_slice(&bytes[..found.start]);
        result.extend_from_slice(&bytes[found.end..]);
        if result.is_empty() {
            return Ok(PatchPlan {
                original_was_absent,
                changed: true,
                result: None,
            });
        }
        validate_output(&result)?;
        return Ok(PatchPlan {
            original_was_absent,
            changed: true,
            result: Some(result),
        });
    }

    if hooks_table(&parsed).is_some() {
        require_one_exact_hooks_header(&scan)?;
        ensure_no_occupied_managed_keys(&parsed, &command)?;
    } else if hooks_entry(&parsed).is_some() {
        return Err(PatchError::AmbiguousHooks(
            "top-level hooks exists but is not a table".into(),
        ));
    } else if !scan.exact.is_empty() || !scan.ambiguous.is_empty() {
        return Err(PatchError::AmbiguousHooks(
            "the textual hooks header does not agree with parsed TOML".into(),
        ));
    }

    Ok(PatchPlan {
        original_was_absent,
        changed: false,
        result: Some(bytes.to_vec()),
    })
}

#[derive(Clone, Copy, Debug)]
struct Span {
    start: usize,
    end: usize,
}

#[derive(Debug, Default)]
struct HeaderScan {
    exact: Vec<Span>,
    ambiguous: Vec<String>,
    all_tables: Vec<Span>,
    syntax_line_starts: Vec<usize>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Multiline {
    Basic,
    Literal,
}

fn input_text(bytes: &[u8]) -> Result<&str, PatchError> {
    std::str::from_utf8(bytes).map_err(|_| PatchError::ConfigIsNotUtf8)
}

fn parse_toml(text: &str, document: &'static str) -> Result<toml::Value, PatchError> {
    toml::from_str(text).map_err(|error| PatchError::InvalidToml {
        document,
        message: error.to_string(),
    })
}

fn validate_output(bytes: &[u8]) -> Result<(), PatchError> {
    let text = input_text(bytes)?;
    parse_toml(text, "planned output")?;
    Ok(())
}

fn managed_command(binary: &str) -> Result<String, PatchError> {
    if binary.is_empty() {
        return Err(PatchError::InvalidManagedBinary(
            "the managed binary path is empty".into(),
        ));
    }
    if binary.contains('\0') {
        return Err(PatchError::InvalidManagedBinary(
            "the managed binary path contains NUL".into(),
        ));
    }
    if !is_absolute_portable(binary) {
        return Err(PatchError::InvalidManagedBinary(format!(
            "managed binary path {binary:?} is not absolute"
        )));
    }
    let quoted = shlex::try_quote(binary).map_err(|error| {
        PatchError::InvalidManagedBinary(format!("managed binary path cannot be quoted: {error}"))
    })?;
    Ok(format!("{quoted} jcode-hook"))
}

fn is_absolute_portable(path: &str) -> bool {
    path.starts_with('/')
        || path.as_bytes().get(0..3).is_some_and(|head| {
            head[0].is_ascii_alphabetic() && head[1] == b':' && matches!(head[2], b'/' | b'\\')
        })
        || path.starts_with("\\\\")
        || path.starts_with("//")
}

fn toml_string(value: &str) -> String {
    let mut out = String::with_capacity(value.len() + 2);
    out.push('"');
    for ch in value.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\u{0008}' => out.push_str("\\b"),
            '\t' => out.push_str("\\t"),
            '\n' => out.push_str("\\n"),
            '\u{000C}' => out.push_str("\\f"),
            '\r' => out.push_str("\\r"),
            ch if ch <= '\u{001F}' || ch == '\u{007F}' => {
                use fmt::Write as _;
                write!(out, "\\u{:04X}", ch as u32).expect("writing to String cannot fail");
            }
            ch => out.push(ch),
        }
    }
    out.push('"');
    out
}

fn preferred_newline(text: &str) -> &'static str {
    if text.as_bytes().windows(2).any(|pair| pair == b"\r\n") {
        "\r\n"
    } else {
        "\n"
    }
}

struct Blocks {
    keys: String,
    keys_special: String,
    table: String,
    table_special: String,
    newline: &'static str,
}

impl Blocks {
    fn new(command: &str, newline: &'static str) -> Self {
        let value = toml_string(command);
        let key_lines = MANAGED_KEYS
            .iter()
            .map(|key| format!("{key} = {value}"))
            .collect::<Vec<_>>()
            .join(newline);
        let keys = format!("{BEGIN}{newline}{key_lines}{newline}{END}{newline}");
        let keys_special =
            format!("{BEGIN_AFTER_UNTERMINATED}{newline}{key_lines}{newline}{END}{newline}");
        let table = format!("{BEGIN}{newline}[hooks]{newline}{key_lines}{newline}{END}{newline}");
        let table_special = format!(
            "{BEGIN_AFTER_UNTERMINATED}{newline}[hooks]{newline}{key_lines}{newline}{END}{newline}"
        );
        Self {
            keys,
            keys_special,
            table,
            table_special,
            newline,
        }
    }

    fn keys_for_insertion(&self, prefix: &str) -> String {
        if prefix.is_empty() || prefix.ends_with('\n') || prefix.ends_with('\r') {
            self.keys.clone()
        } else {
            format!("{}{}", self.newline, self.keys_special)
        }
    }

    fn table_for_insertion(&self, prefix: &str) -> String {
        if prefix.is_empty() || prefix.ends_with('\n') || prefix.ends_with('\r') {
            self.table.clone()
        } else {
            format!("{}{}", self.newline, self.table_special)
        }
    }

    fn exact_forms(&self) -> [(&str, bool, bool); 4] {
        [
            (&self.keys, false, false),
            (&self.keys_special, false, true),
            (&self.table, true, false),
            (&self.table_special, true, true),
        ]
    }
}

fn hooks_table(value: &toml::Value) -> Option<&toml::map::Map<String, toml::Value>> {
    hooks_entry(value)?.as_table()
}

fn hooks_entry(value: &toml::Value) -> Option<&toml::Value> {
    value.as_table()?.get("hooks")
}

fn hook_value<'a>(parsed: &'a toml::Value, key: &str) -> Option<&'a toml::Value> {
    hooks_table(parsed)?.get(key)
}

fn ensure_managed_values(
    parsed: &toml::Value,
    command: &str,
    exact_block_claimed: bool,
) -> Result<(), PatchError> {
    for key in MANAGED_KEYS {
        match hook_value(parsed, key).and_then(toml::Value::as_str) {
            Some(found) if found == command => {}
            Some(found) => {
                return Err(PatchError::ForeignHook {
                    key,
                    expected: command.into(),
                    found: found.into(),
                });
            }
            None if hook_value(parsed, key).is_some() => {
                return Err(PatchError::ForeignHook {
                    key,
                    expected: command.into(),
                    found: hook_value(parsed, key).expect("checked").to_string(),
                });
            }
            None if exact_block_claimed => {
                return Err(PatchError::ModifiedManagedBlock(format!(
                    "the exact-looking block does not parse as hooks.{key}"
                )));
            }
            None => {}
        }
    }
    Ok(())
}

fn ensure_no_occupied_managed_keys(parsed: &toml::Value, command: &str) -> Result<(), PatchError> {
    for key in MANAGED_KEYS {
        let Some(value) = hook_value(parsed, key) else {
            continue;
        };
        match value.as_str() {
            Some(found) if found == command => return Err(PatchError::UnmanagedMatchingHook(key)),
            Some(found) => {
                return Err(PatchError::ForeignHook {
                    key,
                    expected: command.into(),
                    found: found.into(),
                });
            }
            None => {
                return Err(PatchError::ForeignHook {
                    key,
                    expected: command.into(),
                    found: value.to_string(),
                });
            }
        }
    }
    Ok(())
}

fn require_one_exact_hooks_header(scan: &HeaderScan) -> Result<(), PatchError> {
    if !scan.ambiguous.is_empty() {
        return Err(PatchError::AmbiguousHooks(scan.ambiguous.join(", ")));
    }
    match scan.exact.len() {
        1 => Ok(()),
        0 => Err(PatchError::AmbiguousHooks(
            "parsed hooks configuration has no exact [hooks] header (it may use a quoted, dotted, array, or inline form)".into(),
        )),
        count => Err(PatchError::AmbiguousHooks(format!(
            "found {count} exact [hooks] headers"
        ))),
    }
}

fn exact_hooks_table_end(scan: &HeaderScan, text_len: usize) -> usize {
    let hooks = scan.exact[0];
    scan.all_tables
        .iter()
        .filter(|header| header.start > hooks.start)
        .map(|header| header.start)
        .min()
        .unwrap_or(text_len)
}

fn locate_exact_managed_block(
    text: &str,
    scan: &HeaderScan,
    blocks: &Blocks,
) -> Result<Option<Span>, PatchError> {
    let mut matches = Vec::new();
    for (form, includes_table, special) in blocks.exact_forms() {
        for (start, _) in text.match_indices(form) {
            if !scan.syntax_line_starts.contains(&start) {
                continue;
            }
            let mut remove_start = start;
            if special {
                let newline_start = start.checked_sub(blocks.newline.len()).filter(|candidate| {
                    &text.as_bytes()[*candidate..start] == blocks.newline.as_bytes()
                });
                let Some(newline_start) = newline_start else {
                    continue;
                };
                remove_start = newline_start;
            }
            let end = start + form.len();
            let valid_location = if includes_table {
                scan.exact
                    .iter()
                    .any(|header| header.start >= start && header.start < end)
            } else {
                scan.exact.iter().any(|header| {
                    let table_end = scan
                        .all_tables
                        .iter()
                        .filter(|candidate| candidate.start > header.start)
                        .map(|candidate| candidate.start)
                        .min()
                        .unwrap_or(text.len());
                    start >= header.end && start < table_end
                })
            };
            if valid_location {
                matches.push(Span {
                    start: remove_start,
                    end,
                });
            }
        }
    }
    matches.sort_by_key(|span| (span.start, span.end));
    matches.dedup_by_key(|span| (span.start, span.end));
    match matches.len() {
        0 => Ok(None),
        1 => Ok(matches.into_iter().next()),
        count => Err(PatchError::ModifiedManagedBlock(format!(
            "found {count} exact managed blocks"
        ))),
    }
}

fn refuse_modified_markers(
    text: &str,
    blocks: &Blocks,
    scan: &HeaderScan,
) -> Result<(), PatchError> {
    let exact_marker_count = [
        blocks.keys.as_str(),
        blocks.keys_special.as_str(),
        blocks.table.as_str(),
        blocks.table_special.as_str(),
    ]
    .into_iter()
    .map(|block| {
        text.match_indices(block)
            .filter(|(start, _)| scan.syntax_line_starts.contains(start))
            .count()
    })
    .sum::<usize>();
    let signature_count = scan
        .syntax_line_starts
        .iter()
        .filter(|start| {
            let line = text[**start..]
                .split_once('\n')
                .map_or(&text[**start..], |(line, _)| line);
            line.trim_start_matches([' ', '\t']).starts_with('#') && line.contains(MARKER_SIGNATURE)
        })
        .count();
    if signature_count > exact_marker_count.saturating_mul(2) {
        return Err(PatchError::ModifiedManagedBlock(
            "managed delimiter text exists, but the complete block is not byte-exact for this binary"
                .into(),
        ));
    }
    Ok(())
}

fn scan_hooks_headers(text: &str) -> Result<HeaderScan, PatchError> {
    let mut scan = HeaderScan::default();
    let mut multiline = None;
    let mut offset = 0;

    for line_with_ending in text.split_inclusive('\n') {
        let line = line_with_ending
            .strip_suffix('\n')
            .unwrap_or(line_with_ending)
            .strip_suffix('\r')
            .unwrap_or_else(|| {
                line_with_ending
                    .strip_suffix('\n')
                    .unwrap_or(line_with_ending)
            });
        if multiline.is_none() {
            scan.syntax_line_starts.push(offset);
            classify_header_line(line, offset, line_with_ending.len(), &mut scan);
        }
        multiline = multiline_after_line(line, multiline);
        offset += line_with_ending.len();
    }
    if offset < text.len() {
        let line = &text[offset..];
        if multiline.is_none() {
            scan.syntax_line_starts.push(offset);
            classify_header_line(line, offset, line.len(), &mut scan);
        }
    }

    if scan.exact.len() > 1 {
        return Err(PatchError::AmbiguousHooks(format!(
            "found {} duplicate exact [hooks] headers",
            scan.exact.len()
        )));
    }
    if !scan.ambiguous.is_empty() {
        return Err(PatchError::AmbiguousHooks(scan.ambiguous.join(", ")));
    }
    Ok(scan)
}

fn classify_header_line(line: &str, offset: usize, line_len: usize, scan: &mut HeaderScan) {
    let trimmed = line.trim_start_matches([' ', '\t']);
    if !trimmed.starts_with('[') {
        return;
    }
    let leading = line.len() - trimmed.len();
    let header = header_token(trimmed).unwrap_or(trimmed);
    if header_token(trimmed).is_some() {
        scan.all_tables.push(Span {
            start: offset + leading,
            end: offset + line_len,
        });
    }
    if header == "[hooks]" {
        scan.exact.push(Span {
            start: offset + leading,
            end: offset + line_len,
        });
    } else if header_mentions_hooks(header) {
        scan.ambiguous
            .push(format!("unsupported header {header:?}"));
    }
}

fn header_token(line: &str) -> Option<&str> {
    let bytes = line.as_bytes();
    let array = bytes.starts_with(b"[[");
    let mut quote = None;
    let mut escaped = false;
    let mut index = if array { 2 } else { 1 };
    while index < bytes.len() {
        let byte = bytes[index];
        if let Some(delimiter) = quote {
            if delimiter == b'"' && escaped {
                escaped = false;
            } else if delimiter == b'"' && byte == b'\\' {
                escaped = true;
            } else if byte == delimiter {
                quote = None;
            }
        } else if matches!(byte, b'"' | b'\'') {
            quote = Some(byte);
        } else if array && byte == b']' && bytes.get(index + 1) == Some(&b']') {
            return Some(&line[..index + 2]);
        } else if !array && byte == b']' {
            return Some(&line[..index + 1]);
        }
        index += 1;
    }
    None
}

fn header_mentions_hooks(header: &str) -> bool {
    let inner = header
        .strip_prefix("[[")
        .and_then(|value| value.strip_suffix("]]"))
        .or_else(|| {
            header
                .strip_prefix('[')
                .and_then(|value| value.strip_suffix(']'))
        })
        .unwrap_or(header);
    inner
        .split('.')
        .any(|component| matches!(component.trim(), "hooks" | "\"hooks\"" | "'hooks'"))
}

fn multiline_after_line(line: &str, mut state: Option<Multiline>) -> Option<Multiline> {
    let bytes = line.as_bytes();
    let mut index = 0;
    let mut single_quote = None;
    let mut escaped = false;
    while index + 2 < bytes.len() {
        if let Some(kind) = state {
            let delimiter = match kind {
                Multiline::Basic => b'"',
                Multiline::Literal => b'\'',
            };
            if bytes[index..].starts_with(&[delimiter, delimiter, delimiter])
                && (kind == Multiline::Literal || !is_escaped(bytes, index))
            {
                state = None;
                index += 3;
                continue;
            }
            index += 1;
            continue;
        }
        if let Some(delimiter) = single_quote {
            let byte = bytes[index];
            if delimiter == b'"' && escaped {
                escaped = false;
            } else if delimiter == b'"' && byte == b'\\' {
                escaped = true;
            } else if byte == delimiter {
                single_quote = None;
            }
            index += 1;
            continue;
        }
        if bytes[index] == b'#' {
            break;
        }
        if bytes[index..].starts_with(b"\"\"\"") {
            state = Some(Multiline::Basic);
            index += 3;
        } else if bytes[index..].starts_with(b"'''") {
            state = Some(Multiline::Literal);
            index += 3;
        } else if matches!(bytes[index], b'"' | b'\'') {
            single_quote = Some(bytes[index]);
            index += 1;
        } else {
            index += 1;
        }
    }
    state
}

fn is_escaped(bytes: &[u8], index: usize) -> bool {
    let mut backslashes = 0;
    let mut cursor = index;
    while cursor > 0 && bytes[cursor - 1] == b'\\' {
        backslashes += 1;
        cursor -= 1;
    }
    backslashes % 2 == 1
}

#[cfg(test)]
mod tests {
    use super::*;

    const BIN: &str = "/Applications/Azdaja Managed/bin/azdaja";

    fn enabled(input: Option<&[u8]>, binary: &str) -> PatchPlan {
        plan_enable(input, binary).expect("enable plan")
    }

    fn bytes(plan: &PatchPlan) -> &[u8] {
        plan.result.as_deref().expect("resulting file")
    }

    #[test]
    fn enables_current_live_hooks_shape_without_touching_timeout() {
        let input = b"[hooks]\npre_tool_timeout_ms = 5000";
        let plan = enabled(Some(input), BIN);
        let output = std::str::from_utf8(bytes(&plan)).unwrap();
        assert!(plan.changed);
        assert!(!plan.original_was_absent);
        assert!(output.starts_with("[hooks]\npre_tool_timeout_ms = 5000\n"));
        assert!(output.contains(BEGIN_AFTER_UNTERMINATED));
        assert_eq!(
            toml::from_str::<toml::Value>(output).unwrap()["hooks"]["pre_tool_timeout_ms"]
                .as_integer(),
            Some(5000)
        );
        let disabled = plan_disable(plan.result.as_deref(), BIN).unwrap();
        assert_eq!(disabled.result.as_deref(), Some(input.as_slice()));
    }

    #[test]
    fn absent_config_creates_and_can_remove_wholly_managed_file() {
        let plan = enabled(None, BIN);
        assert!(plan.original_was_absent);
        assert!(plan.changed);
        let output = std::str::from_utf8(bytes(&plan)).unwrap();
        assert!(output.starts_with(&format!("{BEGIN}\n[hooks]\n")));
        let disabled = plan_disable(plan.result.as_deref(), BIN).unwrap();
        assert!(disabled.changed);
        assert_eq!(disabled.result, None);
        let absent_noop = plan_disable(None, BIN).unwrap();
        assert!(!absent_noop.changed);
        assert!(absent_noop.original_was_absent);
    }

    #[test]
    fn refuses_each_occupied_managed_key() {
        for key in MANAGED_KEYS {
            let input = format!("[hooks]\n{key} = \"foreign\"\n");
            let error = plan_enable(Some(input.as_bytes()), BIN).unwrap_err();
            assert!(matches!(error, PatchError::ForeignHook { key: found, .. } if found == key));
            let error = plan_disable(Some(input.as_bytes()), BIN).unwrap_err();
            assert!(matches!(error, PatchError::ForeignHook { key: found, .. } if found == key));
        }
    }

    #[test]
    fn exact_existing_managed_block_is_idempotent() {
        let first = enabled(Some(b"[hooks]\npre_tool_timeout_ms = 5000\n"), BIN);
        let second = plan_enable(first.result.as_deref(), BIN).unwrap();
        assert!(!second.changed);
        assert_eq!(second.result, first.result);

        let absent = enabled(None, BIN);
        let again = plan_enable(absent.result.as_deref(), BIN).unwrap();
        assert!(!again.changed);
        assert_eq!(again.result, absent.result);
    }

    #[test]
    fn one_byte_customization_refuses_enable_and_disable() {
        let plan = enabled(Some(b"[hooks]\n"), BIN);
        let mut customized = bytes(&plan).to_vec();
        let needle = b"jcode-hook";
        let index = customized
            .windows(needle.len())
            .position(|window| window == needle)
            .unwrap();
        customized[index] = b'J';
        for result in [
            plan_enable(Some(&customized), BIN).map(|_| ()),
            plan_disable(Some(&customized), BIN).map(|_| ()),
        ] {
            assert!(result.is_err());
        }
    }

    #[test]
    fn comments_order_and_unrelated_tables_are_preserved_byte_for_byte() {
        let input = b"# before\nname = \"keep\"\n\n[hooks] # live\n# timeout comment\npre_tool_timeout_ms = 5000\n\n[other]\nvalue = \"unchanged\" # tail\n";
        let plan = enabled(Some(input), BIN);
        let output = bytes(&plan);
        let other = input
            .windows(b"[other]".len())
            .position(|w| w == b"[other]")
            .unwrap();
        let output_other = output
            .windows(b"[other]".len())
            .position(|w| w == b"[other]")
            .unwrap();
        assert_eq!(&output[.."# before\nname = \"keep\"\n\n[hooks] # live\n# timeout comment\npre_tool_timeout_ms = 5000\n\n".len()], &input[..other]);
        assert_eq!(&output[output_other..], &input[other..]);
        let disabled = plan_disable(plan.result.as_deref(), BIN).unwrap();
        assert_eq!(disabled.result.as_deref(), Some(input.as_slice()));
    }

    #[test]
    fn windows_like_and_unicode_paths_are_toml_and_shell_safe() {
        let binary = r#"C:\Program Files\Azdaja's 工具\azdaja.exe"#;
        let plan = enabled(None, binary);
        let output = std::str::from_utf8(bytes(&plan)).unwrap();
        let parsed: toml::Value = toml::from_str(output).unwrap();
        let command = parsed["hooks"]["pre_tool"].as_str().unwrap();
        assert_eq!(
            shlex::split(command),
            Some(vec![binary.into(), "jcode-hook".into()])
        );
        for key in MANAGED_KEYS {
            assert_eq!(parsed["hooks"][key].as_str(), Some(command));
        }
    }

    #[test]
    fn malformed_toml_is_rejected_without_a_plan() {
        let error = plan_enable(Some(b"[hooks\npre_tool = 1"), BIN).unwrap_err();
        assert!(matches!(error, PatchError::InvalidToml { .. }));
        let error = plan_disable(Some(b"x = ["), BIN).unwrap_err();
        assert!(matches!(error, PatchError::InvalidToml { .. }));
    }

    #[test]
    fn ambiguous_hooks_headers_are_rejected() {
        for input in [
            "[\"hooks\"]\npre_tool_timeout_ms = 5000\n",
            "[hooks.extra]\nx = 1\n",
            "[[hooks]]\nx = 1\n",
            "hooks.pre_tool_timeout_ms = 5000\n",
        ] {
            let error = plan_enable(Some(input.as_bytes()), BIN).unwrap_err();
            assert!(matches!(
                error,
                PatchError::AmbiguousHooks(_) | PatchError::InvalidToml { .. }
            ));
        }
        let duplicate = "[hooks]\nx = 1\n[hooks]\ny = 2\n";
        assert!(matches!(
            plan_enable(Some(duplicate.as_bytes()), BIN),
            Err(PatchError::InvalidToml { .. }) | Err(PatchError::AmbiguousHooks(_))
        ));
    }

    #[test]
    fn exact_matching_values_without_delimiters_are_not_claimed() {
        let command = managed_command(BIN).unwrap();
        let value = toml_string(&command);
        let input =
            format!("[hooks]\npre_tool = {value}\nturn_end = {value}\nsession_end = {value}\n");
        assert!(matches!(
            plan_enable(Some(input.as_bytes()), BIN),
            Err(PatchError::UnmanagedMatchingHook(_))
        ));
        assert!(matches!(
            plan_disable(Some(input.as_bytes()), BIN),
            Err(PatchError::UnmanagedMatchingHook(_))
        ));
    }

    #[test]
    fn marker_text_inside_multiline_string_is_not_a_hooks_header() {
        let input = b"message = '''\n[hooks]\n'''\n";
        let plan = enabled(Some(input), BIN);
        let parsed: toml::Value =
            toml::from_str(std::str::from_utf8(bytes(&plan)).unwrap()).unwrap();
        assert_eq!(parsed["message"].as_str(), Some("[hooks]\n"));
        assert!(parsed["hooks"].is_table());
    }

    #[test]
    fn exact_block_text_inside_multiline_string_is_never_claimed() {
        let generated = enabled(None, BIN);
        let block = std::str::from_utf8(bytes(&generated)).unwrap();
        let command = managed_command(BIN).unwrap();
        let value = toml_string(&command);
        let input = format!(
            "message = '''\n{block}'''\n[hooks]\npre_tool = {value}\nturn_end = {value}\nsession_end = {value}\n"
        );
        assert!(matches!(
            plan_enable(Some(input.as_bytes()), BIN),
            Err(PatchError::UnmanagedMatchingHook(_))
        ));
        assert!(matches!(
            plan_disable(Some(input.as_bytes()), BIN),
            Err(PatchError::UnmanagedMatchingHook(_))
        ));
    }

    #[test]
    fn non_table_hooks_value_is_refused_before_appending() {
        for input in ["hooks = \"foreign\"\n", "hooks = [1, 2]\n"] {
            assert!(matches!(
                plan_enable(Some(input.as_bytes()), BIN),
                Err(PatchError::AmbiguousHooks(_))
            ));
            assert!(matches!(
                plan_disable(Some(input.as_bytes()), BIN),
                Err(PatchError::AmbiguousHooks(_))
            ));
        }
    }

    #[test]
    fn crlf_round_trip_preserves_every_original_byte() {
        let input = b"# keep\r\n[hooks]\r\npre_tool_timeout_ms = 5000\r\n[other]\r\nx = 1\r\n";
        let plan = enabled(Some(input), BIN);
        let output = bytes(&plan);
        assert!(output.windows(2).any(|pair| pair == b"\r\n"));
        assert!(
            !output.windows(1).enumerate().any(|(index, byte)| {
                byte == b"\n" && (index == 0 || output[index - 1] != b'\r')
            })
        );
        let disabled = plan_disable(plan.result.as_deref(), BIN).unwrap();
        assert_eq!(disabled.result.as_deref(), Some(input.as_slice()));
    }
}
