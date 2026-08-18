**Resolved Run**
Read-only inspection found:

- Published cursor: `search_end = 2026-08-09`
- Current taxonomy and local atlas both point to `data/living_catalog/taxonomy_rerun_preflight_2026-08-12/snapshot_full_55_semantic_correction_2026-08-17`
- Latest run: published legacy `update_2026-08-09`
- No `update_2026-08-17/run_manifest.json` exists
- Local date: `2026-08-18`; last fully elapsed Kyiv day: `2026-08-17`

Therefore:

```text
mode      = routine incremental update
date_from = 2026-08-10
date_to   = 2026-08-17
run_id    = update_2026-08-17
taxonomy  = incremental_frozen_taxonomy, taxonomy v1
```

This follows the [runbook](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/protocol/LIVING_REVIEW_RUNBOOK.md) and [current state](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/data/living_catalog/current.json).

**Command Trajectory**
Nothing below was executed.

```bash
export REVIEW_REPO_ROOT="${REVIEW_REPO_ROOT:-/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review}"
export REVIEW_ARTIFACT_ROOT="${REVIEW_ARTIFACT_ROOT:-/Users/bogdan.didenko/lpnu/review}"
export TZ=Europe/Kyiv
cd "$REVIEW_REPO_ROOT"
test "$(git rev-parse --show-toplevel)" = "$REVIEW_REPO_ROOT"
git status --short --branch
git branch --show-current
git log -1 --format='%H %cI %s'
python3 --version
python3 scripts/run_living_review_pipeline.py doctor
jq . data/living_catalog/current.json
jq . data/living_catalog_updates/update_2026-08-09/run_manifest.json
python3 scripts/verify_living_review_method_lock.py --current-taxonomy-tree "$(jq -r .taxonomy_root data/living_catalog/current.json)/taxonomy_tree.json"

END=2026-08-17
RUN_ID=update_${END}
python3 scripts/run_living_review_pipeline.py plan --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-capture --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate --date-to "$END"
python3 scripts/run_living_review_pipeline.py preflight --date-to "$END" --through-stage report
jq . "data/living_catalog_updates/${RUN_ID}/run_manifest.json"

python3 scripts/run_living_review_pipeline.py run --date-to "$END" --manage-server
# Internal order:
# search, deduplicate, prepare-records, enrich-abstracts, abstract-screening,
# fulltext-candidates, fulltext-download, docling-screening, graph-sections,
# fulltext-screening, eligibility-resolution, docling-vlm,
# taxonomy-discovery, taxonomy-classification, crop-validation,
# snapshot, atlas, report.

# After any stop, failure, timeout, or manual gate:
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py run --run-id "$RUN_ID" --from-stage STAGE --manage-server
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"

RUN_ROOT="data/living_catalog_updates/${RUN_ID}"
ARCHIVE_ROOT="/Volumes/INDEPENDENT_BACKUP/text-bio-living-review"
python3 scripts/docling/build_input_taxonomy_artifact_manifest.py --artifact-root "$RUN_ROOT"
python3 scripts/archive_living_review_artifacts.py create --source-root "$RUN_ROOT" --archive-root "$ARCHIVE_ROOT" --receipt-dir data/living_catalog/archives --label "$RUN_ID" --storage-class independent_backup
RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"

python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"
git diff --check
python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor

git status --short
git diff --check
git add data/living_catalog/current.json "data/living_catalog_updates/${RUN_ID}" "$RECEIPT"
git add docs/input-representation-atlas
git add protocol/PRISMA_protocol.md protocol/prisma_search_screening_log_2026-07-07.md
git status --short
git diff --cached --check
git diff --cached --stat
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID" --repository-checkout
git commit -m "Update living review through ${END}"

COMMIT=$(git rev-parse HEAD)
git fetch origin main
git merge-base --is-ancestor origin/main "$COMMIT"
git push origin HEAD:main
if ! git diff-tree --no-commit-id --name-only -r "$COMMIT" | rg -q '^docs/input-representation-atlas/'; then gh workflow run deploy-input-representation-atlas.yml --ref main; fi
GITHUB_RUN_ID=""
for attempt in 1 2 3 4 5 6; do GITHUB_RUN_ID="$(gh run list --workflow deploy-input-representation-atlas.yml --branch main --limit 10 --json databaseId,headSha --jq ".[] | select(.headSha == \"$COMMIT\") | .databaseId" | head -1)"; test -n "$GITHUB_RUN_ID" && break; sleep $((attempt * 5)); done
test -n "$GITHUB_RUN_ID"
gh run watch "$GITHUB_RUN_ID" --exit-status
python3 scripts/run_living_review_pipeline.py verify-live --expected-commit "$COMMIT" --check-assets

RELEASE_ROOT="data/living_catalog/releases/${RUN_ID}"
REMOTE_QA="${RELEASE_ROOT}/remote_browser_qa.json"
NODE_PATH="${NODE_PATH:-$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules}" node scripts/qa_input_representation_atlas.mjs https://bogdandidenko.github.io/text-bio-fundational-models-review/ "$REMOTE_QA"
python3 scripts/run_living_review_pipeline.py doctor

python3 scripts/run_living_review_pipeline.py verify-live --run-id "$RUN_ID" --expected-commit "$COMMIT" --check-assets --record-completion --workflow-run-id "$GITHUB_RUN_ID" --operator "OPERATOR" --browser-qa-report "$REMOTE_QA" --screenshot /tmp/atlas-graph-desktop.png --screenshot /tmp/atlas-graph-mobile.png
git add "data/living_catalog/releases/${RUN_ID}/completion_record.json"
git diff --cached --check
git commit -m "Record verified release evidence for ${RUN_ID}"
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
git push origin HEAD:main
```

