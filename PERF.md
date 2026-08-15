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


## Frozen RULER v42 candidate-90 terminal gate

The immutable v42 `candidate-full-90-v1` run terminated naturally with the exact 90-row
frozen schedule and no retry, resume, scoring, or gold access. Its output SHA-256 is
`420e2519a0846675d480588fdbbd109f6af1bc4b666a514c68761a1de7f4a291` and its
schedule ID is `1dcfee1b32f29813fbfe04081af3c5c3d4b8867b678ec310e63c5380bb9e5177`.
It missed the reliability gate at **89/90 execution**. Ordinal 87, fixture
`rxm-9361854e5de1e01d72c8c549b4006f9e` (`fwe`, 32,768), exited 2 after the second
typed Assertion repair still produced an empty answer. This remains a
`monty_subset_error` fixed-denominator zero. The exact stderr SHA-256 is
`d4c63188bfb017749772c25483fa305fd8f1da91aebb9434d5cfaa46d00347aa`.

The global-width-4 makespan was **699.178999 s**, which passed the 720-second target
with 20.821001 s headroom, but speed cannot compensate for the failed row. The run used
122 root turns, 32 repairs, 2,659.833 s provider inference, 122 exec invocations, 90
snapshot saves, 32 loads, and zero subcalls. All 90 claims/done receipts, schedules,
component and payload identities, route assertions, exact trace captures, workspace/credential cleanup checks, and >=100-character leak scans
passed; every ledger was present and exactly replayed (89 complete; the failed row
intentionally incomplete);
leaks were zero. Product lifecycle passed only 89/90 because of the process failure.
The terminal record is `/private/tmp/azdaja-ruler-width4-candidate90-v42-v1-terminal-record.json`,
SHA-256 `9f82058818f516ed429ece25bc6fc694475e85441ddab0c3bfb7621cc8be6909`. Official `full-v1` remained blocked.

## Frozen RULER width-4 smoke: v42 to v43

This is an immutable paired comparison over the same ordered 20-fixture commitment,
frozen controller, OAuth route, model, reasoning level, global width 4, and
`candidate-smoke-20-v1` no-score/no-gold workflow described above. V43 is a generic
reliability/speed candidate: long low-frequency lines can contribute their first
uncovered bounded structural continuation instead of being suppressed by an overlapping
head/middle/tail region, and typed Assertion repair explicitly re-derives a false
boundary rather than retaining it because an earlier check passed. No benchmark names,
question templates, product tools, config keys, or SKILL strategy were added.

Immutable before (v42):

- candidate binary `5fa5e399801d152915a698a82498ac379ac8ae0335d4626c290c782b3989cd0a`
- output `99dad202607fafb1a9f1102414b596f4d5648d5d498ba0aef9ad9981f36ba38b`
- schedule ID `3f7589e4a497364056be8a96daab8e44cf61fbaa200c3b0dbfd7e4ffecd90512`
- result 20/20 execution, 175.236998 s makespan

Immutable after (v43):

- candidate binary `6be5b9ff567eca6d1a5c2315dfb0c12fb5bd847b58daef0b3b8191151e45b509`
- source patch `b11f34b195a8efcb3f9a857236da03b6fc036dc46dd543a304c4f67b9ab43997`
- source stamp `fd4dcedac4beae4fd55b24d0c6be3f8053b522bb65b3bcf67b82b8a7326b2d0d`
- output `3ffc7e9187b57eeae738f291dea00c935506268338b49599bf82066e93325cfc`
- schedule ID `bce16a4287857d3d0f65c10792d7f8a14d3cc0f4bfe483578eb1c40099cce677`
- result **20/20 execution**, zero process exits/timeouts, 119.739380 s makespan
- 20/20 one root turn and one exec invocation; **zero repairs and zero subcalls**
- all 20 exact traces, ledgers, usage rows, routes, payloads, lifecycles, candidate
  staging, tool-policy checks, credential cleanups, claims/done receipts, and
  >=100-character leak scans passed; leaks 0/20

Aggregate v42 -> v43:

| measure | v42 | v43 | delta |
|---|---:|---:|---:|
| execution | 20/20 | 20/20 | unchanged |
| makespan s | 175.236998 | 119.739380 | -55.497618 (-31.67%) |
| item mean s | 29.284071 | 21.746139 | -7.537932 (-25.74%) |
| item median s | 19.969727 | 21.560276 | +1.590549 (+7.96%) |
| item p95 s | 59.591941 | 29.987673 | -29.604267 (-49.68%) |
| root turns / repairs | 29 / 9 | 20 / 0 | -9 / -9 |
| provider inference s | 577.511 | 426.826 | -150.685 (-26.09%) |
| provider output tokens | 44,240 | 31,859 | -12,381 (-27.99%) |
| provider input tokens | 96,791 | 52,565 | -44,226 (-45.69%) |
| exec count / wall ms | 29 / 251.655 | 20 / 241.386 | -9 / -10.269 |
| snapshot saves / wall ms | 20 / 4.904 | 20 / 4.265 | 0 / -0.640 |
| snapshot loads / wall ms | 9 / 1.888 | 0 / 0.000 | -9 / -1.888 |
| logical subcalls / wall ms | 0 / 0.000 | 0 / 0.000 | unchanged |

This is a `DUAL-WIN:` smoke result: it preserves 20/20 while eliminating every measured
repair, lowering failure surface, mean latency, tail latency, makespan, inference time,
and tokens. Median item latency rose 1.590549 s, so the per-item table remains essential.
The v43 mean is still **2.504x** the historical v38 native mean of 8.685748 s, so the
<=1.5x target remains missed. This smoke proves neither frozen-90 reliability nor
comparative accuracy; v43 must run the entire fresh frozen 90 before `full-v1` can begin.

Per-item columns are root `turns/repairs`, provider inference milliseconds, provider
output tokens across all turns, and `exec/save/load/subcall` counts.

| # | fixture | v42 wall s | v42 t/r | v42 provider ms | v42 out | v42 e/s/l/c | v43 wall s | v43 t/r | v43 provider ms | v43 out | v43 e/s/l/c | wall delta s |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `0842be47` | 16.691 | 1/0 | 16187 | 1208 | 1/1/0/0 | 17.054 | 1/0 | 16532 | 1212 | 1/1/0/0 | +0.364 |
| 2 | `6670e3c8` | 10.022 | 1/0 | 9524 | 636 | 1/1/0/0 | 22.878 | 1/0 | 22374 | 1737 | 1/1/0/0 | +12.856 |
| 3 | `6a55c9a3` | 17.814 | 1/0 | 17311 | 1203 | 1/1/0/0 | 17.068 | 1/0 | 16559 | 1222 | 1/1/0/0 | -0.746 |
| 4 | `05b3f054` | 20.082 | 1/0 | 19573 | 1417 | 1/1/0/0 | 21.967 | 1/0 | 21428 | 1636 | 1/1/0/0 | +1.885 |
| 5 | `324ca4d7` | 16.709 | 1/0 | 16328 | 1238 | 1/1/0/0 | 21.313 | 1/0 | 20893 | 1592 | 1/1/0/0 | +4.604 |
| 6 | `20717f3b` | 44.029 | 2/1 | 43629 | 3440 | 2/1/1/0 | 22.320 | 1/0 | 21938 | 1691 | 1/1/0/0 | -21.709 |
| 7 | `2a38707a` | 43.109 | 2/1 | 42724 | 3321 | 2/1/1/0 | 21.210 | 1/0 | 20835 | 1540 | 1/1/0/0 | -21.899 |
| 8 | `0d5ef27c` | 23.006 | 1/0 | 22659 | 1768 | 1/1/0/0 | 17.320 | 1/0 | 16980 | 1203 | 1/1/0/0 | -5.687 |
| 9 | `2285810b` | 16.738 | 1/0 | 16380 | 1215 | 1/1/0/0 | 21.434 | 1/0 | 21085 | 1472 | 1/1/0/0 | +4.696 |
| 10 | `1d930dbb` | 18.901 | 1/0 | 18549 | 1417 | 1/1/0/0 | 24.023 | 1/0 | 23651 | 1762 | 1/1/0/0 | +5.122 |
| 11 | `4373136e` | 19.857 | 1/0 | 19522 | 1496 | 1/1/0/0 | 23.827 | 1/0 | 23495 | 1800 | 1/1/0/0 | +3.970 |
| 12 | `513316fa` | 47.260 | 2/1 | 46887 | 3621 | 2/1/1/0 | 29.541 | 1/0 | 29179 | 2204 | 1/1/0/0 | -17.719 |
| 13 | `11dc65da` | 59.268 | 2/1 | 58888 | 4674 | 2/1/1/0 | 23.256 | 1/0 | 22882 | 1696 | 1/1/0/0 | -36.012 |
| 14 | `9361854e` | 37.005 | 2/1 | 36648 | 2827 | 2/1/1/0 | 21.687 | 1/0 | 21361 | 1609 | 1/1/0/0 | -15.318 |
| 15 | `2ac3ee8a` | 19.410 | 1/0 | 18934 | 1405 | 1/1/0/0 | 15.300 | 1/0 | 14889 | 1085 | 1/1/0/0 | -4.110 |
| 16 | `4423687d` | 9.755 | 1/0 | 9379 | 604 | 1/1/0/0 | 14.573 | 1/0 | 14092 | 1045 | 1/1/0/0 | +4.819 |
| 17 | `00cc544f` | 11.419 | 1/0 | 11039 | 795 | 1/1/0/0 | 38.481 | 1/0 | 38106 | 2879 | 1/1/0/0 | +27.062 |
| 18 | `0638d6b8` | 34.206 | 1/0 | 33826 | 2654 | 1/1/0/0 | 20.851 | 1/0 | 20493 | 1479 | 1/1/0/0 | -13.355 |
| 19 | `1ed71e2b` | 54.655 | 3/2 | 54224 | 4165 | 3/1/2/0 | 24.306 | 1/0 | 23937 | 1859 | 1/1/0/0 | -30.349 |
| 20 | `44cd3a58` | 65.749 | 3/2 | 65300 | 5136 | 3/1/2/0 | 16.517 | 1/0 | 16117 | 1136 | 1/1/0/0 | -49.232 |

## Frozen v43 RULER candidate gate and official score

The immutable v43 candidate (`6588c06`, binary
`6be5b9ff567eca6d1a5c2315dfb0c12fb5bd847b58daef0b3b8191151e45b509`)
first passed `candidate-full-90-v1` at **90/90 execution**. The candidate-only output
SHA-256 is `bf9af3654972253856d18634492603f1c16d5749c24b7d3714b87f0d8a814815`,
schedule ID `f2086f4b861a03d9b5bf6d570ce309aed6a9bd27b63ad94ccb5afd1fe2d1fb12`.
Global width/peak were 4/4 and makespan was **562.296805 s**, passing the 720-second
gate with 157.703195 s headroom. The 90 jobs used 93 root calls (3 repairs), zero
subcalls, 2,155.362 s provider inference, 249,011 input, 164,731 output, and 5,376
cache-read tokens. All exact per-item runtime ledgers, claims, done receipts, traces,
routes, payloads, lifecycle and cleanup assertions passed; exact >=100-character
root-context leaks were 0/90.

