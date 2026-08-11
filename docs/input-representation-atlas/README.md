# Interactive Input-Representation Taxonomy Atlas

This static GitHub Pages application renders the accepted 55-record corpus as an
explicit taxonomic graph:

`root -> carrier family -> mechanism subtype -> exact membership group -> model`

The graph contains:

- one taxonomy root, five carrier families, and 15 operational subtypes;
- 51 exact subtype-membership groups;
- 117 unique model nodes;
- 400 lifecycle/task configurations and 519 grounded input routes;
- 85 validated model-specific original-paper crops;
- 32 explicit `no_suitable_figure` cases where the papers had text evidence
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

Each model also carries the collection date encoded by its canonical record ID.
The **Collection batch** filter can isolate a living-review update, including the
latest `2026-08-09` batch, across the graph, model index, and evidence table.

## Rebuild

```bash
.venv-docling/bin/python scripts/build_input_representation_atlas.py \
  --taxonomy-root data/living_catalog_updates/update_2026-08-09/14_snapshot_55_records_2026-08-11 \
  --crop-ledger data/living_catalog_updates/update_2026-08-09/14_snapshot_55_records_2026-08-11/crop_ledger.json \
  --output-dir docs/input-representation-atlas \
  --corpus-root data/docling_include_vlm_52_2026-07-10_nolimits \
  --corpus-root data/living_catalog_updates/update_2026-08-09/11_docling_vlm/profiles \
  --corpus-root data/living_catalog_updates/update_2026-08-09/11_docling_vlm_manual_recall_xunzi_2026-08-11/profiles
```

The complete logged crop-validation command sequence is documented in
`CROP_CROSSVALIDATION.md`; the deterministic site build consumes only its frozen
ledger.

The canonical cross-validated crop ledger is:

`data/input_representation_atlas_crop_crossvalidation_2026-07-12/final_crossvalidated_crop_ledger.json`

Its audit report and complete method description are:

- `data/input_representation_atlas_crop_crossvalidation_2026-07-12/crossvalidation_final_report.json`
- `data/input_representation_atlas_crop_crossvalidation_2026-07-12/CROP_CROSSVALIDATION.md`

All Codex subagent prompts, structured responses, stdout events, stderr, schemas,
commands, timestamps, and retry metadata are retained under:

`data/input_representation_atlas_crop_crossvalidation_2026-07-12/subagents/`

No LLM call occurs during the deterministic site build. Integrity results are
written to `data/build_report.json`.

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
