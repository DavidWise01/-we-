/* WAG-254 · contextual cost of changing repair cadence · .dlw
 Synthetic transaction fees are known to the environment but hidden from online
 controller. Learn by offline samples; online controller sees frozen cost table,
 current observed features, and WAG-252 cadence recommendation only.
 Ledger: switching energy is an additional expense outside WAG-244 transfer ledger.
 */
const WAG254_TRAIN=[4001,4002,4003,4004],WAG254_TEST=[4101,4102,4103,4104];
const WAG254_SWITCHES=[3,6,12,24],WAG254_HORIZON=72;
function wag254Signals(x,age,from,to){
 const s=wag251Signals(x);
 return {energy:s.energy,scar:s.scar,material:s.material,age,
   scarce:s.energy<.48||s.material<.032,
   damaged:s.scar>.065,
   reversal:age<12,
   distance:Math.abs(Math.log2(to/from))};
}
function wag254TrueFee(features,from,to){
 if(from===to)return 0;
 // Synthetic world rule, not a measured physical cost.
 const base=wag253Fee(from,to);
 return base*(1+(features.scarce?.65:0)+(features.damaged?.35:0)+
    (features.reversal?.55:0));
}
function wag254Key(from,to,f){return [Math.abs(Math.log2(to/from)),+f.scarce,+f.damaged,+f.reversal].join(':')}
function wag254Parent(from,to,f){return [Math.abs(Math.log2(to/from)),+f.scarce,+f.damaged].join(':')}
function wag254Stat(){return {n:0,mean:0,m2:0}}
function wag254Add(z,value){z.n++;const delta=value-z.mean;z.mean+=delta/z.n;z.m2+=delta*(value-z.mean)}
function wag254Train(models){
 const fine={},parent={};let samples=0;
 for(const cap of CAP234)for(const family of FAMILIES_TRAIN244)for(const seed of WAG254_TRAIN){
  const x=start244(cap,family,seed,480);x.modelTable=models.train250.source;
  while(x.t<240){
   if([36,84,132,180,216].includes(x.t)){
    for(const energy of [.28,.52,.78])for(const age of [3,9,18])
     for(const from of WAG254_SWITCHES)for(const to of WAG254_SWITCHES){
      if(from===to)continue;
      const controlled=clone244(x);controlled.s.energy=energy;
      const features=wag254Signals(controlled,age,from,to);
      const value=wag254TrueFee(features,from,to);
      wag254Add(fine[wag254Key(from,to,features)]??=wag254Stat(),value);
      wag254Add(parent[wag254Parent(from,to,features)]??=wag254Stat(),value);
      samples++;
     }
   }
   step244(x,'abstain');
  }
 }
 return {fine,parent,samples,seeds:WAG254_TRAIN,minFine:12,minParent:24,
   note:'Calibrates a declared synthetic transaction cost law, not an unknown physical law'};
}
function wag254Estimate(x,age,from,to,trained){
 const f=wag254Signals(x,age,from,to),z=trained.fine[wag254Key(from,to,f)]?.n>=trained.minFine?
 trained.fine[wag254Key(from,to,f)]:trained.parent[wag254Parent(from,to,f)]?.n>=trained.minParent?
 trained.parent[wag254Parent(from,to,f)]:null;
 if(!z)return {mean:wag253Fee(from,to)*2.55,upper:wag253Fee(from,to)*2.55,known:false,n:0,features:f};
 const sd=z.n>1?Math.sqrt(z.m2/(z.n-1)):0;
 return {mean:z.mean,upper:z.mean+1.64*sd/Math.sqrt(z.n),known:true,n:z.n,features:f};
}
function wag254State(){return {cadence:6,candidate:null,streak:0,lastChange:-100,
  switches:0,fees:0,blocked:0,requested:0,errors:[],forecasts:[]}}
