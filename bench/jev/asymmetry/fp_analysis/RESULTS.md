# Frozen row651 asymmetry characterization

This is an **offline exploratory analysis**, not a gold relabeling. It reads
`bench/jev/row651_labels/result.json` and the unchanged
`bench/oolong/context-1048576.txt`; it makes no provider calls and changes no
runtime or frozen artifact. `analyze.py` verifies every source span against
the retained record hash before writing `errors.jsonl`.

## Counts and denominators

| quantity | exact value |
|---|---:|
| observed occurrences | 17,469 |
| official ham denominator | 8,638 |
| official spam denominator | 8,831 |
| correctly classified controls | 16,794 |
| false positives (predicted ham, official spam) | 641 |
| false negatives (predicted spam, official ham) | 34 |
| FPR, 641 / 8,831 | 0.0725852112 (7.2585%) |
| FNR, 34 / 8,638 | 0.0039360963 (0.3936%) |
| `sumNoul` | 9,287.38 |
| `sumNoul - official ham` | +649.38 |

`errors.jsonl` retains all 675 errors with ID, `byte_start`, `byte_end`,
`record_sha256`, official label, probability, raw source record, and derived
descriptive keys. The source and frozen-result SHA256 values are recorded in
`analysis.json`: result
`65f5bf14c9c3546cc030b95adcfaaa10ec3b40586fdc06f7bdfc469f92242e13`, source
`78e61364029606a211e8d6fced3fefea42f37651bc2c4b84ef54856e1e70f4fe`.

## Confidence distribution

The threshold is 0.5. Error counts by `p_ham` bin `[0,.1), ...,[.9,1]` are:

| error set | 0-.1 | .1-.2 | .2-.3 | .3-.4 | .4-.5 | .5-.6 | .6-.7 | .7-.8 | .8-.9 | .9-1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all 675 errors | 4 | 4 | 5 | 5 | 16 | 191 | 154 | 130 | 120 | 46 |
| 641 FPs | 0 | 0 | 0 | 0 | 0 | 191 | 154 | 130 | 120 | 46 |
| 34 FNs | 4 | 4 | 5 | 5 | 16 | 0 | 0 | 0 | 0 | 0 |

Using confidence `max(p_ham, 1-p_ham) >= .9`, 50/675 errors (7.4074%) are
confident: 46/641 FPs (7.1763%) and 4/34 FNs (11.7647%). Thus the errors are
not all high confidence.

## Full-denominator lexical clusters

These are mutually exclusive, ordered regex heuristics over the `Instance`
text. Each row uses the complete cluster denominator, not only errors.
“Control” means a correctly classified occurrence in that same cluster.
Enrichment is cluster error rate divided by the panel error rate (675/17,469).

| cluster | n | errors | FP | FN | controls | error rate | enrichment |
|---|---:|---:|---:|---:|---:|---:|---:|
| other | 10,194 | 271 | 240 | 31 | 9,923 | 2.6584% | 0.688x |
| prize / competition / promotion | 2,826 | 19 | 19 | 0 | 2,807 | 0.6723% | 0.174x |
| paid / subscription service | 2,544 | 274 | 274 | 0 | 2,270 | 10.7704% | 2.787x |
| adult / dating chat | 740 | 14 | 14 | 0 | 726 | 1.8919% | 0.490x |
| ordinary personal conversation | 404 | 15 | 14 | 1 | 389 | 3.7129% | 0.961x |
| delivery / transaction notice | 359 | 53 | 53 | 0 | 306 | 14.7632% | 3.821x |
| account / payment / security | 307 | 11 | 9 | 2 | 296 | 3.5831% | 0.927x |
| sports / trivia | 95 | 18 | 18 | 0 | 77 | 18.9474% | 4.904x |

The cluster error denominators sum to 17,469 and the error counts sum to 675.
The strongest descriptive concentrations are transaction/delivery and
sports/trivia, followed by paid-service language. This is association with
hand-written lexical rules, not evidence of a shared cause.

Coarse template normalization masks URLs, phone-like strings, standalone
numbers, and long hex-like codes. It is retained in `analysis.json`; the
largest error template has 18 errors / 27 occurrences / 9 controls:
“customer service announcement ... unable to [re-]schedule ... ref”. Other
14-error templates include ringtone-order notices, insufficient-credit service
notices, a missed-call sentence, and several recurring spam or complaint
messages. Exact normalized-template denominators are available rather than
being selectively reported here.

## Representative manual reads

These readings are agent judgment about message semantics, **not gold changes**.
The official labels remain authoritative for the metrics.

* **Source/context ambiguity, FP `r0049`**, p=0.92, bytes 7,219:7,340,
  hash `89dc8092...a69abf`: “You have ordered a Ringtone. Your order is being
  processed...” It resembles a legitimate transaction status, while the
  official spam label and the surrounding paid-service family make the
  classification boundary non-obvious from text alone.
* **Source/context ambiguity, FP `r0259`**, p=0.95, bytes 40,444:40,571,
  hash `8aca3370...d076f71d`: “Sorry I missed your call ... I'm on
  07090201529.” It is ordinary personal language with a phone number, but is
  officially spam. This is a concrete high-confidence disagreement where a
  lexical phone-number cue can conflict with semantics.
* **Service-context ambiguity, FP `r0415`**, p=0.74, bytes
  63,342:63,539, hash `3a8d6eda...14db589`: a service could not be delivered
  for insufficient credit and asks the recipient to top up. The text alone
  does not establish whether this was a requested service or an unsolicited
  premium-service solicitation. The official label stays spam. No gold error
  or model error cause is established by this reading.
* **Less ambiguous official-ham disagreement, FN `r2631`**, p=0.02, bytes
  407,712:407,785, hash `3db39e31...9d34b0`: “Have a nice day my dear.” This
  is plainly personal/ham on a surface reading, despite the model’s spam
  prediction.
* **Another ham-like FN, `r5195`**, p=0.35, bytes 805,479:805,657, hash
  `504bdde0...54417bc`: affectionate personal conversation about missing a
  partner. The adult-ish wording can plausibly confuse a detector, but this
  remains an exploratory explanation, not a relabel.

## Repeated-message dependence and limits

All 17,469 complete date/user/Instance record hashes are unique, but this
does **not** make the SMS messages independent. Removing date/user metadata
leaves **5,009 exact Instance texts**, or **4,997** after NFKC, casefold and
whitespace normalization. There are **17,371 occurrences in repeated-message
groups**, with **12,460 duplicates beyond the first exact message**. All675
errors belong to messages repeated in the panel and span139 distinct message
texts. The largest exact-text group has14 occurrences, normalized group28.
Repeated messages can receive different decisions because their supplied
record context and surrounding batch differ. No cache independence is implied.

Cluster error rates above use all labels. The corresponding false-positive
denominators are also emitted: paid-service **274/2,446 official negatives
(11.20%)**, transaction/delivery **53/317 (16.72%)**, sports/trivia **18/69
(26.09%)**, compared with **641/8,831 (7.26%)** overall. Personal-language
negatives are14/14, a tiny repeated-message stratum, not a general100% rate.
These post-outcome lexical rules are exploratory, not a validated detector.

The675 errors are occurrence-weighted official-label disagreements in a
public benchmark. No confidence interval,
causal attribution, calibration guarantee, provider authentication, or gold
relabeling is claimed.

## Reproduction

```sh
python3 -B bench/jev/asymmetry/fp_analysis/analyze.py
python3 -B -m unittest bench.jev.asymmetry.fp_analysis.test_analyze -v
```
