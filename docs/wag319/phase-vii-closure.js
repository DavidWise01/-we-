/* WAG-319 · Phase VII 8/8 · acceptance boundary and immutable research closure · .dlw
 * All seven previously published Phase VII audits are re-executed.
 * Research completion is not controller admission. Fail closed on
 * unsigned real-world provenance, absent independent truth attestation,
 * or ANY accepted false-evidence counterexample. No physical actuation.
 * [1] {1} (1) remain mutually blind inside one frontal address.
 */
const WAG319=Object.freeze({phase:'VII',turn:8,of:8,researchComplete:true,
 acceptanceRules:Object.freeze({
  wrongSelectionsAllowed:0,
  realWorldSourceAuthenticationRequired:true,
  realWorldReferenceTruthRequired:true,
  observedClockAttestationRequired:true,
  privateInterpretersRequired:3
 }),next:Object.freeze({phase:'VIII',first:'WAG-320 · Open-World Uncertainty Admission',turns:8}),
 physicalActions:0});
async function wag319Close(authority){
 const before=JSON.stringify(authority);
 const audits=await Promise.all([
  wag312Audit(),wag313Audit(),wag314Audit(),wag315Audit(),
  wag316Audit(),wag317Audit(),wag318Audit()]);
 const milestones=audits.map((audit,i)=>Object.freeze({
  bound:'WAG-'+(312+i),auditPass:audit.pass,
  tests:audit.rows.reduce((s,r)=>s+r.total,0),
  wrong:audit.rows.reduce((s,r)=>s+r.wrong,0),
  abstained:audit.rows.reduce((s,r)=>s+r.abstain,0),
  immutable:Object.isFrozen(audit.rows[0])
 }));
 const wrong=milestones.reduce((s,x)=>s+x.wrong,0);
 const allAuditsPass=audits.every(a=>a.pass);
 const guard=Object.freeze({
  allResearchAuditsPass:allAuditsPass,
  zeroAcceptedWrongDecisions:wrong<=WAG319.acceptanceRules.wrongSelectionsAllowed,
  realWorldSourceAuthenticated:false,
  realWorldReferenceTruthAuthenticated:false,
  actualClockAttested:false,
  exactlyThreePrivateInterpreters:WAG304.forms.length===3,
  authoritativeMemoryUnchanged:JSON.stringify(authority)===before
 });
 const approved=Object.values(guard).every(Boolean);
 const record=wag291DeepFreeze({
  bound:'WAG-319',phase:'VII',turn:'8/8',
  researchComplete:true,acceptance:approved?'PASS':'WITHHELD',
  controllerPromoted:false,physicalActions:0,
  precommittedRules:WAG319.acceptanceRules,
  guard,milestones,
  totalTrials:milestones.reduce((s,x)=>s+x.tests,0),
  wrongSelections:wrong,
  counterexamples:Object.freeze([
   'unreported or undisclosed signing-key compromise',
   'validly signed correlated false observations and references'
  ]),
  provenance:'Synthetic Ed25519 fixtures; no real-world signer identity or trustworthy truth oracle.',
  next:WAG319.next
 });
 if(JSON.stringify(authority)!==before)throw Error('authoritative state changed');
 return record;
}
async function wag319Audit(){
 const source=wag288Initial(),original=JSON.stringify(source),
 a=await wag319Close(source),b=await wag319Close(source);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  authoritativeStateIntact:JSON.stringify(source)===original,
  sevenPriorMilestones:a.milestones.length===7,
  allPreviousAuditsPass:a.guard.allResearchAuditsPass,
  correctTrialCount:a.totalTrials===72+88+96+112+96+104+98,
  unresolvedFalseEvidence:a.wrongSelections>0&&!a.guard.zeroAcceptedWrongDecisions,
  realSourceUnauthenticated:!a.guard.realWorldSourceAuthenticated,
  referenceTruthUnauthenticated:!a.guard.realWorldReferenceTruthAuthenticated,
  trustedClockUnavailable:!a.guard.actualClockAttested,
  withheldAdmission:a.acceptance==='WITHHELD',
  noControllerPromotion:!a.controllerPromoted,
  researchComplete:a.researchComplete&&a.turn==='8/8',
  phaseVIIIHandOff:a.next.phase==='VIII'&&a.next.turns===8,
  threePrivateForms:WAG304.forms.join('|')==='[1]|{1}|(1)',
  noPhysicalActuation:a.physicalActions===0,
  frozen:Object.isFrozen(a)&&Object.isFrozen(a.guard)&&Object.isFrozen(a.milestones[0]),
  signedFalseCounterexampleRetained:a.counterexamples.length===2
 };
 return {bound:'WAG-319',pass:Object.values(checks).every(Boolean),checks,
  phaseProgress:1,record:a};
}
if(typeof module!=='undefined')module.exports={WAG319,wag319Close,wag319Audit};
