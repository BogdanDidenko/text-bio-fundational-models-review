const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const state = {view:"blocks", selected:null, query:"", reuse:"", paper:"", context:null, source:null, receipt:null};
let catalog, assemblies, evidence, atlas, operations, pathTools, diagramTools, activeAssembly;
const paper = (id) => catalog.records[id]?.paper || (id === "full_2026-07-06__rec_001277" ? "OKR-Cell (WITHDRAWN source)" : id);
const icons = () => window.lucide?.createIcons();
const key = (item) => item.operation_id || item.record_id || item.source_operation;
const title = (item) => item.label || (item.record_id ? paper(item.record_id) : item.source_operation.replaceAll("_"," "));

function listItems() {
  let source = state.view === "blocks" || state.view === "reuse" ? catalog.blocks : state.view === "assemblies" ?
    Object.keys(catalog.records).map((id) => ({record_id:id, chains:assemblies.filter((item) => item.record_id === id)})) : catalog.pending;
  if (state.view === "reuse") source = source.filter((item) => item.reuse_record_ids.length > 1);
  return source.filter((item) => {
    const records = item.reuse_record_ids || (item.record_id ? [item.record_id] : item.occurrences.map((use) => use.record_id));
    const matchesReuse = !state.reuse || state.view === "assemblies" || state.view === "proposals" ||
      (state.reuse === "shared" && records.length > 1) || (state.reuse === "single" && records.length === 1) ||
      (state.reuse === "supplemental" && item.supplemental_examples?.length);
    return matchesReuse && (!state.paper || records.includes(state.paper)) && JSON.stringify(item).toLowerCase().includes(state.query.toLowerCase());
  });
}

function quotePanel(item) {
  return `<blockquote class="quote">${esc(item.quote)}</blockquote><div class="provenance">${esc(paper(item.record_id))} / ${esc(item.heading_path.join(" › "))}<br>${esc(item.section_id)} · ${esc(item.kind)} · exact section match<br>section sha256 ${esc(item.section_sha256)}</div>`;
}
function sourceEvidence(record, items) {
  const found = evidence.filter((entry) => entry.record_id === record && items.some((item) => item.quote === entry.quote && item.section_id === entry.section_id));
  return found.map(quotePanel).join("");
}
function sourceFigure(record) {
  const model = atlas.architectures.find((item) => item.record_id === record && item.figure?.asset);
  return model ? `<details class="source-panel"><summary>Original-paper figure · ${esc(model.model_name)}</summary><img class="source-image" src="../${esc(model.figure.asset)}" alt="${esc(model.figure.caption)}" loading="lazy"><p class="small">${esc(model.figure.caption)}</p><a href="${esc(model.paper_url)}" target="_blank" rel="noreferrer">Source paper</a></details>` : "";
}
function ports(heading, specs) {
  return `<div><h3>${heading}</h3><ul class="port-list">${specs.map((port) => `<li><b>${esc(port.name)}</b>${port.optional ? " · optional" : ""}${port.variadic ? " · multiple operands" : ""}<br><span class="small">${esc(port.meaning)}</span></li>`).join("")}</ul></div>`;
}
function callView(call, assembly) {
  const name = call.operation_id ? operations.get(call.operation_id).label : "Unexpanded: " + call.parameters.source_operation.replaceAll("_", " ");
  return `<article class="graph-operation ${call.operation_id ? "" : "unexpanded"}"><h4>${call.operation_id ? `<button class="inline-link" data-block="${esc(call.operation_id)}">${esc(name)}</button>` : esc(name)}</h4><div class="provenance">${esc(call.call_id)} / ${esc(call.component)}</div><div class="operand-list">${Object.entries(call.inputs).map(([port, nodes]) => `${esc(nodes.join(" + "))} → ${esc(port)}`).join("<br>")}<br>→ ${Object.entries(call.outputs).map(([port,nodes]) => `${esc(port)}: ${esc(nodes.join(" + "))}`).join("<br>")}</div><div class="small">${Object.entries(call.parameters).filter(([key]) => key !== "source_port_roles").map(([key,value]) => `${esc(key)}: ${esc(typeof value === "object" ? JSON.stringify(value) : value)}`).join(" · ")}</div>${call.condition ? `<p class="state">When: ${esc(call.condition)}</p>` : ""}${call.uncertainty ? `<details><summary>Uncertainty</summary><p class="small">${esc(call.uncertainty)}</p></details>` : ""}<details><summary>Source evidence</summary>${sourceEvidence(assembly.record_id,call.evidence)}</details></article>`;
}

