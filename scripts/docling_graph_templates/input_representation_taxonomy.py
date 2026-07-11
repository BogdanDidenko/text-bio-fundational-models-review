"""Docling Graph contracts for input-representation taxonomy extraction."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def edge(label: str, **kwargs: Any) -> Any:
    """Create a Pydantic field carrying Docling Graph edge metadata."""
    if "default" not in kwargs and "default_factory" not in kwargs:
        kwargs["default"] = ...
    return Field(json_schema_extra={"edge_label": label}, **kwargs)


class InputRouteDiscovery(BaseModel):
    """One evidence-grounded route without imposing a taxonomy label."""

    model_config = ConfigDict(graph_id_fields=["route_label"], extra="ignore")

    route_label: str = Field(
        ...,
        description=(
            "Concise document-grounded label for exactly one source-to-model path. "
            "Do not create an additional combined or fused route merely because a "
            "configuration uses several already-recorded routes together."
        ),
    )
    model_name: str = Field(
        ...,
        description="Named generative model receiving the input. Copy the paper's name.",
    )
    lifecycle_phase_verbatim: str = Field(
        ...,
        description=(
            "One lifecycle phase stated by the paper, such as pretraining, instruction "
            "tuning, inference, or evaluation. Create separate route records when the "
            "same source-to-model path must be represented in different phases. Do not "
            "normalize the paper's phase wording yet."
        ),
    )
    task_or_configuration_verbatim: str = Field(
        ...,
        description=(
            "Task or permitted input configuration in which this route is used. "
            "Record the paper's wording."
        ),
    )
    source_object_verbatim: str = Field(
        ...,
        description=(
            "One biological or textual source object before model preprocessing, "
            "copied or closely paraphrased from the paper. Do not combine independent "
            "modalities into one source object; each receives its own route."
        ),
    )
    transformation_chain_verbatim: list[str] = Field(
        default_factory=list,
        description=(
            "Ordered operations that transform the source object before it reaches "
            "the generative model. Preserve the paper's terminology and do not "
            "collapse multiple operations into a taxonomy category."
        ),
    )
    model_visible_form_verbatim: str = Field(
        ...,
        description=(
            "What the generative model actually receives: symbols, token IDs, "
            "vectors, projected embeddings, feature sequences, or another form."
        ),
    )
    insertion_or_fusion_verbatim: str = Field(
        ...,
        description=(
            "How the represented input is connected to the generative component, "
            "using the paper's architectural terminology."
        ),
    )
    text_role_verbatim: str = Field(
        ...,
        description=(
            "Role of text in this phase/configuration. Distinguish an actual input "
            "from supervision, a target, or generated output."
        ),
    )
    input_status_verbatim: str = Field(
        ...,
        description=(
            "Whether this is an actual model input, paired training supervision, "
            "training-only target, generated output, baseline, ablation, or unclear."
        ),
    )
    evidence_quote: str = Field(
        ...,
        description=(
            "One short contiguous verbatim quote that directly supports the route. "
            "Never join separate passages, invent, or summarize this field."
        ),
    )
    section_heading: str | None = Field(
        None,
        description="Heading containing the evidence quote, if visible.",
    )
    supporting_figure_or_table: str | None = Field(
        None,
        description=(
            "Figure/table identifier only when it supports this route. A generated "
            "picture description alone is not conclusive evidence."
        ),
    )
    uncertainty: str | None = Field(
        None,
        description="Concise unresolved ambiguity; null when the route is explicit.",
    )


class InputRouteDiscoveryDocument(BaseModel):
    """Open extraction of all candidate input routes in one paper."""

    model_config = ConfigDict(graph_id_fields=["title"], extra="ignore")

    title: str = Field(..., description="Paper title copied from the document.")
    doi: str | None = Field(None, description="DOI if present.")
    input_routes: list[InputRouteDiscovery] = edge(
        "HAS_INPUT_ROUTE",
        default_factory=list,
        description=(
            "All distinct input routes used by the paper's generative model(s). "
            "Create separate routes when model, lifecycle phase, task/configuration, "
            "source object, model-visible form, or fusion mechanism differs. Include "
            "training-only/output/baseline candidates only when needed to explicitly "
            "distinguish them from usable model inputs. A route begins at exactly one "
            "source object. In a multimodal configuration, attach the shared configuration "
            "name to every participating route; never emit another combined/fused route "
            "that duplicates those participants. A fused latent representation is an "
            "intermediate state of its incoming routes, not a new source route."
        ),
    )


CarrierFamily = Literal[
    "text_native_token_stream",
    "discrete_biological_symbol_stream",
    "dense_continuous_carrier",
    "visual_raster_carrier",
    "geometric_or_diffusion_state_carrier",
    "other_evidence_grounded",
]

CarrierSubtype = Literal[
    "plain_language_prompt_or_question",
    "structured_biological_prompt_or_task_scaffold",
    "serialized_biological_context_or_ordered_profile",
    "native_biological_token_stream",
    "multi_track_structural_symbol_stream",
    "learned_quantized_id_or_codebook_token",
    "direct_projected_embedding",
    "virtual_token_prefix",
    "connector_mediated_embedding",
    "pooled_or_aggregated_embedding",
    "raw_slide_or_patch_input",
    "patch_context_or_case_level_visual_reasoning",
    "noisy_diffusion_state",
    "coordinate_backbone_or_shape_conditioning",
    "symbolic_structural_constraint",
    "other_evidence_grounded",
]

LifecyclePhase = Literal["pretraining", "fine_tuning", "inference", "evaluation", "unclear"]

InputStatus = Literal[
    "actual_model_input",
    "paired_alignment_input",
    "training_only_target",
    "generated_output",
    "baseline_only",
    "ablation_only",
    "unclear",
]

TextRole = Literal[
    "biological_payload",
    "semantic_annotation",
    "instruction_or_query",
    "modality_or_task_selector",
    "metadata_or_context",
    "paired_alignment_supervision",
    "training_target",
    "generated_output",
    "no_text_on_this_route",
    "unclear",
]

FusionTopology = Literal[
    "tokenizer_sequence",
    "concatenation",
    "prefix",
    "placeholder_replacement",
    "interleaving",
    "cross_attention",
    "query_bottleneck",
    "shared_latent_alignment",
    "encoder_decoder",
    "side_or_generative_conditioning",
    "retrieval_or_tool_context",
    "other_explicit",
    "unclear",
]

EvidenceStatus = Literal["explicit_text", "text_plus_figure", "figure_only", "inferred"]


class TaxonomyCodedRoute(BaseModel):
    """One route coded against taxonomy v1 while retaining lossless evidence."""

    model_config = ConfigDict(graph_id_fields=["route_label"], extra="ignore")

    route_label: str
    model_name: str
    lifecycle_phase: LifecyclePhase
    task_or_configuration_verbatim: str
    source_object_verbatim: str
    source_object_normalized: str
    source_modality_normalized: str
    transformation_chain_verbatim: list[str] = Field(default_factory=list)
    transformation_chain_normalized: list[str] = Field(default_factory=list)
    model_visible_form_verbatim: str
    carrier_family: CarrierFamily = Field(
        ...,
        description=(
            "Frozen v1 model-visible carrier. text_native_token_stream covers ordinary "
            "language tokens, structured prompts, and deterministic biological text "
            "serializations; discrete_biological_symbol_stream covers native biological "
            "tokens, aligned structural tracks, and learned VQ/RVQ/codebook IDs; "
            "dense_continuous_carrier covers projected, virtual-token, connector-mediated, "
            "or pooled embeddings; visual_raster_carrier covers pixels, slides, patches, "
            "and visual case contexts; geometric_or_diffusion_state_carrier covers noisy "
            "states, coordinates/backbones/shapes, and structural constraints. Classify "
            "the first model-facing carrier before routine embedding lookup or encoder "
            "processing. Do not relabel tokenizer tokens, biological symbols, or pixels "
            "as dense merely because the model subsequently embeds or encodes them."
        ),
    )
    carrier_subtype: CarrierSubtype = Field(
        ...,
        description=(
            "Subtype must belong to carrier_family exactly as defined in the frozen "
            "taxonomy_codebook.md. Learned quantized IDs must not be coded as native "
            "biological tokens or continuous embeddings. Deterministically serialized "
            "cell/gene/profile text belongs to the text-native serialization subtype."
        ),
    )
    insertion_or_fusion_verbatim: str
    fusion_topology: FusionTopology
    text_role: TextRole
    input_status: InputStatus
    evidence_quote: str = Field(
        ...,
        description=(
            "One short contiguous verbatim quote supporting this route. Never concatenate "
            "separate sentences or summarize."
        ),
    )
    section_heading: str | None = None
    supporting_figure_or_table: str | None = None
    evidence_status: EvidenceStatus
    uncertainty: str | None = None


class TaxonomyCodedDocument(BaseModel):
    """Taxonomy-v1 coding for all candidate input routes in one paper."""

    model_config = ConfigDict(graph_id_fields=["title"], extra="ignore")

    taxonomy_version: Literal["input-representation-taxonomy-v1"] = (
        "input-representation-taxonomy-v1"
    )
    title: str
    doi: str | None = None
    input_routes: list[TaxonomyCodedRoute] = edge(
        "HAS_CODED_INPUT_ROUTE",
        default_factory=list,
        description=(
            "All distinct routes, including explicitly identified non-input candidates. "
            "Every route starts at one source object and one lifecycle phase. Never use "
            "a single hybrid or fused-summary route when several source-to-model pathways "
            "exist; record the shared configuration on each participating route."
        ),
    )


CandidateDecision = Literal[
    "exclude_training_only_target",
    "exclude_generated_output",
    "exclude_baseline_only",
    "exclude_ablation_only",
    "exclude_not_a_source_to_model_route",
    "exclude_duplicate_candidate",
    "uncertain",
]


class FixedTaxonomyInputRoute(TaxonomyCodedRoute):
    """Final input route derived from one or more fixed discovery candidates."""

    model_config = ConfigDict(graph_id_fields=["route_label"], extra="forbid")

    source_candidate_refs: list[str] = Field(
        ...,
        description=(
            "Discovery route_ref values supporting this route. A combined discovery "
            "candidate may support several split source-to-model routes; duplicated "
            "discovery candidates may be merged into one final route."
        ),
    )


class ExcludedRouteCandidate(BaseModel):
    """A fixed discovery candidate explicitly excluded from accepted input routes."""

    model_config = ConfigDict(extra="forbid")

    candidate_ref: str
    decision: CandidateDecision
    reason: str
    evidence_quote: str
    uncertainty: str | None = None


class FixedCandidateClassificationDocument(BaseModel):
    """Complete classification of one fixed per-paper discovery inventory."""

    model_config = ConfigDict(extra="forbid")

    taxonomy_version: Literal["input-representation-taxonomy-v1.1-fixed-candidates"] = (
        "input-representation-taxonomy-v1.1-fixed-candidates"
    )
    title: str
    doi: str | None = None
    input_routes: list[FixedTaxonomyInputRoute] = Field(default_factory=list)
    excluded_candidates: list[ExcludedRouteCandidate] = Field(default_factory=list)


DenseCandidateDecision = Literal[
    "supports_accepted_route",
    "accepted_as_dense_only_route",
    "exclude_duplicate",
    "exclude_training_only_target",
    "exclude_generated_output",
    "exclude_baseline_or_ablation",
    "exclude_not_a_source_to_model_route",
    "exclude_figure_only",
    "exclude_ungrounded_or_taxonomy_invalid",
    "unresolved",
]


class DenseCandidateDisposition(BaseModel):
    """Explicit coverage-audit disposition for one dense Graph candidate."""

    model_config = ConfigDict(extra="forbid")

    candidate_ref: str
    decision: DenseCandidateDecision
    linked_route_labels: list[str] = Field(default_factory=list)
    reason: str
    uncertainty: str | None = None


class FinalAdjudicatedInputRoute(FixedTaxonomyInputRoute):
    """Final route grounded in discovery and/or dense Graph evidence."""

    model_config = ConfigDict(graph_id_fields=["route_label"], extra="forbid")

    dense_candidate_refs: list[str] = Field(
        default_factory=list,
        description=(
            "Dense coverage candidate refs supporting this route. At least one source "
            "candidate ref or dense candidate ref must support every final route."
        ),
    )


class FinalAdjudicatedTaxonomyDocument(BaseModel):
    """Blinded final reconciliation with complete candidate accounting."""

    model_config = ConfigDict(extra="forbid")

    taxonomy_version: Literal["input-representation-taxonomy-v1.2-adjudicated"] = (
        "input-representation-taxonomy-v1.2-adjudicated"
    )
    title: str
    doi: str | None = None
    input_routes: list[FinalAdjudicatedInputRoute] = Field(default_factory=list)
    excluded_candidates: list[ExcludedRouteCandidate] = Field(default_factory=list)
    dense_candidate_dispositions: list[DenseCandidateDisposition] = Field(default_factory=list)
