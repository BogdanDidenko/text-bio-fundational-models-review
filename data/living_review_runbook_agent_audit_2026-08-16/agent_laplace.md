I’ll inspect only the runbook and the static repository files it explicitly points to. I’ll distinguish inspection from the hypothetical operator commands, and I will not execute any pipeline, network, generation, publication, or repository-changing command.
The runbook defines 18 named stages and a strict cursor rule: the next start is the day after the published inclusive `search_end`, while the end is the last fully elapsed calendar day in `Europe/Kiev`. I’m now checking the published state, locked configuration, and protocol text for the exact payload fields and role topology.
A material comparability issue is emerging: the frozen screening runner’s visible `safe_record()` keeps only `title` and `abstract`, while the full-text input builder emits `selected_full_text_sections` as a separate field. I’m tracing the orchestrator’s exact invocation to determine whether it explicitly maps those sections into the runner or whether the documented full-text payload is not actually executable as stated.
Static state confirms the published atlas source matches `current.json`, but the prior run manifest predates the current method-lock fields and there is no completion record under `data/living_catalog/releases/update_2026-08-09/`. Because the runbook says a run is complete only after that record exists, an unfamiliar operator must treat the initial `doctor` result as a hard gate rather than assuming the next interval is executable.
The boundary and release contracts are now mapped. One additional publication-order concern needs checking: the archive is required before `publish`, while `publish` changes the run manifest; I’m verifying whether that manifest is part of the archived ledger so the final receipt can actually match the post-publication run root.
# Silent Dry Run

The commands below are the commands I would use; none is reported as executed.

**1. Cursor And Interval**

Published state: [current.json](/Users/bogdan.didenko/lpnu/review/data/living_catalog/current.json)

- Published inclusive cursor: `search_end = 2026-08-09`
- Next `date_from`: `2026-08-10`
- Current date: `2026-08-16` in `Europe/Kiev`
- Last fully elapsed Kyiv calendar day: `2026-08-15`
- Exact next inclusive interval: **`2026-08-10` through `2026-08-15`**
- Run ID: **`update_2026-08-15`**
- `2026-08-16` must not be searched because it is unfinished.
- The runbook records that closed intervals have no automated late-indexing lookback.

The current atlas `generated_from` matches the current `taxonomy_root`. The frozen taxonomy hash is `b36c0261...693bf9`; the current method-lock file hash is `d9ecf9d0...410f5`.

There is, however, no prior completion record for `update_2026-08-09`, and its only repository receipt is marked `local_secondary`, not `independent_backup`. This is an unresolved initial gate discussed below.

**2. Initial Procedure**

```bash
cd /Users/bogdan.didenko/lpnu/review

cat data/living_catalog/current.json
cat data/living_catalog_updates/update_2026-08-09/run_manifest.json

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

python3 scripts/run_living_review_pipeline.py scholar-capture \
  --date-to "$END"

python3 scripts/run_living_review_pipeline.py scholar-validate \
  --date-to "$END"

python3 scripts/run_living_review_pipeline.py preflight \
  --date-to "$END" --through-stage report
```

Proceed only if `doctor` is healthy, method-lock verification returns `ok: true`, the plan reports `date_from=2026-08-10`, `date_to=2026-08-15`, `run_root=data/living_catalog_updates/update_2026-08-15`, the prior taxonomy matches the atlas, and every required preflight check has `ready: true`.

The normal execution command is:

```bash
python3 scripts/run_living_review_pipeline.py run \
  --date-to "$END" --manage-server
```

**3. All 18 Boundaries**

