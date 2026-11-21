function rng(seed){let x=seed>>>0;return ()=>((x=(Math.imul(x,1664525)+1013904223)>>>0)/4294967296)}

function clip(x){return Math.max(0,Math.min(1,x))}

function environment(t,kind,phase){
 let p=.24,frequency=.21;
 if(kind==="chirp"){frequency=.07+.48*t/240;p=.49+.36*Math.sin(phase+.07*t+.001*t*t)}
 if(kind==="scar"){p=.25+(t>=55&&t<100?.70:0)+(t>=164&&t<195?.56:0)}
 if(kind==="famine"){p=.40+.22*Math.sin(phase+t*.14)}
 if(kind==="friction"){p=.42+.25*Math.sin(phase+t*.19)}
 if(kind==="combined"){p=.46+.31*Math.sin(phase+.07*t+.001*t*t)+(t>96&&t<135?.25:0)}
 return {pressure:clip(p),frequency};
}

function simulate(capacity,scenario,seed,mode){
 const random=rng(seed);const phase=random()*6.283185307179586;
 let energy=.78,integrity=.91,ceiling=1,stress=0,action="HOLD",dwell=0,transitions=0,aliveTicks=0,meanIntegrity=0,reserveTicks=0,damageTotal=0,damageIrreversible=0,repairTotal=0,spentSwitch=0,detected=0;
 const hist=[],trace=[],counts={HOLD:0,HIDE:0,FIGHT:0,FLIGHT:0};
 const shield={HOLD:0,HIDE:.46,FIGHT:.64,FLIGHT:.58};
 const actionCost={HOLD:.004,HIDE:.011,FIGHT:.032,FLIGHT:.023};
 for(let t=0;t<240;t++){
  const env=environment(t,scenario,phase),pressure=env.pressure,observed=clip(pressure+(random()-.5)*.09);
  hist.push(observed);
  const w=hist.slice(-8),avg=w.reduce((a,b)=>a+b,0)/w.length,variance=w.reduce((a,b)=>a+(b-avg)**2,0)/w.length;
  const jump=Math.abs(observed-(hist.at(-2)??observed)),memory=mode==="fixed"?8:jump>.16||variance>.035?3:variance<.006?Math.min(21,capacity):8;
  const history=hist.slice(-memory),smoothed=history.reduce((a,b)=>a+b,0)/history.length;
  stress=clip(.75*stress+.25*smoothed);
  let proposal="HOLD";
  if(capacity>=13){
   if(stress>.62&&energy>.49&&integrity>.35)proposal="FIGHT";
   else if(stress>.48&&energy<.49)proposal="FLIGHT";
   else if(stress>.38)proposal="HIDE";
  }else if(capacity>=8&&stress>.42)proposal="HIDE";
  const recent=hist.slice(-32);
  let covariance=0;
  if(recent.length===32){const mean=recent.reduce((a,b)=>a+b,0)/32;for(let k=14;k<32;k++)covariance+=(recent[k]-mean)*(recent[k-14]-mean);covariance/=18}
  const periodic=recent.length===32&&Math.max(...recent)-Math.min(...recent)>.35&&covariance<-.01;
  if(periodic)detected++;
  const emergency=observed>.9&&integrity<.75&&capacity>=13;
  const scarcity=scenario==="famine"||scenario==="combined";
  const friction=scenario==="friction"||scenario==="combined";
  const switchFee=(friction?.003+(.020*(1-energy))**2:.003)+(integrity<.55?.007:0);
  if(mode==="conditional"&&proposal!==action&&periodic&&!emergency&&dwell<8){
   const d=a=>Math.max(0,pressure*(1-shield[a])-.31)*.034;
   const benefit=d(action)-d(proposal)+.25*(actionCost[action]-actionCost[proposal]);
   if(benefit<0)proposal=action;
  }
  if(mode==="reserve"&&proposal!==action&&!emergency){
   const prospectiveLoss=Math.max(0,pressure*(1-shield[proposal])-.31)*.034;
   const currentLoss=Math.max(0,pressure*(1-shield[action])-.31)*.034;
   const benefit=currentLoss-prospectiveLoss;
   const running=actionCost[proposal]-actionCost[action];
   const adaptationReserve=scarcity?.30:.20;
   if(benefit<.45*running+.25*switchFee && energy<adaptationReserve+.32)proposal=action;
  }
  const changed=proposal!==action;if(changed){transitions++;dwell=0;spentSwitch+=switchFee}else dwell++;
  action=proposal;counts[action]++;
  const raw=pressure*(1-shield[action]);
  const generation=(.016+.0005*Math.min(capacity,13)-.012*pressure)*(scarcity?(t>=62?.24:.75):1);
  const damage=Math.max(0,raw-.31)*.034+(energy<.14?.012:0);
  const repairBase=capacity>=21?.020:capacity>=13?.015:capacity>=8?.012:.009;
  const repair=Math.min(Math.max(0,ceiling-integrity),repairBase*Math.max(.22,energy)*(scarcity?.42:1));
  const scarFraction=(scenario==="scar"||scenario==="combined")?.26:0;
  ceiling=clip(ceiling-damage*scarFraction);
  energy=clip(energy+generation-actionCost[action]-.011*raw-repair*.35-(changed?switchFee:0));
  integrity=Math.min(ceiling,clip(integrity-damage+repair));
  damageTotal+=damage;damageIrreversible+=damage*scarFraction;repairTotal+=repair;
  const alive=integrity>.15&&energy>.08;if(alive)aliveTicks++;
  if(energy>.25&&integrity>.30)reserveTicks++;
  meanIntegrity+=integrity/240;
  trace.push({t,pressure:+pressure.toFixed(4),energy:+energy.toFixed(4),integrity:+integrity.toFixed(4),ceiling:+ceiling.toFixed(4),action,changed,periodic,fee:+switchFee.toFixed(5)});
  if(integrity<0||integrity>ceiling+1e-10||energy<0||energy>1)throw Error("bounds");
  if(capacity<13&&(action==="FIGHT"||action==="FLIGHT"))throw Error("capacity gate");
 }
 return {capacity,scenario,seed,mode,meanIntegrity:+meanIntegrity.toFixed(6),finalIntegrity:+integrity.toFixed(6),finalEnergy:+energy.toFixed(6),recoverableCeiling:+ceiling.toFixed(6),aliveTicks,reserveTicks,transitions,spentSwitch:+spentSwitch.toFixed(5),irreversibleDamage:+damageIrreversible.toFixed(5),repairTotal:+repairTotal.toFixed(5),periodicTicks:detected,counts,trace};
}

