/* WAG-287 SILO PREVIEW · quartz isolation topology · .dlw
 Literal user geometry preserved verbatim, including unclosed second left brace:
 ---{Ss@sS}---{Ss@sS---{[(Ss#Ss)]}---{Ss@sS}---{Ss@sS}---
 The balanced computational interpretation has five distinct silos:
 {Ss@sS} {Ss@sS} {[(Ss#Ss)]} {Ss@sS} {Ss@sS}.
 Left and right {Ss@sS} are individually isolated state holders.
 Central # contains brace, box, and toroid shells (three nested views).
 Exchanges across --- are equal/opposite abstract signal transfers only.
 No physical quartz physics / material transport / repair authority.
*/
const WAG287_SILO=Object.freeze({
 literal:'---{Ss@sS}---{Ss@sS---{[(Ss#Ss)]}---{Ss@sS}---{Ss@sS}---',
 balanced:'---{Ss@sS}---{Ss@sS}---{[(Ss#Ss)]}---{Ss@sS}---{Ss@sS}---',
 nodes:['Ss@sS','Ss@sS','Ss#Ss','Ss@sS','Ss@sS'],
 wrappers:['{','{','{[(', '{','{'],
 shells:['brace','box','toroid'],
 hub:2,signalChannels:8,linkCount:4,
 defaultLinkWeight:.125,version:'WAG-287 PREVIEW'
});
function wag287SiloInitial(){
 const nodes=Array.from({length:5},()=>Array(8).fill(0));
 nodes[0]=[.2,.4,.8,.15,.7,.3,.95,.5];
 const isolate=nodes.map(x=>x.slice());
 return {nodes,original:isolate,step:0,ledger:[]};
}
function wag287SiloMass(s){return s.nodes.flat().reduce((sum,x)=>sum+x,0)}
function wag287SiloPulse(s,weights=Array(4).fill(.125)){
 if(weights.length!==4||weights.some(w=>!Number.isFinite(w)||w<0||w>.25))
  throw Error('silo signal weights outside [0,.25]');
 if(s.nodes.length!==5||s.nodes.some(n=>n.length!==8))throw Error('silo count mismatch');
 const before=wag287SiloMass(s),next=s.nodes.map(n=>n.slice()),transfers=[];
 for(let edge=0;edge<4;edge++)for(let channel=0;channel<8;channel++){
  // Reciprocal boundary uses opposing channel orientations.
  const source=channel,destination=channel^7;
  const delta=weights[edge]*(s.nodes[edge][source]-
   s.nodes[edge+1][destination]);
  next[edge][source]-=delta;
  next[edge+1][destination]+=delta;
  transfers.push({edge,channel,delta});
 }
 const result={nodes:next,original:s.original,
  step:s.step+1,ledger:transfers};
 const residual=Math.abs(wag287SiloMass(result)-before);
 if(residual>1e-10||next.flat().some(x=>x< -1e-12||x>1+1e-12))
  throw Error('silo conservation or bound violation');
 return {...result,residual};
}
function wag287SiloCheck(){
 const cases=[];
 for(const weight of [0,.0625,.125,.2,.25]){
  let s=wag287SiloInitial(),residual=0;
  const reference=wag287SiloMass(s),unchanged=s.nodes.map(x=>x.slice());
  for(let tick=0;tick<128;tick++){
   s=wag287SiloPulse(s,Array(4).fill(weight));
   residual=Math.max(residual,s.residual,
    Math.abs(wag287SiloMass(s)-reference));
  }
  const unchangedIfOff=weight!==0||s.nodes.every((node,i)=>
   node.every((x,k)=>x===unchanged[i][k]));
  const copiedSiloStateIsNotAliased=
   s.nodes.every((n,i)=>s.nodes.every((other,j)=>i===j||n!==other));
  cases.push({weight,ticks:s.step,maxResidual:residual,
   unchangedIfOff,copiedSiloStateIsNotAliased,
   hubReceived:Math.max(...s.nodes[2])>0});
 }
 return {topology:WAG287_SILO,cases,
  pass:cases.every(c=>c.maxResidual<1e-9&&
   c.unchangedIfOff&&c.copiedSiloStateIsNotAliased),
  verifiedSiloCount:5,physicalActions:0,
  frozenPhaseIVProgressChanged:false};
}
if(typeof module!=='undefined')module.exports={
 WAG287_SILO,wag287SiloInitial,wag287SiloMass,wag287SiloPulse,wag287SiloCheck};
