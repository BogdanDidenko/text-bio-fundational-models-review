I’ll treat the runbook as the sole authority, trace only its explicit static references, and distinguish verbatim prescribed commands from any unresolved placeholders. I will run no pipeline, network, server, model, artifact-generation, or repository-writing command.
The runbook defines a strict state machine with 18 named stages and makes `doctor` plus manifest hashes authoritative. I’m now extracting the per-boundary reconciliation rules, role topology, reuse limits, and post-report publication sequence so the dry run does not collapse distinct gates into a generic “run pipeline” step.
Static tracing exposes a material comparability issue: abstract screening is routed to the hash-pinned legacy runner, while full-text screening is routed to `scripts/run_codex_screening_pipeline.py`. I’m checking whether that full-text runner and its actual prompt files are independently covered by the method lock, because the runbook describes both passes as locked.
The current cursor and atlas pointer agree statically, but the previous published run does not have the completion record required by the runbook, and its only visible archive receipt is labeled `local_secondary`, not `independent_backup`. I’m incorporating those as no-go findings rather than assuming the prior publication was fully closed.
All commands below are prospective only. The dry run is based on [LIVING_REVIEW_RUNBOOK.md](/Users/bogdan.didenko/lpnu/review/protocol/LIVING_REVIEW_RUNBOOK.md) and its explicit static references.

**1. Cursor And Interval**

The local published-cursor authority, [current.json](/Users/bogdan.didenko/lpnu/review/data/living_catalog/current.json), records:

- Published inclusive `search_end`: `2026-08-09`
- Next `date_from`: `2026-08-10`
- Current date: `2026-08-16` in `Europe/Kiev`
- Last fully elapsed calendar day: `2026-08-15`
- Exact next inclusive interval: **`2026-08-10` through `2026-08-15`**
- Run ID: **`update_2026-08-15`**

The unfinished day `2026-08-16` must not be searched. The run report must retain the documented limitation that no retrospective late-indexing lookback is automated.

**2. Prospective Commands**

Initial doctor, method lock, planning, Scholar capture, and preflight:

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

python3 scripts/run_living_review_pipeline.py plan --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-capture --date-to "$END"
python3 scripts/run_living_review_pipeline.py scholar-validate --date-to "$END"
python3 scripts/run_living_review_pipeline.py preflight \
  --date-to "$END" --through-stage report
```

Proceed only if `doctor` is healthy, method verification returns `ok: true`, the plan says `2026-08-10..2026-08-15`, `run_root` is `data/living_catalog_updates/update_2026-08-15`, prior taxonomy equals atlas `generated_from`, and every required preflight check has `ready: true`.

Canonical execution and recovery:

```bash
python3 scripts/run_living_review_pipeline.py run \
  --date-to "$END" --manage-server

python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID"

# Replace STAGE with doctor.run.first_blocking_stage.
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage STAGE --manage-server
```

After a manual declaration, resume without `--force`. `--force` is reserved for a documented scientific invalidation and invalidates that stage and everything downstream.

Archive and independent verification after all 18 stages are final:

```bash
RUN_ROOT="data/living_catalog_updates/${RUN_ID}"
ARCHIVE_ROOT="/Volumes/INDEPENDENT_BACKUP/text-bio-living-review"

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

python3 scripts/archive_living_review_artifacts.py verify \
  --receipt "$RECEIPT" \
  --archive /path/to/copied/archive.tar.zst

python3 scripts/archive_living_review_artifacts.py restore \
  --receipt "$RECEIPT" \
  --destination /empty/path/restored_run
```

Pre-publication, local promotion, Git, deployment, and completion:

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
git add docs/input-representation-atlas
git add protocol/PRISMA_protocol.md protocol/prisma_search_screening_log_2026-07-07.md
git status --short
git diff --cached --check
git diff --cached --stat

python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID" \
  --repository-checkout

git commit -m "Update living review through ${END}"
git push origin main
gh run list --workflow deploy-input-representation-atlas.yml --limit 5
gh run watch GITHUB_RUN_ID --exit-status

COMMIT=$(git rev-parse HEAD)
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$COMMIT" --check-assets
python3 scripts/run_living_review_pipeline.py doctor

python3 scripts/run_living_review_pipeline.py verify-live \
  --run-id "$RUN_ID" --expected-commit "$COMMIT" --check-assets \
  --record-completion --workflow-run-id "$GITHUB_RUN_ID" \
  --operator "OPERATOR" \
  --screenshot /absolute/path/desktop.png \
  --screenshot /absolute/path/mobile.png

git add "data/living_catalog/releases/${RUN_ID}/completion_record.json"
git diff --cached --check
git commit -m "Record verified release evidence for ${RUN_ID}"
git push origin HEAD
```

Deployment failure must retain the same commit and artifact:

```bash
gh run rerun "$GITHUB_RUN_ID"
gh run watch "$GITHUB_RUN_ID" --exit-status
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$(gh run view "$GITHUB_RUN_ID" --json headSha -q .headSha)" \
  --check-assets

python3 scripts/run_living_review_pipeline.py incident \
  --run-id "$RUN_ID" --phase deployment \
  --summary "Observed failure and chosen recovery" \
  --operator "OPERATOR" --commit "COMMIT" \
  --workflow-run-id "$GITHUB_RUN_ID"
```

