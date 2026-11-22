/* WAG-260 · Hegemonic Best-Action Selector · Phase II turn 4/12 · .dlw
 Single deterministic action from WAIT, PREVENT, REBUILD, PROBE, RETURN.
 Safety gates outrank utility; fixed tie breaks. All online information is
 present/past only, with frozen WAG250 repair model, WAG258 VOI, WAG259 escrow.
 Cost fees are shadow-accounted: inherited simulator may reset external debits.
 Source ancestry = a single deterministic synthetic simulation engine.
*/
const WAG260_TEST=[4801,4802,4803,4804];
const WAG260_REGIMES=['stable','surcharge','nonlinear','shock'];
const WAG260_TIES={wait:0,prevent:1,rebuild:2,probe:3,return:4};
function wag260State(voiChoice){
 return {lastRepair:-100,cadence:6,stage:'idle',ticket:null,
  probeBudget:WAG259_TOTAL_BUDGET,spent:0,lastProbe:-100,
  repairs:0,probes:0,returns:0,breaches:0,trapped:0,
  decisionCounts:{wait:0,prevent:0,rebuild:0,probe:0,return:0},
  voiChoice,actionHistory:[],transactions:[]};
}
function wag260Candidates(x,model,refs,cost,st){
 const list=[{action:'wait',score:0,lower:0,reason:'safe-abstention',allowed:true}];
 if(st.stage==='active'){
  // Return must be executed at its committed time before considering any
  // competing repairs. Until then the probe is a single in-flight obligation.
  if(x.t>=st.ticket.returnTick)return [{action:'return',score:Infinity,lower:Infinity,
    allowed:true,reason:'committed-escrow-return'}];
  return list;
 }
 const floorEnergy=x.s.energy-st.spent;
 if(x.t-st.lastRepair>=6&&floorEnergy>.43){
  for(const action of ['prevent','rebuild']){
   if(!wag246Eligible(x,action))continue;
   const e=wag250Estimate(x,action,model.train250);
   if(!e||e.energy<-.045||e.alive<-.003||e.reserve<-.003)continue;
   if(!Number.isFinite(e.lower)||e.lower<=.000015)continue;
   list.push({action,score:e.lower,lower:e.lower,reason:'positive-repair-bound',allowed:true});
  }
 }
 const opportunity=WAG259_WINDOWS.includes(x.t)&&x.t-st.lastProbe>=42;
 if(st.voiChoice.action==='valueProbe'&&opportunity){
  const to=st.cadence===3?6:3,bid=wag259Escrow(x,st.cadence,to,st.lastProbe,cost,st.spent);
  if(bid.allowed&&st.spent+bid.escrow<=st.probeBudget){
    const lower=st.voiChoice.lower??-Infinity;
    if(lower>.00001)list.push({action:'probe',score:lower,lower,
      bid,to,reason:'positive-voi-and-return-funded',allowed:true});
  }
 }
 return list;
}
function wag260Select(x,model,refs,cost,st){
 const candidates=wag260Candidates(x,model,refs,cost,st);
 const sorted=candidates.slice().sort((a,b)=>(b.score-a.score)||
  ((a.action==='wait'?0:1)-(b.action==='wait'?0:1))||
  (WAG260_TIES[a.action]-WAG260_TIES[b.action]));
 return {action:sorted[0].action,reason:sorted[0].reason,candidates,
  selected:sorted[0],tiePolicy:'max lower-bound, wait on equality, stable action order'};
}
function wag260Run(cap,family,seed,duration,regime,variant,models,refs,cost,voi){
 if(variant==='wag250')return wag250Run(cap,family,seed,duration,'wag250',models.train250,refs);
 if(variant==='wag258')return wag256Run(cap,family,seed,duration,regime,'noProbe',models,refs.ref248,cost);
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const gate=variant==='selector'?wag258Decision(wag258Features(cap,family,seed,duration,models),voi):
  {action:'noProbe',reason:'no-probe-baseline',lower:null};
 const st=wag260State(gate),receipts=[];
 let regret=0,opportunities=0,missed=0;
 while(x.t<duration){
  const tick=x.t,decision=wag260Select(x,models,refs,cost,st),action=decision.action;
  let transition=null,physical='abstain';
  if(action==='prevent'||action==='rebuild'){physical=action;st.lastRepair=tick;st.repairs++;}
  if(action==='probe'){
   const b=decision.selected.bid;st.ticket={home:st.cadence,target:decision.selected.to,
      entryReserve:b.entryReserve,returnReserve:b.returnReserve,returnTick:tick+6};
   transition={from:st.cadence,to:st.ticket.target,phase:'entry'};
   st.cadence=st.ticket.target;st.stage='active';st.probes++;st.lastProbe=tick;
  }else if(action==='return'){
   transition={from:st.cadence,to:st.ticket.home,phase:'return'};
   st.cadence=st.ticket.home;st.returns++;st.stage='idle';
  }
  st.decisionCounts[action]++;
  if(WAG250_SAMPLE.includes(tick%240)&&tick+48<=duration){
   const options=['prevent','rebuild'].filter(a=>wag246Eligible(x,a));
   const future=options.map(a=>wag250Evaluate(x,a).value);
   const best=Math.max(0,...future),chosen=physical==='abstain'?0:wag250Evaluate(x,physical).value;
   const loss=Math.max(0,best-chosen);regret+=loss;
   if(best>.00005){opportunities++;if(physical==='abstain')missed++;}
   receipts.push({tick,action,reason:decision.reason,
     candidates:decision.candidates.map(z=>({action:z.action,score:z.score})),
     energy:x.s.energy,spent:st.spent,regret:loss});
  }
  step244(x,physical);
  if(transition){
   const f=wag254Signals(x,tick-st.lastProbe,transition.from,transition.to);
   const estimate=wag254Estimate(x,tick-st.lastProbe,transition.from,transition.to,cost);
   const charge=wag255ActualFee(x,{...transition,features:f,predicted:estimate.mean},regime,tick);
   const reserved=transition.phase==='entry'?st.ticket.entryReserve:st.ticket.returnReserve;
   if(charge>reserved+1e-10)st.breaches++;
   const debited=Math.min(charge,reserved);
   st.spent+=debited;
   st.transactions.push({tick,phase:transition.phase,from:transition.from,to:transition.to,
     predicted:estimate.mean,actual:charge,reserved,debited});
   if(transition.phase==='return')st.ticket=null;
  }
 }
 if(st.stage==='active')st.trapped++;
 return {mode:variant,regime,scenario:family,capacity:cap,seed,duration,
  meanIntegrity:x.s.area/duration,finalEnergy:x.s.energy,
  aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
  reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  maintenance:x.choices,regret,opportunities,missed,selected:st.decisionCounts,
  repairs:st.repairs,probes:st.probes,returns:st.returns,
  breaches:st.breaches,trapped:st.trapped,spent:st.spent,
  voi:gate,receipts,transactions:st.transactions,
  ledger:wag248Ledger(x),trace:x.s.trace,
  limitations:'WAG250 repair-value gate is conservative; event-level cost uses shadow fees; probe VOI frozen at episode start.'};
}
function wag260Experiment(){
 const models=wag251Models(),refs={...models},cadence=wag252Train(models),cost=wag254Train(models),voi=wag258Train(models,cadence,cost),
  groups={},examples=[];
 for(const regime of WAG260_REGIMES)for(const family of ['scar','combined','phaseflip','famine'])
 for(const cap of CAP234)for(const seed of WAG260_TEST){
  const a=wag260Run(cap,family,seed,240,regime,'selector',models,refs,cost,voi);
  const b=wag260Run(cap,family,seed,240,regime,'wag250',models,refs,cost,voi);
  const g=groups[regime+':'+family]??={n:0,integrity:0,baselineIntegrity:0,alive:0,
   reserve:0,repairs:0,probes:0,breaches:0,trapped:0,nonInferior:0};
  g.n++;g.integrity+=a.meanIntegrity;g.baselineIntegrity+=b.meanIntegrity;
  g.alive+=a.aliveTicks;g.reserve+=a.reserveTicks;g.repairs+=a.repairs;
  g.probes+=a.probes;g.breaches+=a.breaches;g.trapped+=a.trapped;
  g.nonInferior+=a.meanIntegrity>=b.meanIntegrity?1:0;
  if(cap===13&&seed===4801)examples.push({regime,family,selector:{
    integrity:a.meanIntegrity,alive:a.aliveTicks,reserve:a.reserveTicks,
    selected:a.selected,regret:a.regret},baseline:{integrity:b.meanIntegrity,
    alive:b.aliveTicks,reserve:b.reserveTicks},receipts:a.receipts});
 }
 for(const g of Object.values(groups))for(const k of ['integrity','baselineIntegrity','alive','reserve','repairs','probes'])g[k]/=g.n;
 return {bound:'WAG-260',phase:'II',turn:4,testSeeds:WAG260_TEST,groups,examples,
  caution:'Synthetic and conservative; one best action chosen per tick, but not yet calibrated over multiple horizons.'};
}
if(typeof module!=='undefined')module.exports={wag260Run,wag260Select,wag260Candidates,wag260Experiment};
