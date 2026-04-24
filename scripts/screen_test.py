#!/usr/bin/env python3
"""
DEPRECATED: v0.1 one-shot title/abstract screening classifier.

This script is retained as historical reference only. It does NOT implement the
current criterion-by-criterion LatteReview workflow declared in:

- protocol/llm_screening_system_guideline.md
- protocol/lattereview_screening_architecture.md
- protocol/screening_prompt.md
- protocol/screening_prompts/
- protocol/screening_prompt_templates/

Specifically, this script violates the current methodology in several ways:
- it asks the LLM to emit a final INCLUDE/EXCLUDE/UNCERTAIN label directly,
  instead of eliciting criterion-level answers and deriving the final decision
  in Python gate logic;
- it uses a single general-purpose reviewer instead of the scope_reviewer +
  architecture_reviewer + adjudicator topology;
- its system prompt is hardcoded in Python rather than loaded from the
  versioned runtime templates in protocol/screening_prompt_templates/.

For the current screening pipeline use:
    scripts/run_lattereview_guideline_pilot.py

See also scripts/README.md for the operative runtime entry point.

---

Historical description (v0.1, deprecated):
Test LLM-based title/abstract screening on a few sample records.
Uses OpenRouter API with OpenAI-compatible format.
Model: openai/gpt-oss-120b:free (or any other via --model flag)
"""

import json
import argparse
import requests
import time

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """You are an expert systematic review screener for a scoping review on "Generative Foundation Models Bridging Text and Biological Data."

Your task: Given a paper's TITLE and ABSTRACT, decide whether it should be INCLUDED, EXCLUDED, or marked UNCERTAIN for the review.

## Eligibility Criteria

**INCLUDE if ALL of these are true:**
1. IC1 — Works with biological data (gene expression, omics, genomics, transcriptomics, proteomics, epigenomics, spatial transcriptomics, single-cell or bulk)
2. IC2 — Has a text/language component (natural language, gene tokens processed as text, LLM, GPT, CLIP text encoder, NLP, tokenizer for genes, prompt-based, text generation, cell-to-text, text-to-cell)
3. IC3 — Architecture is generative (decoder, autoregressive, encoder-decoder, VAE with decoder, diffusion with language, CLIP-style with generation) — NOT encoder-only (BERT-style)
4. IC4 — Foundation model characteristics (large-scale pretraining, transferable representations, transformer/attention architecture)
5. IC5 — Primary research article or preprint (not a review, editorial, tutorial)
6. Is in English

**EXCLUDE with code if ANY of these:**
- EC1: No biological data — pure NLP/CS/physics without any biology
- EC2: No text/language component — bio-only models (e.g., just RNA+ATAC integration without text)
- EC3: Encoder-only architecture — masked language model without generation (scBERT, Geneformer, pure BERT on genes). Note: list these as "related but excluded"
- EC4: No FM characteristics — small supervised models, rule-based, simple concatenation
- EC5: Non-computational — wet-lab only, no modeling
- EC6: Non-scholarly — editorial, blog, tutorial, software docs
- EC7: Review article — systematic review, narrative review, meta-analysis, opinion
- EC8: Not English

**Mark UNCERTAIN when:**
- Abstract is missing or too short to judge
- Borderline: could be generative or encoder-only but unclear from abstract
- Uses gene tokens but unclear if truly generative vs encoder-only
- Combines text + bio but unclear architecture details

## Key clarifications:
- "Gene tokens" processed by a GPT/decoder = text modality (IC2 satisfied)
- scGPT, tGPT, CellPLM = gene tokens as text → INCLUDE
- scBERT, Geneformer = encoder-only → EXCLUDE (EC3)
- MultiVI, totalVI = bio-only multi-modal, no text → EXCLUDE (EC2)
- LLM agents that use external tools for biology (GeneGPT, EpiAgent) = INCLUDE
- CLIP-style alignment of text + omics (PathOmCLIP) = INCLUDE
- Pure image/histology models without omics AND without text generation = EXCLUDE (EC1 or EC2)

## Output format
Respond with ONLY a JSON object, no other text:
{
  "decision": "INCLUDE" | "EXCLUDE" | "UNCERTAIN",
  "code": "EC1" | "EC2" | "EC3" | "EC4" | "EC5" | "EC6" | "EC7" | "EC8" | null,
  "confidence": 0.0-1.0,
  "reasoning": "Brief 1-2 sentence explanation"
}"""


