const state = {
  atlas: null,
  view: "graph",
  query: "",
  family: "",
  subtype: "",
  lifecycle: "",
  modality: "",
  selection: { type: "root", id: "taxonomy_root" },
  evidencePage: 1,
  evidencePageSize: 50,
};

const familyById = new Map();
const subtypeById = new Map();
const architectureById = new Map();
const graphNodeById = new Map();
let graphZoom = null;
let graphLayout = null;

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function unique(values) {
  return [...new Set((values || []).filter(Boolean))];
}

function refreshIcons() {
  if (window.lucide) window.lucide.createIcons({ attrs: { "aria-hidden": "true" } });
}

function familyMeta(familyId) {
  return familyById.get(familyId) || { color: "#66717a", code: "?", short: familyId };
}

function subtypeLabel(subtypeId) {
  const subtype = subtypeById.get(subtypeId);
  return subtype ? `${subtype.leaf_id} · ${subtype.name}` : subtypeId;
}

function shorten(value, length = 74) {
  const text = String(value || "Not stated").replace(/\s+/g, " ").trim();
  return text.length > length ? `${text.slice(0, length - 1)}…` : text;
}

function cropMarkup(architecture, context = "node") {
  const figure = architecture.figure;
  if (!figure) {
    return `<div class="no-figure no-figure-${context} ${context === "node" || context === "tiny" ? "is-compact" : ""}">
      <i data-lucide="file-x-2"></i><span>No suitable source figure</span>
    </div>`;
  }
  const crop = figure.crop_box;
  const cropRatio = (crop.width * figure.pixel_width) / (crop.height * figure.pixel_height);
  let frameStyle = `aspect-ratio:${cropRatio};`;
  if (context === "node") {
    const width = cropRatio >= 1.26 ? 92 : Math.max(48, 73 * cropRatio);
    const height = cropRatio >= 1.26 ? 92 / cropRatio : 73;
    frameStyle += `width:${width}px;height:${height}px;`;
  }
  const imageStyle = [
    `width:${100 / crop.width}%`,
    `left:${(-100 * crop.x) / crop.width}%`,
    `top:${(-100 * crop.y) / crop.height}%`,
  ].join(";");
  return `<div class="paper-crop paper-crop-${context}" style="${frameStyle}" data-model-crop="${escapeHtml(architecture.model_id)}">
    <img src="${escapeHtml(figure.asset)}" alt="Relevant crop from Figure ${figure.figure_index} for ${escapeHtml(architecture.model_name)}" style="${imageStyle}" loading="lazy">
  </div>`;
}

function exampleMarkup(architecture, context = "node") {
  const example = architecture.illustrative_examples[0];
  if (!example) return "";
  if (context === "node") {
    return `<div class="node-example"><span>Illustrative input</span><code>${escapeHtml(shorten(example.example_input, 56))}</code></div>`;
  }
  return architecture.illustrative_examples
    .map((item) => {
      const family = familyMeta(item.family_id);
      return `<div class="input-example" style="--family-color:${family.color}">
        <div class="example-label"><span>${escapeHtml(subtypeLabel(item.subtype_id))}</span><em>Illustrative · not paper evidence</em></div>
        <div class="example-flow">
          <code>${escapeHtml(item.example_input)}</code><i data-lucide="arrow-right"></i>
          <code>${escapeHtml(item.example_carrier)}</code><i data-lucide="arrow-right"></i>
          <strong>${escapeHtml(item.example_interface)}</strong>
        </div>
        <details><summary>Grounded route represented by this example</summary>
          <p><b>Source:</b> ${escapeHtml(item.actual_source)}</p>
          <p><b>Model-visible form:</b> ${escapeHtml(item.actual_model_visible_form)}</p>
        </details>
      </div>`;
    })
    .join("");
}

function architectureMatches(architecture) {
  if (state.family && !architecture.families.includes(state.family)) return false;
  if (state.subtype && !architecture.subtypes.includes(state.subtype)) return false;
  if (state.lifecycle && !architecture.lifecycle_phases.includes(state.lifecycle)) return false;
  if (state.modality && !architecture.modalities.includes(state.modality)) return false;
  if (!state.query) return true;
  const query = state.query.toLocaleLowerCase();
  const haystack = [
    architecture.model_name,
    architecture.paper_title,
    architecture.doi,
    ...architecture.modalities,
    ...architecture.lifecycle_phases,
    ...architecture.routes.flatMap((route) => [
      route.route_label,
      route.source_object_verbatim,
      route.model_visible_form_verbatim,
      route.evidence_quote,
      route.section_heading,
    ]),
  ].join(" ").toLocaleLowerCase();
  return haystack.includes(query);
}

