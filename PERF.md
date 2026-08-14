# Performance ledger

RULER inference rows now retain a fail-closed per-item ledger at
`arm_evidence.performance_ledger` for the `jcode-azdaja` arm. Controls use `null`.
The ledger is normalized from two already-retained authorities:

- `AZDAJA_MODEL_TRACE` v2: physical root/repair turns, inference milliseconds, and observed repair tokens.
- the unique absolute-EOF `solo_runtime` v1 row in `AZDAJA_SOLO_TRACE`: generated-program execs, in-memory checkpoint serialization/restoration, logical child prompts, and gross child-batch wall.

`exec_wall_ms` contains `sub_call_wall_ms`; do not add them. Snapshot fields describe
Monty in-memory `Dump` save/restore, not input-file I/O. Repair token fields are
`null` with `token_accounting_complete=false` if any repair usage is unobserved.
Missing, duplicated, malformed, unbound, partial, or internally inconsistent evidence
produces no normalized ledger and fails an otherwise-successful candidate item.

## Immutable RULER v38 pre-gold baseline

This is an execution/performance baseline only: every score is still `null`, all 270
rows are `deferred`, gold was not opened, and the terminal record marks the frozen
artifacts immutable. Every summary and raw row below is bound to:

- candidate `azdaja 0.1.0 (monty 0.0.21)`, commit `d21ffe70364ffecb74b32996d9addb02c1c7c8`, binary SHA-256 `13fb5030ac1a516519e03c1108fa0e7a577243e356a0c448b759588ca62a5b83`, config `91a35c191f56856d05fb7c9599bd376e01bbd5d4589d128cc81b733b7056d396`, skill `923d8fc81bb19b5c7bb783b8aa9b6dbfbcc9906fe79fa7ed53272fea202fadc3`, frozen directory `01e379c0ecee2784e44896a34319e13c7deac114edee263d2ce9d39672ae6519`;
- controller SHA-256 `d366d5e8ffa21022f9c44f2ae60740624b7a6e3a7281c522d6d304b0ac9c8e07`; schedule ID `5c91d48ba378fbab82092d7ad6e274bde396c699e8a611d42c7cc784cdbe635d`, seed `20260813`, schedule SHA-256 `e899a537f996be9a444be96362759805c03f8eeaed751dfbf11ee84879c2be86`;
- results SHA-256 `7340cf4f2973f1aeb7c79282cc668cba8c5f824f95f055f64af9f88e99ce436f` and superseding terminal-record v2 SHA-256 `b0e70521bd7f7c17ca6acf9cc619f1b7cde9c159992cabd8692b2a9bb4f11501`.

This is an observability/provenance metadata correction, not a measurement change:
terminal-record v2 (`record_revision=2`) supersedes immutable v1 SHA-256
`f22bd13ca6e4512e753e3ab7d78c282decfea2b4a43b31e4d1a9285d02dddb4a`
because v1 truncated `candidate.commit` to 38 characters. The results file and
all recorded measurements are unchanged.

The controller ran serially (`concurrency=1`): its 270 retained start/wall
intervals do not overlap. Full-schedule makespan was `5465.997s`
(`5064.335s` process wall plus `401.662s` controller gaps). With all 90
samples retained, including failures, linear percentiles (`r=(n-1)p`) are:

| Arm | Execution | Failures | Mean s | p50 s | p95 s | p99 s | Serial wall s | vs native |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| jcode-azdaja | 85/90 | 5 | 36.780699 | 32.345822 | 66.954994 | 84.391078 | 3310.262874 | 4.234603x |
| jcode-native | 90/90 | 0 | 8.685748 | 8.083595 | 16.362929 | 17.944990 | 781.717320 | 1.000000x |
| prime-agent | 90/90 | 0 | 10.803941 | 10.112591 | 16.247422 | 18.919009 | 972.354726 | 1.243870x |

The candidate therefore failed both the required `90/90` execution gate and the
`<=1.5x` native speed target. Failures were process exits at ordinals
`110,127,246` and payload-integrity failures at `136,268`; timeouts were zero.

The 90 root turns cost `2752165ms` and `202224/204353/1792`
input/output/cache-read tokens. Twenty items triggered 30 physical repair turns
(10 one-repair, 10 two-repair): `525471ms` and `169843/40070/77312` tokens;
17 repairs succeeded and 13 were rejected. Total observed inference was
`3277636ms`. The remaining `32626.873505ms` of candidate controller wall is
unattributed, **not** measured execution overhead.

### Candidate per-item raw timing ledger (90/90)

`root` and `repair` are `physical-turns/inference-ms/input/output/cache-read`.
The execution tuple is `success/exit-code/failure-kind`. Controller wall is the
unrounded JSON value in seconds. `NA` means unavailable, never zero: v38 predates
the `solo_runtime` instrumentation for generated-program execs, Monty snapshot
save/load, and logical subcalls.

