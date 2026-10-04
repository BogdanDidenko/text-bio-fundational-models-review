/* Source-backed catalog; all matching and evidence remain in downloadable data. */
const state = { view: "blocks", selected: null, query: "", kind: "", paper: "", context: null };
const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
let catalog, assemblies, evidence, atlas;
let blocks, evidenceMap;
const paperName = (id) => catalog.records[id]?.paper || id;
const icons = () => window.lucide?.createIcons();
const format = (value) => esc(String(value).replaceAll("_", " "));

function recordsFor(item) {
  if (state.view === "blocks") return [...(item.examples || []), ...(item.usage || [])].map((example) => example.record_id);
  if (state.view === "assemblies") return [item.record_id];
  if (state.view === "proposals") return item.occurrences.map((example) => example.record_id);
  return item.affected_block_ids.flatMap((id) => blocks.get(id)?.examples.map((example) => example.record_id) || []);
}

function items() {
  const source = { blocks: catalog.blocks, assemblies, proposals: catalog.proposals, decisions: catalog.decisions }[state.view];
  return source.filter((item) => (!state.kind || item.kind === state.kind || state.view === "assemblies" || state.view === "decisions") &&
    (!state.paper || recordsFor(item).includes(state.paper)) &&
    JSON.stringify(item).toLowerCase().includes(state.query.toLowerCase()));
}

function key(item) { return item.block_id || item.record_id || item.proposal_id || item.decision_id; }
function label(item) { return item.label || (item.record_id ? paperName(item.record_id) : item.source_label || item.subject); }
function drawList() {
  const filtered = items();
  if (!filtered.some((item) => key(item) === state.selected)) state.selected = filtered[0] ? key(filtered[0]) : null;
  $("count").textContent = filtered.length;
  $("list-label").textContent = { blocks: "CATALOG", assemblies: "SOURCE ASSEMBLIES", proposals: "PENDING REVIEW", decisions: "DECISION LEDGER" }[state.view];
  $("catalog-list").innerHTML = filtered.map((item) => {
    const meta = state.view === "assemblies" ? `${item.contexts.length} use contexts` :
      state.view === "blocks" ? `${new Set(recordsFor(item)).size} papers` :
      state.view === "proposals" ? `${item.occurrences.length} instances` : item.action.replaceAll("_", " ");
    return `<button class="list-entry ${state.selected === key(item) ? "active" : ""}" data-select="${esc(key(item))}" aria-pressed="${state.selected === key(item)}"><strong>${esc(label(item))}</strong><span class="list-meta"><span>${esc(item.kind || "model")}</span><span>${esc(meta)}</span></span></button>`;
  }).join("") || '<div class="empty">No matching entries.</div>';
  drawDetail();
}

function quotePanel(item) {
  return `<blockquote class="quote">${esc(item.quote)}</blockquote><div class="provenance">${esc(paperName(item.record_id))} / ${esc(item.heading_path.join(" › "))}<br>${esc(item.section_id)} · ${esc(item.kind)} · exact section match<br>section sha256 ${esc(item.section_sha256)}</div>`;
}

function evidenceFor(record, value) {
  const found = [];
  function visit(obj) {
    if (Array.isArray(obj)) return obj.forEach(visit);
    if (!obj || typeof obj !== "object") return;
    if (obj.quote) {
      const item = evidence.find((entry) => entry.record_id === record && entry.section_id === obj.section_id && entry.quote === obj.quote && entry.kind === obj.kind);
      if (item && !found.some((entry) => entry.evidence_id === item.evidence_id)) found.push(item);
    }
    Object.values(obj).forEach(visit);
  }
  visit(value);
  return found;
}

function sourceFigure(record) {
  const model = atlas.architectures?.find((item) => item.record_id === record && item.figure?.asset);
  if (!model) return "";
  return `<details class="source-panel"><summary>Original-paper figure · ${esc(model.model_name)}</summary><figure><img class="source-image" src="../${esc(model.figure.asset)}" alt="${esc(model.figure.caption)}" loading="lazy"><figcaption>${esc(model.figure.caption)}</figcaption></figure><div class="provenance">page ${esc(model.figure.page_no)} · sha256 ${esc(model.figure.sha256)}</div><a href="${esc(model.paper_url)}" target="_blank" rel="noreferrer">Source paper</a></details>`;
}

