#!/usr/bin/env python3
"""
Run the guideline-aligned LatteReview title/abstract pipeline against an
OpenAI-compatible LLM endpoint such as vLLM.

Expected input CSV columns:
- title
- abstract

The script implements:
- round A: scope reviewer + architecture reviewer
- Python gate logic
- round B: adjudicator only for unresolved / conflicting cases
- rule-based final aggregation
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import requests

if TYPE_CHECKING:
    import pandas as pd

pd = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROMPT_DIR = ROOT / "protocol" / "screening_prompt_templates"
DEFAULT_LATTEREVIEW_PATH = ROOT / "external" / "LatteReview"


SCOPE_RESPONSE_FORMAT: Dict[str, Any] = {
    "paper_type": str,
    "bio_modality_present": str,
    "text_component_present": str,
    "text_bio_bridge_present": str,
    "primary_exclusion_code": str,
    "uncertainty_reason": str,
    "evidence_for_text_component": str,
    "evidence_for_text_bio_bridge": str,
    "evidence_for_generative_model": str,
    "boundary_case": str,
    "decision_rationale": str,
}

ARCHITECTURE_RESPONSE_FORMAT: Dict[str, Any] = {
    "paper_type": str,
    "generative_model_present": str,
    "foundation_model_evidence": str,
    "primary_exclusion_code": str,
    "uncertainty_reason": str,
    "evidence_for_text_component": str,
    "evidence_for_text_bio_bridge": str,
    "evidence_for_generative_model": str,
    "boundary_case": str,
    "decision_rationale": str,
}

ADJUDICATOR_RESPONSE_FORMAT: Dict[str, Any] = {
    "paper_type": str,
    "bio_modality_present": str,
    "text_component_present": str,
    "text_bio_bridge_present": str,
    "generative_model_present": str,
    "foundation_model_evidence": str,
    "primary_exclusion_code": str,
    "uncertainty_reason": str,
    "evidence_for_text_component": str,
    "evidence_for_text_bio_bridge": str,
    "evidence_for_generative_model": str,
    "boundary_case": str,
    "decision_rationale": str,
}


def read_template(prompt_dir: Path, filename: str) -> str:
    path = prompt_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt template file does not exist: {path}")
    return path.read_text(encoding="utf-8").strip()


def normalize_optional_label(value: Any) -> Optional[str]:
    text = str(value or "").strip()
    if text in {"", "none", "null", "None", "NONE"}:
        return None
    return text


def ensure_lattereview_importable(lat_path: Optional[Path]) -> None:
    try:
        importlib.import_module("lattereview")
        return
    except ModuleNotFoundError:
        pass

    if lat_path is None:
        raise ModuleNotFoundError(
            "LatteReview is not importable. Provide --lattereview-path or clone "
            "LatteReview into ./external/LatteReview."
        )
    if not lat_path.exists():
        raise FileNotFoundError(f"LatteReview path does not exist: {lat_path}")
    sys.path.insert(0, str(lat_path))
    importlib.import_module("lattereview")


def serialize_for_output(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if out[col].map(lambda x: isinstance(x, (dict, list))).any():
            out[col] = out[col].map(
                lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else x
            )
    return out


class VLLMOpenAIJSONProvider:
    """Small LatteReview-compatible provider for an OpenAI-style endpoint."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "dummy",
        timeout: int = 300,
        max_retries: int = 3,
        enable_thinking: bool = False,
        reasoning_effort: str = "high",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_thinking = enable_thinking
        self.reasoning_effort = reasoning_effort
        self.system_prompt = ""
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
        if message_list is None:
            messages = [{"role": "user", "content": input_prompt}]
            if self.system_prompt:
                messages.insert(0, {"role": "system", "content": self.system_prompt})
        else:
            messages = message_list

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "seed": kwargs.get("seed", 0),
            "n": kwargs.get("n", 1),
            "max_tokens": kwargs.get("max_tokens", 500),
        }
        if not self.enable_thinking:
            payload["response_format"] = {"type": "json_object"}
        if self.enable_thinking:
            payload["chat_template_kwargs"] = {
                "thinking": True,
                "reasoning_effort": self.reasoning_effort,
            }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                if response.status_code == 429:
                    time.sleep(2 ** (attempt + 1))
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

        raise RuntimeError(f"LLM request failed after {self.max_retries} attempts: {last_error}")

    @staticmethod
    def _extract_content(data: Dict[str, Any]) -> str:
        if "error" in data:
            raise RuntimeError(data["error"].get("message", str(data["error"])))
        message = data["choices"][0]["message"]
        content = message.get("content")
        if isinstance(content, list):
            text_parts = [part.get("text", "") for part in content if isinstance(part, dict)]
            return "".join(text_parts).strip()
        if isinstance(content, str) and content.strip():
            return content.strip()

        reasoning = message.get("reasoning")
        if isinstance(reasoning, str) and reasoning.strip():
            return reasoning.strip()

        return ""

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


