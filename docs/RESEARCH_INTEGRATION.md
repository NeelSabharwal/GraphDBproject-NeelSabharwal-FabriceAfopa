# Research integration and review preparation — 2026-10-20

Scope: prompt #5.2 on `feat/agent-evidence`; deadline October 23; zero paid services.
Local Git history contains merged PR #2 (`aefda4a`) and PR #3 (`e605930`). No ingestion,
claim approval, alias merge, agent, GDS run or ML training was performed here.

## Preserved inputs and validation

The eight supplied artifacts are preserved byte-for-byte:

- `docs/CODEX_HANDOFF.md`, `docs/EVALUATION_PLAN.md`, `docs/ML_RECOMMENDATION.md`;
- `data/evaluation/evaluation_gold.json`;
- `docs/CODEX_GRAPH_HANDOFF.md`, `docs/ENTITY_ALIAS_REVIEW.md`, `docs/GDS_READINESS.md`;
- `corpus/GRAPH_EVIDENCE_CANDIDATES.csv`.

The teammate's `docs/EVALUATION_REVIEW.md` and
`scripts/verify_evaluation_evidence.py` are also unchanged. Their example command
assumes the gold file/PDFs are in the current directory. Repository-compatible flags
are `--gold data/evaluation/evaluation_gold.json --pdf-dir data/raw`; the script already
constructs the actual `2004.04906v1.pdf`, `2005.11401v1.pdf`, `2404.16130v1.pdf` names.
No script-path fix or source-hash/offset edit is necessary.

Actual checks under **pypdf 6.10.0**:

| Check | Actual outcome |
| --- | --- |
| Prototype PDF SHA-256, version marker, page count | All 3 match manifest; 10 / 18 / 15 pages |
| Gold cases / registry | 15 unique cases, 20 unique evidence records; all references resolve |
| Gold status counts | 10 assistant SOURCE_VERIFIED, 2 PENDING_REVIEW, 3 BEHAVIOR_SPEC_ONLY |
| Gold page hashes, exact excerpt offsets and context hashes | 20/20 pass; zero verifier errors |
| Scientific candidate registry | 20 unique GE01–GE20 rows; 14 proposed entities |
| Candidate domains/ranges | 6 USES, 11 EVALUATED_ON, 3 ADDRESSES; all typed correctly |
| Candidate pinned URL/hash/page, raw excerpt/context coordinates/hashes | 20/20 pass |
| Candidate provenance/review | manual research route, assistant source reading, SOURCE_LOCATED; all pending |
| Live chunk text/hash/coordinate agreement | 153 chunks checked; all agree with pinned normalized pages |
| Raw-to-live-chunk mapping | All 40 records mapped; no missing source spans |
| Semantic approvals / aliases | None performed; proposed IDs are not live entity IDs |

All 15 gold cases still have student review PENDING with no reviewer/time. The gold
file's SOURCE_VERIFIED means assistant checking **only**; it is not a graph status
transition, ML label or student sign-off. Treat the 20 scientific candidates as
pending EXTRACTED candidates after future validation, never approved source facts.
They are preserved review artifacts, not imported claims. Existing ingestion accepts
LLM extractions; adding manual research imports requires a separately scoped adapter,
not an ingestion rewrite in this task.

Cross-artifact consistency: the handoffs, alias notes and GDS readiness note agree on
pending student review, work-versus-version citations and the approved-claim-only
projection. GE20 retains component-only evaluation scope. The original ML recommendation
is now adopted **provisionally** through D17, not treated as an instruction to train.
Its eight-paper/96-label targets are conditional. The GDS 0.75-weight example is
conditional arithmetic under all proposed approvals, not measured live topology.

## Evaluation limitations still open

The older review's 8/20 result under pypdf 5.9.0 was a version-specific observation.
The unchanged inputs now reproduce **20/20** under 6.10.0. This resolves that coordinate
blocker, not semantic approval or application evaluation. No answer-quality scores,
retrieval comparisons or guardrail outcomes were produced.

The review's proposed Q15 `candidate_citation_to_validate` field is **still absent**.
The user-page rejection and forged-output-citation rejection need separate future
tests. Preserve the original gold file; any amendment needs an explicit annotation
version and review. Q03's wording clarification is also still a proposed semantic edit.
Q08/Q09 cannot claim verified graph paths until C03/C09 and their required scientific
claims are reviewed. Q07 also depends on reviewed shared-dataset aliases.

The 15 cases are exposed development/acceptance material, with correlated variants;
they are not a hidden generalization test. Their labels/expected answers do not
belong in extraction prompts, retrieval context, features or the graph.

## Isolation and reproducible commands

