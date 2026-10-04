import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const url = process.argv[2] || "http://127.0.0.1:8766/component-library/";
const output = process.argv[3] || "analysis/representation_block_library_2026-10-04/browser_qa";
fs.mkdirSync(output, { recursive: true });
const browser = await chromium.launch({headless:true, executablePath:process.env.PLAYWRIGHT_CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"});
const report = [];
try {
  for (const [name, viewport] of [["desktop", {width:1440,height:1000}], ["mobile", {width:390,height:844}]]) {
    const page = await browser.newPage({viewport});
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
    await page.goto(url, {waitUntil:"networkidle"});
    await page.waitForSelector(".list-entry");
    const expected = await page.evaluate(async () => (await (await fetch("data/catalog.json")).json()).blocks.length);
    if (await page.locator(".list-entry").count() !== expected) throw new Error("Incomplete catalog");
    await page.locator('[data-view="blocks"]').click();
    await page.locator("#kind").selectOption("operation");
    await page.screenshot({path:path.join(output, `${name}-catalog.png`)});
    await page.locator("#search").fill("embedding");
    if (!await page.locator(".list-entry").count()) throw new Error("Search failed");
    await page.locator("#search").fill("");
    await page.locator("#paper").selectOption("full_2026-07-06__rec_001319");
    if (!await page.locator(".list-entry").count()) throw new Error("Paper filter failed");
    const quote = await page.locator("#detail .quote").first().textContent();
    if (!quote || !await page.locator("#detail .provenance").count()) throw new Error("Missing literal source evidence");
    await page.locator("#detail .source-panel summary").first().click();
    await page.waitForFunction(() => [...document.querySelectorAll(".source-image")].some((image) => image.complete && image.naturalWidth > 0));
    await page.locator("#detail [data-assembly]").first().click();
    if (!await page.locator(".graph-operation").count()) throw new Error("Assembly link failed");
    const choices = await page.locator("#context-select option").allTextContents();
    if (choices.length !== 4) throw new Error("InstructCell contexts incomplete");
    await page.locator("#context-select").selectOption({index:1});
    await page.screenshot({path:path.join(output, `${name}-assembly.png`)});
    await page.locator('[data-view="proposals"]').click();
    const pending = await page.locator(".list-entry").count();
    if (!pending) throw new Error("Extension queue missing");
    await page.locator('[data-view="decisions"]').click();
    if (!await page.locator(".list-entry").count()) throw new Error("Steward ledger missing");
    await page.locator('[data-view="blocks"]').click();
    const sizes = await page.evaluate(() => ({
      overflow:document.documentElement.scrollWidth - document.documentElement.clientWidth,
      clipped:[...document.querySelectorAll("h1,h2,h3,.list-entry strong,.quote,.definition")].filter((element) => element.scrollWidth > element.clientWidth + 1).map((element) => element.textContent),
      body:document.body.innerText,
    }));
    if (sizes.overflow > 1 || sizes.clipped.length) throw new Error(`Layout overflow: ${JSON.stringify(sizes)}`);
    if (errors.length) throw new Error(`Browser errors: ${errors.join("; ")}`);
    report.push({name, viewport, catalog_entries:expected, extension_proposals:pending, search:true, paper_filter:true, evidence:true, source_image:true, context_switch:true, page_overflow:sizes.overflow, clipped_labels:sizes.clipped, errors});
    await page.close();
  }
} finally { await browser.close(); }
fs.writeFileSync(path.join(output,"report.json"), JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify(report,null,2));
