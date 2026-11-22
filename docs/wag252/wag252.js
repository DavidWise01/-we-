/* WAG-252 · learned repair rhythm · deterministic, synthetic · .dlw
Train cadence on cloned early/middle/late states using existing WAG-251 gate,
without reading future forcing in online selection. Evaluate all policy choices
on separate seeds; provenance is one simulation engine. */
const WAG252_TRAIN=[3701,3702,3703,3704],WAG252_TEST=[3801,3802,3803,3804];
const WAG252_POINTS=[48,120,192],WAG252_ENERGY=[.24,.57,.78],WAG252_CADENCES=[3,6,12,24];
function wag252Key(x){const s=wag251Signals(x);
return [CAP234.indexOf(x.cap),s.energy<.42?'low':s.energy<.68?'mid':'high',
s.scar<.018?'minor':s.scar<.07?'moderate':'major',s.material<.035?'scarce':'supplied'].join(':')}
function wag252Parent(x){const s=wag251Signals(x);return [CAP234.indexOf(x.cap),
s.energy<.42?'low':s.energy<.68?'mid':'high',s.scar<.018?'minor':s.scar<.07?'moderate':'major'].join(':')}
function wag252Stats(){return {n:0,mean:0,m2:0,integrity:0,alive:0,reserve:0,materials:0,repairCount:0}}
function wag252Add(z,a){z.n++;const d=a.value-z.mean;z.mean+=d/z.n;z.m2+=d*(a.value-z.mean);
for(const k of ['integrity','alive','reserve','materials','repairCount'])z[k]+=(a[k]-z[k])/z.n}
function wag252Roll(x,cadence,models,horizon=72){
const y=clone244(x),t0=y.t,end=Math.min(y.duration,t0+horizon);
let lastRepair=-100,integral=0,alive=0,reserve=0,repairCount=0;
const beforeMaterial=y.material;
while(y.t<end){
 const choice=wag251Choice(y,models,lastRepair,'fixed'+cadence);
 if(choice.action!=='abstain'){lastRepair=y.t;repairCount++}
 step244(y,choice.action);integral+=y.s.integrity;
 alive+=(y.s.energy>.08&&y.s.integrity>.15)?1:0;
 reserve+=(y.s.energy>.25&&y.s.integrity>.30)?1:0;
}
const n=end-t0,integrity=integral/n,aliveFraction=alive/n,reserveFraction=reserve/n,
 materials=beforeMaterial-y.material,energy=y.s.energy;
return {value:integrity+.5*aliveFraction+.25*reserveFraction+.18*energy-.04*materials,
 integrity,alive:aliveFraction,reserve:reserveFraction,materials,repairCount};
}
function wag252Train(models){
 const fine={},parent={};let snapshots=0,comparisons=0;
 for(const cap of CAP234)for(const family of FAMILIES_TRAIN244)for(const seed of WAG252_TRAIN){
  const base=start244(cap,family,seed,480);base.modelTable=models.train250.source;
  while(base.t<240){
   if(WAG252_POINTS.includes(base.t))for(const energy of WAG252_ENERGY){
     const x=clone244(base);x.s.energy=energy;snapshots++;
     const results=WAG252_CADENCES.map(c=>({cadence:c,r:wag252Roll(x,c,models)}));
     const reference=results.find(z=>z.cadence===6).r.value;
     const key=wag252Key(x),pk=wag252Parent(x);
     for(const {cadence,r} of results){
      const v={...r,value:r.value-reference};
      wag252Add((fine[key]??={})[cadence]??=wag252Stats(),v);
      wag252Add((parent[pk]??={})[cadence]??=wag252Stats(),v);comparisons++;
     }
   }
   step244(base,'abstain');
  }
 }
 return {fine,parent,snapshots,comparisons,seeds:WAG252_TRAIN,minimumFine:8,minimumParent:12,
   noFutureLeakage:'Only frozen state-group table used online. Rollout labels used offline.'};
}
function wag252Select(x,model){
 const fine=model.fine[wag252Key(x)],parent=model.parent[wag252Parent(x)];
 const table=fine&&fine[6]?.n>=model.minimumFine?fine:
  parent&&parent[6]?.n>=model.minimumParent?parent:null;
 if(!table)return {cadence:6,reason:'uncovered-fallback',n:0,margin:0};
 // Reject candidates with a mean survival/reserve drop relative to cadence six
 // or with no lower-confidence advantage. All are matched paired rollouts.
 const sorted=WAG252_CADENCES.map(c=>{
 const z=table[c];if(!z||z.n<8)return null;
 const sd=z.n>1?Math.sqrt(z.m2/(z.n-1)):0;
 return {cadence:c,mean:z.mean,lower:z.mean-1.64*sd/Math.sqrt(z.n),n:z.n,
  reserve:z.reserve,alive:z.alive,materials:z.materials};
 }).filter(Boolean).sort((a,b)=>b.lower-a.lower);
 // Paired values are relative to fixed-6; choose shorter rhythm if its
 // estimated confidence-adjusted benefit beats fixed-6 by a modest margin.
 const selected=sorted.find(z=>z.lower>.00015&&z.alive>=.995&&z.reserve>=.995);
 if(!selected)return {cadence:6,reason:'no-verified-advantage',n:table[6]?.n||0,margin:0};
 return {cadence:selected.cadence,reason:'learned-positive-lower-bound',n:selected.n,
 margin:selected.lower};
}
function wag252Run(cap,family,seed,duration,variant,models,trained){
 if(variant!=='learned')return wag251Run(cap,family,seed,duration,variant,models);
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 let lastRepair=-100,repairs=0,missed=0,opportunities=0,regret=0;
 const cadenceCounts={3:0,6:0,12:0,24:0},receipts=[];
 while(x.t<duration){
  const selection=wag252Select(x,trained),cadence=selection.cadence;
  cadenceCounts[cadence]++;
  // Reuse the fixed-cadence action and resource safety gate, not a privileged oracle.
  const decision=wag251Choice(x,models,lastRepair,'fixed'+cadence);
  const action=decision.action;
  if(action!=='abstain'){lastRepair=x.t;repairs++;}
  if(WAG250_SAMPLE.includes(x.t%240)&&x.t+48<=duration){
    const viable=['prevent','rebuild'].filter(a=>wag246Eligible(x,a));
    const vals=Object.fromEntries(viable.map(a=>[a,wag250Evaluate(x,a).value]));
    const best=Math.max(0,...Object.values(vals)),chosen=action==='abstain'?0:(vals[action]??0);
    const loss=Math.max(0,best-chosen);regret+=loss;
    if(best>.00005){opportunities++;if(action==='abstain')missed++;}
    receipts.push({tick:x.t,cadence,action,reason:selection.reason,
      energy:x.s.energy,scar:1-x.s.ceiling,material:x.material,regret:loss,
      confidenceMargin:selection.margin,trainingN:selection.n});
  }
  step244(x,action);
 }
 const ledger=wag248Ledger(x);
 return {mode:variant,capacity:cap,scenario:family,seed,duration,
 meanIntegrity:x.s.area/duration,finalIntegrity:x.s.integrity,
 aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
 reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
 repairs,maintenance:x.choices,materialUsed:x.materialSpent,materialLeft:x.material,
 decisionsByInterval:cadenceCounts,missed,opportunities,regret,receipts,ledger,trace:x.s.trace};
}
function wag252Experiment(){
 const models=wag251Models(),trained=wag252Train(models),groups={},examples=[];
 for(const duration of [240,480])for(const cap of CAP234)
 for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])
 for(const seed of WAG252_TEST){
  const result={};
  for(const variant of ['learned','adaptive','fixed3','fixed6','fixed12','fixed24','wag250']){
   result[variant]=wag252Run(cap,family,seed,duration,variant,models,trained);
  }
  const group=FAMILIES_HOLD244.includes(family)?'withheld':'familiar',key=duration+':'+group;
  const z=groups[key]??={n:0,policies:{},nonInferiorVsWag250:0,nonInferiorVsFixed3:0};
  z.n++;
  if(result.learned.aliveTicks>=result.wag250.aliveTicks&&result.learned.reserveTicks>=result.wag250.reserveTicks)z.nonInferiorVsWag250++;
  if(result.learned.meanIntegrity>=result.fixed3.meanIntegrity)z.nonInferiorVsFixed3++;
  for(const [name,v]of Object.entries(result)){
   const s=z.policies[name]??={integrity:0,alive:0,reserve:0,repairs:0,regret:0,material:0};
   s.integrity+=v.meanIntegrity;s.alive+=v.aliveTicks;s.reserve+=v.reserveTicks;
   s.repairs+=v.maintenance.prevent+v.maintenance.rebuild;s.regret+=v.regret??0;
   s.material+=v.materialUsed??0;
  }
  if(duration===240&&cap===13&&seed===3801&&['scar','phaseflip'].includes(family))
   examples.push({family,cap,seed,receipts:result.learned.receipts,
     policies:Object.fromEntries(Object.entries(result).map(([name,v])=>[name,
       {integrity:v.meanIntegrity,alive:v.aliveTicks,reserve:v.reserveTicks,repairs:v.maintenance.prevent+v.maintenance.rebuild}]))});
 }
 for(const z of Object.values(groups))for(const p of Object.values(z.policies))
  for(const k of Object.keys(p))p[k]/=z.n;
 return {bound:'WAG-252',training:{snapshots:trained.snapshots,comparisons:trained.comparisons,
 fineCells:Object.keys(trained.fine).length,parentCells:Object.keys(trained.parent).length,
 seeds:trained.seeds},testSeeds:WAG252_TEST,groups,examples,
 caveat:'Synthetic simulation, policy learned from one engine; matched holdout required.'};
}
if(typeof module!=='undefined')module.exports={wag252Train,wag252Select,wag252Run,wag252Experiment};
