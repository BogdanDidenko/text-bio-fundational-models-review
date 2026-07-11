const state = {
  atlas: null,
  view: "overview",
  query: "",
  family: "",
  subtype: "",
  lifecycle: "",
  modality: "",
  evidencePage: 1,
  evidencePageSize: 50,
};

const familyById = new Map();
const architectureById = new Map();

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

function textList(values, empty = "Not stated") {
  const clean = [...new Set((values || []).filter(Boolean))];
  return clean.length ? clean.map(escapeHtml).join(", ") : empty;
}

function familyStyle(familyId) {
  const family = familyById.get(familyId);
  return `--family-color:${family?.color || "#66717a"}`;
}

function familyLabel(familyId) {
  return familyById.get(familyId)?.name || familyById.get(familyId)?.label || familyId;
}

function refreshIcons() {
  if (window.lucide) window.lucide.createIcons({ attrs: { "aria-hidden": "true" } });
}

function populateHeader() {
  const meta = state.atlas.meta;
  const stats = [
    [meta.model_count, "models"],
    [meta.route_count, "input routes"],
    [meta.configuration_count, "configurations"],
    [meta.source_figure_count, "source figures"],
  ];
  $("#header-stats").innerHTML = stats
    .map(([value, label]) => `<div class="stat-block"><strong>${value}</strong><span>${label}</span></div>`)
    .join("");
  $("#organizing-principle").textContent = meta.organizing_principle;
}

function populateFilters() {
  const allButton = `<button type="button" class="is-active" data-family="" style="--family-color:#172026" title="All carrier families">All</button>`;
  const familyButtons = state.atlas.families
    .map(
      (family) =>
        `<button type="button" data-family="${escapeHtml(family.family_id)}" style="--family-color:${family.color}" title="${escapeHtml(family.name)}">${escapeHtml(family.code)}</button>`,
    )
    .join("");
  $("#family-filter").innerHTML = allButton + familyButtons;

  const subtypeOptions = state.atlas.families.flatMap((family) =>
    family.subtypes.map(
      (subtype) =>
        `<option value="${escapeHtml(subtype.subtype_id)}">${escapeHtml(subtype.leaf_id)} · ${escapeHtml(subtype.name)}</option>`,
    ),
  );
  $("#subtype-filter").insertAdjacentHTML("beforeend", subtypeOptions.join(""));
  $("#lifecycle-filter").insertAdjacentHTML(
    "beforeend",
    state.atlas.filter_values.lifecycle_phases
      .map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value.replaceAll("_", " "))}</option>`)
      .join(""),
  );
  $("#modality-filter").insertAdjacentHTML(
    "beforeend",
    state.atlas.filter_values.modalities
      .map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`)
      .join(""),
  );
}

function architectureMatches(architecture, forcedFamily = "") {
  const family = forcedFamily || state.family;
  if (family && !architecture.families.includes(family)) return false;
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
    ...architecture.fusion_topologies,
    ...architecture.routes.flatMap((route) => [
      route.route_label,
      route.source_object_verbatim,
      route.model_visible_form_verbatim,
      route.evidence_quote,
      route.section_heading,
    ]),
  ]
    .join(" ")
    .toLocaleLowerCase();
  return haystack.includes(query);
}

