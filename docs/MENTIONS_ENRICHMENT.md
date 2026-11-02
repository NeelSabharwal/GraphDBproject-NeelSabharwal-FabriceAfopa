# Controlled source-mention enrichment — 2026-11-02

The master completion task explicitly authorized the frozen v4 occurrence batch after
backup, source checks, a fresh dry-run and synthetic transactional tests. This is
mechanical source-location enrichment, **not student approval of scientific claims**.

## Frozen inputs and actual application

- Policy: `scoped-exact-mentions-audit-v4`; tracked in `corpus/mentions_policy_v4.json`.
- Original proposal: `data/processed/ml/mentions-audit/proposed_edges-v4.json`.
- Proposal SHA-256: `990e943eb5be101d27a5435738be49aaadcee9a82faeb7ada92c6eb22b42f0b0`.
- Policy SHA-256: `6966fc03fb1633c782edc999acb6d6481fc01d0e5100f1a3b72e81c035c2645f`.
- Protected baseline fingerprint: `a847ebb5017a08830c281a64afbdba68a278d208e88f499ac7bde54628594682`.
- Final full fingerprint: `0a17d318be0066b5b7fb20a88e1821586cc3135c07dbbd9a27012ebfe363d62f`.

`app/mentions/matcher.py` adapts the frozen matcher into a tracked module. The
complete serialized 145-edge proposal reproduced the original SHA-256, rather than
merely reproducing its count. All 153 Chunks and original PDF/page coordinate maps
were revalidated. The same alias, token-boundary, reference-zone, heading, short-label
and caption exclusions apply to every Chunk. There is no annotation/label input.
A17 remains unresolved; rejected aliases remain rejected. The DPR page-7 control-character
warning is preserved, not repaired by changing source bytes.

One real transaction created **145 occurrences**, affecting **52 Chunks** and **14
existing canonical Entities**. Total MENTIONS is **148**, including three pre-existing
LLM mentions. The replay dry-run reports **0 new / 145 reused**. Removing only the
new batch from the complete post-application snapshot reproduces the exact protected
baseline fingerprint: original nodes, source text, embeddings, scientific assertions,
review histories and CITES edges are unchanged.

## Recoverable offline backup

Actual `/data` volume: `ai-research-graphrag_neo4j_data` (discovered from the mount).
Archive, outside that volume:

`data/processed/final-delivery-20261102/neo4j-before-mentions-20261102T130826Z.tar.gz`

Size **10,438,771 bytes**, **132 archive entries**; SHA-256:
`2952f99c907a4f16f2f3bcf0a26f779846898b7f82f4c669d4a3d6412a19a8cb`.
Neo4j/API were stopped before copying. Full gzip CRC/decompression, tar listing,
database/transaction contents, nonzero size and checksum passed; services returned
healthy. The archive, checksum and receipt stay ignored/private. An initial helper
image lookup failed before copying or applying anything; a locally available helper
image resolved it. Both logs remain in the ignored delivery directory.

## Code and safety boundaries

- `source.py`: verifies the pinned policy, reviewed identity records, actual PDF/page
  hashes, reconstructed Chunks, parent links and the exact deterministic proposal.
- `graph.py`: validates every endpoint/span before any CREATE, rejects stale state
  and conflicting occurrences, and uses one explicit transaction without automatic
  write retry. No nodes, reviews, scientific Claims or CITES edges are created.
- Each new relationship stores exact text/PDF/page/raw offsets and hashes, alias
  scope, policy/proposal hashes, batch ID, `origin=DETERMINISTIC_SOURCE_MATCH`,
  `validation=EXACT_SURFACE`, `student_review_status=NOT_REVIEWED`.
- `MentionImporter.rollback(receipt)` removes only owned relationships in that
  receipt's `created_ids`, preserving pre-existing/reused relationships. Mid-write
  failure, ownership, atomicity, idempotency and rollback are tested on UUID-scoped
  synthetic fixtures. No real rollback was performed.

## Reproduce the read-only audit on this database

Use a fresh output filename. Source and raw PDFs are mounted read-only; only ignored
reports are writable. Do not rerun the scientific evidence importer.

```bash
mkdir -p data/processed/mentions-check
# Run from the project root; Compose supplies credentials without printing them.
docker compose run --rm --no-deps -T --user "$(id -u):$(id -g)" \
  -v "$PWD:/workspace:ro" -v "$PWD/data:/workspace/data:ro" \
  -v "$PWD/data/processed:/workspace/data/processed" \
  --entrypoint python api -m scripts.enrich_mentions \
  --output data/processed/mentions-check/dry-run.json
```

`--apply` additionally requires the inspected full `--fingerprint` and a verified
`--backup-receipt`; its archive must still exist with the recorded size and checksum.
This historical authorization is deliberately bound to the protected local snapshot,
including Neo4j element identities. A separately created database cannot borrow that
fingerprint/receipt: establish and review its own baseline before adapting the gate.
Source matching is reproducible from the pinned PDFs and canonical identities; no
private database backup is included in the GitHub packages. Stop on any discrepancy.