| # | Stage | Required input and success/denominator | Failure or recovery |
|---:|---|---|---|
| 1 | `search` | Dated config; eight sources: PubMed, Scopus, OpenAlex, Semantic Scholar, arXiv, Europe PMC bioRxiv/medRxiv, SpringerNature, Google Scholar. Every subquery/page must complete. `raw hits = sum(completed source exports)`. | Missing credentials, failed pagination, malformed responses, or absent Scholar bundle block the stage. Retry `search`; never record failure as zero. |
| 2 | `deduplicate` | Eight exports plus search summary. Export counts must reconcile. `within-update unique = raw hits - duplicate members`; merge/conflict ledger retained. | Repair an invalid export upstream or resume `deduplicate`; identifier/title conflicts remain visible. |
| 3 | `prepare-records` | Update clusters, every published master artifact, Crossref audit, optional supplemental declaration. `new = unique - cumulative matches - Crossref hidden duplicates`. | Resolve every generated cross-dedup conflict in the declared manual JSON, then resume. |
| 4 | `enrich-abstracts` | New records. Every missing/short abstract must be attempted; title fallback needs year or author corroboration. `screening input + unusable-abstract exclusions = new records`. | Retry providers with the same rules. A bounded/incomplete diagnostic result cannot become canonical. |
| 5 | `abstract-screening` | Exact abstract payload below. Every input must have one final `INCLUDE`, `EXCLUDE`, or `UNCERTAIN`. `final decisions = abstract screening inputs`. | Retry incomplete batches with identical runner, prompts, model, and schema. |
| 6 | `fulltext-candidates` | Final abstract decisions plus canonical record crosswalk. `candidates = abstract INCLUDE + abstract UNCERTAIN`, one unique candidate per decision. | Correct only through the upstream declared resolution path. |
| 7 | `fulltext-download` | Candidate metadata and attempt ledger. Every candidate gets exactly one validated PDF/HTML, terminal `not_retrieved*`, or blocking technical/XML disposition. | Retry technical failures or provide a lawful main article in `manual_fulltexts.json`. Supplements, landing pages, and XML-only files are invalid. |
| 8 | `docling-screening` | Validated supported PDF/HTML subset. One identity-corroborated no-VLM profile per supported payload. `profiles = retrieved supported subset`; terminal non-retrieval remains only in the retrieval denominator. | Replace wrong/corrupt source through retrieval, or rerun Docling unchanged. |
| 9 | `graph-sections` | Complete no-VLM profiles. Each profile must yield grounded `data_source` and `input_representation` heading-bounded sections. | Supply canonical heading selectors from the generated override template; no pasted text or whole document. |
| 10 | `fulltext-screening` | Exact full-text payload below. `final decisions = valid section inputs`; every retrieved profile must have a valid automatic or manual pair. | Retry frozen batches or complete section overrides first. |
| 11 | `eligibility-resolution` | Full-text decisions and optional manual CSV. No unresolved record remains. `accepted + excluded = section-screened records`. | Add decision, evidence, resolver, and timestamp only to `manual_resolution.csv`, then resume. |
| 12 | `docling-vlm` | Newly accepted records with validated PDFs. `complete VLM profiles = accepted records`. | HTML-only acceptance blocks; obtain an authorized PDF and resume from `fulltext-download`. |
| 13 | `taxonomy-discovery` | Complete new VLM profiles. Direct open discovery sees full documents without taxonomy family labels. `discovery records = complete VLM profiles`. | Retry failed document shards under the same model/schema; do not synthesize taxonomy here. |
| 14 | `taxonomy-classification` | Fixed inventory, taxonomy v1, three direct runs, dense audit, separate adjudication. Every route grounded; Jaccard `>=0.80`, family agreement `>=0.90`, alpha `>=0.80`; all dense-only candidates dispositioned. | Any failed threshold requires a reviewed whole-cohort rerun under one version. No record-level patching. |
| 15 | `crop-validation` | Accepted routes, model registry, native figures. Two selectors, adjudicator, cropper. `one crop or no-suitable-figure disposition per included model`. | Retry failed model batches while retaining all responses and source-figure identity. |
| 16 | `snapshot` | Prior snapshot/crops plus validated update taxonomy/crops and corpus roots. Exact route/evidence parity and source hashes. `cumulative = prior + accepted update` under explicit linkage. | Repair the earliest invalid upstream stage. Never edit totals. Zero accepted records produce a no-change marker. |
| 17 | `atlas` | Snapshot, all actual VLM corpus roots, prior UI shell/assets. Build counts must match snapshot; desktop/mobile, iteration filter, assets, and console QA pass. | Fix builder/UI code, rebuild this stage, and repeat browser QA. Published atlas remains untouched. |
| 18 | `report` | All stage summaries and dispositions. Every ledger identity above must reconcile; retrieval branches must be mutually exclusive. | Fix the source artifact or report generator. Never hand-edit PRISMA counts. |

After any interruption or non-zero/ambiguous result:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID"
```

Resume the exact first blocking stage reported by `doctor`:

```bash
STAGE=FIRST_BLOCKING_STAGE_FROM_DOCTOR
python3 scripts/run_living_review_pipeline.py run \
  --run-id "$RUN_ID" --from-stage "$STAGE" --manage-server
