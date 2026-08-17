import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const root = path.resolve(import.meta.dirname, "..");
const baseUrl = process.argv[2] || "http://127.0.0.1:8765/";
const outputPath = path.resolve(
  process.argv[3] || path.join(root, "docs/input-representation-atlas/assets/social-preview.png"),
);
const atlasRoot = path.resolve(
  process.argv[4] || path.join(root, "docs/input-representation-atlas"),
);
const atlas = JSON.parse(
  fs.readFileSync(path.join(atlasRoot, "data/atlas.json"), "utf8"),
);
const graphCapturePath = "/tmp/input-representation-atlas-social-graph.png";

const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.PLAYWRIGHT_CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});

const sourcePage = await browser.newPage({ viewport: { width: 1600, height: 1100 }, deviceScaleFactor: 1 });
await sourcePage.goto(baseUrl, { waitUntil: "networkidle" });
await sourcePage.waitForFunction(() => document.querySelector("#loading-screen")?.classList.contains("is-hidden"));
await sourcePage.waitForSelector("foreignObject.graph-node-model");
await sourcePage.locator("#show-all").click();
await sourcePage.waitForTimeout(600);
await sourcePage.locator("#graph-canvas").screenshot({ path: graphCapturePath });
await sourcePage.close();

const graphDataUrl = `data:image/png;base64,${fs.readFileSync(graphCapturePath).toString("base64")}`;
const familySegments = atlas.families.map((family) => `<span style="background:${family.color}"></span>`).join("");
const familyLegend = atlas.families.map((family) => `
  <div class="family" style="--family:${family.color}">
    <b>${family.code}</b><span>${family.short}</span>
  </div>`).join("");

const previewPage = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
await previewPage.setContent(`<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <style>
    * { box-sizing: border-box; }
    html, body { width: 1200px; height: 630px; margin: 0; overflow: hidden; }
    body { background: #f5f7f8; color: #172026; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .preview { position: relative; display: grid; grid-template-columns: 510px 690px; width: 1200px; height: 630px; border: 1px solid #b8c2c8; background: #f5f7f8; }
    .family-bar { position: absolute; z-index: 3; top: 0; left: 0; display: grid; grid-template-columns: repeat(5, 1fr); width: 100%; height: 10px; }
    .copy { position: relative; z-index: 2; display: flex; min-width: 0; flex-direction: column; padding: 50px 42px 34px 48px; border-right: 1px solid #aeb9bf; background: #f5f7f8; }
    .eyebrow { color: #5d6b73; font-size: 14px; font-weight: 800; letter-spacing: 1.4px; text-transform: uppercase; }
    h1 { margin: 18px 0 16px; font-size: 53px; line-height: 0.99; letter-spacing: 0; }
    .description { max-width: 405px; margin: 0; color: #50616b; font-size: 20px; line-height: 1.35; }
    .families { display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 5px; margin-top: 27px; }
    .family { min-width: 0; padding: 7px 5px 6px; border-top: 5px solid var(--family); background: white; }
    .family b, .family span { display: block; letter-spacing: 0; }
    .family b { font-size: 12px; }
    .family span { margin-top: 2px; overflow: hidden; color: #68767e; font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }
    .stats { display: grid; grid-template-columns: repeat(4, 1fr); margin-top: auto; border: 1px solid #bac5ca; background: #bac5ca; gap: 1px; }
    .stat { min-width: 0; padding: 10px 8px 9px; background: white; }
    .stat strong, .stat span { display: block; }
    .stat strong { font-size: 24px; line-height: 1; }
    .stat span { margin-top: 5px; color: #5d6b73; font-size: 10px; line-height: 1.1; }
    .url { margin-top: 17px; font-size: 13px; font-weight: 750; }
    .visual { position: relative; min-width: 0; overflow: hidden; background: #f8fafb; }
    .visual img { width: 100%; height: 100%; object-fit: cover; object-position: center; filter: contrast(1.04) saturate(1.05); }
    .visual-label { position: absolute; top: 28px; right: 28px; padding: 9px 11px; border: 1px solid #aeb9bf; background: rgba(255,255,255,0.94); font-size: 11px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase; }
    .visual-note { position: absolute; right: 28px; bottom: 28px; max-width: 330px; padding: 11px 13px; border-left: 6px solid #172026; background: rgba(255,255,255,0.95); font-size: 13px; font-weight: 700; line-height: 1.3; }
  </style>
</head>
<body>
  <main class="preview">
    <div class="family-bar">${familySegments}</div>
    <section class="copy">
      <div class="eyebrow">Evidence atlas · Taxonomy v1</div>
      <h1>Input representation taxonomy</h1>
      <p class="description">How biological and textual objects become model-visible inputs.</p>
      <div class="families">${familyLegend}</div>
      <div class="stats">
        <div class="stat"><strong>${atlas.meta.record_count}</strong><span>accepted papers</span></div>
        <div class="stat"><strong>${atlas.meta.model_count}</strong><span>model architectures</span></div>
        <div class="stat"><strong>${atlas.meta.membership_group_count}</strong><span>exact subtype groups</span></div>
        <div class="stat"><strong>${atlas.meta.route_count}</strong><span>grounded routes</span></div>
      </div>
      <div class="url">bogdandidenko.github.io/text-bio-fundational-models-review</div>
    </section>
    <section class="visual">
      <img src="${graphDataUrl}" alt="Two-sided input representation taxonomy graph">
      <div class="visual-label">${atlas.meta.record_count}-record accepted corpus</div>
      <div class="visual-note">Exact subtype combinations connect ${atlas.meta.model_count} architectures to evidence-grounded input routes.</div>
    </section>
  </main>
</body>
</html>`, { waitUntil: "load" });
await previewPage.screenshot({ path: outputPath, clip: { x: 0, y: 0, width: 1200, height: 630 } });
await previewPage.close();
await browser.close();

const image = fs.readFileSync(outputPath);
if (image.length < 100_000) throw new Error(`Social preview appears too small: ${image.length} bytes`);
console.log(JSON.stringify({ status: "ok", output: outputPath, width: 1200, height: 630, bytes: image.length }));
