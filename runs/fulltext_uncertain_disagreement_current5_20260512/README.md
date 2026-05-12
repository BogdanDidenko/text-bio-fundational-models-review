# Full-text retrieval manifests

This run folder records best-effort open full-text retrieval for the aggregated
LLM screening uncertainty/disagreement set.

`manifest_current5_uncertain_or_disagreement.*` corresponds to the first pass
using five completed current LLM runs. `manifest_current6_uncertain_or_disagreement.*`
is the current primary manifest after the second Nemotron replicate completed.

Six-run retrieval summary:

- Target records: 932
- Existing HTML from previous pass: 495
- Existing PDF from previous pass: 246
- Newly downloaded HTML in six-run pass: 67
- Newly downloaded PDF in six-run pass: 25
- Not downloaded: 99
- Available as HTML/PDF: 833

Downloaded PDF/HTML full texts are intentionally not committed in normal git in
this repository because Git LFS is not configured here and the full-text cache is
large. The manifests record paths, source URLs, methods, and failures.
