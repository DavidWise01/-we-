/* WAG-284 · Delayed relative repair-value readout · Phase IV 4/12 · .dlw
 Frozen WAG-261 vs unpromoted WAG-276 crystal under same forcing.
 The target is observed delayed paired-POLICY advantage, not a single-action
 causal effect. Read-only 32-feature readout from CURRENT/PREVIOUS reference
 trajectory, never from the future or crystal trajectory. Physically executed
 simulator actions remain assigned to the original frozen policy or existing
 unmodified research arm. No learned policy chooses an action.
*/
const WAG284_CONFIG=Object.freeze({
 primitive:'---@---@---@---@---{} → {\\a{b/}}',
 trainSeeds:[7101,7102,7103],heldoutSeeds:[7201,7202],
 durations:[240],forces:['antiphase','dual-burst'],
 families:['scar','combined'],capacities:[8,13],
 sampleTicks:[48,72,96,120,144,168,192],
 horizons:[24,48],featureCount:32,epochs:120,rate:.035,
 ridge:.003,materialValue:.25,
 target:'delayed relative crystal-vs-reference integrity gain plus material reserve advantage',
 policyAuthority:'WAG-261; read-only observation only'
});
function wag284RawFeatures(trace,t){
 const z=trace[t],prev=trace[Math.max(0,t-12)],prior=trace[Math.max(0,t-24)];
 const norm=x=>Math.max(0,Math.min(1,x));
 const a=[norm(z.integrity),norm(z.energy),norm(z.material),
  norm(prev.integrity),norm(prev.energy),norm(prev.material),
  norm(prior.integrity),norm(prior.energy),norm(prior.material),
  norm(.5+5*(z.integrity-prev.integrity)),
  norm(.5+5*(z.energy-prev.energy)),
  norm(.5+5*(z.material-prev.material)),
  norm(.5+5*(prev.integrity-prior.integrity)),
  norm(.5+5*(prev.energy-prior.energy)),
  norm(.5+5*(prev.material-prior.material)),
  z.action==='prevent'?1:0,z.action==='rebuild'?1:0,
  z.action==='abstain'?1:0,
  t/240,
  norm(1-z.integrity),norm(1-z.material),norm(1-z.energy),
  norm(z.integrity*z.energy),norm(z.integrity*z.material),
  norm(z.energy*z.material),norm(Math.abs(z.integrity-prev.integrity)*8),
  norm(Math.abs(z.material-prev.material)*8),
  norm(Math.abs(z.energy-prev.energy)*8),
  norm(z.integrity*z.integrity),norm(z.energy*z.energy),
  norm(z.material*z.material),1];
 if(a.length!==WAG284_CONFIG.featureCount||a.some(x=>!Number.isFinite(x)))
  throw Error('invalid current-only feature vector');
 return a;
}
function wag284Label(f,c,t,h){
 const end=t+h;
 const base=(c[t].integrity-f[t].integrity)+
  WAG284_CONFIG.materialValue*(c[t].material-f[t].material);
 const future=(c[end].integrity-f[end].integrity)+
  WAG284_CONFIG.materialValue*(c[end].material-f[end].material);
 return future-base;
}
function wag284Data(frozen,models,horizon,seeds){
 const rows=[],scenarios=[];
 for(const seed of seeds)
 for(const family of WAG284_CONFIG.families)
 for(const force of WAG284_CONFIG.forces)
 for(const cap of WAG284_CONFIG.capacities){
  const opts=[cap,family,seed,240,force];
  const reference=wag276Run(...opts,'frozen',frozen,models,horizon),
        crystal=wag276Run(...opts,'crystal',frozen,models,horizon);
  scenarios.push({seed,family,force,cap,referenceAlive:reference.aliveTicks,
   crystalAlive:crystal.aliveTicks});
  for(const t of WAG284_CONFIG.sampleTicks)
  for(const h of WAG284_CONFIG.horizons){
   const features=wag284RawFeatures(reference.trace,t);
   const target=wag284Label(reference.trace,crystal.trace,t,h);
   rows.push({seed,family,force,cap,t,h,features,target,
    crystalAction:crystal.trace[t].action,referenceAction:reference.trace[t].action});
  }
 }
 return {rows,scenarios};
}
function wag284Mean(rows){return rows.reduce((a,r)=>a+r.target,0)/rows.length}
function wag284Train(rows){
 const n=rows.length,mean=wag284Mean(rows);
 const mu=Array(32).fill(0),sd=Array(32).fill(0);
 for(const r of rows)for(let i=0;i<31;i++)mu[i]+=r.features[i]/n;
 for(let i=0;i<31;i++)for(const r of rows)sd[i]+=(r.features[i]-mu[i])**2/n;
 for(let i=0;i<31;i++)sd[i]=Math.max(.02,Math.sqrt(sd[i]));
 mu[31]=0;sd[31]=1;
 const weights=Array(32).fill(0),history=[];
 function vector(f){return f.map((x,i)=>i===31?1:(x-mu[i])/sd[i])}
 const xs=rows.map(r=>vector(r.features));
 for(let epoch=0;epoch<=WAG284_CONFIG.epochs;epoch++){
  let loss=0,grad=Array(32).fill(0);
  for(let j=0;j<n;j++){
   const pred=mean+weights.reduce((s,w,i)=>s+w*xs[j][i],0);
   const e=pred-rows[j].target;loss+=e*e/n;
   for(let i=0;i<32;i++)grad[i]+=2*e*xs[j][i]/n;
  }
  if(epoch%20===0||epoch===WAG284_CONFIG.epochs)
   history.push({epoch,trainMSE:loss});
  if(epoch===WAG284_CONFIG.epochs)break;
  for(let i=0;i<32;i++){
   const clipped=Math.max(-.25,Math.min(.25,grad[i]+
    (i===31?0:2*WAG284_CONFIG.ridge*weights[i])));
   weights[i]-=WAG284_CONFIG.rate*clipped;
  }
 }
 return {weights,mean,mu,sd,history};
}
function wag284Predict(model,features){
 return model.mean+model.weights.reduce((s,w,i)=>s+
  w*(i===31?1:(features[i]-model.mu[i])/model.sd[i]),0);
}
function wag284Evaluate(rows,model){
 const baseline=rows.reduce((a,r)=>a+(r.target-model.mean)**2,0)/rows.length;
 const trained=rows.reduce((a,r)=>a+(r.target-wag284Predict(model,r.features))**2,0)/rows.length;
 const mae=rows.reduce((a,r)=>a+Math.abs(r.target-wag284Predict(model,r.features)),0)/rows.length;
 const signWins=rows.filter(r=>Math.sign(wag284Predict(model,r.features))===Math.sign(r.target)).length;
 const samples=rows.map(r=>({seed:r.seed,family:r.family,force:r.force,
  cap:r.cap,t:r.t,h:r.h,target:r.target,prediction:wag284Predict(model,r.features)}));
 return {baselineMSE:baseline,trainedMSE:trained,mae,signWins,examples:rows.length,samples};
}
function wag284Experiment(frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 const train=wag284Data(frozen,models,horizon,WAG284_CONFIG.trainSeeds),
  held=wag284Data(frozen,models,horizon,WAG284_CONFIG.heldoutSeeds);
 const model=wag284Train(train.rows),
  trainScore=wag284Evaluate(train.rows,model),
  heldScore=wag284Evaluate(held.rows,model);
 return {bound:'WAG-284',phase:'WAG-IV',turn:4,config:WAG284_CONFIG,
  model,training:{count:train.rows.length,scenarios:train.scenarios,
   baselineMSE:trainScore.baselineMSE,trainedMSE:trainScore.trainedMSE},
  heldout:{count:held.rows.length,scenarios:held.scenarios,
   ...heldScore},
  summary:{trainPairs:train.rows.length,heldoutPairs:held.rows.length,
   delayedHorizonTicks:WAG284_CONFIG.horizons,
   baselineMSE:heldScore.baselineMSE,learnedMSE:heldScore.trainedMSE,
   improvementRatio:1-heldScore.trainedMSE/heldScore.baselineMSE,
   heldoutSignAccuracy:heldScore.signWins/heldScore.examples,
   physicalActionSelectionByModel:0,sourceAncestries:1},
  cautions:[
   'Labels are paired policy trajectories, NOT isolated repair-action counterfactuals',
   'Features derive only from current and past frozen-reference observations',
   'Future observations construct labels after simulation; no future feature leakage',
   'Learning is supervised and cannot directly change repairs or issue resource debits',
   'Both policies share one synthetic simulator ancestry; no independent validity claim',
   'WAG-261 baseline and Phase III archive remain immutable'
  ]};
}
if(typeof module!=='undefined')module.exports={WAG284_CONFIG,wag284RawFeatures,
 wag284Label,wag284Data,wag284Mean,wag284Train,wag284Predict,wag284Evaluate,wag284Experiment};
