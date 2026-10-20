# Three-paper evidence ingestion

Implemented on `feat/document-ingestion`, 2026-10-20, under prompt #5 and the
subsequent bounded corrections in prompt #5.1. Zero paid
services. This milestone implements a local CLI; the HTTP API remains health-only.
No LangGraph agent, embeddings/vector index, GDS analytics or ML was implemented.

## Reproduction

Prerequisites: existing Compose services healthy, `.env` configured, approved
models installed, and the supplied `corpus/` handoff present. Rebuild for the new
pypdf dependency; no changes to Compose resource limits or services are required.

```bash
docker compose build api
make ingest
make test
make ingest  # checks existing PDFs, revalidates cached extraction, merges unchanged graph
```

`make ingest` launches a temporary API-image container on the Compose network, as
the host UID/GID, with current application/scripts and corpus read-only, and
`data/` writable. Only the three prototype entries are accepted. No source files
or PDFs enter the image. `make test` likewise mounts current code, runs unit/API
and real Neo4j tests, and writes ignored `data/processed/coverage.xml`. Fixture
cleanup deletes only records belonging to a fresh per-test UUID, never the corpus.

Equivalent Python CLI inside that container:

```bash
python -m scripts.ingest --root /workspace --sample-per-paper 1
python -m scripts.ingest --root /workspace --download-only
```

The sample argument accepts 0–2 chunks per paper; default 1 selects a maximum
500-character window around explicit method use: BERT (DPR PDF page 3), BART-large
(RAG page 3), Leiden (GraphRAG page 4). A second requested sample uses first-page
prose. Original chunks, IDs, pages and coordinates are unchanged.

