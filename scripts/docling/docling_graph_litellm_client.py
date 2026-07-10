"""LiteLLM client adapter for Docling Graph OpenAI-compatible endpoints."""

from __future__ import annotations

import json
from typing import Any, Mapping

import litellm

from docling_graph.exceptions import ClientError
from docling_graph.llm_clients.response_handler import ResponseHandler


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
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.max_tokens = max_tokens
        self.temperature = temperature

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

        try:
            response = litellm.completion(
                **request,
            )
        except Exception as exc:
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
