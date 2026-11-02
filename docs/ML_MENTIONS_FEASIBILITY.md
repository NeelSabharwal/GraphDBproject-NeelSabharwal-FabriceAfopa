# Label-blind MENTIONS feasibility — Prompt #8B

**Decision: FEASIBLE FOR CONTROLLED IMPORT**, subject to explicit authorization of
the frozen policy and exact candidate artifact below. This is feasibility for a
bounded mention layer and exploratory three-paper pilot, not evidence of classifier
accuracy, student approval of each mention, or completion of the 3-point ML rubric.

Audit date: **2026-10-22**; branch `feat/graph-ml`; deadline 2026-10-23; zero paid
services. Read the course requirements, project instructions, plan, architecture,
decisions, ML recommendation, prior audit, scientific review, annotation CSV and
ingestion schemas. The pre-existing untracked `ML_FEASIBILITY_AUDIT.md` was preserved.
No application code, annotations, scientific review status or source PDFs changed.

## Source integrity and frozen policy

The complete live node/relationship/property fingerprint matches Prompt #8A before
and after this audit:
`a847ebb5017a08830c281a64afbdba68a278d208e88f499ac7bde54628594682`.
The graph remains 3 Papers, 153 Chunks, 17 Entities, 25 Claims and **3 MENTIONS**;
the 145 proposals exist only in local files/in-memory calculations.

Using the existing API image, pinned pypdf 6.10.0 and a read-only project mount,
all three PDF byte hashes passed and all **153 Chunks were exactly reproduced**:
IDs, text/hashes, offsets, raw-page hashes, parser/chunker versions and actual
`PART_OF` membership. The original DPR page-7 control-character warning persists;
no text was repaired. All 14 approved canonical Entities match the signed alias
manifest and live `STUDENT_APPROVED_SCOPED` provenance. A17 remains unresolved;
the six rejected equivalences remain rejected.

**Final policy: `scoped-exact-mentions-audit-v4`.** Applied uniformly to every Chunk:

- Literal, case-sensitive matches with Unicode word/hyphen boundaries; only listed
  initial-capital spellings are accepted. No fuzzy matching, dehyphenation, stemming,
  LLM extraction or invented identities. Stored normalized Chunk text is the matching
  source; original raw PDF-text coordinates are preserved through the parser map.
- Named forms come from approved A01–A14. Acronyms/variants retain their scopes:
  NQ/WQ/TQA/Trivia/CT/TREC require an immediate explicit parenthetical expansion
  and the approved paper scope. Generic BERT/BART, Louvain-as-Leiden, Hadoop,
  WebQuestionsSP and generic Podcast/News are diagnostic rejections, not aliases.
- BERT-base denotes architecture, never checkpoint/casing/weight equality.
  GraphRAG's podcast/news names are limited to its reviewed §3.1 corpus description;
  map-reduce workflow forms are limited to the reviewed pages 3/5. QFS remains a
  separate task. These source-identity scopes do not enter numeric feature columns.
- Exclude title metadata, numbered section headings, isolated names, short
  unpunctuated labels, recognizable table column headers and reference/post-reference
  regions. Conservatively exclude the complete page prefix before its first
  figure/table caption. Captions with actual explanatory context can supply mentions.
  The exact rules and dictionary are in the frozen policy and hashed helper.

The layout rules deliberately sacrifice recall: they can exclude valid prose,
appendices after References and meaningful shorthand away from its expansion.
They are conservative heuristics, not a general PDF layout parser. A mention records
an occurrence of an identity; it does **not** assert USES, EVALUATED_ON or ADDRESSES.
New records remain mechanically source-located, with no invented human review.

## Source accuracy checks and actual proposals

Source-only sampling selected up to two distinct coordinate-hash-ordered occurrences
per alias and proposed/rejected status, without annotation access. The assistant
read **28 positive and 27 rejected contexts** in the final sample. The 28 support
their scoped mention identity; the 27 follow the declared rejection policy. This
is an assistant spot-check, not student review or an unbiased population precision
estimate. Many rejected shorthand occurrences are likely valid mentions excluded
for conservatism, not scientifically false identities.

Examples inspected: RAG p.3 `BERT BASE` supports architecture-only identity;
GraphRAG p.4 `Leiden` names the algorithm; p.6 `Behind the Tech` identifies the
scoped transcript collection. RAG p.6 `BART-large` is a baseline mention, not a
new method-use claim. GraphRAG p.2 `Louvain` cannot map to Leiden; bibliography
HotpotQA and generic TREC outside explicit expansion are excluded. Synthetic
negative controls also cover case, token boundaries and unapproved variants.

The initial policy proposed 165 occurrences. Source inspection exposed diagram
labels and a table header; structural gates reduced this to 146 **before the first
annotation/feature join**. A subsequent source-only short-line check found `Fixed
DPR` in a chart legend; the uniform short-label rule reduced the final count to
145, without changing any approved-Chunk vector. All versions and rejected rows
are retained. No classifier outcome, label keyword or class balance guided changes.
The assistant had prior knowledge of the annotations from #8A; this is an input-
isolated deterministic policy, not a claim of a blinded human research design.

