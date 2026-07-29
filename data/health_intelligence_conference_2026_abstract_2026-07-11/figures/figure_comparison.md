# Figure-generation comparison

## Scope

The same taxonomy fact contract was used to compare PaperBanana, AutoFigure, and a deterministic SVG implementation. The figure had to communicate that an input representation is a route, preserve all five carrier families and 15 evidence-grounded subtypes, show route and record denominators, remain legible at one-page conference scale, and introduce no unsupported examples.

## Candidates

| Candidate | Method | Iteration | Content fidelity | Page-scale readability | Main failure mode |
|---|---|---:|---:|---:|---|
| PaperBanana | DiagramIR to Graphviz | structural smoke | low | low | Omitted all subtypes, record denominators, and corpus totals; large unused space |
| AutoFigure | LLM-generated SVG | initial | medium | medium | Preserved family route counts but invented examples and omitted subtypes and record counts |
| AutoFigure | critique/refinement loop | 1 | low-medium | medium | Added an irrelevant placeholder, retained invented examples, and still omitted subtypes and record counts |
| Deterministic SVG | fact-contract-driven vector layout | 0 | high | high | Abbreviated several subtype labels |
| Deterministic SVG | visual QA revision | 1 (selected) | complete | high | No unresolved factual or clipping issue in the standalone render |

## Decision

The deterministic SVG was selected. It is the only candidate that displays the exact route definition, all five carrier families, all 15 codebook subtypes, family-level route and record counts, orthogonal annotations, and corpus totals without generated examples. Its second iteration restored full subtype terminology, wrapped long labels, removed collisions, and compacted the footer.

PaperBanana was useful for testing a graph-first structural representation, but its default Graphviz arrangement was too sparse for the conference template. AutoFigure produced a more polished initial composition and its logged refinement increased its internal score from 6.0 to 7.7; however, the refinement reduced factual fidelity by adding a placeholder and retaining unsupported examples. AutoFigure's placeholder-oriented evaluation criterion was not appropriate for this evidence figure, so its score was not used as the selection criterion.

The selected figure remains generated from `analysis/figure_fact_contract.json` by `scripts/build_health_intelligence_conference_abstract.py`. SVG is the canonical source; PNG is a rendered preview and DOCX insertion asset.

