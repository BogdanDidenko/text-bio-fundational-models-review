# Fixed-Candidate Validator Change Audit

The first fixed-candidate validator treated the strings `hybrid`, `rvq-text`,
and `c ⊕ t` anywhere in a discovery candidate as evidence that the candidate
contained multiple source objects and therefore required a split.

An exhaustive audit found four affected refs:

- `full_2026-07-06__rec_000090::route_015`: false positive; the source is only
  published-study text sections. "Hybrid" describes the shared downstream context.
- `full_2026-07-06__rec_000090::route_016`: false positive; the source is only
  cell sentences. "Hybrid" describes the shared downstream context.
- `full_2026-07-06__rec_000090::route_032`: true composite source; associated
  biological context, scRNA-seq data, and a question.
- `june_update_2026-06-10__rec_000121::route_006`: true composite source; RVQ
  codes and a task instruction.

An intermediate comma/conjunction rule also falsely flagged `rec_000090`
routes 034 and 035, which are single structured prompts containing several
fields. The final validator therefore uses the two explicitly audited composite
refs (`rec_000090::route_032` and `rec_000121::route_006`) rather than a string
regex. The extraction prompt still independently instructs the LLM to split any
other combined candidate it finds.

`rec_000090` had not succeeded in any
replicate before the fix. `rec_000121` had already satisfied the true split
requirement in all completed runs. Therefore no previously accepted record
changed classification or validation status; only the three failed
`rec_000090` attempts were repeated under validator v1.2 with the identical v1
prompt, schema, candidate inventory, model, and temperature.
