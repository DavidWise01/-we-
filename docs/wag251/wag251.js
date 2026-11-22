/* WAG-251 · adaptive repair frequency and resource economics · .dlw
 Synthetic, deterministic, no future labels enter the online controller.
 The WAG-250 reference is run unchanged on matched forcing and seeds.
 */
const WAG251_TEST=[3601,3602,3603,3604];
const WAG251_CADENCES=[3,6,12,24];
const WAG251_MODES=['adaptive','fixed3','fixed6','fixed12','fixed24'];
function wag251Signals(x){
 const trace=x.s.trace.slice(-12);
 const energyTrend=trace.length>5?(trace.slice(-4).reduce((a,z)=>a+z.energy,0)/4-
 trace.slice(0,4).reduce((a,z)=>a+z.energy,0)/4):0;
 const scar=Math.max(0,1-x.s.ceiling),material=x.material,energy=x.s.energy;
 const obs=x.f[x.t].observed;
 const materialRich=material>.08,energyRich=energy>.68;
 const pressureHigh=obs>.65;
 return {energy,energyTrend,scar,material,obs,materialRich,energyRich,pressureHigh,
  scarcity:energy<.46||material<.025||energyTrend<-.12,
  severity:scar>.075?'severe':scar>.018?'moderate':'low'};
}
function wag251Cadence(x,variant='adaptive'){
 if(variant.startsWith('fixed'))return Number(variant.slice(5));
 const s=wag251Signals(x);
 if(s.energy<.38||s.material<.012)return 24;
 if(s.energy<.52||s.material<.035||s.energyTrend<-.085)return 12;
 if(s.scar>.075&&s.energy>.68&&s.material>.055)return 3;
 if(s.scar>.028&&s.energy>.58&&s.material>.04)return 6;
 if(s.pressureHigh&&s.energy>.58&&s.material>.045)return 6;
 return 12;
}
function wag251Choice(x,models,lastRepair,variant){
 const signal=wag251Signals(x),cadence=wag251Cadence(x,variant);
 if(x.t-lastRepair<cadence)return {action:'abstain',reason:'cadence',cadence,signal};
 if(signal.energy<.38||signal.material<.012)return {action:'abstain',reason:'resource-floor',cadence,signal};
 // WAG-250 decision retains its own conservative value, reserve, and eligibility gates.
 // Passing a synthetic old timestamp permits shorter WAG-251 intervals without mutating WAG-250.
 const d=wag250Decision(x,models.train250,models.ref248,models.cal249,models.ref244,
  cadence>=6?lastRepair:-100,'regret');
 let action=d.action;
 if(action!=='abstain'){
  // Cost of action: material/energy budget in the WAG-244 transition.
  const cost=action==='rebuild'?{material:.0035,energy:.004}:{material:.0015,energy:.0012};
  const minEnergy=signal.energy-cost.energy-.010*Math.max(1,cadence/6);
  if(signal.material<cost.material+.012||minEnergy<.37){
   return {action:'abstain',reason:'projected-resource-floor',cadence,signal};
  }
 }
 return {...d,action,cadence,signal};
}
function wag251Run(cap,family,seed,duration,variant,models){
 if(variant==='wag250')return wag250Run(cap,family,seed,duration,'wag250',models.train250,models);
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 let lastRepair=-100,repairs=0,missed=0,opportunities=0,wrong=0,regret=0;
 const choices={3:0,6:0,12:0,24:0},receipts=[];
 while(x.t<duration){
  const d=wag251Choice(x,models,lastRepair,variant);
  const action=d.action,interval=d.cadence;choices[interval]++;
  if(action!=='abstain'){lastRepair=x.t;repairs++;}
  // Paired future branches are evaluation only; held apart from wag251Choice.
  if(WAG250_SAMPLE.includes(x.t%240)&&x.t+48<=duration){
   const valid=['prevent','rebuild'].filter(a=>wag246Eligible(x,a));
   const v=Object.fromEntries(valid.map(a=>[a,wag250Evaluate(x,a).value]));
   const best=Math.max(0,...Object.values(v));
   const chosen=action==='abstain'?0:(v[action]??0);
   const loss=Math.max(0,best-chosen);regret+=loss;
   if(best>.00005){opportunities++;if(action==='abstain')missed++;}
   if(chosen<-.00005)wrong++;
   receipts.push({tick:x.t,action,interval,reason:d.reason,
     energy:d.signal.energy,scar:d.signal.scar,material:d.signal.material,
     regret:loss,best,chosen});
  }
  step244(x,action);
 }
 const ledger=wag248Ledger(x);
 return {mode:variant,capacity:cap,scenario:family,seed,duration,meanIntegrity:x.s.area/duration,
  finalIntegrity:x.s.integrity,finalEnergy:x.s.energy,
  aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
  reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  repairs,maintenance:x.choices,materialUsed:x.materialSpent,materialLeft:x.material,
  decisionsByInterval:choices,missed,opportunities,wrong,regret,receipts,ledger,trace:x.s.trace};
}
function wag251Models(){
 const ref248=wag248Train();
 return {train250:wag250Train(),ref248,cal249:wag249Calibrate(ref248),
  ref247:wag247Train(),ref246:wag246Train(),ref244:train244(),ref245:train245()};
}
function wag251Experiment(){
 const models=wag251Models(),groups={},examples=[];
 for(const duration of [240,480])for(const cap of CAP234)
 for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])for(const seed of WAG251_TEST){
  const r={};
  for(const variant of ['adaptive','fixed3','fixed6','fixed12','fixed24','wag250','wag244','wag245']){
   r[variant]=variant==='wag244'||variant==='wag245'?
      wag250Run(cap,family,seed,duration,variant,models.train250,models):
      wag251Run(cap,family,seed,duration,variant,models);
  }
  const group=FAMILIES_HOLD244.includes(family)?'withheld':'familiar',key=duration+':'+group;
  const z=groups[key]??={n:0,policy:{},survivalNonInferior:0,scarRecoveryNonInferior:0};
  z.n++;
  if(r.adaptive.aliveTicks>=r.wag245.aliveTicks&&r.adaptive.reserveTicks>=r.wag245.reserveTicks)z.survivalNonInferior++;
  if(family==='scar'&&r.adaptive.meanIntegrity>=r.wag244.meanIntegrity)z.scarRecoveryNonInferior++;
  for(const [name,v]of Object.entries(r)){
   const s=z.policy[name]??={integrity:0,alive:0,reserve:0,repairs:0,material:0,regret:0};
   s.integrity+=v.meanIntegrity;s.alive+=v.aliveTicks;s.reserve+=v.reserveTicks;
   s.repairs+=v.maintenance.prevent+v.maintenance.rebuild;
   s.material+=v.materialUsed??0;s.regret+=v.regret??0;
  }
  if(duration===240&&cap===13&&seed===3601&&['scar','phaseflip'].includes(family)){
   examples.push({family,cap,seed,receipts:r.adaptive.receipts,
     policies:Object.fromEntries(Object.entries(r).map(([name,v])=>[name,{
       integrity:v.meanIntegrity,alive:v.aliveTicks,reserve:v.reserveTicks,
       repairs:v.maintenance.prevent+v.maintenance.rebuild}]))});
  }
 }
 for(const z of Object.values(groups))for(const v of Object.values(z.policy))
  for(const k of Object.keys(v))v[k]/=z.n;
 return {bound:'WAG-251',trainSeeds:WAG250_TRAIN,holdoutSeeds:WAG251_TEST,groups,examples,
  invariants:{conservationTolerance:1e-8,temporal:'no future forcing in decision'},
  caution:'Synthetic paired comparisons; unequal decision frequencies are part of the policy under test'};
}
if(typeof module!=='undefined')module.exports={wag251Signals,wag251Cadence,wag251Run,wag251Models,wag251Experiment};
