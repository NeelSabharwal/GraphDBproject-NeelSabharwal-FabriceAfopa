# Demonstration and reproducibility guide

The tracked `demo.ipynb` is executable source with no cached results. `make notebook`
uses the locked Python 3.12 environment and writes authentic outputs to ignored
`data/processed/demo.executed.ipynb`. It does not train a model, ingest documents,
apply reviews or mutate the persisted graph. The final 22-cell version executed successfully on
2026-11-02, including SVG views of the actual directed citation path and PageRank
scores. The earlier 18-cell run is retained as historical evidence. An initial live agent issue and its correction are retained in the validation
report; no failed result is presented as a success.

## Preparation on the existing reviewed deployment

```bash
make docker-run
make install
make health
make models-check
docker compose exec -T api python -m scripts.advanced_graph refresh
make test
make lint
make notebook
```

`refresh` creates/reuses only a managed in-memory projection; no scientific assertions
are imported. After a database restart, missing GDS catalog state can return 503 until
refresh. A fresh machine also needs the pinned corpus, source-approved review integration
and controlled mention layer before reproducing this particular graph/ML demonstration.
Follow the runbooks; do not borrow a historical fingerprint or fabricate approvals.

The notebook uses `DEMO_API_URL` (default `http://api:8000` inside Docker) and `ML_REPORT`
(default the ignored original pilot report). For local kernels, supply the configured
Neo4j environment securely and a reachable API URL. Credentials are never notebook
outputs. A missing ML artifact is reported explicitly; metrics are never substituted
with literals. Reproduce the frozen pilot into a new ignored directory as described in
[GRAPH_ML.md](GRAPH_ML.md), then set ML_REPORT to that report when executing elsewhere.

## Suggested live defense sequence

1. Open Swagger, show ready status and the three real Paper metadata records.
2. Show the editable schema and explain why Claim is separate from Entity and Chunk.
3. Display actual constraints, indexes, hashes, page offsets, review statuses and source
   support. Explain SOURCE_LOCATED versus SOURCE_VERIFIED and mechanical MENTIONS.
4. Run GraphRAG → RAG → DPR in that direction. Inspect both bibliography support bundles;
   then reverse the direction to demonstrate honest unavailability if no approved path.
5. Show the four shared DPR/RAG datasets and the real Leiden concept neighborhood.
6. Inspect the actual Cypher PROFILE plan: aggregation reduces repeated graph work,
   but three papers do not establish large-scale performance.
7. Run weighted PageRank and Louvain; explain the single .75 edge and GraphRAG isolate.
8. Ask Q01/Q04 through the agent and inspect search → source-read traces and quotations.
   CPU runs can take tens of seconds. No semantic-correctness score is invented.
9. Show safe rejection of a mutation request. The automated page-999 fixture is an
   output-validator test, not a modified PDF or executed malicious Cypher.
10. Show frozen ML features, paper split, majority baseline and the failed held-out
    logistic result. Explain development-visible labels, overlap and domain limitations.
11. Show the final test/lint logs and the rubric's actual remaining gaps.

## Editable assets and authentic screenshots

Open `docs/diagrams/graph-schema.drawio` and `system-architecture.drawio` in diagrams.net;
SVG files are viewable exports. These are schema/architecture illustrations, not screenshots
of measured outputs. `docs/screenshots/swagger.png` and `health.png` were captured by a
real headless Chromium browser against the running local API on November 2, 2026.
No results, approvals or UI states were composited into those images.

The notebook's private output contains actual source excerpts and graph details. Share
it privately if needed; the public patch carries the output-free notebook, diagrams,
screenshots and aggregate validation summaries only. Never share `.env`, model weights,
PDF source bytes, database archives or full Chunk exports in the GitHub package.

## Student-defensible modeling appendix

A generic entity/RELATED_TO graph would lose relationship meaning, claim qualifications
and review history. Here, reified Claims connect a Paper subject to a typed Entity or
Paper object and retain all SUPPORTED_BY segments. Direct CITES edges are derived only
from approved citation claims and are checked against their original bibliography
sources. Alias identity acceptance is scoped; BERT variants and unresolved A17 are
not silently collapsed. NEXT preserves same-paper source order rather than inferred
scientific causality. MENTIONS says only that an approved entity surface was located.

An alternative direct `Paper-[:USES]->Method` schema would be simpler to traverse but
would need duplicated relationship evidence and explicit handling of multi-chunk
supports/contradictions. A vector-only system would retrieve similar text but would
not validate a directed citation chain or shared approved benchmark identity. The
chosen graph is useful for those questions while still limited by selective manual
review and sparse extracted entities. GDS operates on a derived similarity projection;
its edges are not persisted as scientific evidence. The ML experiment remains a
small interpretable classical learner on local graph features, not a GNN or a
rebranded PageRank score.
