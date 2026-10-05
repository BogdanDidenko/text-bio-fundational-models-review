// Layout follows Dagre's graphlib/layout API; edges come from recorded operands.
const NS="http://www.w3.org/2000/svg";
const HTML="http://www.w3.org/1999/xhtml";
const element=(name,attrs={})=>{const item=document.createElementNS(NS,name);Object.entries(attrs).forEach(([key,value])=>item.setAttribute(key,value));return item;};
const escape=(value)=>String(value??"").replace(/[&<>"']/g,(char)=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));

export function renderDiagram(container,{diagram,assembly,operations,boundaryNames,onSelect}){
  if(!globalThis.dagre)throw new Error("Dagre layout library unavailable");
  const data=new Map(assembly.nodes.map((node)=>[node.node_id,node]));
  const label=(id)=>data.get(id)?.representation_type.replaceAll("_"," ") || id;
  const measure=document.createElement("div");measure.className="diagram-measure";document.body.append(measure);
  const graph=new dagre.graphlib.Graph({multigraph:true});
  graph.setGraph({rankdir:"TB",nodesep:45,ranksep:65,edgesep:18,marginx:24,marginy:24});
  graph.setDefaultEdgeLabel(()=>({}));
  const htmlFor=(node)=>{
    if(node.kind==="source")return `<button class="diagram-node source-diagram-node" data-diagram-node="source"><span class="diagram-kind">SOURCE</span><strong>${escape(label(node.dataId))}</strong></button>`;
    if(node.kind==="receiver")return `<button class="diagram-node receiver-diagram-node" data-diagram-node="receiver"><span class="diagram-kind">RECEIVING COMPONENT</span><strong>${escape(assembly.recipient_component)}</strong></button>`;
    return `<button class="diagram-node ${node.group.calls.some((call)=>!call.operation_id)?"unexpanded-diagram-node":""}" data-diagram-node="${escape(node.id)}">${node.group.calls.map((call,index)=>`${index?'<span class="in-node-arrow">↓</span>':""}<strong>${escape(call.operation_id?operations.get(call.operation_id).label:boundaryNames[call.parameters.source_operation] || call.parameters.source_operation.replaceAll("_"," "))}</strong>${call.parameters.method?`<span class="diagram-method">${escape(call.parameters.method.replaceAll("_"," "))}</span>`:""}`).join("")}${node.group.calls.some((call)=>!call.operation_id)?'<span class="diagram-status">Internal rule unexpanded</span>':""}${node.group.sideInputs.length?`<span class="diagram-status">+ ${node.group.sideInputs.length} additional inputs</span>`:""}${node.group.calls.some((call)=>call.condition)?'<span class="diagram-status">Conditional operation</span>':""}</button>`;
  };
  for(const node of diagram.nodes){
    const html=htmlFor(node);measure.innerHTML=html;
    const box=measure.firstElementChild.getBoundingClientRect();
    graph.setNode(node.id,{width:box.width,height:box.height,html,descriptor:node});
  }
  diagram.edges.forEach((edge,index)=>{
    const html=`<div class="diagram-edge-label">${edge.dataIds.map((id)=>`<span>${escape(label(id))}</span>`).join("")}${edge.condition?'<small>conditional bypass</small>':""}</div>`;
    measure.innerHTML=html;
    const box=measure.firstElementChild.getBoundingClientRect();
    graph.setEdge(edge.from,edge.to,{width:box.width,height:box.height,labelpos:"c",html,descriptor:edge},String(index));
  });
  dagre.layout(graph);measure.remove();
  const svg=element("svg",{width:graph.graph().width,height:graph.graph().height,viewBox:`0 0 ${graph.graph().width} ${graph.graph().height}`,role:"group","aria-label":"Directed data transformation path; arrows indicate recorded data dependencies"});
  const defs=element("defs");const marker=element("marker",{id:"diagram-arrow",viewBox:"0 -5 10 10",refX:9,refY:0,markerWidth:7,markerHeight:7,orient:"auto"});
  marker.append(element("path",{d:"M0,-5L10,0L0,5",fill:"#365d64"}));defs.append(marker);svg.append(defs);
  const edges=element("g",{class:"diagram-edges"});svg.append(edges);
  graph.edges().forEach((key)=>{
    const edge=graph.edge(key);const path=edge.points.map((point,index)=>`${index?"L":"M"}${point.x},${point.y}`).join(" ");
    const line=element("path",{d:path,fill:"none",stroke:edge.descriptor.condition?"#a2824c":"#365d64","stroke-width":2,"marker-end":"url(#diagram-arrow)","data-from":key.v,"data-to":key.w,class:"dependency-arrow"});
    if(edge.descriptor.condition)line.setAttribute("stroke-dasharray","6 4");
    const title=element("title");title.textContent=edge.descriptor.condition || edge.descriptor.dataIds.join(" + ");line.append(title);edges.append(line);
    const labelBox=element("foreignObject",{x:edge.x-edge.width/2,y:edge.y-edge.height/2,width:edge.width,height:edge.height});
    const labelContent=document.createElementNS(HTML,"div");labelContent.innerHTML=edge.html;labelBox.append(labelContent);edges.append(labelBox);
  });
  const nodeGroup=element("g",{class:"diagram-nodes"});svg.append(nodeGroup);
  graph.nodes().forEach((id)=>{
    const node=graph.node(id);const box=element("foreignObject",{x:node.x-node.width/2,y:node.y-node.height/2,width:node.width,height:node.height,"data-graph-node":id});
    const content=document.createElementNS(HTML,"div");content.innerHTML=node.html;box.append(content);nodeGroup.append(box);
  });
  container.replaceChildren(svg);
  const source=graph.node("source");
  if(source && graph.graph().width>container.clientWidth)container.scrollLeft=Math.max(0,source.x-container.clientWidth/2);
  container.onclick=(event)=>{
    const button=event.target.closest("[data-diagram-node]");if(!button)return;
    container.querySelectorAll(".diagram-node").forEach((item)=>item.classList.toggle("selected",item===button));
    onSelect(graph.node(button.dataset.diagramNode).descriptor);
  };
  return {nodes:graph.nodes().length,edges:graph.edges().length,width:graph.graph().width,height:graph.graph().height};
}
