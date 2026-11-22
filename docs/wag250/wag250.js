/* WAG-250 · regret-aware repair selection · deterministic synthetic lab · .dlw
 Loads WAG-245 through WAG-249. No future data in online policy.
 TRAIN [3401..3404], calibration inherited WAG-249 [3201..3204], TEST [3501..3504].
 Exploration is a deterministic conservative probe, never an oracle action.
 */
const WAG250_TRAIN=[3401,3402,3403,3404],WAG250_TEST=[3501,3502,3503,3504];
const WAG250_ACTIONS=['abstain','prevent','rebuild'];
const WAG250_SAMPLE=[36,48,60,72,84,96,108,120,132,144,156,168,180,192,204,216];
function wag250Key(x){
 const energy=x.s.energy,scar=1-x.s.ceiling,obs=x.f[x.t].observed;
 return [CAP234.indexOf(x.cap),energy<.35?'low':energy<.60?'mid':'high',
 scar<.005?'clear':scar<.04?'light':'heavy',obs<.48?'quiet':'pressured'].join(':');
}
function wag250Parent(x){
 const e=x.s.energy,scar=1-x.s.ceiling;
 return [CAP234.indexOf(x.cap),e<.35?'low':e<.60?'mid':'high',scar<.005?'clear':scar<.04?'light':'heavy'].join(':');
}
function wag250Cell(){return {n:0,mean:0,m2:0,positive:0,negative:0,energy:0,alive:0,reserve:0}}
function wag250Add(z,v){
 z.n++;const d=v.value-z.mean;z.mean+=d/z.n;z.m2+=d*(v.value-z.mean);
 if(v.value>0)z.positive++;else if(v.value<0)z.negative++;
 for(const k of ['energy','alive','reserve'])z[k]+=(v[k]-z[k])/z.n;
}
function wag250Evaluate(x,a,horizon=48){
 const b=branchMetrics245(x,'abstain',horizon),r=branchMetrics245(x,a,horizon);
 const n=Math.min(horizon,x.duration-x.t);
 return {value:r.meanIntegrity-b.meanIntegrity+
 .25*(r.integralReserve-b.integralReserve)/n+
 .5*(r.integralAlive-b.integralAlive)/n+
 .18*(r.finalEnergy-b.finalEnergy)+.04*(r.finalMaterial-b.finalMaterial),
 alive:(r.integralAlive-b.integralAlive)/n,
 reserve:(r.integralReserve-b.integralReserve)/n,energy:r.finalEnergy-b.finalEnergy};
}
function wag250Train(){
 const source=train235(),fine={},parent={};let samples=0;
 for(const cap of CAP234)for(const family of FAMILIES_TRAIN244)for(const seed of WAG250_TRAIN){
 const base=start244(cap,family,seed,480);base.modelTable=source.table;
 while(base.t<240){
  if(WAG250_SAMPLE.includes(base.t))for(const energy of [.24,.55,.78]){
   const x=clone244(base);x.s.energy=energy;
   const k=wag250Key(x),p=wag250Parent(x);
   for(const a of ['prevent','rebuild']){
    if(!wag246Eligible(x,a))continue;
    const v=wag250Evaluate(x,a);
    wag250Add((fine[k]??={})[a]??=wag250Cell(),v);
    wag250Add((parent[p]??={})[a]??=wag250Cell(),v);
    samples++;
   }
  }
  step244(base,'abstain');
 }
 }
 return {source:source.table,fine,parent,samples,seeds:WAG250_TRAIN,minimumFine:8,minimumParent:12};
}
function wag250Estimate(x,a,model){
 const fine=model.fine[wag250Key(x)]?.[a],parent=model.parent[wag250Parent(x)]?.[a];
 const z=fine?.n>=model.minimumFine?fine:parent?.n>=model.minimumParent?parent:null;
 if(!z)return null;
 const sd=z.n>1?Math.sqrt(z.m2/(z.n-1)):0,se=sd/Math.sqrt(z.n);
 return {n:z.n,mean:z.mean,lower:z.mean-1.64*se,upper:z.mean+1.64*se,
   energy:z.energy,alive:z.alive,reserve:z.reserve,winRate:z.positive/z.n};
}
function wag250Decision(x,model,forecast,cal,prior244,lastRepair=-100,variant='regret'){
 const energy=x.s.energy,scar=1-x.s.ceiling,p=x.f[x.t].observed;
 if(x.t-lastRepair<6)return {action:'abstain',reason:'cooldown'};
 if(energy<.37)return {action:'abstain',reason:'reserve-floor'};
 const options=['prevent','rebuild'].filter(a=>wag246Eligible(x,a));
 if(!options.length)return {action:'abstain',reason:'not-eligible'};
 const pred=wag248Forecast(x,forecast),c=cal.rates[wag249Key(pred)];
 const confidenceOK=pred.coverage&&c?.n>=8&&c.lower>=.50;
 const ranked=options.map(a=>({action:a,estimate:wag250Estimate(x,a,model)}));
 const safe=ranked.filter(z=>z.estimate&&z.estimate.energy>=-.045&&
 z.estimate.alive>=-.003&&z.estimate.reserve>=-.003);
 // Expected cost of a wrong repair (negative outcome) and the missed-value cost of abstention
 // are estimated from matched counterfactuals in training, never from live future.
 const best=safe.sort((a,b)=>b.estimate.mean-a.estimate.mean)[0];
 if(best&&best.estimate.lower>.000015&&energy>.43){
  return {action:best.action,reason:'regret-positive',mean:best.estimate.mean,
    lower:best.estimate.lower,confidenceOK};
 }
 // Supported probing is scarce and bounded: it requires a positive upper confidence
 // estimate, abundant energy, existing damage, and no imminent reserve constraint.
 if(variant==='regret'&&energy>.69&&scar>.018&&p<.73&&
    x.t%24===0&&best&&best.estimate.upper>.00008&&best.estimate.mean>-.00005)
  return {action:best.action,reason:'bounded-probe',mean:best.estimate.mean,
   lower:best.estimate.lower,confidenceOK};
 // WAG-244 reference only breaks ties when training coverage is absent,
 // and only with a more conservative resource gate than the reference.
 if(variant==='regret'&&!best&&confidenceOK&&scar>.025&&energy>.72&&x.t%24===0){
  const old=prior244.table244[CAP234.indexOf(x.cap)][bin244(x)].action;
  if(options.includes(old))return {action:old,reason:'reference-safe-fallback',confidenceOK};
 }
 return {action:'abstain',reason:best?'regret-not-positive':'insufficient-training',confidenceOK};
}
function wag250Run(cap,family,seed,duration,mode,model,refs,threshold=.000015){
 if(mode!=='wag250'&&mode!=='conservative')return wag249Run(cap,family,seed,duration,mode,refs.ref248,refs.cal249,refs, .60);
 const x=start244(cap,family,seed,duration);x.modelTable=model.source;
 let lastRepair=-100,applied=0,probes=0,missed=0,wrong=0,opportunities=0,regret=0;
 const receipts=[];
 while(x.t<duration){
  let a='abstain',choice={reason:'outside-checkpoint'};
  if(x.t%6===0){
   choice=wag250Decision(x,model,refs.ref248,refs.cal249,refs.ref244,lastRepair,mode==='wag250'?'regret':'conservative');
   a=choice.action;
   if(a!=='abstain'){lastRepair=x.t;applied++;if(choice.reason==='bounded-probe')probes++;}
   // Ground truth is evaluated only at sparse held-out checkpoints, not used by the action.
   if(WAG250_SAMPLE.includes(x.t%240)&&x.t+48<=duration){
    const values=Object.fromEntries(['prevent','rebuild'].map(k=>[k,wag246Eligible(x,k)?wag250Evaluate(x,k).value:null]));
    const available=Object.entries(values).filter(([k,v])=>v!==null);
    const best=available.length?Math.max(0,...available.map(([k,v])=>v)):0;
    const chosen=a==='abstain'?0:(values[a]??0);
    if(best>.00005){opportunities++;if(a==='abstain')missed++;}
    if(chosen<-.00005)wrong++;
    regret+=Math.max(0,best-chosen);
    receipts.push({tick:x.t,action:a,reason:choice.reason,
      bestValue:best,chosenValue:chosen,regret:Math.max(0,best-chosen)});
   }
  }
  step244(x,a);
 }
 const ledger=wag248Ledger(x);
 return {mode,capacity:cap,scenario:family,seed,duration,meanIntegrity:x.s.area/duration,
  finalIntegrity:x.s.integrity,finalEnergy:x.s.energy,
  aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
  reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  maintenance:x.choices,applied,probes,missed,wrong,opportunities,regret,receipts,ledger,trace:x.s.trace};
}
function wag250Experiment(){
 const model=wag250Train(),refs={ref248:wag248Train(),cal249:null,ref247:wag247Train(),
 ref246:wag246Train(),ref244:train244(),ref245:train245()};
 refs.cal249=wag249Calibrate(refs.ref248);
 const aggregate={},examples=[];
 for(const duration of [240,480])for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])
 for(const cap of CAP234)for(const seed of WAG250_TEST){
  const r={};for(const mode of ['wag250','conservative','wag249','wag248','wag244','wag245'])
   r[mode]=wag250Run(cap,family,seed,duration,mode,model,refs);
  const g=FAMILIES_HOLD244.includes(family)?'withheld':'familiar',key=duration+':'+g;
  const z=aggregate[key]??={n:0,policies:{},survivalNonInferior:0,scarNonInferior:0,regret:0,missed:0,probes:0};
  z.n++;z.regret+=r.wag250.regret;z.missed+=r.wag250.missed;z.probes+=r.wag250.probes;
  if(r.wag250.aliveTicks>=r.wag245.aliveTicks&&r.wag250.reserveTicks>=r.wag245.reserveTicks)z.survivalNonInferior++;
  if(family==='scar'&&r.wag250.meanIntegrity>=r.wag244.meanIntegrity)z.scarNonInferior++;
  for(const [m,v] of Object.entries(r)){const s=z.policies[m]??={integrity:0,alive:0,reserve:0,repairs:0};
   s.integrity+=v.meanIntegrity;s.alive+=v.aliveTicks;s.reserve+=v.reserveTicks;
   s.repairs+=v.maintenance.prevent+v.maintenance.rebuild;}
  if(duration===240&&cap===13&&seed===3501&&['scar','phaseflip'].includes(family))
   examples.push({family,cap,seed,receipts:r.wag250.receipts,policies:Object.fromEntries(Object.entries(r)
   .map(([m,v])=>[m,{integrity:v.meanIntegrity,alive:v.aliveTicks,reserve:v.reserveTicks,
   repairs:v.maintenance.prevent+v.maintenance.rebuild}]))});
 }
 for(const z of Object.values(aggregate))for(const s of Object.values(z.policies))
 for(const k of Object.keys(s))s[k]/=z.n;
 return {bound:'WAG-250',training:{samples:model.samples,fineCells:Object.keys(model.fine).length,
 parentCells:Object.keys(model.parent).length,seedSet:model.seeds},
 testSeeds:WAG250_TEST,aggregate,examples,
 caveat:'Simulator-only; regret labels use privileged paired counterfactuals offline.'};
}
if(typeof module!=='undefined')module.exports={wag250Train,wag250Run,wag250Experiment,wag250Decision};