```

Do not use `--force` for ordinary recovery.

**4. Screening Payloads And Topology**

Abstract model-facing record, as implemented by the frozen legacy runner:

```json
{
  "record_id": "rec_NNNNNN",
  "title": "...",
  "abstract": "...",
  "doi": "...",
  "year": "...",
  "venue": "...",
  "sources": []
}
```

Thus the implemented payload is not literally only `title + abstract`: identifiers and bibliographic metadata are also model-visible.

Full-text model-facing record:

```json
{
  "record_id": "...",
  "candidate_id": "...",
  "source_record_id": "...",
  "source_corpus": "...",
  "title": "...",
  "abstract": "...",
  "doi": "...",
  "year": "...",
  "venue": "...",
  "sources": [],
  "selected_full_text_sections": "[data_source: heading]\n...\n\n[input_representation: heading]\n..."
}
```

`selected_full_text_sections` contains complete, untruncated heading-bounded sections. The model does not receive `selector_reason`, `section_evidence`, complete `docling_markdown`, chunks, or Graph provenance. The adjudicator receives the same record plus `first_pass_outputs` containing scope, architecture, and Python-gate results.

Both passes use:

1. Separate scope-reviewer invocation, `gpt-5.4-mini`.
2. Separate architecture-reviewer invocation, `gpt-5.4-mini`.
3. Deterministic Python criterion gate.
4. Separate `gpt-5.4-mini` adjudicator only for conflicts/uncertainty.
5. Batch size `8`; adjudicator batch size `6`.
6. Abstract legacy concurrency `64`; full-text concurrency `8`.
7. Full-text retries `3`, timeout `1800` seconds, with failed attempts retained.

**5. Modes And Reuse**

| Component | Required mode | Reuse contract |
|---|---|---|
| No-VLM Docling | OCR off; accurate table structure/cell matching; page/picture images at scale `2.0`; formula enrichment off; full headings/text. PDF and validated full HTML allowed. | Existing profile may be reused only with matching source/profile hashes and unchanged locked contract. Wrong or stale profiles are not patched. |
| VLM Docling | Fresh PDF conversion for each newly accepted report, model `gpt-5.5`; native JSON, Markdown, figures, captions, and picture descriptions retained together. | Do not upgrade/patch the no-VLM profile. HTML-only reports cannot be reused as canonical VLM profiles. |
| Docling Graph sections | `direct`, `detailed` provenance, model `openai/gpt-5.4-mini`; complete heading-bounded sections for both targets. | Workspace reuse requires matching source SHA, Docling JSON SHA, Graph code/contract, model, schema, and stage. Otherwise preserve it and create a new sibling attempt. |
| Taxonomy discovery | `inventory`, direct open discovery, replicate `incremental_open_r1`, no frozen labels in extraction. | Prior taxonomy is not resynthesized; discovery results are new-cohort evidence. |
| Taxonomy classification | `incremental_frozen_taxonomy`; taxonomy v1; three direct replicates; dense `scoped` fill with `standard` deduplication; blinded adjudication; temperature `0`; no truncation. | Existing routes are preserved through snapshot merge. Failed agreement requires whole-cohort rerun, not selective reuse. |
| Crops | Two blind selectors, separate adjudicator, cropper; `gpt-5.4-mini`; native figures only. | Prior model dispositions are passed as an exclusion ledger and are not silently replaced. |
| Snapshot | Incremental atomic merge of prior snapshot and update; exact ID/hash reconciliation. | Reuse prior cumulative snapshot and crops. Whole-cohort reruns must use `freeze_full_cohort_snapshot.py`, never this incremental merge. |
| Atlas | Copy current validated UI shell into staged run output; rebuild from snapshot and every real corpus root; local HTTP/Playwright QA. | UI shell and prior assets may be reused. A combined manifest cannot replace corpus roots containing `figures/`. Published files change only at `publish`. |

Successful full-text downloads may survive retrieval retries. Recomputed Docling, Graph, taxonomy, and adjudication outputs are preserved under `preserved_stage_outputs/`; they are evidence, not automatically mixed into a new attempt.

**6. Manual Gates**

- Scholar: `00_search/google_scholar_provider_export.json`, conforming to `protocol/google_scholar_provider_export_schema.md`; normal interface is `scholar-capture` then `scholar-validate`.
- Cross-dedup: `02_records/manual_cross_dedup_resolutions.json`; each row requires `update_cluster_id`, `decision`, `rationale`, `resolver`, `resolved_at`.
- Full text: `05_fulltext/manual_fulltexts.json`; each row requires `candidate_id`, absolute `file`, `source_url`, `retriever`, `retrieved_at`.
- Sections: `08_section_input/manual_section_overrides.json`, schema version 2; exact canonical Markdown path/hash plus heading trails for both target types.
- Eligibility: `10_eligibility/manual_resolution.csv`; columns are `record_id,manual_decision,rationale,resolver,resolved_at`, with decision `INCLUDE` or `EXCLUDE`.

After an edit, resume the blocked stage without `--force` and rerun `doctor`.

**7. Archive, Publication, Deployment, Completion**

After stage 18 and before publication:

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

Pre-publication and local promotion:

```bash
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py status --run-id "$RUN_ID" \
  > "/tmp/${RUN_ID}_status.json"
