"""Ground Docling Graph evidence nodes to chunks and derived full sections."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.docling.build_fulltext_screening_context import Section


ROOT = Path(__file__).resolve().parents[2]


def rel(path: Path | str | None) -> str:
    if not path:
        return ""
    value = Path(path)
    if not value.is_absolute():
        value = ROOT / value
    try:
        return str(value.relative_to(ROOT))
    except ValueError:
        return str(value)


def find_provenance(context: Any) -> Path | None:
    manager = getattr(context, "output_manager", None)
    if not manager:
        return None
    graph_dir = manager.get_docling_graph_dir()
    candidates = [
        graph_dir / "provenance.json",
        manager.get_debug_dir() / "dense_provenance.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def compact_provenance_chunks(provenance: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(provenance, dict):
        return {}
    chunks = provenance.get("chunks") or {}
    if not isinstance(chunks, dict):
        return {}
    return {str(key): value for key, value in chunks.items() if isinstance(value, dict)}


def graph_nodes_by_grounding_item(context: Any) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    data_sources: dict[str, dict[str, Any]] = {}
    input_representations: dict[str, dict[str, Any]] = {}
    for node_id, data in context.knowledge_graph.nodes(data=True):
        node = {"node_id": str(node_id), **dict(data)}
        source_label = node.get("source_label")
        representation_label = node.get("representation_label")
        if source_label:
            data_sources[str(source_label)] = node
        if representation_label:
            input_representations[str(representation_label)] = node
    return data_sources, input_representations


def chunk_anchor_spans(provenance_view: dict[str, Any], chunk_id: int) -> list[dict[str, int]]:
    spans = provenance_view.get("spans") or []
    if not isinstance(spans, list):
        return []
    return [
        {"start": int(span["start"]), "end": int(span["end"])}
        for span in spans
        if isinstance(span, dict)
        and span.get("chunk") == chunk_id
        and isinstance(span.get("start"), int)
        and isinstance(span.get("end"), int)
    ]


def heading_key(value: str | None) -> str:
    if not value:
        return ""
    text = str(value).casefold()
    text = text.replace("&amp;", "&")
    text = text.replace("‐", "-").replace("‑", "-").replace("–", "-").replace("—", "-")
    text = " ".join(text.split())
    text = text.lstrip("#").strip()
    parts = text.split(" ", 1)
    if len(parts) == 2 and all(ch.isdigit() or ch == "." for ch in parts[0].rstrip(".")):
        text = parts[1]
    return "".join(ch for ch in text if ch.isalnum())


def clean_section_text(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()


def parse_markdown_sections_for_derivation(path: Path) -> list[tuple[Section, list[str]]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    headings: list[tuple[int, int, str]] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        hashes = len(stripped) - len(stripped.lstrip("#"))
        if hashes < 1 or hashes > 8 or not stripped[hashes:].startswith(" "):
            continue
        heading = stripped[hashes:].strip()
        if heading:
            headings.append((idx, hashes, heading))
    sections: list[tuple[Section, list[str]]] = []
    trail: list[tuple[int, str]] = []
    for pos, (start, level, heading) in enumerate(headings):
        while trail and trail[-1][0] >= level:
            trail.pop()
        trail.append((level, heading))
        end = len(lines)
        for next_start, next_level, _ in headings[pos + 1 :]:
            if next_level <= level:
                end = next_start
                break
        body = clean_section_text("\n".join(lines[start + 1 : end]))
        if body:
            sections.append(
                (
                    Section(level=level, heading=heading, body=body, start_line=start + 1, end_line=end),
                    [item_heading for _, item_heading in trail],
                )
            )
    return sections


def chunk_body_excerpt(chunk_text: str, heading_path: list[str]) -> str:
    text = chunk_text
    for heading in heading_path:
        if text.startswith(heading):
            text = text[len(heading) :].lstrip()
    return " ".join(text.split())[:320]


def section_contains_text(section: Section, text: str) -> bool:
    if not text:
        return False
    section_text = " ".join(section.body.split()).casefold()
    needle = " ".join(text.split()).casefold()
    if needle and needle in section_text:
        return True
    words = [word for word in needle.split() if len(word) > 3]
    if len(words) < 8:
        return False
    return " ".join(words[:16]) in section_text


def derive_full_section(
    *,
    row: dict[str, str],
    heading_path: list[str],
    chunk_text: str,
    evidence_quote: str | None,
) -> dict[str, Any]:
    markdown = ROOT / row["markdown"] if row.get("markdown") else None
    if not markdown or not markdown.exists():
        return {
            "status": "missing_markdown",
            "derivation_source": "docling_markdown_heading_boundary_from_docling_graph_heading_path",
            "source_markdown": rel(markdown) if markdown else "",
        }

    heading_candidates = [heading for heading in heading_path if heading]
    if not heading_candidates:
        return {
            "status": "missing_heading_path",
            "derivation_source": "docling_markdown_heading_boundary_from_docling_graph_heading_path",
            "source_markdown": rel(markdown),
        }

    sections = parse_markdown_sections_for_derivation(markdown)
    excerpt = chunk_body_excerpt(chunk_text, heading_candidates)
    target_trail = [heading_key(heading) for heading in heading_candidates]
    if not all(target_trail):
        return {
            "status": "invalid_heading_path",
            "derivation_source": "docling_markdown_heading_boundary_from_docling_graph_heading_path",
            "source_markdown": rel(markdown),
            "heading_path": heading_candidates,
        }
    candidates: list[tuple[int, Section, str]] = []
    for section, section_trail in sections:
        if [heading_key(heading) for heading in section_trail] != target_trail:
            continue
        score = 0
        matched_by = "exact_heading_path"
        if evidence_quote and section_contains_text(section, evidence_quote):
            score += 2
            matched_by = "exact_heading_path+evidence_quote"
        elif section_contains_text(section, excerpt):
            score += 1
            matched_by = "exact_heading_path+chunk_excerpt"
        candidates.append((score, section, matched_by))

    if not candidates:
        return {
            "status": "heading_path_not_found",
            "derivation_source": "docling_markdown_heading_boundary_from_docling_graph_heading_path",
            "source_markdown": rel(markdown),
            "heading_path": heading_candidates,
        }
    candidates.sort(key=lambda item: item[0], reverse=True)
    if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
        return {
            "status": "ambiguous_heading_path",
            "derivation_source": "docling_markdown_heading_boundary_from_docling_graph_heading_path",
            "source_markdown": rel(markdown),
            "heading_path": heading_candidates,
            "matching_sections": [
                {"line_start": section.start_line, "line_end": section.end_line}
                for _, section, _ in candidates
            ],
        }
    _, section, matched_by = candidates[0]
    return {
        "status": "ok",
        "derivation_source": "docling_markdown_heading_boundary_from_docling_graph_heading_path",
        "source_markdown": rel(markdown),
        "matched_by": matched_by,
        "heading_path": heading_candidates,
        "heading": section.heading,
        "heading_level": section.level,
        "line_start": section.start_line,
        "line_end": section.end_line,
        "text": section.body,
        "original_chars": len(section.body),
        "contains_evidence_quote": bool(evidence_quote and section_contains_text(section, evidence_quote)),
        "contains_chunk_excerpt": section_contains_text(section, excerpt),
    }


def provenance_chunk_payload(
    *,
    row: dict[str, str],
    item_type: str,
    item_label: str,
    item: dict[str, Any],
    node: dict[str, Any],
    chunk: dict[str, Any],
    chunk_id: int,
) -> dict[str, Any]:
    provenance_view = node.get("__provenance__") or {}
    headings = [str(h) for h in (chunk.get("headings") or []) if h]
    payload = {
        "section_type": item_type,
        "heading_path": headings,
        "heading": headings[-1] if headings else "",
        "chunk_id": chunk_id,
        "pages": chunk.get("page_numbers") or [],
        "doc_item_refs": chunk.get("doc_item_refs") or [],
        "item_geometry": chunk.get("item_geometry") or [],
        "text": chunk.get("text") or "",
        "original_chars": chunk.get("char_length") or len(chunk.get("text") or ""),
        "token_count": chunk.get("token_count") or 0,
        "text_hash": chunk.get("text_hash") or "",
        "resplit_of": chunk.get("resplit_of"),
        "grounded_item_label": item_label,
        "evidence_quote": item.get("evidence_quote"),
        "evidence_section_heading": item.get("section_heading"),
        "docling_graph_node_id": node.get("node_id"),
        "docling_graph_provenance": provenance_view,
        "anchor_spans": chunk_anchor_spans(provenance_view, chunk_id),
        "match_type": provenance_view.get("match") or provenance_view.get("scope") or "",
        "grounding_source": "docling_graph_provenance",
    }
    payload["derived_full_section"] = derive_full_section(
        row=row,
        heading_path=headings,
        chunk_text=payload["text"],
        evidence_quote=item.get("evidence_quote"),
    )
    return payload


def dedupe_grounded_chunks(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int, str], dict[str, Any]] = {}
    for item in items:
        key = (
            str(item["section_type"]),
            int(item["chunk_id"]),
            str(item.get("text_hash") or ""),
        )
        if key not in grouped:
            grouped[key] = {**item, "grounded_items": []}
        grouped[key]["grounded_items"].append(
            {
                "label": item.get("grounded_item_label"),
                "evidence_quote": item.get("evidence_quote"),
                "match_type": item.get("match_type"),
                "anchor_spans": item.get("anchor_spans"),
                "docling_graph_node_id": item.get("docling_graph_node_id"),
            }
        )
        grouped[key]["grounded_item_count"] = len(grouped[key]["grounded_items"])

    def sort_key(item: dict[str, Any]) -> tuple[int, int, int, int, int, int]:
        section = item.get("derived_full_section") or {}
        heading = section.get("heading") or item.get("heading") or ""
        frontmatter = heading_key(heading) in {
            "tableofcontents",
            "listoffigures",
            "listoftables",
            "references",
            "bibliography",
            "acknowledgements",
            "acknowledgments",
        }
        return (
            0 if frontmatter else 1,
            1 if section.get("status") == "ok" else 0,
            1 if section.get("contains_evidence_quote") is True else 0,
            1 if section.get("contains_chunk_excerpt") is True else 0,
            int(item["grounded_item_count"]),
            len(item.get("heading_path") or []),
        )

    return sorted(grouped.values(), key=sort_key, reverse=True)


def build_section_grounding(
    row: dict[str, str],
    models: list[dict[str, Any]],
    context: Any,
    provenance: dict[str, Any] | None,
) -> dict[str, Any]:
    chunks = compact_provenance_chunks(provenance)
    graph_data_sources, graph_input_representations = graph_nodes_by_grounding_item(context)
    data_source_chunks: list[dict[str, Any]] = []
    input_representation_chunks: list[dict[str, Any]] = []

    for model in models:
        if not isinstance(model, dict):
            continue
        for item in model.get("data_sources") or []:
            if isinstance(item, dict):
                data_source_chunks.extend(
                    grounded_chunks_for_item(row, item, "data_source", "source_label", graph_data_sources, chunks)
                )
        for item in model.get("input_representations") or []:
            if isinstance(item, dict):
                input_representation_chunks.extend(
                    grounded_chunks_for_item(
                        row, item, "input_representation", "representation_label", graph_input_representations, chunks
                    )
                )

    data_sections = dedupe_grounded_chunks(data_source_chunks)
    input_sections = dedupe_grounded_chunks(input_representation_chunks)
    primary_data = data_sections[0] if data_sections else None
    primary_input = input_sections[0] if input_sections else None
    sections_for_screening = [item for item in [primary_data, primary_input] if item]
    return {
        "status": "ok" if sections_for_screening else "no_grounded_sections",
        "source_markdown": rel(row.get("markdown")),
        "provenance_path": rel(find_provenance(context) or ""),
        "selection_method": (
            "Docling Graph native provenance: graph node __provenance__.chunks resolved "
            "through docling_graph/provenance.json chunks, preserving chunk text, heading trail, "
            "pages, doc_item_refs, geometry, and spans. No independent markdown regex/LLM selector."
        ),
        "primary_data_source_chunk": primary_data,
        "primary_input_representation_chunk": primary_input,
        "primary_data_source_section": (primary_data or {}).get("derived_full_section") if primary_data else None,
        "primary_input_representation_section": (primary_input or {}).get("derived_full_section") if primary_input else None,
        "data_source_chunks": data_sections,
        "input_representation_chunks": input_sections,
        "data_source_sections": [
            item.get("derived_full_section") for item in data_sections if item.get("derived_full_section")
        ],
        "input_representation_sections": [
            item.get("derived_full_section") for item in input_sections if item.get("derived_full_section")
        ],
        "sections_for_screening": sections_for_screening,
    }


def grounded_chunks_for_item(
    row: dict[str, str],
    item: dict[str, Any],
    item_type: str,
    label_field: str,
    graph_nodes: dict[str, dict[str, Any]],
    chunks: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    label = str(item.get(label_field) or "")
    node = graph_nodes.get(label)
    provenance_view = (node or {}).get("__provenance__") or {}
    grounded = []
    for chunk_id in provenance_view.get("chunks") or []:
        chunk = chunks.get(str(chunk_id))
        if isinstance(chunk, dict) and node:
            grounded.append(
                provenance_chunk_payload(
                    row=row,
                    item_type=item_type,
                    item_label=label,
                    item=item,
                    node=node,
                    chunk=chunk,
                    chunk_id=int(chunk_id),
                )
            )
    return grounded
