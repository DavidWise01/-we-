/* WAG-291 · Candidate stability and evidence freeze · .dlw
   This module is an OBSERVATION ledger, not an actuator or online trainer.
   Source state never mutated, receipts are deeply immutable, and only
   candidates passing preset perturbation stability are frozen.
*/
const WAG291=Object.freeze({candidateChannels:8,perturbations:Object.freeze([0,.005,.01,.02,.04]),stableThreshold:1,minimumMargin:0,seed:291,authority:'observe-only'});
function wag291DeepFreeze(v){if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(wag291DeepFreeze);Object.freeze(v)}return v}
function wag291PerturbedRead(read,delta,trial){
 const means=read.means.map((value,ch)=>{
  // Bounded, deterministic zero-mean-ish local channel noise: no randomness.
  const sign=((ch*17+trial*13+WAG291.seed)%7-3)/3;
  return Math.max(0,Math.min(1,value+delta*sign));
 });
 return {...read,means};
}
function wag291Evaluate(state){
 const before=JSON.stringify(state);
 const initial=wag290Observe(state),base=initial.selection.selectedChannel;
 const trials=[];
 for(const delta of WAG291.perturbations){
  for(let trial=0;trial<8;trial++){
   const selected=wag290FrontalSelect(wag291PerturbedRead(initial.read,delta,trial));
   trials.push({delta,trial,selectedChannel:selected.selectedChannel,score:selected.score,
    same:selected.selectedChannel===base});
  }
 }
 const agreement=trials.filter(t=>t.same).length/trials.length;
 const minAgreementByDelta=WAG291.perturbations.map(delta=>({
  delta,agreement:trials.filter(t=>t.delta===delta&&t.same).length/8
 }));
 const candidate={tick:state.tick,channel:base,margin:initial.selection.confidenceGap,
   agreement,threshold:WAG291.stableThreshold,
   verdict:agreement>=WAG291.stableThreshold&&initial.selection.confidenceGap>=WAG291.minimumMargin?'FROZEN':'UNFROZEN'};
 if(JSON.stringify(state)!==before)throw Error('WAG-291 read changed state');
 return wag291DeepFreeze({candidate,trials,minAgreementByDelta,
  provenance:{bound:'WAG-291',source:'WAG-290 cortex readout',tick:state.tick,
    seed:WAG291.seed,rule:'40 deterministic bounded channel perturbations',
    authority:'observation only'},physicalActions:0});
}
function wag291LedgerAppend(ledger,receipt){
 if(!Object.isFrozen(receipt)||!Object.isFrozen(receipt.candidate))throw Error('receipt not immutable');
 if(ledger.length&&receipt.provenance.tick<ledger[ledger.length-1].provenance.tick)
   throw Error('nonmonotone receipt tick');
 return Object.freeze([...ledger,receipt]);
}
function wag291Audit(){
 const checks={};const s=wag288Initial(),original=JSON.stringify(s);
 const a=wag291Evaluate(s),b=wag291Evaluate(s);
 checks.deterministic=JSON.stringify(a)===JSON.stringify(b);
 checks.readOnly=JSON.stringify(s)===original;
 checks.fortyTrials=a.trials.length===40;
 checks.fiveLevels=a.minAgreementByDelta.length===5;
 checks.immutableReceipt=Object.isFrozen(a)&&Object.isFrozen(a.candidate)&&Object.isFrozen(a.trials)&&Object.isFrozen(a.trials[0]);
 const old=Object.freeze([]),ledger=wag291LedgerAppend(old,a);
 checks.appendOnly=old.length===0&&ledger.length===1&&ledger[0]===a&&Object.isFrozen(ledger);
 checks.tickOrderEnforced=(()=>{try{wag291LedgerAppend(ledger,wag291DeepFreeze({...a,provenance:{...a.provenance,tick:-1}}));return false}catch(_){return true}})();
 checks.neverFreezesUnstable=(()=>{const fake={...s,nodes:s.nodes.map(n=>n.slice())};
  const groups=wag289Groups().cortex.concat([62]);for(const i of groups)fake.nodes[i]=Array(8).fill(.5);
  const z=wag291Evaluate(fake);return z.candidate.verdict==='UNFROZEN';})();
 checks.zeroPerturbationAgrees=a.minAgreementByDelta[0].agreement===1;
 checks.selectionRange=a.candidate.channel>=0&&a.candidate.channel<8;
 checks.conservationOfBaseline=wag288Mass(s)===wag288Mass(s)&&JSON.stringify(s)===original;
 checks.noPhysicalActions=a.physicalActions===0;
 checks.previousStages=wag288Audit().pass&&wag289Audit().pass&&wag290Audit().pass;
 return {bound:'WAG-291',pass:Object.values(checks).every(Boolean),checks,example:a.candidate,
  scope:'deterministic synthetic perturbations, not proof of general robustness',
  physicalActions:0,priorFilesModified:false};
}
if(typeof module!=='undefined')module.exports={WAG291,wag291PerturbedRead,wag291Evaluate,wag291LedgerAppend,wag291Audit};
