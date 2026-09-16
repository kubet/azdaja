# Primary evidence for optional Jev semantic leaves in Azdaja

**Date:** 2026-09-16
**Scope:** Whether TypeSafe Jev, a typed System One model, is a defensible optional semantic leaf-inference component inside Azdaja's RLM layer: persistent sandboxed Monty Python, `llm`/`llm_batch`, and deterministic reductions.

## Bottom line

The literature supports a **testable systems hypothesis**, not a conclusion: typed semantic leaves may improve an RLM when they reduce repeated free-form parsing, expose an independently useful abstention/escalation signal, or make deterministic reductions safer. The relevant evidence is indirect. The RLM paper evaluates recursive calls and programmatic decomposition, not Jev or typed semantic leaves. Calibration literature shows that probabilities often require task- and distribution-specific validation. Long-context studies show aggregation and position failures, which motivate decomposition, but they do not imply that an added classifier will fix them. A Jev leaf can also reproduce the same semantic error as the parent LLM, creating correlated confidence and false consensus.

The right initial claim is therefore narrow: **Jev is an optional candidate leaf whose incremental value must be demonstrated against a strong no-Jev RLM baseline, under matched cost/latency and with held-out calibration.**

## System boundary and terminology

Azdaja's proposed architecture is not itself a new trained language model. It is an RLM-style orchestration layer: a persistent, sandboxed Python environment contains the input and state; the model can use `llm` or `llm_batch` for recursive calls; final aggregation is deterministic. In this report, a “semantic leaf” means a bounded leaf call that maps state to a typed `Choice`, `Noul`, or `Score`, rather than generating an explanation or arbitrary code.

TypeSafe's live documentation describes System One models as returning typed answers and probabilities, and says Jev is its first System One model. It explicitly says calibration is measured across groups of predictions and does **not** guarantee an individual answer is correct. Noul returns a yes/no probability; Choice returns one of a fixed set with probabilities; Score returns a position on an ordered scale. These are vendor descriptions, not independent validation.

Primary vendor documentation:

