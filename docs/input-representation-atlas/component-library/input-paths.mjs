// Reachability over the existing operand/call graph; no annotation changes.
export const refs = (ports) => Object.values(ports).flat();

export function graphIndex(assembly) {
  const next = new Map(), previous = new Map();
  const link = (from,to) => {
    if(!next.has(from))next.set(from,new Set());
    if(!previous.has(to))previous.set(to,new Set());
    next.get(from).add(to);previous.get(to).add(from);
  };
  for(const call of assembly.calls){
    const id="call:"+call.call_id;
    refs(call.inputs).forEach((node)=>link("node:"+node,id));
    refs(call.outputs).forEach((node)=>link(id,"node:"+node));
  }
  for(const edge of assembly.bypasses)link("node:"+edge.source_node_id,"node:"+edge.target_node_id);
  return {next,previous};
}

export function reachable(start, edges) {
  const visited=new Set(), queue=[start];
  for(let i=0;i<queue.length;i++){
    const item=queue[i];if(visited.has(item))continue;visited.add(item);
    for(const child of edges.get(item) || [])if(!visited.has(child))queue.push(child);
  }
  return visited;
}

export function inputPath(assembly,sourceId,targetId) {
  const {next,previous}=graphIndex(assembly);
  const descendants=reachable("node:"+sourceId,next);
  const ancestors=reachable("node:"+targetId,previous);
  const onPath=new Set([...descendants].filter((item)=>ancestors.has(item)));
  const calls=assembly.calls.filter((call)=>onPath.has("call:"+call.call_id));
  const nodeIds=new Set([...onPath].filter((id)=>id.startsWith("node:")).map((id)=>id.substring(5)));
  const sideInputs=[...new Set(calls.flatMap((call)=>refs(call.inputs)).filter((id)=>!nodeIds.has(id)))];
  return {connected:descendants.has("node:"+targetId),calls,nodeIds,sideInputs,
    bypasses:assembly.bypasses.filter((edge)=>nodeIds.has(edge.source_node_id)&&nodeIds.has(edge.target_node_id))};
}

export function availableSources(assembly,targetId) {
  const {previous}=graphIndex(assembly);
  const ancestors=reachable("node:"+targetId,previous);
  const available=assembly.nodes.filter((node)=>ancestors.has("node:"+node.node_id));
  const roots=available.filter((node)=>!previous.has("node:"+node.node_id));
  const score=(node)=>{
    const role=node.contextual_role.toLowerCase();
    if(role.includes("measured source"))return 30;
    if(role.includes("sample_input")||role.includes("sample input"))return 25;
    if(role.includes("measured"))return 20;
    if(role.includes("parameter")||node.origin==="implicit_parameter")return 0;
    if(role.includes("reference")||role.includes("prior"))return 5;
    return 10;
  };
  roots.sort((a,b)=>score(b)-score(a));
  return {roots,intermediates:available.filter((node)=>!roots.includes(node)),defaultSource:roots[0]?.node_id || targetId};
}

export function groupPathCalls(path) {
  const groups=[];
  for(const call of path.calls){
    const last=groups[groups.length-1];
    if(last && last.sourceStepId===call.source_step_id)last.calls.push(call);
    else groups.push({sourceStepId:call.source_step_id,calls:[call]});
  }
  for(const group of groups){
    const inputs=new Set(group.calls.flatMap((call)=>refs(call.inputs)));
    const outputs=new Set(group.calls.flatMap((call)=>refs(call.outputs)));
    group.inputs=[...inputs].filter((id)=>!outputs.has(id));
    group.outputs=[...outputs].filter((id)=>!inputs.has(id));
    group.sideInputs=group.inputs.filter((id)=>!path.nodeIds.has(id));
  }
  const producers=new Map();
  groups.forEach((group)=>group.outputs.forEach((id)=>producers.set(id,group)));
  function depth(group,active=new Set()){
    if(group.level!==undefined)return group.level;
    if(active.has(group)){group.cyclic=true;return 0;}
    const branch=new Set(active);branch.add(group);
    const parents=group.inputs.map((id)=>producers.get(id)).filter((parent)=>parent && parent!==group);
    group.level=parents.length ? 1+Math.max(...parents.map((parent)=>depth(parent,branch))) : 0;
    return group.level;
  }
  groups.forEach((group)=>depth(group));
  return groups;
}
