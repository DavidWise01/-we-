/* WAG-287 · connected zigzag quartz silos · .dlw
  Zigzag connector has TWO independent diagonal paths / and backslash.
  Each couples adjacent individual silo states by paired opposite flux.
  This is connected nearest-neighbor geometry, NOT all-to-all or physics.
*/
const WAG287_ZIGZAG=Object.freeze({
  literal:'---/\\/\\/@\\/\\/---/\\/\\/@\\/\\/---/\\/\\/#\\/\\/---/\\/\\/@\\/\\/---/\\/\\/@\\/\\/----',
  silos:['@','@','#','@','@'],
  internal:['{Ss@sS}','{Ss@sS}','{[(Ss#Ss)]}','{Ss@sS}','{Ss@sS}'],
  links:[[0,1],[1,2],[2,3],[3,4]],
  routes:['/','\\'],channels:8,defaultWeight:.125,
  geometry:'double-diagonal nearest-neighbor quartz signal couplings',
  source:'WAG-287 silo-topology.js',physicalActions:0
});
function wag287MeshInitial(){
  return {nodes:wag287SiloInitial().nodes.map(x=>x.slice()),tick:0,
    deliveredAcrossEdges:[0,0,0,0],maxResidual:0};
}
function wag287MeshMass(s){return s.nodes.flat().reduce((a,b)=>a+b,0)}
function wag287MeshTick(s,weight=.125){
  if(!Number.isFinite(weight)||weight<0||weight>.25)
    throw Error('weight outside allowed [0,.25]');
  const before=wag287MeshMass(s),nodes=s.nodes.map(x=>x.slice());
  const crossing=Array(4).fill(0);
  for(let edge=0;edge<4;edge++)for(let lane=0;lane<8;lane++)
    for(let diagonal=0;diagonal<2;diagonal++){
      const incoming=diagonal===0?(lane^7):((lane+3)&7);
      const delta=(weight/2)*(s.nodes[edge][lane]-s.nodes[edge+1][incoming]);
      nodes[edge][lane]-=delta;
      nodes[edge+1][incoming]+=delta;
      crossing[edge]+=Math.abs(delta);
    }
  const result={nodes,tick:s.tick+1,
    deliveredAcrossEdges:s.deliveredAcrossEdges.map((v,i)=>v+crossing[i]),
    maxResidual:s.maxResidual};
  const residual=Math.abs(wag287MeshMass(result)-before);
  if(residual>1e-10||nodes.some(x=>x.length!==8)||
     nodes.flat().some(v=>!Number.isFinite(v)||v< -1e-12||v>1+1e-12))
    throw Error('zigzag mesh conserved-activation failure');
  result.maxResidual=Math.max(result.maxResidual,residual);
  return result;
}
function wag287MeshAudit(){
  const cases=[];
  for(const weight of [0,.0625,.125,.2,.25]){
    const start=wag287MeshInitial(),initial=JSON.stringify(start.nodes);
    const initialMass=wag287MeshMass(start);let s=start;
    for(let i=0;i<128;i++)s=wag287MeshTick(s,weight);
    const unchangedWhenOff=weight!==0||JSON.stringify(s.nodes)===initial;
    const crossedAllEdges=weight===0
      ?s.deliveredAcrossEdges.every(x=>x===0)
      :s.deliveredAcrossEdges.every(x=>x>0);
    const uniqueSilos=s.nodes.every((node,i)=>s.nodes.every((other,j)=>i===j||node!==other));
    const residual=Math.abs(wag287MeshMass(s)-initialMass);
    cases.push({weight,ticks:s.tick,unchangedWhenOff,crossedAllEdges,
      uniqueSilos,maxResidual:Math.max(residual,s.maxResidual),
      hubReceived:s.nodes[2].some(x=>x>1e-6)});
  }
  return {bound:'WAG-287',stage:'CONNECTED_QUARTZ_PREVIEW',
    literal:WAG287_ZIGZAG.literal,tests:cases,
    pass:cases.every(c=>c.unchangedWhenOff&&c.crossedAllEdges&&
      c.uniqueSilos&&c.maxResidual<1e-9),
    physicalActions:0,modifiedFrozenReceipt:false,
    scope:'abstract reciprocal nearest-neighbor zigzag, not quartz physics'};
}
if(typeof module!=='undefined')module.exports={
  WAG287_ZIGZAG,wag287MeshInitial,wag287MeshMass,wag287MeshTick,wag287MeshAudit
};