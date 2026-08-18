I performed read-only inspection only. I did not execute the runner, providers, models, Docling, builds, Git writes, or deployment.

**Interval**
Stored `search_end` is `2026-08-09` in [current.json](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/data/living_catalog/current.json). With 2026-08-18 as the current Europe/Kiev date, the last fully elapsed day is 2026-08-17.

- Interval: **2026-08-10 through 2026-08-17**, inclusive
- Run ID: **`update_2026-08-17`**
- Run root: `data/living_catalog_updates/update_2026-08-17`
- Following successful completion, the next cursor begins **2026-08-18**

Read-only inspection found a clean `main`, only the published prior run, and no existing `update_2026-08-17` manifest.

**Orientation And Preflight**
The exact initial trajectory from the [runbook](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/protocol/LIVING_REVIEW_RUNBOOK.md:107) is:

```bash
export REVIEW_REPO_ROOT="${REVIEW_REPO_ROOT:-/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review}"
export REVIEW_ARTIFACT_ROOT="${REVIEW_ARTIFACT_ROOT:-/Users/bogdan.didenko/lpnu/review}"
cd "$REVIEW_REPO_ROOT"
test "$(git rev-parse --show-toplevel)" = "$REVIEW_REPO_ROOT"
git status --short --branch
git branch --show-current
git log -1 --format='%H %cI %s'
python3 --version
python3 scripts/run_living_review_pipeline.py doctor
python3 scripts/verify_living_review_method_lock.py \
  --current-taxonomy-tree "$(jq -r .taxonomy_root data/living_catalog/current.json)/taxonomy_tree.json"

END=2026-08-17
RUN_ID=update_${END}
python3 scripts/run_living_review_pipeline.py plan --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-capture --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate --date-to "$END"
python3 scripts/run_living_review_pipeline.py preflight \
  --date-to "$END" --through-stage report
```

Proceed only if `doctor` is healthy, the method lock passes, plan reports `date_from=2026-08-10`, the Google Scholar signed bundle has every configured query/page complete, all eight sources can complete, and every preflight check reports `ready: true`. Missing credentials, an incomplete provider page, an unpublished prior run, atlas/state mismatch, or a changed hash is a hard stop.

**Stage Trajectory**
The sole normal operator command for all 18 stages is:

```bash
python3 scripts/run_living_review_pipeline.py run \
  --date-to "$END" --manage-server
```

