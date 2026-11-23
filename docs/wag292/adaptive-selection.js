/* WAG-292 · read-only adaptive selection / held-out stability · .dlw
  Fixed policies tested against deterministic synthetic channel perturbations.
  Candidate evaluation cannot alter the 125 original silo memories.
  A promotion requires held-out improvement plus perfect held-out agreement.
*/
const WAG292=Object.freeze({policies:Object.freeze([0,.25,.5,.75,1]),
  trainingAmplitude:Object.freeze([0,.01,.02,.04]),holdoutAmplitude:Object.freeze([0,.007,.017,.031,.05]),
  trainingSeed:292,holdoutSeed:9292,trainingTrials:8,holdoutTrials:8,
  scope:'synthetic perturbed cortex readouts; no actual learning or physical actuation'});
function wag292Choose(read,alpha){
 const scores=read.means.map((mean,i)=>(1-alpha)*mean+alpha*read.frontalSnapshot[i]);
 let channel=0;for(let i=1;i<8;i++)if(scores[i]>scores[channel])channel=i;
 const sorted=scores.slice().sort((a,b)=>b-a);
 return {channel,score:scores[channel],margin:sorted[0]-sorted[1],alpha};
}
function wag292Noise(read,delta,trial,seed){
 // Deterministic bounded noise, distinct training/holdout seeds, both
 // cortex aggregation and central frontal snapshot are perturbed.
 function noise(ch,salt){return (((ch*37+trial*19+seed*11+salt*23)%17)-8)/8}
 return {...read,means:read.means.map((v,i)=>Math.max(0,Math.min(1,v+delta*noise(i,1)))),
  frontalSnapshot:read.frontalSnapshot.map((v,i)=>Math.max(0,Math.min(1,v+delta*noise(i,3))))};
}
function wag292Trial(read,alpha,amplitudes,seed,count){
 const baseline=wag292Choose(read,alpha),cases=[];
 for(const delta of amplitudes)for(let t=0;t<count;t++){
  const answer=wag292Choose(wag292Noise(read,delta,t,seed),alpha);
  cases.push({delta,trial:t,channel:answer.channel,stable:answer.channel===baseline.channel});
 }
 return {chosen:baseline,agreement:cases.filter(x=>x.stable).length/cases.length,
  trials:cases.length,unstable:cases.filter(x=>!x.stable).length,
  byAmplitude:amplitudes.map(a=>({delta:a,
    agreement:cases.filter(x=>x.delta===a&&x.stable).length/count}))};
}
function wag292Evaluate(state){
 const source=JSON.stringify(state),read=wag290CortexRead(state);
 const policies=WAG292.policies.map(alpha=>({
  alpha,train:wag292Trial(read,alpha,WAG292.trainingAmplitude,WAG292.trainingSeed,WAG292.trainingTrials),
  holdout:wag292Trial(read,alpha,WAG292.holdoutAmplitude,WAG292.holdoutSeed,WAG292.holdoutTrials)
 }));
 const baseline=policies[0];
 // Policy selection uses training ONLY, with fixed tie break favoring smaller alpha.
 const ranked=policies.slice().sort((a,b)=>b.train.agreement-a.train.agreement||
   b.train.chosen.margin-a.train.chosen.margin||a.alpha-b.alpha);
 const selected=ranked[0];
 // Held-out gate cannot be optimized after seeing test performance.
 const improvement=selected.alpha!==0&&selected.holdout.agreement>baseline.holdout.agreement;
 const accepted=improvement&&selected.holdout.agreement===1&&
   selected.train.agreement===1&&selected.holdout.chosen.margin>0;
 const receipt=wag291DeepFreeze({bound:'WAG-292',provenance:{tick:state.tick,
  trainingSeed:WAG292.trainingSeed,holdoutSeed:WAG292.holdoutSeed,
  rule:'train rank; held-out strict improvement; perfect train and holdout'},
  policies,selectedAlpha:selected.alpha,baselineHoldout:baseline.holdout.agreement,
  selectedHoldout:selected.holdout.agreement,
  selectedChannel:selected.holdout.chosen.channel,
  verdict:accepted?'FROZEN':'UNFROZEN',
  reason:accepted?'strict held-out improvement and full agreement':'no qualifying independently evaluated improvement',
  physicalActions:0});
 if(JSON.stringify(state)!==source)throw Error('observation mutated silo memory');
 return receipt;
}
function wag292LedgerAppend(ledger,receipt){
 if(!Object.isFrozen(receipt)||receipt.bound!=='WAG-292')throw Error('invalid receipt');
 if(ledger.length&&receipt.provenance.tick<ledger[ledger.length-1].provenance.tick)throw Error('non-monotone tick');
 return Object.freeze([...ledger,receipt]);
}
function wag292Audit(){
 const s=wag288Initial(),original=JSON.stringify(s),a=wag292Evaluate(s),b=wag292Evaluate(s);
 const checks={deterministic:JSON.stringify(a)===JSON.stringify(b),
 readOnly:JSON.stringify(s)===original,
 fivePolicies:a.policies.length===5,
 disjointSeed:WAG292.trainingSeed!==WAG292.holdoutSeed,
 trainingCount:a.policies.every(p=>p.train.trials===32),
 holdoutCount:a.policies.every(p=>p.holdout.trials===40),
 noFalseFreeze:a.verdict!=='FROZEN'||(a.selectedAlpha!==0&&a.selectedHoldout===1&&a.selectedHoldout>a.baselineHoldout),
 immutable:Object.isFrozen(a)&&Object.isFrozen(a.policies)&&Object.isFrozen(a.policies[0].holdout.byAmplitude),
 appendOnly:(()=>{const l=Object.freeze([]),n=wag292LedgerAppend(l,a);return l.length===0&&n.length===1&&Object.isFrozen(n)})(),
 independentSilos:new Set(s.nodes).size===125,
 conserved:Math.abs(wag288Mass(s)-wag288Mass(wag288Tick(s,.125)))<1e-9,
 baselinesPass:wag288Audit().pass&&wag289Audit().pass&&wag290Audit().pass&&wag291Audit().pass,
 noActions:a.physicalActions===0};
 return {bound:'WAG-292',pass:Object.values(checks).every(Boolean),checks,example:{verdict:a.verdict,
 selectedAlpha:a.selectedAlpha,baselineHoldout:a.baselineHoldout,selectedHoldout:a.selectedHoldout},
 previousFilesModified:false};
}
if(typeof module!=='undefined')module.exports={WAG292,wag292Choose,wag292Noise,wag292Trial,wag292Evaluate,wag292LedgerAppend,wag292Audit};
