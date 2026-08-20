# Azdaja third-party notices

**Candidate:** Azdaja v0.1.2 public content snapshot
**Supported release targets:** `aarch64-apple-darwin`, `x86_64-unknown-linux-gnu`  
**Generated:** `2026-08-20T03:44:21Z` by a strictly local/offline audit  
**Engineering disposition:** supported-target dependency/font notice gate **PASS only when this file accompanies every applicable release artifact**; see obligations and limits below. This is not legal advice.

## Scope and evidence rules

- The package inventory is the exact union of the two supported `cargo tree --locked --offline --target …` closures supplied by the bound audit. It contains **156 registry packages**; the Azdaja root is deliberately excluded from the third-party table.
- All 195 cached registry archives corresponding to `Cargo.lock` records were re-hashed locally and matched their lock checksums. Exactly 156 are in the supported-target union and are the archive scope used below. No network, provider call, install, source edit, candidate edit, or repository edit was used.
- Every path in every one of the 156 in-scope verified archives was enumerated. All path-named legal files (`LICENSE`, `LICENCE`, `COPYING`, `COPYRIGHT`, `NOTICE`, `AUTHORS`, `UNLICENSE`, and variants), detected legal comment/header blocks, supplemental exact README/plain-text legal sections, Unicode data headers, and the embedded BSD test notice are reproduced below. Exact source bytes are deduplicated by SHA-256; occurrences map each text back to package and archive path. Conservative header capture includes build, documentation, benchmark, and test paths, not merely linked release code.
- For syntactically valid SPDX manifest expressions, the canonical ID/name set is bound to local SPDX License List metadata and a complete, exact verified-archive license-text representative. All package-specific license/copyright variants remain separately reproduced. Seven historical slash-form declarations are preserved verbatim and are **not silently normalized as SPDX**.
- A text fence separator is not source content. Each text record states byte length, SHA-256, UTF-8 encoding, and whether the exact source bytes ended with LF; the machine manifest is authoritative for byte boundaries and occurrence maps.
- Bound inputs: `Cargo.lock` SHA-256 `4e2419eaf2f1cf4818dca37950af56a7aedf6a079567357f4b7b72f8dd72066d`; supported-target private addendum SHA-256 `48a84df5f6fada7dfa30d38ca78ef8a0f6a7e4685f0d52f649d073215542021d`; local SPDX metadata `/opt/homebrew/Library/Homebrew/data/spdx/spdx_licenses.json` version `3.28.0`, SHA-256 `f728c534d8bd1044fc515a2ddb2292be99559021d830bfa3281be0bcd36302ee`.

## Exact supported-target third-party union (root excluded)

| Package | Version | Exact manifest declaration | Supported target membership |
|---|---:|---|---|
| `ahash` | `0.8.12` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `aho-corasick` | `1.1.5` | `Unlicense OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `allocator-api2` | `0.2.21` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `anyhow` | `1.0.104` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `arrayvec` | `0.7.8` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `attribute-derive` | `0.10.5` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `attribute-derive-macro` | `0.10.5` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `autocfg` | `1.5.1` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `bit-set` | `0.8.0` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `bit-vec` | `0.8.0` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `bitflags` | `2.13.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `bitvec` | `1.1.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `bstr` | `1.13.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `byteorder` | `1.5.0` | `Unlicense OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `castaway` | `0.2.4` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `cfg-if` | `1.0.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `chrono` | `0.4.45` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `cobs` | `0.3.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `collection_literals` | `1.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `compact_str` | `0.9.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `core-foundation-sys` | `0.8.7` | `MIT OR Apache-2.0` | `aarch64-apple-darwin` |
| `derive-where` | `1.6.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `displaydoc` | `0.2.7` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `either` | `1.17.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `equivalent` | `1.0.2` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `fancy-regex` | `0.17.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `foldhash` | `0.2.0` | `Zlib` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `fs2` | `0.4.3` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `funty` | `2.0.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `get-size-derive2` | `0.10.3` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `get-size2` | `0.10.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `getopts` | `0.2.24` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `getrandom` | `0.2.17` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `getrandom` | `0.3.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `hash32` | `0.2.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `hashbrown` | `0.16.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `hashbrown` | `0.17.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `heapless` | `0.7.17` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `heck` | `0.5.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `iana-time-zone` | `0.1.65` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `icu_collections` | `2.2.0` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `icu_locale_core` | `2.2.0` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `icu_properties` | `2.2.0` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `icu_properties_data` | `2.2.0` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `icu_provider` | `2.2.0` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `indexmap` | `2.14.0` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `interpolator` | `0.5.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `is-macro` | `0.3.7` | `Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `itertools` | `0.14.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `itertools` | `0.15.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `itoa` | `1.0.18` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `jiter` | `0.16.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `lexical-parse-float` | `1.0.6` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `lexical-parse-integer` | `1.0.6` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `lexical-util` | `1.0.7` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `libc` | `0.2.189` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `libm` | `0.2.16` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `litemap` | `0.8.2` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `lock_api` | `0.4.14` | `MIT OR Apache-2.0` | `x86_64-unknown-linux-gnu` |
| `log` | `0.4.33` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `manyhow` | `0.11.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `manyhow-macros` | `0.11.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `memchr` | `2.8.3` | `Unlicense OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `memmap2` | `0.9.11` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `monty` | `0.0.21` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `monty-macros` | `0.0.21` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `monty-types` | `0.0.21` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `num-bigint` | `0.4.8` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `num-integer` | `0.1.46` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `num-traits` | `0.2.19` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `once_cell` | `1.21.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ordermap` | `1.2.0` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `phf` | `0.11.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `phf_codegen` | `0.11.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `phf_generator` | `0.11.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `phf_shared` | `0.11.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `postcard` | `1.1.3` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `potential_utf` | `0.1.5` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ppv-lite86` | `0.2.21` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `proc-macro-utils` | `0.10.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `proc-macro2` | `1.0.107` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `quote` | `1.0.47` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `quote-use` | `0.8.4` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `quote-use-macros` | `0.8.4` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `radium` | `0.7.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `rand` | `0.8.7` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `rand_chacha` | `0.3.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `rand_core` | `0.6.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `regex` | `1.13.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `regex-automata` | `0.4.18` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `regex-syntax` | `0.8.11` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ruff_python_ast` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ruff_python_codegen` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ruff_python_literal` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ruff_python_parser` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ruff_python_stdlib` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ruff_python_trivia` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ruff_source_file` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ruff_text_size` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `rustc-hash` | `2.1.3` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `rustc_version` | `0.4.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `rustversion` | `1.0.23` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `ryu` | `1.0.23` | `Apache-2.0 OR BSL-1.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `scopeguard` | `1.2.0` | `MIT OR Apache-2.0` | `x86_64-unknown-linux-gnu` |
| `semver` | `1.0.28` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `serde` | `1.0.229` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `serde_core` | `1.0.229` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `serde_derive` | `1.0.229` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `serde_json` | `1.0.151` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `serde_spanned` | `1.1.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `shlex` | `1.3.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `siphasher` | `1.0.3` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `smallvec` | `1.15.2` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `speedate` | `0.17.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `spin` | `0.9.9` | `MIT` | `x86_64-unknown-linux-gnu` |
| `stable_deref_trait` | `1.2.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `static_assertions` | `1.1.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `strip-ansi-escapes` | `0.2.1` | `Apache-2.0/MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `strum` | `0.27.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `strum_macros` | `0.27.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `syn` | `2.0.119` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `syn` | `3.0.3` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `synstructure` | `0.13.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `tap` | `1.0.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `thin-vec` | `0.2.19` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `thiserror` | `2.0.20` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `thiserror-impl` | `2.0.20` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `tinystr` | `0.8.3` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `tinyvec` | `1.12.0` | `Zlib OR Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `tinyvec_macros` | `0.1.1` | `MIT OR Apache-2.0 OR Zlib` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `toml` | `0.9.12+spec-1.1.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `toml_datetime` | `0.7.5+spec-1.1.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `toml_parser` | `1.1.3+spec-1.1.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `toml_writer` | `1.1.2+spec-1.1.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `unicode-general-category` | `1.1.0` | `Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `unicode-ident` | `1.0.24` | `(MIT OR Apache-2.0) AND Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `unicode-normalization` | `0.1.25` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `unicode-width` | `0.2.2` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `unicode_names2` | `1.3.0` | `(MIT OR Apache-2.0) AND Unicode-DFS-2016` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `unicode_names2_generator` | `1.3.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `utf8_iter` | `1.0.4` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `version_check` | `0.9.5` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `vte` | `0.14.1` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `winnow` | `0.7.15` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `winnow` | `1.0.4` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `writeable` | `0.6.3` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `wyz` | `0.5.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `yoke` | `0.8.3` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `yoke-derive` | `0.8.2` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `zerocopy` | `0.8.56` | `BSD-2-Clause OR Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `zerofrom` | `0.1.8` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `zerofrom-derive` | `0.1.7` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `zerotrie` | `0.2.4` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `zerovec` | `0.11.6` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `zerovec-derive` | `0.11.3` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |
| `zmij` | `1.0.23` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-unknown-linux-gnu` |

**Exact count:** 156 third-party name/version records. The local root `azdaja 0.1.2` is excluded.

## Lock records outside both supported closures

The following three records are resolver-only `Cargo.lock` entries outside both supported closures. No cached archive/source is available for them, no source or object from them is asserted to be redistributed in either supported release, and **this bundle makes no license claim for them**:

| Lock record | Version | Lock checksum | Disposition |
|---|---:|---|---|
| `winapi` | `0.3.9` | `5c839a674fcd7a98952e593242ea400abe93992746761e38641405d28b00f419` | Outside `aarch64-apple-darwin` and `x86_64-unknown-linux-gnu`; no license claim |
| `winapi-i686-pc-windows-gnu` | `0.4.0` | `ac3b87c63620426dd9b991e5ce0329eff545bccbbb34f3be09ff6fb6ab51b7b6` | Outside `aarch64-apple-darwin` and `x86_64-unknown-linux-gnu`; no license claim |
| `winapi-x86_64-pc-windows-gnu` | `0.4.0` | `712e227841d057c1ee1cd2fb22fa7e5a5461ae8e48fa2ca79ec42cfc1931183f` | Outside `aarch64-apple-darwin` and `x86_64-unknown-linux-gnu`; no license claim |

The other cached lock archives that are not members of the supported union are likewise outside this supported-release notice scope; their checksum availability is not a redistribution or license claim.

## Canonical full terms for valid SPDX declarations

Canonical identifiers/names were checked against local SPDX License List `3.28.0` metadata (release date `2026-02-20T00:00:00Z`). Full text bytes are mapped to exact, SHA-256-verified archive sources below. This mapping applies only to the 149 packages with valid SPDX-form declarations; the seven legacy slash declarations listed afterward are not recast as SPDX. No absent copyright holder or year is synthesized.

