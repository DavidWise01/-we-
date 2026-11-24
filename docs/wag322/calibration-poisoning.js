/* WAG-322 · Phase VIII 3/8 · Calibration Poisoning Resistance · .dlw
 * Frozen WAG-321 calibration and all historical evidence remain unchanged.
 * External read-only adversarial gate compares two probe roots and a held-out
 * synthetic challenge root against one another and a pinned calibration.
 * A distinct LABEL is not a proven independent external witness.
 * Poisoned, synchronized false probe and challenge evidence remains an
 * explicit accepted-wrong counterexample. No permission to actuate.
 * [1], {1}, (1) remain mutually blind in the one frontal address.
 */
const WAG322=Object.freeze({phase:'VIII',turn:3,of:8,actions:0,
 cases:Object.freeze(['clean','single-probe-poison','conflicting-probes',
 'probe-source-relabel','poisoned-manifest','expired-manifest',
 'missing-probe','missing-challenge','stale-challenge','shared-challenge-root',
 'heldout-detects-poison','coordinated-poison-heldout',
 'coordinated-poison-without-truth','baseline-retained','false-familiar-pattern'])});
function wag322Fixture(kind,seq){
 const f=wag321Fixture(kind==='baseline-retained'||kind==='false-familiar-pattern'?'baseline':'novel-calibrated',seq);
 const challenge={root:'root-H',parent:'root-H',channel:3,seq,
   available:true,claimedIndependent:true,attested:false};
 if(kind==='single-probe-poison'||kind==='conflicting-probes')f.evidence[0].channel=4;
 if(kind==='probe-source-relabel')f.evidence[1].parent='root-P';
 if(kind==='poisoned-manifest')f.manifest.channel=4;
 if(kind==='expired-manifest')f.manifest.validUntil=-1;
 if(kind==='missing-probe')f.evidence.pop();
 if(kind==='missing-challenge')challenge.available=false;
 if(kind==='stale-challenge')challenge.seq=seq-1;
 if(kind==='shared-challenge-root')challenge.root='root-P';
 if(kind==='heldout-detects-poison')challenge.channel=4;
 if(kind==='coordinated-poison-heldout'||kind==='coordinated-poison-without-truth'){
   // Every supplied source claims channel 3 while simulated ground truth is 4.
   challenge.claimedIndependent=true;
 }
 return {probe:f,challenge};
}
function wag322PoisonGate(f){
 const base=wag321CalibrationGate(f.probe);
 const roots=f.probe.evidence.map(x=>x.root);
 const rootSeparate=!!f.challenge.root&&!roots.includes(f.challenge.root)&&
   f.challenge.parent===f.challenge.root;
 const challengeFresh=f.challenge.seq===f.probe.seq;
 const challengeValid=f.challenge.available&&rootSeparate&&challengeFresh&&
   Number.isInteger(f.challenge.channel)&&f.challenge.channel>=0&&f.challenge.channel<8;
 const probesMatch=base.probesAgree&&f.probe.evidence.every(x=>x.channel===f.challenge.channel);
 const supported=base.supported&&challengeValid&&probesMatch;
 return Object.freeze({base,rootSeparate,challengeFresh,challengeValid,
   probesMatch,supported,challengeAttested:false,
   sourceIndependenceProven:false,truthEstablished:false});
}
async function wag322Trial(kind,seq){
 const fixture=wag322Fixture(kind,seq),gate=wag322PoisonGate(fixture);
 const contaminated=['coordinated-poison-heldout','coordinated-poison-without-truth',
  'false-familiar-pattern'].includes(kind);
 const previous=await wag316Trial(contaminated?'correlated-false-reference':'clean',seq);
 const candidate=gate.supported&&previous.status.valid&&previous.clock.valid&&
   previous.distinct?previous.candidate:null;
 return wag291DeepFreeze({kind,seq,gate,candidate,target:contaminated?4:3,
  verdict:!gate.base.supported?'CALIBRATION_REJECTED':
    !gate.challengeValid?'HELDOUT_UNAVAILABLE_OR_SHARED':
    !gate.probesMatch?'HELDOUT_CONFLICT':
    candidate===null?'REFERENCE_WITHHELD':'UNVERIFIED_SYNTHETIC_CANDIDATE',
  independentSourceProven:false,controllerPromoted:false,physicalActions:0});
}
async function wag322Evaluate(authority){
 const before=JSON.stringify(authority),rows=[];
 for(const kind of WAG322.cases){
  let correct=0,wrong=0,abstain=0,calibrationRejected=0,challengeRejected=0;
  for(let seq=0;seq<8;seq++){
   const r=await wag322Trial(kind,seq);
   if(!r.gate.base.supported)calibrationRejected++;
   if(!r.gate.challengeValid||!r.gate.probesMatch)challengeRejected++;
   if(r.candidate===null)abstain++;
   else if(r.candidate===r.target)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,calibrationRejected,challengeRejected,total:8});
 }
 if(JSON.stringify(authority)!==before)throw Error('original authority mutated');
 return wag291DeepFreeze({bound:'WAG-322',phase:'VIII',turn:3,trials:120,rows,
  cryptographicProbeAuthentication:false,externalHeldoutTruthAuthenticated:false,
  actualSourceIndependenceProven:false,controllerPromoted:false,physicalActions:0,
  limitation:'Held-out fixture labels and mutually consistent evidence can all be wrong; even three declared roots are not independently verified witnesses.'});
}
async function wag322Audit(){
 const state=wag288Initial(),frozen=JSON.stringify(state),
  a=await wag322Evaluate(state),b=await wag322Evaluate(state),r=k=>a.rows.find(x=>x.kind===k);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  originalMemoryUntouched:JSON.stringify(state)===frozen,
  fifteenScenarios:a.rows.length===15&&a.trials===120,
  exactAccounting:a.rows.every(x=>x.correct+x.wrong+x.abstain===8),
  baselineCorrect:r('clean').correct===8,
  lonePoisonRejected:r('single-probe-poison').abstain===8,
  probeConflictRejected:r('conflicting-probes').abstain===8,
  ancestryRelabelRejected:r('probe-source-relabel').abstain===8,
  manifestTamperRejected:r('poisoned-manifest').abstain===8,
  expiredManifestRejected:r('expired-manifest').abstain===8,
  absentProbeRejected:r('missing-probe').abstain===8,
  absentHeldoutRejected:r('missing-challenge').abstain===8,
  staleHeldoutRejected:r('stale-challenge').abstain===8,
  sharedHeldoutRootRejected:r('shared-challenge-root').abstain===8,
  heldoutDisagreementRejected:r('heldout-detects-poison').abstain===8,
  coordinatedPoisonCounterexample:r('coordinated-poison-heldout').wrong===8,
  correlatedTruthCounterexample:r('coordinated-poison-without-truth').wrong===8,
  baselineUnchanged:r('baseline-retained').correct===8&&
    WAG320.model.domain==='synthetic-optical-v1'&&WAG321.domain==='synthetic-optical-v2',
  familiarSpoofUnresolved:r('false-familiar-pattern').wrong===8,
  oldPinnedManifestUnchanged:wag307Sha256(JSON.stringify(wag321Manifest()))===WAG321.pin,
  noExternalTruthClaim:!a.externalHeldoutTruthAuthenticated&&!a.actualSourceIndependenceProven,
  noPhantomSignatureClaim:a.cryptographicProbeAuthentication===false,
  noPromotion:!a.controllerPromoted&&a.physicalActions===0,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  privateForms:WAG304.forms.join('|')==='[1]|{1}|(1)',
  phaseContinuity:WAG321.phase==='VIII'&&WAG321.step===2
 };
 return {bound:'WAG-322',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,progress:3/8};
}
if(typeof module!=='undefined')module.exports={WAG322,wag322Fixture,wag322PoisonGate,wag322Trial,wag322Evaluate,wag322Audit};