```text
fixture_id|run_id|ordinal|execution|controller_wall_s|root|repair|exec_count/wall_ms|snapshot_save_count/wall_ms|snapshot_load_count/wall_ms|logical_subcall_count/physical_turns/wall_ms
rxm-11dc65da42de7eb3f228e18a2a8eff65|b0b8cdcbf1a9e6cbb9dda128ec48c49c1dab4f4954871209174a93915888e191|2|true/0/-|39.20829145889729|1/38854/2101/2779/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-2ac3ee8a8d478d822a685de2dc0b16a3|ca092e9f69db5afd0413063e58feb6bb1553af405da36e4dfdec5bf9e574251e|5|true/0/-|18.95729791605845|1/18605/2163/1426/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-b7c35f5ffc59bcc55fb7a9bd4c147d8a|1ce8e90ddc77d5fdb2701f37539edf69bfc893feaed0b2b7ac66fdca566ddeba|7|true/0/-|28.58981183404103|1/28250/2167/2189/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-f64b1dac66a8083bbc2f55055b1d0b8d|7c71893a46ace9b02bc6872faec50713682f03ca84549f2704c99a83f6439258|11|true/0/-|33.50514129176736|1/33184/2158/2577/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-b1c9ec3fb0b063ee0e5f09cc126bb8af|026967d701d2396bbacf20426f1d1d5f62adc5c0adb5a99ed7c7462f640cacb5|13|true/0/-|28.54028958408162|1/28194/2103/2215/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-4423687db17d9a31b3a9857c8cd69f30|d517c54d2e84487c267d704e19f6a483ca600a20de5ca06be642f9e09c05c67e|18|true/0/-|34.87073158333078|1/34516/2166/2747/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-acc02b0d850a448f4378d39d6a2ce7ef|f1089e1a17e74c82d8da83e4509522db68c42778b7d30953f37f38ae624047b6|21|true/0/-|27.853683459106833|1/27539/2128/2087/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-9b08f0ffb3aa22def23a06696ca56e29|6d20a7cb523b1fdd1e17850f02927a145122adeba1fcd825ca7d363f05a22bb1|24|true/0/-|23.492255208082497|1/23131/2105/1793/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-7674d536489dcc16b74eb994c3d6be22|ee4ce40c0251f85f805660d6f58f17394b00bb85efb53cf4d211413f432def81|27|true/0/-|64.57053562486544|1/33145/2130/2622/0|2/31070/11629/2432/6656|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-2a38707acfc3c0c0e7899f893226ce48|ea101017afd4e9800fbcdd9ef33276c0194c4abe1668bdb295221234778d377a|29|true/0/-|38.62030070787296|1/38314/2117/2941/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-cd743bd6c18335b9252ef6d24b35f657|8ea68f1700d8fc3e27fba2436bd18b8e5556d975ae3725308db10f29468894f9|31|true/0/-|20.30223650019616|1/19904/2162/1528/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-d495c04874aa74f5d6eb37ac4a1ddb6a|4f783f92a88a0bf6f87ea40ee9abdb2f916a04294cd0c60a3936cea4cfb3f7f5|34|true/0/-|67.02721270825714|1/44061/2128/3496/0|1/22576/6221/1782/1792|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-0a23d4187ba36c082330ce16cb498818|5f4d76d62a6dda4a067e6ce07b0d513afc4758ce3dd8c5005bc23037a2620741|38|true/0/-|26.55172499967739|1/26221/2132/2040/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-00cc544fcda467237ed86a3e160f886a|6667a06d94e550afbe20026ffc4d1896629263c1ed42cc42008d59ac9bdae16c|40|true/0/-|63.1890322919935|1/38011/2130/2987/0|1/24750/5580/1934/1792|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-678ef1c626d33c5e013313b3f302772a|53b2e32cb2bc63d14742c1f1a2e86c72d606b3d10685d9f5c7f0770ee8072efe|43|true/0/-|16.660554124973714|1/16334/2102/1234/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-e03c7bd38bd988d3064422df6da5634c|581fb3063549b9259fe57269910723e5d7b9ab3fe0e0e105e180ad931a758075|46|true/0/-|35.33980849990621|1/35002/2115/2791/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-9fb887de2c04411d2f609857de5a93e3|c2bee9025104085909b32e32198b0b3828cd2fc221051ecc0d179ed607ba3249|50|true/0/-|26.39324912475422|1/26092/2096/2049/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-e1c4ba3a3c32801adc08c7fd8098bc13|6e413f49765b936433d3dc0e002bd514f9de919716a98b4ccc97095e00666ffd|53|true/0/-|63.13439925014973|1/41356/2128/3310/0|1/21425/5867/1713/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-05b3f054f9022a57c4982c211373027b|9c78f85c140eb4001572ccf7b0e1ef49553904e8ec8f33dd1800aff96e0dc992|56|true/0/-|42.26688220910728|1/41912/2127/3359/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-72f0ee174339cf792776e69257ba0b10|fa20a276c887e89ac1d00bb812160dab3ddd0d766927702dd00db4d58f923c22|60|true/0/-|44.218805416021496|1/43907/2128/3529/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-e0c3b4068e96b281e20646323a23aec3|767fa514418e89d760d80bb9157a73991f3625c79923feb43c6cd6378491cade|63|true/0/-|41.06817216705531|1/40752/2101/3225/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-bbb05e22a15882330e2ba524cfb9117c|3d4946ac5dff21bee6a2372aa12f78351236757b20a2f0bfaca3db12165f4c1a|65|true/0/-|34.19338991679251|1/33884/2165/2676/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-4373136e673616983d16863a929238be|df7799adb4f71ea79c300cfc9015a148e058c3ab899ad6e8e49bc148f945974f|67|true/0/-|60.70487287500873|1/21204/2134/1590/0|2/39114/10204/3033/5632|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-f506e348f8c6c230cfda42408614a107|27be45d5eb8c3e960e854dd6479c33d2bf93bd65a0f045549a98ad8f7d3b7515|71|true/0/-|52.35745912510902|1/30119/2134/2381/0|1/21773/5039/1661/1792|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-85460fbeb24a283cd6c3d2dca7732525|e60b63a5c81eb159adaf3c307f29e94f12d73c8e28bef87739ebb2f93616b2ae|73|true/0/-|28.464415917173028|1/28118/2163/2206/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-d5d07eb201619636dc9dad08e1659a1c|91db2af69f45e0c208978302869a56504598ee8b1f5153f4ecfb4ddd22e1331b|76|true/0/-|46.32137062493712|1/27856/2117/2199/0|1/18105/4509/1433/1792|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-5c84c6f447a71c91552a6420ba413286|0399b9e4452b0186e7eeb9088bc8a98bdf0adb793f57793b6f4eccf88c726a6f|80|true/0/-|29.6617932501249|1/29337/2107/2182/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-0638d6b89286a8334b8af333258cf275|979ebb00e7f1989d39977d248da8a1546bd82aab2cac15c1773c527aeff526d1|82|true/0/-|84.21388629218563|1/42904/2127/3443/0|2/40872/14256/3245/7680|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-44cd3a588f0db7c23e48b584dbfcba22|4614da231ded049fcc84fbdea5fa34648f043a490bbcd440fdc938fb23d6326e|87|true/0/-|27.703843916766346|1/27351/2093/2135/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-20717f3b83d7a80648f95e49e6452346|ca9e56b1f475c016574668a4555989a4b661cdcd9b2d8c6d8349bc171eeec6ec|89|true/0/-|28.673214042093605|1/28366/2123/2225/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-97d6b3340ade8a8366690c58dc984f04|643e518f8851bb5b9e047b567e98e03bd5e62c53bb646b9435da2ff5563d24ff|91|true/0/-|32.60739312507212|1/32295/2102/2557/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-aa716efcae763fd39ed01ab48be84b9e|18d6b45864d70218c1160329bbb3b1ae495a7f44c1c0adba6846ea5a0435b70c|96|true/0/-|52.7116329157725|1/52347/2121/3835/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-ff6de54e7de50318c925e9e4e8b95725|4353f38fcd9037aab9d740426f7d6cd6b2498058bde2245a18a5507344fc8823|98|true/0/-|38.59830679092556|1/38268/2167/2896/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-6a55c9a3cbd7eeb6afa3c9a66cb03ac7|3407e8ca46390809b77534f62a861d4a3c891a8e3894380ab30f8b746dbd4c1f|102|true/0/-|23.467614082619548|1/23119/2159/1812/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-696ca05f6cb95bf40b4c3cc50e7df27d|6e7a2ecb0dcb8dd6e4f34a58946e0a68bc0e2263f689982941c6a6f3972f5ccc|103|true/0/-|27.385086458176374|1/27068/2163/2087/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-c2b8d0f327261be1698e75bd8c6c0d30|ee9ba9e34655bf09350fedabecffa14a95d009e7d3d445d3b75d927d94e1f94a|106|true/0/-|16.795513625256717|1/16451/2160/1241/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-1d930dbb1e9ea475815822e3ac16a999|760eb9262f179b5a9e3322a1bb4dc2c71eb93e79e168e34a80bad7d25bb093cf|110|false/2/process_exit|47.13122766697779|1/18619/2128/1216/0|2/28118/9173/2052/1792|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-62b7d00b3215d98eb67fb68eab213d5d|72beb1ea5e07292788380f00c6a87f7091d57206e3294d0f62959757b745b6d2|113|true/0/-|20.340826875064522|1/19885/2129/1247/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-9625d2dc2ada9879a0fac0417d0f5cd0|5e0a96aa9b5ad3213c49352a8302ba06b7c5dacb1e60efd8cce18c42a889ecdb|116|true/0/-|27.572530374862254|1/27130/2164/2036/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-6670e3c89f0a5890a7e589245915d2c9|1a1527b5cf75e6c8d8617362f61663bdf7a6dc701982e55af3f7715f2c6bf54a|119|true/0/-|20.516221000347286|1/20167/2160/1507/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-ce855cef72d552f137b2dae5421c7a65|58ae9671447eee0df0c973c57a9dea221119e08d76e26cc963a8f698bd55db3e|121|true/0/-|32.428516834042966|1/32076/2130/2299/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-b4c99b6ccf597f46a46c66d5e0e6c783|4380366b25215dab14091fbb1122dbe103084faa597a2fdaf8b821d0964ca9a0|126|true/0/-|20.33763787476346|1/19966/2163/1276/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-36f1a95ad7fa5be35e5287bd4d0e19ad|f634cae32cd556edd80a6aabe166ce38a4397f30284205f4d803a78af8a8acff|127|false/2/process_exit|71.54718591598794|1/34214/2128/2641/0|2/36798/12372/2881/6656|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-467b749369c568b10fef3cef5890c348|18b886ea84010c610bd2a580b7718b289815da256e6fb3d362add642dfffd4a0|131|true/0/-|21.73817150015384|1/21383/2125/1317/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-394c2c2f14dee6d218b1eeed55851769|d07e354ca72710c18ea69df253ee38f073a990fb85211fdbc3f350334a03f117|135|true/0/-|51.06236879201606|1/50687/2128/3950/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-0842be47abaf03e7f7608f4e080b7b49|36db37241f644c1c0baf9a621b2e669f1574389a15d77f7a28aafa68e02937f4|136|false/0/payload_integrity|66.86672758311033|1/50860/6969/387/0|1/15640/7627/809/5888|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-d6794247d180991a32cefceb3c9da71d|b675d1dd474ec6979e48e8d6ba1237d7cfcac12c498e3d6e3c204017926003de|141|true/0/-|29.820156374946237|1/29451/2162/2126/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-b658f3106834fc71c464d1b7d486d15d|22c5096e6e0239b2ae4fcfe40a3120add2396369ee2d677b9cce1755a065f40c|144|true/0/-|22.55028658406809|1/22174/2100/1672/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-92486c24fe9645ad376a8334663064d4|fd025be4b5af6067278647ef907af6c4f845477b54169b345e5526c3eff26c33|145|true/0/-|20.30772166699171|1/19954/2158/1253/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-513316fa756fbec5bc68b46dabcca508|0f57604955f60fd004f3088b6f179c9309dd8b611779622a102646e55e460e4e|149|true/0/-|49.21875600004569|1/30362/2128/2142/0|1/18447/4664/1462/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-b792e68b943e9cb8960f6718fcb5b18c|11c6104db99b5c2b3e86e6876ff0fc4f202f33f53b174dd6806951f4b8c5adae|153|true/0/-|24.61047933343798|1/24196/2163/1869/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-dd3082a81a03975c3592e11232929f37|528ef17b6e61d246e8383d88fd75c8e644ce7dda60013fa736413a274276e40c|155|true/0/-|32.26312670810148|1/31898/2128/2526/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-fdf9225059e12fa628eacf7ffb57edb0|af5c8e87a2cd7c2d97a412c84f32fda6e83c330a2e1a222c47566c54caf2e507|158|true/0/-|30.71196408290416|1/30362/2168/2395/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-a4a45cadc62c9cce17d3853f44252b6a|6b573089383d1c289b6edc421a539689939169240fb670ef0e119609b56001c8|161|true/0/-|27.62002274999395|1/27289/2163/2142/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-6aaaa92ec10e5d3eb832d43cbfe21f72|225130d104f5a64056be929f4ac4c37b8ed175ba99928e450c64b5d80610c91c|165|true/0/-|35.17779487511143|1/34837/2158/2780/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-8a82f054dfd748037debb0915961ee1f|70c587c605c7d0c6e479c8a5b9f367d2cf63b3f5c2cc97914d0f285728ac0c12|167|true/0/-|33.06754720909521|1/32721/2130/2597/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-8cd42dfdae310e8e3116abd8fadf8e43|ded94a14b758aca904191f95ab3a05302f54eb54d9b8effd6fdcd6784a9baf72|171|true/0/-|28.909029041882604|1/28504/2161/2247/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-de9e923237d534e4c7b886460687cd8e|9dd8a86efad498029ebc99d7afd8ca38e10dc98710baf88fcdfb7979183eb6fb|173|true/0/-|65.3926197080873|1/23597/2130/1775/0|2/41361/10590/3080/1792|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-4490877cac6c4e6a043ed7d5363fddb7|308a0883217a27bd889fd4f3f64df367b794fadd1804d196605f41bc2505dfa2|177|true/0/-|31.77827512472868|1/31404/2123/2480/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-aa6e6dec8cdf7714bdb3f850b8e6f70a|2903ab69ed8c4d2c41085f3a7a3d38382f35194f76796b1c5c170cedd4218558|180|true/0/-|28.13776420801878|1/27694/2107/2156/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-7e553f265504bc8c6328900d5e533959|3fd0687737894a5a2858b931ea3ecb5804dfda6a690aee39ee929143e8ab085a|183|true/0/-|25.785312624648213|1/25368/2117/1983/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-d2ad2995853a6b197e6a115b15668a11|e65297041f7d55aea340cc72492d181597a149eb632f94efdaca996a3233b079|186|true/0/-|31.06213670829311|1/30584/2117/2400/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-6bcc86e00831e637ea432192fdf22a26|7f6fcaa10a915259e22c1f3b54ad0b73fadc1d2c466b1226facebcc953262448|189|true/0/-|36.13342774985358|1/35766/2163/2836/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-bc97dd2187a1fccd83439692715f8f7b|df9b71ef1683b0363ad28a772198ca10b41902acc50af52bc3d6ab4f3c942abb|192|true/0/-|36.49687858298421|1/22960/2104/1779/0|1/13196/4227/1033/1792|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-4c44beebebf245aa0be46f397be07161|24bb5596ddc5d0f0d624dadcff4440daf4656029f768684b65a04587d421ffd1|194|true/0/-|38.631050874944776|1/38262/2128/3060/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-e6655a1ef981eae35945754b3c70ded3|e3790a458fba21cfda9a62f96188d4c9a1f9b7b9421387f65a74c1b71a36daee|196|true/0/-|27.076489333994687|1/26717/2099/2068/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-660260a9c73d6cceb03a130e2343e9e6|d2a568ef72aee28366d3393cee4abc5ff498c4d9d5c0f700f57a1f67522c6b1c|200|true/0/-|34.80402445793152|1/34441/2114/2733/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-1080d80094d455939714bf7ab97c7f7d|becceb4c2d32af2c7439fa565496d4ab29ed0348a438fc0a27c9a729e4573a05|202|true/0/-|45.91928625013679|1/45563/2128/3665/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-780fd530469c7758d13fdf495ccbfd80|ad9b48ff228495447770d36750431b050dbe0e4942720cc174a03f521120ce2d|207|true/0/-|21.754902542103082|1/21406/2161/1644/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-b983df14cc50958f7526c96c23691119|322064703fde3a79fcf2065cb3df1b995062e83e7816fcc9810407b6b1306968|209|true/0/-|38.11901358421892|1/37760/2093/2986/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-9cdedb73d75162dd2ff1d76b1c78c2d1|932fb2cb67cdfe4c4b225cdfee51387f801b6bfad1e1df75903d310123952650|212|true/0/-|16.18001220887527|1/15841/2165/1161/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-ebdbe17c07b465f7459fee9cd279fa23|44c9570ef728bc20a103ed609008629ad9519ab2ebc5b2fbef786efcd265d84e|214|true/0/-|30.01992466719821|1/29682/2104/2309/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-c009ba1c8b7d4272f68e9dae41417ea3|ced7dcf27544844720f80cf4a799da8f9cd1cbb1d54fa493929ac817197899ea|217|true/0/-|24.98360454197973|1/24641/2129/1813/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-e20d6ea22d20d672212ab69872718e1a|289d76c79fba6ab65ebae7ca6556f9a3ba25b3ea84174026aefed93a87befbb2|220|true/0/-|49.83435641694814|1/29645/2102/2348/0|2/19782/10620/1379/5632|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-1ed71e2bbcc6731fc8c7b90b288180f7|fcf5080291eb747618e1e33c785489f0fc74ea2da74489ff44f3f68936aeed8a|225|true/0/-|26.984700500033796|1/26673/2109/2032/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-33e39318b148eccab837c19f9499d778|eef2e3ce0f7a884d79ffdf1c36cfa4791fcc60763c41c1c879a241e57c2d1a31|228|true/0/-|85.82472066720948|1/49304/2126/3980/0|2/36085/14694/2731/7680|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-324ca4d778d06fbfa4bb504d8147116a|2273a8bcb1cf774d609202aa2de75ad1bc6769ba215669a7054ea87ee3dc63be|229|true/0/-|53.21341312490404|1/34726/2130/2767/0|1/18158/5418/1451/1792|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-2285810b89e4909ccf15581027b173cc|dbd8b7e284ca9ee0e13fb749482516b897b6835d61721519e213d48399354924|232|true/0/-|22.709845874924213|1/22412/2164/1736/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-e435052ac0d44846101adb42725d03da|f7cd500f3f486b58bc2350122da6d920d351c69726feda881f2bc64d4ab11d2c|237|true/0/-|48.353981208987534|1/18598/2096/1408/0|2/29360/8341/2199/4608|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-5e8b3d46a40b66a64f8160799c010e03|5857715338b50e542394f29103c95ad2b9f22c762f1165f469ccac54f0f4ca6a|238|true/0/-|29.45121133280918|1/29116/2158/2282/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-a9a934718ca127c9fb8e13095b737f67|68da8e34a5dad0e1f0c206b1bf12659da1c35a2bdfc2e46d3247f08d8a7360e2|242|true/0/-|22.479322749655694|1/22179/2104/1667/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-d65551bb2a9f71f31f72bdf9e93ebc9f|77829c508ac1b43a282c55b9ded9d56b9d51a57ef34743eb04c817a1909fa11b|246|false/2/process_exit|65.21350079076365|1/30260/2128/2327/0|2/34522/11004/2691/5632|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-3bc09213f6c544834f36affa13797c12|38a77cc95d2f206be12a99f65d4ec2c77438a3c9cb67cde3eb976daa699ebd3f|249|true/0/-|38.11049779225141|1/37799/2128/3002/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-c7ab5cec71d4fe4eb643efcf7cf8fe3e|b776f8e48cc4306a3b4e862c6394832f852e92b41718152407e61ed2f47ef00f|250|true/0/-|19.658752500079572|1/19358/2118/1444/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-46bf52294049cec2e0a353dbbbf86e39|a185bbc75e9ff9925219e425145a712bd91891a9a64f90ebe94abd0295e201d2|255|true/0/-|41.30142637481913|1/40952/2123/3251/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-ca1270b2718d395c274719377f291d6e|8ed6a1d90228b2537cc54cd7a4050a7e3e5c169f6551c52b33dd5d645dcd8743|258|true/0/-|23.1062290831469|1/22757/2165/1741/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-9361854e5de1e01d72c8c549b4006f9e|53468a6341c036b5f6a3568743b3715b46ecbb4b98030e5d045a1f01bc1c5eea|259|true/0/-|30.31615887535736|1/29958/2102/2315/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-8bb56f2f3ed933ca4406053af2eae6fd|dfd894f47ef3f5eb4619a1d5b2fa9e54f0f8e863f4fabd0c137f00f63075dd9c|263|true/0/-|34.627234749961644|1/34278/2162/2528/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-0d5ef27c4cec939ae76718dcfec439f2|4424053f15c0dfc461542771e476d62313a260549ea0d570bc9422650b1fa2bd|265|true/0/-|32.75319058261812|1/32403/2158/2539/0|0/0/0/0/0|NA/NA|NA/NA|NA/NA|NA/NA/NA
rxm-d02947b5b231ac70b75074f91ce46de4|8f5e0ae251e12ef0c6d4b49581cb3761783938cb1ac0876869df1d4c319a3113|268|false/0/payload_integrity|72.0310997501947|1/57355/7604/124/1792|1/14319/7808/1069/6912|NA/NA|NA/NA|NA/NA|NA/NA/NA
```

