"""Source-backed symbolic trajectories for a supervised development pilot."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(StrictModel):
    section_id: str
    quote: str
    kind: Literal["paper_text", "table", "caption", "equation_context", "vlm_description"]


class Representation(StrictModel):
    node_id: str
    representation_type: str
    symbolic_shape: list[str] | None
    axis_semantics: list[str] | None
    information_content: str
    contextual_role: str
    evidence: list[Evidence]
    uncertainty: str | None


class Operand(StrictModel):
    node_id: str
    port_role: str


class Transformation(StrictModel):
    step_id: str
    component: str
    operation_type: str
    inputs: list[Operand]
    outputs: list[str]
    evidence: list[Evidence]
    uncertainty: str | None


class Trajectory(StrictModel):
    trajectory_id: str
    model_variant: str
    task_configuration: str
    lifecycle_phase: Literal["pretraining", "training", "fine_tuning", "test_time_adaptation", "inference", "evaluation", "unspecified"]
    recipient_component: str
    model_role: Literal["primary_model", "auxiliary_component", "baseline", "ablation", "unresolved"]
    nodes: list[Representation]
    steps: list[Transformation]
    receipt_inputs: list[Operand]
    evidence: list[Evidence]
    open_questions: list[str]


class SymbolicTrajectoryDocument(StrictModel):
    contract_version: Literal["symbolic-trajectories-pilot-v1"]
    record_id: str
    input_packet_sha256: str
    trajectories: list[Trajectory]
    coverage_questions: list[str]
