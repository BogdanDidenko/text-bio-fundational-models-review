# Living Review Runbook Blind-Agent Audit

## Audit identity

- Date: 2026-08-18 (Europe/Kiev).
- Repository commit: `00fe463851924dcd4ba43d6f43f42b0e916d8faf`.
- Runbook SHA-256: `13755e97268928dd00b265b2c8f1fe886aae7a1e5843678cf51a36f1cd65eeab`.
- Runner SHA-256: `f99c74e8f8984f94948c488edff2d81f7717b9a0d0319566c85da4ac0f5b6c5b`.
- Method: three independent explorer agents, identical prompt, no forked
  conversation context, read-only inspection, and no pipeline/network/LLM/
  Docling/build/deployment execution.
- Agents: Singer (`01a01243-0188-7ec3-9636-c6cfd5f2489d`), Peirce (`01a01243-01ef-7f52-b3d7-37fc9eca3f5d`), and
  Archimedes (`01a01243-0276-76b2-9c5f-68e652b8ec1d`).

The files `agent_singer.md`, `agent_peirce.md`, and
`agent_archimedes.md` preserve complete user-visible agent responses. Hidden
chain-of-thought is neither available nor claimed.

## Orientation result

All three independently derived the same correct next routine update:

- canonical checkout:
  `/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review`;
- published cursor: `2026-08-09`;
- inclusive interval: `2026-08-10..2026-08-17`;
- run ID: `update_2026-08-17`;
- first operation: export the repository/artifact roots, enter the canonical
  checkout, inspect Git state, and run `doctor`;
- the same 18-stage state machine;
- the same declared manual inputs and resume discipline;
- F6 and F7 as blocking in-run gates before snapshot creation;
- archive, local publication freeze, commit-bound Pages verification, browser
  QA, and the schema-v2 completion record;
- hash-conditioned preservation and reuse of expensive Docling and Graph
  artifacts.

| Criterion | Singer | Peirce | Archimedes |
|---|---:|---:|---:|
| Correct cursor, interval, and run ID | pass | pass | pass |
| Canonical checkout and artifact-root split | pass | pass | pass |
| Ordered 18-stage trajectory | pass | pass | pass |
| Manual gates and safe resume | pass | pass | pass |
| F6/F7 placement and blocking behavior | pass | pass | pass |
| Docling/Graph preservation and reuse | pass | pass | pass |
| Archive, publish, Pages, completion | pass | pass | pass |
| Fully executable conditional recovery | fail | fail | fail |
| Agent verdict | FAIL | PASS WITH RISKS | PASS WITH RISKS |

## Validated findings

Static inspection after the agent run confirmed these implementation or
operator-contract gaps.

1. **F6 routine correction re-entry is missing.** The routine runner raises a
   manual gate for a non-empty semantic action queue. The runbook documents
   standalone correction commands in the whole-cohort rerun section, but does
   not define how a corrected taxonomy becomes the routine run's authoritative
   taxonomy output, stage inventory, downstream crop input, and snapshot input.
   Resuming the stage recomputes the original classification rather than adopting
   a declared correction.

2. **F7 persistent resolution is underspecified.** The runner performs the full
   exact-preview and replacement sequence and blocks when unresolved models
   remain. A technical retry is supported, but there is no versioned declaration
   or targeted command for a scientifically persistent unresolved result. Manual
   crop-ledger edits are correctly prohibited.

3. **Completion search timestamp uses the wrong field.** Completed stages store
   `finished`; schema-v2 completion creation reads `stages.search.ended`.
   Consequently `search_completed_at` would be null. The existing unit test
   constructs an `ended` field and therefore does not detect the mismatch.

4. **Pre-run Scholar recovery lacks a manifest boundary.** `plan`,
   `scholar-capture`, and `scholar-validate` can create search files before a
   run manifest is saved. If capture fails in that interval,
   `doctor --run-id update_2026-08-17` can fall back to the prior published run
   rather than report the incomplete proposed run.

5. **The restore example bypasses migration-aware runtime resolution.** It calls
   `.venv-docling/bin/python` directly from the canonical checkout, where that
   path is absent on the current machine. Normal runner execution correctly
   resolves the Docling interpreter through the external artifact root.

The absent independent-backup mount, non-transactional local/remote publication,
late-indexing lookback, and lack of a multi-operator lock are already explicit
runtime or engineering limitations. They are not newly discovered silent
method changes.

## Verdict

The revised runbook now gives unfamiliar agents a consistent and correct happy
path: orientation and normal trajectory pass **3/3**. It still does not support
a fully autonomous comparable iteration across all allowed outcomes. The common
F6/F7 recovery gap and the completion timestamp defect are sufficient to prevent
an unconditional pass.

Overall verdict: **PASS WITH RISKS for the healthy path; FAIL for complete
outcome-independent operation.**

No scientific pipeline command was executed and no canonical artifact was
modified during this audit.