## Raw local smoke item

This is a non-subscription command-transport smoke, **not a latency benchmark**. It
exists to pin the emitted and normalized schemas without touching the frozen v38 run.
Every number below is bound to:

- candidate: `azdaja 0.1.0 (monty 0.0.21)` debug binary SHA-256 `928dd300bef91945c0f75db2a2896996a49458d58b0733086d8302abc4139a11`
- controller: `bench/ruler/run.py` SHA-256 `500aae5df22e84dbdd05d25dc1870e83ba0cd184ae165b9cb9a41487bc3f1d4a`
- scorer: `bench/ruler/score.py` SHA-256 `1cd3ebd65d38e3bfc8e1f8e4568ee53105d1ca903f6ea7138f68a86e1f69381c`
- item: `local-command-transport-ledger-smoke`, response `LEDGER_OK`, exit `0`

Raw absolute-EOF runtime row:

```json
{"schema_version":1,"event":"solo_runtime","request_id":"49475-1786664339960906000-1","outcome":"succeeded","exec_invocation_count":1,"exec_wall_ns":199333,"snapshot_save_count":1,"snapshot_save_wall_ns":633083,"snapshot_load_count":0,"snapshot_load_wall_ns":0,"sub_call_count":0,"sub_call_wall_ns":0}
```

