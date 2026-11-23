/* WAG-310 · Signed truth-claim separation · Phase VI 7/8 · .dlw
  Three private interpreters do not receive peer claims or reference labels.
  An EXTERNAL gate compares three Ed25519-verified signed packets against
  separately generated (but unauthenticated) synthetic reference records.
  Correctly signed false data can be vetoed when reference is correct.
  Corrupted reference can cause a false acceptance. No actual truth oracle.
*/
const WAG310=Object.freeze({phase:'VI',turn:7,totalTurns:8,
 scenarios:Object.freeze(['clean','signed-false-correct-reference',
 'signed-false-corrupt-reference','clean-wrong-reference',
 'missing-reference','tampered-vector','sequence-replay']),
 referenceSource:'synthetic-reference-fixture-D',physicalActions:0});
function wag310Reference(scenario,seq){
 if(scenario==='missing-reference')return Object.freeze({available:false,origin:WAG310.referenceSource,seq});
 const truth=scenario.startsWith('signed-false')?4:3;
 const channel=scenario==='signed-false-corrupt-reference'?3:
  scenario==='clean-wrong-reference'?4:truth;
 return Object.freeze({available:true,origin:WAG310.referenceSource,seq,
  channel,claimedIndependence:'SEPARATELY_GENERATED_FIXTURE',
  authenticated:false});
}
function wag310Decision(trial,reference){
 const signed=trial.trusted,unanimous=trial.unanimous;
 const present=reference.available&&Number.isInteger(reference.channel);
 const matching=signed&&unanimous&&present&&trial.candidate===reference.channel;
 const accepted=matching;
 return Object.freeze({
  candidate:accepted?trial.candidate:null,
  verdict:!signed?'SIGNED_OBSERVATION_REJECTED':!unanimous?'PRIVATE_DISAGREEMENT':
   !present?'REFERENCE_MISSING':matching?'SYNTHETIC_REFERENCE_AGREEMENT':'REFERENCE_DISAGREEMENT',
  referenceMatches:matching,
  referenceAuthenticated:false,observationSignatureVerified:signed,
  independentRealWorldEvidence:false,promotionAuthorized:false});
}
async function wag310Trial(scenario,seq){
 const originalScenario=scenario==='tampered-vector'?'vector-tamper':
  scenario==='sequence-replay'?'sequence-replay':
  scenario.startsWith('signed-false')?'signed-false-observation':'clean';
 const observed=await wag309Trial(originalScenario,seq);
 const reference=wag310Reference(scenario,seq);
 const decision=wag310Decision(observed,reference);
 const syntheticTruth=originalScenario==='signed-false-observation'?4:3;
 return {scenario,seq,decision,reference,observed,syntheticTruth};
}
async function wag310Evaluate(authority){
 const before=JSON.stringify(authority),rows=[];
 for(const scenario of WAG310.scenarios){
  let correct=0,wrong=0,abstain=0,signedAccepted=0,referenceDisagreement=0;
  for(let seq=0;seq<8;seq++){
   const t=await wag310Trial(scenario,seq);
   if(t.observed.trusted)signedAccepted++;
   if(t.decision.verdict==='REFERENCE_DISAGREEMENT')referenceDisagreement++;
   const answer=t.decision.candidate;
   if(answer===null)abstain++;else if(answer===t.syntheticTruth)correct++;else wrong++;
  }
  rows.push({scenario,correct,wrong,abstain,signedAccepted,referenceDisagreement,total:8});
 }
 if(JSON.stringify(authority)!==before)throw Error('authoritative source mutated');
 return wag291DeepFreeze({bound:'WAG-310',phase:'VI',turn:7,rows,total:56,
  evidenceClass:'synthetic generated observations and separately generated unsigned reference',
  limitation:'False reference can agree with signed false data; independent generation is not authenticated truth',
  promotionAuthorized:false,physicalActions:0});
}
async function wag310Audit(){
 const s=wag288Initial(),before=JSON.stringify(s),a=await wag310Evaluate(s),b=await wag310Evaluate(s);
 const row=x=>a.rows.find(y=>y.scenario===x),checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  readOnly:JSON.stringify(s)===before,
  sevenCases:a.rows.length===7&&a.total===56,
  completeAccounting:a.rows.every(r=>r.correct+r.wrong+r.abstain===8),
  cleanAccepted:row('clean').correct===8,
  signedFalseRejected:row('signed-false-correct-reference').abstain===8,
  falseReferenceFailurePreserved:row('signed-false-corrupt-reference').wrong===8,
  cleanAgainstWrongReferenceAbstains:row('clean-wrong-reference').abstain===8,
  missingReferenceAbstains:row('missing-reference').abstain===8,
  tamperStillRejected:row('tampered-vector').abstain===8,
  replayStillRejected:row('sequence-replay').abstain===8,
  signatureNotTruth:row('signed-false-correct-reference').signedAccepted===8,
  independentFixtureNotAuthenticated:wag310Reference('clean',0).authenticated===false,
  noPromotion:a.promotionAuthorized===false,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  threePrivateForms:WAG304.forms.join('|')==='[1]|{1}|(1)',
  noActuation:a.physicalActions===0
 };
 return {bound:'WAG-310',pass:Object.values(checks).every(Boolean),checks,
  rows:a.rows,phaseProgress:7/8};
}
if(typeof module!=='undefined')module.exports={WAG310,wag310Reference,wag310Decision,wag310Trial,wag310Evaluate,wag310Audit};
