# Interactive Input-Representation Atlas

This static GitHub Pages application presents the complete taxonomy result for
the 52-paper accepted corpus:

- 111 model entities;
- 376 lifecycle/task configurations;
- 489 grounded input routes;
- five carrier families and 15 operational subtypes;
- 77 deduplicated figures extracted from the original papers.

Every architecture detail view retains its source record, paper title, DOI when
available, original figure caption and page, figure SHA-256, route-level evidence
quote, heading, pages, and native Docling references. The figure-selection score
and reasons are included in `data/atlas.json`.

Rebuild from the canonical taxonomy and Docling corpus with:

```bash
.venv-docling/bin/python scripts/build_input_representation_atlas.py
```

The build fails if a model has no source-paper figure. Integrity results are
written to `data/build_report.json`. No LLM call occurs during site generation.