The subsequent official `full-v1` cohort is exact and immutable: 270 canonical rows,
90/arm, output SHA-256
`c4f90f7aa9d29a09006fc22c954c62d8874976f886e8ef22c9a420c429e44d85`, schedule
ID `46e4be08650b1263e9a9bc98ab7a169b75a2595613cd0eb2f6aea5c34c05b276`, width/peak
4/4, and **1,101.539114 s** makespan. Candidate/native executed 90/90; Prime executed
87/90, with three retained raw `tool_policy` failures counted as fixed zeros. The one
authorized score report has SHA-256
`26ce16464658d57caed466be36f373790b95f44077fe396bc43e4f64bc534c0a`.

| arm | execution | completed strict | fixed strict | official coverage | mean root tokens | p50 wall s | p95 wall s |
|---|---:|---:|---:|---:|---:|---:|---:|
| Azdaja | 90/90 | 85/90 | 85/90 | 96.89% | 2,834.67 | 22.520 | 37.645 |
| native | 90/90 | 86/90 | 86/90 | 98.89% | 16,372.55 | 8.125 | 16.808 |
| Prime | 87/90 | 81/87 | 81/90 | 96.67% | 6,925.36 | 10.867 | 18.992 |

Native-minus-Azdaja fixed strict was +1.11 pp, paired 95% bootstrap CI
[-5.56,+7.78]; no superiority or equivalence claim is supported. Candidate median
latency was 2.77x native, so the <=1.5x target remains missed. Root-token authority
differs by arm: candidate-emitted depth-0 usage versus control terminal-result
character proxies. Score audit found no P0 and one no-score-impact P1: the frozen report
overstated route/usage replay scope for three failed Prime rows. Future reports now distinguish independent successful-row replay from all-attempt
aggregation of controller-recorded assertions and normalized usage, whose failed-row entries
are not replay-validated. Terminal score record:
`/private/tmp/azdaja-ruler-v43-terminal-score-record.json`, SHA-256
`fe7c8e15a9b513ad532edd07de265f084c26afb7604a771e1ff9db6135738198`.

## Frozen v43 derived LongBench-v2 terminal score

The exact fresh 63-fixture x 3-arm cohort ran serially without intervention, retry, or
resume. Output SHA-256 is
`55271a272b61ba973e6e129a8312b3e0229c68342248ddec33669f1a270f6557`, schedule ID
`5bd46a135f01dc0d44e34a8680f82f25ad55dce9ea87354dca49fa62b298f952`, and the
single authorized score report SHA-256 is
`288643391834c9e41966df08f65a297e7750e3e65e925336334a23c12cb7ae5d`.
The serial cohort wall span was **9,662.687354 s** (161.045 minutes). All 189 claims and
completions, 189 artifact directories, 504 retained files, exact payloads, component and
runtime identities, routes, usage receipts and cleanup checks passed. All 63 candidate
solo transcripts were retained and rescanned; exact >=100-character root-context leaks
were 0/63.

| arm | execution | completed official | fixed-63 official | mean root tokens | p50 wall s | p95 wall s | summed wall s |
|---|---:|---:|---:|---:|---:|---:|---:|
| Azdaja | 48/63 | 7/48 (14.58%) | 7/63 (11.11%) | 6,155.63 | 51.429 | 82.100 | 3,430.295 |
| native | 63/63 | 35/63 (55.56%) | 35/63 (55.56%) | 63,223.06 | 19.847 | 50.346 | 1,581.257 |
| Prime | 56/63 | 12/56 (21.43%) | 12/63 (19.05%) | 9,826.73 | 39.369 | 56.072 | 2,537.867 |

The candidate used 239 valid model calls: 63 initial roots, 41 depth-0 repairs across 25
runs, and 135 depth-1 subcalls. Exact totals were 1,476,063 input, 261,322 output,
99,328 cache-read and 1,737,385 total tokens; provider call-latency sum was 3,623.982 s.
Initial roots used 155,161 input / 143,660 output tokens and 1,849.870 s; repairs used
232,644 / 63,500 and 819.447 s; subcalls used 1,088,258 / 54,162 and 954.665 s.
The report's 387,805 root-token total is all depth-0 input, including repairs.

Candidate failures were 15 raw `process_exit` rows: six semantic prompt-envelope
assertions, six solver assertions, two Monty subset-like TypeError/AttributeError rows,
and one inner 30-second cell timeout. Under the campaign reliability taxonomy this is
14 `monty_subset_error` and one `cell_timeout`; the frozen scorer conservatively reports
15 `other_execution`. Prime had seven retained `tool_policy` failures; native had none.
Among the 48 completed candidate rows, 20 failed official extraction, 21 were wrong and
seven were correct. The strict full-string diagnostic was 0/63 because accepted canonical
responses retained a trailing LF.

This misses the preregistered candidate gate of 16/63 fixed official accuracy (execution
48/63 clears the separate 32/63 floor), so OOLONG and RAH are blocked for v43. Candidate
median latency was 2.59x native. The nominal runner also hit a fail-closed terminal
caller bug after row 189: it passed clean fixtures without captured payload bytes to the
frozen validator. A separate no-gold call through the same frozen scorer's public loader
and `validate_frozen_runs` passed exact 189, then the sole CLI score succeeded. The live
controller now reattaches the already captured bytes at that boundary; no frozen row,
claim, artifact, or report was modified.

## LongBench-v2 v43 post-score format and deterministic-failure triage (2026-08-14)

This was read-only, offline diagnosis of the already frozen v43 cohort. It did not invoke
the scorer again, inference, retry, or resume, and it did not modify any frozen row,
claim, transcript, artifact, or report. Frozen inputs remain runs SHA-256
`55271a272b61ba973e6e129a8312b3e0229c68342248ddec33669f1a270f6557` and report SHA-256
`288643391834c9e41966df08f65a297e7750e3e65e925336334a23c12cb7ae5d`.

A syntax-only lenient extractor protocol was committed before candidate responses or gold
were read (SHA-256 `d163ffe52b94011b4a363de9d4373679c2339e90484ca006d5b7fdb6d64e5eb3`).
Across all 48 retained successful responses, the 28 official-recognized rows remained
unchanged at 7 correct and 21 wrong. Every one of the 20 official misses was exactly one
bare uppercase A-D label plus LF; all 20 were unambiguous, with 13 correct and 7 wrong.
The diagnostic format-fixed count is therefore 20/63 (31.746%, +13), above the 16/63
gate, while the immutable official result remains 7/63. Result SHA-256:
`da2d070720e40de1305f1ec4164a94c75ca626bdf1c26f239630d33db6b885d5`.

All 14 non-timeout process exits were then bound to exact frozen trace and generated-program
hashes. The terminal families were six fixed `semantic_manifest` prompt-envelope overflows,
six fail-closed solver/postcondition cardinality assertions, one Monty `int + bool` TypeError,
and one unavailable `dict.__getitem__` AttributeError. The extracted forensic bundle SHA-256
is `3007f7ab0ae4cf7569324187baeddd547d368bd1ecb80d6a14af83a27065bcbe`.
Seven minimal offline cases cover every family; the frozen v43 binary reproduced them with
no network, scorer, gold, or benchmark payload access. Two fresh harness invocations produced
identical result SHA-256 `528051bf4ce94e53aba48ca4c44c1f57599a9a2845f1cb03d5f83daa254ff37e`.
The exact semantic boundary was 44,410 evidence characters fitting a 45,000-character
prompt and 44,411 overflowing before any child call.

The generic v45 reliability patch already supplies exact trusted helper-envelope arithmetic,
actionable complete-boundary repair, typed Program diagnostics, a global three-turn ceiling,
and no repair after child evidence. The v46 step-2 delta only removes `solo`'s injected LF
by byte-writing the already verified FINAL value on all three success paths; it does not
parse, wrap, trim, or otherwise rewrite answers. The exact step-2 patch SHA-256 is
`fac3c1ec36be9c41f04a5ef6911f497e095aac11af9ef2260762d9e1695970ae`.
Its offline e2e asserts raw output bytes and imports the actual pinned `official_extract_answer`
and strict extractor. This remains SPEED-RISK until the full source gate and frozen RULER
smoke/candidate-90 gates pass.

### LongBench-v2 v43 inner-cell timeout closure

The sole timeout was ordinal 127 on an 8,532,958-byte payload (8,532,613 loaded
characters). Its exact generated program SHA-256 was `953efd5e835bc7b8746cd82a0dc64c037b23b7ab5c1839e7702baf208c21bdc1`. Before any child
call it lowercased the full context, ran three full `re.finditer` scans collecting every
match, then for every match performed eight prefix `rfind` and twelve suffix `find` scans
and accumulated unbounded snippets. It exhausted one cell at 30.004649 s with zero
subcalls; this is an algorithmic outlier, not evidence that the global cap is too small.

`solo_runtime.exec_wall_ns - sub_call_wall_ns` gives authoritative local execution wall;
for one-exec items it is an exact cell duration, while multi-exec rows remain aggregates
and were not divided or mislabeled. Among 36 successful one-exec rows, local p50/p95/max
were 0.166/2.908/9.446 s. Among the four successful one-exec rows with payloads at least
5 MiB, p50/p95/max were 2.907/8.895/9.446 s. The timeout was therefore 10.32x the overall
successful exact-cell p95 and 3.37x the same-size-band p95. The 30-second cap remains;
v45's generic policy allows exactly one pristine zero-child Timeout repair with bounded
passes, while repeated/post-child timeout remains terminal under the global three-turn
ceiling. Record SHA-256: `05f62db02dc971c10fedc14fc96635ba4ba0449bf1cc87e852c1b62feeb99f33`.

### v45/v46 RULER smoke closure and v46 freeze

The final pre-inference v46 source state was frozen at binary diff SHA-256
`b3d729aea2c9a0c80b595915eaab2fd37a4c907f5512dfe281864eacb954f3ac`
(stable patch-id `7eafcbb5561431afbe0ce5323d68a1980f353a2b`) after the complete offline gate
passed. The release binary SHA-256 is
`e95f4f64b6edc97d665890fd8cd7cd06c69a9dae0119509eefe7301aab20f6f0`; SKILL and
config remained the v43 bytes. The authoritative source-mode-correct freeze stamp is v2,
SHA-256 `d38167798c4890c9f8b5ae1c9e0209b48e6322d3e98e315c093d4cb505e389c3`.

The first v46 controller invocation stopped in preflight because its source bundle used
snapshot destination modes (0500/0400) rather than the controller-required source modes
(0700/0600). It created no schedule, claims, output rows, model calls, or score. The
failure record SHA-256 is
`df518459a8f0c1e4ec2ca63d64cfaa57bc3e8524e0fee6408da1bf8980075126`; the retained
byte-identical v2 bundle corrected only source file modes before the one inference smoke.

