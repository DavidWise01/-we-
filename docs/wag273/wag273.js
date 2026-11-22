/* WAG-273 · {a{b}} calibration audit · Phase III 5/12 · .dlw
   Prediction before outcomes. Outer a.risk predicts next-24-tick viability
   breach (energy<=.08 or integrity<=.15). Inner b.request ranks repair
   utility against a 12-tick paired no-followup-action counterfactual.
   Counterfactual future is used OFFLINE to generate labels only.
   Fixed recurrent mesh weights, zero tuning or policy promotion.
*/
const WAG273_SEEDS=[6001,6002,6003];
const WAG273_FAMILIES=['scar','combined'];
const WAG273_STRESS=['late-collapse','double-shock','intermittent','resource-squeeze'];
const WAG273_CAP=[8,13],WAG273_DURATIONS=[240,480];
const WAG273_HORIZON=24,WAG273_VALUE_HORIZON=12,WAG273_SAMPLE_STEP=24;
const WAG273_BINS=5;
function wag273Viability(z){return z.energy>.08&&z.integrity>.15}
function wag273Bins(rows,scoreKey,labelKey){
 const bins=Array.from({length:WAG273_BINS},(_,i)=>({bin:i,low:i/WAG273_BINS,
  high:(i+1)/WAG273_BINS,n:0,predSum:0,positive:0}));
 let brier=0,positive=0,falseSafe=0;
 for(const z of rows){
  const p=Math.max(0,Math.min(1,z[scoreKey])),y=z[labelKey]?1:0,
    index=Math.min(WAG273_BINS-1,Math.floor(p*WAG273_BINS));
  const b=bins[index];b.n++;b.predSum+=p;b.positive+=y;
  positive+=y;brier+=(p-y)**2;if(p<.35&&y)falseSafe++;
 }
 const n=rows.length;
 let ece=0;
 for(const b of bins){b.meanPred=b.n?b.predSum/b.n:null;
  b.eventRate=b.n?b.positive/b.n:null;
  if(b.n)ece+=b.n/n*Math.abs(b.meanPred-b.eventRate);
  delete b.predSum;
 }
 return {n,positives:positive,baseRate:n?positive/n:null,
  brier:n?brier/n:null,ece:n?ece:null,
  falseSafe,coverage:n?1-falseSafe/n:null,bins};
}
function wag273Branch(x,action,horizon){
 // Copies only within the offline evaluator, never in online action selection.
 const z=JSON.parse(JSON.stringify(x));
 const materialAtStart=z.material,energyAtStart=z.s.energy;
 let sumIntegrity=0,applied='abstain';
 for(let k=0;k<horizon;k++){
  const t=z.t,requested=k===0?action:'abstain';
  step244(z,requested);
  if(k===0)applied=z.s.trace.at(-1).maintenance;
  const f=wag269Stress(t,z.testStress,z.seed);
  z.s.energy=wag272Clamp(z.s.energy+f.energy);
  z.material=wag272Clamp(z.material+f.material);
  const record=z.s.trace.at(-1);record.energy=z.s.energy;record.material=z.material;
  sumIntegrity+=z.s.integrity;
 }
 return {applied,meanIntegrity:sumIntegrity/horizon,
  materialSpent:z.materialSpent-x.materialSpent,
  finalEnergy:z.s.energy,finalMaterial:z.material,
  initialMaterial:materialAtStart,initialEnergy:energyAtStart};
}
function wag273Value(x,prefer){
 const horizon=Math.min(WAG273_VALUE_HORIZON,x.duration-x.t);
 if(horizon<=0)return {eligible:false,benefit:null,label:null};
 const no=wag273Branch(x,'abstain',horizon),yes=wag273Branch(x,prefer,horizon);
 if(yes.applied!==prefer)return {eligible:false,benefit:null,label:null,
  abstain:no.meanIntegrity,attempt:yes.meanIntegrity};
 // Recovery value, net of explicitly weighted material and energy opportunity
 // cost, is a diagnostic utility, not a physical conservation equation.
 const integrityBenefit=yes.meanIntegrity-no.meanIntegrity;
 const energyCost=Math.max(0,no.finalEnergy-yes.finalEnergy);
 const materialCost=Math.max(0,yes.materialSpent-no.materialSpent);
 const value=integrityBenefit-.1*energyCost-.2*materialCost;
 return {eligible:true,benefit:value,label:value>0,
  integrityBenefit,energyCost,materialCost,horizon};
}
function wag273Run(cap,family,seed,duration,stress,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 const x=start244(cap,family,seed,duration);
 x.modelTable=models.train250.source;x.testStress=stress;
 let neuralMemory=null,lastRepair=-100;
 const trace=[],predictions=[],valueLabels=[];
 const ledger={lastEnergy:x.s.energy,lastMaterial:x.material,continuityMax:0,
  externalEnergy:0,externalMaterial:0,externalEnergyIn:0,externalMaterialIn:0};
 for(let t=0;t<duration;t++){
  ledger.continuityMax=Math.max(ledger.continuityMax,
   Math.abs(x.s.energy-ledger.lastEnergy),Math.abs(x.material-ledger.lastMaterial));
  const mesh=wag272Mesh(x,lastRepair,neuralMemory);
  neuralMemory=mesh.memory;
  if(t%WAG273_SAMPLE_STEP===0){
   predictions.push({tick:t,predicted:mesh.a.risk,
    request:mesh.b.request,prefer:mesh.prefer,
    a:{...mesh.a},b:{...mesh.b},energy:x.s.energy,material:x.material});
   const val=wag273Value(x,mesh.prefer);
   if(val.eligible)valueLabels.push({tick:t,predicted:mesh.b.request,label:val.label,
    benefit:val.benefit,integrityBenefit:val.integrityBenefit,
    materialCost:val.materialCost,energyCost:val.energyCost,prefer:mesh.prefer});
  }
  const requested=mesh.action;step244(x,requested);
  const actual=x.s.trace.at(-1).maintenance;
  if(actual!=='abstain')lastRepair=t;
  const forcing=wag269Stress(t,stress,seed);
  const e0=x.s.energy,m0=x.material;
  x.s.energy=wag272Clamp(e0+forcing.energy);
  x.material=wag272Clamp(m0+forcing.material);
  const de=x.s.energy-e0,dm=x.material-m0;
  ledger.externalEnergy+=Math.max(0,-de);ledger.externalMaterial+=Math.max(0,-dm);
  ledger.externalEnergyIn+=Math.max(0,de);ledger.externalMaterialIn+=Math.max(0,dm);
  ledger.lastEnergy=x.s.energy;ledger.lastMaterial=x.material;
  const z=x.s.trace.at(-1);z.energy=x.s.energy;z.material=x.material;
  trace.push({tick:t,energy:x.s.energy,material:x.material,integrity:z.integrity,
   action:actual,risk:mesh.a.risk,repairScore:mesh.b.request});
 }
 for(const p of predictions){
  // Future outcome is read ONLY after completing the trajectory.
  const future=trace.slice(p.tick+1,Math.min(trace.length,p.tick+WAG273_HORIZON+1));
  p.label=future.some(z=>!wag273Viability(z));
  p.observedWindow=future.length;
 }
 const pending=x.queue.filter(q=>q.due>=duration).reduce((v,q)=>v+q.amount,0);
 const cacheResidual=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const materialResidual=Math.abs(.2+x.materialIn+ledger.externalMaterialIn-
  x.materialSpent-ledger.externalMaterial-x.material);
 if(cacheResidual>1e-8||materialResidual>1e-8)throw Error('ledger failure');
 return {cap,family,seed,duration,stress,predictions,valueLabels,
  aliveTicks:trace.filter(wag273Viability).length,
  ledger:{...ledger,cacheResidual,materialResidual},trace};
}
function wag273Experiment(frozen,models,horizon){
 const risk=[],value=[],cases=[];
 for(const duration of WAG273_DURATIONS)for(const family of WAG273_FAMILIES)
 for(const stress of WAG273_STRESS)for(const cap of WAG273_CAP)
 for(const seed of WAG273_SEEDS){
  const r=wag273Run(cap,family,seed,duration,stress,frozen,models,horizon);
  for(const p of r.predictions)risk.push({duration,family,stress,cap,seed,...p});
  for(const v of r.valueLabels)value.push({duration,family,stress,cap,seed,...v});
  cases.push({duration,family,stress,cap,seed,
   predictions:r.predictions.length,valueLabels:r.valueLabels.length,alive:r.aliveTicks,
   ledger:r.ledger});
 }
 const riskBins=wag273Bins(risk,'predicted','label'),
  valueBins=wag273Bins(value,'predicted','label');
 const badRisk=risk.filter(z=>z.predicted<.35&&z.label).slice(0,20);
 const badValue=value.filter(z=>z.predicted>=.65&&!z.label).slice(0,20);
 return {bound:'WAG-273',phase:'WAG-III',turn:5,primitive:'{a{b}}',
  calibrationDefinition:{outer:'a.risk forecast of any future viability breach within 24 ticks',
   inner:'b.request score for positive 12-tick no-followup repair advantage',
   valueUtility:'integrity benefit − 0.1 × energy cost − 0.2 × material cost',
   trainableWeights:false},
  riskCalibration:riskBins,valueCalibration:valueBins,cases,riskRows:risk,valueRows:value,
  failureExamples:{falseSafe:badRisk,falseWorth:badValue},
  summary:{runs:cases.length,riskObservations:risk.length,valueObservations:value.length,
   maxCacheResidual:Math.max(...cases.map(z=>z.ledger.cacheResidual)),
   maxMaterialResidual:Math.max(...cases.map(z=>z.ledger.materialResidual)),
   continuityMax:Math.max(...cases.map(z=>z.ledger.continuityMax))},
  cautions:['Scores were not fitted as probabilities; this is a falsification of their calibration',
   'Inner utility labels are branch-based diagnostics and only sampled at physically eligible moments',
   'Paired counterfactual branches share deterministic simulator; they are not independent evidence',
   'No weights changed; no policy promoted']};
}
if(typeof module!=='undefined')module.exports={wag273Viability,wag273Bins,wag273Value,wag273Run,wag273Experiment};
