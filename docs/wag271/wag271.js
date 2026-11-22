/* WAG-271 · Phase III turn 3/12 · bounded repair deferral and missed-window audit · .dlw
 Frozen WAG264 WAG261 engine remains unchanged. Delay options are PREDECLARED
 (0,3,6,12 ticks). Delayed work is a single non-duplicated pending ticket.
 At execution time, recheck actual physical eligibility with CURRENT state.
 No future stress information, hidden rollouts, or post-test policy tuning.
 The simulator's forced stress is identical on matched cases across policies.
*/
const WAG271_DELAYS=[0,3,6,12];
const WAG271_SEEDS=[5801,5802,5803];
const WAG271_HORIZONS=[240,480];
const WAG271_FAMILIES=['scar','combined'];
const WAG271_STRESS=['late-collapse','double-shock','intermittent','resource-squeeze'];
const WAG271_CAP=[8,13];
function wag271EligibleNow(x,action){
 if(!['prevent','rebuild'].includes(action))return false;
 if(x.s.energy<=.14||x.s.integrity<=.15)return false;
 // The step244 physical eligibility is checked before it harvests up to
 // .0009 material in this tick. Conservative rejection is intentional.
 if(action==='prevent')return x.f[x.t].observed>.55&&x.material>=.0015;
 return x.s.ceiling<.995&&x.material>=.0035&&x.s.energy>.35;
}
function wag271Run(cap,family,seed,duration,stress,delay,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 if(!WAG271_DELAYS.includes(delay)||!WAG271_HORIZONS.includes(duration))
   throw Error('unsupported delay or duration');
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const state={level:'normal',alarmStreak:0,clearStreak:0,changes:[]};
 const ledger={withdrawnEnergy:0,withdrawnMaterial:0,injectedEnergy:0,injectedMaterial:0,
  lastEnergy:x.s.energy,lastMaterial:x.material,continuityMax:0};
 const timing={requests:0,executed:0,invalidAtDue:0,unfulfilled:0,
  pendingAtEnd:0,dueOnTime:0,repairLate:0,
  missedPrevent:0,missedRebuild:0,physicalRejects:0,
  tickets:[]};
 const trace=[];
 let pending=null,lastRepair=-100;
 for(let t=0;t<duration;t++){
  ledger.continuityMax=Math.max(ledger.continuityMax,
   Math.abs(ledger.lastEnergy-x.s.energy),Math.abs(ledger.lastMaterial-x.material));
  let action='abstain',ticketAtTick=null;
  // A due ticket occupies the decision slot. If it has gone stale, abstain.
  if(pending&&t>=pending.due){
   ticketAtTick=pending;pending=null;
   if(wag271EligibleNow(x,ticketAtTick.action)){
    action=ticketAtTick.action;timing.dueOnTime++;
   }else{
    timing.invalidAtDue++;
    if(ticketAtTick.action==='prevent')timing.missedPrevent++;else timing.missedRebuild++;
    ticketAtTick.state='invalid-at-due';
   }
  }else if(!pending){
   const gate=wag263Gate(x,state);
   const d=wag263Select(x,models,horizon,lastRepair,gate,'baseline');
   if(d.action!=='abstain'){
    timing.requests++;
    if(delay===0){action=d.action;ticketAtTick={action,requested:t,due:t,state:'immediate'}}
    else{pending={action:d.action,requested:t,due:t+delay,state:'pending'};
     timing.tickets.push(pending);}
   }
  }
  // At most one repair, always physically applied by authoritative step244.
  const before={prevent:x.choices.prevent,rebuild:x.choices.rebuild};
  step244(x,action);
  const actual=x.s.trace.at(-1).maintenance;
  if(action!=='abstain'){
   if(actual!==action){timing.physicalRejects++;timing.invalidAtDue++;
    if(action==='prevent')timing.missedPrevent++;else timing.missedRebuild++;
    if(ticketAtTick)ticketAtTick.state='physically-rejected';
   }else{
    timing.executed++;lastRepair=t;
    if(ticketAtTick){ticketAtTick.state='executed';
     if(ticketAtTick.due>ticketAtTick.requested)timing.repairLate++;}
   }
  }
  const force=wag269Stress(t,stress,seed),energyBefore=x.s.energy,matBefore=x.material;
  x.s.energy=Math.max(0,Math.min(1,energyBefore+force.energy));
  x.material=Math.max(0,Math.min(1,matBefore+force.material));
  const ed=x.s.energy-energyBefore,md=x.material-matBefore;
  ledger.withdrawnEnergy+=Math.max(0,-ed);
  ledger.withdrawnMaterial+=Math.max(0,-md);
  ledger.injectedEnergy+=Math.max(0,ed);
  ledger.injectedMaterial+=Math.max(0,md);
  ledger.lastEnergy=x.s.energy;ledger.lastMaterial=x.material;
  const z=x.s.trace.at(-1);z.energy=x.s.energy;z.material=x.material;
  trace.push({tick:t,energy:x.s.energy,material:x.material,integrity:z.integrity,
   action:actual,pending:pending?.action??null,
   queuedAt:pending?.requested??null,dueAt:pending?.due??null});
 }
 if(pending){timing.pendingAtEnd=1;timing.unfulfilled++;timing.tickets.push(
  {action:pending.action,requested:pending.requested,due:pending.due,state:'horizon-expired'});
 }
 const pendingEnergy=x.queue.filter(z=>z.due>=x.duration).reduce((sum,z)=>sum+z.amount,0);
 const cacheResidual=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pendingEnergy*.84));
 const materialResidual=Math.abs(.2+x.materialIn+ledger.injectedMaterial-
  x.materialSpent-ledger.withdrawnMaterial-x.material);
 if(cacheResidual>1e-8||materialResidual>1e-8)throw Error('resource reconciliation failed');
 const aliveTicks=trace.filter(z=>z.energy>.08&&z.integrity>.15).length;
 return {cap,family,seed,duration,stress,delay,
  aliveTicks,fullSurvival:aliveTicks===duration,
  reserveTicks:trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  meanIntegrity:x.s.area/duration,finalEnergy:x.s.energy,finalMaterial:x.material,
  repairs:timing.executed,timing,trace,
  ledger:{...ledger,cacheResidual,materialResidual}};
}
function wag271Aggregate(rows){
 const n=rows.length;return {n,
  fullSurvival:rows.filter(z=>z.fullSurvival).length,
  meanAliveRatio:rows.reduce((v,z)=>v+z.aliveTicks/z.duration,0)/n,
  meanReserveRatio:rows.reduce((v,z)=>v+z.reserveTicks/z.duration,0)/n,
  meanIntegrity:rows.reduce((v,z)=>v+z.meanIntegrity,0)/n,
  meanRepairs:rows.reduce((v,z)=>v+z.repairs,0)/n,
  missedWindows:rows.reduce((v,z)=>v+z.invalidAtDue+z.pendingAtEnd,0),
  pendingAtEnd:rows.reduce((v,z)=>v+z.pendingAtEnd,0)};
}
function wag271Experiment(frozen,models,horizon){
 const rows=[],cases=[];
 for(const duration of WAG271_HORIZONS)for(const family of WAG271_FAMILIES)
 for(const stress of WAG271_STRESS)for(const cap of WAG271_CAP)
 for(const seed of WAG271_SEEDS){
  const runs={};
  for(const delay of WAG271_DELAYS){
   const r=wag271Run(cap,family,seed,duration,stress,delay,frozen,models,horizon);
   const row={duration,family,stress,cap,seed,delay,
    aliveTicks:r.aliveTicks,fullSurvival:r.fullSurvival,
    reserveTicks:r.reserveTicks,meanIntegrity:r.meanIntegrity,
    repairs:r.repairs,requests:r.timing.requests,invalidAtDue:r.timing.invalidAtDue,
    pendingAtEnd:r.timing.pendingAtEnd,
    missedPrevent:r.timing.missedPrevent,missedRebuild:r.timing.missedRebuild,
    energyResidual:r.ledger.cacheResidual,materialResidual:r.ledger.materialResidual,
    continuity:r.ledger.continuityMax};
   rows.push(row);runs[delay]=row;
  }
  cases.push({duration,family,stress,cap,seed,
   comparisons:Object.fromEntries(WAG271_DELAYS.filter(d=>d>0).map(delay=>[delay,{
    aliveDelta:runs[delay].aliveTicks-runs[0].aliveTicks,
    reserveDelta:runs[delay].reserveTicks-runs[0].reserveTicks,
    integrityDelta:runs[delay].meanIntegrity-runs[0].meanIntegrity,
    fewerRepairs:runs[delay].repairs<runs[0].repairs,
    invalidated:runs[delay].invalidAtDue
   }]))});
 }
 const aggregate=Object.fromEntries(WAG271_HORIZONS.map(duration=>[duration,
  Object.fromEntries(WAG271_DELAYS.map(delay=>[delay,
   wag271Aggregate(rows.filter(r=>r.duration===duration&&r.delay===delay))]))]));
 const diagnostics=Object.fromEntries(WAG271_DELAYS.filter(d=>d>0).map(d=>[d,{
  aliveRegressions:cases.filter(c=>c.comparisons[d].aliveDelta<0).length,
  integrityRegressions:cases.filter(c=>c.comparisons[d].integrityDelta< -1e-12).length,
  integrityImprovements:cases.filter(c=>c.comparisons[d].integrityDelta>1e-12).length,
  totalInvalidated:cases.reduce((v,c)=>v+c.comparisons[d].invalidated,0)
 }]));
 return {bound:'WAG-271',phase:'WAG-III',turn:3,delays:WAG271_DELAYS,
  seeds:WAG271_SEEDS,aggregate,diagnostics,rows,cases,
  summary:{policyRuns:rows.length,matchedConditions:cases.length,
   maxContinuity:Math.max(...rows.map(r=>r.continuity)),
   maxEnergyResidual:Math.max(...rows.map(r=>Math.abs(r.energyResidual))),
   maxMaterialResidual:Math.max(...rows.map(r=>Math.abs(r.materialResidual)))},
  limitations:['Single synthetic physics family, no external validation',
   'A queued delayed repair does not reserve resources and is refused if physically stale',
   'Only one pending ticket is maintained: deliberation is suppressed while waiting',
   'Fixed horizon tests do not establish infinite-term recovery','Frozen WAG261 remains unchanged']};
}
if(typeof module!=='undefined')module.exports={wag271EligibleNow,wag271Run,wag271Experiment};
