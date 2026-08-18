No pipeline, network, LLM, Docling, Git-write, publication, or mutation command was executed.

**Resolved Run**

Documented state:

- Published cursor: `search_end=2026-08-09` in [current.json](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/data/living_catalog/current.json:4).
- Current atlas source matches `current.taxonomy_root`: `data/living_catalog/taxonomy_rerun_preflight_2026-08-12/snapshot_full_55_semantic_correction_2026-08-17` in [atlas.json](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/docs/input-representation-atlas/data/atlas.json:5).
- The only update manifest is the published legacy `update_2026-08-09`; no `update_2026-08-17/run_manifest.json` exists.
- Last fully elapsed day on 2026-08-18 in `Europe/Kyiv` is `2026-08-17`.

Therefore:

```text
Mode:      routine incremental update
date_from: 2026-08-10
date_to:   2026-08-17
RUN_ID:    update_2026-08-17
RUN_ROOT:  data/living_catalog_updates/update_2026-08-17
analysis:  incremental_frozen_taxonomy
method_id: living-review-v1-frozen-taxonomy-v1
```

Current method-lock SHA-256 is `718bb59eded9858c7a150ee554d768103207787ab0ab0b62546332c778d945e4`, subject to the mandatory verifier immediately before run creation.

## 1. Command Trajectory

```bash
export TZ=Europe/Kiev
export REVIEW_REPO_ROOT="/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review"
export REVIEW_ARTIFACT_ROOT="/Users/bogdan.didenko/lpnu/review"
cd "$REVIEW_REPO_ROOT"

END=2026-08-17
DATE_FROM=2026-08-10
RUN_ID="update_${END}"
RUN_ROOT="data/living_catalog_updates/${RUN_ID}"
ARCHIVE_ROOT="/Volumes/INDEPENDENT_BACKUP/text-bio-living-review"

test "$(git rev-parse --show-toplevel)" = "$REVIEW_REPO_ROOT"
git status --short --branch
git branch --show-current
git log -1 --format='%H %cI %s'
python3 --version

python3 scripts/run_living_review_pipeline.py doctor
python3 scripts/verify_living_review_method_lock.py \
  --current-taxonomy-tree "$(jq -r .taxonomy_root data/living_catalog/current.json)/taxonomy_tree.json"

python3 scripts/run_living_review_pipeline.py plan --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-capture --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate --date-to "$END"
python3 scripts/run_living_review_pipeline.py preflight \
  --date-to "$END" --through-stage report

python3 scripts/run_living_review_pipeline.py run \
  --date-to "$END" --manage-server
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
```

The `run` command executes, in order:

```text
search -> deduplicate -> prepare-records -> enrich-abstracts
-> abstract-screening -> fulltext-candidates -> fulltext-download
-> docling-screening -> graph-sections -> fulltext-screening
-> eligibility-resolution -> docling-vlm -> taxonomy-discovery
-> taxonomy-classification -> crop-validation -> snapshot -> atlas -> report
```

For any interruption or manual gate:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage STAGE --manage-server
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
```

After all 18 stages are hash-valid:

```bash
python3 scripts/docling/build_input_taxonomy_artifact_manifest.py \
  --artifact-root "$RUN_ROOT"

python3 scripts/archive_living_review_artifacts.py create \
  --source-root "$RUN_ROOT" \
  --archive-root "$ARCHIVE_ROOT" \
  --receipt-dir data/living_catalog/archives \
  --label "$RUN_ID" \
  --storage-class independent_backup

RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"

python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status \
  --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"
git diff --check

python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor
```

Publication commit and remote deployment:

```bash
git status --short
git diff --check
git add data/living_catalog/current.json
git add "data/living_catalog_updates/${RUN_ID}"
git add "$RECEIPT"
git add docs/input-representation-atlas
git add protocol/PRISMA_protocol.md \
  protocol/prisma_search_screening_log_2026-07-07.md
git status --short
git diff --cached --check
git diff --cached --stat

python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor \
  --run-id "$RUN_ID" --repository-checkout

