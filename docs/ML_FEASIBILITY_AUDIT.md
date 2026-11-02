# Graph ML feasibility audit — 2026-10-22

**Result: labels pass technical validation; training is blocked by constant graph
features.** Every approved Chunk has the same eight-feature vector. No informative
supervised graph classifier is currently feasible using the planned inputs.
No model was trained, labels changed, or database records modified. The professor's
**3-point ML prediction/classification workflow remains incomplete**.

Audit: `feat/graph-ml`, starting commit `86c9540`, initially clean working tree;
live Neo4j **5.26.32**, GDS **2.13.2**. Requirements, AGENTS.md,
[ML_RECOMMENDATION.md](ML_RECOMMENDATION.md), [ARCHITECTURE.md](ARCHITECTURE.md),
the decision/plan records and merged annotation CSV were inspected.
Deadline: 2026-10-23; zero paid services.

## Label and source validation

All **15 distinct approved Chunk IDs and 15 distinct stored text hashes** passed:
actual `(Chunk)-[:PART_OF]->(Paper)` membership; CSV/parent/manifest PDF hash
agreement; page and Chunk offsets; exact UTF-8 text SHA-256 recomputation;
and parser/chunker identity (`pypdf-6.10.0`, `page-1400chars-overlap200-v1`).
The broader source-integrity checks passed for all **153** live Chunks.

Eligibility requires unique technical mapping, approved whole-Chunk binary label,
`ELIGIBLE_REVIEWED_PILOT`, and explicit independent approval by **NeelSabharwal,
2026-10-22**. The audit checked these existing CSV fields against live identities;
it did not conduct a new human semantic review or create database approvals.
All annotations remain `DEVELOPMENT_ONLY`.

| Pinned Paper | Approved candidates | METHOD | EVALUATION |
| --- | --- | ---: | ---: |
| DPR — `arxiv:2004.04906v1` | ML01, ML03, ML04, ML05, ML06 | 2 | 3 |
| RAG — `arxiv:2005.11401v1` | ML08, ML09, ML11, ML12, ML13 | 2 | 3 |
| GraphRAG — `arxiv:2404.16130v1` | ML15, ML16, ML18, ML19, ML20 | 2 | 3 |
| Total | 15 | 6 | 9 |

ML02/ML10/ML17 remain unresolved and ML07/ML14/ML21 remain excluded. ML21's
excluded candidate shares a Chunk with independently approved ML18; exclusion is
candidate-specific and does not invalidate ML18. No additional labels were inferred.
ML08/ML09 overlap by 189 source characters within RAG; distinct identities do not
imply independent samples. Whole-paper splitting keeps this overlap in one partition.

Annotation CSV SHA-256:
`301bccb14515daa90bbe67778e77dd8afeaa85e92592e02b42d8286839964b51`.

## Actual graph features and sparsity

The eight exported columns are log1p distinct MENTIONS Entity counts for
Method/Dataset/Task/Topic, previous/next entity-set Jaccard overlap, and
previous/next existence flags. Empty-union Jaccard is zero. Only actual same-paper
NEXT edges contribute. Entity IDs are used without unapproved alias merging;
labels, Claims, text position, headings and cross-paper propagation are not features.

| Paper | Chunks | NEXT edges | MENTIONS edges | Chunks with MENTIONS | Approved Chunks with MENTIONS |
| --- | ---: | ---: | ---: | ---: | ---: |
| DPR | 42 | 41 | 0 | 0/42 | 0/5 |
| RAG | 62 | 61 | 3 | 2/62 (3.23%) | 0/5 |
| GraphRAG | 49 | 48 | 0 | 0/49 | 0/5 |
| Total | 153 | 150 | 3 | 2/153 (1.31%) | 0/15 |

**Approved set, both overall and within each paper:** the first six features are
zero for every Chunk; both existence flags are one. Thus all eight have variance
zero, with exactly **one unique feature vector: `[0,0,0,0,0,0,1,1]`**.

For all 153 Chunks, Dataset/Task/Topic counts and both Jaccard features are zero.
DPR and GraphRAG Method counts are also zero throughout. RAG's Method feature has
60 zeros, one `log(2)=0.693147`, and one `log(3)=1.098612` (mean 0.028899,
population variance 0.026381). Each paper has exactly one zero per existence flag:
the first/last Chunk; other values are one. These boundary flags encode position,
not informative semantic neighborhoods. Full per-paper min/max/mean/variance,
zero counts and unique values are in the ignored audit JSON.

All three MENTIONS edges target unreviewed paper-scoped Method entities in RAG:
two overlapping BART-large surfaces in an ML10 mapping candidate, and one
`seq2seq model` surface in excluded ML14. Their stored surface offsets match source
text exactly, but this does not establish semantic correctness or canonical identity.
The graph does not establish the recommendation's heading-only filter; the export
is explicitly **audit-only, not training-ready**. A stricter filter cannot restore
missing edges on the approved Chunks. Unknown entity kinds, cross-paper/outside
NEXT edges and duplicate NEXT edges: **zero**; no ambiguous NEXT neighborhoods.

