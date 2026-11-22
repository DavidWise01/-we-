/* WAG-262 · persistent unified resources · Phase II 6/12 · .dlw
   The WAG244 internal cache has its own conservation ledger. Energy used by
   actual maintenance is already in physical state, material likewise.
   External probe switching fees are now applied to x.s.energy AFTER step244,
   and kept as the next tick's initial state. Never deduct inherited repair
   costs twice. Append-only tick/transaction receipts verify actual debits.
   A declared 8x bounded fee contract remains synthetic, not a guarantee for
   unknown unbounded costs. Test-only diagnostic probing is not production VOI.
*/
const WAG262_TEST=[5101,5102,5103,5104],WAG262_PROBE_TICK=90;
function wag262Ledger(x){
 return {externalEnergySpent:0,repairEnergyAttributed:0,materialSpent:0,
  repairMaterialAttributed:0,energyPreFee:0,energyPostFee:0,
  feeResidualMax:0,continuityErrorMax:0,overdraw:0,
  transactions:[],ticks:[],probes:0,returns:0,breaches:0,denied:0,
  lastEnergy:x.s.energy};
}
function wag262Charge(x,ledger,tick,phase,from,to,costModel,regime,reserved,lastChange){
 const f=wag254Signals(x,tick-lastChange,from,to);
 const est=wag254Estimate(x,tick-lastChange,from,to,costModel);
 const actual=wag255ActualFee(x,{from,to,features:f,predicted:est.mean},regime,tick);
 const pre=x.s.energy;
 // If unknown cost exceeds escrow, preserve full actual obligation as unpaid
 // liability; test environments are inside the declared envelope.
 const paid=Math.min(pre,actual);
 x.s.energy=pre-paid;
 const unpaid=actual-paid;
 if(unpaid>1e-12)ledger.overdraw+=unpaid;
 const post=x.s.energy;
 const error=Math.abs(pre-paid-post);
 ledger.feeResidualMax=Math.max(ledger.feeResidualMax,error);
 ledger.externalEnergySpent+=paid;
 ledger.energyPreFee+=pre;ledger.energyPostFee+=post;
 const row={tick,phase,from,to,predicted:est.mean,actual,reserved,paid,unpaid,
   pre,post,breach:actual>reserved+1e-10};
 if(row.breach)ledger.breaches++;
 ledger.transactions.push(row);
 // step244 trace was produced before the external fee; fix its energy,
 // reserve and alive classifications from the true post-transaction state.
 const trace=x.s.trace.at(-1);
 if(trace){trace.energy=post;trace.externalFee=paid;
   trace.alive=post>.08&&trace.integrity>.15;
   trace.reserve=post>.25&&trace.integrity>.30;}
 return row;
}
function wag262Run(cap,family,seed,duration,regime,variant,models,horizon,cost,voi){
 if(variant==='wag261')return wag261Run(cap,family,seed,duration,'multi',models,horizon);
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const ledger=wag262Ledger(x),choices={wait:0,prevent:0,rebuild:0,probe:0,return:0},receipts=[];
 const gate=wag258Decision(wag258Features(cap,family,seed,duration,models),voi);
 let lastRepair=-100,lastChange=-100,ticket=null,stage='idle',energyForward=0;
 for(let tick=0;tick<duration;tick++){
  // Resource continuity is observable before action selection, not only in
  // a retrospective receipt.
  ledger.continuityErrorMax=Math.max(ledger.continuityErrorMax,
   Math.abs(x.s.energy-ledger.lastEnergy));
  if(tick===WAG262_PROBE_TICK&&stage==='idle'&&
     (variant==='diagnostic'||gate.action==='valueProbe')){
   const bid=wag259Escrow(x,6,3,lastChange,cost,ledger.externalEnergySpent);
   if(bid.allowed&&ledger.externalEnergySpent+bid.escrow<=WAG259_TOTAL_BUDGET){
    ticket={from:6,to:3,returnTick:tick+6,entryReserve:bid.entryReserve,
      returnReserve:bid.returnReserve};
    stage='active';ledger.probes++;choices.probe++;
   }else ledger.denied++;
  }
  // Use WAG261's deterministic repair decision unless a probe transaction
  // is being executed; probe entry/exit consumes this tick's action slot.
  const entering=stage==='active'&&ticket&&tick===WAG262_PROBE_TICK;
  const exiting=stage==='active'&&ticket&&tick===ticket.returnTick;
  const result=(entering||exiting)?{action:'abstain',reason:entering?'probe-entry':'probe-return'}:
    wag261Select(x,models,horizon,lastRepair);
  const action=result.action;
  if(action!=='abstain')lastRepair=tick;
  choices[action==='abstain'?'wait':action]++;
  const beforeEnergy=x.s.energy,beforeMaterial=x.material,beforeSpent=x.materialSpent;
  step244(x,action);
  const internalMaterialCost=x.materialSpent-beforeSpent;
  const internalEnergyCost=action==='rebuild'?.004:action==='prevent'?.0012:0;
  ledger.repairEnergyAttributed+=internalEnergyCost;
  ledger.repairMaterialAttributed+=internalMaterialCost;
  ledger.materialSpent=x.materialSpent;
  if(entering||exiting){
   const from=entering?ticket.from:ticket.to,to=entering?ticket.to:ticket.from;
   const reserved=entering?ticket.entryReserve:ticket.returnReserve;
   wag262Charge(x,ledger,tick,entering?'entry':'return',from,to,cost,regime,reserved,lastChange);
   lastChange=tick;
   if(exiting){ledger.returns++;stage='idle';ticket=null;choices.return++;}
  }
  ledger.ticks.push({tick,beforeEnergy,beforeMaterial,
   postEngineEnergy:ledger.transactions.at(-1)?.tick===tick?ledger.transactions.at(-1).pre:x.s.energy,
   afterEnergy:x.s.energy,afterMaterial:x.material,repair:action,
   externalFee:ledger.transactions.at(-1)?.tick===tick?ledger.transactions.at(-1).paid:0});
  ledger.lastEnergy=x.s.energy;
  if(WAG250_SAMPLE.includes(tick%240))receipts.push({tick,action,reason:result.reason,
    energy:x.s.energy,material:x.material,externalFeePaid:ledger.externalEnergySpent});
 }
 const original=wag248Ledger(x),aliveTicks=ledger.ticks.filter(t=>t.afterEnergy>.08&&x.s.trace[t.tick].integrity>.15).length,
  reserveTicks=ledger.ticks.filter(t=>t.afterEnergy>.25&&x.s.trace[t.tick].integrity>.30).length;
 return {mode:variant,capacity:cap,scenario:family,seed,duration,regime,
  meanIntegrity:x.s.area/duration,finalIntegrity:x.s.integrity,
  finalEnergy:x.s.energy,finalMaterial:x.material,aliveTicks,reserveTicks,
  maintenance:x.choices,choices,probes:ledger.probes,returns:ledger.returns,
  escrowBreaches:ledger.breaches,deniedProbes:ledger.denied,
  resourceLedger:ledger,engineLedger:original,trace:x.s.trace,receipts,
  note:'External switching fee is physically debited after step244 and carried into the next decision. Internal repair energy/material is charged by step244 only.'};
}
function wag262Experiment(){
 const models=wag251Models(),horizon=wag261Train(models),
 cost=wag254Train(models),cadence=wag252Train(models),voi=wag258Train(models,cadence,cost),
 groups={},examples=[];
 for(const regime of ['stable','surcharge','nonlinear','shock'])
 for(const family of ['scar','combined','phaseflip','famine'])for(const cap of CAP234)
 for(const seed of WAG262_TEST){
  const a=wag262Run(cap,family,seed,240,regime,'production',models,horizon,cost,voi);
  const b=wag262Run(cap,family,seed,240,regime,'diagnostic',models,horizon,cost,voi);
  const key=regime+':'+family,g=groups[key]??={n:0,entries:0,returns:0,breaches:0,
    persistentErrors:0,meanIntegrityDelta:0};
  g.n++;g.entries+=b.probes;g.returns+=b.returns;g.breaches+=b.escrowBreaches;
  g.persistentErrors=Math.max(g.persistentErrors,b.resourceLedger.continuityErrorMax);
  g.meanIntegrityDelta+=b.meanIntegrity-a.meanIntegrity;
  if(cap===13&&seed===5101)examples.push({regime,family,production:{
   integrity:a.meanIntegrity,probes:a.probes},diagnostic:{
    integrity:b.meanIntegrity,probes:b.probes,returns:b.returns,
    fees:b.resourceLedger.externalEnergySpent},transactions:b.resourceLedger.transactions});
 }
 for(const g of Object.values(groups))g.meanIntegrityDelta/=g.n;
 return {bound:'WAG-262',phase:'II',turn:6,groups,examples,
  caveat:'One inherited synthetic simulator; fee is incorporated into physical state, but neither energy generation nor full thermodynamic conservation is independently calibrated.'};
}
if(typeof module!=='undefined')module.exports={wag262Run,wag262Ledger,wag262Charge,wag262Experiment};
