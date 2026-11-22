/* WAG-259 · Probe eligibility & two-leg return escrow · Phase II 3/12 · .dlw
 Synthetic safety contract, NOT assurance against unbounded unknown surcharges.
 Escrow covers both entry + return under declared <=8x cost stress envelope.
 Controller sees only current state, historical receipts, frozen WAG254 estimate.
 Charged switch costs tracked in separate cumulative ledger because inherited
 WAG-244 physics may recompute energy without persisting external debits.
 "diagnostic" probes exercise physical safety independent of frozen VOI gate;
 "gated" respects WAG258's no-probe best choice.
*/
const WAG259_TEST=[4701,4702,4703,4704];
const WAG259_ENVELOPE=8, WAG259_FLOOR=.54,WAG259_TOTAL_BUDGET=.012;
const WAG259_WINDOWS=[90,138,186,234,282,330,378,426];
function wag259Escrow(x,from,to,lastChange,cost,spent){
 const age=x.t-lastChange,forward=wag254Estimate(x,age,from,to,cost);
 const back=wag254Estimate(x,0,to,from,cost);
 const budgetEntry=forward.upper*WAG259_ENVELOPE;
 const budgetReturn=back.upper*WAG259_ENVELOPE;
 const escrow=budgetEntry+budgetReturn;
 const spendable=Math.max(0,x.s.energy-spent);
 return {from,to,escrow,entryReserve:budgetEntry,returnReserve:budgetReturn,
   spendable,allowed:forward.known&&back.known&&spendable-escrow>WAG259_FLOOR&&
   x.material>.055&&x.s.integrity>.30&&x.t+6<x.duration};
}
function wag259Run(cap,family,seed,duration,regime,variant,models,cadence,cost,voi){
 if(variant==='wag256')return wag256Run(cap,family,seed,duration,regime,'valueProbe',models,cadence,cost);
 if(variant==='noProbe')return wag256Run(cap,family,seed,duration,regime,'noProbe',models,cadence,cost);
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const history=[],probes=[],receipts=[],counts={3:0,6:0,12:0,24:0};
 const decision=wag258Decision(wag258Features(cap,family,seed,duration,models),voi);
 let operating=6,lastRepair=-100,lastChange=-100,lastProbe=-100,stage='idle',ticket=null,
   spent=0,probeFees=0,probesStarted=0,probesReturned=0,trapped=0,breaches=0,
   denied=0,unbudgeted=0,entryReserveTotal=0,expectedReserveTotal=0;
 while(x.t<duration){
  const tick=x.t,choice=wag252Select(x,cadence),desired=choice.cadence;
  // Simplified operating policy: select the frozen cadence each tick;
  // fees caused by ordinary cadence changes are NOT priced in this bound.
  // This isolate tests the eligibility and two-leg probe contract, not
  // optimal operating transitions.
  if(stage==='idle')operating=desired;
  let transition=null,reason='operate';
  if(stage==='active'&&tick>=ticket.returnTick){
   transition={from:operating,to:ticket.home,phase:'return',probe:true};
   operating=ticket.home;stage='idle';reason='return-covered';
  }else if(stage==='idle'&&WAG259_WINDOWS.includes(tick)&&tick-lastProbe>=42&&
   (variant==='diagnostic'||decision.action==='valueProbe')){
    const to=operating===3?6:3,bid=wag259Escrow(x,operating,to,lastChange,cost,spent);
    const budgetOK=spent+bid.escrow<=WAG259_TOTAL_BUDGET;
    if(bid.allowed&&budgetOK){
     ticket={home:operating,entryReserve:bid.entryReserve,returnReserve:bid.returnReserve,
       remaining:bid.escrow,committed:bid.escrow,entryTick:tick,returnTick:tick+6};
     expectedReserveTotal+=bid.escrow;entryReserveTotal+=bid.entryReserve;
     transition={from:operating,to,phase:'entry',probe:true};
     operating=to;stage='active';probesStarted++;lastProbe=tick;
     reason='escrow-entry';probes.push({tick,reserve:bid.escrow,home:ticket.home,to});
    }else{denied++;reason=!bid.allowed?'eligibility-denied':'budget-denied'}
  }
  counts[operating]++;
  const a=wag251Choice(x,models,lastRepair,'fixed'+operating).action;
  if(a!=='abstain')lastRepair=tick;
  if(WAG250_SAMPLE.includes(tick%240)&&tick+48<=duration)
   receipts.push({tick,action:a,cadence:operating,reason,
      spent,activeEscrow:ticket?.remaining??0,stage});
  // Cost is outside the WAG-244 energy engine and counted in spendable budget.
  step244(x,a);
  if(transition){
    const features=wag254Signals(x,tick-lastChange,transition.from,transition.to);
    const est=wag254Estimate(x,tick-lastChange,transition.from,transition.to,cost);
    const tx={...transition,features,predicted:est.mean};
    const actual=wag255ActualFee(x,tx,regime,tick);
    const reserved=transition.phase==='entry'?ticket.entryReserve:ticket.returnReserve;
    // Contract is bounded: under envelope, the reserved leg covers the charge.
    if(actual>reserved+1e-10){breaches++;unbudgeted+=actual-reserved}
    const charge=Math.min(actual,reserved);
    ticket.remaining-=charge;spent+=charge;probeFees+=charge;
    if(transition.phase==='return'){
      probesReturned++;history.push({tick,phase:'return',actual,charged:charge,reserved,
        escrowReleased:ticket.remaining,breach:actual>reserved+1e-10});
      ticket=null;lastChange=tick;
    }else history.push({tick,phase:'entry',actual,charged:charge,reserved,
        breach:actual>reserved+1e-10});
  }
 }
 if(stage==='active')trapped++;
 return {mode:variant,capacity:cap,scenario:family,seed,duration,regime,
  decision:decision.action,meanIntegrity:x.s.area/duration,finalEnergy:x.s.energy,
  aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
  reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  maintenance:x.choices,probesStarted,probesReturned,trapped,breaches,
  budgetSpent:spent,probeFees,unbudgeted,denied,history,probes,receipts,counts,
  ledger:wag248Ledger(x),trace:x.s.trace,
  caveat:'Return guaranteed solely inside declared 8x synthetic fee envelope; the energy budget is shadow-accounted.'};
}
function wag259Experiment(){
 const models=wag251Models(),cadence=wag252Train(models),cost=wag254Train(models),
 voi=wag258Train(models,cadence,cost),groups={},examples=[];
 for(const regime of ['stable','surcharge','nonlinear','shock'])
 for(const family of ['scar','combined','phaseflip','famine'])for(const cap of CAP234)
 for(const seed of WAG259_TEST){
  const a=wag259Run(cap,family,seed,240,regime,'diagnostic',models,cadence,cost,voi);
  const b=wag259Run(cap,family,seed,240,regime,'gated',models,cadence,cost,voi);
  const old=wag259Run(cap,family,seed,240,regime,'wag256',models,cadence,cost,voi);
  const key=regime+':'+family,g=groups[key]??={n:0,diagnosticEntries:0,returns:0,trapped:0,
    breaches:0,gatedEntries:0,oldEntries:0,oldTrapped:0,meanFee:0};
  g.n++;g.diagnosticEntries+=a.probesStarted;g.returns+=a.probesReturned;
  g.trapped+=a.trapped;g.breaches+=a.breaches;g.gatedEntries+=b.probesStarted;
  g.oldEntries+=old.probeCount;g.oldTrapped+=(old.probeStage==='trapped'?1:0);
  g.meanFee+=a.probeFees;
  if(cap===13&&seed===4701)examples.push({regime,family,
   diagnostic:{entries:a.probesStarted,returns:a.probesReturned,fees:a.probeFees,breaches:a.breaches},
   gated:{entries:b.probesStarted,returns:b.probesReturned},
   old:{entries:old.probeCount,stage:old.probeStage},history:a.history});
 }
 for(const g of Object.values(groups))g.meanFee/=g.n;
 return {bound:'WAG-259',phase:'II',turn:3,groups,examples,
  envelope:WAG259_ENVELOPE,budget:WAG259_TOTAL_BUDGET,
  caveat:'Bounded 8x synthetic fees only; diagnostic probing does not override production VOI abstention.'};
}
if(typeof module!=='undefined')module.exports={wag259Escrow,wag259Run,wag259Experiment};
