# F7 exact-preview and input-role validation

This audit rendered the crop coordinates from the current crop ledger against the current published atlas assets. Two blind roles separately checked visual sufficiency and exact-model input-role integrity; non-passes were adjudicated. The canonical crop ledger was not silently modified.

- Atlas models: **109**
- Exact crop previews rendered and reviewed: **98**
- Pre-existing `no_suitable_figure`: **11**
- Validated crops: **89**
- Models adjudicated: **19**
- Unresolved models: **0**
- Model for every role: `gpt-5.4-mini`
- Interpretation: repeated computational visual annotation with LLM adjudication, not human ground truth

## Dispositions

- `crop_rejected_no_suitable_figure`: 9
- `validated_adjusted_crop`: 1
- `validated_current_crop`: 79
- `validated_current_crop_after_adjudication`: 9

## Adjusted and revalidated

- `model_f12e33a1e764` — OCellus-Agent

## Rejected after exhaustive figure search

- `model_1fb19463c978` — GPT-4
- `model_2b474a3814ef` — GPT-4
- `model_3d02d9393c92` — DeepSeek-R1-Distill series (14B, 32B, and 70B)
- `model_422e09e03da5` — Clinical-LongFormer
- `model_58435d2084b0` — gene_eng_gpt2_summary
- `model_58c5ce11b66a` — scGPT
- `model_8553f59d67fa` — GPT-OSS-120B
- `model_ab432decc9aa` — Qwen3-1.7B, Qwen3-4B, and Gemma 4 E2B
- `model_f8e766fddf66` — PROCYON

`crop_validation_dispositions.json` contains every model-level decision. Exact prompts, schemas, responses, commands, image hashes, retries, stderr/stdout, and timings are under `runs/`. Review panels are deterministic regenerated intermediates and are excluded from Git; their hashes remain in the manifest and logs.