After any nonzero exit, interruption, timeout, or ambiguity:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage STAGE --manage-server
```

Replace `STAGE` with the literal stage below, using the first blocker reported by `doctor`. Never use `--force` for ordinary recovery.

| Stage / resume literal | Required gate and transition | Failure/manual path |
|---|---|---|
| `search` | Eight completed exports, all pagination exhausted, counts reconciled in `00_search/exports/search_summary_2026-08-17.json`; zero is valid only with completed evidence. | Repair credentials/provider, rerun `scholar-capture` and `scholar-validate`, then resume `search`. No provider substitution under method v1. |
| `deduplicate` | `01_dedup` contains conservative within-update clusters, merge ledger, stats, and visible conflicts; totals equal search summary. | No manual dedup edits. Repair invalid upstream export or resume `deduplicate`. |
| `prepare-records` | DOI/PMID/arXiv/title matching and Crossref audit cover every cumulative master; new cohort and counts reconcile. | Fill only `02_records/manual_cross_dedup_resolutions.json` from its generated template, then resume `prepare-records`. |
| `enrich-abstracts` | Every missing/short abstract route attempted; title fallback is explicitly corroborated; canonical screening input generated. | Resume `enrich-abstracts`; retain failed provider diagnostics. No manually manufactured abstract output. |
| `abstract-screening` | Locked scope and architecture roles, Python gate, and adjudicator produce one final structured result per input under `gpt-5.4-mini`. | Resume unchanged `abstract-screening`; preserve malformed/partial attempts. |
| `fulltext-candidates` | All abstract `INCLUDE + UNCERTAIN` records crosswalk to stable IDs; only declared duplicates may be removed. | Optional sole input: `05_fulltext/postscreen_dedup/duplicate_resolutions.json`; otherwise absence means zero removals. Resume `fulltext-candidates`. |
| `fulltext-download` | Exactly one validated PDF/HTML, terminal evidence-backed `not_retrieved*`, or blocking technical disposition per candidate. | Supply an authorized main article only through `05_fulltext/manual_fulltexts.json`, based on its template, then resume `fulltext-download`. |
| `docling-screening` | Every supported retrieved payload has one complete identity-corroborated no-VLM profile; terminal non-retrieval remains PRISMA-only. | Wrong payload: correct the manual full-text declaration and restart `fulltext-download`. Conversion failure: resume `docling-screening`; never patch Docling JSON/Markdown. |
| `graph-sections` | Graph directly grounds both target types and reconstructs complete heading-bounded sections; root, empty, duplicate, and near-whole-document selections fail. | Graph execution failure: resume `graph-sections`. Missing valid pair is retained and causes the next stage to generate a section-override template. |
| `fulltext-screening` | Same locked role topology sees only title, abstract, and complete selected sections; one final structured result per report. | Fill only `08_section_input/manual_section_overrides.json` from its generated template using exact Markdown hash and heading trails; resume `fulltext-screening`. |
| `eligibility-resolution` | `accepted + excluded = resolved eligibility inputs`; unresolved count is zero. | Fill only `10_eligibility/manual_resolution.csv` with `record_id,manual_decision,rationale,resolver,resolved_at`; resume `eligibility-resolution`. |
| `docling-vlm` | Each accepted report has a fresh complete PDF-based VLM profile, native JSON/Markdown, figures, captions, and descriptions. | An accepted HTML-only report requires an authorized PDF in `manual_fulltexts.json`, then restart `fulltext-download`. Never patch the no-VLM profile. |
| `taxonomy-discovery` | Complete canonical profiles undergo open direct discovery without family labels; inventory and stable registry are complete. | Resume unchanged `taxonomy-discovery`; preserve failed document shards. |
| `taxonomy-classification` | Three direct runs, dense coverage, adjudication and grounding pass; Jaccard ≥0.80, family agreement ≥0.90, alpha ≥0.80; mode is `incremental_frozen_taxonomy`. F6 then performs two complete-document semantic reviews, adjudication, tool isolation, and requires an empty action queue. | Failed agreement requires a reviewed whole-cohort rerun, beginning with `python3 scripts/run_living_review_pipeline.py taxonomy-rerun-preflight --output-dir "$RERUN"`. An F6 action queue blocks snapshot. |
| `crop-validation` | Two selectors, adjudicator/cropper, F7 exact-preview and exact-model input-role reviews, changed-crop review, exhaustive replacement search, final adversarial review, zero unresolved models, and zero tool events. | Resume `crop-validation` for failed batches. Only its zero-unresolved `proposed_crossvalidated_crop_ledger.json` may be promoted. |
| `snapshot` | Prior snapshot plus accepted update reconcile by exact registry, route, evidence, crop, and corpus hashes. Zero accepted writes a no-change marker. | Repair the earliest invalid upstream stage; never edit snapshot totals. |
| `atlas` | Staged atlas is built from the snapshot and all actual corpus roots; desktop/mobile, assets, filters, counts, and console QA pass. Zero accepted keeps published atlas bytes unchanged. | Repair the actual builder/UI defect without bypassing the method lock, then resume `atlas`. |
| `report` | PRISMA facts and update report derive all denominators from artifacts; retrieval branches are mutually exclusive and late-indexing limitation is recorded. | Repair the source artifact or generator and resume `report`; never edit counts manually. |

After each manual declaration, resume without `--force` and run `doctor` again. The declaration hash becomes part of the corresponding stage record.

**Preservation**
Before recomputing expensive Docling, Graph, taxonomy, or crop stages, the runner moves old outputs to `preserved_stage_outputs/<stage>/attempt_NNN/` and appends `preservation_ledger.jsonl`. Successful downloads may be reused. Graph workspaces are reusable only when source-document SHA, Docling JSON SHA, Graph contract/code, model, schema, and stage all match.

After all 18 stages are complete:

```bash
RUN_ROOT="data/living_catalog_updates/${RUN_ID}"
ARCHIVE_ROOT="/Volumes/INDEPENDENT_BACKUP/text-bio-living-review"
python3 scripts/docling/build_input_taxonomy_artifact_manifest.py \
  --artifact-root "$RUN_ROOT"
