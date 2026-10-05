import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const require=createRequire(import.meta.url);
const {chromium}=require("playwright");
const url=process.argv[2] || "http://127.0.0.1:8766/component-library/";
const output=process.argv[3] || "analysis/representation_block_library_2026-10-04/browser_qa";
fs.mkdirSync(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"});
const report=[];
try{
  for(const [name,viewport] of [["desktop",{width:1440,height:1000}],["mobile",{width:390,height:844}]]){
    const page=await browser.newPage({viewport});const errors=[];
    page.on("pageerror",(error)=>errors.push(error.message));
    await page.goto(url,{waitUntil:"networkidle"});await page.waitForSelector(".list-entry");
    const catalog=await page.evaluate(async()=> (await(await fetch("data/catalog.json")).json()));
    if(await page.locator(".list-entry").count() !== catalog.blocks.length)throw new Error("Operation catalog incomplete");
    if(!await page.locator("#detail h2").textContent().then((value)=>value.includes("lookup")))throw new Error("Default lookup view missing");
    await page.screenshot({path:path.join(output,`${name}-catalog.png`)});
    await page.locator("#reuse").selectOption("shared");
    if(await page.locator(".list-entry").count() !== catalog.report.cross_paper_reused_types)throw new Error("Reuse count inflated");
    await page.locator("#search").fill("projection");if(!await page.locator(".list-entry").count())throw new Error("Search failed");
    await page.locator('[data-view="blocks"]').click();
    await page.locator("#paper").selectOption("full_2026-07-06__rec_001319");
    const quote=await page.locator("#detail .quote").first().textContent();if(!quote)throw new Error("Missing exact evidence");
    await page.locator("#detail .source-panel summary").first().click();
    await page.waitForFunction(()=>[...document.querySelectorAll(".source-image")].some((image)=>image.complete && image.naturalWidth>0));
    await page.locator("#detail [data-assembly]").first().click();
    if(await page.locator("#context-select option").count() !== 4)throw new Error("InstructCell contexts missing");
    await page.locator("#context-select").selectOption({index:1});
    await page.screenshot({path:path.join(output,`${name}-assembly.png`)});
    await page.locator('[data-view="blocks"]').click();
    await page.locator('[data-select="bin"]').click();
    await page.locator('[data-supplement="bin"]').click();
    if(!await page.locator("#detail").textContent().then((value)=>value.includes("WITHDRAWN")))throw new Error("Supplement source status hidden");
    if(await page.locator("#full-graph .graph-operation").count() !== 7)throw new Error("Binning/lookup branches incomplete");
    await page.screenshot({path:path.join(output,`${name}-binning-example.png`)});
    await page.locator('[data-view="proposals"]').click();
    if(!await page.locator(".list-entry").count())throw new Error("Opaque source boundaries missing");
    await page.locator('[data-view="reuse"]').click();
    if(await page.locator(".list-entry").count() !== catalog.report.cross_paper_reused_types)throw new Error("Reuse view failed");
    await page.locator('[data-view="assemblies"]').click();
    await page.locator('[data-select="full_2026-07-06__rec_003517"]').click();
    if(await page.locator("#path-source").inputValue() !== "control_pool")throw new Error("X-Cell does not start at measured expression");
    if(await page.locator("#full-graph").getAttribute("open") !== null)throw new Error("Full transformation dump expanded by default");
    if(await page.locator('#focused-path [data-source-step="esm_lookup"]').count())throw new Error("Independent prior preparation leaked into expression path");
    if(!await page.locator("#focused-path .parallel-band").count())throw new Error("Expression branches flattened");
    if(!await page.locator('#path-diagram .dependency-arrow[data-from="source"][data-to="step:control_normalization"]').count())throw new Error("Source arrow absent");
    for(const branch of ["identity_encoder","value_encoder","mask_encoder"]){
      if(!await page.locator(`#path-diagram .dependency-arrow[data-from="step:${branch}"][data-to="step:combine_tokens"]`).count())throw new Error("Missing merge edge: "+branch);
    }
    await page.locator('#path-diagram [data-diagram-node="step:value_encoder"]').click();
    if(!await page.locator("#diagram-inspector").textContent().then((value)=>value.includes("Learned projection")))throw new Error("Diagram inspection failed");
    const diagramGeometry=await page.evaluate(()=>{
      const boxes=[...document.querySelectorAll('#path-diagram foreignObject[data-graph-node]')].map((node)=>({x:Number(node.getAttribute('x')),y:Number(node.getAttribute('y')),w:Number(node.getAttribute('width')),h:Number(node.getAttribute('height'))}));
      let overlaps=0;
      for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){
        const a=boxes[i],b=boxes[j];if(Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>1&&Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>1)overlaps++;
      }
      const clipped=[...document.querySelectorAll('#path-diagram .diagram-node')].filter((node)=>node.scrollHeight>node.clientHeight+1||node.scrollWidth>node.clientWidth+1).length;
      return {nodes:boxes.length,overlaps,clipped};
    });
    if(diagramGeometry.overlaps || diagramGeometry.clipped)throw new Error('Diagram geometry failure: '+JSON.stringify(diagramGeometry));
    await page.screenshot({path:path.join(output,`${name}-xcell-input-path.png`),fullPage:true});
    await page.locator("#path-receipt").selectOption("context");
    await page.locator("#path-source").selectOption("esm_reference");
    if(await page.locator('#focused-path [data-source-step="esm_lookup"]').count() !== 1)throw new Error("Prior path selection failed");
    if(await page.locator('#focused-path [data-source-step="control_normalization"]').count())throw new Error("Expression preprocessing leaked into prior path");
    await page.screenshot({path:path.join(output,`${name}-xcell-prior-path.png`),fullPage:true});
    await page.locator("#full-graph summary").first().click();
    if(await page.locator("#full-graph .graph-operation").count() !== 46)throw new Error("Original operations lost");
    await page.locator("#full-graph summary").first().click();
    const layout=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
      clipped:[...document.querySelectorAll("h1,h2,h3,.quote,.definition,.list-entry strong")].filter((item)=>item.scrollWidth>item.clientWidth+1).map((item)=>item.textContent)}));
    if(layout.overflow>1 || layout.clipped.length || errors.length)throw new Error(JSON.stringify({layout,errors}));
    report.push({name,viewport,operation_types:catalog.blocks.length,reused_types:catalog.report.cross_paper_reused_types,
      search:true,evidence:true,source_image:true,contexts:true,binning_lookup_branches:true,supplement_status:true,xcell_expression_path:true,xcell_prior_path:true,complete_graph_preserved:true,arrows_and_merges:true,node_inspection:true,diagramGeometry,layout,errors});
    await page.close();
  }
}finally{await browser.close();}
fs.writeFileSync(path.join(output,"report.json"),JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify(report,null,2));
