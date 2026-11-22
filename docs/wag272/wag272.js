/* WAG-272 — Two Braced Cubits Neural Mesh {a{b}} · Phase III 4/12 · .dlw
   A (outer brace): resource/survival arbiter. B (inner brace): repair valuation.
   Fixed, auditable recurrent message-passing weights, not trained weights.
   One candidate action enters authoritative step244 gate; no double spending.
   Resource guard spends no reserves speculatively; the engine charges actual costs.
   No external future forcing enters online decisions.
*/
const WAG272_SEEDS=[5901,5902,5903],WAG272_HORIZONS=[240,480];
const WAG272_FAMILIES=['scar','combined'];
const WAG272_STRESS=['late-collapse','double-shock','intermittent','resource-squeeze'];
const WAG272_CAP=[8,13],WAG272_MODES=['frozen','mesh','noRepair'];
const WAG272_COST=Object.freeze({prevent:{energy:.0012,material:.0015},rebuild:{energy:.004,material:.0035}});
const WAG272_GUARD=Object.freeze({energyReserve:.40,materialReserve:.026,scarThreshold:.012,
 minRepairGap:7});
const wag272Clamp=x=>Math.max(0,Math.min(1,x));
function wag272NeuralInputs(x,lastRepair){
 const observed=x.f[x.t].observed,s=x.s;
 const scar=1-s.ceiling,trend=x.s.trace.length>=8?
  (s.energy-x.s.trace.at(-8).energy)/8:0;
 return {energy:wag272Clamp(s.energy),material:wag272Clamp(x.material/.2),
  integrity:wag272Clamp(s.integrity),scar:wag272Clamp(scar/.14),
  pressure:wag272Clamp(observed),trend:wag272Clamp(.5+trend*16),
  timeSinceRepair:wag272Clamp((x.t-lastRepair)/16)};
}
function wag272Mesh(x,lastRepair,memory=null){
 const u=wag272NeuralInputs(x,lastRepair);
 // Three pulses over two braces, bounded by clamped [0,1] neuron channels.
 // Cross-cubit arrows a.reserve -> b.gate -> a.choice; observability only.
 const a=memory?.a?{...memory.a}:{survive:0,reserve:0,risk:0,permit:0};
 const b=memory?.b?{...memory.b}:{prevent:0,rebuild:0,urgency:0,request:0};
 const messages=[];
 for(let pass=0;pass<3;pass++){
  const prevA={...a},prevB={...b};
  a.survive=wag272Clamp(.76*(.46*u.energy+.26*u.integrity+.20*u.material+.08*u.trend)+.24*prevA.survive);
  a.reserve=wag272Clamp(.78*(.63*u.energy+.37*u.material-.16*u.pressure)+.22*prevA.reserve);
  a.risk=wag272Clamp(.80*(.50*(1-u.energy)+.30*(1-u.integrity)+.20*u.pressure)+.20*prevA.risk);
  b.urgency=wag272Clamp(.8*(.63*u.scar+.28*u.pressure+.09*(1-u.integrity))+.2*prevB.urgency);
  b.rebuild=wag272Clamp(.8*(.65*u.scar+.22*u.energy+.13*prevA.reserve)+.2*prevB.rebuild);
  b.prevent=wag272Clamp(.8*(.55*u.pressure+.23*u.energy+.22*prevA.reserve)+.2*prevB.prevent);
  b.request=wag272Clamp(.8*(Math.max(b.rebuild,b.prevent)*.70+b.urgency*.30)+.2*prevB.request);
  a.permit=wag272Clamp(.80*(.54*a.reserve+.26*a.survive+.20*prevB.request-.28*a.risk)+.20*prevA.permit);
  messages.push({pass,a:{...a},b:{...b}});
 }
 const prefer=b.rebuild>=b.prevent?'rebuild':'prevent',cost=WAG272_COST[prefer];
 const physical=prefer==='rebuild'?
  x.s.ceiling<.995&&x.s.energy>.35&&x.material>=.0035:
  u.pressure>.55&&x.material>=.0015;
 const eligible=x.s.energy>.14&&x.s.integrity>.15&&physical;
 const safety=(x.s.energy-cost.energy>=WAG272_GUARD.energyReserve)&&
  (x.material-cost.material>=WAG272_GUARD.materialReserve);
 const timing=x.t-lastRepair>=WAG272_GUARD.minRepairGap;
 const worth=prefer==='rebuild'?
  u.scar>WAG272_GUARD.scarThreshold/.14&&b.rebuild>.28:
  b.prevent>.52&&u.pressure>.55;
 const accepted=eligible&&safety&&timing&&worth&&a.permit>.34;
 return {action:accepted?prefer:'abstain',prefer,accepted,
  reasons:{eligible,safety,timing,worth,permit:a.permit>.34},
  a,b,messages,inputs:u,memory:{a:{...a},b:{...b}}};
}
function wag272Run(cap,family,seed,duration,stress,mode,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 if(!WAG272_MODES.includes(mode)||!WAG272_HORIZONS.includes(duration))throw Error('invalid WAG272 request');
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const state={level:'normal',alarmStreak:0,clearStreak:0,changes:[]};
 let lastRepair=-100,repairCount=0,requestCount=0,guardDenials=0,engineDenials=0;
 let neuralMemory=null;
 const ledger={lastEnergy:x.s.energy,lastMaterial:x.material,continuityMax:0,
  withdrawnEnergy:0,withdrawnMaterial:0,injectedEnergy:0,injectedMaterial:0,
  internalMaterialCharged:0,internalRepairEnergyAttributed:0};
 const traces=[],samples=[];
 for(let t=0;t<duration;t++){
  ledger.continuityMax=Math.max(ledger.continuityMax,Math.abs(x.s.energy-ledger.lastEnergy),
   Math.abs(x.material-ledger.lastMaterial));
  const mesh=wag272Mesh(x,lastRepair,neuralMemory);
  neuralMemory=mesh.memory;
  let action=mode==='mesh'?mesh.action:mode==='noRepair'?'abstain':
   wag263Select(x,models,horizon,lastRepair,wag263Gate(x,state),'baseline').action;
  if(mode==='mesh'&&mesh.prefer!=='abstain'){requestCount++;if(!mesh.accepted)guardDenials++}
  const materialBefore=x.materialSpent;
  step244(x,action);
  const actual=x.s.trace.at(-1).maintenance;
  if(action!=='abstain'&&actual!==action)engineDenials++;
  if(actual!=='abstain'){
   repairCount++;lastRepair=t;
   ledger.internalRepairEnergyAttributed+=WAG272_COST[actual].energy;
  }
  ledger.internalMaterialCharged+=x.materialSpent-materialBefore;
  const forcing=wag269Stress(t,stress,seed),preE=x.s.energy,preM=x.material;
  x.s.energy=wag272Clamp(preE+forcing.energy);x.material=wag272Clamp(preM+forcing.material);
  const de=x.s.energy-preE,dm=x.material-preM;
  ledger.withdrawnEnergy+=Math.max(0,-de);ledger.withdrawnMaterial+=Math.max(0,-dm);
  ledger.injectedEnergy+=Math.max(0,de);ledger.injectedMaterial+=Math.max(0,dm);
  ledger.lastEnergy=x.s.energy;ledger.lastMaterial=x.material;
  const z=x.s.trace.at(-1);z.energy=x.s.energy;z.material=x.material;
  traces.push({tick:t,energy:x.s.energy,material:x.material,
   integrity:z.integrity,action:actual,
   meshAction:mesh.action,meshPermit:mesh.a.permit,meshRequest:mesh.b.request,
   aReserve:mesh.a.reserve,bUrgency:mesh.b.urgency});
  if(t%16===0) samples.push({tick:t,a:mesh.a,b:mesh.b,inputs:mesh.inputs,
   action:actual,proposed:mesh.prefer,reasons:mesh.reasons});
 }
 const pending=x.queue.filter(z=>z.due>=duration).reduce((a,z)=>a+z.amount,0);
 const energyResidual=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const materialResidual=Math.abs(.2+x.materialIn+ledger.injectedMaterial-
  x.materialSpent-ledger.withdrawnMaterial-x.material);
 const chargeError=Math.abs(ledger.internalMaterialCharged-x.materialSpent);
 if(energyResidual>1e-8||materialResidual>1e-8||chargeError>1e-8)throw Error('WAG272 accounting failure');
 const alive=traces.filter(z=>z.energy>.08&&z.integrity>.15).length;
 return {cap,family,seed,duration,stress,mode,aliveTicks:alive,fullSurvival:alive===duration,
  reserveTicks:traces.filter(z=>z.energy>.25&&z.integrity>.30).length,
  meanIntegrity:x.s.area/duration,repairs:repairCount,guardDenials,engineDenials,requestCount,
  ledger:{...ledger,energyResidual,materialResidual,chargeError},
  trace:traces,samples,finalEnergy:x.s.energy,finalMaterial:x.material};
}
function wag272Experiment(frozen,models,horizon){
 const cases=[],rows=[];
 for(const duration of WAG272_HORIZONS)for(const family of WAG272_FAMILIES)
 for(const stress of WAG272_STRESS)for(const cap of WAG272_CAP)
 for(const seed of WAG272_SEEDS){
  const g={};
  for(const mode of WAG272_MODES){
   const r=wag272Run(cap,family,seed,duration,stress,mode,frozen,models,horizon);
   const row={duration,family,stress,cap,seed,mode,aliveTicks:r.aliveTicks,
    fullSurvival:r.fullSurvival,reserveTicks:r.reserveTicks,meanIntegrity:r.meanIntegrity,
    repairs:r.repairs,guardDenials:r.guardDenials,engineDenials:r.engineDenials,
    energyResidual:r.ledger.energyResidual,materialResidual:r.ledger.materialResidual,
    chargeError:r.ledger.chargeError,continuity:r.ledger.continuityMax};
   g[mode]=row;rows.push(row);
  }
  cases.push({duration,family,stress,cap,seed,
   meshAliveDelta:g.mesh.aliveTicks-g.frozen.aliveTicks,
   meshIntegrityDelta:g.mesh.meanIntegrity-g.frozen.meanIntegrity,
   meshReserveDelta:g.mesh.reserveTicks-g.frozen.reserveTicks,
   meshRepairs:g.mesh.repairs,frozenRepairs:g.frozen.repairs});
 }
 const aggregate={};
 for(const duration of WAG272_HORIZONS)aggregate[duration]=Object.fromEntries(WAG272_MODES.map(mode=>{
  const r=rows.filter(x=>x.duration===duration&&x.mode===mode),n=r.length;
  return [mode,{n,fullSurvival:r.filter(z=>z.fullSurvival).length,
   meanAliveRatio:r.reduce((s,z)=>s+z.aliveTicks/z.duration,0)/n,
   meanReserveRatio:r.reduce((s,z)=>s+z.reserveTicks/z.duration,0)/n,
   meanIntegrity:r.reduce((s,z)=>s+z.meanIntegrity,0)/n,
   meanRepairs:r.reduce((s,z)=>s+z.repairs,0)/n,
   physicalDenials:r.reduce((s,z)=>s+z.engineDenials,0)}];
 }));
 return {bound:'WAG-272',phase:'WAG-III',turn:4,primitive:'{a{b}}',
  network:{type:'deterministic recurrent two-cubit mesh',passes:3,
   outer:'a survival/resource governor',inner:'b repair valuation',
   edges:['a.reserve→b.rebuild','a.reserve→b.prevent',
    'b.request→a.permit','a.permit→single action gate','a(t)→a(t+1)','b(t)→b(t+1)'],
   guard:WAG272_GUARD,cost:WAG272_COST},
  aggregate,cases,rows,
  summary:{policyRuns:rows.length,matchedConditions:cases.length,
   meshAliveRegressions:cases.filter(z=>z.meshAliveDelta<0).length,
   meshIntegrityRegressions:cases.filter(z=>z.meshIntegrityDelta< -1e-12).length,
   meshIntegrityImprovements:cases.filter(z=>z.meshIntegrityDelta>1e-12).length,
   maxEnergyResidual:Math.max(...rows.map(z=>z.energyResidual)),
   maxMaterialResidual:Math.max(...rows.map(z=>z.materialResidual)),
   maxChargeError:Math.max(...rows.map(z=>z.chargeError)),
   maxContinuity:Math.max(...rows.map(z=>z.continuity))},
  limits:['Fixed-weight neural-style meshed computation, not learned weights',
   'No neuronal training or external validation, only deterministic synthetic controller',
   'Resource reserve guard is checked before each action, engine remains physical authority',
   'No runtime action changes to the sealed WAG264 policy']};
}
if(typeof module!=='undefined')module.exports={wag272NeuralInputs,wag272Mesh,wag272Run,wag272Experiment};