Raw normalized per-item ledger:

```json
{"complete":true,"exec_invocation_count":1,"exec_wall_ms":0.199333,"repair_cost":{"cache_read_tokens":0,"inference_ms":0,"input_tokens":0,"output_tokens":0,"token_accounting_complete":true},"repair_count":0,"root_inference_ms":30,"root_turn_count":1,"schema_version":1,"snapshot_load_count":0,"snapshot_load_ms":0.0,"snapshot_save_count":1,"snapshot_save_ms":0.633083,"sub_call_count":0,"sub_call_turn_count":0,"sub_call_wall_ms":0.0}
```

## Frozen RULER width-4 smoke: baseline to v42

This is the preregistered `candidate-smoke-20-v1` diagnostic slice, executed at one
**global** controller width of 4 with subscription OAuth, `gpt-5.6-luna`, and root
reasoning `medium`. It is deliberately unscored: no gold or scorer was opened.
Both runs used the exact ordered fixture/payload commitment
`db40308e93a8dcbd520cc10f47d2eb5569369f5402d60ddd9bd57a04fe945bd6`
and frozen controller `bench/ruler/run.py`
`fc15b4dafd5bb07c09169576565eb17e9425b3cf301e6366ebc81676d391ac81`.

Immutable before:

- candidate binary `3948710fd24cd067372c58f2680dc7c2579af458bfa0b7ef33203995195f26bc`
- output `b2ef1bc041210d6e71bd885902f0196f440d90eb0a486eced21d29f0bc3cd2dd`
- schedule `cfe9f38ae2edea35e796e297337483cbe6cd7ab7e8712c78ecc67c32b00aac51`
- result 19/20 execution, one process exit, 178.713122 s makespan

