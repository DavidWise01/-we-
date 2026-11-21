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

function simulate227(capacity,scenario,seed,policy='conditional'){
 const rnd=rng225(seed),s={energy:.78,integrity:.91,stress:0,memory:8,history:[],actions:{HOLD:0,HIDE:0,FIGHT:0,FLIGHT:0},trace:[],transitions:0,oscillatingTicks:0,emergencyOverrides:0,survived:0};
 let current='HOLD',held=0;
 for(let t=0;t<240;t++){
  const pressure=ambient225(t,scenario),observed=clamp225(pressure+(rnd()-.5)*.09);
  s.history.push(observed);
  const recent=s.history.slice(-12),mean=recent.reduce((a,b)=>a+b,0)/recent.length,variance=recent.reduce((a,b)=>a+(b-mean)**2,0)/recent.length;
  const jump=Math.abs(observed-(s.history.at(-2)??observed));
  const changes=[];for(let i=1;i<recent.length;i++)changes.push(recent[i]-recent[i-1]);
  let reversals=0;for(let i=1;i<changes.length;i++)if(changes[i]*changes[i-1]<0&&Math.abs(changes[i])>.07&&Math.abs(changes[i-1])>.07)reversals++;
  const cw=s.history.slice(-32),lag=14;
  let covariance=0;
  if(cw.length===32){const av=cw.reduce((a,b)=>a+b,0)/32;for(let i=lag;i<32;i++)covariance+=(cw[i]-av)*(cw[i-lag]-av);covariance/=18}
  const periodic=cw.length===32&&Math.max(...cw)-Math.min(...cw)>.35&&covariance<-.01;
  const oscillating=policy==='conditional'?periodic:(recent.length>=10&&variance>.016&&reversals>=3);
  if(oscillating)s.oscillatingTicks++;
  if(policy==='fixed')s.memory=8;
  else if(policy==='adaptive'||policy==='conditional')s.memory=jump>.16||variance>.035?3:variance<.006?Math.min(21,capacity):8;
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
  if(policy==='conditional'){
   if(proposal!==current&&oscillating&&!emergency&&held<8){
     const shieldOf=a=>a==='HIDE'?.46:a==='FLIGHT'?.58:a==='FIGHT'?.64:0;
     const costOf=a=>a==='FIGHT'?.032:a==='FLIGHT'?.023:a==='HIDE'?.011:.004;
     const damageOf=a=>Math.max(0,pressure*(1-shieldOf(a))-.31)*.034;
     const benefit=damageOf(current)-damageOf(proposal)+.25*(costOf(current)-costOf(proposal));
     if(benefit<0)proposal=current;
   }
  }else if(policy==='damped'){
   if(proposal!==current&&held<(oscillating?9:4)&&!emergency)proposal=current;
   if(emergency&&proposal==='HOLD'){proposal=s.energy>.49?'FIGHT':'FLIGHT';s.emergencyOverrides++}
  }
  const previousAction=current;const action=proposal;if(action!==current){s.transitions++;held=0}else held++;
  current=action;s.actions[action]++;
  const shield=action==='HIDE'?.46:action==='FLIGHT'?.58:action==='FIGHT'?.64:0;
  const raw=pressure*(1-shield),cost=action==='FIGHT'?.032:action==='FLIGHT'?.023:action==='HIDE'?.011:.004;
  const generation=.016+.0005*Math.min(capacity,13)-.012*pressure;
  const damage=Math.max(0,raw-.31)*.034+(s.energy<.14?.012:0);
  const repairBase=capacity>=21?.020:capacity>=13?.015:capacity>=8?.012:.009;
  const repair=Math.min(1-s.integrity,repairBase*Math.max(.22,s.energy));
  s.energy=clamp225(s.energy+generation-cost-.011*raw-repair*.35-(action!==previousAction?.003:0));
  s.integrity=clamp225(s.integrity-damage+repair);
  const alive=s.integrity>.15&&s.energy>.08;if(alive)s.survived++;
  s.trace.push({t,pressure:+pressure.toFixed(4),observed:+observed.toFixed(4),energy:+s.energy.toFixed(4),integrity:+s.integrity.toFixed(4),stress:+s.stress.toFixed(4),memory:s.memory,action,oscillating,emergency});
 }
 return {capacity,scenario,seed,policy,meanIntegrity:+(s.trace.reduce((a,v)=>a+v.integrity,0)/240).toFixed(4),finalEnergy:+s.energy.toFixed(4),finalIntegrity:+s.integrity.toFixed(4),transitions:s.transitions,oscillatingTicks:s.oscillatingTicks,emergencyOverrides:s.emergencyOverrides,aliveTicks:s.survived,actions:s.actions,trace:s.trace};
}

function experiment227(){
 const scenarios=['stable','shock','oscillating','drift','recovery','default'],capacities=[5,8,13,21],seeds=[229,230,231,232,233,234,235,236];
 const rows=[],examples=[],counterexamples=[];let policyRuns=0,ticks=0,wins=0,losses=0,ties=0,transitionReduction=0,transitionIncrease=0,oscillationTicks=0;
 for(const capacity of capacities)for(const scenario of scenarios){
  const integrity={conditional:0,adaptive:0,damped:0,fixed:0},transitions={conditional:0,adaptive:0,damped:0,fixed:0};
  let caseWins=0,caseLosses=0,caseTies=0;
  for(const seed of seeds){
   const p={};
   for(const mode of ['conditional','adaptive','damped','fixed']){
    p[mode]=simulate227(capacity,scenario,seed,mode);policyRuns++;ticks+=240;
    integrity[mode]+=p[mode].meanIntegrity;transitions[mode]+=p[mode].transitions;
   }
   const c=p.conditional,a=p.adaptive;
   if(c.meanIntegrity>a.meanIntegrity+1e-6){wins++;caseWins++}
   else if(c.meanIntegrity+1e-6<a.meanIntegrity){losses++;caseLosses++}
   else{ties++;caseTies++}
   if(c.transitions<a.transitions)transitionReduction++;
   if(c.transitions>a.transitions)transitionIncrease++;
   oscillationTicks+=c.oscillatingTicks;
   if(seed===229)examples.push({capacity,scenario,conditional:c,adaptiveSummary:{...a,trace:undefined},dampedSummary:{...p.damped,trace:undefined},fixedSummary:{...p.fixed,trace:undefined}});
   if((c.meanIntegrity<a.meanIntegrity||c.transitions>a.transitions)&&counterexamples.length<25){
    counterexamples.push({capacity,scenario,seed,conditionalIntegrity:c.meanIntegrity,adaptiveIntegrity:a.meanIntegrity,conditionalTransitions:c.transitions,adaptiveTransitions:a.transitions});
   }
   for(const z of Object.values(p)){
    if(z.trace.some(v=>v.energy<0||v.integrity<0||v.energy>1||v.integrity>1))throw Error('state bounds');
    if(capacity<13&&(z.actions.FIGHT||z.actions.FLIGHT))throw Error('capacity gate');
   }
  }
  rows.push({capacity,scenario,holdoutPairs:8,meanIntegrity:Object.fromEntries(Object.entries(integrity).map(([k,v])=>[k,+(v/8).toFixed(4)])),transitions,wins:caseWins,losses:caseLosses,ties:caseTies});
 }
 return {holdoutSeeds:seeds,policyRuns,ticks,wins,losses,ties,transitionReduction,transitionIncrease,oscillationTicks,rows,examples,counterexamples};
}
if(typeof module!=='undefined')module.exports={simulate227,experiment227};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment227(),null,2));