| frozen smoke | execution | makespan s | mean s | p50 s | p95 s | root turns | repairs | input tokens | output tokens | >=100-char leaks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v43 | 20/20 | 119.739380 | 21.746139 | 21.560276 | 29.987673 | 20 | 0 | 52,565 | 31,859 | 0 |
| v45 | 20/20 | 138.361953 | 24.710454 | 23.167352 | 39.437929 | 22 | 2 | 63,445 | 36,034 | 0 |
| v46 | 20/20 | 143.415445 | 26.280510 | 24.801299 | 39.744774 | 21 | 1 | 57,400 | 37,551 | 0 |

V45 restored reliability but regressed versus identical v43 by 15.55% makespan, 13.63%
mean, 31.51% p95, and 13.10% output tokens. V46 likewise regressed by 19.77% makespan,
20.85% mean, 15.03% p50, 32.54% p95, and 17.87% output tokens. V46's one functional
delta from v45 is byte-transparent CLI answer emission; because provider generation is
stochastic, the smoke does not attribute these paired token differences to that emitter.
The frozen result nevertheless fails the preregistered no-material-speed/token-regression
gate and remains terminal: no candidate-90 or LongBench inference is authorized.

V46 output SHA-256:
`fa4ad758720db07c0f1341704e147a14da94dac8afb0865d7b5f6fa219876b6c`.
Terminal record SHA-256:
`12dbef41dc30d3db30345091cac036fc0921efa8ba76588307504e2ba1f4366a`.
All 20 rows, 20 claims, 20 completion receipts, route/lifecycle assertions, candidate
pre/post identities, ledgers, and zero-leak checks validated without opening gold or
invoking a scorer.

### v43/v45/v46 smoke provenance and offline speed postmortem

A read-only deterministic audit bound each of the 60 smoke rows to its schedule candidate
aggregate, component binary, frozen controller, run ID, schedule ID, claim filename,
completion filename, and exact JSONL row SHA-256 without the line delimiter. Both runs
of audit script SHA-256
`24b2c3db1c899b6829be0c26a0c1a49af1a95dccb39705876f70274bced6f645`
produced result SHA-256
`e058f3117e4876fbf45d5410fcadeb33dacf69e3c67e6f4b97d42bc015d95362`
with no errors. The immutable v45 terminal-record v1 had compared aggregate candidate
identity to component-binary identity and therefore contained a false negative; v2
supersedes it at SHA-256
`d146c4621b20a0656a78eae48fdce49c63695b05c785d71660a05146bb3cb61c`.
V45 remains rejected on its independent speed/token result.

Offline decomposition attributes 98.1%/98.4%/98.5% of v43/v45/v46 summed item latency
to root inference. After excluding repairs, v45 and v46 initial-root output totals were
34,299 and 36,438 tokens versus v43's 31,859, while visible initial generated-code
characters stayed essentially flat at 10,773/10,662 versus 10,668. V45 to v46 changed
only post-inference byte emission, yet v46 initial inference rose 36.057 s and 2,139
output tokens; it cannot be caused by the emitter. Provider/sample variation and any
v43-to-v45 prompt effect cannot be separated from one frozen stochastic pass. Reducing
the global root-turn cap would not affect 19/20 v46 rows and would trade away recovery,
so no v47 change or repeated smoke is authorized. Offline postmortem SHA-256:
`ffd371ab01ede45702072ce17df9208062828719609426923e13e3708b1694ff`.

## V47 preregistration: static-prefix root/repair prompts (offline, no inference)

- Scope/order: speed ladder step 1 only. V47 changes Azdaja's own initial-root and same-session repair message layout so the reusable contract is a byte-identical prefix and all item-specific question/metadata/sample or typed repair diagnostics are strictly last. It does not change Jcode, model, reasoning effort, tools, controller width, session isolation, caps, subcommands, `assets/SKILL.md`, or `assets/config.toml`.
- Shipped Jcode remains exact v0.75.3 (`fd1ff012c`), installed binary SHA-256 `f01c442265d22e9dead7f227b2ec115ab99164e876ff354a72988a9311bf3c4f`. No patched-harness build is eligible for this lineage. `JCODE_OPENAI_PROMPT_CACHE_KEY` and `JCODE_OPENAI_MAX_OUTPUT_TOKENS` are deliberately unset: v0.75.3 omits both fields for the required ChatGPT OAuth request mode, so code-side forwarding would be a recorded no-op rather than a mechanism.
- The root reusable prefix is 3,328 UTF-8 bytes under the frozen adapter config. A deterministic unit test constructs two disjoint dynamic items and proves their prefix bytes are identical, their dynamic values do not occur in the prefix, metadata/sample follow the marker, and the question is the final prompt bytes. Repair messages likewise share one fixed prefix and put category, bounded line/diagnostic, and category constraint last while retaining the 1,024-character repair bound.
- V46 repair root cause is closed fail-closed before freeze: the reusable contract now forbids treating line count or fixed line indices as evidence/question boundaries and requires observed-boundary validation. A regression executes the diagnosed two-line structural-assumption family (large first evidence line, question second; generated code incorrectly treats `lines[1]` as evidence) and proves typed `Assertion`, zero child calls, no finalized state, and no publishable answer.
- Offline gate: `/private/tmp/azdaja-v47-pre-freeze-offline-gate-v4.log`, SHA-256 `d29b03a476b214cdad4c909de850932f464dd5013660050672df5d8e6d9a2879`; passed diff check, fmt, debug/release checks, strict clippy, debug/release Rust tests, 100 LongBench controller tests under Python 3.12, and 83 RULER controller tests. Superseded immutable v1-v3 logs retain respectively the expected old-string test failures, the repaired-prompt bound failure, and the system-Python/ENOSPC operational failures; none entered inference.
- Fresh-smoke adjudication is preregistered: 20/20 execution, zero leaks/timeouts/cleanup failures, exact v43-equivalent configuration, and per-turn streamed usage are mandatory. Initial-root `cache_read` must be reported separately from same-session repairs; a repair-only cache hit does not prove cross-item prefix caching. Any material wall/output-token regression rejects V47. If all fresh initial roots remain `cache_read=0`, the cache mechanism is unverified and V47 cannot proceed to candidate-90 even if reliability is 20/20.

## V47 terminal smoke: static prefix did not produce cross-item cache reads

- Frozen candidate: `/private/tmp/azdaja-luna-v47-static-prefix-v2`; binary SHA-256 `d1b6ac5745b83fff41303c83e037694bf2b0dbf5898f443ab46b5766cbf5e208`; pre-inference source SHA-256 `9dfc8a2ca651e59ec93996befb03221b00fe6291b1ad5835c78e12922583eb05`; freeze-stamp SHA-256 `3562ce603621e1d066f32cc6d2eb3d80861083c9dbf1fd947f8f4a988ffbc35d`; unchanged Jcode v0.75.3 SHA-256 `f01c442265d22e9dead7f227b2ec115ab99164e876ff354a72988a9311bf3c4f`.
- Frozen output: `/private/tmp/azdaja-ruler-width4-smoke-v47-static-prefix-v2.jsonl`, SHA-256 `bf9c200da44b13ad1ad9f0a68ae004bfac8f095b47bb3e63761653ea7c0068a3`. Terminal record: `/private/tmp/azdaja-ruler-v47-smoke-terminal-record-v1.json`, SHA-256 `d7a3e989cd73946829135a556339f41a90e09a05d5fa839990b038940aa4de71`. Twenty claim files and twenty completion receipts bind the exact no-LF row bytes; no score or gold was invoked.
- Execution/evidence: 20/20; 21 root turns; one repair at ordinal 6; zero subcalls, timeouts, cleanup errors, and >=100-Unicode-character leaks. Root model/route remained `gpt-5.6-luna`, subscription OAuth, reasoning `medium`; global width peaked at four.
- Cache result: all 20 initial roots reported `cache_read=0`. The only cache read was 1,792 tokens on the same-session repair, which is not cross-item prefix evidence. Initial roots used 55,190 input / 38,266 output tokens and 538.811s provider wall; the repair used 4,917 / 991 tokens, 1,792 cache-read tokens, and 12.909s provider wall. The preregistered cache mechanism therefore failed.
- Wall/token result: makespan 175.855413s; mean 30.543499s; median 29.168285s; p95 53.157768s; total input/output 60,107/39,257. Versus the identical frozen v43 smoke, makespan +46.87%, mean +40.45%, median +35.29%, p95 +77.27%, input +14.35%, output +23.22%. Late setup/local overhead outliers occurred at ordinals 15/17/18/19/20, but initial-root cache zero plus material output/wall regression independently reject the candidate.
- The v46 repair root cause did close on its frozen ordinal-19 fixture: V47 used `find`/`rfind` content boundaries, completed in the initial program, and did not repeat the fixed-line assumption. This reliability result does not override the cache/speed gate.
- Terminal disposition: `SPEED-RISK_AND_CACHE-MECHANISM-UNVERIFIED`. No candidate-90, full RULER, LongBench, score, OOLONG, or RAH run is permitted for V47. The README remains on v43.

## V48 preregistration: configured low reasoning for non-root provider turns (offline, no inference)

- Scope/order: speed ladder step 2 only. The initial root remains `gpt-5.6-luna` at `medium`; semantic child calls and same-session repair calls use `low` through the shipped Jcode v0.75.3 `set_reasoning_effort` Harness request. The per-adapter keys are `jcode_reasoning`, `jcode_sub_reasoning`, and `jcode_repair_reasoning` in `assets/config.toml`; no Jcode source or hidden code-side provider setting is modified.
- Lineage: V48 starts from the byte-transparent v46 runtime, does not inherit V47's rejected static-prefix reorder, and carries only the separately mandated generic fixed-line-boundary fail-closed contract/test as a reliability prerequisite. Speed attribution is solely the configured non-root reasoning dial.
- Routing: fresh child sessions are created directly at `low`; a lended root session is reconfigured to the configured child effort immediately before a shared semantic turn; root repair reconfigures the same session to the configured repair effort before consuming an entered provider turn. Reconfiguration errors are typed session-setup failures, do not consume a provider-turn budget, poison the session for bounded cancel/archive, and remain fixed-denominator failures.
- Deterministic protocol evidence: fresh-batch e2e asserts exact `effort=low`; same-session repair e2e asserts the exact sequence `medium, low, low` across initial setup and two repairs; a Unix-pair unit test validates the exact stable Harness request. The diagnosed two-line fixed-index program remains a typed zero-child Assertion with no FINAL publication.
- Fresh-smoke gate: 20/20 execution, zero leaks/timeouts/cleanup failures, and no material wall/token regression versus frozen v43 remain mandatory. Per-turn root/repair usage and the exact frozen config must prove whether any `low` repair was exercised; an all-one-turn/no-subcall smoke can establish non-regression but cannot be labeled an empirical low-reasoning latency win. Candidate-90 remains blocked unless the speed mechanism is exercised or separate preregistered generic evidence demonstrates it without benchmark-specific prompting.

## V48 terminal smoke: low non-root reasoning exercised without a speed/token win

