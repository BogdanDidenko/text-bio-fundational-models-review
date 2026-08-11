# Search-to-Atlas Pipeline Audit

**Audit date:** 2026-08-09  
**Purpose:** Connect the executed 52-record review to the incremental living-review implementation.

## Executed baseline

The historical review is recoverable as one evidence chain rather than a set of
independent experiments:

`7 databases -> 7,531 hits -> 4,802 unique/new records -> 4,577 title/abstract screens -> 250 full-text candidates -> 235 retrieved reports -> 221 complete-section screens -> 52 accepted records / 51 studies -> 111 models -> 376 task-input configurations -> 489 grounded input routes -> 79 validated model-specific crops + 32 explicit no-suitable-figure dispositions`

The last completed update covered 2026-06-11 through 2026-07-06. The next
non-overlapping search interval therefore begins on 2026-07-07.

## Historical-to-living mapping

| Review operation | Executed evidence | Living implementation |
|---|---|---|
| Database-specific search | `scripts/search_config_update_2026-07-06.json`, `scripts/reproduce_search.py`, and dated exports under `analysis/codex_screening_run_artifacts_20260706/inputs/` | `build_search_update_config.py` advances only date clauses; `reproduce_search.py` runs all seven enabled sources and records exact queries and counts. |
| Within-window and cumulative deduplication | Dated `deduplication_log.csv`, Crossref audits, and `new_records_after_cross_dedup_crossref_checked.json` | `deduplicate.py` followed by `prepare_incremental_records.py`; ordered DOI/PMID/arXiv/title matching plus logged Crossref checks for DOI-less records. |
| Abstract acquisition and first screening | Three preserved Codex runs and role-log archives under `analysis/codex_screening_run_artifacts_20260706/` | Abstract enrichment followed by `run_codex_screening_pipeline.py` in `title_abstract` mode. Scope and architecture are separate prompt roles, followed by a deterministic Python gate and an adjudicator. |
| Full-text acquisition | Retrieval manifests and the final 235-report corpus inventory | Parallel lawful OA retrieval, payload-signature validation, PDF-first selection, HTML fallback, and a declared manual/browser ingestion manifest. Every failed URL and unsupported payload remains in the run audit. |
| Screening Docling profiles | No-VLM conversion and coverage artifacts under `data/docling_include_no_vlm_2026-07-09*` and `data/docling_uncertain_*` | Fresh no-VLM Docling conversion with accurate tables, cell matching, page/picture images at scale 2.0, no OCR, and no formula enrichment. |
| Target-section grounding | Direct Graph evidence and `data/fulltext_screening_context_2026-07-10_docling_graph_direct_all235_clean_both_targets/` | Direct Docling Graph extraction of `data_source` and `input_representation`; complete heading-boundary sections are reconstructed, deduplicated, and rejected if root/full-document-like. Provenance is kept outside the reviewer payload. |
| Second screening and resolution | `data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10/` and its six-row manual layer | The same agent topology in `full_text_sections` mode receives only title, abstract, and complete selected sections. Graph failures and residual `UNCERTAIN` cases stop at explicit manual gates. |
| Accepted VLM Docling corpus | `data/docling_include_vlm_52_2026-07-10_nolimits/` | Newly accepted reports are reconverted as complete native profiles with Codex VLM picture descriptions; no-VLM profiles are not patched in place. |
| Route discovery and taxonomy coding | `data/input_representation_taxonomy_2026-07-11/`: 583 open candidates, three direct runs, 2,208 dense candidates, adjudication, 489 final grounded routes | Open direct discovery remains label-free. New routes are coded against frozen taxonomy v1 in three direct replicates, audited by dense Graph extraction, and blindly adjudicated. Failed agreement or grounding checks block publication. |
| Figure selection and crop validation | `data/input_representation_atlas_crop_crossvalidation_2026-07-12/` | Every new source figure is shown to two blind selectors; a third role adjudicates and a cropper produces normalized coordinates. Existing model dispositions remain immutable. |
| Visual catalog | `docs/input-representation-atlas/` | Prior and new registries, routes, provenance, profiles, and crop dispositions are merged into a staged snapshot. The atlas is rebuilt and browser-tested before an explicit atomic publish. |

