/* WAG-321 · Phase VIII 2/8 · Adaptive Support Calibration · .dlw
   Append-only, read-only simulation. New synthetic domain requires a
   fixed SHA-256 calibration manifest and two declared non-shared source roots.
   These fixture roots are NOT independently authenticated real-world sources.
   The three private [1], {1}, (1) interpreters never receive peer evidence.
   Evidence familiarity and cryptographic authenticity do NOT imply truth.
*/
const WAG321=Object.freeze({phase:'VIII',step:2,steps:8,physicalActions:0,
 domain:'synthetic-optical-v2',
 pin:'138241e198ac2aeeed0b968dc2296f47cc3540ecb26b71bb3738156c4c8b6acd',
 cases:Object.freeze(['baseline','novel-uncalibrated','novel-calibrated','single-probe',
  'shared-root','relabeled-shared-root','stale-calibration','manifest-tamper',
  'mutable-pin-swap','contradictory-probes','changed-feature-shape',
  'calibration-without-signatures','signed-false-novel','correlated-false-novel',
  'spoofed-familiar','baseline-retained'])});
function wag321Manifest(){
 return {domain:'synthetic-optical-v2',channel:3,vocab:'neutral',
  version:1,validFrom:0,validUntil:7};
}
function wag321Fixture(kind,seq){
 const manifest=wag321Manifest();
 const evidence=[
  {source:'probe-P',root:'root-P',parent:'root-P',channel:3,seq,signedFixture:true},
  {source:'probe-R',root:'root-R',parent:'root-R',channel:3,seq,signedFixture:true}
 ];
 let domain=WAG321.domain,vocab='neutral',featureCount=8;
 const proposedPin=WAG321.pin;
 let declaredPin=proposedPin;
 if(kind==='baseline'||kind==='baseline-retained'||kind==='spoofed-familiar')domain=WAG320.model.domain;
 if(kind==='novel-uncalibrated')evidence.length=0;
 if(kind==='single-probe')evidence.pop();
 if(kind==='shared-root')evidence[1].root='root-P';
 if(kind==='relabeled-shared-root'){evidence[1].source='renamed-probe';evidence[1].parent='root-P'}
 if(kind==='stale-calibration')manifest.validUntil=-1;
 if(kind==='manifest-tamper')manifest.channel=4;
 if(kind==='mutable-pin-swap'){manifest.channel=4;declaredPin=wag307Sha256(JSON.stringify(manifest))}
 if(kind==='contradictory-probes')evidence[1].channel=4;
 if(kind==='changed-feature-shape')featureCount=7;
 if(kind==='calibration-without-signatures')evidence[0].signedFixture=false;
 return {kind,seq,manifest,evidence,domain,vocab,featureCount,declaredPin};
}
function wag321CalibrationGate(f){
 const baseline=f.domain===WAG320.model.domain;
 const needsExtension=!baseline;
 const canonical=wag307Sha256(JSON.stringify(f.manifest));
 const pinned=canonical===WAG321.pin&&f.declaredPin===WAG321.pin;
 const manifestFresh=f.manifest.validFrom<=f.seq&&f.seq<=f.manifest.validUntil;
 const rootSet=f.evidence.map(x=>x.root),sources=new Set(rootSet);
 const distinctRoots=f.evidence.length===2&&sources.size===2&&
  f.evidence.every(x=>x.root===x.parent)&&
  !rootSet.some(x=>['fixture-A','fixture-B','fixture-C','fixture-D'].includes(x));
 const probesAgree=f.evidence.length===2&&f.evidence.every(x=>x.channel===3&&x.seq===f.seq);
 const fixtureSignatureClaims=f.evidence.length===2&&f.evidence.every(x=>x.signedFixture===true);
 const shape=f.featureCount===8;
 const context=f.manifest.domain===f.domain&&f.manifest.channel===3&&f.manifest.vocab===f.vocab;
 const extensionReady=needsExtension&&pinned&&manifestFresh&&distinctRoots&&probesAgree&&
  fixtureSignatureClaims&&shape&&context;
 const supported=baseline?shape:extensionReady;
 return Object.freeze({baseline,needsExtension,pinned,manifestFresh,distinctRoots,
  probesAgree,fixtureSignatureClaims,shape,context,extensionReady,supported,
  authenticatedExternalCalibration:false,knownTrueObservation:false});
}
async function wag321Trial(kind,seq){
 const f=wag321Fixture(kind,seq);
 const gate=wag321CalibrationGate(f);
 const falseEvidence=['signed-false-novel','correlated-false-novel','spoofed-familiar'].includes(kind);
 const prior=await wag316Trial(falseEvidence?'correlated-false-reference':'clean',seq);
 const candidate=gate.supported&&prior.status.valid&&prior.clock.valid&&prior.distinct?prior.candidate:null;
 return wag291DeepFreeze({kind,seq,gate,candidate,truth:falseEvidence?4:3,
  verdict:!gate.supported?'UNSUPPORTED_ABSTAIN':candidate===null?'REFERENCE_WITHHELD':
  gate.extensionReady?'SYNTHETIC_EXTENSION_CANDIDATE':'BASELINE_CANDIDATE',
  newlyLearnedRuleNotPromoted:true,controllerPromoted:false,physicalActions:0});
}
async function wag321Evaluate(authority){
 const before=JSON.stringify(authority),rows=[];
 for(const kind of WAG321.cases){
  let correct=0,wrong=0,abstain=0,extensionReady=0;
  for(let seq=0;seq<8;seq++){
   const t=await wag321Trial(kind,seq);
   if(t.gate.extensionReady)extensionReady++;
   if(t.candidate===null)abstain++;else if(t.candidate===t.truth)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,extensionReady,total:8});
 }
 if(JSON.stringify(authority)!==before)throw Error('source state modified');
 return wag291DeepFreeze({bound:'WAG-321',phase:'VIII',turn:2,rows,trials:128,
  realWorldSourceIndependence:false,calibrationProbesCryptographicallySigned:false,
  externalTruthAuthenticated:false,controllerPromoted:false,physicalActions:0,
  limitation:'The additional synthetic support domain is not a real-world validated expansion. Signed false familiar data remains a counterexample.'});
}
async function wag321Audit(){
 const source=wag288Initial(),original=JSON.stringify(source),
 a=await wag321Evaluate(source),b=await wag321Evaluate(source),get=k=>a.rows.find(x=>x.kind===k);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  unchanged:JSON.stringify(source)===original,
  sixteenScenarios:a.rows.length===16&&a.trials===128,
  accounting:a.rows.every(x=>x.correct+x.wrong+x.abstain===8),
  frozenPin:wag307Sha256(JSON.stringify(wag321Manifest()))===WAG321.pin,
  baselineCorrect:get('baseline').correct===8,
  uncalibratedRejected:get('novel-uncalibrated').abstain===8,
  calibratedFixtureCandidate:get('novel-calibrated').correct===8,
  loneProbeRejected:get('single-probe').abstain===8,
  sharedRootRejected:get('shared-root').abstain===8,
  renamedRootRejected:get('relabeled-shared-root').abstain===8,
  staleRejected:get('stale-calibration').abstain===8,
  mutatedManifestRejected:get('manifest-tamper').abstain===8,
  mutablePinRejected:get('mutable-pin-swap').abstain===8,
  conflictingProbesRejected:get('contradictory-probes').abstain===8,
  changedShapeRejected:get('changed-feature-shape').abstain===8,
  unsignedClaimsRejected:get('calibration-without-signatures').abstain===8,
  signedFalseRetained:get('signed-false-novel').wrong===8,
  correlatedFalseRetained:get('correlated-false-novel').wrong===8,
  familiarSpoofRetained:get('spoofed-familiar').wrong===8,
  originalBaselinePreserved:get('baseline-retained').correct===8,
  oldCalibrationUnchanged:WAG320.model.domain==='synthetic-optical-v1',
  noExternalProof:!a.realWorldSourceIndependence&&!a.externalTruthAuthenticated&&!a.calibrationProbesCryptographicallySigned,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  noActuation:!a.controllerPromoted&&a.physicalActions===0,
  threeBlindForms:WAG304.forms.join('|')==='[1]|{1}|(1)',
  phaseVIIIContinuity:WAG320.phase==='VIII'&&WAG320.turn===1
 };
 return {bound:'WAG-321',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,progress:2/8};
}
if(typeof module!=='undefined')module.exports={WAG321,wag321Manifest,wag321Fixture,wag321CalibrationGate,wag321Trial,wag321Evaluate,wag321Audit};
