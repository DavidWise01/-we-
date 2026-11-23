/* WAG-320 · Phase VIII 1/8 · Open-World Uncertainty Admission · .dlw
 * This observer-only gate rejects unknown context and out-of-support evidence.
 * Its calibration domain is a SYNTHETIC fixture, not an external truth oracle.
 * Distinct [1], {1}, (1) forms are blind to one another, and the reference
 * gate operates outside their one frontal address. No authority promotion.
 */
const WAG320=Object.freeze({phase:'VIII',turn:1,of:8,physicalActions:0,
 model:Object.freeze({domain:'synthetic-optical-v1',channel:3,featureCount:8,
  permittedVocabulary:Object.freeze(['neutral','baseline']),maxDrift:.2,maxAge:4}),
 cases:Object.freeze(['clean','unseen-domain','unseen-channel','unsupported-vocabulary',
 'feature-count-change','out-of-range-feature','missing-calibration','expired-calibration',
 'distribution-shift','context-contradiction','unsigned-observation',
 'signed-false-in-support','correlated-false-in-support','spoofed-in-support'])});
function wag320Observation(kind,seq){
 const c={domain:WAG320.model.domain,channel:3,vocabulary:'neutral',
 features:[.1,.1,.1,.9,.1,.1,.1,.1],calibrated:true,age:2,drift:.05,seq,
 supported:true,signatureRequired:true,claimConsistency:true};
 if(kind==='unseen-domain')c.domain='synthetic-unseen-v2';
 if(kind==='unseen-channel')c.channel=11;
 if(kind==='unsupported-vocabulary')c.vocabulary='novel-quantum';
 if(kind==='feature-count-change')c.features.pop();
 if(kind==='out-of-range-feature')c.features[2]=1.3;
 if(kind==='missing-calibration')c.calibrated=false;
 if(kind==='expired-calibration')c.age=9;
 if(kind==='distribution-shift')c.drift=.5;
 if(kind==='context-contradiction')c.claimConsistency=false;
 if(kind==='unsigned-observation')c.signatureRequired=false;
 return c;
}
function wag320SupportGate(observation,signatureOK){
 const domainKnown=observation.domain===WAG320.model.domain;
 const channelKnown=observation.channel===WAG320.model.channel;
 const vocabularyKnown=WAG320.model.permittedVocabulary.includes(observation.vocabulary);
 const vectorSupported=Array.isArray(observation.features)&&
  observation.features.length===WAG320.model.featureCount&&
  observation.features.every(x=>Number.isFinite(x)&&x>=0&&x<=1);
 const calibrationFresh=observation.calibrated===true&&
  observation.age>=0&&observation.age<=WAG320.model.maxAge;
 const driftAcceptable=Number.isFinite(observation.drift)&&
  observation.drift<=WAG320.model.maxDrift&&observation.drift>=0;
 const contextCoherent=observation.claimConsistency===true;
 const signatureBound=signatureOK&&observation.signatureRequired===true;
 const supported=domainKnown&&channelKnown&&vocabularyKnown&&vectorSupported&&
  calibrationFresh&&driftAcceptable&&contextCoherent&&signatureBound;
 return Object.freeze({domainKnown,channelKnown,vocabularyKnown,vectorSupported,
  calibrationFresh,driftAcceptable,contextCoherent,signatureBound,supported,
  calibratedRealWorld:false,noveltyProofAuthenticated:false});
}
async function wag320Trial(kind,seq){
 const sourceScenario=kind==='signed-false-in-support'||kind==='correlated-false-in-support'||kind==='spoofed-in-support'
  ?'correlated-signed-false':'clean';
 const prior=await wag316Trial(sourceScenario,seq);
 const observation=wag320Observation(kind,seq);
 const gate=wag320SupportGate(observation,prior.status.valid&&prior.clock.valid&&prior.referenceSignatureOK);
 const evidenceValid=prior.status.valid&&prior.clock.valid&&prior.distinct&&prior.candidate!==null;
 const eligible=gate.supported&&evidenceValid;
 const candidate=eligible?prior.candidate:null;
 const target=sourceScenario==='correlated-signed-false'?4:3;
 return wag291DeepFreeze({kind,seq,gate,priorStatus:prior.status.valid,
  priorClock:prior.clock.valid,candidate,target,
  verdict:!evidenceValid?'SIGNED_EVIDENCE_UNAVAILABLE':!gate.supported?'OUT_OF_SUPPORT_ABSTAIN':
   'IN_SUPPORT_FIXTURE_CANDIDATE',
  externalGroundTruthAttested:false,controllerPromoted:false,physicalActions:0});
}
async function wag320Evaluate(authority){
 const before=JSON.stringify(authority),rows=[];
 for(const kind of WAG320.cases){
  let correct=0,wrong=0,abstain=0,supportRejected=0;
  for(let seq=0;seq<8;seq++){
   const r=await wag320Trial(kind,seq);
   if(!r.gate.supported)supportRejected++;
   if(r.candidate===null)abstain++;else if(r.candidate===r.target)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,supportRejected,total:8});
 }
 if(JSON.stringify(authority)!==before)throw Error('authoritative memory changed');
 return wag291DeepFreeze({bound:'WAG-320',phase:'VIII',turn:1,rows,total:112,
  unsupportedEvidenceAdmitted:false,actualOpenWorldCoverageVerified:false,
  externalTruthAttested:false,controllerPromoted:false,physicalActions:0,
  limitation:'In-support correlated false claims and spoofed known context remain accepted as wrong candidates.'});
}
async function wag320Audit(){
 const state=wag288Initial(),snap=JSON.stringify(state),
 a=await wag320Evaluate(state),b=await wag320Evaluate(state),get=k=>a.rows.find(x=>x.kind===k);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  readOnly:JSON.stringify(state)===snap,
  fourteenScenarios:a.rows.length===14&&a.total===112,
  exactAccounting:a.rows.every(r=>r.correct+r.wrong+r.abstain===8),
  cleanCorrect:get('clean').correct===8,
  unknownDomainAbstains:get('unseen-domain').abstain===8,
  unseenChannelAbstains:get('unseen-channel').abstain===8,
  vocabularyAbstains:get('unsupported-vocabulary').abstain===8,
  shapeAbstains:get('feature-count-change').abstain===8,
  rangeAbstains:get('out-of-range-feature').abstain===8,
  calibrationAbsentAbstains:get('missing-calibration').abstain===8,
  calibrationExpiredAbstains:get('expired-calibration').abstain===8,
  distributionShiftAbstains:get('distribution-shift').abstain===8,
  contradictionsAbstain:get('context-contradiction').abstain===8,
  unsignedAbstains:get('unsigned-observation').abstain===8,
  signedFalseCounterexample:get('signed-false-in-support').wrong===8,
  correlatedFalseCounterexample:get('correlated-false-in-support').wrong===8,
  spoofedSupportCounterexample:get('spoofed-in-support').wrong===8,
  domainNotGroundTruth:!a.actualOpenWorldCoverageVerified&&!a.externalTruthAttested,
  noPromotion:!a.controllerPromoted&&a.physicalActions===0,
  frozen:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  blindForms:WAG304.forms.join('|')==='[1]|{1}|(1)',
  previousPhaseClosed:WAG319.phase==='VII'&&WAG319.researchComplete
 };
 return {bound:'WAG-320',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,progress:1/8};
}
if(typeof module!=='undefined')module.exports={WAG320,wag320Observation,wag320SupportGate,wag320Trial,wag320Evaluate,wag320Audit};
