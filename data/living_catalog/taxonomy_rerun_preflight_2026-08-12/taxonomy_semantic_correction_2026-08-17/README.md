# Taxonomy semantic correction (F6.1)

This version applies a narrow taxonomy-aware correction to the 50 routes flagged by F6. It preserves stable route IDs for retained/revised routes and records removals as tombstones in `route_transition_ledger.jsonl`. The original repeated-classification agreement metrics remain unchanged and are explicitly separated from the post-hoc correction validation.