function blockDetail(block) {
  const records = new Set(recordsFor(block));
  const ports = (name, roles) => `<div><h3>${name}</h3><ul class="port-list">${roles.map((role) => `<li>${esc(role)}</li>`).join("")}</ul>${roles.length ? "" : '<p class="small">No computational port declared for this description type.</p>'}</div>`;
  return `<span class="kind ${esc(block.kind)}">${esc(block.kind)}</span><span class="badge">reviewed candidate</span><h2>${esc(block.label)}</h2><div class="block-id">${esc(block.block_id)} @ ${esc(block.version)}</div><p class="definition">${esc(block.definition)}</p><p class="boundary">${esc(block.boundaries)}</p><div class="metrics"><span><b>${records.size}</b> source papers</span><span><b>${block.usage.length}</b> mapped instances</span></div><div class="section ports">${ports("Input roles", block.input_roles)}${ports("Output roles", block.output_roles)}</div>
    ${block.composition.length ? `<div class="section"><h3>Constituent types</h3><div class="flow">${block.composition.map((id) => `<button class="flow-step" data-block="${esc(id)}">${esc(blocks.get(id)?.label || id)}</button>`).join("")}</div></div>` : ""}
    <div class="section"><h3>Source examples</h3>${block.examples.map((example) => `<article class="example"><div class="example-heading"><strong>${esc(example.paper)}</strong><span class="phase">${format(example.lifecycle_phase)}</span></div><div class="provenance">${esc(example.trajectory_id)} / ${esc(example.element_ids.join(" · "))}</div><p class="rationale">${esc(example.rationale)}</p>${example.elements.filter((item) => item.symbolic_shape).map((item) => `<p class="shape">${esc(item.representation_type)} [${esc(item.symbolic_shape.join(", "))}]<br>${esc((item.axis_semantics || []).join(" / "))}</p>`).join("")}${example.elements.filter((item) => item.inputs).map((item) => `<div class="operand-list">${item.inputs.map((input) => `${esc(input.port_role)} ← ${esc(input.node_id)}`).join("<br>")}<br>→ ${esc((item.outputs || []).join(" / "))}</div>`).join("")}${example.evidence_ids.map((id) => quotePanel(evidenceMap.get(id))).join("")}<div class="nav-inline"><button class="inline-link" data-assembly="${esc(example.record_id)}" data-context="${esc(example.trajectory_id)}">View source assembly</button></div>${sourceFigure(example.record_id)}</article>`).join("")}</div>
    ${block.aliases.length ? `<div class="section"><h3>Aliases</h3><div class="provenance">${block.aliases.map(esc).join(" · ")}</div></div>` : ""}<details><summary>Complete block JSON</summary><pre>${esc(JSON.stringify(block, null, 2))}</pre></details>`;
}

function bindingLabel(binding) {
  if (!binding.block_id) return '<span class="state">Extension proposal pending</span>';
  return `<button class="inline-link" data-block="${esc(binding.block_id)}">${esc(blocks.get(binding.block_id)?.label || binding.block_id)}</button> <span class="small">${esc(binding.relation)}</span>`;
}

function assemblyDetail(assembly) {
  let context = assembly.contexts.find((item) => item.trajectory_id === state.context) || assembly.contexts[0];
  state.context = context.trajectory_id;
  const nodeMap = new Map(assembly.nodes.map((item) => [item.node_id, item]));
  const selectedNodes = context.node_ids.map((id) => nodeMap.get(id));
  const operations = context.step_ids.map((id) => assembly.operations.find((item) => item.step_id === id));
  const recipient = assembly.recipients.find((item) => item.recipient_id === context.recipient_id);
  const nodeName = (id) => nodeMap.get(id)?.original_node_id || id;
  return `<span class="kind component">Model assembly</span><h2>${esc(paperName(assembly.record_id))}</h2><div class="block-id">${esc(assembly.record_id)} · library ${esc(assembly.library_release)}</div><select class="context-select" id="context-select" aria-label="Task and phase">${assembly.contexts.map((item) => `<option value="${esc(item.trajectory_id)}" ${item.trajectory_id === context.trajectory_id ? "selected" : ""}>${esc(item.trajectory_id)} · ${format(item.lifecycle_phase)}</option>`).join("")}</select><p class="definition">${esc(context.task_configuration)}</p><p class="small">${esc(context.model_variant)} · ${format(context.model_role)}</p>
    <div class="section"><h3>Documented transformations</h3><div class="diagram">${operations.map((step, index) => `<article class="graph-operation"><h4>${index + 1}. ${esc(step.original_step_id)} · ${bindingLabel(step.binding)}</h4><div class="small">${esc(step.component)}</div><div class="operand-list">${step.inputs.map((item) => `${esc(nodeName(item.node_id))} → ${esc(item.port_role)}`).join("<br>")}<br>→ ${step.outputs.map((id) => esc(nodeName(id))).join(" / ")}</div>${step.uncertainty ? `<p class="state">${esc(step.uncertainty)}</p>` : ""}<details><summary>Source evidence</summary>${evidenceFor(assembly.record_id, step).map(quotePanel).join("")}</details></article>`).join("")}</div></div>
    <div class="section"><h3>Receiving component</h3><p class="rationale">${esc(recipient.component)}</p><div class="operand-list">${recipient.inputs.map((item) => `${esc(nodeName(item.node_id))} → ${esc(item.port_role)}`).join("<br>")}</div>${evidenceFor(assembly.record_id, context.evidence).map(quotePanel).join("")}</div>
    <div class="section"><h3>Representations</h3><div class="node-list">${selectedNodes.map((node) => `<article class="node"><strong>${esc(node.original_node_id)}</strong><div class="small">${bindingLabel(node.binding)}</div><div class="shape">${esc(node.representation_type)}${node.symbolic_shape ? ` [${esc(node.symbolic_shape.join(", "))}]` : " · shape unresolved"}</div><p class="small">${esc(node.information_content)}</p><div class="provenance">${esc((node.axis_semantics || []).join(" / "))}<br>${format(node.contextual_role)}</div>${node.uncertainty ? `<p class="state">${esc(node.uncertainty)}</p>` : ""}<details><summary>Source evidence</summary>${evidenceFor(assembly.record_id, node).map(quotePanel).join("")}</details></article>`).join("")}</div></div>
    ${context.open_questions.length ? `<div class="section"><h3>Open questions</h3>${context.open_questions.map((question) => `<p class="rationale">${esc(question)}</p>`).join("")}</div>` : ""}<div class="section">${sourceFigure(assembly.record_id)}</div><details><summary>Complete assembly JSON</summary><pre>${esc(JSON.stringify(assembly, null, 2))}</pre></details>`;
}

