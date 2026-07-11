# Interactive Input-Representation Taxonomy Atlas

This static GitHub Pages application renders the accepted 52-paper corpus as an
explicit taxonomic graph:

`root -> carrier family -> mechanism subtype -> model`

The graph contains:

- one taxonomy root, five carrier families, and 15 operational subtypes;
- 111 unique model nodes and 234 explicit taxonomy links;
- 376 lifecycle/task configurations and 489 grounded input routes;
- 103 model-specific original-paper crops drawn from 68 deduplicated source
  figures;
- eight explicit `no_suitable_figure` cases where the papers had text evidence
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
python3 scripts/aggregate_atlas_crop_annotations.py
python3 scripts/build_input_representation_atlas.py
```

The crop ledger is:

`data/input_representation_atlas_redesign_2026-07-11/model_crop_annotations.json`

All Codex subagent prompts, structured responses, stdout events, stderr, schemas,
commands, timestamps, and retry metadata are retained under:

`data/input_representation_atlas_redesign_2026-07-11/subagents/`

No LLM call occurs during the deterministic site build. Integrity results are
written to `data/build_report.json`.
