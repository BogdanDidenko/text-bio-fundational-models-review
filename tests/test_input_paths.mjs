import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {inputPath,availableSources,groupPathCalls,pathDiagram} from "../docs/input-representation-atlas/component-library/input-paths.mjs";

const assemblies=JSON.parse(fs.readFileSync(new URL("../docs/input-representation-atlas/component-library/data/assemblies.json",import.meta.url),"utf8"));
const xcell=assemblies.find((item)=>item.trajectory_id==="xcell_pisces_pretraining_cross_attention");

test("X-Cell defaults to measured expression and excludes independent prior preparation",()=>{
  const source=availableSources(xcell,"query_state");
  assert.equal(source.defaultSource,"control_pool");
  const path=inputPath(xcell,source.defaultSource,"query_state");
  assert.equal(path.connected,true);
  assert.ok(path.calls.some((call)=>call.source_step_id==="control_normalization"));
  assert.ok(!path.calls.some((call)=>call.source_step_id==="esm_lookup"));
  assert.ok(path.sideInputs.includes("context"));
  assert.ok(path.sideInputs.includes("gene_table_raw"));
});

test("An external prior has its own complete input path",()=>{
  const path=inputPath(xcell,"esm_reference","context");
  assert.equal(path.connected,true);
  assert.deepEqual(path.calls.map((call)=>call.source_step_id),["esm_lookup","esm_availability","esm_availability","esm_project","esm_project","assemble_context"]);
  assert.ok(path.sideInputs.includes("genept_projected"));
  assert.ok(!path.calls.some((call)=>call.source_step_id==="control_normalization"));
});

test("All source operations remain in the underlying immutable assembly",()=>{
  const before=JSON.stringify(xcell);
  inputPath(xcell,"control_pool","query_state");
  assert.equal(JSON.stringify(xcell),before);
  assert.equal(xcell.calls.length,46);
});

test("Displayed stages retain primitive order and parallel dependencies",()=>{
  const groups=groupPathCalls(inputPath(xcell,"control_pool","query_state"));
  const normalization=groups.find((group)=>group.sourceStepId==="control_normalization");
  assert.deepEqual(normalization.calls.map((call)=>call.operation_id),["normalize","log_transform"]);
  assert.ok(groups.some((group)=>groups.some((other)=>other!==group && other.level===group.level)));
});

test("Conditional bypass is preserved",()=>{
  const path=inputPath(xcell,"control_pool","query_state");
  assert.ok(path.bypasses.some((edge)=>edge.source_node_id==="control_pool" && edge.target_node_id==="control_normalized"));
});

test("Source unrelated to receiving port does not produce an invented path",()=>{
  assert.equal(inputPath(xcell,"esm_reference","control_normalized").connected,false);
});

test("Every existing receiving operand has a recoverable source boundary",()=>{
  for(const assembly of assemblies){
    for(const receipt of assembly.receipt_inputs){
      const sources=availableSources(assembly,receipt.node_id);
      assert.ok(sources.defaultSource);
      assert.equal(inputPath(assembly,sources.defaultSource,receipt.node_id).connected,true);
    }
  }
});

test("Diagram connects source, actual operations, forks, joins and receiver",()=>{
  const diagram=pathDiagram(inputPath(xcell,"control_pool","query_state"));
  assert.ok(diagram.edges.some((edge)=>edge.from==="source"&&edge.to==="step:control_normalization"));
  assert.ok(diagram.edges.some((edge)=>edge.from==="step:preceding_layers"&&edge.to==="receiver"));
  assert.ok(diagram.edges.some((edge)=>edge.from==="step:value_encoder"&&edge.to==="step:combine_tokens"));
  assert.ok(diagram.edges.some((edge)=>edge.from==="step:mask_encoder"&&edge.to==="step:combine_tokens"));
  assert.ok(diagram.edges.some((edge)=>edge.from==="step:identity_encoder"&&edge.to==="step:combine_tokens"));
  assert.ok(diagram.edges.some((edge)=>edge.condition));
  assert.ok(!diagram.nodes.some((node)=>node.id==="step:esm_lookup"));
});

test("Every diagram edge has real data identity and existing vertices",()=>{
  for(const assembly of assemblies){
    for(const receipt of assembly.receipt_inputs){
      const sources=availableSources(assembly,receipt.node_id);
      const diagram=pathDiagram(inputPath(assembly,sources.defaultSource,receipt.node_id));
      const ids=new Set(diagram.nodes.map((node)=>node.id));
      for(const edge of diagram.edges){
        assert.ok(ids.has(edge.from));assert.ok(ids.has(edge.to));assert.ok(edge.dataIds.length);
      }
    }
  }
});