- Frozen candidate: `/private/tmp/azdaja-luna-v48-low-nonroot-reasoning-v2`; binary SHA-256 `401885aef1242859c7b89c269ba857da5ab34a2274ff89cafd25c960870b80ef`; config SHA-256 `a2df34e03fc72aabbea961841fc0cd3b7024cb1b02eca2d7cef89b40a1a0a0f7`; pre-inference source SHA-256 `4256ec4458d4958c7f05422bf12e25268e86f9dbbf43fbbcfa29c00d08fd58fd`; freeze-stamp v2 SHA-256 `ce443a7e360188c5669ce5567978ebcb29c7228b9cb5d3991f2e257cba2a55ae`; unmodified Jcode v0.75.3 SHA-256 `f01c442265d22e9dead7f227b2ec115ab99164e876ff354a72988a9311bf3c4f`.
- Frozen output: `/private/tmp/azdaja-ruler-width4-smoke-v48-low-nonroot-reasoning-v2.jsonl`, SHA-256 `428a49a973f544d465857c7dccda310f1106be79f0f00816e3f23efc94971d09`. Terminal record SHA-256 `4450e5967797638da270eec821acc240c99bef3a2753f6275ef3f54f5a5801bd`. Twenty claim/receipt pairs bind exact row bytes; no score or gold was invoked.
- Execution: 20/20; 22 root turns; two configured-`low` same-session repairs at ordinals 5 and 10; zero subcalls, leaks, timeouts, or cleanup errors. Initial root stayed `medium`; deterministic protocol tests and the frozen adapter config bind repair/subcall effort `low`.
- Performance: makespan 137.259492s; mean 26.514156s; median 22.962568s; p95 45.131297s; total input/output 64,809/39,332. Initial medium roots used 54,126/37,542 tokens and 497.359s provider wall. The two low repairs used 10,683/1,790 tokens, zero cache-read tokens, and 24.263s provider wall.
- Versus frozen v43: makespan +14.63%, mean +21.93%, median +6.50%, p95 +50.50%, input +23.29%, output +23.46%. Non-provider overhead stayed normal at an upper-bound mean 0.433s/item, so there is no controller/setup anomaly to excuse the provider/token regression.
- The smoke proves no execution-accuracy loss on the slice and exercises the low repair path, but it does not show latency or token benefit; switching effort also eliminated the historical same-session 1,792-token cache reads. V48 is terminally rejected. Candidate-90, full RULER, LongBench, scoring, OOLONG, and RAH were not started.

## V49 preregistration: cheaper same-session root repair model (offline, no benchmark inference)

- Scope/order: speed ladder step 3 only. Initial roots remain `gpt-5.6-luna` at `medium`; only depth-0 same-session root repair provider turns switch to configured `gpt-5.4-mini` at `low`. Fresh and repaired-program semantic child turns remain configured `gpt-5.6-luna` at `low`. Prompts, Monty strategy, fixtures, controls, width, caps, and shipped Jcode v0.75.3 are unchanged from V48.
- Fail-closed routing: `set_model` is acknowledged and followed by a runtime-info assertion requiring the requested OpenAI subscription-OAuth route before an entered turn is consumed. A lended post-repair session restores the configured semantic-child model before low-reasoning setup and before child provider entry; already-correct Luna sessions are not repinned. Model/reasoning setup failures poison the session for bounded cancel/archive and record physical `attempt=1` for each distinct logical repair request, including `-repair-2`.
- Configuration/evidence: `jcode_repair_model` is an explicit nonblank adapter key. Schema-v2 traces carry typed `category=turn|repair`; schedules and scorers bind the repair model, accept mini only for depth-0 repair rows, and require Luna for ordinary root and child rows. RULER and LongBench retain legacy default-Luna schedule compatibility; LongBench resume retains legacy frozen-adapter compatibility, while fresh runs require and compare source/frozen repair-model configuration.
- Regression evidence: the same-session mock proves exact root/repair/child route order `Luna/medium -> mini/low -> configured child/Luna-low`, one archive, and category-aware trace rows. Separate tests cover blank repair configuration, pre-entry setup failure and cleanup, category/config rejection, RULER mini schedule reconstruction, transformed LongBench receipts, typed OOLONG JSONL, and legacy LongBench resume behavior.
- Live control-plane evidence only: the zero-inference unmodified-Jcode probe at `/private/tmp/azdaja-v49-live-zero-inference-route-probe-v1.json` (SHA-256 `93a365243aadb3f2cefccf48490fc22c29292b813037babeab1d3f6f27b321aa`) proves route availability, exact mini selection, low reasoning request, archive success, and zero provider turns. It does not establish repair latency, reliability, or post-repair conversation compatibility.
- Fresh-smoke gate remains unchanged: exactly one fresh width-4 20-item RULER smoke after source/binary/controller freeze; require 20/20, zero leaks/timeouts/cleanup failures, at least one exercised mini/low repair, and Luna/low for any repaired-program child. Reject on any execution failure or material wall/token regression versus frozen v43. Candidate-90 and larger suites remain blocked until that gate passes.
- Prefreeze closure: the seven focused regressions fail on the staged pre-fix controller baseline and pass on V49 (proof SHA-256 `f2d7b501c54a8449b9b0b8b8dae17146f6a0d05a4c6173db109a5288e24a9b0b`). The LongBench config/schedule/score/raw-trace path passes end to end (SHA-256 `b1ee6a5535d4830a566a06cffdb9b2d7a223c4f2afcfee3fb7de2872f91c0104`). Final offline gate v2 passed debug/release Rust tests, strict clippy, 24 OOLONG, 35 RULER-run, 34 RULER-score, 38 LongBench-run, and 48 LongBench-score tests; log SHA-256 `b7ba67e565090ca92dd32464211b05ea69927661c492ae34a8386d5f9788e935`. Independent production and focused controller audits both report P0=0/P1=0.

## V49 terminal smoke: same-session mini route failed closed and latency missed the best-candidate bar

- Frozen candidate: `/private/tmp/azdaja-luna-v49-cheap-repair-model-v2`; binary SHA-256 `f1eb69371777dccfdafa1d50b96d20b6b2673703ce88c6a294901c34bcffb5a1`; config SHA-256 `ce900322eff9da6f3e7fac16a76e1e4acfba6f77ca696c7449dfe6301faad12b`; bundle aggregate `d55339284b10c825740572c2426ee919ef78cab638d429710a47a72eb92c4aa0`; freeze-stamp SHA-256 `ad993eaf79b8facddc3f0422caef4884aeb204e4e9c10cef6b0505dca46c5643`.
- Frozen output: `/private/tmp/azdaja-ruler-width4-smoke-v49-cheap-repair-model-v2.jsonl`, 20 immutable rows, SHA-256 `85a932d9362926277bf9f13e5b9b561ad6141028a092cf029c508eddf7ca3894`. Terminal record `/private/tmp/azdaja-ruler-v49-smoke-terminal-record-v1.json`, SHA-256 `00298de1f4cd332b7910d252ad359f39dccd626094a76d23f1eddae1cba53760`. All 20 claims and 20 completion receipts bind exact row bytes; no scorer or gold was invoked.
- Reliability/route result: 18/20 execution. All 20 initial provider turns succeeded on `gpt-5.6-luna`; ordinals 7 and 11 then hit typed Assertion failures and attempted repair. Both `set_model` acknowledgements were followed by runtime-info that failed the required same-session `gpt-5.4-mini` OAuth route assertion, so both repairs failed closed as `SetupRoute` with physical `attempt=1`, zero entered mini turns, and bounded cleanup. This proves the earlier zero-inference fresh-session probe did not establish same-session post-root compatibility. There were zero timeouts, context leaks, semantic children, or cleanup failures.
- Performance: width-4 makespan 143.443818s; mean 27.012876s; median 26.509694s; p95 38.765729s. Twenty successful Luna initial turns used 54,129 input / 39,719 output / 0 cache-read tokens. Versus frozen v43, makespan +19.80%, mean +24.22%, median +22.96%, p95 +29.27%, input +2.98%, and output +24.67%.
- Terminal disposition: `REJECTED_RELIABILITY_LATENCY_AND_MECHANISM_GATE`. V49 missed 20/20, exceeded the current-best v43 119.739380s makespan bar, and entered no mini repair provider turn. No retry, resume, candidate-90, full RULER, LongBench, OOLONG, or RAH is permitted for V49. Frozen v43 remains the headline candidate.

## V50 step-4 feasibility: provider connection/session reuse is unsupported under fresh-context isolation

- Scope was offline-only against clean Jcode v0.75.3 source commit `fd1ff012cd463c413d53a3de358ceb7a7b8459a2` and the exact installed binary SHA-256 `f01c442265d22e9dead7f227b2ec115ab99164e876ff354a72988a9311bf3c4f`. No candidate was built or frozen; no inference, benchmark, scorer, or gold access occurred. Evidence record: `/private/tmp/azdaja-v50-step4-connection-session-reuse-offline-no-go-v2.json`, SHA-256 `1ba56aac6ba44e50dbb0c32db42d62b983c0027ba07049ff535255a6b978fd31`.
- The stable bridge holds one attached session at a time on each API/legacy connection; `attach_session` can rebind that same connection to an existing session. This does not carry the old provider WebSocket into a fresh isolated target: a live target uses its own Agent/provider, while an empty non-live target restores into the connection provider but its next first-root input is non-growing, so the shipped provider clears `persistent_ws`. A fresh daemon client likewise forks the OpenAI provider with `persistent_ws=None`, and Jcode `clear` creates a fresh Agent/session ID but also makes the next root non-growing. Skipping clear or fresh-target rotation preserves prior response-chain/transcript context. No stable request resets only the response chain while retaining the socket.
- The frozen v43 smoke has 434.922781 summed item seconds, of which authoritative provider spans account for 426.826000s (98.14%). The entire non-provider item envelope is 8.096781s, mean 0.404839s/item. In fixed-order width-4 list scheduling, deleting all of that envelope—not just bridge startup—saves at most 1.961661s, or 1.64% of the frozen 119.739380s bar. The corresponding generous v49 ceiling is 2.006369s/1.40%. Fresh-session transport reuse changes no provider input and has zero causal token benefit.
- Adjacent unsupported ideas do not create a candidate: the stable subscription-OAuth API has no per-turn output/verbosity/response-format/cache-key control; early cancellation has no server-validated complete-program boundary before `TurnDone`; repair-only tuning has zero causal opportunity on v43's zero-repair bar slice; and service-tier/transport settings are daemon-global rather than candidate-scoped and frozen.
- Disposition: speed-ladder step 4 is `NO_GO`, and no V50 is manufactured from a micro startup bound with larger isolation/evidence risk. V43 remains frozen headline evidence; V44-V49 remain terminal and untouched. Candidate-90, LongBench, OOLONG, and RAH remain blocked. A material next mechanism requires separately authorized relaxation of at least one current constraint.


## V43 trace-receipted top-five latency ledger and authorized attack order

