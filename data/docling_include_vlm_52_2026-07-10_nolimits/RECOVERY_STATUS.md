# VLM Docling Corpus Recovery Status

This directory is a partial recovery of the canonical 52-record VLM-enriched
Docling corpus that existed before the laptop migration.

## Exactly recovered

- 52/52 VLM-enriched Markdown documents.
- Heading structure, body text, tables and captions represented in Markdown.
- Inline VLM picture descriptions present in those Markdown documents.
- The historical 52-record profile registry, including source PDF paths,
  profile metadata and figure counts.
- 59/506 source figure PNGs that had been copied into the committed interactive
  atlas. Every restored image matches the SHA-256 recorded by the atlas.
- Valid source PDFs for 52/52 records are available in
  `../source_pdf_recovery_52_2026-07-29/canonical_pdfs/`; 28 match their
  historical PDF SHA-256 exactly.

Each recovered Markdown file was extracted from the logged complete-document
prompt used by the open-discovery Docling Graph run. Its byte-level SHA-256 and
character count were verified against the corresponding historical values in
the run summary. See `recovery_manifest.csv` or `recovery_manifest.json` for
the source log, request index, expected hash and restored path.

## Not recovered

- Native `documents/*.docling.json` files.
- The remaining 447/506 picture bitmap files and all rendered page images.
- Per-paper `figures_manifest.json` files.
- Any chunks that would have been derived separately from the native profiles.

The original corpus contained 506 picture descriptions across the 52 records.
Those descriptions remain embedded in the recovered Markdown. Native Docling
picture items are absent, and only the 59 figures preserved by the atlas are
available as image files. See `recovered_figure_manifest.csv` or
`recovered_figure_manifest.json` for their hashes and recovery sources.

## Consequence

The recovered Markdown is exact and remains suitable for text-level inspection,
section recovery and logged direct-mode reproduction. This directory must not
be described as a complete native Docling profile corpus until the missing
`.docling.json` and image layers have been regenerated from the source PDFs.
The recovered PDF set makes that regeneration possible without repeating
full-text discovery.