- [System One](https://docs.typesafe.ai/concepts/system-one)
- [Noul](https://docs.typesafe.ai/primitives/noul)
- [Choice](https://docs.typesafe.ai/primitives/choice)
- [Score](https://docs.typesafe.ai/primitives/score)
- [Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) **Vendor launch post, 2026-09-15**
- [TypeSafe privacy policy](https://typesafe.ai/legal/privacy-policy) **Vendor policy, last updated 2025-11-19**

### Direct vendor-source limitations

The launch post adds important qualification to the vendor claims. Its four workflow evaluations use the average predictions of GPT-6 Astra and Fable 5.1 as the reference, not independently adjudicated ground truth. The reference therefore measures agreement with those models and can inherit their errors or bias toward OpenAI and Anthropic. The post also says the workflows were authored by TypeSafe's model-capabilities team, so construction bias remains possible even though the authors say the workflows were not deliberately designed for Jev. LLM baselines use TypeSafe's System One adapter to force structured probabilistic outputs; the post says this is more accurate for decisions but slower and more expensive than asking for decisions without probabilities. Cost, speed, and West Coast service-location claims are vendor-reported and must be remeasured from Azdaja.

The launch post's “0% type errors” plot is a schema/type guarantee, not a measured 0% semantic-error rate. Type safety prevents malformed values under the declared schema; it does not establish that the selected label or score is correct. The post reports a $0.042 per million input-token price and free output, but also says the sustainability of pricing is not proven. Jev supports Choice cardinality up to 255 in the launch material. These claims should be recorded as versioned service facts, not assumed invariants.

Privacy is an integration constraint, not evidence of model quality. TypeSafe's policy says it does not train or fine-tune models on prompts or other Input, but says it may retain personal data as reasonably necessary for service or business purposes, may disclose it to service providers, and hosts the services in the United States. It also disclaims guarantees of security. For Azdaja, the frozen protocol's synthetic-only input rule and explicit live opt-in are therefore appropriate. Production use would require a separate data-protection review covering US transfer, retention, service providers, sensitive evidence, deletion, and incident risk.

### 1. Recursive Language Models motivate decomposition, but do not validate Jev

Zhang, Kraska, and Khattab, *Recursive Language Models*, current retrieved version v3 ([arXiv](https://arxiv.org/abs/2512.24601), [HTML v3](https://arxiv.org/html/2512.24601v3), 11 May 2026), introduce an inference strategy that treats a long prompt as an external environment. The LLM programmatically inspects and decomposes that environment, recursively invokes itself on snippets, and combines observations. Their experiments report strong results on long-context tasks, including inputs beyond the base model context window, with comparable cost in the evaluated settings.

The transferable mechanism is architectural: externalize long input, choose bounded views, and use recursive calls instead of one monolithic context. That is compatible with Azdaja's persistent sandbox and deterministic reduction. It does **not** establish that a second model family, a typed output, or a probability improves correctness. The paper's recursive calls are still language-model calls; its tasks and implementations do not test Jev, System One, or a semantic-leaf substitution. Treat its gains as evidence for the RLM decomposition pattern only.

Important limitations for extrapolation:

- The paper is a single primary study with particular models, prompts, tasks, and pricing assumptions.
- Reported gains are benchmark- and scaffold-dependent, so they should not be restated as general production guarantees.
- An RLM can fail through bad chunking, omitted evidence, premature stopping, or a wrong deterministic reducer even when each leaf is locally plausible.
- “Arbitrarily long” means the external environment can hold more input; it does not mean every task is solved with constant compute or bounded error.

### 2. Long-context access and aggregation are known failure points

Liu et al., *Lost in the Middle: How Language Models Use Long Contexts* ([ACL Anthology](https://aclanthology.org/2024.tacl-1.9/), DOI [10.1162/tacl_a_00638](https://doi.org/10.1162/tacl_a_00638)), evaluate multi-document question answering and key-value retrieval while varying the position of relevant information. They find a positional U-shape: performance is often better when evidence is near the beginning or end and degrades when relevant evidence is in the middle, including for long-context models.

This supports measuring **where** leaf evidence appears and whether chunking changes recall. It does not show that typed classification solves positional bias. A leaf asked about an incomplete or misleading snippet can be confidently wrong; a deterministic reducer can then make the error look more reliable by aggregating it.

For Azdaja, test at least: shuffled evidence order, relevant evidence at chunk boundaries and interiors, duplicate evidence, distractor density, and adversarially plausible contradictory snippets. Report per-position and per-density results, not only aggregate accuracy.

### 3. Confidence is useful only after calibration on the deployment task

Guo et al., *On Calibration of Modern Neural Networks* ([arXiv:1706.04599](https://arxiv.org/abs/1706.04599)), study the relationship between predicted confidence and empirical correctness. They show modern neural networks can be miscalibrated and find temperature scaling effective in many of their classification settings. The central operational definition is group-level: among predictions assigned confidence near `p`, the correctness frequency should be near `p`.

This is directly relevant to Jev's returned probabilities, but the evidence is not a guarantee that Jev's values are calibrated for an Azdaja leaf prompt. Calibration can shift with question wording, label taxonomy, domain, class balance, chunking, and the policy used to adjudicate “correct.” A probability should therefore be treated as a feature for routing or abstention only after held-out calibration evaluation on the exact leaf schemas and data distribution.

Do not use raw Jev probability as proof of correctness. Measure reliability diagrams, Brier score, log loss, expected calibration error with sensitivity to binning, and selective risk versus coverage. Keep calibration data separate from threshold-selection and final test data.

### 4. Selective prediction gives the right decision framing

Geifman and El-Yaniv, *Selective Classification for Deep Neural Networks* ([arXiv:1705.08500](https://arxiv.org/abs/1705.08500)), formalize classifiers that may abstain. The system trades coverage for selective risk: it answers only when its confidence supports an acceptable error rate and rejects otherwise. This is a better model for an optional Jev leaf than “confidence means truth.”

For Azdaja, a Jev leaf should have an explicit policy: answer, ask the RLM for more evidence, invoke a stronger LLM leaf, or escalate. The policy should be selected on validation data and evaluated on a test set. A useful acceptance criterion is not merely higher raw accuracy, but lower risk at the same coverage and total cost, or higher coverage at the same risk.

A typed output helps make this policy deterministic. It does not itself provide a selective-prediction guarantee. If the leaf's confidence is not calibrated under the actual state-construction process, thresholding may selectively retain exactly the hard correlated failures.

### 5. Cascades and routers provide useful cost baselines, but differ from Jev leaves

Chen, Zaharia, and Zou, *FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance* ([arXiv](https://arxiv.org/abs/2305.05176), [HTML](https://arxiv.org/html/2305.05176), v1, 9 May 2023), formulate API selection as a budget-constrained strategy and study prompt adaptation, approximation, and cascades. Their cascade is sequential: cheaper models are tried first and later calls are made when the system decides more capability is needed. The paper explicitly models prompt, output, and fixed per-call costs. For Azdaja, this yields a directly testable accounting identity for an optional Jev leaf:

`E[C] = C_jev + P(abstain) * C_fallback + C_overhead`

where `C_jev` includes request cost and local transport/validation cost, and the fallback term includes the conditional cost of the generative or stronger leaf. If Jev is only called on a subset, multiply `C_jev` by its invocation rate. A cost claim must use observed usage and billed prices, not the vendor's headline price alone. A sequential cascade also has expected latency approximately `E[L] = L_jev + P(abstain) * L_fallback + queue/retry overhead`, whereas parallel `llm_batch` changes the latency model but not necessarily total cost.

Ong et al., *RouteLLM: Learning to Route LLMs with Preference Data* ([arXiv](https://arxiv.org/abs/2406.18665), [HTML v4](https://arxiv.org/html/2406.18665v4), v4, 23 February 2025), train routers to choose between strong and weak models from preference data. Their main latency argument is that one routed call avoids the multi-call latency of cascades. This is relevant as a control, but RouteLLM routes before generation and does not establish that Jev's semantic probabilities are calibrated for evidence judgments. Its preference labels are also not the same as independently adjudicated correctness labels.

These papers imply that the experiment must separate at least four baselines: (a) generative labels-only, (b) generative labels plus requested probabilities, (c) Jev typed labels without using confidence, and (d) Jev typed labels with the frozen abstention policy. Otherwise the comparison can favor Jev because the baseline was burdened with probabilistic output or because extra calls were not cost-matched. Report sequential and parallel latency separately.

### 6. Ensemble agreement can be illusory when errors are correlated

Ortega, Cabañas, and Masegosa, *Diversity and Generalization in Neural Network Ensembles* ([PMLR HTML](https://proceedings.mlr.press/v151/ortega22a.html), [PMLR PDF](https://proceedings.mlr.press/v151/ortega22a/ortega22a.pdf), AISTATS 2022; [arXiv](https://arxiv.org/abs/2110.13786)), analyze how ensemble diversity relates to generalization. The practical implication is that independent-looking votes are not automatically independent evidence. Shared data, representations, prompts, or inductive biases can make errors correlated.

That concern is relevant to an RLM plus Jev arrangement, whose diversity has not been measured. Both may read the same chunk, inherit the same misleading premise from the orchestrator, or be trained on overlapping internet data. A deterministic reducer that rewards agreement can amplify a shared mistake. The system should log paired outcomes and estimate conditional error correlation, not infer independence from different APIs or typed output formats.

Operational tests:

- Compare parent-LLM and Jev errors on the same adjudicated examples.
- Stratify correlation by task, class, evidence density, and confidence.
- Include prompt paraphrases, alternative chunkings, and independent evidence selections.
- Evaluate whether Jev adds value after the parent model's features and votes are known.

### 7. What the primary evidence does not establish

I found no independent, peer-reviewed evaluation establishing that Jev improves an RLM, that System One probabilities remain calibrated under recursive chunking, or that typed leaves reduce end-to-end error in long-context aggregation. TypeSafe's documentation is useful for interface semantics and stated design intent, but it is vendor evidence. Any TypeSafe benchmark or price/speed claim should be labeled as a vendor claim unless independently reproduced with disclosed tasks, prompts, model versions, costs, and ground truth.

The RLM paper is recent and its reported results should be treated as one primary study, not a settled consensus. The calibration and selective-prediction papers mostly study supervised classifiers, not black-box API models with natural-language instructions. Their definitions and evaluation protocol transfer; their numerical findings do not automatically transfer.

## Falsifiable experimental plan

This is the broader research agenda, not a claim that all these experiments were run. The small, sequential screening campaign is defined separately in [the frozen protocol](jev-experiment-protocol-20260916.md). Its authored dependent cases and early stopping do not support the inferential guarantees discussed for a future representative study.

### Hypotheses

- **H1 benefit:** Adding Jev leaves improves end-to-end correctness or selective risk at fixed cost/latency versus the best no-Jev RLM baseline.
- **H2 mechanism:** Any gain comes from typed semantic decisions and routing, not simply from extra model calls or more sampled tokens.
- **H3 calibration:** After held-out calibration, Jev confidence predicts leaf correctness sufficiently well to improve abstention or escalation decisions.
- **H4 diversity:** Jev adds value specifically on examples where parent-LLM leaves fail, rather than duplicating their errors.

### Arms and controls

At minimum compare:

1. Direct single-call LLM baseline.
2. Persistent-sandbox RLM with `llm` leaves and deterministic reducer.
3. Same RLM with `llm_batch`, matched leaf-call budget.
4. RLM plus Jev typed leaves, with no extra untyped calls.
5. RLM plus a control typed-output implementation or constrained JSON LLM leaf, if available.
6. Jev-only leaves where appropriate, to separate leaf quality from orchestration effects.

Match or report input tokens, output tokens, number of calls, wall-clock latency, retries, and monetary cost. Freeze prompts, model versions, reducer code, and random seeds where possible. Pre-register the primary metric and stopping rule.

### Tasks and stress tests

Use a mixture of adjudicated real cases and synthetic controls with known answers. Include classification, scalar scoring, contradiction detection, and evidence aggregation. Vary:

- context length and information density;
- relevant evidence position and chunk boundaries;
- contradictory and duplicated evidence;
- label imbalance and rare classes;
- paraphrases and ambiguous wording;
- distribution shift and out-of-domain cases;
- missing, malformed, or adversarial leaf inputs;
- repeated calls and persistent-state contamination.

For each task, retain leaf-level inputs and outputs so failures can be audited. The deterministic reducer must have tests for missing answers, incompatible schemas, ties, NaNs/out-of-range scores, and contradictory high-confidence leaves.

### Metrics

Primary end-to-end metrics should include exact correctness or task-specific utility, selective risk at fixed coverage, and cost/latency-adjusted utility. Secondary metrics:

- coverage-risk curves and area under the risk-coverage curve;
- Brier score and log loss for probabilistic leaves;
- reliability diagrams and calibration error under multiple bin counts;
- class-conditional recall and false-positive/false-negative costs;
- evidence-position and context-density slices;
- pairwise error correlation and conditional mutual information where sample size permits;
- reducer-level error contribution versus leaf-level error contribution.

A Jev leaf should be called a benefit only if the improvement survives a held-out test set, confidence intervals, multiple task slices, and matched resource accounting. If it only raises agreement while correctness is unchanged, it is not evidence of improved reliability.

### Accumulated workflow risk

If a workflow requires 100 exact semantic judgments and each judgment were independently correct with probability 0.99, the probability that all 100 are correct would be `0.99^100 ≈ 0.366`. This is illustrative arithmetic, not a measured Azdaja guarantee. Independence is usually implausible: shared evidence, shared prompts, model priors, and reducer decisions create correlation. Positive correlation can produce clusters of failures, but does not uniformly increase the probability of any error versus independence. Marginal error, error multiplicity, and exact-workflow success are different quantities. Averaging or agreeing probabilities does not repair a shared systematic error. Measure both per-leaf risk and exact-workflow success on complete cases.

## Statistical and sample-size caveats

Small evaluation sets make calibration and correlation estimates especially unstable. For a binomial accuracy estimate near 0.5, an approximate 95% half-width is `1.96 * sqrt(p(1-p)/n)`, so about 2,401 independent examples are needed for a ±2 percentage-point margin in the worst case. This approximation is not a substitute for Wilson or exact intervals, and clustered examples reduce the effective sample size.

For paired system comparisons, use paired bootstrap or an appropriate paired test over independent cases, not a test treating every leaf call as independent. If one user task generates many leaves, those leaves share context and are clustered. Report the number of independent top-level cases and, where relevant, bootstrap by case or document rather than by leaf.

Calibration bins can be nearly empty. Prefer adaptive bins or reliability plots with counts and confidence intervals, and report a proper scoring rule such as Brier or log loss. Thresholds chosen after looking at the test set invalidate the reported selective-risk estimate. If many tasks, thresholds, reducers, and slices are tried, control or at least disclose multiplicity and distinguish exploratory findings from confirmatory ones.

For detecting a modest improvement, power depends on the baseline rate, correlation between paired predictions, class balance, and the minimum effect worth paying for. Run a prospective power calculation after defining the primary metric. When labels are expensive, use a pilot only to estimate variance and effect size, then collect a separately held-out confirmatory set.

## Evidence that would refute a benefit

The Jev leaf hypothesis should be considered unsupported or refuted for a given deployment if any of the following persists under fair matching:

- no statistically and practically meaningful improvement in end-to-end utility at matched cost and latency;
- gains disappear when the no-Jev RLM receives the same number of calls or equivalent token budget;
- calibration is no better than the baseline routing signal, or degrades under chunking and distribution shift;
- Jev errors are strongly correlated with parent-LLM errors, especially on high-confidence cases;
- agreement increases but adjudicated correctness does not;
- benefit occurs only on synthetic or vendor-designed tasks and not on held-out representative cases;
- deterministic reduction of typed outputs introduces more aggregation failures than it prevents;
- thresholding yields lower risk only by rejecting most cases, making the system operationally unusable;
- the incremental cost, latency, privacy, or availability burden exceeds the value of the observed error reduction.

Conversely, a credible positive result would require an independently reproducible, held-out improvement with disclosed resource use, confidence intervals, calibration analysis, and failure slices. The strongest evidence would show that Jev is complementary to the RLM, not merely another correlated vote.

## Gaps and next research steps

1. Obtain a reproducible Jev evaluation protocol and public test set, or construct an internal adjudicated set with stable labeling and versioned schemas.
2. Measure calibration separately for Noul, Choice, and Score. A Score's numerical output is not automatically a probability and should not be evaluated with binary calibration metrics without a defined event.
3. Test whether state serialization, chunking, and persistent sandbox history change Jev calibration.
4. Compare Jev against a constrained JSON/function-calling LLM leaf at equal calls and budget.
5. Add an explicit abstain/insufficient-evidence outcome where the task permits it.
6. Validate sandbox isolation and state hygiene. A persistent environment can improve reuse but can also leak prior evidence or decisions across cases.
7. Re-run after model-version changes. Calibration and error correlation are properties of the deployed combination, not permanent API guarantees.

## Sources

- Zhang, Alex L., Tim Kraska, and Omar Khattab. “Recursive Language Models.” Current retrieved version v3, 11 May 2026. [arXiv](https://arxiv.org/abs/2512.24601), [HTML v3](https://arxiv.org/html/2512.24601v3).
- Liu, Nelson F. et al. “Lost in the Middle: How Language Models Use Long Contexts.” *TACL* 12, 157–173, 2024. [ACL Anthology](https://aclanthology.org/2024.tacl-1.9/), [DOI](https://doi.org/10.1162/tacl_a_00638).
- Guo, Chuan et al. “On Calibration of Modern Neural Networks.” 2017. [arXiv](https://arxiv.org/abs/1706.04599).
- Geifman, Yonatan and Ran El-Yaniv. “Selective Classification for Deep Neural Networks.” 2017. [arXiv](https://arxiv.org/abs/1705.08500).
- Chen, Lingjiao, Matei Zaharia, and James Zou. “FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance.” v1, 9 May 2023. [arXiv](https://arxiv.org/abs/2305.05176), [HTML](https://arxiv.org/html/2305.05176).
- Ong, Isaac et al. “RouteLLM: Learning to Route LLMs with Preference Data.” Current retrieved version v4, 23 February 2025. [arXiv](https://arxiv.org/abs/2406.18665), [HTML v4](https://arxiv.org/html/2406.18665v4).
- Ortega, Luis Antonio, Andrés Masegosa, and Rafael Cabañas. “Diversity and Generalization in Neural Network Ensembles.” AISTATS 2022. [PMLR HTML](https://proceedings.mlr.press/v151/ortega22a.html), [PMLR PDF](https://proceedings.mlr.press/v151/ortega22a/ortega22a.pdf), [arXiv](https://arxiv.org/abs/2110.13786).
- TypeSafe AI. “System One,” “Noul,” “Choice,” and “Score” documentation. [System One](https://docs.typesafe.ai/concepts/system-one), [Noul](https://docs.typesafe.ai/primitives/noul), [Choice](https://docs.typesafe.ai/primitives/choice), [Score](https://docs.typesafe.ai/primitives/score). **Vendor documentation, not independent evidence.**
