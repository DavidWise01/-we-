/* WAG-278 · Minimal observable counterexample prefixes (not causal proof).
  Preserve WAG277 hidden seeds and frozen weights. No controller updates.
  For each selected failure, find earliest tick at which a predeclared
  deterministic property is observed. Prefix includes initial state and
  all original forcing; no synthetic shortened-horizon run or hindsight
  action substitution. One duplicate full replay verifies exact prefix.
*/
const WAG278_THRESHOLD=.02;
const WAG278_MAX_CASES=10;
function wag278IsViable(z){return z.energy>.08&&z.integrity>.15}
function wag278FirstDifference(f,c,type,threshold=WAG278_THRESHOLD){
 if(f.trace.length!==c.trace.length)throw Error('unmatched traces');
 for(let t=0;t<f.trace.length;t++){
  const a=f.trace[t],b=c.trace[t];
  if(type==='survival-loss'&&wag278IsViable(a)&&!wag278IsViable(b))return t;
  if(type==='integrity-gap'&&a.integrity-b.integrity>=threshold)return t;
  if(type==='chain-gap'&&a.integrity-b.integrity>=threshold)return t;
 }
 return -1;
}
function wag278FirstActionDiff(a,b,stop){
 for(let t=0;t<=stop;t++)if(a.trace[t].action!==b.trace[t].action)return t;
 return -1;
}
function wag278Extract(caseId,kind,frozen,models,horizon){
 const {duration,family,force,cap,seed}=caseId;
 const leftMode=kind==='chain-gap'?'crystal':'frozen';
 const rightMode=kind==='chain-gap'?'chain':'crystal';
 const args=[cap,family,seed,duration,force];
 const left=wag277Run(...args,leftMode,frozen,models,horizon);
 const right=wag277Run(...args,rightMode,frozen,models,horizon);
 const stop=wag278FirstDifference(left,right,kind);
 if(stop<0)throw Error('unreproduced counterexample '+JSON.stringify(caseId));
 const firstAction=wag278FirstActionDiff(left,right,stop);
 const initialViolation=wag278FirstDifference(left,right,kind,kind==='survival-loss'?undefined:WAG278_THRESHOLD);
 if(initialViolation!==stop)throw Error('failed shortest-prefix proof');
 const repeatLeft=wag277Run(...args,leftMode,frozen,models,horizon);
 const repeatRight=wag277Run(...args,rightMode,frozen,models,horizon);
 if(JSON.stringify(left.trace.slice(0,stop+1))!==
    JSON.stringify(repeatLeft.trace.slice(0,stop+1))||
    JSON.stringify(right.trace.slice(0,stop+1))!==
    JSON.stringify(repeatRight.trace.slice(0,stop+1)))throw Error('nondeterministic replay');
 const lo=Math.max(0,stop-8),hi=Math.min(duration-1,stop+4);
 const window=Array.from({length:hi-lo+1},(_,i)=>{
  const t=lo+i,a=left.trace[t],b=right.trace[t];
  return {tick:t,integrityLeft:a.integrity,integrityRight:b.integrity,
   energyLeft:a.energy,energyRight:b.energy,
   materialLeft:a.material,materialRight:b.material,
   actionLeft:a.action,actionRight:b.action,
   gap:a.integrity-b.integrity,
   viableLeft:wag278IsViable(a),viableRight:wag278IsViable(b)};
 });
 return {case:caseId,kind,leftMode,rightMode,
  minimalObservablePrefixTicks:stop+1,firstFailureTick:stop,
  earliestActionDisagreementTick:firstAction,
  secondsBeforeFirstFailure:firstAction>=0?stop-firstAction:null,
  decisiveState:window.find(z=>z.tick===stop),
  window,reproduction:{duplicateFullReplay:true,
   noEarlierObservedViolation:true,threshold:kind==='survival-loss'?null:WAG278_THRESHOLD,
   fullOriginalDuration:duration,forcingUnchanged:true},
  maxAccountingResidual:Math.max(left.error,right.error)};
}
function wag278Experiment(frozen,models,horizon,previous){
 wag264VerifyFreeze(frozen);
 if(previous?.bound!=='WAG-277'||previous.summary.matchedConditions!==128)
  throw Error('WAG277 immutable evidence required');
 const cases=previous.cases.slice();
 const survival=cases.filter(z=>z.crystalAliveDelta<0)
  .sort((a,b)=>a.crystalAliveDelta-b.crystalAliveDelta).slice(0,2)
  .map(z=>({id:z,kind:'survival-loss'}));
 const integrity=cases.filter(z=>z.crystalIntegrityDelta< -WAG278_THRESHOLD)
  .sort((a,b)=>a.crystalIntegrityDelta-b.crystalIntegrityDelta)
  .filter(z=>!survival.some(y=>sameCase(y.id,z))).slice(0,6)
  .map(z=>({id:z,kind:'integrity-gap'}));
 const chain=cases.filter(z=>z.chainIntegrityDelta< -WAG278_THRESHOLD)
  .sort((a,b)=>a.chainIntegrityDelta-b.chainIntegrityDelta).slice(0,2)
  .map(z=>({id:z,kind:'chain-gap'}));
 const wanted=[...survival,...integrity,...chain].slice(0,WAG278_MAX_CASES);
 const examples=wanted.map(z=>wag278Extract(z.id,z.kind,frozen,models,horizon));
 return {bound:'WAG-278',phase:'WAG-III',turn:10,
  primitive:'---@---@---@---@---{}',threshold:WAG278_THRESHOLD,
  casesScanned:cases.length,examples,
  summary:{selected:examples.length,
   survivalLoss:examples.filter(z=>z.kind==='survival-loss').length,
   integrityGap:examples.filter(z=>z.kind==='integrity-gap').length,
   chainGap:examples.filter(z=>z.kind==='chain-gap').length,
   shortestPrefixVerified:examples.every(z=>z.reproduction.noEarlierObservedViolation),
   exactReplayVerified:examples.every(z=>z.reproduction.duplicateFullReplay),
   maxAccountingResidual:Math.max(...examples.map(z=>z.maxAccountingResidual))},
  limitations:[
   'Minimal observable prefix means earliest property crossing, NOT a minimized independent causal input',
   'Original duration remains 480/720 because the underlying forcing and controller initialization depend on duration',
   'First differing action precedes the observed failure, but is not established as its isolated cause',
   'All examples are selected from the same held-out evidence; no retuning and no candidate promotion'
  ]};
}
function sameCase(a,b){return a.duration===b.duration&&a.family===b.family&&
 a.force===b.force&&a.cap===b.cap&&a.seed===b.seed}
if(typeof module!=='undefined')module.exports={
 wag278IsViable,wag278FirstDifference,wag278Extract,wag278Experiment};
