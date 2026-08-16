# Living Review Runbook Blind-Agent Audit

## Purpose

This audit tests whether an unfamiliar agent can reconstruct the next routine
living-review iteration from repository instructions alone. It evaluates
operator-document interpretability; it does not execute or validate the
scientific pipeline.

## Design

- Date: 2026-08-16 (`Europe/Kiev`).
- Primary instruction: `protocol/LIVING_REVIEW_RUNBOOK.md`.
- Evaluators: three independent explorer agents with no forked conversation
  context.
- Agent IDs: `01a00a97-7615-77f1-b3cc-b5a1107ab29e`,
  `01a00a97-767f-7fd0-a121-1b4ba1c50e84`, and
  `01a00a97-7707-7980-802d-769d399f8c21`.
- Identical prompt: `experiment_prompt.md`.
- Permitted work: read-only inspection of the runbook and explicitly referenced
  static files.
- Prohibited work: pipeline/network/LLM/server execution and every filesystem or
  Git write.

The complete explicit first-pass responses are preserved as `agent_volta.md`,
`agent_dalton.md`, and `agent_laplace.md`. After the first corrections, the same
prompt was sent to three new blind agents: Kierkegaard
(`01a00aae-6d6b-72b1-9794-daa36c880257`), Godel
(`01a00aae-6e63-73e3-b7ec-22c414e5206a`), and Meitner
(`01a00aae-6dd9-76b0-b618-76885faedaf5`). Their explicit responses are the
`postfix_agent_*.md` files. These logs contain only user-visible agent messages
recovered from the local session log; hidden chain-of-thought is neither
available nor claimed.

A final single-agent pass used the unchanged prompt after the second corrections:
Averroes (`01a00aba-6836-7642-b94f-070dd25299f7`), preserved as
`final_agent_averroes.md`. A prior Euclid attempt was stopped before completion
because a locked file changed while it was reading; it is excluded from the
audit denominator.

## Orientation Result

All three agents independently recovered:

- published cursor `2026-08-09`;
- next interval `2026-08-10` through `2026-08-15`, excluding the unfinished
  local day;
- run ID `update_2026-08-15`;
- the ordered 18-stage state machine and manual gates;
- the abstract and selected-section reviewer/adjudicator topology;
- no-VLM Docling screening, Graph section grounding, VLM canonical profiles,
  frozen-taxonomy classification, crop validation, cumulative snapshot, atlas,
  archive, deployment, and completion sequence;
- the rule that expensive Docling/Graph artifacts may be reused only under
  matching identity, hash, and locked-contract conditions.

| Criterion | Volta | Dalton | Laplace |
|---|---:|---:|---:|
| Cursor and inclusive interval | pass | pass | pass |
| Ordered 18-stage path | pass | pass | pass |
| Manual gates and recovery | pass | pass | pass |
| Screening roles and modes | pass | pass | pass |
| Docling/Graph retention and reuse | pass | pass | pass |
| Frozen taxonomy and agreement gates | pass | pass | pass |
| Publication, deployment, and completion | pass | pass | pass |

## Independent Findings

The agents converged on the following material gaps in the pre-audit runbook and
implementation:

1. The method lock covered the legacy abstract runner but omitted the
   selected-section runner and its prompt files.
2. “Exactly title + abstract” described scientific evidence but not the complete
   model-visible transport JSON. The same ambiguity affected selected-section
   screening and omitted adjudicator `first_pass_outputs`.
3. Selected-section prompt templates request legacy `evidence_for_*` and
   `boundary_case` fields that the strict runner schema does not accept.
4. Archive creation occurs before `publish`, but `publish` mutates the run
   manifest. Rebuilding the artifact ledger afterward would detach it from the
   verified receipt.
5. The implemented completion record did not explicitly bind the method lock,
   independent archive, PRISMA facts, and catalog counts promised by the runbook.
6. The runbook lacked executable commands for restored-profile validation and
   remote interactive browser QA.
7. The historical `update_2026-08-09` run has no completion record and only
   `local_secondary` receipts because it predates the new release contract.

## Disposition

- Findings 1, 2, 4, 5, and 6 were corrected in the method lock, runbook, runner,
  restore validator, and tests produced from this audit.
- Finding 3 is frozen and disclosed as a method-v1 known issue. Changing prompts
  or schema during a routine update is prohibited; it requires a new method
  version and bridge analysis.
- Finding 7 remains a declared legacy exception. No retrospective completion
  record will be fabricated.
- Independent off-device/cloud storage, automated late-indexing lookback, and a
  multi-operator lease remain operational limitations rather than undocumented
  assumptions.

## Post-Fix Rerun

All three new agents again recovered the correct cursor, inclusive interval,
18-stage order, model roles, Docling/Graph modes, frozen-taxonomy gates, archive,
and publication sequence. Their deeper static traces found additional boundary
defects:

1. the legacy abstract runner generated positional IDs but the orchestrator did
   not create the crosswalk required by `fulltext-candidates`;
2. `fulltext-candidates` always passed a post-screen duplicate declaration path
   even when no such optional declaration existed;
3. the abstract prompt/schema conflict was not disclosed alongside the known
   selected-section conflict;
4. a new run could default to the unfinished current date if `--date-to` was
   omitted;
5. the runbook used an imprecise search-summary path and did not stage the archive
   receipt, bind the Pages workflow ID to the commit, or safely publish from a
   non-`main` worktree;
6. the generated report did not itself disclose the absent late-indexing
   lookback.

These defects were corrected with a deterministic stable-ID crosswalk, optional
hash-fingerprinted duplicate declarations, explicit end-date enforcement,
machine-readable denominator/report fields, and commit-bound publication
commands. One agent claimed that the full-text input builder omitted
`doi/year/venue/sources`; direct inspection rejected that claim because
`make_record()` explicitly carries all four fields.

The remaining prompt/schema mismatch is intentionally not repaired in v1. The
independent storage mount, operator identity, lawful manual-PDF access, and live
provider/GitHub credentials are runtime resources that preflight must verify, not
values that should be hard-coded in the repository.

## Final Single-Agent Pass

Averroes recovered the crosswalk, optional duplicate contract, explicit date
boundary, full screening payloads, all 18 stages, archive/restore flow, and
commit-bound Pages verification without any scientific-pipeline blocker. It
identified three remaining release/recovery edge cases, which were then closed:

- zero-accepted updates now explicitly dispatch the Pages workflow when the atlas
  path filter would otherwise produce no commit-bound deployment;
- restore validation derives the accepted-record denominator from the restored
  tree, not the possibly lost original root;
- rollback commits are promoted to `main` and explicitly dispatched when the
  restored atlas is byte-identical.

The generic Scholar provider wording was also narrowed: comparable method-v1
runs use the now hash-locked SerpAPI capture; another provider requires a
versioned method change. Remaining items in the final response are genuine
runtime prerequisites or declared limitations, not missing pipeline steps.

## Conclusion

The runbook now provides strong initial orientation: seven of seven completed
blind agents derived the same next cohort and complete pipeline topology across
three phases.
The audit was still useful because agreement on the broad path exposed precise
contract and release gaps that prose review alone had not eliminated. A future
audit should reuse the same prompt after any method-version or publication-
protocol change.