const boundaryNames={
  stratified_target_set_and_matched_control_sampling:"Paired cell-set sampling",
  combine_identity_value_and_mask:"Combine identity, value and reveal status",
  interleaved_post_layer_norm_transformer_encoding:"Interleaved Transformer layers",
  interleaved_pre_rms_norm_swiglu_qk_norm_transformer_encoding:"Interleaved Transformer layers",
  stack_source_tokens_and_align_availability_mask:"Assemble prior tokens and availability mask",
  sample_reveal_fraction_and_positions:"Choose training reveal positions",
  conditioned_full_profile_prediction:"Predict full expression profile",
  gene_identity_context_encoding:"Encode perturbation-gene condition",
};
const nodeLabel=(node)=>node?.representation_type.replaceAll("_"," ") || "unknown node";
function pathView(assembly){
  const nodes=new Map(assembly.nodes.map((node)=>[node.node_id,node]));
  const receipt=assembly.receipt_inputs.find((item)=>item.node_id===state.receipt) || assembly.receipt_inputs[0];
  if(!receipt)return '<p class="empty">Receiving operand is unspecified.</p>';
  state.receipt=receipt.node_id;
  const available=pathTools.availableSources(assembly,receipt.node_id);
  if(![...available.roots,...available.intermediates].some((node)=>node.node_id===state.source))state.source=available.defaultSource;
  const path=pathTools.inputPath(assembly,state.source,receipt.node_id);
  const groups=pathTools.groupPathCalls(path);
  const levels=[...new Set(groups.map((group)=>group.level))].sort((a,b)=>a-b);
  const option=(node)=>`<option value="${esc(node.node_id)}" ${node.node_id===state.source ? "selected" : ""}>${esc(nodeLabel(node))} · ${esc(node.node_id)}</option>`;
  const dataLabel=(id)=>`<span class="path-data" title="${esc(nodes.get(id)?.information_content)}">${esc(nodeLabel(nodes.get(id)))}<small class="node-reference">${esc(id)}</small></span>`;
  return `<div class="path-controls"><label>Source / input boundary<select id="path-source"><optgroup label="Source and parameter boundaries">${available.roots.map(option).join("")}</optgroup><optgroup label="Intermediate representations">${available.intermediates.map(option).join("")}</optgroup></select></label><label>Receiving port<select id="path-receipt">${assembly.receipt_inputs.map((item)=>`<option value="${esc(item.node_id)}" ${item.node_id===state.receipt ? "selected" : ""}>${esc(item.port_role)}</option>`).join("")}</select></label></div>
    <div id="path-diagram" class="diagram-viewport"></div><section id="diagram-inspector" class="diagram-inspector"></section>
    <details class="textual-path"><summary>Textual path and step evidence</summary><div class="path-endpoint"><span class="phase">SOURCE</span><strong>${esc(nodeLabel(nodes.get(state.source)))}</strong><p class="small">${esc(nodes.get(state.source)?.information_content)}</p></div>
    <div id="focused-path">${levels.map((level)=>{
      const band=groups.filter((group)=>group.level===level);
      return `<div class="path-band ${band.length>1 ? "parallel-band" : ""}">${band.length>1 ? '<div class="branch-heading">Parallel dependency branches</div>' : ""}<div class="path-stage-grid">${band.map((group)=>{
        const localInputs=group.inputs.filter((id)=>path.nodeIds.has(id));
        const localOutputs=group.outputs.filter((id)=>path.nodeIds.has(id));
        return `<article class="path-stage" data-source-step="${esc(group.sourceStepId)}"><div class="path-inputs">${localInputs.map(dataLabel).join('<span class="join-symbol">+</span>')}</div><div class="path-operations">${group.calls.map((call)=>`<span class="operation-token ${call.operation_id ? "" : "boundary-token"}">${esc(call.operation_id ? operations.get(call.operation_id).label : boundaryNames[call.parameters.source_operation] || call.parameters.source_operation.replaceAll("_"," "))}${call.parameters.method ? `<small>${esc(call.parameters.method.replaceAll("_"," "))}</small>` : ""}</span>`).join('<span class="within-step-arrow">→</span>')}</div><div class="path-outputs">${localOutputs.map(dataLabel).join('<span class="join-symbol">+</span>')}</div>${group.calls.some((call)=>!call.operation_id) ? '<span class="boundary-state">Internal rule remains unexpanded</span>' : ""}${[...new Set(group.calls.map((call)=>call.condition ? ((call.operation_id ? operations.get(call.operation_id).label : "Source step")+" applies when "+call.condition) : null).filter(Boolean))].map((condition)=>`<p class="path-condition">${esc(condition)}</p>`).join("")}${group.sideInputs.length ? `<details class="side-inputs"><summary>Additional inputs · ${group.sideInputs.length}</summary>${group.sideInputs.map((id)=>`<div class="side-input-row"><span>${esc(nodeLabel(nodes.get(id)))}</span><button class="inline-link" data-path-source="${esc(id)}">Trace this input</button></div>`).join("")}</details>` : ""}<details class="step-details"><summary>Parameters and evidence</summary>${group.calls.map((call)=>callView(call,assembly)).join("")}</details></article>`;
      }).join("")}</div></div>`;
    }).join("")}${groups.length ? "" : '<p class="small">This representation is supplied directly at the selected receiving boundary.</p>'}</div>
    ${path.bypasses.length ? `<details class="path-bypasses"><summary>Conditional bypasses on this path</summary>${path.bypasses.map((edge)=>`<p class="small">${esc(nodeLabel(nodes.get(edge.source_node_id)))} → ${esc(nodeLabel(nodes.get(edge.target_node_id)))}<br>${esc(edge.condition)}</p>`).join("")}</details>` : ""}
    <div class="path-endpoint receipt-endpoint"><span class="phase">RECEIVER</span><strong>${esc(assembly.recipient_component)}</strong><p class="small">${esc(receipt.port_role)} ← ${esc(nodeLabel(nodes.get(receipt.node_id)))}</p></div></details>`;
}

