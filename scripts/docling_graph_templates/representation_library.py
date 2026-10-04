"""Versioned description primitives and source-preserving architecture assemblies."""

from typing import Literal

from pydantic import Field, model_validator

from scripts.docling_graph_templates.symbolic_trajectories import (
    Evidence, Operand, Representation, StrictModel, Transformation,
)


class ExampleRef(StrictModel):
    record_id: str
    trajectory_id: str
    element_kind: Literal["node", "step", "recipient", "subgraph"]
    element_ids: list[str]
    rationale: str


class BlockDefinition(StrictModel):
    block_id: str
    kind: Literal["representation", "operation", "component", "composite"]
    label: str
    definition: str
    boundaries: str
    input_roles: list[str]
    output_roles: list[str]
    aliases: list[str]
    status: Literal["reviewed_candidate", "proposed", "deprecated"]
    examples: list[ExampleRef]
    composition: list[str]
    version: str = "0.1.0"


class Mapping(StrictModel):
    kind: Literal["representation", "operation", "component"]
    source_label: str
    block_id: str
    relation: Literal["reuse", "specialization"]
    rationale: str


class StewardDecision(StrictModel):
    decision_id: str
    action: Literal["reuse", "alias", "compatible_enrichment", "new_block", "unresolved"]
    subject: str
    rationale: str
    affected_block_ids: list[str]


class CatalogSeed(StrictModel):
    release: str
    blocks: list[BlockDefinition]
    mappings: list[Mapping]
    decisions: list[StewardDecision]

    @model_validator(mode="after")
    def check_references(self):
        blocks = {block.block_id: block for block in self.blocks}
        if len(blocks) != len(self.blocks):
            raise ValueError("Duplicate block ID")
        seen = set()
        for mapping in self.mappings:
            key = (mapping.kind, mapping.source_label)
            if key in seen:
                raise ValueError(f"Duplicate source mapping: {key}")
            seen.add(key)
            if mapping.block_id not in blocks or blocks[mapping.block_id].kind != mapping.kind:
                raise ValueError(f"Unknown or wrong-kind mapping: {mapping.block_id}")
        for block in self.blocks:
            if not block.definition or not block.boundaries:
                raise ValueError(f"Missing definition/boundaries: {block.block_id}")
            if block.status == "reviewed_candidate" and not block.examples:
                raise ValueError(f"Reviewed block has no source example: {block.block_id}")
            if any(ref not in blocks for ref in block.composition):
                raise ValueError(f"Unknown composition member: {block.block_id}")
        for decision in self.decisions:
            if any(ref not in blocks for ref in decision.affected_block_ids):
                raise ValueError(f"Unknown decision block: {decision.decision_id}")
        return self


class Binding(StrictModel):
    block_id: str | None
    block_version: str | None
    relation: Literal["reuse", "specialization", "unresolved"]
    rationale: str
    proposal_id: str | None

    @model_validator(mode="after")
    def check_binding(self):
        if self.relation == "unresolved":
            if self.block_id is not None or self.block_version is not None or not self.proposal_id:
                raise ValueError("Unresolved binding needs a proposal and no asserted library type")
        elif not self.block_id or not self.block_version or self.proposal_id is not None:
            raise ValueError("Resolved binding needs a pinned block and no extension proposal")
        if not self.rationale:
            raise ValueError("Binding decision needs an explicit rationale")
        return self


class AssemblyNode(Representation):
    binding: Binding
    original_node_id: str


class AssemblyOperation(Transformation):
    binding: Binding
    component_binding: Binding
    original_step_id: str
    normalized_input_roles: dict[str, str] = Field(default_factory=dict)


class Receipt(StrictModel):
    recipient_id: str
    component: str
    binding: Binding
    inputs: list[Operand]


class UseContext(StrictModel):
    trajectory_id: str
    model_variant: str
    task_configuration: str
    lifecycle_phase: Literal["pretraining", "training", "fine_tuning", "test_time_adaptation", "inference", "evaluation", "unspecified"]
    model_role: Literal["primary_model", "auxiliary_component", "baseline", "ablation", "unresolved"]
    node_ids: list[str]
    step_ids: list[str]
    recipient_id: str
    evidence: list[Evidence]
    open_questions: list[str]


class IdentityLink(StrictModel):
    node_ids: list[str]
    relation: Literal["same_value", "shared_parameters", "repeated_computation"]
    evidence: list[Evidence]
    status: Literal["supported", "provisional"]
    uncertainty: str | None


class AssemblyDocument(StrictModel):
    contract_version: Literal["representation-assembly-v1"]
    record_id: str
    input_packet_sha256: str
    source_artifact: str
    source_artifact_sha256: str
    library_release: str
    library_sha256: str
    nodes: list[AssemblyNode]
    operations: list[AssemblyOperation]
    recipients: list[Receipt]
    contexts: list[UseContext]
    identity_links: list[IdentityLink]
    coverage_questions: list[str]

    @model_validator(mode="after")
    def check_graph(self):
        nodes = {node.node_id: node for node in self.nodes}
        steps = {step.step_id: step for step in self.operations}
        recipients = {item.recipient_id: item for item in self.recipients}
        for collection, items in ((nodes, self.nodes), (steps, self.operations), (recipients, self.recipients)):
            if len(collection) != len(items):
                raise ValueError("Duplicate graph ID")
        for node in self.nodes:
            shape, axes = node.symbolic_shape, node.axis_semantics
            if shape and any(any(char.isdigit() for char in axis) for axis in shape):
                raise ValueError("Concrete numeric architecture width in symbolic shape")
            if shape is not None and axes is not None and len(shape) != len(axes):
                raise ValueError("Symbolic shape/axis rank mismatch")
        for step in self.operations:
            refs = [operand.node_id for operand in step.inputs] + step.outputs
            if any(ref not in nodes for ref in refs):
                raise ValueError(f"Unknown operation operand: {step.step_id}")
        for recipient in self.recipients:
            if any(item.node_id not in nodes for item in recipient.inputs):
                raise ValueError("Invalid receiving operand")
        if len({context.trajectory_id for context in self.contexts}) != len(self.contexts):
            raise ValueError("Duplicate use context")
        for context in self.contexts:
            if any(ref not in nodes for ref in context.node_ids) or any(ref not in steps for ref in context.step_ids):
                raise ValueError("Unknown context graph reference")
            if context.recipient_id not in recipients:
                raise ValueError("Unknown context recipient")
            allowed = set(context.node_ids)
            selected_steps = [steps[ref] for ref in context.step_ids]
            used = {ref for step in selected_steps for ref in step.outputs}
            used.update(operand.node_id for step in selected_steps for operand in step.inputs)
            used.update(item.node_id for item in recipients[context.recipient_id].inputs)
            if not used <= allowed:
                raise ValueError("Operation or receipt leaks outside its use context")
        for link in self.identity_links:
            if any(ref not in nodes for ref in link.node_ids) or not link.evidence:
                raise ValueError("Identity link needs valid nodes and source evidence")
        return self
