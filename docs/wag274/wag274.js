/* WAG-274 · paired unfamiliar forcing · {a{b}} · Phase III turn 6/12
  Predeclared four OOD force patterns, disjoint 6101..6103 seeds.
  Fixed WAG272 weights, frozen WAG264 policy, same forcing for both arms.
  Predictions at tick t use only observations through t.
  Labels are computed after run from future 24 ticks (never online).
  One physical engine and one source ancestry; no independent physics claim.
*/
const WAG274_SEEDS=[6101,6102,6103],WAG274_DURATIONS=[240,480],
 WAG274_CAP=[8,13],WAG274_FAMILIES=['scar','combined'],
 WAG274_FORCES=['antiphase','surge-crash','shrinking-cycle','dual-burst'];
const WAG274_SAMPLE_EVERY=24,WAG274_FORECAST=24;
function wag274Force(t,kind,seed){
 const shift=seed%17,phase=t+shift,cycle=Math.floor(t/120);
 if(kind==='antiphase'){
   return {energy:(phase%60<19)?-.006:0,
    material:(phase%60>=30&&phase%60<51)?-.0018:0};
 }
 if(kind==='surge-crash'){
   const p=phase%160;return {energy:p<26?.0015:p>=65&&p<93?-.012:0,
    material:p>=67&&p<94?-.00125:0};
 }
 if(kind==='shrinking-cycle'){
   const interval=Math.max(13,56-5*cycle),p=phase%interval;
   return {energy:p<Math.max(3,Math.floor(interval*.24))?-.009:0,
    material:p>=Math.floor(interval*.5)&&p<Math.floor(interval*.7)?-.0016:0};
 }
 if(kind==='dual-burst'){
   const p=phase%137;
   return {energy:[9,10,11,56,57,115].includes(p)?-.09:0,
    material:(p>=9&&p<=14)||(p>=113&&p<=118)?-.007:0};
 }
 throw Error('Unsupported WAG274 forcing');
}
function wag274Run(cap,family,seed,duration,force,mode,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 if(!WAG274_FORCES.includes(force)||!WAG274_DURATIONS.includes(duration)||
    !['mesh','frozen'].includes(mode))throw Error('Invalid WAG274 run');
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const gate={level:'normal',alarmStreak:0,clearStreak:0,changes:[]};
 let memory=null,lastRepair=-100,repairs=0,rejects=0;
 const trace=[],predictions=[];
 const ledger={lastEnergy:x.s.energy,lastMaterial:x.material,continuity:0,
   energyOut:0,materialOut:0,energyIn:0,materialIn:0,charge:0};
 for(let t=0;t<duration;t++){
  ledger.continuity=Math.max(ledger.continuity,
   Math.abs(ledger.lastEnergy-x.s.energy),Math.abs(ledger.lastMaterial-x.material));
  const mesh=wag272Mesh(x,lastRepair,memory);memory=mesh.memory;
  if(t%WAG274_SAMPLE_EVERY===0&&t+WAG274_FORECAST<=duration){
   predictions.push({tick:t,score:mesh.a.risk,request:mesh.b.request,
    reserve:mesh.a.reserve,permit:mesh.a.permit});
  }
  const action=mode==='mesh'?mesh.action:
   wag263Select(x,models,horizon,lastRepair,wag263Gate(x,gate),'baseline').action;
  const spent=x.materialSpent;step244(x,action);
  const actual=x.s.trace.at(-1).maintenance;
  if(action!==actual&&action!=='abstain')rejects++;
  if(actual!=='abstain'){repairs++;lastRepair=t}
  ledger.charge+=x.materialSpent-spent;
  const z=wag274Force(t,force,seed),preE=x.s.energy,preM=x.material;
  x.s.energy=wag272Clamp(preE+z.energy);x.material=wag272Clamp(preM+z.material);
  const dE=x.s.energy-preE,dM=x.material-preM;
  ledger.energyOut+=Math.max(0,-dE);ledger.materialOut+=Math.max(0,-dM);
  ledger.energyIn+=Math.max(0,dE);ledger.materialIn+=Math.max(0,dM);
  ledger.lastEnergy=x.s.energy;ledger.lastMaterial=x.material;
  const last=x.s.trace.at(-1);last.energy=x.s.energy;last.material=x.material;
  trace.push({tick:t,energy:x.s.energy,material:x.material,
   integrity:last.integrity,action:actual,risk:mesh.a.risk});
 }
 for(const p of predictions){
  const next=trace.slice(p.tick+1,p.tick+1+WAG274_FORECAST);
  if(next.length!==WAG274_FORECAST)throw Error('Incomplete prediction window');
  p.outcome=next.some(z=>z.energy<=.08||z.integrity<=.15);
 }
 const pending=x.queue.filter(z=>z.due>=duration).reduce((s,z)=>s+z.amount,0);
 const residual=Math.max(
  Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84),
  Math.abs(.2+x.materialIn+ledger.materialIn-x.materialSpent-ledger.materialOut-x.material),
  Math.abs(ledger.charge-x.materialSpent));
 if(residual>1e-8)throw Error('WAG274 conservation violation');
 const alive=trace.filter(z=>z.energy>.08&&z.integrity>.15).length;
 return {cap,family,seed,duration,force,mode,aliveTicks:alive,
  fullSurvival:alive===duration,
  reserveTicks:trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  meanIntegrity:x.s.area/duration,repairs,rejects,ledger,
  residual,predictions,trace};
}
function wag274Reliability(rows){
 const bins=Array.from({length:5},(_,i)=>({band:i,
  low:i*.2,high:(i+1)*.2,n:0,predSum:0,positives:0}));
 let brier=0;
 for(const r of rows){
  const p=Math.max(0,Math.min(1,r.score)),b=bins[Math.min(4,Math.floor(p*5))];
  const y=r.outcome?1:0;b.n++;b.predSum+=p;b.positives+=y;brier+=(p-y)**2;
 }
 const n=rows.length;let ece=0;
 for(const b of bins){b.meanScore=b.n?b.predSum/b.n:null;
  b.eventRate=b.n?b.positives/b.n:null;
  if(b.n)ece+=b.n/n*Math.abs(b.meanScore-b.eventRate);
  delete b.predSum;
 }
 return {n,brier:n?brier/n:null,ece:n?ece:null,
  events:rows.filter(r=>r.outcome).length,
  bins};
}
function wag274Experiment(frozen,models,horizon){
 const cases=[],rows=[],forecast=[];
 for(const duration of WAG274_DURATIONS)
 for(const family of WAG274_FAMILIES)
 for(const force of WAG274_FORCES)
 for(const cap of WAG274_CAP)
 for(const seed of WAG274_SEEDS){
  const pair={};
  for(const mode of ['frozen','mesh']){
   const r=wag274Run(cap,family,seed,duration,force,mode,frozen,models,horizon);
   const row={duration,family,force,cap,seed,mode,aliveTicks:r.aliveTicks,
    fullSurvival:r.fullSurvival,reserveTicks:r.reserveTicks,
    meanIntegrity:r.meanIntegrity,repairs:r.repairs,residual:r.residual,
    continuity:r.ledger.continuity};
   rows.push(row);pair[mode]=row;
   if(mode==='mesh')for(const p of r.predictions)forecast.push({...p,
    duration,family,force,cap,seed});
  }
  cases.push({duration,family,force,cap,seed,
   aliveDelta:pair.mesh.aliveTicks-pair.frozen.aliveTicks,
   reserveDelta:pair.mesh.reserveTicks-pair.frozen.reserveTicks,
   integrityDelta:pair.mesh.meanIntegrity-pair.frozen.meanIntegrity});
 }
 const aggregates=Object.fromEntries(WAG274_DURATIONS.map(d=>[d,
  Object.fromEntries(['frozen','mesh'].map(mode=>{
   const rr=rows.filter(x=>x.duration===d&&x.mode===mode),n=rr.length;
   return [mode,{n,fullSurvival:rr.filter(x=>x.fullSurvival).length,
    meanAliveRatio:rr.reduce((a,z)=>a+z.aliveTicks/z.duration,0)/n,
    meanReserveRatio:rr.reduce((a,z)=>a+z.reserveTicks/z.duration,0)/n,
    meanIntegrity:rr.reduce((a,z)=>a+z.meanIntegrity,0)/n,
    meanRepairs:rr.reduce((a,z)=>a+z.repairs,0)/n}];
  }))]));
 const risk=wag274Reliability(forecast);
 return {bound:'WAG-274',phase:'WAG-III',turn:6,primitive:'{a{b}}',
  forceNames:WAG274_FORCES,seeds:WAG274_SEEDS,aggregates,
  calibration:risk,cases,rows,forecast,
  examples:{falseSafe:forecast.filter(x=>x.score<.35&&x.outcome).slice(0,20),
   highFalseAlarms:forecast.filter(x=>x.score>.65&&!x.outcome).slice(0,20)},
  summary:{policyRuns:rows.length,matchedConditions:cases.length,
   meshAliveRegressions:cases.filter(x=>x.aliveDelta<0).length,
   meshIntegrityRegressions:cases.filter(x=>x.integrityDelta< -1e-12).length,
   meshIntegrityImprovements:cases.filter(x=>x.integrityDelta>1e-12).length,
   maxResidual:Math.max(...rows.map(z=>z.residual)),
   maxContinuity:Math.max(...rows.map(z=>z.continuity))},
  limitations:['New forcing patterns still use the same simulator family',
   'Neural weights and frozen WAG261 policy are not changed',
   'Forecasts are made before outcomes; labels attached only offline',
   'Repeated windows within each trajectory are statistically dependent',
   'No controller promotion from this evaluation']};
}
if(typeof module!=='undefined')module.exports={wag274Force,wag274Run,wag274Reliability,wag274Experiment};
