# Blind Agent Dry-Run Prompt

The following prompt was sent unchanged to three independent explorer agents.
They received no forked conversation context.

```text
You are an independent blind evaluator of the living-review operator instructions.

Workspace: /Users/bogdan.didenko/lpnu/review
Primary instruction: /Users/bogdan.didenko/lpnu/review/protocol/LIVING_REVIEW_RUNBOOK.md

Perform a SILENT DRY RUN for the next routine incremental review iteration.

Rules:
- Do not modify, create, delete, move, stage, commit, or push any file.
- Do not execute the scientific pipeline, call network services, start servers, invoke LLMs, or generate artifacts.
- Read-only inspection of the runbook and static repository files it explicitly references is permitted.
- Write the exact shell commands you would execute, but do not execute those commands.
- Do not use prior conversation context and do not infer undocumented steps as established protocol.
- When the instructions are ambiguous or incomplete, identify the ambiguity rather than silently filling it in.

Your response must contain:
1. The current published cursor and the exact next inclusive search interval you would use, including how the end date is chosen.
2. The ordered operator procedure from initial doctor/preflight through all 18 stages, manual gates, publication, deployment verification, and completion record.
3. For every major boundary: required input, success condition, denominator reconciliation, and failure/recovery action.
4. The exact screening payloads and role/model topology at abstract and full-text stages.
5. The Docling, Docling Graph, taxonomy, crop, snapshot, and atlas modes, including what may and may not be reused.
6. The commands for method-lock verification, run planning, preflight, execution/resume, status/doctor, artifact manifest creation, independent backup verification/restore, publication, and remote verification.
7. A final list of anything that would still prevent an unfamiliar agent from executing the next iteration reproducibly and comparably.

Be operational and specific. Do not claim to have run any command.
```