function drawDiagram(){
  const container=$("path-diagram");if(!container||!activeAssembly)return;
  const assembly=activeAssembly;
  const path=pathTools.inputPath(assembly,state.source,state.receipt);
  const diagram=pathTools.pathDiagram(path);
  const select=(node)=>{
    const panel=$("diagram-inspector");
    if(node.kind==="step")panel.innerHTML=`<h4>${esc(node.group.calls.map((call)=>call.operation_id ? operations.get(call.operation_id).label : boundaryNames[call.parameters.source_operation] || call.parameters.source_operation.replaceAll("_"," ")).join(" → "))}</h4>${node.group.sideInputs.length?`<details><summary>Additional inputs · ${node.group.sideInputs.length}</summary>${node.group.sideInputs.map((id)=>`<div class="side-input-row"><span>${esc(nodeLabel(assembly.nodes.find((item)=>item.node_id===id)))}</span><button class="inline-link" data-path-source="${esc(id)}">Trace this input</button></div>`).join("")}</details>`:""}${node.group.calls.map((call)=>callView(call,assembly)).join("")}`;
    else{
      const data=assembly.nodes.find((item)=>item.node_id===node.dataId);
      panel.innerHTML=`<h4>${esc(nodeLabel(data))}</h4><p class="small">${esc(data?.information_content)}</p>${node.kind==="receiver"?`<p class="small">${esc(assembly.receipt_inputs.find((item)=>item.node_id===node.dataId)?.port_role)}</p>`:""}<details><summary>Source evidence</summary>${sourceEvidence(assembly.record_id,data?.evidence || [])}</details>`;
    }
  };
  diagramTools.renderDiagram(container,{diagram,assembly,operations,boundaryNames,onSelect:select});
  select(diagram.nodes[0]);
}