The live database contains 3 Papers, 153 Chunks, 17 Entities and 25 Claims, with
153 PART_OF, 150 NEXT, 3 MENTIONS, 25 SUBJECT, 25 OBJECT, 60 SUPPORTED_BY and
2 CITES relationships. Reviewed Claim support does not automatically create
MENTIONS features. Existing GDS results do not repair this feature gate.

## Whole-paper experiment and minimal remedy

A split is structurally possible: any two papers give 10 labels (4 METHOD,
6 EVALUATION), and the remaining paper gives 5 (2 METHOD, 3 EVALUATION).
However, every such training and test matrix is constant. A classifier cannot
distinguish these Chunks from these inputs. No model or baseline score was measured.

The earlier recommendation proposes eight papers, 96 labels and at least four
examples per class per test paper; these targets are unmet. The present labels
are exposed development labels, not a sealed test set or a blinded second-label
study. Three related papers and five test labels cannot establish broad scientific
generalization. A paper-disjoint pilot could prevent direct train/test leakage,
but its scope must be explicitly revised and its exploratory status disclosed.

**Smallest proposed next task:** separately authorize a bounded, uniform,
label-blind MENTIONS completeness/quality pass over the existing three papers,
using actual source spans and a fixed entity-kind, alias and heading-filter policy.
Do not select or improve extraction using METHOD/EVALUATION labels, copy labels
from section headings, turn Claim support into invented mentions, or silently merge
aliases. Preserve existing reviews and unresolved candidates. Re-audit the same
eight features before any fitting; nonconstant values alone do not prove useful
predictive signal. No new papers or synthetic labels are needed to investigate
this immediate blocker.

Only if genuine usable neighborhoods become available and students approve the
reduced pilot: predeclare DPR+RAG training and whole-paper GraphRAG testing (a
subset of the prior proposed split); freeze extraction, eligible labels and settings;
fit training-only scaling and one fixed L2 logistic regression against a
training-majority baseline. Keep labels out of feature construction, graph properties
and serving/retrieval; do not tune on the held-out paper. Report macro-F1, per-class
metrics/confusion matrix and five-example support with the limitations above.
This conditional proposal is not authorization or a claim that current training is
feasible. The larger recommendation and architecture were left unchanged.

## Read-only execution, artifacts and checks

The operational audit used nine fixed read queries in a `READ_ACCESS` transaction,
checked zero update counters and explicitly rolled back. Health/connectivity tests
only inspected readiness, versions and procedure catalogs. No GDS algorithm ran.
Read routing alone is not a permissions boundary: safety also depends on these
inspected queries. Full node/relationship/property fingerprints matched before and
after the audit and after tests:
`a847ebb5017a08830c281a64afbdba68a278d208e88f499ac7bde54628594682`.
This establishes no observed change to graph data during the checks, not absence
of operational query logs or server metrics.

Ignored local artifacts under `data/processed/ml/feasibility-20261022/`:

- `audit.json`: timestamp, nine query texts/parameters, validation provenance,
  graph fingerprints, counts, per-paper distributions and all 153 feature rows.
- `approved_chunk_features.csv`: 15 rows; `all_chunk_features.csv`: 153 rows.
  Each has Chunk join ID plus the eight numeric features, with no labels, full text,
  embeddings or credentials. IDs are join metadata, never model inputs.
- `checks.json`: actual test outcomes and final database fingerprint.

Operational helpers are ignored at `data/processed/ml/feasibility_audit.py` and
`data/processed/ml/test_feasibility_audit.py`. They are not application changes.
The audit command was `python3 data/processed/ml/feasibility_audit.py`; its dated
output directory refuses overwrite. Early wrapper attempts hit a source-splitting
syntax error and Cypher aggregation ordering error; the post-test fingerprint
wrapper initially lacked Neo4j datetime serialization. These operational errors
were corrected before the successful outputs; no write queries were involved.

| Check actually executed | Result |
| --- | --- |
| `python3 data/processed/ml/test_feasibility_audit.py` | 10 passed, 0 failed, 0.005 s; distinct counts, Jaccard, direction, cross-paper exclusion, constants and approval gates |
| `docker compose exec -T api python -m pytest -q tests/test_health.py tests/test_connectivity.py` | 14 passed, 0 failed, 1.07 s; one upstream Starlette/AnyIO deprecation warning |
| Live audit integrity assertions | All 153 sources and 15 approved mappings passed |
| Post-test graph fingerprint | Identical to initial fingerprint |
| Feature CSV checks | 15/153 unique rows respectively; exactly eight features, identical to audit JSON |
| `git diff --check` and new-document whitespace check | Passed; only this report is a new non-ignored file |
| Annotation hash, ignore rules and document links | Passed; annotations unchanged and operational artifacts ignored |

The complete `make test` suite was deliberately not run because integration fixtures
write to Neo4j. Coverage was not measured. No existing source, requirement, annotation,
gold evaluation or architecture file was changed; no model fitting, commit or push.
