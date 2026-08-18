You are independently auditing whether a new operator can correctly execute the next routine living-review iteration from the canonical manual.

Canonical repository:
  /Users/bogdan.didenko/lpnu/text-bio-fundational-models-review
Canonical manual:
  /Users/bogdan.didenko/lpnu/text-bio-fundational-models-review/protocol/LIVING_REVIEW_RUNBOOK.md
Assume the calendar date is 2026-08-18 in Europe/Kiev.

SILENT / READ-ONLY SIMULATION:
- Do not modify, create, delete, move, commit, or push files.
- Do not execute the pipeline, network/API calls, Codex/LLM calls, Docling, downloads, builds, deployment, or any command that changes state.
- You may use only read-only inspection commands to understand the manual, runner, config, current state, and referenced contracts.
- Do not ask the user questions and do not see or coordinate with other auditors.
- Write operational commands only as a hypothetical trajectory; do not execute them.
- Treat the manual as authoritative. Do not use conversation history or undocumented guesses.

Task:
Simulate the exact operator trajectory for the next ROUTINE INCREMENTAL UPDATE, from initial orientation through completion. Determine the date interval from the stored state and runbook. For every stage, state:
1. exact command(s) you would issue;
2. prerequisite artifacts and gate conditions;
3. expected output/state transition;
4. stop/recovery behavior if the gate fails;
5. manual inputs, if any, and the only supported way to provide them.

Explicitly cover search/provider completion, cumulative deduplication, abstract enrichment and screening, full-text retrieval, Docling screening, Graph section recovery, full-text screening, eligibility, canonical VLM profiles, taxonomy discovery/classification including F6, crop validation including F7, snapshot, atlas, report, archive, publish, GitHub Pages verification, completion record, and preservation/reuse of expensive Docling/Graph artifacts.

At the end provide:
- the first exact command you would run;
- the next interval and run ID;
- any ambiguity, missing instruction, unsafe shortcut, or contradiction that could cause two agents to diverge;
- a PASS / PASS WITH RISKS / FAIL verdict on whether the manual alone supports a reproducible comparable iteration.

Be concrete and concise. Do not claim to have executed anything.