The immutable ledger is `/private/tmp/azdaja-v43-top5-latency-ledger-draft.json`, SHA-256 `4375cf1bb930f2024cc7efdc02bed522992ff164e76dce617707793dfc51188b`. It binds every candidate row to retained `AZDAJA_MODEL_TRACE` schema-v2 and `AZDAJA_SOLO_TRACE` bytes: 20 smoke, 90 full-RULER, and 63 LongBench items; all 173 trace pairs match, all 110 RULER controller-ledger receipts match, and the additive partition has zero negative residuals. Medians below are ordinary item medians with zero-duration items retained; no cell percentiles are inferred from aggregates.

| frozen v43 cohort | recorded total median ms/item | initial depth-0 `turn` median ms/item (turns/item median) | sub-call wall median ms/item (calls/item median) | repair median ms/item (events/item median; conditional nonzero) | snapshot I/O median ms/item | exact residual median ms/item |
|---|---:|---:|---:|---:|---:|---:|
| RULER smoke-20 | 21,560.276 | 21,223 (1) | 0 (0) | 0 (0; n/a) | 0.186 | 374.610 |
| RULER full-90 | 22,520.093 | 22,078 (1) | 0 (0) | 0 (0; 16,082 across 4 nonzero items) | 0.147 | 362.365 |
| LongBench candidate-63 | 51,429.212 | 30,969 (1) | 6,461.233 (2) | 0 (0; 34,327 across 25 nonzero items/41 events) | 1.637 | 569.293 |

For smoke, initial root inference is 21,223ms against a 21,560.276ms item median (98.44% ratio of medians); its summed 426,826ms is 98.14% of summed item wall. Thus transport, session reuse, and snapshots are closed unless a later ledger makes one exceed 10%. The authorized one-mechanism sequence is: (1) reduce root turn count through a generic one-cell `load -> single exec: select -> llm_batch -> FINAL` trajectory and report turns/item before/after; (2) only separately, test byte-identical static-prefix cache hits plus shipped-config low/minimal effort on repairs/sub-calls, requiring streamed cache-read receipts and smoke accuracy; (3) only separately, remove non-load-bearing solo contract/envelope tokens without adding strategy. No implementation is authorized until its preregistration names the attacked term, current milliseconds/item, and projects >=10% median improvement.

## Fresh exact-v43 LongBench controller preregistration

The fresh schedule binds a generated legacy repair capability receipt only when the exact config lacks `jcode_repair_model`: exact config must make `azdaja list` exit 0 silently, the Luna-key-augmented config must exit 2 with the typed unknown-field diagnostic, neither probe may create a model trace, and candidate/binary/config hashes must match source, frozen snapshot, schedule, scorer, and held ceremony. This changes no v43 byte or strategy. The derived gate is also frozen in the schedule as `end_to_end_official_plus_exact_bare_lf_correct`, fixed denominator 63, minimum 16: the pinned official extractor runs unchanged first, then and only then `re.fullmatch(r"([A-D])\n", response)` may recover a label. Official LongBench fields and claims remain independent and authoritative as official metrics.


## Root-latency floor: ordered V52-V54 mechanism closure

The user-ordered speed campaign is closed without manufacturing a candidate. The combined immutable closure is `/private/tmp/azdaja-v52-v54-root-latency-mechanism-closure-v1.json`, SHA-256 `33be3d4c9eeaf77d180ca268d21d28b1a8f6d0274c4b546c7f9b0911162c26fd`. All three decisions use the trace-receipted v43 ledger SHA-256 `4375cf1bb930f2024cc7efdc02bed522992ff164e76dce617707793dfc51188b`, whose smoke floor is 21,223ms initial-root median against 21,560.276ms total median. A candidate needed a causal projection of at least 2,156.028ms/item (10% total median) before implementation.

1. **V52 trajectory shape — NO-GO.** All 20 smoke rows already have one initial provider turn, one authored exec, zero repairs, and zero subcalls. The proposed `load -> one exec -> FINAL` shape is already the observed median and every-row shape; moving the mandatory planner call to a child does not remove a provider round trip. Record `cab13b98ef363f3396bc6465d132cc6e10d3feddf874c58f085c90b1bdb9a2c7`; independent audit passed.
2. **V53 cheaper turns — NO-GO.** V47's 3,328-byte static Azdaja prefix received zero fresh-root cache reads because Jcode inserts varying per-session UTC/cwd context first and ChatGPT OAuth omits explicit cache keys. Exact-v43 smoke also has zero repair/subcall exposure, so low/minimal effort has zero causal opportunity. Projected saving is 0ms/item. Record `26d098682260837bafcb93e7c0979da62775fe45224302d77415a7036476aba2`; independent audit passed.
3. **V54 shorter turns — NO-GO.** Exact static contract weight is 2,811 chars / 554 o200k diagnostic tokens (diagnostic segment accounting, not provider-authoritative). Only 130 chars / 19 tokens are arguably redundant. Observationally generous bounds project 13.47-50.93ms/item; even the invalid all-static deletion upper bound is 1,485.09ms/6.888%, below the gate and destructive to load-bearing exactness/reliability text. Record `689705f91e68dd6773f8f6c0fbc94f9c5bbaa52b68ebf59df83ab2eb5acabf38`; independent audit passed.

No V52, V53, or V54 candidate, build, smoke, score, gold access, source mechanism edit, or downstream suite exists. Transport, session reuse, snapshots, service tier, and these three root mechanisms are closed. The speed-candidate workstream is terminal by user decision.

## Exact-v43 fresh LongBench terminal-invalid floor

Run `/private/tmp/azdaja-lb2-v43-refresh-v1` completed the entire frozen schedule before refusal: 189 canonical result rows, 189 claim receipts, 189 done receipts, and exact retained artifacts. Output SHA-256 is `1578d7a38200f0c7631f90f17bc7b233f735af6b0ecd0792f540b1cc66fe3062`; schedule SHA-256 `f7de7ed119347a9cea27ace3bb9cc1b7a6879e781a6e50da5f8c014ba68d4249`; schedule ID `b419be9844d635169642945ee1f20306dc4b276e3beedcd0c3b0d8265c10a908`; terminal closure SHA-256 `cf9cac65ef28cbdada293d8b7e82d4159d8c261ae430416d2a618367ca9c4915`. Execution was Azdaja 48/63, native 63/63, Prime 57/63.

The frozen validator SHA-256 `8466b39a0a60bbd10ae7762af283cfa028977ea92ecd6c7c103a632e9d647c81` stopped before gold access because it compared each model-trace object to sorted-key `canonical_json_file_bytes`, whereas Rust `serde_json` emits compact duplicate-free struct-field order. All 247/247 retained Azdaja trace lines parse as duplicate-free schema-v2 known-field JSON; 246 succeeded and one typed depth-1 timeout was followed by a successful degraded retry. The latter exposed a second frozen omission: only session-setup failures were accepted. Independent audit found complete inference closure and exact artifact receipts, but the pre-frozen acceptance predicate controls. Protocol disposition is permanently terminal-invalid and unscored: no post-hoc authoritative salvage, no gold opening, no retry/resume/replay, and no OOLONG authorization. A generic future validator correction and mandatory pre-freeze synthetic-gold dress rehearsal are separate new protocol work and cannot relabel this run.


## Two-speed benchmark operation (effective 2026-08-14)

Benchmark iteration now has exactly two modes; neither changes candidate semantics, output bytes, models, or the frozen-score contract.

### SCOUT

SCOUT is fast, disposable, and gold-blind. It may use any existing slice size and exists only to answer directional execution, recognition, latency, or token questions. A scout has no receipts, frozen schedule binding, protocol audit, gold access, authoritative score, promotion authority, or publication path. Its results may be recorded only in `PERF.md`/`FAILS.md`, never in README headline tables.

A candidate may enter a future frozen LongBench run only after the existing 20-item scout slice records **20/20 execution** and **at least 17/20 (85%) gold-blind extractor recognition**. Recognition means `execution_success` plus a non-null prediction from the existing preregistered derived extractor: pinned official extraction first, then only `re.fullmatch(r"([A-D])\n", response)`. It makes no correctness claim.

### FROZEN

FROZEN retains the complete version-bound schedule, receipts, artifacts, terminal no-gold validator, scorer, fixed denominators, and immutable evidence rules. It is reserved for candidates that already cleared SCOUT. The already-launched exact-v43 189-row freeze is explicitly grandfathered: its execution/recognition rates are known, it runs to terminal completion regardless of checkpoints, and its deliverable is a score.

### Mandatory gold-blind early aborts after v43

Both modes use the candidate arm first within each checkpoint window so the signal arrives before controls. Checkpoints count cumulative scheduled `jcode-azdaja` rows, not total three-arm rows:

- after 10 Azdaja rows: abort if execution is below 8/10 **or** recognition is below 7/10;
- after 30 Azdaja rows: abort if cumulative execution is below 80% (fewer than 24/30) **or** recognition is below 75% (fewer than 23/30).

An abort opens no gold. It immediately records per-row execution failure kinds plus recognized/unrecognized output taxonomy, stops unscheduled work, and returns to iteration. Correct/wrong taxonomy remains impossible until a terminal frozen validator authorizes scoring. No retry, resume, selective completion, headline result, or promotion may be derived from an aborted run.


## Exact-v43 LongBench refresh v2 authoritative score

The mandatory fixed 20x3 synthetic rehearsal exited 0 and produced terminal score evidence before the new freeze. The new exact-v43 freeze then completed exactly 189/189 inference rows and 378/378 claim/done receipts under schedule `0a7d3021442d2b449cac9c99179a60214a1239645cd000f088289d21540b144d`. Terminal no-gold validation passed; runner exit 1 is its documented successful-terminal-with-execution-failures status. Frozen output SHA-256: `96ae71df5299d8c8a394d12531baa208f546d8b8f70e5b2d295e6424128eaa0e`; schedule SHA-256: `422ad89b6b59bae00068a40733e62eceef5a2bfc79a6bc8f7163f8b709a34359`; report SHA-256: `5997a69808ab4acd8a688245d53d9b468d8bc92ff4f6c86015d63f0905eee13a`.

| Arm | Execution | Official fixed-63 | Derived envelope fixed-63 | Root-token p50 | Latency p50 all attempts |
|---|---:|---:|---:|---:|---:|
| Azdaja exact-v43 | 45/63 | 17/63 | **24/63 (PASS >=16)** | 7,965 | 53.670s |
| Native jcode | 63/63 | 36/63 | 36/63 | 42,141 | 20.840s |
| Prime Agent | 57/63 | 11/63 | 11/63 | 8,700 | 36.398s |

Azdaja derived taxonomy: 24 correct, 20 recognized/wrong, one extractor-unrecognized, and 18 execution failures. Official completed-only accuracy is 17/45; strict exact is 0/63. All-attempt Azdaja total-token p50 is 25,515 and recorded total is 1,818,756. The derived gate passes, but the 71.43% execution rate and 2.58x native median show why v43 is only the frozen baseline and why future candidates must clear SCOUT before any freeze. Same-binary OOLONG launched immediately after scoring.


## Exact-v43 frozen OOLONG terminal result

