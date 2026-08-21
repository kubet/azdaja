/// Azdaja banner: a serpent coiled around a pole.
#[rustfmt::skip]
const ART: [&str; 15] = [
    "      ▂",
    "     ▐█▌",
    "   ▄▄▟█▛",
    "  ▐█▙▄█▖",
    "   ▝▜██▙▄",
    "     ▐█▝█▙",
    "     ▐█ ▐█▌",
    "     ▐█▗█▛",
    "   ▄▟██▛▘",
    "  ▐█▛▀█▖",
    "   ▀▙▄█▙▄",
    "     ▐█▝▜█▖",
    "     ▐█  ▀▘",
    "     ▐█▌",
    "      ▔",
];

/// On these rows, the pole passes in front of the serpent.
#[rustfmt::skip]
const POLE_FRONT: [bool; 15] = [
    true, true, false, false, false, true, true, true,
    false, false, false, true, true, true, true,
];

const POLE: &str = "\x1b[38;2;92;14;14m"; // blood #5C0E0E
const SNAKE: &str = "\x1b[38;2;162;28;28m"; // crimson #A21C1C
const DIM: &str = "\x1b[38;2;120;60;60m"; // wordmark
const RESET: &str = "\x1b[0m";

pub fn banner(color: bool) -> String {
    let mut out = String::new();
    for (row_index, row) in ART.iter().enumerate() {
        if color {
            for (column, character) in row.chars().enumerate() {
                if character == ' ' {
                    out.push(' ');
                    continue;
                }
                let pole_is_visible = POLE_FRONT[row_index] && (5..=7).contains(&column);
                out.push_str(if pole_is_visible { POLE } else { SNAKE });
                out.push(character);
            }
            out.push_str(RESET);
        } else {
            out.push_str(row);
        }
        out.push('\n');
    }

    if color {
        out.push_str(DIM);
    }
    out.push_str("   azdaja v");
    out.push_str(env!("CARGO_PKG_VERSION"));
    if color {
        out.push_str(RESET);
    }
    out.push('\n');
    out
}

pub fn color_enabled(is_terminal: bool, no_color: bool, term: Option<&str>) -> bool {
    is_terminal && !no_color && !term.is_some_and(|value| value.eq_ignore_ascii_case("dumb"))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn strip_ansi(text: &str) -> String {
        let bytes = strip_ansi_escapes::strip(text.as_bytes());
        String::from_utf8(bytes).unwrap()
    }

    #[test]
    fn plain_renderer_is_the_exact_art_and_current_version() {
        let expected = format!(
            "{}\n   azdaja v{}\n",
            ART.join("\n"),
            env!("CARGO_PKG_VERSION")
        );
        assert_eq!(banner(false), expected);
        assert_eq!(banner(false).lines().count(), 16);
        assert!(!banner(false).contains('\x1b'));
    }

    #[test]
    fn colored_renderer_preserves_the_plain_glyphs_and_depth_palette() {
        let rendered = banner(true);
        assert_eq!(strip_ansi(&rendered), banner(false));
        assert!(rendered.contains(POLE));
        assert!(rendered.contains(SNAKE));
        assert!(rendered.contains(DIM));
        assert!(rendered.contains(RESET));
        assert!(!rendered.contains("\x1b[m"));
    }

    #[test]
    fn art_and_depth_masks_stay_aligned() {
        assert_eq!(ART.len(), POLE_FRONT.len());
        assert!(ART.iter().all(|row| !row.contains('\n')));
        assert!(
            ART.iter()
                .zip(POLE_FRONT)
                .filter(|(_, pole_front)| *pole_front)
                .all(|(row, _)| row
                    .chars()
                    .enumerate()
                    .any(|(column, character)| { character != ' ' && (5..=7).contains(&column) }))
        );
    }

    #[test]
    fn color_gate_requires_a_capable_terminal() {
        assert!(color_enabled(true, false, Some("xterm-truecolor")));
        assert!(color_enabled(true, false, None));
        assert!(!color_enabled(false, false, Some("xterm-truecolor")));
        assert!(!color_enabled(true, true, Some("xterm-truecolor")));
        assert!(!color_enabled(true, false, Some("dumb")));
        assert!(!color_enabled(true, false, Some("DUMB")));
    }
}
