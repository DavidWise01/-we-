/* WAG-290 · Cortex observation / frontal selection, read-only append · .dlw
  3³ cortex readout includes center exactly once. Frontal 1³ selects a
  channel candidate from 8 aggregated channels; it does NOT actuate.
  Baseline WAG-288 and WAG-289 remain unchanged.
*/
const WAG290=Object.freeze({center:62,channels:8,mode:'observe-only',tieBreak:'lowest channel index',physicalActions:0});
function wag290CortexRead(state){
 const ids=wag289Groups(),included=ids.cortex.concat(ids.frontal);
 const means=Array.from({length:8},(_,ch)=>{
  let total=0;for(const i of included)total+=state.nodes[i][ch];
  return total/included.length;
 });
 const center=state.nodes[62].slice();
 const variances=Array.from({length:8},(_,ch)=>{
  let total=0;for(const i of included)total+=(state.nodes[i][ch]-means[ch])**2;
  return total/included.length;
 });
 return {tick:state.tick,cortexCount:included.length,means,variances,frontalSnapshot:center,
  sourceAddresses:included.slice().sort((a,b)=>a-b)};
}
function wag290FrontalSelect(read){
 let selected=0;
 for(let ch=1;ch<8;ch++)if(read.means[ch]>read.means[selected])selected=ch;
 return {tick:read.tick,selectedChannel:selected,score:read.means[selected],
  centerLocalValue:read.frontalSnapshot[selected],confidenceGap:
    read.means[selected]-Math.max(...read.means.filter((_,i)=>i!==selected)),
  authority:'candidate only; no actuation'};
}
function wag290Observe(state){
 const read=wag290CortexRead(state);return {read,selection:wag290FrontalSelect(read)};
}
function wag290Audit(){
 const checks={};
 const s=wag288Initial(),snapshot=JSON.stringify(s);
 const o1=wag290Observe(s),o2=wag290Observe(s);
 checks.unchangedMemory=JSON.stringify(s)===snapshot;
 checks.deterministic=JSON.stringify(o1)===JSON.stringify(o2);
 checks.includes27Once=o1.read.cortexCount===27&&o1.read.sourceAddresses.length===27&&new Set(o1.read.sourceAddresses).size===27;
 checks.centerOnce=o1.read.sourceAddresses.filter(i=>i===62).length===1;
 checks.centerAddress=o1.read.sourceAddresses.includes(62)&&wag289Role(62)==='frontal';
 checks.channelRange=o1.selection.selectedChannel>=0&&o1.selection.selectedChannel<8;
 checks.argmax=o1.selection.score===Math.max(...o1.read.means);
 const tied={means:[.5,.5,.1,.2,.3,.4,.2,.1],frontalSnapshot:Array(8).fill(0),tick:7};
 checks.tieBreak=wag290FrontalSelect(tied).selectedChannel===0;
 let t=s;for(let i=0;i<64;i++)t=wag288Tick(t,.125);
 const before=JSON.stringify(t),mass=wag288Mass(t),ot=wag290Observe(t);
 checks.postTickReadOnly=JSON.stringify(t)===before&&wag288Mass(t)===mass;
 checks.validVariance=ot.read.variances.every(v=>Number.isFinite(v)&&v>=0);
 checks.zeroCouplingUnchanged=(function(){let q=s;for(let j=0;j<20;j++)q=wag288Tick(q,0);return JSON.stringify(q.nodes)===JSON.stringify(s.nodes)})();
 checks.singleCenter=wag289Groups().frontal.length===1;
 checks.noExternalActions=o1.selection.authority==='candidate only; no actuation'&&WAG290.physicalActions===0;
 return {bound:'WAG-290',checks,pass:Object.values(checks).every(Boolean),
  cortexIncluded:27,center:62,authority:'READ_ONLY_CANDIDATE',baselineModified:false};
}
if(typeof module!=='undefined')module.exports={WAG290,wag290CortexRead,wag290FrontalSelect,wag290Observe,wag290Audit};