def make_reviewers(
    base_url: str,
    api_key: str,
    model: str,
    max_concurrent: int,
    timeout: int,
    max_tokens: int,
    prompt_dir: Path,
    enable_thinking: bool,
    reasoning_effort: str,
):
    from lattereview.agents import ScoringReviewer

    class SelfContainedPromptReviewer(ScoringReviewer):
        def _build_system_prompt(self) -> str:
            return ""

    provider_kwargs = {
        "base_url": base_url,
        "api_key": api_key,
        "model": model,
        "timeout": timeout,
        "enable_thinking": enable_thinking,
        "reasoning_effort": reasoning_effort,
    }

    shared_args = {
        "model_args": {"temperature": 0.7, "top_p": 1.0, "n": 1, "seed": 0, "max_tokens": max_tokens},
        "max_concurrent_requests": max_concurrent,
        "scoring_set": [0],
    }

    scope_reviewer = SelfContainedPromptReviewer(
        provider=VLLMOpenAIJSONProvider(**provider_kwargs),
        name="scope_reviewer",
        generic_prompt=None,
        prompt_path=prompt_dir / "scope_reviewer_prompt.txt",
        backstory="",
        response_format=SCOPE_RESPONSE_FORMAT,
        **shared_args,
    )

    architecture_reviewer = SelfContainedPromptReviewer(
        provider=VLLMOpenAIJSONProvider(**provider_kwargs),
        name="architecture_reviewer",
        generic_prompt=None,
        prompt_path=prompt_dir / "architecture_reviewer_prompt.txt",
        backstory="",
        response_format=ARCHITECTURE_RESPONSE_FORMAT,
        **shared_args,
    )

    adjudicator = SelfContainedPromptReviewer(
        provider=VLLMOpenAIJSONProvider(**provider_kwargs),
        name="adjudicator",
        generic_prompt=None,
        prompt_path=prompt_dir / "adjudicator_prompt.txt",
        backstory="",
        response_format=ADJUDICATOR_RESPONSE_FORMAT,
        **shared_args,
    )

    return scope_reviewer, architecture_reviewer, adjudicator


def build_round_a_workflow(
    base_url: str,
    api_key: str,
    model: str,
    max_concurrent: int,
    timeout: int,
    max_tokens: int,
    prompt_dir: Path,
    enable_thinking: bool,
    reasoning_effort: str,
):
    from lattereview.workflows import ReviewWorkflow

    scope_reviewer, architecture_reviewer, _ = make_reviewers(
        base_url=base_url,
        api_key=api_key,
        model=model,
        max_concurrent=max_concurrent,
        timeout=timeout,
        max_tokens=max_tokens,
        prompt_dir=prompt_dir,
        enable_thinking=enable_thinking,
        reasoning_effort=reasoning_effort,
    )

    return ReviewWorkflow(
        workflow_schema=[
            {
                "round": "A",
                "reviewers": [scope_reviewer, architecture_reviewer],
                "text_inputs": ["title", "abstract"],
            },
        ],
        verbose=True,
    )


