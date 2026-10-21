# Reviewed evidence integration — Prompt #7A

Prepared 2026-10-21 on `feat/advanced-graph-gds`, initially clean at `db934a5`
(PR #5 merge; PR #4 also present). Deadline: October 23, 2026. Zero paid services.
**STOPPED AFTER VALIDATED DRY-RUN. No real approval or alias merge was applied.**
No commit, staging, push, merge, branch switch, GDS computation or ML training.

## Authority and safeguards

The authority is [GRAPH_EVIDENCE_REVIEW.md, Section 9](GRAPH_EVIDENCE_REVIEW.md),
including the qualified assertions in sections 2–5 and alias boundaries in section 6.
Reviewer: `fabrice12345C`; sign-off **recorded** 2026-10-21, Europe/Paris.
The actual personal inspection time is unknown and remains unset. The original
student documents, CSVs, manifest, gold and professor requirements are unchanged.
[review_decisions.json](../corpus/review_decisions.json) is an exact checked
transcription, not independent authorization or a new student attestation.
Its source pins and exact decisions/qualifications are rechecked on every command.
An unsigned CSV entry, source-location check or confidence value cannot grant approval.

`--apply` requires both explicit operator authorization and the inspected graph
fingerprint. Preparation revalidates source text, typed assertions and approved aliases.
Application uses existing `review_claim()` and `refresh_citations()` in one transaction;
conflicts, stale state or mismatched evidence reject the batch. Existing approved or
rejected decisions are not overwritten. Repeated application reuses identical records
without new review events. Review history and the prior pending citation evidence are
retained. The actual UTC `review_applied_at`/`reviewed_at` differs from the historical
`signoff_recorded_date`. Local review recording cannot authenticate a person's identity.

Scientific assertions use the existing reified model:
`(Paper)<-[:SUBJECT]-(Claim)-[:OBJECT]->(Entity)`. No duplicate direct scientific
edges are added. Only approved citation Claims derive CITES. A pinned v1 target is
navigation to a representative of the cited work, never proof of the consulted revision.

## Source checks and observed graph

The pypdf **6.10.0** audit verified all three pinned PDF byte hashes, versions and
page counts (DPR 10, RAG 18, GraphRAG 15), all 153 authentic existing Chunks,
and **20/20 scientific** excerpt/page/context hashes and raw offsets. C03 and C09
passed the existing bibliography validator. No substitute quotations or altered
source coordinates were used. The existing DPR page-7 control-character warning is
retained; it does not affect these mapped claims.

The separate research integrity audit also passed **20/20 evaluation evidence location
checks**; evaluation labels/answers are never loaded by the importer or retrieval.
The gold Q15 field remains absent and unchanged; the existing synthetic forged-page
regression test still passes. An audit's source CSV `PENDING` metadata is historical;
the separately signed review supplies authority, without rewriting the source CSV.

| Actual live record | Before | After final dry-run/tests |
|---|---:|---:|
| Paper | 3 | 3 |
| Chunk | 153 | 153 |
| Entity | 3 | 3 |
| Claim | 5 | 5 |
| CITES | 0 | 0 |

All five actual Claims remain EXTRACTED/pending (two bibliography, three LLM).
Other actual relationship counts: PART_OF 153, NEXT 150, MENTIONS 3, SUBJECT 5,
OBJECT 5, SUPPORTED_BY 5. The original three LLM entities/claims remain untouched.

The importer's logical snapshot fingerprint before/after is:
`d3eb56b2277c2e4c93f350384c3c8004005c8e594db8b133c745960d88a93f62`.
The independent existing research audit fingerprint before/after is:
`01e374982f87e11138363d4baac50b355e718fdebf664779758c2645cbd901d0`.
These are different serialization/snapshot functions, each compared only with itself.
Both comparisons passed; the real corpus was unchanged.

## Complete 22-claim mapping

Every row below has student decision **APPROVED**, by the reviewer/date above, and
readiness **READY_AFTER_OPERATOR_AUTHORIZATION**. None has been applied. Source
Paper IDs and target IDs are exact. K identifiers expand to exact existing Chunk IDs
in the next table. The listed support union includes both excerpt and full context;
ordered segments, exact quotes, raw/normalized offsets and hashes are in the dry-run
JSON. Twelve scientific contexts and C09's bibliography context require two chunks.
All were retained, with **57 support relationships** across the 22 proposed records.

| Evidence | Source Paper ID | Target ID | Predicate | PDF page | Supporting chunks | Accepted qualification and retained source limits |
|---|---|---|---|---:|---|---|
| GE01 | arxiv:2004.04906v1 | method:bert-base | USES | 3 | K10, K16 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Question and passage encoders; base uncased variant. Merge with RAG only at BERT-base architecture level; checkpoint identity is not established. |
| GE02 | arxiv:2004.04906v1 | task:open-domain-question-answering | ADDRESSES | 2 | K01 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Paper studies extractive open-domain textual QA and its retrieval stage. Shared task family with RAG; extractive and generative answer settings remain distinct. |
| GE03 | arxiv:2004.04906v1 | dataset:natural-questions | EVALUATED_ON | 4 | K18, K19 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Open-domain QA evaluation; preserve the paper-specific splits and preprocessing. Dataset identity only; not evidence of matched evaluation settings with RAG. |
| GE04 | arxiv:2004.04906v1 | dataset:triviaqa | EVALUATED_ON | 4 | K18, K19 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Open-domain QA evaluation; preserve the paper-specific splits and preprocessing. Dataset identity only; not evidence of matched evaluation settings with RAG. |
| GE05 | arxiv:2004.04906v1 | dataset:webquestions | EVALUATED_ON | 4 | K18, K19 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Open-domain QA evaluation; preserve the paper-specific splits and preprocessing. Dataset identity only; not evidence of matched evaluation settings with RAG. |
| GE06 | arxiv:2004.04906v1 | dataset:curatedtrec | EVALUATED_ON | 4 | K18, K19 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Open-domain QA evaluation; preserve the paper-specific splits and preprocessing. Dataset identity only; not evidence of matched evaluation settings with RAG. |
| GE07 | arxiv:2005.11401v1 | method:dpr | USES | 3 | K06 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Retriever initialized with a pretrained DPR bi-encoder. The method Entity is distinct from the DPR Paper node and from a citation assertion. |
| GE08 | arxiv:2005.11401v1 | method:bert-base | USES | 3 | K06 | BERT-base architecture within DPR component; casing/checkpoint/trained-weight identity not established. BERT-base query and document encoders within the DPR retrieval component. Casing/checkpoint identity is not specified here; merge architecture name only. |
| GE09 | arxiv:2005.11401v1 | method:bart-large | USES | 3 | K15 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Generator architecture in the reported RAG implementation. Do not merge with BERT or treat every BART variant as this exact model. |
| GE10 | arxiv:2005.11401v1 | task:open-domain-question-answering | ADDRESSES | 4 | K14, K17 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Generative answers in the open-domain QA setting. Shared task family with DPR does not equate their answer mechanisms. |
| GE11 | arxiv:2005.11401v1 | dataset:natural-questions | EVALUATED_ON | 4 | K14, K17 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. One of the four datasets selected for open-domain QA experiments. Retain paper-specific splits/scoring; CuratedTREC answer treatment continues on PDF page 5. |
| GE12 | arxiv:2005.11401v1 | dataset:triviaqa | EVALUATED_ON | 4 | K14, K17 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. One of the four datasets selected for open-domain QA experiments. Retain paper-specific splits/scoring; CuratedTREC answer treatment continues on PDF page 5. |
| GE13 | arxiv:2005.11401v1 | dataset:webquestions | EVALUATED_ON | 4 | K14, K17 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. One of the four datasets selected for open-domain QA experiments. Retain paper-specific splits/scoring; CuratedTREC answer treatment continues on PDF page 5. |
| GE14 | arxiv:2005.11401v1 | dataset:curatedtrec | EVALUATED_ON | 4 | K14, K17 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. One of the four datasets selected for open-domain QA experiments. Retain paper-specific splits/scoring; CuratedTREC answer treatment continues on PDF page 5. |
| GE15 | arxiv:2404.16130v1 | method:leiden | USES | 4 | K02, K03 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Hierarchical community detection in the graph index. Leiden is distinct from Louvain, the algorithm planned for our project analytics. |
| GE16 | arxiv:2404.16130v1 | method:map-reduce-summarization | USES | 3 | K04 | Map-reduce summarization workflow; no particular software framework identity. Parallel community-level partial answers followed by global synthesis; see also section 2.6, page 5. A summarization workflow, not evidence that the authors used Hadoop or a particular MapReduce framework. |
| GE17 | arxiv:2404.16130v1 | task:query-focused-summarization | ADDRESSES | 1 | K07, K09 | Qualified assertion in sections 2-5 approved; retain all per-claim evidence limitations. Corpus-level global sensemaking through query-focused summarization. Do not equate with the factoid open-domain QA task in GE02/GE10. |
| GE18 | arxiv:2404.16130v1 | dataset:graphrag-v1-behind-the-tech-transcripts | EVALUATED_ON | 6 | K20 | GraphRAG v1 Behind the Tech transcript corpus only; preserve dataset-specific scope. Podcast transcript corpus used with generated global questions; source collection scoped to this paper. Not a universal Podcast dataset; exact downloadable corpus identity has not been established here. |
| GE19 | arxiv:2404.16130v1 | dataset:multihop-rag-news-corpus | EVALUATED_ON | 6 | K20 | MultiHop-RAG news corpus in this experiment; no equivalence to original QA labels. News corpus from MultiHop-RAG used for global questions; not a claim of using its original QA labels. Do not merge corpus and benchmark task/split without reviewing scope and source identity. |
| GE20 | arxiv:2404.16130v1 | dataset:hotpotqa | EVALUATED_ON | 3 | K05, K11 | Approved for HotPotQA entity-extraction analysis only, not end-to-end QA evaluation; retain evaluation_stage=entity_extraction, COMPONENT_ONLY and sample/chunk-size/gleanings context. COMPONENT_ONLY: chunk-size/entity-extraction experiment; not the main end-to-end answer evaluation. Preserve evaluation_stage=entity_extraction. Shared benchmark family does not imply equal splits or QA evaluation. |
| C03 | arxiv:2005.11401v1 | arxiv:2004.04906v1 | CITES | 13 | K08 | Work-level RAG to DPR citation only; cited arXiv revision unspecified. |
| C09 | arxiv:2404.16130v1 | arxiv:2005.11401v1 | CITES | 13 | K12, K13 | Work-level GraphRAG to RAG citation only; cited arXiv revision unspecified. |

For general section 2–5 approvals, the exact per-claim signed context and inspected locations are also preserved in `review_context_json` and `reviewed_source_locations`, and verbatim in the decision manifest. GE08 remains architecture use through DPR, GE18 the experiment-specific transcript corpus, GE19 the news corpus only, and GE20 entity-extraction COMPONENT_ONLY including the signed sample/chunk-size/gleanings context.

| Key | Exact existing Chunk ID |
|---|---|
| K01 | `10a700b91b8958b06cc812de4df4d3911f9556ec9be2bbae43403a90728c619b` |
| K02 | `20458f66656ee3a42e0b7cd4ed809f17a06f42b8881e89ec0a37548518123db0` |
| K03 | `242f1e4ea282d55c962e205e4352d9dd0bfc0df49ce36be71dfe81deb1541c7d` |
| K04 | `256f935537faa66d1cc6cce9623e010a3c9612d1e77017620c2d923b0c6ebebe` |
| K05 | `44523ced489eef3f98ec37d67ce02025c66a8556c2a14954255c9bf1a5e5e6c3` |
| K06 | `62a59ed9dcd80e7da04f325abd5ed9ea4131960bd0b793bbe324490e4003581d` |
| K07 | `6e57fbafe67c9c13dc9a44d52d0432a361c4ba2a6f0b764c4026dfe442884f65` |
| K08 | `7c3f63ae733fb4207c354cc67dfaeda3c60d782ca71043c555dd627701de4957` |
| K09 | `8972c467bd5b1f590252892e8d363984301e601c945805ffe590c371f964b33a` |
| K10 | `99d443f9eb46e05ca7393c5594be959c500c0fe7fdeba3a7e33ca8b135678df9` |
| K11 | `abeb54c8ae01e48f9bc5412ccae6c614a369afa29cda969c7d6c3dd3e2175d9a` |
| K12 | `ace0086b047574f03e499fac80efe3cab4afd63862be668266b8fbaf86362ae5` |
| K13 | `b5db00dcf2bce7c40d4a67a210fb4c80fee48b60cf4adbf4abad0fb4557932ca` |
| K14 | `bc82c6c4c872cc4b07170569d06261a255d1c9bcccb8c18c4e3aac7540b4153b` |
| K15 | `c11cac7868c07ded56639c91e57a045f67c1e44b4ef94194e190351a57e6bb01` |
| K16 | `c664046a6df44e38d10090ba6f5a5f7b041f24cf4a766a87df5e0b812223b74a` |
| K17 | `d150f9c0a2771388e84e81608154d701219dcc1b4926e7600355a458cace4bef` |
| K18 | `d1c3c5ec507d7347b4ae7774a412d5870d24aa9d32caba18e38b93585b24e1d9` |
| K19 | `f67778ff5f3fa948315dbaa3fc9098162bed80417a1e22c106ad28f080b91146` |
| K20 | `fc1c8aea398b9fb9db9fb75079e04f3396458705c92d443511790e8afc17358a` |

Stable source-specific scientific IDs use the existing hash helper with policy, source Paper ID, PDF hash and GE identifier. C03/C09 reuse their actual existing IDs.

| Evidence | Exact Claim ID |
|---|---|
| GE01 | `a32478347951abc869e54b3e9d01f63d3b61c1ab9e64e36886fa134cd27d7fd8` |
| GE02 | `56f655713226675ca5bcf5c3cdce546d2f44a56d3f35edaf9aa56c70fa0b019a` |
| GE03 | `bb0b65b852b2f5eab48cbeec64663137af85e4c3bbebac2a9d768e4a42c364d6` |
| GE04 | `4d4697a8e804e1885f44b1f575130ae4eaee482c1af4996f60597a733f2bb4ad` |
| GE05 | `be94c64428e3c5566dca26c89fd105e3da67522bf582816774bdfe2eea487bd2` |
| GE06 | `406f2854ffb007ecc4adab3d0b5722f9bf826226b6fce666c00bfacd439075b1` |
| GE07 | `85925964d190ec7d7c5586c2187345ec072875249215aaf5a0cca6bde73b3e2a` |
| GE08 | `b502784b36365f1dbc75475fa32a53ef628a330f57908202a16099f72fc29d51` |
| GE09 | `e2cc2ecff9a021f3204d3b378750efe079a311d6523b8989f238aa07d287cb3b` |
| GE10 | `4cdae187974d4cedd83e75e251d796ea874bd1a876d22ca0cc50cf822976ec58` |
| GE11 | `97c5a0ba105808d638f2b6d5f680ce8044fff2afbc7cc7139bbd66f857933a05` |
| GE12 | `1cd054a2de76096f0ebd15856d2af3f79fa7dacfb4ee24e35eafee2f8fa3d773` |
| GE13 | `4a5222489592107aa61d43b872cef5be1a69c96d353644cd121cd1d5b5da0048` |
| GE14 | `406c6ece2dda6b190d967ee8f4109012948d3a04d7ddb0b2f6319ec16767f437` |
| GE15 | `93c4e79ae6b76af73d351d381e53e9c1da9eb5ff5d5a04f57036c50705934af0` |
| GE16 | `422252afe808914e8244d33fb4904eeb55fec1381a8ba04f44fac3d6bb56eb7d` |
| GE17 | `4eb0fa976c7b2d6e89c9b18ce97989ffba29d3599f117d86243d6e594b4b8714` |
| GE18 | `63446e573d1f354035b24418dcd3ec6e9c5be3b2ea2c71c1393e33b6e16e1d94` |
| GE19 | `879ee6e0a508e79196fd6c996ca69fa02691fcdcd73abb9c5ff0511cfa2a39a5` |
| GE20 | `f912bd1db1c64fa58a6f70767f9b953e6004854cdf9227e55b0a0e9b6560efb5` |
| C03 | `222c833171dc108fb82236c75de7be8bdfd159b58fa18b54de9d9eee82c0c206` |
| C09 | `87e9c7f0228c0da86e2fc46679dfc09c2cad356f889f8c92324b605cf9f7eadd` |

## All 21 alias decisions

A signed decision approving a rejection does **not** approve the equivalence. Negative/unresolved outcomes remain in the manifest/audit with no canonical identity merge. The fourteen accepted scoped identities preserve Method/Dataset/Task kinds. DPR the method stays distinct from DPR the Paper. Existing unreviewed LLM Entity nodes are not silently merged.

| Decision | Outcome | Canonical Entity ID | Mapping | Boundary retained |
|---|---|---|---|---|
| A01 | ACCEPT | dataset:natural-questions | Natural Questions ↔ NQ (Dataset) | DPR p. 4 §4.2; RAG p. 4 §3.1. Same benchmark family; retain splits, answer annotations and preprocessing. |
| A02 | ACCEPT | dataset:triviaqa | TriviaQA ↔ Trivia (DPR) ↔ TQA (RAG) (Dataset) | DPR p. 4 §4.2/footnote 6; RAG pp. 4–6 §3.1/Table 1 and p. 17 Appendix B. Restrict shorthand to these contexts; keep Web Development and Wiki test settings distinct. |
| A03 | ACCEPT | dataset:webquestions | WebQuestions ↔ WQ (Dataset) | Explicit expansions in DPR p. 4 §4.2 and RAG p. 4 §3.1. WebQuestionsSP is a distinct variant, not an accepted mapping here. |
| A04 | ACCEPT | dataset:curatedtrec | CuratedTREC ↔ CuratedTrec ↔ CT (RAG) ↔ TREC (DPR) | DPR p. 4 §4.2; RAG pp. 4–5 §3.1. Only these explicit expansions; generic TREC tracks/corpora are broader. Preserve regex-answer handling. |
| A05 | ACCEPT | method:bert-base | base-uncased BERT (DPR) ↔ BERT BASE (RAG), architecture-level BERT-base | DPR p. 3 §3.1; RAG p. 3 §2.2. Keep uncased qualifier on DPR and unspecified casing on this RAG passage; no checkpoint/weight identity. |
| A06 | ACCEPT | task:open-domain-question-answering | open-domain textual QA (DPR) ↔ open-domain QA (RAG), Task family | DPR p. 2 §2; RAG pp. 4–5 §3.1. Keep extractive and generative settings as distinct qualifications. |
| A07 | ACCEPT | method:dpr | DPR acronym ↔ Dense Passage Retrieval Method | RAG p. 3 §2.2 and DPR p. 3 §3. Distinct typed Entity from the DPR Paper/version. |
| A08 | ACCEPT | method:bart-large | BART-large ↔ BART-large Method spelling | RAG p. 3 §2.3. Preserve named size/variant; this is an identity entry, not an inference that every BART is BART-large. |
| A09 | ACCEPT | method:leiden | Leiden ↔ Leiden Method | GraphRAG p. 4 §2.4 and p. 5 Figure 3. No Louvain alias. |
| A10 | ACCEPT | method:map-reduce-summarization | map-reduce approach ↔ map-reduce summarization workflow | GraphRAG p. 3 introduction continuation and p. 5 §2.6. Scope to summarization; no software-framework identity. |
| A11 | ACCEPT | task:query-focused-summarization | query-focused summarization ↔ QFS Task | GraphRAG p. 1 abstract. Global sensemaking is its use context, not an exact alias for all QFS or QA. |
| A12 | ACCEPT | dataset:graphrag-v1-behind-the-tech-transcripts | podcast transcripts ↔ Behind the Tech transcripts (GraphRAG v1 corpus) | GraphRAG p. 6 §3.1 first bullet. Use `dataset:graphrag-v1-behind-the-tech-transcripts`; generic podcasts outside this scope are not aliases. Corpus bytes/access unverified. |
| A13 | ACCEPT | dataset:multihop-rag-news-corpus | news articles ↔ MultiHop-RAG news corpus, in GraphRAG's experiment | GraphRAG p. 6 §3.1 second bullet/§3.2. Use `dataset:multihop-rag-news-corpus`; distinguish source corpus from original QA labels, temporal scope and derived processing. |
| A14 | ACCEPT | dataset:hotpotqa | HotPotQA ↔ HotpotQA (Dataset family, capitalization) | GraphRAG p. 3 §2.1/Figure 2. Use `dataset:hotpotqa`; preserve sample identity limits and component-only role. |
| A15 | REJECT | None — no merge | DPR Method = DPR Paper/version | RAG §2.2 describes a method; ref. [22] cites a work. Relation between them does not establish node identity. |
| A16 | REJECT | None — no merge | Leiden = Louvain | GraphRAG p. 4 §2.4 names Leiden. Distinct methods; project algorithm choice is separate. |
| A17 | NEEDS_CLARIFICATION | None — no merge | BERT-base entries = identical checkpoint/casing/weights | RAG p. 3 §2.2 plus p. 4 §2.4 do not establish this identity. Do not perform such a merge. |
| A18 | REJECT | None — no merge | BART-large = BERT or every BART variant | RAG p. 3 §§2.2–2.3 distinguishes retriever architecture and generator variant. |
| A19 | REJECT | None — no merge | map-reduce summarization = Hadoop/particular MapReduce framework | GraphRAG p. 5 §2.6 supports a workflow, not framework identity. |
| A20 | REJECT | None — no merge | QFS = factoid QA | GraphRAG p. 1 abstract/p. 6 §3.2 contrasts global sensemaking with explicit fact retrieval. |
| A21 | REJECT | None — no merge | GraphRAG's MultiHop-RAG experiment = original benchmark QA task/labels | GraphRAG p. 6 §3.2 generates new global questions. Shared source articles do not equate experimental tasks. |

## Exact proposal, not achieved graph statistics

- Create **20** scientific Claims and **14** canonical Entities; reuse and enrich
  **2** pending citation Claims; record **22** documented approvals only on application.
- Store **57** complete excerpt/context SUPPORTED_BY relationships, replacing the
  two pending citation supports only after preserving their old properties in history.
  The three unrelated LLM supports remain. Add 20 SUBJECT and 20 OBJECT relationships.
- Derive **2** work-level CITES edges through the existing review mechanism:
  C03 `arxiv:2005.11401v1 → arxiv:2004.04906v1`, target work `arxiv:2004.04906`;
  C09 `arxiv:2404.16130v1 → arxiv:2005.11401v1`, target work `arxiv:2005.11401`.
  Both retain `target_version_as_cited=unspecified`.
- Expected post-application totals, **not measured**: Paper 3, Chunk 153, Entity 17,
  Claim 25 (22 reviewed and 3 pending), CITES 2, SUPPORTED_BY 60.
- No deferred claims or evidence blockers in this exact batch. A17 remains unresolved
  and is excluded from alias merging; it does not block the narrower GE01/GE08 scope.

## Actual verification and development failures

Final `make test`: **280 passed, 0 failed, 1 warning, 16.03 seconds**.
Coverage: **96%**, 1,463 application statements, 63 missed (`--cov=app`); this is
not a separate claim of CLI script coverage. Warning: Starlette uses the deprecated
AnyIO `BlockingPortal` alias. Existing tests continue passing. Current code is copied
into an isolated workspace in the API container by Make; the running API image has
not been rebuilt as part of this milestone.

New tests cover source hashes/offsets/parent associations, signed-manifest tampering,
types/predicates, missing decisions, ambiguous/rejected/unresolved aliases, complete
cross-chunk context, GE20 scope, work-level direction, stale fingerprints, existing
rejections, atomic rollback, repeat application, re-ingestion preservation, source
corruption, retrieval of qualified bundles and approval-status gates. Real Neo4j
integration tests use UUID-named **synthetic** papers and `SYNTHETIC TEST STUDENT`,
then clean them up. Those approvals establish no real-corpus result. Existing Q14/Q15
controls remain covered. The live catalog test now consults recorded approval state
instead of permanently assuming that the corpus has no approved path.

During development the first new suite had one failure/four errors caused by a
synthetic bibliography fixture missing a page-boundary newline; the fixture was
corrected without relaxing the validator. Two initial read-only dry-runs also failed:
Neo4j temporal properties needed stable JSON serialization, and the bibliography
validator needed source-paper-filtered chunks. Both were corrected; subsequent
source audits/dry-runs succeeded. No failed attempt applied real approvals.

Ignored local artifacts (not committed):

- `data/processed/review-integration/dry-run-final.json`: complete proposal and support payload.
- `data/processed/review-integration/research-audit-before.json` and `research-audit-after.json`.
- `data/processed/review-integration/test-final.log` and `data/processed/coverage.xml`.

## Operator runbook — application requires the user's subsequent confirmation

Run from repository root, with the existing Compose dependencies available. This
helper mounts only the relevant source files and PDFs read-only, **not evaluation
gold**, and uses the existing API image/dependencies. It is a local operator command,
not a LangGraph tool or a new service. Read routing is not database authorization.

```bash
review_evidence() {
  docker compose run --rm --no-deps \
    -v "$PWD/app:/workspace/app:ro" \
    -v "$PWD/scripts:/workspace/scripts:ro" \
    -v "$PWD/corpus:/workspace/corpus:ro" \
    -v "$PWD/docs/GRAPH_EVIDENCE_REVIEW.md:/workspace/docs/GRAPH_EVIDENCE_REVIEW.md:ro" \
    -v "$PWD/data/raw:/workspace/data/raw:ro" \
    api python -m scripts.integrate_reviewed_evidence "$@"
}
mkdir -p data/processed/review-integration
review_evidence > data/processed/review-integration/dry-run-next.json
```

Compare the entire next proposal/fingerprint with the reviewed report. A changed
fingerprint is a reason to inspect the new state, not automatically copy a new token.
The following exact application command is **documented only, not executed**, and
requires the user's explicit confirmation of this batch:

```bash
review_evidence --apply \
  --expected-fingerprint d3eb56b2277c2e4c93f350384c3c8004005c8e594db8b133c745960d88a93f62 \
  > data/processed/review-integration/applied.json
```

For a new shell, define the helper above first. `--apply` without a fingerprint
exits 2; validation mismatch exits 1; successful dry-run/application exits 0.
Database/transport errors also fail nonzero. The batch is atomic; a later separate
post-application verification failure cannot retroactively undo a committed batch,
so inspect state and reports before retrying. Credentials stay in Compose environment,
never in commands or logs. The baseline token is a graph checksum, not a secret.

After authorization and successful application, run:

```bash
review_evidence --verify > data/processed/review-integration/post-apply-verification.json
review_evidence > data/processed/review-integration/post-apply-dry-run.json
```

`--verify` requires all 22 actual records to match the signed decisions, approval flags,
review metadata, source bundles and endpoints. It checks real CITES edges and queries
the actual directed two-edge GraphRAG → RAG → DPR path. It reports the approved
reified scientific assertions and four shared named benchmarks (NQ, TriviaQA,
WebQuestions, CuratedTREC), retaining experiment-specific limits. None of those
positive **real-corpus** checks has passed yet: application is still pending.

For an authorized repeat-run idempotency check, inspect the post-apply dry-run:
all 22 actions must be `REUSE_APPROVED` with no proposed new entities. Copy its
reviewed **post-apply** fingerprint, then run `review_evidence --apply
--expected-fingerprint <reviewed-post-apply-fingerprint>` and compare fingerprints,
counts, review history and all records. Do not reuse the obsolete pre-apply token.
This repeat application is already tested on synthetic graphs, not on real approvals.

Before using the running API for new bundle-aware retrieval, update that existing
service from this checkout, then rerun health/tests:

```bash
docker compose build api
docker compose up -d --no-deps api
make health
make test
```

No image rebuild or service restart was performed in this milestone. The old image
must not be used as evidence that the new multi-chunk retrieval code is deployed.

## Files and readiness for Prompt #7B

New: `app/ingestion/research.py` (shared mapping), `reviews.py` (signed decisions/aliases),
`support.py` (complete support validation), `reviewed.py` (bounded prepare/transaction),
`scripts/integrate_reviewed_evidence.py`, `corpus/review_decisions.json`,
`tests/test_reviewed_evidence.py`, and this report.
Modified: `app/ingestion/graph.py` (review provenance/transaction/support checks),
`app/agent/tools.py` (full support and qualification propagation),
`scripts/verify_research_handoff.py` (reuse mapping helper),
`tests/test_retrieval_graph.py` (approval-aware live expectation), `PROJECT_PLAN.md`,
`docs/ARCHITECTURE.md`, `docs/DECISIONS.md`.

Remaining gate: explicit confirmation of this reviewed batch, actual application,
positive real-graph verification and deployment of the tested retrieval code.
Then separately approve Prompt #7B's advanced-query/GDS scope and defensible projection.
Three papers and two work-level edges would still be a tiny citation graph; shared
benchmark edges must preserve task/split/component qualifications. No algorithm,
projection quality, scientific superiority or grading credit is claimed here.