## Incremental control plane

`scripts/run_living_review_pipeline.py` is the single entry point. Its 18
resumable stages own versioned directories below
`data/living_catalog_updates/update_<date>/`. Each stage stores commands,
stdout/stderr, timestamps, result status, declared artifacts, and a SHA-256
inventory of every stage-owned file. Mutation of an output or log invalidates
that stage; recomputing an upstream stage invalidates every downstream status.

Publication is separate from execution. It advances the search boundary only
after screening, extraction, taxonomy validation, crop validation, atlas build,
and browser QA have completed. The state file also preserves an append-only
PRISMA update history, so failed or concurrent runs cannot create silent date
gaps or overwrite a newer catalog.

## Evidence contracts

- First screen: `record identifiers + title + abstract`.
- Second screen: `record identifiers + title + abstract + complete selected_full_text_sections`.
- Section provenance: separate Graph ledger with heading paths, quotes, pages,
  Docling references, and rejection diagnostics.
- Taxonomy: complete VLM-enriched Docling document, open route inventory,
  frozen controlled schema, and verified verbatim/native-item grounding.
- Figure layer: source images and logged crop coordinates; VLM descriptions may
  locate evidence but cannot independently establish an accepted route.
- Logs preserve model-visible prompts, structured responses, evidence snippets,
  concise rationales, errors, and retries. They do not contain or claim hidden
  chain-of-thought.
- Abstract recovery by DOI or PMID is identifier-based. Title-search recovery
  records the candidate metadata and requires title similarity plus compatible
  year or author corroboration; conflicts or missing independent corroboration
  remain rejection evidence rather than silently replacing an abstract.
- A limited abstract-fetch invocation cannot create a screening artifact while
  any missing abstract was unattempted.
- Full-text URLs obtained from a title search must satisfy the same corroboration
  rule before downloading; their accepted or rejected candidate metadata is in
  the per-record download-attempt log. Identifier-derived retrieval paths do not
  use this fallback rule.
- The `download manifest -> Docling` handoff applies PDF signature/size and HTML
  body-text thresholds on both automatic and manual paths, so landing pages do
  not become a source profile by filename or content type alone.
- Graph section recovery rejects a root-level container at 80% markdown coverage
  and every section at 90% coverage. These cases stop at the existing manual
  section gate rather than turning a near-complete paper into reviewer input.
- Incremental taxonomy classification no longer treats an unestimable
  Krippendorff alpha as passing. All declared agreement thresholds are hard
  publication gates.
- Snapshot construction requires exact route/evidence-ledger ID equality, matching
  record IDs, validated grounding, a nonempty quote, source location, and a
  verified canonical/native quote for every route.
- Graph section input is bound one-to-one to the current complete Docling
  manifest by candidate ID, artifact path, and SHA-256. Stale, mutated,
  duplicate, base-unmatched, source-mismatched, or
  missing-Markdown Graph summaries stop before manual section resolution.
- Every fresh Docling profile must corroborate its expected DOI or title in the
  converted document. The identity evidence is retained per candidate, so a
  valid but incorrectly retrieved PDF cannot silently enter screening.
- Full-text retrieval distinguishes true negative retrieval evidence, explicit
  access restrictions, XML-only payloads, and retryable transport/provider
  failures. Technical failures and unsupported XML stop the pipeline; 401/403
  outcomes remain a separately reported PRISMA not-retrieved reason.
- Publication verifies the complete hash-valid closure from `search` through
  `report`, rather than treating the report artifact alone as evidence that its
  upstream inputs remain intact.