def build_round_b_workflow(
    base_url: str,
    api_key: str,
    model: str,
    max_concurrent: int,
    timeout: int,
    max_tokens: int,
    prompt_dir: Path,
    enable_thinking: bool,
    reasoning_effort: str,
):
    from lattereview.workflows import ReviewWorkflow

    _, _, adjudicator = make_reviewers(
        base_url=base_url,
        api_key=api_key,
        model=model,
        max_concurrent=max_concurrent,
        timeout=timeout,
        max_tokens=max_tokens,
        prompt_dir=prompt_dir,
        enable_thinking=enable_thinking,
        reasoning_effort=reasoning_effort,
    )

    return ReviewWorkflow(
        workflow_schema=[
            {
                "round": "B",
                "reviewers": [adjudicator],
                "text_inputs": [
                    "title",
                    "abstract",
                    "round-A_scope_reviewer_paper_type",
                    "round-A_scope_reviewer_bio_modality_present",
                    "round-A_scope_reviewer_text_component_present",
                    "round-A_scope_reviewer_text_bio_bridge_present",
                    "round-A_scope_reviewer_primary_exclusion_code",
                    "round-A_scope_reviewer_uncertainty_reason",
                    "round-A_architecture_reviewer_paper_type",
                    "round-A_architecture_reviewer_generative_model_present",
                    "round-A_architecture_reviewer_foundation_model_evidence",
                    "round-A_architecture_reviewer_primary_exclusion_code",
                    "round-A_architecture_reviewer_uncertainty_reason",
                ],
            },
        ],
        verbose=True,
    )


def format_text_input(row: pd.Series, text_inputs: List[str], round_id: str, idx: Any) -> str:
    parts = []
    for text_input in text_inputs:
        value = str(row[text_input]).strip()
        parts.append(f"=== {text_input} ===\n{value}")
    return f"Review Task ID: {round_id}-{idx}\n" + "\n\n".join(parts)


def normalize_reviewer_output(output: Any, response_format: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(output, dict):
        processed = dict(output)
    else:
        processed = json.loads(output)
    for key in response_format:
        processed.setdefault(key, None)
    return processed


def reviewer_columns(round_id: str, reviewer: Any) -> tuple[str, List[str]]:
    response_keywords = list(reviewer.response_format.keys())
    output_col = f"round-{round_id}_{reviewer.name}_output"
    response_cols = [f"round-{round_id}_{reviewer.name}_{keyword}" for keyword in response_keywords]
    return output_col, response_cols


async def run_reviewer_for_row(
    reviewer: Any,
    row: pd.Series,
    idx: Any,
    round_id: str,
    text_inputs: List[str],
    request_semaphore: asyncio.Semaphore,
) -> Dict[str, Any]:
    text_input_string = format_text_input(row, text_inputs, round_id, idx)
    async with request_semaphore:
        output, input_prompt, cost = await reviewer.review_item(text_input_string, [])

    if isinstance(cost, dict):
        cost_value = cost.get("total_cost", 0.0)
    else:
        cost_value = cost
    reviewer.cost_so_far += cost_value
    reviewer.memory.append(
        {
            "system_prompt": reviewer.system_prompt,
            "model_args": reviewer.model_args,
            "input_prompt": input_prompt,
            "response": output,
            "cost": cost_value,
        }
    )

    processed = normalize_reviewer_output(output, reviewer.response_format)
    output_col, _ = reviewer_columns(round_id, reviewer)
    row_updates = {output_col: output}
    for keyword in reviewer.response_format.keys():
        row_updates[f"round-{round_id}_{reviewer.name}_{keyword}"] = processed.get(keyword)
    return row_updates


async def run_streaming_guideline_pipeline(
    df: pd.DataFrame,
    base_url: str,
    api_key: str,
    model: str,
    max_concurrent: int,
    timeout: int,
    max_tokens: int,
    prompt_dir: Path,
    enable_thinking: bool,
    reasoning_effort: str,
    output_dir: Optional[Path] = None,
) -> pd.DataFrame:
    scope_reviewer, architecture_reviewer, adjudicator = make_reviewers(
        base_url=base_url,
        api_key=api_key,
        model=model,
        max_concurrent=max_concurrent,
        timeout=timeout,
        max_tokens=max_tokens,
        prompt_dir=prompt_dir,
        enable_thinking=enable_thinking,
        reasoning_effort=reasoning_effort,
    )
    for reviewer in (scope_reviewer, architecture_reviewer, adjudicator):
        reviewer.setup()

    request_semaphore = asyncio.Semaphore(max_concurrent)

    async def process_row(idx: Any, source_row: pd.Series) -> Dict[str, Any]:
        row_data = source_row.to_dict()
        working_row = pd.Series(row_data)

        scope_task = asyncio.create_task(
            run_reviewer_for_row(
                scope_reviewer,
                working_row,
                idx,
                "A",
                ["title", "abstract"],
                request_semaphore,
            )
        )
        architecture_task = asyncio.create_task(
            run_reviewer_for_row(
                architecture_reviewer,
                working_row,
                idx,
                "A",
                ["title", "abstract"],
                request_semaphore,
            )
        )
        scope_updates, architecture_updates = await asyncio.gather(scope_task, architecture_task)
        row_data.update(scope_updates)
        row_data.update(architecture_updates)

        working_row = pd.Series(row_data)
        row_data["pilot_roundA_scope_gate"] = scope_gate_decision(working_row)
        row_data["pilot_roundA_architecture_gate"] = architecture_gate_decision(working_row)
        working_row = pd.Series(row_data)
        row_data["pilot_needs_adjudication"] = needs_adjudication(working_row)

        if row_data["pilot_needs_adjudication"]:
            adjudication_updates = await run_reviewer_for_row(
                adjudicator,
                pd.Series(row_data),
                idx,
                "B",
                [
                    "title",
                    "abstract",
                    "round-A_scope_reviewer_paper_type",
                    "round-A_scope_reviewer_bio_modality_present",
                    "round-A_scope_reviewer_text_component_present",
                    "round-A_scope_reviewer_text_bio_bridge_present",
                    "round-A_scope_reviewer_primary_exclusion_code",
                    "round-A_scope_reviewer_uncertainty_reason",
                    "round-A_architecture_reviewer_paper_type",
                    "round-A_architecture_reviewer_generative_model_present",
                    "round-A_architecture_reviewer_foundation_model_evidence",
                    "round-A_architecture_reviewer_primary_exclusion_code",
                    "round-A_architecture_reviewer_uncertainty_reason",
                ],
                request_semaphore,
            )
            row_data.update(adjudication_updates)

        return row_data

    pending_rows = list(df.iterrows())
    active_rows = min(len(pending_rows), max(1, max_concurrent))
    tasks = [asyncio.create_task(process_row(*pending_rows.pop(0))) for _ in range(active_rows)]
    results = []
    completed = 0
    total = len(df)
    raw_jsonl = output_dir / "guideline_pilot_raw_completed.jsonl" if output_dir else None
    partial_raw_csv = output_dir / "guideline_pilot_raw_completed.csv" if output_dir else None
    partial_csv = output_dir / "guideline_pilot_results_partial.csv" if output_dir else None

    while tasks:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        tasks = list(pending)
        for task in done:
            row_result = await task
            results.append(row_result)
            if pending_rows:
                tasks.append(asyncio.create_task(process_row(*pending_rows.pop(0))))

            completed += 1
            current_raw = pd.DataFrame(results).sort_values("_pilot_row_id").reset_index(drop=True)
            if raw_jsonl:
                with raw_jsonl.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row_result, ensure_ascii=False, default=str) + "\n")
            if partial_raw_csv:
                serialize_for_output(current_raw).to_csv(partial_raw_csv, index=False)
            if partial_csv:
                serialize_for_output(postprocess_results(current_raw)).to_csv(partial_csv, index=False)
            print(f"Streaming pipeline completed {completed}/{total} records", flush=True)

    result_df = pd.DataFrame(results)
    return result_df.sort_values("_pilot_row_id").reset_index(drop=True)


