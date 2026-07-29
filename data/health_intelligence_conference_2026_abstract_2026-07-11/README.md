# Health Intelligence Conference 2026 abstract package

## Scientific focus

This package presents the evidence-grounded taxonomy of input-representation routes as the primary contribution. PRISMA-ScR search/screening, Docling/Docling Graph processing, and corpus-derived motivation are supporting methodology and provenance.

The fixed corpus is 52 accepted records (51 primary studies). The prior 14 reports without a valid targeted-section pair were not reopened or mixed into this taxonomy run.

## Submission files

- `health_intelligence_conference_2026_taxonomy_abstract_EN.docx`
- `health_intelligence_conference_2026_taxonomy_abstract_EN.pdf`
- `manuscript_draft.md`
- `manuscript_content.json`

The DOCX and PDF intentionally retain placeholders for authors, affiliations, correspondence, received date, and funding.

## Evidence and analysis

- `analysis/manuscript_fact_table.json`: recomputed taxonomy and screening facts.
- `analysis/prisma_fact_table.csv` and `.md`: verified supporting review funnel.
- `analysis/taxonomy_frequencies.csv`: five families and 15 subtype frequencies.
- `motivation_extraction/`: 52 per-paper prompts, responses, grounded outputs, and a 208-claim ledger; 174 exact verified claims cover all 52 records. The remaining 34 unmatched candidate claims are retained for audit but excluded from synthesis.
- `motivation_synthesis/`: logged synthesis using only verified claim IDs and programmatically derived supporting-record counts.
- `figures/`: the deterministic manuscript taxonomy figure, a supplementary workflow figure, PaperBanana/AutoFigure candidates, comparison, tool versions, and reproduction notes.
- `validation_report.json` and `.md`: numeric, provenance, figure, taxonomy, and one-page checks.

## Reproduction

The local OpenAI-compatible Codex wrapper must be running for motivation extraction and synthesis:

```bash
.venv-docling/bin/python scripts/docling/codex_openai_compat_server.py \
  --port 8877 --model gpt-5.4-mini --timeout 600 --quiet

.venv-docling/bin/python scripts/extract_conference_motivation_evidence.py \
  --base-url http://127.0.0.1:8877/v1 --workers 8 --timeout 900 --retries 1

.venv-docling/bin/python scripts/synthesize_conference_motivation_evidence.py \
  --base-url http://127.0.0.1:8877/v1 --timeout 900
```

Build the facts, figures, Markdown, and DOCX:

```bash
PY=/Users/bogdan.didenko/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
$PY scripts/build_health_intelligence_conference_abstract.py --build-docx
```

Render and validate:

```bash
SKILL=/Users/bogdan.didenko/.codex/plugins/cache/openai-primary-runtime/documents/26.709.11516/skills/documents
env TMPDIR=/private/tmp $PY $SKILL/render_docx.py \
  data/health_intelligence_conference_2026_abstract_2026-07-11/health_intelligence_conference_2026_taxonomy_abstract_EN.docx \
  --output_dir data/health_intelligence_conference_2026_abstract_2026-07-11/build/render_08 \
  --emit_pdf

$PY scripts/validate_health_intelligence_conference_abstract.py
```

## Final checks

- 52/52 motivation extractions succeeded.
- Verified motivation evidence covers 52/52 records.
- Manuscript numeric claims match canonical taxonomy artifacts.
- Figure fact-contract validation passed.
- All taxonomy acceptance criteria passed.
- Final PDF is exactly one A4 page.
- Header, footer, page geometry, theme, and font table are preserved from the template.
