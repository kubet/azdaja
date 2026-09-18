# Azdaja third-party notices

**Candidate:** Azdaja v0.1.18 public content snapshot
**Supported release targets:** `aarch64-apple-darwin`, `x86_64-apple-darwin`, `x86_64-unknown-linux-gnu`
**Feature scope:** `default` and default + `typesafe`, separately qualified below.
**Engineering status:** deterministic archive-derived corpus; not legal advice or legal-sufficiency approval.

- Bound inputs: `Cargo.lock` SHA-256 `204f0ad14854e714bea8dc456b1116049226922a3d9bcd0be7f80943cac4a3e5`
- Cargo.toml SHA-256 `4ecd6a074e3bfe97b801b0b2e879cd32498005e1f615d40c2ecffb223dd3868b`

The root package is excluded. Each feature/target closure is resolved by offline, locked Cargo tree.
Named legal files and declared license-file paths are inventoried from checksum-verified archives.
Packaged declarations are verbatim, not rewritten as SPDX. Packages with no named legal file are explicitly listed below.
This inventory is not a new audit of every source header or a claim of legal completeness.

## Current feature-qualified package union

| Package | Version | Exact packaged declaration | default targets | typesafe targets | Archive SHA-256 |
|---|---:|---|---|---|---|
| `ahash` | `0.8.12` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `5a15f179cd60c4584b8a8c596927aadc462e27f2ca70c04e0071964a73ba7a75` |
| `aho-corasick` | `1.1.5` | `Unlicense OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c982642fa9e8606056828ee9a8505737230110bb1099153c79efe865c59d12ba` |
| `allocator-api2` | `0.2.21` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `683d7910e743518b0e34f1186f92494becacb047c7b6bf616c96772180fef923` |
| `anyhow` | `1.0.104` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `330a5ed07fa54e4702c9d6c4174f74427fc0ef6e214bbd677ae50a5099946470` |
| `arrayvec` | `0.7.8` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d3fb67a6e08acf24fdeccbac2cb6ac4305825bd1f117462e0e6f2f193345ad56` |
| `atomic-waker` | `1.1.2` | `Apache-2.0 OR MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1505bd5d3d116872e7271a6d4e16d81d0c8570876c8de68093a09ac269d8aac0` |
| `attribute-derive` | `0.10.5` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `05832cdddc8f2650cc2cc187cc2e952b8c133a48eb055f35211f61ee81502d77` |
| `attribute-derive-macro` | `0.10.5` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0a7cdbbd4bd005c5d3e2e9c885e6fa575db4f4a3572335b974d8db853b6beb61` |
| `autocfg` | `1.5.1` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `f2032f911046de80f0a198e0901378627c33f59ea0ac00e363d481118bd70a53` |
| `base64` | `0.22.1` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `72b3254f16251a8381aa12e40e3c4d2f0199f8c6508fbecb9d91f575e0fbb8c6` |
| `bit-set` | `0.8.0` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `08807e080ed7f9d5433fa9b275196cfc35414f66a0c79d864dc51a0d825231a3` |
| `bit-vec` | `0.8.0` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `5e764a1d40d510daf35e07be9eb06e75770908c27d411ee6c92109c9840eaaf7` |
| `bitflags` | `2.13.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b588b76d00fde79687d7646a9b5bdf3cc0f655e0bbd080335a95d7e96f3587da` |
| `bitvec` | `1.1.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ddcec3d12c579d40898fe0a9a358a803c23e9c52ca3c425707f81c9436211837` |
| `bstr` | `1.13.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `6bb31b46c14244e20ee9984b11bf5c992b91fb6939fea616e3512c8baecdbe5f` |
| `byteorder` | `1.5.0` | `Unlicense OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1fd0f2584146f6f2ef48085050886acf353beff7305ebd1ae69500e27c67f64b` |
| `bytes` | `1.12.1` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `fc652a48c352aef3ea3aed32080501cf3ef6ed5da78602a020c991775b0aff04` |
| `castaway` | `0.2.4` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `dec551ab6e7578819132c713a93c022a05d60159dc86e7a7050223577484c55a` |
| `cc` | `1.4.2` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `5d262e149917187838d5b42777c8253bcb64500067342904e7d429499a6f277e` |
| `cfg-if` | `1.0.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `9330f8b2ff13f34540b44e946ef35111825727b38d33286ef986142615121801` |
| `chrono` | `0.4.45` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1aa79e62e7697b8e29b513a68abacf485adcd1fe8284a4316c5ae868e6633327` |
| `cobs` | `0.3.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0fa961b519f0b462e3a3b4a34b64d119eeaca1d59af726fe450bbba07a9fc0a1` |
| `collection_literals` | `1.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `2550f75b8cfac212855f6b1885455df8eaee8fe8e246b647d69146142e016084` |
| `compact_str` | `0.9.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `3fdb1325a1cece981e8a296ab8f0f9b63ae357bd0784a9faaf548cc7b480707a` |
| `convert_case` | `0.10.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `633458d4ef8c78b72454de2d54fd6ab2e60f9e02be22f3c6104cdc8a4e0fceb9` |
| `core-foundation-sys` | `0.8.7` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin` | `773648b94d0e5d620f64f280777445740e61fe701025087ec8b57f45c791888b` |
| `crossterm` | `0.29.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d8b9f2e4c67f833b660cdb0a3523065869fb35570177239812ed4c905aeff87b` |
| `darling` | `0.24.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ed17f5901b6630b993ca003def43f2f8ef4014fc13b047b57aad617ff32bc2ec` |
| `darling_core` | `0.24.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `6837e2cf7485aaae18f86181d2f0e9a7ed297a025e220aeabf63fdebd3a2ddff` |
| `darling_macro` | `0.24.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `2ac7135c3ef02b2f7833bbeb1be5ba7f966dcde8a87c6b87f65a778d71a02785` |
| `derive-where` | `1.6.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d08b3a0bcc0d079199cd476b2cae8435016ec11d1c0986c6901c5ac223041534` |
| `derive_more` | `2.1.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d751e9e49156b02b44f9c1815bcb94b984cdcc4396ecc32521c739452808b134` |
| `derive_more-impl` | `2.1.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `799a97264921d8623a957f6c3b9011f3b5492f557bbb7a5a19b7fa6d06ba8dcb` |
| `displaydoc` | `0.2.7` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c6232dd377dcc64799954cbd3a9bb882e9cdc1308ccd87b1c098f1fb2eaf82a8` |
| `document-features` | `0.2.12` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d4b8a88685455ed29a21542a33abd9cb6510b6b129abadabdcef0f4c55bc8f61` |
| `either` | `1.17.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `9e5e8f6c15a24b9a3ee5efec809ccd006d3b30e8b3bb63c39af737c7f87daa1d` |
| `equivalent` | `1.0.2` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `877a4ace8713b0bcf2a4e7eec82529c029f1d0619886d18145fea96c3ffe5c0f` |
| `errno` | `0.3.14` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `39cab71617ae0d63f51a36d69f866391735b51691dbda63cf6f96d042b63efeb` |
| `fancy-regex` | `0.17.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `72cf461f865c862bb7dc573f643dd6a2b6842f7c30b07882b56bd148cc2761b8` |
| `find-msvc-tools` | `0.1.10` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `26b73573e6edcd2af0cdf47bd6cb58f0b3839491263c314eaad1ccf24430e1de` |
| `foldhash` | `0.2.0` | `Zlib` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `77ce24cb58228fbb8aa041425bb1050850ac19177686ea6e0f41a70416f56fdb` |
| `form_urlencoded` | `1.2.2` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `cb4cb245038516f5f85277875cdaa4f7d2c9a0fa0468de06ed190163b1581fcf` |
| `fs2` | `0.4.3` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `9564fc758e15025b46aa6643b1b77d047d1a56a1aea6e01002ac0c7026876213` |
| `funty` | `2.0.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `e6d5a32815ae3f33302d95fdcb2ce17862f8c65363dcfd29360480ba1001fc9c` |
| `futures-channel` | `0.3.34` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b1f9e3d69d39e4862ffed03ed071a76f9a13ba1d9109d355b0f0aa6b15e393c4` |
| `futures-core` | `0.3.34` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `92d699e522242e69e3003b94ecc1f960f3a5e015aa7c5d7486e65ad01dd94f5e` |
| `futures-io` | `0.3.34` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `53c0fa8157de1303bfffdaa1cc2a673bfffb60102f76b0ef4441659124373fed` |
| `futures-sink` | `0.3.34` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1944426bf7d03f1d14f708785e4b33efd750b36d48a157b836b3efc15ede8e1d` |
| `futures-task` | `0.3.34` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `cd417de3d1d015fc3bfd2b1ea46dfc7bab72ef86f1cc7cc9c78e728b34a6d1fd` |
| `futures-util` | `0.3.34` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0d50a92467f8ba5dd6e3ee5d4bd04d73ab2e4e1c44474a0674821dfce14b79bc` |
| `get-size-derive2` | `0.10.3` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c736d226c32e496b8377813b52269e11ad3a48d8373b68862d0364f04fd1229d` |
| `get-size2` | `0.10.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `823645bc6404ae2915707777061a47d3a031a9ee0bff51b34ec973df3d8d2990` |
| `getopts` | `0.2.24` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `cfe4fbac503b8d1f88e6676011885f34b7174f46e59956bba534ba83abded4df` |
| `getrandom` | `0.2.17` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ff2abc00be7fca6ebc474524697ae276ad847ad0a6b3faa4bcb027e9a4614ad0` |
| `getrandom` | `0.3.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `899def5c37c4fd7b2664648c28120ecec138e4d395b459e5ca34f9cce2dd77fd` |
| `hash32` | `0.2.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b0c35f58762feb77d74ebe43bdbc3210f09be9fe6742234d573bacc26ed92b67` |
| `hashbrown` | `0.16.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `841d1cc9bed7f9236f321df977030373f4a4163ae1a7dbfe1a51a2c1a51d9100` |
| `hashbrown` | `0.17.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ed5909b6e89a2db4456e54cd5f673791d7eca6732202bbf2a9cc504fe2f9b84a` |
| `heapless` | `0.7.17` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `cdc6457c0eb62c71aac4bc17216026d8410337c4126773b9c5daba343f17964f` |
| `heck` | `0.5.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `2304e00983f87ffb38b55b444b5e3b60a884b5d30c0fca7d82fe33449bbe55ea` |
| `http` | `1.5.0` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `918d3568bebf352712bc2ef3d46a8bcf1a75b373be6539de198e9105cbbf9ce0` |
| `http-body` | `1.1.0` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ca2a8f2913ee65f60facd6a5905613afaa448497a0230cc41ce022d93290bc2c` |
| `http-body-util` | `0.1.5` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `23169fe34a5fbcdd3f3862e78fb9b6fccd5f02a6dc6f732547005d45631ce71c` |
| `httparse` | `1.10.1` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `6dbf3de79e51f3d586ab4cb9d5c3e2c14aa28ed23d180cf89b4df0454a69cc87` |
| `hyper` | `1.11.1` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `27b501faa50e7a26c3d3560ca625132f4078a17771f4810baf70475ae48cbe43` |
| `hyper-rustls` | `0.27.9` | `Apache-2.0 OR ISC OR MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `33ca68d021ef39cf6463ab54c1d0f5daf03377b70561305bb89a8f83aab66e0f` |
| `hyper-util` | `0.1.20` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `96547c2556ec9d12fb1578c4eaf448b04993e7fb79cbaad930a656880a6bdfa0` |
| `iana-time-zone` | `0.1.65` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `e31bc9ad994ba00e440a8aa5c9ef0ec67d5cb5e5cb0cc7f8b744a35b389cc470` |
| `icu_collections` | `2.2.0` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `2984d1cd16c883d7935b9e07e44071dca8d917fd52ecc02c04d5fa0b5a3f191c` |
| `icu_locale_core` | `2.2.0` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `92219b62b3e2b4d88ac5119f8904c10f8f61bf7e95b640d25ba3075e6cac2c29` |
| `icu_normalizer` | `2.2.0` | `Unicode-3.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c56e5ee99d6e3d33bd91c5d85458b6005a22140021cc324cea84dd0e72cff3b4` |
| `icu_normalizer_data` | `2.2.0` | `Unicode-3.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `da3be0ae77ea334f4da67c12f149704f19f81d1adf7c51cf482943e84a2bad38` |
| `icu_properties` | `2.2.0` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `bee3b67d0ea5c2cca5003417989af8996f8604e34fb9ddf96208a033901e70de` |
| `icu_properties_data` | `2.2.0` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `8e2bbb201e0c04f7b4b3e14382af113e17ba4f63e2c9d2ee626b720cbce54a14` |
| `icu_provider` | `2.2.0` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `139c4cf31c8b5f33d7e199446eff9c1e02decfc2f0eec2c8d71f65befa45b421` |
| `ident_case` | `1.0.1` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b9e0384b61958566e926dc50660321d12159025e767c18e043daf26b70104c39` |
| `idna` | `1.1.0` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `3b0875f23caa03898994f6ddc501886a45c7d3d62d04d2d90788d47be1b1e4de` |
| `idna_adapter` | `1.2.2` | `Apache-2.0 OR MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `cb68373c0d6620ef8105e855e7745e18b0d00d3bdb07fb532e434244cdb9a714` |
| `indexmap` | `2.14.0` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d466e9454f08e4a911e14806c24e16fba1b4c121d1ea474396f396069cf949d9` |
| `indoc` | `2.0.7` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `79cf5c93f93228cf8efb3ba362535fb11199ac548a09ce117c9b1adc3030d706` |
| `instability` | `0.3.13` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `2bf84e73fa6f27f299dec58e13223cf70db80da872eb921d4f6138342a0eabc8` |
| `interpolator` | `0.5.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `71dd52191aae121e8611f1e8dc3e324dd0dd1dee1e6dd91d10ee07a3cfb4d9d8` |
| `ipnet` | `2.12.2` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `791930b43c0d5973160d90a8f3894509f2b273430f5c5c73b668636d0287c5c0` |
| `is-macro` | `0.3.7` | `Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1d57a3e447e24c22647738e4607f1df1e0ec6f72e16182c4cd199f647cdfb0e4` |
| `itertools` | `0.14.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `2b192c782037fadd9cfa75548310488aabdbf3d2da73885b31bd0abd03351285` |
| `itertools` | `0.15.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `8b4baf93f58d4425749ca49a51c50ebab072c5df6994d08fed93541c331481dc` |
| `itoa` | `1.0.18` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `8f42a60cbdf9a97f5d2305f08a87dc4e09308d1276d28c869c684d7777685682` |
| `jiter` | `0.16.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `820ddcacd75c9782308d3fa594f3885630ea3f49adba78a8a29abdfe4b81630c` |
| `kasuari` | `0.4.12` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `bde5057d6143cc94e861d90f591b9303d6716c6b9602309150bd068853c10899` |
| `lexical-parse-float` | `1.0.6` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `52a9f232fbd6f550bc0137dcb5f99ab674071ac2d690ac69704593cb4abbea56` |
| `lexical-parse-integer` | `1.0.6` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `9a7a039f8fb9c19c996cd7b2fcce303c1b2874fe1aca544edc85c4a5f8489b34` |
| `lexical-util` | `1.0.7` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `2604dd126bb14f13fb5d1bd6a66155079cb9fa655b37f875b3a742c705dbed17` |
| `libc` | `0.2.189` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `3eaf3ede3fee6db1a4c2ee091bf8a8b4dccdc6d17f656fb07896ee72867612f2` |
| `libm` | `0.2.16` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b6d2cec3eae94f9f509c767b45932f1ada8350c4bdb85af2fcab4a3c14807981` |
| `line-clipping` | `0.3.8` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `e752191d037c44ad111a8caa762921926658402f01cc1253f7bef2020ece4f5e` |
| `linux-raw-sys` | `0.12.1` | `Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT` | `x86_64-unknown-linux-gnu` | `x86_64-unknown-linux-gnu` | `32a66949e030da00e8c7d4434b251670a91556f4144941d37452769c25d58a53` |
| `litemap` | `0.8.2` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `92daf443525c4cce67b150400bc2316076100ce0b3686209eb8cf3c31612e6f0` |
| `litrs` | `1.0.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `11d3d7f243d5c5a8b9bb5d6dd2b1602c0cb0b9db1621bafc7ed66e35ff9fe092` |
| `lock_api` | `0.4.14` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `224399e74b87b5f3557511d98dff8b14089b3dadafcab6bb93eab67d3aace965` |
| `log` | `0.4.33` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0ceec5bc11778974d1bcb055b18002eba7f4b3518b6a0081b3af5f21666da9ad` |
| `lru` | `0.18.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `5d2f2f9b4ba7e6b24d95e7e899329d35be83bcded72c8540cdd5368932d1d90a` |
| `manyhow` | `0.11.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b33efb3ca6d3b07393750d4030418d594ab1139cee518f0dc88db70fec873587` |
| `manyhow-macros` | `0.11.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `46fce34d199b78b6e6073abf984c9cf5fd3e9330145a93ee0738a7443e371495` |
| `memchr` | `2.8.3` | `Unlicense OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `cf8baf1c55e62ffcace7a9f06f4bd9cd3f0c4beb022d3b367256b91b87513d98` |
| `memmap2` | `0.9.11` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d1219ed1b7f229ee7104d281dd01d6802fe28bb6e95d292942c4daacdeb798c0` |
| `mio` | `1.2.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `30d65c71f1ce40ab09135ce117d742b9f8a19ff91a41a8b57ed50bc2de59c427` |
| `monty` | `0.0.21` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `db44565f603ada5dd98bd580623cd9ce299c8b823bd7195c654826fa536b4d48` |
| `monty-macros` | `0.0.21` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `40ed428288161f63d2bec7929438563fe31390f08e014e58ce20be96d7ef82ee` |
| `monty-types` | `0.0.21` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `00b4b3318107fee36c5eee05c52f16f6565a63aa29d04f8608ebc221e3fe5dd8` |
| `num-bigint` | `0.4.8` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c89e69e7e0f03bea5ef08013795c25018e101932225a656383bd384495ecc367` |
| `num-integer` | `0.1.46` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `7969661fd2958a5cb096e56c8e1ad0444ac2bbcd0061bd28660485a44879858f` |
| `num-traits` | `0.2.19` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `071dfc062690e90b734c0b2273ce72ad0ffa95f0c74596bc250dcfd960262841` |
| `once_cell` | `1.21.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `9f7c3e4beb33f85d45ae3e3a1792185706c8e16d043238c593331cc7cd313b50` |
| `ordermap` | `1.2.0` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `7f7476a5b122ff1fce7208e7ee9dccd0a516e835f5b8b19b8f3c98a34cf757c1` |
| `parking_lot` | `0.12.5` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `93857453250e3077bd71ff98b6a65ea6621a19bb0f559a85248955ac12c45a1a` |
| `parking_lot_core` | `0.9.12` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `2621685985a2ebf1c516881c026032ac7deafcda1a2c9b7850dc81e3dfcb64c1` |
| `percent-encoding` | `2.3.2` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `9b4f627cb1b25917193a259e49bdad08f671f8d9708acfd5fe0a8c1455d87220` |
| `phf` | `0.11.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1fd6780a80ae0c52cc120a26a1a42c1ae51b247a253e4e06113d23d2c2edd078` |
| `phf_codegen` | `0.11.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aef8048c789fa5e851558d709946d6d79a8ff88c0440c587967f8e94bfb1216a` |
| `phf_generator` | `0.11.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `3c80231409c20246a13fddb31776fb942c38553c51e871f8cbd687a4cfb5843d` |
| `phf_shared` | `0.11.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `67eabc2ef2a60eb7faa00097bd1ffdb5bd28e62bf39990626a582201b7a754e5` |
| `pin-project-lite` | `0.2.17` | `Apache-2.0 OR MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `a89322df9ebe1c1578d689c92318e070967d1042b512afbe49518723f4e6d5cd` |
| `postcard` | `1.1.3` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `6764c3b5dd454e283a30e6dfe78e9b31096d9e32036b5d1eaac7a6119ccb9a24` |
| `potential_utf` | `0.1.5` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0103b1cef7ec0cf76490e969665504990193874ea05c85ff9bab8b911d0a0564` |
| `ppv-lite86` | `0.2.21` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `85eae3c4ed2f50dcfe72643da4befc30deadb458a9b590d720cde2f2b1e97da9` |
| `proc-macro-utils` | `0.10.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `eeaf08a13de400bc215877b5bdc088f241b12eb42f0a548d3390dc1c56bb7071` |
| `proc-macro2` | `1.0.107` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `985e7ec9bb745e6ce6535b544d84d6cd6f7ad8bd711c398938ae983b91a766d9` |
| `quote` | `1.0.47` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1fbf4db142a473a8d80c26bbf18454ed458bf8d26c8219c331daecfdbd079001` |
| `quote-use` | `0.8.4` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `9619db1197b497a36178cfc736dc96b271fe918875fbf1344c436a7e93d0321e` |
| `quote-use-macros` | `0.8.4` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `82ebfb7faafadc06a7ab141a6f67bcfb24cb8beb158c6fe933f2f035afa99f35` |
| `radium` | `0.7.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `dc33ff2d4973d518d823d61aa239014831e521c75da58e3df4840d3f47749d09` |
| `rand` | `0.8.7` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `22f6172bdec972074665ed81ed53b71da00bfc44b65a753cfde883ec4c702a1a` |
| `rand_chacha` | `0.3.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `e6c10a63a0fa32252be49d21e7709d4d4baf8d231c2dbce1eaa8141b9b127d88` |
| `rand_core` | `0.6.4` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ec0be4795e2f6a28069bec0b5ff3e2ac9bafc99e6a9a7dc3547996c5c816922c` |
| `ratatui` | `0.30.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `3274ba0a2c5e1bcad2a2005d20f4dc59dad26b2eb0940fb094500dba4099d57d` |
| `ratatui-core` | `0.1.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `cbb175c433c8e28a809d1f5773a2ae96e68c0ce40db865cbab1020bf33ae479c` |
| `ratatui-crossterm` | `0.1.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `567584a3b0e6a8203c23de40b4861497266725eb5363dbfd18a1edd603cca9f0` |
| `ratatui-widgets` | `0.3.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `66e3d19bcc9130ca376277d93b60767ff121ace3be06f5f95f81dd68956407d1` |
| `regex` | `1.13.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `f020237b6c8eed93db2e2cb53c00c60a8e1bc73da7d073199a1180401450218d` |
| `regex-automata` | `0.4.18` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ad8553b9b26413251cbf30e620595c7a41b3887f03da04579c0e6b0d6a06b4b2` |
| `regex-syntax` | `0.8.11` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d6f6ff9a378485b298a5286656da665ba74413d36db0979633275d2e708145d4` |
| `reqwest` | `0.12.28` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `eddd3ca559203180a307f12d114c268abf583f59b03cb906fd0b3ff8646c1147` |
| `ring` | `0.17.14` | `Apache-2.0 AND ISC` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `a4689e6c2294d81e88dc6261c768b63bc4fcdb852be6d1352498b114f61383b7` |
| `ruff_python_ast` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `a10ab966362319801f5e85ce5c6aeac69f0cf50936a31e888f5d004e9279f337` |
| `ruff_python_codegen` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1902d82ae0745be9d3d12a1aee4429acff987c768710dc38a6521eab05990ca0` |
| `ruff_python_literal` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `af3e1f868fa58adc12d1fa3ce1b29c6098aa4b101739d9589cbde9fec239af59` |
| `ruff_python_parser` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `4e3b8436fb010636ea79ce545acc3e391296ef4e804f7cef336dd5f9c8a4aa3a` |
| `ruff_python_stdlib` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `8c8860927bf42efdabb31ccb2ac9b8f98ee43897b45536f8023e217b158e49a4` |
| `ruff_python_trivia` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `969e4a14b2550818efea99b9e2361c714c72e4f1fb94799251d55aed20345189` |
| `ruff_source_file` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c194e02d121e4a1744464ce3a982c4c196eb039bbf67532d18c8ce09f8da6381` |
| `ruff_text_size` | `0.0.3` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c91652ad39be604bc4d5299a5d19feccdd89e255609d89a031e7bb8e0d0aef9f` |
| `rustc-hash` | `2.1.3` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `6b1e7f9a428571be2dc5bc0505c13fb6bf936822b894ec87abf8a08a4e51742d` |
| `rustc_version` | `0.4.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `cfcb3a22ef46e85b45de6ee7e79d063319ebb6594faafcf1c225ea92ab6e9b92` |
| `rustix` | `1.1.4` | `Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b6fe4565b9518b83ef4f91bb47ce29620ca828bd32cb7e408f0062e9930ba190` |
| `rustls` | `0.23.45` | `Apache-2.0 OR ISC OR MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634` |
| `rustls-pki-types` | `1.15.1` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `2f4925028c7eb5d1fcdaf196971378ed9d2c1c4efc7dc5d011256f76c99c0a96` |
| `rustls-webpki` | `0.103.15` | `ISC` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `f3c3cf1d8b1e7d4927e2d154c3fcb02979afb9939629c62cd9048d4f07b60ac2` |
| `rustversion` | `1.0.23` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `cf54715a573b99ac80df0bc206da022bcd442c974952c7b9720069370852e21f` |
| `ryu` | `1.0.23` | `Apache-2.0 OR BSL-1.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `9774ba4a74de5f7b1c1451ed6cd5285a32eddb5cccb8cc655a4e50009e06477f` |
| `scopeguard` | `1.2.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `94143f37725109f92c262ed2cf5e59bce7498c01bcc1502d7b9afe439a4e9f49` |
| `semver` | `1.0.28` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `8a7852d02fc848982e0c167ef163aaff9cd91dc640ba85e263cb1ce46fae51cd` |
| `serde` | `1.0.229` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `4148590afebada386688f18773da617792bf2ef03ffc1e4cbd2b1d45b023e0ba` |
| `serde_core` | `1.0.229` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `67dca2c9c51e58a4791a4b1ed58308b39c64224d349a935ab5039aa360942a48` |
| `serde_derive` | `1.0.229` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `e7a5d71263a5a7d47b41f6b3f06ba276f10cc18b0931f1799f710578e2309348` |
| `serde_json` | `1.0.151` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c841b55ecdae098c80dcae9cf767f6f8a0c2cdb3416bbef72181df4d0fe73f14` |
| `serde_spanned` | `1.1.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `6662b5879511e06e8999a8a235d848113e942c9124f211511b16466ee2995f26` |
| `serde_urlencoded` | `0.7.1` | `MIT/Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d3491c14715ca2294c4d6a88f15e84739788c1d030eed8c110436aafdaa2f3fd` |
| `serde_yaml` | `0.9.34+deprecated` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `6a8b1a1a2ebf674015cc02edccce75287f1a0130d394307b36743c2f5d504b47` |
| `shlex` | `1.3.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0fda2ff0d084019ba4d7c6f371c95d8fd75ce3524c3cb8fb653a3023f6323e64` |
| `shlex` | `2.0.1` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `f8fadd59c855ef2080decdef8ff161eb6661b86933c9d82e5ba29dc602a55aba` |
| `signal-hook` | `0.3.18` | `Apache-2.0/MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d881a16cf4426aa584979d30bd82cb33429027e42122b169753d6ef1085ed6e2` |
| `signal-hook-mio` | `0.2.5` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b75a19a7a740b25bc7944bdee6172368f988763b744e3d4dfe753f6b4ece40cc` |
| `signal-hook-registry` | `1.4.8` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c4db69cba1110affc0e9f7bcd48bbf87b3f4fc7c61fc9155afd4c469eb3d6c1b` |
| `siphasher` | `1.0.3` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `8ee5873ec9cce0195efcb7a4e9507a04cd49aec9c83d0389df45b1ef7ba2e649` |
| `slab` | `0.4.12` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0c790de23124f9ab44544d7ac05d60440adc586479ce501c1d6d7da3cd8c9cf5` |
| `smallvec` | `1.15.2` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `8ed6a63f02c8539c91a8685a86f4099661ba3da017932f6ebbea6de3f0fa7c90` |
| `socket2` | `0.6.5` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c3d1e2c7f27f8d4cb10542a02c49005dbd6e93095799d6f3be745fae9f8fedd4` |
| `speedate` | `0.17.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aba069c070b5e213f2a094deb7e5ed50ecb092be36102a4f4042e8d2056d060e` |
| `spin` | `0.9.9` | `MIT` | `x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `3763264f6b73151db08c50ff20d7d8a0b8796e021cdea7ceedad07b80155fa0e` |
| `stable_deref_trait` | `1.2.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `6ce2be8dc25455e1f91df71bfa12ad37d7af1092ae736f3a6cd0e37bc7810596` |
| `static_assertions` | `1.1.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `a2eb9349b6444b326872e140eb1cf5e7c522154d69e7a0ffb0fb81c06b37543f` |
| `strip-ansi-escapes` | `0.2.1` | `Apache-2.0/MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `2a8f8038e7e7969abb3f1b7c2a811225e9296da208539e0f79c5251d6cac0025` |
| `strsim` | `0.11.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `7da8b5736845d9f2fcb837ea5d9e2628564b3b043a70948a3f0b778838c5fb4f` |
| `strum` | `0.27.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `af23d6f6c1a224baef9d3f61e287d2761385a5b88fdab4eb4c6f11aeb54c4bcf` |
| `strum` | `0.28.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `9628de9b8791db39ceda2b119bbe13134770b56c138ec1d3af810d045c04f9bd` |
| `strum_macros` | `0.27.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `7695ce3845ea4b33927c055a39dc438a45b059f7c1b3d91d38d10355fb8cbca7` |
| `strum_macros` | `0.28.0` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ab85eea0270ee17587ed4156089e10b9e6880ee688791d45a905f5b1ca36f664` |
| `subtle` | `2.6.1` | `BSD-3-Clause` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `13c2bddecc57b384dee18652358fb23172facb8a2c51ccc10d74c157bdea3292` |
| `syn` | `2.0.119` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `872831b642d1a07999a962a351ed35b955ea2cfc8f3862091e2a240a84f17297` |
| `syn` | `3.0.3` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `53e9bae58849f64dfa4f5d5ae372c8341f7305f82a3868709269343628b659a3` |
| `sync_wrapper` | `1.0.2` | `Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0bf256ce5efdfa370213c1dabab5935a12e49f2c58d15e9eac2870d3b4f27263` |
| `synstructure` | `0.13.2` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `728a70f3dbaf5bab7f0c4b1ac8d7ae5ea60a4b5549c8a5914361c99147a709d2` |
| `tap` | `1.0.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `55937e1799185b12863d447f42597ed69d9928686b8d88a1df17376a097d8369` |
| `thin-vec` | `0.2.19` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `79def32ffcd477db1ff26f76dab9e3a91f0bd42a85ca96577089b24623056f9d` |
| `thiserror` | `2.0.20` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ec86235f5fcc2a73650310756d2ac5b138a5780bbbdfae3eeccec992c435ba4f` |
| `thiserror-impl` | `2.0.20` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `bc04cd3e1236dd4a98afca4569f2deb3f120e5422a4023be2cb683f8486292af` |
| `tinystr` | `0.8.3` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c8323304221c2a851516f22236c5722a72eaa19749016521d6dff0824447d96d` |
| `tinyvec` | `1.12.0` | `Zlib OR Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `bb4ebadaa0af04fab11ae01eb5f9fdb5f9c5b875506e210e71c07873528baa7f` |
| `tinyvec_macros` | `0.1.1` | `MIT OR Apache-2.0 OR Zlib` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1f3ccbac311fea05f86f61904b462b55fb3df8837a366dfc601a0161d0532f20` |
| `tokio` | `1.53.1` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `202caea871b69668250d242070849eb495be178ed697a3e98aebce5bc81a0bed` |
| `tokio-rustls` | `0.26.5` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b0c85f2c3ef0b1cd58b36682f4b17aaa995f0e5db534d85692b4903abce21f67` |
| `toml` | `0.9.12+spec-1.1.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `cf92845e79fc2e2def6a5d828f0801e29a2f8acc037becc5ab08595c7d5e9863` |
| `toml_datetime` | `0.7.5+spec-1.1.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `92e1cfed4a3038bc5a127e35a2d360f145e1f4b971b551a2ba5fd7aedf7e1347` |
| `toml_parser` | `1.1.3+spec-1.1.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1d38ac1cf9b95face32296c0a3ede1fdc270627c9d9c02a7274dd6d960dc4d56` |
| `toml_writer` | `1.1.2+spec-1.1.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `7d56353a2a665ad0f41a421187180aab746c8c325620617ad883a99a1cbe66d2` |
| `tower` | `0.5.3` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ebe5ef63511595f1344e2d5cfa636d973292adc0eec1f0ad45fae9f0851ab1d4` |
| `tower-http` | `0.6.11` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `4cfcf7e2740e6fc6d4d688b4ef00650406bb94adf4731e43c096c3a19fe40840` |
| `tower-layer` | `0.3.3` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `121c2a6cda46980bb0fcd1647ffaf6cd3fc79a013de288782836f6df9c48780e` |
| `tower-service` | `0.3.3` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `8df9b6e13f2d32c91b9bd719c00d1958837bc7dec474d94952798cc8e69eeec3` |
| `tracing` | `0.1.44` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `63e71662fa4b2a2c3a26f570f037eb95bb1f85397f3cd8076caed2f026a6d100` |
| `tracing-core` | `0.1.36` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `db97caf9d906fbde555dd62fa95ddba9eecfd14cb388e4f491a66d74cd5fb79a` |
| `try-lock` | `0.2.5` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `e421abadd41a4225275504ea4d6566923418b7f05506fbc9c0fe86ba7396114b` |
| `unicode-general-category` | `1.1.0` | `Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0b993bddc193ae5bd0d623b49ec06ac3e9312875fdae725a975c51db1cc1677f` |
| `unicode-ident` | `1.0.24` | `(MIT OR Apache-2.0) AND Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `e6e4313cd5fcd3dad5cafa179702e2b244f760991f45397d14d4ebf38247da75` |
| `unicode-normalization` | `0.1.25` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `5fd4f6878c9cb28d874b009da9e8d183b5abc80117c40bbd187a1fde336be6e8` |
| `unicode-segmentation` | `1.13.3` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `c6f5d3c3b1bf09027a88a6bc961fc00497d651009560b5463668dc81b0fa87a8` |
| `unicode-truncate` | `2.0.1` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `16b380a1238663e5f8a691f9039c73e1cdae598a30e9855f541d29b08b53e9a5` |
| `unicode-width` | `0.2.2` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b4ac048d71ede7ee76d585517add45da530660ef4390e49b098733c6e897f254` |
| `unicode_names2` | `1.3.0` | `(MIT OR Apache-2.0) AND Unicode-DFS-2016` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `d1673eca9782c84de5f81b82e4109dcfb3611c8ba0d52930ec4a9478f547b2dd` |
| `unicode_names2_generator` | `1.3.0` | `MIT OR Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b91e5b84611016120197efd7dc93ef76774f4e084cd73c9fb3ea4a86c570c56e` |
| `unsafe-libyaml` | `0.2.11` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `673aac59facbab8a9007c7f6108d11f63b603f7cabff99fabf650fea5c32b861` |
| `untrusted` | `0.9.0` | `ISC` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `8ecb6da28b8a351d773b68d5825ac39017e680750f980f3a1a85cd8dd28a47c1` |
| `url` | `2.5.8` | `MIT OR Apache-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `ff67a8a4397373c3ef660812acab3268222035010ab8680ec4215f38ba3d0eed` |
| `utf8_iter` | `1.0.4` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `b6c140620e7ffbb22c2dee59cafe6084a59b5ffc27a8859a5f0d494b5d52b6be` |
| `version_check` | `0.9.5` | `MIT/Apache-2.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0b928f33d975fc6ad9f86c8f283853ad26bdd5b10b7f1542aa2fa15e2289105a` |
| `vte` | `0.14.1` | `Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `231fdcd7ef3037e8330d8e17e61011a2c244126acc0a982f4040ac3f9f0bc077` |
| `want` | `0.3.1` | `MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `bfa7760aed19e106de2c7c0b581b509f2f25d3dacaf737cb82ac61bc6d760b0e` |
| `webpki-roots` | `1.0.9` | `CDLA-Permissive-2.0` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `7dcd9d09a39985f5344844e66b0c530a33843579125f23e21e9f0f220850f22a` |
| `winnow` | `0.7.15` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `df79d97927682d2fd8adb29682d1140b343be4ac0f08fd68b7765d9c059d3945` |
| `winnow` | `1.0.4` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `23b97319f7b8343df12cc98938e5c3eb436064524c8d2b4e30a1d3a36eecdf81` |
| `writeable` | `0.6.3` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `1ffae5123b2d3fc086436f8834ae3ab053a283cfac8fe0a0b8eaae044768a4c4` |
| `wyz` | `0.5.1` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `05f360fc0b24296329c78fda852a1e9ae82de9cf7b27dae4b7f62f118f77b9ed` |
| `yoke` | `0.8.3` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `709fe23a0424b6a435d82152b1bd3fdfb0833487d5fa90d05d42762a9891fef5` |
| `yoke-derive` | `0.8.2` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `de844c262c8848816172cef550288e7dc6c7b7814b4ee56b3e1553f275f1858e` |
| `zerocopy` | `0.8.56` | `BSD-2-Clause OR Apache-2.0 OR MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `556764e583adb45a9f8d413c2a147fa7e8d821e48e12b14fd560b607998b75eb` |
| `zerofrom` | `0.1.8` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0ec05a11813ea801ff6d75110ad09cd0824ddba17dfe17128ea0d5f68e6c5272` |
| `zerofrom-derive` | `0.1.7` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `11532158c46691caf0f2593ea8358fed6bbf68a0315e80aae9bd41fbade684a1` |
| `zeroize` | `1.9.0` | `Apache-2.0 OR MIT` | (absent) | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `e13c156562582aa81c60cb29407084cdb54c4164760106ab78e6c5b0858cf64e` |
| `zerotrie` | `0.2.4` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `0f9152d31db0792fa83f70fb2f83148effb5c1f5b8c7686c3459e361d9bc20bf` |
| `zerovec` | `0.11.6` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `90f911cbc359ab6af17377d242225f4d75119aec87ea711a880987b18cd7b239` |
| `zerovec-derive` | `0.11.3` | `Unicode-3.0` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `625dc425cab0dca6dc3c3319506e6593dcb08a9f387ea3b284dbd52a92c40555` |
| `zmij` | `1.0.23` | `MIT` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `aarch64-apple-darwin`<br>`x86_64-apple-darwin`<br>`x86_64-unknown-linux-gnu` | `29666d0abbfad1e3dc4dcf6144730dd3a3ab225bbbdac83319345b1b44ccfc1b` |

