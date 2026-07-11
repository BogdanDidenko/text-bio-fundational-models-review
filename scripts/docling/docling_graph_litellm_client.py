"""LiteLLM client adapter for Docling Graph OpenAI-compatible endpoints."""

from __future__ import annotations

import json
import hashlib
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import litellm

from docling_graph.exceptions import ClientError
from docling_graph.llm_clients.response_handler import ResponseHandler


def strict_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Convert a Pydantic schema to the strict subset accepted by Codex."""
    value = deepcopy(schema)

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                properties = node.get("properties") or {}
                node["additionalProperties"] = False
                node["required"] = list(properties)
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    return value


class LiteLLMEndpointClient:
    """Small Docling Graph client for one OpenAI-compatible endpoint."""

    def __init__(
        self,
        *,
        model: str,
        base_url: str,
        api_key: str,
        timeout_s: int,
        max_tokens: int | None,
        temperature: float,
        log_path: Path | None = None,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.log_path = log_path
        self.request_index = 0

    def _log(self, payload: dict[str, Any]) -> None:
        if self.log_path is None:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def get_json_response(
        self,
        prompt: str | Mapping[str, str],
        schema_json: str,
        structured_output: bool = True,
        response_top_level: str = "object",
        response_schema_name: str = "docling_graph_extraction",
        **_: Any,
    ) -> dict[str, Any] | list[Any]:
        response_format: dict[str, Any] = {"type": "json_object"}
        try:
            schema = json.loads(schema_json)
        except json.JSONDecodeError:
            schema = None
        if isinstance(schema, dict) and schema:
            response_format = {
                "type": "json_schema",
                "json_schema": {"name": response_schema_name, "schema": schema},
            }
        if not structured_output:
            response_format = {"type": "json_object"}

        request: dict[str, Any] = {
            "model": self.model,
            "messages": self._messages(prompt),
            "api_base": self.base_url,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "timeout": self.timeout_s,
            "response_format": response_format,
        }
        if self.max_tokens is not None:
            request["max_tokens"] = self.max_tokens

        self.request_index += 1
        request_index = self.request_index
        started = time.time()
        prompt_payload = prompt if isinstance(prompt, str) else dict(prompt)
        self._log(
            {
                "event": "request",
                "timestamp_utc": self._timestamp(),
                "request_index": request_index,
                "model": self.model,
                "base_url": self.base_url,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "structured_output": structured_output,
                "response_top_level": response_top_level,
                "response_schema_name": response_schema_name,
                "prompt": prompt_payload,
                "prompt_sha256": hashlib.sha256(
                    json.dumps(
                        prompt_payload, ensure_ascii=False, sort_keys=True, default=str
                    ).encode()
                ).hexdigest(),
                "schema_json": schema_json,
            }
        )
        try:
            response = litellm.completion(
                **request,
            )
        except Exception as exc:
            self._log(
                {
                    "event": "error",
                    "timestamp_utc": self._timestamp(),
                    "request_index": request_index,
                    "elapsed_seconds": round(time.time() - started, 3),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            raise ClientError(
                f"LiteLLM call failed: {type(exc).__name__}",
                details={
                    "model": self.model,
                    "api_base": self.base_url,
                    "error": str(exc),
                },
                cause=exc,
            ) from exc

        choices = response.get("choices", [])
        if not choices:
            raise ClientError("No choices in response", details={"model": self.model})
        content = choices[0].get("message", {}).get("content") or ""
        self._log(
            {
                "event": "response",
                "timestamp_utc": self._timestamp(),
                "request_index": request_index,
                "elapsed_seconds": round(time.time() - started, 3),
                "finish_reason": choices[0].get("finish_reason"),
                "content": content,
                "response_model": response.get("model"),
                "usage": response.get("usage"),
            }
        )
        return ResponseHandler.parse_json_response(
            content,
            client_name=self.__class__.__name__,
            aggressive_clean=False,
            truncated=choices[0].get("finish_reason") == "length",
            max_tokens=self.max_tokens,
        )

    def _messages(self, prompt: str | Mapping[str, str]) -> list[dict[str, str]]:
        if isinstance(prompt, Mapping):
            out = []
            if prompt.get("system"):
                out.append({"role": "system", "content": prompt["system"]})
            if prompt.get("user"):
                out.append({"role": "user", "content": prompt["user"]})
            return out or [{"role": "user", "content": ""}]
        return [{"role": "user", "content": prompt}]
