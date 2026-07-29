# Source PDF Recovery for the 52-Record Corpus

This directory records the post-migration recovery of the source papers used to
build the 52-record VLM-enriched Docling corpus.

## Result

- 52/52 records have a structurally valid PDF in `canonical_pdfs/`.
- 28 PDFs exactly match their historical SHA-256.
- 13 were recovered from the historical versioned bioRxiv/arXiv URL but have a
  different current byte stream.
- 9 are valid PDFs for records whose historical manifest did not retain a PDF
  hash.
- 2 are valid alternative repository copies whose hashes differ from the
  historical files.

Every canonical PDF passes `pdfinfo` and has a positive page count. The final
selection, current and historical hashes, page counts, original paths and
recovery sources are recorded in `final_pdf_recovery_manifest.csv` and
`final_pdf_recovery_manifest.json`.

## Method

Recovery used the original candidate registry and the restored
`scripts/download_full_texts.py` resolver. Failed records were retried with the
historical OpenAlex and Semantic Scholar credentials restored to the ignored
local `api_keys.json`. Known versioned bioRxiv and arXiv URLs preserved in
historical download logs were then fetched directly with conservative retry
delays.

The `canonical_pdfs/` files are hard links to the selected recovered payloads
where the filesystem supports them. This avoids storing a second physical copy
while retaining one stable, flat input directory.

## Interpretation

`exact_historical_pdf` means byte identity with the pre-migration file.
Other statuses mean that the scientific paper was recovered and validated as a
PDF, but byte identity cannot be claimed. Server-side PDF regeneration,
repository versions and alternative mirrors can change metadata or content.
The exact VLM-enriched Markdown recovered separately remains the reference for
the analysis that was already completed.

