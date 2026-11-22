/* WAG-247 · opportunity persistence · deterministic synthetic model · .dlw
 Load after WAG-245 and WAG-246. The controller uses only its current observed state
 and a pre-trained persistence table, never future forcing at decision time. */
const WAG247_TRAIN=[2801,2802,2803,2804],WAG247_TEST=[2901,2902,2903,2904];
const WAG247_DELAYS=[0,3,9,18],WAG247_CHECKPOINTS=[36,72,120,156,204,228];
const WAG247_REPAIR=['prevent','rebuild'];
function wag247Raw(x,a,delay,horizon=48){
 const y=clone244(x),initial=y.t,end=Math.min(y.duration,initial+horizon);
 while(y.t<end){
  const action=y.t===initial+delay&&wag246Eligible(y,a)?a:'abstain';
  step244(y,action);
 }
 const n=end-initial;
 return {score:(y.s.area-x.s.area)/n+.25*y.s.reserve/n+.5*y.s.alive/n+.18*y.s.energy+.04*y.material,
  integral:(y.s.area-x.s.area)/n,alive:y.s.alive-x.s.alive,reserve:y.s.reserve-x.s.reserve,
  energy:y.s.energy,used:y.choices[a]||0};
}
function wag247Profile(x){
 const abstain=wag247Raw(x,'abstain',0),byAction={};
 for(const a of WAG247_REPAIR)byAction[a]=WAG247_DELAYS.map(delay=>{
  const r=wag247Raw(x,a,delay);
  return {delay,gain:r.score-abstain.score,used:r.used,integrity:r.integral,
    alive:r.alive,reserve:r.reserve,energy:r.energy};
 });
 const valid=Object.values(byAction).flat().filter(v=>v.used>0);
 const immediate=valid.filter(v=>v.delay===0).sort((a,b)=>b.gain-a.gain)[0];
 const best=valid.sort((a,b)=>b.gain-a.gain)[0];
 const lastPositive=valid.filter(v=>v.gain>.00005).reduce((m,v)=>Math.max(m,v.delay),-1);
 return {byAction,immediate,optimal:best,lastPositive,
  lostByWaiting:immediate?Math.max(0,immediate.gain-Math.max(...valid.filter(v=>v.delay>0).map(v=>v.gain),0)):0};
}
function wag247Key(x){return [CAP234.indexOf(x.cap),wag246Phase(x.t%240),wag246Resources(x.s.energy),bin244(x)].join(':')}
function wag247Train(){
 const source=train235(),cells={};let profiles=0;
 for(const cap of CAP234)for(const family of FAMILIES_TRAIN244)for(const seed of WAG247_TRAIN){
  const base=start244(cap,family,seed,480);base.modelTable=source.table;
  while(base.t<240){
   if(WAG247_CHECKPOINTS.includes(base.t))for(const en of [.24,.78]){
    const x=clone244(base);x.s.energy=en;
    const k=wag247Key(x),p=wag247Profile(x);
    const c=cells[k]??={n:0,immediate:0,delay3:0,delay9:0,delay18:0,miss:0,beneficial:0};
    c.n++;profiles++;if(p.immediate?.gain>.00005){c.beneficial++;c.immediate+=p.immediate.gain;
      if(p.lostByWaiting>.00005)c.miss++;}
    for(const delay of [3,9,18]){
     const z=Object.values(p.byAction).flat().filter(v=>v.delay===delay&&v.used);
     c['delay'+delay]+=z.length?Math.max(...z.map(v=>v.gain)):0;
    }
   }
   step244(base,'abstain');
  }
 }
 const table={};
 for(const [k,c] of Object.entries(cells)){
  // Important: statistical means are estimates, not safe action certificates.
  const now=c.immediate/c.n,delay3=c.delay3/c.n,delay9=c.delay9/c.n,delay18=c.delay18/c.n;
  table[k]={n:c.n,now,delay3,delay9,delay18,missRate:c.beneficial?c.miss/c.beneficial:0,
   decision:now>.00005&&(now>delay3+.00005||now>delay9+.0001)?'act':'observe'};
 }
 return {table,source:source.table,profiles,trainingSeeds:WAG247_TRAIN};
}
function wag247Decision(x,model,policy){
 if(policy==='wag246')return 'abstain'; // assigned separately by WAG-246 runner
 if(policy==='always')return wag247Eligible(x,'rebuild')?'rebuild':wag247Eligible(x,'prevent')?'prevent':'abstain';
 const record=model.table[wag247Key(x)];
 if(!record||record.decision!=='act')return 'abstain';
 // Rank both repair actions by observable eligibility and structural need.
 if(wag247Eligible(x,'rebuild')&&1-x.s.ceiling>.012)return 'rebuild';
 if(wag247Eligible(x,'prevent'))return 'prevent';
 return 'abstain';
}
function wag247Run(cap,family,seed,duration,policy,model,model246,ref244,ref245){
 if(policy==='wag246')return wag246Run(cap,family,seed,duration,'wag246',model246,ref244,ref245);
 if(policy==='wag245')return wag246Run(cap,family,seed,duration,'wag245',model246,ref244,ref245);
 if(policy==='wag244')return wag246Run(cap,family,seed,duration,'wag244',model246,ref244,ref245);
 const x=start244(cap,family,seed,duration);x.modelTable=model.source;
 let positive=0,missed=0,expired=0,opportunityLoss=0;
 const receipts=[];
 while(x.t<duration){
  const window=WAG247_CHECKPOINTS.includes(x.t%240),a=wag247Decision(x,model,policy);
  if(window&&x.t+48<=duration){
   // Evaluation only: counterfactuals are never fed to the live decision gate.
   const p=wag247Profile(x),benefit=p.immediate?.gain??0;
   if(benefit>.00005){positive++;if(a==='abstain'){missed++;opportunityLoss+=p.lostByWaiting;
     if(p.lastPositive<9)expired++;}}
   receipts.push({tick:x.t,action:a,immediate:benefit,latest:p.lastPositive,
     loss:p.lostByWaiting});
  }
  step244(x,a);
 }
 const pending=x.queue.filter(z=>z.due>=duration).reduce((s,z)=>s+z.amount,0);
 const energyError=Math.max(Math.abs(.2+x.energyIn-x.energyWithdrawn-x.cache),
 Math.abs(x.energyFlux-x.energyIn-x.energyWaste),
 Math.abs(x.energyWithdrawn-x.energyDelivered-x.transferLost-pending*.84));
 const materialError=Math.max(Math.abs(.2+x.materialIn-x.materialSpent-x.material),
 Math.abs(duration*.0009-x.materialIn-x.materialWaste));
 if(energyError>1e-8||materialError>1e-8)throw Error('WAG-247 ledger violation');
 return {mode:policy,capacity:cap,scenario:family,seed,duration,
 meanIntegrity:x.s.area/duration,finalIntegrity:x.s.integrity,
 aliveTicks:x.s.trace.filter(z=>z.energy>.08&&z.integrity>.15).length,
 reserveTicks:x.s.trace.filter(z=>z.energy>.25&&z.integrity>.30).length,
 maintenance:x.choices,positive,missed,expired,opportunityLoss,receipts,energyError,materialError,trace:x.s.trace};
}
function wag247Experiment(){
 const model=wag247Train(),model246=wag246Train(),ref244=train244(),ref245=train245();
 const summary={},examples=[];
 for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])for(const cap of CAP234)
 for(const seed of WAG247_TEST){
  const r={};for(const policy of ['wag247','wag246','wag245','wag244','always'])
   r[policy]=wag247Run(cap,family,seed,240,policy,model,model246,ref244,ref245);
  const group=FAMILIES_HOLD244.includes(family)?'withheld':'familiar';
  const z=summary[group]??={count:0,models:{},survivalNonInferior:0,repairNonInferior:0};
  z.count++;for(const [name,v] of Object.entries(r)){const a=z.models[name]??={integrity:0,alive:0,reserve:0,missed:0,repairs:0};
   a.integrity+=v.meanIntegrity;a.alive+=v.aliveTicks;a.reserve+=v.reserveTicks;
   a.missed+=v.missed||0;a.repairs+=(v.maintenance.prevent+v.maintenance.rebuild);}
  if(r.wag247.aliveTicks>=r.wag245.aliveTicks&&r.wag247.reserveTicks>=r.wag245.reserveTicks)z.survivalNonInferior++;
  if(family==='scar'&&r.wag247.meanIntegrity>=r.wag244.meanIntegrity)z.repairNonInferior++;
  if(family==='scar'&&cap===13&&seed===2901)examples.push({family,cap,seed,
   policies:Object.fromEntries(Object.entries(r).map(([name,v])=>[name,{
    integrity:v.meanIntegrity,alive:v.aliveTicks,reserve:v.reserveTicks,repairs:v.maintenance}]))});
 }
 for(const z of Object.values(summary))for(const v of Object.values(z.models))for(const k of Object.keys(v))v[k]/=z.count;
 return {bound:'WAG-247',training:{profiles:model.profiles,cells:Object.keys(model.table).length},
  testSeeds:WAG247_TEST,summary,examples,qualification:'Synthetic observed-state policy; counterfactuals used only in training and evaluation'};
}
if(typeof module!=='undefined')module.exports={wag247Train,wag247Run,wag247Experiment,wag247Profile};
