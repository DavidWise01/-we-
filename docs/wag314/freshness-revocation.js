/* WAG-314 · Phase VII 3/8 · Freshness + revocation boundary · .dlw
 * External policy only. [1] {1} (1) know neither references nor one another.
 * Test-time monotonic ticks are simulated; NOT a secure external clock.
 * Revocation ledger is a separately pinned simulated checkpoint; NOT signed.
 * Reported key compromise can be rejected; undisclosed compromise cannot.
 * A signature never establishes observation truth, and no actuation occurs.
 */
const WAG314=Object.freeze({phase:'VII',turn:3,of:8,epoch:313,
 expiryTicks:4,pinnedRevocationVersion:7,physicalActions:0,
 cases:Object.freeze(['clean','deadline-edge','late-response','future-response',
 'reported-revocation','revoked-after-observation','status-rollback',
 'missing-status','unreported-compromise','reported-compromise',
 'correlated-false-reference','nonce-replay'])});
function wag314Policy(kind,seq){
 const issued=seq*10+1000;
 const received=issued+(kind==='late-response'?5:kind==='deadline-edge'?4:
   kind==='future-response'?-1:2);
 const referenceTime=issued+2;
 const knownRevoked=['reported-revocation','reported-compromise','revoked-after-observation'].includes(kind);
 return Object.freeze({
  issued,received,referenceTime,
  statusVersion:kind==='status-rollback'?6:7,
  statusAvailable:kind!=='missing-status',
  keyStatus:knownRevoked?'REVOKED':'ACTIVE',
  revokedAt:kind==='revoked-after-observation'?issued+3:issued-1,
  referenceKeyLabel:'fixture-D',
  reportedCompromise:['reported-compromise','reported-revocation'].includes(kind)
 });
}
function wag314Gate(referenceResult,policy,expectedSeq){
 const base=referenceResult.reference;
 const challengeOK=base.valid&&referenceResult.observedSigned;
 const freshness=policy.received>=policy.issued&&
  policy.received-policy.issued<=WAG314.expiryTicks;
 const checkpointOK=policy.statusAvailable&&policy.statusVersion>=WAG314.pinnedRevocationVersion;
 // Policy is evaluated at receipt time; revocation known by then blocks use.
 const keyActive=policy.keyStatus==='ACTIVE'||policy.revokedAt>policy.received;
 const eligible=challengeOK&&freshness&&checkpointOK&&keyActive;
 const candidate=eligible&&referenceResult.candidate!==null?referenceResult.candidate:null;
 return Object.freeze({
  candidate,verdict:!challengeOK?'SIGNED_CHALLENGE_REJECTED':
   !freshness?'EXPIRED_OR_FUTURE_RESPONSE':
   !checkpointOK?'REVOCATION_CHECKPOINT_UNTRUSTED':
   !keyActive?'REVOKED_KEY':
   referenceResult.candidate===null?'REFERENCE_CONFLICT':'SYNTHETIC_SIGNED_AGREEMENT',
  freshness,checkpointOK,keyActive,signatureValid:base.signatureOK,
  statusVersion:policy.statusVersion,deadline:policy.issued+WAG314.expiryTicks,
  policyClockAttested:false,statusLedgerAuthenticated:false,
  realWorldKeyControlVerified:false,truthVerified:false,promotionAuthorized:false
 });
}
async function wag314Trial(kind,seq){
 const referenceKind=kind==='nonce-replay'?'nonce-replay':
  kind==='correlated-false-reference'||kind==='unreported-compromise'?'correlated-signed-false':'clean';
 const original=await wag313Trial(referenceKind,seq);
 const policy=wag314Policy(kind,seq);
 const decision=wag314Gate(original,policy,seq);
 return Object.freeze({kind,seq,policy,referenceResult:original,decision,
  target:['correlated-false-reference','unreported-compromise'].includes(kind)?4:3});
}
async function wag314Evaluate(authority){
 const before=JSON.stringify(authority),rows=[];
 for(const kind of WAG314.cases){
  let correct=0,wrong=0,abstain=0,signatureAccepted=0,policyRejected=0;
  for(let seq=0;seq<8;seq++){
   const x=await wag314Trial(kind,seq),v=x.decision;
   if(v.signatureValid)signatureAccepted++;
   if(!v.freshness||!v.checkpointOK||!v.keyActive)policyRejected++;
   if(v.candidate===null)abstain++;
   else if(v.candidate===x.target)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,signatureAccepted,policyRejected,total:8});
 }
 if(JSON.stringify(authority)!==before)throw Error('authoritative memory mutated');
 return wag291DeepFreeze({bound:'WAG-314',phase:'VII',turn:3,rows,testCases:96,
  clockAuthenticated:false,revocationStatusAuthenticated:false,
  cryptographicReferenceVerification:true,controllerPromoted:false,physicalActions:0,
  limitation:'Unreported key compromise and correlated false claims can produce accepted wrong decisions. Simulated policy clock and revocation status lack external attestation.'});
}
async function wag314Audit(){
 const source=wag288Initial(),before=JSON.stringify(source),
  a=await wag314Evaluate(source),b=await wag314Evaluate(source),get=k=>a.rows.find(r=>r.kind===k);
 const checks={
  repeatable:JSON.stringify(a)===JSON.stringify(b),
  sourceUnchanged:JSON.stringify(source)===before,
  twelveCases:a.rows.length===12&&a.testCases===96,
  completeAccounting:a.rows.every(r=>r.correct+r.wrong+r.abstain===8),
  cleanPasses:get('clean').correct===8,
  deadlineEdgeAccepted:get('deadline-edge').correct===8,
  lateWithheld:get('late-response').abstain===8,
  futureWithheld:get('future-response').abstain===8,
  revokedWithheld:get('reported-revocation').abstain===8,
  revokedAfterReceivedWithheld:get('revoked-after-observation').abstain===8,
  statusRollbackWithheld:get('status-rollback').abstain===8,
  missingStatusWithheld:get('missing-status').abstain===8,
  undisclosedCompromiseCounterexample:get('unreported-compromise').wrong===8,
  disclosedCompromiseWithheld:get('reported-compromise').abstain===8,
  correlatedFalseCounterexample:get('correlated-false-reference').wrong===8,
  replayWithheld:get('nonce-replay').abstain===8,
  signaturesRemainValidUnderRevocation:get('reported-revocation').signatureAccepted===8,
  keyTruthDistinction:!a.clockAuthenticated&&!a.revocationStatusAuthenticated,
  readOnly:a.physicalActions===0&&!a.controllerPromoted,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  oneCenter:wag289Groups().frontal.length===1,
  priorPrivateArchitecture:WAG304.forms.join('|')==='[1]|{1}|(1)'
 };
 return {bound:'WAG-314',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,progress:3/8};
}
if(typeof module!=='undefined')module.exports={WAG314,wag314Policy,wag314Gate,wag314Trial,wag314Evaluate,wag314Audit};