`.gitignore` now ignores every data child by default, permits the evaluation directory,
and permits **only** `data/evaluation/evaluation_gold.json` within it. Raw PDFs,
extracted text, generated data, caches, credentials and model weights remain ignored.
The existing Docker build allowlist excludes data/corpus/docs, so the gold file is not
in the application image. The runtime application and ingestion never load it.
Do not add a broad evaluation-data mount to a future agent service. The following
mounts are for offline audit containers only; no inference endpoint is called.

```bash
docker compose run --rm --no-deps \
  -v "$PWD/scripts:/workspace/scripts:ro" -v "$PWD/data:/workspace/data:ro" \
  api python scripts/verify_evaluation_evidence.py \
  --gold data/evaluation/evaluation_gold.json --pdf-dir data/raw

docker compose run --rm --no-deps --user "$(id -u):$(id -g)" \
  -v "$PWD/app:/workspace/app:ro" -v "$PWD/scripts:/workspace/scripts:ro" \
  -v "$PWD/corpus:/workspace/corpus:ro" \
  -v "$PWD/data/evaluation:/workspace/data/evaluation:ro" \
  -v "$PWD/data/raw:/workspace/data/raw:ro" \
  -v "$PWD/data/processed:/workspace/data/processed" \
  api python -m scripts.verify_research_handoff --root /workspace
```

The new audit tool checks structures/provenance, uses fixed read queries, verifies live
chunk text, exports normalized/chunk-local spans, and checks the graph fingerprint
is unchanged. Output is ignored `data/processed/research-review/validation.json`.
It prints metadata/counts, not expected answers. A nonzero exit means a failed audit;
do not use unresolved spans as verified mappings. `--output` selects a local audit
file for isolated negative-control runs.

## Raw evidence to actual chunk IDs

Raw coordinates refer to unnormalized pypdf page text, while chunk offsets refer to
normalized page text. Use the parser's raw-start/raw-end mapping to map each interval,
then cover the normalized interval with actual page-bounded chunks. Never copy raw
indices directly. Each excerpt fits one chunk, but **12 candidate contexts and 10 gold
contexts need two chunks**; retain full-context supports for semantic review.
Overlapping chunks can provide alternative valid excerpt supports. K-keys below are
local display keys for real IDs, not new nodes or entity aliases. Machine-readable
output contains exact normalized-page and chunk-local offsets for every support.
| Key | Existing Chunk ID |
| --- | --- |
| K01 | `06c89eaeeaa709fce9d3eeaec500704cdfbd866309d0894f5169d76999b33ce0` |
| K02 | `10a700b91b8958b06cc812de4df4d3911f9556ec9be2bbae43403a90728c619b` |
| K03 | `11a949312bcfa9ab07b91e0027aec7b978442abf6e29da56d5d8e9e7d60d9d94` |
| K04 | `11bc5bdbf555c1dffce5736b7b291f6d24d9a940261afee4733f512f398b4b0b` |
| K05 | `1eaf6f982e0dff29e72e45893f4d71485bfcc7984c0ff16cdbec32c9eee238ad` |
| K06 | `20458f66656ee3a42e0b7cd4ed809f17a06f42b8881e89ec0a37548518123db0` |
| K07 | `242f1e4ea282d55c962e205e4352d9dd0bfc0df49ce36be71dfe81deb1541c7d` |
| K08 | `24bfdc5433a63ac37727b1e67388c542bdecc9218d924c442c08a337ceb0d4b2` |
| K09 | `256f935537faa66d1cc6cce9623e010a3c9612d1e77017620c2d923b0c6ebebe` |
| K10 | `44523ced489eef3f98ec37d67ce02025c66a8556c2a14954255c9bf1a5e5e6c3` |
| K11 | `614d6ca7a5b6e7189ce1ec976756d86e369cdb70cf0ca75f4a388199470e2b9f` |
| K12 | `62a59ed9dcd80e7da04f325abd5ed9ea4131960bd0b793bbe324490e4003581d` |
| K13 | `651d3ede4b76912d5aa04aecd2e6a7a4e42008cf3447e928cd13290d584eed0d` |
| K14 | `6e57fbafe67c9c13dc9a44d52d0432a361c4ba2a6f0b764c4026dfe442884f65` |
| K15 | `70211c11062664ee7cc1d112026fbfd6958b48309c76e07b6759bd6ff6d658da` |
| K16 | `7c3f63ae733fb4207c354cc67dfaeda3c60d782ca71043c555dd627701de4957` |
| K17 | `8972c467bd5b1f590252892e8d363984301e601c945805ffe590c371f964b33a` |
| K18 | `99d443f9eb46e05ca7393c5594be959c500c0fe7fdeba3a7e33ca8b135678df9` |
| K19 | `abeb54c8ae01e48f9bc5412ccae6c614a369afa29cda969c7d6c3dd3e2175d9a` |
| K20 | `ace0086b047574f03e499fac80efe3cab4afd63862be668266b8fbaf86362ae5` |
| K21 | `b5db00dcf2bce7c40d4a67a210fb4c80fee48b60cf4adbf4abad0fb4557932ca` |
| K22 | `bc82c6c4c872cc4b07170569d06261a255d1c9bcccb8c18c4e3aac7540b4153b` |
| K23 | `c11cac7868c07ded56639c91e57a045f67c1e44b4ef94194e190351a57e6bb01` |
| K24 | `c664046a6df44e38d10090ba6f5a5f7b041f24cf4a766a87df5e0b812223b74a` |
| K25 | `cc3eefc367d26128befbc1724498029aebf9799afd21000ad494e093a1511f62` |
| K26 | `d150f9c0a2771388e84e81608154d701219dcc1b4926e7600355a458cace4bef` |
| K27 | `d1c3c5ec507d7347b4ae7774a412d5870d24aa9d32caba18e38b93585b24e1d9` |
| K28 | `f67778ff5f3fa948315dbaa3fc9098162bed80417a1e22c106ad28f080b91146` |
| K29 | `fc1c8aea398b9fb9db9fb75079e04f3396458705c92d443511790e8afc17358a` |

