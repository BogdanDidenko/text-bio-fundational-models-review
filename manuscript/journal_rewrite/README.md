# Journal rewrite of paper 1: records and checks

This folder documents the rewrite of paper 1 from a PRISMA-style report (v0.5.1) into a journal review
article (v0.6). The rewrite changed the presentation only.

| File | Contents |
|---|---|
| `RULES_APPLIED.md` | The rules followed, their sources and where each was applied |
| `CHANGE_LOG.md` | What changed, and the open items |
| `LABEL_CENSUS.md` | Internal labels in the prose before and after, by category and section (generated) |
| `label_census_before.csv`, `label_census_after.csv` | The census rows behind `LABEL_CENSUS.md` (generated) |
| `number_check_report.md` | Every number of the typed text checked against the previous version (generated) |
| `number_check_allowed_new.csv` | The new numbers, each with its reason (edited by hand) |
| `MOVE_LIST.md`, `move_list.csv` | Where every block of the previous version went (generated) |
| `COMPLIANCE.md` | Lengths and counts against the target conventions (generated) |

Rebuild and check:

```bash
python3 scripts/build_manuscript.py          # article and Supplementary Information
python3 scripts/manuscript_rewrite_audit.py  # census, number check, move list, lengths
```

The scripts need the project's Python environment (pandas and scipy for the synthesis module that the
build imports), TeX Live with the OUP authoring template, and pandoc with XeLaTeX for the supplement.