function experiment(){
 const seeds=[401,402,403,404,405,406,407,408],scenarios=["chirp","scar","famine","friction","combined"],capacities=[5,8,13,21],modes=["conditional","adaptive","fixed","reserve"];
 const rows=[],examples=[],counterexamples=[];let wins=0,losses=0,ties=0,policyRuns=0;
 for(const capacity of capacities)for(const scenario of scenarios){
  const sums=Object.fromEntries(modes.map(m=>[m,{integrity:0,energy:0,reserve:0,alive:0}]));
  for(const seed of seeds){
   const runs=Object.fromEntries(modes.map(m=>[m,simulate(capacity,scenario,seed,m)]));
   for(const m of modes){const r=runs[m];policyRuns++;sums[m].integrity+=r.meanIntegrity;sums[m].energy+=r.finalEnergy;sums[m].reserve+=r.reserveTicks;sums[m].alive+=r.aliveTicks}
   const c=runs.conditional,a=runs.adaptive,d=c.meanIntegrity-a.meanIntegrity;
   if(d>1e-6)wins++;else if(d< -1e-6)losses++;else ties++;
   if(d< -1e-6&&counterexamples.length<32)counterexamples.push({capacity,scenario,seed,conditional:c.meanIntegrity,adaptive:a.meanIntegrity});
   if(seed===401)examples.push({capacity,scenario,conditional:c,adaptive:{...a,trace:undefined},fixed:{...runs.fixed,trace:undefined},reserve:{...runs.reserve,trace:undefined}});
  }
  rows.push({capacity,scenario,means:Object.fromEntries(modes.map(m=>[m,Object.fromEntries(Object.entries(sums[m]).map(([k,v])=>[k,+(v/8).toFixed(5)]))]))});
 }
 return {bound:"WAG-228",seeds,scenarioFamilies:scenarios,capacities,modes,policyRuns,ticks:policyRuns*240,conditionalVsAdaptive:{wins,losses,ties},rows,examples,counterexamples};
}