function reviewPanel(assembly) {
  const record = catalog.records[assembly.record_id];
  if (!record?.decomposition_status) return "";
  const chains = new Set(assemblies.filter((item) => item.record_id === assembly.record_id).map((item) => item.trajectory_id));
  const own = (record.open_findings || []).filter((item) => item.trajectory_id === assembly.trajectory_id);
  const paperLevel = (record.open_findings || []).filter((item) => !chains.has(item.trajectory_id));
  const blocking = own.filter((item) => item.severity === "blocking").length;
  const card = (item) => `<article class="example"><strong>${esc(item.severity)} · ${esc(item.issue_type.replaceAll("_", " "))}</strong>${item.step_id ? `<div class="provenance">${esc(item.step_id)}</div>` : ""}<p class="small">${esc(item.detail)}</p><p class="small"><b>Required change:</b> ${esc(item.required_change)}</p></article>`;
  return `<details class="source-panel review-panel"><summary>Agent-decomposed candidate · independent review: ${record.open_blocking_findings} open blocking findings in this paper, ${blocking} on this path</summary>${own.map(card).join("") || '<p class="small">No open findings on this path.</p>'}${paperLevel.length ? `<h4 class="paper-level">Paper-level findings · ${paperLevel.length} (paths the paper documents but this reconstruction lacks)</h4>${paperLevel.map(card).join("")}` : ""}</details>`;
}

function chainView(assembly, supplemental = false) {
  activeAssembly=assembly;
  const contexts=assemblies.filter((item)=>item.record_id===assembly.record_id);
  const variants=[...new Set(contexts.map((item)=>item.model_variant))];
  return `<span class="kind">${supplemental ? "Supplemental section example · WITHDRAWN source" : "Model input paths"}</span><h2>${esc(paper(assembly.record_id))}</h2><div class="block-id">${esc(assembly.model_variant)} · ${esc(assembly.lifecycle_phase.replaceAll("_"," "))} · ${esc(assembly.model_role.replaceAll("_"," "))}</div>${supplemental ? "" : `<label class="context-label">Model variant · task · phase<select id="context-select" class="context-select" aria-label="Task and phase">${variants.map((variant)=>`<optgroup label="${esc(variant)}">${contexts.filter((item)=>item.model_variant===variant).map((item)=>`<option value="${esc(item.trajectory_id)}" ${item.trajectory_id===assembly.trajectory_id ? "selected" : ""}>${esc(item.lifecycle_phase.replaceAll("_"," "))} · ${esc(item.task_configuration)}</option>`).join("")}</optgroup>`).join("")}</select></label>`}<p class="task-description">${esc(assembly.task_configuration)}</p>${supplemental ? "" : reviewPanel(assembly)}<section class="input-path-section"><h3>Input path</h3><div id="path-panel">${pathView(assembly)}</div></section><details id="full-graph" class="section"><summary>Complete transformation graph · ${assembly.calls.length} calls</summary>${assembly.calls.map((call)=>callView(call,assembly)).join("")}${assembly.bypasses.map((edge)=>`<p class="small">${esc(edge.source_node_id)} → ${esc(edge.target_node_id)} · ${esc(edge.condition)}</p>`).join("")}</details><details><summary>Data nodes and parameter resources</summary>${assembly.nodes.map((node)=>`<p class="shape">${esc(node.node_id)} · ${esc(node.representation_type)}${node.symbolic_shape ? ` [${esc(node.symbolic_shape.join(", "))}]` : ""}</p><p class="small">${esc(node.information_content)}</p>`).join("")}</details><details class="section"><summary>Source questions and original-paper figure</summary>${assembly.open_questions.map((question)=>`<p class="small">${esc(question)}</p>`).join("")}${sourceFigure(assembly.record_id)}</details><details><summary>Complete chain JSON</summary><pre>${esc(JSON.stringify(assembly,null,2))}</pre></details>`;
}