Manual-gate substitutions for `STAGE` are determined by `doctor`, never guessed:

| Gate | Declaration | Expected resume |
|---|---|---|
| Scholar | `00_search/google_scholar_provider_export.json` | `search`, after `scholar-capture` and `scholar-validate` |
| Cumulative duplicate | `02_records/manual_cross_dedup_resolutions.json` | `prepare-records` |
| Post-screen duplicate | `05_fulltext/postscreen_dedup/duplicate_resolutions.json` | `fulltext-candidates` |
| Manual main article | `05_fulltext/manual_fulltexts.json` | `fulltext-download` |
| Section override | `08_section_input/manual_section_overrides.json` | doctor-reported blocking stage, normally `graph-sections` |
| Eligibility | `10_eligibility/manual_resolution.csv` | `eligibility-resolution` |

**Stage Contracts**

| Stage | Accepted input | Success and downstream product | Supported recovery |
|---|---|---|---|
| `search` | Dated config, credentials, validated Scholar bundle | All eight sources and pagination complete; exports plus `search_summary_2026-08-17.json` | Restore access/capture; resume `search` |
| `deduplicate` | Eight completed exports | Counts reconcile; clusters and merge ledger | Repair invalid export or resume reported stage |
| `prepare-records` | Update clusters, every published master, Crossref audit | All cumulative comparisons complete; new-record cohort | Fill generated cross-dedup declaration |
| `enrich-abstracts` | New-record cohort | Every missing abstract attempted; corroborated fallbacks only | Resume unchanged provider routes |
| `abstract-screening` | Locked title/abstract transport | One final structured result per record | Retry incomplete frozen batches |
| `fulltext-candidates` | INCLUDE/UNCERTAIN results, crosswalk, optional duplicate declaration | Raw and adjusted candidate denominators reconcile | Correct identity/declaration and resume |
| `fulltext-download` | Candidate metadata and lawful manual declarations | Exactly one validated payload, terminal non-retrieval, or blocking disposition per candidate | Retry providers or declare lawful main article |
| `docling-screening` | Validated PDF/HTML payloads | One complete identity-corroborated no-VLM profile per retrieved candidate | Replace invalid source or rerun Docling |
| `graph-sections` | No-VLM profiles and optional heading overrides | Grounded, complete heading-bounded sections for both targets | Supply canonical heading selectors |
| `fulltext-screening` | Title, abstract, selected sections | Final structured decision for every candidate | Retry unchanged batches or resolve sections |
| `eligibility-resolution` | Full-text results and manual CSV | `accepted + excluded`, with zero unresolved | Add declared evidence-based resolution |
| `docling-vlm` | Accepted main-article PDFs | Complete fresh VLM profiles, figures, captions and descriptions | Obtain valid PDF; rerun from download |
| `taxonomy-discovery` | Complete VLM profiles | Open route inventory and study/model registry | Retry unchanged failed document batches |
| `taxonomy-classification` | Inventory, profiles, taxonomy v1 | Thresholds pass, routes grounded, F6 passes, authoritative root declared | One automatic F6 correction; otherwise whole-cohort rerun |
| `crop-validation` | Authoritative routes and native figures | One reviewed crop or `no_suitable_figure` per model; zero unresolved | Retry technical batches; terminalize exhaustive semantic failures |
| `snapshot` | Prior snapshot plus accepted routes/evidence/crops | Counts and IDs reconcile in immutable cumulative snapshot | Repair earliest invalid upstream stage |
| `atlas` | Snapshot, all VLM corpus roots, prior UI shell | Build report and desktop/mobile browser QA pass | Rebuild atlas and rerun QA |
| `report` | All stage summaries and dispositions | Reconciled PRISMA facts and update report | Fix source/generator, never hand-edit counts |

