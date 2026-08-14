# Operator Simulation Audit of the Living Review Runbook

**Date:** 2026-08-12
**Method:** three independent read-only agent simulations. Agents were given
the complete runbook in their prompt, told to write intended commands, and
prohibited from executing tools, commands, network calls, or file changes.

## Roles

1. New research engineer with no repository history.
2. Incident-response engineer stress-testing partial failures and recovery.
3. Systematic-review reproducibility auditor emphasizing PRISMA-S and frozen
   computational annotation.

## Behavioral result

All three reconstructed the same happy path:

`doctor -> plan -> preflight -> run -> doctor/gate resolution -> publish`

All three then stopped before Git publication because they could not derive a
safe staging allowlist, preferred deployment branch, workflow-monitoring
command, or rollback procedure. None was willing to use `git add .`. This is
the strongest evidence that the original document was a maintainer reminder,
not a self-sufficient operator runbook.

All three independently identified the same highest-severity ambiguity:
`publish` advances local `current.json` before GitHub Pages deployment. If the
deployment fails and another run is planned, the cursor can move ahead of the
public catalog. The implementation has local atomic rollback, but not a
two-phase local/remote publication transaction.

## Consensus gaps

| Gap | Agents identifying it | Assessment |
|---|---:|---|
| No exact environment/bootstrap and clean-tree procedure | 3/3 | Valid. Added. |
| Date inclusivity, same-day cutoff, and late indexing unspecified | 3/3 | Valid. Added; late lookback remains open. |
| Run-ID collision, resume, `--force`, and invalidation unclear | 3/3 | Valid. Added. |
| Manual schemas/evidence requirements missing | 3/3 | Valid. Added with examples. |
| Per-stage success and recovery contracts absent | 3/3 | Valid. Added for all 18 stages. |
| Frozen model/prompt/schema behavior not visible in runbook | 3/3 | Valid, although detailed protocol already contained it. Added concise mapping. |
| Git allowlist, branch, workflow monitoring, and rollback missing | 3/3 | Valid. Added. |
| Supplemental reconciliation not executable from runbook | 3/3 | Valid. Added worked syntax. |
| UI acceptance did not cover assets or interaction | 3/3 | Valid. Added. |
| No local/remote two-phase publication | 3/3 | Valid implementation gap; documented, not solved by prose. |

## Agent assumptions checked against code

- Agents worried that completed stage data might be overwritten on retry. The
  runner inventories stage files, uses append-only attempt directories, and
  invalidates downstream state. Full-text retrieval additionally reuses valid
  prior payloads. The original runbook did not state these guarantees.
- Agents worried that `verify-live` might compare counts only. That was valid at
  the time of the first simulation. The implementation now checks six semantic
  fields, exact `atlas.json` bytes, deployed commit identity, the complete atlas
  tree hash, and every remote static-asset hash.
- Agents asked whether failed sources could publish. Search completeness is a
  hard gate: every enabled source must complete. The runbook now says this
  explicitly.
- Agents assumed human dual review might be required. That is not the executed
  method. Manual resolutions retain resolver/evidence but must not be reported
  as independent human validation.
- Agents identified concurrent publication as unsafe. `publish` rejects a
  changed prior living state, but the broader run has no multi-operator lock.

## Verdict

The original 96-line runbook was insufficient. It enabled an experienced
maintainer to remember the top-level commands but did not let an unfamiliar
operator recover safely or prove publication completeness. The revised runbook
is a stage-by-stage operational contract and explicitly labels the remaining
engineering gaps instead of claiming that documentation alone resolves them.

## Second simulation after revision

The same experiment was repeated with three fresh agents and the revised
436-line runbook. The roles and no-execution constraint were unchanged. Each
agent additionally scored onboarding, happy path, manual gates, incident
recovery, reproducibility, publication/deployment, and overall autonomy.

### Behavioral comparison