function simulate229(capacity,scenario,seed,mode="rest"){
 if(mode!=="rest")return simulate(capacity,scenario,seed,mode);
 const random=rng(seed),phase=random()*Math.PI*2;
 let energy=.78,integrity=.91,ceiling=1,stress=0,action="HOLD",restLatch=false,dwell=0;
 let transitions=0,meanIntegrity=0,aliveTicks=0,reserveTicks=0,restTicks=0,restEntries=0,exitEmergency=0,recoveryEvents=0;
 const hist=[],trace=[],counts={HOLD:0,HIDE:0,FIGHT:0,FLIGHT:0,REST:0};
 const shield={HOLD:0,HIDE:.46,FIGHT:.64,FLIGHT:.58,REST:.08},cost={HOLD:.004,HIDE:.011,FIGHT:.032,FLIGHT:.023,REST:.0015};
 let prevEnergy=energy;
 for(let t=0;t<240;t++){
  const pressure=environment(t,scenario,phase).pressure,observed=clip(pressure+(random()-.5)*.09);
  hist.push(observed);
  const w=hist.slice(-8),avg=w.reduce((a,b)=>a+b,0)/w.length,variance=w.reduce((a,b)=>a+(b-avg)**2,0)/w.length;
  const jump=Math.abs(observed-(hist.at(-2)??observed)),memory=jump>.16||variance>.035?3:variance<.006?Math.min(21,capacity):8;
  const h=hist.slice(-memory);stress=clip(.75*stress+.25*h.reduce((a,b)=>a+b,0)/h.length);
  let proposal="HOLD";
  if(capacity>=13){
   if(stress>.62&&energy>.49&&integrity>.35)proposal="FIGHT";
   else if(stress>.48&&energy<.49)proposal="FLIGHT";
   else if(stress>.38)proposal="HIDE";
  }else if(capacity>=8&&stress>.42)proposal="HIDE";
  const threat=observed>.78||stress>.70||integrity<.26;
  // Reserve mode uses only observed information; scenario family isn't exposed.
  if(restLatch){
   if(threat||energy>.53||dwell>=36){restLatch=false;if(threat)exitEmergency++}
  }else if(energy<.38&&!threat&&observed<.57&&stress<.60&&integrity>.27){
   restLatch=true;restEntries++;
  }
  if(restLatch)proposal="REST";
  const scarcity=scenario==="famine"||scenario==="combined";
  const friction=scenario==="friction"||scenario==="combined";
  const switchFee=(friction?.003+(.020*(1-energy))**2:.003)+(integrity<.55?.007:0);
  const changed=proposal!==action;
  if(changed){transitions++;dwell=0}else dwell++;
  action=proposal;counts[action]++;if(action==="REST")restTicks++;
  const raw=pressure*(1-shield[action]);
  const generation=(.016+.0005*Math.min(capacity,13)-.012*pressure)*(scarcity?(t>=62?.24:.75):1);
  const damage=Math.max(0,raw-.31)*.034+(energy<.14?.012:0);
  const repairBase=capacity>=21?.020:capacity>=13?.015:capacity>=8?.012:.009;
  const repair=Math.min(Math.max(0,ceiling-integrity),repairBase*Math.max(.22,energy)*(scarcity?.42:1));
  const scarFraction=(scenario==="scar"||scenario==="combined")?.26:0;
  ceiling=clip(ceiling-damage*scarFraction);
  energy=clip(energy+generation-cost[action]-.011*raw-repair*.35-(changed?switchFee:0));
  integrity=Math.min(ceiling,clip(integrity-damage+repair));
  const alive=integrity>.15&&energy>.08;
  if(alive)aliveTicks++;
  if(energy>.25&&integrity>.30)reserveTicks++;
  if(prevEnergy<=.25&&energy>.25)recoveryEvents++;
  prevEnergy=energy;meanIntegrity+=integrity/240;
  trace.push({t,pressure:+pressure.toFixed(4),energy:+energy.toFixed(4),integrity:+integrity.toFixed(4),ceiling:+ceiling.toFixed(4),action,restLatch,changed,alive});
  if(energy<0||energy>1||integrity<0||integrity>ceiling+1e-10)throw Error("state bounds");
  if(capacity<13&&(action==="FIGHT"||action==="FLIGHT"))throw Error("capacity gate");
 }
 return {capacity,scenario,seed,mode,meanIntegrity:+meanIntegrity.toFixed(6),finalIntegrity:+integrity.toFixed(6),finalEnergy:+energy.toFixed(6),recoverableCeiling:+ceiling.toFixed(6),aliveTicks,reserveTicks,transitions,restTicks,restEntries,exitEmergency,recoveryEvents,counts,trace};
}
function experiment229(){
 const seeds=[501,502,503,504,505,506,507,508],capacities=[5,8,13,21],scenarios=["chirp","scar","famine","friction","combined"],modes=["rest","conditional","reserve","adaptive"];
 const rows=[],examples=[],counterexamples=[];let wins=0,losses=0,ties=0,runCount=0;
 for(const capacity of capacities)for(const scenario of scenarios){
  const sums=Object.fromEntries(modes.map(m=>[m,{integrity:0,finalEnergy:0,aliveTicks:0,reserveTicks:0,transitions:0}]));
  for(const seed of seeds){
   const runs=Object.fromEntries(modes.map(m=>[m,simulate229(capacity,scenario,seed,m)]));
   for(const mode of modes){const r=runs[mode];runCount++;for(const key of Object.keys(sums[mode]))sums[mode][key]+=(key==='integrity'?r.meanIntegrity:(r[key]??0))}
   const a=runs.rest,b=runs.conditional,delta=a.meanIntegrity-b.meanIntegrity;
   if(delta>1e-6)wins++;else if(delta< -1e-6)losses++;else ties++;
   if(delta< -1e-6||a.aliveTicks<b.aliveTicks){counterexamples.push({capacity,scenario,seed,rest:{meanIntegrity:a.meanIntegrity,aliveTicks:a.aliveTicks,finalEnergy:a.finalEnergy},conditional:{meanIntegrity:b.meanIntegrity,aliveTicks:b.aliveTicks,finalEnergy:b.finalEnergy}})}
   if(seed===501)examples.push({capacity,scenario,rest:a,conditional:{...b,trace:undefined},reserve:{...runs.reserve,trace:undefined},adaptive:{...runs.adaptive,trace:undefined}});
  }
  rows.push({capacity,scenario,average:Object.fromEntries(modes.map(m=>[m,Object.fromEntries(Object.entries(sums[m]).map(([k,v])=>[k,+(v/seeds.length).toFixed(6)]))]))});
 }
 return {bound:"WAG-229",seeds,capacities,scenarios,modes,policyRuns:runCount,ticks:runCount*240,restVsConditional:{wins,losses,ties},rows,counterexamples,examples};
}

