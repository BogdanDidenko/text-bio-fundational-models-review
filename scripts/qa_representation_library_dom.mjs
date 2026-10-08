// Browser-free QA of the component library with jsdom (no layout engine: overlap/overflow geometry is out of scope;
// use qa_representation_library.mjs with Playwright + Chrome for those). Needs: npm install jsdom.
// Usage: node scripts/qa_representation_library_dom.mjs [page URL] [component-library dir]
// Mirrors the functional assertions of scripts/qa_representation_library.mjs and adds 1.1.0 checks.
import fs from "node:fs";
import path from "node:path";
import { JSDOM } from "jsdom";

const BASE = process.argv[2] || "https://bogdandidenko.github.io/text-bio-fundational-models-review/component-library/";
const SRC = path.resolve(process.argv[3] || new URL("../docs/input-representation-atlas/component-library", import.meta.url).pathname);
const results = [];
const check = (name, ok, detail = "") => results.push({ name, ok: Boolean(ok), detail: String(detail) });

// Bytes served from SRC, which was verified SHA-256-identical to the live site for every page file.
const atlasRoot = path.dirname(SRC);
const fetch = async (url) => {
  const rel = decodeURIComponent(new URL(url).pathname.replace(/^\/text-bio-fundational-models-review\//, ""));
  const file = path.join(atlasRoot, rel.endsWith("/") ? rel + "index.html" : rel);
  const body = fs.readFileSync(file);
  return { ok: true, status: 200, text: async () => body.toString("utf8"), json: async () => JSON.parse(body.toString("utf8")) };
};
const html = await (await fetch(BASE)).text();
const dom = new JSDOM(html, { url: BASE, runScripts: "outside-only", pretendToBeVisual: true });
const { window } = dom;
const errors = [];
window.addEventListener("error", (e) => errors.push(e.message));
window.fetch = (url, opts) => fetch(new URL(url, BASE).href, opts);
window.eval(await (await fetch(new URL("vendor/dagre-1.1.5.min.js", BASE))).text());
const paths = await import(`${SRC}/input-paths.mjs`);
const diagram = await import(`${SRC}/diagram-view.mjs`);
window.__paths = paths; window.__diagram = diagram;
globalThis.dagre = window.dagre; globalThis.document = window.document; globalThis.window = window;
for (const k of ["SVGElement", "Element", "HTMLElement", "Node", "getComputedStyle", "requestAnimationFrame"]) if (!(k in globalThis) && window[k]) globalThis[k] = window[k];
let source = await (await fetch(new URL("library.js", BASE))).text();
source = source.replace('import("./input-paths.mjs")', "Promise.resolve(window.__paths)")
               .replace('import("./diagram-view.mjs")', "Promise.resolve(window.__diagram)");
const started = Date.now();
window.eval(source);

const $ = (sel) => window.document.querySelector(sel);
const $$ = (sel) => [...window.document.querySelectorAll(sel)];
const until = async (fn, ms = 120000) => { const t = Date.now(); while (Date.now() - t < ms) { if (fn()) return true; await new Promise((r) => setTimeout(r, 100)); } return false; };
const click = (el) => el.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
const change = (el, value) => { el.value = value; el.dispatchEvent(new window.Event("change", { bubbles: true })); };

check("page loads catalog", await until(() => $$(".list-entry").length > 0), `${((Date.now() - started) / 1000).toFixed(1)} s incl. data download`);
const catalog = await (await fetch(new URL("data/catalog.json", BASE))).json();
check("no 'Library unavailable' error", !$("#detail .error"), $("#detail .error")?.textContent || "");
check("header shows release 1.1.0", $("#release").textContent.includes("1.1.0"), $("#release").textContent);
check("totals text", $("#totals").textContent.includes("22 operations"), $("#totals").textContent);
check("operation list complete (22)", $$(".list-entry").length === catalog.blocks.length, $$(".list-entry").length);
check("default view is Table lookup", $("#detail h2").textContent.includes("lookup"), $("#detail h2").textContent);
check("lookup lists key_space parameter", $("#detail").textContent.includes("key_space"), "");
check("no 'pilot papers' wording", !window.document.body.textContent.includes("pilot papers"), "");
change($("#reuse"), "shared");
check(`shared filter = report (${catalog.report.cross_paper_reused_types})`, $$(".list-entry").length === catalog.report.cross_paper_reused_types, $$(".list-entry").length);
$("#search").value = "projection"; $("#search").dispatchEvent(new window.Event("input", { bubbles: true }));
check("search works", $$(".list-entry").length > 0, $$(".list-entry").length);
click($('[data-view="blocks"]'));
change($("#paper"), "full_2026-07-06__rec_001319");
check("InstructCell exact evidence quote", ($("#detail .quote")?.textContent || "").length > 0, "");
click($("#detail [data-assembly]"));
check("InstructCell has 4 contexts", $$("#context-select option").length === 4, $$("#context-select option").length);
click($('[data-view="blocks"]')); click($('[data-select="bin"]')); click($('[data-supplement="bin"]'));
check("supplement shows WITHDRAWN", $("#detail").textContent.includes("WITHDRAWN"), "");
check("binning/lookup branches: 7 operations", $$("#full-graph .graph-operation").length === 7, $$("#full-graph .graph-operation").length);
click($('[data-view="proposals"]'));
check("unexpanded boundaries listed", $$(".list-entry").length > 0, $$(".list-entry").length);
click($('[data-view="assemblies"]'));
const papers = Object.keys(catalog.records).length;
check(`model chains list all ${papers} papers`, $$(".list-entry").length === papers, $$(".list-entry").length);
click($('[data-select="full_2026-07-06__rec_003517"]'));
check("X-Cell starts at measured expression", $("#path-source")?.value === "control_pool", $("#path-source")?.value);
check("X-Cell full graph collapsed by default", $("#full-graph")?.getAttribute("open") === null, "");
check("X-Cell expression branches kept parallel", $$("#focused-path .parallel-band").length > 0, "");
check("X-Cell no prior-path leak", $$('#focused-path [data-source-step="esm_lookup"]').length === 0, "");
check("X-Cell diagram drawn", $$("#path-diagram svg").length > 0 || $$("#path-diagram [data-diagram-node]").length > 0, $$("#path-diagram [data-diagram-node]").length + " nodes");
for (const branch of ["identity_encoder", "value_encoder", "mask_encoder"])
  check(`X-Cell merge edge ${branch}`, $$(`#path-diagram .dependency-arrow[data-from="step:${branch}"][data-to="step:combine_tokens"]`).length > 0, "");
check("X-Cell (pilot) has no candidate panel", !$(".review-panel"), "");
check("X-Cell complete graph = 46 operations", $$("#full-graph .graph-operation").length === 46, $$("#full-graph .graph-operation").length);

const agent = Object.entries(catalog.records).filter(([, v]) => v.decomposition_status);
let panels = 0, findingsShown = 0, diagrams = 0, mismatches = [];
for (const [id, meta] of agent) {
  click($(`[data-select="${id}"]`));
  const panel = $(".review-panel");
  if (panel) panels++;
  const contexts = $$("#context-select option").map((o) => o.value);
  let cards = 0;
  for (const ctx of contexts) {
    change($("#context-select"), ctx);
    const own = (meta.open_findings || []).filter((f) => f.trajectory_id === ctx || !contexts.includes(f.trajectory_id)).length;
    const shown = $$(".review-panel article").length;
    if (shown !== own) mismatches.push(`${id}/${ctx}: shown ${shown} vs data ${own}`);
    cards += shown;
    if ($$("#path-diagram [data-diagram-node]").length || $$("#path-diagram svg").length) diagrams++;
  }
  const ownOnly = (meta.open_findings || []).filter((f) => contexts.includes(f.trajectory_id)).length;
  const paperOnly = (meta.open_findings || []).filter((f) => !contexts.includes(f.trajectory_id)).length;
  findingsShown += ownOnly + (paperOnly && $$(".review-panel .paper-level").length ? paperOnly : 0);
}
const totalFindings = agent.reduce((n, [, v]) => n + (v.open_findings || []).length, 0);
check(`candidate panel on all ${agent.length} agent papers`, panels === agent.length, panels);
check("findings shown per path = data", mismatches.length === 0, mismatches.slice(0, 3).join("; "));
check("findings shown match total", findingsShown === totalFindings, `${findingsShown}/${totalFindings}`);
check("diagram rendered for agent paper contexts", diagrams > 0, `${diagrams} contexts with a diagram`);
check("no script errors", errors.length === 0, errors.slice(0, 3).join(" | "));
fs.writeFileSync(process.env.QA_REPORT || "qa_dom_report.json", JSON.stringify({ base: BASE, results, errors }, null, 2));
for (const r of results) console.log(`${r.ok ? "PASS" : "FAIL"}  ${r.name}${r.detail ? "  [" + r.detail + "]" : ""}`);
console.log(`${results.filter((r) => r.ok).length}/${results.length} passed`);
window.close();
if (results.some((r) => !r.ok)) process.exit(1);