| Paper | Proposed occurrence edges | Distinct Chunk–Entity pairs | Affected Chunks | Entities | Edges on approved Chunks | Approved Chunks reached |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DPR | 64 | 37 | 23/42 | 6 | 25 | 4/5 |
| RAG | 54 | 38 | 16/62 | 8 | 21 | 3/5 |
| GraphRAG | 27 | 20 | 13/49 | 6 | 9 | 3/5 |
| Total | **145** | **95** | **52/153** | **14 unique** | **55** | **10/15** |

These are occurrence edges keyed by Chunk, Entity and offsets, not 145 independent
scientific observations. Overlapping Chunks duplicate 13 source occurrences:
132 distinct paper/page/entity/span occurrences remain after source deduplication.
All 347 candidate/diagnostic rows have exact valid surface spans and source hashes.

**202 rejections:** 52 ambiguous generic names; 30 shorthand without explicit
expansion; 50 pre-caption layout; 49 reference/post-reference; 4 numbered headings;
4 diagnostic subspans of accepted names; 5 outside scoped corpus description;
3 outside workflow context; and one each for title metadata, column header, short
legend, rejected equivalence and outside approved paper scope. Full per-paper
reasons and coordinates are retained. The six ineligible ML candidates remain excluded.

## Hypothetical eight-feature comparison

Order: log1p distinct **Method, Dataset, Task, Topic** Entity counts;
Jaccard with previous/next same-paper NEXT neighbors; previous/next existence.
Counts use distinct canonical IDs, not occurrence frequency. All 153 feature rows
were constructed before joining approved identities. No labels enter feature creation.

**Before:** every approved Chunk is exactly `[0,0,0,0,0,0,1,1]`.
Below, `L2=ln(2)`, `L3=ln(3)`, `L4=ln(4)`, `L5=ln(5)`; these symbolic values
and fractions specify exact vectors without decimal rounding.

| Candidate | Proposed edges | After: proposed canonical layer only |
| --- | ---: | --- |
| ML01 | 5 | `[L2,0,L2,0,0,0,1,1]` |
| ML03 | 0 | `[0,0,0,0,0,0,1,1]` |
| ML04 | 10 | `[0,L5,L2,0,1/5,4/5,1,1]` |
| ML05 | 8 | `[L2,L4,0,0,1/4,1/4,1,1]` |
| ML06 | 2 | `[L2,0,0,0,0,1/2,1,1]` |
| ML08 | 0 | `[0,0,0,0,0,0,1,1]` |
| ML09 | 8 | `[L4,L3,0,0,0,1/5,1,1]` |
| ML11 | 11 | `[0,L5,L2,0,0,2/5,1,1]` |
| ML12 | 2 | `[L2,0,L2,0,0,1/2,1,1]` |
| ML13 | 0 | `[0,0,0,0,0,0,1,1]` |
| ML15 | 1 | `[0,L2,0,0,1/2,0,1,1]` |
| ML16 | 2 | `[L2,0,L2,0,0,1/2,1,1]` |
| ML18 | 6 | `[0,L4,0,0,0,0,1,1]` |
| ML19 | 0 | `[0,0,0,0,0,0,1,1]` |
| ML20 | 0 | `[0,0,0,0,0,0,1,1]` |

All prior variances are zero. Hypothetical population variances, rounded to six
decimals, for the first six features:

| Approved subset | Method | Dataset | Task | Topic | Previous Jaccard | Next Jaccard |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DPR (5) | .115309 | .543444 | .115309 | 0 | .012400 | .094400 |
| RAG (5) | .307490 | .466106 | .115309 | 0 | 0 | .041600 |
| Train DPR+RAG (10) | .211399 | .505603 | .115309 | 0 | .008225 | .070025 |
| Held-out GraphRAG (5) | .076872 | .307490 | .076872 | 0 | .040000 | .040000 |
| All 15 | .183640 | .444869 | .106767 | 0 | .019489 | .066067 |

Five of six gain variance overall and in both proposed partitions; RAG alone has
constant previous Jaccard. Topic remains zero because the approved inventory has
no Topic entities. Both existence flags remain one. There are 10 distinct vectors
overall, 8 in training and 4 in held-out GraphRAG; five approved Chunks still have
no accepted mention. Full distributions for all Chunks and approved subsets are saved.

**Preserving old edges matters:** a separate in-memory union with the existing
three unreviewed paper-scoped mentions changes ML09's next Jaccard from **1/5 to
1/7**; all other approved entries stay the same. Nothing was silently merged or
discarded. A future feature export must explicitly choose the approved canonical
mention layer to reproduce the table; an unrestricted MENTIONS query will differ.

Variation is not merely the constant position flags: typed source-grounded entity
neighborhoods vary within each paper. However, these counts are closely related to
lexical named-entity indicators; no advantage over a text baseline is established.
Jaccard is substantially driven by the existing overlapping Chunk windows. Removing
overlapping-neighbor pairs as a diagnostic makes previous-Jaccard variance zero
everywhere; next-Jaccard variance remains .0225 in training but becomes zero in
GraphRAG. This diagnostic did not replace or tune the planned features.

