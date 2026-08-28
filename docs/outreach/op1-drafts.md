# OP-1 outreach drafts

Prepared copy only. **Nothing here authorizes sending, posting, replying, submitting, or requesting amplification.** Before each action, the operator must re-check the route and venue rules, approve that exact message, and confirm every link works signed out.

Evidence link used below: <https://github.com/kubet/azdaja/blob/main/BENCHMARKS.md>

## 1. Oolong authors

**Route:** the contact route published at <https://oolongbench.github.io/>. Ask whether system results are in scope before proposing an issue.

**Subject:** Are external system results in scope for Oolong?

```text
I built Azdaja, a system/harness rather than a standalone model. It keeps the
complete source in a persistent local Python evaluator, lets a bounded root
program use code plus explicit model calls, and fails closed when record
coverage is incomplete.

I measured it on a fixed 199-row validation-derived Oolong slice under the RAH
protocol. The private single-arm result was 68.64%, with every input,
transcript, retained zero, and failure row linked from the public receipt:
https://github.com/kubet/azdaja/blob/main/BENCHMARKS.md

Your site invites model submissions, but this is a system result. Are system or
harness results in scope, and if so would an external-results issue be useful?
I would rather follow your preferred protocol than force the result into the
wrong category.
```

## 2. Alex L. Zhang

**Route:** the contact method explicitly published on the author's site.

**Subject:** A fail-closed production implementation of the RLM pattern

```text
I built Azdaja, an MIT-licensed Rust implementation of the recursive-language-
model pattern: complete UTF-8 source in one persistent sandboxed Python
evaluator, bounded root prompts, explicit llm/llm_batch calls, and fail-closed
record coverage.

On a fixed 199-row validation-derived Oolong slice under the RAH protocol it
scored 68.64% as a bare RLM layer. The comparison is private and single-arm,
not a superiority claim. Inputs, transcripts, score accounting, and completed-
but-wrong rows are public here:
https://github.com/kubet/azdaja/blob/main/BENCHMARKS.md

If you have ten minutes, I would value methodological criticism more than
promotion. If the implementation departs from the pattern in a material way, I
want to correct the record.
```

## 3. Latent Space

**Route:** `tips@latent.space`, the published editorial pitch address. Do not use the sponsorship address.

**Subject:** Pitch: a production RLM layer with auditable failure receipts

```text
Azdaja is a local Rust layer that keeps large source material outside the root
model prompt, works through a persistent Python evaluator, and makes bounded
model calls only when judgment is needed. The interesting story is not another
context-window claim; it is what had to be made fail-closed before the pattern
was safe enough to ship: exact record coverage, typed final answers, hash-bound
receipts, and published failure autopsies.

The repository includes a private single-arm Oolong/RAH result, complete score
accounting, and the rows that failed. The methodology and limitations are here:
https://github.com/kubet/azdaja/blob/main/BENCHMARKS.md

If this fits your editorial calendar, I can provide a short technical outline
and a fully reproducible local demo. No embargo or launch timing is required.
```

## 4. RAH authors

**Route:** the author contact locations published with the paper. One message to the corresponding author, no parallel blast.

**Subject:** Independent validation-derived RAH-protocol implementation

```text
I ran a fixed 199-row validation-derived slice under your protocol against a
bare RLM layer and published the complete mortality accounting: 185 valid
predictions, 14 retained zeros in the denominator, and a frozen score sum of
136.597 (68.64%).

Azdaja is an independent Rust implementation, not an official reproduction and
not a superiority claim. The artifacts include the completed-but-wrong rows and
root-side task-modeling failures:
https://github.com/kubet/azdaja/blob/main/BENCHMARKS.md

If any protocol detail differs from your intent, I would rather correct it than
defend it. Is there a specific reporting format you would prefer for external
system results?
```

## 5. Prime Intellect community

**Route:** the community route published on the Prime Intellect site. Post only after reading the current channel rules.

```text
Disclosure: I build Azdaja. It is an independent single-binary implementation
of the recursive-language-model pattern, with the complete source kept in a
persistent local Python evaluator and public receipts for coverage, scoring,
and failure rows. I am sharing it here because this community has discussed the
pattern technically, not to ask for amplification. Methodology and limitations:
https://github.com/kubet/azdaja/blob/main/BENCHMARKS.md
```

## Pre-send gate

For each message, require all of the following:

- the v0.1.14 release and linked pages resolve signed out;
- the route and venue rules were re-checked that day;
- claims still match `BENCHMARKS.md` exactly;
- gate-645 and row-651 diagnostics are not cited as campaign evidence;
- the operator explicitly authorizes this target and exact payload;
- for Oolong, no repository issue is opened unless the private route first confirms system results are in scope;
- the append-only send log in `docs/visibility-ops.md` is updated only after the action succeeds.