git commit -m "Update living review through ${END}"
COMMIT="$(git rev-parse HEAD)"
git fetch origin main
git merge-base --is-ancestor origin/main "$COMMIT"
git push origin HEAD:main

if ! git diff-tree --no-commit-id --name-only -r "$COMMIT" |
  rg -q '^docs/input-representation-atlas/'; then
  gh workflow run deploy-input-representation-atlas.yml --ref main
fi

GITHUB_RUN_ID=""
for attempt in 1 2 3 4 5 6; do
  GITHUB_RUN_ID="$(gh run list \
    --workflow deploy-input-representation-atlas.yml --branch main --limit 10 \
    --json databaseId,headSha \
    --jq ".[] | select(.headSha == \"$COMMIT\") | .databaseId" | head -1)"
  test -n "$GITHUB_RUN_ID" && break
  sleep $((attempt * 5))
done
test -n "$GITHUB_RUN_ID"
gh run watch "$GITHUB_RUN_ID" --exit-status

python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$COMMIT" --check-assets

RELEASE_ROOT="data/living_catalog/releases/${RUN_ID}"
REMOTE_QA="${RELEASE_ROOT}/remote_browser_qa.json"
NODE_PATH="${NODE_PATH:-$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules}" \
  node scripts/qa_input_representation_atlas.mjs \
  https://bogdandidenko.github.io/text-bio-fundational-models-review/ \
  "$REMOTE_QA"

python3 scripts/run_living_review_pipeline.py doctor
```

Completion needs an accountable operator identity not present in repository state:

```bash
: "${OPERATOR:?Set the documented accountable operator name}"

python3 scripts/run_living_review_pipeline.py verify-live \
  --run-id "$RUN_ID" --expected-commit "$COMMIT" --check-assets \
  --record-completion --workflow-run-id "$GITHUB_RUN_ID" \
  --operator "$OPERATOR" --browser-qa-report "$REMOTE_QA" \
  --screenshot /tmp/atlas-graph-desktop.png \
  --screenshot /tmp/atlas-graph-mobile.png

