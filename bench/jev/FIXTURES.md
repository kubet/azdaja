# Jev semantic leaf fixtures

Preregistered classification fixtures for the optional semantic leaf experiment. Evidence is untrusted data, never an instruction. Artifacts are frozen before live testing.

## Composition

Smoke has 6 cases, two per label. Challenge has 30 cases, ten per label. Holdout has 30 cases, ten per label. Contexts cover software, release, memory, and source evidence. Challenge cases test negation scope, necessary versus sufficient conditions, temporal supersession, scope and identity mismatch, quoted prompt injection, absence, hypothetical versus actual events, exception paths, and joins whose required evidence is supplied.

Challenge-only same-claim evidence flips include c05/c06, c17/c18, and c29/c30. Each pair changes a decisive evidence fact while keeping the claim fixed; the pairs test whether a judgment changes rather than merely matching a template. The holdout uses distinct surfaces and relation types from challenge.

## Independent neutral critique

This revision records an audit correction pass before inference. Earlier risks included under-specified identity joins, treating absent evidence as negation, and confusing linguistic quotation with instruction authority. Root corrected additional independent-review findings before any user-key inference: inverted migration gold, listed-versus-global quantifiers, skipped-test outcome versus parser capability, signer identity, exclusive causality, normative approval versus observed bypass, exact revision identity, and exhaustive cleanup scope. These corrections are not outcome-conditioned. This suite measures evidence discipline as well as semantic reasoning. Repeated words such as current, authoritative, or complete may create shortcut risk despite distinct split wording. Compact cases underrepresent long chains, equal-authority conflicts, and messy identifiers. Holdout is a coverage sample, not a population estimate. Main residual risks are overcalling absence, treating plans or quoted instructions as events, ignoring exception scope, and joining near-match identifiers. The main coverage gap is calibrated insufficiency when one plausible interpretation feels salient.

## Measurement

Report exact-match accuracy by split and label, macro-F1, a 3x3 confusion matrix, and family accuracy. Report unsupported-entailment rate (insufficient called supported), contradiction miss rate, and insufficiency recall. For challenge pairs, report the expected flip rate and pairwise errors separately because paired observations are not independent. Do not bootstrap individual cases. Paired challenge cases and ten holdout triples are dependent, hand-authored, nonrandom samples, and the campaign stops adaptively. Report descriptive observed-prefix statistics with denominators, not population confidence claims. The runner's fixed-n IID binomial reference is explicitly invalid for this sampling design. Do not pool pair counts as extra independent cases. Exact-duplicate checks and source-index expansion are handled elsewhere.
