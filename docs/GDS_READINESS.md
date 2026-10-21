# GDS readiness

**Decision: the three-paper projection is suitable for an implementation and provenance demonstration, but too small for strong centrality or community conclusions.** Prepare the existing PageRank/Louvain design after review; do not force connectivity or change the schema. No Neo4j query, projection or GDS algorithm was run in this task.

## Inputs and present limitation

Read: attached projects_spec.md (Project 8 and GDS rubric), project_checklist.md, PROJECT_BRIEF.md and ARCHITECTURE.md, the ten-paper corpus manifest, citation evidence, current evaluation plan/gold and ML recommendation. The Library's planning documents predate the user's reported implementation. Their claim/projection contracts guide this handoff; their old “not implemented” wording does not override the user's update.

The user reports 153 Chunks, three Entities, five unreviewed Claims and no student-verified CITES edges. These are **reported counts, not a database audit**. Chunks provide retrieval coverage, not 153 Paper vertices. Unreviewed claims contribute nothing to the architecture's verified projection. On the reported state, there is no demonstrated reviewed shared-entity adjacency yet. The earlier 13 located references are not 13 approved database edges.

The professor requires an in-memory GDS projection and at least two algorithms (2 points), separately from an ML prediction/classification workflow (3 points). PageRank and Louvain address the algorithm requirement only after actual execution and evidence. They do not replace the ML experiment.

## Keep the architecture's projection

For each selected Paper version p, let E(p) be the set of resolved Entity IDs reached through student SOURCE_VERIFIED USES, EVALUATED_ON or ADDRESSES Claims. Include all selected papers, including isolates. Deduplicate entities per paper, regardless of repeated chunks or claims. Project one undirected pair for each nonempty intersection, with:

`weight(p,q) = |E(p) intersection E(q)| / |E(p) union E(q)|`

Exclude self-loops and zero weights. Emit each unordered pair once before undirected projection; account for the GDS representation of both directions when reporting relationship count. Retain contributing entity IDs and the approved claims for **both** papers in an explanation map. Qualifiers stay accessible even though Jaccard uses entity identity alone. Do not include NEXT, PART_OF, raw MENTIONS, CITES, unreviewed claims or ML predictions in this projection.

| Layer | Meaning | May become a source fact? |
| --- | --- | --- |
| Reviewed Claim | A student confirmed what a particular passage states | Only through the existing review process; not proof of independent scientific truth |
| SHARES_ENTITY adjacency and weight | Deterministic similarity derived from a particular reviewed snapshot | No; it is an analytical result, with parent claim provenance |
| PageRank / Louvain output | Ranking / partition of that derived graph | No; neither citation influence nor an author-stated relationship |
| ML prediction | A learned label or predicted link | No; retain HYPOTHESIS status outside factual answers |

## What these 20 candidates would produce

**Conditional arithmetic only:** if all candidates and proposed aliases are approved, and no other claims are included, DPR has six unique entities, RAG eight, and GraphRAG six. DPR and RAG share six entities: four datasets, BERT-base and the open-domain QA task family. Their union is eight, so Jaccard is **6/8 = 0.75**. Neither shares an entity with GraphRAG in this bounded candidate set.

That gives three Paper vertices, one logical undirected edge, two connected components and one isolate. This is a checkable expectation for this exact fixture, not a prediction about the complete literature or the live database. If the BERT-base merge is deferred, or scope changes, recompute the sets. Uniformly initialized PageRank should treat the two linked vertices symmetrically; a ranking between them would need investigation. Louvain cannot reveal a rich research taxonomy from one pair and an isolate.

## Small expansion within the existing ten papers

**Practical minimum for the deadline: five papers with reviewed provenance for at least four logical shared-entity edges, at least three recurring entities, and some variation in neighborhoods or weights.** This is a proposed educational target, not a statistical threshold or professor rule. A corpus with two components is acceptable; report that community separation may simply reflect disconnectedness. Do not drop the isolate or broaden aliases to achieve a target.