**Exact count:** default 191; typesafe 242; combined 242 current package records; 402 named legal-file occurrences.

## Packages with no supplied named legal file

These declarations do not substitute for supplied legal text or establish that no other obligations exist.

- `monty 0.0.21`: `MIT` (manifest declaration only).
- `monty-macros 0.0.21`: `MIT` (manifest declaration only).
- `monty-types 0.0.21`: `MIT` (manifest declaration only).
- `quote-use 0.8.4`: `MIT` (manifest declaration only).
- `quote-use-macros 0.8.4`: `MIT` (manifest declaration only).
- `ruff_python_ast 0.0.3`: `MIT` (manifest declaration only).
- `ruff_python_codegen 0.0.3`: `MIT` (manifest declaration only).
- `ruff_python_literal 0.0.3`: `MIT` (manifest declaration only).
- `ruff_python_parser 0.0.3`: `MIT` (manifest declaration only).
- `ruff_python_stdlib 0.0.3`: `MIT` (manifest declaration only).
- `ruff_python_trivia 0.0.3`: `MIT` (manifest declaration only).
- `ruff_source_file 0.0.3`: `MIT` (manifest declaration only).
- `ruff_text_size 0.0.3`: `MIT` (manifest declaration only).

## Supplied legal files (deduplicated bodies)

The machine index `release/current-third-party-notice.json` is authoritative for exact source bytes:
UTF-8 encode each body text without newline conversion; occurrences reference its SHA-256 key.
Rendering converts CRLF and lone CR to LF. All source trailing newlines are retained; when absent,
one framing LF is added before the closing fence. Fences and framing LF are not source bytes.

### Body `000b4962e6b27176a0ff89cce4be555b16472cafb5671eb2804a8fdac6854793`

Source bytes: `11357`; source SHA-256 `000b4962e6b27176a0ff89cce4be555b16472cafb5671eb2804a8fdac6854793`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `005fc765ddc5115da796cca915baa9557abae13ff35e0a47c47affc56f6c414d`

Source bytes: `14870`; source SHA-256 `005fc765ddc5115da796cca915baa9557abae13ff35e0a47c47affc56f6c414d`; line endings: `{'crlf': 0, 'lf': 272, 'cr': 0}`; ends with LF: `true`.

```text

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


Licenses for support code
-------------------------

Parts of the TLS test suite are under the Go license. This code is not included
in BoringSSL (i.e. libcrypto and libssl) when compiled, however, so
distributing code linked against BoringSSL does not trigger this license:

Copyright (c) 2009 The Go Authors. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

   * Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the
distribution.
   * Neither the name of Google Inc. nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

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


BoringSSL uses the Chromium test infrastructure to run a continuous build,
trybots etc. The scripts which manage this, and the script for generating build
metadata, are under the Chromium license. Distributing code linked against
BoringSSL does not trigger this license.

Copyright 2015 The Chromium Authors. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

   * Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the
distribution.
   * Neither the name of Google Inc. nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

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
```

### Body `013ca8b1499479ce162f0d68ff25f4ac0a98dae625d55a8eabfb1fb4aa38933d`

Source bytes: `1082`; source SHA-256 `013ca8b1499479ce162f0d68ff25f4ac0a98dae625d55a8eabfb1fb4aa38933d`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f`

Source bytes: `126`; source SHA-256 `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f`; line endings: `{'crlf': 0, 'lf': 3, 'cr': 0}`; ends with LF: `true`.

```text
This project is dual-licensed under the Unlicense and MIT licenses.

You may use this code under the terms of either license.
```

### Body `0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a`

Source bytes: `10854`; source SHA-256 `0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `0352320d9929e862c1f07b59caacc3cd1bbacfec0ad4136bf4c89d4ca8939781`

Source bytes: `1114`; source SHA-256 `0352320d9929e862c1f07b59caacc3cd1bbacfec0ad4136bf4c89d4ca8939781`; line endings: `{'crlf': 0, 'lf': 22, 'cr': 0}`; ends with LF: `true`.

```text
# MIT License

Copyright (c) 2020 Stephen M. Coakley
Copyright (c) The Ratatui Developers

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
```

### Body `035e70219855119df4273b3c5b97543ae82e0dd60c520416e759107c602f651b`

Source bytes: `1058`; source SHA-256 `035e70219855119df4273b3c5b97543ae82e0dd60c520416e759107c602f651b`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `0444c6991eead6822f7b9102e654448d51624431119546492e8b231db42c48bb`

Source bytes: `1057`; source SHA-256 `0444c6991eead6822f7b9102e654448d51624431119546492e8b231db42c48bb`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `04ea4849dba9dcae07113850c6f1b1a69052c625210639914eee352023f750ad`

Source bytes: `10835`; source SHA-256 `04ea4849dba9dcae07113850c6f1b1a69052c625210639914eee352023f750ad`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `061dc50af2cd9340703daf61978af3200cf681b12ea67a323c33ba109a23a45e`

Source bytes: `1071`; source SHA-256 `061dc50af2cd9340703daf61978af3200cf681b12ea67a323c33ba109a23a45e`; line endings: `{'crlf': 0, 'lf': 20, 'cr': 0}`; ends with LF: `false`.

```text
MIT License

Copyright (c) 2016 Jerome Froelich

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
```

### Body `074e6e32c86a4c0ef8b3ed25b721ca23aca83df277cd88106ef7177c354615ff`

Source bytes: `10280`; source SHA-256 `074e6e32c86a4c0ef8b3ed25b721ca23aca83df277cd88106ef7177c354615ff`; line endings: `{'crlf': 0, 'lf': 73, 'cr': 0}`; ends with LF: `true`.

