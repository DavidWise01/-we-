/* WAG-256 · bounded information-seeking about hidden switching costs · .dlw
   Synthetic laboratory. Cost regime and future truth hidden from online policy.
   A probe changes the operating cadence: it is NOT a free measurement.
   Every observation requires a paid transition; all receipts are append-only.
*/
const WAG256_TEST=[4301,4302,4303,4304];
const WAG256_VARIANTS=['valueProbe','periodicProbe','noProbe','frozen'];
const WAG256_PROBE_TICKS=[90,138,186,234,282,330,378,426];
const WAG256_PROBE_BUDGET=.006, WAG256_PROBE_GAP=42;
function wag256Control(){return {cadence:6,candidate:null,streak:0,lastChange:-100,
 switches:0,fees:0,blocked:0,charges:0,observed:[],probes:0,
 probeDebits:0,probeBudget:WAG256_PROBE_BUDGET,probeTarget:null,
 returnAt:-1,lastProbe:-100,probeStage:'idle',detectedTick:null,
 overrun:0,feeErrors:[],opportunityLoss:0};}
function wag256Risk(st){
 const receipts=st.observed.slice(-4);
 const ratios=receipts.map(r=>r.ratio);
 const upper=ratios.length?Math.max(1,...ratios):1;
 const mismatch=ratios.some(r=>r>1.55);
 const stale=st.observed.length?Math.max(0,st.currentTick-st.observed.at(-1).tick):Infinity;
 return {mismatch,upper,stale,n:receipts.length,
   status:mismatch?'mismatch':!receipts.length?'unobserved':stale>48?'stale':'recent'};
}
function wag256ProbeDecision(x,st,trainedCost,variant){
 const risk=wag256Risk(st),current=st.cadence,target=current===3?6:3;
 const features=wag254Signals(x,x.t-st.lastChange,current,target);
 const estimate=wag254Estimate(x,x.t-st.lastChange,current,target,trainedCost);
 const surcharge=risk.mismatch?Math.max(2,risk.upper):1.8;
 const upper=estimate.upper*surcharge;
 const returnEstimate=wag254Estimate(x,0,target,current,trainedCost);
 const roundTrip=upper+returnEstimate.upper*surcharge;
 const safe=x.s.energy-roundTrip>.54&&x.material>.055&&x.s.integrity>.30;
 const budget=st.probeBudget-st.probeDebits>=roundTrip;
 const gap=x.t-st.lastProbe>=WAG256_PROBE_GAP;
 const highInformation=risk.n===0||risk.stale>=48||risk.mismatch;
 const policyWants=variant==='periodicProbe'?true:highInformation;
 const window=WAG256_PROBE_TICKS.includes(x.t);
 // Paired fast intervals are allowed only if underlying economics can afford a
 // switch AND a return. No future regime price is available here.
 return {permit:window&&safe&&budget&&gap&&policyWants,
   safe,budget,gap,window,policyWants,from:current,to:target,
   estimate,expectedRoundTrip:roundTrip,risk,features};
}
function wag256Run(cap,family,seed,duration,regime,variant,models,cadenceModel,costModel){
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 const st=wag256Control(),transactions=[],probes=[],timeline=[],counts={3:0,6:0,12:0,24:0};
 let lastRepair=-100,missed=0,opportunities=0,regret=0,baselineChanges=0;
 while(x.t<duration){
  st.currentTick=x.t;
  const tick=x.t,nominal=wag252Select(x,cadenceModel),riskBefore=wag256Risk(st);
  let transition=null,reason='hold',action='abstain';
  // Finish a previously committed measurement attempt. The actual surcharge
  // paid on entry has been observed and affects the exit safety check.
  if(st.probeStage==='active'&&tick>=st.returnAt){
    const from=st.cadence,to=st.probeTarget,features=wag254Signals(x,tick-st.lastChange,from,to);
    const est=wag254Estimate(x,tick-st.lastChange,from,to,costModel);
    const padded=est.upper*Math.max(2,wag256Risk(st).upper);
    if(x.s.energy-padded>.38&&st.probeBudget-st.probeDebits>=padded){
      transition={from,to,features,predicted:est.mean,upper:est.upper,probe:true,phase:'return'};
      st.cadence=to;st.switches++;st.lastChange=tick;reason='probe-return';
      st.probeStage='idle';st.probeTarget=null;
    }else{
      // A failed return is not silently treated as free: remain at probe
      // cadence and record that the probe trapped the controller.
      st.probeStage='trapped';st.blocked++;reason='unsafe-return';
    }
  }else if(st.probeStage==='idle'){
    // A genuine cadence recommendation uses WAG-255's frozen cost gate.
    const target=nominal.cadence;
    if(target!==st.cadence){
      if(target!==st.candidate){st.candidate=target;st.streak=1;}else st.streak++;
      if(st.streak>=2){
        const features=wag254Signals(x,tick-st.lastChange,st.cadence,target);
        const est=wag254Estimate(x,tick-st.lastChange,st.cadence,target,costModel);
        const limit=variant==='frozen'?est.upper:est.upper*Math.max(1,riskBefore.upper);
        if(est.known&&x.s.energy-limit>.40&&nominal.margin>.18*limit+.00002){
          transition={from:st.cadence,to:target,features,predicted:est.mean,upper:est.upper,probe:false,phase:'operational'};
          st.cadence=target;st.switches++;st.lastChange=tick;baselineChanges++;reason='operational';
          st.candidate=null;st.streak=0;
        }else{st.blocked++;reason='model-gate'}
      }else reason='confirming';
    }else{st.candidate=null;st.streak=0;}
    // Information-seeking only when no operating transition happened this tick.
    if(!transition&&variant!=='noProbe'&&variant!=='frozen'){
      const p=wag256ProbeDecision(x,st,costModel,variant);
      if(p.permit){
        transition={from:p.from,to:p.to,features:p.features,predicted:p.estimate.mean,
         upper:p.estimate.upper,probe:true,phase:'entry'};
        st.probeTarget=p.from;st.probeStage='active';st.returnAt=tick+6;
        st.lastProbe=tick;st.probes++;st.cadence=p.to;st.switches++;st.lastChange=tick;
        reason='probe-entry';probes.push({tick,expectedRoundTrip:p.expectedRoundTrip,risk:p.risk.status});
      }
    }
  }else if(st.probeStage==='trapped'){reason='probe-trapped';}
  counts[st.cadence]++;
  const choice=wag251Choice(x,models,lastRepair,'fixed'+st.cadence);
  action=choice.action;if(action!=='abstain')lastRepair=tick;
  if(WAG250_SAMPLE.includes(tick%240)&&tick+48<=duration){
   const viable=['prevent','rebuild'].filter(a=>wag246Eligible(x,a));
   const values=Object.fromEntries(viable.map(a=>[a,wag250Evaluate(x,a).value]));
   const best=Math.max(0,...Object.values(values)),chosen=action==='abstain'?0:values[action]??0;
   const loss=Math.max(0,best-chosen);regret+=loss;
   if(best>.00005){opportunities++;if(action==='abstain')missed++;}
   timeline.push({tick,action,cadence:st.cadence,status:riskBefore.status,
     reason,regret:loss,energy:x.s.energy});
  }
  step244(x,action);
  if(transition){
    const actual=wag255ActualFee(x,transition,regime,tick),debit=Math.min(x.s.energy,actual);
    x.s.energy-=debit;x.s.trace.at(-1).energy=x.s.energy;st.fees+=debit;st.charges++;
    if(transition.probe)st.probeDebits+=debit;
    const ratio=actual/Math.max(transition.predicted,1e-12);
    if(ratio>1.55){st.overrun++;if(st.detectedTick===null)st.detectedTick=tick;}
    const receipt={tick,from:transition.from,to:transition.to,predicted:transition.predicted,
      actual,charged:debit,ratio,probe:transition.probe,phase:transition.phase,
      priorStatus:riskBefore.status};
    st.observed.push(receipt);transactions.push(receipt);
  }
 }
 const ledger=wag248Ledger(x),risk=wag256Risk(st);
 return {mode:variant,regime,scenario:family,capacity:cap,seed,duration,
  meanIntegrity:x.s.area/duration,finalIntegrity:x.s.integrity,finalEnergy:x.s.energy,
  aliveTicks:x.s.trace.filter(v=>v.energy>.08&&v.integrity>.15).length,
  reserveTicks:x.s.trace.filter(v=>v.energy>.25&&v.integrity>.30).length,
  maintenance:x.choices,switches:st.switches,fees:st.fees,probeCount:st.probes,
  probeDebits:st.probeDebits,probeBudget:st.probeBudget,probeStage:st.probeStage,
  blocked:st.blocked,overruns:st.overrun,detectedTick:st.detectedTick,
  baselineChanges,missed,opportunities,regret,
  observedStatus:risk.status,lastObservedTick:st.observed.at(-1)?.tick??null,
  transactions,probes,timeline,cadenceCounts:counts,ledger,trace:x.s.trace};
}
function wag256Experiment(){
 const models=wag251Models(),cadence=wag252Train(models),cost=wag254Train(models);
 const groups={},examples=[];
 for(const regime of WAG255_REGIMES)for(const duration of [240,480])
 for(const cap of CAP234)for(const family of [...FAMILIES_TRAIN244,...FAMILIES_HOLD244])
 for(const seed of WAG256_TEST){
  const runs={};for(const mode of WAG256_VARIANTS)
    runs[mode]=wag256Run(cap,family,seed,duration,regime,mode,models,cadence,cost);
  const key=regime+':'+duration+':'+(FAMILIES_HOLD244.includes(family)?'withheld':'familiar');
  const g=groups[key]??={n:0,models:{},survivalNonInferior:0,detectedAny:0};
  g.n++;if(runs.valueProbe.aliveTicks>=runs.noProbe.aliveTicks&&
   runs.valueProbe.reserveTicks>=runs.noProbe.reserveTicks)g.survivalNonInferior++;
  if(runs.valueProbe.detectedTick!==null)g.detectedAny++;
  for(const [name,r] of Object.entries(runs)){
    const a=g.models[name]??={integrity:0,alive:0,reserve:0,probes:0,fees:0,detected:0,trapped:0};
    a.integrity+=r.meanIntegrity;a.alive+=r.aliveTicks;a.reserve+=r.reserveTicks;
    a.probes+=r.probeCount;a.fees+=r.fees;
    a.detected+=(r.detectedTick===null?0:1);a.trapped+=(r.probeStage==='trapped'?1:0);
  }
  if(duration===240&&cap===13&&seed===4301&&['scar','combined'].includes(family))
   examples.push({regime,family,policies:Object.fromEntries(Object.entries(runs).map(([name,r])=>[name,{
    integrity:r.meanIntegrity,alive:r.aliveTicks,reserve:r.reserveTicks,probes:r.probeCount,
    fees:r.fees,detectedTick:r.detectedTick,trapped:r.probeStage==='trapped'}])),
    transactions:runs.valueProbe.transactions});
 }
 for(const g of Object.values(groups))for(const v of Object.values(g.models))
  for(const key of Object.keys(v))v[key]/=g.n;
 return {bound:'WAG-256',testSeeds:WAG256_TEST,regimes:WAG255_REGIMES,groups,examples,
  constraints:{probeBudget:WAG256_PROBE_BUDGET,probeGap:WAG256_PROBE_GAP,
   reserveFloor:.54,returnFloor:.38},
  caveat:'Probes physically change the synthetic control cadence and may trap the policy; zero observations do not mean zero hidden cost.'};
}
if(typeof module!=='undefined')module.exports={wag256Run,wag256Experiment,wag256Risk,wag256ProbeDecision};
