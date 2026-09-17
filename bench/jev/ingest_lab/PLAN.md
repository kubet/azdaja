# Ingestion to relevant RAG context: separate bounded experiment

Status: preregistered design before retrieval outcomes or new provider calls. This does not reopen the closed six-angle, seven-task or eighteen-span studies.

## Question and boundary

Does explicit source ingestion produce fresh, scoped, cited context that helps the next agent answer, and what does the entire pipeline cost? Reranking is one replaceable operator, not ingestion itself. Raw UTF-8 and revisions remain canonical. Lexical indexes, chunk selection and Jev judgments are derived views. There is no automatic production memory writer, authenticated multiuser service, embedding requirement or claimed infinite attention.

Implementation is confined to `bench/jev/ingest_lab`. Existing Rust/native transport and previously frozen experiments remain unchanged. The local TypeSafe skill applies. SQLite through Python's standard library is the selected local store, not a new hosted dependency.

## Hypotheses and independent controls

1. **Durable ingestion:** one repository snapshot atomically changes its current sources. No-op sync retains generation. Updates, deletion, ownership and visibility changes invalidate old views. Other repositories remain untouched. Raw history retention is not secure deletion.
2. **Scope and citations:** repository/actor visibility filtering occurs before returning candidate text, computing lexical statistics, constructing provider input or recording context. Every cited byte span reproduces exact retained source bytes. Trust is the explicitly authorized host caller, not Git email or a source-supplied command.
3. **Retrieval versus ordering:** compute scoped BM25 over all eligible chunks. Keep the top16 as the common candidate pool. Compare a strong fixed BM25+MMR view with optional Jev relevance ordering over the SAME pool. Measure candidate recall, selected evidence coverage and final answer quality separately. No reranker can recover omitted candidates.
4. **Actual next-agent outcome:** send each method's explicit task-specific view into actual persistent Azdaja `load/exec/final`, not just an offline ranking metric. A separate full-evidence generative reference uses the complete frozen small corpus. No automatic context injection into unrelated sessions.
5. **Performance:** measure raw input bytes, document/chunk counts, cold ingestion, no-op/update/delete, fresh-process open/query, context assembly, native handoff, provider calls, input/output tokens and storage footprint separately. No provider latency is inferred from local SQLite timings.

## Frozen retrieval policy

- Exact source chunks are contiguous, UTF-8-safe and at most1024 bytes. They cover every source byte without an unreported lossy summary. Metadata records repository/source/revision/content hash/byte interval and actor attribution.
- Unicode text is NFKC-normalized and casefolded ONLY for lexical indexing. Word tokenization is `\w+`. Raw bytes never change. No stopword list, stemming or embeddings.
- BM25 uses `k1=1.2`, `b=0.75`, `log(1+(N-df+0.5)/(df+0.5))`, one contribution per distinct query token, and scoped document frequency. Ties use exact chunk ID.
- Top16 includes zero-scoring candidates when needed. This is a bounded pool, not a completeness claim. All eligible IDs and exclusions remain in receipts.
- MMR greedily maximizes `0.75 * normalized_BM25 - 0.25 * max_Jaccard_with_selected`, with chunk-ID tie order. Maximum Jaccard is0 for the first item. Compute the whole ordering before byte-budget packing.
- Both views are packed by the same deterministic greedy-fit function under **3000 serialized UTF-8 bytes per query**, including citation metadata. Oversized rows are omitted explicitly, never silently truncated. No confidence or truth cutoff is imposed.
- Jev asks a Noul relevance question per candidate with the full query meaning in the instructions and state. Ranking is descending returned probability, with chunk-ID ties. Full distributions/usage/source bindings are retained. This is a fallible relevance score, not a relevance label or proof of truth.
- A view binds the source generations, authorized scope, actor, question and retrieval policy. Before reentry, recompute against the current store and reject changed/deleted/revoked evidence. Reordering IDs is not positional binding. Metadata from source text cannot alter host scope, commands, model or budget.

