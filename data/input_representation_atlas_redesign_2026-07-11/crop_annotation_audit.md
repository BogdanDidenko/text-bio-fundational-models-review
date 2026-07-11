# Model figure crop audit

This ledger preserves model-specific source-figure selection and normalized crop coordinates. Source pixels are not altered; the web atlas applies the recorded crop as a viewport over the canonical PNG.

- Models: 111
- Cropped source figures: 103
- Explicit no-suitable-figure cases: 8
- Initial crops retained: 74
- Figures reselected and recropped: 29
- Full or near-full crops: 11
- Subagent logs: `data/input_representation_atlas_redesign_2026-07-11/subagents`

A `no_suitable_figure` status is intentional: performance plots, outputs, logos, and other non-input figures are not used as visual evidence.
