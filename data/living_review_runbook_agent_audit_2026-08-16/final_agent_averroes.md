I’ll treat the runbook as the sole authority, then inspect only the static repository files it explicitly names. I’ll separate commands prescribed by the protocol from commands I actually use for read-only inspection; none of the prescribed operational commands will be run.
The runbook defines the routine interval as inclusive and closes it at the last fully elapsed `Europe/Kiev` day. I’m now checking the published state, frozen configuration, method lock, and schemas named by the runbook so the payloads, stage order, and reuse rules come from recorded contracts rather than assumptions.
Static state shows the published cursor is `2026-08-09`, so the routine dry-run interval is `2026-08-10` through `2026-08-15` inclusive. The prior publication is explicitly a legacy exception; the next run must use method lock `living-review-v1-frozen-taxonomy-v1` and cannot inherit that exception’s relaxed archive/completion requirements.
The execution boundary is clear: the operator uses the orchestrator for the normal path, and only generated declaration files may resolve human gates. I’m checking the release workflow and QA contract next, because local `publish` is explicitly insufficient and the completion record depends on exact remote evidence.
Silent dry run only. None of the operational commands below was executed, and no files or external services were touched.

**Cursor**
The published state in [current.json](/Users/bogdan.didenko/lpnu/review/data/living_catalog/current.json) records:

- Published cursor: `search_end = 2026-08-09`, inclusive.
- Next `date_from`: `2026-08-10`.
- Today is `2026-08-16` in `Europe/Kiev`; therefore the last fully elapsed day is `2026-08-15`.
- Exact interval: **`2026-08-10..2026-08-15`, inclusive**.
- Run ID/root: `update_2026-08-15` and `data/living_catalog_updates/update_2026-08-15`.
- Late indexing is not searched retrospectively; that limitation must appear in the update report.

The next run directory is presently absent. Static pointers show the atlas and current taxonomy root agree at 55 records, 54 studies, 109 models, 468 configurations, and 586 routes. This does not replace `doctor`.

The applicable method is `living-review-v1-frozen-taxonomy-v1`; current lock SHA-256 is `95eff1994a9b327200e2b951dff9dd722401160d022df225671bdb15e90b3b58`, and frozen taxonomy SHA-256 is `b36c0261a93c6d0e19a2502ec416ba26bf71315cfc04bf3323b260c239693bf9`.

**Initial Procedure**
```bash
cd /Users/bogdan.didenko/lpnu/review
git status --short --branch
git branch --show-current
git log -1 --format='%H %cI %s'
python3 --version
python3 scripts/run_living_review_pipeline.py doctor
python3 scripts/verify_living_review_method_lock.py \
  --current-taxonomy-tree "$(jq -r .taxonomy_root data/living_catalog/current.json)/taxonomy_tree.json"

END=2026-08-15
RUN_ID=update_${END}
RUN_ROOT="data/living_catalog_updates/${RUN_ID}"

python3 scripts/run_living_review_pipeline.py plan --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-capture --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate --date-to "$END"
python3 scripts/run_living_review_pipeline.py preflight \
  --date-to "$END" --through-stage report
python3 scripts/run_living_review_pipeline.py run \
  --date-to "$END" --manage-server
```

Proceed only if `doctor` is healthy, method-lock verification succeeds, the plan returns `date_from=2026-08-10`, `date_to=2026-08-15`, the expected run root and current prior state, Scholar validation is complete, and every required preflight check reports `ready: true`.

**Eighteen Stages**