def screen_record(title, abstract, api_key, model):
    """Send a single record to the LLM for screening."""
    user_msg = f"{SYSTEM_PROMPT}\n\n---\n\nScreen this paper:\n\nTITLE: {title}\n\nABSTRACT: {abstract if abstract else '[No abstract available]'}"

    payload = {
        "model": model,
        "temperature": 0,
        "max_tokens": 300,
        "messages": [
            {"role": "user", "content": user_msg},
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/BogdanDidenko/text-bio-fundational-models-review",
        "X-Title": "Systematic Review Screening",
    }

    # Retry with exponential backoff for rate limits
    for attempt in range(4):
        r = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=120)
        if r.status_code == 429:
            wait = 2 ** (attempt + 1)
            print(f"    Rate limited. Waiting {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        break
    else:
        raise Exception("Rate limited after 4 retries")

    data = r.json()
    if "error" in data:
        raise Exception(data["error"].get("message", str(data["error"])))
    content = data["choices"][0]["message"]["content"]

    # Parse JSON from response
    # Handle potential markdown code blocks
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]  # remove first line
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {"decision": "ERROR", "code": None, "confidence": 0, "reasoning": f"Failed to parse: {content[:200]}"}

    return result, data.get("usage", {})


def main():
    parser = argparse.ArgumentParser(description="Test LLM screening on sample records")
    parser.add_argument("--api-key", required=True, help="OpenRouter API key")
    parser.add_argument("--model", default="openai/gpt-oss-120b:free", help="Model ID")
    args = parser.parse_args()

    # Load deduplicated records
    with open("data/deduplicated_records.json") as f:
        data = json.load(f)
    records = data["records"]

    # Select test records: ground truth models + some obvious noise
    test_indices = []

    # Find ground truth models
    gt_models = ["scGPT", "LangCell", "ChatCell", "CellWhisperer", "GenePT", "GeneGPT",
                 "EpiAgent", "PathOmCLIP", "Nicheformer", "CellPLM"]
    # Also find encoder-only (should be EC3)
    encoder_only = ["scBERT", "Geneformer"]
    # Also find some obviously off-topic (should be EC1/EC2)

    gt_found = {}
    for i, r in enumerate(records):
        text = (r["title"] + " " + r.get("abstract", "")).lower()
        for model in gt_models + encoder_only:
            if model.lower() in text and model not in gt_found:
                gt_found[model] = i

    # Add first 3 records as random samples
    test_set = []
    for model, idx in gt_found.items():
        test_set.append((model, records[idx]))
    # Add 3 random records for noise testing
    for idx in [0, 100, 500]:
        test_set.append((f"random_{idx}", records[idx]))

    print(f"Model: {args.model}")
    print(f"Testing {len(test_set)} records\n")
    print("=" * 80)

    for label, rec in test_set:
        title = rec["title"]
        abstract = rec.get("abstract", "")

        print(f"\n[{label}]")
        print(f"  Title: {title[:100]}...")
        print(f"  Abstract: {abstract[:100]}..." if abstract else "  Abstract: [none]")

        try:
            result, usage = screen_record(title, abstract, args.api_key, args.model)
            decision = result.get("decision", "?")
            code = result.get("code", "")
            confidence = result.get("confidence", "?")
            reasoning = result.get("reasoning", "")

            # Color-code decision
            marker = {"INCLUDE": "+", "EXCLUDE": "-", "UNCERTAIN": "?", "ERROR": "!"}.get(decision, "?")
            print(f"  [{marker}] {decision} {f'({code})' if code else ''} [conf={confidence}]")
            print(f"  Reasoning: {reasoning}")
            if usage:
                print(f"  Tokens: prompt={usage.get('prompt_tokens', '?')}, completion={usage.get('completion_tokens', '?')}")
        except Exception as e:
            print(f"  ERROR: {e}")

        time.sleep(5)  # Rate limit courtesy for free tier

    print("\n" + "=" * 80)
    print("Done.")


if __name__ == "__main__":
    main()
