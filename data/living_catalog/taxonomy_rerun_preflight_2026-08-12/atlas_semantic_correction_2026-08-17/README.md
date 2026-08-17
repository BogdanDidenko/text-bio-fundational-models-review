# Interactive Input-Representation Taxonomy Atlas

This static GitHub Pages application renders the accepted 55-record corpus as an
explicit taxonomic graph:

`root -> carrier family -> mechanism subtype -> exact membership group -> model`

The graph contains:

- one taxonomy root, five carrier families, and 15 operational subtypes;
- 47 exact subtype-membership groups;
- 109 unique model nodes;
- 467 lifecycle/task configurations and 585 grounded input routes;
- 89 exact-preview-validated model-specific original-paper crops;
- 20 explicit `no_suitable_figure` cases where the papers had text evidence
  but no figure that responsibly illustrated the input route.

Each model node separates two visual roles:

- **Original-paper crop**: source pixels shown through a recorded normalized
  crop viewport, with figure, page, caption, confidence, SHA-256, and rationale.
- **Illustrative input**: a small explanatory example of how the route's carrier
  may look. It is always labeled as non-evidence.

Every model occurs once and belongs to exactly one membership group defined by
its complete subtype set. Subtypes connect to the group, and the group connects
to its models. The interactive layout keeps one canonical node for every
carrier family on the central spine and mirrors only subtype layout ports on
the left and right to balance the graph without duplicating groups or models. A
focused model exposes the complete grounded route inventory with source object,
transformation chain, model-visible form, quote, heading, and pages.

Each model also carries the review iteration encoded by its canonical record ID.
The **Review iteration** filter isolates the exact records added in a living-review
update, including the latest `2026-08-09` iteration, across the graph, model
index, and evidence table. The atlas contract retains the complete `record_id`
list, model count, and route count for every selectable iteration.

## Rebuild

```bash
.venv-docling/bin/python scripts/build_input_representation_atlas.py \
  --taxonomy-root data/living_catalog/taxonomy_rerun_preflight_2026-08-12/snapshot_full_55_semantic_correction_2026-08-17 \
  --crop-ledger analysis/atlas_exact_preview_validation_2026-08-17/proposed_crossvalidated_crop_ledger.json \
  --output-dir docs/input-representation-atlas \
  --prior-atlas-root docs/input-representation-atlas \
  --corpus-root "$DOCLING_WORKSPACE/data/living_catalog/taxonomy_rerun_preflight_2026-08-12/baseline_vlm_profiles" \
  --corpus-root data/living_catalog_updates/update_2026-08-09/11_docling_vlm/profiles \
  --corpus-root data/living_catalog_updates/update_2026-08-09/11_docling_vlm_manual_recall_xunzi_2026-08-11/profiles \
  --artifact-root "$DOCLING_WORKSPACE"
```

The full-cohort run method, retained logs, acceptance metrics, profile hashes,
crop dispositions, and immutable snapshot are documented under
`data/living_catalog/taxonomy_rerun_preflight_2026-08-12/`. The deterministic
site build consumes only the frozen snapshot and crop ledger; it makes no LLM
calls.

Build integrity results are written to `data/build_report.json`.

## Social preview

The GitHub Pages entrypoint includes Open Graph and Twitter Card metadata for a
1200 x 630 large-image preview. The image is generated from the actual rendered
atlas graph rather than a separate diagram.

After starting a static server for `docs/input-representation-atlas/`, rebuild
the preview with:

```bash
NODE_PATH=/path/to/node_modules node \
  scripts/render_input_representation_atlas_social_preview.mjs \
  http://127.0.0.1:8765/
```
