#!/usr/bin/env python3
"""
Pilot title/abstract screening pipeline using LatteReview + OpenRouter.

This script is intentionally isolated from the main search/dedup/enrichment pipeline.
It loads the existing screened-ready corpus, selects a small pilot subset, and runs
LatteReview reviewers against OpenRouter using an OpenAI-compatible chat endpoint.

Usage:
  python scripts/run_lattereview_pilot.py --prepare-only
  python scripts/run_lattereview_pilot.py --api-key $OPENROUTER_API_KEY
  python scripts/run_lattereview_pilot.py --api-key $OPENROUTER_API_KEY --limit 24
  python scripts/run_lattereview_pilot.py --api-key $OPENROUTER_API_KEY --selection slice --offset 100 --limit 20
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RECORDS_PATH = ROOT / "data" / "deduplicated_records.json"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "pilot_runs"
DEFAULT_LATTEREVIEW_PATH = ROOT.parent / "LatteReview"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

GROUND_TRUTH_MODELS = [
    "scGPT",
    "tGPT",
    "LangCell",
    "ChatCell",
    "CellWhisperer",
    "CellPLM",
    "Nicheformer",
    "EpiAgent",
    "GenePT",
    "GeneGPT",
    "PathOmCLIP",
    "Cell2Seq",
    "X-Cell",
]

INCLUSION_CRITERIA = """
Include only if ALL of these are true:
1. The paper works with biological data modality: gene expression, transcriptomics, genomics, proteomics, epigenomics, spatial transcriptomics, single-cell, bulk, or other omics.
2. The paper has a genuine text/language component, using one of these tiers:
   - Tier A strong include: explicit natural-language and biology bridge such as text-to-cell, cell-to-text, text-guided generation, text-omics alignment, CLIP-style text encoder, retrieval between text and cells, or LLM agent grounded in biological data/tools.
   - Tier B include per protocol: gene tokens used in a GPT-like, decoder, autoregressive, or other clearly generative architecture, even if there is little or no natural-language interaction. Examples: scGPT, tGPT.
   - Do NOT count encoder-only gene tokenization as satisfying this criterion.
3. The architecture is generative, such as decoder-only, autoregressive, encoder-decoder, diffusion with generation, or CLIP-style system with generation/retrieval grounded in text.
4. The model has foundation-model characteristics: substantial pretraining, transferable representations, or large transformer/attention architecture intended for broad downstream use.
5. The paper is a primary research article or preprint, not a review, editorial, tutorial, benchmark overview, or commentary.
6. The paper is in English.
"""

EXCLUSION_CRITERIA = """
Exclude if ANY of these are true:
- EC1: No biological data modality. Examples: pure NLP/LLM papers that only mention genes or proteins in text, pure medical imaging or histopathology papers without omics.
- EC2: No text/language component. Examples: bio-only multimodal integration, cell type annotation, perturbation modeling, or omics prediction without any text bridge.
- EC3: Encoder-only architecture, especially BERT, MLM, masked language model, encoder-only transformer, or representation model without generation.
- EC4: No foundation-model component. Examples: small supervised model, conventional deep learning pipeline, rule-based method, narrow predictor, or simple wrapper around an existing LLM.
- EC5: Non-computational wet-lab paper.
- EC6: Non-scholarly source.
- EC7: Review/survey/meta-analysis/opinion.
- EC8: Not English.