The same exact-v43 aggregate ran on the fixed 26-fixture / 78-row OOLONG-Synth validation campaign after LongBench authorization. Terminal report validation exited 0; output SHA-256 `6f6a9c524b69ef16ef9eb8b85b375b2caeddae6c1226d53dda9675dffcbf5bfd`, schedule SHA-256 `7970cbae26e55c62058bb431dfafd1540b64e8176ddce3e050f9d776c5ae14ef`, score rows SHA-256 `869ae46012875f3d7df8154af9af1d7572ee3dd6ffba9e1326940024b8aa090e`, report SHA-256 `80bad59b241064b6430f4c56c1f9f114c4c82fdf564483b74906c4e43c8acfec`.

| Arm | Execution | Fixed-26 exact | Root input mean | Total tokens | Latency p50 |
|---|---:|---:|---:|---:|---:|
| Azdaja exact-v43 | 22/26 | 19/26 | 6,166 | 403,897 | 31.338s |
| Native jcode | 26/26 | 22/26 | 30,382 | 2,802,109 | 9.691s |
| Prime Agent | 26/26 | 20/26 | 2,278 | 437,594 | 11.985s |

Azdaja's four execution failures normalize to `monty_subset_tax`; three additional completed rows failed strict scoring. Zero of 26 root transcripts leaked >=100 context characters. It missed the frozen 25/26 execution and 24/26 exact gates, so RAH is blocked. On both-correct rows Azdaja/native geometric ratios were 0.218x root tokens, 0.133x total tokens, and 1.519x latency; overall median latency was 3.23x native.


## Ultra-fast constraint frontier after exact-v43 scoring

The current best 20-item RULER smoke has total p50 21,560.276ms and initial Luna/medium root p50 21,223ms: **98.44%** of item latency. Non-provider residual plus snapshots is only 374.796ms, so deleting all product-side work projects 1.738%, not the required 10% (2,156.028ms).

Across retained RULER, LongBench, and OOLONG traces, successful root latency is almost entirely provider output generation: R² 0.991/0.998/0.999 and roughly 12ms per billed output token. A compact local plan/DSL cannot clear the gate: the exact diagnostic median visible reply is 169 o200k tokens, and physically deleting every visible token projects only 2,126.426ms / 9.863%, while a usable grammar saves less and cannot remove hidden medium-reasoning tokens.

A cross-fixture dual-flight estimate initially appeared to exceed 10%, but conditioning on RULER's actual repeated `task x target_length` strata corrects it to 22.520s -> 20.612s, only **8.47%**, so dual flight is also a latency NO-GO. Triple flight projects 17.541s / -22.11% on the same-stratum order statistic, but can approach 3x provider tokens, repeats physical work, and selects stochastically by first success. It is rejected because the active objective requires materially better token numbers as well as latency and because conservative attempt policy disallows hiding duplicate attempts. Immutable projection erratum SHA-256 `efe3b7e719246b8d1570016d6791ff008938e8dc65985ba396a479bfb1e59d0e`.

Result: no defensible generic single-trajectory >=10% mechanism remains under unchanged Luna/medium plus unmodified Jcode. The only clean frontier move is a separately authorized gold-blind SCOUT of Luna **low** root reasoning (or a faster root model), retaining the 20/20 execution, >=17/20 recognition, >=10% latency, lower-token, and early-abort gates. No such inference had yet been launched. Evidence record SHA-256 `a2a7f082a18aa661cd7dffeb42f4c79c76ee8ceacd46e34be830546dc54d9c04`.


## SCOUT Luna/low root v1 — checkpoint-10 rejection

This disposable, gold-blind SCOUT changed exactly one candidate setting from exact-v43: `jcode_reasoning = "medium"` to `"low"`. It retained exact-v43's `SKILL.md` and binary byte-for-byte, used unmodified Jcode v0.75.3 through subscription OAuth, and produced candidate aggregate SHA-256 `5fbd279c778691d1c57018ea5c1a3613469b58850269e572ad421e1f87693216` (binary `6be5b9ff567eca6d1a5c2315dfb0c12fb5bd847b58daef0b3b8191151e45b509`, config `ca3f153c8a5a80c3727473fea90452ade5c556a24d026fb54084257791fd8eb8`). The existing public 20-item LongBench SCOUT slice was selected without gold; only its first 10 candidate rows ran because checkpoint 10 was terminal.

| Same 10 public fixtures | Execution | Gold-blind recognition | All-attempt latency p50 | Total tokens | Token p50 |
|---|---:|---:|---:|---:|---:|
| exact-v43 Luna/medium retained baseline | 8/10 | 8/10 | 52.775s | 263,776 | 26,422 |
| disposable Luna/low SCOUT v1 | **3/10** | **3/10** | 27.567s | 246,782 | 13,838 |

The low-root direction cut all-attempt median latency 47.77%, token p50 47.63%, and aggregate tokens 6.44% on this aborted window, but reliability collapsed. All seven failures normalized to `monty_subset_tax`; their exact raw responses were empty. The three executed rows were all recognized by the preregistered gold-blind extractor, so taxonomy is three executed-and-recognized, zero executed-but-unrecognized, and seven execution failures. All ten runs retained byte-transparent stdout, asserted the Luna OAuth route with reasoning `low`, used fresh isolated task/session state, had zero >=100-character root-context leaks, and reported zero cleanup errors.

The mandatory 8/10 execution and 7/10 recognition checkpoint failed at 3/10 and 3/10. The controller therefore stopped immediately: rows 11-20, all control inference, gold access, scoring, retry, FROZEN promotion, and publication were not attempted. Frozen v43 evidence was read-only and unchanged. The disposable directional results JSONL has SHA-256 `003fc64aaff709674056ee6f22b2131db94d2536b879603919e053e0e48f6fe3`; it is not a receipt, schedule, score, or promotable artifact.


## SCOUT Luna/low root v2 — generic envelope guidance still rejected

A second disposable candidate kept Luna/low and added one 896-character generic solo instruction: preflight semantic item size, derive faithful task-anchored evidence instead of sending an oversized whole document, represent a single choice as one item with alternative labels, and keep banned introspection out of repairs. Candidate aggregate SHA-256 is `8f3e193e85fbab51dcbbd183678174e753428cd2fb2ea8a4143603e88d108633`; its binary and config are unchanged from SCOUT v1, and its SKILL SHA-256 is `bbc100feff440392afeae625eb622e53fe0ca2fa4317f4c331d19837d2acbc1d`. It used the same first checkpoint window, without gold or controls.

| Same 10 public fixtures | Execution | Gold-blind recognition | All-attempt latency p50 | Total tokens | Token p50 |
|---|---:|---:|---:|---:|---:|
| exact-v43 Luna/medium retained baseline | 8/10 | 8/10 | 52.775s | 263,776 | 26,422 |
| disposable Luna/low SCOUT v2 | **6/10** | **6/10** | 30.308s | 300,400 | 20,020.5 |

All six executed outputs were recognized and all four failures normalized to `monty_subset_tax`: three still exceeded the semantic item envelope after repairs and one supplied invalid helper labels after repairs. Typical latency and token p50 improved 42.57% and 24.23%, respectively, but total tokens regressed 13.88%; reliability remained below both checkpoint thresholds. Zero rows leaked >=100 context characters and zero reported cleanup errors.

The 8/10 execution and 7/10 recognition checkpoint again forced an immediate abort at 6/10 and 6/10. Rows 11-20, controls, gold, scoring, retry, FROZEN promotion, and publication were not attempted. Directional results JSONL SHA-256 is `b9bc67cf90b2050466fe5d38c3511fc2b303f195aa8a03ba93c60189d8b74064`; it carries no receipt, schedule, score, or promotion authority.


### Causal erratum: SCOUT v2 guidance was not on the solo inference path

Post-run trace inspection found that `azdaja solo` constructs its root request from text compiled into the binary; the staged `SKILL.md` is not interpolated into that request. None of v2's added 896 characters appears in any retained root request. Because v1 and v2 used the same binary, config, model, and effective solo prompt, v2 is only an independent stochastic Luna/low repeat, not a causal test of the proposed envelope guidance. Its 6/10 execution, 6/10 recognition, latency, token, and mandatory-abort observations remain exact directional facts, but the apparent improvement over v1 cannot be attributed to the SKILL edit. Any real retrieval/envelope mechanism must change the compiled generic solo protocol or runtime helper and receive a new candidate identity.


## SCOUT V55 Luna/low + native lexical relevance — promotion-impossibility abort at 10

V55 is the first causal low-root retrieval candidate. Starting from exact-v43 source commit `6588c06`, it adds a compiled, solo-only native `lexical_relevance` helper: deterministic integer chunk-document-frequency ranking, verbatim Unicode character ranges, explicit omission metadata, a 20,000-character serialized evidence cap, no provider calls, and no availability in ordinary `exec`. Its compiled root contract permits it only for relevance-local semantic work and forbids exact/exhaustive use. Candidate source commit is `40f9819beeab9348b0a88b0af1f57ce7cc3fb619`; source patch SHA-256 `28c797b7960beb3967832655d65705414d160c69394d77f9fd4f6e262cc78ce2`; candidate aggregate `f1c38aeebdf0dbe839fdbc37cd651e6fc21b412f66e794af795a661dd7a359fe`; binary `5852be035329b547e14416c14db14d0b2ec43c0449582febe345a336b7d4409e`. The only config change from exact-v43 is root reasoning medium to low.

Before inference, full locked tests passed, strict clippy passed, a 16M-character release stress completed in 0.56s, and an independent source audit found no P0/P1. A gold-blind local diagnostic constructed capped views for all 20 public SCOUT contexts; per-item helper time was 69-954ms (median about 153ms), with exact output ranges and no provider calls. This quantified a credible path below the retained 52.775s / 263,776-token same-10 baseline.

| Same 10 public fixtures | Execution | Gold-blind recognition | All-attempt latency p50 | Total tokens | Token p50 |
|---|---:|---:|---:|---:|---:|
| exact-v43 Luna/medium retained baseline | 8/10 | 8/10 | 52.775s | 263,776 | 26,422 |
| disposable V55 Luna/low native relevance | **8/10** | **8/10** | **19.799s** | **175,571** | **16,134** |

V55 cut median latency 62.48%, aggregate tokens 33.44%, and token p50 38.94%. All eight executed outputs were extractor-recognized. The native helper appeared in model-authored code on 9/10 rows. The two failures normalized to `monty_subset_tax`: row 7 never invoked the helper and still sent oversized evidence after both repairs; row 9 invoked it but a later repair supplied non-list labels. Zero rows leaked >=100 context characters and zero reported cleanup errors.

V55 exactly met the mandatory checkpoint-10 floors (8/10 execution, 8/10 recognition), but two failures made the required 20/20 full-SCOUT execution gate mathematically unreachable. The run therefore stopped at 10 rather than spending on non-promotable rows 11-20. No controls, gold, scoring, retry, FROZEN promotion, merge to main, or publication occurred. Directional results JSONL SHA-256 is `01449dc6e41c76e54aae061e56cc55166795b9d5879f2353f637019ba8c5390c`; it is not a receipt, schedule, score, or promotion artifact.