git diff --check

python3 scripts/run_living_review_pipeline.py publish --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor
```

Documented staging and deployment:

```bash
git status --short
git diff --check
git add data/living_catalog/current.json
git add "data/living_catalog_updates/${RUN_ID}"
git add docs/input-representation-atlas
git add protocol/PRISMA_protocol.md protocol/prisma_search_screening_log_2026-07-07.md

python3 scripts/docling/build_input_taxonomy_artifact_manifest.py \
  --artifact-root "data/living_catalog_updates/${RUN_ID}"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID"
python3 scripts/run_living_review_pipeline.py doctor --run-id "$RUN_ID" \
  --repository-checkout

git status --short
git diff --cached --check
git diff --cached --stat
git commit -m "Update living review through ${END}"
git push origin main

gh run list --workflow deploy-input-representation-atlas.yml --limit 5
gh run watch RUN_ID_FROM_GITHUB --exit-status

COMMIT=$(git rev-parse HEAD)
python3 scripts/run_living_review_pipeline.py verify-live \
  --expected-commit "$COMMIT" --check-assets
python3 scripts/run_living_review_pipeline.py doctor
```

Completion, using the fixed screenshots produced by the atlas QA script:

```bash
GITHUB_RUN_ID=RUN_ID_FROM_GITHUB
OPERATOR="OPERATOR"

python3 scripts/run_living_review_pipeline.py verify-live \
  --run-id "$RUN_ID" --expected-commit "$COMMIT" --check-assets \
  --record-completion --workflow-run-id "$GITHUB_RUN_ID" \
  --operator "$OPERATOR" \
  --screenshot /tmp/atlas-graph-desktop.png \
  --screenshot /tmp/atlas-graph-mobile.png

git add "data/living_catalog/releases/${RUN_ID}/completion_record.json"
git diff --cached --check
git commit -m "Record verified release evidence for ${RUN_ID}"
git push origin HEAD
```

**8. Reproducibility Blockers And Ambiguities**

1. The prior published run has no `completion_record.json` and only a `local_secondary` receipt. The runbook says that update is not complete, but `doctor` does not enforce the missing completion record for this legacy run.
2. The full-text runner `scripts/run_codex_screening_pipeline.py` and `protocol/screening_prompt_templates/*` are absent from `living_review_method_lock_v1.json`, despite the runbook calling selected-section screening hash-pinned.
3. Abstract screening uses the locked legacy runner/prompts, while full-text screening uses a different runner and different prompts. “Same role topology” is true; “same/hash-pinned runner and prompts” is not.
4. The current full-text prompts require `evidence_for_*` and `boundary_case`, while the runner’s output schema disallows those fields and instead requires `evidence_snippet`.
5. The declared abstract payload is “exactly title + abstract,” but actual model-facing JSON also includes DOI, year, venue, sources, and record ID.
6. Publication requires an independent archive before `publish`, but `publish` changes `run_manifest.json`. That file is included in `artifact_manifest.csv`. Section 10 then rebuilds the manifest without instructing the operator to recreate and reverify the independent archive, leaving the final manifest unmatched to its receipt.
7. No exact post-restore commands are specified for profile-contract validation and canonical-manifest validation, although both are required.
8. The denominator identities are documented but there is no dedicated command that asserts all identities before publication; the report generator mainly derives counts.
9. Remote byte verification is specified, but no exact command is given for visual browser QA against the deployed remote URL. The documented screenshots are generated against the staged local server.
10. `ARCHIVE_ROOT`, operator/resolver identity, actual Git branch, workflow run ID, credentials, and lawful manual full-text locations remain runtime prerequisites.
11. There is no multi-operator filesystem lock and no retrospective late-indexing search. These are acknowledged limitations affecting operational safety and recall comparability.

Until items 1–6 are explicitly resolved or versioned, an unfamiliar agent cannot execute this iteration with the reproducibility and method comparability claimed by the runbook.