Important boundaries:
- scGPT/tGPT-like gene-token decoder models are in scope.
- LangCell, ChatCell, CellWhisperer, GenePT, GeneGPT, EpiAgent, PathOmCLIP, Cell2Seq, and X-Cell are strong include-style reference points.
- scBERT, Geneformer, scFoundation, and UCE are out of scope because they are encoder-only.
- MultiVI/totalVI-style bio-only multimodal models are out of scope.
- A paper that only applies ChatGPT or another existing LLM to answer biology questions without introducing a real text+bio model bridge should usually be excluded.
"""

SHARED_CONTEXT = """
Use a precision-first screening strategy.
If the abstract is too short, looks like a search snippet, author list, or metadata rather than a true abstract, return score 3.
If the architecture is unclear and you cannot confidently distinguish generative from encoder-only, return score 3.
Heuristics:
- Mentions of BERT, MLM, masked language model, encoder-only without generation are strong exclusion signals.
- Mentions of autoregressive, decoder, generation, GPT, or cell-to-text/text-to-cell are strong inclusion signals.
- Mentions of survey, review, benchmark, perspective, editorial, tutorial, or commentary are strong exclusion signals.
- Mentions of transformer alone are not enough for inclusion.
- If the paper appears relevant to biology but lacks a clear text bridge, prefer score 2 or 3, not 4 or 5.
"""


def clean_text(text: str) -> str:
    if text is None:
        return ""
    text = str(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^Abstract\s+", "", text, flags=re.IGNORECASE)
    return text


def load_records(records_path: Path) -> List[Dict[str, Any]]:
    with records_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["records"]


def source_key(record: Dict[str, Any]) -> str:
    srcs = record.get("sources") or []
    if isinstance(srcs, str):
        srcs = [srcs]
    return "|".join(sorted(srcs)) if srcs else "unknown"


def abstract_quality_flag(record: Dict[str, Any]) -> str:
    abstract = clean_text(record.get("abstract", ""))
    if not abstract:
        return "missing"
    if abstract == "[No authors listed]":
        return "metadata_only"
    if len(abstract) < 120 and abstract.count(",") >= 2 and "(" in abstract:
        return "metadata_only"
    if len(abstract) < 250:
        return "short"
    if source_key(record) == "google_scholar" and len(abstract) < 500:
        return "gs_snippet_like"
    return "ok"


def find_ground_truth_matches(records: List[Dict[str, Any]]) -> List[int]:
    found = []
    seen_models = set()
    for idx, record in enumerate(records):
        text = f"{record.get('title', '')} {record.get('abstract', '')}".lower()
        for model in GROUND_TRUTH_MODELS:
            if model.lower() in text and model not in seen_models:
                found.append(idx)
                seen_models.add(model)
    return found


def select_indices(
    records: List[Dict[str, Any]],
    selection: str,
    limit: int,
    offset: int,
    seed: int,
) -> List[int]:
    total = len(records)
    rng = random.Random(seed)

    if selection == "slice":
        return list(range(offset, min(offset + limit, total)))

    if selection == "random":
        candidates = list(range(total))
        rng.shuffle(candidates)
        return sorted(candidates[:limit])

    gt_matches = find_ground_truth_matches(records)
    if selection == "ground_truth":
        return gt_matches[:limit] if limit else gt_matches

    if selection == "mixed":
        chosen = []
        chosen_set = set()

        for idx in gt_matches:
            chosen.append(idx)
            chosen_set.add(idx)
            if limit and len(chosen) >= min(limit, max(8, len(gt_matches))):
                break

        candidates = [i for i in range(total) if i not in chosen_set]
        rng.shuffle(candidates)
        for idx in candidates:
            if limit and len(chosen) >= limit:
                break
            chosen.append(idx)
            if limit and len(chosen) >= limit:
                break
        return sorted(chosen)

    raise ValueError(f"Unknown selection mode: {selection}")


def records_to_dataframe(records: List[Dict[str, Any]], indices: List[int]) -> pd.DataFrame:
    rows = []
    gt_lookup = {idx for idx in find_ground_truth_matches(records)}
    for idx in indices:
        record = records[idx]
        rows.append(
            {
                "record_idx": idx,
                "title": clean_text(record.get("title", "")),
                "abstract": clean_text(record.get("abstract", "")),
                "year": record.get("year", ""),
                "doi": record.get("doi", ""),
                "pmid": record.get("pmid", ""),
                "venue": clean_text(record.get("venue", "")),
                "sources": source_key(record),
                "n_sources": record.get("n_sources", 0),
                "duplicate_count": record.get("duplicate_count", 0),
                "abstract_len": len(clean_text(record.get("abstract", ""))),
                "abstract_quality_flag": abstract_quality_flag(record),
                "is_ground_truth_match": idx in gt_lookup,
            }
        )
    return pd.DataFrame(rows)


def score_to_decision(score: Any) -> str:
    try:
        score = int(score)
    except (TypeError, ValueError):
        return "ERROR"
    if score <= 2:
        return "EXCLUDE"
    if score == 3:
        return "UNCERTAIN"
    return "INCLUDE"


def serialize_for_output(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if out[col].map(lambda x: isinstance(x, (dict, list))).any():
            out[col] = out[col].map(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else x)
    return out


def ensure_lattereview_importable(lat_path: Path) -> None:
    if not lat_path.exists():
        raise FileNotFoundError(f"LatteReview path does not exist: {lat_path}")
    sys.path.insert(0, str(lat_path))


class OpenRouterJSONProvider:
    """
    Minimal provider compatible with LatteReview reviewers.
    It avoids the fragile OpenAI/LiteLLM integration path and uses OpenRouter directly.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        referer: str,
        title: str,
        timeout: int = 180,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.referer = referer
        self.title = title
        self.timeout = timeout
        self.max_retries = max_retries
        self.system_prompt = "You are a helpful assistant."
        self.response_format: Optional[Dict[str, Any]] = None

    def set_response_format(self, response_format: Dict[str, Any]) -> None:
        self.response_format = response_format

    async def get_json_response(
        self,
        input_prompt: str,
        image_path_list: Optional[List[str]] = None,
        message_list: Optional[List[Dict[str, str]]] = None,
        **kwargs: Any,
    ) -> tuple[Dict[str, Any], Dict[str, float]]:
        if image_path_list:
            raise ValueError("Image inputs are not supported in this pilot provider.")
        return await asyncio.to_thread(self._sync_get_json_response, input_prompt, message_list, kwargs)

    def _sync_get_json_response(
        self,
        input_prompt: str,
        message_list: Optional[List[Dict[str, str]]],
        kwargs: Dict[str, Any],
    ) -> tuple[Dict[str, Any], Dict[str, float]]:
        messages = message_list or [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": input_prompt},
        ]

        base_payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0),
            "max_tokens": kwargs.get("max_tokens", 400),
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.referer,
            "X-Title": self.title,
        }

        last_error = None
        for attempt in range(self.max_retries):
            payload = dict(base_payload)
            use_json_mode = attempt == 0
            if use_json_mode:
                payload["response_format"] = {"type": "json_object"}
            try:
                response = requests.post(
                    OPENROUTER_URL,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                if response.status_code == 429:
                    wait = 2 ** (attempt + 1)
                    time.sleep(wait)
                    continue
                if response.status_code >= 400 and use_json_mode:
                    # Some models/providers reject json mode; retry without it.
                    last_error = RuntimeError(f"OpenRouter error {response.status_code}: {response.text[:300]}")
                    continue
                response.raise_for_status()
                data = response.json()
                content = self._extract_content(data)
                parsed = self._parse_json_content(content)
                parsed = self._normalize_response(parsed)
                usage = data.get("usage") or {}
                cost = {
                    "input_cost": 0.0,
                    "output_cost": 0.0,
                    "total_cost": 0.0,
                    "prompt_tokens": float(usage.get("prompt_tokens", 0) or 0),
                    "completion_tokens": float(usage.get("completion_tokens", 0) or 0),
                    "total_tokens": float(usage.get("total_tokens", 0) or 0),
                }
                return parsed, cost
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                time.sleep(2 ** attempt)

        raise RuntimeError(f"OpenRouter request failed after {self.max_retries} attempts: {last_error}")

    @staticmethod
    def _extract_content(data: Dict[str, Any]) -> str:
        if "error" in data:
            raise RuntimeError(data["error"].get("message", str(data["error"])))
        message = data["choices"][0]["message"]["content"]
        if isinstance(message, list):
            text_parts = [part.get("text", "") for part in message if isinstance(part, dict)]
            return "".join(text_parts).strip()
        return str(message).strip()

    @staticmethod
    def _parse_json_content(content: str) -> Dict[str, Any]:
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?", "", content).strip()
            content = re.sub(r"```$", "", content).strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, flags=re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))

    def _normalize_response(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        if not self.response_format:
            return parsed
        normalized = dict(parsed)
        for key, expected_type in self.response_format.items():
            if key not in normalized:
                normalized[key] = None
                continue
            value = normalized[key]
            if value is None:
                continue
            if expected_type is int:
                if isinstance(value, str) and value.strip().isdigit():
                    normalized[key] = int(value.strip())
            elif expected_type is float:
                try:
                    normalized[key] = float(value)
                except (TypeError, ValueError):
                    normalized[key] = None
            elif expected_type is str and not isinstance(value, str):
                normalized[key] = str(value)
        return normalized


def make_reviewers(api_key: str, model: str, max_concurrent: int):
    from lattereview.agents import TitleAbstractReviewer

    referer = "https://github.com/BogdanDidenko/text-bio-fundational-models-review"
    title = "LatteReview Pilot Screening"

    reviewer_a = TitleAbstractReviewer(
        provider=OpenRouterJSONProvider(api_key=api_key, model=model, referer=referer, title=title),
        name="Conservative",
        backstory="a methodologically strict systematic review screener prioritizing precision and low false-positive rate",
        inclusion_criteria=INCLUSION_CRITERIA,
        exclusion_criteria=EXCLUSION_CRITERIA,
        additional_context=SHARED_CONTEXT,
        reasoning="brief",
        model_args={"temperature": 0.0, "max_tokens": 350},
        max_concurrent_requests=max_concurrent,
    )

    reviewer_b = TitleAbstractReviewer(
        provider=OpenRouterJSONProvider(api_key=api_key, model=model, referer=referer, title=title),
        name="Balanced",
        backstory="a computational biology reviewer balancing recall with protocol-faithful exclusions",
        inclusion_criteria=INCLUSION_CRITERIA,
        exclusion_criteria=EXCLUSION_CRITERIA,
        additional_context=SHARED_CONTEXT,
        reasoning="brief",
        model_args={"temperature": 0.2, "max_tokens": 350},
        max_concurrent_requests=max_concurrent,
    )

    adjudicator = TitleAbstractReviewer(
        provider=OpenRouterJSONProvider(api_key=api_key, model=model, referer=referer, title=title),
        name="Adjudicator",
        backstory="a senior reviewer resolving disagreements using a conservative final judgment",
        inclusion_criteria=INCLUSION_CRITERIA,
        exclusion_criteria=EXCLUSION_CRITERIA,
        additional_context=(
            SHARED_CONTEXT
            + " Resolve disagreements between the two round-A reviewers. If evidence is insufficient, return score 3."
        ),
        reasoning="brief",
        model_args={"temperature": 0.0, "max_tokens": 400},
        max_concurrent_requests=max_concurrent,
    )

    return reviewer_a, reviewer_b, adjudicator


def postprocess_results(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["pilot_roundA_conservative_decision"] = out["round-A_Conservative_evaluation"].map(score_to_decision)
    out["pilot_roundA_balanced_decision"] = out["round-A_Balanced_evaluation"].map(score_to_decision)
    out["pilot_roundA_agreement"] = (
        out["pilot_roundA_conservative_decision"] == out["pilot_roundA_balanced_decision"]
    ).map(lambda x: "agree" if x else "disagree")

    if "round-B_Adjudicator_evaluation" in out.columns:
        out["pilot_roundB_adjudicator_decision"] = out["round-B_Adjudicator_evaluation"].map(score_to_decision)
    else:
        out["pilot_roundB_adjudicator_decision"] = None

    out["pilot_final_decision"] = out["pilot_roundB_adjudicator_decision"]
    agreed_mask = out["pilot_roundA_agreement"] == "agree"
    out.loc[agreed_mask, "pilot_final_decision"] = out.loc[agreed_mask, "pilot_roundA_conservative_decision"]

    out["pilot_needs_manual_review"] = out["pilot_final_decision"].isin(["UNCERTAIN", "ERROR"])
    out["pilot_any_short_abstract_signal"] = out["abstract_quality_flag"].isin(["short", "gs_snippet_like", "metadata_only"])
    return out


def build_workflow(api_key: str, model: str, max_concurrent: int):
    from lattereview.workflows import ReviewWorkflow

    reviewer_a, reviewer_b, adjudicator = make_reviewers(api_key=api_key, model=model, max_concurrent=max_concurrent)

    return ReviewWorkflow(
        workflow_schema=[
            {
                "round": "A",
                "reviewers": [reviewer_a, reviewer_b],
                "text_inputs": ["title", "abstract"],
            },
            {
                "round": "B",
                "reviewers": [adjudicator],
                "text_inputs": [
                    "title",
                    "abstract",
                    "round-A_Conservative_output",
                    "round-A_Balanced_output",
                ],
                "filter": lambda row: row["round-A_Conservative_evaluation"] != row["round-A_Balanced_evaluation"],
            },
        ],
        verbose=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pilot LatteReview screening with OpenRouter + Qwen")
    parser.add_argument("--api-key", default=os.getenv("OPENROUTER_API_KEY"), help="OpenRouter API key")
    parser.add_argument("--model", default="qwen/qwen3.5-35b-a3b", help="OpenRouter model ID")
    parser.add_argument("--records-path", default=str(DEFAULT_RECORDS_PATH), help="Path to deduplicated_records.json")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for pilot outputs")
    parser.add_argument("--lattereview-path", default=str(DEFAULT_LATTEREVIEW_PATH), help="Path to local LatteReview clone")
    parser.add_argument("--selection", choices=["mixed", "slice", "random", "ground_truth"], default="mixed")
    parser.add_argument("--limit", type=int, default=24, help="Number of records in the pilot set")
    parser.add_argument("--offset", type=int, default=0, help="Offset for slice selection")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for pilot set selection")
    parser.add_argument("--max-concurrent", type=int, default=2, help="Max concurrent requests per reviewer")
    parser.add_argument("--prepare-only", action="store_true", help="Prepare the pilot CSV and exit without LLM calls")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started_at = time.time()

    records_path = Path(args.records_path).resolve()
    output_dir = Path(args.output_dir).resolve()
    lattereview_path = Path(args.lattereview_path).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    records = load_records(records_path)
    selected_indices = select_indices(
        records=records,
        selection=args.selection,
        limit=args.limit,
        offset=args.offset,
        seed=args.seed,
    )
    pilot_df = records_to_dataframe(records, selected_indices)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prepared_csv = output_dir / f"pilot_input_{stamp}.csv"
    pilot_df.to_csv(prepared_csv, index=False)

    print(f"Prepared pilot set: {len(pilot_df)} records")
    print(f"Selection mode: {args.selection}")
    print(f"Prepared CSV: {prepared_csv}")
    print("Abstract quality flags:")
    print(pilot_df["abstract_quality_flag"].value_counts(dropna=False).to_string())

    if args.prepare_only:
        return

    if not args.api_key:
        raise SystemExit("Missing OpenRouter API key. Pass --api-key or set OPENROUTER_API_KEY.")

    ensure_lattereview_importable(lattereview_path)
    workflow = build_workflow(
        api_key=args.api_key,
        model=args.model,
        max_concurrent=args.max_concurrent,
    )

    results_df = asyncio.run(workflow(pilot_df))
    results_df = postprocess_results(results_df)
    results_out = serialize_for_output(results_df)

    results_csv = output_dir / f"pilot_results_{stamp}.csv"
    results_out.to_csv(results_csv, index=False)

    summary = {
        "timestamp": stamp,
        "model": args.model,
        "records": int(len(results_df)),
        "selection": args.selection,
        "prepared_csv": str(prepared_csv),
        "results_csv": str(results_csv),
        "final_decision_counts": results_df["pilot_final_decision"].value_counts(dropna=False).to_dict(),
        "manual_review_count": int(results_df["pilot_needs_manual_review"].sum()),
        "agreement_counts": results_df["pilot_roundA_agreement"].value_counts(dropna=False).to_dict(),
        "abstract_quality_counts": results_df["abstract_quality_flag"].value_counts(dropna=False).to_dict(),
        "elapsed_seconds": round(time.time() - started_at, 2),
    }

    summary_json = output_dir / f"pilot_summary_{stamp}.json"
    with summary_json.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Results CSV: {results_csv}")
    print(f"Summary JSON: {summary_json}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
