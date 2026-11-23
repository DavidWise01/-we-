/* WAG-296 · Phase V / Turn 1 · Reference-independent prototype learning · .dlw
   No shell anchor copies, no target parameter in inference.
   Synthetic ground-truth labels are used ONLY to generate/train/score data.
   The eight hidden labels imprint deterministic TWO-channel patterns into
   27 local observations; readout learns per-label prototypes from TRAIN only.
   Holdout uses distinct trial IDs and disturbances. Read-only authoritative
   125-silo state, immutable evidence, no physical/software actuation.
*/
const WAG296=Object.freeze({phase:'V',step:1,plannedSteps:8,
  labels:8,trainPerClass:24,holdoutPerClass:24,channels:8,
  conditions:Object.freeze(['ordinary','site-dropout','drift','coherent-confusion']),
  confidenceFloor:.035,seed:296,physicalActions:0});
function wag296Signature(label){return [(label*3+1)%8,(label*5+2)%8]}
function wag296Pattern(label,trial,condition){
 // 27-site readout is produced independently; no references or source memory edits.
 const sites=wag289Groups().cortex.concat(wag289Groups().frontal);
 const [a,b]=wag296Signature(label),wrong=wag296Signature((label+1)%8)[0];
 return sites.map((id,j)=>Array.from({length:8},(_,ch)=>{
  const jitter=(((id*19+trial*23+ch*17+WAG296.seed*3)%29)-14)/150;
  let v=.18+jitter+(ch===a?.50:0)+(ch===b?.25:0);
  if(condition==='site-dropout'&&(j+trial)%4===0)v=.18;
  if(condition==='drift')v=v*.78+.11;
  if(condition==='coherent-confusion'){
   // Deliberately makes the next class look stronger in many observations.
   v=(.18+jitter)+(ch===wrong?.69:0)+(ch===a?.08:0);
  }
  return Math.max(0,Math.min(1,v));
 }));
}
function wag296Features(sites){
 return Array.from({length:8},(_,ch)=>sites.reduce((sum,row)=>sum+row[ch],0)/sites.length);
}
function wag296Train(){
 const prototypes=[];
 for(let label=0;label<8;label++){
  let sum=Array(8).fill(0);
  for(let trial=0;trial<WAG296.trainPerClass;trial++){
   const x=wag296Features(wag296Pattern(label,trial,'ordinary'));
   sum=sum.map((v,i)=>v+x[i]);
  }
  prototypes.push(sum.map(x=>x/WAG296.trainPerClass));
 }
 return wag291DeepFreeze({prototypes,trainingExamples:WAG296.trainPerClass*8,
  method:'nearest Euclidean class prototype learned from labeled training samples'});
}
function wag296Predict(model,features){
 const d=model.prototypes.map(proto=>proto.reduce((s,x,i)=>s+(x-features[i])**2,0));
 const rank=d.map((value,label)=>({label,value})).sort((a,b)=>a.value-b.value||a.label-b.label);
 const margin=Math.sqrt(rank[1].value)-Math.sqrt(rank[0].value);
 return {channel:margin>=WAG296.confidenceFloor?rank[0].label:null,
  abstain:margin<WAG296.confidenceFloor,margin};
}
function wag296Baseline(features){
 const max=features.reduce((best,x,i)=>x>features[best]?i:best,0);
 return max;
}
function wag296Evaluate(authority){
 const before=JSON.stringify(authority),model=wag296Train(),rows=[];
 for(const condition of WAG296.conditions){
  let correct=0,wrong=0,abstain=0,baselineCorrect=0;
  for(let label=0;label<8;label++)for(let t=0;t<WAG296.holdoutPerClass;t++){
   const features=wag296Features(wag296Pattern(label,1000+t,condition));
   const pred=wag296Predict(model,features);
   if(pred.abstain)abstain++;
   else if(pred.channel===label)correct++;
   else wrong++;
   baselineCorrect+=Number(wag296Baseline(features)===label);
  }
  rows.push({condition,correct,wrong,abstain,total:192,
   coverage:(correct+wrong)/192,accuracy:correct/192,
   baselineAccuracy:baselineCorrect/192});
 }
 if(JSON.stringify(authority)!==before)throw Error('source memory modified');
 return wag291DeepFreeze({bound:'WAG-296',phase:'V',tick:authority.tick,
  trainingExamples:model.trainingExamples,prototypes:model.prototypes,
  cases:rows,referenceAnchorsUsed:0,authority:'READ_ONLY',physicalActions:0,
  limitation:'synthetic labels created by deterministic patterns, not autonomous environmental discovery'});
}
function wag296Append(ledger,receipt){
 if(!Object.isFrozen(receipt)||receipt.bound!=='WAG-296')throw Error('invalid receipt');
 if(ledger.length&&receipt.tick<ledger[ledger.length-1].tick)throw Error('nonmonotone tick');
 return Object.freeze([...ledger,receipt]);
}
function wag296Audit(){
 const s=wag288Initial(),original=JSON.stringify(s),a=wag296Evaluate(s),b=wag296Evaluate(s);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  readOnly:JSON.stringify(s)===original,
  noAnchorCopies:a.referenceAnchorsUsed===0,
  trainCount:a.trainingExamples===192,
  disjointTrialWindows:1000>=WAG296.trainPerClass,
  eightPrototypes:a.prototypes.length===8&&a.prototypes.every(p=>p.length===8),
  fourConditions:a.cases.length===4&&a.cases.every(p=>p.total===192),
  evidenceAccounting:a.cases.every(p=>p.correct+p.wrong+p.abstain===p.total),
  completeBaseline:a.cases.every(p=>p.baselineAccuracy>=0&&p.baselineAccuracy<=1),
  nullOnLowMargin:wag296Predict(wag296Train(),Array(8).fill(.5)).abstain,
  independentSilos:new Set(s.nodes).size===125,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.prototypes)&&Object.isFrozen(a.cases[0]),
  appendOnly:(()=>{const l=Object.freeze([]),n=wag296Append(l,a);return !l.length&&n.length===1&&Object.isFrozen(n)})(),
  priorClosure:wag295Audit().pass&&wag295Audit().receipt.acceptance==='WITHHELD',
  noAction:a.physicalActions===0
 };
 return {bound:'WAG-296',pass:Object.values(checks).every(Boolean),checks,
  results:a.cases,phaseProgress:1/WAG296.plannedSteps,
  physicalActions:0};
}
if(typeof module!=='undefined')module.exports={WAG296,wag296Signature,wag296Pattern,wag296Features,wag296Train,wag296Predict,wag296Baseline,wag296Evaluate,wag296Append,wag296Audit};
