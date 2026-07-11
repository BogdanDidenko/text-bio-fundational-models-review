#!/usr/bin/env python3
"""Local OpenAI-compatible wrapper around `codex exec`.

This is a narrow shim for local Docling/Docling Graph experiments. It exposes
`POST /v1/chat/completions` on localhost, accepts OpenAI-style text or
multimodal messages, invokes `codex exec`, and returns an OpenAI-compatible
response with one assistant message.

It is intentionally local-only and slow: each request starts one Codex CLI run.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import signal
import subprocess
import tempfile
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPO = Path(__file__).resolve().parents[2]
JSON_OBJECT_INSTRUCTION = (
    "Return only valid JSON. Do not wrap it in Markdown fences, prose, or comments."
)


def parse_data_url(url: str) -> tuple[str, bytes]:
    match = re.match(r"^data:image/([a-zA-Z0-9.+-]+);base64,(.*)$", url, re.S)
    if not match:
        raise ValueError("Only data:image/*;base64 image_url payloads are supported")
    ext = match.group(1).lower().replace("jpeg", "jpg")
    return ext, base64.b64decode(match.group(2), validate=False)


def content_to_text_and_images(content: Any, image_paths: list[Path]) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for part in content:
        if not isinstance(part, dict):
            continue
        if part.get("type") == "text":
            text = part.get("text")
            if text:
                parts.append(str(text))
        elif part.get("type") == "image_url":
            image_url = (part.get("image_url") or {}).get("url")
            if image_url:
                ext, data = parse_data_url(str(image_url))
                tmp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=f".{ext}", prefix="codex_vlm_"
                )
                tmp.write(data)
                tmp.close()
                image_paths.append(Path(tmp.name))
    return "\n\n".join(part.strip() for part in parts if part.strip())


def extract_prompt_and_images(payload: dict[str, Any]) -> tuple[str, list[Path]]:
    messages = payload.get("messages") or []
    prompt_parts: list[str] = []
    image_paths: list[Path] = []

    for message in messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or "user")
        text = content_to_text_and_images(message.get("content"), image_paths)
        if not text:
            continue
        prompt_parts.append(f"[{role}]\n{text.strip()}")

    prompt = "\n\n".join(p.strip() for p in prompt_parts if p and p.strip())
    if not prompt:
        prompt = "Describe this image for retrieval."
    return prompt, image_paths


def response_schema(payload: dict[str, Any]) -> tuple[dict[str, Any] | None, bool]:
    response_format = payload.get("response_format")
    if not isinstance(response_format, dict):
        return None, False
    rtype = response_format.get("type")
    if rtype == "json_schema":
        json_schema = response_format.get("json_schema")
        if isinstance(json_schema, dict):
            schema = json_schema.get("schema")
            if isinstance(schema, dict):
                return schema, True
        schema = response_format.get("schema")
        if isinstance(schema, dict):
            return schema, True
        return None, True
    if rtype == "json_object":
        return None, True
    return None, False


def normalize_model(requested: Any, default_model: str) -> str:
    model = str(requested or default_model)
    if model.startswith("openai/"):
        model = model.split("/", 1)[1]
    if model.startswith("codex/"):
        model = model.split("/", 1)[1]
    return model


def run_codex(
    *,
    prompt: str,
    image_paths: list[Path],
    model: str,
    timeout: int,
    schema: dict[str, Any] | None,
    wants_json: bool,
    sandbox: str,
    cwd: Path,
    extra_args: list[str],
) -> str:
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        output_path = Path(tmp.name)
    schema_path: Path | None = None
    try:
        if wants_json and schema is None:
            prompt = f"{prompt.rstrip()}\n\n{JSON_OBJECT_INSTRUCTION}"
        if schema is not None:
            with tempfile.NamedTemporaryFile(
                "w+", suffix=".schema.json", delete=False
            ) as sf:
                schema_path = Path(sf.name)
                json.dump(schema, sf, ensure_ascii=False)
                sf.write("\n")
        cmd = [
            "codex",
            "-a",
            "never",
            "exec",
            "--model",
            model,
            "--cd",
            str(cwd),
            "--sandbox",
            sandbox,
            "--ignore-user-config",
            "--ignore-rules",
            "--ephemeral",
            "--output-last-message",
            str(output_path),
        ]
        if schema_path is not None:
            cmd += ["--output-schema", str(schema_path)]
        cmd += extra_args
        for image_path in image_paths:
            cmd += ["--image", str(image_path)]
        cmd.append("-")

        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(input=prompt, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate()
            raise subprocess.TimeoutExpired(cmd, timeout) from exc
        final_message = output_path.read_text(encoding="utf-8").strip()
        if proc.returncode != 0:
            stderr_tail = "\n".join(stderr.strip().splitlines()[-20:])
            raise RuntimeError(
                f"codex exec failed with returncode={proc.returncode}: {stderr_tail}"
            )
        return final_message or stdout.strip()
    finally:
        output_path.unlink(missing_ok=True)
        if schema_path is not None:
            schema_path.unlink(missing_ok=True)


def openai_response(model: str, content: str) -> dict[str, Any]:
    now = int(time.time())
    return {
        "id": f"chatcmpl-codex-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": now,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "CodexOpenAICompat/0.2"

    def _write_json(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/health", "/v1/health"}:
            self._write_json(200, {"status": "ok"})
        elif path == "/v1/models":
            self._write_json(
                200,
                {
                    "object": "list",
                    "data": [
                        {
                            "id": self.server.codex_model,  # type: ignore[attr-defined]
                            "object": "model",
                            "owned_by": "local-codex-cli",
                            "permission": [],
                        }
                    ],
                },
            )
        else:
            self._write_json(404, {"error": {"message": "not found"}})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/v1/chat/completions":
            self._write_json(404, {"error": {"message": "not found"}})
            return

        image_paths: list[Path] = []
        try:
            length = int(self.headers.get("content-length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if payload.get("stream"):
                self._write_json(
                    400,
                    {
                        "error": {
                            "message": (
                                "stream=true is not supported by this local wrapper"
                            )
                        }
                    },
                )
                return
            prompt, image_paths = extract_prompt_and_images(payload)
            model = normalize_model(payload.get("model"), self.server.codex_model)  # type: ignore[attr-defined]
            schema, wants_json = response_schema(payload)
            content = run_codex(
                prompt=prompt,
                image_paths=image_paths,
                model=str(model),
                timeout=self.server.codex_timeout,  # type: ignore[attr-defined]
                schema=schema,
                wants_json=wants_json,
                sandbox=self.server.codex_sandbox,  # type: ignore[attr-defined]
                cwd=self.server.codex_cwd,  # type: ignore[attr-defined]
                extra_args=self.server.codex_extra_args,  # type: ignore[attr-defined]
            )
            self._write_json(200, openai_response(str(model), content))
        except Exception as exc:
            self._write_json(500, {"error": {"message": repr(exc)}})
        finally:
            for image_path in image_paths:
                image_path.unlink(missing_ok=True)

    def log_message(self, fmt: str, *args: Any) -> None:
        if self.server.quiet:  # type: ignore[attr-defined]
            return
        super().log_message(fmt, *args)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument(
        "--sandbox",
        default="read-only",
        choices=["read-only", "workspace-write", "danger-full-access"],
    )
    parser.add_argument("--cwd", type=Path, default=REPO)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--codex-arg",
        action="append",
        default=[],
        help="Extra argument passed through to `codex exec`; repeat for multiple args.",
    )
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.codex_model = args.model  # type: ignore[attr-defined]
    server.codex_timeout = args.timeout  # type: ignore[attr-defined]
    server.codex_sandbox = args.sandbox  # type: ignore[attr-defined]
    server.codex_cwd = args.cwd.resolve()  # type: ignore[attr-defined]
    server.codex_extra_args = args.codex_arg  # type: ignore[attr-defined]
    server.quiet = args.quiet  # type: ignore[attr-defined]
    print(
        json.dumps(
            {
                "status": "listening",
                "base_url": f"http://{args.host}:{args.port}/v1",
                "chat_completions_url": f"http://{args.host}:{args.port}/v1/chat/completions",
                "model": args.model,
                "sandbox": args.sandbox,
                "cwd": str(args.cwd.resolve()),
            }
        ),
        flush=True,
    )
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