Automated-script exit contract (prompt #5.1):

- **0:** core PDF/graph import succeeded. Optional extraction can fail; the JSON report
  then says `overall_status=PARTIAL_SUCCESS`, `import_status=SUCCEEDED`,
  `extraction_status=FAILED` and records the failed attempts.
- **1:** core download, parser, citation validation or database import failure.
  Per-paper results show any already-completed imports.
- **2:** with `--require-extraction`, core succeeded but optional extraction failed.
  GNU Make reports a failed recipe as exit 2; use the Python CLI for exact code handling.

`--sample-per-paper 0` disables optional extraction. `--download-only` records
`import_status=NOT_REQUESTED`. Unavailable models, invalid extraction/cache payloads
and unavailable sampling anchors are optional failures; they do not discard core
imports. Model digest mismatches prevent inference. Saved failures are never relabeled
as successful calls. Inspect `report.json` as well as the exit status.

PR #2 correction: required in-corpus citations are preflighted before any graph
writes, including schema creation and paper metadata registration. If any fails,
the entire run aborts: affected papers are FAILED, other papers are NOT_STARTED,
the overall/core status is FAILED, and both default and strict CLI modes exit 1.
Audit details include the source paper, evidence ID and exact validation error.
Already stored graph data remains unchanged, including on failed re-import. No LLM
requests are made after a failed citation preflight. Valid citations and optional
extraction failures retain the exit contract above.

Entity validation also checks every entity, including those without claims: its
chunk must exist in the import batch and belong to the same paper. A matching chunk
elsewhere in Neo4j is insufficient. Invalid batches are rejected before writes.
PDF saving now uses a same-directory temporary file, flush/fsync and complete-file
verification before atomic replacement; failed saves clean up the temporary file
and leave an existing valid destination unchanged.

## Pinned input and parsing

| Paper | Version | SHA-256 | Pages | Chunks |
| --- | --- | --- | ---: | ---: |
| DPR | 2004.04906v1 | `2b03fbde33c88fcf82091e6325806bd2656ca777032471e182c602c76ccdab01` | 10 | 42 |
| RAG | 2005.11401v1 | `25b55fd0f7c6c91cbe2c88690a33923077103e8f563d154faa1ce11d3527e601` | 18 | 62 |
| GraphRAG | 2404.16130v1 | `33524b3b56910c513affdad8dbf67d14e68edf0572e4debdb09a9f1916463b06` | 15 | 49 |

These are measured parser outputs, not dataset targets: **43 pages, 153 chunks**.
All three files were downloaded to their manifest-designated ignored paths.
HTTP content type, PDF magic, byte count, SHA-256, page count and expected arXiv
version marker were checked. A checksum mismatch fails without replacing an existing
file or trying another version. Downloads are limited to 20 MiB per PDF.

pypdf **6.10.0** matches the handoff parser. Page numbers are 1-based PDF pages;
printed page labels are separate. Character offsets are 0-based, half-open Python
string positions in extracted text, not PDF byte positions or visual coordinates.
Each page artifact stores original text/hash, normalized text/hash, and a raw
start/end mapping for every normalized character. Per-character NFKC expands
ligatures; whitespace/control characters become collapsed spaces. Hyphenation
is retained rather than guessed.

Chunks use 1400-character windows and approximately 200-character overlap, with
whitespace boundaries, never crossing pages. This deliberately replaces the
unimplemented token/paragraph proposal with a small deterministic starting point.
IDs include paper version, PDF hash, parser/chunker version, page, offsets and
text hash. `NEXT` follows parser order across a paper's pages; it does not certify
visually correct multi-column reading order.

Observed parsing issue: **DPR PDF page 7 contains control characters**; recorded
as a warning and normalized with location mappings. No empty pages were found.
Tables, equations, OCR and visual reading-order validation remain outside scope.
The [pypdf extraction guide](https://pypdf.readthedocs.io/en/6.10.0/user/extract-text.html)
explains these layout limitations.

## Evidence graph and indexes

| Label | Implemented role |
| --- | --- |
| Paper | Selected version; work ID, title/authors/year, source URL/version/hash, license note, parse status |
| Chunk | One page span; original/normalized positions, text/hash, page label, order and parser/chunker versions |
| Entity | Exact surface candidate; Method/Dataset/Task/Topic kind, normalized name, paper-scoped ID, unresolved status |
| Topic | Additional label only when an extracted Entity has Topic kind |
| Claim | Source-specific relation, origin/status, qualifiers, quote and model/review provenance |

Directions: `Chunk → Paper PART_OF`; `Chunk → Chunk NEXT`; `Chunk → Entity MENTIONS`;
`Claim → Paper SUBJECT`; `Claim → Paper/Entity OBJECT`; `Claim → Chunk SUPPORTED_BY`;
`Paper → Paper CITES`. A mention proves only a located surface form, not method use.
Evidence edges retain quotes, offsets and hashes. No `USES` or other scientific
direct edge is generated from an LLM suggestion.

Four uniqueness constraints cover `Paper.id`, `Chunk.id`, `Entity.id`, `Claim.id`.
Their backing indexes handle merges/lookups. Four additional indexes serve work
resolution `Paper(work_id)`, entity candidates `Entity(kind, normalized_name)`,
page evidence `Chunk(paper_id, page)`, and review filtering `Claim(status, predicate)`.
No duplicate ID indexes or premature vector index are added. Index existence alone
does not claim the later EXPLAIN/PROFILE optimization criterion.

Scientific entities deliberately remain paper-scoped to avoid unreviewed global
alias merges. This limits cross-paper concept joins until students approve identity
resolution. A Topic label is created only from actual validated output, never to
inflate label counts.

## Citation review policy

Prompt #5.1 supersedes the earlier automatic approval exception. Location policy
`automated-bibliography-v1` still rechecks:

1. Source PDF identity/hash/URL and raw page hash.
2. Supplied reference-title offsets and normalized match to the target title.
3. A preceding References heading and reference entry locator.
4. First-author identity within that entry; year for author-date references.
5. Explicit target arXiv work ID when claimed by the research row.
6. Exact normalized title quote in an actual source chunk.

Research CSV status alone never passes this policy. Only the in-prototype rows
C03 and C09 are considered; absent rows are unknown, not negative evidence.
Successful automated records have `status=EXTRACTED`,
`source_location_status=SOURCE_LOCATED`, `location_policy`, `location_verified_at`,
source page/hash, raw reference context and `student_review_status=pending`.
No automatic check establishes student semantic approval.

Legacy automated SOURCE_VERIFIED claims are restored to pending review during the
next source-paper import. Full prior properties, including the old automatic reviewer,
are retained in JSON review history. Claims, support quotations and source pointers
are preserved. Only the derived CITES cache is removed until human approval.

An independent student must inspect the PDF/reference context and the resolved work,
then explicitly invoke the local operator action:

```python
graph.review_claim(claim_id, reviewer="Student full name", note="Specific source review findings", approved=True)
```

This is an explicit attestation, never called by import or an LLM. No approval was
applied to the real corpus in prompt #5.1. The method checks source-quote alignment,
records named reviewer/time/note/history, and atomically refreshes derived citations.
Rejection uses `approved=False`. CITES requires SOURCE_VERIFIED **and** approved human
review metadata under `student-semantic-review-v1`; setting status alone is insufficient.
Local operator identity is not authenticated by this method.

The target remains resolved by work identity with `target_version_as_cited=unspecified`.
The target Paper v1 is a corpus representative. The previously demonstrated
GraphRAG → RAG → DPR citation evidence remains pending; a verified CITES path is no
longer served until the two bibliography claims receive student approval.

## Extraction and reproducibility

Qwen uses the installed digest from `models.lock.json`. A request sends a fixed
system prompt, source text as untrusted data, and a JSON schema. Application-side
Pydantic validation rejects extra fields, unknown predicates/kinds, overlong output,
missing entities, invalid predicate ranges and nonmatching quotes. Entity names
must occur in their quotes. USES requires explicit author use in the prompt; exact
quote matching cannot establish semantic entailment, so **every accepted LLM claim
stays EXTRACTED**, with student review pending and qualifiers preserved.

Historical first trial `paper-extraction-v1` used bounded-string JSON grammar and a 600-token
output budget. The focused retry `paper-extraction-v2` simplifies the server grammar
while retaining all local schema bounds, limits output to 400 tokens and explicitly
sets 8 CPU threads. Context remains 2048, temperature 0, seed 42, HTTP timeout 90 s.
The initial slowdown's cause is unproven; no GPU or paid-service switch was made.
The prompt #5 revision `paper-extraction-v3` asks for only one short relation and
omits title/author text before an `Abstract` heading from the model input, retaining
the unchanged source chunk and recording the input's starting offset. Validation
limits remain unchanged; no rejected claim is repaired into a verified assertion.
See [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs).

Current prompt #5.1 uses `paper-extraction-v5`. Method samples use a schema with
one entity embedded inside its USES relation, instead of two independently copied
entity names. Only Method/USES is allowed in that sample schema. A maximum
160-character quote must include the exact entity and occur within the exact input
window; offsets still address the original chunk. The general schema retains its
typed predicate ranges. No fuzzy matching, dehyphenation, predicate rewriting or
automatic semantic approval is performed. A schema-valid output can still contain
a poor entity span; it remains unreviewed.

Ignored `data/processed/ingestion/<run-id>/` holds pages, maps, chunks, claims,
raw model outputs, timings, failures and a report with input hashes.
`data/processed/extraction-cache/` keys include chunk ID, model digest and prompt
version and input-window offsets. Successful cached raw output is validated again before use. Failed calls
are retained and reported again; normal reimports do not silently retry them.
A deliberate prompt version change creates a separate attempt history.

Parameterized UNWIND batches of at most 100 records run in a 30-second transaction
per paper. The importer uses deterministic MERGE identities and ON CREATE claim
properties, preserving prior reviews. It refreshes only that paper's derived CITES
inside the same transaction; rejected claims cannot recreate edges. Changed PDF,
parser or chunker versions for an existing Paper fail and require a reviewed migration.
Run reports hash logical node/edge identities and properties to detect re-import
changes beyond mere counts.

## Historical prompt #5 verification record (superseded by #5.1 below)

The supplied professor Pylint template is preserved unchanged. No lint
configuration, score, CI run or broader rubric completion is claimed here.

Actual run artifacts (all ignored):

- Download/parse: `data/processed/ingestion/20261020T111422Z-cb7b7475/report.json`;
  exit 0, 2.023 s.
- First real import: `20261020T111737Z-4aa442bb/report.json`; all three model
  requests timed out at 90.093 s each. Source/chunk/citation import succeeded;
  CLI exit 1 truthfully recorded extraction failure. Total 272.527 s.
- Simplified grammar: `20261020T112311Z-52a87d2c/report.json`; all three model
  responses arrived but failed validation, at 25.186/17.543/21.153 s for
  DPR/RAG/GraphRAG. Total 65.235 s. No invalid claims were loaded.
- Final prompt: `20261020T112515Z-42a1928f/report.json`; total 23.167 s.
- Unchanged re-import: `20261020T112621Z-275e6e9d/report.json`; total 0.974 s,
  all three cached attempts reused. No additional inference was performed.

Final real-model sample:

| Paper | Time | Result |
| --- | ---: | --- |
| DPR | 7.867 s | Rejected: relation object missing/incompatible with predicate range |
| RAG | 6.610 s | One entity and one source-located claim accepted as EXTRACTED |
| GraphRAG | 7.733 s | Rejected: supporting quote/object did not match source |

This is **one accepted sample out of three**, not measured semantic precision.
Both failures and all earlier attempts remain available. `make ingest` still
returns nonzero (CLI 1, GNU Make 2) because two cached samples failed. This is
deliberate truthful failure reporting; graph import itself is complete. No claim
is silently discarded from the audit or reclassified as verified.

Measured final corpus:

| Nodes | Count |
| --- | ---: |
| Paper | 3 |
| Chunk | 153 |
| Entity | 1 |
| Topic | 0 (supported by implementation and tested on a fixture) |
| Claim | 3 |

| Relationships | Count |
| --- | ---: |
| PART_OF | 153 |
| NEXT | 150 |
| MENTIONS | 1 |
| SUBJECT | 3 |
| OBJECT | 3 |
| SUPPORTED_BY | 3 |
| CITES | 2 |

Two claims are SOURCE_VERIFIED bibliography assertions under the approved
automated policy; one is an unreviewed LLM extraction. No student review is claimed.
Authenticated read-only verification found the actual two-edge directed path
`arxiv:2404.16130v1 → arxiv:2005.11401v1 → arxiv:2004.04906v1`,
with C09/C03 evidence on source PDF page 13 in both cases. Four uniqueness
constraints and all four additional lookup indexes were present/ONLINE.
Details: `data/processed/graph-verification.json`.

The final re-import preserved both counts **and every logical node/relationship
identity and property**. Before/after SHA-256:
`b5a74b84aa514f5da9f7995ab216a533721ad3c348b0442b4c0db17aedf44d62`.
`graph_unchanged=true`. Neo4j internal relationship IDs are intentionally excluded
because derived CITES edges are rebuilt transactionally.

Tests executed:

```text
docker compose build api
docker compose run --rm --no-deps [read-only source/test mounts] api \
  python -m pytest -q --cov=app --cov-report=term-missing
make test
make help
git diff --check
sha256sum -c /tmp/graphrag-source-hashes.txt
```

The initial test run found a Neo4j managed-transaction timeout API mistake and a
JSON-null test-fixture mistake; both were corrected. The **final `make test`**
result was **99 passed, 1 warning in 6.14 s**, with **91% application coverage
(398 statements, 37 missed)** and `data/processed/coverage.xml` generated.
All 52 pre-existing tests passed. The warning is the existing Starlette/AnyIO
BlockingPortal deprecation. New tests cover real PDF parsing, normalization,
page offsets/IDs, checksum/version failure, malformed extraction, exact quotes,
bibliography checks, real Neo4j uniqueness, direction, idempotency, rejected-review
preservation, missing-target rollback and index presence.

A Docker snapshot during first-trial inference measured Ollama **3.959 GiB / 6 GiB**,
Neo4j **1.718 GiB / 4 GiB**, running API **70.45 MiB / 1 GiB**, and importer
**98.8 MiB / 1 GiB**. These are point samples, not measured run peaks. No memory
limit or GPU configuration was changed. Core services remained running throughout.
Source-file checksums confirmed all six corpus artifacts and all three professor
files unchanged. PDF/artifact ignore checks and `git diff --check` passed.

## Remaining limitations and next milestone

Extraction quality remains the principal blocker: DPR and GraphRAG have no accepted
scientific claims from this bounded sample. The simplest zero-cost next step is
student review of the saved failures and a small, explicitly scoped extraction
improvement using cleaner complete prose passages; keep the evidence checks strict.
Do not present the tiny successful sample as an evaluated knowledge graph.

After reviewing this milestone, implement the first LangGraph slice around the
verified citation path and page evidence: typed read-only tools, state, conditional
routing, bounded calls, evidence trace and abstention. Add chunk embeddings/vector
retrieval as a separately tested part of that slice. Default factual graph expansion
must distinguish automated bibliography verification from unreviewed semantic
claims. Defer GDS algorithms, ML and corpus expansion to their approved milestones.

## Current prompt #5.1 verification — supersedes the historical results above

The original DPR response used Method + ADDRESSES (invalid range), and its quote
did not contain its named entity. The original GraphRAG quote changed source
`in- dexed` to `indexed`. Both remain rejected; source text and original attempts
were preserved. Prompt v4 selected explicit method-use passages, but its DPR output
appended “Method” to the relation target and its GraphRAG quote omitted the entity.
The method-specific v5 schema removes that redundant target field while keeping
all evidence checks strict.

Actual v4 trial: `data/processed/ingestion/20261020T113544Z-cd58e344/report.json`.
DPR rejected in 11.216 s; RAG accepted as unreviewed in 4.012 s; GraphRAG rejected
in 3.125 s. Total 19.391 s; default CLI exit 0 with PARTIAL_SUCCESS.

Final bounded v5 trial: `20261020T113740Z-00f06b4f/report.json`, total **29.233 s**:

| Paper / genuine method in input | PDF page | Time | Actual result |
| --- | ---: | ---: | --- |
| DPR / BERT | 3 | 6.039 s | Rejected: generated entity name not present exactly in source |
| RAG / BART-large | 3 | 2.818 s | Passed structure/quote checks; EXTRACTED, pending semantic review |
| GraphRAG / Leiden | 4 | 19.348 s | Rejected: repeated malformed quote exhausted the 400-token budget |

The accepted RAG candidate is literally `use BART-large`, including the surrounding
verb. It is a located candidate span, not a student-approved canonical entity or
scientific assertion. It needs student cleanup/review. This sample is development
debugging, not a precision/recall evaluation. No further model tuning was performed.

Measured graph after preserving all prior attempts:

- **3 Papers, 153 Chunks, 3 Entities, 0 Topics, 5 Claims.**
- All **5 claims are EXTRACTED**: 2 bibliography assertions and 3 retained RAG
  extraction attempts from different prompt versions. These are not five independent
  scientific facts; the entity candidates are all from RAG.
- **0 SOURCE_VERIFIED claims, 0 CITES edges.** Human approval has not been applied
  to any real corpus claim.
- PART_OF 153; NEXT 150; MENTIONS 3; SUBJECT 5; OBJECT 5; SUPPORTED_BY 5.
- C03/C09 retain their source page 13, quote, support relationship and old automatic
  review metadata in history; location status is SOURCE_LOCATED, student review pending.

An unchanged strict-mode re-import (`20261020T113942Z-0cb5d866/report.json`) reused
caches, took **0.861 s**, and returned **exit 2** as requested by
`--require-extraction`. Graph counts/properties were unchanged; before/after fingerprint:
`e7593218057aa7c3e49a0a8afe9fdee838204d1d216c5b3712126cad679177c1`.
Default `make ingest` returned exit 0 for the same partial-success classification.
Independent read-only assertions are saved in ignored
`data/processed/corrections-verification.json`.

Actual final `make test`: **113 passed, 1 existing Starlette/AnyIO deprecation warning
in 6.43 s**. Application coverage **91% (449 statements, 39 missed)**; XML generated
at `data/processed/coverage.xml`. All 99 prior tests remain passing. New regressions
cover the specific predicate/quote failures, embedded-entity schema, original offsets,
CLI exit contract, legacy approval correction/history retention, explicit human
approval/rejection/re-import transitions, and rejection of status-only CITES approval.
`git diff --check` and checksum checks of all corpus/professor files passed.

**Exact next step:** an independent student must inspect C03 (RAG page 13, reference
[22]) and C09 (GraphRAG page 13, Lewis et al. reference), check target work identity
and the recorded evidence, then explicitly approve or reject each with a named
review note. Review the RAG candidate spans and retained DPR/GraphRAG failures as
well. No actual approval should be inferred from this report. Keep agent, GDS and ML
work out of this correction milestone.

## PR #2 review verification — prompt #5.3

`make test`: **127 passed, 0 failed, 1 existing Starlette/AnyIO deprecation warning
in 20.28 s**. Application coverage **93% (466 statements, 33 missed)**; XML generated
at ignored `data/processed/coverage.xml`. All 113 existing tests still pass, alongside
14 new regression cases. No live model inference or real-corpus re-import was needed.

New tests cover missing/foreign entity source chunks and no partial writes; real
PDF parsing plus invalid citation page hashes; default/strict core-failure exit 1;
no database access before failed preflight; unchanged real Neo4j fingerprints for
fresh failures and failed re-imports; valid citation imports despite an optional model
HTTP 503; and PDF save failures during fsync, atomic replacement and truncated-file
verification. Temporary Neo4j fixtures use UUID-scoped IDs and are cleaned up.
Successful PDF downloading/publication is also tested with an original generated PDF.
