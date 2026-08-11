import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const baseUrl = process.argv[2] || "http://127.0.0.1:8765/";
const reportPath = process.argv[3] || "data/input_representation_atlas_crop_crossvalidation_2026-07-12/browser_qa.json";
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

  const initial = await page.evaluate(async () => {
    const atlas = await (await fetch("data/atlas.json")).json();
    const nodeElements = [...document.querySelectorAll("foreignObject.graph-node")];
    const edgeElements = [...document.querySelectorAll("path.graph-edge")];
    const boxes = nodeElements.map((node) => ({
      id: node.dataset.nodeId,
      x: Number(node.getAttribute("x")),
      y: Number(node.getAttribute("y")),
      width: Number(node.getAttribute("width")),
      height: Number(node.getAttribute("height")),
    }));
    let overlaps = 0;
    for (let i = 0; i < boxes.length; i += 1) {
      for (let j = i + 1; j < boxes.length; j += 1) {
        const width = Math.min(boxes[i].x + boxes[i].width, boxes[j].x + boxes[j].width) - Math.max(boxes[i].x, boxes[j].x);
        const height = Math.min(boxes[i].y + boxes[i].height, boxes[j].y + boxes[j].height) - Math.max(boxes[i].y, boxes[j].y);
        if (width > 0.1 && height > 0.1) overlaps += 1;
      }
    }
    const canonicalGroups = atlas.graph.nodes.filter((node) => node.type === "membership_group");
    const groupFailures = canonicalGroups.flatMap((group) => {
      const groupNodeId = `group::${group.group_id}`;
      const nodeCount = nodeElements.filter((node) => node.dataset.nodeId === groupNodeId).length;
      const parentEdges = edgeElements.filter((edge) => edge.dataset.target === groupNodeId).length;
      const modelEdges = edgeElements.filter((edge) => edge.dataset.source === groupNodeId).length;
      return nodeCount === 1 && parentEdges === group.subtype_ids.length && modelEdges === group.model_ids.length
        ? []
        : [{ groupNodeId, nodeCount, parentEdges, expectedParents: group.subtype_ids.length, modelEdges, expectedModels: group.model_ids.length }];
    });
    const modelIncomingFailures = atlas.architectures.filter((model) => edgeElements.filter((edge) => edge.dataset.target === `model::${model.model_id}`).length !== 1).length;
    const root = boxes.find((box) => box.id === "taxonomy_root");
    const groupBoxes = boxes.filter((box) => box.id.startsWith("group::"));
    const rootCenter = root.x + root.width / 2;
    return {
      graphNodes: nodeElements.length,
      rootNodes: document.querySelectorAll("foreignObject.graph-node-root").length,
      familyNodes: document.querySelectorAll("foreignObject.graph-node-family").length,
      subtypeNodes: document.querySelectorAll("foreignObject.graph-node-subtype").length,
      membershipGroupNodes: document.querySelectorAll("foreignObject.graph-node-membership_group").length,
      modelNodes: document.querySelectorAll("foreignObject.graph-node-model").length,
      edges: edgeElements.length,
      uniqueNodeIds: new Set(nodeElements.map((node) => node.dataset.nodeId)).size,
      cropNodes: document.querySelectorAll("[data-model-crop]").length,
      pageOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      graphBox: document.querySelector("#taxonomy-graph").getBoundingClientRect().toJSON(),
      canonicalGroupCount: canonicalGroups.length,
      leftGroups: groupBoxes.filter((box) => box.x + box.width / 2 < rootCenter).length,
      rightGroups: groupBoxes.filter((box) => box.x + box.width / 2 > rootCenter).length,
      overlaps,
      groupFailures,
      modelIncomingFailures,
      expectedMembershipGroups: atlas.graph.counts.membership_groups,
      expectedModels: atlas.meta.model_count,
      expectedCropNodes: atlas.meta.models_with_cropped_figure * 2,
    };
  });
  if (initial.rootNodes !== 1 || initial.membershipGroupNodes !== initial.expectedMembershipGroups || initial.modelNodes !== initial.expectedModels || initial.uniqueNodeIds !== initial.graphNodes) {
    throw new Error(`Unexpected graph node counts: ${JSON.stringify(initial)}`);
  }
  if (initial.familyNodes !== 5 || initial.subtypeNodes < 15 || initial.subtypeNodes > 30) throw new Error(`Canonical families or mirrored subtype ports are incomplete: ${JSON.stringify(initial)}`);
  if (initial.leftGroups < 1 || initial.rightGroups < 1) throw new Error(`Membership groups were not split across both sides: ${JSON.stringify(initial)}`);
  if (initial.overlaps !== 0 || initial.groupFailures.length || initial.modelIncomingFailures) throw new Error(`Grouped graph topology failed: ${JSON.stringify(initial)}`);
  if (initial.cropNodes !== initial.expectedCropNodes) throw new Error(`Expected ${initial.expectedCropNodes} crop viewports across graph and index, found ${initial.cropNodes}`);
  if (initial.pageOverflow > 1) throw new Error(`Page has ${initial.pageOverflow}px horizontal overflow`);
  if (initial.graphBox.width < 300 || initial.graphBox.height < 450) throw new Error("Graph viewport is undersized");

  const socialPreview = await page.evaluate(async () => {
    const meta = (selector) => document.querySelector(selector)?.content;
    const localImage = new Image();
    const loaded = new Promise((resolve, reject) => {
      localImage.onload = resolve;
      localImage.onerror = reject;
    });
    localImage.src = new URL("assets/social-preview.png", document.baseURI).href;
    await loaded;
    return {
      canonical: document.querySelector('link[rel="canonical"]')?.href,
      ogTitle: meta('meta[property="og:title"]'),
      ogImage: meta('meta[property="og:image"]'),
      ogWidth: meta('meta[property="og:image:width"]'),
      ogHeight: meta('meta[property="og:image:height"]'),
      twitterCard: meta('meta[name="twitter:card"]'),
      twitterImage: meta('meta[name="twitter:image"]'),
      localImageWidth: localImage.naturalWidth,
      localImageHeight: localImage.naturalHeight,
    };
  });
  const publicPreview = "https://bogdandidenko.github.io/text-bio-fundational-models-review/assets/social-preview.png";
  if (socialPreview.ogImage !== publicPreview || socialPreview.twitterImage !== publicPreview || socialPreview.twitterCard !== "summary_large_image" || socialPreview.ogWidth !== "1200" || socialPreview.ogHeight !== "630" || socialPreview.localImageWidth !== 1200 || socialPreview.localImageHeight !== 630) {
    throw new Error(`Social preview metadata failed: ${JSON.stringify(socialPreview)}`);
  }

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

  const chatCell = await page.evaluate(async () => {
    const atlas = await (await fetch("data/atlas.json")).json();
    const model = atlas.architectures.find((item) => item.model_name === "CHATCELL");
    const group = atlas.graph.nodes.find((item) => item.type === "membership_group" && item.group_id === model.membership_group_id);
    return { modelId: model.model_id, groupId: model.membership_group_id, groupModelCount: group.model_count };
  });
  await page.locator(`foreignObject[data-node-id="model::${chatCell.modelId}"]`).dispatchEvent("click");
  const chatCellPaths = await page.evaluate(() => ({
    heading: document.querySelector("#graph-inspector .model-path-heading")?.textContent?.replace(/\s+/g, " ").trim(),
    scope: document.querySelector("#graph-inspector .model-path-summary > p")?.textContent?.trim(),
    chips: [...document.querySelectorAll("#graph-inspector [data-inspector-subtype-path]")].map((item) => item.textContent.replace(/\s+/g, " ").trim()),
  }));
  if (chatCellPaths.chips.length !== 3 || !chatCellPaths.heading?.includes("3 subtype paths · 7 routes") || chatCellPaths.scope !== "All subtype paths remain within F1.") {
    throw new Error(`CHATCELL graph-path explanation is incomplete: ${JSON.stringify(chatCellPaths)}`);
  }
  await page.locator(`foreignObject[data-node-id="group::${chatCell.groupId}"]`).dispatchEvent("click");
  const chatCellGroup = await page.evaluate(() => ({
    title: document.querySelector("#graph-inspector .membership-group-inspector h3")?.textContent?.trim(),
    subtypeRows: document.querySelectorAll("#graph-inspector .membership-path-row").length,
    modelRows: document.querySelectorAll("#graph-inspector [data-inspector-model]").length,
  }));
  if (chatCellGroup.subtypeRows !== 3 || chatCellGroup.modelRows !== chatCell.groupModelCount) {
    throw new Error(`CHATCELL exact membership group is incomplete: ${JSON.stringify({ chatCell, chatCellGroup })}`);
  }
  await page.locator("#graph-inspector .membership-group-inspector h3").click();
  const groupInspectorKeepsFocus = await page.locator("foreignObject.graph-node-membership_group.is-highlighted").count() === 1;
  if (!groupInspectorKeepsFocus) throw new Error("Clicking inside the membership-group inspector cleared group focus");
  await page.locator("#graph-summary").click();
  const groupOutsideClickClearsFocus = await page.locator("#graph-inspector .root-inspector").count() === 1
    && await page.locator("foreignObject.graph-node.is-dimmed").count() === 0;
  if (!groupOutsideClickClearsFocus) throw new Error("Clicking outside a membership-group card did not clear focus");

  await page.locator("#show-all").click();
  await page.locator('#family-filter button[data-family="dense_continuous_carrier"]').click();
  await page.waitForTimeout(550);
  const focused = await page.evaluate(() => ({
    families: document.querySelectorAll("foreignObject.graph-node-family").length,
    subtypes: document.querySelectorAll("foreignObject.graph-node-subtype").length,
    groups: document.querySelectorAll("foreignObject.graph-node-membership_group").length,
    models: document.querySelectorAll("foreignObject.graph-node-model").length,
    edges: document.querySelectorAll("path.graph-edge").length,
  }));
  if (focused.families !== 1 || focused.subtypes < 1 || focused.groups < 1 || focused.models < 1 || focused.models >= initial.expectedModels) {
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
    return { modelNodes: boxes.length, groupNodes: document.querySelectorAll("foreignObject.graph-node-membership_group").length, overlaps };
  });
  if (subtypeLayout.overlaps !== 0 || subtypeLayout.groupNodes !== 1) throw new Error(`Subtype graph grouping failed: ${JSON.stringify(subtypeLayout)}`);
  if (!mobile) await page.screenshot({ path: "/tmp/atlas-graph-subtype-focus.png" });
  await page.locator("#show-all").click();
  await page.waitForTimeout(500);

  const latestBatchContract = await page.evaluate(async () => {
    const atlas = await (await fetch("data/atlas.json")).json();
    const batch = atlas.filter_values.collection_batches[0];
    return {
      ...batch,
      modelNames: atlas.architectures
        .filter((architecture) => architecture.collection_date === batch.date)
        .map((architecture) => architecture.model_name)
        .sort(),
    };
  });
  await page.selectOption("#collection-filter", latestBatchContract.date);
  await page.waitForTimeout(700);
  const latestBatch = await page.evaluate(() => ({
    selected: document.querySelector("#collection-filter")?.value,
    modelNames: [...document.querySelectorAll("foreignObject.graph-node-model strong[title]")].map((node) => node.textContent.trim()),
    cardCount: document.querySelectorAll("#architecture-grid .architecture-card").length,
    evidenceCount: Number(document.querySelector("#evidence-result-count")?.textContent?.match(/^\d+/)?.[0] || 0),
  }));
  const actualModelNames = [...latestBatch.modelNames].sort();
  if (latestBatch.selected !== latestBatchContract.date || latestBatch.cardCount !== latestBatchContract.model_count || latestBatch.evidenceCount !== latestBatchContract.route_count || JSON.stringify(actualModelNames) !== JSON.stringify(latestBatchContract.modelNames)) {
    throw new Error(`Latest collection-batch filter failed: ${JSON.stringify({ latestBatchContract, latestBatch })}`);
  }
  latestBatch.contract = latestBatchContract;
  if (!mobile) {
    latestBatch.screenshot = "/tmp/atlas-latest-batch-desktop.png";
    await page.screenshot({ path: latestBatch.screenshot });
  }
  await page.locator("#show-all").click();
  await page.waitForTimeout(500);

  const audit = await page.evaluate(async () => {
    const atlas = await (await fetch("data/atlas.json")).json();
    const multi = atlas.architectures.reduce((best, item) => item.subtypes.length > best.subtypes.length ? item : best, atlas.architectures[0]);
    const noFigure = atlas.architectures.find((item) => !item.figure);
    return { multiId: multi.model_id, multiParents: multi.subtypes.length, noFigureId: noFigure.model_id };
  });
  await page.locator(`foreignObject[data-node-id="model::${audit.multiId}"]`).dispatchEvent("click");
  const modelIncoming = page.locator(`path.graph-edge[data-target="model::${audit.multiId}"]`);
  const multiIncoming = await modelIncoming.count();
  const membershipGroupId = await modelIncoming.first().getAttribute("data-source");
  const groupIncoming = await page.locator(`path.graph-edge[data-target="${membershipGroupId}"]`).count();
  if (multiIncoming !== 1 || groupIncoming !== audit.multiParents || await page.locator(`foreignObject[data-node-id="model::${audit.multiId}"]`).count() !== 1) {
    throw new Error(`Multi-parent model grouping failed: ${JSON.stringify({ audit, multiIncoming, membershipGroupId, groupIncoming })}`);
  }
  await page.locator(`foreignObject[data-node-id="model::${audit.noFigureId}"]`).dispatchEvent("click");
  if (await page.locator("#graph-inspector .evidence-absence").count() !== 1) throw new Error("No-suitable-figure state is not explicit");

  await page.locator('.view-tab[data-view="architectures"]').click();
  if (await page.locator("#architecture-grid .architecture-card").count() !== initial.expectedModels) throw new Error(`Model index does not contain ${initial.expectedModels} cards`);
  await page.locator('.view-tab[data-view="evidence"]').click();
  if (await page.locator("#evidence-rows tr").count() !== 50) throw new Error("Evidence pagination does not expose the first 50 routes");
  await page.locator('.view-tab[data-view="graph"]').click();

  await page.screenshot({ path: screenshot, fullPage: mobile });
  const screenshotSize = fs.statSync(screenshot).size;
  if (screenshotSize < 50_000) throw new Error(`Screenshot appears blank: ${screenshotSize} bytes`);
  await page.close();
  return { viewport, initial, socialPreview, inspector, inspectorClickKeepsFocus, outsideClick, chatCellPaths, chatCellGroup, groupInspectorKeepsFocus, groupOutsideClickClearsFocus, focused, subtypeLayout, latestBatch, audit: { ...audit, multiIncoming, membershipGroupId, groupIncoming }, screenshot, screenshotSize, consoleErrors: errors };
}

const desktop = await inspect({ width: 1440, height: 1000 }, "/tmp/atlas-graph-desktop.png");
const mobile = await inspect({ width: 390, height: 844 }, "/tmp/atlas-graph-mobile.png", true);
await browser.close();

const result = { status: "ok", desktop, mobile };
fs.writeFileSync("/tmp/atlas-graph-qa.json", JSON.stringify(result, null, 2));
fs.mkdirSync(path.dirname(reportPath), { recursive: true });
fs.writeFileSync(reportPath, `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result));