| Evidence ID | Paper / PDF page | Raw excerpt [start,end) | Raw context [start,end) | Excerpt chunk | Full-context chunks |
| --- | --- | --- | --- | --- | --- |
| GE01 | arxiv:2004.04906v1 / 3 | [2441, 2461] | [2312, 2584] | K24 | K18 |
| GE02 | arxiv:2004.04906v1 / 2 | [2659, 2699] | [2631, 3693] | K02 | K02 |
| GE03 | arxiv:2004.04906v1 / 4 | [2716, 2738] | [2460, 3911] | K27 | K27, K28 |
| GE04 | arxiv:2004.04906v1 / 4 | [2947, 2964] | [2460, 3911] | K27 | K27, K28 |
| GE05 | arxiv:2004.04906v1 / 4 | [3079, 3091] | [2460, 3911] | K27 | K27, K28 |
| GE06 | arxiv:2004.04906v1 / 4 | [3219, 3230] | [2460, 3911] | K27 | K27, K28 |
| GE07 | arxiv:2005.11401v1 / 3 | [1650, 1662] | [1597, 2401] | K12 | K12 |
| GE08 | arxiv:2005.11401v1 / 3 | [1800, 1809] | [1597, 2401] | K12 | K12 |
| GE09 | arxiv:2005.11401v1 / 3 | [2508, 2525] | [2401, 3001] | K23 | K23 |
| GE10 | arxiv:2005.11401v1 / 4 | [2942, 2966] | [2783, 3881] | K26 | K26, K22 |
| GE11 | arxiv:2005.11401v1 / 4 | [3547, 3569] | [2783, 3881] | K26 | K26, K22 |
| GE12 | arxiv:2005.11401v1 / 4 | [3577, 3585] | [2783, 3881] | K26 | K26, K22 |
| GE13 | arxiv:2005.11401v1 / 4 | [3598, 3610] | [2783, 3881] | K22 | K26, K22 |
| GE14 | arxiv:2005.11401v1 / 4 | [3625, 3636] | [2783, 3881] | K22 | K26, K22 |
| GE15 | arxiv:2404.16130v1 / 4 | [3468, 3481] | [2892, 3816] | K07 | K07, K06 |
| GE16 | arxiv:2404.16130v1 / 3 | [512, 533] | [316, 695] | K09 | K09 |
| GE17 | arxiv:2404.16130v1 / 1 | [817, 851] | [421, 2005] | K17 | K17, K14 |
| GE18 | arxiv:2404.16130v1 / 6 | [1773, 1788] | [1426, 2243] | K29 | K29 |
| GE19 | arxiv:2404.16130v1 / 6 | [2109, 2121] | [1426, 2243] | K29 | K29 |
| GE20 | arxiv:2404.16130v1 / 3 | [2406, 2430] | [1780, 2699] | K19 | K10, K19 |
| D01 | arxiv:2004.04906v1 / 3 | [2441, 2461] | [2312, 2584] | K24 | K18 |
| D02 | arxiv:2004.04906v1 / 3 | [1313, 1324] | [845, 1377] | K18 | K13 |
| D03 | arxiv:2004.04906v1 / 4 | [2183, 2202] | [1699, 2460] | K25 | K25 |
| D04 | arxiv:2004.04906v1 / 4 | [1802, 1815] | [1699, 2460] | K25 | K25 |
| D05 | arxiv:2004.04906v1 / 4 | [2464, 2491] | [2460, 3911] | K27 | K27, K28 |
| R01 | arxiv:2005.11401v1 / 4 | [417, 448] | [0, 450] | K05 | K05 |
| R02 | arxiv:2005.11401v1 / 3 | [1142, 1166] | [738, 1597] | K08 | K08, K12 |
| R03 | arxiv:2005.11401v1 / 4 | [2204, 2228] | [1907, 2783] | K11 | K11, K26 |
| R04 | arxiv:2005.11401v1 / 4 | [2147, 2160] | [1907, 2783] | K11 | K11, K26 |
| R05 | arxiv:2005.11401v1 / 4 | [3509, 3545] | [2783, 3881] | K26 | K26, K22 |
| R06 | arxiv:2005.11401v1 / 13 | [726, 742] | [547, 788] | K16 | K16 |
| R07 | arxiv:2005.11401v1 / 3 | [1650, 1662] | [1597, 2401] | K12 | K12 |
| R08 | arxiv:2005.11401v1 / 3 | [2515, 2525] | [2401, 3001] | K23 | K23 |
| G01 | arxiv:2404.16130v1 / 4 | [3468, 3481] | [2892, 3816] | K07 | K07, K06 |
| G02 | arxiv:2404.16130v1 / 5 | [2429, 2451] | [1522, 2965] | K15 | K01, K15 |
| G03 | arxiv:2404.16130v1 / 5 | [2695, 2719] | [1522, 2965] | K15 | K01, K15 |
| G04 | arxiv:2404.16130v1 / 13 | [2379, 2389] | [2379, 2655] | K21 | K21, K20 |
| G05 | arxiv:2404.16130v1 / 7 | [1053, 1078] | [0, 1806] | K03 | K03, K04 |
| G06 | arxiv:2404.16130v1 / 6 | [1640, 1660] | [1426, 2243] | K29 | K29 |
| G07 | arxiv:2404.16130v1 / 6 | [1902, 1916] | [1426, 2243] | K29 | K29 |

