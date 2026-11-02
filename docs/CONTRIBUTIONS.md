# Team contributions — Project 8

**AI Research GraphRAG Assistant, Level 3+ — evidence checked 2026-11-02.**
This report covers merged main `106c2f345b4443ccd8bda6c655d945804118f559`.
Neel Sabharwal coordinated architecture, implementation and technical integration;
Fabrice Afopa contributed scientific review, evaluation preparation and documentation.
The table records responsibilities and delivered changes supported by PR authors,
changed files and review records. AI assistance and coordinated package preparation
were used; committing or submitting a prepared file does not establish sole or
independent implementation.

| Student | Main workstreams and delivered work | Merged PR evidence |
|---|---|---|
| Neel Sabharwal (`NeelSabharwal`) | Docker Compose and local services; Neo4j schema and provenance; PDF ingestion; LangGraph hybrid retrieval, source grounding and guardrails. | [#1](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/1), [#2](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/2), [#4](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/4) |
| Neel Sabharwal | Reviewed-evidence import; advanced Cypher, PageRank and Louvain; source-mention enrichment; fixed graph ML experiment; FastAPI endpoints/authentication, tests and CI. | [#7](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/7), [#9](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/9), [#10](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/10) |
| Neel Sabharwal | Final lint/docstrings, technical validation, notebook visualizations and integration; API image redistribution gates, publication workflow and public-pull verification. | [#12](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/12), [#13](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/13), [#14](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/14), [#15](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/15) |
| Fabrice Afopa (`fabrice12345C`) | Evaluation evidence/test-case review and verification script; scientific passage, relationship, citation and entity-alias review; recorded qualified claim decisions. | [#3](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/3), [#5](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/5) |
| Fabrice Afopa | METHOD/EVALUATION candidate preparation and source-review records; integration of the demonstration notebook, guide, schema/architecture diagrams, screenshots and final documentation package. Technical peer-review feedback also informed application corrections. | [#8](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/8), [#11](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/11); review examples below |

## Integration of scientific and application work

Fabrice's [scientific review](GRAPH_EVIDENCE_REVIEW.md) records approval of 22 qualified
claims and decisions on 21 alias proposals, retaining unresolved A17 and rejected
equivalences. Neel's importer integrated these records with source coordinates,
validation and review provenance; document approval and database execution remained
separate. Fabrice's [labeling preparation](ML_LABELING_REVIEW.md) retained AI-assisted
recommendations and passage decisions. Neel separately recorded independent approval
of 15 complete Chunks before PR #8 merged. The evaluation review does not imply human
sign-off for every evaluation case. The frozen ML experiment retains its negative
0/5 result versus the majority baseline's 3/5.

## Peer review and assessment limits

**Before merge:** Fabrice raised dependency-failure and malformed-response concerns
on #1, ingestion integrity/atomicity concerns on #2, and router wiring, self-matches
and retrieval limits on [#4](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/4#pullrequestreview-5592557960).
Neel requested reproducible evidence checks and a separate forged-citation fixture
on [#3](https://github.com/NeelSabharwal/GraphDBproject-NeelSabharwal-FabriceAfopa/pull/3#discussion_r4326356657),
reviewed #5's qualified scientific decisions, and approved #8's complete-Chunk labels.
Code inspection is not an independently reproduced test run.

**After merge:** 18 comments on #7–#13 were posted on 2026-11-02, addressing provenance,
ML limitations, GDS interpretation and reproducibility. Their authors, timestamps and
links are preserved in the [review chronology](FINAL_VALIDATION.md#retrospective-review-evidence-inspected-on-2026-11-02).
Own-PR comments are not independent peer review. No nonempty discussion/inline/review
records were returned for #14/#15 in this audit.

**R47 — PARTIAL (3 points):** the evidence supports substantial complementary work,
not equal effort. At the stated baseline, `git shortlog -sn --no-merges HEAD` records
15 Neel commits (two name spellings) and 11 Fabrice commits; including merges, 30 and
11. These counts are not hours, ownership percentages or proof of balanced substantive
contribution. The professor must assess the delivered work and each student's understanding.

**R48 — VERIFIED evidence (3 points):** merged application PRs such as #4/#10 and
scientific-review/documentation PRs #5/#8/#11 substantiate substantial delivered work
from both members, with the authorship qualifications above.

**R42 — PARTIAL (1 point):** genuine review participation is documented, but two
constructive comments per PR are not established across every PR. Retrospective
comments do not establish pre-merge review. These are evidence statuses, not awarded marks.