Immutable after (v42):

- candidate binary `5fa5e399801d152915a698a82498ac379ac8ae0335d4626c290c782b3989cd0a`
- source stamp `546bc62b8832f6b4632ea160230b18ca55b6c653e747a3fc66052fe0507c01bc`
- output `99dad202607fafb1a9f1102414b596f4d5648d5d498ba0aef9ad9981f36ba38b`
- schedule `3f7589e4a497364056be8a96daab8e44cf61fbaa200c3b0dbfd7e4ffecd90512`
- result **20/20 execution**, zero process exits/timeouts, 175.236998 s makespan
- all 20 product lifecycles, payload checks, exact trace captures, performance ledgers,
  OAuth routes, credential cleanups, and >=100-character leak scans asserted; leaks 0/20

Aggregate before -> after:

| measure | before | v42 | delta |
|---|---:|---:|---:|
| execution | 19/20 | 20/20 | +1 item |
| makespan s | 178.713122 | 175.236998 | -3.476124 (-1.95%) |
| item mean s | 31.992169 | 29.284071 | -2.708099 (-8.46%) |
| item median s | 28.621568 | 19.969727 | -8.651841 (-30.23%) |
| item p95 s | 51.018710 | 59.591941 | +8.573230 |
| root turns / repairs | 25 / 5 | 29 / 9 | +4 / +4 |
| provider inference s | 631.329 | 577.511 | -53.818 |
| provider output tokens | 49,039 | 44,240 | -4,799 |
| provider input tokens | 69,508 | 96,791 | +27,283 |
| exec count / wall ms | 25 / 212.841 | 29 / 251.655 | +4 / +38.815 |
| snapshot saves / wall ms | 20 / 3.194 | 20 / 4.904 | 0 / +1.710 |
| snapshot loads / wall ms | 5 / 0.583 | 9 / 1.888 | +4 / +1.305 |
| logical subcalls / wall ms | 0 / 0.000 | 0 / 0.000 | 0 / 0.000 |

