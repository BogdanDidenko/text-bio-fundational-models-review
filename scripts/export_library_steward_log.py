"""Export native steward task/visible responses/tool events, excluding reasoning."""

import argparse
import json
from pathlib import Path


def export(agent_id, output):
    logs = list((Path.home() / ".codex/sessions").rglob(f"*{agent_id}.jsonl"))
    if len(logs) != 1:
        raise ValueError(f"Expected one native agent log; found {len(logs)}")
    visible = []
    metadata = {"agent_id": agent_id, "turn_models": [], "reasoning_content_exported": False}
    for line in logs[0].read_text().splitlines():
        event = json.loads(line)
        payload = event.get("payload", {})
        if event.get("type") == "session_meta":
            metadata.update({key: payload.get(key) for key in ("cli_version", "timestamp", "agent_role", "agent_nickname")})
        elif event.get("type") == "turn_context":
            entry = {"model": payload.get("model"), "effort": payload.get("effort")}
            if entry not in metadata["turn_models"]:
                metadata["turn_models"].append(entry)
        elif event.get("type") == "response_item":
            kind = payload.get("type")
            if kind == "message":
                content = "\n".join(item.get("text", "") for item in payload.get("content", []))
                public = payload.get("role") == "assistant" and payload.get("phase") in {"commentary", "final_answer"}
                task = payload.get("role") == "user" and content.startswith(("You are the component-library steward", "Coordinator review:"))
                if public or task:
                    visible.append({"timestamp": event.get("timestamp"), "type": "message", "role": payload.get("role"),
                                    "phase": payload.get("phase"), "content": payload.get("content")})
            elif kind in {"custom_tool_call", "custom_tool_call_output", "function_call", "function_call_output"}:
                visible.append({"timestamp": event.get("timestamp"), **{key: payload[key] for key in
                    ("type", "name", "id", "call_id", "input", "arguments", "output") if key in payload}})
    output.mkdir(parents=True, exist_ok=True)
    (output / "steward.visible.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in visible))
    (output / "steward.metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"visible_events": len(visible), **metadata}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    export(args.agent_id, args.output)