**3. Eighteen Stage Boundaries**

| # | Stage | Required input | Pass and denominator reconciliation | Failure/recovery |
|---|---|---|---|---|
| 1 | `search` | Dated config plus complete Scholar bundle | All eight sources and pagination paths complete; `raw hits = sum(completed exports)` | Fix access or matching Scholar export; resume `search`; never record failure as zero. |
| 2 | `deduplicate` | Eight validated exports | Export totals reconcile; `within-update unique = raw hits - duplicate members`; full cluster/merge ledger retained | Repair invalid export or resume `deduplicate`; keep DOI/title conflicts visible. |
| 3 | `prepare-records` | Update clusters plus every published master | DOI/PMID/preprint/title comparison complete; `new = unique - cumulative matches/exclusions` | Fill generated cross-dedup resolution file and resume. |
| 4 | `enrich-abstracts` | New-record cohort | Every missing/short abstract attempted; usable cohort plus explicit exclusions equals input | Retry providers; rejected and diagnostic candidates remain logged. |
| 5 | `abstract-screening` | Declared title/abstract payload | Every usable record has one final structured result; `abstract-screened = final decisions` | Resume unchanged runner/model/schema; never merge changed prompts. |
| 6 | `fulltext-candidates` | Final abstract decisions | Stable one-to-one IDs; candidates equal abstract `INCLUDE + UNCERTAIN` | Correct decisions only through their declared resolution path. |
| 7 | `fulltext-download` | Candidate manifest | Each candidate has one validated PDF/HTML, terminal not-retrieved status, or blocking disposition; retrieval partition is mutually exclusive | Retry providers or declare lawful main article; wrong PDFs, supplements, XML, and login pages are invalid. |
| 8 | `docling-screening` | Validated supported PDF/HTML subset | Exactly one identity-corroborated no-VLM profile per supported retrieved report | Replace wrong source and rerun from download, or rerun Docling. |
| 9 | `graph-sections` | Complete no-VLM profiles | One-to-one Graph summaries; grounded complete sections for both targets; no root/whole-document substitutes | Complete canonical heading override and resume `fulltext-screening`. |
| 10 | `fulltext-screening` | Title, abstract, selected complete sections | One final result per valid targeted-section pair; this count is `section-screened` | Retry unchanged batches or resolve section override first. |
| 11 | `eligibility-resolution` | Full-text decisions | No unresolved rows; `accepted + excluded = resolved eligibility inputs` | Add declared CSV resolution with evidence, resolver, and timestamp. |
| 12 | `docling-vlm` | Newly accepted records with PDFs | Fresh complete VLM profile per accepted report; `taxonomy records = accepted records with profiles` | Obtain authorized PDF for HTML-only acceptance; rerun from download. |
| 13 | `taxonomy-discovery` | Complete new VLM profiles | All records yield open route inventory and stable registry without family labels | Retry unchanged failed document batches. |
| 14 | `taxonomy-classification` | Fixed inventory plus taxonomy v1 | Three direct runs, dense audit, adjudication, route grounding; Jaccard ≥0.80, family agreement ≥0.90, alpha ≥0.80 | Stop and perform reviewed whole-cohort rerun; never patch records or select a convenient replicate. |
| 15 | `crop-validation` | Accepted routes plus native figures | One crop or explicit `no_suitable_figure` per included model; route and source-figure identities valid | Retry failed model batches with all selector evidence retained. |
| 16 | `snapshot` | Prior snapshot plus validated update | Route/evidence IDs and counts reconcile; cumulative records equal prior plus accepted update with duplicate/version links | Repair earliest invalid upstream stage; no hand-edited totals. |
| 17 | `atlas` | Snapshot plus every actual VLM corpus root | Build counts equal snapshot; desktop/mobile, filters, assets, and console QA pass | Fix builder/UI, rebuild stage, rerun browser QA. |
| 18 | `report` | All stage summaries | Every denominator identity and mutually exclusive retrieval branch is artifact-derived | Fix source artifact or generator; never edit report counts. |

**4. Screening Payloads And Topology**

Declared evidence payloads are:

- Abstract: `title + abstract`; title-only fallback must be explicit and identity-corroborated.
- Full text: `title + abstract + complete selected_full_text_sections`.
- Forbidden full-text reviewer fields: `selector_reason`, `section_evidence`, section-selection audit, complete `docling_markdown`, and Graph evidence objects.

Actual serialized abstract reviewer records also contain `record_id`, `doi`, `year`, `venue`, and `sources`. Full-text records contain `record_id`, `candidate_id`, `source_record_id`, `source_corpus`, `title`, `abstract`, `doi`, `year`, `venue`, `sources`, and `selected_full_text_sections`. The adjudicator additionally receives `first_pass_outputs`.