## C03/C09: read-only inspection first

Actual inspected claims (both EXTRACTED / SOURCE_LOCATED / pending):

| Evidence | Real Claim ID | Pinned source and reference | Cited work |
| --- | --- | --- | --- |
| C03 | `222c833171dc108fb82236c75de7be8bdfd159b58fa18b54de9d9eee82c0c206` | RAG v1 PDF page 13, reference [22] | arxiv:2004.04906 |
| C09 | `87e9c7f0228c0da86e2fc46679dfc09c2cad356f889f8c92324b605cf9f7eadd` | GraphRAG v1 PDF page 13, Lewis et al. (2020) | arxiv:2005.11401 |

Use the real source PDFs `data/raw/2005.11401v1.pdf` and
`data/raw/2404.16130v1.pdf`, page 13 in a PDF viewer. Recheck bytes against
`corpus/corpus_manifest.json`; the audit above already checks pinned hashes. For
reference-title coordinates use the unchanged `corpus/citation_evidence.csv` C03/C09
rows, not gold expected answers. Their page hashes must match pypdf 6.10.0 before
reading raw offsets. R06/G04 above provide additional full-context chunk mappings.

This fixed query only inspects the stored assertion and supporting quote:

```bash
docker compose exec -T api python - <<'PY'
from neo4j import GraphDatabase, Query
from app.config import Settings
config = Settings.from_environment()
with GraphDatabase.driver(config.neo4j_uri,
    auth=(config.neo4j_user, config.neo4j_password.get_secret_value())) as driver:
    with driver.session(default_access_mode="READ") as session:
        rows = session.run(Query("""
            MATCH (c:Claim)-[:SUBJECT]->(source:Paper),
                  (c)-[:OBJECT]->(target:Paper), (c)-[support:SUPPORTED_BY]->(chunk:Chunk)
            WHERE c.evidence_id IN $ids
            RETURN c.id AS claim_id, c.evidence_id AS evidence_id, c.status AS status,
                   c.student_review_status AS review_status, source.id AS source,
                   source.pdf_sha256 AS source_hash, chunk.id AS chunk_id,
                   chunk.page AS pdf_page, support.quote AS quote,
                   support.start_char AS chunk_quote_start, support.end_char AS chunk_quote_end,
                   target.work_id AS target_work, c.target_version_as_cited AS target_version_as_cited
            ORDER BY evidence_id
        """, timeout=5), ids=["C03", "C09"])
        for row in rows:
            print(dict(row))
PY
```

