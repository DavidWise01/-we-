/* WAG-249 · calibrated selective repair · deterministic synthetic evidence · .dlw
 Load WAG-245 → WAG-246 → WAG-247 → WAG-248 → WAG-249.
 Training 3001-3006; calibration 3201-3204; test 3301-3304.
 Calibration labels are privileged OFFLINE only; controller receives frozen lookup. */
const WAG249_CAL=[3201,3202,3203,3204],WAG249_TEST=[3301,3302,3303,3304];
const WAG249_CLASSES=['opening','stable','closing'];
function wag249Bucket(conf){return Math.min(4,Math.max(0,Math.floor(conf*5)))}
function wag249Key(p){return p.state+':'+wag249Bucket(p.confidence)}
function wag249SampleCell(){return {n:0,correct:0,closingTrue:0,closingFalse:0,beneficial:0,missCost:0}}
function wag249Add(cell,p,truth){
 cell.n++;if(p.state===truth.label)cell.correct++;
 if(truth.label==='closing')cell.closingTrue++;
 if(p.state==='closing'&&truth.label!=='closing')cell.closingFalse++;
 if(truth.now>WAG248_BENEFIT){cell.beneficial++;cell.missCost+=truth.missed}
}
function wag249Calibrate(base){
 const groups={},all=wag249SampleCell(),reliability=[];
 for(const cap of CAP234)for(const family of FAMILIES_TRAIN244)for(const seed of WAG249_CAL){
  const x=start244(cap,family,seed,480);x.modelTable=base.source;
  while(x.t<240){
   if(WAG248_TIMES.includes(x.t)){
    const p=wag248Forecast(x,base),truth=wag248Label(x);
    if(p.coverage){const key=wag249Key(p),c=groups[key]??=wag249SampleCell();wag249Add(c,p,truth);wag249Add(all,p,truth);
      reliability.push({bucket:key,confidence:p.confidence,correct:p.state===truth.label?1:0})}
   }
   step244(x,'abstain');
  }
 }
 const rates={};for(const [key,c] of Object.entries(groups)){
  // Beta(2,2) shrinkage; nonempty sparse bins are rejected instead of overtrusted.
  const calibrated=(c.correct+2)/(c.n+4);
  const se=Math.sqrt(calibrated*(1-calibrated)/(c.n+5));
  rates[key]={...c,calibrated,lower:Math.max(0,calibrated-1.64*se),upper:Math.min(1,calibrated+1.64*se)};
 }
 const ece=reliability.length?reliability.reduce((s,q)=>s+Math.abs(q.confidence-rates[q.bucket].correct/rates[q.bucket].n),0)/reliability.length:null;
 return {rates,global:all,calSeeds:WAG249_CAL,samples:all.n,ece,
   minBin:8,calibration:'Beta(2,2) smoothed accuracy with normal lower uncertainty bound'};
}
function wag249Decision(x,p,cal,minimum=.60){
 if(!p.coverage)return {action:'abstain',reason:'no-model',lower:null};
 const cell=cal.rates[wag249Key(p)];
 if(!cell||cell.n<cal.minBin)return {action:'abstain',reason:'insufficient-calibration',lower:null};
 if(cell.lower<minimum)return {action:'abstain',reason:'uncertain',lower:cell.lower};
 if(p.expectedValue<=WAG248_BENEFIT)return {action:'abstain',reason:'low-value',lower:cell.lower};
 if(p.state==='opening')return {action:'abstain',reason:'opening',lower:cell.lower};
 if(p.state==='stable'&&p.expectedMissed<.0001)return {action:'abstain',reason:'persistent',lower:cell.lower};
 if(p.features.energy<.38)return {action:'abstain',reason:'reserve',lower:cell.lower};
 const action=wag246Eligible(x,'rebuild')&&p.features.scar>.012?'rebuild':
 wag246Eligible(x,'prevent')?'prevent':'abstain';
 return {action,reason:action==='abstain'?'ineligible':'calibrated',lower:cell.lower};
}
function wag249Run(cap,family,seed,duration,mode,base,cal,refs,minimum=.60){
 if(mode!=='wag249')return wag248Run(cap,family,seed,duration,mode,base,refs);
 const x=start244(cap,family,seed,duration);x.modelTable=base.source;
 let n=0,correct=0,covered=0,missed=0,positive=0,brier=0;
 const decisions=[],reliability={};
 while(x.t<duration){
  let a='abstain';
  if(WAG248_TIMES.includes(x.t%240)){
   const p=wag248Forecast(x,base),choice=wag249Decision(x,p,cal,minimum);
   a=choice.action;
   if(x.t+48<=duration){
    const y=wag248Label(x);n++;
    if(p.coverage){covered++;if(p.state===y.label)correct++;
      brier+=WAG249_CLASSES.reduce((s,k)=>s+(p.probabilities[k]-(k===y.label?1:0))**2,0)/3;
      const key=wag249Key(p),z=reliability[key]??={n:0,correct:0,nominal:0};
      z.n++;z.correct+=(p.state===y.label?1:0);z.nominal+=p.confidence;
    }
    if(y.now>WAG248_BENEFIT){positive++;if(a==='abstain')missed++;}
    decisions.push({tick:x.t,pred:p.state,nominal:p.confidence,lower:choice.lower,
       actual:y.label,action:a,reason:choice.reason,now:y.now,later:y.later});
   }
  }
  step244(x,a);
 }
 const ledger=wag248Ledger(x);
 const calibration=Object.values(reliability);
 const ece=covered?calibration.reduce((v,c)=>v+c.n/covered*Math.abs(c.correct/c.n-c.nominal/c.n),0):null;
 return {mode,capacity:cap,scenario:family,seed,duration,
   meanIntegrity:x.s.area/duration,finalIntegrity:x.s.integrity,finalEnergy:x.s.energy,
   aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
   reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
   maintenance:x.choices,n,covered,correct,accuracy:covered?correct/covered:null,
   brier:covered?brier/covered:null,ece,missed,positive,decisions,ledger,trace:x.s.trace};
}
function wag249Experiment(){
 const base=wag248Train(),cal=wag249Calibrate(base),
 refs={ref247:wag247Train(),ref246:wag246Train(),ref244:train244(),ref245:train245()};
 const summary={},examples=[];
 for(const cap of CAP234)for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])
 for(const seed of WAG249_TEST){
  const runs={};for(const name of ['wag249','wag248','wag247','wag246','wag245','wag244'])
    runs[name]=wag249Run(cap,family,seed,240,name,base,cal,refs);
  const key=FAMILIES_HOLD244.includes(family)?'withheld':'familiar',z=summary[key]??={
   cases:0,models:{},correct:0,covered:0,missed:0,positive:0,nonInferior:0,scarBetter:0};
  z.cases++;const r=runs.wag249;z.covered+=r.covered;z.correct+=r.correct;z.missed+=r.missed;z.positive+=r.positive;
  if(r.aliveTicks>=runs.wag245.aliveTicks&&r.reserveTicks>=runs.wag245.reserveTicks)z.nonInferior++;
  if(family==='scar'&&r.meanIntegrity>=runs.wag244.meanIntegrity)z.scarBetter++;
  for(const [k,v] of Object.entries(runs)){const s=z.models[k]??={integrity:0,alive:0,reserve:0,repairs:0};
    s.integrity+=v.meanIntegrity;s.alive+=v.aliveTicks;s.reserve+=v.reserveTicks;
    s.repairs+=v.maintenance.prevent+v.maintenance.rebuild;}
  if(cap===13&&seed===3301&&['scar','phaseflip'].includes(family))
   examples.push({family,cap,seed,decisions:r.decisions,comparison:Object.fromEntries(Object.entries(runs)
    .map(([k,v])=>[k,{integrity:v.meanIntegrity,alive:v.aliveTicks,reserve:v.reserveTicks,maintenance:v.maintenance}]))});
 }
 for(const s of Object.values(summary)){
  s.accuracy=s.covered?s.correct/s.covered:null;
  for(const v of Object.values(s.models))for(const k of Object.keys(v))v[k]/=s.cases;
 }
 return {bound:'WAG-249',calibration:{samples:cal.samples,bins:Object.keys(cal.rates).length,
   calibrationECE:cal.ece,calibrationSeeds:WAG249_CAL},
  testSeeds:WAG249_TEST,summary,examples,
  caveat:'Conservative selective policy, not guaranteed repair; simulation holdout only'};
}
if(typeof module!=='undefined')module.exports={wag249Calibrate,wag249Decision,wag249Run,wag249Experiment};
