# Parameter pass: predeclared design and gate (2026-10-13, before the first run)

Purpose: for every library call of release 1.2.0 (operations fixed, not changed by this pass), decide
for each declared parameter whether the paper states its value for this data path, using the whole
paper text, and give the value with verbatim evidence. Definitions: `protocol/OPERATION_PARAMETER_GLOSSARY.md`.

Unit: parameter slot = (step_id, call index, parameter name). One Codex run per paper (gpt-5.6-luna,
reasoning high, full untruncated paper text), mechanical checks: every slot answered exactly once;
stated values need >= 1 verbatim quote from the cited section; unspecified slots carry no value.

Published decision per slot = majority status of 3 runs (stated / unspecified); value and evidence
from the lowest-numbered majority run.

Sets: development = stabilization/dev_set.json (10 papers; prompt tuning allowed);
held-out = stabilization/heldout4_set.json (10 papers; rules frozen before its runs);
the remaining 30 papers are run 3 times with the frozen rules.

Gate (held-out, consensus of runs 1-3 vs runs 4-6):
- P1 all runs valid;
- P2 slot status agreement >= 0.90;
- P3 per-parameter unspecified share (parameters with >= 20 held-out slots) differs by <= 0.10
  between the two consensus halves.
Also reported (no threshold): normalised value agreement among slots stated in both halves.