- Atlas publication uses a durable journal and automatic rollback on the next
  runner initialization, covering a crash between public atlas promotion and the
  living-state/manifest transition.
- Manual section resolution uses schema-v2 canonical selectors. It validates the
  profile-bound Markdown path/hash and exact heading trails, then reconstructs
  the actual payload; arbitrary pasted evidence is rejected.
- PRISMA update facts partition each full-text candidate once by retrieval
  disposition. Missing Docling payloads are retained only as a labeled overlap
  audit, so they cannot be counted again as a second retrieval branch. The same
  facts distinguish confirmed source-date-filtered hits from retained
  uncertain-date recall candidates.
- Each rerun receives an append-only `attempt_###` command-log namespace. Derived
  shard/profile/classification outputs are reset before that attempt; manual
  declarations are retained and revalidated, preventing stale outputs from being
  combined with a fresh invocation.
- A published snapshot now records a source-corpus inventory. Every artifact in the
  new VLM cohort is hash-verified; unavailable historical profile manifests remain
  explicit migration limitations rather than implicit evidence of corpus completeness.
- Crop validation binds figures to route records through the canonical Docling
  profile manifest. It cannot silently convert a candidate/record identifier
  mismatch into a `no_suitable_figure` result.

## Current recovery and execution constraints

The migrated baseline VLM corpus is only partially restored. All 52 exact
Markdown documents and their inline VLM descriptions are available, as are
52 source PDFs, but native `.docling.json` documents, page images, and 447 of
506 extracted figure bitmaps are absent. The 59 atlas-retained figures are
hash-verified. This is sufficient to preserve the published taxonomy and atlas
and to append newly processed papers, but not to claim that the historical
directory is still a complete native Docling corpus. It can be regenerated from
the recovered PDFs when historical native-item operations are required.

The current machine lacks configured Scopus and both SpringerNature interface
keys, and the provider-mediated Google Scholar export has not been supplied. A
resumed 2026-08-09-boundary run completed PubMed (27), Semantic Scholar (183),
arXiv (14), and bioRxiv/medRxiv (20), retaining 244 raw records as a partial
checkpoint. The orchestrator now stops this as a manual search gate before
deduplication, so missing sources cannot be recorded as zero results or advance
an incomplete seven-source update. The machine-readable evidence is in
`data/living_catalog_updates/update_2026-08-09/00_search/search_completion_gate.json`.

The isolated `.venv-docling` has now been rebuilt under Python 3.12 from pinned
requirements. The first resolver result exposed an otherwise silent Intel-macOS
conflict (Transformers 5.8 required Torch >=2.4, while the newest available x86
wheel was Torch 2.2.2; NumPy 2.x also broke that wheel). The reproducible
constraints now use Transformers 4.57.6, NumPy 1.26.4, SciPy 1.13.1, and OpenCV
4.11.0.86. Preflight verifies every pinned version, `pip check`, Docling/Graph
imports, and a real Torch-to-NumPy conversion rather than import success alone.

The current S2 implementation has been upgraded from short generic retries to a
resumable, page-level bulk-search controller with query identity, raw response
hashes, continuation-token lineage, and non-secret 429 audit events. Google
Scholar direct scraping is no longer an acceptable canonical recovery path; a
provider-mediated, seven-query raw-response contract is required. Preflight can
now be scoped to a target stage, so search readiness is not obscured by later
Docling, crop, or atlas dependencies.

## Canonical entry points

- Configuration: `config/living_review_pipeline.json`
- Orchestrator: `scripts/run_living_review_pipeline.py`
- Full protocol: `protocol/living_review_update_pipeline_2026-08-09.md`
- Historical PRISMA log: `protocol/prisma_search_screening_log_2026-07-07.md`
- Machine-readable baseline PRISMA facts:
  `analysis/living_review_baseline_prisma_facts_2026-08-09.json`
- Current taxonomy: `data/input_representation_taxonomy_2026-07-11/`
- Current atlas: `docs/input-representation-atlas/`
