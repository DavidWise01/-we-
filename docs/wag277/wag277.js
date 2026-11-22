/* WAG-277 withheld trial + SEPARATE lattice-chain exploratory controller.
 Frozen candidate source: WAG-276 unchanged, 480/720 seeds 6401..6404.
 Chain signal ingress modifies only exploratory chain's decision.
 Both subject to WAG244 material/energy authority.
 */
const WAG277_HOLDOUT=Object.freeze({
 seeds:[6401,6402,6403,6404],durations:[480,720],
 families:['scar','combined'],forces:['antiphase','surge-crash','shrinking-cycle','dual-burst'],
 capacities:[8,13],modes:['frozen','crystal','chain'],
 chainParams:{junctions:4,passes:3,terminalBlend:.20,ingress:.35}
});
function wag277ChainDecision(x,lastRepair,memory,lattice){
 const c=wag276Candidate(x,lastRepair,memory);
 const u=c.base.inputs;
 const values=[u.energy,u.material,u.integrity,u.scar,u.pressure,
  c.base.a.reserve,c.base.b.request,c.base.a.risk];
 // Current observation is an EXTERNAL signal input; conservation checks apply
 // only to closed subsequent rail propagation, not this observation injection.
 const ingress=WAG277_HOLDOUT.chainParams.ingress;
 for(let j=0;j<8;j++)lattice.junctionSignals[0][j]+=
  ingress*(values[j]-lattice.junctionSignals[0][j]);
 for(let k=0;k<WAG277_HOLDOUT.chainParams.passes;k++)lattice=wag277Step(lattice);
 const terminalA=lattice.terminalSignals.slice(0,8),
  terminalB=lattice.terminalSignals.slice(8);
 const meanA=terminalA.reduce((s,v)=>s+v,0)/8,
  meanB=terminalB.reduce((s,v)=>s+v,0)/8;
 const blend=WAG277_HOLDOUT.chainParams.terminalBlend;
 const permitted=(1-blend)*c.railPermit+blend*meanA,
  requested=(1-blend)*c.railRequest+blend*meanB;
 const action=c.physical&&c.base.reasons.worth&&
  permitted>=WAG276_CONFIG.minPermit&&requested>=WAG276_CONFIG.minRequest?
   c.prefer:'abstain';
 return {action,lattice,memory:c.memory,
  terminalA:meanA,terminalB:meanB,baseAction:c.action,
  admitted:action!=='abstain'};
}
function wag277Run(cap,family,seed,duration,force,mode,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 if(!WAG277_HOLDOUT.durations.includes(duration)||
  !WAG277_HOLDOUT.seeds.includes(seed)||
  !WAG277_HOLDOUT.families.includes(family)||
  !WAG277_HOLDOUT.forces.includes(force)||
  !WAG277_HOLDOUT.capacities.includes(cap)||
  !WAG277_HOLDOUT.modes.includes(mode))throw Error('invalid WAG277 test');
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const gate={level:'normal',alarmStreak:0,clearStreak:0,changes:[]};
 let memory=null,lastRepair=-100,repairs=0,changedDecisions=0,rejects=0,
  lattice=wag277Initial(4,'uniform'),maxRailResidual=0;
 const ledger={lastEnergy:x.s.energy,lastMaterial:x.material,
  externalEnergyOut:0,externalEnergyIn:0,externalMaterialOut:0,
  externalMaterialIn:0,internalMaterialCharge:0,continuityMax:0};
 const trace=[],samples=[];
 for(let t=0;t<duration;t++){
  ledger.continuityMax=Math.max(ledger.continuityMax,
   Math.abs(x.s.energy-ledger.lastEnergy),
   Math.abs(x.material-ledger.lastMaterial));
  // The two-cubit oracle is identical to WAG276 for mode "crystal".
  // Chain mode uses separately bounded external signal ingress.
  const crystal=mode==='chain'?null:wag276Candidate(x,lastRepair,memory);
  let req;
  if(mode==='chain'){
   const z=wag277ChainDecision(x,lastRepair,memory,lattice);
   lattice=z.lattice;memory=z.memory;req=z.action;
   if(z.action!==z.baseAction)changedDecisions++;
   maxRailResidual=Math.max(maxRailResidual,lattice.signalResidual);
   if(t%60===0)samples.push({tick:t,signalA:z.terminalA,
    signalB:z.terminalB,action:z.action,changedDecisions});
  }else{
   memory=crystal.memory;
   req=mode==='crystal'?crystal.action:
    wag263Select(x,models,horizon,lastRepair,wag263Gate(x,gate),'baseline').action;
  }
  const preSpent=x.materialSpent;
  step244(x,req);
  const actual=x.s.trace.at(-1).maintenance;
  if(req!=='abstain'&&req!==actual)rejects++;
  if(actual!=='abstain'){lastRepair=t;repairs++}
  ledger.internalMaterialCharge+=x.materialSpent-preSpent;
  const forceValue=wag274Force(t,force,seed),preEnergy=x.s.energy,preMaterial=x.material;
  x.s.energy=wag272Clamp(preEnergy+forceValue.energy);
  x.material=wag272Clamp(preMaterial+forceValue.material);
  const deltaE=x.s.energy-preEnergy,deltaM=x.material-preMaterial;
  ledger.externalEnergyOut+=Math.max(0,-deltaE);
  ledger.externalEnergyIn+=Math.max(0,deltaE);
  ledger.externalMaterialOut+=Math.max(0,-deltaM);
  ledger.externalMaterialIn+=Math.max(0,deltaM);
  ledger.lastEnergy=x.s.energy;ledger.lastMaterial=x.material;
  const z=x.s.trace.at(-1);z.energy=x.s.energy;z.material=x.material;
  trace.push({tick:t,energy:x.s.energy,material:x.material,
   integrity:z.integrity,action:actual});
 }
 const pending=x.queue.filter(z=>z.due>=duration).reduce((s,z)=>s+z.amount,0);
 const error=Math.max(
  Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84),
  Math.abs(.2+x.materialIn+ledger.externalMaterialIn-
   x.materialSpent-ledger.externalMaterialOut-x.material),
  Math.abs(ledger.internalMaterialCharge-x.materialSpent));
 if(error>1e-8||maxRailResidual>1e-9)throw Error('WAG277 conservation violation');
 const alive=trace.filter(z=>z.energy>.08&&z.integrity>.15).length;
 return {mode,cap,family,seed,duration,force,aliveTicks:alive,
  fullSurvival:alive===duration,
  reserveTicks:trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  meanIntegrity:x.s.area/duration,repairs,changedDecisions,rejects,
  error,maxRailResidual,continuityMax:ledger.continuityMax,
  trace,samples};
}
function wag277Experiment(frozen,models,horizon){
 const rows=[],cases=[];
 for(const duration of WAG277_HOLDOUT.durations)
 for(const family of WAG277_HOLDOUT.families)
 for(const force of WAG277_HOLDOUT.forces)
 for(const cap of WAG277_HOLDOUT.capacities)
 for(const seed of WAG277_HOLDOUT.seeds){
  const g={};
  for(const mode of WAG277_HOLDOUT.modes){
   const r=wag277Run(cap,family,seed,duration,force,mode,frozen,models,horizon);
   const row={duration,family,force,cap,seed,mode,
    aliveTicks:r.aliveTicks,fullSurvival:r.fullSurvival,
    reserveTicks:r.reserveTicks,meanIntegrity:r.meanIntegrity,
    repairs:r.repairs,changedDecisions:r.changedDecisions,
    error:r.error,continuity:r.continuityMax,
    maxRailResidual:r.maxRailResidual};
   rows.push(row);g[mode]=row;
  }
  cases.push({duration,family,force,cap,seed,
   crystalAliveDelta:g.crystal.aliveTicks-g.frozen.aliveTicks,
   crystalIntegrityDelta:g.crystal.meanIntegrity-g.frozen.meanIntegrity,
   chainAliveDelta:g.chain.aliveTicks-g.crystal.aliveTicks,
   chainIntegrityDelta:g.chain.meanIntegrity-g.crystal.meanIntegrity});
 }
 const aggregate=Object.fromEntries(WAG277_HOLDOUT.durations.map(duration=>[
  duration,Object.fromEntries(WAG277_HOLDOUT.modes.map(mode=>{
   const r=rows.filter(x=>x.duration===duration&&x.mode===mode),n=r.length;
   return [mode,{n,fullSurvival:r.filter(z=>z.fullSurvival).length,
    meanAliveRatio:r.reduce((a,z)=>a+z.aliveTicks/z.duration,0)/n,
    meanReserveRatio:r.reduce((a,z)=>a+z.reserveTicks/z.duration,0)/n,
    meanIntegrity:r.reduce((a,z)=>a+z.meanIntegrity,0)/n,
    meanRepairs:r.reduce((a,z)=>a+z.repairs,0)/n,
    changedDecisions:r.reduce((a,z)=>a+z.changedDecisions,0)}];
  }))]));
 return {bound:'WAG-277',phase:'WAG-III',turn:9,primitive:'---@---@---@---@---{}',
  holdout:WAG277_HOLDOUT,aggregate,rows,cases,
  summary:{policyRuns:rows.length,matchedConditions:cases.length,
   crystalIntegrityRegressions:cases.filter(z=>z.crystalIntegrityDelta< -1e-12).length,
   crystalAliveRegressions:cases.filter(z=>z.crystalAliveDelta<0).length,
   chainIntegrityRegressions:cases.filter(z=>z.chainIntegrityDelta< -1e-12).length,
   maxConservation:Math.max(...rows.map(z=>z.error)),
   maxContinuity:Math.max(...rows.map(z=>z.continuity)),
   maxRailResidual:Math.max(...rows.map(z=>z.maxRailResidual))},
  limitations:['Frozen crystal vs WAG261 is the precommitted holdout',
   'Chain mode is exploratory and cannot be promoted based on this set',
   'Signal ingress is external and not part of closed-signal conservation',
   'One synthetic simulator ancestry; no external physical validation']};
}
if(typeof module!=='undefined')module.exports={
 WAG277_HOLDOUT,wag277ChainDecision,wag277Run,wag277Experiment};
