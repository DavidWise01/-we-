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
function experiment225(){
 let runs=0,slots=0,adaptiveWins=0,fixedWins=0,ties=0,modeChanges=0;const cases=[],examples=[],counterexamples=[];
 const scenarios=['stable','shock','oscillating','drift','recovery','default'];
 for(const capacity of W225_CAPACITIES)for(const scenario of scenarios){
  let adaptiveSum=0,fixedSum=0,improvements=0,regressions=0,differentActions=0;
  for(let seed=225;seed<233;seed++){
   const a=simulate225(capacity,scenario,seed,true),b=simulate225(capacity,scenario,seed,false);
   runs+=2;slots+=480;adaptiveSum+=a.meanIntegrity;fixedSum+=b.meanIntegrity;
   if(a.meanIntegrity>b.meanIntegrity+1e-6){adaptiveWins++;improvements++}
   else if(b.meanIntegrity>a.meanIntegrity+1e-6){fixedWins++;regressions++}else ties++;
   if(JSON.stringify(a.actions)!==JSON.stringify(b.actions))differentActions++;
   modeChanges+=a.trajectory.filter((v,i)=>i>0&&v.memory!==a.trajectory[i-1].memory).length;
   if(seed===225)examples.push({capacity,scenario,adaptive:a,fixed:{...b,trajectory:undefined}});
   if(b.meanIntegrity>a.meanIntegrity+.015&&counterexamples.length<18)counterexamples.push({capacity,scenario,seed,adaptiveMeanIntegrity:a.meanIntegrity,fixedMeanIntegrity:b.meanIntegrity,adaptiveActions:a.actions,fixedActions:b.actions});
   if(a.trajectory.some(x=>x.energy<0||x.energy>1||x.integrity<0||x.integrity>1))throw Error('bounds');
   if(capacity<13&&(a.actions.FIGHT||a.actions.FLIGHT))throw Error('premature agency');
  }
  cases.push({capacity,scenario,runs:8,adaptiveMeanIntegrity:+(adaptiveSum/8).toFixed(4),fixedMeanIntegrity:+(fixedSum/8).toFixed(4),improvements,regressions,differentActions});
 }
 return {runs,slots,adaptiveWins,fixedWins,ties,modeChanges,cases,examples,counterexamples};
}
if(typeof module!=='undefined')module.exports={simulate225,experiment225};
if(typeof require!=='undefined'&&require.main===module)console.log(JSON.stringify(experiment225(),null,2));