| Observable behavior | Original | Revised |
|---|---:|---:|
| Chose the last fully elapsed day (`2026-08-11`) rather than the unfinished current day | 0/3 | 3/3 |
| Derived the exact interval `2026-08-10..2026-08-11` | 0/3 | 3/3 |
| Reached Git commit, workflow monitoring, remote byte verification, and UI QA | 0/3 | 3/3 |
| Supplied the correct files and evidence fields for all five manual gates | 0/3 | 3/3 |
| Correctly avoided routine `--force` and used doctor-directed restart boundaries | 3/3 conceptually | 3/3 with exact commands |
| Distinguished documentation gaps from explicitly declared implementation limitations | 0/3 | 3/3 |
| Could complete every requested incident without inventing an interface | 0/3 | 0/3 |

The revised-run scores were:

| Role | Onboarding | Happy path | Manual gates | Incident recovery | Reproducibility | Publication | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|
| New engineer | 3.0 | 4.0 | 4.0 | 4.0 | 4.0 | 3.0 | 3.0 |
| Incident response | 4.0 | 4.5 | 4.0 | 3.0 | 4.5 | 3.5 | 3.5 |
| Reproducibility audit | 3.0 | 4.0 | 3.0 | 3.0 | 4.0 | 3.0 | 3.0 |
| **Mean** | **3.33** | **4.17** | **3.67** | **3.33** | **4.17** | **3.17** | **3.17** |

### Remaining consensus blockers

All three could now complete the normal path, but all three still refused to
claim unconditional autonomy. Their recurring blockers were:

1. The runbook references the Scholar provider schema but does not include the
   exact capture/validation command.
2. It describes evidence-backed terminal non-retrieval but does not identify
   the generated disposition artifact and clarify that an operator must not
   manufacture it.
3. It states that a failed taxonomy schema/prompt threshold requires a complete
   cohort rerun, but the living orchestrator has no exact whole-corpus rerun
   command.
4. It documents `reconcile`, but not a first-class command that processes a
   supplemental record through the preceding stages.
5. It gives the rollback policy but not an exact guarded GitHub workflow rerun
   and same-commit rollback sequence.
6. It does not define a durable completion/incident record path for commit SHA,
   workflow ID, screenshots, and remote verification evidence.

### Second-round verdict

Orientation improved substantially: agents no longer guessed the date, gate
schemas, restart boundary, Git staging scope, or remote acceptance sequence.
The document now supports supervised operation and a complete healthy-path run.
It still does not support fully autonomous incident recovery. The remaining
stops are mostly missing interfaces or cross-system transaction guarantees,
not requests for more narrative explanation.

## Implementation closure

The six second-round blockers were converted into executable interfaces and
versioned contracts:

| Former blocker | Implemented component |
|---|---|
| Scholar capture/validation was implicit | First-class `scholar-capture` and `scholar-validate` commands with signed query and raw-page validation. |
| Terminal full-text outcomes were ambiguous | Stage-owned `fulltext_retrieval_dispositions.json` plus a versioned status contract and explicit retrieved-only Docling cohort. |
| Whole-cohort taxonomy rerun was not executable | `taxonomy-rerun-preflight` inventories all current profiles and writes the baseline regeneration plus complete repeated-classification command sequence. |
| Supplemental recall bypassed the ordinary path | `register-supplemental` declares and hashes records before cumulative deduplication, then invalidates all downstream stages. |
| Deployment verification lacked release identity | Pages creates a commit-bound tree manifest; `verify-live --expected-commit --check-assets` verifies every deployed byte. |
| Completion and incidents had no durable location | Immutable completion records and append-only incidents live under `data/living_catalog/releases/<run_id>/`. |

Additional boundary testing found and corrected two issues not named explicitly
by the agents. New absent optional inputs are backward compatible with older
stage fingerprints, while any actual new file still invalidates the stage. Also,
terminal not-retrieved reports remain in the PRISMA denominator but no longer
enter Docling or eligibility as if a source document existed.

Verification on 2026-08-12: 88 repository tests passed; Python compilation,
Markdown-fence checks, and `git diff --check` passed; `doctor` was healthy;
search preflight was ready; and the published Scholar bundle revalidated as 252
normalized records over 13 hashed raw pages. The complete 55-record taxonomy
rerun is prepared but intentionally blocked until 52 recovered baseline PDFs
are regenerated into native VLM Docling profiles. The readiness ledger records
28 exact historical PDFs and 24 valid version/hash-different sources.
