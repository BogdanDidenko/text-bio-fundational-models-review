# Representation block library: supervised development release

Release `0.1.0`, created 2026-10-04. This package implements the shared annotation
format, reusable description catalog, library-steward procedure and static Pages
browser. It uses existing four-paper source-reviewed trajectories. No new corpus
extraction, PDF/VLM conversion, eligibility change or canonical taxonomy migration
was performed.

## Contents and scope

The candidate catalog has 91 definitions: 34 representations, 29 operations,
20 functional components and eight composite motifs. It contains 117 reviewed
exact-label mappings and 18 steward decisions. The source assemblies retain all
47 pilot task/phase trajectories for InstructCell, ChatNT, MUPAD and X-Cell.

192 distinct unmapped source labels remain in the extension queue, with every
original occurrence available. They require semantic review; these counts do not
measure unique computational mechanisms. Global mappings were reviewed on these
four records. Application to further records requires a collision/context review.

`catalog_seed.json` is steward-owned source. `STEWARD_TASK.md`, `dispatch.json`,
`STEWARD_REVIEW.md` and `visible_sessions/` preserve the actual task, native session,
source decisions and visible tool/response trace. The native session used
GPT-6.1 Sol, reasoning medium. Hidden reasoning is excluded.

`pilot_input.jsonl` is the complete trajectory snapshot, with relative artifact
paths and original artifact hashes. `evidence_snapshot.json` preserves all 89 unique
quoted evidence records with section/document hashes, heading trails and
capture-time offsets. All quotations matched their own original selected section
at capture. Every original trajectory field is restored identically by the
compiled assemblies; verification checks full data equality.

`release/` is the current generated projection. `releases/0.1.0/` preserves the
immutable release, seed and hash lock. The build refuses changed frozen output
under the same release. Public copies are under
`docs/input-representation-atlas/component-library/data/`.

Source packets and original pilot artifacts remain at their existing locations
under `analysis/nickerson_taxonomy_2026-09-20/object_unit_reassessment_2026-09-22/`.
The source originals are not duplicated in this package. Source evidence uses
recovered-Markdown section IDs; native PDF item geometry remains unavailable.

## Important decisions

- Every graph use retains model, task, one phase and component role.
- Library definitions supply type reuse. Instance identity needs evidence.
- Symbolic dimensions and axes remain intact; original numbers remain in quotations.
- Shared values, repeated computations and shared parameters have explicit link
  types. The adaptation inferred no cross-context identity links.
- Composite examples contain their actual subgraphs, boundary operands and external
  receiving ports. Constituent arrays imply no sequential ordering of branches.
- RNA condition internals remain uncertain on the preserved MUPAD instance.
  The initial uncertainty-based representation type was removed during review.
- Mechanical matching, lossless restoration and schema integrity remain distinct
  from scientific entailment and coverage.

## Reproduce

Use Python with Pydantic `2.13.5`, as pinned in the Pages workflow:

```bash
python scripts/build_representation_library.py --check
python -m unittest discover -s tests -p test_representation_library.py
```

The original capture used the existing isolated environment:
`/Users/bogdan.didenko/.cache/codex-envs/nickerson-docling-2026-09-29/bin/python`.
`--capture-inputs` requires local original sources. Regular checks are reproducible
from committed snapshots and do not contact model providers.

The shared protocol is `protocol/REPRESENTATION_LIBRARY_GUIDE.md`; the reusable
steward task is `protocol/REPRESENTATION_LIBRARY_STEWARD_PROMPT.md`.
`review_representation_library_change.py` compares a frozen seed and proposed seed
and flags changes requiring author approval and affected source labels.

## Interface validation

`browser_qa/` contains desktop/mobile screenshots and the automated report. Search,
kind/paper filtering, complete evidence, original-paper asset loading, source
assembly navigation, task/phase switching and the extension/steward views passed.
No page overflow, clipped labels or browser errors were found. The coordinator
visually inspected the rendered screenshots. The existing reviewed atlas annotation
check also passed; its canonical data were unchanged.

## Remaining scientific work

Review pending labels and explicit source gaps. Normalize port roles only after
source-backed matching. Evaluate documented cross-context resource identity and
the remaining hard cases before extending reconstruction across the corpus.
Clustering, final taxonomy synthesis and canonical publication remain subsequent
stages. This development release supplies their reproducible input-description
infrastructure.