## SCOUT V56 mandatory native relevance — 19/20 near miss

V56 retained V55's audited native helper and changed only the compiled generic root contract in response to observed failures: relevance-local semantic sources above 30,000 characters must use the helper before `semantic_manifest`, and the helper labels argument must be a Python list rather than a dictionary or set. Source commit `a0f3085fc00f2cb045cf73847286397d49e93937`; source patch SHA-256 `08752e873c726b48f551cb0b62f753b74d8f79f77c97aee41897ef4ac02e0e30`; candidate aggregate `0a1869917b6cb67fd83c2885cfd5a8a95d9f5129ba5ab9d94e0313c37c21e623`; binary `857d1f2f5991761876cd78849e1bcf2905af0c901709f0d4b13534f3091fe2b3`. Full locked tests and strict clippy passed before inference.

Checkpoint 10 passed at 10/10 execution and 10/10 recognition, with 26.589s median latency (-49.62%) and 250,037 total tokens (-5.21%) against the same-10 retained medium baseline. The unchanged candidate therefore continued through the full 20-item SCOUT.

| Same 20 public fixtures | Execution | Gold-blind recognition | All-attempt latency p50 | Total tokens | Token p50 |
|---|---:|---:|---:|---:|---:|
| exact-v43 Luna/medium retained baseline | 15/20 | 15/20 | 49.697s | 491,575 | 25,087.5 |
| disposable V56 Luna/low mandatory relevance | **19/20** | **19/20** | **22.884s** | **446,557** | **21,603** |

V56 improved median latency 53.95%, aggregate tokens 9.16%, and token p50 13.89%. All 19 executed outputs were recognized. Model-authored code referenced the native helper on 19/20 rows; the short direct-answer row also executed and was recognized. Zero rows leaked >=100 context characters and zero reported cleanup errors.

The sole row-18 failure normalized to `monty_subset_tax`. The initial program correctly called the helper but requested nonexistent `view["text"]` instead of the documented `view["evidence"]`; its repair then discarded the helper result for forbidden head/tail slicing and used four independent correct/incorrect items, producing two winners and failing closed. This is an observed generic API/choice-shape instruction failure, not a provider, OAuth, helper-runtime, envelope, or cleanup failure.

The required full-SCOUT gate is 20/20 execution, so 19/20 is a rejection despite clearing recognition, latency, and token gates. No retry, controls, gold, scoring, FROZEN promotion, merge, or publication occurred. Directional results JSONL SHA-256 is `baee329a45630945387a4665ef5373bbd1fb4792a555884508cbf8fa8b280f64`; it carries no receipt, schedule, score, or promotion authority.


## SCOUT V57 pinned evidence/joint-choice contract — abort at 9/10

V57 changed only the compiled generic contract after V56's observed failure: use exactly `view["evidence"]`, retain the helper result during Key repairs, forbid arbitrary head/tail replacement, and represent one choice as one semantic item rather than independent correct/incorrect items. Source commit `61c5e9fbf984a45ca1ad365dab70d5edc152a4f0`; source patch SHA-256 `ed55d405dcaa69def85f6e1216d1e5699a2725618d2867850a5fc9f9005ef324`; candidate aggregate `c7b81dc4a8dd93bf1dc5804072598e1c8ec27b6c76165dd8e07bba5f1119ca49`; binary `1ca9d3b5f71dad2c9e03edfaf66ddcf6d6273f39f2fb77cbf84c7c11f3da5944`. Full locked tests and strict clippy passed.

| Same first 10 public fixtures | Execution | Gold-blind recognition | All-attempt latency p50 | Total tokens | Token p50 |
|---|---:|---:|---:|---:|---:|
| exact-v43 Luna/medium retained baseline | 8/10 | 8/10 | 52.775s | 263,776 | 26,422 |
| disposable V57 Luna/low joint relevance | **9/10** | **9/10** | **17.463s** | **206,958** | **20,873.5** |

V57 improved median latency 66.91%, aggregate tokens 21.54%, and token p50 21.00%. All nine executed outputs were recognized, every row called the native helper, and zero rows leaked >=100 context characters or reported cleanup errors.

The sole row-9 failure correctly used one item and the documented evidence key, but supplied the four full alternative texts as semantic labels. The dual-manifest provider could not reliably reproduce those long labels in the strict `ID|LABEL` wire format; the malformed primary retry failed `invalid label manifest` after semantic child calls, so conservative no-repair-after-evidence policy stopped the row. The next generic correction is to require compact stable alternative identifiers as labels while keeping full alternative text in evidence/task.

Although 9/10 clears the mandatory checkpoint floor, one failure makes 20/20 unreachable, so rows 11-20 were not run. No controls, gold, scoring, retry, FROZEN promotion, merge, or publication occurred. Directional results JSONL SHA-256 is `f1fb411bc7a3d51eb825c49394f2c17760be99ccac202f30feeacea7b0771cc5`; it has no receipt, schedule, score, or promotion authority.


## SCOUT V58 compact-choice native relevance — full 20-item PASS

V58 changed only the compiled generic contract after V57's observed wire failure: a one-of-K semantic choice must use compact stable alternative identifiers as labels, while full alternative text stays in evidence/task. It retains the same audited native helper and Luna/low config. Source commit `f6e024aac58783d8a723c5a2f722037b8452fd59`; source patch SHA-256 `ab3bcdefb2bfb2339627fe4531466fbdeb51294043440272376d12e276a762c8`; candidate aggregate `0fb0c6b52e5ad22dc1ea7b12bd44ff264c728e1df55f7c5b3746f6e08283d5cf`; binary `1d1e70b4e8720792553e89726a33472825d55a2365a504744cf9a747697c3224`. Full locked tests and strict clippy passed before inference.

Checkpoint 10 passed at 10/10 execution and 10/10 recognition, 17.926s latency p50 (-66.03%), and 203,971 total tokens (-22.67%) against the same-10 retained medium baseline. The unchanged candidate continued to the full 20-item SCOUT.

| Same 20 public fixtures | Execution | Gold-blind recognition | All-attempt latency p50 | Total tokens | Token p50 |
|---|---:|---:|---:|---:|---:|
| exact-v43 Luna/medium retained baseline | 15/20 | 15/20 | 49.697s | 491,575 | 25,087.5 |
| disposable V58 Luna/low compact relevance | **20/20 PASS** | **20/20 PASS** | **17.970s** | **378,572** | **17,681** |

V58 cleared every preregistered SCOUT gate: 20/20 execution, at least 17/20 recognition, median latency -63.84%, aggregate tokens -22.99%, and token p50 -29.52%. Nineteen rows used the native helper; one short direct-answer row remained valid. Every exact raw output was recognized by official extraction or the sole fullmatch bare-letter fallback. All rows used fresh isolated sessions and the subscription-OAuth Luna/low route, with zero >=100-character root-context leaks and zero cleanup errors.

This is gold-blind execution/format evidence, not correctness or benchmark superiority. No gold, scoring, controls, retry, README headline, public release, merge, or publication occurred. V58 is now SCOUT-qualified for a genuinely fresh immutable FROZEN campaign using the exact unchanged candidate; it is not yet promoted. Directional results JSONL SHA-256 is `f825a1b5265a96cbb9afdd2c180902e9e231cbec1664ceb346a193ab701cf6cf`.


## V58 FROZEN LongBench-v2 preregistration — Luna/low, candidate-first v1

The exact SCOUT-qualified treatment is immutable for this campaign: candidate aggregate `0fb0c6b52e5ad22dc1ea7b12bd44ff264c728e1df55f7c5b3746f6e08283d5cf`, binary `1d1e70b4e8720792553e89726a33472825d55a2365a504744cf9a747697c3224`, SKILL `c4990d75786c2c9a822abeb4d905fdc70ee129dcaf39df444568d77792015c0d`, config `ca3f153c8a5a80c3727473fea90452ade5c556a24d026fb54084257791fd8eb8`, source commit `f6e024aac58783d8a723c5a2f722037b8452fd59`, and base-to-candidate patch `ab3bcdefb2bfb2339627fe4531466fbdeb51294043440272376d12e276a762c8`. The treatment remains on the private `candidate/v58-low-relevance` branch and is not merged or promoted.

The fresh campaign is fixed to public manifest `4fb02fc769badfe6aafd84f4cc38bc8f77f71d93671613788650a63b2031876f`, `gpt-5.6-luna`, reasoning `low`, seed `20260813`, timeout 1,800 seconds, one repetition, and the unmodified Jcode v0.75.3 binary `f01c442265d22e9dead7f227b2ec115ab99164e876ff354a72988a9311bf3c4f`. Final controller code is private-main commit `10cb4ea3f649f56c44f87c6944e006c9fe7262ee`: `run.py` `129bd6d3201bb2f7d5a29d17f22566268ca5ea0b6548f2788810f7e6fa8738bc`, `score.py` `f4f2344d265a19f1bd98e18344f1186a770798f69a16ec0a618fc9e518093706`, `rehearsal.py` `28013e55f9ca3927497b0969ae910df2e85ae80a5e6e42809822f421f1da84f8`, and shared adapter `3e7d27fed90c654bce4cd00754da3ee9959161ab991056ab097c36712846d0b3`. LongBench discovery passed 113/113; independent source and controller audits found no P0/P1 and returned GO.

Before inference, one fresh target-bound 20x3 offline rehearsal must complete and verify against those exact bytes. Production publishes one immutable 189-job schedule. After one seeded fixture shuffle, order is candidate rows 1-10, their 20 controls, candidate rows 11-30, their 40 controls, remaining 33 candidate rows, then their 66 controls: exact candidate ordinals 1-10, 31-50, and 91-123. At candidate count 10, abort permanently below 8 execution or 7 gold-blind recognition; at candidate count 30, abort permanently below 24 execution or 23 recognition. Recognition is execution success plus the pinned official extractor, then only `re.fullmatch(r"([A-D])\n", response)`. Exit 3 is a policy abort: retain/hash the ordinary rows, claim/done files, and artifacts, emit the response-free taxonomy, and never resume, retry, score, open gold, relabel, or promote that run.

If both checkpoints pass, the same prepublished schedule continues unchanged. Only exact terminal completion—189 rows, 189 claims, 189 done receipts, 189 artifact directories, and the schedule-bound no-gold validator—permits one fresh scoring invocation. Fixed denominators remain 63 per arm; official scoring is unchanged; the separate preregistered derived gate remains at least 16/63 using `end_to_end_official_plus_exact_bare_lf_correct`. The encrypted gold image stays detached through rehearsal and inference. A terminal score is evidence, not automatic promotion or a downstream-suite authorization.

Capacity was restored to 11 GiB free by deleting only regenerable Cargo target trees; no frozen campaign artifact was removed. No FROZEN run root, schedule, receipt, inference row, control, gold access, score, merge, release, publication, or headline claim existed at preregistration time.


### V58 target-bound pre-freeze rehearsal — PASS

