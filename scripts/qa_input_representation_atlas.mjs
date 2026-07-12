import fs from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const baseUrl = process.argv[2] || "http://127.0.0.1:8765/";
const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.PLAYWRIGHT_CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});

async function inspect(viewport, screenshot, mobile = false) {
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#loading-screen")?.classList.contains("is-hidden"));
  await page.waitForSelector("foreignObject.graph-node-model");

  const initial = await page.evaluate(() => ({
    graphNodes: document.querySelectorAll("foreignObject.graph-node").length,
    rootNodes: document.querySelectorAll("foreignObject.graph-node-root").length,
    familyNodes: document.querySelectorAll("foreignObject.graph-node-family").length,
    subtypeNodes: document.querySelectorAll("foreignObject.graph-node-subtype").length,
    modelNodes: document.querySelectorAll("foreignObject.graph-node-model").length,
    edges: document.querySelectorAll("path.graph-edge").length,
    uniqueNodeIds: new Set([...document.querySelectorAll("foreignObject.graph-node")].map((node) => node.dataset.nodeId)).size,
    cropNodes: document.querySelectorAll("[data-model-crop]").length,
    pageOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    graphBox: document.querySelector("#taxonomy-graph").getBoundingClientRect().toJSON(),
  }));
  if (initial.graphNodes !== 132 || initial.rootNodes !== 1 || initial.familyNodes !== 5 || initial.subtypeNodes !== 15 || initial.modelNodes !== 111 || initial.uniqueNodeIds !== 132) {
    throw new Error(`Unexpected graph node counts: ${JSON.stringify(initial)}`);
  }
  if (initial.edges !== 234) throw new Error(`Expected 234 edges, found ${initial.edges}`);
  if (initial.cropNodes !== 158) throw new Error(`Expected 158 crop viewports for 79 validated figures across graph and index, found ${initial.cropNodes}`);
  if (initial.pageOverflow > 1) throw new Error(`Page has ${initial.pageOverflow}px horizontal overflow`);
  if (initial.graphBox.width < 300 || initial.graphBox.height < 450) throw new Error("Graph viewport is undersized");

  const firstModel = page.locator("foreignObject.graph-node-model").filter({ has: page.locator(".paper-crop") }).first();
  await firstModel.dispatchEvent("click");
  await page.waitForSelector("#graph-inspector .inspector-title");
  const inspector = await page.evaluate(() => ({
    title: document.querySelector("#graph-inspector .inspector-title h3")?.textContent?.trim(),
    evidence: Boolean(document.querySelector("#graph-inspector .inspector-evidence, #graph-inspector .evidence-absence")),
    examples: document.querySelectorAll("#graph-inspector .input-example").length,
    routes: document.querySelectorAll("#graph-inspector .route-record").length,
    highlightedEdges: document.querySelectorAll("path.graph-edge.is-highlighted").length,
    evidenceImageWidth: document.querySelector("#graph-inspector .inspector-evidence img")?.naturalWidth || 0,
  }));
  if (!inspector.title || !inspector.evidence || inspector.examples < 1 || inspector.routes < 1 || inspector.highlightedEdges < 3 || inspector.evidenceImageWidth < 20) {
    throw new Error(`Model focus failed: ${JSON.stringify(inspector)}`);
  }

  await page.locator("#graph-inspector .inspector-title").click();
  const inspectorClickKeepsFocus = await page.locator("foreignObject.graph-node-model.is-highlighted").count() === 1;
  if (!inspectorClickKeepsFocus) throw new Error("Clicking inside the inspector cleared model focus");

  await page.locator("#graph-summary").click();
  const outsideClick = await page.evaluate(() => ({
    title: document.querySelector("#graph-inspector .root-inspector h3")?.textContent?.trim(),
    dimmedNodes: document.querySelectorAll("foreignObject.graph-node.is-dimmed").length,
  }));
  if (!outsideClick.title || outsideClick.dimmedNodes !== 0) {
    throw new Error(`Clicking outside the selected card did not clear focus: ${JSON.stringify(outsideClick)}`);
  }

  await firstModel.dispatchEvent("click");
  if (!mobile) await page.screenshot({ path: "/tmp/atlas-graph-model-focus.png" });

  await page.locator("#show-all").click();
  await page.locator('#family-filter button[data-family="dense_continuous_carrier"]').click();
  await page.waitForTimeout(550);
  const focused = await page.evaluate(() => ({
    families: document.querySelectorAll("foreignObject.graph-node-family").length,
    subtypes: document.querySelectorAll("foreignObject.graph-node-subtype").length,
    models: document.querySelectorAll("foreignObject.graph-node-model").length,
    edges: document.querySelectorAll("path.graph-edge").length,
  }));
  if (focused.families !== 1 || focused.subtypes < 1 || focused.models < 1 || focused.models >= 111) {
    throw new Error(`Family focus failed: ${JSON.stringify(focused)}`);
  }
  await page.selectOption("#subtype-filter", "connector_mediated_embedding");
  await page.waitForTimeout(1200);
  await page.evaluate(() => document.body.getBoundingClientRect().height);
  const subtypeLayout = await page.evaluate(() => {
    const boxes = [...document.querySelectorAll("foreignObject.graph-node-model")].map((node) => node.getBoundingClientRect());
    let overlaps = 0;
    for (let i = 0; i < boxes.length; i += 1) {
      for (let j = i + 1; j < boxes.length; j += 1) {
        const width = Math.min(boxes[i].right, boxes[j].right) - Math.max(boxes[i].left, boxes[j].left);
        const height = Math.min(boxes[i].bottom, boxes[j].bottom) - Math.max(boxes[i].top, boxes[j].top);
        if (width > 1 && height > 1) overlaps += 1;
      }
    }
    return { modelNodes: boxes.length, overlaps };
  });
  if (subtypeLayout.overlaps !== 0) throw new Error(`Subtype graph has overlapping model nodes: ${JSON.stringify(subtypeLayout)}`);
  if (!mobile) await page.screenshot({ path: "/tmp/atlas-graph-subtype-focus.png" });
  await page.locator("#show-all").click();
  await page.waitForTimeout(500);

  const audit = await page.evaluate(async () => {
    const atlas = await (await fetch("data/atlas.json")).json();
    const multi = atlas.architectures.reduce((best, item) => item.subtypes.length > best.subtypes.length ? item : best, atlas.architectures[0]);
    const noFigure = atlas.architectures.find((item) => !item.figure);
    return { multiId: multi.model_id, multiParents: multi.subtypes.length, noFigureId: noFigure.model_id };
  });
  await page.locator(`foreignObject[data-node-id="model::${audit.multiId}"]`).dispatchEvent("click");
  const multiIncoming = await page.locator(`path.graph-edge[data-target="model::${audit.multiId}"]`).count();
  if (multiIncoming !== audit.multiParents || await page.locator(`foreignObject[data-node-id="model::${audit.multiId}"]`).count() !== 1) {
    throw new Error(`Multi-parent model identity failed: ${JSON.stringify({ audit, multiIncoming })}`);
  }
  await page.locator(`foreignObject[data-node-id="model::${audit.noFigureId}"]`).dispatchEvent("click");
  if (await page.locator("#graph-inspector .evidence-absence").count() !== 1) throw new Error("No-suitable-figure state is not explicit");

  await page.locator('.view-tab[data-view="architectures"]').click();
  if (await page.locator("#architecture-grid .architecture-card").count() !== 111) throw new Error("Model index does not contain 111 cards");
  await page.locator('.view-tab[data-view="evidence"]').click();
  if (await page.locator("#evidence-rows tr").count() !== 50) throw new Error("Evidence pagination does not expose the first 50 routes");
  await page.locator('.view-tab[data-view="graph"]').click();

  await page.screenshot({ path: screenshot, fullPage: mobile });
  const screenshotSize = fs.statSync(screenshot).size;
  if (screenshotSize < 50_000) throw new Error(`Screenshot appears blank: ${screenshotSize} bytes`);
  await page.close();
  return { viewport, initial, inspector, inspectorClickKeepsFocus, outsideClick, focused, subtypeLayout, audit, screenshot, screenshotSize, consoleErrors: errors };
}

const desktop = await inspect({ width: 1440, height: 1000 }, "/tmp/atlas-graph-desktop.png");
const mobile = await inspect({ width: 390, height: 844 }, "/tmp/atlas-graph-mobile.png", true);
await browser.close();

const result = { status: "ok", desktop, mobile };
fs.writeFileSync("/tmp/atlas-graph-qa.json", JSON.stringify(result, null, 2));
fs.writeFileSync(
  "data/input_representation_atlas_crop_crossvalidation_2026-07-12/browser_qa.json",
  `${JSON.stringify(result, null, 2)}\n`,
);
console.log(JSON.stringify(result));
