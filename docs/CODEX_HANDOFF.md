# Codex handoff — evaluation and ML preparation

These are integration instructions, not completed implementation. The current repository, professor requirements and student decisions remain authoritative. Do not modify GitHub or the architecture merely because these files recommend an experiment.

## 1. Add the artifacts and validate inputs

Suggested locations: `docs/EVALUATION_PLAN.md`, `docs/ML_RECOMMENDATION.md`, `docs/CODEX_HANDOFF.md`, `data/evaluation/evaluation_gold.json`. Adjust local documentation links to those paths. Keep the gold file and label tables out of the ingestion input directory, vector index, LLM prompts and application image. Preserve the original corpus manifest and citation CSV.

Read the actual repository schema first. The JSON's Paper IDs and conceptual relations are source identities, not asserted live database IDs. Add a mapping layer to existing IDs and interfaces; do not redesign ingestion to match this artifact.

Acceptance: 15 unique cases; 10 SOURCE_VERIFIED, 2 PENDING_REVIEW, 3 BEHAVIOR_SPEC_ONLY; 20 evidence records; three PDF hashes match; every excerpt matches its declared raw-page offsets. Factual answers require independent student approval for final scoring. The JSON records no executed result.

## 2. Map evidence to ingested chunks

Resolve `(paper work ID, pinned version/hash, PDF page, context span)` to actual chunks after PDF parsing finishes. These offsets use unnormalized pypdf 6.10.0 page text; application-normalized offsets require the ingestion mapping. Do not directly copy offsets into a differently normalized string. If mappings or hashes fail, flag the record for review; do not silently shift it.

Reference sections must remain available for citation validation and retrieval even if excluded from semantic method-use extraction. Q08 needs both bibliography entries. Q09 additionally needs explicit method-use statements. Test the reference-to-work identity separately from the selected target version: the bibliography does not specify v1.

Acceptance: every answerable case resolves to actual supporting chunks or has a documented blocking reason; no fake Chunk IDs. Use full contextual passages when scoring, not only the tiny stored excerpt.

## 3. Run paired retrieval and guardrail checks

Build the smallest adapter around the existing ask/retrieval interfaces. Send **only the question and explicitly allowed synthetic fixture fields** to the system; never send expected answers or handpicked gold evidence as ordinary retrieved context. Retrieve the same real corpus in vector and hybrid modes. Record configuration, evidence, raw answers, timings and operational tool traces. Implement the metrics and denominators in EVALUATION_PLAN.md. Preserve missing dependencies/timeouts as failures.

Run the ten source-verified factual cases for semantic/citation scoring after student approval; otherwise mark scores provisional. Q10/Q11 need student abstention-label review. Q13–Q15 require dedicated fixtures and must be reported separately. For Q14 inject the raw mutation string into the validator only and assert zero executor writes; do not run the mutation even in a disposable database. A successful refusal is not proof that the validator boundary was exercised.

Acceptance: paired result rows and a per-case source review, plus a real multi-tool graph trace where available. A test suite passing on mocked responses does not establish real-model GraphRAG quality. Do not claim hybrid superiority without the recorded comparison. Q04/Q12/Q13 and Q01/Q15 are correlated variants.

## 4. ML decision boundary

Recommendation: choose the Method/Evaluation Chunk classifier described in ML_RECOMMENDATION.md. It requires actual annotations and graph features; the JSON's QA facts are not ML labels. Record the student's adoption in the normal project decision process before implementing the alternative. This handoff does not change the existing citation-link experiment or create annotations.

Once adopted: use the fixed six-paper training / two-paper test proposal; freeze reviewed Chunk labels; export the eight label-blind graph features; fit the majority baseline and one regularized logistic model; save real held-out predictions and metrics. Keep test labels isolated and fit preprocessing on training data only. No paid services, GNN or new graph labels/relations are needed.

Acceptance: reproducible training/evaluation commands, actual counts, reviewer evidence, leakage checks and honest baseline comparison. Until these exist, the ML requirement remains unverified. Do not claim that the recommended target of 96 annotations already exists.