Fresh bundle `/private/tmp/azdaja-v58-lb2-prefreeze-shared-v1/bundle` completed and independently reopened with exit 0. Final receipt SHA-256 `b0c4b67d960e0e5479c80e715bfe0c09139223e24c7de9fe25efbc3bcd28b7aa`, receipt ID `096ee4003ed7f2ea1a2c2c798818811cfde3c4c3d7a8c7453ca1b00df773efc1`, target SHA-256 `28b14daef7daed598dd2959ebe46ee52c2ff820c2d934a90b5070a24db2a85a5`, and bundle-inventory SHA-256 `d22141bcbc2aada3a71ada4fe67cab8939b014902b9ee8eb490dd65bc4abfdb7`. The receipt binds the exact V58 aggregate, Luna/low production configuration, manifest, Jcode, controller, scorer, adapter, rehearsal code, Prime/Node/kernel closure, 189-job target, and 16/63 derived gate. Its synthetic cohort has 60 rows, 60 claims, 60 done receipts, and 60 artifact directories. It is explicitly offline, OAuth-free, inference-free, and not a benchmark result. Gold remained detached. The exact bound candidate/controller may now enter one fresh production invocation under the preregistered checkpoint policy.


## V58 FROZEN LongBench-v2 — terminal score PASS

The exact preregistered Luna/low candidate ran once at `/private/tmp/azdaja-v58-lb2-frozen-v1`. Both gold-blind checkpoints passed: 10/10 execution and recognition at candidate count 10; 26/30 execution and recognition at candidate count 30. The immutable schedule then completed with runner exit 1, meaning terminal completion with explicit failure rows rather than controller error. Independent no-gold validation accepted exactly 189 rows, 189 claims, 189 done receipts, and 189 artifact directories before the encrypted gold image was attached. The frozen scorer was invoked exactly once, exited 0, and the image was immediately detached.

| Frozen Luna/low arm, fixed denominator 63 | Execution | Official correct | Derived envelope correct | All-attempt latency p50 | Total-token authority |
|---|---:|---:|---:|---:|---|
| V58 Azdaja | **58/63** | **17/63** | **24/63 PASS** | **18.045s** | 1,127,460 recorded across 59/63; 4 missing |
| native Jcode | 63/63 | 34/63 | 34/63 | 14.542s | 2,440,035 unconditional |
| Prime Agent | 57/63 | 11/63 | 11/63 | 29.261s | 1,256,632 unconditional |

Against the authoritative exact-v43 Azdaja freeze, V58 preserves the exact official result (17/63) and preregistered derived result (24/63), improves execution from 45/63 to 58/63, and lowers all-attempt latency p50 from 53.670s to 18.045s (-66.38%). All 58 successful V58 outputs were recognized: 42 by the official extractor and 16 only by the exact bare-letter-plus-LF fallback. The five execution failures normalize to four `other_execution` and one `transport`; there were zero >=100-character treatment context leaks. The derived >=16/63 continuation gate passed.

FROZEN aggregate token evidence is intentionally not overstated. The scorer has exact usage for only 59/63 V58 attempts, so 1,127,460 recorded tokens (-38.01% versus exact-v43's unconditional 1,818,756) is not an unconditional aggregate. Recorded p50 is 17,201 versus exact-v43's unconditional 25,515, and root-token economy is available on 62/63, but the four missing total-usage rows are not treated as zero. The preregistered full-SCOUT token gate remains independently passed at 378,572 versus 491,575 (-22.99%) on its fixed 20 rows.

Integrity is terminal and immutable: schedule ID `9974d300e1d0b38312b3c4927dd0ca306320debe62effcbb69c9c88b5b7b3eac`; inference SHA-256 `61220abc079390bf8b6a5c0326fe963d08861f862f64ed0a86faef37cf5618ce`; schedule SHA-256 `45d3c4833be4a9193ee8999e475b35124e589a6179e3ce535f3eb8afc4c33102`; report SHA-256 `327e9dcf2e753f53abcb6853c56c7a51583d276058547788997ca675ea5246ed`. The report asserts terminal-before-gold validation, exact candidate/executable identity, 378 matching receipts, 62 exact valid treatment root transcripts, and zero treatment leaks.

This is a private derived cohort, not an official leaderboard result or superiority claim. V58 passes its fresh LongBench gate and is the first ultra-fast candidate to preserve exact-v43's official/derived totals while materially improving execution and latency. It is not automatically merged, released, headline-published, or authorized for OOLONG/RAH; downstream promotion disposition remains separate.


## V58 private source promotion

After the terminal FROZEN PASS and independent no-P0/P1 audit, private main merged the exact evaluated V58 source lineage at `a90f6fe8ab70b0effa9fc723b1e704edf0f92a43` (parents `af6b53e` and `f6e024a`). `src/lib.rs`, `src/main.rs`, `assets/SKILL.md`, and the Rust integration tests are byte-identical to the audited V58 source commit; the shipped config is the evaluated Luna/low config (`ca3f153c8a5a80c3727473fea90452ade5c556a24d026fb54084257791fd8eb8`). This intentionally replaces the rejected V49 product-source experiment while retaining its historical evidence and hardened benchmark controllers.

Promotion validation passed `cargo fmt --all -- --check`, `cargo test --locked` (90 passed, one release-only test ignored), `cargo clippy --locked --all-targets -- -D warnings`, `cargo build --locked --release`, and the ignored 16M-character release stress test. The local main-worktree rebuild SHA-256 `f441ac1a41f5e5e6832102cd93188e50d5a4b4d6affcf2c90f6ae2f3abd4ff7a` is an unbound verification build, not a relabel of the frozen evaluated executable `1d1e70b4e8720792553e89726a33472825d55a2365a504744cf9a747697c3224`; the frozen candidate aggregate remains the sole benchmark identity.

This is source-only private promotion. It does not authorize a public release, README headline, OOLONG/RAH inference, or a general superiority claim.


## V59 next-version mechanism triage — no candidate created

The strict next incomplete step was completed read-only against the immutable V58 FROZEN evidence. No Cargo build or benchmark process was active, so there was nothing to poll. The V58 output, schedule, and report retained their exact SHA-256 identities `61220abc079390bf8b6a5c0326fe963d08861f862f64ed0a86faef37cf5618ce`, `45d3c4833be4a9193ee8999e475b35124e589a6179e3ce535f3eb8afc4c33102`, and `327e9dcf2e753f53abcb6853c56c7a51583d276058547788997ca675ea5246ed`; gold remained detached.

The five V58 failures separate into three error-bearing second semantic primaries at ordinals 33/37/39, one ambiguous root WebSocket reset at ordinal 44, and one local assertion/repair exhaustion at ordinal 101. Even the entire terminal-failure envelope is only 5/63 (7.94%), below the existing requirement that a new implementation first have a causal projection of at least 10% median item-latency improvement. The repeated forbidden-percent-format repairs at ordinals 104/119 cost 11.382s and 8,424 tokens but affected only 2/63 and already recovered successfully.

Two additional generic ideas were quantified rather than implemented. Reducing the relevance budget from 20,000 to 16,000 characters could plausibly reduce median recorded tokens by 9.19-11.49% if the cap binds, but its item-latency ceiling is only about 5-6%, its defensible lower bound is zero, and it exposes 16 currently correct helper rows to unquantified evidence loss. A fixed relevance-choice wrapper could reduce the median authored program from 20 lines/860 characters toward four lines/151 characters, but V58 code length did not significantly predict root output (`r=0.183`, `p=0.174`) or root latency (`r=0.019`, `p=0.888`). Root output predicts latency, but the wrapper-to-output causal link is unproven, so the >=10% item-latency projection remains speculative.

Disposition: `NO_CANDIDATE_CREATED`. No source edit, build, candidate identity, SCOUT, rerun, OOLONG, gold access, or promotion was performed. The owner-only triage record is `/private/tmp/azdaja-v59-mechanism-triage-v1.json`, SHA-256 `3521acc1023ffc6b20f590eaff40a405e6e31ae082c95c09ea44fc63600c6655`.


## V60 preregistration — generic relevance-choice wrapper

A new offline counterfactual supplies the missing quantified mechanism evidence after V59 triage; it does not alter that earlier record. On the 57 immutable V58 helper-success traces, the model-authored root response has median 253 visible `o200k_base` diagnostic tokens while a canonical three-line caller of a fixed generic relevance-choice wrapper has 38, a paired median reduction of 215 tokens (minimum 179). Provider-authoritative root output is 627 tokens median and root latency is 9.755s within a 17.216s item median. Root latency regressed on provider total output at 11.805ms/token (95% slope interval 9.007-14.604ms, `r=0.752`, `p=1.60e-11`). Holding hidden reasoning and every child call unchanged, the 215-visible-token reduction projects 2.538s/14.74% item latency at the point slope and 1.936s/11.25% at the lower slope bound, clearing the existing causal >=10% gate. The owner-only counterfactual record is `/private/tmp/azdaja-v60-choice-wrapper-counterfactual-v1.json`, SHA-256 `791eb62e51541049b6136dcdc92d00097f7505a3ec0c58ecf2e66f5ccf3ef265`.

V60 is preregistered as exactly one generic mechanism: add a fixed preloaded `relevance_choice(source, question, alternatives, max_chars=20000)` convenience wrapper over the unchanged `lexical_relevance` and `semantic_manifest` contracts, and replace the long model-authored one-of-K recipe with a canonical short call. It is eligible only for genuinely semantic, relevance-local one-of-K tasks. It must remain forbidden for exact counts, order, multiplicity, exhaustive extraction, or any complete-source claim. It must validate nonempty question/source and ordered alternatives, create compact private wire IDs, retain every full alternative and the full question, use complete source at or below the existing threshold and the unchanged documented relevance view above it, call `semantic_manifest` exactly once, strictly validate the singleton result, and return the exact caller key. It adds no provider, filesystem, process, environment, network, output-format, or ordinary-`exec` capability and no fallback or head/tail path.

Before inference, focused table/boundary/Unicode/adversarial/call-envelope/fail-closed tests, locked Rust tests, formatting, strict all-target clippy, release build/stress, a static trace-eligibility linter, and an independent no-P0/P1 source audit are mandatory. The exact source patch, binary, SKILL, Luna/low config, wrapper contract, and unchanged SCOUT adapter must then be hashed once.

The single permitted V60 SCOUT uses the existing fixed public 20-item slice in a fresh nonexistent root with fresh isolated OAuth sessions; it is a new effective candidate, not a V58 rerun. At candidate 10 it requires >=8 execution and >=7 pinned gold-blind recognition. Full entry requires 20/20 execution and >=17/20 recognition, zero ineligible wrapper use, zero leaks/timeouts/cleanup errors, latency p50 <=16.173s (>=10% below V58's retained 17.970s), and aggregate recorded tokens below V58's complete 378,572 with no missing usage. Any execution failure makes 20/20 impossible and stops the candidate permanently. Passing SCOUT authorizes only a separately frozen, target-bound rehearsal and fresh FROZEN LongBench gates; it does not authorize promotion, OOLONG, gold, publication, or a rerun.
