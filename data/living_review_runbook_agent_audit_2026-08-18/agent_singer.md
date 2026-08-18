**Audit Basis**

Read-only inspection only. I did not run the pipeline, network calls, models, Docling, builds, Git operations, or publication commands.

Stored state has `search_end: 2026-08-09`; the atlas `meta.generated_from` matches the stored taxonomy root. With the assumed Kyiv date, the next routine interval is **2026-08-10 through 2026-08-17**, inclusive.

**Orientation And Preflight**

Hypothetical commands, in order:

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

Gates: `doctor` healthy; method lock valid; plan reports `date_from=2026-08-10`, `date_to=2026-08-17`, and `run_root=data/living_catalog_updates/update_2026-08-17`; prior taxonomy equals atlas source; all preflight checks have `ready:true`. Scholar capture must exhaust and hash every configured page. Any existing run root means resume, never overwrite.

The eight enabled sources are PubMed, Scopus, OpenAlex, Semantic Scholar, arXiv, bioRxiv/medRxiv, SpringerNature, and Google Scholar. Routine v1 permits Scholar input only through the locked `scholar-capture` SerpAPI path; a different provider requires a new method version and bridge analysis.

**Scientific Stages**

Normal execution is one command:

```bash
python3 scripts/run_living_review_pipeline.py run \
  --date-to "$END" --manage-server
```

After any nonzero exit, timeout, or ambiguous state:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage STAGE --manage-server
```

Replace `STAGE` only with the first blocking stage reported by `doctor`.

| Stage | Prerequisite and success transition | Failure/recovery and manual input |
|---|---|---|
| `search` | Valid dated config and Scholar bundle; all eight sources and pagination complete. Produces `00_search/exports/search_summary_2026-08-17.json`. | Resume `search`; never convert a failed source to zero. Credentials stay in ignored `api_keys.json`. |
| `deduplicate` | Search totals reconcile. Produces within-update records, stats, clusters, merge/review ledger in `01_dedup/`. | Resume `deduplicate`, or `search` if an export is invalid. |
| `prepare-records` | Compare DOI/PMID/preprint ID/title against every published master and Crossref. Produces the new-record cohort and audit in `02_records/`. | Only `02_records/manual_cross_dedup_resolutions.json`, copied structurally from its generated template; then resume `prepare-records`. |
| `enrich-abstracts` | Every missing/short abstract route attempted; title fallback identity-corroborated. Produces `03_abstracts/abstract_screening_input.json`. | Resume `enrich-abstracts`; retain failed/rejected provider evidence. |
| `abstract-screening` | Frozen runner/prompts/model/schema; complete scope, architecture, Python-gate and adjudicated rows. | Resume `abstract-screening`; never mix changed prompts or fabricated parsed rows. |
| `fulltext-candidates` | Abstract `INCLUDE + UNCERTAIN`, stable-ID crosswalk, denominator reconciliation. | Optional proven duplicates only through `05_fulltext/postscreen_dedup/duplicate_resolutions.json`; absent means none. |
| `fulltext-download` | One disposition per candidate: validated PDF/HTML, terminal not-retrieved, or blocking technical failure. | Manual articles only through `05_fulltext/manual_fulltexts.json` using the generated template; then resume `fulltext-download`. |
| `docling-screening` | Valid supported payloads only; one complete identity-corroborated no-VLM profile each. | Wrong source: correct the manual full-text declaration and resume from download. Otherwise resume `docling-screening`. |
| `graph-sections` | Complete heading-bounded `data_source` and `input_representation` sections; no root/empty/whole-document selection. | Invalid selections are recorded in `08_section_input/run_metadata.json`; the next stage blocks for an override. |
| `fulltext-screening` | Title, abstract, and selected sections only; complete frozen-role decisions. | Only `08_section_input/manual_section_overrides.json`, built from its template with canonical Markdown hash and exact heading trails; resume `fulltext-screening`. |
| `eligibility-resolution` | Every full-text result resolves to accepted or excluded. | Only `10_eligibility/manual_resolution.csv` with decision, evidence rationale, resolver, timestamp; resume the stage. |
| `docling-vlm` | Every accepted report has an authorized PDF and fresh complete VLM profile with figures/captions/descriptions. | HTML-only acceptance blocks. Add PDF through `manual_fulltexts.json`, then resume from `fulltext-download`. |
| `taxonomy-discovery` | Full canonical profiles, open discovery without family labels; produces route inventory and study/model registry. | Resume unchanged `taxonomy-discovery`; all documents/shards must succeed. |
| `taxonomy-classification` | Three direct runs, dense audit, adjudication, grounding, agreement thresholds, then F6 two-reviewer semantic sufficiency. Mode is `incremental_frozen_taxonomy`. | Agreement failure requires whole-cohort rerun. Nonempty F6 queue blocks snapshot and requires versioned correction, not hand edits. See risk below. |
| `crop-validation` | Two selectors/adjudicator plus F7 exact-preview, input-role, adjusted and exhaustive replacement reviews; zero unresolved; tool audit clean. | Resume `crop-validation` for failed batches. No manual crop declaration is supported; never promote an unreviewed ledger. |
| `snapshot` | Exact route/evidence/crop parity and source hashes; merges prior snapshot plus accepted update only. | Repair the earliest invalid upstream stage; never edit snapshot totals. |
| `atlas` | Build report matches snapshot; local HTTP browser QA passes desktop/mobile/filter/assets/console checks. | Fix locked builder/UI only through a reviewed method-compatible change, then resume `atlas`. |
| `report` | All PRISMA denominator identities and retrieval branches reconcile; late-indexing limitation recorded. | Fix the originating artifact or generator and resume `report`; never edit counts manually. |

For any generated manual file, the only supported operation is to populate the exact target from its generated template and resume without `--force`. There is no supported direct edit to generated decisions, taxonomy routes, crop ledgers, snapshots, reports, or cursor state.

**Preservation And Archive**

Retries automatically rotate Docling profiles, Graph workspaces, taxonomy runs, and adjudications into `preserved_stage_outputs/<stage>/attempt_NNN/`, recording hashes and sizes in `preservation_ledger.jsonl`. Reuse requires matching source/profile hashes and the same locked contract. A different source PDF hash is a new profile.

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

Missing/unlisted files, hash mismatch, or non-independent storage stops publication. Keep the live run plus one verified independent archive. Never rebuild the artifact manifest after publication.

**Publish And Pages**

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"
git diff --check
python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor
```

