const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const state = {view:"blocks", selected:null, query:"", reuse:"", paper:"", context:null};
let catalog, assemblies, evidence, atlas, operations;
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

function chainView(assembly, supplemental = false) {
  return `<span class="kind">${supplemental ? "Supplemental section example · WITHDRAWN source" : "Model chain"}</span><h2>${esc(paper(assembly.record_id))}</h2><div class="block-id">${esc(assembly.trajectory_id)} · ${esc(assembly.lifecycle_phase.replaceAll("_"," "))}</div>${supplemental ? "" : `<select id="context-select" class="context-select" aria-label="Task and phase">${assemblies.filter((item) => item.record_id === assembly.record_id).map((item) => `<option value="${esc(item.trajectory_id)}" ${item.trajectory_id === assembly.trajectory_id ? "selected" : ""}>${esc(item.trajectory_id)} · ${esc(item.lifecycle_phase)}</option>`).join("")}</select>`}<p class="definition">${esc(assembly.task_configuration)}</p><p class="small">${esc(assembly.model_variant)}</p><div class="section"><h3>Data transformations</h3>${assembly.calls.map((call) => callView(call,assembly)).join("")}</div>${assembly.bypasses.length ? `<div class="section"><h3>Conditional bypasses</h3>${assembly.bypasses.map((edge) => `<p class="operand-list">${esc(edge.source_node_id)} → ${esc(edge.target_node_id)}<br>${esc(edge.condition)}</p>`).join("")}</div>` : ""}<div class="section"><h3>Model input</h3><p class="rationale">${esc(assembly.recipient_component)}</p>${assembly.receipt_inputs.map((item) => `<div class="operand-list">${esc(item.node_id)} → ${esc(item.port_role)}</div>`).join("")}</div><details><summary>Data nodes and parameter resources</summary>${assembly.nodes.map((node) => `<p class="shape">${esc(node.node_id)} · ${esc(node.representation_type)}${node.symbolic_shape ? ` [${esc(node.symbolic_shape.join(", "))}]` : ""}</p><p class="small">${esc(node.information_content)}</p>`).join("")}</details><div class="section">${assembly.open_questions.map((question) => `<p class="small">${esc(question)}</p>`).join("")}${sourceFigure(assembly.record_id)}</div><details><summary>Complete chain JSON</summary><pre>${esc(JSON.stringify(assembly,null,2))}</pre></details>`;
}

function operationView(block) {
  const byPaper = new Map();
  for (const use of block.usage) if (!byPaper.has(use.record_id)) byPaper.set(use.record_id,use);
  return `<span class="kind">Reusable operation</span><h2>${esc(block.label)}</h2><div class="block-id">${esc(block.operation_id)} @ ${esc(catalog.release)}</div><p class="definition">${esc(block.definition)}</p><p class="boundary">${esc(block.boundaries)}</p><div class="metrics"><span><b>${block.reuse_record_ids.length}</b> pilot papers</span><span><b>${block.usage.length}</b> operation calls</span></div><div class="section ports">${ports("Inputs",block.inputs)}${ports("Outputs",block.outputs)}</div><div class="section"><h3>Instance parameters</h3><div class="provenance">${block.parameters.map(esc).join(" · ")}</div></div><div class="section"><h3>Applications across papers</h3>${[...byPaper.values()].map((use) => {
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
  icons();
}
function drawList() {
  const filtered=listItems();
  if (!filtered.some((item) => key(item) === state.selected)) state.selected=filtered[0] ? key(filtered[0]) : null;
  $("count").textContent=filtered.length;
  $("list-label").textContent={blocks:"OPERATIONS",assemblies:"MODEL CHAINS",proposals:"UNEXPANDED BOUNDARIES",reuse:"REUSED ACROSS PAPERS"}[state.view];
  $("catalog-list").innerHTML=filtered.map((item) => `<button class="list-entry ${key(item) === state.selected ? "active" : ""}" data-select="${esc(key(item))}"><strong>${esc(title(item))}</strong><span class="list-meta"><span>${item.operation_id ? `${item.reuse_record_ids.length} pilot papers` : item.chains ? `${item.chains.length} contexts` : `${item.occurrences.length} source uses`}</span><span>${item.operation_id ? item.usage.length ? `${item.usage.length} calls` : `${item.supplemental_examples.length} section example` : ""}</span></span></button>`).join("") || '<p class="empty">No matching entries.</p>';
  drawDetail();
}
function navigate(view,id,context=null) {
  Object.assign(state,{view,selected:id,context,query:"",reuse:"",paper:""});
  $("search").value=""; $("reuse").value=""; $("paper").value="";
  $("reuse").disabled=view === "assemblies" || view === "proposals";
  document.querySelectorAll("[data-view]").forEach((button) => button.setAttribute("aria-selected",button.dataset.view === view));
  history.replaceState(null,"",`#${view}/${encodeURIComponent(id || "")}${context ? "/"+encodeURIComponent(context) : ""}`);
  drawList();
}
document.addEventListener("click",(event) => {
  const button=event.target.closest("button"); if(!button)return;
  if(button.dataset.view)navigate(button.dataset.view,null);
  if(button.dataset.select){state.selected=button.dataset.select;state.context=null;drawList();}
  if(button.dataset.block)navigate("blocks",button.dataset.block);
  if(button.dataset.assembly)navigate("assemblies",button.dataset.assembly,button.dataset.context);
  if(button.dataset.supplement){const item=operations.get(button.dataset.supplement).supplemental_examples[Number(button.dataset.example)];$("detail").innerHTML=chainView(item.assembly,true);icons();}
});
$("search").addEventListener("input",(event)=>{state.query=event.target.value;drawList();});
$("reuse").addEventListener("change",(event)=>{state.reuse=event.target.value;drawList();});
$("paper").addEventListener("change",(event)=>{state.paper=event.target.value;drawList();});
document.addEventListener("change",(event)=>{if(event.target.id === "context-select"){state.context=event.target.value;drawDetail();}});
async function start(){
  const read=async(url)=>{const response=await fetch(url);if(!response.ok)throw new Error(`${url}: ${response.status}`);return response.json();};
  [catalog,assemblies,evidence,atlas]=await Promise.all([read("data/catalog.json"),read("data/assemblies.json"),read("data/evidence.json"),read("../data/atlas.json")]);
  operations=new Map(catalog.blocks.map((block)=>[block.operation_id,block]));
  $("release").textContent=`RELEASE ${catalog.release} / OPERATION CONSTRUCTOR`;
  $("totals").textContent=`${catalog.blocks.length} operations · ${catalog.report.cross_paper_reused_types} reused across pilot papers`;
  $("paper").innerHTML+=Object.entries(catalog.records).map(([id,item])=>`<option value="${esc(id)}">${esc(item.paper)}</option>`).join("");
  const [view,id,context]=location.hash.substring(1).split("/").map(decodeURIComponent);
  navigate(["blocks","assemblies","proposals","reuse"].includes(view)?view:"blocks",id || "lookup",context);icons();
}
start().catch((error)=>{$("detail").innerHTML=`<h2 class="error">Library unavailable</h2><p>${esc(error.message)}</p>`;console.error(error);});
