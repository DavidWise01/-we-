// WAG-225 · autonomous homeostatic emergence · .dlw
// Synthetic controller and observations; not a biological emergence claim.
// {24/[2]/[4]/(3)/(3)/(1)/(1)}
const W225_CAPACITIES=[5,8,13,21],W225_ACTIONS=['HOLD','HIDE','FIGHT','FLIGHT'];
function rng225(seed){let n=seed>>>0;return ()=>((n=(Math.imul(n,1664525)+1013904223)>>>0)/4294967296)}
function clamp225(x,lo=0,hi=1){return Math.max(lo,Math.min(hi,x))}
function ambient225(t,scenario){
 const segment=Math.floor(t/40)%6,regimes=[.14,.24,.79,.33,.9,.2];let pressure=regimes[segment];
 if(scenario==='stable')pressure=.25;
 if(scenario==='shock')pressure=t>=80&&t<120?.96:.21;
 if(scenario==='oscillating')pressure=.22+.65*(.5+.5*Math.sin(t*.21));
 if(scenario==='drift')pressure=.17+.7*t/240;
 if(scenario==='recovery')pressure=t<80?.25:t<160?.82:.16;
 return clamp225(pressure);
}
function simulate225(capacity,scenario,seed,adaptive=true){
 const rnd=rng225(seed),s={energy:.78,integrity:.91,stress:0,memory:8,history:[],actions:{HOLD:0,HIDE:0,FIGHT:0,FLIGHT:0},repaired:0,trajectory:[],survived:0,transitions:0};
 let previous='HOLD';
 for(let t=0;t<240;t++){
  const external=ambient225(t,scenario),noise=(rnd()-.5)*.09,perceived=clamp225(external+noise);s.history.push(perceived);
  if(adaptive){
   const prev=s.history.slice(-8),mean=prev.reduce((a,b)=>a+b,0)/prev.length,variance=prev.reduce((a,b)=>a+(b-mean)**2,0)/prev.length;
   const jump=Math.abs(perceived-(s.history[s.history.length-2]??perceived));
   s.memory=jump>.16||variance>.035?3:variance<.006?Math.min(21,capacity):8;
  }else s.memory=8;
  const h=s.history.slice(-s.memory),smoothed=h.reduce((a,b)=>a+b,0)/h.length;s.stress=clamp225(.75*s.stress+.25*smoothed);
  let action='HOLD';
  if(capacity>=13){
   if(s.stress>.62&&s.energy>.49&&s.integrity>.35)action='FIGHT';
   else if(s.stress>.48&&s.energy<.49)action='FLIGHT';
   else if(s.stress>.38)action='HIDE';
  }else if(capacity>=8){if(s.stress>.42)action='HIDE'}
  const shield=action==='HIDE'?.46:action==='FLIGHT'?.58:action==='FIGHT'?.64:0;
  const raw=external*(1-shield),cost=action==='FIGHT'?.032:action==='FLIGHT'?.023:action==='HIDE'?.011:.004;
  const generation=.016+.0005*Math.min(capacity,13)-.012*external,damage=Math.max(0,raw-.31)*.034+(s.energy<.14?.012:0);
  const repairBase=capacity>=21?.020:capacity>=13?.015:capacity>=8?.012:.009;
  const repair=Math.min((1-s.integrity),repairBase*Math.max(.22,s.energy));
  s.energy=clamp225(s.energy+generation-cost-.011*raw-repair*.35);s.integrity=clamp225(s.integrity-damage+repair);s.repaired+=repair;
  if(action!==previous)s.transitions++;previous=action;s.actions[action]++;
  const alive=s.integrity>.15&&s.energy>.08;if(alive)s.survived++;
  s.trajectory.push({t,pressure:+external.toFixed(4),observed:+perceived.toFixed(4),energy:+s.energy.toFixed(4),integrity:+s.integrity.toFixed(4),stress:+s.stress.toFixed(4),memory:s.memory,action,alive});
 }
 return {capacity,scenario,seed,adaptive,aliveTicks:s.survived,finalEnergy:+s.energy.toFixed(4),finalIntegrity:+s.integrity.toFixed(4),meanIntegrity:+(s.trajectory.reduce((a,x)=>a+x.integrity,0)/240).toFixed(4),actions:s.actions,transitions:s.transitions,repaired:+s.repaired.toFixed(3),trajectory:s.trajectory};
}