**F6 And F7**
F6 runs two complete-document semantic reviewers, comparison, adjudication, and finalization. Any non-retain row enters one separate versioned correction root; the runner applies the correction, reruns the complete F6 sequence without document truncation, and writes `12_taxonomy/authoritative_taxonomy.json`. A second non-empty queue stops the update and requires `taxonomy-rerun-preflight`; routes cannot be silently deleted.

F7 reviews exact published pixels and exact-model input role, then re-reviews adjusted crops and performs exhaustive native-figure replacement rounds. A persistent semantic failure becomes `crop_rejected_no_suitable_figure`: coordinates and supported route IDs are cleared, while `preterminal_status`, responses, hashes, and attempts remain. Only zero-unresolved `proposed_crossvalidated_crop_ledger.json` can reach the snapshot.

**Artifact Survival**
Before expensive recomputation, existing Docling, Graph, taxonomy and adjudication outputs move to `preserved_stage_outputs/<stage>/attempt_NNN/`; `preservation_ledger.jsonl` records paths, counts, bytes and time. Reuse requires matching source/profile hashes and the same locked contract.

After all 18 stages, the complete run root is inventoried and archived as a verified `.tar.zst` on independent storage. It includes PDFs/HTML, both Docling profile types, native JSON/Markdown/figures, every Graph workspace, VLM descriptions, taxonomy-agent and crop-agent prompts/responses/retries, snapshots and logs. Restore is only into an empty directory using `archive_living_review_artifacts.py restore`; then verify the receipt, validate `11_docling_vlm/profiles/manifests/canonical_docling_profile_manifest.csv`, and run `doctor`. Immutable provenance paths remain unchanged after migration and are resolved through declared artifact roots. Recompute only if bytes are missing or fail hash/identity contracts.

**Runbook Risks**
1. `END` is manually assigned; no executable last-fully-elapsed-day calculation or timezone assertion is provided. `Europe/Kiev` versus `Europe/Kyiv` is also inconsistent.
2. Actual health cannot be established in this silent experiment because `doctor` and preflight were prohibited.
3. `OPERATOR`, independent backup ownership, `LAST_GOOD_COMMIT`, copied archive paths, and sibling-route adjudicators remain operator-selected.
4. Manual declaration files have schemas but no exact creation/validation command; decisions are not automatically dual-reviewed.
5. The F6 sibling-route instruction says to run grouped adjudication “here” but omits a future-cohort command and arguments.
6. The whole-cohort preflight writes `commands.sh`, but the runbook does not state exactly how it is reviewed and invoked.
7. Targeted post-correction F7 reruns describe a target manifest but omit its construction command.
8. Restore instructions do not show how `doctor` is pointed at a restored run outside the canonical `updates_root`.
9. `CORPUS_ROOT_1`, `CORPUS_ROOT_2`, archive-copy paths and screenshot generation remain placeholders.
10. The archive section says to commit the receipt before publication, while the Git section commits it with the post-`publish` state.
11. The Git command hard-codes `protocol/prisma_search_screening_log_2026-07-07.md`, which may omit a future dated log.
12. `git add data/living_catalog_updates/${RUN_ID}` is broad and relies on manual secret/licensed-content inspection.
13. Local `publish` advances `current.json` before GitHub Pages succeeds; recovery is operational rather than transactional.
14. No multi-operator lock exists, and no automated late-indexing lookback covers already closed intervals.
15. Frozen model names are mutable service aliases rather than immutable provider model revisions; temperature is explicit only for taxonomy.
16. Known prompt/schema contradictions can change retry behavior while remaining frozen under v1.
17. Historical current corpora have only declared `local_secondary` archives; the next run must create its own independent archive, but baseline device-loss exposure remains.
18. Manual full-text authorization and section/eligibility judgments preserve provenance but can still vary between operators.

**Verdict: PASS WITH RISKS**

The normal routine path, stage boundaries, recovery semantics, F6/F7 behavior, immutable archiving, publication verification, and completion record are substantially executable and auditable. The main risks are conditional recovery commands, operator-dependent gates, mutable hosted models, incomplete migration ergonomics, and the non-transactional local-to-remote publication boundary.