python3 scripts/archive_living_review_artifacts.py create \
  --source-root "$RUN_ROOT" --archive-root "$ARCHIVE_ROOT" \
  --receipt-dir data/living_catalog/archives --label "$RUN_ID" \
  --storage-class independent_backup
RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
```

Archive the complete run root, including source payloads, both Docling representations, every Graph workspace, prompts/responses/retries, taxonomy runs, crops, figures, snapshots, atlas evidence, and logs. Keep the live root plus one independently stored verified archive.

**Publish And Pages**
```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"
git diff --check
python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor

git status --short
git diff --check
git add data/living_catalog/current.json
git add "data/living_catalog_updates/${RUN_ID}"
git add "$RECEIPT"
git add docs/input-representation-atlas
git add protocol/PRISMA_protocol.md protocol/prisma_search_screening_log_2026-07-07.md
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
```

Then locate and watch the workflow for exactly `$COMMIT`, manually dispatch it only if the commit did not change the atlas path, and run:

```bash
gh run watch "$GITHUB_RUN_ID" --exit-status
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$COMMIT" --check-assets

RELEASE_ROOT="data/living_catalog/releases/${RUN_ID}"
REMOTE_QA="${RELEASE_ROOT}/remote_browser_qa.json"
NODE_PATH="${NODE_PATH:-$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules}" \
  node scripts/qa_input_representation_atlas.mjs \
  https://bogdandidenko.github.io/text-bio-fundational-models-review/ "$REMOTE_QA"
python3 scripts/run_living_review_pipeline.py doctor
```

Remote atlas bytes, commit, tree, every asset hash, counts, desktop/mobile screenshots, review-iteration filter, model details, and console state must match. If deployment fails after local publish, freeze further review work and retry the same commit/artifact; never advance another interval or restore only `current.json`.

Finally:

```bash
python3 scripts/run_living_review_pipeline.py verify-live \
  --run-id "$RUN_ID" --expected-commit "$COMMIT" --check-assets \
  --record-completion --workflow-run-id "$GITHUB_RUN_ID" \
  --operator "OPERATOR" --browser-qa-report "$REMOTE_QA" \
  --screenshot /tmp/atlas-graph-desktop.png \
  --screenshot /tmp/atlas-graph-mobile.png

git add "data/living_catalog/releases/${RUN_ID}/completion_record.json"
git diff --cached --check
git commit -m "Record verified release evidence for ${RUN_ID}"
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
git push origin HEAD:main
```

**Risks And Verdict**
- Routine F6 failure has no declared human-input artifact or runner option for reinserting a versioned corrected taxonomy. The standalone correction commands are documented inside the whole-cohort section, creating an unclear routine-manifest re-entry path.
- Routine F7 unresolved models likewise have no declared manual artifact or targeted runner command after exhaustive replacement. Re-running the whole stage is supported, but persistent resolution is underspecified.
- The literal independent-backup path is not currently present under `/Volumes`; an actual independent destination must be mounted before archive creation.
- Atlas recovery says to fix builder/UI code, while locked builder or QA changes require a new method version and bridge. Operators must stop if the necessary fix touches a locked file.
- Late indexing has no automated lookback, and no filesystem lock prevents concurrent operators.
- Prompt/schema mismatches are documented; changing either during this run is an unsafe shortcut requiring a new method lock and bridge cohort.

**First exact command:**
`export REVIEW_REPO_ROOT="${REVIEW_REPO_ROOT:-/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review}"`

**Next interval/run:** `2026-08-10..2026-08-17`, `update_2026-08-17`.

**Verdict: PASS WITH RISKS.** The passing routine path is explicit, hash-locked, and publication-gated. Conditional F6/F7 recovery and the independent-backup location are not fully executable from the manual alone, but those gaps force a stop rather than permit silent publication.