function simulate230(capacity,scenario,seed,mode="graded"){
 if(mode!=="graded")return simulate229(capacity,scenario,seed,mode);
 const random=rng(seed),phase=random()*Math.PI*2,trace=[],history=[];
 let energy=.78,integrity=.91,ceiling=1,stress=0,protection=0,transitions=0,meanIntegrity=0,aliveTicks=0,reserveTicks=0,defenseTicks=0,recoveryTicks=0,protectionSum=0,spentSwitch=0;
 let prevBand="REST",previousPressure=0;
 const capShield=capacity>=13?.64:capacity>=8?.46:.22;
 for(let t=0;t<240;t++){
  const pressure=environment(t,scenario,phase).pressure;
  const observed=clip(pressure+(random()-.5)*.09);
  history.push(observed);
  const recent=history.slice(-8),average=recent.reduce((a,b)=>a+b,0)/recent.length;
  const variance=recent.reduce((a,b)=>a+(b-average)**2,0)/recent.length;
  const jump=Math.abs(observed-(history.at(-2)??observed));
  const memory=jump>.16||variance>.035?3:variance<.006?Math.min(21,capacity):8;
  const h=history.slice(-memory);const smoothed=h.reduce((a,b)=>a+b,0)/h.length;
  stress=clip(.75*stress+.25*smoothed);
  // Only observable values may influence the control decision.
  const danger=clip(.64*observed+.36*stress+Math.max(0,observed-previousPressure)*.30);
  const urgency=clip((danger-.27)/.62);
  const fragility=clip((.78-integrity)/.60);
  const reserve=clip((.43-energy)/.43);
  const irrecoverableRisk=clip((.96-ceiling)*2.0);
  const desired=capShield*clip(.06+.83*urgency+.22*fragility+.12*irrecoverableRisk-.30*reserve*(1-urgency));
  // Do not abandon critical protection just because energy is low.
  const emergency=danger>.79||integrity<.32;
  const target=emergency?Math.max(desired,capShield*.65):desired;
  const step=emergency?.22:.095;
  const next=clip(Math.max(protection-step,Math.min(protection+step,target)));
  const delta=Math.abs(next-protection);
  const scarcity=scenario==="famine"||scenario==="combined";
  const friction=scenario==="friction"||scenario==="combined";
  const switchFee=(friction?.003+(.020*(1-energy))**2:.003)+(integrity<.55?.007:0);
  // Graded protection has an explicit convex running cost and proportional modulation cost.
  const runCost=.0015+.029*Math.pow(next/.64,1.7);
  const modulationCost=switchFee*delta/.64;
  spentSwitch+=modulationCost;
  protection=next;
  const band=protection<.12?"REST":protection<.40?"GUARD":"DEFEND";
  if(band!==prevBand)transitions++;
  prevBand=band;if(band==="DEFEND")defenseTicks++;if(band==="REST")recoveryTicks++;
  const raw=pressure*(1-protection);
  const generation=(.016+.0005*Math.min(capacity,13)-.012*pressure)*(scarcity?(t>=62?.24:.75):1);
  const damage=Math.max(0,raw-.31)*.034+(energy<.14?.012:0);
  const repairBase=capacity>=21?.020:capacity>=13?.015:capacity>=8?.012:.009;
  const repair=Math.min(Math.max(0,ceiling-integrity),repairBase*Math.max(.22,energy)*(scarcity?.42:1));
  const scarFraction=(scenario==="scar"||scenario==="combined")?.26:0;
  ceiling=clip(ceiling-damage*scarFraction);
  energy=clip(energy+generation-runCost-.011*raw-repair*.35-modulationCost);
  integrity=Math.min(ceiling,clip(integrity-damage+repair));
  const alive=integrity>.15&&energy>.08;
  if(alive)aliveTicks++;if(energy>.25&&integrity>.30)reserveTicks++;
  meanIntegrity+=integrity/240;protectionSum+=protection/240;
  trace.push({t,pressure:+pressure.toFixed(4),observed:+observed.toFixed(4),energy:+energy.toFixed(4),integrity:+integrity.toFixed(4),ceiling:+ceiling.toFixed(4),protection:+protection.toFixed(4),action:band,emergency,alive});
  previousPressure=observed;
  if(energy<0||energy>1||integrity<0||integrity>ceiling+1e-10||protection<0||protection>capShield+1e-10)throw Error("state bounds");
 }
 return {capacity,scenario,seed,mode,meanIntegrity:+meanIntegrity.toFixed(6),finalEnergy:+energy.toFixed(6),finalIntegrity:+integrity.toFixed(6),recoverableCeiling:+ceiling.toFixed(6),aliveTicks,reserveTicks,transitions,defenseTicks,recoveryTicks,meanProtection:+protectionSum.toFixed(6),spentSwitch:+spentSwitch.toFixed(6),trace};
}
function experiment230(){
 const seeds=[601,602,603,604,605,606,607,608],capacities=[5,8,13,21],scenarios=["chirp","scar","famine","friction","combined"],modes=["graded","rest","conditional","reserve"];
 let policyRuns=0,wins=0,losses=0,ties=0;
 const rows=[],examples=[],counterexamples=[];
 for(const capacity of capacities)for(const scenario of scenarios){
  const sums=Object.fromEntries(modes.map(m=>[m,{meanIntegrity:0,finalEnergy:0,aliveTicks:0,reserveTicks:0,transitions:0}]));
  for(const seed of seeds){
   const runs=Object.fromEntries(modes.map(m=>[m,simulate230(capacity,scenario,seed,m)]));
   for(const mode of modes){policyRuns++;for(const k of Object.keys(sums[mode]))sums[mode][k]+=runs[mode][k]}
   const a=runs.graded,b=runs.rest,d=a.meanIntegrity-b.meanIntegrity;
   if(d>1e-6)wins++;else if(d< -1e-6)losses++;else ties++;
   if(d< -1e-6||a.aliveTicks<b.aliveTicks||a.reserveTicks<b.reserveTicks)counterexamples.push({capacity,scenario,seed,graded:{meanIntegrity:a.meanIntegrity,aliveTicks:a.aliveTicks,reserveTicks:a.reserveTicks,finalEnergy:a.finalEnergy},rest:{meanIntegrity:b.meanIntegrity,aliveTicks:b.aliveTicks,reserveTicks:b.reserveTicks,finalEnergy:b.finalEnergy}});
   if(seed===601)examples.push({capacity,scenario,graded:a,rest:{...b,trace:undefined},conditional:{...runs.conditional,trace:undefined},reserve:{...runs.reserve,trace:undefined}});
  }
  rows.push({capacity,scenario,average:Object.fromEntries(modes.map(m=>[m,Object.fromEntries(Object.entries(sums[m]).map(([k,v])=>[k,+(v/seeds.length).toFixed(6)]))]))});
 }
 return {bound:"WAG-230",seeds,capacities,scenarios,modes,policyRuns,ticks:policyRuns*240,gradedVsRest:{wins,losses,ties},rows,counterexamples,examples};
}