git add "data/living_catalog/releases/${RUN_ID}/completion_record.json"
git diff --cached --check
git commit -m "Record verified release evidence for ${RUN_ID}"
git fetch origin main
git merge-base --is-ancestor origin/main HEAD
git push origin HEAD:main
```

## 2. Stage Contracts

| Stage | Accepted input | Success and downstream | Supported recovery |
|---|---|---|---|
| `search` | Dated config plus complete PubMed, Scopus, OpenAlex, Semantic Scholar, arXiv, bioRxiv/medRxiv, SpringerNature and Scholar captures | All sources and pagination complete; exports and `search_summary_2026-08-17.json` enter dedup | Restore credentials or matching Scholar capture; resume `search` |
| `deduplicate` | Eight exports | Counts reconcile; conservative clusters and merge ledger enter cumulative comparison | Repair invalid export or resolve reported conflict |
| `prepare-records` | Update clusters plus every `current.master_record_files` artifact | DOI/PMID/arXiv/title comparison and Crossref audit complete; new cohort enters enrichment | Fill `02_records/manual_cross_dedup_resolutions.json`; resume |
| `enrich-abstracts` | New-record cohort | Every missing abstract attempted; corroborated title fallback; `abstract_screening_input.json` enters screening | Retry same providers and stage |
| `abstract-screening` | Locked bibliographic transport; scientific evidence is title and abstract | Every row has final scope/architecture/Python-gate/adjudicated result | Retry incomplete frozen batches only |
| `fulltext-candidates` | Abstract `INCLUDE` and `UNCERTAIN`, stable-ID crosswalk | Raw candidates reconcile; declared post-screen duplicates removed | Correct identity or `05_fulltext/postscreen_dedup/duplicate_resolutions.json` |
| `fulltext-download` | Candidate metadata and optional manual manifest | One validated PDF/HTML, terminal not-retrieved, or blocking technical disposition per candidate | Retry; or fill `05_fulltext/manual_fulltexts.json` with lawful main article |
| `docling-screening` | Validated supported payloads only | Exactly one identity-corroborated no-VLM profile per retrieved candidate | Correct payload and resume from download, otherwise rerun Docling |
| `graph-sections` | Complete no-VLM profiles | Grounded, complete heading-bounded `data_source` and `input_representation` sections | Fill `08_section_input/manual_section_overrides.json`; resume |
| `fulltext-screening` | Title, abstract and complete selected sections | Every retrieved candidate has final structured decision | Retry frozen batches after section gate is resolved |
| `eligibility-resolution` | Full-text decisions | `accepted + excluded = resolved inputs`; no unresolved rows | Fill `10_eligibility/manual_resolution.csv`; resume |
| `docling-vlm` | Newly accepted records with validated PDFs | Complete fresh VLM profile, native JSON/Markdown, figures, captions and descriptions | Add authorized PDF via manual full-text manifest; resume from `fulltext-download` |
| `taxonomy-discovery` | Complete new VLM profiles | Open direct route inventory and stable study/model registry | Retry unchanged document shards |
| `taxonomy-classification` | Inventory, taxonomy v1, three direct runs, dense audit | All records complete; Jaccard ≥0.80, family agreement ≥0.90, alpha ≥0.80; F6 passes | One automatic F6 correction; second queue or threshold failure requires whole-cohort rerun |
| `crop-validation` | Authoritative routes and every native source figure | One reviewed crop or explicit no-suitable disposition per model; zero unresolved | Retry technical batches; persistent semantic failure becomes omission |
| `snapshot` | Prior snapshot plus authoritative routes/evidence/crops | IDs, counts, corpus hashes and route/evidence parity reconcile | Repair earliest invalid upstream stage |
| `atlas` | Snapshot and every cumulative VLM corpus root | Build report and local desktop/mobile browser QA pass | Fix builder/UI, rebuild this stage, rerun QA |
| `report` | All stage summaries and denominator ledgers | PRISMA transitions and mutually exclusive retrieval branches reconcile | Repair source artifact or generator; never edit counts |

Manual gate resume stages are `prepare-records`, `fulltext-download`, `graph-sections`, and `eligibility-resolution`. An accepted HTML-only report later blocked at `docling-vlm` resumes from `fulltext-download`.

## 3. F6 And F7

**F6 non-retain**

`taxonomy-classification` writes `12_taxonomy/semantic_sufficiency/semantic_sufficiency_action_queue.csv`. A non-empty queue causes the runner to:

1. Preserve the original taxonomy and F6 evidence.
2. Run isolated correction into `semantic_correction_decisions/`.
3. Apply it into `semantic_correction_applied/`, retaining stable route IDs, transition ledger and tombstones.
4. Repeat both complete-document reviewers, comparison, adjudication and finalization in `semantic_sufficiency_revalidation/`.
5. Write `12_taxonomy/authoritative_taxonomy.json`; crops, snapshot and report use that root.

If revalidation still has any action row, the runner stops. The only supported next action is:

```bash
RERUN="data/living_catalog/taxonomy_rerun_preflight_$(date +%F)"
python3 scripts/run_living_review_pipeline.py taxonomy-rerun-preflight \
  --output-dir "$RERUN"
cat "$RERUN/readiness.json"
```

**F7 persistent crop failure**

F7 performs exact-preview review, exact-model input-role review, adjudication, adjusted-crop review, exhaustive replacement search, two replacement-preview rounds and final replacement input-role review. After that complete sequence, persistent semantic failure is terminalized as:

```text
status: crop_rejected_no_suitable_figure
crop coordinates: cleared
route_ids_supported: cleared
preterminal_status: retained
```

Only zero-unresolved `13_crops/exact_preview_validation/proposed_crossvalidated_crop_ledger.json` is copied to `13_crops/crop_ledger.json`. This is a transparent omission, not a passed crop.

## 4. Preservation And Restore

Before recomputing expensive stages, the runner moves existing profiles, Graph workspaces, taxonomy runs/adjudication and crop-agent outputs under:

```text
preserved_stage_outputs/<stage>/attempt_NNN/
preserved_stage_outputs/preservation_ledger.jsonl
```

Every attempt retains original/preserved paths, timestamp, file count and byte count. LLM prompts, responses, schemas, retries, errors and commands remain under `logs/<stage>/attempt_NNN/`.

The immutable archive contains source PDFs/HTML, no-VLM/VLM Docling profiles, native JSON/Markdown, images and captions, Graph `document.dclg`, `document.json`, `chunks.json`, `graph.html`, metadata, extraction outputs, taxonomy-agent runs, F6 corrections, crop-agent/F7 runs, snapshot, atlas and logs.

Restore is:

```bash
RESTORE_ROOT=/empty/path/restored_run
python3 scripts/archive_living_review_artifacts.py restore \
  --receipt "$RECEIPT" --destination "$RESTORE_ROOT"
