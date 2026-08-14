# Git branch reconciliation

Date: 2026-08-15

## Objective

Consolidate all surviving review-project branches into `main` without losing
the July screening artifacts, the recovered taxonomy/atlas history, the August
living-review implementation, or the full-cohort rerun.

## Branch topology before reconciliation

| Ref | Tip before reconciliation | Relationship to local recovery branch |
|---|---|---|
| `main`, `origin/main` | `75e51c21` | Direct ancestor; 18 project commits behind before the audit commit |
| `origin/codex/fulltext-section-screening-audit` | `24a088ff` | Direct ancestor |
| `origin/recovery/crabs-2026-abstract-20260729` | `24a088ff` | Direct ancestor |
| local `recovery/crabs-2026-abstract-20260729` | `0281bcf0` | Most complete linear project history |
| `origin/codex/july-2026-screening-artifacts` | `28b9c2d8` | Diverged at `9665b466`; two unique commits |

The local `main` worktree was clean. The recovery worktree contained only the
new taxonomy-trace audit files, which were committed separately as `7d4a8e96`.

## July branch content audit

The two July commits changed 102 paths relative to their merge base. Blob-level
comparison against the recovery tree found:

- 100 paths already present byte-for-byte in recovery;
- 0 paths missing from recovery;
- 2 paths with newer recovery content:
  `protocol/PRISMA_protocol.md` and `protocol/prisma_flow_template.md`.

The July versions stopped at the title/abstract checkpoint. The recovery
versions preserve those results and additionally document targeted full-text
screening, manual resolution, the completed 52-record baseline, and the August
living-review update. The merge therefore retained the recovery versions of
both files while joining the July commit history through merge commit
`ad7facd4`.

## Validation

- `origin/codex/july-2026-screening-artifacts` is an ancestor of the reconciled
  recovery HEAD.
- `origin/codex/fulltext-section-screening-audit` is an ancestor.
- `origin/recovery/crabs-2026-abstract-20260729` is an ancestor.
- the pre-merge `main` is an ancestor.
- `git diff --check` passed.
- Python compilation of the living-review runner and taxonomy audit passed.
- the taxonomy audit reproduced byte-for-byte.
- `.venv-docling/bin/python tests/test_living_review_pipeline.py` passed all 90
  tests.
- `python3 scripts/run_living_review_pipeline.py doctor` reported `healthy:
  true`, a published cursor through 2026-08-09, and the 55-record/109-model/
  586-route atlas.
- A clean Git checkout initially invalidated stages whose complete PDF,
  Docling, Graph, and image payloads are intentionally excluded by repository
  policy. The release gate now uses explicit `doctor --repository-checkout`
  semantics: only untracked, ignored files whose path, byte count, and SHA-256
  agree in both the stage inventory and committed run-level artifact ledger may
  be absent. The complete local archive remains subject to strict `doctor`.

## Scope boundary

This reconciliation preserves all branch content and makes one canonical Git
history. It does not by itself resolve the registry, generated-Methods,
cross-version route-drift, semantic evidence-sufficiency, or crop-validation
findings recorded in
`analysis/taxonomy_agent_trace_audit_2026-08-14.md`. Those findings remain
explicit follow-up work rather than being hidden by the merge.