function simulate231(capacity,scenario,seed,mode="forecast"){
 if(mode!=="forecast")return simulate230(capacity,scenario,seed,mode);
 const random=rng(seed),phase=random()*Math.PI*2,trace=[],history=[];
 let energy=.78,integrity=.91,ceiling=1,stress=0,protection=0,transitions=0,meanIntegrity=0,aliveTicks=0,reserveTicks=0,defenseTicks=0,recoveryTicks=0,protectionSum=0,spentSwitch=0;
 let prevBand="REST",previousPressure=0;
 const energyDeltas=[],pendingForecasts=[];let predictionCount=0,squaredError=0,bias=0,covered=0,guardTicks=0;
 let lastEnergy=energy;
 const capShield=capacity>=13?.64:capacity>=8?.46:.22;
 for(let t=0;t<240;t++){
  const pressure=environment(t,scenario,phase).pressure;
  const observed=clip(pressure+(random()-.5)*.09);
  history.push(observed);
  const recent=history.slice(-8),average=recent.reduce((a,b)=>a+b,0)/recent.length;
  const variance=recent.reduce((a,b)=>a+(b-average)**2,0)/recent.length;
  const jump=Math.abs(observed-(history.at(-2)??observed));
  const memory=jump>.16||variance>.035?3:variance<.006?Math.min(21,capacity):8;
  const h=history.slice(-memory);const smoothed=h.reduce((a,b)=>a+b,0)/h.length;
  stress=clip(.75*stress+.25*smoothed);
  // Only observable values may influence the control decision.
  const danger=clip(.64*observed+.36*stress+Math.max(0,observed-previousPressure)*.30);
  const urgency=clip((danger-.27)/.62);
  const fragility=clip((.78-integrity)/.60);
  const reserve=clip((.43-energy)/.43);
  const irrecoverableRisk=clip((.96-ceiling)*2.0);
  // Predict the energy budget from trailing observed energy changes, never future inputs.
  const tail=energyDeltas.slice(-8);
  const rate=tail.length?tail.reduce((a,b)=>a+b,0)/tail.length:0;
  const forecast=clip(energy+12*rate);
  pendingForecasts.push({due:t+12,predicted:forecast,issued:t});
  const shortfall=clip((.36-forecast)/.36);
  let desired=capShield*clip(.06+.83*urgency+.22*fragility+.12*irrecoverableRisk-.30*reserve*(1-urgency));
  if(shortfall>.05&&urgency<.72){desired*=1-.45*shortfall*(1-urgency);guardTicks++}
  // Do not abandon critical protection just because energy is low.
  const emergency=danger>.79||integrity<.32;
  const target=emergency?Math.max(desired,capShield*.65):desired;
  const step=emergency?.22:.095;
  const next=clip(Math.max(protection-step,Math.min(protection+step,target)));
  const delta=Math.abs(next-protection);
  const scarcity=scenario==="famine"||scenario==="combined";
  const friction=scenario==="friction"||scenario==="combined";
  const switchFee=(friction?.003+(.020*(1-energy))**2:.003)+(integrity<.55?.007:0);
  // Graded protection has an explicit convex running cost and proportional modulation cost.
  const runCost=.0015+.029*Math.pow(next/.64,1.7);
  const modulationCost=switchFee*delta/.64;
  spentSwitch+=modulationCost;
  protection=next;
  const band=protection<.12?"REST":protection<.40?"GUARD":"DEFEND";
  if(band!==prevBand)transitions++;
  prevBand=band;if(band==="DEFEND")defenseTicks++;if(band==="REST")recoveryTicks++;
  const raw=pressure*(1-protection);
  const generation=(.016+.0005*Math.min(capacity,13)-.012*pressure)*(scarcity?(t>=62?.24:.75):1);
  const damage=Math.max(0,raw-.31)*.034+(energy<.14?.012:0);
  const repairBase=capacity>=21?.020:capacity>=13?.015:capacity>=8?.012:.009;
  const repair=Math.min(Math.max(0,ceiling-integrity),repairBase*Math.max(.22,energy)*(scarcity?.42:1));
  const scarFraction=(scenario==="scar"||scenario==="combined")?.26:0;
  ceiling=clip(ceiling-damage*scarFraction);
  energy=clip(energy+generation-runCost-.011*raw-repair*.35-modulationCost);
  integrity=Math.min(ceiling,clip(integrity-damage+repair));
  energyDeltas.push(energy-lastEnergy);lastEnergy=energy;
  for(const forecastEntry of pendingForecasts){
   if(forecastEntry.due===t){const err=energy-forecastEntry.predicted;predictionCount++;squaredError+=err*err;bias+=err;if(Math.abs(err)<=.10)covered++}
  }
  const alive=integrity>.15&&energy>.08;
  if(alive)aliveTicks++;if(energy>.25&&integrity>.30)reserveTicks++;
  meanIntegrity+=integrity/240;protectionSum+=protection/240;
  trace.push({t,pressure:+pressure.toFixed(4),observed:+observed.toFixed(4),energy:+energy.toFixed(4),integrity:+integrity.toFixed(4),ceiling:+ceiling.toFixed(4),protection:+protection.toFixed(4),action:band,emergency,forecast:+forecast.toFixed(4),shortfall:+shortfall.toFixed(4),alive});
  previousPressure=observed;
  if(energy<0||energy>1||integrity<0||integrity>ceiling+1e-10||protection<0||protection>capShield+1e-10)throw Error("state bounds");
 }
 return {capacity,scenario,seed,mode,meanIntegrity:+meanIntegrity.toFixed(6),finalEnergy:+energy.toFixed(6),finalIntegrity:+integrity.toFixed(6),recoverableCeiling:+ceiling.toFixed(6),aliveTicks,reserveTicks,transitions,defenseTicks,recoveryTicks,meanProtection:+protectionSum.toFixed(6),spentSwitch:+spentSwitch.toFixed(6),forecastRMSE:+Math.sqrt(squaredError/Math.max(1,predictionCount)).toFixed(6),forecastBias:+(bias/Math.max(1,predictionCount)).toFixed(6),forecastCoverage10:+(covered/Math.max(1,predictionCount)).toFixed(6),predictionCount,guardTicks,trace};
}