## Controlled import proposal — NOT EXECUTED

The exact **145** edges, including hashes, PDF/page/raw and Chunk-local offsets,
surface, existing Entity ID/kind, alias scope and policy version, are in ignored
`data/processed/ml/mentions-audit/proposed_edges-v4.json`.
SHA-256: `990e943eb5be101d27a5435738be49aaadcee9a82faeb7ada92c6eb22b42f0b0`.
Policy SHA-256: `6966fc03fb1633c782edc999acb6d6481fc01d0e5100f1a3b72e81c035c2645f`.
The policy also pins the matcher implementation hash.

Before a separately authorized import:

1. Inspect/freeze these artifacts and the approved-canonical feature-selection
   policy. Do not widen matching to improve a class result. Recheck current graph,
   alias/source/Chunk hashes and exact candidate set; stop on any drift.
2. Stop API and Neo4j cleanly and back up the discovered complete Neo4j `/data`
   volume outside the live volume. Verify nonzero archive size, contents, archive
   integrity and SHA-256, retain a restore procedure, restart and check readiness.
   Never delete volumes or overwrite an older backup.
3. Use one bounded transaction for all 145 rows. Require existing Chunk/Entity
   endpoints, correct PART_OF, exact hash/span/surface and approved alias identity
   before writes. An occurrence identity is `(chunk_id, entity_id, start, end,
   text_sha256)`. Reuse an identical existing occurrence; reject conflicting
   properties, and never overwrite another producer's edge. Do not duplicate the
   same occurrence merely because a policy version changes. Require one operator
   and no concurrent ingestion; record the exact IDs created by this batch.
4. Store deterministic proposal IDs, source coordinates/hashes, policy and artifact
   hash, batch ID, `EXACT_SURFACE` source-location validation and explicitly
   unreviewed semantic status. Preserve all three old MENTIONS, all nodes, Claims,
   CITES, aliases and review history. No SOURCE_VERIFIED promotion is involved.
5. Verify exactly 145 new edges (expected total **148**, conditional on unchanged
   baseline), zero other changes, authentic offsets and expected canonical-layer
   vectors. A second dry-run must propose zero new edges. Transaction failure rolls
   back atomically. After commit, rollback should remove **only recorded newly
   created edges from this batch**, after checking their provenance; never remove
   reused edges. Restoring the verified offline backup is the fallback, not an
   automatic action that could erase subsequent legitimate work.
6. Before live application, test first import, idempotent replay, conflicting existing
   edge, missing endpoint, changed text/hash, injected mid-transaction failure and
   batch-only rollback in an isolated fixture database. Those write-path tests were
   **not run** during this read-only task. Follow with read-only live integrity,
   counts, feature reproduction and unchanged node/Claim/review checks.

## Limits, checks and next action

This is an explicitly limited **DPR+RAG train / GraphRAG held-out** pilot, not the
original eight-paper/96-label plan. Existing labels are exposed development labels,
not a sealed evaluation set. The dictionary came from curated scientific review
and includes the held-out paper's identities: it is label-blind, but not independent
of the test document. Extraction scopes and layout exclusions can bias coverage.
No test labels, paper IDs, positions, headings, gold answers or Claim status become
features; graph neighborhoods stay within each paper. Any future scaler must fit
training data only. No model was trained or tested; useful predictive signal and
generalization remain unknown, and the eight-paper review targets remain unmet.

Actual checks:

- `python3 data/processed/ml/mentions-audit/test_matcher.py`: **14 passed**,
  0 failures, 0.240 s; boundaries/case, alias scopes, headings/references, negative
  controls, deterministic regeneration, label-input independence and source tampering.
- `python3 data/processed/ml/test_feasibility_audit.py`: **10 passed**,
  0 failures, 0.002 s; existing feature calculations and approval gates.
- Source reconstruction: **153/153** Chunks; candidate spans/hashes **347/347**;
  annotation hash matches #8A; all three pinned PDFs unchanged.
- Neo4j reads: two fixed MATCH queries per snapshot, explicit READ_ACCESS and
  rollback, no update counters; final complete fingerprint matches #8A. Read
  routing alone is not a database permission boundary.
- Git whitespace checks passed. Protected source/annotation/gold files match HEAD;
  all operational artifacts are ignored. Final checks confirmed 145 unique new
  occurrence keys, no collision with existing MENTIONS, 132 unique source spans,
  153 unique feature rows and matching policy/implementation hashes. Artifact
  checksums are saved in the ignored `SHA256SUMS` file.

Ignored helpers, snapshots, versioned policy/candidate records, source-review notes,
153-row feature export and exact before/after JSON live under
`data/processed/ml/mentions-audit/`. Earlier attempts are retained; **v4** is final.
Full application tests were not run because integration fixtures mutate Neo4j;
coverage was not measured. No commit, push, branch change or paid service.

**Smallest next action:** review and explicitly authorize this frozen 145-edge
import proposal and canonical-layer feature scope, then implement its backup,
transaction/idempotency and rollback checks. Training remains a separate task.