| # | Stage | Required input and success/denominator boundary | Failure or recovery |
|---:|---|---|---|
| 1 | `search` | Dated v3.3 config, keys, signed Scholar bundle. All eight sources and pagination paths complete. `raw hits = sum(completed export counts)`; provider failure is not zero. | Fix access/provider capture and resume `search`; retain completed checkpoints. |
| 2 | `deduplicate` | Eight exports plus search summary. Preserve conflict queue and provenance. `within-update unique = raw hits - duplicate members`. | Correct only invalid upstream exports; resume the first stage reported by `doctor`. |
| 3 | `prepare-records` | Update clusters, every published master, Crossref audit, optional supplemental declarations. Queue empty or resolved. `new = unique - cumulative matches/exclusions`. | Complete generated cross-dedup resolutions; resume `prepare-records`. |
| 4 | `enrich-abstracts` | New records. Every missing/short abstract attempted; title matches require year/author corroboration. Screening input plus unusable-abstract exclusions must cover the new-record cohort. | Retry providers in the same stage; bounded diagnostic output is noncanonical. |
| 5 | `abstract-screening` | Usable title/abstract cohort. Every input gets a structured final result. `abstract-screened = final decisions`. | Retry incomplete batches with identical runner, prompts, schema, and model. |
| 6 | `fulltext-candidates` | Abstract results, input and stable-ID crosswalk; optional duplicate declaration. `raw candidates = INCLUDE + UNCERTAIN`; retrieval candidates subtract only declared duplicates. | Correct identity/decisions or declaration; never infer duplicates from missing files. |
| 7 | `fulltext-download` | Retrieval candidates and optional manual full texts. Exactly one validated retrieved or terminal-not-retrieved disposition; no technical/XML blockers. `candidates = retrieved + terminal not-retrieved`. | Retry providers or declare an authorized main article; supplements/landing pages are invalid. |
| 8 | `docling-screening` | Validated supported PDF/HTML subset. Exactly one identity-corroborated no-VLM profile per retrieved supported candidate. | Correct wrong/corrupt source via `fulltext-download`, otherwise rerun Docling. |
| 9 | `graph-sections` | Complete no-VLM manifest. One-to-one Graph results and grounded, heading-bounded `data_source` and `input_representation` sections. | Supply canonical heading overrides; no pasted text or whole-document section. |
| 10 | `fulltext-screening` | Title, abstract and complete selected sections. Every valid section-pair input gets a final result. | Resolve section gate first or retry unchanged frozen batches. |
| 11 | `eligibility-resolution` | Full-text decisions plus optional manual CSV. No unresolved records. `accepted + excluded = eligibility inputs`. | Add evidence-bearing manual resolution and resume this stage. |
| 12 | `docling-vlm` | Newly accepted records with authorized PDFs. One fresh complete VLM profile per accepted record. | HTML-only accepted records return to `fulltext-download` for a lawful PDF. |
| 13 | `taxonomy-discovery` | Complete new VLM profiles. Open direct discovery without family labels plus fixed inventory and study/model registry. `discovery documents = taxonomy records`. | Retry failed document shards unchanged. |
| 14 | `taxonomy-classification` | Inventory, taxonomy v1, full profiles. Three direct runs, dense audit and adjudication all complete and grounded; Jaccard ≥0.80, family agreement ≥0.90, alpha ≥0.80 and estimable. | Threshold failure requires reviewed whole-cohort rerun, not record-level patching. |
| 15 | `crop-validation` | Accepted routes and native figures. Every included model has a valid crop or explicit `no_suitable_figure`. | Retry failed model batches while retaining selectors, responses and figure identity. |
| 16 | `snapshot` | Prior snapshot, update taxonomy/crops, all corpus roots. Route/evidence IDs, counts and source hashes reconcile. `cumulative = prior + accepted update` with explicit linkage. | Repair earliest invalid upstream stage; never edit totals. |
| 17 | `atlas` | Snapshot, prior UI shell and all figure-bearing corpus roots. Build counts match snapshot; local desktop/mobile, filter, assets and console QA pass. | Fix builder/UI, rebuild `atlas`, rerun QA. Published atlas remains unchanged. |
| 18 | `report` | All stage summaries. Every PRISMA transition and mutually exclusive retrieval branch reconciles; record/study/model/configuration/route counts remain distinct. | Fix the source artifact or generator; never edit counts manually. |

A true upstream zero may propagate through empty-stage markers, but only after the upstream source completed and evidenced zero.