def scope_gate_decision(row: pd.Series) -> str:
    paper_type = str(row.get("round-A_scope_reviewer_paper_type") or "").strip()
    bio = str(row.get("round-A_scope_reviewer_bio_modality_present") or "").strip()
    text = str(row.get("round-A_scope_reviewer_text_component_present") or "").strip()
    bridge = str(row.get("round-A_scope_reviewer_text_bio_bridge_present") or "").strip()

    if paper_type in {"review_editorial", "benchmark_resource", "application_wrapper"}:
        return "EXCLUDE"
    if paper_type == "unclear":
        return "UNCERTAIN"
    if bio == "no" or text == "no" or bridge == "no":
        return "EXCLUDE"
    if bio == "unclear" or text == "unclear" or bridge == "unclear":
        return "UNCERTAIN"
    return "PASS"


def architecture_gate_decision(row: pd.Series) -> str:
    paper_type = str(row.get("round-A_architecture_reviewer_paper_type") or "").strip()
    generative = str(row.get("round-A_architecture_reviewer_generative_model_present") or "").strip()

    if paper_type in {"review_editorial", "benchmark_resource", "application_wrapper"}:
        return "EXCLUDE"
    if paper_type == "unclear":
        return "UNCERTAIN"
    if generative == "no":
        return "EXCLUDE"
    if generative == "unclear":
        return "UNCERTAIN"
    return "PASS"


