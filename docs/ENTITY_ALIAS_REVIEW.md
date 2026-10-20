# Entity and alias review

Prepared 2026-10-20 for the October 23 deadline. **All 20 CSV candidates are SOURCE_LOCATED. None is student SOURCE_VERIFIED.** They propose 14 distinct entities: five Methods, seven Datasets and two Tasks. The rows comprise six USES, eleven EVALUATED_ON and three ADDRESSES assertions. They are candidates, not imported graph facts or an exhaustive inventory.

## Evidence and status contract

The pinned [DPR v1](https://arxiv.org/pdf/2004.04906v1), [RAG v1](https://arxiv.org/pdf/2005.11401v1) and [GraphRAG v1](https://arxiv.org/pdf/2404.16130v1) bytes were rehashed and page text re-extracted with pypdf 6.10.0. Their hashes match the corpus manifest. Relevant source contexts were inspected; the newly used DPR page 2 and GraphRAG pages 3 and 6 were also visually inspected. The CSV carries the hashes, URLs, pages and exact text coordinates.

Each short excerpt locates a passage. Review the **entire context interval and PDF page**, including qualifiers, to decide whether it supports the proposed assertion. A dataset name alone does not entail EVALUATED_ON. All selected rows have explicit author-method, experimental-use or stated-task context; none is justified solely by related work or a bibliography.

SOURCE_LOCATED means Work found and checked the passage. The existing architecture maps an unapproved candidate to Claim status EXTRACTED after ingestion validation. Only a real student may promote it to SOURCE_VERIFIED, recording identity, time and the review decision. `origin=manual` describes this research route, not human approval; `research_origin=assistant_source_reading` makes that explicit. The reviewer, reviewed-at and Chunk-ID cells are deliberately blank.

Earlier evaluation files use SOURCE_VERIFIED for assistant-checked answers, and the citation CSV uses VERIFIED_REFERENCE_IN_SELECTED_SOURCE. **Neither status is a student graph approval.** Preserve those files; apply this distinction when integrating them.

## Proposed mappings requiring review

Every mapping below remains pending. Merge only within the stated kind and scope; preserve surface forms and qualifiers.

| Proposed canonical entity | Source forms / candidate IDs | Review decision to make |
| --- | --- | --- |
| Dataset: Natural Questions | NQ; GE03, GE11 | Same named dataset family. Preserve splits and preprocessing; no matched-benchmark claim. |
| Dataset: TriviaQA | Trivia in DPR, TQA in RAG; GE04, GE12 | Same named benchmark. Keep open-domain setup qualifiers. |
| Dataset: WebQuestions | WQ; GE05, GE13 | Same named dataset. Do not merge with WebQuestionsSP or other variants. |
| Dataset: CuratedTREC | TREC in DPR, CuratedTrec / CT in RAG; GE06, GE14 | Resolve only these explicit expansions. Bare TREC elsewhere is ambiguous. Scoring and answer handling remain paper-specific. |
| Method: BERT-base | DPR's base uncased encoders; RAG's BERT BASE; GE01, GE08 | Merge at architecture level only. RAG's passage does not establish identical casing, weights or checkpoint. Do not merge with generic BERT or BERT-large automatically. |
| Task: Open-domain question answering | DPR's open-domain textual QA, RAG's open-domain QA; GE02, GE10 | Same task family. Preserve DPR's extractive versus RAG's generative setting. |
| Method: Dense Passage Retrieval | DPR in GE07 | Resolve the method acronym. Keep the method Entity separate from the DPR Paper version and its CITES claims. |
| Method: BART-large | GE09 | Keep the named variant. BART, BERT and BART-large are not interchangeable exact identities. |
| Method: Leiden | GE15 | Keep separate from Louvain. The source paper's method and this project's planned GDS algorithm are different things. |
| Method: Map-reduce summarization | GE16 | A summarization workflow; do not identify it with Hadoop/software MapReduce or all hierarchical summarization. |
| Task: Query-focused summarization | QFS; GE17 | Keep separate from factoid open-domain QA. Global sensemaking is context here, not an automatically equivalent task label everywhere. |
| Dataset: Behind the Tech transcripts (GraphRAG v1 corpus) | Podcast transcripts; GE18 | Use the scoped proposed ID. No universal dataset called Podcast is established. Exact corpus bytes/access need separate checking. |
| Dataset: MultiHop-RAG news corpus | News articles; GE19 | The paper uses the news corpus with generated global questions. Do not merge this automatically with the original benchmark question set or with an arbitrary news corpus. |
| Dataset: HotpotQA | HotPotQA; GE20 | Case-normalize the named benchmark family. Retain **entity-extraction component experiment** scope; this is not GraphRAG's main answer benchmark. |

## Interpretation traps to reject

- GraphRAG page 6 §3.2 lists HotpotQA and MT-Bench while discussing existing benchmarks. That list alone does not establish experimental use. GE20 instead points to page 3 §2.1 and the Figure 2 experiment. No MT-Bench use candidate is proposed.
- RAG's comparison with closed-book QA does not establish use of every compared model. GE07–GE09 use the implementation description in §2.2–2.3.
- A reference to a paper does not imply use of its method. A method-use assertion does not itself supply a CITES edge.
- Shared dataset identity permits a join; it does not establish equal questions, training data, splits, metrics or comparable numerical performance.

## Short review order

First review GE03–GE06 and GE11–GE14 together to enable the four-dataset intersection in evaluation Q07. Then review GE01/GE08, GE02/GE10, GE07/GE09, and GE15/GE17. Finally review GE16 and the scoped GraphRAG datasets GE18–GE20. Reject or defer ambiguous rows individually; do not approve the file as a batch merely because offsets match.

Keep a separate decision record keyed by candidate ID with student name, timestamp, APPROVED/REJECTED/NEEDS_CLARIFICATION, resolved entity ID and rationale. No approval or alias merge is supplied by this handoff.
