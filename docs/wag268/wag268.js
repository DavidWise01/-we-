/* WAG-268 · Phase II deterministic closeout / immutable release audit · .dlw
   Zero new policy training. No retroactive policy tuning.
   FNV-1a checks below are non-cryptographic replay checksums, not signatures.
   GitHub content SHA values are recorded in release manifest separately.
*/
const WAG268_SEEDS=[5501,5502,5503,5504];
const WAG268_MODES=['frozen','rejectedAdaptive','noRepair'];
const WAG268_EXPECTED={matchedScenarios:256,policyRuns:768,frozenFailures:43,
 rankOrder:['noRepair','rejectedAdaptive','frozen'],
 fullSurvival:[218,214,213],counterexamples:4,originalFailures:43};
function wag268Digest(value){
 const s=JSON.stringify(value);let h=2166136261;
 for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}
 return (h>>>0).toString(16).padStart(8,'0');
}
function wag268AssertFreeze(f){
 wag264VerifyFreeze(f);
 for(const c of CAP234)if(f.policy[c]!=='baseline')throw Error('Frozen controller unexpectedly changed for cap '+c);
 return true;
}
function wag268AuditReceipt(release,receipts){
 if(!release||release.bound!=='WAG-268')throw Error('Invalid WAG268 release');
 if(!receipts||!receipts.wag266||!receipts.wag267)throw Error('Missing source receipt');
 const a=receipts.wag266,b=receipts.wag267;
 if(a.summary.failures!==43||!a.summary.allReproduced||a.representativeMinima.length!==4)
  throw Error('Failure archive incomplete');
 if(b.summary.policyRuns!==768||b.summary.frozenFailures!==43)throw Error('Ranking archive incomplete');
 const rank=b.ranking.map(z=>z.mode);
 if(JSON.stringify(rank)!==JSON.stringify(WAG268_EXPECTED.rankOrder))
  throw Error('Ranking changed from frozen receipt');
 if(JSON.stringify(b.ranking.map(z=>z.fullSurvival))!==JSON.stringify(WAG268_EXPECTED.fullSurvival))
  throw Error('Survival counts changed');
 if(release.finalState!=='CLOSED'||
    release.phaseProgressPercent!==100||release.completedTurns!==12)
  throw Error('Release not closed');
 return {accepted:true,archivedFailures:a.summary.failures,
  minimized:a.representativeMinima.length,ranking:rank};
}
function wag268Replay(frozen,models,horizon,receipt266,receipt267){
 wag268AssertFreeze(frozen);
 const cases=[
  {cap:13,family:'combined',seed:5501,stress:'late-collapse'},
  {cap:13,family:'combined',seed:5501,stress:'double-shock'},
  {cap:5,family:'combined',seed:5502,stress:'intermittent'},
  {cap:21,family:'scar',seed:5504,stress:'resource-squeeze'}
 ];
 const samples=[];
 for(const p of cases){
  const same=()=>WAG268_MODES.map(mode=>{
   const r=wag267Run(p.cap,p.family,p.seed,240,p.stress,mode,frozen,models,horizon);
   return {mode,alive:r.aliveTicks,reserve:r.reserveTicks,
    meanIntegrity:+r.meanIntegrity.toFixed(12),
    finalEnergy:+r.finalEnergy.toFixed(12),
    finalMaterial:+r.finalMaterial.toFixed(12),
    traceDigest:wag268Digest(r.trace.map(z=>[z.energy,z.integrity,z.material]))};
  });
  const one=same(),two=same(),equal=JSON.stringify(one)===JSON.stringify(two);
  if(!equal)throw Error('Nondeterministic paired replay '+JSON.stringify(p));
  samples.push({case:p,pass:equal,digest:wag268Digest(one),runs:one});
 }
 const reduced=receipt266.representativeMinima.map(z=>{
  const k=z.case;
  const r=wag266Run(k.cap,k.family,k.seed,k.stress,z.minimized.eventsSchedule,
    frozen,models,horizon);
  if(!r.failed||r.aliveTicks!==z.minimized.alive)throw Error('Minimized replay changed '+k.stress);
  return {stress:k.stress,cap:k.cap,family:k.family,seed:k.seed,
   pass:true,alive:r.aliveTicks,originalAlive:z.original.alive,
   events:z.minimized.events,traceDigest:wag268Digest(r.trace.map(v=>[v.energy,v.integrity,v.material]))};
 });
 const summary=receipt267.summary;
 if(summary.frozenFailures!==WAG268_EXPECTED.frozenFailures||
    summary.policyRuns!==WAG268_EXPECTED.policyRuns)throw Error('Scorecard changed');
 return {bound:'WAG-268',phase:'WAG-II',policyFrozen:true,
  deterministicSamples:samples,originalFailureCount:receipt266.failingCases.length,
  minimizedReplays:reduced,passed:samples.every(z=>z.pass)&&reduced.every(z=>z.pass),
  totalReplayRuns:samples.length*2*WAG268_MODES.length+reduced.length,
  warning:'Determinism sampled on four fixed cases; no proof of all possible runs. One synthetic model ancestry.'};
}
if(typeof module!=='undefined')module.exports={wag268Digest,wag268AssertFreeze,wag268AuditReceipt,wag268Replay};