1. **FiD v1 (2007.01282), six pages:** first expansion candidate. Its page 2 §3 retrieval description identifies DPR, and the opening results discussion identifies Natural Questions/TriviaQA. Inspect the experimental section before approving dataset claims. This is a promising way to add a third member to the DPR/RAG group. These are research leads, not additional approved CSV rows.
2. **HippoRAG v1 (2405.14831):** page 5 §3.1 explicitly includes HotpotQA in retrieval evaluation. The main-text passage was located here, but no student claim was created. Together with GE20 it offers a possible shared-benchmark-family edge to GraphRAG. It joins an extraction-component experiment to a retrieval experiment; disclose that scope difference. It does not establish comparable QA performance or a bridge to DPR/RAG.
3. **REALM v1 (2002.08909):** next reserve if time remains. Check its actual method/evaluation sections for shared QA datasets and encoder identities; prior citations alone are insufficient. Further edges remain unverified here.

After FiD/HippoRAG review, the expected structural opportunity is a three-paper retrieval group and a separate two-paper group, not guaranteed global connectivity. Record actual edges after review. Six to eight papers may improve variety, but stop expansion once the demonstration is reproducible. LightRAG and Self-RAG remain reserve sources requiring direct use/evaluation checks; do not promote their baseline mentions. Avoid ColBERT/G-Retriever first because the earlier manifest flags extraction issues. No new papers, paid APIs or large extraction rerun are needed for this bounded plan.

## Algorithm configuration and validation

Use the exact installed Neo4j/GDS versions and the architecture's compatibility gate. Current official [PageRank documentation](https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/) supports a weight property, damping, iteration/tolerance controls and convergence reporting. Proposed run: weighted, damping 0.85, maxIterations 100, tolerance 1e-7, concurrency 1; record actual supported settings and convergence. Compare ordering with weighted degree and show the shared entities behind a top result. Interpret it as navigation prominence within this selected graph, not scientific impact.

The official [Louvain documentation](https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/) describes modularity-based grouping and weighted execution. Record modularity, community sizes and parameters. Start with installed-version defaults for levels/iterations/tolerance and concurrency 1. The documented `seedProperty` initializes communities; it is not a random-number seed. Do not invent a `randomSeed` argument. Repeat the same frozen run three times if practical and compare membership pairs, not arbitrary numeric community IDs. Preserve variation.

Before either algorithm, estimate memory and export the exact projection inputs, review/alias snapshot hashes, node count, logical pair count, projected relationship count, components, isolates, degree/weight distributions and exclusions. Use stream/stats modes for inspection; do not overwrite source claims with scores. Include isolated nodes in output. Reject stale projections after a review or alias change.

| Validation example | Check to perform later |
| --- | --- |
| GE03–GE06 with GE11–GE14 | Four named dataset joins, each backed by two separately approved source claims |
| Exactly the 20-row approved fixture | Three vertices; one logical DPR–RAG edge; weight 0.75; GraphRAG retained as isolated |
| Duplicate support in overlapping chunks | No increase in distinct-entity sets or pair weight |
| Pending/rejected claim or unapproved alias | Does not contribute to verified projection; empty result is valid |
| Synthetic three-node equal-weight path, outside corpus | Endpoints symmetric; center ranks above endpoints under ordinary uniform PageRank; no invented numeric score |
| Louvain on the actual snapshot | Report partition, component structure and shared-entity explanations; do not demand a preset number of groups |

The synthetic fixture checks mechanics only. Deliver real corpus outputs, commands/configuration, timings and limitations before claiming the rubric evidence. Community output on a tiny or component-separated graph remains exploratory, even when the code runs correctly.

## Deadline gate

October 20: review prototype claims/aliases and resolve real Chunk IDs. October 21: run the three-paper structural checks; add FiD and HippoRAG only if bounded annotation is practical. October 22: execute both algorithms, compare PageRank with degree, inspect communities and retain failures. October 23: reproduce the frozen snapshot and demonstrate it. If review or compatible GDS installation is incomplete, report that specific blocker; do not substitute fabricated communities or import unreviewed claims as facts.
