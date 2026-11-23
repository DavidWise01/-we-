/* WAG-315 · Phase VII 4/8 · Dual pinned status/monotonic reference · .dlw
 * Synthetic SHA-256 anchor digests constrain independently labelled status
 * and clock records. NOT signed attestations or independently trusted hardware.
 * Explicit compromised-verifier scenario shows what root-of-trust replacement
 * can invalidate. No source receives reference, clock or peers.
 * 5^3 quartz / 3^3 cortex / 1^3 frontal remains unchanged. .dlw
 */
const WAG315=Object.freeze({phase:'VII',turn:4,of:8,
 statusPin:'8aeb0e02d00ec92831abf63660a575b3c46035af50b055e3351dbf7449720189',
 clockPin:'c9c3f547cf19095d5dc578f9071acdbb5e913bb7941ffe09e6be5055af6f1a06',
 baselineCounter:120,physicalActions:0,
 cases:Object.freeze(['clean','revoked-key','stale-status','status-rollback',
 'counter-rollback','counter-ahead','anchors-disagree','status-tamper',
 'clock-tamper','compromised-status-anchor','both-anchors-compromised',
 'unreported-compromise','correlated-false-reference','nonce-replay'])});
function wag315Baseline(){
 return {status:{version:8,key:'fixture-D',status:'ACTIVE',effective:1100},
  clock:{version:12,epoch:313,baseCounter:120,authority:'clock-fixture-T'}};
}
function wag315Fixture(kind,seq){
 const {status,clock}=wag315Baseline();
 let counter=WAG315.baselineCounter+seq,statusCounter=counter;
 if(kind==='revoked-key')status.status='REVOKED';
 if(kind==='stale-status')status.effective=990;
 if(kind==='status-rollback')status.version=7;
 if(kind==='counter-rollback')counter-=1;
 if(kind==='counter-ahead')counter+=5;
 if(kind==='anchors-disagree')statusCounter+=1;
 if(kind==='status-tamper'||kind==='compromised-status-anchor'||kind==='both-anchors-compromised')status.key='rogue-signer';
 if(kind==='clock-tamper'||kind==='both-anchors-compromised')clock.authority='rogue-time';
 const pins={status:WAG315.statusPin,clock:WAG315.clockPin};
 if(kind==='compromised-status-anchor'||kind==='both-anchors-compromised')
   pins.status=wag307Sha256(JSON.stringify(status));
 if(kind==='both-anchors-compromised')pins.clock=wag307Sha256(JSON.stringify(clock));
 return Object.freeze({status,clock,counter,statusCounter,pins,
   statusAge:kind==='stale-status'?100:2,challengeCounter:WAG315.baselineCounter+seq});
}
function wag315AnchorCheck(f){
 const statusDigest=wag307Sha256(JSON.stringify(f.status));
 const clockDigest=wag307Sha256(JSON.stringify(f.clock));
 const statusAnchorValid=statusDigest===f.pins.status;
 const clockAnchorValid=clockDigest===f.pins.clock;
 const statusPinnedToOriginal=f.pins.status===WAG315.statusPin;
 const clockPinnedToOriginal=f.pins.clock===WAG315.clockPin;
 const keyActive=f.status.status==='ACTIVE';
 const statusFresh=f.statusAge<=4&&f.status.version>=8;
 const sequenceMonotonic=f.counter===f.challengeCounter;
 const anchorsCoherent=f.counter===f.statusCounter;
 const counterInRange=f.counter>=f.clock.baseCounter&&f.counter<=f.clock.baseCounter+7;
 return Object.freeze({statusDigest,clockDigest,statusAnchorValid,clockAnchorValid,
  statusPinnedToOriginal,clockPinnedToOriginal,
  keyActive,statusFresh,sequenceMonotonic,anchorsCoherent,counterInRange,
  effectiveTrustAnchorsAuthenticated:false});
}
async function wag315Trial(kind,seq){
 const fixture=wag315Fixture(kind,seq);
 const evidenceKind=kind==='nonce-replay'?'nonce-replay':
  ['unreported-compromise','correlated-false-reference'].includes(kind)?'correlated-signed-false':'clean';
 const reference=await wag313Trial(evidenceKind,seq);
 const a=wag315AnchorCheck(fixture);
 // Source-level pin identity is immutable in code, independent of mutable supplied pins.
 const pinned=a.statusAnchorValid&&a.clockAnchorValid&&a.statusPinnedToOriginal&&a.clockPinnedToOriginal;
 const statusReady=a.keyActive&&a.statusFresh;
 const clockReady=a.sequenceMonotonic&&a.anchorsCoherent&&a.counterInRange;
 const valid=reference.reference.valid&&reference.observedSigned&&pinned&&statusReady&&clockReady;
 const candidate=valid&&reference.candidate!==null?reference.candidate:null;
 return Object.freeze({kind,seq,fixture,anchors:a,candidate,
  syntheticTruth:evidenceKind==='correlated-signed-false'?4:3,
  signatureValid:reference.reference.signatureOK,
  verdict:!reference.reference.valid?'CHALLENGE_REJECTED':!pinned?'PINNED_ANCHOR_MISMATCH':
   !statusReady?'STATUS_NOT_TRUSTWORTHY':!clockReady?'COUNTER_REJECTED':
   reference.candidate===null?'REFERENCE_DISAGREEMENT':'SYNTHETIC_CANDIDATE',
  promotionAuthorized:false});
}
async function wag315Evaluate(authority){
 const baseline=JSON.stringify(authority),rows=[];
 for(const kind of WAG315.cases){
  let correct=0,wrong=0,abstain=0,anchorRejected=0,counterRejected=0;
  for(let seq=0;seq<8;seq++){
   const t=await wag315Trial(kind,seq),a=t.anchors;
   if(!(a.statusAnchorValid&&a.clockAnchorValid&&a.statusPinnedToOriginal&&a.clockPinnedToOriginal))anchorRejected++;
   if(!(a.sequenceMonotonic&&a.anchorsCoherent&&a.counterInRange))counterRejected++;
   if(t.candidate===null)abstain++;
   else if(t.candidate===t.syntheticTruth)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,anchorRejected,counterRejected,total:8});
 }
 if(JSON.stringify(authority)!==baseline)throw Error('authoritative memory mutated');
 return wag291DeepFreeze({bound:'WAG-315',phase:'VII',turn:4,rows,
  trials:112,roots:'two separately labelled synthetic checkpoint records, not real independently anchored witnesses',
  authenticExternalClock:false,authenticatedStatusRegistry:false,
  controllerPromoted:false,physicalActions:0});
}
async function wag315Audit(){
 const state=wag288Initial(),baseline=JSON.stringify(state);
 const a=await wag315Evaluate(state),b=await wag315Evaluate(state),r=k=>a.rows.find(x=>x.kind===k);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  stateUnchanged:JSON.stringify(state)===baseline,
  sampleAccounting:a.trials===112&&a.rows.length===14&&a.rows.every(x=>x.correct+x.wrong+x.abstain===8),
  pinnedStatusDigest:wag307Sha256(JSON.stringify(wag315Baseline().status))===WAG315.statusPin,
  pinnedClockDigest:wag307Sha256(JSON.stringify(wag315Baseline().clock))===WAG315.clockPin,
  cleanCorrect:r('clean').correct===8,
  reportedRevocationWithheld:r('revoked-key').abstain===8,
  staleStatusWithheld:r('stale-status').abstain===8,
  statusRollbackWithheld:r('status-rollback').abstain===8,
  counterRollbackWithheld:r('counter-rollback').abstain===8,
  counterAheadWithheld:r('counter-ahead').abstain===8,
  inconsistentCountersWithheld:r('anchors-disagree').abstain===8,
  statusTamperWithheld:r('status-tamper').abstain===8,
  clockTamperWithheld:r('clock-tamper').abstain===8,
  compromisedStatusPinWithheld:r('compromised-status-anchor').abstain===8,
  compromisedBothPinsWithheld:r('both-anchors-compromised').abstain===8,
  unreportedCompromiseFails:r('unreported-compromise').wrong===8,
  correlatedFalseFails:r('correlated-false-reference').wrong===8,
  replayWithheld:r('nonce-replay').abstain===8,
  syntheticTrustLimit:!a.authenticExternalClock&&!a.authenticatedStatusRegistry,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  noActuation:!a.controllerPromoted&&a.physicalActions===0,
  privateFormsUntouched:WAG304.forms.join('|')==='[1]|{1}|(1)'
 };
 return {bound:'WAG-315',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,progress:4/8};
}
if(typeof module!=='undefined')module.exports={WAG315,wag315Baseline,wag315Fixture,wag315AnchorCheck,wag315Trial,wag315Evaluate,wag315Audit};