function simulate226(capacity,scenario,seed,policy='damped'){
 const rnd=rng225(seed),s={energy:.78,integrity:.91,stress:0,memory:8,history:[],actions:{HOLD:0,HIDE:0,FIGHT:0,FLIGHT:0},trace:[],transitions:0,oscillatingTicks:0,emergencyOverrides:0,survived:0};
 let current='HOLD',held=0;
 for(let t=0;t<240;t++){
  const pressure=ambient225(t,scenario),observed=clamp225(pressure+(rnd()-.5)*.09);
  s.history.push(observed);
  const recent=s.history.slice(-12),mean=recent.reduce((a,b)=>a+b,0)/recent.length,variance=recent.reduce((a,b)=>a+(b-mean)**2,0)/recent.length;
  const jump=Math.abs(observed-(s.history.at(-2)??observed));
  const changes=[];for(let i=1;i<recent.length;i++)changes.push(recent[i]-recent[i-1]);
  let reversals=0;for(let i=1;i<changes.length;i++)if(changes[i]*changes[i-1]<0&&Math.abs(changes[i])>.07&&Math.abs(changes[i-1])>.07)reversals++;
  const oscillating=recent.length>=10&&variance>.016&&reversals>=3;
  if(oscillating)s.oscillatingTicks++;
  if(policy==='fixed')s.memory=8;
  else if(policy==='adaptive')s.memory=jump>.16||variance>.035?3:variance<.006?Math.min(21,capacity):8;
  else s.memory=oscillating?Math.min(21,capacity):jump>.16?3:variance<.006?Math.min(21,capacity):8;
  const history=s.history.slice(-s.memory),smoothed=history.reduce((a,b)=>a+b,0)/history.length;
  const target=policy==='damped'&&oscillating?.65*smoothed+.35*mean:smoothed;
  const inertia=policy==='damped'&&oscillating?.13:.25;
  s.stress=clamp225((1-inertia)*s.stress+inertia*target);
  let proposal='HOLD';
  if(capacity>=13){
   if(s.stress>.62&&s.energy>.49&&s.integrity>.35)proposal='FIGHT';
   else if(s.stress>.48&&s.energy<.49)proposal='FLIGHT';
   else if(s.stress>.38)proposal='HIDE';
  }else if(capacity>=8&&s.stress>.42)proposal='HIDE';
  const emergency=observed>.9&&s.integrity<.75&&capacity>=13;
  if(policy==='damped'){
   if(proposal!==current&&held<(oscillating?9:4)&&!emergency)proposal=current;
   if(emergency&&proposal==='HOLD'){proposal=s.energy>.49?'FIGHT':'FLIGHT';s.emergencyOverrides++}
  }
  const action=proposal;if(action!==current){s.transitions++;held=0}else held++;
  current=action;s.actions[action]++;
  const shield=action==='HIDE'?.46:action==='FLIGHT'?.58:action==='FIGHT'?.64:0;
  const raw=pressure*(1-shield),cost=action==='FIGHT'?.032:action==='FLIGHT'?.023:action==='HIDE'?.011:.004;
  const generation=.016+.0005*Math.min(capacity,13)-.012*pressure;
  const damage=Math.max(0,raw-.31)*.034+(s.energy<.14?.012:0);
  const repairBase=capacity>=21?.020:capacity>=13?.015:capacity>=8?.012:.009;
  const repair=Math.min(1-s.integrity,repairBase*Math.max(.22,s.energy));
  s.energy=clamp225(s.energy+generation-cost-.011*raw-repair*.35);
  s.integrity=clamp225(s.integrity-damage+repair);
  const alive=s.integrity>.15&&s.energy>.08;if(alive)s.survived++;
  s.trace.push({t,pressure:+pressure.toFixed(4),observed:+observed.toFixed(4),energy:+s.energy.toFixed(4),integrity:+s.integrity.toFixed(4),stress:+s.stress.toFixed(4),memory:s.memory,action,oscillating,emergency});
 }
 return {capacity,scenario,seed,policy,meanIntegrity:+(s.trace.reduce((a,v)=>a+v.integrity,0)/240).toFixed(4),finalEnergy:+s.energy.toFixed(4),finalIntegrity:+s.integrity.toFixed(4),transitions:s.transitions,oscillatingTicks:s.oscillatingTicks,emergencyOverrides:s.emergencyOverrides,aliveTicks:s.survived,actions:s.actions,trace:s.trace};
}
function experiment226(){
 const scenarios=['stable','shock','oscillating','drift','recovery','default'],cases=[],examples=[],counterexamples=[];
 let runs=0,ticks=0,dampedWins=0,dampedLosses=0,dampedTies=0,transitionReduction=0,transitionIncreases=0,emergencyOverrides=0;
 for(const capacity of W225_CAPACITIES)for(const scenario of scenarios){
  let meanD=0,meanA=0,meanF=0,transD=0,transA=0,transF=0,win=0,loss=0,tie=0;
  for(let seed=225;seed<233;seed++){
   const d=simulate226(capacity,scenario,seed,'damped'),a=simulate226(capacity,scenario,seed,'adaptive'),f=simulate226(capacity,scenario,seed,'fixed');
   runs+=3;ticks+=720;meanD+=d.meanIntegrity;meanA+=a.meanIntegrity;meanF+=f.meanIntegrity;
   transD+=d.transitions;transA+=a.transitions;transF+=f.transitions;
   if(d.meanIntegrity>a.meanIntegrity+1e-6){win++;dampedWins++}else if(a.meanIntegrity>d.meanIntegrity+1e-6){loss++;dampedLosses++}else{tie++;dampedTies++}
   if(d.transitions<a.transitions)transitionReduction++;if(d.transitions>a.transitions)transitionIncreases++;
   emergencyOverrides+=d.emergencyOverrides;
   if(seed===225)examples.push({capacity,scenario,damped:d,adaptive:{...a,trace:undefined},fixed:{...f,trace:undefined}});
   if(a.meanIntegrity>d.meanIntegrity+.015&&counterexamples.length<18)counterexamples.push({capacity,scenario,seed,dampedIntegrity:d.meanIntegrity,adaptiveIntegrity:a.meanIntegrity,dampedTransitions:d.transitions,adaptiveTransitions:a.transitions});
   for(const r of [d,a,f]){
    if(r.trace.some(v=>v.energy<0||v.energy>1||v.integrity<0||v.integrity>1))throw Error('out of bounds');
    if(capacity<13&&(r.actions.FLIGHT||r.actions.FIGHT))throw Error('capacity gate violated');
   }
  }
  cases.push({capacity,scenario,pairedSeeds:8,dampedMeanIntegrity:+(meanD/8).toFixed(4),adaptiveMeanIntegrity:+(meanA/8).toFixed(4),fixedMeanIntegrity:+(meanF/8).toFixed(4),dampedTransitions:transD,adaptiveTransitions:transA,fixedTransitions:transF,wins:win,losses:loss,ties:tie});
 }
 return {runs,ticks,dampedWins,dampedLosses,dampedTies,transitionReduction,transitionIncreases,emergencyOverrides,cases,examples,counterexamples};
}
if(typeof module!=='undefined')module.exports={simulate226,experiment226};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment226(),null,2));
