/// azdaja banner — indexed sprite, half-block truecolor renderer
const PAL: [(u8, u8, u8); 5] = [
    (0, 0, 0),      // 0 transparent
    (92, 14, 14),   // 1 blood   #5C0E0E  spear
    (162, 28, 28),  // 2 crimson #A21C1C  dragon
    (224, 59, 47),  // 3 bright  #E03B2F  tongue
    (200, 160, 80), // 4 gold    #C8A050  sun
];

#[rustfmt::skip]
const SPRITE: [&str; 32] = [
    "00000000000011100000000000",
    "00000000000011110000000000",
    "00000000000111111000000000",
    "00000000024411110000000000",
    "00000004222412140000000000",
    "00000042222222222200000000",
    "00000442211222222200000000",
    "00000442222222222200000000",
    "00004442222222222222222000",
    "00004442222222222222222220",
    "00004422224412220333333300",
    "00004422224412122222222000",
    "00004442222212144440000000",
    "00000444222222144400000000",
    "00000444422222144400000000",
    "00000044442222224000000000",
    "00000004444422222200000000",
    "00000000044412222220000000",
    "00000000000022222200000000",
    "00000000022222220000000000",
    "00000000222222100000000000",
    "00000002222012100000000000",
    "00000000222222100000000000",
    "00000000002222200000000000",
    "00000000000022222000000000",
    "00000000000012222200000000",
    "00000000000012100220000000",
    "00000000000012100000000000",
    "00000000000012100000000000",
    "00000000000012100000000000",
    "00000000000111110000000000",
    "00000000000011100000000000",
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
        assert_eq!(PAL.len(), 5);
        assert_eq!(
            PAL,
            [
                (0, 0, 0),
                (92, 14, 14),
                (162, 28, 28),
                (224, 59, 47),
                (200, 160, 80),
            ]
        );
        assert_eq!(SPRITE.len(), 32);
        assert!(SPRITE.iter().all(|row| row.len() == 26));
        assert!(
            SPRITE
                .iter()
                .flat_map(|row| row.bytes())
                .all(|value| { value.is_ascii_digit() && usize::from(value - b'0') < PAL.len() })
        );
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
