/* WAG-286 quartz visual topology preview · ---@---@---#---@---@--- · .dlw
   Four faceted quartz @ nodes around a central # signal coupling hub.
   Abstract reciprocal signal rails; no claim of physical crystalline quartz
   dynamics or mechanical/electrical behavior. No physical action executes.
   Read-only, separate from frozen WAG281–285 results.
*/
const WAG286_QUARTZ=Object.freeze({
 glyph:'---@---@---#---@---@---',materialStyle:'clear-quartz',
 nodeLabels:['@0','@1','#','@2','@3'],
 types:['quartz','quartz','hub','quartz','quartz'],
 edges:[[0,1],[1,2],[2,3],[3,4]],
 signalSitesPerNode:8,links:4,initialLinkWeight:.125
});
function wag286QuartzInitial(){
 const signals=Array.from({length:5},()=>Array(8).fill(0));
 signals[0]=[1,.3,.8,.2,.65,.1,.9,.4];
 return {signals,step:0};
}
function wag286QuartzMass(s){return s.signals.flat().reduce((a,b)=>a+b,0)}
function wag286QuartzPulse(s,weights=Array(4).fill(.125)){
 if(weights.length!==4||weights.some(w=>!Number.isFinite(w)||w<0||w>.25))
  throw Error('invalid quartz signal-coupling weights');
 if(s.signals.length!==5||s.signals.some(z=>z.length!==8))throw Error('invalid topology');
 const original=wag286QuartzMass(s),next=s.signals.map(a=>a.slice());
 // Each undirected rail is updated exactly once with symmetric flux.
 for(let e=0;e<4;e++)for(let k=0;k<8;k++){
  const source=s.signals[e][k],destination=s.signals[e+1][k^7],
    flux=weights[e]*(source-destination);
  next[e][k]-=flux;next[e+1][k^7]+=flux;
 }
 const newState={signals:next,step:s.step+1},
  residual=Math.abs(wag286QuartzMass(newState)-original);
 if(residual>1e-10)throw Error('signal conservation violated');
 if(!next.flat().every(v=>v>=-1e-12&&v<=1+1e-12))
  throw Error('activation out of bounds');
 return {...newState,residual};
}
function wag286QuartzCheck(){
 const audits=[];
 for(const w of [0,.0625,.125,.2,.25]){
  let s=wag286QuartzInitial(),maxResidual=0;
  const original=wag286QuartzMass(s);
  for(let n=0;n<144;n++){
   s=wag286QuartzPulse(s,Array(4).fill(w));
   maxResidual=Math.max(maxResidual,s.residual,
    Math.abs(wag286QuartzMass(s)-original));
  }
  audits.push({weight:w,steps:s.step,maxResidual,
   hubReceived:s.signals[2].some(x=>x>0),
   farEndReceived:s.signals[4].some(x=>x>0)});
 }
 return {topology:WAG286_QUARTZ,checks:audits,
  allPass:audits.every(z=>z.maxResidual<1e-9),
  referencePolicyChanged:false,physicalActions:0};
}
if(typeof module!=='undefined')module.exports={WAG286_QUARTZ,wag286QuartzInitial,
 wag286QuartzMass,wag286QuartzPulse,wag286QuartzCheck};