def needs_adjudication(row: pd.Series) -> bool:
    scope_gate = str(row.get("pilot_roundA_scope_gate") or "")
    architecture_gate = str(row.get("pilot_roundA_architecture_gate") or "")
    scope_paper_type = str(row.get("round-A_scope_reviewer_paper_type") or "").strip()
    architecture_paper_type = str(row.get("round-A_architecture_reviewer_paper_type") or "").strip()

    if scope_gate == "UNCERTAIN" or architecture_gate == "UNCERTAIN":
        return True
    if scope_paper_type and architecture_paper_type:
        if scope_paper_type != architecture_paper_type and "unclear" not in {scope_paper_type, architecture_paper_type}:
            return True
    return False


def aggregate_decision(
    paper_type: Any,
    bio_modality_present: Any,
    text_component_present: Any,
    text_bio_bridge_present: Any,
    generative_model_present: Any,
    foundation_model_evidence: Any,
    fallback_code: Any,
) -> tuple[str, Optional[str], Optional[str]]:
    paper_type = str(paper_type or "").strip()
    bio_modality_present = str(bio_modality_present or "").strip()
    text_component_present = str(text_component_present or "").strip()
    text_bio_bridge_present = str(text_bio_bridge_present or "").strip()
    generative_model_present = str(generative_model_present or "").strip()
    fallback_code = normalize_optional_label(fallback_code)

    if paper_type in {"review_editorial", "benchmark_resource", "application_wrapper"}:
        code_map = {
            "review_editorial": "review_editorial",
            "benchmark_resource": "benchmark_resource",
            "application_wrapper": "application_wrapper",
        }
        return "EXCLUDE", code_map[paper_type], None
    if paper_type == "unclear":
        return "UNCERTAIN", fallback_code, "paper_type_unclear"
    if bio_modality_present == "no":
        return "EXCLUDE", "EC1_no_bio_modality", None
    if bio_modality_present == "unclear":
        return "UNCERTAIN", fallback_code, "bio_modality_unclear"
    if text_component_present == "no":
        return "EXCLUDE", "EC2_no_text_component", None
    if text_component_present == "unclear":
        return "UNCERTAIN", fallback_code, "text_component_unclear"
    if text_bio_bridge_present == "no":
        return "EXCLUDE", "EC2_no_substantive_text_bio_bridge", None
    if text_bio_bridge_present == "unclear":
        return "UNCERTAIN", fallback_code, "text_bio_bridge_unclear"
    if generative_model_present == "no":
        return "EXCLUDE", "EC3_not_generative", None
    if generative_model_present == "unclear":
        return "UNCERTAIN", fallback_code, "generative_status_unclear"
    return "INCLUDE", None, None


def choose_final_columns(df: pd.DataFrame, source_prefix: str) -> pd.DataFrame:
    out = df.copy()
    fields = (
        "paper_type",
        "bio_modality_present",
        "text_component_present",
        "text_bio_bridge_present",
        "generative_model_present",
        "foundation_model_evidence",
        "primary_exclusion_code",
        "uncertainty_reason",
        "evidence_for_text_component",
        "evidence_for_text_bio_bridge",
        "evidence_for_generative_model",
        "boundary_case",
        "decision_rationale",
    )
    for field in fields:
        src_col = f"{source_prefix}_{field}"
        out[f"pilot_selected_{field}"] = out.get(src_col)
    return out