Both stages use separate `gpt-5.4-mini` scope and architecture invocations, deterministic Python gate, then a separate `gpt-5.4-mini` adjudicator only for conflict or uncertainty. Scope evaluates paper type, biological modality, text component, and substantive bridge. Architecture evaluates paper type, generative model, and foundation-model evidence. Final outcomes are `INCLUDE`, `EXCLUDE`, or `UNCERTAIN`.

Abstract batches are 8, adjudicator batches 6, and legacy maximum workers 64. Full-text batches are 8, adjudicator batches 6, workers 8, three attempts, and 1,800-second timeout.

**5. Manual Gates**

- Scholar: `00_search/google_scholar_provider_export.json`; signature, query names, page hashes, pagination end, dates, and count must match.
- Cross-dedup: `02_records/manual_cross_dedup_resolutions.json`, wrapper `{"schema_version":1,"records":[...]}` with `update_cluster_id`, `decision`, `rationale`, `resolver`, `resolved_at`.
- Manual full text: `05_fulltext/manual_fulltexts.json`, wrapper `{"records":[...]}` with `candidate_id`, absolute `file`, `source_url`, `retriever`, `retrieved_at`.
- Section override: `08_section_input/manual_section_overrides.json`, schema version 2 with exact canonical Markdown path/hash and heading trails covering `data_source` and `input_representation`.
- Eligibility: `10_eligibility/manual_resolution.csv` with `record_id,manual_decision,rationale,resolver,resolved_at`.

Generated templates determine the exact candidates. After editing, resume the reported blocking stage without `--force`, then rerun `doctor`.

**6. Processing Modes And Reuse**

| Component | Required mode | Reuse boundary |
|---|---|---|
| Docling screening | No VLM; OCR off, accurate tables/cell matching, page/picture images at 2.0, no formula enrichment, no truncation | Supported validated PDF/HTML only; profile must match source identity and hashes. |
| Docling VLM | Fresh PDF profile using `gpt-5.5` | Never patch the no-VLM profile; HTML-only acceptance cannot be reused as canonical VLM evidence. |
| Docling Graph | Direct extraction, detailed provenance, complete heading-bounded `data_source` and `input_representation` sections | Workspace reusable only when source, Docling JSON, code/contract, model, schema, and stage all match. |
| Taxonomy | `incremental_frozen_taxonomy`; open discovery, three direct classifications, dense scoped fill, separate adjudicator, taxonomy v1 | Prior taxonomy definitions remain fixed; failed thresholds require one complete version-consistent cohort rerun. |
| Crop | Two blind selectors, separate adjudicator and cropper, `gpt-5.4-mini` | Existing dispositions are not silently replaced; only native-profile figures and accepted route IDs are valid. |
| Snapshot | Incremental merge of prior snapshot plus accepted cohort | Prior routes persist; never fake an empty prior snapshot or use incremental merge for a whole-cohort rerun. |
| Atlas | Staged rebuild from snapshot, prior UI shell, and all real corpus roots | Live atlas is untouched until `publish`; a combined manifest cannot replace figure-bearing corpus roots. |

Hash-valid completed stages may be skipped. Successful downloads may survive retrieval retries. Failed LLM attempts and expensive outputs are preserved, but may enter a new attempt only with matching hashes and the same locked contract. Outputs from routine, resume, supplemental, and whole-cohort modes must not be mixed.

**7. Reproducibility Blockers**

This is presently a **no-go for an unfamiliar operator** until these are resolved:

1. The current published update has no `data/living_catalog/releases/update_2026-08-09/completion_record.json`. Its visible run archive receipt is `local_secondary`, not `independent_backup`. The current whole-cohort correction archive is also `local_secondary`. That does not satisfy the runbook’s completion and retention rules.
2. Full-text screening invokes `scripts/run_codex_screening_pipeline.py` and `protocol/screening_prompt_templates/*`, but those files are absent from [living_review_method_lock_v1.json](/Users/bogdan.didenko/lpnu/review/protocol/living_review_method_lock_v1.json). Only the different legacy abstract runner/prompts are locked. Full-text comparability can therefore change without method-lock failure.
3. The runbook calls the evidence payload “exactly” title/abstract or title/abstract/sections, while the actual model-facing JSON includes identifiers and bibliographic fields, and the adjudicator includes first-pass outputs. The authoritative payload contract is therefore inconsistent.
4. The archive is created before `publish`, but `publish` mutates `run_manifest.json`. Section 10 then directs rebuilding the artifact ledger without creating a new matching independent archive. The instructions do not define one immutable post-publication archive sequence.
5. The specified completion record promises method ID, method-lock hash, independent receipt, source configuration, and counts, but the implementation’s completion object does not directly record those fields.
6. `verify-live` performs hash/HTTP verification, not the required remote browser interaction checks. No exact remote visual-QA command or screenshot-generation command is prescribed.
7. Restore aftercare names profile-contract validation and canonical-manifest checks but gives no exact commands or selection rule for the “relevant” manifest.
8. `ARCHIVE_ROOT`, operator identity, screenshot paths, GitHub workflow run ID, branch transition to `main`, and deterministic selection of the workflow run remain unresolved operator inputs.
9. Late indexing, lack of a multi-operator lock, and non-transactional local/remote publication remain documented comparability and operational risks.
