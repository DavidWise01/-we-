/* WAG-311 · Phase VI closure and admission gate · .dlw
 * Research closure is NOT authority promotion. Pin requirements BEFORE tests.
 * Signed content integrity, context, reference availability, and truth are
 * different claims. An unsigned synthetic reference cannot establish truth.
 * 3 private forms remain blind, same frontend geometry and 125 silos.
 * Retain both signed-false and signed-false + wrong-reference counterexamples.
 */
const WAG311=Object.freeze({phase:'VI',turn:8,of:8,next:'VII',
  requirements:Object.freeze({
    cleanMinimum:1,
    tamperingWrongMaximum:0,
    replayWrongMaximum:0,
    signedFalseWrongMaximum:0,
    referenceFalseWrongMaximum:0,
    realOriginAuthenticationRequired:true,
    referenceAuthenticationRequired:true
  }),
  physicalActions:0,mode:'OBSERVE_ONLY'});
async function wag311Close(state){
 const baseline=JSON.stringify(state);
 const signed=await wag309Evaluate(state),reference=await wag310Evaluate(state);
 const pick=(rows,key)=>rows.find(r=>r.scenario===key);
 const check={
  cleanSignedObservation:pick(signed.rows,'clean').correct/signed.rows[0].total>=WAG311.requirements.cleanMinimum,
  tamperBlocked:pick(signed.rows,'vector-tamper').wrong<=WAG311.requirements.tamperingWrongMaximum,
  replayBlocked:pick(signed.rows,'sequence-replay').wrong<=WAG311.requirements.replayWrongMaximum,
  signedFalseBlocked:pick(signed.rows,'signed-false-observation').wrong<=WAG311.requirements.signedFalseWrongMaximum,
  referenceFalseBlocked:pick(reference.rows,'signed-false-corrupt-reference').wrong<=WAG311.requirements.referenceFalseWrongMaximum,
  externalOriginAuthenticated:signed.realWorldOriginAuthenticated===true,
  referenceAuthenticated:wag310Reference('clean',0).authenticated===true,
  blindInterpreterCount:WAG304.forms.length===3,
  stateUntouched:JSON.stringify(state)===baseline
 };
 const approved=Object.values(check).every(Boolean);
 const record=wag291DeepFreeze({
  bound:'WAG-311',phase:'VI',turn:'8/8',phaseResearchComplete:true,
  admission:approved?'PASS':'WITHHELD',controllerPromotion:false,
  gateRequirements:WAG311.requirements,checks:check,
  evidence:{
    signedObservationCases:signed.tests,
    referenceCases:reference.total,
    signatureMismatchAbstentions:pick(signed.rows,'vector-tamper').abstain,
    replayAbstentions:pick(signed.rows,'sequence-replay').abstain,
    signedFalseWrong:pick(signed.rows,'signed-false-observation').wrong,
    falseReferenceWrong:pick(reference.rows,'signed-false-corrupt-reference').wrong
  },
  lineage:'3 signed fixture roots do not authenticate real-world independence',
  limitations:'Cryptographic fixture signatures are valid, but neither signer identity nor reference truth is independently attested. A validly signed false observation can agree with a false reference.',
  nextPhase:{id:'VII',name:'Reference Adversaries and Open-World Abstention',
    first:'WAG-312 · Untrusted Reference Challenge',totalSteps:8},
  physicalActions:0
 });
 if(JSON.stringify(state)!==baseline)throw Error('authoritative memory modified');
 return record;
}
async function wag311Audit(){
 const s=wag288Initial(),before=JSON.stringify(s),a=await wag311Close(s),b=await wag311Close(s);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  sourceUnchanged:JSON.stringify(s)===before,
  allEightMilestones:a.turn==='8/8'&&a.phaseResearchComplete,
  admissionWithheld:a.admission==='WITHHELD',
  noControllerPromotion:!a.controllerPromotion,
  signatureTamperHandled:a.checks.tamperBlocked,
  replayHandled:a.checks.replayBlocked,
  signedFalseRetained:a.evidence.signedFalseWrong===8,
  correlatedReferenceFailureRetained:a.evidence.falseReferenceWrong===8,
  signedFalseRequirementFailed:!a.checks.signedFalseBlocked,
  falseReferenceRequirementFailed:!a.checks.referenceFalseBlocked,
  noRealWorldAuth:!a.checks.externalOriginAuthenticated,
  referenceNotAuthenticated:!a.checks.referenceAuthenticated,
  intactTopology:wag289Groups().frontal.length===1&&WAG304.forms.join('|')==='[1]|{1}|(1)',
  exactTestCounts:a.evidence.signedObservationCases===72&&a.evidence.referenceCases===56,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.evidence)&&Object.isFrozen(a.gateRequirements),
  nextPhaseDefined:a.nextPhase.id==='VII',
  noActuation:a.physicalActions===0
 };
 return {bound:'WAG-311',pass:Object.values(checks).every(Boolean),checks,
  decision:a.admission,phaseProgress:1,record:a};
}
if(typeof module!=='undefined')module.exports={WAG311,wag311Close,wag311Audit};
