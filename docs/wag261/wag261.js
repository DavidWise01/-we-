/* WAG-261 · multi-horizon recovery decision · Phase II 5/12 · .dlw
 Three horizons (24,48,96) labelled offline from synthetic branch rollouts.
 Frozen state bins only online. WAG250's certified decision is fallback;
 longer-horizon evidence may upgrade abstention if robust benefit survives
 all three scales. One deterministic decision at each tick.
*/
const WAG261_TRAIN=[4901,4902,4903],WAG261_TEST=[5001,5002,5003,5004];
const WAG261_HORIZONS=[24,48,96],WAG261_TICKS=[48,96,144,192];
function wag261Key(x){const s=wag251Signals(x);
 return [CAP234.indexOf(x.cap),s.scar>.065?'heavy':s.scar>.018?'mid':'light',
 s.energy<.47?'low':s.energy<.70?'mid':'high',s.material<.04?'scarce':'supplied'].join(':')}
function wag261Parent(x){const s=wag251Signals(x);return [CAP234.indexOf(x.cap),
 s.scar>.065?'heavy':s.scar>.018?'mid':'light',s.energy<.47?'low':'supplied'].join(':')}
function wag261Cell(){return {n:0,means:[0,0,0],m2:[0,0,0],survival:[0,0,0],reserve:[0,0,0]}}
function wag261Add(z,observations){z.n++;observations.forEach((v,i)=>{const delta=v.value-z.means[i];z.means[i]+=delta/z.n;z.m2[i]+=delta*(v.value-z.means[i]);z.survival[i]+=(v.alive-z.survival[i])/z.n;z.reserve[i]+=(v.reserve-z.reserve[i])/z.n})}
function wag261Train(models){const fine={},coarse={};let observations=0,snapshots=0;
 for(const cap of CAP234)for(const family of FAMILIES_TRAIN244)for(const seed of WAG261_TRAIN){
  const x=start244(cap,family,seed,360);x.modelTable=models.train250.source;
  while(x.t<240){
   if(WAG261_TICKS.includes(x.t)){
    for(const energy of [.45,.65,.83]){
     const y=clone244(x);y.s.energy=energy;snapshots++;
     for(const action of ['prevent','rebuild']){
      if(!wag246Eligible(y,action))continue;
      const outcomes=WAG261_HORIZONS.map(h=>wag250Evaluate(y,action,h));
      const key=wag261Key(y),parent=wag261Parent(y);
      wag261Add((fine[key]??={})[action]??=wag261Cell(),outcomes);
      wag261Add((coarse[parent]??={})[action]??=wag261Cell(),outcomes);
      observations+=3;
     }
    }
   }
   step244(x,'abstain');
  }
 }
 return {fine,coarse,snapshots,observations,seeds:WAG261_TRAIN,horizons:WAG261_HORIZONS,minFine:8,minCoarse:12};
}
function wag261Estimate(x,action,trained){
 const f=trained.fine[wag261Key(x)]?.[action],p=trained.coarse[wag261Parent(x)]?.[action];
 const z=f?.n>=trained.minFine?f:p?.n>=trained.minCoarse?p:null;
 if(!z)return null;
 const lowers=z.means.map((mean,i)=>mean-1.64*Math.sqrt((z.n>1?z.m2[i]/(z.n-1):0)/z.n));
 const combined=.25*lowers[0]+.35*lowers[1]+.40*lowers[2];
 return {n:z.n,means:z.means,lowers,combined,survival:z.survival,reserve:z.reserve};
}
function wag261Select(x,models,trained,lastRepair,variant='multi'){
 const baseline=wag250Decision(x,models.train250,models.ref248,models.cal249,models.ref244,lastRepair,'regret');
 if(variant==='wag250')return {action:baseline.action,reason:'reference',baseline:baseline.action};
 if(x.t%6!==0)return {action:'abstain',reason:'checkpoint-schedule',baseline:'abstain'};
 if(x.t-lastRepair<6||x.s.energy<.43||x.material<.017)
  return {action:'abstain',reason:'resource-or-cooldown',baseline:baseline.action};
 if(baseline.action!=='abstain')return {action:baseline.action,reason:'reference-preserved',baseline:baseline.action};
 // Explicitly restrict upgrades to well-supported delayed benefits; do not
 // infer future from the held-out rollout. No exploration by default.
 const options=['prevent','rebuild'].filter(a=>wag246Eligible(x,a)).map(action=>({
  action,estimate:wag261Estimate(x,action,trained)
 })).filter(v=>v.estimate&&v.estimate.n>=12&&
 v.estimate.lowers[2]>.00012&&v.estimate.combined>.00007&&
 v.estimate.survival.every(n=>n>=-.002)&&v.estimate.reserve.every(n=>n>=-.002));
 options.sort((a,b)=>b.estimate.combined-a.estimate.combined||
  (a.action==='prevent'?-1:1));
 if(options.length)return {action:options[0].action,reason:'supported-long-horizon',baseline:'abstain',estimate:options[0].estimate};
 return {action:'abstain',reason:'no-supported-upgrade',baseline:'abstain'};
}
function wag261Run(cap,family,seed,duration,variant,models,trained){
 if(variant==='wag260')return wag260Run(cap,family,seed,duration,'stable','selector',models,models,null,{});
 if(variant==='wag250')return wag250Run(cap,family,seed,duration,'wag250',models.train250,models);
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 let lastRepair=-100,regret=0,opportunities=0,missed=0;
 const counts={wait:0,prevent:0,rebuild:0},receipts=[],upgrades=[];
 while(x.t<duration){
  const decision=wag261Select(x,models,trained,lastRepair);
  const action=decision.action;if(action!=='abstain')lastRepair=x.t;
  counts[action==='abstain'?'wait':action]++;
  if(decision.reason==='supported-long-horizon')upgrades.push({tick:x.t,action,estimate:decision.estimate});
  if(WAG250_SAMPLE.includes(x.t%240)&&x.t+48<=duration){
   const choices=['prevent','rebuild'].filter(a=>wag246Eligible(x,a));
   const values=Object.fromEntries(choices.map(a=>[a,wag250Evaluate(x,a).value]));
   const best=Math.max(0,...Object.values(values));
   const selected=action==='abstain'?0:values[action]??0;
   const loss=Math.max(0,best-selected);regret+=loss;
   if(best>.00005){opportunities++;if(action==='abstain')missed++}
   receipts.push({tick:x.t,action,reason:decision.reason,baseline:decision.baseline,
    regret:loss,energy:x.s.energy,scar:1-x.s.ceiling});
  }
  step244(x,action);
 }
 return {mode:variant,capacity:cap,scenario:family,seed,duration,
  meanIntegrity:x.s.area/duration,finalIntegrity:x.s.integrity,finalEnergy:x.s.energy,
  aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
  reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  counts,upgrades,maintenance:x.choices,regret,missed,opportunities,
  ledger:wag248Ledger(x),receipts,trace:x.s.trace};
}
function wag261Experiment(){
 const models=wag251Models(),trained=wag261Train(models),groups={},examples=[];
 for(const cap of CAP234)for(const family of ['scar','combined','phaseflip','famine'])
 for(const seed of WAG261_TEST){
  const a=wag261Run(cap,family,seed,240,'multi',models,trained);
  const b=wag261Run(cap,family,seed,240,'wag250',models,trained);
  const g=groups[family]??={n:0,integrityDelta:0,aliveNonInferior:0,reserveNonInferior:0,
   integrityNonInferior:0,upgrades:0};
  g.n++;g.integrityDelta+=a.meanIntegrity-b.meanIntegrity;
  g.aliveNonInferior+=a.aliveTicks>=b.aliveTicks?1:0;
  g.reserveNonInferior+=a.reserveTicks>=b.reserveTicks?1:0;
  g.integrityNonInferior+=a.meanIntegrity>=b.meanIntegrity?1:0;
  g.upgrades+=a.upgrades.length;
  if(cap===13&&seed===5001)examples.push({family,seed,integrity:a.meanIntegrity,
   reference:b.meanIntegrity,upgrades:a.upgrades.length,alive:a.aliveTicks,reserve:a.reserveTicks});
 }
 for(const g of Object.values(groups))g.integrityDelta/=g.n;
 return {bound:'WAG-261',trainSnapshots:trained.snapshots,trainObservations:trained.observations,
  trainingSeeds:trained.seeds,heldOutSeeds:WAG261_TEST,groups,examples,
  limitation:'Offline multi-horizon labels share the simulator; only frozen state-cell estimates are allowed online.'};
}
if(typeof module!=='undefined')module.exports={wag261Train,wag261Estimate,wag261Select,wag261Run,wag261Experiment};