```text
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

"License" shall mean the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 9 of this document.

"Licensor" shall mean the copyright owner or entity authorized by the copyright owner that is granting the License.

"Legal Entity" shall mean the union of the acting entity and all other entities that control, are controlled by, or are under common control with that entity. For the purposes of this definition, "control" means (i) the power, direct or indirect, to cause the direction or management of such entity, whether by contract or otherwise, or (ii) ownership of fifty percent (50%) or more of the outstanding shares, or (iii) beneficial ownership of such entity.

"You" (or "Your") shall mean an individual or Legal Entity exercising permissions granted by this License.

"Source" form shall mean the preferred form for making modifications, including but not limited to software source code, documentation source, and configuration files.

"Object" form shall mean any form resulting from mechanical transformation or translation of a Source form, including but not limited to compiled object code, generated documentation, and conversions to other media types.

"Work" shall mean the work of authorship, whether in Source or Object form, made available under the License, as indicated by a copyright notice that is included in or attached to the work (an example is provided in the Appendix below).

"Derivative Works" shall mean any work, whether in Source or Object form, that is based on (or derived from) the Work and for which the editorial revisions, annotations, elaborations, or other modifications represent, as a whole, an original work of authorship. For the purposes of this License, Derivative Works shall not include works that remain separable from, or merely link (or bind by name) to the interfaces of, the Work and Derivative Works thereof.

"Contribution" shall mean any work of authorship, including the original version of the Work and any modifications or additions to that Work or Derivative Works thereof, that is intentionally submitted to Licensor for inclusion in the Work by the copyright owner or by an individual or Legal Entity authorized to submit on behalf of the copyright owner. For the purposes of this definition, "submitted" means any form of electronic, verbal, or written communication sent to the Licensor or its representatives, including but not limited to communication on electronic mailing lists, source code control systems, and issue tracking systems that are managed by, or on behalf of, the Licensor for the purpose of discussing and improving the Work, but excluding communication that is conspicuously marked or otherwise designated in writing by the copyright owner as "Not a Contribution."

"Contributor" shall mean Licensor and any individual or Legal Entity on behalf of whom a Contribution has been received by Licensor and subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, publicly perform, sublicense, and distribute the Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable (except as stated in this section) patent license to make, have made, use, offer to sell, sell, import, and otherwise transfer the Work, where such license applies only to those patent claims licensable by such Contributor that are necessarily infringed by their Contribution(s) alone or by combination of their Contribution(s) with the Work to which such Contribution(s) was submitted. If You institute patent litigation against any entity (including a cross-claim or counterclaim in a lawsuit) alleging that the Work or a Contribution incorporated within the Work constitutes direct or contributory patent infringement, then any patent licenses granted to You under this License for that Work shall terminate as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the Work or Derivative Works thereof in any medium, with or without modifications, and in Source or Object form, provided that You meet the following conditions:

     (a) You must give any other recipients of the Work or Derivative Works a copy of this License; and

     (b) You must cause any modified files to carry prominent notices stating that You changed the files; and

     (c) You must retain, in the Source form of any Derivative Works that You distribute, all copyright, patent, trademark, and attribution notices from the Source form of the Work, excluding those notices that do not pertain to any part of the Derivative Works; and

     (d) If the Work includes a "NOTICE" text file as part of its distribution, then any Derivative Works that You distribute must include a readable copy of the attribution notices contained within such NOTICE file, excluding those notices that do not pertain to any part of the Derivative Works, in at least one of the following places: within a NOTICE text file distributed as part of the Derivative Works; within the Source form or documentation, if provided along with the Derivative Works; or, within a display generated by the Derivative Works, if and wherever such third-party notices normally appear. The contents of the NOTICE file are for informational purposes only and do not modify the License. You may add Your own attribution notices within Derivative Works that You distribute, alongside or as an addendum to the NOTICE text from the Work, provided that such additional attribution notices cannot be construed as modifying the License.

     You may add Your own copyright statement to Your modifications and may provide additional or different license terms and conditions for use, reproduction, or distribution of Your modifications, or for any such Derivative Works as a whole, provided Your use, reproduction, and distribution of the Work otherwise complies with the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise, any Contribution intentionally submitted for inclusion in the Work by You to the Licensor shall be under the terms and conditions of this License, without any additional terms or conditions. Notwithstanding the above, nothing herein shall supersede or modify the terms of any separate license agreement you may have executed with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade names, trademarks, service marks, or product names of the Licensor, except as required for reasonable and customary use in describing the origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory, whether in tort (including negligence), contract, or otherwise, unless required by applicable law (such as deliberate and grossly negligent acts) or agreed to in writing, shall any Contributor be liable to You for damages, including any direct, indirect, special, incidental, or consequential damages of any character arising as a result of this License or out of the use or inability to use the Work (including but not limited to damages for loss of goodwill, work stoppage, computer failure or malfunction, or any and all other commercial damages or losses), even if such Contributor has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing the Work or Derivative Works thereof, You may choose to offer, and charge a fee for, acceptance of support, warranty, indemnity, or other liability obligations and/or rights consistent with this License. However, in accepting such obligations, You may act only on Your own behalf and on Your sole responsibility, not on behalf of any other Contributor, and only if You agree to indemnify, defend, and hold each Contributor harmless for any liability incurred by, or claims asserted against, such Contributor by reason of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

To apply the Apache License to your work, attach the following boilerplate notice, with the fields enclosed by brackets "[]" replaced with your own identifying information. (Don't include the brackets!)  The text should be enclosed in the appropriate comment syntax for the file format. We also recommend that a file or class name and description of purpose be included on the same "printed page" as the copyright notice for easier identification within third-party archives.

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
```

### Body `07919255c7e04793d8ea760d6c2ce32d19f9ff02bdbdde3ce90b1e1880929a9b`

Source bytes: `1082`; source SHA-256 `07919255c7e04793d8ea760d6c2ce32d19f9ff02bdbdde3ce90b1e1880929a9b`; line endings: `{'crlf': 0, 'lf': 19, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2014 Carl Lerche and other MIO contributors

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
```

### Body `0ab4d106b6faac07fb6a051815fd1b4d862d730895e2d7d7358c2f13565e7a38`

Source bytes: `1099`; source SHA-256 `0ab4d106b6faac07fb6a051815fd1b4d862d730895e2d7d7358c2f13565e7a38`; line endings: `{'crlf': 0, 'lf': 20, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9`