function operationView(block) {
  const byPaper = new Map();
  for (const use of block.usage) if (!byPaper.has(use.record_id)) byPaper.set(use.record_id,use);
  return `<span class="kind">Reusable operation</span><h2>${esc(block.label)}</h2><div class="block-id">${esc(block.operation_id)} @ ${esc(catalog.release)}</div><p class="definition">${esc(block.definition)}</p><p class="boundary">${esc(block.boundaries)}</p><div class="metrics"><span><b>${block.reuse_record_ids.length}</b> papers</span><span><b>${block.usage.length}</b> operation calls</span></div><div class="section ports">${ports("Inputs",block.inputs)}${ports("Outputs",block.outputs)}</div><div class="section"><h3>Instance parameters</h3><div class="provenance">${block.parameters.map(esc).join(" · ")}</div></div><div class="section"><h3>Applications across papers</h3>${[...byPaper.values()].map((use) => {
    const assembly = assemblies.find((item) => item.record_id === use.record_id && item.trajectory_id === use.trajectory_id);
    const call = assembly.calls.find((item) => item.call_id === use.call_id);
    return `<article class="example"><div class="example-heading"><strong>${esc(paper(use.record_id))}</strong><span class="phase">${esc(assembly.lifecycle_phase)}</span></div>${callView(call,assembly)}${use.evidence_ids.map((id) => quotePanel(evidence.find((entry) => entry.evidence_id === id))).join("")}<button class="inline-link" data-assembly="${esc(use.record_id)}" data-context="${esc(use.trajectory_id)}">Open full chain</button>${sourceFigure(use.record_id)}</article>`;
  }).join("")}${block.supplemental_examples.map((item,index) => `<article class="example"><strong>${esc(item.paper)} · ${esc(item.source_status)}</strong><p class="small">${esc(item.scope)}</p><div class="flow">${item.assembly.calls.map((call) => `<span class="flow-step">${esc(operations.get(call.operation_id).label)}</span>`).join("")}</div><button class="inline-link" data-supplement="${esc(block.operation_id)}" data-example="${index}">Inspect branched expression / gene-ID chain</button></article>`).join("")}</div>${block.official_reference ? `<div class="section"><a href="${esc(block.official_reference)}" target="_blank" rel="noreferrer">Official operation reference</a></div>` : ""}<details><summary>All uses and operation JSON</summary><pre>${esc(JSON.stringify(block,null,2))}</pre></details>`;
}