def merge_round_a_fields(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    def get_text_col(name: str) -> pd.Series:
        if name in out.columns:
            return out[name]
        return pd.Series([""] * len(out), index=out.index)

    out["pilot_selected_paper_type"] = out["round-A_scope_reviewer_paper_type"]
    fallback_mask = out["pilot_selected_paper_type"].fillna("").isin(["", "unclear"])
    out.loc[fallback_mask, "pilot_selected_paper_type"] = out.loc[
        fallback_mask, "round-A_architecture_reviewer_paper_type"
    ]
    out["pilot_selected_bio_modality_present"] = out["round-A_scope_reviewer_bio_modality_present"]
    out["pilot_selected_text_component_present"] = out["round-A_scope_reviewer_text_component_present"]
    out["pilot_selected_text_bio_bridge_present"] = out["round-A_scope_reviewer_text_bio_bridge_present"]
    out["pilot_selected_generative_model_present"] = out["round-A_architecture_reviewer_generative_model_present"]
    out["pilot_selected_foundation_model_evidence"] = out["round-A_architecture_reviewer_foundation_model_evidence"]
    out["pilot_selected_primary_exclusion_code"] = out["round-A_scope_reviewer_primary_exclusion_code"].fillna(
        out["round-A_architecture_reviewer_primary_exclusion_code"]
    )
    out["pilot_selected_uncertainty_reason"] = out["round-A_scope_reviewer_uncertainty_reason"].fillna(
        out["round-A_architecture_reviewer_uncertainty_reason"]
    )
    out["pilot_selected_evidence_for_text_component"] = get_text_col(
        "round-A_scope_reviewer_evidence_for_text_component"
    )
    out["pilot_selected_evidence_for_text_bio_bridge"] = get_text_col(
        "round-A_scope_reviewer_evidence_for_text_bio_bridge"
    )
    out["pilot_selected_evidence_for_generative_model"] = get_text_col(
        "round-A_architecture_reviewer_evidence_for_generative_model"
    )
    scope_boundary = get_text_col("round-A_scope_reviewer_boundary_case").fillna("").astype(str).str.strip()
    arch_boundary = get_text_col("round-A_architecture_reviewer_boundary_case").fillna("").astype(str).str.strip()
    out["pilot_selected_boundary_case"] = scope_boundary
    use_arch_boundary = scope_boundary.isin(["", "none", "not_assessed"]) & arch_boundary.ne("")
    out.loc[use_arch_boundary, "pilot_selected_boundary_case"] = arch_boundary[use_arch_boundary]
    combine_boundary = (
        scope_boundary.ne("")
        & arch_boundary.ne("")
        & ~scope_boundary.isin(["none", "not_assessed"])
        & ~arch_boundary.isin(["none", "not_assessed"])
        & scope_boundary.ne(arch_boundary)
    )
    out.loc[combine_boundary, "pilot_selected_boundary_case"] = (
        scope_boundary[combine_boundary] + "|" + arch_boundary[combine_boundary]
    )
    scope_rationale = out["round-A_scope_reviewer_decision_rationale"].fillna("").astype(str).str.strip()
    arch_rationale = out["round-A_architecture_reviewer_decision_rationale"].fillna("").astype(str).str.strip()
    out["pilot_selected_decision_rationale"] = scope_rationale
    both_mask = scope_rationale.ne("") & arch_rationale.ne("")
    arch_only_mask = scope_rationale.eq("") & arch_rationale.ne("")
    out.loc[both_mask, "pilot_selected_decision_rationale"] = scope_rationale[both_mask] + " | " + arch_rationale[both_mask]
    out.loc[arch_only_mask, "pilot_selected_decision_rationale"] = arch_rationale[arch_only_mask]
    return out


def postprocess_results(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["pilot_roundA_scope_gate"] = out.apply(scope_gate_decision, axis=1)
    out["pilot_roundA_architecture_gate"] = out.apply(architecture_gate_decision, axis=1)
    out["pilot_roundA_gate_pattern"] = (
        out["pilot_roundA_scope_gate"].fillna("MISSING") + "|" + out["pilot_roundA_architecture_gate"].fillna("MISSING")
    )
    out["pilot_needs_adjudication"] = out.apply(needs_adjudication, axis=1)

    if "round-B_adjudicator_paper_type" in out.columns:
        out = choose_final_columns(out, "round-B_adjudicator")
        adjudicated_mask = out["round-B_adjudicator_paper_type"].notna()
        round_a_rows = merge_round_a_fields(out.loc[~adjudicated_mask].copy())
        for field in (
            "paper_type",
            "bio_modality_present",
            "text_component_present",
            "text_bio_bridge_present",
            "generative_model_present",
            "foundation_model_evidence",
            "primary_exclusion_code",
            "uncertainty_reason",
            "decision_rationale",
        ):
            out.loc[~adjudicated_mask, f"pilot_selected_{field}"] = round_a_rows[f"pilot_selected_{field}"]
    else:
        out = merge_round_a_fields(out)

    for col in ("pilot_selected_primary_exclusion_code", "pilot_selected_uncertainty_reason"):
        if col in out.columns:
            out[col] = out[col].map(normalize_optional_label)

    aggregate_results = out.apply(
        lambda row: aggregate_decision(
            row["pilot_selected_paper_type"],
            row["pilot_selected_bio_modality_present"],
            row["pilot_selected_text_component_present"],
            row["pilot_selected_text_bio_bridge_present"],
            row["pilot_selected_generative_model_present"],
            row["pilot_selected_foundation_model_evidence"],
            row["pilot_selected_primary_exclusion_code"],
        ),
        axis=1,
        result_type="expand",
    )
    aggregate_results.columns = [
        "pilot_rule_based_decision",
        "pilot_rule_based_exclusion_code",
        "pilot_rule_based_uncertainty_reason",
    ]
    out = pd.concat([out, aggregate_results], axis=1)
    out["pilot_final_decision"] = out["pilot_rule_based_decision"]
    out["pilot_final_exclusion_code"] = out["pilot_rule_based_exclusion_code"]
    missing_exclusion_code = out["pilot_final_exclusion_code"].isna() & out["pilot_final_decision"].ne("INCLUDE")
    out.loc[missing_exclusion_code, "pilot_final_exclusion_code"] = out.loc[
        missing_exclusion_code, "pilot_selected_primary_exclusion_code"
    ]
    out["pilot_final_uncertainty_reason"] = out["pilot_rule_based_uncertainty_reason"]
    missing_uncertainty_reason = out["pilot_final_uncertainty_reason"].isna() & out["pilot_final_decision"].ne("INCLUDE")
    out.loc[missing_uncertainty_reason, "pilot_final_uncertainty_reason"] = out.loc[
        missing_uncertainty_reason, "pilot_selected_uncertainty_reason"
    ]
    out["pilot_final_exclusion_code"] = out["pilot_final_exclusion_code"].map(normalize_optional_label)
    out["pilot_final_uncertainty_reason"] = out["pilot_final_uncertainty_reason"].map(normalize_optional_label)
    out["pilot_needs_manual_review"] = out["pilot_final_decision"].isin(["UNCERTAIN", None])
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run guideline-aligned LatteReview pilot against an OpenAI-style LLM")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1", help="OpenAI-compatible base URL")
    parser.add_argument("--api-key", default="dummy", help="Bearer token for the endpoint")
    parser.add_argument("--model", required=True, help="Served model name")
    parser.add_argument("--input-csv", required=True, help="CSV with at least title and abstract columns")
    parser.add_argument("--output-dir", required=True, help="Directory for run outputs")
    parser.add_argument(
        "--lattereview-path",
        default=str(DEFAULT_LATTEREVIEW_PATH),
        help="Path to a local LatteReview clone; ignored if lattereview is already importable",
    )
    parser.add_argument("--max-concurrent", type=int, default=1, help="Max concurrent requests per reviewer")
    parser.add_argument("--max-records", type=int, default=10, help="Run only the first N records; use 0 for all records")
    parser.add_argument("--timeout", type=int, default=300, help="Per-request timeout in seconds")
    parser.add_argument("--max-tokens", type=int, default=420, help="Per-request maximum generated tokens")
    parser.add_argument(
        "--enable-thinking",
        action="store_true",
        help="Pass DeepSeek-V4 thinking controls in chat_template_kwargs",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=["high", "max"],
        default="high",
        help="DeepSeek-V4 reasoning effort used when --enable-thinking is set",
    )
    parser.add_argument(
        "--pipeline-mode",
        choices=["streaming", "stage-batched"],
        default="streaming",
        help=(
            "streaming runs each record through scope/architecture/adjudication as soon as dependencies are ready; "
            "stage-batched preserves the original LatteReview all-records-per-stage execution"
        ),
    )
    parser.add_argument(
        "--prompt-dir",
        default=str(DEFAULT_PROMPT_DIR),
        help="Directory containing the canonical screening prompt templates",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    global pd
    import pandas as pd  # type: ignore[no-redef]
    started_at = time.time()

    input_csv = Path(args.input_csv).resolve()
    output_dir = Path(args.output_dir).resolve()
    lattereview_path = Path(args.lattereview_path).resolve() if args.lattereview_path else None
    prompt_dir = Path(args.prompt_dir).resolve()

    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV does not exist: {input_csv}")
    if not prompt_dir.exists():
        raise FileNotFoundError(f"Prompt directory does not exist: {prompt_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    ensure_lattereview_importable(lattereview_path)

    df = pd.read_csv(input_csv)
    if "title" not in df.columns or "abstract" not in df.columns:
        raise ValueError("Input CSV must contain 'title' and 'abstract' columns")

    if args.max_records > 0:
        df = df.head(args.max_records).copy()
    else:
        df = df.copy()
    df["_pilot_row_id"] = range(len(df))
    df["title"] = df["title"].fillna("").astype(str)
    df["abstract"] = df["abstract"].fillna("").astype(str)

    if args.pipeline_mode == "streaming":
        raw_results = asyncio.run(
            run_streaming_guideline_pipeline(
                df=df,
                base_url=args.base_url,
                api_key=args.api_key,
                model=args.model,
                max_concurrent=args.max_concurrent,
                timeout=args.timeout,
                max_tokens=args.max_tokens,
                prompt_dir=prompt_dir,
                enable_thinking=args.enable_thinking,
                reasoning_effort=args.reasoning_effort,
                output_dir=output_dir,
            )
        )
    else:
        round_a_workflow = build_round_a_workflow(
            base_url=args.base_url,
            api_key=args.api_key,
            model=args.model,
            max_concurrent=args.max_concurrent,
            timeout=args.timeout,
            max_tokens=args.max_tokens,
            prompt_dir=prompt_dir,
            enable_thinking=args.enable_thinking,
            reasoning_effort=args.reasoning_effort,
        )

        round_a_results = asyncio.run(round_a_workflow(df))
        round_a_results["pilot_roundA_scope_gate"] = round_a_results.apply(scope_gate_decision, axis=1)
        round_a_results["pilot_roundA_architecture_gate"] = round_a_results.apply(architecture_gate_decision, axis=1)
        round_a_results["pilot_needs_adjudication"] = round_a_results.apply(needs_adjudication, axis=1)

        adjudication_inputs = round_a_results.loc[round_a_results["pilot_needs_adjudication"]].copy()
        if len(adjudication_inputs):
            round_b_workflow = build_round_b_workflow(
                base_url=args.base_url,
                api_key=args.api_key,
                model=args.model,
                max_concurrent=args.max_concurrent,
                timeout=args.timeout,
                max_tokens=args.max_tokens,
                prompt_dir=prompt_dir,
                enable_thinking=args.enable_thinking,
                reasoning_effort=args.reasoning_effort,
            )
            round_b_results = asyncio.run(round_b_workflow(adjudication_inputs))
            round_b_columns = [col for col in round_b_results.columns if col.startswith("round-B_")]
            round_b_results = round_b_results[["_pilot_row_id", *round_b_columns]].copy()
            raw_results = round_a_results.merge(round_b_results, on="_pilot_row_id", how="left")
        else:
            raw_results = round_a_results

    results = postprocess_results(raw_results)

    results_csv = output_dir / "guideline_pilot_results.csv"
    summary_json = output_dir / "guideline_pilot_summary.json"
    serialize_for_output(results).to_csv(results_csv, index=False)

    decision_counts = {
        str(k): int(v)
        for k, v in results["pilot_final_decision"].fillna("MISSING").value_counts(dropna=False).to_dict().items()
    }
    agreement_counts = {
        str(k): int(v)
        for k, v in results["pilot_roundA_gate_pattern"].fillna("MISSING").value_counts(dropna=False).to_dict().items()
    }

    summary = {
        "run_started_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": args.model,
        "base_url": args.base_url,
        "prompt_dir": str(prompt_dir),
        "input_csv": str(input_csv),
        "results_csv": str(results_csv),
        "num_records": int(len(results)),
        "max_concurrent": int(args.max_concurrent),
        "max_records": int(args.max_records),
        "max_tokens": int(args.max_tokens),
        "enable_thinking": bool(args.enable_thinking),
        "reasoning_effort": args.reasoning_effort if args.enable_thinking else None,
        "pipeline_mode": args.pipeline_mode,
        "elapsed_seconds": round(time.time() - started_at, 2),
        "decision_counts": decision_counts,
        "roundA_gate_pattern_counts": agreement_counts,
        "adjudication_count": int(results["pilot_needs_adjudication"].sum()),
        "manual_review_count": int(results["pilot_needs_manual_review"].sum()),
    }
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Completed guideline-aligned LatteReview pilot for {len(results)} records")
    print(f"Results CSV: {results_csv}")
    print(f"Summary JSON: {summary_json}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