| SPDX ID | Packages whose valid expression contains ID | Full text SHA-256 / anchor | Exact verified source(s) for selected representative |
|---|---:|---|---|
| `Apache-2.0` | 92 | [`a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`](#text-a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2) | `ahash 0.8.12/LICENSE-APACHE`, `arrayvec 0.7.8/LICENSE-APACHE`, `autocfg 1.5.1/LICENSE-APACHE`, `bitflags 2.13.1/LICENSE-APACHE`, `bstr 1.13.1/LICENSE-APACHE`, `cfg-if 1.0.4/LICENSE-APACHE`, `core-foundation-sys 0.8.7/LICENSE-APACHE`, `displaydoc 0.2.7/LICENSE-APACHE`, `either 1.17.0/LICENSE-APACHE`, `equivalent 1.0.2/LICENSE-APACHE`, `fs2 0.4.3/LICENSE-APACHE`, `getopts 0.2.24/LICENSE-APACHE`, `hash32 0.2.1/LICENSE-APACHE`, `hashbrown 0.16.1/LICENSE-APACHE`, `hashbrown 0.17.1/LICENSE-APACHE`, `heapless 0.7.17/LICENSE-APACHE`, `heck 0.5.0/LICENSE-APACHE`, `indexmap 2.14.0/LICENSE-APACHE`, `itertools 0.14.0/LICENSE-APACHE`, `itertools 0.15.0/LICENSE-APACHE`, `lock_api 0.4.14/LICENSE-APACHE`, `log 0.4.33/LICENSE-APACHE`, `num-bigint 0.4.8/LICENSE-APACHE`, `num-integer 0.1.46/LICENSE-APACHE`, `num-traits 0.2.19/LICENSE-APACHE`, `once_cell 1.21.4/LICENSE-APACHE`, `ordermap 1.2.0/LICENSE-APACHE`, `postcard 1.1.3/LICENSE-APACHE`, `regex 1.13.1/LICENSE-APACHE`, `regex-automata 0.4.18/LICENSE-APACHE`, `regex-syntax 0.8.11/LICENSE-APACHE`, `rustc_version 0.4.1/LICENSE-APACHE`, `scopeguard 1.2.0/LICENSE-APACHE`, `smallvec 1.15.2/LICENSE-APACHE`, `stable_deref_trait 1.2.1/LICENSE-APACHE`, `strip-ansi-escapes 0.2.1/LICENSE-APACHE`, `unicode-normalization 0.1.25/LICENSE-APACHE`, `unicode-width 0.2.2/LICENSE-APACHE`, `unicode_names2 1.3.0/LICENSE-APACHE`, `unicode_names2_generator 1.3.0/LICENSE-APACHE`, `version_check 0.9.5/LICENSE-APACHE` |
| `BSD-2-Clause` | 1 | [`83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32`](#text-83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32) | `zerocopy 0.8.56/LICENSE-BSD` |
| `BSL-1.0` | 1 | [`c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566`](#text-c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566) | `ryu 1.0.23/LICENSE-BOOST` |
| `MIT` | 129 | [`cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d`](#text-cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d) | `winnow 0.7.15/LICENSE-MIT`, `winnow 1.0.4/LICENSE-MIT` |
| `Unicode-3.0` | 17 | [`f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`](#text-f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2) | `icu_collections 2.2.0/LICENSE`, `icu_locale_core 2.2.0/LICENSE`, `icu_properties 2.2.0/LICENSE`, `icu_properties_data 2.2.0/LICENSE`, `icu_provider 2.2.0/LICENSE`, `litemap 0.8.2/LICENSE`, `potential_utf 0.1.5/LICENSE`, `tinystr 0.8.3/LICENSE`, `writeable 0.6.3/LICENSE`, `yoke 0.8.3/LICENSE`, `yoke-derive 0.8.2/LICENSE`, `zerofrom 0.1.8/LICENSE`, `zerofrom-derive 0.1.7/LICENSE`, `zerotrie 0.2.4/LICENSE`, `zerovec 0.11.6/LICENSE`, `zerovec-derive 0.11.3/LICENSE` |
| `Unicode-DFS-2016` | 1 | [`74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3`](#text-74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3) | `regex-syntax 0.8.11/src/unicode_tables/LICENSE-UNICODE` |
| `Unlicense` | 3 | [`7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c`](#text-7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c) | `aho-corasick 1.1.5/UNLICENSE`, `byteorder 1.5.0/UNLICENSE`, `memchr 2.8.3/UNLICENSE` |
| `Zlib` | 3 | [`b1181a40b2a7b25cf66fd01481713bc1005df082c53ef73e851e55071b102744`](#text-b1181a40b2a7b25cf66fd01481713bc1005df082c53ef73e851e55071b102744) | `foldhash 0.2.0/LICENSE` |

Every other exact archive text variant remains included in the text corpus rather than being replaced by the representative. In particular, package-specific MIT, Zlib, BSD, Unicode, and combined texts retain the notices actually furnished upstream.

### Historical slash-form declarations (not valid modern SPDX expressions)

| Package | Exact declaration | Treatment |
|---|---|---|
| `fs2 0.4.3` | `MIT/Apache-2.0` | Preserved verbatim; all legal files found in its verified archive are reproduced; no expression rewrite |
| `lexical-parse-float 1.0.6` | `MIT/Apache-2.0` | Preserved verbatim; all legal files found in its verified archive are reproduced; no expression rewrite |
| `lexical-parse-integer 1.0.6` | `MIT/Apache-2.0` | Preserved verbatim; all legal files found in its verified archive are reproduced; no expression rewrite |
| `lexical-util 1.0.7` | `MIT/Apache-2.0` | Preserved verbatim; all legal files found in its verified archive are reproduced; no expression rewrite |
| `siphasher 1.0.3` | `MIT/Apache-2.0` | Preserved verbatim; all legal files found in its verified archive are reproduced; no expression rewrite |
| `strip-ansi-escapes 0.2.1` | `Apache-2.0/MIT` | Preserved verbatim; all legal files found in its verified archive are reproduced; no expression rewrite |
| `version_check 0.9.5` | `MIT/Apache-2.0` | Preserved verbatim; all legal files found in its verified archive are reproduced; no expression rewrite |

## Thirteen MIT-declared archives with no detected legal file

For these 13 packages, the audit enumerated every archive member path and inspected the normalized manifest, original manifest, README, and every UTF-8 source/header for strict legal-attribution markers. The exact normalized package manifest is the authoritative in-archive MIT declaration. No full license/permission text, copyright statement, `NOTICE`, or SPDX source header was found. The canonical MIT terms mapped above are therefore supplied **without inventing a missing copyright holder or year**. `authors` metadata, where present, is not re-labelled as copyright.

| Package | Members / path-inventory SHA-256 | Exact manifest evidence | README evidence | Attribution finding |
|---|---|---|---|---|
| `monty 0.0.21` | 756 / `9328f0b0dca5294947e6b9375fa8dca96a01ff6bf6ccad7d1c8adaf530460c59` | `Cargo.toml:38` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:5` `license = { workspace = true }`; normalized manifest SHA `0a3253841dbea04618bd70964140baf7ae61f8ef064ed504d5bd4ad24e53179d` | `README.md` SHA `ad65a07aff825fcdf42aa4e1b787ed8911fb4603f26d481a88ff3f0d3d956329`: line 5: `[![license](https://img.shields.io/github/license/pydantic/monty.svg?v=2)](https://github.com/pydantic/monty/blob/main/LICENSE)`; line 132: `## License`; line 133: ``; line 134: `MIT` | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Samuel Colvin <samuel@pydantic.dev>"]` are not asserted as copyright |
| `monty-macros 0.0.21` | 8 / `6008747327cea48001474f9f9fdd6574c31ffb0f9350ddb5b894fa87a71039c9` | `Cargo.toml:27` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:5` `license = { workspace = true }`; normalized manifest SHA `74d5755a08bd79358a0b449584525aacdbf075bc5cbf274d0b0fdb3246c23a12` | `README.md` SHA `c63a872ea960c76db5653b4c17c3272d738e75d96346435962a7c60bf79827d2`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Samuel Colvin <samuel@pydantic.dev>"]` are not asserted as copyright |
| `monty-types 0.0.21` | 18 / `5a04854e8c1102a26e5195dfd798c78c6d118b45442f83dbe63b2676a107fe48` | `Cargo.toml:38` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:5` `license = { workspace = true }`; normalized manifest SHA `cc48256ad55c63ca66ffc3e85603e70129943aa99e15f193d3c68cc9b24d73d2` | `README.md` SHA `18cffb85ecd76e32e1e3ed8249f1ebcf6dea24c4a01364970ee6eea2662c84b2`: line 54: `## License`; line 55: ``; line 56: `MIT` | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Samuel Colvin <samuel@pydantic.dev>"]` are not asserted as copyright |
| `quote-use 0.8.4` | 5 / `7db714b9155fd5597e70ddb2d9b21d36e650735e2fd6b025bd80c6c12146c692` | `Cargo.toml:35` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:13` `license = "MIT"`; normalized manifest SHA `aeecafa377cc97d08cac24211ec573b3e3c74338f86885c60003828032e0b40e` | `README.md` SHA `dc83b2025026eb2090028368abbdc9e6969795098a25a7033d91ed376beb13a7`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `null` are not asserted as copyright |
| `quote-use-macros 0.8.4` | 10 / `94c50647fdf608fa9ff779c239f49133e2422f78507b2d8a41623e3fff9eb690` | `Cargo.toml:35` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:11` `license = "MIT"`; normalized manifest SHA `cdfa5d01a4c3dae7422d194d862aa9269903a2828cf9154cb88f658d79d5d732` | `README.md` SHA `dc83b2025026eb2090028368abbdc9e6969795098a25a7033d91ed376beb13a7`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `null` are not asserted as copyright |
| `ruff_python_ast 0.0.3` | 38 / `5d50d715602d5bdc3211b213536f189f6efda5c339a7dc70009ce8043f2b286a` | `Cargo.toml:28` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:11` `license = { workspace = true }`; normalized manifest SHA `540f0c2aa025bded9b98325f0ecd30fd9869d1ef5512c676f709cea06c960082` | `README.md` SHA `31b619995ea4e2e08361ee57a1bd6b1617c29874d8dc8317a9863490e1cb87ca`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Charlie Marsh <charlie.r.marsh@gmail.com>"]` are not asserted as copyright |
| `ruff_python_codegen 0.0.3` | 8 / `0fe107975d95d9565bbd51499a1bad1f2c782d638c30ae4c8c32edf3b53ec20e` | `Cargo.toml:28` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:11` `license = { workspace = true }`; normalized manifest SHA `d2018ff07da63f3acf54e0400c6b044d89cb674945651c4badd119d8a924d742` | `README.md` SHA `0479954ed5bff9fc3fbdf3576850d540be2222849bff63a70950f612ceb1930d`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Charlie Marsh <charlie.r.marsh@gmail.com>"]` are not asserted as copyright |
| `ruff_python_literal 0.0.3` | 11 / `a21e363726e1bfa6c23d4baa6852145b068833d6555dbee5f0f86b754e65e297` | `Cargo.toml:31` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:11` `license = { workspace = true }`; normalized manifest SHA `7e9023387d063e428fcfa22e2d97fe74a2bc372bf71369db626819780252774d` | `README.md` SHA `80706700368a1e1a3ec9d6afa09fed69435beb082bebc5f6e775a5784be2bb73`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Charlie Marsh <charlie.r.marsh@gmail.com>", "RustPython Team"]` are not asserted as copyright |
| `ruff_python_parser 0.0.3` | 1335 / `a1d1a2b63528128e62ee1fd6e2fc2c8c54c1056989c394e86b969c10fa2de9a0` | `Cargo.toml:31` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:11` `license = { workspace = true }`; normalized manifest SHA `8923417bf1d59005e2d997b95e441cafb6b081bc5803a0c83885d63bdb1d2b93` | `README.md` SHA `70ee081576e0a60b88a712977a6583a0ef17edea50081ff8ba6a2259dbb25ffa`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Charlie Marsh <charlie.r.marsh@gmail.com>", "RustPython Team"]` are not asserted as copyright |
| `ruff_python_stdlib 0.0.3` | 17 / `689f0cc6fe09fc765b7bf9f6ec3e9ec76a6ecea0de7fef8b3d0c987d2c1715af` | `Cargo.toml:28` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:11` `license = { workspace = true }`; normalized manifest SHA `e030b71f6135c109d1f367fff93954648405e9a9ffdfbd5a7be21f93d11b2332` | `README.md` SHA `9963ed24ca88632298b35410ce7ba5907b080d65c727b3b81f93a5547a4c5e39`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Charlie Marsh <charlie.r.marsh@gmail.com>"]` are not asserted as copyright |
| `ruff_python_trivia 0.0.3` | 13 / `dcc20606b46ae53f77b8c9578f93ad9e4176295c1fd32d24ed8757ca8da34a5f` | `Cargo.toml:28` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:11` `license = { workspace = true }`; normalized manifest SHA `709a5123df3084e086474e7e8b89fe82e2fb356a8e2641912173e7be2ae226c4` | `README.md` SHA `efb029cb2fdef9aa6396c832d5ab3f9495b60406341a45db00329225e7754107`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Charlie Marsh <charlie.r.marsh@gmail.com>"]` are not asserted as copyright |
| `ruff_source_file 0.0.3` | 9 / `ed0da4e0cb829fee33bdfd206e22e1db18b168e4678781efdb7f3e887e596abc` | `Cargo.toml:28` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:11` `license = { workspace = true }`; normalized manifest SHA `ee1f9b455592033cf985913ec5420616333f90eb81ea2f8b4139b6c93eccd221` | `README.md` SHA `98140fc40863ea8e3b017386f69cdba55a04f96b7027ffd6d2beba9efe78646f`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Charlie Marsh <charlie.r.marsh@gmail.com>"]` are not asserted as copyright |
| `ruff_text_size 0.0.3` | 16 / `43d385476069ef6159e235b8648f4761b78c925bcdbd8bfc76674166c77c14b0` | `Cargo.toml:28` `license = "MIT"`; `Cargo.toml.orig` `Cargo.toml.orig:11` `license = { workspace = true }`; normalized manifest SHA `42a4cd6685fa86689f9b2ccd9c9ff574046c62ca514ea7ad43e6e0d5b59e7c81` | `README.md` SHA `34f7df056cfc75937bb3c8d7c32d020cb205db20b7947a0bc8a87176690f0376`: No license/copyright/permission/SPDX line | No named legal path and no strict legal attribution header in any other textual member; manifest authors `["Charlie Marsh <charlie.r.marsh@gmail.com>"]` are not asserted as copyright |

The machine manifest records the archive hash, counts, complete relative-path inventory hash, manifest/README hashes, exact evidence lines, and zero source-header hit list for each package.

## Bundled font notice

- Font file: `site/fonts/cormorant-light.woff2` — SHA-256 `ee185375114e22d847ace51ba8fa0293e29c401a541eaccfec6b50448368d755`.
- Embedded face metadata: **Cormorant Garamond Light**, subfamily Regular, version 4.001. CSS weight 300 matches the intended Light face.
- Co-located source notice: `site/fonts/Cormorant-Garamond-OFL.txt` — SHA-256 `60700d351cac4650c51f3f9db318d2a420f8b45052dba2715eb5fec41f0f6956`; its exact copyright is **“Copyright 2015 the Cormorant Project Authors (github.com/CatharsisFonts/Cormorant)”** and its complete SIL OFL 1.1 terms are reproduced once as [text `60700d351cac4650c51f3f9db318d2a420f8b45052dba2715eb5fec41f0f6956`](#text-60700d351cac4650c51f3f9db318d2a420f8b45052dba2715eb5fec41f0f6956). No additional font copyright is inferred.

## Obligations, unsatisfied cases, and release conditions

| Case / obligation | Bundle result | Release consequence |
|---|---|---|
| MIT and MIT-like notice retention | All detected exact copyright/permission texts are included; canonical MIT permission terms cover valid MIT declarations that furnished no text. | **Satisfied by this bundle only if it accompanies the binary.** A bare binary does not carry these texts and is not cleared. |
| Apache-2.0 §4(a) license copy | Complete Apache-2.0 terms are included and source-mapped. | Satisfied when bundle accompanies object distribution. Source modifications, if ever distributed, still need prominent change notices and retained source notices under §4(b)/(c). |
| Apache-2.0 §4(d) NOTICE | Exhaustive case-insensitive archive-path enumeration detected **zero `NOTICE` files** in the 156 supported archives. No upstream `NOTICE` payload exists to reproduce. | No separate detected §4(d) payload. If build inputs change, rescan. |
| BSD-2-Clause binary notice | Exact `zerocopy` BSD text and detected embedded BSD blocks (including conservative test/benchmark blocks) are included. | Satisfied in documentation/materials only when this bundle accompanies the binary; bare binary release is not cleared. |
| Unicode-3.0 / Unicode-DFS-2016 | Exact Unicode notices/terms found in archives are included. | Satisfied when bundle accompanies the binary; do not remove the notice/terms. |
| BSL-1.0, Zlib, Unlicense | Exact detected texts are included. | No further notice payload detected; other behavioral conditions (for example, Zlib origin/misrepresentation limits) remain applicable. |
| SIL OFL 1.1 font redistribution | Exact font copyright and complete OFL accompany the identified font. | Bundle satisfies notice-copy requirement only when shipped with distributions containing the font. Do not sell font by itself, relicense it, use reserved names for a modified version without permission, or imply endorsement. |
| 13 MIT archives without a legal file | Exact manifest/README/path/header evidence is disclosed; no absent notice is fabricated. | Evidence limitation remains visible, but no locally available copyright/permission/NOTICE text remains omitted. Escalate for legal review if policy requires a holder-specific copyright statement rather than authoritative manifest metadata plus canonical terms. |
| Seven slash-form manifest values | Raw values and archive texts are preserved; no SPDX normalization is claimed. | Engineering policy note, not an omitted-text finding. Escalate only if release policy forbids legacy Cargo slash syntax. |
| Bare binaries or download pages that do not co-distribute/link this bundle | Not satisfied. | **Do not release bare binaries.** Put this file in each archive/package and make it accessible adjacent to each standalone binary download. |
| Trademark, patent termination, warranty, endorsement, and modified-work restrictions | License texts state these terms; a notice bundle cannot perform ongoing behavioral compliance. | Release owner must continue to observe them. |
| Logo/site-art provenance | Outside this third-party dependency/font notice bundle and unchanged from the prior separate gate. | This bundle does **not** clear the separate art-provenance gate. |

**Supported-target license-gate decision:** this bundle clears the dependency/font notice-text gate for the two supported targets **narrowly and conditionally**, provided the exact reviewed file is placed and co-distributed as specified, hashes are re-bound after any dependency/font/build-scope change, and release policy accepts the disclosed manifest-only MIT evidence and legacy slash syntax. It does not clear unrelated provenance, product-accuracy, signing, packaging, or legal-review gates.

## Exact-text corpus (deduplicated by SHA-256)

**Corpus:** 593 source occurrences → **245 unique exact byte texts**, totaling **385,064 source bytes** before Markdown framing.

<a id="text-013ca8b1499479ce162f0d68ff25f4ac0a98dae625d55a8eabfb1fb4aa38933d"></a>
### Text `013ca8b1499479ce162f0d68ff25f4ac0a98dae625d55a8eabfb1fb4aa38933d`
- SHA-256: `013ca8b1499479ce162f0d68ff25f4ac0a98dae625d55a8eabfb1fb4aa38933d`
- Exact source bytes: `1082`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/get-size2@0.10.1 — `LICENSE` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2022 Denis Kerp & 2025 Nicolas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f"></a>
### Text `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f`
- SHA-256: `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f`
- Exact source bytes: `126`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/aho-corasick@1.1.5 — `COPYING` (archive_named_legal_file)
  - pkg:cargo/byteorder@1.5.0 — `COPYING` (archive_named_legal_file)
  - pkg:cargo/memchr@2.8.3 — `COPYING` (archive_named_legal_file)
````text
This project is dual-licensed under the Unlicense and MIT licenses.

You may use this code under the terms of either license.

````

<a id="text-0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a"></a>
### Text `0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a`
- SHA-256: `0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a`
- Exact source bytes: `10854`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/ppv-lite86@0.2.21 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright 2019 The CryptoCorrosion Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

````

<a id="text-035e70219855119df4273b3c5b97543ae82e0dd60c520416e759107c602f651b"></a>
### Text `035e70219855119df4273b3c5b97543ae82e0dd60c520416e759107c602f651b`
- SHA-256: `035e70219855119df4273b3c5b97543ae82e0dd60c520416e759107c602f651b`
- Exact source bytes: `1058`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/heapless@0.7.17 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2017 Jorge Aparicio

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-0372df70e5652415fa6fdb9147e8f7efd878ce606b5890678def629645b78104"></a>
### Text `0372df70e5652415fa6fdb9147e8f7efd878ce606b5890678def629645b78104`
- SHA-256: `0372df70e5652415fa6fdb9147e8f7efd878ce606b5890678def629645b78104`
- Exact source bytes: `471`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/log@0.4.33 — `src/macros.rs` (archive_legal_header_block)
````text
// Copyright 2014-2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-0444c6991eead6822f7b9102e654448d51624431119546492e8b231db42c48bb"></a>
### Text `0444c6991eead6822f7b9102e654448d51624431119546492e8b231db42c48bb`
- SHA-256: `0444c6991eead6822f7b9102e654448d51624431119546492e8b231db42c48bb`
- Exact source bytes: `1057`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/ahash@0.8.12 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2018 Tom Kaitchuck

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-04ea4849dba9dcae07113850c6f1b1a69052c625210639914eee352023f750ad"></a>
### Text `04ea4849dba9dcae07113850c6f1b1a69052c625210639914eee352023f750ad`
- SHA-256: `04ea4849dba9dcae07113850c6f1b1a69052c625210639914eee352023f750ad`
- Exact source bytes: `10835`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/memmap2@0.9.11 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [2015] [Dan Burkert]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

````

<a id="text-0612a90594c434a7d2e10fd439b44e0984e0f0edff501c70028f7c60a9c41975"></a>
### Text `0612a90594c434a7d2e10fd439b44e0984e0f0edff501c70028f7c60a9c41975`
- SHA-256: `0612a90594c434a7d2e10fd439b44e0984e0f0edff501c70028f7c60a9c41975`
- Exact source bytes: `185`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set1.16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set1.16
#
# machine-generated by: ucptrietest.c

````

<a id="text-077bb1b55842a8918cb44fa2bc837898374b78e993ab41a09b0a8030aa63a908"></a>
### Text `077bb1b55842a8918cb44fa2bc837898374b78e993ab41a09b0a8030aa63a908`
- SHA-256: `077bb1b55842a8918cb44fa2bc837898374b78e993ab41a09b0a8030aa63a908`
- Exact source bytes: `184`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set1.8.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set1.8
#
# machine-generated by: ucptrietest.c

````

<a id="text-0877e3815c7b0a9f7698dfe334aafa4d4c677a11addc745fa8450b959ed2a657"></a>
### Text `0877e3815c7b0a9f7698dfe334aafa4d4c677a11addc745fa8450b959ed2a657`
- SHA-256: `0877e3815c7b0a9f7698dfe334aafa4d4c677a11addc745fa8450b959ed2a657`
- Exact source bytes: `200`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/small0-in-fast.small16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: small0-in-fast.small16
#
# machine-generated by: ucptrietest.c

````

<a id="text-08a39cc318d41fade9a1a4984f15cdfcc5d013ee9be65c44c65b655b4d55d4a9"></a>
### Text `08a39cc318d41fade9a1a4984f15cdfcc5d013ee9be65c44c65b655b4d55d4a9`
- SHA-256: `08a39cc318d41fade9a1a4984f15cdfcc5d013ee9be65c44c65b655b4d55d4a9`
- Exact source bytes: `195`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set-empty.small16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set-empty.small16
#
# machine-generated by: ucptrietest.c

````

<a id="text-09d5310bbaaa9e8df55e9746713f3c2c9b56b1868e5b3cef98f585d0107f90a9"></a>
### Text `09d5310bbaaa9e8df55e9746713f3c2c9b56b1868e5b3cef98f585d0107f90a9`
- SHA-256: `09d5310bbaaa9e8df55e9746713f3c2c9b56b1868e5b3cef98f585d0107f90a9`
- Exact source bytes: `375`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `tests/codegen.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `tests/include.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/late-compile-pass.rs` (archive_legal_header_block)
````text
// Copyright 2026 The Fuchsia Authors
//
// Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-09da7652e2fd41a7c24d3f75423f749f0d88fe1dba8dd02034bb9a506a5a1c70"></a>
### Text `09da7652e2fd41a7c24d3f75423f749f0d88fe1dba8dd02034bb9a506a5a1c70`
- SHA-256: `09da7652e2fd41a7c24d3f75423f749f0d88fe1dba8dd02034bb9a506a5a1c70`
- Exact source bytes: `508`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/getopts@0.2.24 — `src/lib.rs` (archive_legal_header_block)
````text
// Copyright 2012-2014 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.
//
// ignore-lexer-test FIXME #15677

````

<a id="text-0ab4d106b6faac07fb6a051815fd1b4d862d730895e2d7d7358c2f13565e7a38"></a>
### Text `0ab4d106b6faac07fb6a051815fd1b4d862d730895e2d7d7358c2f13565e7a38`
- SHA-256: `0ab4d106b6faac07fb6a051815fd1b4d862d730895e2d7d7358c2f13565e7a38`
- Exact source bytes: `1099`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/phf@0.11.3 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/phf_codegen@0.11.3 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/phf_generator@0.11.3 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/phf_shared@0.11.3 — `LICENSE` (archive_named_legal_file)
````text
The MIT License (MIT)

Copyright (c) 2014-2022 Steven Fackler, Yuki Okushi

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

````

<a id="text-0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9"></a>
### Text `0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9`
- SHA-256: `0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9`
- Exact source bytes: `1072`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/smallvec@1.15.2 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2018 The Servo Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-0beade56a930d1c1a35daa8cd5bbe8350757c3b38ac025a553f7db8bdfaf9e16"></a>
### Text `0beade56a930d1c1a35daa8cd5bbe8350757c3b38ac025a553f7db8bdfaf9e16`
- SHA-256: `0beade56a930d1c1a35daa8cd5bbe8350757c3b38ac025a553f7db8bdfaf9e16`
- Exact source bytes: `428`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/sin.rs` (archive_legal_header_block)
````text
// origin: FreeBSD /usr/src/lib/msun/src/s_sin.c */
//
// ====================================================
// Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
//
// Developed at SunPro, a Sun Microsystems, Inc. business.
// Permission to use, copy, modify, and distribute this
// software is freely granted, provided that this notice
// is preserved.
// ====================================================

````

<a id="text-0c3d0381d2cd647be68590170490be5f624c962d9f95eb698489e578c1de8f05"></a>
### Text `0c3d0381d2cd647be68590170490be5f624c962d9f95eb698489e578c1de8f05`
- SHA-256: `0c3d0381d2cd647be68590170490be5f624c962d9f95eb698489e578c1de8f05`
- Exact source bytes: `379`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/lexical-parse-float@1.0.6 — `src/libm.rs` starting line 15 (archive_legal_header_block)
  - pkg:cargo/lexical-parse-float@1.0.6 — `src/libm.rs` starting line 378 (archive_legal_header_block)
  - pkg:cargo/lexical-util@1.0.7 — `src/libm.rs` starting line 209 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/acosf.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/asinf.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/atan.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/atan2f.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/atanf.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/cbrtf.rs` starting line 6 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/cosf.rs` starting line 6 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/erf.rs` starting line 3 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/erff.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/expf.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/expm1.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/expm1f.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/j0f.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/j1f.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/jnf.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/k_cosf.rs` starting line 6 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/k_sinf.rs` starting line 6 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/lgammaf_r.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/log10f.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/log1p.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/log1pf.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/log2f.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/logf.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/powf.rs` starting line 5 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/rem_pio2f.rs` starting line 6 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/sincos.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/sincosf.rs` starting line 6 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/sinf.rs` starting line 6 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/tanf.rs` starting line 6 (archive_legal_header_block)
````text
/*
 * ====================================================
 * Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
 *
 * Developed at SunPro, a Sun Microsystems, Inc. business.
 * Permission to use, copy, modify, and distribute this
 * software is freely granted, provided that this notice
 * is preserved.
 * ====================================================
 */
````

<a id="text-0d25d03b5ab49576178ad0cae7a2648d12c17ad0452fe49c07e55e4b59aa5257"></a>
### Text `0d25d03b5ab49576178ad0cae7a2648d12c17ad0452fe49c07e55e4b59aa5257`
- SHA-256: `0d25d03b5ab49576178ad0cae7a2648d12c17ad0452fe49c07e55e4b59aa5257`
- Exact source bytes: `1091`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/memmap2@0.9.11 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2020 Yevhenii Reizner
Copyright (c) 2015 Dan Burkert

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-0d52feec79589df30138dad3800323fe5686b764b73347330a2dfef8ac83efe8"></a>
### Text `0d52feec79589df30138dad3800323fe5686b764b73347330a2dfef8ac83efe8`
- SHA-256: `0d52feec79589df30138dad3800323fe5686b764b73347330a2dfef8ac83efe8`
- Exact source bytes: `1073`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/compact_str@0.9.0 — `LICENSE` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2021 Parker Timmerman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f"></a>
### Text `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f`
- SHA-256: `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f`
- Exact source bytes: `1081`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/aho-corasick@1.1.5 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/byteorder@1.5.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/memchr@2.8.3 — `LICENSE-MIT` (archive_named_legal_file)
````text
The MIT License (MIT)

Copyright (c) 2015 Andrew Gallant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

````

<a id="text-117319946a34c90bd030673bd950776f1a2d46320be153c61de06dbcb55bacf0"></a>
### Text `117319946a34c90bd030673bd950776f1a2d46320be153c61de06dbcb55bacf0`
- SHA-256: `117319946a34c90bd030673bd950776f1a2d46320be153c61de06dbcb55bacf0`
- Exact source bytes: `686`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/utf8_iter@1.0.4 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/utf8_iter@1.0.4 — `src/report.rs` (archive_legal_header_block)
````text
// Copyright Mozilla Foundation
//
// Licensed under the Apache License (Version 2.0), or the MIT license,
// (the "Licenses") at your option. You may not use this file except in
// compliance with one of the Licenses. You may obtain copies of the
// Licenses at:
//
//    https://www.apache.org/licenses/LICENSE-2.0
//    https://opensource.org/licenses/MIT
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the Licenses is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the Licenses for the specific language governing permissions and
// limitations under the Licenses.

````

<a id="text-118929e2af641db591b373fe6a3c607fedca84f7f877f81e68743cfaf69f1cfd"></a>
### Text `118929e2af641db591b373fe6a3c607fedca84f7f877f81e68743cfaf69f1cfd`
- SHA-256: `118929e2af641db591b373fe6a3c607fedca84f7f877f81e68743cfaf69f1cfd`
- Exact source bytes: `119`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/chrono@0.4.45 — `src/format/parse.rs` (archive_legal_header_block)
````text
// This is a part of Chrono.
// Portions copyright (c) 2015, John Nagle.
// See README.md and LICENSE.txt for details.

````

<a id="text-118d5286b713391d3a7a4f5fc99979c325243975f67b2c7962913fa6965cb8b3"></a>
### Text `118d5286b713391d3a7a4f5fc99979c325243975f67b2c7962913fa6965cb8b3`
- SHA-256: `118d5286b713391d3a7a4f5fc99979c325243975f67b2c7962913fa6965cb8b3`
- Exact source bytes: `194`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/small0-in-fast.8.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: small0-in-fast.8
#
# machine-generated by: ucptrietest.c

````

<a id="text-11f476f899dacfef801a097465ad0755ad4546afe03b02c9a17aa38e228344e1"></a>
### Text `11f476f899dacfef801a097465ad0755ad4546afe03b02c9a17aa38e228344e1`
- SHA-256: `11f476f899dacfef801a097465ad0755ad4546afe03b02c9a17aa38e228344e1`
- Exact source bytes: `383`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/atan2.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/lgamma_r.rs` starting line 2 (archive_legal_header_block)
````text
/*
 * ====================================================
 * Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
 *
 * Developed at SunSoft, a Sun Microsystems, Inc. business.
 * Permission to use, copy, modify, and distribute this
 * software is freely granted, provided that this notice
 * is preserved.
 * ====================================================
 *
 */
````

<a id="text-11f5c6d7e635e6f459aedeecc6540e1a29e3e988555caf82281c17b7acb3a2a7"></a>
### Text `11f5c6d7e635e6f459aedeecc6540e1a29e3e988555caf82281c17b7acb3a2a7`
- SHA-256: `11f5c6d7e635e6f459aedeecc6540e1a29e3e988555caf82281c17b7acb3a2a7`
- Exact source bytes: `471`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/bit-set@0.8.0 — `benches/bench.rs` (archive_legal_header_block)
````text
// Copyright 2012-2024 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e"></a>
### Text `123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e`
- SHA-256: `123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e`
- Exact source bytes: `1066`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/libc@0.2.189 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-12be7051cc7f7e11f992c70c25b5e23b5e459ee4f5cad31f03227df0e32f7714"></a>
### Text `12be7051cc7f7e11f992c70c25b5e23b5e459ee4f5cad31f03227df0e32f7714`
- SHA-256: `12be7051cc7f7e11f992c70c25b5e23b5e459ee4f5cad31f03227df0e32f7714`
- Exact source bytes: `495`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `src/deprecated.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/error.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/impls.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/layout.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/macros.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/ref.rs` (archive_legal_header_block)
````text
// SPDX-License-Identifier: BSD-2-Clause OR Apache-2.0 OR MIT
//
// Copyright 2024 The Fuchsia Authors
//
// Licensed under the 2-Clause BSD License <LICENSE-BSD or
// https://opensource.org/license/bsd-2-clause>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-13f4cc9fbc8d4a447b28aa84019c10ad4abf4b5f6919db061bf6690ccc23bc02"></a>
### Text `13f4cc9fbc8d4a447b28aa84019c10ad4abf4b5f6919db061bf6690ccc23bc02`
- SHA-256: `13f4cc9fbc8d4a447b28aa84019c10ad4abf4b5f6919db061bf6690ccc23bc02`
- Exact source bytes: `1079`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/radium@0.7.0 — `LICENSE.txt` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2019 kneecaw (Nika Layzell)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-1418fdabd96762bb5892098a229061f07dd624245687fd0a95ef33f3feb845a0"></a>
### Text `1418fdabd96762bb5892098a229061f07dd624245687fd0a95ef33f3feb845a0`
- SHA-256: `1418fdabd96762bb5892098a229061f07dd624245687fd0a95ef33f3feb845a0`
- Exact source bytes: `1051`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/strip-ansi-escapes@0.2.1 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2018 Mozilla

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-15ad306b04e911801dbfaad02f12a17d07f3244c59f77140f361adb291ebd5d1"></a>
### Text `15ad306b04e911801dbfaad02f12a17d07f3244c59f77140f361adb291ebd5d1`
- SHA-256: `15ad306b04e911801dbfaad02f12a17d07f3244c59f77140f361adb291ebd5d1`
- Exact source bytes: `195`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/small0-in-fast.32.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: small0-in-fast.32
#
# machine-generated by: ucptrietest.c

````

<a id="text-15e78071c8347a689c48ec92bbdd5eba7bd8dc74f86ee3e7ad31d34b24fefe83"></a>
### Text `15e78071c8347a689c48ec92bbdd5eba7bd8dc74f86ee3e7ad31d34b24fefe83`
- SHA-256: `15e78071c8347a689c48ec92bbdd5eba7bd8dc74f86ee3e7ad31d34b24fefe83`
- Exact source bytes: `320`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/lexical-parse-float@1.0.6 — `src/libm.rs` starting line 533 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/exp.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/pow.rs` starting line 2 (archive_legal_header_block)
````text
/*
 * ====================================================
 * Copyright (C) 2004 by Sun Microsystems, Inc. All rights reserved.
 *
 * Permission to use, copy, modify, and distribute this
 * software is freely granted, provided that this notice
 * is preserved.
 * ====================================================
 */
````

<a id="text-177540cad091a40e8071db310bc3b6115c4e329a92a234609b60c154b008a888"></a>
### Text `177540cad091a40e8071db310bc3b6115c4e329a92a234609b60c154b008a888`
- SHA-256: `177540cad091a40e8071db310bc3b6115c4e329a92a234609b60c154b008a888`
- Exact source bytes: `1063`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/postcard@1.1.3 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2019 Anthony James Munns

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-18fba61c8218e152386ba7738a48af76403fb984ca28df7432b2f7c864b3b0df"></a>
### Text `18fba61c8218e152386ba7738a48af76403fb984ca28df7432b2f7c864b3b0df`
- SHA-256: `18fba61c8218e152386ba7738a48af76403fb984ca28df7432b2f7c864b3b0df`
- Exact source bytes: `368`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `clippy.toml` (archive_legal_header_block)
````text
# Copyright 2023 The Fuchsia Authors
#
# Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
# <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
# license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
# This file may not be copied, modified, or distributed except according to
# those terms.

````

<a id="text-1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df"></a>
### Text `1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df`
- SHA-256: `1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df`
- Exact source bytes: `1060`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright 2023 The Fuchsia Authors

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-1beef92d224e4007ac9420f0888c7011de630d475d8d541a12a68e4d00c93fb9"></a>
### Text `1beef92d224e4007ac9420f0888c7011de630d475d8d541a12a68e4d00c93fb9`
- SHA-256: `1beef92d224e4007ac9420f0888c7011de630d475d8d541a12a68e4d00c93fb9`
- Exact source bytes: `194`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/short-all-same.8.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: short-all-same.8
#
# machine-generated by: ucptrietest.c

````

<a id="text-1cc060e851d62adaf4209f5978d5f155b159bc29d3012a96482a90802ad5b99a"></a>
### Text `1cc060e851d62adaf4209f5978d5f155b159bc29d3012a96482a90802ad5b99a`
- SHA-256: `1cc060e851d62adaf4209f5978d5f155b159bc29d3012a96482a90802ad5b99a`
- Exact source bytes: `375`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/diagnostic-not-implemented.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/transmute-ptr-to-usize.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/transmute.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/try_transmute.rs` (archive_legal_header_block)
````text
// Copyright 2022 The Fuchsia Authors
//
// Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-1dd8eca0f83669e75fa119e34fb9e1be9d16e3e9b6368962b8019db6e8ae5f7b"></a>
### Text `1dd8eca0f83669e75fa119e34fb9e1be9d16e3e9b6368962b8019db6e8ae5f7b`
- SHA-256: `1dd8eca0f83669e75fa119e34fb9e1be9d16e3e9b6368962b8019db6e8ae5f7b`
- Exact source bytes: `1062`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/tinyvec_macros@0.1.1 — `LICENSE-MIT.md` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2020 Soveu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-1dfeac2b788d56ff9f9e053197e95aeea3a66bbceefed4cced444623c2c1cdd9"></a>
### Text `1dfeac2b788d56ff9f9e053197e95aeea3a66bbceefed4cced444623c2c1cdd9`
- SHA-256: `1dfeac2b788d56ff9f9e053197e95aeea3a66bbceefed4cced444623c2c1cdd9`
- Exact source bytes: `332`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/lock_api@0.4.14 — `src/rwlock.rs` (archive_legal_header_block)
````text
// Copyright 2016 Amanieu d'Antras
//
// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
// http://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.

````

<a id="text-209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b"></a>
### Text `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b`
- SHA-256: `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b`
- Exact source bytes: `1117`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/rand@0.8.7 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/rand_chacha@0.3.1 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/rand_core@0.6.4 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright 2018 Developers of the Rand project
Copyright (c) 2014 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-20fe7b00e904ed690e3b9fd6073784d3fc428141dbd10b81c01fd143d0797f58"></a>
### Text `20fe7b00e904ed690e3b9fd6073784d3fc428141dbd10b81c01fd143d0797f58`
- SHA-256: `20fe7b00e904ed690e3b9fd6073784d3fc428141dbd10b81c01fd143d0797f58`
- Exact source bytes: `9899`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/allocator-api2@0.2.21 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

````

<a id="text-219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59"></a>
### Text `219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59`
- SHA-256: `219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59`
- Exact source bytes: `1052`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/synstructure@0.13.2 — `LICENSE` (archive_named_legal_file)
````text
Copyright 2016 Nika Layzell

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

````

<a id="text-225167f203ade8fe5b0714aed4abf358d23fb9dd385a63580ba216ac88a7b799"></a>
### Text `225167f203ade8fe5b0714aed4abf358d23fb9dd385a63580ba216ac88a7b799`
- SHA-256: `225167f203ade8fe5b0714aed4abf358d23fb9dd385a63580ba216ac88a7b799`
- Exact source bytes: `137`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/cbrt.rs` starting line 2 (archive_legal_header_block)
````text
/* origin: core-math/src/binary64/cbrt/cbrt.c
 * Copyright (c) 2021-2022 Alexei Sibidanov.
 * Ported to Rust in 2025 by Trevor Gross.
 */
````

<a id="text-2378439e1bf5c7850bf36c70708717f83576405586a8e90db5f925b82390a800"></a>
### Text `2378439e1bf5c7850bf36c70708717f83576405586a8e90db5f925b82390a800`
- SHA-256: `2378439e1bf5c7850bf36c70708717f83576405586a8e90db5f925b82390a800`
- Exact source bytes: `390`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `ci/check_msrv_is_minimal.sh` (archive_legal_header_block)
````text
#!/usr/bin/env bash
#
# Copyright 2025 The Fuchsia Authors
#
# Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
# <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
# license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
# This file may not be copied, modified, or distributed except according to
# those terms.

````

<a id="text-23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d"></a>
### Text `23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d`
- SHA-256: `23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d`
- Exact source bytes: `321`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/unicode-normalization@0.1.25 — `COPYRIGHT` (archive_named_legal_file)
  - pkg:cargo/unicode-width@0.2.2 — `COPYRIGHT` (archive_named_legal_file)
````text
Licensed under the Apache License, Version 2.0
<LICENSE-APACHE or
http://www.apache.org/licenses/LICENSE-2.0> or the MIT
license <LICENSE-MIT or http://opensource.org/licenses/MIT>,
at your option. All files in the project carrying such
notice may not be copied, modified, or distributed except
according to those terms.

````

<a id="text-23d6f253d73a884498c6979c2d94f9aeaeb9d244557729b7706a332c16bce2f1"></a>
### Text `23d6f253d73a884498c6979c2d94f9aeaeb9d244557729b7706a332c16bce2f1`
- SHA-256: `23d6f253d73a884498c6979c2d94f9aeaeb9d244557729b7706a332c16bce2f1`
- Exact source bytes: `1075`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/interpolator@0.5.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/manyhow@0.11.4 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/proc-macro-utils@0.10.0 — `LICENSE-MIT` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2023 Roland Fredenhagen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"></a>
### Text `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`
- SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`
- Exact source bytes: `1023`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/anyhow@1.0.104 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/displaydoc@0.2.7 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/itoa@1.0.18 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/lexical-parse-float@1.0.6 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/lexical-parse-integer@1.0.6 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/lexical-util@1.0.7 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/once_cell@1.21.4 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/proc-macro2@1.0.107 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/quote@1.0.47 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/rustversion@1.0.23 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/semver@1.0.28 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/serde@1.0.229 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/serde_core@1.0.229 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/serde_derive@1.0.229 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/serde_json@1.0.151 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/syn@2.0.119 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/syn@3.0.3 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/thin-vec@0.2.19 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/thiserror@2.0.20 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/thiserror-impl@2.0.20 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/unicode-ident@1.0.24 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/zmij@1.0.23 — `LICENSE-MIT` (archive_named_legal_file)
````text
Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-25554ab20d1f5810583755711f6fece5895bee1527c3ab7ee7580985a891e262"></a>
### Text `25554ab20d1f5810583755711f6fece5895bee1527c3ab7ee7580985a891e262`
- SHA-256: `25554ab20d1f5810583755711f6fece5895bee1527c3ab7ee7580985a891e262`
- Exact source bytes: `487`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/unicode-width@0.2.2 — `scripts/unicode.py` (archive_legal_header_block)
````text
#!/usr/bin/env python3
#
# Copyright 2011-2025 The Rust Project Developers. See the COPYRIGHT
# file at the top-level directory of this distribution and at
# http://rust-lang.org/COPYRIGHT.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

````

<a id="text-2563a9437ab9ee8c7ad1fe59ad9150449088da8cb7bc4eb27401cfd7012a271f"></a>
### Text `2563a9437ab9ee8c7ad1fe59ad9150449088da8cb7bc4eb27401cfd7012a271f`
- SHA-256: `2563a9437ab9ee8c7ad1fe59ad9150449088da8cb7bc4eb27401cfd7012a271f`
- Exact source bytes: `1118`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/fancy-regex@0.17.0 — `benches/bench.rs` (archive_legal_header_block)
  - pkg:cargo/fancy-regex@0.17.0 — `examples/toy.rs` (archive_legal_header_block)
  - pkg:cargo/fancy-regex@0.17.0 — `src/analyze.rs` (archive_legal_header_block)
  - pkg:cargo/fancy-regex@0.17.0 — `src/compile.rs` (archive_legal_header_block)
  - pkg:cargo/fancy-regex@0.17.0 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/fancy-regex@0.17.0 — `src/parse.rs` (archive_legal_header_block)
  - pkg:cargo/fancy-regex@0.17.0 — `src/vm.rs` (archive_legal_header_block)
````text
// Copyright 2016 The Fancy Regex Authors.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

````

<a id="text-2728151294eb93196ab6dd7cb28ddc6e9ab76bf7ebf8c2e1a15f0d2221c98c76"></a>
### Text `2728151294eb93196ab6dd7cb28ddc6e9ab76bf7ebf8c2e1a15f0d2221c98c76`
- SHA-256: `2728151294eb93196ab6dd7cb28ddc6e9ab76bf7ebf8c2e1a15f0d2221c98c76`
- Exact source bytes: `1422`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/exp2.rs` (archive_legal_header_block)
````text
// origin: FreeBSD /usr/src/lib/msun/src/s_exp2.c */
//-
// Copyright (c) 2005 David Schultz <das@FreeBSD.ORG>
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
// 1. Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.
//
// THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
// OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
// HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
// LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
// OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
// SUCH DAMAGE.

````

<a id="text-27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac"></a>
### Text `27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac`
- SHA-256: `27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac`
- Exact source bytes: `1054`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/autocfg@1.5.1 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2018 Josh Stone

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-2920d95f305fc6b013622b65b2ed60fa82026ab1f0d32e8b039f9981b0c04cef"></a>
### Text `2920d95f305fc6b013622b65b2ed60fa82026ab1f0d32e8b039f9981b0c04cef`
- SHA-256: `2920d95f305fc6b013622b65b2ed60fa82026ab1f0d32e8b039f9981b0c04cef`
- Exact source bytes: `486`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/unicode-normalization@0.1.25 — `scripts/unicode.py` (archive_legal_header_block)
````text
#!/usr/bin/env python
#
# Copyright 2011-2018 The Rust Project Developers. See the COPYRIGHT
# file at the top-level directory of this distribution and at
# http://rust-lang.org/COPYRIGHT.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

````

<a id="text-29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4"></a>
### Text `29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4`
- SHA-256: `29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4`
- Exact source bytes: `1130`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/getrandom@0.3.4 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2018-2025 The rust-random Project Developers
Copyright (c) 2014 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-2afdd30d54b4d62b6f488a6bcc1546e84ec5061f13f4209c03d012348783795a"></a>
### Text `2afdd30d54b4d62b6f488a6bcc1546e84ec5061f13f4209c03d012348783795a`
- SHA-256: `2afdd30d54b4d62b6f488a6bcc1546e84ec5061f13f4209c03d012348783795a`
- Exact source bytes: `1080`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/speedate@0.17.0 — `LICENSE` (archive_named_legal_file)
````text
The MIT License (MIT)

Copyright (c) 2022 Samuel Colvin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-2e2f50240bb6b9740e20cfcbd770139f485a055088e4bbf6f48fc4e6214c38d0"></a>
### Text `2e2f50240bb6b9740e20cfcbd770139f485a055088e4bbf6f48fc4e6214c38d0`
- SHA-256: `2e2f50240bb6b9740e20cfcbd770139f485a055088e4bbf6f48fc4e6214c38d0`
- Exact source bytes: `471`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/unicode-width@0.2.2 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/unicode-width@0.2.2 — `src/tables.rs` (archive_legal_header_block)
  - pkg:cargo/unicode-width@0.2.2 — `tests/tests.rs` (archive_legal_header_block)
````text
// Copyright 2012-2025 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652"></a>
### Text `30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652`
- SHA-256: `30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652`
- Exact source bytes: `1022`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/rustc-hash@2.1.3 — `LICENSE-MIT` (archive_named_legal_file)
````text
Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
````

<a id="text-31763fd3a985beee0412efbb0983721462c7a704829c473d9747fda4728f0918"></a>
### Text `31763fd3a985beee0412efbb0983721462c7a704829c473d9747fda4728f0918`
- SHA-256: `31763fd3a985beee0412efbb0983721462c7a704829c473d9747fda4728f0918`
- Exact source bytes: `355`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/rand@0.8.7 — `src/distributions/slice.rs` (archive_legal_header_block)
````text
// Copyright 2021 Developers of the Rand project.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-347f2c2000ae198c8ac874f7d7812aa8dffc1a55e1e84defc4cf0661ab2a58ef"></a>
### Text `347f2c2000ae198c8ac874f7d7812aa8dffc1a55e1e84defc4cf0661ab2a58ef`
- SHA-256: `347f2c2000ae198c8ac874f7d7812aa8dffc1a55e1e84defc4cf0661ab2a58ef`
- Exact source bytes: `471`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/bit-vec@0.8.0 — `src/lib.rs` (archive_legal_header_block)
````text
// Copyright 2012-2023 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab"></a>
### Text `35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab`
- SHA-256: `35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab`
- Exact source bytes: `9724`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/rand@0.8.7 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     https://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

````

<a id="text-36516aefdc84c5d5a1e7485425913a22dbda69eb1930c5e84d6ae4972b5194b9"></a>
### Text `36516aefdc84c5d5a1e7485425913a22dbda69eb1930c5e84d6ae4972b5194b9`
- SHA-256: `36516aefdc84c5d5a1e7485425913a22dbda69eb1930c5e84d6ae4972b5194b9`
- Exact source bytes: `1046`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/allocator-api2@0.2.21 — `LICENSE-MIT` (archive_named_legal_file)
````text
Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"></a>
### Text `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`
- SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`
- Exact source bytes: `1057`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/cfg-if@1.0.4 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2014 Alex Crichton

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-3823dda7cf046602f4b4e77ec8e227863dc4736037cc85bb33d9f19febe16bb7"></a>
### Text `3823dda7cf046602f4b4e77ec8e227863dc4736037cc85bb33d9f19febe16bb7`
- SHA-256: `3823dda7cf046602f4b4e77ec8e227863dc4736037cc85bb33d9f19febe16bb7`
- Exact source bytes: `14088`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `LICENSE.txt` (archive_named_legal_file)
````text
rust-lang/libm as a whole is available for use under the MIT license:

------------------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
------------------------------------------------------------------------------

As a contributor, you agree that your code can be used under either the MIT
license or the Apache-2.0 license:

------------------------------------------------------------------------------
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
------------------------------------------------------------------------------

This Rust library contains the following copyrights:

    Copyright (c) 2018 Jorge Aparicio

Portions of this software are derived from third-party works licensed under
terms compatible with the above MIT license:

* musl libc https://www.musl-libc.org/. This library contains the following
  copyright:

      Copyright © 2005-2020 Rich Felker, et al.

* The CORE-MATH project https://core-math.gitlabpages.inria.fr/. CORE-MATH
  routines are available under the MIT license on a per-file basis.

The musl libc COPYRIGHT file also includes the following notice relevant to
math portions of the library:

------------------------------------------------------------------------------
Much of the math library code (src/math/* and src/complex/*) is
Copyright © 1993,2004 Sun Microsystems or
Copyright © 2003-2011 David Schultz or
Copyright © 2003-2009 Steven G. Kargl or
Copyright © 2003-2009 Bruce D. Evans or
Copyright © 2008 Stephen L. Moshier or
Copyright © 2017-2018 Arm Limited
and labelled as such in comments in the individual source files. All
have been licensed under extremely permissive terms.
------------------------------------------------------------------------------

Copyright notices are retained in src/* files where relevant.

````

<a id="text-388ab80c8f3a357eaf6c89d831047392791cb8439a538dedf1a2af6f05a7c344"></a>
### Text `388ab80c8f3a357eaf6c89d831047392791cb8439a538dedf1a2af6f05a7c344`
- SHA-256: `388ab80c8f3a357eaf6c89d831047392791cb8439a538dedf1a2af6f05a7c344`
- Exact source bytes: `440`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `src/byte_slice.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/pointer/inner.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/pointer/invariant.rs` (archive_legal_header_block)
````text
// SPDX-License-Identifier: BSD-2-Clause OR Apache-2.0 OR MIT
//
// Copyright 2024 The Fuchsia Authors
//
// Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-39b6a8b9fcf1a0185dc399cd87da2e7010226744172e83fcdb218f0b6079dcf3"></a>
### Text `39b6a8b9fcf1a0185dc399cd87da2e7010226744172e83fcdb218f0b6079dcf3`
- SHA-256: `39b6a8b9fcf1a0185dc399cd87da2e7010226744172e83fcdb218f0b6079dcf3`
- Exact source bytes: `190`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/grow-data.32.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: grow-data.32
#
# machine-generated by: ucptrietest.c

````

<a id="text-3b7df402160fc95c1ec4d256f720da6b75b1c5c69ad6826acfa5f096e349a42c"></a>
### Text `3b7df402160fc95c1ec4d256f720da6b75b1c5c69ad6826acfa5f096e349a42c`
- SHA-256: `3b7df402160fc95c1ec4d256f720da6b75b1c5c69ad6826acfa5f096e349a42c`
- Exact source bytes: `466`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/bitflags@2.13.1 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/siphasher@1.0.3 — `src/tests.rs` (archive_legal_header_block)
  - pkg:cargo/siphasher@1.0.3 — `src/tests128.rs` (archive_legal_header_block)
````text
// Copyright 2014 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-3bc70e239e91272782006c638fc0452a714d384224f11f0923036b7be07cf9b5"></a>
### Text `3bc70e239e91272782006c638fc0452a714d384224f11f0923036b7be07cf9b5`
- SHA-256: `3bc70e239e91272782006c638fc0452a714d384224f11f0923036b7be07cf9b5`
- Exact source bytes: `1081`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/fancy-regex@0.17.0 — `LICENSE` (archive_named_legal_file)
````text
The MIT License

Copyright 2015 The Fancy Regex Authors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

````

<a id="text-3c2c9de0245f30e640e8a22b4525d04a3c8e2323a2ee7b96befbb28cdca4066e"></a>
### Text `3c2c9de0245f30e640e8a22b4525d04a3c8e2323a2ee7b96befbb28cdca4066e`
- SHA-256: `3c2c9de0245f30e640e8a22b4525d04a3c8e2323a2ee7b96befbb28cdca4066e`
- Exact source bytes: `190`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set-empty.16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set-empty.16
#
# machine-generated by: ucptrietest.c

````

<a id="text-3e4240602e3018225d203839bb70430c8a6a173c0307f1ea2872e90be9a5a137"></a>
### Text `3e4240602e3018225d203839bb70430c8a6a173c0307f1ea2872e90be9a5a137`
- SHA-256: `3e4240602e3018225d203839bb70430c8a6a173c0307f1ea2872e90be9a5a137`
- Exact source bytes: `197`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set-single-value.16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set-single-value.16
#
# machine-generated by: ucptrietest.c

````

<a id="text-3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c"></a>
### Text `3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c`
- SHA-256: `3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c`
- Exact source bytes: `1053`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/utf8_iter@1.0.4 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright Mozilla Foundation

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-411781fd38700f2357a14126d0ab048164ab881f1dcb335c1bb932e232c9a2f5"></a>
### Text `411781fd38700f2357a14126d0ab048164ab881f1dcb335c1bb932e232c9a2f5`
- SHA-256: `411781fd38700f2357a14126d0ab048164ab881f1dcb335c1bb932e232c9a2f5`
- Exact source bytes: `1082`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/bitvec@1.1.1 — `LICENSE.txt` (archive_named_legal_file)
  - pkg:cargo/wyz@0.5.1 — `LICENSE.txt` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2018 myrrlyn (Alexander Payne)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-41ace205715d9f19a3214218cc1c01d57c533e02cd0fef7c8e51a49a7fce5ac5"></a>
### Text `41ace205715d9f19a3214218cc1c01d57c533e02cd0fef7c8e51a49a7fce5ac5`
- SHA-256: `41ace205715d9f19a3214218cc1c01d57c533e02cd0fef7c8e51a49a7fce5ac5`
- Exact source bytes: `864`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/tinyvec_macros@0.1.1 — `LICENSE-ZLIB.md` (archive_named_legal_file)
````text
zlib License

(C) 2020 Tomasz "Soveu" Marx

This software is provided 'as-is', without any express or implied
warranty.  In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.

````

<a id="text-42fa16951ce7f24b5a467a40e5b449a1d41e662f97ca779864f053f39e097737"></a>
### Text `42fa16951ce7f24b5a467a40e5b449a1d41e662f97ca779864f053f39e097737`
- SHA-256: `42fa16951ce7f24b5a467a40e5b449a1d41e662f97ca779864f053f39e097737`
- Exact source bytes: `1130`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/getrandom@0.2.17 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2018-2024 The rust-random Project Developers
Copyright (c) 2014 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1"></a>
### Text `4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1`
- SHA-256: `4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1`
- Exact source bytes: `1092`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/shlex@1.3.0 — `LICENSE-MIT` (archive_named_legal_file)
````text
The MIT License (MIT)

Copyright (c) 2015 Nicholas Allegra (comex).

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

````

<a id="text-4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f"></a>
### Text `4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f`
- SHA-256: `4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f`
- Exact source bytes: `1076`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/ppv-lite86@0.2.21 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2019 The CryptoCorrosion Contributors

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-4d6a22864230012069284ffc528e169aa077cb0a96dbac8d144ce42df8261c15"></a>
### Text `4d6a22864230012069284ffc528e169aa077cb0a96dbac8d144ce42df8261c15`
- SHA-256: `4d6a22864230012069284ffc528e169aa077cb0a96dbac8d144ce42df8261c15`
- Exact source bytes: `431`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/array.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/base.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/bundle.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/data.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/date.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/dictionary.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/filedescriptor.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/messageport.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/number.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/propertylist.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/runloop.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/set.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/string.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/timezone.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/url.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/uuid.rs` (archive_legal_header_block)
````text
// Copyright 2013-2015 The Servo Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-4d854c78554e7b14dd38275a06a5ec9ea6294e514a6cd609136f5f9feb5bfb06"></a>
### Text `4d854c78554e7b14dd38275a06a5ec9ea6294e514a6cd609136f5f9feb5bfb06`
- SHA-256: `4d854c78554e7b14dd38275a06a5ec9ea6294e514a6cd609136f5f9feb5bfb06`
- Exact source bytes: `32`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/stable_deref_trait@1.2.1 — `src/lib.rs` (archive_legal_header_block)
````text
// Copyright 2017 Robert Grosse

````

<a id="text-4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871"></a>
### Text `4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871`
- SHA-256: `4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871`
- Exact source bytes: `1071`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/arrayvec@0.7.8 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) Ulrik Sverdrup "bluss" 2015-2023

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-4db045835f216d50e0ac5bc3742ddd91756257a8c96578f9f98545d58a1237df"></a>
### Text `4db045835f216d50e0ac5bc3742ddd91756257a8c96578f9f98545d58a1237df`
- SHA-256: `4db045835f216d50e0ac5bc3742ddd91756257a8c96578f9f98545d58a1237df`
- Exact source bytes: `1075`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/collection_literals@1.0.3 — `LICENSE` (archive_named_legal_file)
````text
Copyright (c) The collection_literals Contributors

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-4e3aca3dd41be9fb851fb8b9ce7e226675b0d38253d464ed6c27bff955f4c3d6"></a>
### Text `4e3aca3dd41be9fb851fb8b9ce7e226675b0d38253d464ed6c27bff955f4c3d6`
- SHA-256: `4e3aca3dd41be9fb851fb8b9ce7e226675b0d38253d464ed6c27bff955f4c3d6`
- Exact source bytes: `192`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/char16trie/months.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: months.toml
#
# machine-generated by: ucharstrietest.c

````

<a id="text-4e586e422c78f9cd82f86003cb32bf03311334fde19afab31904a7b5b3d5b671"></a>
### Text `4e586e422c78f9cd82f86003cb32bf03311334fde19afab31904a7b5b3d5b671`
- SHA-256: `4e586e422c78f9cd82f86003cb32bf03311334fde19afab31904a7b5b3d5b671`
- Exact source bytes: `196`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set-single-value.8.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set-single-value.8
#
# machine-generated by: ucptrietest.c

````

<a id="text-4f2c4ed3fc3a86bde1cb544218f8cc519cac8cce0382f3ec0cad53ed8e7a787c"></a>
### Text `4f2c4ed3fc3a86bde1cb544218f8cc519cac8cce0382f3ec0cad53ed8e7a787c`
- SHA-256: `4f2c4ed3fc3a86bde1cb544218f8cc519cac8cce0382f3ec0cad53ed8e7a787c`
- Exact source bytes: `430`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/ptr-is-invariant-over-v.rs` (archive_legal_header_block)
````text
// Copyright 2025 The Fuchsia Authors
//
// Licensed under the 2-Clause BSD License <LICENSE-BSD or
// https://opensource.org/license/bsd-2-clause>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-4f44572785f35152c1fd2eadf565b7e079c0f300b4324f0af653419f9d76b735"></a>
### Text `4f44572785f35152c1fd2eadf565b7e079c0f300b4324f0af653419f9d76b735`
- SHA-256: `4f44572785f35152c1fd2eadf565b7e079c0f300b4324f0af653419f9d76b735`
- Exact source bytes: `11350`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/tinyvec_macros@0.1.1 — `LICENSE-APACHE.md` (archive_named_legal_file)
````text
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2020 Tomasz "Soveu" Marx

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

````

<a id="text-51ec638fc82fe0599885f52546681020dd371528562e0a1ca0b44ac7b3ed6583"></a>
### Text `51ec638fc82fe0599885f52546681020dd371528562e0a1ca0b44ac7b3ed6583`
- SHA-256: `51ec638fc82fe0599885f52546681020dd371528562e0a1ca0b44ac7b3ed6583`
- Exact source bytes: `191`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/char16trie/empty.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: empty.toml
#
# machine-generated by: ucharstrietest.c

````

<a id="text-54ae92b804ef9e09d376213e3878c9649e417531a2d81d74e8a1fa2be2f0b94a"></a>
### Text `54ae92b804ef9e09d376213e3878c9649e417531a2d81d74e8a1fa2be2f0b94a`
- SHA-256: `54ae92b804ef9e09d376213e3878c9649e417531a2d81d74e8a1fa2be2f0b94a`
- Exact source bytes: `192`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/free-blocks.32.toml` starting line 5 (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: free-blocks.32
#
# machine-generated by: ucptrietest.c

````

<a id="text-553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583"></a>
### Text `553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583`
- SHA-256: `553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583`
- Exact source bytes: `566`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/shlex@1.3.0 — `LICENSE-APACHE` (archive_named_legal_file)
````text
Copyright 2015 Nicholas Allegra (comex).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

````

<a id="text-562c625100a5ee635f35de5908c206b7d8783e4dcd10ede1c90e4c0e7dddfe5f"></a>
### Text `562c625100a5ee635f35de5908c206b7d8783e4dcd10ede1c90e4c0e7dddfe5f`
- SHA-256: `562c625100a5ee635f35de5908c206b7d8783e4dcd10ede1c90e4c0e7dddfe5f`
- Exact source bytes: `1075`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/attribute-derive@0.10.5 — `LICENSE-MIT` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2024 Roland Fredenhagen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-5822e59f88392b4a35965134c4c974e475959ebc625f140e42b1f39ba2495cc7"></a>
### Text `5822e59f88392b4a35965134c4c974e475959ebc625f140e42b1f39ba2495cc7`
- SHA-256: `5822e59f88392b4a35965134c4c974e475959ebc625f140e42b1f39ba2495cc7`
- Exact source bytes: `537`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/serde_json@1.0.151 — `src/lexical/mod.rs` (archive_legal_header_block)
````text
// The code in this module is derived from the `lexical` crate by @Alexhuszagh
// which the author condensed into this minimal subset for use in serde_json.
// For the serde_json use case we care more about reliably round tripping all
// possible floating point values than about parsing any arbitrarily long string
// of digits with perfect accuracy, as the latter would take a high cost in
// compile time and performance.
//
// Dual licensed as MIT and Apache 2.0 just like the rest of serde_json, but
// copyright Alexander Huszagh.

````

<a id="text-58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd"></a>
### Text `58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd`
- SHA-256: `58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd`
- Exact source bytes: `11357`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/is-macro@0.3.7 — `LICENSE` (archive_named_legal_file)
````text

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
````

<a id="text-59a322909293377fdc4ff626c4bd146f046119c3eac7e2add27385db6e38926e"></a>
### Text `59a322909293377fdc4ff626c4bd146f046119c3eac7e2add27385db6e38926e`
- SHA-256: `59a322909293377fdc4ff626c4bd146f046119c3eac7e2add27385db6e38926e`
- Exact source bytes: `200`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set3-initial-9.small16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set3-initial-9.small16
#
# machine-generated by: ucptrietest.c

````

<a id="text-59ee71a59035c18a5043881ef760e797cc17dc0cfd65eb43075f72a0ecf8292a"></a>
### Text `59ee71a59035c18a5043881ef760e797cc17dc0cfd65eb43075f72a0ecf8292a`
- SHA-256: `59ee71a59035c18a5043881ef760e797cc17dc0cfd65eb43075f72a0ecf8292a`
- Exact source bytes: `428`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/tan.rs` (archive_legal_header_block)
````text
// origin: FreeBSD /usr/src/lib/msun/src/s_tan.c */
//
// ====================================================
// Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
//
// Developed at SunPro, a Sun Microsystems, Inc. business.
// Permission to use, copy, modify, and distribute this
// software is freely granted, provided that this notice
// is preserved.
// ====================================================

````

<a id="text-5a534ed1f9266ed799e9f2e3f830f15411762021829da121b23df5edc498c6b6"></a>
### Text `5a534ed1f9266ed799e9f2e3f830f15411762021829da121b23df5edc498c6b6`
- SHA-256: `5a534ed1f9266ed799e9f2e3f830f15411762021829da121b23df5edc498c6b6`
- Exact source bytes: `314`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/k_tanf.rs` starting line 2 (archive_legal_header_block)
````text
/*
 * ====================================================
 * Copyright 2004 Sun Microsystems, Inc.  All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this
 * software is freely granted, provided that this notice
 * is preserved.
 * ====================================================
 */
````

<a id="text-5c9d9df788ce35272ca21ab16e09e947bd2883bf6858f1b8160ea8ad1948c7c6"></a>
### Text `5c9d9df788ce35272ca21ab16e09e947bd2883bf6858f1b8160ea8ad1948c7c6`
- SHA-256: `5c9d9df788ce35272ca21ab16e09e947bd2883bf6858f1b8160ea8ad1948c7c6`
- Exact source bytes: `467`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_plain_legal_section`
- Occurrences:
  - pkg:cargo/bstr@1.13.1 — `README.md` starting line 226 (archive_plain_legal_section)
````text
### License

This project is licensed under either of

 * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
   https://www.apache.org/licenses/LICENSE-2.0)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or
   https://opensource.org/licenses/MIT)

at your option.

The data in `src/unicode/data/` is licensed under the Unicode License Agreement
([LICENSE-UNICODE](https://www.unicode.org/copyright.html#License)), although
this data is only used in tests.

````

<a id="text-5d392ff1ac69a18c9beb41720ecbfd56f7792a1ec4321428e73757d4283f5a61"></a>
### Text `5d392ff1ac69a18c9beb41720ecbfd56f7792a1ec4321428e73757d4283f5a61`
- SHA-256: `5d392ff1ac69a18c9beb41720ecbfd56f7792a1ec4321428e73757d4283f5a61`
- Exact source bytes: `466`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/log@0.4.33 — `src/lib.rs` (archive_legal_header_block)
````text
// Copyright 2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-5d906a2707a058a8338b20e59d67581a4eb1fc949dabccd1396f790c62ac7f77"></a>
### Text `5d906a2707a058a8338b20e59d67581a4eb1fc949dabccd1396f790c62ac7f77`
- SHA-256: `5d906a2707a058a8338b20e59d67581a4eb1fc949dabccd1396f790c62ac7f77`
- Exact source bytes: `489`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/unicode-width@0.2.2 — `benches/benches.rs` (archive_legal_header_block)
````text
// Copyright 2012-2025 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.
#![feature(test)]

````

<a id="text-5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7"></a>
### Text `5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7`
- SHA-256: `5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7`
- Exact source bytes: `1056`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/stable_deref_trait@1.2.1 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2017 Robert Grosse

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
````

<a id="text-5eb447ab49a139299a9242218745eaf936ec997fcb32ea17c8d8ee855cd78686"></a>
### Text `5eb447ab49a139299a9242218745eaf936ec997fcb32ea17c8d8ee855cd78686`
- SHA-256: `5eb447ab49a139299a9242218745eaf936ec997fcb32ea17c8d8ee855cd78686`
- Exact source bytes: `1690`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/num-bigint@0.4.8 — `benches/shootout-pidigits.rs` starting line 6 (archive_legal_header_block)
````text
// Copyright (c) 2013-2014 The Rust Project Developers
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
//
// - Redistributions of source code must retain the above copyright
//   notice, this list of conditions and the following disclaimer.
//
// - Redistributions in binary form must reproduce the above copyright
//   notice, this list of conditions and the following disclaimer in
//   the documentation and/or other materials provided with the
//   distribution.
//
// - Neither the name of "The Computer Language Benchmarks Game" nor
//   the name of "The Computer Language Shootout Benchmarks" nor the
//   names of its contributors may be used to endorse or promote
//   products derived from this software without specific prior
//   written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
// FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
// COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
// INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
// SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
// HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
// STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
// OF THE POSSIBILITY OF SUCH DAMAGE.

````

<a id="text-60700d351cac4650c51f3f9db318d2a420f8b45052dba2715eb5fec41f0f6956"></a>
### Text `60700d351cac4650c51f3f9db318d2a420f8b45052dba2715eb5fec41f0f6956`
- SHA-256: `60700d351cac4650c51f3f9db318d2a420f8b45052dba2715eb5fec41f0f6956`
- Exact source bytes: `4387`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `font_license_file`
- Occurrences:
  - Azdaja bundled font asset — `site/fonts/Cormorant-Garamond-OFL.txt` (font_license_file)
````text
Copyright 2015 the Cormorant Project Authors (github.com/CatharsisFonts/Cormorant)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at:
https://scripts.sil.org/OFL


-----------------------------------------------------------
SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007
-----------------------------------------------------------

PREAMBLE
The goals of the Open Font License (OFL) are to stimulate worldwide
development of collaborative font projects, to support the font creation
efforts of academic and linguistic communities, and to provide a free and
open framework in which fonts may be shared and improved in partnership
with others.

The OFL allows the licensed fonts to be used, studied, modified and
redistributed freely as long as they are not sold by themselves. The
fonts, including any derivative works, can be bundled, embedded, 
redistributed and/or sold with any software provided that any reserved
names are not used by derivative works. The fonts and derivatives,
however, cannot be released under any other type of license. The
requirement for fonts to remain under this license does not apply
to any document created using the fonts or their derivatives.

DEFINITIONS
"Font Software" refers to the set of files released by the Copyright
Holder(s) under this license and clearly marked as such. This may
include source files, build scripts and documentation.

"Reserved Font Name" refers to any names specified as such after the
copyright statement(s).

"Original Version" refers to the collection of Font Software components as
distributed by the Copyright Holder(s).

"Modified Version" refers to any derivative made by adding to, deleting,
or substituting -- in part or in whole -- any of the components of the
Original Version, by changing formats or by porting the Font Software to a
new environment.

"Author" refers to any designer, engineer, programmer, technical
writer or other person who contributed to the Font Software.

PERMISSION & CONDITIONS
Permission is hereby granted, free of charge, to any person obtaining
a copy of the Font Software, to use, study, copy, merge, embed, modify,
redistribute, and sell modified and unmodified copies of the Font
Software, subject to the following conditions:

1) Neither the Font Software nor any of its individual components,
in Original or Modified Versions, may be sold by itself.

2) Original or Modified Versions of the Font Software may be bundled,
redistributed and/or sold with any software, provided that each copy
contains the above copyright notice and this license. These can be
included either as stand-alone text files, human-readable headers or
in the appropriate machine-readable metadata fields within text or
binary files as long as those fields can be easily viewed by the user.

3) No Modified Version of the Font Software may use the Reserved Font
Name(s) unless explicit written permission is granted by the corresponding
Copyright Holder. This restriction only applies to the primary font name as
presented to the users.

4) The name(s) of the Copyright Holder(s) or the Author(s) of the Font
Software shall not be used to promote, endorse or advertise any
Modified Version, except to acknowledge the contribution(s) of the
Copyright Holder(s) and the Author(s) or with their explicit written
permission.

5) The Font Software, modified or unmodified, in part or in whole,
must be distributed entirely under this license, and must not be
distributed under any other license. The requirement for fonts to
remain under this license does not apply to any document created
using the Font Software.

TERMINATION
This license becomes null and void if any of the above conditions are
not met.

DISCLAIMER
THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
OF COPYRIGHT, PATENT, TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL THE
COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
INCLUDING ANY GENERAL, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
DAMAGES, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF THE USE OR INABILITY TO USE THE FONT SOFTWARE OR FROM
OTHER DEALINGS IN THE FONT SOFTWARE.

````

<a id="text-60b302e19911888d62ded3a5b4046eaf884778d9423715c720ea42376979122f"></a>
### Text `60b302e19911888d62ded3a5b4046eaf884778d9423715c720ea42376979122f`
- SHA-256: `60b302e19911888d62ded3a5b4046eaf884778d9423715c720ea42376979122f`
- Exact source bytes: `407`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/rand@0.8.7 — `src/distributions/uniform.rs` (archive_legal_header_block)
````text
// Copyright 2018-2020 Developers of the Rand project.
// Copyright 2017 The Rust Project Developers.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-612efb98c85f9cec3dbeb80a43e139beb7c35298d01e2d58adca703e64360da3"></a>
### Text `612efb98c85f9cec3dbeb80a43e139beb7c35298d01e2d58adca703e64360da3`
- SHA-256: `612efb98c85f9cec3dbeb80a43e139beb7c35298d01e2d58adca703e64360da3`
- Exact source bytes: `195`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/grow-data.small16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: grow-data.small16
#
# machine-generated by: ucptrietest.c

````

<a id="text-62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3"></a>
### Text `62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3`
- SHA-256: `62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3`
- Exact source bytes: `1067`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/core-foundation-sys@0.8.7 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2012-2013 Mozilla Foundation

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"></a>
### Text `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`
- SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`
- Exact source bytes: `9723`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/anyhow@1.0.104 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/itoa@1.0.18 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/libc@0.2.189 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/proc-macro2@1.0.107 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/quote@1.0.47 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/rustversion@1.0.23 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/ryu@1.0.23 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/semver@1.0.28 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/serde@1.0.229 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/serde_core@1.0.229 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/serde_derive@1.0.229 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/serde_json@1.0.151 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/syn@2.0.119 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/syn@3.0.3 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/thin-vec@0.2.19 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/thiserror@2.0.20 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/thiserror-impl@2.0.20 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/unicode-ident@1.0.24 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/vte@0.14.1 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

````

<a id="text-64404f740af59299f95e50eae055069fb74bd5ae794f80acdc60412b85c413ef"></a>
### Text `64404f740af59299f95e50eae055069fb74bd5ae794f80acdc60412b85c413ef`
- SHA-256: `64404f740af59299f95e50eae055069fb74bd5ae794f80acdc60412b85c413ef`
- Exact source bytes: `363`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `AGENTS.md` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `agent_docs/development.md` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `agent_docs/reviewing.md` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `agent_docs/style.md` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `agent_docs/ui_tests.md` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `agent_docs/unsafe_code.md` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `agent_docs/validation.md` (archive_legal_header_block)
````text
<!-- Copyright 2025 The Fuchsia Authors

Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
<LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
This file may not be copied, modified, or distributed except according to
those terms. -->
````

<a id="text-6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"></a>
### Text `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`
- SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`
- Exact source bytes: `1071`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/bitflags@2.13.1 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/getopts@0.2.24 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/log@0.4.33 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/num-bigint@0.4.8 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/num-integer@0.1.46 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/num-traits@0.2.19 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/regex@1.13.1 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/regex-automata@0.4.18 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/regex-syntax@0.8.11 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2014 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-64aa46cb220cae30db13a5a9f6a3adc56589b4963ddc7062e5b8657dabcb0e58"></a>
### Text `64aa46cb220cae30db13a5a9f6a3adc56589b4963ddc7062e5b8657dabcb0e58`
- SHA-256: `64aa46cb220cae30db13a5a9f6a3adc56589b4963ddc7062e5b8657dabcb0e58`
- Exact source bytes: `390`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `ci/check_stale_stderr.sh` (archive_legal_header_block)
````text
#!/usr/bin/env bash
#
# Copyright 2026 The Fuchsia Authors
#
# Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
# <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
# license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
# This file may not be copied, modified, or distributed except according to
# those terms.

````

<a id="text-64f88915058f45a4396fd174e037b1aa7a25ff920bdabb22f204a3e6dda5cca7"></a>
### Text `64f88915058f45a4396fd174e037b1aa7a25ff920bdabb22f204a3e6dda5cca7`
- SHA-256: `64f88915058f45a4396fd174e037b1aa7a25ff920bdabb22f204a3e6dda5cca7`
- Exact source bytes: `517`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `README.md` (archive_legal_header_block)
````text
<!-- Copyright 2024 The Fuchsia Authors

Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
<LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
This file may not be copied, modified, or distributed except according to
those terms.

WARNING: DO NOT EDIT THIS FILE. It is generated automatically. Edits should be
made in the doc comment on `src/lib.rs` or in `../tools/generate-readme`.
-->
````

<a id="text-66a9cd5772937b5ecd2c60734ab5d653c299965caad230e941f7fedc84587651"></a>
### Text `66a9cd5772937b5ecd2c60734ab5d653c299965caad230e941f7fedc84587651`
- SHA-256: `66a9cd5772937b5ecd2c60734ab5d653c299965caad230e941f7fedc84587651`
- Exact source bytes: `189`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set-empty.8.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set-empty.8
#
# machine-generated by: ucptrietest.c

````

<a id="text-68653aaa727a2bfa31b7a751e31701ce33c49d695c12dd291a07d1c54da4c14b"></a>
### Text `68653aaa727a2bfa31b7a751e31701ce33c49d695c12dd291a07d1c54da4c14b`
- SHA-256: `68653aaa727a2bfa31b7a751e31701ce33c49d695c12dd291a07d1c54da4c14b`
- Exact source bytes: `262`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/bstr@1.13.1 — `COPYING` (archive_named_legal_file)
````text
This project is licensed under either of

 * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
   https://www.apache.org/licenses/LICENSE-2.0)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or
   https://opensource.org/licenses/MIT)

at your option.

````

<a id="text-691d2d8b780bfb116d8da2b446109c3fcce7609679713b8d5b5a61865d709250"></a>
### Text `691d2d8b780bfb116d8da2b446109c3fcce7609679713b8d5b5a61865d709250`
- SHA-256: `691d2d8b780bfb116d8da2b446109c3fcce7609679713b8d5b5a61865d709250`
- Exact source bytes: `204`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/char16trie/test_long_sequence.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: test_long_sequence.toml
#
# machine-generated by: ucharstrietest.c

````

<a id="text-696759d65dfe558ff7d9f031c76db19ec5c0767470fb67c4e8d990820d1e99c9"></a>
### Text `696759d65dfe558ff7d9f031c76db19ec5c0767470fb67c4e8d990820d1e99c9`
- SHA-256: `696759d65dfe558ff7d9f031c76db19ec5c0767470fb67c4e8d990820d1e99c9`
- Exact source bytes: `10832`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/iana-time-zone@0.1.65 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright 2020 Andrew Straw

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

````

<a id="text-69863ca0dc884ec590f75a811f610b2d3ae60bc75d77b591489ab3ea48269625"></a>
### Text `69863ca0dc884ec590f75a811f610b2d3ae60bc75d77b591489ab3ea48269625`
- SHA-256: `69863ca0dc884ec590f75a811f610b2d3ae60bc75d77b591489ab3ea48269625`
- Exact source bytes: `190`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/grow-data.16.toml` starting line 5 (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: grow-data.16
#
# machine-generated by: ucptrietest.c

````

<a id="text-6ac8711fb340c62ce0a4ecd463342d3fa0e8e70de697c863a2e1c0c53006003c"></a>
### Text `6ac8711fb340c62ce0a4ecd463342d3fa0e8e70de697c863a2e1c0c53006003c`
- SHA-256: `6ac8711fb340c62ce0a4ecd463342d3fa0e8e70de697c863a2e1c0c53006003c`
- Exact source bytes: `1084`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/spin@0.9.9 — `LICENSE` (archive_named_legal_file)
````text
The MIT License (MIT)

Copyright (c) 2014 Mathijs van de Nes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
````

<a id="text-6b664a7c3acad25366aba9ee177e0e5de1b377c5f64f3b4a71594536e71bf315"></a>
### Text `6b664a7c3acad25366aba9ee177e0e5de1b377c5f64f3b4a71594536e71bf315`
- SHA-256: `6b664a7c3acad25366aba9ee177e0e5de1b377c5f64f3b4a71594536e71bf315`
- Exact source bytes: `790`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/ryu@1.0.23 — `src/common.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `src/d2s.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `src/d2s_full_table.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `src/d2s_intrinsics.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `src/d2s_small_table.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `src/digit_table.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `src/f2s.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `src/f2s_intrinsics.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `tests/common_test.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `tests/d2s_intrinsics_test.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `tests/d2s_table_test.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `tests/d2s_test.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `tests/f2s_test.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `tests/s2d_test.rs` (archive_legal_header_block)
  - pkg:cargo/ryu@1.0.23 — `tests/s2f_test.rs` (archive_legal_header_block)
````text
// Translated from C to Rust. The original C code can be found at
// https://github.com/ulfjack/ryu and carries the following license:
//
// Copyright 2018 Ulf Adams
//
// The contents of this file may be used under the terms of the Apache License,
// Version 2.0.
//
//    (See accompanying file LICENSE-Apache or copy at
//     http://www.apache.org/licenses/LICENSE-2.0)
//
// Alternatively, the contents of this file may be used under the terms of
// the Boost Software License, Version 1.0.
//    (See accompanying file LICENSE-Boost or copy at
//     https://www.boost.org/LICENSE_1_0.txt)
//
// Unless required by applicable law or agreed to in writing, this software
// is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.

````

<a id="text-6b71b95b501ccc8248effd2044017ed96689943a7e70e49cee66263bca8cebd0"></a>
### Text `6b71b95b501ccc8248effd2044017ed96689943a7e70e49cee66263bca8cebd0`
- SHA-256: `6b71b95b501ccc8248effd2044017ed96689943a7e70e49cee66263bca8cebd0`
- Exact source bytes: `192`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/free-blocks.16.toml` starting line 5 (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: free-blocks.16
#
# machine-generated by: ucptrietest.c

````

<a id="text-6b7374c39a57e57fc2c38eb529c4c88340152b10f51dd5ae2d819dfa67f61715"></a>
### Text `6b7374c39a57e57fc2c38eb529c4c88340152b10f51dd5ae2d819dfa67f61715`
- SHA-256: `6b7374c39a57e57fc2c38eb529c4c88340152b10f51dd5ae2d819dfa67f61715`
- Exact source bytes: `1086`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/bstr@1.13.1 — `LICENSE-MIT` (archive_named_legal_file)
````text
The MIT License (MIT)

Copyright (c) 2018-2019 Andrew Gallant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

````

<a id="text-6d3a9431e65e69c73a8923e6517b889d17549b23db406b9ec027710d16af701f"></a>
### Text `6d3a9431e65e69c73a8923e6517b889d17549b23db406b9ec027710d16af701f`
- SHA-256: `6d3a9431e65e69c73a8923e6517b889d17549b23db406b9ec027710d16af701f`
- Exact source bytes: `1054`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/unicode_names2@1.3.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/unicode_names2_generator@1.3.0 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2014 Huon Wilson

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
````

<a id="text-6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51"></a>
### Text `6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51`
- SHA-256: `6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51`
- Exact source bytes: `10282`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/rand_core@0.6.4 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     https://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

````

<a id="text-6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6"></a>
### Text `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`
- SHA-256: `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`
- Exact source bytes: `1062`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/serde_spanned@1.1.1 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/toml@0.9.12+spec-1.1.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/toml_datetime@0.7.5+spec-1.1.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/toml_parser@1.1.3+spec-1.1.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/toml_writer@1.1.2+spec-1.1.0 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) Individual contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-6f522182efab85555609cec6958526611837eb275ef71410f1c2ef60373ac6ff"></a>
### Text `6f522182efab85555609cec6958526611837eb275ef71410f1c2ef60373ac6ff`
- SHA-256: `6f522182efab85555609cec6958526611837eb275ef71410f1c2ef60373ac6ff`
- Exact source bytes: `198`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/char16trie/test_compact.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: test_compact.toml
#
# machine-generated by: ucharstrietest.c

````

<a id="text-7299168b13050b209679192397a39aee58f9cf65a84bbf8e4fbc873bc00e8883"></a>
### Text `7299168b13050b209679192397a39aee58f9cf65a84bbf8e4fbc873bc00e8883`
- SHA-256: `7299168b13050b209679192397a39aee58f9cf65a84bbf8e4fbc873bc00e8883`
- Exact source bytes: `257`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/unicode_names2@1.3.0 — `data/NameAliases.txt` (archive_legal_header_block)
````text
# NameAliases-16.0.0.txt
# Date: 2024-04-24
# © 2024 Unicode®, Inc.
# Unicode and the Unicode Logo are registered trademarks of Unicode, Inc. in the U.S. and other countries.
# For terms of use and license, see https://www.unicode.org/terms_of_use.html
#

````

<a id="text-72dc4b3a89a21d41d0446b77aedd4c6839324892bd07de227ea0e4ca5bdfbadc"></a>
### Text `72dc4b3a89a21d41d0446b77aedd4c6839324892bd07de227ea0e4ca5bdfbadc`
- SHA-256: `72dc4b3a89a21d41d0446b77aedd4c6839324892bd07de227ea0e4ca5bdfbadc`
- Exact source bytes: `202`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set-single-value.small16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set-single-value.small16
#
# machine-generated by: ucptrietest.c

````

<a id="text-7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349"></a>
### Text `7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349`
- SHA-256: `7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349`
- Exact source bytes: `1049`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/equivalent@1.0.2 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2016--2023

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-74344ebf347f27ca446e00f1c1921f705546f4b20e0fb31c183cd2c8464b1bc5"></a>
### Text `74344ebf347f27ca446e00f1c1921f705546f4b20e0fb31c183cd2c8464b1bc5`
- SHA-256: `74344ebf347f27ca446e00f1c1921f705546f4b20e0fb31c183cd2c8464b1bc5`
- Exact source bytes: `380`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/lexical-parse-float@1.0.6 — `src/libm.rs` starting line 994 (archive_legal_header_block)
  - pkg:cargo/lexical-util@1.0.7 — `src/libm.rs` starting line 88 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/acos.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/asin.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/j0.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/j1.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/jn.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/log.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/log10.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/log2.rs` starting line 2 (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/rem_pio2_large.rs` starting line 3 (archive_legal_header_block)
````text
/*
 * ====================================================
 * Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
 *
 * Developed at SunSoft, a Sun Microsystems, Inc. business.
 * Permission to use, copy, modify, and distribute this
 * software is freely granted, provided that this notice
 * is preserved.
 * ====================================================
 */
````

<a id="text-74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3"></a>
### Text `74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3`
- SHA-256: `74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3`
- Exact source bytes: `2847`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/regex-syntax@0.8.11 — `src/unicode_tables/LICENSE-UNICODE` (archive_named_legal_file)
````text
UNICODE, INC. LICENSE AGREEMENT - DATA FILES AND SOFTWARE

Unicode Data Files include all data files under the directories
http://www.unicode.org/Public/, http://www.unicode.org/reports/,
http://www.unicode.org/cldr/data/, http://source.icu-project.org/repos/icu/, and
http://www.unicode.org/utility/trac/browser/.

Unicode Data Files do not include PDF online code charts under the
directory http://www.unicode.org/Public/.

Software includes any source code published in the Unicode Standard
or under the directories
http://www.unicode.org/Public/, http://www.unicode.org/reports/,
http://www.unicode.org/cldr/data/, http://source.icu-project.org/repos/icu/, and
http://www.unicode.org/utility/trac/browser/.

NOTICE TO USER: Carefully read the following legal agreement.
BY DOWNLOADING, INSTALLING, COPYING OR OTHERWISE USING UNICODE INC.'S
DATA FILES ("DATA FILES"), AND/OR SOFTWARE ("SOFTWARE"),
YOU UNEQUIVOCALLY ACCEPT, AND AGREE TO BE BOUND BY, ALL OF THE
TERMS AND CONDITIONS OF THIS AGREEMENT.
IF YOU DO NOT AGREE, DO NOT DOWNLOAD, INSTALL, COPY, DISTRIBUTE OR USE
THE DATA FILES OR SOFTWARE.

COPYRIGHT AND PERMISSION NOTICE

Copyright © 1991-2018 Unicode, Inc. All rights reserved.
Distributed under the Terms of Use in http://www.unicode.org/copyright.html.

Permission is hereby granted, free of charge, to any person obtaining
a copy of the Unicode data files and any associated documentation
(the "Data Files") or Unicode software and any associated documentation
(the "Software") to deal in the Data Files or Software
without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, and/or sell copies of
the Data Files or Software, and to permit persons to whom the Data Files
or Software are furnished to do so, provided that either
(a) this copyright and permission notice appear with all copies
of the Data Files or Software, or
(b) this copyright and permission notice appear in associated
Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT OF THIRD PARTY RIGHTS.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS
NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL
DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THE DATA FILES OR SOFTWARE.

Except as contained in this notice, the name of a copyright holder
shall not be used in advertising or otherwise to promote the sale,
use or other dealings in these Data Files or Software without prior
written authorization of the copyright holder.

````

<a id="text-750dc1b658a160daf327d14379dc223ec8cc49213d195f2929bad72fa31cfffd"></a>
### Text `750dc1b658a160daf327d14379dc223ec8cc49213d195f2929bad72fa31cfffd`
- SHA-256: `750dc1b658a160daf327d14379dc223ec8cc49213d195f2929bad72fa31cfffd`
- Exact source bytes: `332`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/lock_api@0.4.14 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/lock_api@0.4.14 — `src/mutex.rs` (archive_legal_header_block)
  - pkg:cargo/lock_api@0.4.14 — `src/remutex.rs` (archive_legal_header_block)
````text
// Copyright 2018 Amanieu d'Antras
//
// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
// http://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.

````

<a id="text-7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545"></a>
### Text `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545`
- SHA-256: `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545`
- Exact source bytes: `1043`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/either@1.17.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/itertools@0.14.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/itertools@0.15.0 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2015

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-77ee9bce4ac66db1a7c4d5981acb771b85bda28ec5a34205eacfba5790c18367"></a>
### Text `77ee9bce4ac66db1a7c4d5981acb771b85bda28ec5a34205eacfba5790c18367`
- SHA-256: `77ee9bce4ac66db1a7c4d5981acb771b85bda28ec5a34205eacfba5790c18367`
- Exact source bytes: `440`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `src/byteorder.rs` (archive_legal_header_block)
````text
// SPDX-License-Identifier: BSD-2-Clause OR Apache-2.0 OR MIT
//
// Copyright 2019 The Fuchsia Authors
//
// Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-78faf2571fe417f3bcd7b38798c4d9ddf499ca43d1ede6fa44992ba75445bff7"></a>
### Text `78faf2571fe417f3bcd7b38798c4d9ddf499ca43d1ede6fa44992ba75445bff7`
- SHA-256: `78faf2571fe417f3bcd7b38798c4d9ddf499ca43d1ede6fa44992ba75445bff7`
- Exact source bytes: `428`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/cos.rs` (archive_legal_header_block)
````text
// origin: FreeBSD /usr/src/lib/msun/src/s_cos.c */
//
// ====================================================
// Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
//
// Developed at SunPro, a Sun Microsystems, Inc. business.
// Permission to use, copy, modify, and distribute this
// software is freely granted, provided that this notice
// is preserved.
// ====================================================

````

<a id="text-7b273685779bddaafd4c83040dc25fe8c747b73d21f894741df9065609abdff9"></a>
### Text `7b273685779bddaafd4c83040dc25fe8c747b73d21f894741df9065609abdff9`
- SHA-256: `7b273685779bddaafd4c83040dc25fe8c747b73d21f894741df9065609abdff9`
- Exact source bytes: `1075`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/attribute-derive-macro@0.10.5 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/manyhow-macros@0.11.4 — `LICENSE` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2022 Roland Fredenhagen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-7b359e490732b5a6e9a0eafb91aa90f09de3afebb17810450304556b7134d5cc"></a>
### Text `7b359e490732b5a6e9a0eafb91aa90f09de3afebb17810450304556b7134d5cc`
- SHA-256: `7b359e490732b5a6e9a0eafb91aa90f09de3afebb17810450304556b7134d5cc`
- Exact source bytes: `426`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/bag.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/binary_heap.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/bit_vector.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/calendar.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/date_formatter.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/file_security.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/locale.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/mach_port.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/notification_center.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/number_formatter.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/plugin.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/preferences.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/socket.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/stream.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/string_tokenizer.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/tree.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/url_enumerator.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/user_notification.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/xml_node.rs` (archive_legal_header_block)
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/xml_parser.rs` (archive_legal_header_block)
````text
// Copyright 2023 The Servo Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0"></a>
### Text `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0`
- SHA-256: `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0`
- Exact source bytes: `1071`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/fs2@0.4.3 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/heck@0.5.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/unicode-normalization@0.1.25 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/unicode-width@0.2.2 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2015 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-7c7134b9f7b978c03fca875517cf398db91f19bbb8109b6685e742aa3f57468e"></a>
### Text `7c7134b9f7b978c03fca875517cf398db91f19bbb8109b6685e742aa3f57468e`
- SHA-256: `7c7134b9f7b978c03fca875517cf398db91f19bbb8109b6685e742aa3f57468e`
- Exact source bytes: `1091`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/jiter@0.16.0 — `LICENSE` (archive_named_legal_file)
````text
The MIT License (MIT)

Copyright (c) 2022 to present Samuel Colvin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-7dedeb59e2a6b10de97d188169b3331e98036023f531346f626b07734b6fcec1"></a>
### Text `7dedeb59e2a6b10de97d188169b3331e98036023f531346f626b07734b6fcec1`
- SHA-256: `7dedeb59e2a6b10de97d188169b3331e98036023f531346f626b07734b6fcec1`
- Exact source bytes: `426`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/attributed_string.rs` (archive_legal_header_block)
````text
// Copyright 2013 The Servo Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c"></a>
### Text `7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c`
- SHA-256: `7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c`
- Exact source bytes: `1211`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/aho-corasick@1.1.5 — `UNLICENSE` (archive_named_legal_file)
  - pkg:cargo/byteorder@1.5.0 — `UNLICENSE` (archive_named_legal_file)
  - pkg:cargo/memchr@2.8.3 — `UNLICENSE` (archive_named_legal_file)
````text
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>

````

<a id="text-804daaec937a7c6cc91f6b1d16136e4ff4763655e680b5a925b809e4504741a0"></a>
### Text `804daaec937a7c6cc91f6b1d16136e4ff4763655e680b5a925b809e4504741a0`
- SHA-256: `804daaec937a7c6cc91f6b1d16136e4ff4763655e680b5a925b809e4504741a0`
- Exact source bytes: `355`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/rand@0.8.7 — `src/distributions/bernoulli.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/distributions/float.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/distributions/integer.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/distributions/other.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/distributions/utils.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/distributions/weighted.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/distributions/weighted_index.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/prelude.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/rngs/adapter/mod.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/rngs/mock.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/rngs/mod.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/rngs/small.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/rngs/std.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/rngs/thread.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/rngs/xoshiro128plusplus.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/rngs/xoshiro256plusplus.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/seq/index.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/seq/mod.rs` (archive_legal_header_block)
  - pkg:cargo/rand_chacha@0.3.1 — `src/chacha.rs` (archive_legal_header_block)
  - pkg:cargo/rand_chacha@0.3.1 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/rand_core@0.6.4 — `src/block.rs` (archive_legal_header_block)
  - pkg:cargo/rand_core@0.6.4 — `src/error.rs` (archive_legal_header_block)
  - pkg:cargo/rand_core@0.6.4 — `src/impls.rs` (archive_legal_header_block)
  - pkg:cargo/rand_core@0.6.4 — `src/le.rs` (archive_legal_header_block)
````text
// Copyright 2018 Developers of the Rand project.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90"></a>
### Text `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90`
- SHA-256: `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90`
- Exact source bytes: `10850`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/bit-set@0.8.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/bit-vec@0.8.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/lexical-parse-float@1.0.6 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/lexical-parse-integer@1.0.6 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/lexical-util@1.0.7 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

````

<a id="text-83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32"></a>
### Text `83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32`
- SHA-256: `83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32`
- Exact source bytes: `1275`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `LICENSE-BSD` (archive_named_legal_file)
````text
Copyright 2019 The Fuchsia Authors.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

   * Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the
distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

````

<a id="text-84b34dd7608f7fb9b17bd588a6bf392bf7de504e2716f024a77d89f1b145a151"></a>
### Text `84b34dd7608f7fb9b17bd588a6bf392bf7de504e2716f024a77d89f1b145a151`
- SHA-256: `84b34dd7608f7fb9b17bd588a6bf392bf7de504e2716f024a77d89f1b145a151`
- Exact source bytes: `851`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/tinyvec@1.12.0 — `LICENSE-ZLIB.md` (archive_named_legal_file)
````text
Copyright (c) 2019 Daniel "Lokathor" Gee.

This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.

2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.

3. This notice may not be removed or altered from any source distribution.

````

<a id="text-84ff7c28d9c95012acb6be697e80602dcf2297f6542da3a0a5c7aebcdfd66512"></a>
### Text `84ff7c28d9c95012acb6be697e80602dcf2297f6542da3a0a5c7aebcdfd66512`
- SHA-256: `84ff7c28d9c95012acb6be697e80602dcf2297f6542da3a0a5c7aebcdfd66512`
- Exact source bytes: `471`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/num-bigint@0.4.8 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/num-integer@0.1.46 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/num-traits@0.2.19 — `src/lib.rs` (archive_legal_header_block)
````text
// Copyright 2013-2014 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-8a0642cdc4de5e26788e744de733c2bdc36087ffc10bbebffd391858a6ac8b87"></a>
### Text `8a0642cdc4de5e26788e744de733c2bdc36087ffc10bbebffd391858a6ac8b87`
- SHA-256: `8a0642cdc4de5e26788e744de733c2bdc36087ffc10bbebffd391858a6ac8b87`
- Exact source bytes: `197`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/free-blocks.small16.toml` starting line 5 (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: free-blocks.small16
#
# machine-generated by: ucptrietest.c

````

<a id="text-8a9fd5b74bc2c5fdc91f606cfbe87557337b4fcd86bb1246958132ce219d23d7"></a>
### Text `8a9fd5b74bc2c5fdc91f606cfbe87557337b4fcd86bb1246958132ce219d23d7`
- SHA-256: `8a9fd5b74bc2c5fdc91f606cfbe87557337b4fcd86bb1246958132ce219d23d7`
- Exact source bytes: `195`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/small0-in-fast.16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: small0-in-fast.16
#
# machine-generated by: ucptrietest.c

````

<a id="text-8ab841eafef4b22e2d39d38c7cd60c364e8b94457bafe272c09b579810c2119e"></a>
### Text `8ab841eafef4b22e2d39d38c7cd60c364e8b94457bafe272c09b579810c2119e`
- SHA-256: `8ab841eafef4b22e2d39d38c7cd60c364e8b94457bafe272c09b579810c2119e`
- Exact source bytes: `407`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/rand_core@0.6.4 — `src/lib.rs` (archive_legal_header_block)
````text
// Copyright 2018 Developers of the Rand project.
// Copyright 2017-2018 The Rust Project Developers.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-8b4e95f5cf0dc40269c99f7b787203ffe04ded245ca2427422c196efa2b2f42a"></a>
### Text `8b4e95f5cf0dc40269c99f7b787203ffe04ded245ca2427422c196efa2b2f42a`
- SHA-256: `8b4e95f5cf0dc40269c99f7b787203ffe04ded245ca2427422c196efa2b2f42a`
- Exact source bytes: `1090`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/tap@1.0.1 — `LICENSE.txt` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2017 Elliot Linder <darfink@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-8b83c643769dcd716b09eae129df29d86cb30299552e60e24c9e24ad9c388629"></a>
### Text `8b83c643769dcd716b09eae129df29d86cb30299552e60e24c9e24ad9c388629`
- SHA-256: `8b83c643769dcd716b09eae129df29d86cb30299552e60e24c9e24ad9c388629`
- Exact source bytes: `197`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set-single-value.32.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set-single-value.32
#
# machine-generated by: ucptrietest.c

````

<a id="text-8bce3b45e49ecd1461f223b46de133d8f62cd39f745cfdaf81bee554b908bd42"></a>
### Text `8bce3b45e49ecd1461f223b46de133d8f62cd39f745cfdaf81bee554b908bd42`
- SHA-256: `8bce3b45e49ecd1461f223b46de133d8f62cd39f745cfdaf81bee554b908bd42`
- Exact source bytes: `1072`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/strum@0.27.2 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/strum_macros@0.27.2 — `LICENSE` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2019 Peter Glotfelty

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5"></a>
### Text `90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5`
- SHA-256: `90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5`
- Exact source bytes: `569`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/rand@0.8.7 — `COPYRIGHT` (archive_named_legal_file)
  - pkg:cargo/rand_chacha@0.3.1 — `COPYRIGHT` (archive_named_legal_file)
  - pkg:cargo/rand_core@0.6.4 — `COPYRIGHT` (archive_named_legal_file)
````text
Copyrights in the Rand project are retained by their contributors. No
copyright assignment is required to contribute to the Rand project.

For full authorship information, see the version control history.

Except as otherwise noted (below and/or in individual files), Rand is
licensed under the Apache License, Version 2.0 <LICENSE-APACHE> or
<http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
<LICENSE-MIT> or <http://opensource.org/licenses/MIT>, at your option.

The Rand project includes code from the Rust project
published under these same licenses.

````

<a id="text-932e4ab34f8ee85390542105497ef60e6e73dab2c8883d6250f2d427ec6439e3"></a>
### Text `932e4ab34f8ee85390542105497ef60e6e73dab2c8883d6250f2d427ec6439e3`
- SHA-256: `932e4ab34f8ee85390542105497ef60e6e73dab2c8883d6250f2d427ec6439e3`
- Exact source bytes: `407`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/rand@0.8.7 — `src/distributions/distribution.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/distributions/mod.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/rng.rs` (archive_legal_header_block)
````text
// Copyright 2018 Developers of the Rand project.
// Copyright 2013-2017 The Rust Project Developers.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-937230c05b5673fe216dda49dfc7c96591c63d0ea4c029e3e1b84aef3a45cbfd"></a>
### Text `937230c05b5673fe216dda49dfc7c96591c63d0ea4c029e3e1b84aef3a45cbfd`
- SHA-256: `937230c05b5673fe216dda49dfc7c96591c63d0ea4c029e3e1b84aef3a45cbfd`
- Exact source bytes: `1075`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/derive-where@1.6.1 — `LICENSE-MIT` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2021 Roland Fredenhagen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-946c9835d8034d24404f8cfec5f4654cee5dad17e944afc3d06d742cf2882831"></a>
### Text `946c9835d8034d24404f8cfec5f4654cee5dad17e944afc3d06d742cf2882831`
- SHA-256: `946c9835d8034d24404f8cfec5f4654cee5dad17e944afc3d06d742cf2882831`
- Exact source bytes: `12307`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/chrono@0.4.45 — `LICENSE.txt` (archive_named_legal_file)
````text
Rust-chrono is dual-licensed under The MIT License [1] and
Apache 2.0 License [2]. Copyright (c) 2014--2026, Kang Seonghoon and
contributors.

Nota Bene: This is same as the Rust Project's own license.


[1]: <http://opensource.org/licenses/MIT>, which is reproduced below:

~~~~
The MIT License (MIT)

Copyright (c) 2014, Kang Seonghoon.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
~~~~


[2]: <http://www.apache.org/licenses/LICENSE-2.0>, which is reproduced below:

~~~~
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
~~~~

````

<a id="text-95ab6672135bb7e33c5125f938a4cf6af33d2777efa27faca8986de933ec8ba5"></a>
### Text `95ab6672135bb7e33c5125f938a4cf6af33d2777efa27faca8986de933ec8ba5`
- SHA-256: `95ab6672135bb7e33c5125f938a4cf6af33d2777efa27faca8986de933ec8ba5`
- Exact source bytes: `741`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/spin@0.9.9 — `src/barrier.rs` (archive_legal_header_block)
````text
//! Synchronization primitive allowing multiple threads to synchronize the
//! beginning of some computation.
//!
//! Implementation adapted from the 'Barrier' type of the standard library. See:
//! <https://doc.rust-lang.org/std/sync/struct.Barrier.html>
//!
//! Copyright 2014 The Rust Project Developers. See the COPYRIGHT
//! file at the top-level directory of this distribution and at
//! <http://rust-lang.org/COPYRIGHT>.
//!
//! Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
//! <http://www.apache.org/licenses/LICENSE-2.0>> or the MIT license
//! <LICENSE-MIT or <http://opensource.org/licenses/MIT>>, at your
//! option. This file may not be copied, modified, or distributed
//! except according to those terms.

````

<a id="text-95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc"></a>
### Text `95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc`
- SHA-256: `95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc`
- Exact source bytes: `9722`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/rustc-hash@2.1.3 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS
````

<a id="text-971959106478e79569bf22111ed4454a05ca9c97f29b7ff37785909377d49183"></a>
### Text `971959106478e79569bf22111ed4454a05ca9c97f29b7ff37785909377d49183`
- SHA-256: `971959106478e79569bf22111ed4454a05ca9c97f29b7ff37785909377d49183`
- Exact source bytes: `466`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/unicode-normalization@0.1.25 — `src/lookups.rs` (archive_legal_header_block)
  - pkg:cargo/unicode-normalization@0.1.25 — `src/perfect_hash.rs` (archive_legal_header_block)
````text
// Copyright 2019 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-9979eb44ee95a8daac18ebfb3efb1e6d1fa54d447293424a820c430533245186"></a>
### Text `9979eb44ee95a8daac18ebfb3efb1e6d1fa54d447293424a820c430533245186`
- SHA-256: `9979eb44ee95a8daac18ebfb3efb1e6d1fa54d447293424a820c430533245186`
- Exact source bytes: `191`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/free-blocks.8.toml` starting line 5 (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: free-blocks.8
#
# machine-generated by: ucptrietest.c

````

<a id="text-99aab70a96f3ecab683d8a319d9070af2213ae4c1601fb053fbe85e1361e32fe"></a>
### Text `99aab70a96f3ecab683d8a319d9070af2213ae4c1601fb053fbe85e1361e32fe`
- SHA-256: `99aab70a96f3ecab683d8a319d9070af2213ae4c1601fb053fbe85e1361e32fe`
- Exact source bytes: `19251`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/lexical-parse-float@1.0.6 — `LICENSE.md` (archive_named_legal_file)
  - pkg:cargo/lexical-parse-integer@1.0.6 — `LICENSE.md` (archive_named_legal_file)
````text
# Licensing

Lexical is dual licensed under the Apache 2.0 license as well as the MIT
license. See the LICENCE-MIT and the LICENCE-APACHE files for the licenses.

Other licensing terms may apply, as described in depth below for various features and functionality. All assume use of `lexical` or `lexical-core`.

## `write-floats, not(compact)`

`lexical-write-float/src/algorithm.rs` is a direct port of the reference C++ implementation of Dragonbox, found [here](https://github.com/jk-jeon/dragonbox/).
This code (used if the `write-floats` feature is enabled and the `compact` feature is disabled) is subject to a [Boost Software License](https://github.com/jk-jeon/dragonbox/blob/71993f55067a89f4b4e27591605e21521f5c61be/LICENSE-Boost) and a modified [Apache2 license](https://github.com/jk-jeon/dragonbox/blob/71993f55067a89f4b4e27591605e21521f5c61be/LICENSE-Apache2-LLVM), shown in the [Boost Software License](#boost-software-license) and [Apache2 With LLVM Exceptions](#apache2-with-llvm-exceptions) sections below.

## `write-floats, compact`

`lexical-write-float/src/compact.rs` is a direct port of a C++ implementation of the Grisu algorithm, found [here](https://github.com/night-shift/fpconv/).
This code (used if both the `write-floats` and `compact` features are enabled) is subject to a [MIT License](https://github.com/night-shift/fpconv/blob/dfeb7e938fb85fb5eca130b84f856705ced75012/license), shown in the [fpconv License](#fpconv-license) section below.

## `write-floats, radix`

`lexical-write-float/src/radix.rs` is adapted from the V8 implementation found [here](). This code (used if both the `parse-floats` and `radix` features are enabled) is subject to a [3-clause BSD license](https://github.com/v8/v8/blob/f80bfeaf0792652bfbc1f174d5a7b8ab8bc0cbbd/LICENSE.v8), shown in the [V8 License](#v8-license) section below.

## `parse-floats, compact`

`lexical-parse-float/src/bellerophon.rs` is loosely based off the Golang implementation,
found [here](https://github.com/golang/go/blob/b10849fbb97a2244c086991b4623ae9f32c212d0/src/strconv/extfloat.go). This code (used if both the `parse-floats` and `compact` features are enabled) is subject to a [3-clause BSD license](https://github.com/golang/go/blob/b10849fbb97a2244c086991b4623ae9f32c212d0/LICENSE), shown in the [Go License](#go-license) section below.

# License Terms

This contains complete copies of the licensing terms for the feature-dependent code described above.

## Go License

Copyright (c) 2009 The Go Authors. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of Google Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Boost Software License

Boost Software License - Version 1.0 - August 17th, 2003

Permission is hereby granted, free of charge, to any person or organization
obtaining a copy of the software and accompanying documentation covered by
this license (the "Software") to use, reproduce, display, distribute,
execute, and transmit the Software, and to prepare derivative works of the
Software, and to permit third-parties to whom the Software is furnished to
do so, all subject to the following:

The copyright notices in the Software and this entire statement, including
the above license grant, this restriction and the following disclaimer,
must be included in all copies of the Software, in whole or in part, and
all derivative works of the Software, unless such copies or derivative
works are solely in the form of machine-executable object code generated by
a source language processor.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO EVENT
SHALL THE COPYRIGHT HOLDERS OR ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE
FOR ANY DAMAGES OR OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

## Apache2 With LLVM Exceptions

_Version 2.0, January 2004_
_&lt;<http://www.apache.org/licenses/>&gt;_

### Terms and Conditions for use, reproduction, and distribution

#### 1. Definitions

“License” shall mean the terms and conditions for use, reproduction, and
distribution as defined by Sections 1 through 9 of this document.

“Licensor” shall mean the copyright owner or entity authorized by the copyright
owner that is granting the License.

“Legal Entity” shall mean the union of the acting entity and all other entities
that control, are controlled by, or are under common control with that entity.
For the purposes of this definition, “control” means **(i)** the power, direct or
indirect, to cause the direction or management of such entity, whether by
contract or otherwise, or **(ii)** ownership of fifty percent (50%) or more of the
outstanding shares, or **(iii)** beneficial ownership of such entity.

“You” (or “Your”) shall mean an individual or Legal Entity exercising
permissions granted by this License.

“Source” form shall mean the preferred form for making modifications, including
but not limited to software source code, documentation source, and configuration
files.

“Object” form shall mean any form resulting from mechanical transformation or
translation of a Source form, including but not limited to compiled object code,
generated documentation, and conversions to other media types.

“Work” shall mean the work of authorship, whether in Source or Object form, made
available under the License, as indicated by a copyright notice that is included
in or attached to the work (an example is provided in the Appendix below).

“Derivative Works” shall mean any work, whether in Source or Object form, that
is based on (or derived from) the Work and for which the editorial revisions,
annotations, elaborations, or other modifications represent, as a whole, an
original work of authorship. For the purposes of this License, Derivative Works
shall not include works that remain separable from, or merely link (or bind by
name) to the interfaces of, the Work and Derivative Works thereof.

“Contribution” shall mean any work of authorship, including the original version
of the Work and any modifications or additions to that Work or Derivative Works
thereof, that is intentionally submitted to Licensor for inclusion in the Work
by the copyright owner or by an individual or Legal Entity authorized to submit
on behalf of the copyright owner. For the purposes of this definition,
“submitted” means any form of electronic, verbal, or written communication sent
to the Licensor or its representatives, including but not limited to
communication on electronic mailing lists, source code control systems, and
issue tracking systems that are managed by, or on behalf of, the Licensor for
the purpose of discussing and improving the Work, but excluding communication
that is conspicuously marked or otherwise designated in writing by the copyright
owner as “Not a Contribution.”

“Contributor” shall mean Licensor and any individual or Legal Entity on behalf
of whom a Contribution has been received by Licensor and subsequently
incorporated within the Work.

#### 2. Grant of Copyright License

Subject to the terms and conditions of this License, each Contributor hereby
grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free,
irrevocable copyright license to reproduce, prepare Derivative Works of,
publicly display, publicly perform, sublicense, and distribute the Work and such
Derivative Works in Source or Object form.

#### 3. Grant of Patent License

Subject to the terms and conditions of this License, each Contributor hereby
grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free,
irrevocable (except as stated in this section) patent license to make, have
made, use, offer to sell, sell, import, and otherwise transfer the Work, where
such license applies only to those patent claims licensable by such Contributor
that are necessarily infringed by their Contribution(s) alone or by combination
of their Contribution(s) with the Work to which such Contribution(s) was
submitted. If You institute patent litigation against any entity (including a
cross-claim or counterclaim in a lawsuit) alleging that the Work or a
Contribution incorporated within the Work constitutes direct or contributory
patent infringement, then any patent licenses granted to You under this License
for that Work shall terminate as of the date such litigation is filed.

#### 4. Redistribution

You may reproduce and distribute copies of the Work or Derivative Works thereof
in any medium, with or without modifications, and in Source or Object form,
provided that You meet the following conditions:

* **(a)** You must give any other recipients of the Work or Derivative Works a copy of
this License; and
* **(b)** You must cause any modified files to carry prominent notices stating that You
changed the files; and
* **(c)** You must retain, in the Source form of any Derivative Works that You distribute,
all copyright, patent, trademark, and attribution notices from the Source form
of the Work, excluding those notices that do not pertain to any part of the
Derivative Works; and
* **(d)** If the Work includes a “NOTICE” text file as part of its distribution, then any
Derivative Works that You distribute must include a readable copy of the
attribution notices contained within such NOTICE file, excluding those notices
that do not pertain to any part of the Derivative Works, in at least one of the
following places: within a NOTICE text file distributed as part of the
Derivative Works; within the Source form or documentation, if provided along
with the Derivative Works; or, within a display generated by the Derivative
Works, if and wherever such third-party notices normally appear. The contents of
the NOTICE file are for informational purposes only and do not modify the
License. You may add Your own attribution notices within Derivative Works that
You distribute, alongside or as an addendum to the NOTICE text from the Work,
provided that such additional attribution notices cannot be construed as
modifying the License.

You may add Your own copyright statement to Your modifications and may provide
additional or different license terms and conditions for use, reproduction, or
distribution of Your modifications, or for any such Derivative Works as a whole,
provided Your use, reproduction, and distribution of the Work otherwise complies
with the conditions stated in this License.

#### 5. Submission of Contributions

Unless You explicitly state otherwise, any Contribution intentionally submitted
for inclusion in the Work by You to the Licensor shall be under the terms and
conditions of this License, without any additional terms or conditions.
Notwithstanding the above, nothing herein shall supersede or modify the terms of
any separate license agreement you may have executed with Licensor regarding
such Contributions.

#### 6. Trademarks

This License does not grant permission to use the trade names, trademarks,
service marks, or product names of the Licensor, except as required for
reasonable and customary use in describing the origin of the Work and
reproducing the content of the NOTICE file.

#### 7. Disclaimer of Warranty

Unless required by applicable law or agreed to in writing, Licensor provides the
Work (and each Contributor provides its Contributions) on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,
including, without limitation, any warranties or conditions of TITLE,
NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are
solely responsible for determining the appropriateness of using or
redistributing the Work and assume any risks associated with Your exercise of
permissions under this License.

#### 8. Limitation of Liability

In no event and under no legal theory, whether in tort (including negligence),
contract, or otherwise, unless required by applicable law (such as deliberate
and grossly negligent acts) or agreed to in writing, shall any Contributor be
liable to You for damages, including any direct, indirect, special, incidental,
or consequential damages of any character arising as a result of this License or
out of the use or inability to use the Work (including but not limited to
damages for loss of goodwill, work stoppage, computer failure or malfunction, or
any and all other commercial damages or losses), even if such Contributor has
been advised of the possibility of such damages.

#### 9. Accepting Warranty or Additional Liability

While redistributing the Work or Derivative Works thereof, You may choose to
offer, and charge a fee for, acceptance of support, warranty, indemnity, or
other liability obligations and/or rights consistent with this License. However,
in accepting such obligations, You may act only on Your own behalf and on Your
sole responsibility, not on behalf of any other Contributor, and only if You
agree to indemnify, defend, and hold each Contributor harmless for any liability
incurred by, or claims asserted against, such Contributor by reason of your
accepting any such warranty or additional liability.

_END OF TERMS AND CONDITIONS_

### APPENDIX: How to apply the Apache License to your work

To apply the Apache License to your work, attach the following boilerplate
notice, with the fields enclosed by brackets `[]` replaced with your own
identifying information. (Don't include the brackets!) The text should be
enclosed in the appropriate comment syntax for the file format. We also
recommend that a file or class name and description of purpose be included on
the same “printed page” as the copyright notice for easier identification within
third-party archives.

    Copyright [yyyy] [name of copyright owner]

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

### LLVM Exceptions to the Apache 2.0 License

As an exception, if, as a result of your compiling your source code, portions
of this Software are embedded into an Object form of such source code, you
may redistribute such embedded portions in such Object form without complying
with the conditions of Sections 4(a), 4(b) and 4(d) of the License.

In addition, if you combine or link compiled forms of this Software with
software that is licensed under the GPLv2 ("Combined Software") and if a
court of competent jurisdiction determines that the patent provision (Section
3), the indemnity provision (Section 9) or other Section of the License
conflicts with the conditions of the GPLv2, you may retroactively and
prospectively choose to deem waived or otherwise exclude such Section(s) of
the License, but only in their entirety and only with respect to the Combined
Software.

## V8 License

Copyright 2014, the V8 project authors. All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of Google Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## fpconv License

The MIT License

Copyright (c) 2013 Andreas Samoljuk

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

````

<a id="text-9a23caa2adcaff6dc2da09b396bfdc9c443dda54fb0593b39d520c3bbcb00eaa"></a>
### Text `9a23caa2adcaff6dc2da09b396bfdc9c443dda54fb0593b39d520c3bbcb00eaa`
- SHA-256: `9a23caa2adcaff6dc2da09b396bfdc9c443dda54fb0593b39d520c3bbcb00eaa`
- Exact source bytes: `263`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/unicode-width@0.2.2 — `tests/emoji-test.txt` (archive_legal_header_block)
````text
# emoji-test.txt
# Date: 2025-08-04, 20:55:31 GMT
# © 2025 Unicode®, Inc.
# Unicode and the Unicode Logo are registered trademarks of Unicode, Inc. in the U.S. and other countries.
# For terms of use and license, see https://www.unicode.org/terms_of_use.html
#

````

<a id="text-9c485f2d4c2b6fce2f027217d09db4b4fc18e58b3fa815b7cba7ba32e759dce8"></a>
### Text `9c485f2d4c2b6fce2f027217d09db4b4fc18e58b3fa815b7cba7ba32e759dce8`
- SHA-256: `9c485f2d4c2b6fce2f027217d09db4b4fc18e58b3fa815b7cba7ba32e759dce8`
- Exact source bytes: `273`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_plain_legal_section`
- Occurrences:
  - pkg:cargo/memmap2@0.9.11 — `README.md` starting line 24 (archive_plain_legal_section)
````text
## License

`memmap2` is primarily distributed under the terms of both the MIT license and the
Apache License (Version 2.0).

See [LICENSE-APACHE](LICENSE-APACHE), [LICENSE-MIT](LICENSE-MIT) for details.

Copyright (c) 2020 Yevhenii Reizner

Copyright (c) 2015 Dan Burkert

````

<a id="text-9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3"></a>
### Text `9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3`
- SHA-256: `9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3`
- Exact source bytes: `11350`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2023 The Fuchsia Authors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

````

<a id="text-9daa4480b2108384a4f6c5b16adc6f31e4db2ff635b732ad069a9e567fb2333f"></a>
### Text `9daa4480b2108384a4f6c5b16adc6f31e4db2ff635b732ad069a9e567fb2333f`
- SHA-256: `9daa4480b2108384a4f6c5b16adc6f31e4db2ff635b732ad069a9e567fb2333f`
- Exact source bytes: `375`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/try_transmute_mut.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/try_transmute_ref.rs` (archive_legal_header_block)
````text
// Copyright 2024 The Fuchsia Authors
//
// Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-9df565718226f2fd496eda234cd1fff3d3ff974adc0d87a189a2096553594ed8"></a>
### Text `9df565718226f2fd496eda234cd1fff3d3ff974adc0d87a189a2096553594ed8`
- SHA-256: `9df565718226f2fd496eda234cd1fff3d3ff974adc0d87a189a2096553594ed8`
- Exact source bytes: `53`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/fancy-regex@0.17.0 — `tests/oniguruma/test_utf8.c` (archive_legal_header_block)
````text
/*
 * test_utf8.c
 * Copyright (c) 2019  K.Kosako
 */
````

<a id="text-9ee8e4a765798341aefd1a7a02cc26a63bc5d599fd32df6c86a41d84976d6149"></a>
### Text `9ee8e4a765798341aefd1a7a02cc26a63bc5d599fd32df6c86a41d84976d6149`
- SHA-256: `9ee8e4a765798341aefd1a7a02cc26a63bc5d599fd32df6c86a41d84976d6149`
- Exact source bytes: `307`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/shlex@1.3.0 — `src/bytes.rs` (archive_legal_header_block)
  - pkg:cargo/shlex@1.3.0 — `src/lib.rs` (archive_legal_header_block)
````text
// Copyright 2015 Nicholas Allegra (comex).
// Licensed under the Apache License, Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0> or
// the MIT license <https://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.

````

<a id="text-9f5d28cffc17ef4a474fcb72cdacb51a38c95a5581bffec5af6c3c0c1a3f97c7"></a>
### Text `9f5d28cffc17ef4a474fcb72cdacb51a38c95a5581bffec5af6c3c0c1a3f97c7`
- SHA-256: `9f5d28cffc17ef4a474fcb72cdacb51a38c95a5581bffec5af6c3c0c1a3f97c7`
- Exact source bytes: `426`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/characterset.rs` (archive_legal_header_block)
````text
// Copyright 2019 The Servo Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-a0391b94bba1e28d1067237466a4d6e590f369ffb21755535a4aaf3b2f437825"></a>
### Text `a0391b94bba1e28d1067237466a4d6e590f369ffb21755535a4aaf3b2f437825`
- SHA-256: `a0391b94bba1e28d1067237466a4d6e590f369ffb21755535a4aaf3b2f437825`
- Exact source bytes: `440`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `src/pointer/mod.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/pointer/ptr.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/util/macros.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/util/mod.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/wrappers.rs` (archive_legal_header_block)
````text
// SPDX-License-Identifier: BSD-2-Clause OR Apache-2.0 OR MIT
//
// Copyright 2023 The Fuchsia Authors
//
// Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-a16bac74535d4205846d05a5714b5d9f1292dc812637cc2db0685eeb29a84380"></a>
### Text `a16bac74535d4205846d05a5714b5d9f1292dc812637cc2db0685eeb29a84380`
- SHA-256: `a16bac74535d4205846d05a5714b5d9f1292dc812637cc2db0685eeb29a84380`
- Exact source bytes: `233`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_plain_legal_section`
- Occurrences:
  - pkg:cargo/fs2@0.4.3 — `README.md` starting line 43 (archive_plain_legal_section)
````text
## License

`fs2` is primarily distributed under the terms of both the MIT license and the
Apache License (Version 2.0).

See [LICENSE-APACHE](LICENSE-APACHE), [LICENSE-MIT](LICENSE-MIT) for details.

Copyright (c) 2015 Dan Burkert.

````

<a id="text-a18873a1cb2db8f556a0d163de065d681538a93e313caf9c5cb012201cdc9d2e"></a>
### Text `a18873a1cb2db8f556a0d163de065d681538a93e313caf9c5cb012201cdc9d2e`
- SHA-256: `a18873a1cb2db8f556a0d163de065d681538a93e313caf9c5cb012201cdc9d2e`
- Exact source bytes: `375`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/include_value.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/max-align.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/transmute_mut.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui/transmute_ref.rs` (archive_legal_header_block)
````text
// Copyright 2023 The Fuchsia Authors
//
// Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-a4a800e538e1946ac0d7c4f4654ec800a1a59e46950e4431e9f6fbeb96cb8309"></a>
### Text `a4a800e538e1946ac0d7c4f4654ec800a1a59e46950e4431e9f6fbeb96cb8309`
- SHA-256: `a4a800e538e1946ac0d7c4f4654ec800a1a59e46950e4431e9f6fbeb96cb8309`
- Exact source bytes: `190`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set-empty.32.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set-empty.32
#
# machine-generated by: ucptrietest.c

````

<a id="text-a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"></a>
### Text `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`
- SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`
- Exact source bytes: `10847`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/ahash@0.8.12 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/arrayvec@0.7.8 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/autocfg@1.5.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/bitflags@2.13.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/bstr@1.13.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/cfg-if@1.0.4 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/core-foundation-sys@0.8.7 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/displaydoc@0.2.7 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/either@1.17.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/equivalent@1.0.2 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/fs2@0.4.3 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/getopts@0.2.24 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/hash32@0.2.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/hashbrown@0.16.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/hashbrown@0.17.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/heapless@0.7.17 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/heck@0.5.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/indexmap@2.14.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/itertools@0.14.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/itertools@0.15.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/lock_api@0.4.14 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/log@0.4.33 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/num-bigint@0.4.8 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/num-integer@0.1.46 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/num-traits@0.2.19 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/once_cell@1.21.4 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/ordermap@1.2.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/postcard@1.1.3 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/regex@1.13.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/regex-automata@0.4.18 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/regex-syntax@0.8.11 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/rustc_version@0.4.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/scopeguard@1.2.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/smallvec@1.15.2 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/stable_deref_trait@1.2.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/strip-ansi-escapes@0.2.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/unicode-normalization@0.1.25 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/unicode-width@0.2.2 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/unicode_names2@1.3.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/unicode_names2_generator@1.3.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/version_check@0.9.5 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

````

<a id="text-a997449a08324894b63f1159f979a44ef52a95bd4a0d2374c76e2e1b87e50963"></a>
### Text `a997449a08324894b63f1159f979a44ef52a95bd4a0d2374c76e2e1b87e50963`
- SHA-256: `a997449a08324894b63f1159f979a44ef52a95bd4a0d2374c76e2e1b87e50963`
- Exact source bytes: `48`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/generic/fmax.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/generic/fmaximum.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/generic/fmaximum_num.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/generic/fmin.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/generic/fminimum.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/generic/fminimum_num.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/generic/fmod.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/support/int_traits/narrowing_div.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/support/modular.rs` (archive_legal_header_block)
````text
/* SPDX-License-Identifier: MIT OR Apache-2.0 */
````

<a id="text-a9a4c8b3613e78168dffd65818d29de2e60dbcf301d349a8e2b6834f962e4a87"></a>
### Text `a9a4c8b3613e78168dffd65818d29de2e60dbcf301d349a8e2b6834f962e4a87`
- SHA-256: `a9a4c8b3613e78168dffd65818d29de2e60dbcf301d349a8e2b6834f962e4a87`
- Exact source bytes: `440`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_plain_legal_section`
- Occurrences:
  - pkg:cargo/regex@1.13.1 — `README.md` starting line 326 (archive_plain_legal_section)
````text
### License

This project is licensed under either of

 * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
   https://www.apache.org/licenses/LICENSE-2.0)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or
   https://opensource.org/licenses/MIT)

at your option.

The data in `regex-syntax/src/unicode_tables/` is licensed under the Unicode
License Agreement
([LICENSE-UNICODE](https://www.unicode.org/copyright.html#License)).

````

<a id="text-aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf"></a>
### Text `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf`
- SHA-256: `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf`
- Exact source bytes: `10849`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/getrandom@0.2.17 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/getrandom@0.3.4 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/rand_chacha@0.3.1 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                              Apache License
                        Version 2.0, January 2004
                     https://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

````

<a id="text-abf8f3253498c07abb340315b01c73c2151f9f2a5622ea0b44bd8cadfa34072a"></a>
### Text `abf8f3253498c07abb340315b01c73c2151f9f2a5622ea0b44bd8cadfa34072a`
- SHA-256: `abf8f3253498c07abb340315b01c73c2151f9f2a5622ea0b44bd8cadfa34072a`
- Exact source bytes: `11357`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/attribute-derive@0.10.5 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/interpolator@0.5.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/manyhow@0.11.4 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/proc-macro-utils@0.10.0 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a peretual,
      worldwide, non-exclusive, no-cpharge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
     agreed to in writing, Licensor provides the Work (and each
      Contributor provides it s Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

````

<a id="text-ad9f087cad6ae9e4e25637be7ee6ff4fa039cf2a6277206067d041f39801c1a4"></a>
### Text `ad9f087cad6ae9e4e25637be7ee6ff4fa039cf2a6277206067d041f39801c1a4`
- SHA-256: `ad9f087cad6ae9e4e25637be7ee6ff4fa039cf2a6277206067d041f39801c1a4`
- Exact source bytes: `195`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set3-initial-9.32.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set3-initial-9.32
#
# machine-generated by: ucptrietest.c

````

<a id="text-ae36b8732e1a0fd7cf1b44f0840d2fca6e15432a92e6c1a1d7ef4bd5b5d83bc6"></a>
### Text `ae36b8732e1a0fd7cf1b44f0840d2fca6e15432a92e6c1a1d7ef4bd5b5d83bc6`
- SHA-256: `ae36b8732e1a0fd7cf1b44f0840d2fca6e15432a92e6c1a1d7ef4bd5b5d83bc6`
- Exact source bytes: `363`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/k_tan.rs` (archive_legal_header_block)
````text
// origin: FreeBSD /usr/src/lib/msun/src/k_tan.c */
//
// ====================================================
// Copyright 2004 Sun Microsystems, Inc.  All Rights Reserved.
//
// Permission to use, copy, modify, and distribute this
// software is freely granted, provided that this notice
// is preserved.
// ====================================================

````

<a id="text-b0c001ef4630f620cb39d1122a051616ca4e50355dd13b5be095f99287acba7d"></a>
### Text `b0c001ef4630f620cb39d1122a051616ca4e50355dd13b5be095f99287acba7d`
- SHA-256: `b0c001ef4630f620cb39d1122a051616ca4e50355dd13b5be095f99287acba7d`
- Exact source bytes: `402`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/rand@0.8.7 — `src/rngs/adapter/read.rs` (archive_legal_header_block)
  - pkg:cargo/rand@0.8.7 — `src/rngs/adapter/reseeding.rs` (archive_legal_header_block)
````text
// Copyright 2018 Developers of the Rand project.
// Copyright 2013 The Rust Project Developers.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-b0ee486fbb4a7a5d57b0710223ba9dc1536db1333d6eb769f475607a1c7b62e4"></a>
### Text `b0ee486fbb4a7a5d57b0710223ba9dc1536db1333d6eb769f475607a1c7b62e4`
- SHA-256: `b0ee486fbb4a7a5d57b0710223ba9dc1536db1333d6eb769f475607a1c7b62e4`
- Exact source bytes: `195`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set3-initial-9.16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set3-initial-9.16
#
# machine-generated by: ucptrietest.c

````

<a id="text-b1181a40b2a7b25cf66fd01481713bc1005df082c53ef73e851e55071b102744"></a>
### Text `b1181a40b2a7b25cf66fd01481713bc1005df082c53ef73e851e55071b102744`
- SHA-256: `b1181a40b2a7b25cf66fd01481713bc1005df082c53ef73e851e55071b102744`
- Exact source bytes: `856`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/foldhash@0.2.0 — `LICENSE` (archive_named_legal_file)
````text
Copyright (c) 2024 Orson Peters

This software is provided 'as-is', without any express or implied warranty. In
no event will the authors be held liable for any damages arising from the use of
this software.

Permission is granted to anyone to use this software for any purpose, including
commercial applications, and to alter it and redistribute it freely, subject to
the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim
    that you wrote the original software. If you use this software in a product,
    an acknowledgment in the product documentation would be appreciated but is
    not required.

2. Altered source versions must be plainly marked as such, and must not be
    misrepresented as being the original software.

3. This notice may not be removed or altered from any source distribution.
````

<a id="text-b1e0b197ab096657b36a818578674de4e4af0030827bf8a6e5b4405fafda000d"></a>
### Text `b1e0b197ab096657b36a818578674de4e4af0030827bf8a6e5b4405fafda000d`
- SHA-256: `b1e0b197ab096657b36a818578674de4e4af0030827bf8a6e5b4405fafda000d`
- Exact source bytes: `67`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/generic/trunc.rs` (archive_legal_header_block)
````text
/* SPDX-License-Identifier: MIT
 * origin: musl src/math/trunc.c */
````

<a id="text-b305318b1fbbb7951781216030d8e7abcad22b4f271060ffba04c0dcb1786a58"></a>
### Text `b305318b1fbbb7951781216030d8e7abcad22b4f271060ffba04c0dcb1786a58`
- SHA-256: `b305318b1fbbb7951781216030d8e7abcad22b4f271060ffba04c0dcb1786a58`
- Exact source bytes: `390`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `cargo.sh` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `ci/check_all_toolchains_tested.sh` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `ci/check_fmt.sh` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `ci/check_readme.sh` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `ci/check_versions.sh` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `ci/release_crate_version.sh` (archive_legal_header_block)
````text
#!/usr/bin/env bash
#
# Copyright 2024 The Fuchsia Authors
#
# Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
# <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
# license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
# This file may not be copied, modified, or distributed except according to
# those terms.

````

<a id="text-b38de021a085da9f83d9e8203ccc9e8cd0eafa2177c2d3822ca75ccf98eafb15"></a>
### Text `b38de021a085da9f83d9e8203ccc9e8cd0eafa2177c2d3822ca75ccf98eafb15`
- SHA-256: `b38de021a085da9f83d9e8203ccc9e8cd0eafa2177c2d3822ca75ccf98eafb15`
- Exact source bytes: `406`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/rand_chacha@0.3.1 — `src/guts.rs` (archive_legal_header_block)
````text
// Copyright 2019 The CryptoCorrosion Contributors
// Copyright 2020 Developers of the Rand project.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1"></a>
### Text `b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1`
- SHA-256: `b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1`
- Exact source bytes: `11357`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/unicode-general-category@1.1.0 — `LICENSE` (archive_named_legal_file)
````text
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "{}"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright {yyyy} {name of copyright owner}

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

````

<a id="text-b4a75f5af25eb835415391455104fcdeb0b3dab81e73618682efc2aa3a71cf24"></a>
### Text `b4a75f5af25eb835415391455104fcdeb0b3dab81e73618682efc2aa3a71cf24`
- SHA-256: `b4a75f5af25eb835415391455104fcdeb0b3dab81e73618682efc2aa3a71cf24`
- Exact source bytes: `363`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `CHANGELOG.md` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `POLICIES.md` (archive_legal_header_block)
````text
<!-- Copyright 2023 The Fuchsia Authors

Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
<LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
This file may not be copied, modified, or distributed except according to
those terms. -->
````

<a id="text-b5ab246b98dc28128956e85060bcc3816fd28768ad49b2fc87e2e91a2a3b7112"></a>
### Text `b5ab246b98dc28128956e85060bcc3816fd28768ad49b2fc87e2e91a2a3b7112`
- SHA-256: `b5ab246b98dc28128956e85060bcc3816fd28768ad49b2fc87e2e91a2a3b7112`
- Exact source bytes: `202`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/char16trie/test_long_branch.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: test_long_branch.toml
#
# machine-generated by: ucharstrietest.c

````

<a id="text-b65d99387acb18a9257229af6ac9ac7b51c3a4adebf08d64ea2267e8278f30e7"></a>
### Text `b65d99387acb18a9257229af6ac9ac7b51c3a4adebf08d64ea2267e8278f30e7`
- SHA-256: `b65d99387acb18a9257229af6ac9ac7b51c3a4adebf08d64ea2267e8278f30e7`
- Exact source bytes: `195`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/char16trie/test_a_ab.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: test_a_ab.toml
#
# machine-generated by: ucharstrietest.c

````

<a id="text-b68d02644fde43f2fc8d0c5a76e5b5bff11ccf6174d5981b4e8ba57bdaa2d687"></a>
### Text `b68d02644fde43f2fc8d0c5a76e5b5bff11ccf6174d5981b4e8ba57bdaa2d687`
- SHA-256: `b68d02644fde43f2fc8d0c5a76e5b5bff11ccf6174d5981b4e8ba57bdaa2d687`
- Exact source bytes: `1118`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/fancy-regex@0.17.0 — `src/optimize.rs` (archive_legal_header_block)
````text
// Copyright 2025 The Fancy Regex Authors.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

````

<a id="text-b6adbd1aa47e52ff23227e30ec16807c5a5b8b8bd416394051ca11e776b611ca"></a>
### Text `b6adbd1aa47e52ff23227e30ec16807c5a5b8b8bd416394051ca11e776b611ca`
- SHA-256: `b6adbd1aa47e52ff23227e30ec16807c5a5b8b8bd416394051ca11e776b611ca`
- Exact source bytes: `471`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/siphasher@1.0.3 — `src/sip.rs` (archive_legal_header_block)
  - pkg:cargo/siphasher@1.0.3 — `src/sip128.rs` (archive_legal_header_block)
  - pkg:cargo/unicode-normalization@0.1.25 — `src/decompose.rs` (archive_legal_header_block)
  - pkg:cargo/unicode-normalization@0.1.25 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/unicode-normalization@0.1.25 — `src/normalize.rs` (archive_legal_header_block)
  - pkg:cargo/unicode-normalization@0.1.25 — `src/recompose.rs` (archive_legal_header_block)
  - pkg:cargo/unicode-normalization@0.1.25 — `src/replace.rs` (archive_legal_header_block)
  - pkg:cargo/unicode-normalization@0.1.25 — `src/test.rs` (archive_legal_header_block)
````text
// Copyright 2012-2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e"></a>
### Text `b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e`
- SHA-256: `b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e`
- Exact source bytes: `1085`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/version_check@0.9.5 — `LICENSE-MIT` (archive_named_legal_file)
````text
The MIT License (MIT)
Copyright (c) 2017-2018 Sergio Benitez

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

````

<a id="text-c09395beab9eb2491d0e36a969f9fe84c4ad47010acf3e8e089117fe3df9592c"></a>
### Text `c09395beab9eb2491d0e36a969f9fe84c4ad47010acf3e8e089117fe3df9592c`
- SHA-256: `c09395beab9eb2491d0e36a969f9fe84c4ad47010acf3e8e089117fe3df9592c`
- Exact source bytes: `349`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/rustc_version@0.4.1 — `src/lib.rs` (archive_legal_header_block)
````text
// Copyright 2016 rustc-version-rs developers
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-c0b40f9058265fff749bc1f80e6c7e78cffb0f72de699c01cbb03adcdca481cc"></a>
### Text `c0b40f9058265fff749bc1f80e6c7e78cffb0f72de699c01cbb03adcdca481cc`
- SHA-256: `c0b40f9058265fff749bc1f80e6c7e78cffb0f72de699c01cbb03adcdca481cc`
- Exact source bytes: `189`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/grow-data.8.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: grow-data.8
#
# machine-generated by: ucptrietest.c

````

<a id="text-c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c"></a>
### Text `c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c`
- SHA-256: `c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c`
- Exact source bytes: `1742`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/utf8_iter@1.0.4 — `COPYRIGHT` (archive_named_legal_file)
````text
Copyright Mozilla Foundation

Licensed under the Apache License (Version 2.0), or the MIT license,
(the "Licenses") at your option. You may not use this file except in
compliance with one of the Licenses. You may obtain copies of the
Licenses at:

   https://www.apache.org/licenses/LICENSE-2.0
   https://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software
distributed under the Licenses is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licenses for the specific language governing permissions and
limitations under the Licenses.

--

Test code is dedicated to the Public Domain when so designated (see
the individual files for PD/CC0-dedicated sections).

--

The implementation for Utf8CharIndices was adapted from the
CharIndices implementation of the Rust standard library at revision
ab32548539ec38a939c1b58599249f3b54130026
(https://github.com/rust-lang/rust/blob/ab32548539ec38a939c1b58599249f3b54130026/library/core/src/str/iter.rs).

Excerpt from https://github.com/rust-lang/rust/blob/ab32548539ec38a939c1b58599249f3b54130026/COPYRIGHT ,
which refers to
https://github.com/rust-lang/rust/blob/ab32548539ec38a939c1b58599249f3b54130026/LICENSE-APACHE
and
https://github.com/rust-lang/rust/blob/ab32548539ec38a939c1b58599249f3b54130026/LICENSE-MIT
:

For full authorship information, see the version control history or
https://thanks.rust-lang.org

Except as otherwise noted (below and/or in individual files), Rust is
licensed under the Apache License, Version 2.0 <LICENSE-APACHE> or
<http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
<LICENSE-MIT> or <http://opensource.org/licenses/MIT>, at your option.

````

<a id="text-c4304c40043b16a1aa4b15c12dba7741d166f0ea9c9616a2c786a49518312469"></a>
### Text `c4304c40043b16a1aa4b15c12dba7741d166f0ea9c9616a2c786a49518312469`
- SHA-256: `c4304c40043b16a1aa4b15c12dba7741d166f0ea9c9616a2c786a49518312469`
- Exact source bytes: `630`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_provider@2.2.0 — `src/marker.rs` starting line 251 (archive_legal_header_block)
````text
    // This code is adapted from https://github.com/rust-lang/rustc-hash,
    // whose license text is reproduced below.
    //
    // Copyright 2015 The Rust Project Developers. See the COPYRIGHT
    // file at the top-level directory of this distribution and at
    // http://rust-lang.org/COPYRIGHT.
    //
    // Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
    // http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
    // <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
    // option. This file may not be copied, modified, or distributed
    // except according to those terms.

````

<a id="text-c43e5660cd51a5b3704711c389850534ef4b5ce424583bd07ca3ad8604325421"></a>
### Text `c43e5660cd51a5b3704711c389850534ef4b5ce424583bd07ca3ad8604325421`
- SHA-256: `c43e5660cd51a5b3704711c389850534ef4b5ce424583bd07ca3ad8604325421`
- Exact source bytes: `193`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set2-overlap.32.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set2-overlap.32
#
# machine-generated by: ucptrietest.c

````

<a id="text-c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"></a>
### Text `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`
- SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`
- Exact source bytes: `11358`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/cobs@0.3.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/serde_spanned@1.1.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/toml@0.9.12+spec-1.1.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/toml_datetime@0.7.5+spec-1.1.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/toml_parser@1.1.3+spec-1.1.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/toml_writer@1.1.2+spec-1.1.0 — `LICENSE-APACHE` (archive_named_legal_file)
````text
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "{}"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright {yyyy} {name of copyright owner}

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

````

<a id="text-c962ee4d1d05ddc138b202b2540219ebc57893fcf97b364852094a9a94ce1365"></a>
### Text `c962ee4d1d05ddc138b202b2540219ebc57893fcf97b364852094a9a94ce1365`
- SHA-256: `c962ee4d1d05ddc138b202b2540219ebc57893fcf97b364852094a9a94ce1365`
- Exact source bytes: `281`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/siphasher@1.0.3 — `COPYING` (archive_named_legal_file)
````text
Copyright 2012-2016 The Rust Project Developers.
Copyright 2016-2026 Frank Denis.

Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
<LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
option.

````

<a id="text-c986bcdb83103d4ddf58aeb7b5302359782e54dc4eea14a0cc27c62dcbd50729"></a>
### Text `c986bcdb83103d4ddf58aeb7b5302359782e54dc4eea14a0cc27c62dcbd50729`
- SHA-256: `c986bcdb83103d4ddf58aeb7b5302359782e54dc4eea14a0cc27c62dcbd50729`
- Exact source bytes: `1058`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/hash32@0.2.1 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2018 Jorge Aparicio

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5"></a>
### Text `c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5`
- SHA-256: `c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5`
- Exact source bytes: `1071`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/lock_api@0.4.14 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/rustc_version@0.4.1 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2016 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566"></a>
### Text `c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566`
- SHA-256: `c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566`
- Exact source bytes: `1338`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/ryu@1.0.23 — `LICENSE-BOOST` (archive_named_legal_file)
````text
Boost Software License - Version 1.0 - August 17th, 2003

Permission is hereby granted, free of charge, to any person or organization
obtaining a copy of the software and accompanying documentation covered by
this license (the "Software") to use, reproduce, display, distribute,
execute, and transmit the Software, and to prepare derivative works of the
Software, and to permit third-parties to whom the Software is furnished to
do so, all subject to the following:

The copyright notices in the Software and this entire statement, including
the above license grant, this restriction and the following disclaimer,
must be included in all copies of the Software, in whole or in part, and
all derivative works of the Software, unless such copies or derivative
works are solely in the form of machine-executable object code generated by
a source language processor.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO EVENT
SHALL THE COPYRIGHT HOLDERS OR ANYONE DISTRIBUTING THE SOFTWARE BE LIABLE
FOR ANY DAMAGES OR OTHER LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-c9f150dbfe3617671e63ac054472d09b1e99ad6024bb14b94d7328fc9fcdcf26"></a>
### Text `c9f150dbfe3617671e63ac054472d09b1e99ad6024bb14b94d7328fc9fcdcf26`
- SHA-256: `c9f150dbfe3617671e63ac054472d09b1e99ad6024bb14b94d7328fc9fcdcf26`
- Exact source bytes: `199`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/char16trie/test_branches.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: test_branches.toml
#
# machine-generated by: ucharstrietest.c

````

<a id="text-cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d"></a>
### Text `cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d`
- SHA-256: `cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d`
- Exact source bytes: `1023`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/winnow@0.7.15 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/winnow@1.0.4 — `LICENSE-MIT` (archive_named_legal_file)
````text
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

````

<a id="text-cc7ddd4aec15d176fc40570979991b6bbe00d3ec3d9bbf7c5dd8bfe0e04278b9"></a>
### Text `cc7ddd4aec15d176fc40570979991b6bbe00d3ec3d9bbf7c5dd8bfe0e04278b9`
- SHA-256: `cc7ddd4aec15d176fc40570979991b6bbe00d3ec3d9bbf7c5dd8bfe0e04278b9`
- Exact source bytes: `67`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/generic/floor.rs` (archive_legal_header_block)
````text
/* SPDX-License-Identifier: MIT
 * origin: musl src/math/floor.c */
````

<a id="text-cd052f4fc22d6625c9f4439c66d4512a9011446d3f2dff15842925b024821cbb"></a>
### Text `cd052f4fc22d6625c9f4439c66d4512a9011446d3f2dff15842925b024821cbb`
- SHA-256: `cd052f4fc22d6625c9f4439c66d4512a9011446d3f2dff15842925b024821cbb`
- Exact source bytes: `426`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/k_cos.rs` (archive_legal_header_block)
````text
// origin: FreeBSD /usr/src/lib/msun/src/k_cos.c
//
// ====================================================
// Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
//
// Developed at SunSoft, a Sun Microsystems, Inc. business.
// Permission to use, copy, modify, and distribute this
// software is freely granted, provided that this notice
// is preserved.
// ====================================================

````

<a id="text-cfc4f3947aea229c6924bbfaa1b8210f57b4247a6b8537da455b1de37d323612"></a>
### Text `cfc4f3947aea229c6924bbfaa1b8210f57b4247a6b8537da455b1de37d323612`
- SHA-256: `cfc4f3947aea229c6924bbfaa1b8210f57b4247a6b8537da455b1de37d323612`
- Exact source bytes: `190`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set1.small16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set1.small16
#
# machine-generated by: ucptrietest.c

````

<a id="text-cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"></a>
### Text `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`
- SHA-256: `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`
- Exact source bytes: `11358`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/derive-where@1.6.1 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/static_assertions@1.1.0 — `LICENSE-APACHE` (archive_named_legal_file)
  - pkg:cargo/tinyvec@1.12.0 — `LICENSE-APACHE.md` (archive_named_legal_file)
  - pkg:cargo/utf8_iter@1.0.4 — `LICENSE-APACHE` (archive_named_legal_file)
````text

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

````

<a id="text-d3e55cbef0010ddd8b3bdfe9ee922a3794ed8f177121f16edf926e5039efae7a"></a>
### Text `d3e55cbef0010ddd8b3bdfe9ee922a3794ed8f177121f16edf926e5039efae7a`
- SHA-256: `d3e55cbef0010ddd8b3bdfe9ee922a3794ed8f177121f16edf926e5039efae7a`
- Exact source bytes: `194`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set3-initial-9.8.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set3-initial-9.8
#
# machine-generated by: ucptrietest.c

````

<a id="text-d50cfa4c60b2a66f71ebf885be982d5308ca104e0b337e4e33315ddb453daaa9"></a>
### Text `d50cfa4c60b2a66f71ebf885be982d5308ca104e0b337e4e33315ddb453daaa9`
- SHA-256: `d50cfa4c60b2a66f71ebf885be982d5308ca104e0b337e4e33315ddb453daaa9`
- Exact source bytes: `200`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/short-all-same.16.toml` (archive_legal_header_block)
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/short-all-same.small16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: short-all-same.small16
#
# machine-generated by: ucptrietest.c

````

<a id="text-d57938f5c09e67192a65f65731297e5b8b145f499f59580a1dfca3fc6597e947"></a>
### Text `d57938f5c09e67192a65f65731297e5b8b145f499f59580a1dfca3fc6597e947`
- SHA-256: `d57938f5c09e67192a65f65731297e5b8b145f499f59580a1dfca3fc6597e947`
- Exact source bytes: `391`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `win-cargo.bat` (archive_legal_header_block)
````text
@rem Copyright 2024 The Fuchsia Authors

@rem Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
@rem <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
@rem license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
@rem This file may not be copied, modified, or distributed except according to
@rem those terms.

````

<a id="text-d5b9c11d6cc93e6ffc28197564a15c7a2f50209317c02810f96b34bf24a17d11"></a>
### Text `d5b9c11d6cc93e6ffc28197564a15c7a2f50209317c02810f96b34bf24a17d11`
- SHA-256: `d5b9c11d6cc93e6ffc28197564a15c7a2f50209317c02810f96b34bf24a17d11`
- Exact source bytes: `1067`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/get-size-derive2@0.10.3 — `LICENSE` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2022 Denis Kerp

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-d5fca2653c88ad02d197faead77e22b80c70636b5bec6e02f2805f389a21b86d"></a>
### Text `d5fca2653c88ad02d197faead77e22b80c70636b5bec6e02f2805f389a21b86d`
- SHA-256: `d5fca2653c88ad02d197faead77e22b80c70636b5bec6e02f2805f389a21b86d`
- Exact source bytes: `345`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/fancy-regex@0.17.0 — `AUTHORS` (archive_named_legal_file)
````text
# This is the list of Fancy Regex authors for copyright purposes.
#
# This does not necessarily list everyone who has contributed code, since in
# some cases, their employer may be the copyright holder.  To see the full list
# of contributors, see the revision history in source control.
Google LLC
Raph Levien
Robin Stocker
Keith Hall
Jon Perry
````

<a id="text-d7a897946c233c44d9a976aa030d02eeff05b86df54157d9f5d478ef0cc214e7"></a>
### Text `d7a897946c233c44d9a976aa030d02eeff05b86df54157d9f5d478ef0cc214e7`
- SHA-256: `d7a897946c233c44d9a976aa030d02eeff05b86df54157d9f5d478ef0cc214e7`
- Exact source bytes: `516`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/arrayvec@0.7.8 — `src/char.rs` (archive_legal_header_block)
````text
// Copyright 2012-2016 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.
//
// Original authors: alexchrichton, bluss

````

<a id="text-d929e0be94b1f678f280e580b0c9abad1725c002cc9d7f991bafe64b5d80980f"></a>
### Text `d929e0be94b1f678f280e580b0c9abad1725c002cc9d7f991bafe64b5d80980f`
- SHA-256: `d929e0be94b1f678f280e580b0c9abad1725c002cc9d7f991bafe64b5d80980f`
- Exact source bytes: `338`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/toml@0.9.12+spec-1.1.0 — `src/map.rs` (archive_legal_header_block)
````text
// Copyright 2017 Serde Developers
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-d9d31636bf6dc09dbbe83abe0514e8d867f635bf3ef99b5163b54c56e6524077"></a>
### Text `d9d31636bf6dc09dbbe83abe0514e8d867f635bf3ef99b5163b54c56e6524077`
- SHA-256: `d9d31636bf6dc09dbbe83abe0514e8d867f635bf3ef99b5163b54c56e6524077`
- Exact source bytes: `1420`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/exp2f.rs` (archive_legal_header_block)
````text
// origin: FreeBSD /usr/src/lib/msun/src/s_exp2f.c
//-
// Copyright (c) 2005 David Schultz <das@FreeBSD.ORG>
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
// 1. Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.
//
// THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
// FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
// DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
// OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
// HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
// LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
// OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
// SUCH DAMAGE.

````

<a id="text-da28bd93659d512cba362af000b10121e71e63ef135f3ba398a05f376e90bc7e"></a>
### Text `da28bd93659d512cba362af000b10121e71e63ef135f3ba398a05f376e90bc7e`
- SHA-256: `da28bd93659d512cba362af000b10121e71e63ef135f3ba398a05f376e90bc7e`
- Exact source bytes: `468`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/rem_pio2.rs` (archive_legal_header_block)
````text
// origin: FreeBSD /usr/src/lib/msun/src/e_rem_pio2.c
//
// ====================================================
// Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
//
// Developed at SunPro, a Sun Microsystems, Inc. business.
// Permission to use, copy, modify, and distribute this
// software is freely granted, provided that this notice
// is preserved.
// ====================================================
//
// Optimized by Bruce D. Evans. */

````

<a id="text-da28ccc6b158fc2d8cccc74e99794b1cff1d29bd7bbeb019442fcf0c04c6cad9"></a>
### Text `da28ccc6b158fc2d8cccc74e99794b1cff1d29bd7bbeb019442fcf0c04c6cad9`
- SHA-256: `da28ccc6b158fc2d8cccc74e99794b1cff1d29bd7bbeb019442fcf0c04c6cad9`
- Exact source bytes: `1059`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/iana-time-zone@0.1.65 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2020 Andrew D. Straw

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-da9a380820f787e8b75d3c8d238c54e42f78cb5b4cf7659593a69f3c5e5d6004"></a>
### Text `da9a380820f787e8b75d3c8d238c54e42f78cb5b4cf7659593a69f3c5e5d6004`
- SHA-256: `da9a380820f787e8b75d3c8d238c54e42f78cb5b4cf7659593a69f3c5e5d6004`
- Exact source bytes: `360`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `rustdoc/style.css` starting line 2 (archive_legal_header_block)
````text
/*
Copyright 2026 The Fuchsia Authors

Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
<LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
This file may not be copied, modified, or distributed except according to
those terms.
*/
````

<a id="text-dadaa9a06c3e61c96d8334be78855ab4c034ef21e773b1d8e1e4a36a68ebf51c"></a>
### Text `dadaa9a06c3e61c96d8334be78855ab4c034ef21e773b1d8e1e4a36a68ebf51c`
- SHA-256: `dadaa9a06c3e61c96d8334be78855ab4c034ef21e773b1d8e1e4a36a68ebf51c`
- Exact source bytes: `355`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/rand_core@0.6.4 — `src/os.rs` (archive_legal_header_block)
````text
// Copyright 2019 Developers of the Rand project.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-de4a26716065cae199b574a72000b66d969086bdf4a386b0d9deccaeb1cee8a1"></a>
### Text `de4a26716065cae199b574a72000b66d969086bdf4a386b0d9deccaeb1cee8a1`
- SHA-256: `de4a26716065cae199b574a72000b66d969086bdf4a386b0d9deccaeb1cee8a1`
- Exact source bytes: `185`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set1.32.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set1.32
#
# machine-generated by: ucptrietest.c

````

<a id="text-de65574563f159c56c8ccacb85629f4684a202a7e5a0d38cb2c593d569bb61de"></a>
### Text `de65574563f159c56c8ccacb85629f4684a202a7e5a0d38cb2c593d569bb61de`
- SHA-256: `de65574563f159c56c8ccacb85629f4684a202a7e5a0d38cb2c593d569bb61de`
- Exact source bytes: `206`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/char16trie/test_shortest_branch.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: test_shortest_branch.toml
#
# machine-generated by: ucharstrietest.c

````

<a id="text-de8cd39a486da1a2018c36284211f1175e9395b0a6460b43faf386b0a5b62bce"></a>
### Text `de8cd39a486da1a2018c36284211f1175e9395b0a6460b43faf386b0a5b62bce`
- SHA-256: `de8cd39a486da1a2018c36284211f1175e9395b0a6460b43faf386b0a5b62bce`
- Exact source bytes: `441`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/lib.rs` (archive_legal_header_block)
````text
// Copyright 2013-2015 The Servo Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.
#![allow(

````

<a id="text-def6bb0777cfa3bc16283d5ace2ff8b0f8b3e2c06e92856d04b92319354453a2"></a>
### Text `def6bb0777cfa3bc16283d5ace2ff8b0f8b3e2c06e92856d04b92319354453a2`
- SHA-256: `def6bb0777cfa3bc16283d5ace2ff8b0f8b3e2c06e92856d04b92319354453a2`
- Exact source bytes: `64`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `rustdoc/style.css` (archive_legal_header_block)
````text
/* SPDX-License-Identifier: BSD-2-Clause OR Apache-2.0 OR MIT */
````

<a id="text-dfa265ace1a8eac40d3059e3bce1a736460a767bc58c74162c39a688a14988a8"></a>
### Text `dfa265ace1a8eac40d3059e3bce1a736460a767bc58c74162c39a688a14988a8`
- SHA-256: `dfa265ace1a8eac40d3059e3bce1a736460a767bc58c74162c39a688a14988a8`
- Exact source bytes: `375`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `tests/ui.rs` (archive_legal_header_block)
````text
// Copyright 2019 The Fuchsia Authors
//
// Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-e00a06f546cd736ac64d82d5c88c23810aec69eec0f61cc64705ea57693e6049"></a>
### Text `e00a06f546cd736ac64d82d5c88c23810aec69eec0f61cc64705ea57693e6049`
- SHA-256: `e00a06f546cd736ac64d82d5c88c23810aec69eec0f61cc64705ea57693e6049`
- Exact source bytes: `426`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/k_sin.rs` (archive_legal_header_block)
````text
// origin: FreeBSD /usr/src/lib/msun/src/k_sin.c
//
// ====================================================
// Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
//
// Developed at SunSoft, a Sun Microsystems, Inc. business.
// Permission to use, copy, modify, and distribute this
// software is freely granted, provided that this notice
// is preserved.
// ====================================================

````

<a id="text-e0cfa1006a64520633de6bfbf563f5b1bea04ef0c5b73f049681931fa297dda3"></a>
### Text `e0cfa1006a64520633de6bfbf563f5b1bea04ef0c5b73f049681931fa297dda3`
- SHA-256: `e0cfa1006a64520633de6bfbf563f5b1bea04ef0c5b73f049681931fa297dda3`
- Exact source bytes: `1066`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/cobs@0.3.0 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2015 The cobs.rs Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-e1b4da0b7c4e2dd8a0eb02fda5f511ad292ac9bb39baa38daee5f2f34dfc5a07"></a>
### Text `e1b4da0b7c4e2dd8a0eb02fda5f511ad292ac9bb39baa38daee5f2f34dfc5a07`
- SHA-256: `e1b4da0b7c4e2dd8a0eb02fda5f511ad292ac9bb39baa38daee5f2f34dfc5a07`
- Exact source bytes: `253`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/vte@0.14.1 — `src/ansi.rs` (archive_legal_header_block)
````text
// SPDX-License-Identifier: Apache-2.0
//
// This module was originally part of the `alacritty_terminal` crate, which is
// licensed under the Apache License, Version 2.0 and is part of the Alacritty
// project (https://github.com/alacritty/alacritty).

````

<a id="text-e382906616915453c368b64c2eb946f37747f1848360203299d8d15587ed9fb0"></a>
### Text `e382906616915453c368b64c2eb946f37747f1848360203299d8d15587ed9fb0`
- SHA-256: `e382906616915453c368b64c2eb946f37747f1848360203299d8d15587ed9fb0`
- Exact source bytes: `440`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `src/util/macro_util.rs` (archive_legal_header_block)
````text
// SPDX-License-Identifier: BSD-2-Clause OR Apache-2.0 OR MIT
//
// Copyright 2022 The Fuchsia Authors
//
// Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-e3a5bc4c031cd9bb27c0a286c4a06837e62342ef41a9ecf03e27b3b5346617be"></a>
### Text `e3a5bc4c031cd9bb27c0a286c4a06837e62342ef41a9ecf03e27b3b5346617be`
- SHA-256: `e3a5bc4c031cd9bb27c0a286c4a06837e62342ef41a9ecf03e27b3b5346617be`
- Exact source bytes: `198`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set2-overlap.small16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set2-overlap.small16
#
# machine-generated by: ucptrietest.c

````

<a id="text-e3eea2ef8e1e4af1cb162f24fc48c4ab05b38ca1cbf7d706449d8b61e271d145"></a>
### Text `e3eea2ef8e1e4af1cb162f24fc48c4ab05b38ca1cbf7d706449d8b61e271d145`
- SHA-256: `e3eea2ef8e1e4af1cb162f24fc48c4ab05b38ca1cbf7d706449d8b61e271d145`
- Exact source bytes: `368`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `Cargo.toml.orig` (archive_legal_header_block)
````text
# Copyright 2018 The Fuchsia Authors
#
# Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
# <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
# license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
# This file may not be copied, modified, or distributed except according to
# those terms.

````

<a id="text-e4c9b06fa850cb9b540a5e400e9f6394cf15efcf4098144de477d1d3dae10150"></a>
### Text `e4c9b06fa850cb9b540a5e400e9f6394cf15efcf4098144de477d1d3dae10150`
- SHA-256: `e4c9b06fa850cb9b540a5e400e9f6394cf15efcf4098144de477d1d3dae10150`
- Exact source bytes: `1052`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/vte@0.14.1 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2016 Joe Wilm

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-e82b60e540ed77cbb45789b5e80e5f1d5af296cf33b7a1dc398baf5cf2eba4df"></a>
### Text `e82b60e540ed77cbb45789b5e80e5f1d5af296cf33b7a1dc398baf5cf2eba4df`
- SHA-256: `e82b60e540ed77cbb45789b5e80e5f1d5af296cf33b7a1dc398baf5cf2eba4df`
- Exact source bytes: `426`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/core-foundation-sys@0.8.7 — `src/error.rs` (archive_legal_header_block)
````text
// Copyright 2016 The Servo Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-e87f02d3b556acb2d4ab78ad7de2b70ef4c5103573fb839bd5d2cf79bac58ec2"></a>
### Text `e87f02d3b556acb2d4ab78ad7de2b70ef4c5103573fb839bd5d2cf79bac58ec2`
- SHA-256: `e87f02d3b556acb2d4ab78ad7de2b70ef4c5103573fb839bd5d2cf79bac58ec2`
- Exact source bytes: `193`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/cpt/set2-overlap.16.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: set2-overlap.16
#
# machine-generated by: ucptrietest.c

````

<a id="text-ea084a2373ebc1f0902c09266e7bf25a05ab3814c1805bb017ffa7308f90c061"></a>
### Text `ea084a2373ebc1f0902c09266e7bf25a05ab3814c1805bb017ffa7308f90c061`
- SHA-256: `ea084a2373ebc1f0902c09266e7bf25a05ab3814c1805bb017ffa7308f90c061`
- Exact source bytes: `1072`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/static_assertions@1.1.0 — `LICENSE-MIT` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2017 Nikolai Vazquez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-eae6ac089cd32010ffacb4b2f0f8cbac03ad2623e115386af53bfc93e04d1903"></a>
### Text `eae6ac089cd32010ffacb4b2f0f8cbac03ad2623e115386af53bfc93e04d1903`
- SHA-256: `eae6ac089cd32010ffacb4b2f0f8cbac03ad2623e115386af53bfc93e04d1903`
- Exact source bytes: `1904`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_embedded_legal_file`
- Occurrences:
  - pkg:cargo/fancy-regex@0.17.0 — `tests/oniguruma/README.md` (archive_embedded_legal_file)
````text
Oniguruma tests
===============

The tests in here are from the Oniguruma project, namely the file
[`test_utf8.c`](https://github.com/kkos/oniguruma/blob/master/test/test_utf8.c).
See below for that file's license.

The `test_utf8_ignore.c` file is a subset with tests that were failing
against fancy-regex at the time of writing.

The test case in `oniguruma.rs` reads both files, and executes the tests
unless they are in the ignore file.

Some of the ignored tests should be fixed in fancy-regex, others can
probably stay ignored (e.g. supporting `a{3,2}`).


Oniguruma LICENSE
-----------------

Copyright (c) 2002-2019  K.Kosako  <kkosako0@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.

````

<a id="text-ec69a93290dc42c3f177906f27e8665533c60ebb1cae9260316776d09934dd67"></a>
### Text `ec69a93290dc42c3f177906f27e8665533c60ebb1cae9260316776d09934dd67`
- SHA-256: `ec69a93290dc42c3f177906f27e8665533c60ebb1cae9260316776d09934dd67`
- Exact source bytes: `471`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/unicode-normalization@0.1.25 — `src/tables.rs` (archive_legal_header_block)
````text
// Copyright 2012-2018 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055"></a>
### Text `ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055`
- SHA-256: `ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055`
- Exact source bytes: `1049`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/indexmap@2.14.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/ordermap@1.2.0 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2016--2017

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-f0ce91d6d6f66e7be0ee4596d1b3292aa04eaa9fd459fb71047fc93e113435b5"></a>
### Text `f0ce91d6d6f66e7be0ee4596d1b3292aa04eaa9fd459fb71047fc93e113435b5`
- SHA-256: `f0ce91d6d6f66e7be0ee4596d1b3292aa04eaa9fd459fb71047fc93e113435b5`
- Exact source bytes: `440`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `src/pointer/transmute.rs` (archive_legal_header_block)
````text
// SPDX-License-Identifier: BSD-2-Clause OR Apache-2.0 OR MIT
//
// Copyright 2025 The Fuchsia Authors
//
// Licensed under a BSD-style license <LICENSE-BSD>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"></a>
### Text `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`
- SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`
- Exact source bytes: `2195`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/icu_locale_core@2.2.0 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/icu_properties@2.2.0 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/icu_properties_data@2.2.0 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/icu_provider@2.2.0 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/litemap@0.8.2 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/potential_utf@0.1.5 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/tinystr@0.8.3 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/writeable@0.6.3 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/yoke@0.8.3 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/yoke-derive@0.8.2 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/zerofrom@0.1.8 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/zerofrom-derive@0.1.7 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/zerotrie@0.2.4 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/zerovec@0.11.6 — `LICENSE` (archive_named_legal_file)
  - pkg:cargo/zerovec-derive@0.11.3 — `LICENSE` (archive_named_legal_file)
````text
UNICODE LICENSE V3

COPYRIGHT AND PERMISSION NOTICE

Copyright © 2020-2024 Unicode, Inc.

NOTICE TO USER: Carefully read the following legal agreement. BY
DOWNLOADING, INSTALLING, COPYING OR OTHERWISE USING DATA FILES, AND/OR
SOFTWARE, YOU UNEQUIVOCALLY ACCEPT, AND AGREE TO BE BOUND BY, ALL OF THE
TERMS AND CONDITIONS OF THIS AGREEMENT. IF YOU DO NOT AGREE, DO NOT
DOWNLOAD, INSTALL, COPY, DISTRIBUTE OR USE THE DATA FILES OR SOFTWARE.

Permission is hereby granted, free of charge, to any person obtaining a
copy of data files and any associated documentation (the "Data Files") or
software and any associated documentation (the "Software") to deal in the
Data Files or Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, and/or sell
copies of the Data Files or Software, and to permit persons to whom the
Data Files or Software are furnished to do so, provided that either (a)
this copyright and permission notice appear with all copies of the Data
Files or Software, or (b) this copyright and permission notice appear in
associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF
THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE
BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES,
OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA
FILES OR SOFTWARE.

Except as contained in this notice, the name of a copyright holder shall
not be used in advertising or otherwise to promote the sale, use or other
dealings in these Data Files or Software without prior written
authorization of the copyright holder.

SPDX-License-Identifier: Unicode-3.0

—

Portions of ICU4X may have been adapted from ICU4C and/or ICU4J.
ICU 1.8.1 to ICU 57.1 © 1995-2016 International Business Machines Corporation and others.

````

<a id="text-f3e4452a50490fd9b5f1c5fea4cd3ed45a7ada46f81ddf2dd66bfab28a742b51"></a>
### Text `f3e4452a50490fd9b5f1c5fea4cd3ed45a7ada46f81ddf2dd66bfab28a742b51`
- SHA-256: `f3e4452a50490fd9b5f1c5fea4cd3ed45a7ada46f81ddf2dd66bfab28a742b51`
- Exact source bytes: `471`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/bit-set@0.8.0 — `src/lib.rs` (archive_legal_header_block)
  - pkg:cargo/bit-vec@0.8.0 — `benches/bench.rs` (archive_legal_header_block)
  - pkg:cargo/chrono@0.4.45 — `src/offset/local/unix.rs` (archive_legal_header_block)
  - pkg:cargo/chrono@0.4.45 — `src/offset/local/windows.rs` (archive_legal_header_block)
  - pkg:cargo/chrono@0.4.45 — `src/time_delta.rs` (archive_legal_header_block)
````text
// Copyright 2012-2014 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

````

<a id="text-f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7"></a>
### Text `f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7`
- SHA-256: `f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7`
- Exact source bytes: `1071`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/bit-set@0.8.0 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/bit-vec@0.8.0 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2023 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-f69bde76c0f2b86b2b6da92b70aed18ca7b2d3f2e7052fe204ddee6d572e28c2"></a>
### Text `f69bde76c0f2b86b2b6da92b70aed18ca7b2d3f2e7052fe204ddee6d572e28c2`
- SHA-256: `f69bde76c0f2b86b2b6da92b70aed18ca7b2d3f2e7052fe204ddee6d572e28c2`
- Exact source bytes: `192`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/icu_collections@2.2.0 — `tests/data/char16trie/test_a.toml` (archive_legal_header_block)
````text
# Copyright (C) 2021 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html
#
# file name: test_a.toml
#
# machine-generated by: ucharstrietest.c

````

<a id="text-f73e293daa12abe52dd73882816fe4002b4f6e69065892abd57881180fb26bf2"></a>
### Text `f73e293daa12abe52dd73882816fe4002b4f6e69065892abd57881180fb26bf2`
- SHA-256: `f73e293daa12abe52dd73882816fe4002b4f6e69065892abd57881180fb26bf2`
- Exact source bytes: `34`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/libm@0.2.16 — `src/math/cbrt.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/fma.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/generic/ceil.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/generic/fma.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/generic/rint.rs` (archive_legal_header_block)
  - pkg:cargo/libm@0.2.16 — `src/math/generic/sqrt.rs` (archive_legal_header_block)
````text
/* SPDX-License-Identifier: MIT */
````

<a id="text-f790cc576999f5998c766d3d26d7d64dc368e805a98461484f65e8d961ec6d9f"></a>
### Text `f790cc576999f5998c766d3d26d7d64dc368e805a98461484f65e8d961ec6d9f`
- SHA-256: `f790cc576999f5998c766d3d26d7d64dc368e805a98461484f65e8d961ec6d9f`
- Exact source bytes: `1082`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/funty@2.0.0 — `LICENSE.txt` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2020 myrrlyn (Alexander Payne)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1"></a>
### Text `f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1`
- SHA-256: `f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1`
- Exact source bytes: `1995`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/unicode-ident@1.0.24 — `LICENSE-UNICODE` (archive_named_legal_file)
````text
UNICODE LICENSE V3

COPYRIGHT AND PERMISSION NOTICE

Copyright © 1991-2023 Unicode, Inc.

NOTICE TO USER: Carefully read the following legal agreement. BY
DOWNLOADING, INSTALLING, COPYING OR OTHERWISE USING DATA FILES, AND/OR
SOFTWARE, YOU UNEQUIVOCALLY ACCEPT, AND AGREE TO BE BOUND BY, ALL OF THE
TERMS AND CONDITIONS OF THIS AGREEMENT. IF YOU DO NOT AGREE, DO NOT
DOWNLOAD, INSTALL, COPY, DISTRIBUTE OR USE THE DATA FILES OR SOFTWARE.

Permission is hereby granted, free of charge, to any person obtaining a
copy of data files and any associated documentation (the "Data Files") or
software and any associated documentation (the "Software") to deal in the
Data Files or Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, and/or sell
copies of the Data Files or Software, and to permit persons to whom the
Data Files or Software are furnished to do so, provided that either (a)
this copyright and permission notice appear with all copies of the Data
Files or Software, or (b) this copyright and permission notice appear in
associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF
THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE
BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES,
OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA
FILES OR SOFTWARE.

Except as contained in this notice, the name of a copyright holder shall
not be used in advertising or otherwise to promote the sale, use or other
dealings in these Data Files or Software without prior written
authorization of the copyright holder.

````

<a id="text-f812a5adbf82bb30c24f3b732e62468b1f0166ab6808654a241de100c81986f6"></a>
### Text `f812a5adbf82bb30c24f3b732e62468b1f0166ab6808654a241de100c81986f6`
- SHA-256: `f812a5adbf82bb30c24f3b732e62468b1f0166ab6808654a241de100c81986f6`
- Exact source bytes: `495`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `src/doctests.rs` (archive_legal_header_block)
  - pkg:cargo/zerocopy@0.8.56 — `src/split_at.rs` (archive_legal_header_block)
````text
// SPDX-License-Identifier: BSD-2-Clause OR Apache-2.0 OR MIT
//
// Copyright 2025 The Fuchsia Authors
//
// Licensed under the 2-Clause BSD License <LICENSE-BSD or
// https://opensource.org/license/bsd-2-clause>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-f858d5fab15f87699a92876e78d7699a92bdb116b57bf64bf6778c374b5cb0fe"></a>
### Text `f858d5fab15f87699a92876e78d7699a92bdb116b57bf64bf6778c374b5cb0fe`
- SHA-256: `f858d5fab15f87699a92876e78d7699a92bdb116b57bf64bf6778c374b5cb0fe`
- Exact source bytes: `1975`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/unicode_names2@1.3.0 — `data/LICENSE-UNICODE` (archive_named_legal_file)
````text
COPYRIGHT AND PERMISSION NOTICE

Copyright © 1991-2023 Unicode, Inc.

NOTICE TO USER: Carefully read the following legal agreement. BY
DOWNLOADING, INSTALLING, COPYING OR OTHERWISE USING DATA FILES, AND/OR
SOFTWARE, YOU UNEQUIVOCALLY ACCEPT, AND AGREE TO BE BOUND BY, ALL OF THE
TERMS AND CONDITIONS OF THIS AGREEMENT. IF YOU DO NOT AGREE, DO NOT
DOWNLOAD, INSTALL, COPY, DISTRIBUTE OR USE THE DATA FILES OR SOFTWARE.

Permission is hereby granted, free of charge, to any person obtaining a
copy of data files and any associated documentation (the "Data Files") or
software and any associated documentation (the "Software") to deal in the
Data Files or Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, and/or sell
copies of the Data Files or Software, and to permit persons to whom the
Data Files or Software are furnished to do so, provided that either (a)
this copyright and permission notice appear with all copies of the Data
Files or Software, or (b) this copyright and permission notice appear in
associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF
THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE
BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES,
OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA
FILES OR SOFTWARE.

Except as contained in this notice, the name of a copyright holder shall
not be used in advertising or otherwise to promote the sale, use or other
dealings in these Data Files or Software without prior written
authorization of the copyright holder.

````

<a id="text-f888610a86bbfdcdc165d48b72792d373404a3094b39d258e628e26941ca110e"></a>
### Text `f888610a86bbfdcdc165d48b72792d373404a3094b39d258e628e26941ca110e`
- SHA-256: `f888610a86bbfdcdc165d48b72792d373404a3094b39d258e628e26941ca110e`
- Exact source bytes: `495`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `src/lib.rs` (archive_legal_header_block)
````text
// SPDX-License-Identifier: BSD-2-Clause OR Apache-2.0 OR MIT
//
// Copyright 2018 The Fuchsia Authors
//
// Licensed under the 2-Clause BSD License <LICENSE-BSD or
// https://opensource.org/license/bsd-2-clause>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-f98e09091d5ae02b2f2ec1ead4f7f28c4c44d1cb98b078739ba67091637e170c"></a>
### Text `f98e09091d5ae02b2f2ec1ead4f7f28c4c44d1cb98b078739ba67091637e170c`
- SHA-256: `f98e09091d5ae02b2f2ec1ead4f7f28c4c44d1cb98b078739ba67091637e170c`
- Exact source bytes: `1075`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/castaway@0.2.4 — `LICENSE` (archive_named_legal_file)
````text
MIT License

Copyright (c) 2021 Stephen M. Coakley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

````

<a id="text-fb77f0a9c53e473abe5103c8632ef9f0f2874d4fb3f17cb2d8c661aab9cee9d7"></a>
### Text `fb77f0a9c53e473abe5103c8632ef9f0f2874d4fb3f17cb2d8c661aab9cee9d7`
- SHA-256: `fb77f0a9c53e473abe5103c8632ef9f0f2874d4fb3f17cb2d8c661aab9cee9d7`
- Exact source bytes: `1097`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/scopeguard@1.2.0 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2016-2019 Ulrik Sverdrup "bluss" and scopeguard developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````

<a id="text-fce91ad40420ecb8a4e3116e4f3ce7c80fc647aea2a78786be424d5227f1a46e"></a>
### Text `fce91ad40420ecb8a4e3116e4f3ce7c80fc647aea2a78786be424d5227f1a46e`
- SHA-256: `fce91ad40420ecb8a4e3116e4f3ce7c80fc647aea2a78786be424d5227f1a46e`
- Exact source bytes: `430`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_legal_header_block`
- Occurrences:
  - pkg:cargo/zerocopy@0.8.56 — `build.rs` (archive_legal_header_block)
````text
// Copyright 2024 The Fuchsia Authors
//
// Licensed under the 2-Clause BSD License <LICENSE-BSD or
// https://opensource.org/license/bsd-2-clause>, Apache License, Version 2.0
// <LICENSE-APACHE or https://www.apache.org/licenses/LICENSE-2.0>, or the MIT
// license <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your option.
// This file may not be copied, modified, or distributed except according to
// those terms.

````

<a id="text-fd80a26fbb3f644af1fa994134446702932968519797227e07a1368dea80f0bc"></a>
### Text `fd80a26fbb3f644af1fa994134446702932968519797227e07a1368dea80f0bc`
- SHA-256: `fd80a26fbb3f644af1fa994134446702932968519797227e07a1368dea80f0bc`
- Exact source bytes: `1023`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/tinyvec@1.12.0 — `LICENSE-MIT.md` (archive_named_legal_file)
````text
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

````

<a id="text-ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2"></a>
### Text `ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2`
- SHA-256: `ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2`
- Exact source bytes: `1060`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `archive_named_legal_file`
- Occurrences:
  - pkg:cargo/hashbrown@0.16.1 — `LICENSE-MIT` (archive_named_legal_file)
  - pkg:cargo/hashbrown@0.17.1 — `LICENSE-MIT` (archive_named_legal_file)
````text
Copyright (c) 2016 Amanieu d'Antras

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

````