function filteredArchitectures() {
  return state.atlas.architectures.filter(architectureMatches);
}

function filteredRoutes() {
  const rows = [];
  filteredArchitectures().forEach((architecture) => {
    architecture.routes.forEach((route) => {
      if (state.family && route.carrier_family !== state.family) return;
      if (state.subtype && route.carrier_subtype !== state.subtype) return;
      if (state.lifecycle && route.lifecycle_phase !== state.lifecycle) return;
      if (state.modality && route.source_modality_normalized !== state.modality) return;
      rows.push({ architecture, route });
    });
  });
  return rows;
}

function populateHeader() {
  const meta = state.atlas.meta;
  const stats = [
    [meta.model_count, "models"],
    [meta.route_count, "routes"],
    [meta.models_with_cropped_figure, "cropped figures"],
    [meta.models_without_suitable_figure, "text-only visual cases"],
  ];
  $("#header-stats").innerHTML = stats
    .map(([value, label]) => `<div class="stat-block"><strong>${value}</strong><span>${label}</span></div>`)
    .join("");
}

function populateFilters() {
  $("#family-filter").innerHTML = [
    `<button type="button" class="is-active" data-family="" style="--family-color:#172026" title="All carrier families">All</button>`,
    ...state.atlas.families.map((family) => `<button type="button" data-family="${escapeHtml(family.family_id)}" style="--family-color:${family.color}" title="${escapeHtml(family.name)}">${escapeHtml(family.code)}</button>`),
  ].join("");

  $("#subtype-filter").insertAdjacentHTML("beforeend", state.atlas.families
    .flatMap((family) => family.subtypes.map((subtype) => `<option value="${escapeHtml(subtype.subtype_id)}">${escapeHtml(subtype.leaf_id)} · ${escapeHtml(subtype.name)}</option>`))
    .join(""));
  $("#lifecycle-filter").insertAdjacentHTML("beforeend", state.atlas.filter_values.lifecycle_phases
    .map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value.replaceAll("_", " "))}</option>`).join(""));
  $("#modality-filter").insertAdjacentHTML("beforeend", state.atlas.filter_values.modalities
    .map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join(""));
}

function syncFilterControls() {
  $$("#family-filter button").forEach((button) => button.classList.toggle("is-active", button.dataset.family === state.family));
  $("#subtype-filter").value = state.subtype;
  $("#lifecycle-filter").value = state.lifecycle;
  $("#modality-filter").value = state.modality;
  $("#search-input").value = state.query;
}

function graphData() {
  const models = filteredArchitectures();
  const allowedSubtypeIds = new Set();
  models.forEach((model) => model.subtypes.forEach((subtypeId) => {
    const subtype = subtypeById.get(subtypeId);
    if ((!state.family || subtype.family_id === state.family) && (!state.subtype || subtypeId === state.subtype)) {
      allowedSubtypeIds.add(subtypeId);
    }
  }));
  const families = state.atlas.families
    .filter((family) => !state.family || family.family_id === state.family)
    .map((family) => ({
      ...family,
      visibleSubtypes: family.subtypes.filter((subtype) => allowedSubtypeIds.has(subtype.subtype_id)),
    }))
    .filter((family) => family.visibleSubtypes.length);
  return { models, families, allowedSubtypeIds };
}

function calculateGraphLayout() {
  const { models, families, allowedSubtypeIds } = graphData();
  const modelMap = new Map(models.map((model) => [model.model_id, model]));
  const subtypeOrder = new Map();
  let orderIndex = 0;
  state.atlas.families.forEach((family) => family.subtypes.forEach((subtype) => subtypeOrder.set(subtype.subtype_id, orderIndex++)));
  const assigned = new Map([...allowedSubtypeIds].map((id) => [id, []]));
  const parentSubtypes = new Map();
  models.forEach((model) => {
    const parents = model.subtypes.filter((id) => allowedSubtypeIds.has(id)).sort((a, b) => subtypeOrder.get(a) - subtypeOrder.get(b));
    parentSubtypes.set(model.model_id, parents);
    const primary = parents.includes(model.primary_subtype) ? model.primary_subtype : parents[0];
    if (primary) assigned.get(primary).push(model);
  });
  assigned.forEach((list) => list.sort((a, b) => a.model_name.localeCompare(b.model_name)));

  const modelColumns = models.length <= 12 ? 3 : models.length <= 35 ? 5 : 7;
  const positions = new Map();
  const ROOT_X = 44;
  const FAMILY_X = 302;
  const SUBTYPE_X = 600;
  const MODEL_X = 960;
  const MODEL_W = 230;
  const MODEL_H = 132;
  const MODEL_GAP_X = 22;
  const MODEL_GAP_Y = 18;
  let cursorY = 48;
  const visibleSubtypes = [];

  families.forEach((family) => {
    const familyStart = cursorY;
    family.visibleSubtypes.forEach((subtype) => {
      const subtypeModels = assigned.get(subtype.subtype_id) || [];
      const rows = Math.max(1, Math.ceil(subtypeModels.length / modelColumns));
      const blockHeight = Math.max(138, rows * (MODEL_H + MODEL_GAP_Y));
      const centerY = cursorY + blockHeight / 2;
      positions.set(`subtype::${subtype.subtype_id}`, { x: SUBTYPE_X, y: centerY - 46, width: 280, height: 92, type: "subtype" });
      visibleSubtypes.push(subtype);
      subtypeModels.forEach((model, index) => {
        const column = index % modelColumns;
        const row = Math.floor(index / modelColumns);
        positions.set(`model::${model.model_id}`, {
          x: MODEL_X + column * (MODEL_W + MODEL_GAP_X),
          y: cursorY + row * (MODEL_H + MODEL_GAP_Y),
          width: MODEL_W,
          height: MODEL_H,
          type: "model",
        });
      });
      cursorY += blockHeight + 28;
    });
    const familyEnd = cursorY - 28;
    positions.set(`family::${family.family_id}`, { x: FAMILY_X, y: (familyStart + familyEnd) / 2 - 43, width: 228, height: 86, type: "family" });
    cursorY += 38;
  });
  const graphHeight = Math.max(680, cursorY + 24);
  positions.set("taxonomy_root", { x: ROOT_X, y: graphHeight / 2 - 49, width: 196, height: 98, type: "root" });
  const graphWidth = MODEL_X + modelColumns * (MODEL_W + MODEL_GAP_X) + 48;

  const nodes = [{ id: "taxonomy_root", type: "root", label: "Model-visible input representation" }];
  families.forEach((family) => {
    nodes.push({ id: `family::${family.family_id}`, type: "family", label: family.name, family_id: family.family_id, data: family });
    family.visibleSubtypes.forEach((subtype) => nodes.push({ id: `subtype::${subtype.subtype_id}`, type: "subtype", label: subtype.name, family_id: family.family_id, subtype_id: subtype.subtype_id, data: subtype }));
  });
  models.forEach((model) => nodes.push({ id: `model::${model.model_id}`, type: "model", label: model.model_name, model_id: model.model_id, data: model }));

  const edges = [];
  families.forEach((family) => {
    edges.push({ id: `edge::root::${family.family_id}`, source: "taxonomy_root", target: `family::${family.family_id}`, type: "contains_family" });
    family.visibleSubtypes.forEach((subtype) => edges.push({ id: `edge::${family.family_id}::${subtype.subtype_id}`, source: `family::${family.family_id}`, target: `subtype::${subtype.subtype_id}`, type: "contains_subtype", family_id: family.family_id }));
  });
  models.forEach((model) => {
    (parentSubtypes.get(model.model_id) || []).forEach((subtypeId) => edges.push({
      id: `edge::${subtypeId}::${model.model_id}`,
      source: `subtype::${subtypeId}`,
      target: `model::${model.model_id}`,
      type: "classifies_model_route",
      family_id: subtypeById.get(subtypeId).family_id,
    }));
  });
  return { nodes, edges, positions, graphWidth, graphHeight, modelMap };
}

function edgePath(edge, positions) {
  const source = positions.get(edge.source);
  const target = positions.get(edge.target);
  const x1 = source.x + source.width;
  const y1 = source.y + source.height / 2;
  const x2 = target.x;
  const y2 = target.y + target.height / 2;
  const bend = x1 + (x2 - x1) * 0.52;
  return `M${x1},${y1} C${bend},${y1} ${bend},${y2} ${x2},${y2}`;
}

function taxonomyNodeMarkup(node) {
  if (node.type === "root") {
    return `<div class="taxonomy-node root-node"><span>Taxonomy root</span><strong>${escapeHtml(node.label)}</strong><small>489 grounded input routes</small></div>`;
  }
  if (node.type === "family") {
    const family = familyMeta(node.family_id);
    return `<div class="taxonomy-node family-node" style="--family-color:${family.color}"><span>${escapeHtml(family.code)} · Carrier family</span><strong>${escapeHtml(node.label)}</strong><small>${node.data.route_count} routes · ${node.data.model_count} models</small></div>`;
  }
  const family = familyMeta(node.family_id);
  return `<div class="taxonomy-node subtype-node" style="--family-color:${family.color}"><span>${escapeHtml(node.data.leaf_id)} · Subtype</span><strong>${escapeHtml(node.label)}</strong><small>${node.data.route_count} routes · ${node.data.model_count} models</small></div>`;
}

function modelNodeMarkup(architecture) {
  const primaryFamily = familyMeta(subtypeById.get(architecture.primary_subtype).family_id);
  return `<div class="model-graph-node" style="--family-color:${primaryFamily.color}" data-model-id="${escapeHtml(architecture.model_id)}">
    <div class="model-node-media">
      <div class="node-evidence"><span>Paper evidence</span>${cropMarkup(architecture, "node")}</div>
      ${exampleMarkup(architecture, "node")}
    </div>
    <div class="model-node-footer">
      <strong title="${escapeHtml(architecture.model_name)}">${escapeHtml(architecture.model_name)}</strong>
      <span>${architecture.route_count} routes${architecture.families.length > 1 ? ` · ${architecture.families.length} families` : ""}</span>
    </div>
  </div>`;
}

function renderGraph({ fit = false } = {}) {
  graphLayout = calculateGraphLayout();
  const svg = d3.select("#taxonomy-graph");
  const edges = d3.select("#graph-edges").selectAll("path.graph-edge").data(graphLayout.edges, (item) => item.id);
  edges.exit().remove();
  edges.enter().append("path")
    .attr("class", "graph-edge")
    .attr("marker-end", "url(#arrowhead)")
    .merge(edges)
    .attr("data-edge-id", (item) => item.id)
    .attr("data-source", (item) => item.source)
    .attr("data-target", (item) => item.target)
    .attr("stroke", (item) => item.family_id ? familyMeta(item.family_id).color : "#87929a")
    .attr("d", (item) => edgePath(item, graphLayout.positions));

  const nodes = d3.select("#graph-nodes").selectAll("foreignObject.graph-node").data(graphLayout.nodes, (item) => item.id);
  nodes.exit().remove();
  const entered = nodes.enter().append("foreignObject").attr("class", (item) => `graph-node graph-node-${item.type}`);
  entered.append("xhtml:div");
  const merged = entered.merge(nodes)
    .attr("data-node-id", (item) => item.id)
    .attr("x", (item) => graphLayout.positions.get(item.id).x)
    .attr("y", (item) => graphLayout.positions.get(item.id).y)
    .attr("width", (item) => graphLayout.positions.get(item.id).width)
    .attr("height", (item) => graphLayout.positions.get(item.id).height)
    .on("mouseenter", (_, item) => highlightGraph(item.id))
    .on("mouseleave", () => applySelectionHighlight())
    .on("click", (_, item) => selectGraphNode(item));
  merged.select("div").html((item) => item.type === "model" ? modelNodeMarkup(item.data) : taxonomyNodeMarkup(item));

  $("#graph-summary").textContent = `${graphLayout.nodes.filter((node) => node.type === "model").length} models · ${graphLayout.edges.length} visible links`;
  if (!graphZoom) {
    graphZoom = d3.zoom().scaleExtent([0.12, 3]).on("zoom", (event) => d3.select("#graph-stage").attr("transform", event.transform));
    svg.call(graphZoom).on("dblclick.zoom", null);
  }
  applySelectionHighlight();
  refreshIcons();
  if (fit) requestAnimationFrame(fitGraph);
}

function fitGraph() {
  if (!graphLayout || !graphZoom) return;
  const svgElement = $("#taxonomy-graph");
  const width = svgElement.clientWidth;
  const height = svgElement.clientHeight;
  if (!width || !height) return;
  const scale = Math.max(0.12, Math.min(1.15, 0.94 * Math.min(width / graphLayout.graphWidth, height / graphLayout.graphHeight)));
  const x = (width - graphLayout.graphWidth * scale) / 2;
  const y = (height - graphLayout.graphHeight * scale) / 2;
  d3.select(svgElement).transition().duration(420).call(graphZoom.transform, d3.zoomIdentity.translate(x, y).scale(scale));
}

function zoomBy(factor) {
  d3.select("#taxonomy-graph").transition().duration(220).call(graphZoom.scaleBy, factor);
}

function highlightedIds(nodeId) {
  if (!graphLayout) return { nodes: new Set(), edges: new Set() };
  const node = graphLayout.nodes.find((item) => item.id === nodeId);
  if (!node) return { nodes: new Set(), edges: new Set() };
  const nodeIds = new Set([nodeId]);
  const edgeIds = new Set();
  let changed = true;
  while (changed) {
    changed = false;
    graphLayout.edges.forEach((edge) => {
      const includeAncestor = nodeIds.has(edge.target);
      const includeDescendant = node.type !== "model" && nodeIds.has(edge.source);
      if ((includeAncestor || includeDescendant) && !edgeIds.has(edge.id)) {
        edgeIds.add(edge.id);
        nodeIds.add(edge.source);
        nodeIds.add(edge.target);
        changed = true;
      }
    });
  }
  return { nodes: nodeIds, edges: edgeIds };
}

function highlightGraph(nodeId) {
  const active = highlightedIds(nodeId);
  const hasActive = active.nodes.size > 0;
  d3.selectAll(".graph-node").classed("is-dimmed", function () { return hasActive && !active.nodes.has(this.dataset.nodeId); })
    .classed("is-highlighted", function () { return active.nodes.has(this.dataset.nodeId); });
  d3.selectAll(".graph-edge").classed("is-dimmed", function () { return hasActive && !active.edges.has(this.dataset.edgeId); })
    .classed("is-highlighted", function () { return active.edges.has(this.dataset.edgeId); });
}

function applySelectionHighlight() {
  const nodeId = state.selection?.id;
  if (nodeId && graphLayout?.nodes.some((node) => node.id === nodeId)) highlightGraph(nodeId);
  else {
    d3.selectAll(".graph-node,.graph-edge").classed("is-dimmed", false).classed("is-highlighted", false);
  }
}

function selectGraphNode(node) {
  state.selection = { type: node.type, id: node.id };
  if (node.type === "family") {
    state.family = node.family_id;
    state.subtype = "";
    syncFilterControls();
    renderAll({ fitGraph: true });
    state.selection = { type: "family", id: node.id };
  } else if (node.type === "subtype") {
    state.family = node.family_id;
    state.subtype = node.subtype_id;
    syncFilterControls();
    renderAll({ fitGraph: true });
    state.selection = { type: "subtype", id: node.id };
  }
  renderInspector();
  applySelectionHighlight();
}

function evidenceProvenance(architecture) {
  const figure = architecture.figure;
  if (!figure) {
    return `<div class="evidence-absence"><i data-lucide="file-x-2"></i><div><strong>No suitable source figure</strong><p>${escapeHtml(architecture.no_figure_rationale)}</p></div></div>`;
  }
  const crop = figure.crop_box;
  return `<div class="inspector-evidence">
    <div class="evidence-heading"><span>Original-paper crop</span><em>${escapeHtml(figure.suitability)} · ${escapeHtml(figure.confidence)} confidence</em></div>
    ${cropMarkup(architecture, "detail")}
    <p class="crop-readout">Crop x=${crop.x.toFixed(3)}, y=${crop.y.toFixed(3)}, w=${crop.width.toFixed(3)}, h=${crop.height.toFixed(3)} · source pixels preserved</p>
    <p class="figure-caption">${escapeHtml(figure.caption)}</p>
    <dl class="provenance-grid">
      <div><dt>Figure</dt><dd>${figure.figure_index}${figure.panel_label ? ` · panel ${escapeHtml(figure.panel_label)}` : ""}</dd></div>
      <div><dt>Page</dt><dd>${figure.page_no ?? "n/a"}</dd></div>
      <div><dt>Visible input</dt><dd>${escapeHtml(figure.visible_input_object)}</dd></div>
      <div><dt>Interface</dt><dd>${escapeHtml(figure.visible_model_interface)}</dd></div>
      <div class="wide"><dt>Source SHA-256</dt><dd><code>${escapeHtml(figure.sha256)}</code></dd></div>
    </dl>
  </div>`;
}

function routeMarkup(route) {
  const family = familyMeta(route.carrier_family);
  const transforms = (route.transformation_chain_verbatim || []).length
    ? route.transformation_chain_verbatim.map((item) => escapeHtml(item)).join(" → ")
    : "No transformation stated";
  return `<article class="route-record" style="--family-color:${family.color}">
    <div class="route-record-head"><strong>${escapeHtml(route.route_label || route.task_or_configuration_verbatim)}</strong><span>${escapeHtml(route.evidence_status)}</span></div>
    <div class="route-flow">
      <div><span>Source object</span><p>${escapeHtml(route.source_object_verbatim)}</p></div>
      <i data-lucide="arrow-right"></i>
      <div><span>Transformation</span><p>${transforms}</p></div>
      <i data-lucide="arrow-right"></i>
      <div><span>Model-visible carrier</span><p>${escapeHtml(route.model_visible_form_verbatim)}</p></div>
    </div>
    <blockquote>“${escapeHtml(route.evidence_quote)}”</blockquote>
    <p class="route-provenance">${escapeHtml(route.section_heading)} · pages ${escapeHtml((route.pages || []).join(", ") || "n/a")} · ${escapeHtml(subtypeLabel(route.carrier_subtype))}</p>
  </article>`;
}

function modelInspector(architecture) {
  const familyChips = architecture.families.map((familyId) => {
    const family = familyMeta(familyId);
    return `<span class="family-chip" style="--family-color:${family.color}">${escapeHtml(family.code)} · ${escapeHtml(family.short)}</span>`;
  }).join("");
  return `<div class="inspector-scroll">
    <div class="inspector-title"><p class="section-kicker">Model node</p><h3>${escapeHtml(architecture.model_name)}</h3><p>${escapeHtml(architecture.paper_title)}</p></div>
    <div class="chip-row">${familyChips}</div>
    ${evidenceProvenance(architecture)}
    <section class="inspector-section"><div class="inspector-section-title"><h4>What the input can look like</h4><span>Explanatory examples</span></div>${exampleMarkup(architecture, "detail")}</section>
    <section class="inspector-section"><div class="inspector-section-title"><h4>Grounded routes</h4><span>${architecture.route_count} routes</span></div>${architecture.routes.map(routeMarkup).join("")}</section>
    <div class="paper-link-row">
      ${architecture.paper_url ? `<a href="${escapeHtml(architecture.paper_url)}" target="_blank" rel="noreferrer"><i data-lucide="external-link"></i>Open paper</a>` : ""}
      <span>${escapeHtml(architecture.record_id)}</span>
    </div>
  </div>`;
}

function renderInspector() {
  const inspector = $("#graph-inspector");
  const selection = state.selection || { type: "root", id: "taxonomy_root" };
  if (selection.type === "model") {
    const architecture = architectureById.get(selection.id.replace("model::", ""));
    inspector.innerHTML = architecture ? modelInspector(architecture) : rootInspector();
  } else if (selection.type === "family") {
    const family = familyById.get(selection.id.replace("family::", ""));
    inspector.innerHTML = familyInspector(family);
  } else if (selection.type === "subtype") {
    const subtype = subtypeById.get(selection.id.replace("subtype::", ""));
    inspector.innerHTML = subtypeInspector(subtype);
  } else {
    inspector.innerHTML = rootInspector();
  }
  refreshIcons();
}

function rootInspector() {
  return `<div class="inspector-scroll root-inspector">
    <p class="section-kicker">How to read the graph</p>
    <h3>Follow the carrier into the model</h3>
    <p>Each edge maps a grounded input route from the model-visible carrier family to a mechanism subtype and then to a single model identity.</p>
    <div class="reading-sequence"><span>Root</span><i data-lucide="arrow-right"></i><span>Family</span><i data-lucide="arrow-right"></i><span>Subtype</span><i data-lucide="arrow-right"></i><span>Model</span></div>
    <div class="inspector-family-list">${state.atlas.families.map((family) => `<button data-inspector-family="${escapeHtml(family.family_id)}" style="--family-color:${family.color}"><b>${escapeHtml(family.code)}</b><span>${escapeHtml(family.name)}</span><em>${family.model_count} models</em></button>`).join("")}</div>
    <div class="method-note"><i data-lucide="scan-line"></i><p><b>Evidence and explanation are separate.</b> Paper pixels appear under “Original-paper crop.” Small input strings or vectors are illustrative and never presented as source evidence.</p></div>
  </div>`;
}

function familyInspector(family) {
  if (!family) return rootInspector();
  return `<div class="inspector-scroll family-inspector" style="--family-color:${family.color}">
    <p class="section-kicker">${escapeHtml(family.code)} · Carrier family</p><h3>${escapeHtml(family.name)}</h3>
    <p>${escapeHtml(family.definition)}</p>
    <dl class="family-metrics"><div><dt>Routes</dt><dd>${family.route_count}</dd></div><div><dt>Models</dt><dd>${family.model_count}</dd></div><div><dt>Subtypes</dt><dd>${family.subtypes.length}</dd></div></dl>
    <div class="inspector-subtypes">${family.subtypes.map((subtype) => `<button data-inspector-subtype="${escapeHtml(subtype.subtype_id)}"><b>${escapeHtml(subtype.leaf_id)}</b><span>${escapeHtml(subtype.name)}</span><em>${subtype.model_count} models</em></button>`).join("")}</div>
  </div>`;
}

function subtypeInspector(subtype) {
  if (!subtype) return rootInspector();
  const family = familyMeta(subtype.family_id);
  const models = filteredArchitectures().filter((model) => model.subtypes.includes(subtype.subtype_id));
  return `<div class="inspector-scroll subtype-inspector" style="--family-color:${family.color}">
    <p class="section-kicker">${escapeHtml(subtype.leaf_id)} · ${escapeHtml(family.short)}</p><h3>${escapeHtml(subtype.name)}</h3>
    <p>${escapeHtml(subtype.definition)}</p>
    <div class="input-example standalone-example"><div class="example-label"><span>Mechanism example</span><em>Illustrative · not paper evidence</em></div><div class="example-flow"><code>${escapeHtml(subtype.example.input)}</code><i data-lucide="arrow-right"></i><code>${escapeHtml(subtype.example.carrier)}</code><i data-lucide="arrow-right"></i><strong>${escapeHtml(subtype.example.model)}</strong></div></div>
    <h4 class="model-list-title">${models.length} visible models</h4>
    <div class="inspector-model-list">${models.map((model) => `<button data-inspector-model="${escapeHtml(model.model_id)}"><span>${cropMarkup(model, "tiny")}</span><b>${escapeHtml(model.model_name)}</b><em>${model.route_count} routes</em></button>`).join("")}</div>
  </div>`;
}

function architectureCard(architecture) {
  const example = architecture.illustrative_examples[0];
  const family = familyMeta(example.family_id);
  return `<button class="architecture-card" type="button" data-open-model="${escapeHtml(architecture.model_id)}" style="--family-color:${family.color}">
    <div class="architecture-card-media"><div><span>Original-paper crop</span>${cropMarkup(architecture, "card")}</div><div class="card-example"><span>Illustrative input</span><code>${escapeHtml(shorten(example.example_input, 74))}</code><small>${escapeHtml(shorten(example.example_carrier, 74))}</small></div></div>
    <div class="architecture-card-body"><h3>${escapeHtml(architecture.model_name)}</h3><p>${escapeHtml(architecture.paper_title)}</p><div><span>${architecture.route_count} routes</span><span>${architecture.subtypes.length} subtypes</span><span>${architecture.figure ? `Fig. ${architecture.figure.figure_index}` : "Text evidence only"}</span></div></div>
  </button>`;
}

function renderArchitectures() {
  const architectures = filteredArchitectures();
  $("#architecture-result-count").textContent = `${architectures.length} of ${state.atlas.meta.model_count} models`;
  $("#architecture-grid").innerHTML = architectures.map(architectureCard).join("");
  $("#architecture-empty").hidden = architectures.length > 0;
}

function renderEvidence() {
  const rows = filteredRoutes();
  const pages = Math.max(1, Math.ceil(rows.length / state.evidencePageSize));
  state.evidencePage = Math.min(state.evidencePage, pages);
  const start = (state.evidencePage - 1) * state.evidencePageSize;
  const visible = rows.slice(start, start + state.evidencePageSize);
  $("#evidence-result-count").textContent = `${rows.length} grounded routes`;
  $("#evidence-rows").innerHTML = visible.map(({ architecture, route }) => {
    const family = familyMeta(route.carrier_family);
    return `<tr>
      <td><button class="table-model-link" data-open-model="${escapeHtml(architecture.model_id)}">${escapeHtml(architecture.model_name)}</button><small>${escapeHtml(architecture.paper_title)}</small></td>
      <td><b>${escapeHtml(route.source_object_verbatim)}</b><i data-lucide="arrow-right"></i><span>${escapeHtml(route.model_visible_form_verbatim)}</span></td>
      <td><span class="table-family" style="--family-color:${family.color}">${escapeHtml(family.code)}</span><small>${escapeHtml(subtypeLabel(route.carrier_subtype))}</small></td>
      <td><blockquote>“${escapeHtml(route.evidence_quote)}”</blockquote><small>${escapeHtml(route.section_heading)} · pages ${escapeHtml((route.pages || []).join(", ") || "n/a")}</small></td>
    </tr>`;
  }).join("");
  $("#evidence-pagination").innerHTML = pages > 1 ? `<button type="button" data-page="${state.evidencePage - 1}" ${state.evidencePage === 1 ? "disabled" : ""}><i data-lucide="chevron-left"></i>Previous</button><span>Page ${state.evidencePage} of ${pages}</span><button type="button" data-page="${state.evidencePage + 1}" ${state.evidencePage === pages ? "disabled" : ""}>Next<i data-lucide="chevron-right"></i></button>` : "";
}

function renderAll({ fitGraph: shouldFit = false } = {}) {
  renderGraph({ fit: shouldFit });
  renderArchitectures();
  renderEvidence();
  renderInspector();
  refreshIcons();
}

function setView(view) {
  state.view = view;
  $$(".view-tab").forEach((button) => {
    const active = button.dataset.view === view;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", String(active));
  });
  $$(".view-panel").forEach((panel) => panel.classList.toggle("is-active", panel.id === `view-${view}`));
  if (view === "graph") requestAnimationFrame(() => fitGraph());
}

function clearFilters() {
  state.query = "";
  state.family = "";
  state.subtype = "";
  state.lifecycle = "";
  state.modality = "";
  state.selection = { type: "root", id: "taxonomy_root" };
  state.evidencePage = 1;
  syncFilterControls();
  renderAll({ fitGraph: true });
}

function openModel(modelId) {
  const architecture = architectureById.get(modelId);
  if (!architecture) return;
  state.selection = { type: "model", id: `model::${modelId}` };
  setView("graph");
  renderInspector();
  applySelectionHighlight();
}

function bindEvents() {
  $$(".view-tab").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
  $("#search-input").addEventListener("input", (event) => {
    state.query = event.target.value.trim();
    state.evidencePage = 1;
    state.selection = { type: "root", id: "taxonomy_root" };
    renderAll({ fitGraph: true });
  });
  $("#family-filter").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-family]");
    if (!button) return;
    state.family = button.dataset.family;
    if (state.subtype && subtypeById.get(state.subtype)?.family_id !== state.family) state.subtype = "";
    state.selection = state.family ? { type: "family", id: `family::${state.family}` } : { type: "root", id: "taxonomy_root" };
    state.evidencePage = 1;
    syncFilterControls();
    renderAll({ fitGraph: true });
  });
  $("#subtype-filter").addEventListener("change", (event) => {
    state.subtype = event.target.value;
    if (state.subtype) state.family = subtypeById.get(state.subtype).family_id;
    state.selection = state.subtype ? { type: "subtype", id: `subtype::${state.subtype}` } : state.family ? { type: "family", id: `family::${state.family}` } : { type: "root", id: "taxonomy_root" };
    state.evidencePage = 1;
    syncFilterControls();
    renderAll({ fitGraph: true });
  });
  $("#lifecycle-filter").addEventListener("change", (event) => { state.lifecycle = event.target.value; state.evidencePage = 1; renderAll({ fitGraph: true }); });
  $("#modality-filter").addEventListener("change", (event) => { state.modality = event.target.value; state.evidencePage = 1; renderAll({ fitGraph: true }); });
  $("#clear-filters").addEventListener("click", clearFilters);
  $("#show-all").addEventListener("click", clearFilters);
  $("#fit-graph").addEventListener("click", fitGraph);
  $("#zoom-in").addEventListener("click", () => zoomBy(1.3));
  $("#zoom-out").addEventListener("click", () => zoomBy(1 / 1.3));

  document.addEventListener("click", (event) => {
    const modelButton = event.target.closest("[data-open-model],[data-inspector-model]");
    if (modelButton) openModel(modelButton.dataset.openModel || modelButton.dataset.inspectorModel);
    const familyButton = event.target.closest("[data-inspector-family]");
    if (familyButton) {
      state.family = familyButton.dataset.inspectorFamily;
      state.subtype = "";
      state.selection = { type: "family", id: `family::${state.family}` };
      syncFilterControls();
      renderAll({ fitGraph: true });
    }
    const subtypeButton = event.target.closest("[data-inspector-subtype]");
    if (subtypeButton) {
      state.subtype = subtypeButton.dataset.inspectorSubtype;
      state.family = subtypeById.get(state.subtype).family_id;
      state.selection = { type: "subtype", id: `subtype::${state.subtype}` };
      syncFilterControls();
      renderAll({ fitGraph: true });
    }
    const pageButton = event.target.closest("[data-page]");
    if (pageButton && !pageButton.disabled) { state.evidencePage = Number(pageButton.dataset.page); renderEvidence(); refreshIcons(); }
  });
  window.addEventListener("resize", () => { if (state.view === "graph") fitGraph(); });
}

async function initialize() {
  try {
    const response = await fetch("data/atlas.json");
    if (!response.ok) throw new Error(`Atlas data request failed: ${response.status}`);
    state.atlas = await response.json();
    state.atlas.families.forEach((family) => {
      familyById.set(family.family_id, family);
      family.subtypes.forEach((subtype) => subtypeById.set(subtype.subtype_id, { ...subtype, family_id: family.family_id }));
    });
    state.atlas.architectures.forEach((architecture) => architectureById.set(architecture.model_id, architecture));
    state.atlas.graph.nodes.forEach((node) => graphNodeById.set(node.id, node));
    populateHeader();
    populateFilters();
    bindEvents();
    renderAll({ fitGraph: true });
    $("#loading-screen").classList.add("is-hidden");
  } catch (error) {
    $("#loading-screen").innerHTML = `<p>Could not load the atlas.</p><pre>${escapeHtml(error.message)}</pre>`;
  }
}

window.addEventListener("DOMContentLoaded", initialize);
