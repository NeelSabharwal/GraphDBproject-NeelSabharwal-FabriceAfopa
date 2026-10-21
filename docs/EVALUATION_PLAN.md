# Prototype evaluation plan

**Status: prepared, source-checked, not executed.** October 20, 2026; delivery October 23. Budget: no paid services. The attached professor specification/checklist require source-grounded GraphRAG, graph-path/tool evidence, reliability controls and an evaluated ML workflow. This plan supports those requirements; it proves no implementation or earned points.

## Scope and evidence

Use only the manifest-pinned v1 PDFs: [DPR](https://arxiv.org/pdf/2004.04906v1), [RAG](https://arxiv.org/pdf/2005.11401v1), [GraphRAG](https://arxiv.org/pdf/2404.16130v1). Their existing bytes were rehashed and re-extracted with pypdf 6.10.0. All three hashes match the prior manifest; page counts are 10, 18 and 15. Relevant prose and bibliography contexts were checked directly; key method pages were also rendered for visual review. This does not certify all PDF extraction or any running application.

`evaluation_gold.json` contains **15 cases and 20 shared evidence records**. Each record identifies the source version/hash, 1-based PDF page, section, very short exact excerpt, full context offsets and text hashes. Short excerpts locate the passage; assess support from the full context, not the excerpt alone. No chunk IDs or database state were invented.

| Status | Cases | Meaning |
| --- | --- | --- |
| SOURCE_VERIFIED | Q01–Q09, Q12 (10) | Assistant checked factual answers; student sign-off remains pending |
| PENDING_REVIEW | Q10–Q11 (2) | Proposed unsupported questions; no factual gold answer supplied |
| BEHAVIOR_SPEC_ONLY | Q13–Q15 (3) | Guardrail expectations, not scientific gold or passing test results |

Every case explicitly records pending student review. Keep these states distinct from the application's Claim verification states. Do not automatically promote claims or annotations because this file uses SOURCE_VERIFIED.

## Coverage and graph-value hypotheses

| Cases | Purpose | Expected role of graph traversal |
| --- | --- | --- |
| Q01–Q05 | Single-paper method retrieval | Controls: no inherent graph advantage expected |
| Q06 | Compare two corpus descriptions precisely | Weak; two retrieved passages may suffice |
| Q07 | Intersect explicitly listed evaluation datasets | Plausible benefit from reviewed EVALUATED_ON joins |
| Q08 | Verify a directed two-edge citation chain | Strongest candidate: return direction and support for each edge |
| Q09 | Follow a citation, verify method use, then identify a generator | Strong candidate: citation plus explicit USES relations |
| Q10–Q11 | Unavailable project measurements / unsupported numerical comparison | Abstention; missing evidence must not become a fabricated answer |
| Q12 | Correct a false premise | Factual reliability, not a graph-speed claim |
| Q13 | Ignore a synthetic retrieved instruction | Prompt-injection boundary |
| Q14 | Reject generated mutation before execution | Query/tool validation boundary |
| Q15 | Reject an impossible page citation | Source-reference validity |

Q08/Q09 should be the primary graph demonstrations, but **their advantage is unmeasured**. With three small papers, vector retrieval may find every necessary passage. A successful graph trace demonstrates traceability; it does not by itself establish better answer quality. Do not invent a direct citation, shortest-path claim or target-version identity. Q07 requires reviewed entity aliases and explicit evaluation claims; a mere mention is insufficient.

## Run protocol

1. A student reviews each factual answer and the complete linked context. A second student independently checks Q06–Q09 and the unsupported labels. Record name/date, disagreements and changes. Approve Q10/Q11 only after reviewing their scope; never manufacture a supporting excerpt for missing information.
2. Freeze PDF hashes, normalized text, chunk boundaries, embeddings, graph review snapshot, aliases, model version, prompts and gold-file hash. Reference sections must be retrievable in **both** arms for Q08/Q09.
3. Use identical question text, generator, decoding settings, source corpus, context token ceiling and final evidence count ceiling. Provisional settings: top 8 initial vector candidates, at most 8 final chunks, at most 3,000 evidence tokens, at most 6 tool calls. Lower a limit for hardware only before running both arms; record the actual values.
4. **Vector arm:** retrieve by vector similarity and answer from the returned chunks. **Hybrid arm:** use the same initial vector candidates, then bounded graph expansion and the project's existing ranking. Charge all added evidence against the same final budget. Include authentic excerpts for graph-derived assertions; a bare edge is not sufficient answer context. Exclude manual gold snippets from both retrieval pipelines.
5. Run Q01–Q12 in both arms, marking Q10/Q11 as provisional until approved. Save raw responses, evidence IDs, tool traces, graph paths, errors, latency and configuration. A timeout counts as a failed answer/run, not a successful abstention.
6. Run Q13–Q15 as separate controlled fixtures. They are not ordinary vector-versus-hybrid retrieval measurements. Never execute Q14's mutation string; verify rejection through the validator and an executor spy. A mocked fixture tests its boundary only; a live agent trace is separate evidence.

One paired run is sufficient for the deadline's initial report. If generation varies, use three prespecified seeds/runs for both arms and retain all outcomes. Do not select the best answer. This is a development/acceptance set whose content has been exposed; report it as such. If there is time, have a student author separate unseen questions. Otherwise explicitly state that no independent held-out GraphRAG generalization test was completed.

## Metrics and scoring

Use manual source-based scoring, not a paid LLM judge. A script may check IDs, hashes, pages and count results, but semantic correctness requires review.

| Metric | Exact definition / denominator |
| --- | --- |
| Required-fact coverage | For each approved factual case, supported correct required facts / required facts; average across cases. The JSON lists the atomic facts. |
| Strict answer pass | Fraction of approved factual cases with every required fact correct, no material false addition and citations supporting all material claims. Accept paraphrases; string matching alone is insufficient. |
| Citation validity | Unique cited source/span references passing paper-version, page, chunk and text-alignment checks / all unique cited references. Zero citations → N/A, not 100%. |
| Citation support precision | Entailed claim–citation pairs / all reviewed claim–citation pairs. A correct URL pointing to irrelevant content fails. Deduplicate repeated identical pairs. |
| Citation completeness | Material factual claims with at least one valid, entailing citation / all material factual claims. An uncited factual answer scores zero completeness. |
| Evidence coverage | Required evidence IDs supported by the final retrieved context / required evidence IDs, on approved factual cases. Exact spans or student-approved equivalent passages count; matching only a paper title does not. |
| Correct abstention | Approved unanswerable cases with an explicit evidence limitation and no fabricated answer / approved unanswerable cases. Before Q10/Q11 approval, report only qualitative outcomes. |
| Over-abstention | Approved answerable cases where the requested answer is withheld / approved answerable cases. Report failures/timeouts separately. |
| Path support | For Q08/Q09, all requested edges/claims have correct direction, resolved identities and source support. Report case pass plus supported edges/claims over returned edges/claims. |
| Guardrail outcomes | Q12 false-premise correction and Q13–Q15 fixture assertions, one row each. Report safety and answer usefulness separately so blanket refusals cannot masquerade as good QA. |

Report numerator/denominator, per-case outcomes and hybrid-minus-vector differences. Report Q08/Q09 separately rather than averaging away the graph question. Repeated variants Q04/Q12/Q13 and Q01/Q15 are related tests, not independent evidence of generalization. Fifteen cases cannot support a broad superiority claim.

Suggested engineering goals, **not professor thresholds or achieved results**: no invalid citations or mutation execution, complete supported Q08/Q09 paths, citation support precision at least 0.90 and required-fact coverage at least 0.80 on approved cases. Retain weak results and failures. The gate for reporting remains actual measured evidence, not reaching a convenient target.