function drawDetail() {
  const item = listItems().find((entry) => key(entry) === state.selected);
  if (!item) { $("detail").innerHTML='<p class="empty">No matching entries.</p>'; return; }
  if (state.view === "blocks" || state.view === "reuse") $("detail").innerHTML = operationView(item);
  else if (state.view === "assemblies") {
    const assembly = item.chains.find((chain) => chain.trajectory_id === state.context) || item.chains[0];
    state.context = assembly.trajectory_id;
    $("detail").innerHTML = chainView(assembly);
  } else $("detail").innerHTML = `<span class="kind">Documented boundary awaiting decomposition</span><h2>${esc(title(item))}</h2>${item.occurrences.map((use) => `<article class="example"><strong>${esc(paper(use.record_id))}</strong><div class="provenance">${esc(use.trajectory_id)} / ${esc(use.source_step_id)}</div><button class="inline-link" data-assembly="${esc(use.record_id)}" data-context="${esc(use.trajectory_id)}">Inspect complete source chain</button></article>`).join("")}`;
  icons();drawDiagram();
}
function drawList() {
  const filtered=listItems();
  if (!filtered.some((item) => key(item) === state.selected)) state.selected=filtered[0] ? key(filtered[0]) : null;
  $("count").textContent=filtered.length;
  $("list-label").textContent={blocks:"OPERATIONS",assemblies:"MODEL CHAINS",proposals:"UNEXPANDED BOUNDARIES",reuse:"REUSED ACROSS PAPERS"}[state.view];
  $("catalog-list").innerHTML=filtered.map((item) => `<button class="list-entry ${key(item) === state.selected ? "active" : ""}" data-select="${esc(key(item))}"><strong>${esc(title(item))}</strong><span class="list-meta"><span>${item.operation_id ? `${item.reuse_record_ids.length} papers` : item.chains ? `${item.chains.length} contexts` : `${item.occurrences.length} source uses`}</span><span>${item.operation_id ? item.usage.length ? `${item.usage.length} calls` : `${item.supplemental_examples.length} section example` : ""}</span></span></button>`).join("") || '<p class="empty">No matching entries.</p>';
  drawDetail();
}
function navigate(view,id,context=null) {
  Object.assign(state,{view,selected:id,context,query:"",reuse:"",paper:"",source:null,receipt:null});
  $("search").value=""; $("reuse").value=""; $("paper").value="";
  $("reuse").disabled=view === "assemblies" || view === "proposals";
  document.querySelectorAll("[data-view]").forEach((button) => button.setAttribute("aria-selected",button.dataset.view === view));
  history.replaceState(null,"",`#${view}/${encodeURIComponent(id || "")}${context ? "/"+encodeURIComponent(context) : ""}`);
  drawList();
}
document.addEventListener("click",(event) => {
  const button=event.target.closest("button"); if(!button)return;
  if(button.dataset.view)navigate(button.dataset.view,null);
  if(button.dataset.select){state.selected=button.dataset.select;state.context=null;state.source=null;state.receipt=null;drawList();}
  if(button.dataset.block)navigate("blocks",button.dataset.block);
  if(button.dataset.assembly)navigate("assemblies",button.dataset.assembly,button.dataset.context);
  if(button.dataset.supplement){const item=operations.get(button.dataset.supplement).supplemental_examples[Number(button.dataset.example)];$("detail").innerHTML=chainView(item.assembly,true);icons();drawDiagram();}
  if(button.dataset.pathSource){state.source=button.dataset.pathSource;$("path-panel").innerHTML=pathView(activeAssembly);drawDiagram();}
});
$("search").addEventListener("input",(event)=>{state.query=event.target.value;drawList();});
$("reuse").addEventListener("change",(event)=>{state.reuse=event.target.value;drawList();});
$("paper").addEventListener("change",(event)=>{state.paper=event.target.value;drawList();});
document.addEventListener("change",(event)=>{
  if(event.target.id === "context-select"){state.context=event.target.value;state.source=null;state.receipt=null;drawDetail();}
  if(event.target.id === "path-source"){state.source=event.target.value;$("path-panel").innerHTML=pathView(activeAssembly);drawDiagram();}
  if(event.target.id === "path-receipt"){state.receipt=event.target.value;state.source=null;$("path-panel").innerHTML=pathView(activeAssembly);drawDiagram();}
});
async function start(){
  const read=async(url)=>{const response=await fetch(url);if(!response.ok)throw new Error(`${url}: ${response.status}`);return response.json();};
  [catalog,assemblies,evidence,atlas,pathTools,diagramTools]=await Promise.all([read("data/catalog.json"),read("data/assemblies.json"),read("data/evidence.json"),read("../data/atlas.json"),import("./input-paths.mjs"),import("./diagram-view.mjs")]);
  operations=new Map(catalog.blocks.map((block)=>[block.operation_id,block]));
  $("release").textContent=`RELEASE ${catalog.release} / OPERATION CONSTRUCTOR`;
  $("totals").textContent=`${catalog.blocks.length} operations · ${catalog.report.cross_paper_reused_types} reused across papers`;
  $("paper").innerHTML+=Object.entries(catalog.records).map(([id,item])=>`<option value="${esc(id)}">${esc(item.paper)}</option>`).join("");
  const [view,id,context]=location.hash.substring(1).split("/").map(decodeURIComponent);
  navigate(["blocks","assemblies","proposals","reuse"].includes(view)?view:"blocks",id || "lookup",context);icons();
}
start().catch((error)=>{$("detail").innerHTML=`<h2 class="error">Library unavailable</h2><p>${esc(error.message)}</p>`;console.error(error);});
