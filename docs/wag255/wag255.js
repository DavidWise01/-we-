/* WAG-255 · unseen switching cost and online mismatch detection · .dlw
  Load WAG-245..254 first. Simulation regimes hidden from controller until costs are
  charged. Receipts are append-only; online forecasts use only past receipts.
  Synthetic model only. Seed families never used to tune the frozen policy.
*/
const WAG255_TEST=[4201,4202,4203,4204];
const WAG255_REGIMES=['stable','surcharge','nonlinear','shock'];
const WAG255_VARIANTS=['detect','frozen','cautious','confirm4'];
function wag255ActualFee(x,transition,regime,tick){
 const f=transition.features,nominal=wag254TrueFee(f,transition.from,transition.to);
 if(regime==='stable')return nominal;
 if(regime==='surcharge')return nominal*(tick>=60?3.5:1);
 if(regime==='nonlinear')return nominal*(1+3.2*Math.max(0,.65-x.s.energy)+
   2.1*Math.max(0,f.scar-.03)+1.5*(tick%48<12?1:0));
 if(regime==='shock')return nominal*(tick>=108&&tick<190?6.0:1);
 throw Error('Unknown cost regime');
}
function wag255State(){
 return {cadence:6,candidate:null,streak:0,lastChange:-100,
   switches:0,fees:0,observed:[],mismatches:0,flagged:0,blocked:0,
   charges:0,overruns:0};
}
function wag255Risk(state){
 const recent=state.observed.slice(-5);
 const ratios=recent.map(r=>r.ratio);
 if(!ratios.length)return {status:'unseen',multiplier:1,n:0,upper:1};
 const mean=ratios.reduce((a,b)=>a+b,0)/ratios.length;
 const upper=Math.max(...ratios,mean);
 const alarm=ratios.slice(-2).some(v=>v>1.55)||mean>1.55;
 return {status:alarm?'mismatch':'observed',multiplier:mean,n:ratios.length,upper};
}
function wag255Select(x,state,cadenceModel,costModel,variant){
 const recommendation=wag252Select(x,cadenceModel),target=recommendation.cadence;
 const risk=wag255Risk(state);
 if(target===state.cadence){state.candidate=null;state.streak=0;
   return {cadence:state.cadence,target,reason:'stable',risk};}
 if(target!==state.candidate){state.candidate=target;state.streak=1;}else state.streak++;
 const age=x.t-state.lastChange,est=wag254Estimate(x,age,state.cadence,target,costModel);
 const minStreak=variant==='confirm4'?4:variant==='cautious'?6:2;
 if(state.streak<minStreak){state.blocked++;
   return {cadence:state.cadence,target,reason:'confirming',risk,est};}
 let upper=est.upper;
 if(variant==='detect'&&risk.status==='mismatch')upper*=Math.max(2,risk.upper);
 if(variant==='cautious')upper*=2.5;
 const safe=x.s.energy-upper>.38;
 const expectedGain=Math.max(0,recommendation.margin||0),costInValue=.18*upper;
 const supported=variant==='confirm4'?safe:safe&&est.known&&expectedGain>costInValue+.00002;
 if(!supported){state.blocked++;if(risk.status==='mismatch')state.flagged++;
   return {cadence:state.cadence,target,reason:risk.status==='mismatch'?'cost-mismatch-gate':'not-worth-cost',risk,est};}
 const from=state.cadence;state.cadence=target;state.streak=0;state.candidate=null;
 state.lastChange=x.t;state.switches++;
 return {cadence:target,target,reason:risk.status==='mismatch'?'repriced':'approved',risk,est,
   transition:{from,to:target,predicted:est.mean,upper:est.upper,features:est.features}};
}
function wag255Run(cap,family,seed,duration,regime,variant,models,cadenceModel,costModel){
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const state=wag255State(),counts={3:0,6:0,12:0,24:0},transitions=[],receipts=[];
 let lastRepair=-100,regret=0,missed=0,opportunities=0;
 while(x.t<duration){
  const d=wag255Select(x,state,cadenceModel,costModel,variant),cadence=d.cadence;
  counts[cadence]++;
  const repair=wag251Choice(x,models,lastRepair,'fixed'+cadence),action=repair.action;
  if(action!=='abstain')lastRepair=x.t;
  if(WAG250_SAMPLE.includes(x.t%240)&&x.t+48<=duration){
   const choices=['prevent','rebuild'].filter(a=>wag246Eligible(x,a));
   const values=Object.fromEntries(choices.map(a=>[a,wag250Evaluate(x,a).value]));
   const best=Math.max(0,...Object.values(values));
   const chosen=action==='abstain'?0:(values[action]??0);
   regret+=Math.max(0,best-chosen);
   if(best>.00005){opportunities++;if(action==='abstain')missed++;}
   receipts.push({tick:x.t,action,cadence,suggested:d.target,
     status:d.risk.status,ratio:d.risk.multiplier,reason:d.reason,
     energy:x.s.energy,scar:1-x.s.ceiling});
  }
  // Transition uses unchanged inherited physics before fee is charged.
  step244(x,action);
  if(d.transition){
   const actual=wag255ActualFee(x,d.transition,regime,x.t-1);
   const charged=Math.min(x.s.energy,actual);
   x.s.energy-=charged;
   x.s.trace.at(-1).energy=x.s.energy;
   state.fees+=charged;state.charges++;
   const predicted=d.transition.predicted,ratio=actual/Math.max(1e-12,predicted);
   if(ratio>1.55)state.mismatches++;
   if(actual>d.transition.upper)state.overruns++;
   const receipt={tick:x.t-1,from:d.transition.from,to:d.transition.to,
     predicted,actual,charged,ratio,regime,priorStatus:d.risk.status};
   state.observed.push(receipt);transitions.push(receipt);
  }
 }
 const ledger=wag248Ledger(x);
 return {mode:variant,regime,capacity:cap,scenario:family,seed,duration,
   meanIntegrity:x.s.area/duration,finalIntegrity:x.s.integrity,finalEnergy:x.s.energy,
   aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
   reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
   maintenance:x.choices,materialUsed:x.materialSpent,
   switches:state.switches,switchFees:state.fees,
   mismatchReceipts:state.mismatches,exceededBounds:state.overruns,
   deferred:state.blocked,blockedByMismatch:state.flagged,
   cadenceCounts:counts,missed,opportunities,regret,transitions,receipts,
   ledger,trace:x.s.trace,
   provenance:'Regime is read only by hidden synthetic fee environment; online policy sees charged receipts'};
}
function wag255Experiment(){
 const models=wag251Models(),cadence=wag252Train(models),cost=wag254Train(models);
 const groups={},examples=[];
 for(const regime of WAG255_REGIMES)for(const duration of [240,480])
 for(const cap of CAP234)for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])
 for(const seed of WAG255_TEST){
  const runs={};for(const v of WAG255_VARIANTS)
   runs[v]=wag255Run(cap,family,seed,duration,regime,v,models,cadence,cost);
  const group=regime+':'+duration+':'+(FAMILIES_HOLD244.includes(family)?'withheld':'familiar');
  const z=groups[group]??={n:0,policies:{},survivalNonInferior:0};
  z.n++;
  if(runs.detect.aliveTicks>=runs.frozen.aliveTicks&&runs.detect.reserveTicks>=runs.frozen.reserveTicks)z.survivalNonInferior++;
  for(const [v,r] of Object.entries(runs)){
   const p=z.policies[v]??={integrity:0,alive:0,reserve:0,switches:0,fees:0,
     mismatch:0,overruns:0,regret:0};
   p.integrity+=r.meanIntegrity;p.alive+=r.aliveTicks;p.reserve+=r.reserveTicks;
   p.switches+=r.switches;p.fees+=r.switchFees;p.mismatch+=r.mismatchReceipts;
   p.overruns+=r.exceededBounds;p.regret+=r.regret;
  }
  if(duration===240&&cap===13&&seed===4201&&['scar','combined'].includes(family))
   examples.push({regime,family,seed,
     policies:Object.fromEntries(Object.entries(runs).map(([k,v])=>[k,{
       integrity:v.meanIntegrity,alive:v.aliveTicks,reserve:v.reserveTicks,
       switches:v.switches,fees:v.switchFees,overruns:v.exceededBounds}])),
     receipts:runs.detect.transitions});
 }
 for(const z of Object.values(groups))for(const p of Object.values(z.policies))
  for(const k of Object.keys(p))p[k]/=z.n;
 return {bound:'WAG-255',regimes:WAG255_REGIMES,testSeeds:WAG255_TEST,groups,examples,
   limitations:'Synthetic hidden transaction regimes; mismatch can only be detected after at least one paid transition'};
}
if(typeof module!=='undefined')module.exports={wag255Run,wag255Experiment,wag255Risk,wag255ActualFee};