**Screening Contract**
Both passes use two separate first-pass invocations of `gpt-5.4-mini`, followed by the deterministic Python gate. Only `ADJUDICATE` cases enter a separate adjudicator invocation of the same model.

Abstract first-pass model payload, in batches of 8:

```json
{"record_id":"rec_NNNNNN","title":"...","abstract":"...","doi":"...","year":"...","venue":"...","sources":[]}
```

The legacy positional `record_id` is mapped one-to-one to canonical `record_id` and `candidate_id` in `04_abstract_screening/record_id_crosswalk.json`. Abstract adjudication adds:

```json
{"first_pass_outputs":{"scope_reviewer":{},"architecture_reviewer":{},"python_gate":{}}}
```

Full-text first-pass payload, also batches of 8:

```json
{"record_id":"...","candidate_id":"...","source_record_id":"...","source_corpus":"...","title":"...","abstract":"...","doi":"...","year":"...","venue":"...","sources":[],"selected_full_text_sections":[]}
```

Its adjudicator adds the same `first_pass_outputs`. `selector_reason`, `section_evidence`, and complete `docling_markdown` are excluded. Adjudicator batches contain 6 records. Abstract execution uses the hash-pinned legacy runner with `max_workers=64`; selected-section execution uses 8 workers, three batch attempts, and a 1,800-second timeout.

Strict output is `{"results":[...]}`, one ordered row per input. Scope requires `record_id,paper_type,bio_modality_present,text_component_present,text_bio_bridge_present,primary_exclusion_code,uncertainty_reason,decision_rationale,evidence_snippet`; architecture substitutes `generative_model_present,foundation_model_evidence`; adjudication requires all criteria. The strict schema/parser overrides known prompt-key mismatches; prompts or schemas must not be repaired during this routine iteration.

**Modes And Reuse**

- No-VLM Docling: PDF/HTML screening profiles; PDF settings are OCR off, accurate tables/cell matching on, page/picture images on at scale 2.0, formula enrichment off, heading hierarchy from bookmarks/numbering/style, no truncation.
- VLM Docling: fresh PDF-only profiles for newly accepted reports, using `gpt-5.5`; do not patch no-VLM profiles in place.
- Graph sections: `openai/gpt-5.4-mini`, direct extraction, detailed provenance, then complete heading-boundary reconstruction.
- Taxonomy: `incremental_frozen_taxonomy`; open direct discovery, inventory-only synthesis, three direct fixed-candidate replicates, dense scoped-fill/standard-dedup coverage, separate adjudication, taxonomy v1, prompt `v3-interface-boundary`, temperature 0, no truncation.
- Crops: two blind selectors, separate adjudicator and cropper using `gpt-5.4-mini`; prior model dispositions are passed as the exclusion ledger and cannot be silently replaced.
- Snapshot: incremental immutable merge only. Whole-cohort reruns require `freeze_full_cohort_snapshot.py`, never a fabricated empty prior or incremental merge.
- Atlas: copy the prior validated UI into staging, rebuild from the snapshot and every actual figure corpus, then run browser QA. Publish only after success.
- Successful downloads may be reused. A canonical profile or Graph workspace is reusable only when source/profile hashes, locked code/contract, model, schema and stage match. A different source-document hash requires a new profile. Expensive reruns are preserved under `preserved_stage_outputs`; `--force` is not routine recovery.

**Manual Gates**

- Scholar: `00_search/google_scholar_provider_export.json`; signature, exact queries, year/date bounds, all raw hashes, query completion rows, pagination termination and counts must validate.
- Cross-dedup: populate `02_records/manual_cross_dedup_resolutions.json` from its template with `update_cluster_id,decision,rationale,resolver,resolved_at`; resume `prepare-records`.
- Optional post-screen duplicate: `05_fulltext/postscreen_dedup/duplicate_resolutions.json`; each row requires both screening IDs, `resolution=duplicate_of`, rationale, resolver and timestamp; resume `fulltext-candidates`.
- Manual retrieval: populate `05_fulltext/manual_fulltexts.json` from its template with `candidate_id,file,source_url,retriever,retrieved_at`; resume `fulltext-download`.
- Section override: schema-v2 `08_section_input/manual_section_overrides.json`, exact Markdown path/hash and heading trails covering both target roles; resume `fulltext-screening`.
- Eligibility: `10_eligibility/manual_resolution.csv` with exact header `record_id,manual_decision,rationale,resolver,resolved_at`; decisions are `INCLUDE` or `EXCLUDE`; resume `eligibility-resolution`.

