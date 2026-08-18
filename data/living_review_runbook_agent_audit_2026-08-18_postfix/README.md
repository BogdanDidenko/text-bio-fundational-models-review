# Living Review Runbook Blind-Agent Audit After Recovery Fixes

## Audit identity

- Date: 2026-08-18 (Europe/Kyiv).
- Audited repository commit: `d5f03afa8d53e812aea023c3a6f79f11ded95326`.
- Runbook SHA-256: `c6dc9753e9843cbb88d355c92766c04110bd665e6547d9a4bed5afafcab8c43f`.
- Runner SHA-256: `fd4f45736ddb281e2e8215ceb1950289d478aded22031825678aab37793f9990`.
- Method-lock SHA-256: `718bb59eded9858c7a150ee554d768103207787ab0ab0b62546332c778d945e4`.
- Method: three independent explorer agents, identical prompt, no forked
  conversation context, read-only inspection, and no pipeline, network, LLM,
  Docling, build, Git-write, or deployment execution.
- Agents: Confucius (`01a0125c-f024-7ac0-9634-42f92a178c92`), Kepler
  (`01a0125c-f08f-74a1-9c4e-531fd6944163`), and Rawls
  (`01a0125c-f107-7641-9f28-7d9bce4d301b`).

`agent_confucius.md`, `agent_kepler.md`, and `agent_rawls.md` preserve the
complete user-visible responses. Hidden chain-of-thought is neither available
nor claimed.

## Result

All three agents independently derived the same routine update:

- canonical checkout:
  `/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review`;
- external artifact root: `/Users/bogdan.didenko/lpnu/review`;
- published cursor: `2026-08-09`;
- inclusive interval: `2026-08-10..2026-08-17`;
- run ID: `update_2026-08-17`;
- analysis mode: `incremental_frozen_taxonomy` under taxonomy v1;
- the same ordered 18-stage state machine;
- the same manual declarations and doctor-directed resume discipline;
- pre-publication independent archive, local publication freeze, exact-commit
  GitHub Pages verification, remote browser QA, and schema-v2 completion record.

| Criterion | Confucius | Kepler | Rawls |
|---|---:|---:|---:|
| Correct cursor, interval, and run ID | pass | pass | pass |
| Canonical checkout and artifact-root split | pass | pass | pass |
| Ordered 18-stage trajectory | pass | pass | pass |
| Manual gates and first-blocking-stage resume | pass | pass | pass |
| Automatic F6 correction and complete-document revalidation | pass | pass | pass |
| Authoritative taxonomy used by downstream stages | pass | pass | pass |
| F7 exhaustive validation and conservative omission | pass | pass | pass |
| Expensive Docling/Graph/agent artifact preservation | pass | pass | pass |
| Archive, publish, Pages, QA, and completion trajectory | pass | pass | pass |
| Agent verdict | PASS WITH RISKS | PASS WITH RISKS | PASS WITH RISKS |

## Previously identified defects

The five concrete defects from the preceding audit are closed.

1. **F6 routine re-entry:** the routine runner now materializes one versioned
   semantic correction, reruns all complete-document F6 roles, and writes
   `12_taxonomy/authoritative_taxonomy.json`. Crop selection, snapshot merge,
   and report metrics resolve that marker. A second non-empty queue stops at the
   declared whole-cohort bridge.
2. **F7 persistent resolution:** exhaustive semantic failures are converted to
   `crop_rejected_no_suitable_figure`; coordinates and claimed routes are
   cleared while `preterminal_status` and the terminal rationale remain logged.
3. **Completion timestamp:** schema-v2 completion reads the stage's actual
   `finished` field, with legacy `ended` fallback.
4. **Scholar manifest boundary:** `scholar-capture` and `scholar-validate`
   persist the proposed run manifest before creating or validating run-scoped
   search artifacts.
5. **Migrated Docling runtime:** restore instructions resolve the configured
   Docling interpreter from the canonical checkout or external artifact root
   instead of assuming a checkout-local `.venv-docling`.

The implementation was also checked by 116 local unit/contract tests, the
method-lock verifier (53 files and 20 configured parameters), and the GitHub
Actions `Living review contract` workflow for commit `d5f03afa`.

## Residual risks

The common residual findings no longer prevent an unfamiliar agent from
following the normal routine trajectory, but they remain relevant limitations:

- publication providers and hosted model aliases can change behind stable
  names; no retrospective late-indexing lookback currently exists;
- manual evidence judgments, operator identity, and the physical independent
  backup destination necessarily require accountable operator input;
- local `publish` and remote Pages deployment are operationally frozen between
  steps but are not one transaction;
- there is no multi-operator filesystem lock;
- exceptional whole-cohort and cross-machine recovery sections still contain
  installation-specific placeholders or historical denominators;
- a restore to an arbitrary external directory cannot be discovered by
  `doctor --run-id` unless it is restored into the configured update root;
- initial F6 review roles rely on read-only Codex execution and prompt-level
  tool prohibition, whereas the correction and F7 paths additionally enforce a
  machine-audited zero evidence-bearing tool-event rule;
- exact day selection is documented but remains operator-supplied.

These are engineering, external-validity, or exceptional-recovery limitations.
They are not evidence that the routine path silently changes the scientific
method.

## Comparison with the preceding audit

The preceding audit produced one `FAIL` and two `PASS WITH RISKS` verdicts and
found a shared inability to complete F6/F7 recovery. This audit produced three
`PASS WITH RISKS` verdicts. All agents correctly explained the new F6
correction/revalidation path and F7 terminal omission without inventing a manual
route edit or an unsupported crop.

Overall verdict: **PASS WITH RISKS for the documented routine update path.**

No scientific pipeline command was executed and no canonical scientific
artifact was modified during this audit.