python3 scripts/archive_living_review_artifacts.py verify \
  --receipt "$RECEIPT"
```

Then validate the canonical VLM manifest with `validate_canonical_profile_manifest.py` and run `doctor`. Immutable provenance paths are not rewritten; old bases must be supplied through `REVIEW_ARTIFACT_ROOT` or repeatable `--artifact-root`. Reuse is allowed only when source/profile hashes and locked contracts match.

## 5. Remaining Risks And Omissions

1. `END` is manually chosen. The runner rejects reversed ranges but does not enforce `Europe/Kiev` or reject an unfinished/future date.
2. Closed intervals have no retrospective late-indexing lookback, so delayed indexing can permanently miss records.
3. There is no filesystem lock and no initial `git fetch origin main`; another operator or remote publication can make an expensive run stale.
4. `OPERATOR`, manual resolvers, the real independent-backup device, `CORPUS_ROOT_*`, and rollback `LAST_GOOD_COMMIT` are unresolved placeholders.
5. `--storage-class independent_backup` is declarative. The archive code does not verify that the target is physically independent from the source filesystem.
6. `RECEIPT="$(ls -t ...)"` selects by mtime rather than binding directly to the archive command’s returned receipt.
7. The arbitrary restore example does not show how a restored run is placed so `doctor --run-id` can discover it. The supplied semantic validation command covers VLM profiles, but no executable sequence validates no-VLM profiles, Graph contracts, taxonomy and crop semantics after migration. It also assumes a VLM manifest exists, which is false for a zero-accepted run.
8. Future F6 sibling-route conflicts require grouped adjudication, but the runbook supplies no generic case schema or executable command. The routine runner currently applies correction immediately.
9. Initial F6 reviewer roles are not subject to the explicit empty-workspace/tool-isolation audit required for F6 correction and F7 agents.
10. “Repeat F6 with a fresh revalidation directory” and selective post-hoc F7 dependency revalidation are prose, not complete commands.
11. Manual duplicate, eligibility and section decisions are not automatically dual-human reviewed. Lawful manual PDF acquisition also has no executable acquisition protocol.
12. Local `publish` advances `current.json` before GitHub Pages succeeds. The freeze is policy, not enforced transactionally.
13. The Git sequence can include pre-existing staged changes; the fixed PRISMA paths have no documented generator in this trajectory.
14. Model names such as `gpt-5.4-mini` and `gpt-5.5` are locked strings, not immutable provider snapshot identifiers. Backend drift and nondeterminism limit exact temporal reproducibility.
15. The frozen prompts have documented prompt/schema key conflicts. They must remain unchanged for v1, but can create brittle retries.
16. Google Scholar is year-bounded and explicitly not day-exhaustive; source completeness is provider-visible pagination, not complete Scholar-index coverage.
17. The previous update is a declared legacy run without a method lock or schema-v2 completion record. Comparability therefore relies on the bridged 55-record snapshot, not a shared run-manifest lock across consecutive updates.

## Verdict

**PASS WITH RISKS**

The normal runner path is sufficiently specified to resolve and execute `update_2026-08-17` reproducibly under the current frozen method, with strong stage hashes, denominator checks, F6/F7 gates, immutable archives and remote byte verification. It is not an unconditional pass because backup independence, cross-machine restoration, concurrent publication, future F6 grouped conflicts and several manual/provenance steps remain incompletely executable or policy-only.
