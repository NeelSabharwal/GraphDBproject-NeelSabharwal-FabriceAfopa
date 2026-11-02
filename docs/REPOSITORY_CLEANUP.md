# Repository cleanup — final acceptance, 2026-11-02

Baseline: merged PR #12, `b782bbf`; isolated `feat/final-acceptance` worktree.
All 136 tracked files were inventoried by path/size/hash. None is empty, no pair is
byte-identical, and all Markdown relative file links resolved before cleanup.

- **Files removed/renamed:** none. No demonstrated obsolete file justified deletion.
  Historical handoffs, audits and research proposals retain design/review provenance.
- **Code cleanup:** remove the unused `map_supports` import from
  `scripts/verify_research_handoff.py`. Pylint identified it; repository-wide references
  confirm this script does not call/export it to a consumer. The actual helper and
  its use by source validation/review integration remain intact.
- **Documentation:** root evaluator navigation identifies current runbooks versus
  historical records. PROJECT_BRIEF and the original architecture proposals are
  explicitly historical. Current publication/CI status supersedes stale statements;
  original scientific reviews and decision entries are preserved.
- **Presentation:** the notebook now displays actual directed citation-path and
  PageRank results as SVG using existing IPython/standard-library dependencies.
  It never invents missing paths and keeps generated output ignored.
- **Dependencies/fixtures removed:** none. Every direct dependency serves runtime,
  tests, lint/format or notebook execution; transitive pins remain unchanged. The
  in-code fixture suite and package `__init__.py` files are functional, not scaffolding.
- **Preserved:** course requirements, all corpus hashes/manifests, Claim/alias/label
  approvals, gold, scientific limitations, model settings/results, diagrams, genuine
  contribution/review history and AI-assistance disclosures. No mass renaming.

## PR presentation

No closed PR title/description or discussion was edited. PR #3's concatenated title
could be rendered more clearly in an evaluator index as “Review evaluation evidence
and guardrail cases”; PR #7 can be referenced without its leading whitespace. These
are proposed display labels, not retrospective metadata changes. The new acceptance
PR should describe final acceptance evidence, notebook visualization and publication
blockers explicitly, rather than claim “100/100”.

## Validation

Cleanup completed before final build/test/notebook/image inspection. Actual command
results, failures, coverage, lint, link checks and protected graph fingerprint are
recorded in [FINAL_VALIDATION.md](FINAL_VALIDATION.md). Private inventories and logs
remain under ignored `data/processed/final-acceptance/`. No deletion/rename dependency
repair was needed. Publication permissions, full redistribution evidence and genuine
human review/defense requirements are not cosmetic cleanup tasks.
