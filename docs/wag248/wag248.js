/* WAG-248 · observed-trend recovery-window prediction · synthetic only · .dlw
 Loads WAG-245 → WAG-246 → WAG-247 → WAG-248.
 Temporal discipline: no forcing beyond current tick enters online prediction.
 Later counterfactuals are privileged labels used only during training/evaluation. */
const WAG248_TRAIN=[3001,3002,3003,3004,3005,3006],WAG248_TEST=[3101,3102,3103,3104];
const WAG248_TIMES=[36,48,72,84,108,120,132,156,168,192,204,216];
const WAG248_HORIZON=9, WAG248_BENEFIT=.00005;
function wag248Features(x){
 const h=x.s.trace,last=h.slice(-12);
 const slope=(k)=>last.length<6?0:(last.slice(-4).reduce((a,b)=>a+b[k],0)/4-
 last.slice(0,4).reduce((a,b)=>a+b[k],0)/4);
 const energySlope=slope('energy'),pressureSlope=slope('pressure'),ceilingSlope=slope('ceiling');
 const scar=1-x.s.ceiling, energy=x.s.energy, pressure=x.f[x.t].observed;
 return {energy,scar,pressure,energySlope,pressureSlope,ceilingSlope,
  energyTrend:energySlope<-.025?'fall':energySlope>.025?'rise':'steady',
  pressureTrend:pressureSlope<-.09?'fall':pressureSlope>.09?'rise':'steady',
  fragility:scar>.04?'scarred':'intact',resources:energy>.43?'rich':'poor'};
}
function wag248Key(x,f){return [CAP234.indexOf(x.cap),f.resources,f.fragility,f.energyTrend,f.pressureTrend].join(':')}
function wag248Group(x,f){return [CAP234.indexOf(x.cap),f.resources,f.fragility,f.energyTrend].join(':')}
function wag248ScoreAt(x,delay){
 const baseline=wag247Raw(x,'abstain',0,48),options=WAG247_REPAIR.map(a=>{
 const r=wag247Raw(x,a,delay,48);return {action:a,gain:r.score-baseline.score,used:r.used};});
 const valid=options.filter(v=>v.used).sort((a,b)=>b.gain-a.gain);
 return valid[0]||{action:'abstain',gain:0,used:0};
}
function wag248Label(x){
 const now=wag248ScoreAt(x,0),later=wag248ScoreAt(x,WAG248_HORIZON);
 const delta=later.gain-now.gain;let label='stable';
 if(now.gain<=WAG248_BENEFIT&&later.gain>WAG248_BENEFIT)label='opening';
 else if(now.gain>WAG248_BENEFIT&&
  (later.gain<=WAG248_BENEFIT||delta<-.0001))label='closing';
 else if(delta>.0001)label='opening';
 return {label,now:now.gain,later:later.gain,preferred:now.action,
  missed:Math.max(0,now.gain-later.gain)};
}
function wag248Cell(){return {n:0,counts:{opening:0,stable:0,closing:0},value:0,missed:0}}
function wag248Acc(m,k,y){const z=m[k]??=wag248Cell();z.n++;z.counts[y.label]++;z.value+=(y.now-z.value)/z.n;z.missed+=(y.missed-z.missed)/z.n;}
function wag248Train(){
 const source=train235(),fine={},coarse={},examples=[];
 for(const cap of CAP234)for(const family of FAMILIES_TRAIN244)for(const seed of WAG248_TRAIN){
  const x=start244(cap,family,seed,480);x.modelTable=source.table;
  while(x.t<240){
   if(WAG248_TIMES.includes(x.t)){
    const f=wag248Features(x),y=wag248Label(x);
    wag248Acc(fine,wag248Key(x,f),y);wag248Acc(coarse,wag248Group(x,f),y);
    examples.push({family,cap,seed,t:x.t,features:f,label:y.label,now:y.now,later:y.later});
   }
   step244(x,'abstain');
  }
 }
 return {source:source.table,fine,coarse,examples:examples.length,
  seeds:WAG248_TRAIN,minimumCellN:8,
  labelDefinition:'opening / stable / closing classified by 9-tick delayed counterfactual'};
}
function wag248Forecast(x,model){
 const f=wag248Features(x);
 const fine=model.fine[wag248Key(x,f)],coarse=model.coarse[wag248Group(x,f)];
 const cell=fine?.n>=8?fine:coarse?.n>=8?coarse:null;
 if(!cell)return {state:'unknown',confidence:0,probabilities:{opening:0,stable:0,closing:0},
    coverage:false,features:f,n:0};
 const probabilities=Object.fromEntries(Object.entries(cell.counts).map(([k,v])=>[k,(v+1)/(cell.n+3)]));
 const state=Object.keys(probabilities).sort((a,b)=>probabilities[b]-probabilities[a])[0];
 const confidence=probabilities[state];
 return {state,confidence,probabilities,coverage:true,features:f,n:cell.n,
   expectedValue:cell.value,expectedMissed:cell.missed};
}
function wag248Action(x,pred){
 if(pred.state==='unknown'||pred.confidence<.48)return 'abstain';
 if(pred.expectedValue<=WAG248_BENEFIT)return 'abstain';
 if(pred.state==='opening'&&pred.confidence>.57)return 'abstain'; // waiting is preferable if window opens
 if(pred.state!=='closing'&&pred.expectedMissed<.0001)return 'abstain';
 if(wag247Eligible(x,'rebuild')&&pred.features.scar>.012)return 'rebuild';
 if(wag247Eligible(x,'prevent'))return 'prevent';
 return 'abstain';
}
function wag248Ledger(x){
 const pending=x.queue.filter(z=>z.due>=x.duration).reduce((s,z)=>s+z.amount,0);
 const energy=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
  Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
  Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const material=Math.max(Math.abs(.2+x.materialIn-x.materialSpent-x.material),
  Math.abs(x.duration*.0009-x.materialIn-x.materialWaste));
 if(energy>1e-8||material>1e-8)throw Error('WAG-248 conservation invariant failed');
 return {energy,material};
}
function wag248Run(cap,family,seed,duration,mode,model,refs={}){
 if(mode==='wag247')return wag247Run(cap,family,seed,duration,'wag247',refs.ref247,refs.ref246,refs.ref244,refs.ref245);
 if(mode==='wag246')return wag246Run(cap,family,seed,duration,'wag246',refs.ref246,refs.ref244,refs.ref245);
 if(mode==='wag245')return wag246Run(cap,family,seed,duration,'wag245',refs.ref246,refs.ref244,refs.ref245);
 if(mode==='wag244')return wag246Run(cap,family,seed,duration,'wag244',refs.ref246,refs.ref244,refs.ref245);
 const x=start244(cap,family,seed,duration);x.modelTable=model.source;
 let nPred=0,correct=0,covered=0,unknown=0,missed=0,positive=0;
 let brier=0;const predictions=[];
 while(x.t<duration){
  let action='abstain';
  if(WAG248_TIMES.includes(x.t%240)){
   const pred=wag248Forecast(x,model);
   action=wag248Action(x,pred);
   if(x.t+48<=duration){
    // Evaluation-only future label; never used by wag248Action.
    const truth=wag248Label(x);nPred++;if(pred.coverage){covered++;if(pred.state===truth.label)correct++;
      brier+=Object.keys(pred.probabilities).reduce((s,k)=>s+Math.pow(pred.probabilities[k]-(k===truth.label?1:0),2),0)/3;
    }else unknown++;
    if(truth.now>WAG248_BENEFIT){positive++;if(action==='abstain')missed++;}
    predictions.push({tick:x.t,pred:pred.state,confidence:pred.confidence,
     actual:truth.label,now:truth.now,later:truth.later,action,covered:pred.coverage});
   }
  }
  step244(x,action);
 }
 const ledger=wag248Ledger(x);
 return {mode,capacity:cap,scenario:family,seed,duration,meanIntegrity:x.s.area/duration,
  finalIntegrity:x.s.integrity,finalEnergy:x.s.energy,
  aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
  reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
  maintenance:x.choices,nPred,correct,covered,unknown,accuracy:covered?correct/covered:null,
  brier:covered?brier/covered:null,missed,positive,predictions,ledger,trace:x.s.trace};
}
function wag248Experiment(){
 const model=wag248Train(),refs={ref247:wag247Train(),ref246:wag246Train(),ref244:train244(),ref245:train245()},
  summary={},examples=[];
 for(const duration of [240,480])for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])
 for(const cap of CAP234)for(const seed of WAG248_TEST){
  const runs={};for(const mode of ['wag248','wag247','wag246','wag245','wag244'])
   runs[mode]=wag248Run(cap,family,seed,duration,mode,model,refs);
  const group=FAMILIES_HOLD244.includes(family)?'withheld':'familiar',key=duration+':'+group;
  const z=summary[key]??={n:0,values:{},correct:0,covered:0,unknown:0,brierSum:0,scarWins:0,survivalNonInferior:0};
  z.n++;const p=runs.wag248;
  z.correct+=p.correct;z.covered+=p.covered;z.unknown+=p.unknown;z.brierSum+=(p.brier||0)*p.covered;
  for(const [m,v] of Object.entries(runs)){const w=z.values[m]??={integrity:0,alive:0,reserve:0,repairs:0};
   w.integrity+=v.meanIntegrity;w.alive+=v.aliveTicks;w.reserve+=v.reserveTicks;
   w.repairs+=v.maintenance.prevent+v.maintenance.rebuild;}
  if(family==='scar'&&p.meanIntegrity>=runs.wag244.meanIntegrity)z.scarWins++;
  if(p.aliveTicks>=runs.wag245.aliveTicks&&p.reserveTicks>=runs.wag245.reserveTicks)z.survivalNonInferior++;
  if(seed===3101&&cap===13&&family==='scar'&&duration===240)examples.push({
   family,cap,seed,forecasts:p.predictions,
   policies:Object.fromEntries(Object.entries(runs).map(([k,v])=>[k,{integrity:v.meanIntegrity,alive:v.aliveTicks,reserve:v.reserveTicks}]))});
 }
 for(const z of Object.values(summary)){
  z.accuracy=z.covered?z.correct/z.covered:null;z.brier=z.covered?z.brierSum/z.covered:null;
  for(const v of Object.values(z.values))for(const k of Object.keys(v))v[k]/=z.n;
 }
 return {bound:'WAG-248',training:{examples:model.examples,fineCells:Object.keys(model.fine).length,
  coarseCells:Object.keys(model.coarse).length},testSeeds:WAG248_TEST,summary,examples,
  caveat:'Synthetic simulator; classification and policy improvements require holdout tests'};
}
if(typeof module!=='undefined')module.exports={wag248Train,wag248Forecast,wag248Run,wag248Experiment};