The fixed query is read-only. Driver READ routing is not a database permission boundary
in Community edition; never replace this template with arbitrary generated Cypher.
Student review must check author/title/work identity and the full reference context,
not infer a target v1 from the corpus representative. No citation implies method use.

## Separate human-triggered review action

After independently inspecting a claim, an actual student sets the host environment
variables `CLAIM_ID`, `REVIEWER_NAME`, `REVIEW_NOTE`, and `REVIEW_DECISION` to their real
claim selection, name, specific findings and either APPROVE or REJECT. Do not use
example names or copied rationales. Perform one decision at a time. This is an
explicit graph write, separate from the read-only inspection above; **not executed
by this integration task**.

```bash
docker compose run --rm --no-deps -T -v "$PWD/app:/workspace/app:ro" \
  -e CLAIM_ID -e REVIEWER_NAME -e REVIEW_NOTE -e REVIEW_DECISION api python - <<'PY'
import os
from neo4j import GraphDatabase
from app.config import Settings
from app.ingestion.graph import EvidenceGraph
claim_id = os.environ["CLAIM_ID"]
reviewer = os.environ["REVIEWER_NAME"]
note = os.environ["REVIEW_NOTE"]
decision = os.environ["REVIEW_DECISION"]
if decision not in {"APPROVE", "REJECT"}:
    raise ValueError("Explicit APPROVE or REJECT decision required")
config = Settings.from_environment()
with GraphDatabase.driver(config.neo4j_uri,
    auth=(config.neo4j_user, config.neo4j_password.get_secret_value())) as driver:
    EvidenceGraph(driver).review_claim(claim_id, reviewer, note, approved=(decision == "APPROVE"))
PY
```

The existing method validates stored quote alignment, records reviewer/time/note/history,
sets SOURCE_VERIFIED or REJECTED, and refreshes derived citations atomically. A true
citation approval can create a CITES edge; rejection removes its support from the
cache. Re-import preserves explicit reviews. This is a local operator attestation,
not identity authentication. Never call this method from an LLM tool or treat the
research file's status as permission to execute it. Rerun read-only inspection after
a real decision and retain the actual review record.

## ML and readiness for prompt #6

D17 and architecture section 7 now provisionally choose Method/Evaluation classification
with real within-paper graph features, source-reviewed labels and held-out whole papers.
The original research files remain recommendations; no labels or model were created.
Only three papers are ingested and three MENTIONS relationships exist, so an eight-paper
feature/label experiment is not ready. Constant/missing features are a blocker, not a
reason to substitute section names or QA gold. GDS algorithms remain separate work.

Ready to **scope** a first LangGraph implementation using actual chunks, typed read-only
tools, conditional state, evidence traces and abstention. It is not ready to claim a
verified citation-path demo or a scored evaluation pass: C03/C09, scientific candidate
claims/aliases and factual evaluation cases still require student review. Reference
chunks are mapped; vector embeddings/index and agent behavior remain unimplemented.
The manual-research import adapter and alias review must be explicitly scoped before
using the 20 candidates as graph assertions. Keep gold and labels offline throughout.

## Checks executed in this integration task

- Teammate evidence verifier: exit 0, 20/20 evidence records, zero errors, pypdf 6.10.0.
- Reusable handoff audit: exit 0, 20/20 candidates and 20/20 gold evidence mapped,
  all 153 live chunks checked, zero errors, unchanged graph fingerprint.
- Negative control: a temporary copy with only D01's page hash corrupted returned
  exit 1 and exactly `D01: Raw page hash mismatch` (19/20 gold checks). Original
  annotations remained unchanged; this is expected rejection, not a source failure.
- Ignore checks: 9/9 representative paths match the intended gold-only exception.
- Source preservation: all 14 recorded hashes unchanged, including all eight supplied
  artifacts, teammate review/script, manifest/citation inputs and professor documents.
- Rubric checks: all 49 original criterion identities/point allocations preserved;
  total 100. Proposed six/two ML paper sets are disjoint and present in the manifest.
- The documented read-only citation query was executed; no human review write was executed.
- `git diff --check` passed. Application behavior was not changed; pytest/coverage
  and live model inference were not rerun for this research/documentation integration.

The eight pre-existing untracked inputs remain untracked and byte-identical. This
task changed `.gitignore`, PROJECT_PLAN.md, ARCHITECTURE.md and DECISIONS.md; added
this report and the offline audit script; and wrote ignored local audit reports.
Nothing was committed, pushed or approved.