Expected transition: `current.json.search_end` becomes `2026-08-17`; accepted records add the new snapshot/corpus/atlas, while a zero-accepted update advances only the search/PRISMA state and leaves atlas content unchanged. Freeze further review work until remote verification finishes.

Stage only the explicit runbook paths, verify the receipt and both doctor modes, then commit:

```bash
git add data/living_catalog/current.json
git add "data/living_catalog_updates/${RUN_ID}"
git add "$RECEIPT"
git add docs/input-representation-atlas
git add protocol/PRISMA_protocol.md protocol/prisma_search_screening_log_2026-07-07.md
git diff --cached --check
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID" --repository-checkout
git commit -m "Update living review through ${END}"
```

Then enforce `origin/main` ancestry, push `HEAD:main`, find/watch the matching workflow run, and run:

```bash
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$COMMIT" --check-assets

RELEASE_ROOT="data/living_catalog/releases/${RUN_ID}"
REMOTE_QA="${RELEASE_ROOT}/remote_browser_qa.json"
NODE_PATH="${NODE_PATH:-$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules}" \
  node scripts/qa_input_representation_atlas.mjs \
  https://bogdandidenko.github.io/text-bio-fundational-models-review/ "$REMOTE_QA"
```

The workflow and verification must bind exact atlas bytes, complete tree hashes, assets, counts, and commit. Failure freezes the cursor: retry the same workflow/artifact and record an `incident`; if withdrawal is necessary, restore state and atlas together in a new rollback commit.

**Completion Record**

After successful remote and visual QA:

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

**Divergence And Defects**

1. F6 recovery is incomplete for routine runs. The manual’s correction commands use whole-cohort `$RERUN` paths, while the routine runner has no correction declaration/input and recomputes the original taxonomy on resume. Two operators would have to improvise reintegration. [Runbook](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/protocol/LIVING_REVIEW_RUNBOOK.md:604), [runner](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/scripts/run_living_review_pipeline.py:2387).
2. F7 unresolved cases are called a manual gate, but no manual artifact or exact supported correction command is defined. Resuming recomputes the stage; manual crop edits are forbidden. [Runner](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/scripts/run_living_review_pipeline.py:2505).
3. Completion records read `stages.search.ended`, but the runner records `finished`; therefore `search_completed_at` will be null despite being mandatory. Tests mask this by constructing an `ended` field. [Writer](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/scripts/run_living_review_pipeline.py:3520), [stage record](/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/scripts/run_living_review_pipeline.py:1095).
4. `ARCHIVE_ROOT` and physical independence are site-specific placeholders, not discovered or configured by the manual.
5. Local publish precedes remote deployment and is not transactional; the documented freeze reduces but does not remove this risk.
6. Late indexing has no retrospective lookback, so closed-interval recall depends on later supplemental discovery.

**Final Determination**

- **First exact command:**
  `export REVIEW_REPO_ROOT="${REVIEW_REPO_ROOT:-/Users/bogdan.didenko/lpnu/text-bio-fundational-models-review}"`
- **Next interval:** `2026-08-10` through `2026-08-17`, inclusive.
- **Run ID:** `update_2026-08-17`.
- **Verdict: FAIL.** The happy path is substantially specified, but the manual alone cannot reproducibly complete routine F6/F7 recovery, and the mandatory completion timestamp is not produced correctly by the canonical runner.
