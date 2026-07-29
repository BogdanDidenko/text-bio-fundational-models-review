# Template execution contract

## Reference

- Retained template: `/Users/bogdan.didenko/lpnu/review/data/health_intelligence_conference_2026_template/health_intelligence_conference_2026_abstract_template_EN.docx`
- SHA-256: `093e3f6a4e79b717d836032b6a994b121523cf801658b2d4074333c4e851b946`
- Reference pages: 1
- Sections: 1
- Reference render: `build/fidelity_diff_07/a_render/page-1.png`
- Final render: `build/fidelity_diff_07/b_render/page-1.png`
- Structural evidence: `build/template_audit/`, `build/final_section_audit.txt`, and `build/package_preservation_audit.json`

## Page system

- A4 portrait: 8.27 x 11.69 in.
- Margins: left/right 0.65 in; top/bottom 0.75 in.
- Header and footer use the retained template parts; first-page and odd/even variants are disabled.
- Main title/metadata/abstract and figures are full width.
- Main prose is the retained one-row, two-column table with zeroed cell margins.

## Typography and components

- Title: Arial bold, 12.5 pt, retained two-line capacity.
- Author line: Arial bold, 9 pt.
- Metadata and structured abstract: Times New Roman, 8.5 pt.
- Column body: Times New Roman, 8.2 pt; Arial bold section headings.
- Figure captions: Times New Roman italic, 7 pt.
- References: Times New Roman, 7.2 pt, separate left-aligned paragraphs.
- Header/footer, rule positions, margins, and page numbering remain source-derived.
- The template's demonstration benchmark table was an editable example and was removed. One full-width taxonomy figure was inserted before the retained two-column body. The workflow figure remains a supplementary reproducibility artifact and is not placed in the manuscript.

## Slot map

- Title, authors, affiliations, correspondence, and received date: replaced in the retained top block.
- Structured abstract: `Motivation`, `Results`, and `Availability and implementation` replaced in place.
- Full-width content before the body table: taxonomy figure and caption.
- Left column: Introduction, Methods, and the structural part of Results.
- Right column: continuation of Results, Discussion and Conclusion, Availability, Funding, and References.
- Author, affiliation, correspondence, received-date, and funding placeholders are intentional because source metadata were not supplied.

## Fidelity gates

- Final section audit matches the reference page size, orientation, and margins.
- `word/header1.xml`, `word/footer1.xml`, `word/theme/theme1.xml`, and `word/fontTable.xml` are byte-identical to the reference.
- No reference package part is missing; only `word/media/image1.png` and `word/media/image2.png` were added.
- Final PDF renders as exactly one A4 page.
- `build/render_08/page-1.png` was inspected at original resolution; no clipping, overlap, missing glyphs, or broken figure labels were observed.