Source bytes: `1072`; source SHA-256 `0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `0d25d03b5ab49576178ad0cae7a2648d12c17ad0452fe49c07e55e4b59aa5257`

Source bytes: `1091`; source SHA-256 `0d25d03b5ab49576178ad0cae7a2648d12c17ad0452fe49c07e55e4b59aa5257`; line endings: `{'crlf': 0, 'lf': 26, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `0d52feec79589df30138dad3800323fe5686b764b73347330a2dfef8ac83efe8`

Source bytes: `1073`; source SHA-256 `0d52feec79589df30138dad3800323fe5686b764b73347330a2dfef8ac83efe8`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`

Source bytes: `10174`; source SHA-256 `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`; line endings: `{'crlf': 0, 'lf': 177, 'cr': 0}`; ends with LF: `true`.

```text

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
```

### Body `0dd882e53de11566d50f8e8e2d5a651bcf3fabee4987d70f306233cf39094ba7`

Source bytes: `1076`; source SHA-256 `0dd882e53de11566d50f8e8e2d5a651bcf3fabee4987d70f306233cf39094ba7`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
The MIT License (MIT)

Copyright (c) 2015 Alice Maz

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
```

### Body `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f`

Source bytes: `1081`; source SHA-256 `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e`

Source bytes: `1066`; source SHA-256 `123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `13f4cc9fbc8d4a447b28aa84019c10ad4abf4b5f6919db061bf6690ccc23bc02`

Source bytes: `1079`; source SHA-256 `13f4cc9fbc8d4a447b28aa84019c10ad4abf4b5f6919db061bf6690ccc23bc02`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `1418fdabd96762bb5892098a229061f07dd624245687fd0a95ef33f3feb845a0`

Source bytes: `1051`; source SHA-256 `1418fdabd96762bb5892098a229061f07dd624245687fd0a95ef33f3feb845a0`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `177540cad091a40e8071db310bc3b6115c4e329a92a234609b60c154b008a888`

Source bytes: `1063`; source SHA-256 `177540cad091a40e8071db310bc3b6115c4e329a92a234609b60c154b008a888`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df`

Source bytes: `1060`; source SHA-256 `1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df`; line endings: `{'crlf': 0, 'lf': 26, 'cr': 0}`; ends with LF: `true`.

```text
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

```

### Body `1dd8eca0f83669e75fa119e34fb9e1be9d16e3e9b6368962b8019db6e8ae5f7b`

Source bytes: `1062`; source SHA-256 `1dd8eca0f83669e75fa119e34fb9e1be9d16e3e9b6368962b8019db6e8ae5f7b`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `1e697ce8d21401fbf1bddd9b5c3fd4c4c79ae1e3bdf51f81761c85e11d5a89cd`

Source bytes: `1166`; source SHA-256 `1e697ce8d21401fbf1bddd9b5c3fd4c4c79ae1e3bdf51f81761c85e11d5a89cd`; line endings: `{'crlf': 0, 'lf': 23, 'cr': 0}`; ends with LF: `true`.

```text
The MIT License (MIT)

Copyright (c) 2015 Danny Guo
Copyright (c) 2016 Titus Wormer <tituswormer@gmail.com>
Copyright (c) 2018 Akash Kurdekar

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
```

### Body `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b`

Source bytes: `1117`; source SHA-256 `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b`; line endings: `{'crlf': 0, 'lf': 26, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `20c7855c364d57ea4c97889a5e8d98470a9952dade37bd9248b9a54431670e5e`

Source bytes: `1072`; source SHA-256 `20c7855c364d57ea4c97889a5e8d98470a9952dade37bd9248b9a54431670e5e`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2013-2016 The rust-url developers

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
```

### Body `20fe7b00e904ed690e3b9fd6073784d3fc428141dbd10b81c01fd143d0797f58`

Source bytes: `9899`; source SHA-256 `20fe7b00e904ed690e3b9fd6073784d3fc428141dbd10b81c01fd143d0797f58`; line endings: `{'crlf': 176, 'lf': 0, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59`

Source bytes: `1052`; source SHA-256 `219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59`; line endings: `{'crlf': 0, 'lf': 7, 'cr': 0}`; ends with LF: `true`.

```text
Copyright 2016 Nika Layzell

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

### Body `23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d`

Source bytes: `321`; source SHA-256 `23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d`; line endings: `{'crlf': 0, 'lf': 7, 'cr': 0}`; ends with LF: `true`.

```text
Licensed under the Apache License, Version 2.0
<LICENSE-APACHE or
http://www.apache.org/licenses/LICENSE-2.0> or the MIT
license <LICENSE-MIT or http://opensource.org/licenses/MIT>,
at your option. All files in the project carrying such
notice may not be copied, modified, or distributed except
according to those terms.
```

### Body `23d6f253d73a884498c6979c2d94f9aeaeb9d244557729b7706a332c16bce2f1`

Source bytes: `1075`; source SHA-256 `23d6f253d73a884498c6979c2d94f9aeaeb9d244557729b7706a332c16bce2f1`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Source bytes: `1023`; source SHA-256 `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`; line endings: `{'crlf': 0, 'lf': 23, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `248378d0a3383c173fb925f17141b88e71580b3ba17ddc6ac3d2a344683232ab`

Source bytes: `1083`; source SHA-256 `248378d0a3383c173fb925f17141b88e71580b3ba17ddc6ac3d2a344683232ab`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2019-2026 Sean McArthur & Hyper Contributors

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
```

### Body `253cd04c6714889df2d32f3f64d669179a1c95c76ac43c40882c52eb06bc3552`

Source bytes: `1070`; source SHA-256 `253cd04c6714889df2d32f3f64d669179a1c95c76ac43c40882c52eb06bc3552`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
MIT License

Copyright (c) Tokio Contributors

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
```

### Body `268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5`

Source bytes: `12243`; source SHA-256 `268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5`; line endings: `{'crlf': 0, 'lf': 220, 'cr': 0}`; ends with LF: `true`.

```text

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


--- LLVM Exceptions to the Apache 2.0 License ----

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

```

### Body `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427`

Source bytes: `10874`; source SHA-256 `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427`; line endings: `{'crlf': 0, 'lf': 202, 'cr': 0}`; ends with LF: `true`.

```text
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

Copyright (c) 2016 Alex Crichton
Copyright (c) 2017 The Tokio Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Body `27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac`

Source bytes: `1054`; source SHA-256 `27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4`

Source bytes: `1130`; source SHA-256 `29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4`; line endings: `{'crlf': 0, 'lf': 26, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `2afdd30d54b4d62b6f488a6bcc1546e84ec5061f13f4209c03d012348783795a`

Source bytes: `1080`; source SHA-256 `2afdd30d54b4d62b6f488a6bcc1546e84ec5061f13f4209c03d012348783795a`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `2d01890414494742ba4a509fcec8efa40f6d8be22cbd72be7cff08d6fda4ec89`

Source bytes: `1062`; source SHA-256 `2d01890414494742ba4a509fcec8efa40f6d8be22cbd72be7cff08d6fda4ec89`; line endings: `{'crlf': 0, 'lf': 19, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2014-2026 Sean McArthur

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
```

### Body `30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652`

Source bytes: `1022`; source SHA-256 `30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652`; line endings: `{'crlf': 0, 'lf': 22, 'cr': 0}`; ends with LF: `false`.

```text
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
```

### Body `3290ae0fbc9ddb77d2239121d710f0bb9d31b3b4744e6d97fe01e652b4c1870b`

Source bytes: `881`; source SHA-256 `3290ae0fbc9ddb77d2239121d710f0bb9d31b3b4744e6d97fe01e652b4c1870b`; line endings: `{'crlf': 0, 'lf': 29, 'cr': 0}`; ends with LF: `true`.

```text
Short version for non-lawyers:

`linux-raw-sys` is triple-licensed under Apache 2.0 with the LLVM Exception,
Apache 2.0, and MIT terms.


Longer version:

Copyrights in the `linux-raw-sys` project are retained by their contributors.
No copyright assignment is required to contribute to the `linux-raw-sys`
project.

Some files include code derived from Rust's `libstd`; see the comments in
the code for details.

Except as otherwise noted (below and/or in individual files), `linux-raw-sys`
is licensed under:

 - the Apache License, Version 2.0, with the LLVM Exception
   <LICENSE-Apache-2.0_WITH_LLVM-exception> or
   <http://llvm.org/foundation/relicensing/LICENSE.txt>
 - the Apache License, Version 2.0
   <LICENSE-APACHE> or
   <http://www.apache.org/licenses/LICENSE-2.0>,
 - or the MIT license
   <LICENSE-MIT> or
   <http://opensource.org/licenses/MIT>,

at your option.
```

### Body `35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab`

Source bytes: `9724`; source SHA-256 `35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab`; line endings: `{'crlf': 0, 'lf': 176, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `36516aefdc84c5d5a1e7485425913a22dbda69eb1930c5e84d6ae4972b5194b9`

Source bytes: `1046`; source SHA-256 `36516aefdc84c5d5a1e7485425913a22dbda69eb1930c5e84d6ae4972b5194b9`; line endings: `{'crlf': 23, 'lf': 0, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `377c2e7c53250cc5905c0b0532d35973392af16ffb9596a41d99d202cf3617c9`

Source bytes: `853`; source SHA-256 `377c2e7c53250cc5905c0b0532d35973392af16ffb9596a41d99d202cf3617c9`; line endings: `{'crlf': 0, 'lf': 29, 'cr': 0}`; ends with LF: `true`.

```text
Short version for non-lawyers:

`rustix` is triple-licensed under Apache 2.0 with the LLVM Exception,
Apache 2.0, and MIT terms.


Longer version:

Copyrights in the `rustix` project are retained by their contributors.
No copyright assignment is required to contribute to the `rustix`
project.

Some files include code derived from Rust's `libstd`; see the comments in
the code for details.

Except as otherwise noted (below and/or in individual files), `rustix`
is licensed under:

 - the Apache License, Version 2.0, with the LLVM Exception
   <LICENSE-Apache-2.0_WITH_LLVM-exception> or
   <http://llvm.org/foundation/relicensing/LICENSE.txt>
 - the Apache License, Version 2.0
   <LICENSE-APACHE> or
   <http://www.apache.org/licenses/LICENSE-2.0>,
 - or the MIT license
   <LICENSE-MIT> or
   <http://opensource.org/licenses/MIT>,

at your option.
```

### Body `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Source bytes: `1057`; source SHA-256 `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `3823dda7cf046602f4b4e77ec8e227863dc4736037cc85bb33d9f19febe16bb7`

Source bytes: `14088`; source SHA-256 `3823dda7cf046602f4b4e77ec8e227863dc4736037cc85bb33d9f19febe16bb7`; line endings: `{'crlf': 0, 'lf': 258, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `391a5396cec6230bfabd4ef4eb2350eb895bc5efce377a2218f5702ed020d3e3`

Source bytes: `1063`; source SHA-256 `391a5396cec6230bfabd4ef4eb2350eb895bc5efce377a2218f5702ed020d3e3`; line endings: `{'crlf': 0, 'lf': 20, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2015-2025 Sean McArthur

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

```

### Body `3bc70e239e91272782006c638fc0452a714d384224f11f0923036b7be07cf9b5`

Source bytes: `1081`; source SHA-256 `3bc70e239e91272782006c638fc0452a714d384224f11f0923036b7be07cf9b5`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c`

Source bytes: `1053`; source SHA-256 `3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `411781fd38700f2357a14126d0ab048164ab881f1dcb335c1bb932e232c9a2f5`

Source bytes: `1082`; source SHA-256 `411781fd38700f2357a14126d0ab048164ab881f1dcb335c1bb932e232c9a2f5`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `41ace205715d9f19a3214218cc1c01d57c533e02cd0fef7c8e51a49a7fce5ac5`

Source bytes: `864`; source SHA-256 `41ace205715d9f19a3214218cc1c01d57c533e02cd0fef7c8e51a49a7fce5ac5`; line endings: `{'crlf': 0, 'lf': 20, 'cr': 0}`; ends with LF: `true`.

```text
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

```

### Body `4249c8e6c5ebb85f97c77e6457c6fafc1066406eb8f1ef61e796fbdc5ff18482`

Source bytes: `1062`; source SHA-256 `4249c8e6c5ebb85f97c77e6457c6fafc1066406eb8f1ef61e796fbdc5ff18482`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2019 Tower Contributors

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
```

### Body `42fa16951ce7f24b5a467a40e5b449a1d41e662f97ca779864f053f39e097737`

Source bytes: `1130`; source SHA-256 `42fa16951ce7f24b5a467a40e5b449a1d41e662f97ca779864f053f39e097737`; line endings: `{'crlf': 0, 'lf': 26, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1`

Source bytes: `1092`; source SHA-256 `4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `45f522cacecb1023856e46df79ca625dfc550c94910078bd8aec6e02880b3d42`

Source bytes: `1055`; source SHA-256 `45f522cacecb1023856e46df79ca625dfc550c94910078bd8aec6e02880b3d42`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2018 Carl Lerche

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
```

### Body `45fd05c4865e7c350b98ad7ac50e1b15462d49af4a91e9b0c9dd933dc9a69742`

Source bytes: `10835`; source SHA-256 `45fd05c4865e7c350b98ad7ac50e1b15462d49af4a91e9b0c9dd933dc9a69742`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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

Copyright 2023 Dirkjan Ochtman

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Body `47d4e1803702728e03d30f8a848ae2249ba274bbd9f8443e803f7924d83cd371`

Source bytes: `1063`; source SHA-256 `47d4e1803702728e03d30f8a848ae2249ba274bbd9f8443e803f7924d83cd371`; line endings: `{'crlf': 0, 'lf': 20, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2016-2025 Sean McArthur

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

```

### Body `47dc9ff29128ddfb4d6a0435383c9f89120bc374dbcc1dd00b933a0b28aa7865`

Source bytes: `1062`; source SHA-256 `47dc9ff29128ddfb4d6a0435383c9f89120bc374dbcc1dd00b933a0b28aa7865`; line endings: `{'crlf': 0, 'lf': 7, 'cr': 0}`; ends with LF: `true`.

```text
Copyright 2017 Juniper Networks, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

### Body `4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f`

Source bytes: `1076`; source SHA-256 `4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871`

Source bytes: `1071`; source SHA-256 `4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `4db045835f216d50e0ac5bc3742ddd91756257a8c96578f9f98545d58a1237df`

Source bytes: `1075`; source SHA-256 `4db045835f216d50e0ac5bc3742ddd91756257a8c96578f9f98545d58a1237df`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `4f44572785f35152c1fd2eadf565b7e079c0f300b4324f0af653419f9d76b735`

Source bytes: `11350`; source SHA-256 `4f44572785f35152c1fd2eadf565b7e079c0f300b4324f0af653419f9d76b735`; line endings: `{'crlf': 0, 'lf': 202, 'cr': 0}`; ends with LF: `true`.

```text
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

```

### Body `503558bfefe66ca15e4e3f7955b3cb0ec87fd52f29bf24b336af7bd00e946d5c`

Source bytes: `1068`; source SHA-256 `503558bfefe66ca15e4e3f7955b3cb0ec87fd52f29bf24b336af7bd00e946d5c`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2017 tokio-jsonrpc developers

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
```

### Body `5049cf464977eff4b4fcfa7988d84e74116956a3eb9d5f1d451b3f828f945233`

Source bytes: `1067`; source SHA-256 `5049cf464977eff4b4fcfa7988d84e74116956a3eb9d5f1d451b3f828f945233`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2019-2021 Tower Contributors

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
```

### Body `508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1`

Source bytes: `1036`; source SHA-256 `508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1`; line endings: `{'crlf': 0, 'lf': 19, 'cr': 0}`; ends with LF: `true`.

```text
MIT License

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
```

### Body `50eb43e8d742c9c61a9391e42b2184fce54dbd1893a1bb1c85b8c9ee217ab1f5`

Source bytes: `1132`; source SHA-256 `50eb43e8d742c9c61a9391e42b2184fce54dbd1893a1bb1c85b8c9ee217ab1f5`; line endings: `{'crlf': 0, 'lf': 22, 'cr': 0}`; ends with LF: `true`.

```text
The MIT License (MIT)

Copyright (c) 2016-2022 Florian Dehau
Copyright (c) 2023-2025 The Ratatui Developers

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
```

### Body `520a93f9b172b4c8d2a7ab6f0da1f5f987eba7270ab64a02972095cd87df7fc4`

Source bytes: `1070`; source SHA-256 `520a93f9b172b4c8d2a7ab6f0da1f5f987eba7270ab64a02972095cd87df7fc4`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
MIT License

Copyright (c) 2024 Josh McKinney

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
```

### Body `553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583`

Source bytes: `566`; source SHA-256 `553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583`; line endings: `{'crlf': 0, 'lf': 13, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `562c625100a5ee635f35de5908c206b7d8783e4dcd10ede1c90e4c0e7dddfe5f`

Source bytes: `1075`; source SHA-256 `562c625100a5ee635f35de5908c206b7d8783e4dcd10ede1c90e4c0e7dddfe5f`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `58545fed1565e42d687aecec6897d35c6d37ccb71479a137c0deb2203e125c79`

Source bytes: `1085`; source SHA-256 `58545fed1565e42d687aecec6897d35c6d37ccb71479a137c0deb2203e125c79`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd`

Source bytes: `11357`; source SHA-256 `58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `false`.

```text

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
```

### Body `5b698ca13897be3afdb7174256fa1574f8c6892b8bea1a66dd6469d3fe27885a`

Source bytes: `916`; source SHA-256 `5b698ca13897be3afdb7174256fa1574f8c6892b8bea1a66dd6469d3fe27885a`; line endings: `{'crlf': 0, 'lf': 19, 'cr': 0}`; ends with LF: `true`.

```text
Except as otherwise noted, this project is licensed under the following
(ISC-style) terms:

Copyright 2015 Brian Smith.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIM ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

The files under third-party/chromium are licensed as described in
third-party/chromium/LICENSE.
```

### Body `5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7`

Source bytes: `1056`; source SHA-256 `5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7`; line endings: `{'crlf': 0, 'lf': 24, 'cr': 0}`; ends with LF: `false`.

```text
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
```

### Body `62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3`

Source bytes: `1067`; source SHA-256 `62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `6226d0632e2e1a80c23597e964da9812ae193c535fe058154afb034e94167aa5`

Source bytes: `1849`; source SHA-256 `6226d0632e2e1a80c23597e964da9812ae193c535fe058154afb034e94167aa5`; line endings: `{'crlf': 0, 'lf': 45, 'cr': 0}`; ends with LF: `true`.

```text
===============================================================================

Copyright (c) 2016 Alex Crichton
Copyright (c) 2017 The Tokio Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

===============================================================================

Copyright (c) 2016 Alex Crichton
Copyright (c) 2017 The Tokio Authors

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
```

### Body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

Source bytes: `9723`; source SHA-256 `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`; line endings: `{'crlf': 0, 'lf': 176, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Source bytes: `1071`; source SHA-256 `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd`

Source bytes: `1094`; source SHA-256 `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd`; line endings: `{'crlf': 0, 'lf': 26, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2016 Alex Crichton
Copyright (c) 2017 The Tokio Authors

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
```

### Body `68653aaa727a2bfa31b7a751e31701ce33c49d695c12dd291a07d1c54da4c14b`

Source bytes: `262`; source SHA-256 `68653aaa727a2bfa31b7a751e31701ce33c49d695c12dd291a07d1c54da4c14b`; line endings: `{'crlf': 0, 'lf': 8, 'cr': 0}`; ends with LF: `true`.

```text
This project is licensed under either of

 * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
   https://www.apache.org/licenses/LICENSE-2.0)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or
   https://opensource.org/licenses/MIT)

at your option.
```

### Body `696759d65dfe558ff7d9f031c76db19ec5c0767470fb67c4e8d990820d1e99c9`

Source bytes: `10832`; source SHA-256 `696759d65dfe558ff7d9f031c76db19ec5c0767470fb67c4e8d990820d1e99c9`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `6ac8711fb340c62ce0a4ecd463342d3fa0e8e70de697c863a2e1c0c53006003c`

Source bytes: `1084`; source SHA-256 `6ac8711fb340c62ce0a4ecd463342d3fa0e8e70de697c863a2e1c0c53006003c`; line endings: `{'crlf': 0, 'lf': 20, 'cr': 0}`; ends with LF: `false`.

```text
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
```

### Body `6b7374c39a57e57fc2c38eb529c4c88340152b10f51dd5ae2d819dfa67f61715`

Source bytes: `1086`; source SHA-256 `6b7374c39a57e57fc2c38eb529c4c88340152b10f51dd5ae2d819dfa67f61715`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `6d3a9431e65e69c73a8923e6517b889d17549b23db406b9ec027710d16af701f`

Source bytes: `1054`; source SHA-256 `6d3a9431e65e69c73a8923e6517b889d17549b23db406b9ec027710d16af701f`; line endings: `{'crlf': 0, 'lf': 24, 'cr': 0}`; ends with LF: `false`.

```text
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
```

### Body `6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51`

Source bytes: `10282`; source SHA-256 `6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51`; line endings: `{'crlf': 0, 'lf': 187, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `6ee2ed6c77710de911761acd5fc1ad1da00f476beb1a7ef27e78c2d1858deafc`

Source bytes: `1022`; source SHA-256 `6ee2ed6c77710de911761acd5fc1ad1da00f476beb1a7ef27e78c2d1858deafc`; line endings: `{'crlf': 0, 'lf': 23, 'cr': 0}`; ends with LF: `true`.

```text
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
SHALL THE AUTHOR OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
```

### Body `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`

Source bytes: `1062`; source SHA-256 `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`; line endings: `{'crlf': 0, 'lf': 19, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `709e3175b4212f7b13aa93971c9f62ff8c69ec45ad8c6532a7e0c41d7a7d6f8c`

Source bytes: `1082`; source SHA-256 `709e3175b4212f7b13aa93971c9f62ff8c69ec45ad8c6532a7e0c41d7a7d6f8c`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2016 Joseph Birr-Pixton <jpixton@gmail.com>

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
```

### Body `7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349`

Source bytes: `1049`; source SHA-256 `7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `74a7056189235b49336669da4e67ad1b315de4ed17e93df751f48c3fab403812`

Source bytes: `1109`; source SHA-256 `74a7056189235b49336669da4e67ad1b315de4ed17e93df751f48c3fab403812`; line endings: `{'crlf': 0, 'lf': 22, 'cr': 0}`; ends with LF: `true`.

```text
The MIT License (MIT)

Copyright (c) 2016 Dylan Ede
Copyright (c) 2024 Josh McKinney

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
```

### Body `74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3`

Source bytes: `2847`; source SHA-256 `74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3`; line endings: `{'crlf': 0, 'lf': 57, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `751963a8b88c0e3a9f27e98933079fbcf09b9998b2c13ac49c2e4d58444520d6`

Source bytes: `10833`; source SHA-256 `751963a8b88c0e3a9f27e98933079fbcf09b9998b2c13ac49c2e4d58444520d6`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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

Copyright 2016 Sean McArthur

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Body `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545`

Source bytes: `1043`; source SHA-256 `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `7abd9b6960dcf7d4d0a48606a5b71bfe37d472db68d70637f3a58a56785f1621`

Source bytes: `769`; source SHA-256 `7abd9b6960dcf7d4d0a48606a5b71bfe37d472db68d70637f3a58a56785f1621`; line endings: `{'crlf': 0, 'lf': 13, 'cr': 0}`; ends with LF: `true`.

```text
// Copyright 2015-2016 Brian Smith.
//
// Permission to use, copy, modify, and/or distribute this software for any
// purpose with or without fee is hereby granted, provided that the above
// copyright notice and this permission notice appear in all copies.
//
// THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIM ALL WARRANTIES
// WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
// MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR
// ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
// WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
// ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
// OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

### Body `7b273685779bddaafd4c83040dc25fe8c747b73d21f894741df9065609abdff9`

Source bytes: `1075`; source SHA-256 `7b273685779bddaafd4c83040dc25fe8c747b73d21f894741df9065609abdff9`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0`

Source bytes: `1071`; source SHA-256 `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `7c7134b9f7b978c03fca875517cf398db91f19bbb8109b6685e742aa3f57468e`

Source bytes: `1091`; source SHA-256 `7c7134b9f7b978c03fca875517cf398db91f19bbb8109b6685e742aa3f57468e`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `7cfafc877eccc46c0e346ccbaa5c51bb6b894d2b818e617d970211e232785ad4`

Source bytes: `775`; source SHA-256 `7cfafc877eccc46c0e346ccbaa5c51bb6b894d2b818e617d970211e232785ad4`; line endings: `{'crlf': 0, 'lf': 15, 'cr': 0}`; ends with LF: `true`.

```text
ISC License (ISC)
Copyright (c) 2016, Joseph Birr-Pixton <jpixton@gmail.com>

Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted, provided that the
above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.
```

### Body `7dc1552e88f49132cb358b1b962fc5e79fa42d70bcbb88c526d33e45b8e98036`

Source bytes: `1062`; source SHA-256 `7dc1552e88f49132cb358b1b962fc5e79fa42d70bcbb88c526d33e45b8e98036`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2020 Project Developers

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
```

### Body `7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c`

Source bytes: `1211`; source SHA-256 `7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c`; line endings: `{'crlf': 0, 'lf': 24, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90`

Source bytes: `10850`; source SHA-256 `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32`

Source bytes: `1275`; source SHA-256 `83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32`; line endings: `{'crlf': 0, 'lf': 24, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `84b34dd7608f7fb9b17bd588a6bf392bf7de504e2716f024a77d89f1b145a151`

Source bytes: `851`; source SHA-256 `84b34dd7608f7fb9b17bd588a6bf392bf7de504e2716f024a77d89f1b145a151`; line endings: `{'crlf': 0, 'lf': 11, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2019 Daniel "Lokathor" Gee.

This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.

2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.

3. This notice may not be removed or altered from any source distribution.
```

### Body `86f2767527a034d6b9cb8bd98676925e58ed75bf805d234dc2a71a54150cbad1`

Source bytes: `11343`; source SHA-256 `86f2767527a034d6b9cb8bd98676925e58ed75bf805d234dc2a71a54150cbad1`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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

   Copyright 2024 Josh McKinney

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

### Body `8764a597675778ddfd4e25f81b08a05dbcf089ac05662df7613fe67f150e3aa2`

Source bytes: `1054`; source SHA-256 `8764a597675778ddfd4e25f81b08a05dbcf089ac05662df7613fe67f150e3aa2`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2014 Chris Wong

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
```

### Body `87d9feb9238c6bd8e0024fc4733b06cff036f89f36d93b7df1c8a0549bbb7a5b`

Source bytes: `11352`; source SHA-256 `87d9feb9238c6bd8e0024fc4733b06cff036f89f36d93b7df1c8a0549bbb7a5b`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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

   Copyright 2017 Juniper Networks, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

### Body `898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1`

Source bytes: `1062`; source SHA-256 `898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2019 Tokio Contributors

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
```

### Body `8a35369f3ca263b3c62fbb5032947e53b6bfebc6c8a4d1bb982de1c069f6fba5`

Source bytes: `1080`; source SHA-256 `8a35369f3ca263b3c62fbb5032947e53b6bfebc6c8a4d1bb982de1c069f6fba5`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
The MIT License (MIT)

Copyright (c) 2016 Jelte Fennema

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
```

### Body `8b43ce8accd61e9d370b5ca9e9c4f953279b5c239926c62315b40e24df51b726`

Source bytes: `1062`; source SHA-256 `8b43ce8accd61e9d370b5ca9e9c4f953279b5c239926c62315b40e24df51b726`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) The rust-url developers

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
```

### Body `8b4e95f5cf0dc40269c99f7b787203ffe04ded245ca2427422c196efa2b2f42a`

Source bytes: `1090`; source SHA-256 `8b4e95f5cf0dc40269c99f7b787203ffe04ded245ca2427422c196efa2b2f42a`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `8bb1b50b0e5c9399ae33bd35fab2769010fa6c14e8860c729a52295d84896b7a`

Source bytes: `10835`; source SHA-256 `8bb1b50b0e5c9399ae33bd35fab2769010fa6c14e8860c729a52295d84896b7a`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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

Copyright 2017 http-rs authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Body `8bce3b45e49ecd1461f223b46de133d8f62cd39f745cfdaf81bee554b908bd42`

Source bytes: `1072`; source SHA-256 `8bce3b45e49ecd1461f223b46de133d8f62cd39f745cfdaf81bee554b908bd42`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `8c7516d4b27b1e495be5e38b612298b63de48d05f49cdac94f70f3cd70f8864b`

Source bytes: `1082`; source SHA-256 `8c7516d4b27b1e495be5e38b612298b63de48d05f49cdac94f70f3cd70f8864b`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2018-2026 The RustCrypto Project Developers

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
```

### Body `8ce0830173fdac609dfb4ea603fdc002c2f4af0dc9b1a005653f5da9cf534b18`

Source bytes: `1055`; source SHA-256 `8ce0830173fdac609dfb4ea603fdc002c2f4af0dc9b1a005653f5da9cf534b18`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2019 Carl Lerche

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
```

### Body `8ea93490d74a5a1b1af3ff71d786271b3f1e5f0bea79ac16e02ec533cef040d6`

Source bytes: `1067`; source SHA-256 `8ea93490d74a5a1b1af3ff71d786271b3f1e5f0bea79ac16e02ec533cef040d6`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
MIT License

Copyright (c) 2017 Ted Driggs

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
```

### Body `90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5`

Source bytes: `569`; source SHA-256 `90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5`; line endings: `{'crlf': 0, 'lf': 12, 'cr': 0}`; ends with LF: `true`.

```text
Copyrights in the Rand project are retained by their contributors. No
copyright assignment is required to contribute to the Rand project.

For full authorship information, see the version control history.

Except as otherwise noted (below and/or in individual files), Rand is
licensed under the Apache License, Version 2.0 <LICENSE-APACHE> or
<http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
<LICENSE-MIT> or <http://opensource.org/licenses/MIT>, at your option.

The Rand project includes code from the Rust project
published under these same licenses.
```

### Body `9117d922e667125508dde62b02c1f57ed22f5ad21eb536aa2e2d99e1c796e639`

Source bytes: `1080`; source SHA-256 `9117d922e667125508dde62b02c1f57ed22f5ad21eb536aa2e2d99e1c796e639`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2023 Dirkjan Ochtman <dirkjan@ochtman.nl>

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
```

### Body `937230c05b5673fe216dda49dfc7c96591c63d0ea4c029e3e1b84aef3a45cbfd`

Source bytes: `1075`; source SHA-256 `937230c05b5673fe216dda49dfc7c96591c63d0ea4c029e3e1b84aef3a45cbfd`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `946c9835d8034d24404f8cfec5f4654cee5dad17e944afc3d06d742cf2882831`

Source bytes: `12307`; source SHA-256 `946c9835d8034d24404f8cfec5f4654cee5dad17e944afc3d06d742cf2882831`; line endings: `{'crlf': 0, 'lf': 240, 'cr': 0}`; ends with LF: `true`.

```text
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

```

### Body `95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc`

Source bytes: `9722`; source SHA-256 `95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc`; line endings: `{'crlf': 0, 'lf': 175, 'cr': 0}`; ends with LF: `false`.

```text
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
```

### Body `99aab70a96f3ecab683d8a319d9070af2213ae4c1601fb053fbe85e1361e32fe`

Source bytes: `19251`; source SHA-256 `99aab70a96f3ecab683d8a319d9070af2213ae4c1601fb053fbe85e1361e32fe`; line endings: `{'crlf': 0, 'lf': 337, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3`

Source bytes: `11350`; source SHA-256 `9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3`; line endings: `{'crlf': 0, 'lf': 202, 'cr': 0}`; ends with LF: `true`.

```text
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

```

### Body `9e0a97848ea543aef745c98e84fde696a9a3e0735538f6daefdd3cb1942effc1`

Source bytes: `1062`; source SHA-256 `9e0a97848ea543aef745c98e84fde696a9a3e0735538f6daefdd3cb1942effc1`; line endings: `{'crlf': 0, 'lf': 19, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2023-2025 Sean McArthur

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
```

### Body `9eacbcb81be660840c714a560a9d65ba07913db98dd4baf969f78dd499fdd60f`

Source bytes: `638`; source SHA-256 `9eacbcb81be660840c714a560a9d65ba07913db98dd4baf969f78dd499fdd60f`; line endings: `{'crlf': 0, 'lf': 15, 'cr': 0}`; ends with LF: `true`.

```text
The Apache License, Version 2.0 (Apache-2.0)

Copyright 2015-2020 the fiat-crypto authors (see the AUTHORS file)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Source bytes: `10847`; source SHA-256 `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `a65f5d0a945d267751344c95665945b90c030ea107faf5c85d518929886187da`

Source bytes: `1063`; source SHA-256 `a65f5d0a945d267751344c95665945b90c030ea107faf5c85d518929886187da`; line endings: `{'crlf': 0, 'lf': 20, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2018-2019 Sean McArthur

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

```

### Body `aa893340d14b9844625be6a50ac644169a01b52f0211cbf81b09e1874c8cd81d`

Source bytes: `1082`; source SHA-256 `aa893340d14b9844625be6a50ac644169a01b52f0211cbf81b09e1874c8cd81d`; line endings: `{'crlf': 0, 'lf': 19, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2020 Olivier Goffart <ogoffart@sixtyfps.io>

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
```

### Body `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf`

Source bytes: `10849`; source SHA-256 `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `abf8f3253498c07abb340315b01c73c2151f9f2a5622ea0b44bd8cadfa34072a`

Source bytes: `11357`; source SHA-256 `abf8f3253498c07abb340315b01c73c2151f9f2a5622ea0b44bd8cadfa34072a`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `aca4760f2a5eba9ce9d4448fe7cd3fcf98245a8315ede59ebd0c6085dd542e61`

Source bytes: `1083`; source SHA-256 `aca4760f2a5eba9ce9d4448fe7cd3fcf98245a8315ede59ebd0c6085dd542e61`; line endings: `{'crlf': 21, 'lf': 0, 'cr': 0}`; ends with LF: `true`.

```text
MIT License

Copyright (c) 2019 Timon

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
```

### Body `aed7b1758e35afa0cd0fde059d61950747ca11cd0e5e169cb21c11608daed772`

Source bytes: `1062`; source SHA-256 `aed7b1758e35afa0cd0fde059d61950747ca11cd0e5e169cb21c11608daed772`; line endings: `{'crlf': 0, 'lf': 20, 'cr': 0}`; ends with LF: `false`.

```text
MIT License

Copyright (c) 2025 rutrum

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
```

### Body `b1181a40b2a7b25cf66fd01481713bc1005df082c53ef73e851e55071b102744`

Source bytes: `856`; source SHA-256 `b1181a40b2a7b25cf66fd01481713bc1005df082c53ef73e851e55071b102744`; line endings: `{'crlf': 0, 'lf': 18, 'cr': 0}`; ends with LF: `false`.

```text
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
```

### Body `b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5`

Source bytes: `1072`; source SHA-256 `b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2013-2025 The rust-url developers

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
```

### Body `b3d734001a94efff3579978d953391aa7115f877657d25eb54037a43875d078a`

Source bytes: `499`; source SHA-256 `b3d734001a94efff3579978d953391aa7115f877657d25eb54037a43875d078a`; line endings: `{'crlf': 0, 'lf': 9, 'cr': 0}`; ends with LF: `true`.

```text
*ring* uses an "ISC" license, like BoringSSL used to use, for new code
files. See LICENSE-other-bits for the text of that license.

See LICENSE-BoringSSL for code that was sourced from BoringSSL under the
Apache 2.0 license. Some code that was sourced from BoringSSL under the ISC
license. In each case, the license info is at the top of the file.

See src/polyfill/once_cell/LICENSE-APACHE and src/polyfill/once_cell/LICENSE-MIT
for the license to code that was sourced from the once_cell project.
```

### Body `b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1`

Source bytes: `11357`; source SHA-256 `b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e`

Source bytes: `1085`; source SHA-256 `b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e`; line endings: `{'crlf': 0, 'lf': 19, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `b9eb266294324f672cbe945fe8f2e32f85024f0d61a1a7d14382cdde0ac44769`

Source bytes: `1058`; source SHA-256 `b9eb266294324f672cbe945fe8f2e32f85024f0d61a1a7d14382cdde0ac44769`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2016 Anthony Ramine

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
```

### Body `c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c`

Source bytes: `1742`; source SHA-256 `c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c`; line endings: `{'crlf': 0, 'lf': 42, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

Source bytes: `11358`; source SHA-256 `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`; line endings: `{'crlf': 0, 'lf': 202, 'cr': 0}`; ends with LF: `true`.

```text
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

```

### Body `c816a0749cdc6bf062a5111c159723de51b2bfac66a1dac2655abd9e6b1583eb`

Source bytes: `1096`; source SHA-256 `c816a0749cdc6bf062a5111c159723de51b2bfac66a1dac2655abd9e6b1583eb`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2018-2023 Sean McArthur
Copyright (c) 2016 Alex Crichton

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

```

### Body `c962ee4d1d05ddc138b202b2540219ebc57893fcf97b364852094a9a94ce1365`

Source bytes: `281`; source SHA-256 `c962ee4d1d05ddc138b202b2540219ebc57893fcf97b364852094a9a94ce1365`; line endings: `{'crlf': 0, 'lf': 7, 'cr': 0}`; ends with LF: `true`.

```text
Copyright 2012-2016 The Rust Project Developers.
Copyright 2016-2026 Frank Denis.

Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
<LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
option.
```

### Body `c986bcdb83103d4ddf58aeb7b5302359782e54dc4eea14a0cc27c62dcbd50729`

Source bytes: `1058`; source SHA-256 `c986bcdb83103d4ddf58aeb7b5302359782e54dc4eea14a0cc27c62dcbd50729`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5`

Source bytes: `1071`; source SHA-256 `c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566`

Source bytes: `1338`; source SHA-256 `c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566`; line endings: `{'crlf': 0, 'lf': 23, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d`

Source bytes: `1023`; source SHA-256 `cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d`; line endings: `{'crlf': 0, 'lf': 18, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `cc117d90b498b32b11a886f279b359da16a73c3b01efbb2f5cc004b20262334e`

Source bytes: `10832`; source SHA-256 `cc117d90b498b32b11a886f279b359da16a73c3b01efbb2f5cc004b20262334e`; line endings: `{'crlf': 0, 'lf': 201, 'cr': 0}`; ends with LF: `true`.

```text
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

Copyright 2017 quininer kel

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Body `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`

Source bytes: `11358`; source SHA-256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`; line endings: `{'crlf': 0, 'lf': 202, 'cr': 0}`; ends with LF: `true`.

```text

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
```

### Body `d1fc1bc0d155df60b2e7705b6b2ae02a05c96f948e1cec6e2fb86360b09f346b`

Source bytes: `1582`; source SHA-256 `d1fc1bc0d155df60b2e7705b6b2ae02a05c96f948e1cec6e2fb86360b09f346b`; line endings: `{'crlf': 0, 'lf': 29, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2016-2017 Isis Agora Lovecruft, Henry de Valence. All rights reserved.
Copyright (c) 2016-2024 Isis Agora Lovecruft. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
```

### Body `d5b9c11d6cc93e6ffc28197564a15c7a2f50209317c02810f96b34bf24a17d11`

Source bytes: `1067`; source SHA-256 `d5b9c11d6cc93e6ffc28197564a15c7a2f50209317c02810f96b34bf24a17d11`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `d5fca2653c88ad02d197faead77e22b80c70636b5bec6e02f2805f389a21b86d`

Source bytes: `345`; source SHA-256 `d5fca2653c88ad02d197faead77e22b80c70636b5bec6e02f2805f389a21b86d`; line endings: `{'crlf': 0, 'lf': 9, 'cr': 0}`; ends with LF: `false`.

```text
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
```

### Body `da28ccc6b158fc2d8cccc74e99794b1cff1d29bd7bbeb019442fcf0c04c6cad9`

Source bytes: `1059`; source SHA-256 `da28ccc6b158fc2d8cccc74e99794b1cff1d29bd7bbeb019442fcf0c04c6cad9`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `dc91f8200e4b2a1f9261035d4c18c33c246911a6c0f7b543d75347e61b249cff`

Source bytes: `1059`; source SHA-256 `dc91f8200e4b2a1f9261035d4c18c33c246911a6c0f7b543d75347e61b249cff`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2017 http-rs authors

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
```

### Body `e0cfa1006a64520633de6bfbf563f5b1bea04ef0c5b73f049681931fa297dda3`

Source bytes: `1066`; source SHA-256 `e0cfa1006a64520633de6bfbf563f5b1bea04ef0c5b73f049681931fa297dda3`; line endings: `{'crlf': 0, 'lf': 19, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `e20fa2b8e0a2565f24a792b94b4bf4b6c2b9d36f781d8a9516e218a036e6677a`

Source bytes: `1056`; source SHA-256 `e20fa2b8e0a2565f24a792b94b4bf4b6c2b9d36f781d8a9516e218a036e6677a`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2017 quininer kel

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
```

### Body `e271993808fec50ab29350b39539cdec611a9103f827e0aa26d61da70e2d33f8`

Source bytes: `2371`; source SHA-256 `e271993808fec50ab29350b39539cdec611a9103f827e0aa26d61da70e2d33f8`; line endings: `{'crlf': 0, 'lf': 61, 'cr': 0}`; ends with LF: `true`.

```text
# Community Data License Agreement - Permissive - Version 2.0

This is the Community Data License Agreement - Permissive, Version
2.0 (the "agreement"). Data Provider(s) and Data Recipient(s) agree
as follows:

## 1. Provision of the Data

1.1. A Data Recipient may use, modify, and share the Data made
available by Data Provider(s) under this agreement if that Data
Recipient follows the terms of this agreement.

1.2. This agreement does not impose any restriction on a Data
Recipient's use, modification, or sharing of any portions of the
Data that are in the public domain or that may be used, modified,
or shared under any other legal exception or limitation.

## 2. Conditions for Sharing Data

2.1. A Data Recipient may share Data, with or without modifications, so
long as the Data Recipient makes available the text of this agreement
with the shared Data.

## 3. No Restrictions on Results

3.1. This agreement does not impose any restriction or obligations
with respect to the use, modification, or sharing of Results.

## 4. No Warranty; Limitation of Liability

4.1. All Data Recipients receive the Data subject to the following
terms:

THE DATA IS PROVIDED ON AN "AS IS" BASIS, WITHOUT REPRESENTATIONS,
WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESS OR IMPLIED
INCLUDING, WITHOUT LIMITATION, ANY WARRANTIES OR CONDITIONS OF TITLE,
NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.

NO DATA PROVIDER SHALL HAVE ANY LIABILITY FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING
WITHOUT LIMITATION LOST PROFITS), HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE DATA OR RESULTS,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

## 5. Definitions

5.1. "Data" means the material received by a Data Recipient under
this agreement.

5.2. "Data Provider" means any person who is the source of Data
provided under this agreement and in reliance on a Data Recipient's
agreement to its terms.

5.3. "Data Recipient" means any person who receives Data directly
or indirectly from a Data Provider and agrees to the terms of this
agreement.

5.4. "Results" means any outcome obtained by computational analysis
of Data, including for example machine learning models and models'
insights.
```

### Body `e4c9b06fa850cb9b540a5e400e9f6394cf15efcf4098144de477d1d3dae10150`

Source bytes: `1052`; source SHA-256 `e4c9b06fa850cb9b540a5e400e9f6394cf15efcf4098144de477d1d3dae10150`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `ea084a2373ebc1f0902c09266e7bf25a05ab3814c1805bb017ffa7308f90c061`

Source bytes: `1072`; source SHA-256 `ea084a2373ebc1f0902c09266e7bf25a05ab3814c1805bb017ffa7308f90c061`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055`

Source bytes: `1049`; source SHA-256 `ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `f025ccfb7dfb6bdfedc75ca0f67acc69e6fb4998143d834f7c2f38a29989680f`

Source bytes: `731`; source SHA-256 `f025ccfb7dfb6bdfedc75ca0f67acc69e6fb4998143d834f7c2f38a29989680f`; line endings: `{'crlf': 0, 'lf': 13, 'cr': 0}`; ends with LF: `true`.

```text
Copyright 2015-2025 Brian Smith.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

### Body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

Source bytes: `2195`; source SHA-256 `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`; line endings: `{'crlf': 0, 'lf': 46, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7`

Source bytes: `1071`; source SHA-256 `f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `f790cc576999f5998c766d3d26d7d64dc368e805a98461484f65e8d961ec6d9f`

Source bytes: `1082`; source SHA-256 `f790cc576999f5998c766d3d26d7d64dc368e805a98461484f65e8d961ec6d9f`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1`

Source bytes: `1995`; source SHA-256 `f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1`; line endings: `{'crlf': 0, 'lf': 39, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `f858d5fab15f87699a92876e78d7699a92bdb116b57bf64bf6778c374b5cb0fe`

Source bytes: `1975`; source SHA-256 `f858d5fab15f87699a92876e78d7699a92bdb116b57bf64bf6778c374b5cb0fe`; line endings: `{'crlf': 0, 'lf': 37, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `f98e09091d5ae02b2f2ec1ead4f7f28c4c44d1cb98b078739ba67091637e170c`

Source bytes: `1075`; source SHA-256 `f98e09091d5ae02b2f2ec1ead4f7f28c4c44d1cb98b078739ba67091637e170c`; line endings: `{'crlf': 0, 'lf': 21, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `fa226a5c235dafc28fc9303b03f6bf5f7483c31d8355a031ebd6963ffeb65b95`

Source bytes: `1085`; source SHA-256 `fa226a5c235dafc28fc9303b03f6bf5f7483c31d8355a031ebd6963ffeb65b95`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
Copyright (c) 2019 Aetf <aetf at unlimitedcodeworks dot xyz>

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
```

### Body `fb77f0a9c53e473abe5103c8632ef9f0f2874d4fb3f17cb2d8c661aab9cee9d7`

Source bytes: `1097`; source SHA-256 `fb77f0a9c53e473abe5103c8632ef9f0f2874d4fb3f17cb2d8c661aab9cee9d7`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

### Body `fd80a26fbb3f644af1fa994134446702932968519797227e07a1368dea80f0bc`

Source bytes: `1023`; source SHA-256 `fd80a26fbb3f644af1fa994134446702932968519797227e07a1368dea80f0bc`; line endings: `{'crlf': 0, 'lf': 5, 'cr': 0}`; ends with LF: `true`.

```text
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

### Body `ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2`

Source bytes: `1060`; source SHA-256 `ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2`; line endings: `{'crlf': 0, 'lf': 25, 'cr': 0}`; ends with LF: `true`.

```text
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
```

## Occurrence attribution index

- `ahash 0.8.12` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `ahash 0.8.12` / `LICENSE-MIT` -> body `0444c6991eead6822f7b9102e654448d51624431119546492e8b231db42c48bb` (1057 source bytes)
- `aho-corasick 1.1.5` / `COPYING` -> body `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f` (126 source bytes)
- `aho-corasick 1.1.5` / `LICENSE-MIT` -> body `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f` (1081 source bytes)
- `aho-corasick 1.1.5` / `UNLICENSE` -> body `7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c` (1211 source bytes)
- `allocator-api2 0.2.21` / `LICENSE-APACHE` -> body `20fe7b00e904ed690e3b9fd6073784d3fc428141dbd10b81c01fd143d0797f58` (9899 source bytes)
- `allocator-api2 0.2.21` / `LICENSE-MIT` -> body `36516aefdc84c5d5a1e7485425913a22dbda69eb1930c5e84d6ae4972b5194b9` (1046 source bytes)
- `anyhow 1.0.104` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `anyhow 1.0.104` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `arrayvec 0.7.8` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `arrayvec 0.7.8` / `LICENSE-MIT` -> body `4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871` (1071 source bytes)
- `atomic-waker 1.1.2` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `atomic-waker 1.1.2` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `atomic-waker 1.1.2` / `LICENSE-THIRD-PARTY` -> body `6226d0632e2e1a80c23597e964da9812ae193c535fe058154afb034e94167aa5` (1849 source bytes)
- `attribute-derive 0.10.5` / `LICENSE-APACHE` -> body `abf8f3253498c07abb340315b01c73c2151f9f2a5622ea0b44bd8cadfa34072a` (11357 source bytes)
- `attribute-derive 0.10.5` / `LICENSE-MIT` -> body `562c625100a5ee635f35de5908c206b7d8783e4dcd10ede1c90e4c0e7dddfe5f` (1075 source bytes)
- `attribute-derive-macro 0.10.5` / `LICENSE` -> body `7b273685779bddaafd4c83040dc25fe8c747b73d21f894741df9065609abdff9` (1075 source bytes)
- `autocfg 1.5.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `autocfg 1.5.1` / `LICENSE-MIT` -> body `27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac` (1054 source bytes)
- `base64 0.22.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `base64 0.22.1` / `LICENSE-MIT` -> body `0dd882e53de11566d50f8e8e2d5a651bcf3fabee4987d70f306233cf39094ba7` (1076 source bytes)
- `bit-set 0.8.0` / `LICENSE-APACHE` -> body `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90` (10850 source bytes)
- `bit-set 0.8.0` / `LICENSE-MIT` -> body `f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7` (1071 source bytes)
- `bit-vec 0.8.0` / `LICENSE-APACHE` -> body `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90` (10850 source bytes)
- `bit-vec 0.8.0` / `LICENSE-MIT` -> body `f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7` (1071 source bytes)
- `bitflags 2.13.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `bitflags 2.13.1` / `LICENSE-MIT` -> body `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` (1071 source bytes)
- `bitvec 1.1.1` / `LICENSE.txt` -> body `411781fd38700f2357a14126d0ab048164ab881f1dcb335c1bb932e232c9a2f5` (1082 source bytes)
- `bstr 1.13.1` / `COPYING` -> body `68653aaa727a2bfa31b7a751e31701ce33c49d695c12dd291a07d1c54da4c14b` (262 source bytes)
- `bstr 1.13.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `bstr 1.13.1` / `LICENSE-MIT` -> body `6b7374c39a57e57fc2c38eb529c4c88340152b10f51dd5ae2d819dfa67f61715` (1086 source bytes)
- `byteorder 1.5.0` / `COPYING` -> body `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f` (126 source bytes)
- `byteorder 1.5.0` / `LICENSE-MIT` -> body `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f` (1081 source bytes)
- `byteorder 1.5.0` / `UNLICENSE` -> body `7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c` (1211 source bytes)
- `bytes 1.12.1` / `LICENSE` -> body `45f522cacecb1023856e46df79ca625dfc550c94910078bd8aec6e02880b3d42` (1055 source bytes)
- `castaway 0.2.4` / `LICENSE` -> body `f98e09091d5ae02b2f2ec1ead4f7f28c4c44d1cb98b078739ba67091637e170c` (1075 source bytes)
- `cc 1.4.2` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `cc 1.4.2` / `LICENSE-MIT` -> body `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397` (1057 source bytes)
- `cfg-if 1.0.4` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `cfg-if 1.0.4` / `LICENSE-MIT` -> body `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397` (1057 source bytes)
- `chrono 0.4.45` / `LICENSE.txt` -> body `946c9835d8034d24404f8cfec5f4654cee5dad17e944afc3d06d742cf2882831` (12307 source bytes)
- `cobs 0.3.0` / `LICENSE-APACHE` -> body `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08` (11358 source bytes)
- `cobs 0.3.0` / `LICENSE-MIT` -> body `e0cfa1006a64520633de6bfbf563f5b1bea04ef0c5b73f049681931fa297dda3` (1066 source bytes)
- `collection_literals 1.0.3` / `LICENSE` -> body `4db045835f216d50e0ac5bc3742ddd91756257a8c96578f9f98545d58a1237df` (1075 source bytes)
- `compact_str 0.9.0` / `LICENSE` -> body `0d52feec79589df30138dad3800323fe5686b764b73347330a2dfef8ac83efe8` (1073 source bytes)
- `convert_case 0.10.0` / `LICENSE` -> body `aed7b1758e35afa0cd0fde059d61950747ca11cd0e5e169cb21c11608daed772` (1062 source bytes)
- `core-foundation-sys 0.8.7` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `core-foundation-sys 0.8.7` / `LICENSE-MIT` -> body `62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3` (1067 source bytes)
- `crossterm 0.29.0` / `LICENSE` -> body `aca4760f2a5eba9ce9d4448fe7cd3fcf98245a8315ede59ebd0c6085dd542e61` (1083 source bytes)
- `darling 0.24.1` / `LICENSE` -> body `8ea93490d74a5a1b1af3ff71d786271b3f1e5f0bea79ac16e02ec533cef040d6` (1067 source bytes)
- `darling_core 0.24.1` / `LICENSE` -> body `8ea93490d74a5a1b1af3ff71d786271b3f1e5f0bea79ac16e02ec533cef040d6` (1067 source bytes)
- `darling_macro 0.24.1` / `LICENSE` -> body `8ea93490d74a5a1b1af3ff71d786271b3f1e5f0bea79ac16e02ec533cef040d6` (1067 source bytes)
- `derive-where 1.6.1` / `LICENSE-APACHE` -> body `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` (11358 source bytes)
- `derive-where 1.6.1` / `LICENSE-MIT` -> body `937230c05b5673fe216dda49dfc7c96591c63d0ea4c029e3e1b84aef3a45cbfd` (1075 source bytes)
- `derive_more 2.1.1` / `LICENSE` -> body `8a35369f3ca263b3c62fbb5032947e53b6bfebc6c8a4d1bb982de1c069f6fba5` (1080 source bytes)
- `derive_more-impl 2.1.1` / `LICENSE` -> body `8a35369f3ca263b3c62fbb5032947e53b6bfebc6c8a4d1bb982de1c069f6fba5` (1080 source bytes)
- `displaydoc 0.2.7` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `displaydoc 0.2.7` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `document-features 0.2.12` / `LICENSE-APACHE` -> body `074e6e32c86a4c0ef8b3ed25b721ca23aca83df277cd88106ef7177c354615ff` (10280 source bytes)
- `document-features 0.2.12` / `LICENSE-MIT` -> body `aa893340d14b9844625be6a50ac644169a01b52f0211cbf81b09e1874c8cd81d` (1082 source bytes)
- `either 1.17.0` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `either 1.17.0` / `LICENSE-MIT` -> body `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545` (1043 source bytes)
- `equivalent 1.0.2` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `equivalent 1.0.2` / `LICENSE-MIT` -> body `7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349` (1049 source bytes)
- `errno 0.3.14` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `errno 0.3.14` / `LICENSE-MIT` -> body `8764a597675778ddfd4e25f81b08a05dbcf089ac05662df7613fe67f150e3aa2` (1054 source bytes)
- `fancy-regex 0.17.0` / `AUTHORS` -> body `d5fca2653c88ad02d197faead77e22b80c70636b5bec6e02f2805f389a21b86d` (345 source bytes)
- `fancy-regex 0.17.0` / `LICENSE` -> body `3bc70e239e91272782006c638fc0452a714d384224f11f0923036b7be07cf9b5` (1081 source bytes)
- `find-msvc-tools 0.1.10` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `find-msvc-tools 0.1.10` / `LICENSE-MIT` -> body `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397` (1057 source bytes)
- `foldhash 0.2.0` / `LICENSE` -> body `b1181a40b2a7b25cf66fd01481713bc1005df082c53ef73e851e55071b102744` (856 source bytes)
- `form_urlencoded 1.2.2` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `form_urlencoded 1.2.2` / `LICENSE-MIT` -> body `20c7855c364d57ea4c97889a5e8d98470a9952dade37bd9248b9a54431670e5e` (1072 source bytes)
- `fs2 0.4.3` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `fs2 0.4.3` / `LICENSE-MIT` -> body `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0` (1071 source bytes)
- `funty 2.0.0` / `LICENSE.txt` -> body `f790cc576999f5998c766d3d26d7d64dc368e805a98461484f65e8d961ec6d9f` (1082 source bytes)
- `futures-channel 0.3.34` / `LICENSE-APACHE` -> body `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427` (10874 source bytes)
- `futures-channel 0.3.34` / `LICENSE-MIT` -> body `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd` (1094 source bytes)
- `futures-core 0.3.34` / `LICENSE-APACHE` -> body `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427` (10874 source bytes)
- `futures-core 0.3.34` / `LICENSE-MIT` -> body `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd` (1094 source bytes)
- `futures-io 0.3.34` / `LICENSE-APACHE` -> body `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427` (10874 source bytes)
- `futures-io 0.3.34` / `LICENSE-MIT` -> body `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd` (1094 source bytes)
- `futures-sink 0.3.34` / `LICENSE-APACHE` -> body `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427` (10874 source bytes)
- `futures-sink 0.3.34` / `LICENSE-MIT` -> body `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd` (1094 source bytes)
- `futures-task 0.3.34` / `LICENSE-APACHE` -> body `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427` (10874 source bytes)
- `futures-task 0.3.34` / `LICENSE-MIT` -> body `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd` (1094 source bytes)
- `futures-util 0.3.34` / `LICENSE-APACHE` -> body `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427` (10874 source bytes)
- `futures-util 0.3.34` / `LICENSE-MIT` -> body `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd` (1094 source bytes)
- `get-size-derive2 0.10.3` / `LICENSE` -> body `d5b9c11d6cc93e6ffc28197564a15c7a2f50209317c02810f96b34bf24a17d11` (1067 source bytes)
- `get-size2 0.10.1` / `LICENSE` -> body `013ca8b1499479ce162f0d68ff25f4ac0a98dae625d55a8eabfb1fb4aa38933d` (1082 source bytes)
- `getopts 0.2.24` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `getopts 0.2.24` / `LICENSE-MIT` -> body `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` (1071 source bytes)
- `getrandom 0.2.17` / `LICENSE-APACHE` -> body `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf` (10849 source bytes)
- `getrandom 0.2.17` / `LICENSE-MIT` -> body `42fa16951ce7f24b5a467a40e5b449a1d41e662f97ca779864f053f39e097737` (1130 source bytes)
- `getrandom 0.3.4` / `LICENSE-APACHE` -> body `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf` (10849 source bytes)
- `getrandom 0.3.4` / `LICENSE-MIT` -> body `29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4` (1130 source bytes)
- `hash32 0.2.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `hash32 0.2.1` / `LICENSE-MIT` -> body `c986bcdb83103d4ddf58aeb7b5302359782e54dc4eea14a0cc27c62dcbd50729` (1058 source bytes)
- `hashbrown 0.16.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `hashbrown 0.16.1` / `LICENSE-MIT` -> body `ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2` (1060 source bytes)
- `hashbrown 0.17.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `hashbrown 0.17.1` / `LICENSE-MIT` -> body `ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2` (1060 source bytes)
- `heapless 0.7.17` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `heapless 0.7.17` / `LICENSE-MIT` -> body `035e70219855119df4273b3c5b97543ae82e0dd60c520416e759107c602f651b` (1058 source bytes)
- `heck 0.5.0` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `heck 0.5.0` / `LICENSE-MIT` -> body `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0` (1071 source bytes)
- `http 1.5.0` / `LICENSE-APACHE` -> body `8bb1b50b0e5c9399ae33bd35fab2769010fa6c14e8860c729a52295d84896b7a` (10835 source bytes)
- `http 1.5.0` / `LICENSE-MIT` -> body `dc91f8200e4b2a1f9261035d4c18c33c246911a6c0f7b543d75347e61b249cff` (1059 source bytes)
- `http-body 1.1.0` / `LICENSE` -> body `248378d0a3383c173fb925f17141b88e71580b3ba17ddc6ac3d2a344683232ab` (1083 source bytes)
- `http-body-util 0.1.5` / `LICENSE` -> body `248378d0a3383c173fb925f17141b88e71580b3ba17ddc6ac3d2a344683232ab` (1083 source bytes)
- `httparse 1.10.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `httparse 1.10.1` / `LICENSE-MIT` -> body `391a5396cec6230bfabd4ef4eb2350eb895bc5efce377a2218f5702ed020d3e3` (1063 source bytes)
- `hyper 1.11.1` / `LICENSE` -> body `2d01890414494742ba4a509fcec8efa40f6d8be22cbd72be7cff08d6fda4ec89` (1062 source bytes)
- `hyper-rustls 0.27.9` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `hyper-rustls 0.27.9` / `LICENSE-ISC` -> body `7cfafc877eccc46c0e346ccbaa5c51bb6b894d2b818e617d970211e232785ad4` (775 source bytes)
- `hyper-rustls 0.27.9` / `LICENSE-MIT` -> body `709e3175b4212f7b13aa93971c9f62ff8c69ec45ad8c6532a7e0c41d7a7d6f8c` (1082 source bytes)
- `hyper-util 0.1.20` / `LICENSE` -> body `9e0a97848ea543aef745c98e84fde696a9a3e0735538f6daefdd3cb1942effc1` (1062 source bytes)
- `iana-time-zone 0.1.65` / `LICENSE-APACHE` -> body `696759d65dfe558ff7d9f031c76db19ec5c0767470fb67c4e8d990820d1e99c9` (10832 source bytes)
- `iana-time-zone 0.1.65` / `LICENSE-MIT` -> body `da28ccc6b158fc2d8cccc74e99794b1cff1d29bd7bbeb019442fcf0c04c6cad9` (1059 source bytes)
- `icu_collections 2.2.0` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `icu_locale_core 2.2.0` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `icu_normalizer 2.2.0` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `icu_normalizer_data 2.2.0` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `icu_properties 2.2.0` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `icu_properties_data 2.2.0` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `icu_provider 2.2.0` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `ident_case 1.0.1` / `LICENSE` -> body `508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1` (1036 source bytes)
- `idna 1.1.0` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `idna 1.1.0` / `LICENSE-MIT` -> body `b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5` (1072 source bytes)
- `idna_adapter 1.2.2` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `idna_adapter 1.2.2` / `LICENSE-MIT` -> body `8b43ce8accd61e9d370b5ca9e9c4f953279b5c239926c62315b40e24df51b726` (1062 source bytes)
- `indexmap 2.14.0` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `indexmap 2.14.0` / `LICENSE-MIT` -> body `ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055` (1049 source bytes)
- `indoc 2.0.7` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `indoc 2.0.7` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `instability 0.3.13` / `LICENSE.md` -> body `0352320d9929e862c1f07b59caacc3cd1bbacfec0ad4136bf4c89d4ca8939781` (1114 source bytes)
- `interpolator 0.5.0` / `LICENSE-APACHE` -> body `abf8f3253498c07abb340315b01c73c2151f9f2a5622ea0b44bd8cadfa34072a` (11357 source bytes)
- `interpolator 0.5.0` / `LICENSE-MIT` -> body `23d6f253d73a884498c6979c2d94f9aeaeb9d244557729b7706a332c16bce2f1` (1075 source bytes)
- `ipnet 2.12.2` / `LICENSE-APACHE` -> body `87d9feb9238c6bd8e0024fc4733b06cff036f89f36d93b7df1c8a0549bbb7a5b` (11352 source bytes)
- `ipnet 2.12.2` / `LICENSE-MIT` -> body `47dc9ff29128ddfb4d6a0435383c9f89120bc374dbcc1dd00b933a0b28aa7865` (1062 source bytes)
- `is-macro 0.3.7` / `LICENSE` -> body `58d1e17ffe5109a7ae296caafcadfdbe6a7d176f0bc4ab01e12a689b0499d8bd` (11357 source bytes)
- `itertools 0.14.0` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `itertools 0.14.0` / `LICENSE-MIT` -> body `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545` (1043 source bytes)
- `itertools 0.15.0` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `itertools 0.15.0` / `LICENSE-MIT` -> body `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545` (1043 source bytes)
- `itoa 1.0.18` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `itoa 1.0.18` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `jiter 0.16.0` / `LICENSE` -> body `7c7134b9f7b978c03fca875517cf398db91f19bbb8109b6685e742aa3f57468e` (1091 source bytes)
- `kasuari 0.4.12` / `LICENSE-APACHE` -> body `000b4962e6b27176a0ff89cce4be555b16472cafb5671eb2804a8fdac6854793` (11357 source bytes)
- `kasuari 0.4.12` / `LICENSE-MIT` -> body `74a7056189235b49336669da4e67ad1b315de4ed17e93df751f48c3fab403812` (1109 source bytes)
- `lexical-parse-float 1.0.6` / `LICENSE-APACHE` -> body `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90` (10850 source bytes)
- `lexical-parse-float 1.0.6` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `lexical-parse-float 1.0.6` / `LICENSE.md` -> body `99aab70a96f3ecab683d8a319d9070af2213ae4c1601fb053fbe85e1361e32fe` (19251 source bytes)
- `lexical-parse-integer 1.0.6` / `LICENSE-APACHE` -> body `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90` (10850 source bytes)
- `lexical-parse-integer 1.0.6` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `lexical-parse-integer 1.0.6` / `LICENSE.md` -> body `99aab70a96f3ecab683d8a319d9070af2213ae4c1601fb053fbe85e1361e32fe` (19251 source bytes)
- `lexical-util 1.0.7` / `LICENSE-APACHE` -> body `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90` (10850 source bytes)
- `lexical-util 1.0.7` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `libc 0.2.189` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `libc 0.2.189` / `LICENSE-MIT` -> body `123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e` (1066 source bytes)
- `libm 0.2.16` / `LICENSE.txt` -> body `3823dda7cf046602f4b4e77ec8e227863dc4736037cc85bb33d9f19febe16bb7` (14088 source bytes)
- `line-clipping 0.3.8` / `LICENSE-APACHE` -> body `86f2767527a034d6b9cb8bd98676925e58ed75bf805d234dc2a71a54150cbad1` (11343 source bytes)
- `line-clipping 0.3.8` / `LICENSE-MIT` -> body `520a93f9b172b4c8d2a7ab6f0da1f5f987eba7270ab64a02972095cd87df7fc4` (1070 source bytes)
- `linux-raw-sys 0.12.1` / `COPYRIGHT` -> body `3290ae0fbc9ddb77d2239121d710f0bb9d31b3b4744e6d97fe01e652b4c1870b` (881 source bytes)
- `linux-raw-sys 0.12.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `linux-raw-sys 0.12.1` / `LICENSE-Apache-2.0_WITH_LLVM-exception` -> body `268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5` (12243 source bytes)
- `linux-raw-sys 0.12.1` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `litemap 0.8.2` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `litrs 1.0.0` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `litrs 1.0.0` / `LICENSE-MIT` -> body `7dc1552e88f49132cb358b1b962fc5e79fa42d70bcbb88c526d33e45b8e98036` (1062 source bytes)
- `lock_api 0.4.14` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `lock_api 0.4.14` / `LICENSE-MIT` -> body `c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5` (1071 source bytes)
- `log 0.4.33` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `log 0.4.33` / `LICENSE-MIT` -> body `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` (1071 source bytes)
- `lru 0.18.2` / `LICENSE` -> body `061dc50af2cd9340703daf61978af3200cf681b12ea67a323c33ba109a23a45e` (1071 source bytes)
- `manyhow 0.11.4` / `LICENSE-APACHE` -> body `abf8f3253498c07abb340315b01c73c2151f9f2a5622ea0b44bd8cadfa34072a` (11357 source bytes)
- `manyhow 0.11.4` / `LICENSE-MIT` -> body `23d6f253d73a884498c6979c2d94f9aeaeb9d244557729b7706a332c16bce2f1` (1075 source bytes)
- `manyhow-macros 0.11.4` / `LICENSE` -> body `7b273685779bddaafd4c83040dc25fe8c747b73d21f894741df9065609abdff9` (1075 source bytes)
- `memchr 2.8.3` / `COPYING` -> body `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f` (126 source bytes)
- `memchr 2.8.3` / `LICENSE-MIT` -> body `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f` (1081 source bytes)
- `memchr 2.8.3` / `UNLICENSE` -> body `7e12e5df4bae12cb21581ba157ced20e1986a0508dd10d0e8a4ab9a4cf94e85c` (1211 source bytes)
- `memmap2 0.9.11` / `LICENSE-APACHE` -> body `04ea4849dba9dcae07113850c6f1b1a69052c625210639914eee352023f750ad` (10835 source bytes)
- `memmap2 0.9.11` / `LICENSE-MIT` -> body `0d25d03b5ab49576178ad0cae7a2648d12c17ad0452fe49c07e55e4b59aa5257` (1091 source bytes)
- `mio 1.2.2` / `LICENSE` -> body `07919255c7e04793d8ea760d6c2ce32d19f9ff02bdbdde3ce90b1e1880929a9b` (1082 source bytes)
- `num-bigint 0.4.8` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `num-bigint 0.4.8` / `LICENSE-MIT` -> body `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` (1071 source bytes)
- `num-integer 0.1.46` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `num-integer 0.1.46` / `LICENSE-MIT` -> body `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` (1071 source bytes)
- `num-traits 0.2.19` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `num-traits 0.2.19` / `LICENSE-MIT` -> body `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` (1071 source bytes)
- `once_cell 1.21.4` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `once_cell 1.21.4` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `ordermap 1.2.0` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `ordermap 1.2.0` / `LICENSE-MIT` -> body `ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055` (1049 source bytes)
- `parking_lot 0.12.5` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `parking_lot 0.12.5` / `LICENSE-MIT` -> body `c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5` (1071 source bytes)
- `parking_lot_core 0.9.12` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `parking_lot_core 0.9.12` / `LICENSE-MIT` -> body `c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5` (1071 source bytes)
- `percent-encoding 2.3.2` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `percent-encoding 2.3.2` / `LICENSE-MIT` -> body `b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5` (1072 source bytes)
- `phf 0.11.3` / `LICENSE` -> body `0ab4d106b6faac07fb6a051815fd1b4d862d730895e2d7d7358c2f13565e7a38` (1099 source bytes)
- `phf_codegen 0.11.3` / `LICENSE` -> body `0ab4d106b6faac07fb6a051815fd1b4d862d730895e2d7d7358c2f13565e7a38` (1099 source bytes)
- `phf_generator 0.11.3` / `LICENSE` -> body `0ab4d106b6faac07fb6a051815fd1b4d862d730895e2d7d7358c2f13565e7a38` (1099 source bytes)
- `phf_shared 0.11.3` / `LICENSE` -> body `0ab4d106b6faac07fb6a051815fd1b4d862d730895e2d7d7358c2f13565e7a38` (1099 source bytes)
- `pin-project-lite 0.2.17` / `LICENSE-APACHE` -> body `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594` (10174 source bytes)
- `pin-project-lite 0.2.17` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `postcard 1.1.3` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `postcard 1.1.3` / `LICENSE-MIT` -> body `177540cad091a40e8071db310bc3b6115c4e329a92a234609b60c154b008a888` (1063 source bytes)
- `potential_utf 0.1.5` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `ppv-lite86 0.2.21` / `LICENSE-APACHE` -> body `0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a` (10854 source bytes)
- `ppv-lite86 0.2.21` / `LICENSE-MIT` -> body `4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f` (1076 source bytes)
- `proc-macro-utils 0.10.0` / `LICENSE-APACHE` -> body `abf8f3253498c07abb340315b01c73c2151f9f2a5622ea0b44bd8cadfa34072a` (11357 source bytes)
- `proc-macro-utils 0.10.0` / `LICENSE-MIT` -> body `23d6f253d73a884498c6979c2d94f9aeaeb9d244557729b7706a332c16bce2f1` (1075 source bytes)
- `proc-macro2 1.0.107` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `proc-macro2 1.0.107` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `quote 1.0.47` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `quote 1.0.47` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `radium 0.7.0` / `LICENSE.txt` -> body `13f4cc9fbc8d4a447b28aa84019c10ad4abf4b5f6919db061bf6690ccc23bc02` (1079 source bytes)
- `rand 0.8.7` / `COPYRIGHT` -> body `90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5` (569 source bytes)
- `rand 0.8.7` / `LICENSE-APACHE` -> body `35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab` (9724 source bytes)
- `rand 0.8.7` / `LICENSE-MIT` -> body `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b` (1117 source bytes)
- `rand_chacha 0.3.1` / `COPYRIGHT` -> body `90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5` (569 source bytes)
- `rand_chacha 0.3.1` / `LICENSE-APACHE` -> body `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf` (10849 source bytes)
- `rand_chacha 0.3.1` / `LICENSE-MIT` -> body `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b` (1117 source bytes)
- `rand_core 0.6.4` / `COPYRIGHT` -> body `90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5` (569 source bytes)
- `rand_core 0.6.4` / `LICENSE-APACHE` -> body `6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51` (10282 source bytes)
- `rand_core 0.6.4` / `LICENSE-MIT` -> body `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b` (1117 source bytes)
- `ratatui 0.30.2` / `LICENSE` -> body `50eb43e8d742c9c61a9391e42b2184fce54dbd1893a1bb1c85b8c9ee217ab1f5` (1132 source bytes)
- `ratatui-core 0.1.2` / `LICENSE` -> body `50eb43e8d742c9c61a9391e42b2184fce54dbd1893a1bb1c85b8c9ee217ab1f5` (1132 source bytes)
- `ratatui-crossterm 0.1.2` / `LICENSE` -> body `50eb43e8d742c9c61a9391e42b2184fce54dbd1893a1bb1c85b8c9ee217ab1f5` (1132 source bytes)
- `ratatui-widgets 0.3.2` / `LICENSE` -> body `50eb43e8d742c9c61a9391e42b2184fce54dbd1893a1bb1c85b8c9ee217ab1f5` (1132 source bytes)
- `regex 1.13.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `regex 1.13.1` / `LICENSE-MIT` -> body `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` (1071 source bytes)
- `regex-automata 0.4.18` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `regex-automata 0.4.18` / `LICENSE-MIT` -> body `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` (1071 source bytes)
- `regex-syntax 0.8.11` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `regex-syntax 0.8.11` / `LICENSE-MIT` -> body `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb` (1071 source bytes)
- `regex-syntax 0.8.11` / `src/unicode_tables/LICENSE-UNICODE` -> body `74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3` (2847 source bytes)
- `reqwest 0.12.28` / `LICENSE-APACHE` -> body `751963a8b88c0e3a9f27e98933079fbcf09b9998b2c13ac49c2e4d58444520d6` (10833 source bytes)
- `reqwest 0.12.28` / `LICENSE-MIT` -> body `47d4e1803702728e03d30f8a848ae2249ba274bbd9f8443e803f7924d83cd371` (1063 source bytes)
- `ring 0.17.14` / `LICENSE` -> body `b3d734001a94efff3579978d953391aa7115f877657d25eb54037a43875d078a` (499 source bytes)
- `ring 0.17.14` / `LICENSE-BoringSSL` -> body `005fc765ddc5115da796cca915baa9557abae13ff35e0a47c47affc56f6c414d` (14870 source bytes)
- `ring 0.17.14` / `LICENSE-other-bits` -> body `f025ccfb7dfb6bdfedc75ca0f67acc69e6fb4998143d834f7c2f38a29989680f` (731 source bytes)
- `ring 0.17.14` / `src/polyfill/once_cell/LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `ring 0.17.14` / `src/polyfill/once_cell/LICENSE-MIT` -> body `6ee2ed6c77710de911761acd5fc1ad1da00f476beb1a7ef27e78c2d1858deafc` (1022 source bytes)
- `ring 0.17.14` / `third_party/fiat/LICENSE` -> body `9eacbcb81be660840c714a560a9d65ba07913db98dd4baf969f78dd499fdd60f` (638 source bytes)
- `rustc-hash 2.1.3` / `LICENSE-APACHE` -> body `95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc` (9722 source bytes)
- `rustc-hash 2.1.3` / `LICENSE-MIT` -> body `30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652` (1022 source bytes)
- `rustc_version 0.4.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `rustc_version 0.4.1` / `LICENSE-MIT` -> body `c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5` (1071 source bytes)
- `rustix 1.1.4` / `COPYRIGHT` -> body `377c2e7c53250cc5905c0b0532d35973392af16ffb9596a41d99d202cf3617c9` (853 source bytes)
- `rustix 1.1.4` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `rustix 1.1.4` / `LICENSE-Apache-2.0_WITH_LLVM-exception` -> body `268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5` (12243 source bytes)
- `rustix 1.1.4` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `rustls 0.23.45` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `rustls 0.23.45` / `LICENSE-ISC` -> body `7cfafc877eccc46c0e346ccbaa5c51bb6b894d2b818e617d970211e232785ad4` (775 source bytes)
- `rustls 0.23.45` / `LICENSE-MIT` -> body `709e3175b4212f7b13aa93971c9f62ff8c69ec45ad8c6532a7e0c41d7a7d6f8c` (1082 source bytes)
- `rustls-pki-types 1.15.1` / `LICENSE-APACHE` -> body `45fd05c4865e7c350b98ad7ac50e1b15462d49af4a91e9b0c9dd933dc9a69742` (10835 source bytes)
- `rustls-pki-types 1.15.1` / `LICENSE-MIT` -> body `9117d922e667125508dde62b02c1f57ed22f5ad21eb536aa2e2d99e1c796e639` (1080 source bytes)
- `rustls-webpki 0.103.15` / `LICENSE` -> body `5b698ca13897be3afdb7174256fa1574f8c6892b8bea1a66dd6469d3fe27885a` (916 source bytes)
- `rustversion 1.0.23` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `rustversion 1.0.23` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `ryu 1.0.23` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `ryu 1.0.23` / `LICENSE-BOOST` -> body `c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566` (1338 source bytes)
- `scopeguard 1.2.0` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `scopeguard 1.2.0` / `LICENSE-MIT` -> body `fb77f0a9c53e473abe5103c8632ef9f0f2874d4fb3f17cb2d8c661aab9cee9d7` (1097 source bytes)
- `semver 1.0.28` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `semver 1.0.28` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `serde 1.0.229` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `serde 1.0.229` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `serde_core 1.0.229` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `serde_core 1.0.229` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `serde_derive 1.0.229` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `serde_derive 1.0.229` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `serde_json 1.0.151` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `serde_json 1.0.151` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `serde_spanned 1.1.1` / `LICENSE-APACHE` -> body `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08` (11358 source bytes)
- `serde_spanned 1.1.1` / `LICENSE-MIT` -> body `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6` (1062 source bytes)
- `serde_urlencoded 0.7.1` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `serde_urlencoded 0.7.1` / `LICENSE-MIT` -> body `b9eb266294324f672cbe945fe8f2e32f85024f0d61a1a7d14382cdde0ac44769` (1058 source bytes)
- `serde_yaml 0.9.34+deprecated` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `serde_yaml 0.9.34+deprecated` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `shlex 1.3.0` / `LICENSE-APACHE` -> body `553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583` (566 source bytes)
- `shlex 1.3.0` / `LICENSE-MIT` -> body `4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1` (1092 source bytes)
- `shlex 2.0.1` / `LICENSE-APACHE` -> body `553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583` (566 source bytes)
- `shlex 2.0.1` / `LICENSE-MIT` -> body `4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1` (1092 source bytes)
- `signal-hook 0.3.18` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `signal-hook 0.3.18` / `LICENSE-MIT` -> body `503558bfefe66ca15e4e3f7955b3cb0ec87fd52f29bf24b336af7bd00e946d5c` (1068 source bytes)
- `signal-hook-mio 0.2.5` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `signal-hook-mio 0.2.5` / `LICENSE-MIT` -> body `503558bfefe66ca15e4e3f7955b3cb0ec87fd52f29bf24b336af7bd00e946d5c` (1068 source bytes)
- `signal-hook-registry 1.4.8` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `signal-hook-registry 1.4.8` / `LICENSE-MIT` -> body `503558bfefe66ca15e4e3f7955b3cb0ec87fd52f29bf24b336af7bd00e946d5c` (1068 source bytes)
- `siphasher 1.0.3` / `COPYING` -> body `c962ee4d1d05ddc138b202b2540219ebc57893fcf97b364852094a9a94ce1365` (281 source bytes)
- `slab 0.4.12` / `LICENSE` -> body `8ce0830173fdac609dfb4ea603fdc002c2f4af0dc9b1a005653f5da9cf534b18` (1055 source bytes)
- `smallvec 1.15.2` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `smallvec 1.15.2` / `LICENSE-MIT` -> body `0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9` (1072 source bytes)
- `socket2 0.6.5` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `socket2 0.6.5` / `LICENSE-MIT` -> body `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397` (1057 source bytes)
- `speedate 0.17.0` / `LICENSE` -> body `2afdd30d54b4d62b6f488a6bcc1546e84ec5061f13f4209c03d012348783795a` (1080 source bytes)
- `spin 0.9.9` / `LICENSE` -> body `6ac8711fb340c62ce0a4ecd463342d3fa0e8e70de697c863a2e1c0c53006003c` (1084 source bytes)
- `stable_deref_trait 1.2.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `stable_deref_trait 1.2.1` / `LICENSE-MIT` -> body `5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7` (1056 source bytes)
- `static_assertions 1.1.0` / `LICENSE-APACHE` -> body `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` (11358 source bytes)
- `static_assertions 1.1.0` / `LICENSE-MIT` -> body `ea084a2373ebc1f0902c09266e7bf25a05ab3814c1805bb017ffa7308f90c061` (1072 source bytes)
- `strip-ansi-escapes 0.2.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `strip-ansi-escapes 0.2.1` / `LICENSE-MIT` -> body `1418fdabd96762bb5892098a229061f07dd624245687fd0a95ef33f3feb845a0` (1051 source bytes)
- `strsim 0.11.1` / `LICENSE` -> body `1e697ce8d21401fbf1bddd9b5c3fd4c4c79ae1e3bdf51f81761c85e11d5a89cd` (1166 source bytes)
- `strum 0.27.2` / `LICENSE` -> body `8bce3b45e49ecd1461f223b46de133d8f62cd39f745cfdaf81bee554b908bd42` (1072 source bytes)
- `strum 0.28.0` / `LICENSE` -> body `8bce3b45e49ecd1461f223b46de133d8f62cd39f745cfdaf81bee554b908bd42` (1072 source bytes)
- `strum_macros 0.27.2` / `LICENSE` -> body `8bce3b45e49ecd1461f223b46de133d8f62cd39f745cfdaf81bee554b908bd42` (1072 source bytes)
- `strum_macros 0.28.0` / `LICENSE` -> body `8bce3b45e49ecd1461f223b46de133d8f62cd39f745cfdaf81bee554b908bd42` (1072 source bytes)
- `subtle 2.6.1` / `LICENSE` -> body `d1fc1bc0d155df60b2e7705b6b2ae02a05c96f948e1cec6e2fb86360b09f346b` (1582 source bytes)
- `syn 2.0.119` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `syn 2.0.119` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `syn 3.0.3` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `syn 3.0.3` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `sync_wrapper 1.0.2` / `LICENSE` -> body `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594` (10174 source bytes)
- `synstructure 0.13.2` / `LICENSE` -> body `219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59` (1052 source bytes)
- `tap 1.0.1` / `LICENSE.txt` -> body `8b4e95f5cf0dc40269c99f7b787203ffe04ded245ca2427422c196efa2b2f42a` (1090 source bytes)
- `thin-vec 0.2.19` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `thin-vec 0.2.19` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `thiserror 2.0.20` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `thiserror 2.0.20` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `thiserror-impl 2.0.20` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `thiserror-impl 2.0.20` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `tinystr 0.8.3` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `tinyvec 1.12.0` / `LICENSE-APACHE.md` -> body `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` (11358 source bytes)
- `tinyvec 1.12.0` / `LICENSE-MIT.md` -> body `fd80a26fbb3f644af1fa994134446702932968519797227e07a1368dea80f0bc` (1023 source bytes)
- `tinyvec 1.12.0` / `LICENSE-ZLIB.md` -> body `84b34dd7608f7fb9b17bd588a6bf392bf7de504e2716f024a77d89f1b145a151` (851 source bytes)
- `tinyvec_macros 0.1.1` / `LICENSE-APACHE.md` -> body `4f44572785f35152c1fd2eadf565b7e079c0f300b4324f0af653419f9d76b735` (11350 source bytes)
- `tinyvec_macros 0.1.1` / `LICENSE-MIT.md` -> body `1dd8eca0f83669e75fa119e34fb9e1be9d16e3e9b6368962b8019db6e8ae5f7b` (1062 source bytes)
- `tinyvec_macros 0.1.1` / `LICENSE-ZLIB.md` -> body `41ace205715d9f19a3214218cc1c01d57c533e02cd0fef7c8e51a49a7fce5ac5` (864 source bytes)
- `tokio 1.53.1` / `LICENSE` -> body `253cd04c6714889df2d32f3f64d669179a1c95c76ac43c40882c52eb06bc3552` (1070 source bytes)
- `tokio-rustls 0.26.5` / `LICENSE-APACHE` -> body `cc117d90b498b32b11a886f279b359da16a73c3b01efbb2f5cc004b20262334e` (10832 source bytes)
- `tokio-rustls 0.26.5` / `LICENSE-MIT` -> body `e20fa2b8e0a2565f24a792b94b4bf4b6c2b9d36f781d8a9516e218a036e6677a` (1056 source bytes)
- `toml 0.9.12+spec-1.1.0` / `LICENSE-APACHE` -> body `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08` (11358 source bytes)
- `toml 0.9.12+spec-1.1.0` / `LICENSE-MIT` -> body `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6` (1062 source bytes)
- `toml_datetime 0.7.5+spec-1.1.0` / `LICENSE-APACHE` -> body `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08` (11358 source bytes)
- `toml_datetime 0.7.5+spec-1.1.0` / `LICENSE-MIT` -> body `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6` (1062 source bytes)
- `toml_parser 1.1.3+spec-1.1.0` / `LICENSE-APACHE` -> body `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08` (11358 source bytes)
- `toml_parser 1.1.3+spec-1.1.0` / `LICENSE-MIT` -> body `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6` (1062 source bytes)
- `toml_writer 1.1.2+spec-1.1.0` / `LICENSE-APACHE` -> body `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08` (11358 source bytes)
- `toml_writer 1.1.2+spec-1.1.0` / `LICENSE-MIT` -> body `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6` (1062 source bytes)
- `tower 0.5.3` / `LICENSE` -> body `4249c8e6c5ebb85f97c77e6457c6fafc1066406eb8f1ef61e796fbdc5ff18482` (1062 source bytes)
- `tower-http 0.6.11` / `LICENSE` -> body `5049cf464977eff4b4fcfa7988d84e74116956a3eb9d5f1d451b3f828f945233` (1067 source bytes)
- `tower-layer 0.3.3` / `LICENSE` -> body `4249c8e6c5ebb85f97c77e6457c6fafc1066406eb8f1ef61e796fbdc5ff18482` (1062 source bytes)
- `tower-service 0.3.3` / `LICENSE` -> body `4249c8e6c5ebb85f97c77e6457c6fafc1066406eb8f1ef61e796fbdc5ff18482` (1062 source bytes)
- `tracing 0.1.44` / `LICENSE` -> body `898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1` (1062 source bytes)
- `tracing-core 0.1.36` / `LICENSE` -> body `898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1` (1062 source bytes)
- `tracing-core 0.1.36` / `src/spin/LICENSE` -> body `58545fed1565e42d687aecec6897d35c6d37ccb71479a137c0deb2203e125c79` (1085 source bytes)
- `try-lock 0.2.5` / `LICENSE` -> body `c816a0749cdc6bf062a5111c159723de51b2bfac66a1dac2655abd9e6b1583eb` (1096 source bytes)
- `unicode-general-category 1.1.0` / `LICENSE` -> body `b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1` (11357 source bytes)
- `unicode-ident 1.0.24` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `unicode-ident 1.0.24` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `unicode-ident 1.0.24` / `LICENSE-UNICODE` -> body `f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1` (1995 source bytes)
- `unicode-normalization 0.1.25` / `COPYRIGHT` -> body `23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d` (321 source bytes)
- `unicode-normalization 0.1.25` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `unicode-normalization 0.1.25` / `LICENSE-MIT` -> body `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0` (1071 source bytes)
- `unicode-segmentation 1.13.3` / `COPYRIGHT` -> body `23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d` (321 source bytes)
- `unicode-segmentation 1.13.3` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `unicode-segmentation 1.13.3` / `LICENSE-MIT` -> body `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0` (1071 source bytes)
- `unicode-truncate 2.0.1` / `COPYRIGHT` -> body `23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d` (321 source bytes)
- `unicode-truncate 2.0.1` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `unicode-truncate 2.0.1` / `LICENSE-MIT` -> body `fa226a5c235dafc28fc9303b03f6bf5f7483c31d8355a031ebd6963ffeb65b95` (1085 source bytes)
- `unicode-width 0.2.2` / `COPYRIGHT` -> body `23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d` (321 source bytes)
- `unicode-width 0.2.2` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `unicode-width 0.2.2` / `LICENSE-MIT` -> body `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0` (1071 source bytes)
- `unicode_names2 1.3.0` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `unicode_names2 1.3.0` / `LICENSE-MIT` -> body `6d3a9431e65e69c73a8923e6517b889d17549b23db406b9ec027710d16af701f` (1054 source bytes)
- `unicode_names2 1.3.0` / `data/LICENSE-UNICODE` -> body `f858d5fab15f87699a92876e78d7699a92bdb116b57bf64bf6778c374b5cb0fe` (1975 source bytes)
- `unicode_names2_generator 1.3.0` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `unicode_names2_generator 1.3.0` / `LICENSE-MIT` -> body `6d3a9431e65e69c73a8923e6517b889d17549b23db406b9ec027710d16af701f` (1054 source bytes)
- `unsafe-libyaml 0.2.11` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)
- `untrusted 0.9.0` / `LICENSE.txt` -> body `7abd9b6960dcf7d4d0a48606a5b71bfe37d472db68d70637f3a58a56785f1621` (769 source bytes)
- `url 2.5.8` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `url 2.5.8` / `LICENSE-MIT` -> body `b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5` (1072 source bytes)
- `utf8_iter 1.0.4` / `COPYRIGHT` -> body `c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c` (1742 source bytes)
- `utf8_iter 1.0.4` / `LICENSE-APACHE` -> body `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` (11358 source bytes)
- `utf8_iter 1.0.4` / `LICENSE-MIT` -> body `3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c` (1053 source bytes)
- `version_check 0.9.5` / `LICENSE-APACHE` -> body `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2` (10847 source bytes)
- `version_check 0.9.5` / `LICENSE-MIT` -> body `b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e` (1085 source bytes)
- `vte 0.14.1` / `LICENSE-APACHE` -> body `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a` (9723 source bytes)
- `vte 0.14.1` / `LICENSE-MIT` -> body `e4c9b06fa850cb9b540a5e400e9f6394cf15efcf4098144de477d1d3dae10150` (1052 source bytes)
- `want 0.3.1` / `LICENSE` -> body `a65f5d0a945d267751344c95665945b90c030ea107faf5c85d518929886187da` (1063 source bytes)
- `webpki-roots 1.0.9` / `LICENSE` -> body `e271993808fec50ab29350b39539cdec611a9103f827e0aa26d61da70e2d33f8` (2371 source bytes)
- `winnow 0.7.15` / `LICENSE-MIT` -> body `cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d` (1023 source bytes)
- `winnow 1.0.4` / `LICENSE-MIT` -> body `cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d` (1023 source bytes)
- `writeable 0.6.3` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `wyz 0.5.1` / `LICENSE.txt` -> body `411781fd38700f2357a14126d0ab048164ab881f1dcb335c1bb932e232c9a2f5` (1082 source bytes)
- `yoke 0.8.3` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `yoke-derive 0.8.2` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `zerocopy 0.8.56` / `LICENSE-APACHE` -> body `9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3` (11350 source bytes)
- `zerocopy 0.8.56` / `LICENSE-BSD` -> body `83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32` (1275 source bytes)
- `zerocopy 0.8.56` / `LICENSE-MIT` -> body `1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df` (1060 source bytes)
- `zerofrom 0.1.8` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `zerofrom-derive 0.1.7` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `zeroize 1.9.0` / `LICENSE-APACHE` -> body `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` (11358 source bytes)
- `zeroize 1.9.0` / `LICENSE-MIT` -> body `8c7516d4b27b1e495be5e38b612298b63de48d05f49cdac94f70f3cd70f8864b` (1082 source bytes)
- `zerotrie 0.2.4` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `zerovec 0.11.6` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `zerovec-derive 0.11.3` / `LICENSE` -> body `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2` (2195 source bytes)
- `zmij 1.0.23` / `LICENSE-MIT` -> body `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3` (1023 source bytes)

## Historical supplemental attributions (not current-scope evidence)

The full former root notice is retained unchanged at [release/historical/THIRD-PARTY-NOTICES-pre-v0.1.17.md](release/historical/THIRD-PARTY-NOTICES-pre-v0.1.17.md).
Original SHA-256: `393cfd092b543059d376b96134e7dadf2da5e2f5e76df84d9edbca42d22f62d2`. It contains historical scope/binding claims, not current ones.
The following header, marker, embedded, supplemental, and font records are carried forward verbatim
from that historical artifact. Named-file inventory does not supersede these attributions.
They have NOT been re-audited as current or complete. Historical package/version/path labels are preserved.
Their historical exact-byte claims are not new source verification claims. Current named-file normalization
rules above do not reinterpret these frozen historical renderings.

<a id="additive-text-069e8f08ced4cdfc06f3c5002eaee86f93adc622bf9f8e23b65e16890bb82df3"></a>
#### Additive text `069e8f08ced4cdfc06f3c5002eaee86f93adc622bf9f8e23b65e16890bb82df3`
- SHA-256: `069e8f08ced4cdfc06f3c5002eaee86f93adc622bf9f8e23b65e16890bb82df3`
- Exact source bytes: `110`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/crossterm@0.29.0 — `examples/README.md:29-33` (legal_header_or_marker)
`````text

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.

`````

<a id="additive-text-0f14a7e78f0a0d41b5e294e97313487d904863edc3e764a131cbfa48aef09c9b"></a>
#### Additive text `0f14a7e78f0a0d41b5e294e97313487d904863edc3e764a131cbfa48aef09c9b`
- SHA-256: `0f14a7e78f0a0d41b5e294e97313487d904863edc3e764a131cbfa48aef09c9b`
- Exact source bytes: `997`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/unicode-truncate@2.0.1 — `src/lib.rs:1-25` (legal_header_or_marker)
`````text
// Copyright 2019 Aetf <aetf at unlimitedcodeworks dot xyz>.
// See the COPYRIGHT file at the top-level directory of this distribution.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

#![forbid(missing_docs, unsafe_code)]
#![warn(clippy::arithmetic_side_effects)]
#![cfg_attr(not(feature = "std"), no_std)]

//! Unicode-aware algorithm to pad or truncate `str` in terms of displayed width.
//!
//! See the [`UnicodeTruncateStr`](crate::UnicodeTruncateStr) trait for new methods available on
//! `str`.
//!
//! # Examples
//! Safely truncate string to display width even not at character boundaries.
//! ```rust
//! use unicode_truncate::UnicodeTruncateStr;
//! assert_eq!("你好吗".unicode_truncate(5), ("你好", 4));
//! ```
#![cfg_attr(
`````

<a id="additive-text-120c57e0add48a1808ae07248bbeca7432cd8dcfbf146dc9d50b3df3b8b1e932"></a>
#### Additive text `120c57e0add48a1808ae07248bbeca7432cd8dcfbf146dc9d50b3df3b8b1e932`
- SHA-256: `120c57e0add48a1808ae07248bbeca7432cd8dcfbf146dc9d50b3df3b8b1e932`
- Exact source bytes: `710`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/derive_more@2.1.1 — `src/as_dyn_error.rs:1-16` (legal_header_or_marker)
`````text
//! Coercion into `dyn `[`Error`] used in macro expansions.
//!
//! # Credits
//!
//! The initial idea and implementation was taken from the [`thiserror`] crate and its
//! [`AsDynError`] trait implementation, and slightly modified for usage in derive [`derive_more`].
//!
//! The original code was dual licensed under [Apache License, Version 2.0][APACHE] and [MIT]
//! licenses.
//!
//! [`AsDynError`]: https://github.com/dtolnay/thiserror/blob/2.0.3/src/aserror.rs
//! [`derive_more`]: crate
//! [`thiserror`]: https://github.com/dtolnay/thiserror/blob/2.0.3
//! [APACHE]: https://github.com/dtolnay/thiserror/blob/2.0.3/LICENSE-APACHE
//! [MIT]: https://github.com/dtolnay/thiserror/blob/2.0.3/LICENSE-MIT

`````

<a id="additive-text-1223e80ad7a671ed238694a18ba9e80064bbd3e68115a5bf82d1cd32d131be2b"></a>
#### Additive text `1223e80ad7a671ed238694a18ba9e80064bbd3e68115a5bf82d1cd32d131be2b`
- SHA-256: `1223e80ad7a671ed238694a18ba9e80064bbd3e68115a5bf82d1cd32d131be2b`
- Exact source bytes: `73`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/indoc@2.0.7 — `README.md:148-148` (legal_header_or_marker)
  - pkg:cargo/serde_yaml@0.9.34+deprecated — `README.md:142-142` (legal_header_or_marker)
`````text
Licensed under either of <a href="LICENSE-APACHE">Apache License, Version
`````

<a id="additive-text-13005416a669c7cd96ef8501bfd202d3e6faa7953354c94915c43d0808a2dc7a"></a>
#### Additive text `13005416a669c7cd96ef8501bfd202d3e6faa7953354c94915c43d0808a2dc7a`
- SHA-256: `13005416a669c7cd96ef8501bfd202d3e6faa7953354c94915c43d0808a2dc7a`
- Exact source bytes: `604`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/errno@0.3.14 — `src/unix.rs:1-14` (legal_header_or_marker)
`````text
//! Implementation of `errno` functionality for Unix systems.
//!
//! Adapted from `src/libstd/sys/unix/os.rs` in the Rust distribution.

// Copyright 2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

`````

<a id="additive-text-158f757f25df2225eec072072423a3990b55b7d7a9cbb522553ac7aaccbdeb86"></a>
#### Additive text `158f757f25df2225eec072072423a3990b55b7d7a9cbb522553ac7aaccbdeb86`
- SHA-256: `158f757f25df2225eec072072423a3990b55b7d7a9cbb522553ac7aaccbdeb86`
- Exact source bytes: `96`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/instability@0.3.13 — `README.md:48-52` (legal_header_or_marker)
`````text

## License

This project's source code and documentation are licensed under the MIT [License].

`````

<a id="additive-text-19b716ccede4037997c01142956af7341b0981e7acccff6b75b5bcfa0dc26253"></a>
#### Additive text `19b716ccede4037997c01142956af7341b0981e7acccff6b75b5bcfa0dc26253`
- SHA-256: `19b716ccede4037997c01142956af7341b0981e7acccff6b75b5bcfa0dc26253`
- Exact source bytes: `234`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/signal-hook@0.3.18 — `README.md:55-62` (legal_header_or_marker)
`````text

## License

Licensed under either of

 * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

`````

<a id="additive-text-1b25bc306fc76a267878d00d3b6e5f9a9a1fef73e76a5ffd22b004e55e917a6d"></a>
#### Additive text `1b25bc306fc76a267878d00d3b6e5f9a9a1fef73e76a5ffd22b004e55e917a6d`
- SHA-256: `1b25bc306fc76a267878d00d3b6e5f9a9a1fef73e76a5ffd22b004e55e917a6d`
- Exact source bytes: `107`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/signal-hook-mio@0.2.5 — `README.md:8-13` (legal_header_or_marker)
  - pkg:cargo/signal-hook-registry@1.4.8 — `README.md:9-14` (legal_header_or_marker)
`````text

## License

Licensed under either of

 * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
`````

<a id="additive-text-1dfeac2b788d56ff9f9e053197e95aeea3a66bbceefed4cced444623c2c1cdd9"></a>
#### Additive text `1dfeac2b788d56ff9f9e053197e95aeea3a66bbceefed4cced444623c2c1cdd9`
- SHA-256: `1dfeac2b788d56ff9f9e053197e95aeea3a66bbceefed4cced444623c2c1cdd9`
- Exact source bytes: `332`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/parking_lot@0.12.5 — `src/condvar.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot@0.12.5 — `src/elision.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot@0.12.5 — `src/fair_mutex.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot@0.12.5 — `src/mutex.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot@0.12.5 — `src/once.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot@0.12.5 — `src/raw_fair_mutex.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot@0.12.5 — `src/raw_mutex.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot@0.12.5 — `src/raw_rwlock.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot@0.12.5 — `src/remutex.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot@0.12.5 — `src/rwlock.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot@0.12.5 — `src/util.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot_core@0.9.12 — `src/spinwait.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot_core@0.9.12 — `src/thread_parker/linux.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot_core@0.9.12 — `src/thread_parker/redox.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot_core@0.9.12 — `src/thread_parker/sgx.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot_core@0.9.12 — `src/thread_parker/wasm_atomic.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot_core@0.9.12 — `src/thread_parker/windows/keyed_event.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot_core@0.9.12 — `src/thread_parker/windows/mod.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot_core@0.9.12 — `src/thread_parker/windows/waitaddress.rs:1-7` (legal_header_or_marker)
  - pkg:cargo/parking_lot_core@0.9.12 — `src/word_lock.rs:1-7` (legal_header_or_marker)
`````text
// Copyright 2016 Amanieu d'Antras
//
// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
// http://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.

`````

<a id="additive-text-1e89802484803214efab94cbb2adc74039abe6575c463a30bd81ee2bb88e8e22"></a>
#### Additive text `1e89802484803214efab94cbb2adc74039abe6575c463a30bd81ee2bb88e8e22`
- SHA-256: `1e89802484803214efab94cbb2adc74039abe6575c463a30bd81ee2bb88e8e22`
- Exact source bytes: `42`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/line-clipping@0.3.8 — `README.md:73-75` (legal_header_or_marker)
`````text

This project is licensed under either of

`````

<a id="additive-text-32cc710e31f555a2c596b18fb5d7f8da009a60225417613d2007166feb802941"></a>
#### Additive text `32cc710e31f555a2c596b18fb5d7f8da009a60225417613d2007166feb802941`
- SHA-256: `32cc710e31f555a2c596b18fb5d7f8da009a60225417613d2007166feb802941`
- Exact source bytes: `553`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/errno@0.3.14 — `src/wasi.rs:1-14` (legal_header_or_marker)
`````text
//! Implementation of `errno` functionality for WASI.
//!
//! Adapted from `unix.rs`.

// Copyright 2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

`````

<a id="additive-text-35b3c60850ca1ec40a5679ab32e4e259dcc22a0ff256d3af65735413e1aa2831"></a>
#### Additive text `35b3c60850ca1ec40a5679ab32e4e259dcc22a0ff256d3af65735413e1aa2831`
- SHA-256: `35b3c60850ca1ec40a5679ab32e4e259dcc22a0ff256d3af65735413e1aa2831`
- Exact source bytes: `2152`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/line-clipping@0.3.8 — `src/lib.rs:1-62` (legal_header_or_marker)
`````text
#![no_std]
//! A Rust crate implementing line and polygon clipping algorithms. See the
//! [documentation](https://docs.rs/line_clipping) for more information. The choice of algorithms is
//! based on the following article which contains a good summary of the options:
//!
//! Matthes D, Drakopoulos V. [Line Clipping in 2D: Overview, Techniques and
//! Algorithms](https://pmc.ncbi.nlm.nih.gov/articles/PMC9605407/). J Imaging. 2022 Oct
//! 17;8(10):286. doi: 10.3390/jimaging8100286. PMID: 36286380; PMCID: PMC9605407.
//!
//! Supports:
//!
//! - [x] [Cohen-Sutherland](crate::cohen_sutherland)
//! - [x] [Sutherland-Hodgman](https://docs.rs/line-clipping/latest/line_clipping/sutherland_hodgman/)
//!   polygon clipping algorithm
//!
//! TODO
//!
//! - [ ] Cyrus-Beck
//! - [ ] Liang-Barsky
//! - [ ] Nicholl-Lee-Nicholl
//! - [ ] More comprehensive testing
//!
//! # Installation
//!
//! ```shell
//! cargo add line-clipping
//! ```
//!
//! # Minimum supported Rust version
//!
//! The crate is built with Rust 1.85 to match the 2024 edition. The MSRV may increase in a
//! future minor release, but will be noted in the changelog.
//!
//! # Usage
//!
//! ```rust
//! use line_clipping::cohen_sutherland::clip_line;
//! use line_clipping::{LineSegment, Point, Window};
//!
//! let line = LineSegment::new(Point::new(-10.0, -10.0), Point::new(20.0, 20.0));
//! let window = Window::new(0.0, 10.0, 0.0, 10.0);
//! let clipped_line = clip_line(line, window);
//! ```
//!
//! # License
//!
//! Copyright (c) Josh McKinney
//!
//! This project is licensed under either of
//!
//! - MIT license ([LICENSE-MIT](LICENSE-MIT) or <http://opensource.org/licenses/MIT>)
//! - Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or <http://www.apache.org/licenses/LICENSE-2.0>)
//!
//! at your option.
//!
//! # Contribution
//!
//! Contributions are welcome! Please open an issue or submit a pull request.
//!
//! Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in
//! the work by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without
//! any additional terms or conditions.
`````

<a id="additive-text-3a8c0376080dd3f8e9f4fd6922a9eca8cba83527da382eb99920a083d10b7965"></a>
#### Additive text `3a8c0376080dd3f8e9f4fd6922a9eca8cba83527da382eb99920a083d10b7965`
- SHA-256: `3a8c0376080dd3f8e9f4fd6922a9eca8cba83527da382eb99920a083d10b7965`
- Exact source bytes: `360`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/parking_lot_core@0.9.12 — `src/util.rs:1-8` (legal_header_or_marker)
`````text
// Copyright 2016 Amanieu d'Antras
//
// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
// http://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.

// Option::unchecked_unwrap
`````

<a id="additive-text-45e5f1fe053af076ce7f26204decb8c301abed7faf5d2638ae06d396be13ffde"></a>
#### Additive text `45e5f1fe053af076ce7f26204decb8c301abed7faf5d2638ae06d396be13ffde`
- SHA-256: `45e5f1fe053af076ce7f26204decb8c301abed7faf5d2638ae06d396be13ffde`
- Exact source bytes: `738`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/unicode-segmentation@1.13.3 — `tests/testdata/mod.rs:1-15` (legal_header_or_marker)
`````text
// Copyright 2012-2018 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

// NOTE: The following code was generated by "scripts/unicode.py", do not edit directly

#![allow(missing_docs, non_upper_case_globals, non_snake_case)]
    // official Unicode test data
    // http://www.unicode.org/Public/17.0.0/ucd/auxiliary/GraphemeBreakTest.txt
`````

<a id="additive-text-46394aa2814fd4911df5c4554be367758cd004d01e8a9d8e815e8d153309cefa"></a>
#### Additive text `46394aa2814fd4911df5c4554be367758cd004d01e8a9d8e815e8d153309cefa`
- SHA-256: `46394aa2814fd4911df5c4554be367758cd004d01e8a9d8e815e8d153309cefa`
- Exact source bytes: `99`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/document-features@0.2.12 — `lib.rs:1-4` (legal_header_or_marker)
`````text
// Copyright © SixtyFPS GmbH <info@sixtyfps.io>
// SPDX-License-Identifier: MIT OR Apache-2.0

/*!
`````

<a id="additive-text-4714de7a3c60c60e5da4f0e2033eacd7fdb99ae56712e749e3dbb1a71bd0f39f"></a>
#### Additive text `4714de7a3c60c60e5da4f0e2033eacd7fdb99ae56712e749e3dbb1a71bd0f39f`
- SHA-256: `4714de7a3c60c60e5da4f0e2033eacd7fdb99ae56712e749e3dbb1a71bd0f39f`
- Exact source bytes: `2013`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/parking_lot_core@0.9.12 — `src/lib.rs:1-42` (legal_header_or_marker)
`````text
// Copyright 2016 Amanieu d'Antras
//
// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
// http://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.

//! This library exposes a low-level API for creating your own efficient
//! synchronization primitives.
//!
//! # The parking lot
//!
//! To keep synchronization primitives small, all thread queuing and suspending
//! functionality is offloaded to the *parking lot*. The idea behind this is based
//! on the Webkit [`WTF::ParkingLot`](https://webkit.org/blog/6161/locking-in-webkit/)
//! class, which essentially consists of a hash table mapping of lock addresses
//! to queues of parked (sleeping) threads. The Webkit parking lot was itself
//! inspired by Linux [futexes](http://man7.org/linux/man-pages/man2/futex.2.html),
//! but it is more powerful since it allows invoking callbacks while holding a
//! queue lock.
//!
//! There are two main operations that can be performed on the parking lot:
//!
//!  - *Parking* refers to suspending the thread while simultaneously enqueuing it
//! on a queue keyed by some address.
//! - *Unparking* refers to dequeuing a thread from a queue keyed by some address
//! and resuming it.
//!
//! See the documentation of the individual functions for more details.
//!
//! # Building custom synchronization primitives
//!
//! Building custom synchronization primitives is very simple since the parking
//! lot takes care of all the hard parts for you. A simple example for a
//! custom primitive would be to integrate a `Mutex` inside another data type.
//! Since a mutex only requires 2 bits, it can share space with other data.
//! For example, one could create an `ArcMutex` type that combines the atomic
//! reference count and the two mutex bits in the same atomic word.

#![warn(missing_docs)]
#![warn(rust_2018_idioms)]
#![cfg_attr(
`````

<a id="additive-text-4b70e343ad6027188cf2768db4f2131136e54070d3dd8d4fdbdca538b797be93"></a>
#### Additive text `4b70e343ad6027188cf2768db4f2131136e54070d3dd8d4fdbdca538b797be93`
- SHA-256: `4b70e343ad6027188cf2768db4f2131136e54070d3dd8d4fdbdca538b797be93`
- Exact source bytes: `41`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/line-clipping@0.3.8 — `README.md:69-73` (legal_header_or_marker)
`````text

## License

Copyright (c) Josh McKinney

`````

<a id="additive-text-4c1678385fd883e974b5d2836a99f051ac5563c0a4b6aa8681b51f1f2d8ddd73"></a>
#### Additive text `4c1678385fd883e974b5d2836a99f051ac5563c0a4b6aa8681b51f1f2d8ddd73`
- SHA-256: `4c1678385fd883e974b5d2836a99f051ac5563c0a4b6aa8681b51f1f2d8ddd73`
- Exact source bytes: `105`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/crossterm@0.29.0 — `README.md:203-203` (legal_header_or_marker)
`````text
`crossterm_input`, `crossterm_terminal`, `crossterm_winapi`, `crossterm_utils` are licensed under the MIT
`````

<a id="additive-text-4e6d7d4db1d3804a01fa937ebbddbfdbca537ed27031683555207c8afb82a47f"></a>
#### Additive text `4e6d7d4db1d3804a01fa937ebbddbfdbca537ed27031683555207c8afb82a47f`
- SHA-256: `4e6d7d4db1d3804a01fa937ebbddbfdbca537ed27031683555207c8afb82a47f`
- Exact source bytes: `444`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/parking_lot_core@0.9.12 — `src/thread_parker/generic.rs:1-10` (legal_header_or_marker)
`````text
// Copyright 2016 Amanieu d'Antras
//
// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
// http://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.

//! A simple spin lock based thread parker. Used on platforms without better
//! parking facilities available.

`````

<a id="additive-text-4ecf8d9fe2410f3ae52b9339697213626c4d754db7fc5335ca8f36f0b1cf7451"></a>
#### Additive text `4ecf8d9fe2410f3ae52b9339697213626c4d754db7fc5335ca8f36f0b1cf7451`
- SHA-256: `4ecf8d9fe2410f3ae52b9339697213626c4d754db7fc5335ca8f36f0b1cf7451`
- Exact source bytes: `2810`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/ratatui-core@0.1.2 — `src/lib.rs:8-76` (legal_header_or_marker)
`````text
//! **ratatui-core** is the core library of the [ratatui] project,
//! providing the essential building blocks for creating rich terminal user interfaces in Rust.
//!
//! [ratatui]: https://github.com/ratatui/ratatui
//!
//! # Why `ratatui-core`?
//!
//! The `ratatui-core` crate is split from the main [`ratatui`](https://crates.io/crates/ratatui)
//! crate to offer better stability for widget library authors and advanced integrations. Widget
//! libraries should generally depend on `ratatui-core`, benefiting from a stable API and reducing
//! the need for frequent updates.
//!
//! Most applications, on the other hand, should depend on the main `ratatui` crate, which
//! includes built-in widgets, backend re-exports, and higher-level setup helpers.
//!
//! In practice:
//!
//! - Use [`ratatui`] to build applications.
//! - Use `ratatui-core` to implement widgets, backend integrations, or other code that needs the
//!   core rendering and layout contracts directly.
//!
//! # Installation
//!
//! Add `ratatui-core` to your `Cargo.toml`:
//!
//! ```shell
//! cargo add ratatui-core
//! ```
//!
//! # Crate Organization
//!
//! `ratatui-core` is part of the Ratatui workspace that was modularized in version 0.30.0 to
//! improve compilation times, API stability, and dependency management. This crate provides the
//! foundational types and traits that other crates in the workspace depend on.
//!
//! **When to use `ratatui-core`:**
//!
//! - Building widget libraries that implement [`Widget`] or [`StatefulWidget`]
//! - Building custom integrations on top of Ratatui's core rendering contracts
//! - You want minimal dependencies and faster compilation times
//! - You need maximum API stability (core types change less frequently)
//!
//! **When to use the main [`ratatui`] crate:**
//!
//! - Building applications
//! - You want built-in widgets, backend re-exports, and setup helpers such as `ratatui::run`
//!
//! For detailed information about the workspace organization, see [ARCHITECTURE.md].
//!
//! [`ratatui`]: https://crates.io/crates/ratatui
//! [`Widget`]: widgets::Widget
//! [`StatefulWidget`]: widgets::StatefulWidget
//! [ARCHITECTURE.md]: https://github.com/ratatui/ratatui/blob/main/ARCHITECTURE.md
#![cfg_attr(feature = "document-features", doc = "\n## Features")]
#![cfg_attr(feature = "document-features", doc = document_features::document_features!())]
//!
//! # Contributing
//!
//! We welcome contributions from the community! Please see our [CONTRIBUTING](../CONTRIBUTING.md)
//! guide for more details on how to get involved.
//!
//! ## License
//!
//! This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

#![warn(clippy::std_instead_of_core)]
#![warn(clippy::std_instead_of_alloc)]
#![warn(clippy::alloc_instead_of_core)]

`````

<a id="additive-text-50ba5e9f3718ea4d21e687bc795903540096d248b1aca0e89abeaab5d12da419"></a>
#### Additive text `50ba5e9f3718ea4d21e687bc795903540096d248b1aca0e89abeaab5d12da419`
- SHA-256: `50ba5e9f3718ea4d21e687bc795903540096d248b1aca0e89abeaab5d12da419`
- Exact source bytes: `72`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/ratatui@0.30.2 — `README.md:135-139` (legal_header_or_marker)
`````text

## License

This project is licensed under the [MIT License][License].

`````

<a id="additive-text-51de09826fd47c91cd1ddcf4186e62274276a2097f8d9e4f80780122cfbbb616"></a>
#### Additive text `51de09826fd47c91cd1ddcf4186e62274276a2097f8d9e4f80780122cfbbb616`
- SHA-256: `51de09826fd47c91cd1ddcf4186e62274276a2097f8d9e4f80780122cfbbb616`
- Exact source bytes: `602`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/errno@0.3.14 — `src/windows.rs:1-14` (legal_header_or_marker)
`````text
//! Implementation of `errno` functionality for Windows.
//!
//! Adapted from `src/libstd/sys/windows/os.rs` in the Rust distribution.

// Copyright 2014 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

`````

<a id="additive-text-5ad1c491be4546efb2ecd7d44a21ee9b193999a525bdadacfdd3ed449914d7f4"></a>
#### Additive text `5ad1c491be4546efb2ecd7d44a21ee9b193999a525bdadacfdd3ed449914d7f4`
- SHA-256: `5ad1c491be4546efb2ecd7d44a21ee9b193999a525bdadacfdd3ed449914d7f4`
- Exact source bytes: `807`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/ident_case@1.0.1 — `src/lib.rs:1-24` (legal_header_or_marker)
`````text
//! Crate for changing case of Rust identifiers.
//!
//! # Features
//! * Supports `snake_case`, `lowercase`, `camelCase`, 
//!   `PascalCase`, `SCREAMING_SNAKE_CASE`, and `kebab-case`
//! * Rename variants, and fields
//! 
//! # Examples
//! ```rust
//! use ident_case::RenameRule;
//!
//! assert_eq!("helloWorld", RenameRule::CamelCase.apply_to_field("hello_world"));
//!
//! assert_eq!("i_love_serde", RenameRule::SnakeCase.apply_to_variant("ILoveSerde"));
//! ```

// Copyright 2017 Serde Developers
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

`````

<a id="additive-text-5b3c730a832b13c43789ce462e24c9d6056d3ca5447807d387e6bbfb8ddea8a8"></a>
#### Additive text `5b3c730a832b13c43789ce462e24c9d6056d3ca5447807d387e6bbfb8ddea8a8`
- SHA-256: `5b3c730a832b13c43789ce462e24c9d6056d3ca5447807d387e6bbfb8ddea8a8`
- Exact source bytes: `256`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/linux-raw-sys@0.12.1 — `ORG_CODE_OF_CONDUCT.md:105-111` (legal_header_or_marker)
  - pkg:cargo/rustix@1.1.4 — `ORG_CODE_OF_CONDUCT.md:105-111` (legal_header_or_marker)
`````text

   * Abide by all applicable open source license terms.  Do not engage
     in copyright violation or misattribution of any kind.

   * Do not claim others' ideas or designs as your own.

   * When others engage in publicly visible work (e.g., an upcoming
`````

<a id="additive-text-626c600aa39a0f4f6623ab22f64bb1720634aa0c7cfb114a7eb8c6657a8272dc"></a>
#### Additive text `626c600aa39a0f4f6623ab22f64bb1720634aa0c7cfb114a7eb8c6657a8272dc`
- SHA-256: `626c600aa39a0f4f6623ab22f64bb1720634aa0c7cfb114a7eb8c6657a8272dc`
- Exact source bytes: `134`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/ratatui-widgets@0.3.2 — `README.md:101-106` (legal_header_or_marker)
`````text

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

<!-- cargo-rdme end -->

`````

<a id="additive-text-724b41a22171ef69e4b9eebb4b7250189518786d636714607153254cf9587ad3"></a>
#### Additive text `724b41a22171ef69e4b9eebb4b7250189518786d636714607153254cf9587ad3`
- SHA-256: `724b41a22171ef69e4b9eebb4b7250189518786d636714607153254cf9587ad3`
- Exact source bytes: `236`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/parking_lot@0.12.5 — `README.md:136-143` (legal_header_or_marker)
`````text

## License

Licensed under either of

 * Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or https://www.apache.org/licenses/LICENSE-2.0)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or https://opensource.org/licenses/MIT)

`````

<a id="additive-text-8f7722ade0ca33094c5507159f2bbd61aeb905904ccdeae943d99dc066d0de6a"></a>
#### Additive text `8f7722ade0ca33094c5507159f2bbd61aeb905904ccdeae943d99dc066d0de6a`
- SHA-256: `8f7722ade0ca33094c5507159f2bbd61aeb905904ccdeae943d99dc066d0de6a`
- Exact source bytes: `135`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/ratatui-core@0.1.2 — `README.md:68-73` (legal_header_or_marker)
`````text

### License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

<!-- cargo-rdme end -->

`````

<a id="additive-text-903fb9aff6d1777a054067b53a00092a74507afc78aaeac3638e27b230c6e796"></a>
#### Additive text `903fb9aff6d1777a054067b53a00092a74507afc78aaeac3638e27b230c6e796`
- SHA-256: `903fb9aff6d1777a054067b53a00092a74507afc78aaeac3638e27b230c6e796`
- Exact source bytes: `331`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/parking_lot_core@0.9.12 — `src/parking_lot.rs:1-6` (legal_header_or_marker)
`````text
// Copyright 2016 Amanieu d'Antras
//
// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
// http://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.
`````

<a id="additive-text-b6adbd1aa47e52ff23227e30ec16807c5a5b8b8bd416394051ca11e776b611ca"></a>
#### Additive text `b6adbd1aa47e52ff23227e30ec16807c5a5b8b8bd416394051ca11e776b611ca`
- SHA-256: `b6adbd1aa47e52ff23227e30ec16807c5a5b8b8bd416394051ca11e776b611ca`
- Exact source bytes: `471`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/unicode-segmentation@1.13.3 — `tests/test.rs:1-10` (legal_header_or_marker)
`````text
// Copyright 2012-2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

`````

<a id="additive-text-ba613b0d9e67912f6891d668edf518d05d15cb5ee8fdd1de563a005be8b97ef4"></a>
#### Additive text `ba613b0d9e67912f6891d668edf518d05d15cb5ee8fdd1de563a005be8b97ef4`
- SHA-256: `ba613b0d9e67912f6891d668edf518d05d15cb5ee8fdd1de563a005be8b97ef4`
- Exact source bytes: `603`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/parking_lot@0.12.5 — `src/lib.rs:1-14` (legal_header_or_marker)
`````text
// Copyright 2016 Amanieu d'Antras
//
// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
// http://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.

//! This library provides implementations of `Mutex`, `RwLock`, `Condvar` and
//! `Once` that are smaller, faster and more flexible than those in the Rust
//! standard library. It also provides a `ReentrantMutex` type.

#![warn(missing_docs)]
#![warn(rust_2018_idioms)]

`````

<a id="additive-text-bb1894d4f828155ddd48971d57724c230ea8d2254c1d8e3a2c85ea020037fe1b"></a>
#### Additive text `bb1894d4f828155ddd48971d57724c230ea8d2254c1d8e3a2c85ea020037fe1b`
- SHA-256: `bb1894d4f828155ddd48971d57724c230ea8d2254c1d8e3a2c85ea020037fe1b`
- Exact source bytes: `364`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/parking_lot_core@0.9.12 — `src/thread_parker/unix.rs:1-8` (legal_header_or_marker)
`````text
// Copyright 2016 Amanieu d'Antras
//
// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
// http://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.

#[cfg(target_vendor = "apple")]
`````

<a id="additive-text-bfd706e1d42a588d1d1037652dd78c2ca612bb5ccaa658be25f001bfccd82355"></a>
#### Additive text `bfd706e1d42a588d1d1037652dd78c2ca612bb5ccaa658be25f001bfccd82355`
- SHA-256: `bfd706e1d42a588d1d1037652dd78c2ca612bb5ccaa658be25f001bfccd82355`
- Exact source bytes: `91`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/litrs@1.0.0 — `README.md:76-81` (legal_header_or_marker)
`````text

---

## License

Licensed under either of <a href="LICENSE-APACHE">Apache License, Version
`````

<a id="additive-text-d0649bc089f9093fbf18ddd2976f64cb85d4bec9ac9658abea392bdc9bf6e723"></a>
#### Additive text `d0649bc089f9093fbf18ddd2976f64cb85d4bec9ac9658abea392bdc9bf6e723`
- SHA-256: `d0649bc089f9093fbf18ddd2976f64cb85d4bec9ac9658abea392bdc9bf6e723`
- Exact source bytes: `1798`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/unicode-segmentation@1.13.3 — `src/lib.rs:1-51` (legal_header_or_marker)
`````text
// Copyright 2012-2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

//! Iterators which split strings on Grapheme Cluster, Word, or Sentence boundaries, according
//! to the [Unicode Standard Annex #29](https://www.unicode.org/reports/tr29/) rules.
//!
//! ```rust
//! use unicode_segmentation::UnicodeSegmentation;
//!
//! fn main() {
//!     let s = "a̐éö̲\r\n";
//!     let g = s.graphemes(true).collect::<Vec<&str>>();
//!     let b: &[_] = &["a̐", "é", "ö̲", "\r\n"];
//!     assert_eq!(g, b);
//!
//!     let s = "The quick (\"brown\") fox can't jump 32.3 feet, right?";
//!     let w = s.unicode_words().collect::<Vec<&str>>();
//!     let b: &[_] = &["The", "quick", "brown", "fox", "can't", "jump", "32.3", "feet", "right"];
//!     assert_eq!(w, b);
//!
//!     let s = "The quick (\"brown\")  fox";
//!     let w = s.split_word_bounds().collect::<Vec<&str>>();
//!     let b: &[_] = &["The", " ", "quick", " ", "(", "\"", "brown", "\"", ")", "  ", "fox"];
//!     assert_eq!(w, b);
//! }
//! ```
//!
//! # no_std
//!
//! unicode-segmentation does not depend on libstd, so it can be used in crates
//! with the `#![no_std]` attribute.
//!
//! # crates.io
//!
//! You can use this package in your project by adding the following
//! to your `Cargo.toml`:
//!
//! ```toml
//! [dependencies]
//! unicode-segmentation = "1"
//! ```

#![deny(missing_docs, unsafe_code)]
#![doc(
`````

<a id="additive-text-d5d52b02158b13096907947e47ee95ca9a628ec0a594c4167c07f03da7292885"></a>
#### Additive text `d5d52b02158b13096907947e47ee95ca9a628ec0a594c4167c07f03da7292885`
- SHA-256: `d5d52b02158b13096907947e47ee95ca9a628ec0a594c4167c07f03da7292885`
- Exact source bytes: `3671`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/ratatui-widgets@0.3.2 — `src/lib.rs:25-110` (legal_header_or_marker)
`````text
//!
//! # Installation
//!
//! Run the following command to add this crate to your project:
//!
//! ```sh
//! cargo add ratatui-widgets
//! ```
//!
//! # Available Widgets
//!
//! - [`BarChart`]: displays multiple datasets as bars with optional grouping.
//! - [`Block`]: a basic widget that draws a block with optional borders, titles, and styles.
//! - [`calendar::Monthly`]: displays a single month.
//! - [`Canvas`]: draws arbitrary shapes using drawing characters.
//! - [`Chart`]: displays multiple datasets as lines or scatter graphs.
//! - [`Clear`]: clears the area it occupies. Useful to render over previously drawn widgets.
//! - [`Fill`]: paints every cell in its area with a single repeated symbol and style.
//! - [`Gauge`]: displays progress percentage using block characters.
//! - [`LineGauge`]: displays progress as a line.
//! - [`List`]: displays a list of items and allows selection.
//! - [`RatatuiLogo`]: displays the Ratatui logo.
//! - [`RatatuiMascot`]: displays the Ratatui mascot.
//! - [`Paragraph`]: displays a paragraph of optionally styled and wrapped text.
//! - [`Scrollbar`]: displays a scrollbar.
//! - [`Sparkline`]: displays a single dataset as a sparkline.
//! - [`Table`]: displays multiple rows and columns in a grid and allows selection.
//! - [`Tabs`]: displays a tab bar and allows selection.
//!
//! [`BarChart`]: crate::barchart::BarChart
//! [`Block`]: crate::block::Block
//! [`calendar::Monthly`]: crate::calendar::Monthly
//! [`Canvas`]: crate::canvas::Canvas
//! [`Chart`]: crate::chart::Chart
//! [`Clear`]: crate::clear::Clear
//! [`Fill`]: crate::fill::Fill
//! [`Gauge`]: crate::gauge::Gauge
//! [`LineGauge`]: crate::gauge::LineGauge
//! [`List`]: crate::list::List
//! [`RatatuiLogo`]: crate::logo::RatatuiLogo
//! [`RatatuiMascot`]: crate::mascot::RatatuiMascot
//! [`Paragraph`]: crate::paragraph::Paragraph
//! [`Scrollbar`]: crate::scrollbar::Scrollbar
//! [`Sparkline`]: crate::sparkline::Sparkline
//! [`Table`]: crate::table::Table
//! [`Tabs`]: crate::tabs::Tabs
//!
//! All these widgets are re-exported directly under `ratatui::widgets` in the `ratatui` crate.
//!
//! # Crate Organization
//!
//! `ratatui-widgets` is part of the Ratatui workspace that was modularized in version 0.30.0.
//! This crate contains all the built-in widget implementations that were previously part of the
//! main `ratatui` crate.
//!
//! **When to use `ratatui-widgets`:**
//!
//! - Building widget libraries that need to compose with built-in widgets
//! - You want finer-grained dependencies and only need specific widgets
//! - Creating custom widgets that extend or wrap the built-in ones
//!
//! **When to use the main [`ratatui`] crate:**
//!
//! - Building applications (recommended - includes everything you need)
//! - You want the convenience of having all widgets available
//!
//! For detailed information about the workspace organization, see [ARCHITECTURE.md].
//!
//! [`ratatui`]: https://crates.io/crates/ratatui
//! [ARCHITECTURE.md]: https://github.com/ratatui/ratatui/blob/main/ARCHITECTURE.md
#![cfg_attr(feature = "document-features", doc = "\n## Features")]
#![cfg_attr(feature = "document-features", doc = document_features::document_features!())]
//!
//! # Contributing
//!
//! Contributions are welcome! Please open an issue or submit a pull request on GitHub. For more
//! details on contributing, please see the [CONTRIBUTING](CONTRIBUTING.md) document.
//!
//! # License
//!
//! This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.

#![warn(clippy::std_instead_of_core)]
#![warn(clippy::std_instead_of_alloc)]
#![warn(clippy::alloc_instead_of_core)]

`````

<a id="additive-text-e140c51df38e78baeefd6964784717ae14063810e71a74e58b5e1c78db42c281"></a>
#### Additive text `e140c51df38e78baeefd6964784717ae14063810e71a74e58b5e1c78db42c281`
- SHA-256: `e140c51df38e78baeefd6964784717ae14063810e71a74e58b5e1c78db42c281`
- Exact source bytes: `465`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/parking_lot_core@0.9.12 — `src/thread_parker/wasm.rs:1-10` (legal_header_or_marker)
`````text
// Copyright 2016 Amanieu d'Antras
//
// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
// http://opensource.org/licenses/MIT>, at your option. This file may not be
// copied, modified, or distributed except according to those terms.

//! The wasm platform can't park when atomic support is not available.
//! So this ThreadParker just panics on any attempt to park.

`````

<a id="additive-text-e24b6c7a1c7fd130a6a236102212e389771cab65469ba0cf167811490abb9571"></a>
#### Additive text `e24b6c7a1c7fd130a6a236102212e389771cab65469ba0cf167811490abb9571`
- SHA-256: `e24b6c7a1c7fd130a6a236102212e389771cab65469ba0cf167811490abb9571`
- Exact source bytes: `731`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/errno@0.3.14 — `src/hermit.rs:1-16` (legal_header_or_marker)
`````text
//! Implementation of `errno` functionality for RustyHermit.
//!
//! Currently, the error handling in RustyHermit isn't clearly
//! defined. At the current stage of RustyHermit, only a placeholder
//! is provided to be compatible to the classical errno interface.

// Copyright 2015 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

`````

<a id="additive-text-effd4a37a9d0d6a1644e56e23acbfedb1ee294044d071fca557fb406049c96d4"></a>
#### Additive text `effd4a37a9d0d6a1644e56e23acbfedb1ee294044d071fca557fb406049c96d4`
- SHA-256: `effd4a37a9d0d6a1644e56e23acbfedb1ee294044d071fca557fb406049c96d4`
- Exact source bytes: `38`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/kasuari@0.4.12 — `README.md:55-59` (legal_header_or_marker)
`````text

## License

Licensed under either of

`````

<a id="additive-text-f3e4452a50490fd9b5f1c5fea4cd3ed45a7ada46f81ddf2dd66bfab28a742b51"></a>
#### Additive text `f3e4452a50490fd9b5f1c5fea4cd3ed45a7ada46f81ddf2dd66bfab28a742b51`
- SHA-256: `f3e4452a50490fd9b5f1c5fea4cd3ed45a7ada46f81ddf2dd66bfab28a742b51`
- Exact source bytes: `471`; encoding: UTF-8; ends with LF: `true`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/unicode-segmentation@1.13.3 — `src/grapheme.rs:1-10` (legal_header_or_marker)
  - pkg:cargo/unicode-segmentation@1.13.3 — `src/sentence.rs:1-10` (legal_header_or_marker)
  - pkg:cargo/unicode-segmentation@1.13.3 — `src/word.rs:1-10` (legal_header_or_marker)
`````text
// Copyright 2012-2014 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

`````

<a id="additive-text-f5583b4941dd55620b6ac36966d065c0008a5bbbb436b36d45d364609843c415"></a>
#### Additive text `f5583b4941dd55620b6ac36966d065c0008a5bbbb436b36d45d364609843c415`
- SHA-256: `f5583b4941dd55620b6ac36966d065c0008a5bbbb436b36d45d364609843c415`
- Exact source bytes: `738`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/unicode-segmentation@1.13.3 — `src/tables.rs:1-16` (legal_header_or_marker)
`````text
// Copyright 2012-2018 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

// NOTE: The following code was generated by "scripts/unicode.py", do not edit directly

#![allow(missing_docs, non_upper_case_globals, non_snake_case)]

/// The version of [Unicode](http://www.unicode.org/)
/// that this version of unicode-segmentation is based on.
`````

<a id="additive-text-ff2ed3a5bc2a6ad00c391e66f05e272aa02f91fb0bc18a8919f638316bea8c17"></a>
#### Additive text `ff2ed3a5bc2a6ad00c391e66f05e272aa02f91fb0bc18a8919f638316bea8c17`
- SHA-256: `ff2ed3a5bc2a6ad00c391e66f05e272aa02f91fb0bc18a8919f638316bea8c17`
- Exact source bytes: `2436`; encoding: UTF-8; ends with LF: `false`
- Kind(s): `legal_header_or_marker`
- Occurrences:
  - pkg:cargo/lru@0.18.2 — `src/lib.rs:1-62` (legal_header_or_marker)
`````text
// MIT License

// Copyright (c) 2016 Jerome Froelich

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

//! An implementation of a LRU cache. The cache supports `get`, `get_mut`, `put`,
//! and `pop` operations, all of which are O(1). This crate was heavily influenced
//! by the [LRU Cache implementation in an earlier version of Rust's std::collections crate](https://doc.rust-lang.org/0.12.0/std/collections/lru_cache/struct.LruCache.html).
//!
//! ## Example
//!
//! ```rust
//! extern crate lru;
//!
//! use lru::LruCache;
//! use std::num::NonZeroUsize;
//!
//! fn main() {
//!         let mut cache = LruCache::new(NonZeroUsize::new(2).unwrap());
//!         cache.put("apple", 3);
//!         cache.put("banana", 2);
//!
//!         assert_eq!(*cache.get(&"apple").unwrap(), 3);
//!         assert_eq!(*cache.get(&"banana").unwrap(), 2);
//!         assert!(cache.get(&"pear").is_none());
//!
//!         assert_eq!(cache.put("banana", 4), Some(2));
//!         assert_eq!(cache.put("pear", 5), None);
//!
//!         assert_eq!(*cache.get(&"pear").unwrap(), 5);
//!         assert_eq!(*cache.get(&"banana").unwrap(), 4);
//!         assert!(cache.get(&"apple").is_none());
//!
//!         {
//!             let v = cache.get_mut(&"banana").unwrap();
//!             *v = 6;
//!         }
//!
//!         assert_eq!(*cache.get(&"banana").unwrap(), 6);
//! }
//! ```

#![no_std]

#[cfg(feature = "hashbrown")]
`````

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

