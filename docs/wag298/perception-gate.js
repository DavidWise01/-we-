/* WAG-298 · shadow-to-signal perception · .dlw
 * Three frontal forms remain one address. Their observation privileges
 * open at progressively higher illumination levels.
 * No latent channel data may escape when forms are shadowed.
 * Abstract measurement interface; NOT photon simulation.
 */
const WAG298=Object.freeze({
 center:62,geometry:'{[()]}',
 forms:Object.freeze([
  Object.freeze({name:'[1]',threshold:.25,source:'frontal-local'}),
  Object.freeze({name:'{1}',threshold:.5,source:'cortex-inclusive'}),
  Object.freeze({name:'(1)',threshold:.75,source:'cortex-shell'})
 ]),
 minimumForms:2,minimumMargin:.005,physicalActions:0
});
function wag298Read(state,illumination){
 if(!Number.isFinite(illumination)||illumination<0||illumination>1)throw Error('invalid illumination');
 const groups=wag289Groups(),cortex=groups.cortex.concat(groups.frontal);
 const visible=WAG298.forms.filter(f=>illumination>=f.threshold);
 const records=visible.map(form=>{
  let scores;
  if(form.name==='[1]')scores=state.nodes[62].slice();
  else if(form.name==='{1}')scores=Array.from({length:8},(_,ch)=>cortex.reduce((sum,id)=>sum+state.nodes[id][ch],0)/27);
  else scores=Array.from({length:8},(_,ch)=>groups.cortex.reduce((sum,id)=>sum+state.nodes[id][ch],0)/26);
  return {form:form.name,source:form.source,scores};
 });
 const evidenceCount=records.length;
 let candidate=null,margin=null;
 if(evidenceCount>=WAG298.minimumForms){
  const means=Array.from({length:8},(_,ch)=>records.reduce((sum,r)=>sum+r.scores[ch],0)/evidenceCount);
  let winning=0;for(let ch=1;ch<8;ch++)if(means[ch]>means[winning])winning=ch;
  const sorted=means.slice().sort((a,b)=>b-a);
  margin=sorted[0]-sorted[1];
  if(margin>=WAG298.minimumMargin)candidate=winning;
 }
 return wag291DeepFreeze({tick:state.tick,illumination,visibleForms:visible.map(f=>f.name),
   evidence:records,observationCount:evidenceCount,
   candidate,margin,abstain:candidate===null,
   status:evidenceCount===0?'SHADOW':candidate===null?'INSUFFICIENT_EVIDENCE':'OBSERVED_CANDIDATE',
   authority:'READ_ONLY'});
}
function wag298Evaluate(source){
 const initial=JSON.stringify(source),levels=[0,.2,.25,.49,.5,.74,.75,1];
 const receipts=levels.map(level=>{
  const p=wag298Read(source,level);
  return {level,forms:p.visibleForms.slice(),status:p.status,candidate:p.candidate,
   abstain:p.abstain,evidenceCount:p.observationCount};
 });
 if(JSON.stringify(source)!==initial)throw Error('authoritative source mutated');
 return wag291DeepFreeze({bound:'WAG-298',tick:source.tick,
  receipts,scope:'visibility gating for abstract measurements, no physical optics',
  authority:'READ_ONLY',physicalActions:0});
}
function wag298Audit(){
 const state=wag288Initial(),source=JSON.stringify(state),
 dark=wag298Read(state,0),early=wag298Read(state,.49),
 mid=wag298Read(state,.5),full=wag298Read(state,1);
 const comparison=state.nodes.map(n=>n.slice());
 comparison[62]=Array(8).fill(0).map((_,i)=>i===7?1:0);
 const diffDark=wag298Read({...state,nodes:comparison},0);
 const checks={
   threeForms:WAG298.forms.map(x=>x.name).join('|')==='[1]|{1}|(1)',
   nestedAperture:WAG298.geometry==='{[()]}',
   darkNoEvidence:dark.evidence.length===0&&dark.visibleForms.length===0,
   darkAbstains:dark.candidate===null&&dark.abstain,
   darkNoLeak:JSON.stringify(dark)===JSON.stringify(diffDark),
   oneFormCannotDecide:early.observationCount===1&&early.abstain,
   secondFormOpens:mid.observationCount===2,
   allThreeOpen:full.observationCount===3,
   monotonicVisibility:WAG298.forms.every(f=>wag298Read(state,f.threshold).visibleForms.includes(f.name)),
   immutable:Object.isFrozen(full)&&Object.isFrozen(full.evidence)&&Object.isFrozen(full.evidence[0].scores),
   readOnly:source===JSON.stringify(state),
   centerStillOne:wag289Groups().frontal.length===1&&WAG298.center===62,
   resultSequence:wag298Evaluate(state).receipts.length===8,
   deterministic:JSON.stringify(wag298Evaluate(state))===JSON.stringify(wag298Evaluate(state)),
   baselinePass:wag297Audit().pass,
   noActuation:WAG298.physicalActions===0
 };
 return {bound:'WAG-298',pass:Object.values(checks).every(Boolean),checks,
   examples:{dark:dark.status,oneForm:early.status,partial:mid.status,full:full.status},
   phaseProgress:3/8};
}
if(typeof module!=='undefined')module.exports={WAG298,wag298Read,wag298Evaluate,wag298Audit};