function proposalDetail(item) {
  return `<span class="kind ${esc(item.kind)}">${esc(item.kind)}</span><h2>${format(item.source_label)}</h2><p class="boundary">Awaiting steward review</p><div class="block-id">${esc(item.proposal_id)}</div><div class="section"><h3>Preserved source instances</h3>${item.occurrences.map((occurrence) => `<article class="example"><strong>${esc(paperName(occurrence.record_id))}</strong><div class="provenance">${esc(occurrence.trajectory_id)} / ${esc(occurrence.element_id)}</div><p><button class="inline-link" data-assembly="${esc(occurrence.record_id)}" data-context="${esc(occurrence.trajectory_id)}">Inspect documented mechanism</button></p></article>`).join("")}</div>`;
}

function drawDetail() {
  const item = items().find((entry) => key(entry) === state.selected);
  if (!item) { $("detail").innerHTML = '<p class="empty">No matching entries.</p>'; return; }
  $("detail").innerHTML = state.view === "blocks" ? blockDetail(item) : state.view === "assemblies" ? assemblyDetail(item) : state.view === "proposals" ? proposalDetail(item) : `<span class="kind">${format(item.action)}</span><h2>${esc(item.subject)}</h2><div class="block-id">${esc(item.decision_id)}</div><p class="definition">${esc(item.rationale)}</p>${item.affected_block_ids.map((id) => `<p><button class="inline-link" data-block="${esc(id)}">${esc(blocks.get(id)?.label || id)}</button></p>`).join("")}`;
  icons();
}

function navigate(view, selected, context = null) {
  state.view = view; state.selected = selected; state.context = context;
  state.query = ""; state.kind = ""; state.paper = "";
  $("search").value = ""; $("kind").value = ""; $("paper").value = "";
  document.querySelectorAll("[data-view]").forEach((button) => button.setAttribute("aria-selected", button.dataset.view === view));
  $("kind").disabled = view === "assemblies" || view === "decisions";
  history.replaceState(null, "", `#${view}/${encodeURIComponent(selected || "")}${context ? `/${encodeURIComponent(context)}` : ""}`);
  drawList();
}

document.addEventListener("click", (event) => {
  const target = event.target.closest("button");
  if (!target) return;
  if (target.dataset.view) navigate(target.dataset.view, null);
  if (target.dataset.select) { state.selected = target.dataset.select; state.context = null; drawList(); history.replaceState(null, "", `#${state.view}/${encodeURIComponent(state.selected)}`); }
  if (target.dataset.block) navigate("blocks", target.dataset.block);
  if (target.dataset.assembly) navigate("assemblies", target.dataset.assembly, target.dataset.context);
});
$("search").addEventListener("input", (event) => { state.query = event.target.value; drawList(); });
$("kind").addEventListener("change", (event) => { state.kind = event.target.value; drawList(); });
$("paper").addEventListener("change", (event) => { state.paper = event.target.value; drawList(); });
document.addEventListener("change", (event) => { if (event.target.id === "context-select") { state.context = event.target.value; drawDetail(); } });

async function start() {
  const read = async (url) => { const response = await fetch(url); if (!response.ok) throw new Error(`${url}: ${response.status}`); return response.json(); };
  [catalog, assemblies, evidence, atlas] = await Promise.all([read("data/catalog.json"), read("data/assemblies.json"), read("data/evidence.json"), read("../data/atlas.json")]);
  blocks = new Map(catalog.blocks.map((block) => [block.block_id, block]));
  evidenceMap = new Map(evidence.map((item) => [item.evidence_id, item]));
  $("release").textContent = `RELEASE ${catalog.release} / DEVELOPMENT CANDIDATE`;
  $("totals").textContent = `${catalog.blocks.length} blocks · ${assemblies.length} papers · ${catalog.report.trajectory_count} use contexts`;
  $("paper").innerHTML += Object.entries(catalog.records).map(([id, item]) => `<option value="${esc(id)}">${esc(item.paper)}</option>`).join("");
  const [view, id, context] = location.hash.substring(1).split("/").map(decodeURIComponent);
  navigate(["blocks", "assemblies", "proposals", "decisions"].includes(view) ? view : "blocks", id || null, context || null);
  icons();
}
start().catch((error) => { $("detail").innerHTML = `<h2 class="error">Library unavailable</h2><p>${esc(error.message)}</p>`; console.error(error); });
