# Cross-paper evaluation candidates

Checked 2026-10-20 (Europe/Paris). All source versions are v1. These are development prompts, not a frozen held-out test or student-approved gold answers. The JSON companion records exact passage offsets and hashes. PDF page numbers below are 1-based.

## Q1 — prototype

How does RAG use DPR, and what differs between training the DPR retriever and fine-tuning the retrieval/generation components in RAG?

Passages to check:

- **P01: [DPR v1, PDF p. 3](https://arxiv.org/pdf/2004.04906v1#page=3)**, §3.1. Overview through encoder and inference paragraphs, including equation 1.
- **P02: [DPR v1, PDF p. 3](https://arxiv.org/pdf/2004.04906v1#page=3)**, §3.2. Training objective and positive/negative passage discussion; continues onto next page.
- **P03: [RAG v1, PDF p. 3](https://arxiv.org/pdf/2005.11401v1#page=3)**, §2.2. Retriever definition and pretrained encoder initialization.
- **P04: [RAG v1, PDF p. 3](https://arxiv.org/pdf/2005.11401v1#page=3)**, §2.4. Start of joint-training description.
- **P05: [RAG v1, PDF p. 4](https://arxiv.org/pdf/2005.11401v1#page=4)**, §2.4 (continued). Continuation specifying which components are kept fixed or fine-tuned.

Review checks: Distinguish explicit method use from a bibliography mention. Identify components and training stage accurately; cite both papers.

Gold answer: **not yet authored or independently reviewed**.

## Q2 — prototype

Compare DPR’s passage-retrieval evaluation, RAG’s open-domain QA evaluation and GraphRAG’s global-summary evaluation: what datasets and scoring criteria do they use, and are their scores directly comparable?

Passages to check:

- **P18: [DPR v1, PDF p. 3](https://arxiv.org/pdf/2004.04906v1#page=3)**, opening paragraph before §3. Definition of the isolated retriever evaluation measure.
- **P06: [DPR v1, PDF p. 4](https://arxiv.org/pdf/2004.04906v1#page=4)**, §4.2. Descriptions of the five QA datasets.
- **P07: [RAG v1, PDF p. 4](https://arxiv.org/pdf/2005.11401v1#page=4)**, §3.1. Open-domain QA formulation and dataset list; paragraph continues on page 5.
- **P08: [RAG v1, PDF p. 5](https://arxiv.org/pdf/2005.11401v1#page=5)**, §3.1 (continued). Remaining QA setup and scoring description.
- **P09: [GraphRAG v1, PDF p. 6](https://arxiv.org/pdf/2404.16130v1#page=6)**, §3.1–3.2. Corpus descriptions and activity-based question-generation setup.
- **P10: [GraphRAG v1, PDF p. 7](https://arxiv.org/pdf/2404.16130v1#page=7)**, §3.4. Evaluation procedure and criteria.

Review checks: Separate retrieval, answer and corpus-summary evaluation; do not infer a universal winner. Do not confuse a dataset mentioned elsewhere with a dataset used in the selected evaluation.

Gold answer: **not yet authored or independently reviewed**.

## Q3 — prototype

Can you substantiate a two-edge directed citation path from GraphRAG to DPR within the three-paper corpus? Identify the intermediate paper and the bibliography evidence for each edge.

Passages to check:

- **C03: [RAG v1, PDF p. 13](https://arxiv.org/pdf/2005.11401v1#page=13)**, Reference [22]; target arxiv:2004.04906. See CSV for source hash and title location.
- **C09: [GraphRAG v1, PDF p. 13](https://arxiv.org/pdf/2404.16130v1#page=13)**, References: Patrick Lewis et al. (2020); target arxiv:2005.11401. See CSV for source hash and title location.

Review checks: Follow direction from citing paper to cited work. A reference to a work does not establish which arXiv version was read. Do not label this the shortest path without a complete edge audit.

Gold answer: **not yet authored or independently reviewed**.

## Q4 — development

How do GraphRAG and HippoRAG construct their graph representations and use them at question time to select or compose evidence?

Passages to check:

- **P11: [GraphRAG v1, PDF p. 3](https://arxiv.org/pdf/2404.16130v1#page=3)**, §2.2. Entity and relationship extraction paragraph.
- **P12: [GraphRAG v1, PDF p. 4](https://arxiv.org/pdf/2404.16130v1#page=4)**, §2.4–2.5. Graph definition, community algorithm and start of community-summary procedure.
- **P13: [GraphRAG v1, PDF p. 5](https://arxiv.org/pdf/2404.16130v1#page=5)**, §2.6. Query-time community-answer and global-answer procedure.
- **P14: [HippoRAG v1, PDF p. 4](https://arxiv.org/pdf/2405.14831v1#page=4)**, §2.3. Offline indexing and online entity-linking procedure.
- **P15: [HippoRAG v1, PDF p. 5](https://arxiv.org/pdf/2405.14831v1#page=5)**, §2.3 (continued). Query-seeded graph computation and conversion to passage scores.

Review checks: Separate offline construction from query-time operations. Name the graph algorithms using source evidence; do not substitute the project’s proposed GDS algorithms. Describe differences without inventing an experiment comparing the two papers.

Gold answer: **not yet authored or independently reviewed**.

## Q5 — development

How do RAG-Sequence, RAG-Token and Fusion-in-Decoder combine information from multiple retrieved passages, and where in each model does that combination occur?

Passages to check:

- **P16: [RAG v1, PDF p. 3](https://arxiv.org/pdf/2005.11401v1#page=3)**, §2.1. The two marginalization formulations and equations.
- **P17: [FiD v1, PDF p. 3](https://arxiv.org/pdf/2007.01282v1#page=3)**, §3 (continued). The two reading paragraphs explaining encoder/decoder passage combination.

Review checks: Read equations and the FiD reading paragraphs together. Require support from both papers; do not infer mechanism solely from model names.

Gold answer: **not yet authored or independently reviewed**.

## Annotation procedure

Two students should independently read the listed passages, write supported answer statements and page citations, resolve disagreements, and record reviewer/date. Split compound questions into atomic claims when scoring. Reject invented facts and unsupported comparisons; allow qualified abstention where the sources are insufficient. These questions have already been exposed during research, so use them for development. Create new, separately frozen questions for final testing.
