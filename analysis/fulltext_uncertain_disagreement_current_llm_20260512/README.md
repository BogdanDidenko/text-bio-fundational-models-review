# Full-text target set from current LLM screening runs

This folder contains the aggregated screening decision matrix used to select
records for full-text retrieval after the current prompt update.

The primary analysis set is `current_6_complete_*`, built from six complete
full-corpus runs:

- DeepSeek-V4-Flash current prompt, replicate 1
- DeepSeek-V4-Flash current prompt, replicate 2
- GPT-OSS-120B current prompt, replicate 1
- GPT-OSS-120B current prompt, replicate 2
- NVIDIA Nemotron-3-Super-120B-A12B-FP8 current prompt, replicate 1
- NVIDIA Nemotron-3-Super-120B-A12B-FP8 current prompt, replicate 2

Full-text retrieval targets include every record where at least one run returned
`UNCERTAIN` or where the six final decisions were not unanimous.

Current six-run summary:

- Records common to all runs: 4027
- Fully unanimous records: 3160
- Unanimous INCLUDE: 23
- Unanimous UNCERTAIN: 65
- Unanimous EXCLUDE: 3072
- Full-text target records: 932

The `current_5_complete_*` files are retained because the first full-text
download pass was started before the second Nemotron replicate finished.
