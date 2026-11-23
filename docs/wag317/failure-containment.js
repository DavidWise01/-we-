/* WAG-317 · Phase VII 6/8 · Independent Authority Failure Containment · .dlw
 * One failing authority cannot rewrite the other's immutable receipt.
 * Both independent fixture attestations are mandatory for admission.
 * Observer inputs [1] {1} (1) remain private, read-only and unaware.
 * Distinct test keys do not establish real-world independence or truth.
 */
const WAG317=Object.freeze({phase:'VII',turn:6,of:8,physicalActions:0,
 scenarios:Object.freeze(['clean','status-missing','clock-missing','status-tamper',
  'clock-tamper','status-key-swapped','clock-key-swapped','shared-root',
  'status-recovered','clock-recovered','both-missing','unreported-compromise',
  'correlated-false-reference'])});
function wag317Fixture(scenario,seq){
 const status=wag316Packet('status',seq),clock=wag316Packet('clock',seq);
 if(['status-missing','both-missing'].includes(scenario))status.signature='';
 if(['clock-missing','both-missing'].includes(scenario))clock.signature='';
 if(scenario==='status-tamper')status.body.state='REVOKED';
 if(scenario==='clock-tamper')clock.body.tick+=1;
 if(scenario==='status-key-swapped')status.publicKey=clock.publicKey;
 if(scenario==='clock-key-swapped')clock.publicKey=status.publicKey;
 if(scenario==='shared-root')clock.roots=['fixture-Q'];
 return {status,clock};
}
async function wag317Trial(scenario,seq){
 const fixture=wag317Fixture(scenario,seq);
 const originals={status:JSON.stringify(fixture.status),clock:JSON.stringify(fixture.clock)};
 const [status,clock]=await Promise.all([
  wag316Verify(fixture.status,'status',seq),wag316Verify(fixture.clock,'clock',seq)
 ]);
 const independentRoots=!fixture.status.roots.some(r=>fixture.clock.roots.includes(r));
 const statusReceipt=Object.freeze({...status,root:'fixture-Q',scope:'status-Q'});
 const clockReceipt=Object.freeze({...clock,root:fixture.clock.roots[0],scope:'clock-T'});
 const correlated=['unreported-compromise','correlated-false-reference'].includes(scenario);
 const observed=await wag313Trial(correlated?'correlated-signed-false':'clean',seq);
 const jointReady=statusReceipt.valid&&clockReceipt.valid&&independentRoots;
 const candidate=jointReady&&observed.reference.valid&&observed.observedSigned?observed.candidate:null;
 const verdict=!statusReceipt.valid&&!clockReceipt.valid?'BOTH_AUTHORITIES_WITHHELD':
  !statusReceipt.valid?'STATUS_AUTHORITY_WITHHELD':
  !clockReceipt.valid?'CLOCK_AUTHORITY_WITHHELD':
  !independentRoots?'SHARED_ANCESTRY_WITHHELD':
  candidate===null?'REFERENCE_WITHHELD':'CORRELATED_FIXTURE_CANDIDATE';
 const result=wag291DeepFreeze({scenario,seq,
  status:statusReceipt,clock:clockReceipt,jointReady,independentRoots,
  statusStillAvailable:statusReceipt.valid,clockStillAvailable:clockReceipt.valid,
  candidate,verdict,target:correlated?4:3,
  survivingEvidenceUsableForAdmission:false,
  referenceTruthAuthenticated:false,realOriginAuthenticated:false,
  promotionAuthorized:false});
 if(JSON.stringify(fixture.status)!==originals.status||JSON.stringify(fixture.clock)!==originals.clock)
  throw Error('fixture evidence mutated');
 return result;
}
async function wag317Evaluate(authority){
 const before=JSON.stringify(authority),rows=[];
 for(const scenario of WAG317.scenarios){
  let correct=0,wrong=0,abstain=0,statusValid=0,clockValid=0;
  for(let seq=0;seq<8;seq++){
   const t=await wag317Trial(scenario,seq);
   if(t.status.valid)statusValid++;
   if(t.clock.valid)clockValid++;
   if(t.candidate===null)abstain++;
   else if(t.candidate===t.target)correct++;else wrong++;
  }
  rows.push({scenario,correct,wrong,abstain,statusValid,clockValid,total:8});
 }
 if(JSON.stringify(authority)!==before)throw Error('authoritative state changed');
 return wag291DeepFreeze({bound:'WAG-317',phase:'VII',turn:6,rows,
  scenarioTrials:104,partialRecordsPreserved:true,partialAdmissionPermitted:false,
  externalOriginsVerified:false,truthVerified:false,promotionAuthorized:false,physicalActions:0,
  limitation:'Valid surviving fixture receipt is retained as evidence, never promoted into an action vote; undisclosed compromise or coordinated false evidence still yields wrong synthetic candidates.'});
}
async function wag317Audit(){
 const state=wag288Initial(),baseline=JSON.stringify(state),
 a=await wag317Evaluate(state),b=await wag317Evaluate(state),get=k=>a.rows.find(x=>x.scenario===k);
 const singleStatus=await wag317Trial('status-missing',0),
  singleClock=await wag317Trial('clock-missing',0),
  recovered=await wag317Trial('status-recovered',0);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  originalStateUnchanged:JSON.stringify(state)===baseline,
  allThirteenScenarios:a.rows.length===13&&a.scenarioTrials===104,
  exactAccounting:a.rows.every(x=>x.correct+x.wrong+x.abstain===8),
  cleanAccepted:get('clean').correct===8,
  statusMissingAbstains:get('status-missing').abstain===8,
  clockMissingAbstains:get('clock-missing').abstain===8,
  statusTamperAbstains:get('status-tamper').abstain===8,
  clockTamperAbstains:get('clock-tamper').abstain===8,
  statusSubstitutionAbstains:get('status-key-swapped').abstain===8,
  clockSubstitutionAbstains:get('clock-key-swapped').abstain===8,
  sharedAncestryAbstains:get('shared-root').abstain===8,
  recoveryPermitsCleanCase:get('status-recovered').correct===8&&get('clock-recovered').correct===8,
  bothMissingAbstains:get('both-missing').abstain===8,
  validClockSurvivesStatusFailure:singleStatus.clock.valid&&!singleStatus.status.valid,
  validStatusSurvivesClockFailure:singleClock.status.valid&&!singleClock.clock.valid,
  recoveredNoInheritedVeto:recovered.status.valid&&recovered.clock.valid,
  survivingEvidenceNoAction:!singleStatus.survivingEvidenceUsableForAdmission&&!singleClock.promotionAuthorized,
  unreportedCompromiseCounterexample:get('unreported-compromise').wrong===8,
  correlatedFalseCounterexample:get('correlated-false-reference').wrong===8,
  noIndependentRealWorldProof:!a.externalOriginsVerified&&!a.truthVerified,
  immutableReceipts:Object.isFrozen(singleStatus)&&Object.isFrozen(singleStatus.clock)&&Object.isFrozen(a.rows[0]),
  priorStageIntact:WAG316.turn===5&&WAG316.phase==='VII',
  noActuation:a.physicalActions===0&&!a.promotionAuthorized
 };
 return {bound:'WAG-317',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,progress:6/8};
}
if(typeof module!=='undefined')module.exports={WAG317,wag317Fixture,wag317Trial,wag317Evaluate,wag317Audit};
