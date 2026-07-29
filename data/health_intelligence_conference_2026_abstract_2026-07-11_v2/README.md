# Health Intelligence Conference 2026 abstract v2

This version preserves the original template and v1 package while replacing
the taxonomy-only layout with a high-density scientific results page.

## Submission artifacts

- `health_intelligence_conference_2026_taxonomy_abstract_EN.docx`
- `health_intelligence_conference_2026_taxonomy_abstract_EN.pdf`
- `manuscript_content.json` and `manuscript_draft.md`
- `figures/deterministic/figure_1_taxonomy.svg` and `.png`

Author, affiliation, correspondence, received date, and funding are populated.

The submission PDF contains a selectable vector figure. The DOCX retains a
high-resolution PNG fallback because Word/LibreOffice rasterizes the figure
during document export.

## Reproduction

```bash
PY=/Users/bogdan.didenko/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3

$PY scripts/build_health_intelligence_conference_abstract.py \
  --output-dir data/health_intelligence_conference_2026_abstract_2026-07-11_v2 \
  --figure-variant compact-v3 \
  --build-docx

# Render the DOCX, then replace its raster figure with the canonical SVG as
# selectable vector PDF content.
$PY scripts/finalize_health_intelligence_vector_pdf.py \
  --input-pdf data/health_intelligence_conference_2026_abstract_2026-07-11_v2/build/render_45_received_date/health_intelligence_conference_2026_taxonomy_abstract_EN.pdf \
  --figure-svg data/health_intelligence_conference_2026_abstract_2026-07-11_v2/figures/deterministic/figure_1_taxonomy.svg \
  --output-pdf data/health_intelligence_conference_2026_abstract_2026-07-11_v2/health_intelligence_conference_2026_taxonomy_abstract_EN.pdf \
  --audit-json data/health_intelligence_conference_2026_abstract_2026-07-11_v2/analysis/vector_pdf_audit.json

$PY scripts/validate_health_intelligence_conference_abstract.py \
  --output-dir data/health_intelligence_conference_2026_abstract_2026-07-11_v2 \
  --render-dir data/health_intelligence_conference_2026_abstract_2026-07-11_v2/build/render_46_vector_received_date
```

The DOCX-to-PDF render uses the bundled `documents` skill renderer. The final
vector PDF is rendered again for color and grayscale QA in
`build/render_46_vector_received_date/`.

## Validation result

- One A4 page.
- 163 structured-abstract words, 463 main-body words, and 64 reference words.
- All canonical, section, figure-contract, redundancy, and visual checks pass.
- Page geometry, body-table grid, and the template's 288 dxa (5.08 mm)
  inter-column inset match the original English DOCX template.
- Figure labels use at least 20 px in the 1800 px canonical SVG; family names,
  panel headings, totals, and key metrics remain larger.
- The compact-v3 figure is 640 px high instead of 850 px; all subtype labels
  are single-line and the main body uses 8.6 pt type.
- Figure labels and values are searchable, selectable PDF text objects.
- The original 2084x984 raster figure is removed from the final PDF.
- No clipping, overlap, missing glyph, picture-only evidence, or second page.

See `validation_report.md` and `comparison/v1_v2.md`.
