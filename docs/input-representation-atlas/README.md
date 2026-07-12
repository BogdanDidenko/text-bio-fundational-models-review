# Interactive Input-Representation Taxonomy Atlas

This static GitHub Pages application renders the accepted 52-paper corpus as an
explicit taxonomic graph:

`root -> carrier family -> mechanism subtype -> model`

The graph contains:

- one taxonomy root, five carrier families, and 15 operational subtypes;
- 111 unique model nodes and 234 explicit taxonomy links;
- 376 lifecycle/task configurations and 489 grounded input routes;
- 79 independently cross-validated model-specific original-paper crops;
- 32 explicit `no_suitable_figure` cases where the papers had text evidence
  but no figure that responsibly illustrated the input route.

Each model node separates two visual roles:

- **Original-paper crop**: source pixels shown through a recorded normalized
  crop viewport, with figure, page, caption, confidence, SHA-256, and rationale.
- **Illustrative input**: a small explanatory example of how the route's carrier
  may look. It is always labeled as non-evidence.

Multi-family models occur once and receive multiple incoming subtype links. A
focused node exposes the complete grounded route inventory with source object,
transformation chain, model-visible form, quote, heading, and pages.

## Rebuild

```bash
python3 scripts/build_input_representation_atlas.py
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