## Fresh panel and separation

A separate author chooses at most20,000 exact full-file UTF-8 bytes from committed Azdaja documentation before retrieval results are inspected. Six new queries have explicit finite answer fields and independent exact supporting spans. At least one asks for information absent from this corpus and requires `unknown`. Source corpus/tasks go to model arms, never detached gold. The verifier checks full-file bytes against the selected Git revision and all gold spans.

This is a small source-backed documentation RAG panel, not a finished code change or representative enterprise corpus. No observed failure is repaired by editing prompts, gold, thresholds or source selection after sealing. Multi-hop source coverage is graded independently from a model's decision to abstain. A full-evidence model can itself be wrong.

## Progressive gates and stop bars

### P0: provider-free correctness, mandatory

Actual fresh-process CLI and direct store checks must pass: exact Unicode reconstruction; duplicate occurrence preservation; idempotent sync; content/metadata changes; deletion and revocation; other-repo/private exclusions; invalid-batch atomicity; concurrent writer acceptance without mixed snapshots; literal BM25/MMR controls; exact context size; stale/cross-scope/tampered context rejection; actual Azdaja reentry and ordinary-session cleanup. Any failure blocks live admission until fixed and the revised methods are sealed.

### P1: local performance, mandatory before any scalability claim

Run1k and10k distinct source IDs across31 repository partitions and97 actor IDs. Text is deterministically varied and unique, but structurally synthetic, not semantically diverse. Measure disk-backed ingestion, no-op sync, one-source change, one deletion, reopen/query, database bytes and process wall time. Separate fixture generation/serialization from measured storage time and report both. Queries remain scoped. Record the actual eligible population rather than asserting sublinear global search. A correctness failure stops the benchmark. A phase exceeding30 seconds stops that scale and records incomplete, not a faster partial result.

### P2: one bounded native RAG pilot, only after P0 and source audit

- Models: requested/returned `jev-1.13.0`, and `gpt-5.6-sol` through the existing actual native `llm` route.
- Maximum6 typed requests,96 typed questions,3 logical generative calls,500,000 reported typed input tokens and900 seconds. Native per-call limits remain tighter where applicable. Unknown usage or contract/model drift stops without retry.
- Order: six relevance requests in stable task-ID order, then one batched generative call per arm in fixed order **BM25+MMR, Jev view, full evidence**. Each field is answered from its own declared view. The full-evidence reference receives the whole source corpus, not gold-selected excerpts.
- State<=24,000 serialized bytes per request and<=64 questions. If any preregistered pack does not fit, stop before inference rather than truncate or silently split.
- One explicit live admission marker, source/binary/input hashes and separate new output directory. Retain failed calls, unknown usage and setup failures. No rerun to find a positive result.
- Quality bar: every required known field correct and source-supported, the absent-information field unknown, and no invented/private/stale evidence. Report per-method fields and complete queries, not just aggregate accuracy.
- Advantage bar on this panel: Jev view improves supported complete-query count over BM25+MMR with no extra unsupported answers and at most2x measured retrieval-plus-answer call time, OR matches quality while reducing both observed input-token use and measured call time by at least20%. Full-evidence reference is reported separately. Failing this bar is a negative result, not a reason to lower the bar.
- Dollar reporting uses measured tokens and the current documented typed rate only. Generative billing is unknown unless independently available. Cold ingestion is amortized only when an explicit query count is stated. Single runs are descriptive, not confidence intervals or production SLOs.

## Not covered

Cross-machine replication, malicious multi-tenant containment, authenticated actor mapping, production automatic ingestion, PDF/OCR/web connectors, secure historical erasure, million-event semantic quality and a general RLM advantage are outside this bounded prototype. They need separate interfaces, threat models and evidence. Do not present SQLite scalability or a tiny RAG win as those results.
