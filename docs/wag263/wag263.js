/* WAG-263 · observed drift-aware downgrade and recovery · Phase II 7/12 · .dlw
 Read only current/past state. A deterministic external stress schedule is visible
 ONLY to the simulator; controller sees consequences after prior ticks.
 The inherited energy cache ledger remains distinct from operational energy.
 All external energy injections/withdrawals are appended and persist.
*/
const WAG263_TEST=[5201,5202,5203,5204];
const WAG263_DRIFTS=['none','drain','pulse','recovery'];
function wag263External(t,kind){
 if(kind==='none')return 0;
 if(kind==='drain')return (t>=70&&t<145)?-.0032:0;
 if(kind==='pulse')return [76,105,134,163].includes(t)?-.12:0;
 if(kind==='recovery')return (t>=68&&t<126)?-.0035:(t>=150&&t<206?.0032:0);
 throw Error('unknown drift');
}
function wag263Trend(x){
 const h=x.s.trace.slice(-12);
 const vals=h.map(z=>z.energy),short=vals.slice(-4),older=vals.slice(-12,-8);
 const mean=a=>a.length?a.reduce((v,z)=>v+z,0)/a.length:0;
 return {energy:x.s.energy,material:x.material,integrity:x.s.integrity,
  recentSlope:vals.length>=8?(mean(short)-mean(older))/8:0,
  scar:1-x.s.ceiling,observed:x.f[x.t]?.observed??0};
}
function wag263Gate(x,st){
 const z=wag263Trend(x);
 const alarm=z.energy<.37||z.material<.018||(z.energy<.48&&z.recentSlope<-.006);
 const warning=z.energy<.48||z.material<.035||(z.energy<.59&&z.recentSlope<-.004);
 const stable=z.energy>.59&&z.material>.052&&z.recentSlope>-.003;
 if(alarm){st.alarmStreak++;st.clearStreak=0;}
 else if(warning){st.alarmStreak=Math.max(st.alarmStreak,1);st.clearStreak=0;}
 else if(stable){st.clearStreak++;st.alarmStreak=0;}
 else {st.clearStreak=0;st.alarmStreak=0;}
 const before=st.level;
 if(alarm&&st.alarmStreak>=2)st.level='emergency';
 else if(warning&&st.level==='normal')st.level='caution';
 else if(st.level==='emergency'&&!alarm&&st.clearStreak>=8)st.level='caution';
 else if(st.level==='caution'&&st.clearStreak>=14)st.level='normal';
 if(before!==st.level)st.changes.push({tick:x.t,from:before,to:st.level,energy:z.energy,slope:z.recentSlope});
 return {level:st.level,signals:z,alarm,warning};
}
function wag263Select(x,models,horizon,lastRepair,gate,variant){
 const normal=wag261Select(x,models,horizon,lastRepair);
 if(variant==='baseline'||gate.level==='normal')return {...normal,level:gate.level};
 if(normal.action==='abstain')return {...normal,level:gate.level};
 if(gate.level==='emergency')return {action:'abstain',reason:'drift-emergency',level:gate.level,
  suppressed:normal.action};
 if(x.t-lastRepair<12||gate.signals.energy<.49||gate.signals.material<.032)
  return {action:'abstain',reason:'drift-caution',level:gate.level,suppressed:normal.action};
 return {...normal,level:gate.level};
}
function wag263Run(cap,family,seed,duration,drift,variant,models,horizon){
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const state={level:'normal',alarmStreak:0,clearStreak:0,changes:[]},receipts=[],trace=[];
 const resources={externalWithdrawn:0,externalInjected:0,externalUnserved:0,
  continuityMax:0,last:x.s.energy,transactions:[]};
 let lastRepair=-100,suppressed=0,repairs=0,regret=0,missed=0,opportunities=0;
 const counts={normal:0,caution:0,emergency:0};
 for(let tick=0;tick<duration;tick++){
  resources.continuityMax=Math.max(resources.continuityMax,Math.abs(x.s.energy-resources.last));
  const gate=wag263Gate(x,state);counts[gate.level]++;
  const choose=wag263Select(x,models,horizon,lastRepair,gate,variant);
  const action=choose.action;
  if(choose.suppressed)suppressed++;
  if(action!=='abstain'){lastRepair=tick;repairs++}
  if(WAG250_SAMPLE.includes(tick%240)&&tick+48<=duration){
   const opts=['prevent','rebuild'].filter(a=>wag246Eligible(x,a));
   const vals=Object.fromEntries(opts.map(a=>[a,wag250Evaluate(x,a).value]));
   const best=Math.max(0,...Object.values(vals)),used=action==='abstain'?0:vals[action]??0;
   regret+=Math.max(0,best-used);
   if(best>.00005){opportunities++;if(action==='abstain')missed++}
   receipts.push({tick,action,level:gate.level,reason:choose.reason,
    energy:x.s.energy,slope:gate.signals.recentSlope,regret:Math.max(0,best-used)});
  }
  step244(x,action);
  const delta=wag263External(tick,drift);
  const pre=x.s.energy,post=Math.max(0,Math.min(1,pre+delta));
  const actual=post-pre;
  if(actual<0)resources.externalWithdrawn-=actual;
  else resources.externalInjected+=actual;
  if(delta<0&&actual>delta)resources.externalUnserved+=actual-delta;
  if(delta!==0){
   resources.transactions.push({tick,requested:delta,actual,pre,post});
   x.s.energy=post;
   const z=x.s.trace.at(-1);z.energy=post;z.externalDrift=actual;
  }
  resources.last=x.s.energy;
  const z=x.s.trace.at(-1);
  trace.push({tick,energy:x.s.energy,integrity:z.integrity,material:x.material,
   level:gate.level,action,drift:actual});
 }
 return {mode:variant,capacity:cap,scenario:family,seed,duration,drift,
  meanIntegrity:x.s.area/duration,finalEnergy:x.s.energy,finalMaterial:x.material,
  aliveTicks:trace.filter(v=>v.energy>.08&&v.integrity>.15).length,
  reserveTicks:trace.filter(v=>v.energy>.25&&v.integrity>.30).length,
  repairs,suppressed,levels:counts,changes:state.changes,
  regret,missed,opportunities,resources,ledger:wag248Ledger(x),trace,receipts,
  interpretation:'External environmental energy shocks are explicitly separate from cache-transfer conservation'};
}
function wag263Experiment(){
 const models=wag251Models(),horizon=wag261Train(models),groups={},examples=[];
 for(const drift of WAG263_DRIFTS)for(const family of ['scar','combined','phaseflip','famine'])
 for(const cap of CAP234)for(const seed of WAG263_TEST){
  const a=wag263Run(cap,family,seed,240,drift,'adaptive',models,horizon);
  const b=wag263Run(cap,family,seed,240,drift,'baseline',models,horizon);
  const key=drift+':'+family,g=groups[key]??={n:0,integrityDelta:0,aliveDelta:0,reserveDelta:0,
   suppression:0,modeChanges:0,resourceViolations:0};
  g.n++;g.integrityDelta+=a.meanIntegrity-b.meanIntegrity;
  g.aliveDelta+=a.aliveTicks-b.aliveTicks;g.reserveDelta+=a.reserveTicks-b.reserveTicks;
  g.suppression+=a.suppressed;g.modeChanges+=a.changes.length;
  g.resourceViolations+=a.resources.continuityMax>1e-9?1:0;
  if(cap===13&&seed===5201)examples.push({drift,family,
   adaptive:{integrity:a.meanIntegrity,alive:a.aliveTicks,reserve:a.reserveTicks,
   suppressed:a.suppressed,changes:a.changes},baseline:{integrity:b.meanIntegrity,
   alive:b.aliveTicks,reserve:b.reserveTicks}});
 }
 for(const g of Object.values(groups))for(const k of ['integrityDelta','aliveDelta','reserveDelta'])g[k]/=g.n;
 return {bound:'WAG-263',phase:'II',turn:7,groups,examples,testSeeds:WAG263_TEST,
  caveat:'Drift schedules deterministic and known to simulator but hidden from controller. No guarantee that abstention improves recovery.'};
}
if(typeof module!=='undefined')module.exports={wag263External,wag263Trend,wag263Gate,wag263Select,wag263Run,wag263Experiment};
