/* WAG-253 · cadence switching inertia · synthetic research · .dlw
 Loaded after WAG-245..252. Switching fee is an explicit *additional*
 modeled energy debit, distinct from WAG-244's source/transfer ledger.
 Future counterfactual regrets are logged after choice, never consumed online. */
const WAG253_TEST=[3901,3902,3903,3904];
const WAG253_VARIANTS=['immediate','confirm2','confirm4','hold12','no-fee-reference'];
const WAG253_SWITCH_BASE=.00020,WAG253_SWITCH_DISTANCE=.00008;
function wag253Fee(a,b){return a===b?0:WAG253_SWITCH_BASE+WAG253_SWITCH_DISTANCE*Math.abs(Math.log2(b/a))}
function wag253Controller(){return {cadence:6,candidate:null,streak:0,lastChange:-100,
 switches:0,fees:0,attempts:0,blocked:0,debts:0}};
function wag253Choose(x,model,state,variant){
 const selection=wag252Select(x,model),suggested=selection.cadence;
 if(variant==='immediate'||variant==='no-fee-reference'){
  const prev=state.cadence;state.cadence=suggested;
  if(prev!==suggested){state.switches++;state.lastChange=x.t}
  return {cadence:state.cadence,suggested,reason:prev===suggested?'stable':'immediate',selection,transition:prev===suggested?null:{from:prev,to:suggested,cost:wag253Fee(prev,suggested)}};
 }
 if(suggested===state.cadence){state.candidate=null;state.streak=0;
   return {cadence:state.cadence,suggested,reason:'agree',selection}}
 if(suggested!==state.candidate){state.candidate=suggested;state.streak=1}
 else state.streak++;
 state.attempts++;
 const required=variant==='confirm4'?4:variant==='confirm2'?2:1;
 const hold=variant==='hold12'?12:0;
 const cost=wag253Fee(state.cadence,suggested);
 const confidence=selection.margin??0;
 // Emergency escalation: shorter cadence can bypass sustained evidence only when
 // damage is severe and the system has resources to afford switching.
 const signals=wag251Signals(x);
 const urgency=suggested<state.cadence&&signals.scar>.09&&signals.energy>.68&&signals.material>.045;
 const ready=(state.streak>=required&&x.t-state.lastChange>=hold)||urgency;
 if(!ready){state.blocked++;return {cadence:state.cadence,suggested,reason:'pending',selection}}
 // The learned source policy is not permitted to switch if fee would push energy
 // through the established resource floor.
 if(x.s.energy-cost<.38){state.blocked++;return {cadence:state.cadence,suggested,reason:'switch-cost-floor',selection}}
 const prior=state.cadence;state.cadence=suggested;state.candidate=null;state.streak=0;
 state.switches++;state.lastChange=x.t;
 return {cadence:state.cadence,suggested,reason:urgency?'urgent-escalation':'confirmed',
   selection,transition:{from:prior,to:suggested,cost}};
}
function wag253Run(cap,family,seed,duration,variant,models,trained){
 if(variant==='wag252')return wag252Run(cap,family,seed,duration,'learned',models,trained);
 if(variant==='fixed3')return wag252Run(cap,family,seed,duration,'fixed3',models,trained);
 if(variant==='wag250')return wag252Run(cap,family,seed,duration,'wag250',models,trained);
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const state=wag253Controller(),cadenceCounts={3:0,6:0,12:0,24:0},transitions=[];
 let lastRepair=-100,regret=0,missed=0,opportunities=0;
 const receipts=[];
 while(x.t<duration){
  const decision=wag253Choose(x,trained,state,variant),cadence=decision.cadence;
  cadenceCounts[cadence]++;
  const repair=wag251Choice(x,models,lastRepair,'fixed'+cadence),action=repair.action;
  if(action!=='abstain')lastRepair=x.t;
  if(WAG250_SAMPLE.includes(x.t%240)&&x.t+48<=duration){
   const eligible=['prevent','rebuild'].filter(a=>wag246Eligible(x,a));
   const values=Object.fromEntries(eligible.map(a=>[a,wag250Evaluate(x,a).value]));
   const best=Math.max(0,...Object.values(values));
   const chosen=action==='abstain'?0:(values[action]??0);
   const loss=Math.max(0,best-chosen);regret+=loss;
   if(best>.00005){opportunities++;if(action==='abstain')missed++;}
   receipts.push({tick:x.t,cadence,suggested:decision.suggested,action,
    reason:decision.reason,regret:loss,energy:x.s.energy,scar:1-x.s.ceiling});
  }
  step244(x,action);
  if(decision.transition){transitions.push({tick:x.t-1,...decision.transition})}
  if(variant!=='no-fee-reference'&&decision.transition){
   // Charge fee on every actual cadence transition, once, after normal tick.
   const fee=decision.transition.cost;
   if(fee){x.s.energy=Math.max(0,x.s.energy-fee);state.fees+=fee;
     x.s.trace.at(-1).energy=+x.s.energy.toFixed(5)}
  }
 }
 const ledger=wag248Ledger(x);
 const result={mode:variant,capacity:cap,scenario:family,seed,duration,
  meanIntegrity:x.s.area/duration,finalIntegrity:x.s.integrity,finalEnergy:x.s.energy,
  aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
  reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  maintenance:x.choices,materialUsed:x.materialSpent,materialLeft:x.material,
  switches:state.switches,switchFees:state.fees,blocked:state.blocked,
  decisionCounts:cadenceCounts,regret,missed,opportunities,
  receipts,transitions,ledger,trace:x.s.trace,
  note:'Additional explicit energy switch fees do not participate in WAG-244 source/transfer conservation ledger'};
 return result;
}
function wag253Experiment(){
 const models=wag251Models(),trained=wag252Train(models),groups={},examples=[];
 for(const duration of [240,480])for(const cap of CAP234)
 for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])
 for(const seed of WAG253_TEST){
  const runs={};
  for(const variant of [...WAG253_VARIANTS,'wag252','fixed3','wag250'])
   runs[variant]=wag253Run(cap,family,seed,duration,variant,models,trained);
  const group=FAMILIES_HOLD244.includes(family)?'withheld':'familiar',key=duration+':'+group,
   z=groups[key]??={n:0,models:{},survivalNonInferior:0};
  z.n++;
  if(runs.confirm2.aliveTicks>=runs.wag252.aliveTicks&&runs.confirm2.reserveTicks>=runs.wag252.reserveTicks)
    z.survivalNonInferior++;
  for(const [name,r] of Object.entries(runs)){
   const p=z.models[name]??={integrity:0,alive:0,reserve:0,repairs:0,switches:0,fees:0,regret:0};
   p.integrity+=r.meanIntegrity;p.alive+=r.aliveTicks;p.reserve+=r.reserveTicks;
   p.repairs+=r.maintenance.prevent+r.maintenance.rebuild;
   p.switches+=r.switches??0;p.fees+=r.switchFees??0;p.regret+=r.regret??0;
  }
  if(duration===240&&cap===13&&seed===3901&&['scar','combined','phaseflip'].includes(family))
    examples.push({family,cap,seed,transitions:runs.confirm2.transitions,
      policies:Object.fromEntries(Object.entries(runs).map(([name,r])=>[name,{
      integrity:r.meanIntegrity,alive:r.aliveTicks,reserve:r.reserveTicks,
      switches:r.switches,fees:r.switchFees}]))});
 }
 for(const z of Object.values(groups))for(const v of Object.values(z.models))
  for(const k of Object.keys(v))v[k]/=z.n;
 return {bound:'WAG-253',testSeeds:WAG253_TEST,groups,examples,
  feeModel:{base:WAG253_SWITCH_BASE,perDoubling:WAG253_SWITCH_DISTANCE},
  caveat:'Fixed, preregistered hysteresis comparisons; synthetic switching fees; not a demonstrated general optimum.'};
}
if(typeof module!=='undefined')module.exports={wag253Run,wag253Experiment,wag253Choose,wag253Fee};
