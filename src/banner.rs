/// azdaja banner — a serpent around a pole, rendered with half blocks
const PAL: [(u8, u8, u8); 3] = [
    (0, 0, 0),      // 0 transparent
    (200, 160, 80), // 1 pole    #C8A050
    (162, 28, 28),  // 2 serpent #A21C1C
];

#[rustfmt::skip]
const SPRITE: [&str; 32] = [
    "000000001000000000",
    "000000001000000000",
    "000000001000222000",
    "000000001002222200",
    "000000001002222000",
    "000000001022200000",
    "000000001222000000",
    "000000002220000000",
    "000000022200000000",
    "000000222000000000",
    "000002221000000000",
    "000022201000000000",
    "000222001000000000",
    "000022201000000000",
    "000002221000000000",
    "000000222000000000",
    "000000022200000000",
    "000000002220000000",
    "000000001222000000",
    "000000001022200000",
    "000000001002220000",
    "000000001000222000",
    "000000001002220000",
    "000000001022200000",
    "000000001222000000",
    "000000002220000000",
    "000000022200000000",
    "000000222000000000",
    "000002221000000000",
    "000000222000000000",
    "000000022000000000",
    "000000001000000000",
];

pub fn banner() -> String {
    let mut out = String::new();
    for pair in SPRITE.chunks(2) {
        let (top, bot) = (pair[0].as_bytes(), pair[1].as_bytes());
        for x in 0..top.len() {
            let (t, b) = ((top[x] - b'0') as usize, (bot[x] - b'0') as usize);
            match (t, b) {
                (0, 0) => out.push(' '),
                (t, 0) => {
                    let c = PAL[t];
                    out.push_str(&format!(
                        "\x1b[38;2;{};{};{}m\u{2580}\x1b[0m",
                        c.0, c.1, c.2
                    ));
                }
                (0, b) => {
                    let c = PAL[b];
                    out.push_str(&format!(
                        "\x1b[38;2;{};{};{}m\u{2584}\x1b[0m",
                        c.0, c.1, c.2
                    ));
                }
                (t, b) => {
                    let (f, g) = (PAL[t], PAL[b]);
                    out.push_str(&format!(
                        "\x1b[38;2;{};{};{}m\x1b[48;2;{};{};{}m\u{2580}\x1b[0m",
                        f.0, f.1, f.2, g.0, g.1, g.2
                    ));
                }
            }
        }
        out.push('\n');
    }
    out
}

pub fn color_enabled(is_terminal: bool, no_color: bool, term: Option<&str>) -> bool {
    is_terminal && !no_color && !term.is_some_and(|value| value.eq_ignore_ascii_case("dumb"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn indexed_sprite_dimensions_palette_and_indices_are_exact() {
        assert_eq!(PAL, [(0, 0, 0), (200, 160, 80), (162, 28, 28)]);
        assert_eq!(SPRITE.len(), 32);
        assert!(SPRITE.iter().all(|row| row.len() == 18));

        let mut counts = [0usize; 3];
        for row in SPRITE {
            assert!(matches!(row.as_bytes()[8], b'1' | b'2'));
            for (x, value) in row.bytes().enumerate() {
                match value {
                    b'0' => counts[0] += 1,
                    b'1' => {
                        assert_eq!(x, 8);
                        counts[1] += 1;
                    }
                    b'2' => counts[2] += 1,
                    _ => panic!("unexpected sprite index {value}"),
                }
            }
        }
        assert_eq!(counts, [466, 21, 89]);
    }

    #[test]
    fn renderer_has_sixteen_rows_truecolor_and_resets() {
        let rendered = banner();
        assert_eq!(rendered.bytes().filter(|value| *value == b'\n').count(), 16);
        assert_eq!(rendered.lines().count(), 16);
        assert!(rendered.contains("\x1b[38;2;"));
        assert!(rendered.contains("\x1b[48;2;"));
        assert!(rendered.contains("\x1b[0m"));
        assert!(rendered.contains('▀') || rendered.contains('▄'));
        assert!(!rendered.contains("\x1b[m"));
    }

    #[test]
    fn color_gate_requires_tty_and_respects_no_color_and_dumb_term() {
        assert!(color_enabled(true, false, Some("xterm-truecolor")));
        assert!(color_enabled(true, false, None));
        assert!(!color_enabled(false, false, Some("xterm-truecolor")));
        assert!(!color_enabled(true, true, Some("xterm-truecolor")));
        assert!(!color_enabled(true, false, Some("dumb")));
        assert!(!color_enabled(true, false, Some("DUMB")));
    }
}
