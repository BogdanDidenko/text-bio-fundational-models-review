# LLM Screening Prompt — Title/Abstract Phase

## Current Prompt (v0.1)

The system prompt used for LLM-based title/abstract screening is embedded in
`scripts/screen_test.py`. It instructs the model to classify each paper as
INCLUDE / EXCLUDE / UNCERTAIN based on the eligibility criteria from
`protocol/eligibility_criteria.md`.

### Decision logic (prompt summary)

**INCLUDE** if ALL of:
1. IC1 — biological data (gene expression, omics, genomics, etc.)
2. IC2 — text/language component (NL, gene tokens, LLM, CLIP text encoder, etc.)
3. IC3 — generative architecture (decoder, autoregressive, VAE, diffusion, CLIP+generation)
4. IC4 — FM characteristics (pretraining, transferable, transformer/attention)
5. IC5 — primary research or preprint (not review/editorial)
6. English language

**EXCLUDE** with code if ANY of EC1–EC8 (see `eligibility_criteria.md`).

**UNCERTAIN** when abstract is ambiguous about architecture or modalities.

### Output format

```json
{
  "decision": "INCLUDE | EXCLUDE | UNCERTAIN",
  "code": "EC1 | EC2 | ... | EC8 | null",
  "confidence": 0.0-1.0,
  "reasoning": "Brief 1-2 sentence explanation"
}
```

---

## Known Problems (from v0.1 testing with Gemma 12B)

### P1: Too liberal — high false-positive rate
The prompt lets through too many papers that mention biology + transformer but are
NOT actually multi-modal text+bio foundation models. Examples of false includes:
- Standard scRNA-seq analysis pipelines that use a transformer for cell type annotation
  (no text modality, should be EC2)
- NLP papers that mention "gene" or "protein" in passing but work purely on text
  (should be EC1 — no actual biological data)
- Encoder-only models not clearly identified as such (should be EC3)
- Papers applying an existing LLM (ChatGPT) to answer biology questions without
  building a model that bridges text and bio data (should be EC4 or EC2)

### P2: Overly broad IC2 — "gene tokens" catches too much
The prompt says gene tokens processed by GPT/decoder = text modality. This is correct
for scGPT/tGPT, but many single-cell foundation models tokenize genes into sequences
without any actual text/NL component. The prompt needs a sharper boundary between:
- **In scope**: models that bridge text AND biology (cross-modal, e.g., LangCell,
  ChatCell, CLIP-style alignment, cell-to-text generation)
- **Borderline**: models that use gene tokens in a GPT-like decoder but never interact
  with natural language (e.g., scGPT — included per protocol decision, but the prompt
  should explicitly distinguish this case)
- **Out of scope**: models that merely tokenize genes for an encoder-only architecture

### P3: Weak discrimination of architecture type
Many abstracts describe "transformer-based" models without specifying encoder-only vs
decoder/generative. The prompt tells the model to mark these UNCERTAIN, but in practice
the LLM often guesses INCLUDE with moderate confidence. Need:
- Explicit heuristics: if abstract mentions "masked language model" / "MLM" / "BERT"
  without mentioning generation → lean EXCLUDE (EC3)
- If abstract mentions "autoregressive" / "decoder" / "generation" / "GPT" → lean INCLUDE

### P4: No calibration data in prompt
The prompt has key clarification examples (scGPT=include, scBERT=exclude, etc.) but
lacks a few-shot calibration set with borderline cases showing expected decisions.
Adding 3-5 worked examples of INCLUDE, EXCLUDE, and UNCERTAIN would anchor the model.

### P5: Model quality
Gemma 12B (free tier via OpenRouter) may not have sufficient reasoning for borderline
cases. Need to test with stronger models (GPT-4o-mini, Claude Haiku) and compare
precision/recall on a manually labeled calibration set.

---

## Work Plan for Prompt Improvement

### Step 1: Build calibration set (~30 records)
Manually label ~30 records from the 4,027 pool:
- 10 clear INCLUDE (ground truth models + new papers like X-Cell)
- 10 clear EXCLUDE (various EC codes)
- 10 borderline/UNCERTAIN

### Step 2: Tighten IC2 definition
Rewrite the IC2 section to have a 3-tier classification:
- **Tier A (strong include)**: model explicitly bridges NL text and biological data
  (cross-modal retrieval, cell-to-text, text-guided generation)
- **Tier B (include per protocol)**: model uses gene tokens in GPT/decoder architecture
  without NL (scGPT, tGPT) — include but flag as "gene-token-only"
- **Tier C (exclude)**: model tokenizes genes but is encoder-only or has no
  generative component

### Step 3: Add few-shot examples
Add 3-5 worked examples directly in the system prompt:
- 1 clear INCLUDE with reasoning
- 1 EC2 exclude (bio-only, no text)
- 1 EC3 exclude (encoder-only)
- 1 UNCERTAIN (ambiguous architecture)

### Step 4: Add negative signal heuristics
Explicit patterns that should push toward EXCLUDE:
- "BERT" / "masked language model" / "MLM" without "generation" → EC3
- "survey" / "review" / "benchmark" in title → EC7
- "image" / "histopathology" / "radiology" without omics → EC1
- Generic "deep learning for [disease]" without FM/pretraining → EC4

### Step 5: Model comparison
Test prompt v0.2 on the calibration set with:
- Gemma 12B (free baseline)
- GPT-4o-mini (cheap, good reasoning)
- Claude Haiku (alternative)

Target: **>90% precision** (reduce false includes) while maintaining **>95% recall**
(don't lose ground truth models).

### Step 6: Full screening run
Run on all 4,027 records with the validated prompt+model combination.
Dual-pass strategy: if two models disagree → mark UNCERTAIN for manual review.