function wag254Choose(x,trainedCadence,costModel,state,variant){
 const recommended=wag252Select(x,trainedCadence),target=recommended.cadence;
 if(target===state.cadence){state.candidate=null;state.streak=0;
  return {cadence:state.cadence,target,reason:'steady'};}
 if(target!==state.candidate){state.candidate=target;state.streak=1}
 else state.streak++;
 state.requested++;
 const age=x.t-state.lastChange,est=wag254Estimate(x,age,state.cadence,target,costModel);
 const predValue=Math.max(0,recommended.margin||0);
 // Fee is compared in the SAME normalized 72-tick value scale:
 // WAG-252 value adds 0.18 * terminal energy, hence convert fee to value units.
 const feeValue=.18*est.upper;
 const urgent=target<state.cadence&&est.features.damaged&&
 est.features.energy>.65&&est.features.material>.045;
 const enough=variant==='learnedCost'?state.streak>=2:
  variant==='confirm4'?state.streak>=4:state.streak>=2;
 if(!enough&&!urgent){state.blocked++;
  return {cadence:state.cadence,target,reason:'confirming',estimated:est}}
 if(variant==='learnedCost'&&!urgent&&(!est.known||predValue<=feeValue+.00002)){
  state.blocked++;return {cadence:state.cadence,target,reason:'fee-exceeds-margin',estimated:est}}
 if(x.s.energy-est.upper<.38){state.blocked++;
  return {cadence:state.cadence,target,reason:'energy-floor',estimated:est}}
 const previous=state.cadence;state.cadence=target;state.candidate=null;state.streak=0;
 state.lastChange=x.t;state.switches++;
 return {cadence:target,target,reason:urgent?'urgent':'approved',estimated:est,
  transition:{from:previous,to:target,predicted:est.mean,upper:est.upper,features:est.features}};
}
function wag254Run(cap,family,seed,duration,variant,models,cadenceModel,costModel){
 if(variant==='wag252'||variant==='fixed3'||variant==='wag250')
  return wag253Run(cap,family,seed,duration,variant,models,cadenceModel);
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const st=wag254State(),counts={3:0,6:0,12:0,24:0},receipts=[],transitions=[];
 let lastRepair=-100,regret=0,missed=0,opportunities=0;
 while(x.t<duration){
  const choice=wag254Choose(x,cadenceModel,costModel,st,variant),
   cadence=choice.cadence;counts[cadence]++;
  const d=wag251Choice(x,models,lastRepair,'fixed'+cadence),action=d.action;
  if(action!=='abstain')lastRepair=x.t;
  if(WAG250_SAMPLE.includes(x.t%240)&&x.t+48<=duration){
   const eligible=['prevent','rebuild'].filter(a=>wag246Eligible(x,a));
   const vals=Object.fromEntries(eligible.map(a=>[a,wag250Evaluate(x,a).value]));
   const best=Math.max(0,...Object.values(vals)),chosen=action==='abstain'?0:(vals[action]??0),
    loss=Math.max(0,best-chosen);
   regret+=loss;if(best>.00005){opportunities++;if(action==='abstain')missed++}
   receipts.push({tick:x.t,action,cadence,target:choice.target,reason:choice.reason,
     energy:x.s.energy,scar:1-x.s.ceiling,regret:loss});
  }
  step244(x,action);
  if(choice.transition){
   // Actual simulator fee is measured only after deciding. This is never leaked
   // back into the current decision. Future decisions can observe spent energy.
   const trueFee=wag254TrueFee(choice.transition.features,choice.transition.from,choice.transition.to);
   const debit=Math.min(x.s.energy,trueFee);
   x.s.energy-=debit;st.fees+=debit;
   x.s.trace[x.s.trace.length-1].energy=x.s.energy;
   const record={tick:x.t-1,from:choice.transition.from,to:choice.transition.to,
     predicted:choice.transition.predicted,actual:trueFee,charged:debit,upper:choice.transition.upper};
   transitions.push(record);st.errors.push(Math.abs(trueFee-record.predicted));
  }
 }
 const ledger=wag248Ledger(x);
 return {mode:variant,capacity:cap,scenario:family,seed,duration,
 meanIntegrity:x.s.area/duration,finalIntegrity:x.s.integrity,finalEnergy:x.s.energy,
 aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
 reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
 maintenance:x.choices,materialUsed:x.materialSpent,materialLeft:x.material,
 switches:st.switches,switchFees:st.fees,blocked:st.blocked,requested:st.requested,
 cadenceCounts:counts,feeMAE:st.errors.length?st.errors.reduce((a,b)=>a+b,0)/st.errors.length:null,
 regret,missed,opportunities,transitions,receipts,ledger,trace:x.s.trace,
 feeProvenance:'synthetic fee schedule, measured after policy decision'};
}
function wag254Experiment(){
 const models=wag251Models(),cadence=wag252Train(models),cost=wag254Train(models),
 groups={},examples=[];
 for(const duration of [240,480])for(const cap of CAP234)
 for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])for(const seed of WAG254_TEST){
  const results={};
  for(const variant of ['learnedCost','confirm2','confirm4','wag252','fixed3','wag250'])
   results[variant]=wag254Run(cap,family,seed,duration,variant,models,cadence,cost);
  const key=duration+':'+(FAMILIES_HOLD244.includes(family)?'withheld':'familiar');
  const g=groups[key]??={n:0,policy:{},survivalVsWag252:0,integrityVsWag252:0};
  g.n++;if(results.learnedCost.aliveTicks>=results.wag252.aliveTicks&&
    results.learnedCost.reserveTicks>=results.wag252.reserveTicks)g.survivalVsWag252++;
  if(results.learnedCost.meanIntegrity>=results.wag252.meanIntegrity)g.integrityVsWag252++;
  for(const [name,r] of Object.entries(results)){
   const z=g.policy[name]??={integrity:0,alive:0,reserve:0,repairs:0,switches:0,fee:0,regret:0};
   z.integrity+=r.meanIntegrity;z.alive+=r.aliveTicks;z.reserve+=r.reserveTicks;
   z.repairs+=r.maintenance.prevent+r.maintenance.rebuild;
   z.switches+=r.switches??0;z.fee+=r.switchFees??0;z.regret+=r.regret??0;
  }
  if(duration===240&&cap===13&&seed===4101&&['scar','combined','phaseflip'].includes(family))
   examples.push({family,cap,seed,transitions:results.learnedCost.transitions,
    policies:Object.fromEntries(Object.entries(results).map(([k,r])=>[k,{
     integrity:r.meanIntegrity,alive:r.aliveTicks,reserve:r.reserveTicks,
     switches:r.switches,fees:r.switchFees}]))});
 }
 for(const g of Object.values(groups))for(const z of Object.values(g.policy))
  for(const k of Object.keys(z))z[k]/=g.n;
 return {bound:'WAG-254',training:{feeSamples:cost.samples,fine:Object.keys(cost.fine).length,
  parent:Object.keys(cost.parent).length,seeds:cost.seeds},testSeeds:WAG254_TEST,
  groups,examples,limitations:'All costs from one declared synthetic transaction law'};
}
if(typeof module!=='undefined')module.exports={wag254Train,wag254Estimate,wag254Run,wag254Experiment};
