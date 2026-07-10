"""Docling Graph template for biomedical screening evidence extraction.

This template extracts only two grounded evidence types needed before screening:
source data and input representation. It does not make INCLUDE/EXCLUDE
decisions.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def edge(label: str, **kwargs: Any) -> Any:
    """Create a Pydantic Field with Docling Graph edge metadata."""
    if "default" not in kwargs and "default_factory" not in kwargs:
        kwargs["default"] = ...
    return Field(json_schema_extra={"edge_label": label}, **kwargs)


class DataSourceEvidence(BaseModel):
    """Primary source-data evidence for the paper's main model, not every dataset."""

    model_config = ConfigDict(graph_id_fields=["source_label"], extra="ignore")

    source_label: str = Field(
        ...,
        description=(
            "Short verbatim label for the dataset, corpus, cohort, benchmark, "
            "database, or source-data phrase used by the paper's main model. "
            "Prefer training/pretraining/fine-tuning data over downstream benchmarks. "
            "Copy from the paper; do not invent."
        ),
        examples=["PRISM-12M", "MERFISH mouse brain dataset", "ENCODE cCREs"],
    )
    data_kind: str | None = Field(
        None,
        description=(
            "Brief type of data, e.g. spatial transcriptomics, DNA sequences, "
            "protein sequences, histology images, or scRNA-seq."
        ),
    )
    use_role: str | None = Field(
        None,
        description=(
            "How the paper uses this data: pretraining, training, fine-tuning, "
            "evaluation, benchmark, case study, or unclear. Prefer the role for "
            "the main model rather than baseline or downstream-only datasets."
        ),
    )
    evidence_quote: str | None = Field(
        None,
        description="Short verbatim quote supporting this source-data evidence.",
    )
    section_heading: str | None = Field(
        None,
        description="Section heading where this evidence appears, if visible.",
    )


class InputRepresentationEvidence(BaseModel):
    """Primary input-representation evidence for the paper's main model."""

    model_config = ConfigDict(graph_id_fields=["representation_label"], extra="ignore")

    representation_label: str = Field(
        ...,
        description=(
            "Short verbatim label for the model input representation, prompt "
            "format, tokenization, or input unit used by the paper's main model. "
            "Do not extract baseline-only or downstream supervised-model inputs "
            "unless they are the main model's representation. Copy from the paper; "
            "do not invent."
        ),
        examples=["cell sentence", "spatial sentence", "text prompts", "DNA token sequence"],
    )
    input_kind: str | None = Field(
        None,
        description=(
            "What is fed to the model, e.g. cells, genes, DNA segments, proteins, "
            "images, tissue patches, or prompts."
        ),
    )
    representation_method: str | None = Field(
        None,
        description=(
            "Brief description of serialization, tokenization, ranking, embedding, "
            "prompting, or other representation method."
        ),
    )
    evidence_quote: str | None = Field(
        None,
        description="Short verbatim quote supporting this input-representation evidence.",
    )
    section_heading: str | None = Field(
        None,
        description="Section heading where this evidence appears, if visible.",
    )


class BiomedicalScreeningEvidence(BaseModel):
    """Root document entity for extracting screening evidence only."""

    model_config = ConfigDict(graph_id_fields=["title"], extra="ignore")

    title: str = Field(
        ...,
        description="Paper title copied from the document.",
        examples=["TissueNarrator: Generative Modeling of Spatial Transcriptomics"],
    )
    doi: str | None = Field(None, description="DOI if present.")

    data_sources: list[DataSourceEvidence] = edge(
        "HAS_DATA_SOURCE",
        default_factory=list,
        description=(
            "One or two primary source-data evidence items used by the paper's "
            "main model. Do not enumerate every downstream benchmark or case study."
        ),
    )
    input_representations: list[InputRepresentationEvidence] = edge(
        "HAS_INPUT_REPRESENTATION",
        default_factory=list,
        description=(
            "One or two primary evidence items describing the main model input "
            "representation. Do not enumerate baseline-only input formats."
        ),
    )
