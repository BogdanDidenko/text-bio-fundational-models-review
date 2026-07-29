# Unrecovered or Partial Artifacts

## Native Docling Payloads

The original VLM-enriched corpus was approximately 1.9 GB. Its 52 complete Markdown documents and all embedded VLM descriptions were recovered exactly, but the native `.docling.json` files, page images, and 447 of 506 picture bitmaps were not found.

The recovered Markdown supports reading, section recovery, and text-grounded analysis. Operations requiring native Docling item graphs, page geometry, or the missing bitmaps require reprocessing the recovered PDFs.

## Historical Working Copies

Large no-VLM Docling and Docling Graph working directories were untracked and were intentionally excluded from the repository’s artifact policy. Historical measurements indicate approximately:

- 5.4 GB of no-VLM Docling working data;
- 8.0 GB of full Graph/native working copies;
- 6.1 GB of taxonomy working data, much of it duplicated complete-document payloads.

Committed summaries, selected sections, classifications, prompts, responses, and final taxonomy artifacts remain available. The large duplicate intermediates were not blindly recreated.

## Full-Text Retrieval Corpus

All 52 accepted-paper PDFs were recovered. The larger historical retrieval workspace for the 235 candidate reports was not reconstructed in full. Existing Git manifests still preserve screening and retrieval outcomes.

## Determinism Run

The original `run_1/`, `run_2/`, and `run_3/` directories and their role-level request/response logs were not found. The historical report preserves per-record final decisions, codes, and decision sources. A fresh rerun was deliberately avoided because it would not reproduce the original stochastic outputs.

## Missing Helper Source

No trustworthy complete source was found for:

- `scripts/dedup_diagnostic.py`
- `scripts/delta_search_space_variants.py`

Their outputs or later equivalents remain elsewhere in the repository. The scripts were not fabricated from incomplete recollections.

## Environment

The former `.venv-docling` directory was about 1.4 GB and was not restored. It is a reproducible dependency environment rather than a research artifact.

## Credentials

API keys were recovered locally from the private session history and stored only in ignored `api_keys.json` with mode `0600`. Because they appeared in conversation history, rotating both keys is recommended.