The one-turn subset changed from 17 items at 27.877 s mean / 2,134 root output
tokens mean to 13 items at 18.047 s / 1,312 tokens. This is descriptive rather than a
paired accuracy claim; repairs increased from 5 to 9 and remain the dominant avoidable
tail. The v42 mean is 3.371x the historical v38 native mean of 8.685748 s, so the
<=1.5x acceptance target is still **not met**. The smoke proves the <=5-minute and
20/20 gates only, not the frozen-90 or comparative accuracy gates.

Per-item columns are `turns/repairs`, provider inference milliseconds, provider output
tokens across all turns, and `exec/save/load/subcall` counts. The failed before row
retains its measured runtime but its incomplete ledger remains a fixed-denominator zero.

| # | fixture | B status | B wall s | B t/r | B provider ms | B out | B e/s/l/c | A status | A wall s | A t/r | A provider ms | A out | A e/s/l/c | wall delta s |
|---:|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `0842be47` | ok | 17.785 | 1/0 | 17336 | 1283 | 1/1/0/0 | ok | 16.691 | 1/0 | 16187 | 1208 | 1/1/0/0 | -1.094 |
| 2 | `6670e3c8` | ok | 25.699 | 1/0 | 25245 | 1951 | 1/1/0/0 | ok | 10.022 | 1/0 | 9524 | 636 | 1/1/0/0 | -15.678 |
| 3 | `6a55c9a3` | ok | 40.161 | 1/0 | 39663 | 3110 | 1/1/0/0 | ok | 17.814 | 1/0 | 17311 | 1203 | 1/1/0/0 | -22.348 |
| 4 | `05b3f054` | ok | 27.692 | 1/0 | 27225 | 2098 | 1/1/0/0 | ok | 20.082 | 1/0 | 19573 | 1417 | 1/1/0/0 | -7.610 |
| 5 | `324ca4d7` | ok | 35.252 | 1/0 | 34895 | 2760 | 1/1/0/0 | ok | 16.709 | 1/0 | 16328 | 1238 | 1/1/0/0 | -18.543 |
| 6 | `20717f3b` | ok | 27.611 | 1/0 | 27255 | 2155 | 1/1/0/0 | ok | 44.029 | 2/1 | 43629 | 3440 | 2/1/1/0 | +16.418 |
| 7 | `2a38707a` | ok | 18.440 | 1/0 | 18102 | 1389 | 1/1/0/0 | ok | 43.109 | 2/1 | 42724 | 3321 | 2/1/1/0 | +24.668 |
| 8 | `0d5ef27c` | ok | 16.793 | 1/0 | 16295 | 1217 | 1/1/0/0 | ok | 23.006 | 1/0 | 22659 | 1768 | 1/1/0/0 | +6.213 |
| 9 | `2285810b` | ok | 23.932 | 1/0 | 23579 | 1815 | 1/1/0/0 | ok | 16.738 | 1/0 | 16380 | 1215 | 1/1/0/0 | -7.194 |
| 10 | `1d930dbb` | ok | 29.551 | 1/0 | 29189 | 2187 | 1/1/0/0 | ok | 18.901 | 1/0 | 18549 | 1417 | 1/1/0/0 | -10.650 |
| 11 | `4373136e` | ok | 73.824 | 3/2 | 73204 | 5778 | 3/1/2/0 | ok | 19.857 | 1/0 | 19522 | 1496 | 1/1/0/0 | -53.967 |
| 12 | `513316fa` | ok | 49.818 | 3/2 | 49292 | 3709 | 3/1/2/0 | ok | 47.260 | 2/1 | 46887 | 3621 | 2/1/1/0 | -2.559 |
| 13 | `11dc65da` | ok | 22.362 | 1/0 | 22011 | 1707 | 1/1/0/0 | ok | 59.268 | 2/1 | 58888 | 4674 | 2/1/1/0 | +36.906 |
| 14 | `9361854e` | ok | 24.319 | 1/0 | 23925 | 1864 | 1/1/0/0 | ok | 37.005 | 2/1 | 36648 | 2827 | 2/1/1/0 | +12.686 |
| 15 | `2ac3ee8a` | ok | 18.599 | 1/0 | 18250 | 1391 | 1/1/0/0 | ok | 19.410 | 1/0 | 18934 | 1405 | 1/1/0/0 | +0.811 |
| 16 | `4423687d` | ok | 34.423 | 1/0 | 34007 | 2638 | 1/1/0/0 | ok | 9.755 | 1/0 | 9379 | 604 | 1/1/0/0 | -24.669 |
| 17 | `00cc544f` | ok | 42.296 | 2/1 | 41768 | 3276 | 2/1/1/0 | ok | 11.419 | 1/0 | 11039 | 795 | 1/1/0/0 | -30.877 |
| 18 | `0638d6b8` | ok | 42.816 | 1/0 | 42439 | 3413 | 1/1/0/0 | ok | 34.206 | 1/0 | 33826 | 2654 | 1/1/0/0 | -8.611 |
| 19 | `1ed71e2b` | ok | 32.721 | 1/0 | 32245 | 2531 | 1/1/0/0 | ok | 54.655 | 3/2 | 54224 | 4165 | 3/1/2/0 | +21.935 |
| 20 | `44cd3a58` | FAIL | 35.748 | 1/0 | 35404 | 2767 | 1/1/0/0 | ok | 65.749 | 3/2 | 65300 | 5136 | 3/1/2/0 | +30.001 |

Discarded immutable intermediates were not retried: v39 19/20 at 202.734077 s, v40
19/20 at 205.010624 s, and v41 19/20 at 149.102636 s. V41 had 20 nonempty product
results but one trace-retention failure; its sampler was superseded after an exact
206-character adversarial self-embedding was reproduced. V42 adds a streaming,
fail-closed 100-codepoint overlap guard with bounded sample hashes and no
source-sized hash materialization.
