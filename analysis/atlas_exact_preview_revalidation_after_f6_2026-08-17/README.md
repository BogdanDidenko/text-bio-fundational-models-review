# F7 exact-preview and input-role validation

This audit rendered the crop coordinates from the current crop ledger against the current published atlas assets. Two blind roles separately checked visual sufficiency and exact-model input-role integrity; non-passes were adjudicated. The canonical crop ledger was not silently modified.

- Atlas models: **4**
- Exact crop previews rendered and reviewed: **4**
- Pre-existing `no_suitable_figure`: **0**
- Validated crops: **4**
- Models adjudicated: **0**
- Unresolved models: **0**
- Model for every role: `gpt-5.4-mini`
- Interpretation: repeated computational visual annotation with LLM adjudication, not human ground truth

## Dispositions

- `validated_current_crop`: 4

`crop_validation_dispositions.json` contains every model-level decision. Exact prompts, schemas, responses, commands, image hashes, retries, stderr/stdout, and timings are under `runs/`. Review panels are deterministic regenerated intermediates and are excluded from Git; their hashes remain in the manifest and logs.

## Scope and isolation

Only the four current crops whose claimed route set intersected the F6 correction population were revalidated. Both blind roles passed every crop with at least one common supported route, so no adjudicator, crop replacement, or full-atlas rerun was required. The earlier whole-atlas F7 run allowed shell access in some calls; this post-F6 run used an empty temporary workspace with shell, exec, apps, plugins, browser, computer-use, and workspace tools disabled. `tool_isolation_audit.json` records zero tool events. This remains repeated computational visual annotation, not human validation.