After each declaration:

```bash
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage STAGE --manage-server
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
```

`STAGE` must be the first blocking stage reported by `doctor`.

**Closure And Publication**
```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" > "/tmp/${RUN_ID}_status.json"

python3 scripts/docling/build_input_taxonomy_artifact_manifest.py \
  --artifact-root "$RUN_ROOT"

ARCHIVE_ROOT="/Volumes/INDEPENDENT_BACKUP/text-bio-living-review"
python3 scripts/archive_living_review_artifacts.py create \
  --source-root "$RUN_ROOT" --archive-root "$ARCHIVE_ROOT" \
  --receipt-dir data/living_catalog/archives --label "$RUN_ID" \
  --storage-class independent_backup
RECEIPT="$(ls -t data/living_catalog/archives/${RUN_ID}__*.json | head -1)"
python3 scripts/archive_living_review_artifacts.py verify --receipt "$RECEIPT"

python3 scripts/archive_living_review_artifacts.py restore \
  --receipt "$RECEIPT" --destination /empty/path/restored_run
EXPECTED_ACCEPTED_RECORDS="$(jq '.records | length' "$RUN_ROOT/10_eligibility/accepted_records.json")"
.venv-docling/bin/python scripts/docling/validate_canonical_profile_manifest.py \
  --manifest /empty/path/restored_run/11_docling_vlm/profiles/manifests/canonical_docling_profile_manifest.csv \
  --original-run-root "$RUN_ROOT" --restored-run-root /empty/path/restored_run \
  --expected-records "$EXPECTED_ACCEPTED_RECORDS"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"

git diff --check
python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor

git status --short
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
GITHUB_RUN_ID="$(gh run list --workflow deploy-input-representation-atlas.yml --branch main --limit 10 --json databaseId,headSha --jq ".[] | select(.headSha == \"$COMMIT\") | .databaseId" | head -1)"
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

Do not rebuild `artifact_manifest.csv` after local publication. If deployment fails, freeze further review work, record an incident, and retry the same commit/artifact; withdrawal must restore `current.json` and the atlas together through a new rollback commit.

**Remaining Execution Gaps**

1. Actual `doctor`, method-lock verification and preflight results remain unknown by design; static inspection cannot establish runtime health.
2. API credential validity, provider access, model availability, GitHub authentication and push permissions are external prerequisites.
3. `/Volumes/INDEPENDENT_BACKUP/...` is an example, not a documented verified mount. An unfamiliar operator needs the actual physically independent storage location.
4. `OPERATOR`, authorized manual resolvers, and authority for lawful manual full-text acquisition are unspecified.
5. A zero-accepted update leaves the atlas unchanged. The Pages workflow is path-filtered to atlas/workflow changes, so a publication commit may produce no workflow run, while completion still requires the exact commit in `deployment.json`. No zero-catalog-change deployment procedure is documented.
6. The restore example derives `EXPECTED_ACCEPTED_RECORDS` from the original run root; that command is unusable when the original root is what was lost. No alternate documented command derives it from the restored tree.
7. “Approved provider” alternatives to SerpAPI are not enumerated, and no approval authority is named.
8. The rollback example pushes a `codex/rollback-*` branch, but the Pages workflow does not trigger on that branch; the exact promotion/dispatch procedure is missing.
9. Manual declarations are schema-defined but no editor/creation command or independent dual-review requirement is prescribed.
10. Automated late-indexing lookback and a multi-operator filesystem lock remain explicitly absent, limiting recall completeness and concurrent reproducibility.