function experiment231(){
 const seeds=[701,702,703,704,705,706,707,708],capacities=[5,8,13,21],scenarios=["chirp","scar","famine","friction","combined"],modes=["forecast","graded","rest","reserve"];
 const rows=[],examples=[],counterexamples=[];let wins=0,losses=0,ties=0,policyRuns=0;
 let totalSquared=0,totalCount=0,totalBias=0,totalCovered=0;
 for(const capacity of capacities)for(const scenario of scenarios){
  const totals=Object.fromEntries(modes.map(m=>[m,{meanIntegrity:0,finalEnergy:0,aliveTicks:0,reserveTicks:0}]));
  for(const seed of seeds){
   const runs=Object.fromEntries(modes.map(m=>[m,simulate231(capacity,scenario,seed,m)]));
   policyRuns+=modes.length;
   for(const m of modes)for(const key of Object.keys(totals[m]))totals[m][key]+=runs[m][key];
   const a=runs.forecast,b=runs.graded,d=a.meanIntegrity-b.meanIntegrity;
   if(d>1e-6)wins++;else if(d< -1e-6)losses++;else ties++;
   if(d< -1e-6||a.aliveTicks<b.aliveTicks||a.reserveTicks<b.reserveTicks)counterexamples.push({capacity,scenario,seed,forecast:{meanIntegrity:a.meanIntegrity,finalEnergy:a.finalEnergy,aliveTicks:a.aliveTicks,reserveTicks:a.reserveTicks},graded:{meanIntegrity:b.meanIntegrity,finalEnergy:b.finalEnergy,aliveTicks:b.aliveTicks,reserveTicks:b.reserveTicks}});
   // Each forecast outcome is checked only after the forecast horizon elapsed.
   totalCount+=a.predictionCount;totalSquared+=a.forecastRMSE*a.forecastRMSE*a.predictionCount;totalBias+=a.forecastBias*a.predictionCount;totalCovered+=a.forecastCoverage10*a.predictionCount;
   if(seed===701)examples.push({capacity,scenario,forecast:a,graded:{...b,trace:undefined},rest:{...runs.rest,trace:undefined},reserve:{...runs.reserve,trace:undefined}});
  }
  rows.push({capacity,scenario,average:Object.fromEntries(modes.map(m=>[m,Object.fromEntries(Object.entries(totals[m]).map(([k,v])=>[k,+(v/8).toFixed(6)]))]))});
 }
 return {bound:"WAG-231",seeds,capacities,scenarios,modes,policyRuns,ticks:policyRuns*240,forecastVsGraded:{wins,losses,ties},forecastCalibration:{n:totalCount,rmse:+Math.sqrt(totalSquared/totalCount).toFixed(5),bias:+(totalBias/totalCount).toFixed(5),withinPointOne:+(totalCovered/totalCount).toFixed(5)},rows,counterexamples,examples};
}
if(typeof module!=="undefined")module.exports={simulate231,experiment231};
if(typeof require!=="undefined"&&require.main===module)console.log(JSON.stringify(experiment231(),null,2));
