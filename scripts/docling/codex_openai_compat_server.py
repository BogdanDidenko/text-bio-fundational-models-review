#!/usr/bin/env python3
"""Local OpenAI-compatible wrapper around `codex exec`.

This is a narrow shim for Docling picture-description enrichment. It exposes
`POST /v1/chat/completions` on localhost, accepts OpenAI-style multimodal
messages with data-URL images, invokes `codex exec --image ...`, and returns an
OpenAI-compatible response with one assistant message.

It is intentionally local-only and slow: each request starts one Codex CLI run.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import tempfile
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]


def parse_data_url(url: str) -> tuple[str, bytes]:
    match = re.match(r"^data:image/([a-zA-Z0-9.+-]+);base64,(.*)$", url, re.S)
    if not match:
        raise ValueError("Only data:image/*;base64 image_url payloads are supported")
    ext = match.group(1).lower().replace("jpeg", "jpg")
    return ext, base64.b64decode(match.group(2), validate=False)


def extract_prompt_and_images(payload: dict[str, Any]) -> tuple[str, list[Path]]:
    messages = payload.get("messages") or []
    prompt_parts: list[str] = []
    image_paths: list[Path] = []

    for message in messages:
        content = message.get("content")
        if isinstance(content, str):
            prompt_parts.append(content)
            continue
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "text":
                text = part.get("text")
                if text:
                    prompt_parts.append(str(text))
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

    prompt = "\n\n".join(p.strip() for p in prompt_parts if p and p.strip())
    if not prompt:
        prompt = "Describe this image for retrieval."
    return prompt, image_paths


def run_codex(prompt: str, image_paths: list[Path], model: str, timeout: int) -> str:
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as tmp:
        output_path = Path(tmp.name)
    try:
        cmd = [
            "codex",
            "exec",
            "--model",
            model,
            "--sandbox",
            "read-only",
            "--output-last-message",
            str(output_path),
        ]
        for image_path in image_paths:
            cmd += ["--image", str(image_path)]
        cmd.append("-")

        proc = subprocess.run(
            cmd,
            cwd=REPO,
            text=True,
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        final_message = output_path.read_text(encoding="utf-8").strip()
        if proc.returncode != 0:
            stderr_tail = "\n".join(proc.stderr.strip().splitlines()[-20:])
            raise RuntimeError(
                f"codex exec failed with returncode={proc.returncode}: {stderr_tail}"
            )
        return final_message or proc.stdout.strip()
    finally:
        output_path.unlink(missing_ok=True)


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
    server_version = "CodexOpenAICompat/0.1"

    def _write_json(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._write_json(200, {"status": "ok"})
        elif self.path == "/v1/models":
            self._write_json(
                200,
                {
                    "object": "list",
                    "data": [
                        {
                            "id": self.server.codex_model,  # type: ignore[attr-defined]
                            "object": "model",
                            "owned_by": "local-codex-cli",
                        }
                    ],
                },
            )
        else:
            self._write_json(404, {"error": {"message": "not found"}})

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self._write_json(404, {"error": {"message": "not found"}})
            return

        image_paths: list[Path] = []
        try:
            length = int(self.headers.get("content-length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            prompt, image_paths = extract_prompt_and_images(payload)
            model = payload.get("model") or self.server.codex_model  # type: ignore[attr-defined]
            content = run_codex(
                prompt=prompt,
                image_paths=image_paths,
                model=str(model),
                timeout=self.server.codex_timeout,  # type: ignore[attr-defined]
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
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.codex_model = args.model  # type: ignore[attr-defined]
    server.codex_timeout = args.timeout  # type: ignore[attr-defined]
    server.quiet = args.quiet  # type: ignore[attr-defined]
    print(
        json.dumps(
            {
                "status": "listening",
                "url": f"http://{args.host}:{args.port}/v1/chat/completions",
                "model": args.model,
            }
        ),
        flush=True,
    )
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