function filteredArchitectures() {
  return state.atlas.architectures.filter((architecture) => architectureMatches(architecture));
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

function renderFamilies() {
  $("#family-grid").innerHTML = state.atlas.families
    .map(
      (family) => `
        <article class="family-column" style="--family-color:${family.color}">
          <div class="family-title-row">
            <h3>${escapeHtml(family.name)}</h3>
            <span class="family-code">${escapeHtml(family.code)}</span>
          </div>
          <p class="family-definition">${escapeHtml(family.definition)}</p>
          <div class="family-counts">
            <span><strong>${family.route_count}</strong><br>routes</span>
            <span><strong>${family.model_count}</strong><br>models</span>
          </div>
          <div class="subtype-links">
            ${family.subtypes
              .map(
                (subtype) => `
                  <button type="button" class="subtype-link" data-subtype="${escapeHtml(subtype.subtype_id)}" data-family="${escapeHtml(family.family_id)}">
                    <span class="leaf-code">${escapeHtml(subtype.leaf_id)}</span>
                    <span>${escapeHtml(subtype.name)}</span>
                    <span class="leaf-count">${subtype.route_count}</span>
                  </button>`,
              )
              .join("")}
          </div>
        </article>`,
    )
    .join("");
}

function renderArchitectureMap() {
  $("#architecture-map").innerHTML = state.atlas.families
    .map((family) => {
      const models = state.atlas.architectures.filter((architecture) => architectureMatches(architecture, family.family_id));
      return `
        <section class="map-lane" style="--family-color:${family.color}">
          <div class="lane-label">
            <strong>${escapeHtml(family.code)} · ${escapeHtml(family.short)}</strong>
            <span>${models.length} visible models · ${family.route_count} total routes</span>
          </div>
          <div class="lane-models">
            ${models
              .map(
                (architecture) => `
                  <button type="button" class="model-node" data-model-id="${escapeHtml(architecture.model_id)}" title="${escapeHtml(architecture.model_name)} · ${architecture.family_counts[family.family_id] || 0} ${family.code} routes">
                    ${escapeHtml(architecture.model_name)} · ${architecture.family_counts[family.family_id] || 0}
                  </button>`,
              )
              .join("") || `<span class="cell-muted">No model under current filters</span>`}
          </div>
        </section>`;
    })
    .join("");
}

function renderExamples() {
  const families = state.atlas.families.filter((family) => !state.family || family.family_id === state.family);
  const rows = families.flatMap((family) =>
    family.subtypes
      .filter((subtype) => !state.subtype || subtype.subtype_id === state.subtype)
      .map(
        (subtype) => `
          <article class="example-row" id="example-${escapeHtml(subtype.subtype_id)}" style="--family-color:${family.color}">
            <div class="example-name">
              <strong>${escapeHtml(subtype.name)}</strong>
              <span>${escapeHtml(subtype.leaf_id)} · ${subtype.route_count} routes</span>
            </div>
            <div class="example-stage"><label>Source object</label><code>${escapeHtml(subtype.example.input)}</code></div>
            <div class="example-arrow" aria-hidden="true">→</div>
            <div class="example-stage"><label>Model-visible carrier</label><code>${escapeHtml(subtype.example.carrier)}</code></div>
            <div class="example-arrow" aria-hidden="true">→</div>
            <div class="example-stage"><label>Interface</label><code>${escapeHtml(subtype.example.model)}</code></div>
          </article>`,
      ),
  );
  $("#example-list").innerHTML = rows.join("");
}

function familyTags(architecture) {
  return architecture.families
    .map((familyId) => {
      const family = familyById.get(familyId);
      return `<span class="family-tag" style="--family-color:${family.color}">${family.code} · ${architecture.family_counts[familyId]}</span>`;
    })
    .join("");
}

function architectureCard(architecture) {
  const primaryFamily = familyById.get(architecture.families[0]);
  const figureDescription = architecture.figure.description || architecture.figure.caption || architecture.model_name;
  return `
    <article class="architecture-card" style="--primary-family:${primaryFamily.color}">
      <button type="button" class="card-figure" data-model-id="${escapeHtml(architecture.model_id)}" aria-label="Open ${escapeHtml(architecture.model_name)} details">
        <img src="${escapeHtml(architecture.figure.asset)}" alt="${escapeHtml(figureDescription.split("\n").filter(Boolean).slice(0, 2).join(" ").slice(0, 220))}" loading="lazy">
        <span class="figure-index">Fig. ${architecture.figure.figure_index} · p. ${architecture.figure.page_no ?? "?"}</span>
      </button>
      <div class="card-content">
        <h3>${escapeHtml(architecture.model_name)}</h3>
        <p class="paper-title">${escapeHtml(architecture.paper_title)}</p>
        <div class="tag-row">
          ${familyTags(architecture)}
          <span class="meta-tag">${architecture.route_count} routes</span>
          <span class="meta-tag">${architecture.configuration_count} configs</span>
        </div>
        <ul class="card-route-preview">
          ${architecture.routes
            .slice(0, 3)
            .map(
              (route) => `
                <li style="--family-color:${familyById.get(route.carrier_family).color}">
                  <span class="route-dot"></span><span>${escapeHtml(route.source_object_verbatim)} → ${escapeHtml(route.model_visible_form_verbatim)}</span>
                </li>`,
            )
            .join("")}
        </ul>
        <button type="button" class="inspect-button" data-model-id="${escapeHtml(architecture.model_id)}">
          <span>Inspect grounded routes</span><i data-lucide="arrow-right" aria-hidden="true"></i>
        </button>
      </div>
    </article>`;
}

function renderArchitectures() {
  const architectures = filteredArchitectures();
  $("#architecture-result-count").textContent = `${architectures.length} of ${state.atlas.meta.model_count} models`;
  $("#architecture-grid").innerHTML = architectures.map(architectureCard).join("");
  $("#architecture-empty").hidden = architectures.length > 0;
  refreshIcons();
}

function routeChain(route) {
  const transforms = (route.transformation_chain_verbatim || []).slice(0, 3);
  const nodes = [
    `<span class="chain-node">${escapeHtml(route.source_object_verbatim)}</span>`,
    ...transforms.flatMap((item) => [
      `<span class="chain-arrow">→</span>`,
      `<span class="chain-node">${escapeHtml(item)}</span>`,
    ]),
    `<span class="chain-arrow">→</span>`,
    `<span class="chain-node">${escapeHtml(route.model_visible_form_verbatim)}</span>`,
  ];
  return nodes.join("");
}

function renderEvidence() {
  const rows = filteredRoutes();
  const pageCount = Math.max(1, Math.ceil(rows.length / state.evidencePageSize));
  state.evidencePage = Math.min(state.evidencePage, pageCount);
  const start = (state.evidencePage - 1) * state.evidencePageSize;
  const pageRows = rows.slice(start, start + state.evidencePageSize);
  $("#evidence-result-count").textContent = `${rows.length} of ${state.atlas.meta.route_count} routes`;
  $("#evidence-rows").innerHTML = pageRows
    .map(({ architecture, route }) => {
      const family = familyById.get(route.carrier_family);
      const subtype = family.subtypes.find((item) => item.subtype_id === route.carrier_subtype);
      return `
        <tr style="--family-color:${family.color}">
          <td>
            <button type="button" class="model-link" data-model-id="${escapeHtml(architecture.model_id)}">${escapeHtml(architecture.model_name)}</button>
            <span class="cell-muted">${escapeHtml(route.lifecycle_phase)} · ${escapeHtml(route.route_id)}</span>
          </td>
          <td><div class="route-chain">${routeChain(route)}</div></td>
          <td>
            <span class="family-tag" style="--family-color:${family.color}">${family.code}</span>
            ${escapeHtml(subtype?.name || route.carrier_subtype)}
            <span class="cell-muted">${escapeHtml(route.fusion_topology)} · ${escapeHtml(route.text_role)}</span>
          </td>
          <td>
            <blockquote class="evidence-quote">${escapeHtml(route.evidence_quote)}</blockquote>
            <span class="cell-muted">${escapeHtml(route.section_heading || "Heading unavailable")} · pp. ${escapeHtml((route.pages || []).join(", ") || "?")}</span>
          </td>
        </tr>`;
    })
    .join("");
  $("#evidence-pagination").innerHTML = `
    <button type="button" class="page-button" data-page="prev" ${state.evidencePage === 1 ? "disabled" : ""}>
      <i data-lucide="arrow-left" aria-hidden="true"></i><span>Previous</span>
    </button>
    <span class="page-status">Page ${state.evidencePage} of ${pageCount} · rows ${rows.length ? start + 1 : 0}–${Math.min(start + state.evidencePageSize, rows.length)}</span>
    <button type="button" class="page-button" data-page="next" ${state.evidencePage === pageCount ? "disabled" : ""}>
      <span>Next</span><i data-lucide="arrow-right" aria-hidden="true"></i>
    </button>`;
  refreshIcons();
}

function subtypeName(familyId, subtypeId) {
  return familyById.get(familyId)?.subtypes.find((item) => item.subtype_id === subtypeId)?.name || subtypeId;
}

function routeDetail(route, index) {
  const family = familyById.get(route.carrier_family);
  return `
    <details class="route-detail" style="--family-color:${family.color}" ${index === 0 ? "open" : ""}>
      <summary>
        <div><strong>${escapeHtml(route.route_label)}</strong><span>${escapeHtml(route.task_or_configuration_verbatim)}</span></div>
        <div class="tag-row">
          <span class="family-tag" style="--family-color:${family.color}">${family.code}</span>
          <span class="meta-tag">${escapeHtml(route.lifecycle_phase)}</span>
        </div>
      </summary>
      <div class="route-detail-content">
        <div class="route-pipeline">
          <div class="pipeline-stage"><label>Source object</label><p>${escapeHtml(route.source_object_verbatim)}</p><p class="cell-muted">${escapeHtml(route.source_modality_normalized)}</p></div>
          <div class="pipeline-arrow" aria-hidden="true">→</div>
          <div class="pipeline-stage"><label>Transformation chain</label><ol>${(route.transformation_chain_verbatim || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("") || "<li>Not explicitly stated</li>"}</ol></div>
          <div class="pipeline-arrow" aria-hidden="true">→</div>
          <div class="pipeline-stage"><label>Model-visible carrier</label><p>${escapeHtml(route.model_visible_form_verbatim)}</p><p class="cell-muted">${escapeHtml(subtypeName(route.carrier_family, route.carrier_subtype))}</p></div>
        </div>
        <div class="grounding-block">
          <blockquote>${escapeHtml(route.evidence_quote)}</blockquote>
          <div class="grounding-meta">
            <strong>${escapeHtml(route.section_heading || "Heading unavailable")}</strong><br>
            Pages: ${escapeHtml((route.pages || []).join(", ") || "not mapped")}<br>
            Fusion: ${escapeHtml(route.fusion_topology)}<br>
            Text role: ${escapeHtml(route.text_role)}<br>
            Docling refs: ${escapeHtml((route.doc_item_refs || []).join(", "))}
          </div>
        </div>
      </div>
    </details>`;
}

function openArchitecture(modelId, updateHash = true) {
  const architecture = architectureById.get(modelId);
  if (!architecture) return;
  const dialog = $("#architecture-dialog");
  $("#dialog-title").textContent = architecture.model_name;
  $("#dialog-kicker").textContent = `${architecture.route_count} grounded routes · ${architecture.configuration_count} configurations`;
  const paperLink = architecture.paper_url
    ? `<a class="paper-link" href="${escapeHtml(architecture.paper_url)}" target="_blank" rel="noreferrer">Open source paper <i data-lucide="external-link" aria-hidden="true"></i></a>`
    : `<span class="cell-muted">DOI unavailable in the screening record</span>`;
  $("#dialog-body").innerHTML = `
    <div class="dialog-overview">
      <figure class="source-figure">
        <a href="${escapeHtml(architecture.figure.asset)}" target="_blank" title="Open original figure image">
          <img src="${escapeHtml(architecture.figure.asset)}" alt="${escapeHtml((architecture.figure.description || architecture.figure.caption).slice(0, 260))}">
        </a>
        <figcaption><strong>Original paper figure ${architecture.figure.figure_index}, page ${architecture.figure.page_no ?? "?"}.</strong> ${escapeHtml(architecture.figure.caption)}</figcaption>
        <div class="figure-provenance"><span>SHA-256 ${architecture.figure.sha256.slice(0, 16)}…</span><span>Docling corpus asset</span></div>
      </figure>
      <section class="architecture-summary">
        <p class="section-kicker">Source study</p>
        <h3>${escapeHtml(architecture.paper_title)}</h3>
        ${paperLink}
        <div class="tag-row" style="margin-top:16px">${familyTags(architecture)}</div>
        <div class="summary-grid">
          <div class="summary-item"><label>Source modalities</label><div>${textList(architecture.modalities)}</div></div>
          <div class="summary-item"><label>Lifecycle phases</label><div>${textList(architecture.lifecycle_phases)}</div></div>
          <div class="summary-item"><label>Fusion topologies</label><div>${textList(architecture.fusion_topologies)}</div></div>
          <div class="summary-item"><label>Text roles</label><div>${textList(architecture.text_roles)}</div></div>
          <div class="summary-item"><label>Record</label><div>${escapeHtml(architecture.record_id)}</div></div>
          <div class="summary-item"><label>Figure selection provenance</label><div>${textList(architecture.figure.selection_reasons)}</div></div>
        </div>
        <details style="margin-top:16px">
          <summary class="model-link">VLM description of the source figure</summary>
          <p class="section-note" style="margin-top:8px;white-space:pre-line">${escapeHtml(architecture.figure.description || "No VLM description available.")}</p>
        </details>
      </section>
    </div>
    <section class="routes-section">
      <div class="routes-toolbar"><h3>Input routes</h3><span class="result-count">${architecture.route_count} routes · all provenance-verified</span></div>
      <div class="route-detail-list">${architecture.routes.map(routeDetail).join("")}</div>
    </section>`;
  if (!dialog.open) dialog.showModal();
  dialog.scrollTop = 0;
  refreshIcons();
  if (updateHash) history.replaceState(null, "", `#model=${encodeURIComponent(modelId)}`);
}

function closeArchitecture(updateHash = true) {
  const dialog = $("#architecture-dialog");
  if (dialog.open) dialog.close();
  if (updateHash && location.hash.startsWith("#model=")) history.replaceState(null, "", location.pathname + location.search);
}

function setView(view) {
  state.view = view;
  $$(".view-tab").forEach((button) => {
    const active = button.dataset.view === view;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", String(active));
  });
  $$(".view-panel").forEach((panel) => panel.classList.toggle("is-active", panel.id === `view-${view}`));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function syncFilterUi() {
  $$("#family-filter button").forEach((button) => button.classList.toggle("is-active", button.dataset.family === state.family));
  $("#subtype-filter").value = state.subtype;
  $("#lifecycle-filter").value = state.lifecycle;
  $("#modality-filter").value = state.modality;
  $("#search-input").value = state.query;
}

function renderFilteredViews() {
  state.evidencePage = 1;
  renderArchitectureMap();
  renderExamples();
  renderArchitectures();
  renderEvidence();
}

function clearFilters() {
  Object.assign(state, { query: "", family: "", subtype: "", lifecycle: "", modality: "", evidencePage: 1 });
  syncFilterUi();
  renderFilteredViews();
}

function bindEvents() {
  $$(".view-tab").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
  $("#search-input").addEventListener("input", (event) => {
    state.query = event.target.value.trim().toLocaleLowerCase();
    renderFilteredViews();
  });
  $("#family-filter").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-family]");
    if (!button) return;
    state.family = button.dataset.family;
    if (state.subtype) {
      const valid = familyById.get(state.family)?.subtypes.some((item) => item.subtype_id === state.subtype);
      if (state.family && !valid) state.subtype = "";
    }
    syncFilterUi();
    renderFilteredViews();
  });
  $("#subtype-filter").addEventListener("change", (event) => {
    state.subtype = event.target.value;
    if (state.subtype) {
      const family = state.atlas.families.find((item) => item.subtypes.some((subtype) => subtype.subtype_id === state.subtype));
      state.family = family?.family_id || state.family;
    }
    syncFilterUi();
    renderFilteredViews();
  });
  $("#lifecycle-filter").addEventListener("change", (event) => {
    state.lifecycle = event.target.value;
    renderFilteredViews();
  });
  $("#modality-filter").addEventListener("change", (event) => {
    state.modality = event.target.value;
    renderFilteredViews();
  });
  $("#clear-filters").addEventListener("click", clearFilters);
  $("#family-grid").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-subtype]");
    if (!button) return;
    state.family = button.dataset.family;
    state.subtype = button.dataset.subtype;
    syncFilterUi();
    renderFilteredViews();
    document.getElementById(`example-${state.subtype}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
  });
  document.body.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-model-id]");
    if (trigger) openArchitecture(trigger.dataset.modelId);
  });
  $("#evidence-pagination").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-page]");
    if (!button || button.disabled) return;
    state.evidencePage += button.dataset.page === "next" ? 1 : -1;
    renderEvidence();
    $("#view-evidence").scrollIntoView({ behavior: "smooth" });
  });
  $(".dialog-close").addEventListener("click", () => closeArchitecture());
  $("#architecture-dialog").addEventListener("click", (event) => {
    if (event.target === event.currentTarget) closeArchitecture();
  });
  $("#architecture-dialog").addEventListener("close", () => {
    if (location.hash.startsWith("#model=")) history.replaceState(null, "", location.pathname + location.search);
  });
}

async function init() {
  try {
    const response = await fetch("data/atlas.json");
    if (!response.ok) throw new Error(`Atlas request failed: ${response.status}`);
    state.atlas = await response.json();
    state.atlas.families.forEach((family) => familyById.set(family.family_id, family));
    state.atlas.architectures.forEach((architecture) => architectureById.set(architecture.model_id, architecture));
    populateHeader();
    populateFilters();
    renderFamilies();
    renderArchitectureMap();
    renderExamples();
    renderArchitectures();
    renderEvidence();
    bindEvents();
    refreshIcons();
    const hashMatch = location.hash.match(/^#model=(.+)$/);
    if (hashMatch) openArchitecture(decodeURIComponent(hashMatch[1]), false);
    $("#loading-screen").classList.add("is-hidden");
  } catch (error) {
    console.error(error);
    $("#loading-screen").innerHTML = `<p>Atlas data could not be loaded.</p><code>${escapeHtml(error.message)}</code>`;
  }
}

document.addEventListener("DOMContentLoaded", init);
