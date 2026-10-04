"""Operation-level building blocks for evidence-backed data transformation graphs."""

from typing import Any, Literal

from pydantic import model_validator

from scripts.docling_graph_templates.symbolic_trajectories import (
    Evidence, Operand, Representation, StrictModel, Trajectory, Transformation,
)


class Port(StrictModel):
    name: str
    meaning: str
    variadic: bool = False
    optional: bool = False


class OperationBlock(StrictModel):
    operation_id: str
    label: str
    definition: str
    inputs: list[Port]
    outputs: list[Port]
    parameters: list[str]
    boundaries: str
    official_reference: str | None


class OperationCatalog(StrictModel):
    contract_version: Literal["operation-library-v1"]
    release: str
    blocks: list[OperationBlock]

    @model_validator(mode="after")
    def unique_ids_and_ports(self):
        if len({block.operation_id for block in self.blocks}) != len(self.blocks):
            raise ValueError("Duplicate operation ID")
        for block in self.blocks:
            for ports in (block.inputs, block.outputs):
                if len({port.name for port in ports}) != len(ports):
                    raise ValueError("Duplicate operation port")
            if not block.definition or not block.boundaries:
                raise ValueError("Operation needs a definition and boundaries")
        return self


class DataNode(Representation):
    origin: Literal["source_annotation", "documented_intermediate", "implicit_parameter"]


class OperationCall(StrictModel):
    call_id: str
    operation_id: str | None
    component: str
    inputs: dict[str, list[str]]
    outputs: dict[str, list[str]]
    parameters: dict[str, Any]
    condition: str | None
    source_step_id: str
    evidence: list[Evidence]
    uncertainty: str | None
    status: Literal["documented_operation", "unexpanded_source_boundary"]


class Bypass(StrictModel):
    source_node_id: str
    target_node_id: str
    condition: str
    source_step_id: str


class OperationAssembly(StrictModel):
    contract_version: Literal["operation-assembly-v1"]
    record_id: str
    trajectory_id: str
    library_release: str
    library_sha256: str
    model_variant: str
    task_configuration: str
    lifecycle_phase: Literal["pretraining", "training", "fine_tuning", "test_time_adaptation", "inference", "evaluation", "unspecified"]
    model_role: Literal["primary_model", "auxiliary_component", "baseline", "ablation", "unresolved"]
    recipient_component: str
    nodes: list[DataNode]
    calls: list[OperationCall]
    bypasses: list[Bypass]
    source_steps: list[Transformation]
    receipt_inputs: list[Operand]
    evidence: list[Evidence]
    open_questions: list[str]

    @model_validator(mode="after")
    def validate_graph(self):
        nodes = {node.node_id: node for node in self.nodes}
        if len(nodes) != len(self.nodes) or len({call.call_id for call in self.calls}) != len(self.calls):
            raise ValueError("Duplicate graph ID")
        steps = {step.step_id for step in self.source_steps}
        for node in self.nodes:
            if node.symbolic_shape is not None:
                if any(any(c.isdigit() for c in axis) for axis in node.symbolic_shape):
                    raise ValueError("Concrete architecture width in symbolic shape")
                if node.axis_semantics is not None and len(node.axis_semantics) != len(node.symbolic_shape):
                    raise ValueError("Shape/axis rank mismatch")
        for call in self.calls:
            if call.source_step_id not in steps or not call.evidence:
                raise ValueError("Call needs its original step and evidence")
            refs = [ref for port in list(call.inputs.values()) + list(call.outputs.values()) for ref in port]
            if any(ref not in nodes for ref in refs):
                raise ValueError("Unknown operation operand")
            if (call.operation_id is None) != (call.status == "unexpanded_source_boundary"):
                raise ValueError("Unexpanded source boundary must retain its unresolved operation")
        for edge in self.bypasses:
            if edge.source_node_id not in nodes or edge.target_node_id not in nodes or edge.source_step_id not in steps:
                raise ValueError("Invalid conditional bypass")
        if any(operand.node_id not in nodes for operand in self.receipt_inputs):
            raise ValueError("Unknown receiving operand")
        return self


def restore_source(assembly: dict) -> dict:
    """Recover the complete original trajectory independently of decomposition."""
    data = {key: assembly[key] for key in (
        "trajectory_id", "model_variant", "task_configuration", "lifecycle_phase",
        "model_role", "recipient_component", "receipt_inputs", "evidence", "open_questions",
    )}
    data["nodes"] = [{key: value for key, value in node.items() if key != "origin"}
                     for node in assembly["nodes"] if node["origin"] == "source_annotation"]
    data["steps"] = assembly["source_steps"]
    Trajectory.model_validate(data)
    return data


def validate_operation_ports(assembly: dict, catalog: dict):
    definitions = {block["operation_id"]: block for block in catalog["blocks"]}
    for call in assembly["calls"]:
        if call["operation_id"] is None:
            continue
        if call["operation_id"] not in definitions:
            raise ValueError("Unknown library operation")
        block = definitions[call["operation_id"]]
        for direction in ("inputs", "outputs"):
            signature = {port["name"]: port for port in block[direction]}
            supplied = call[direction]
            if set(supplied) - set(signature):
                raise ValueError(f"Unknown {direction} port in {call['call_id']}")
            for name, port in signature.items():
                values = supplied.get(name, [])
                if not port["optional"] and not values:
                    raise ValueError(f"Missing required port: {call['call_id']}/{name}")
                if not port["variadic"] and len(values) > 1:
                    raise ValueError("Multiple operands on a scalar port")
