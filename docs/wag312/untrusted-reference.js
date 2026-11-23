/* WAG-312 · Phase VII 1/8 · Untrusted Reference Challenge · .dlw
 * External reference is an adversarial input, not a truth oracle.
 * Three private frontal forms do not receive reference, source ancestry,
 * signatures, or peer claims; comparison happens only outside the forms.
 * Reference trace is synthetic and unsigned; distinct fixture roots
 * do NOT prove real-world source independence or observation truth.
 * No controller promotion and no physical actions.
 */
const WAG312=Object.freeze({phase:'VII',turn:1,of:8,epoch:309,
 cases:Object.freeze(['clean','stale-reference','shared-ancestry','relabel-shared',
 'missing-ancestry','corrupt-reference','signed-false-correct-reference',
 'correlated-false-reference','reference-unavailable']),
 claimedReferenceRoot:'fixture-D',physicalActions:0});
function wag312Reference(kind,seq){
 const signedFalse=kind==='signed-false-correct-reference'||kind==='correlated-false-reference';
 const channel=kind==='corrupt-reference'?4:
  kind==='correlated-false-reference'?3:signedFalse?4:3;
 const graph={
  'fixture-A':[], 'fixture-B':[], 'fixture-C':[], 'fixture-D':[],
  'ref-leaf':['fixture-D']
 };
 const ref={origin:'reference-service',leaf:'ref-leaf',seq,epoch:309,
  channel,available:kind!=='reference-unavailable',graph,
  claimedIndependent:true,authenticated:false};
 if(kind==='stale-reference')ref.seq=seq-1;
 if(kind==='shared-ancestry')graph['ref-leaf']=['fixture-D','fixture-A'];
 if(kind==='relabel-shared'){ref.origin='brand-new-reference';graph['ref-leaf']=['fixture-B'];}
 if(kind==='missing-ancestry')delete graph['fixture-D'];
 return ref;
}
function wag312Trace(graph,leaf){
 const roots=new Set(),seen=new Set(),stack=new Set();
 function visit(k){
  if(stack.has(k))throw Error('CYCLIC_REFERENCE');
  if(!Object.prototype.hasOwnProperty.call(graph,k))throw Error('MISSING_PARENT');
  if(seen.has(k))return;
  stack.add(k);
  const parents=graph[k];
  if(!Array.isArray(parents))throw Error('INVALID_PARENT_SET');
  if(!parents.length)roots.add(k);
  for(const p of parents)visit(p);
  stack.delete(k);seen.add(k);
 }
 visit(leaf);
 return Object.freeze([...roots].sort());
}
function wag312External(observation,reference,expectedSeq){
 let roots=[],traceError=null;
 try{roots=wag312Trace(reference.graph,reference.leaf)}
 catch(e){traceError=e.message}
 const sourceRoots=['fixture-A','fixture-B','fixture-C'];
 const rootCollision=roots.some(k=>sourceRoots.includes(k));
 const independent=!!roots.length&&!rootCollision&&!traceError;
 const fresh=reference.seq===expectedSeq&&reference.epoch===309;
 const available=reference.available&&Number.isInteger(reference.channel)&&reference.channel>=0&&reference.channel<8;
 const trustedPacket=observation.trusted&&observation.unanimous&&observation.candidate!==null;
 const agrees=trustedPacket&&available&&observation.candidate===reference.channel;
 const allow=trustedPacket&&available&&fresh&&independent&&agrees;
 return Object.freeze({
  candidate:allow?observation.candidate:null,
  verdict:!trustedPacket?'SIGNED_PACKET_REJECTED':!available?'REFERENCE_MISSING':
   !fresh?'STALE_REFERENCE':traceError?'BROKEN_REFERENCE_LINEAGE':
   rootCollision?'SHARED_ANCESTRY':
   !agrees?'REFERENCE_CONFLICT':'UNAUTHENTICATED_REFERENCE_MATCH',
  roots,traceError,rootCollision,independentFixtureRoots:independent,
  referenceFresh:fresh,referenceAuthenticated:false,
  signerOriginAuthenticated:false,truthVerified:false,
  promotionAuthorized:false
 });
}
async function wag312Trial(kind,seq){
 const observed=await wag309Trial(kind.startsWith('signed-false')||kind==='correlated-false-reference'?
  'signed-false-observation':'clean',seq);
 const reference=wag312Reference(kind,seq);
 const decision=wag312External(observed,reference,seq);
 return {kind,seq,reference,observed,decision,
  syntheticTruth:kind.startsWith('signed-false')||kind==='correlated-false-reference'?4:3};
}
async function wag312Evaluate(source){
 const before=JSON.stringify(source),rows=[];
 for(const kind of WAG312.cases){
  let correct=0,wrong=0,abstain=0,ancestryRejected=0,staleRejected=0;
  for(let seq=0;seq<8;seq++){
   const x=await wag312Trial(kind,seq);
   const d=x.decision;
   if(d.rootCollision||d.traceError)ancestryRejected++;
   if(!d.referenceFresh)staleRejected++;
   if(d.candidate===null)abstain++;
   else if(d.candidate===x.syntheticTruth)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,ancestryRejected,staleRejected,total:8});
 }
 if(JSON.stringify(source)!==before)throw Error('authority state mutated');
 return wag291DeepFreeze({bound:'WAG-312',phase:'VII',turn:1,rows,testCases:72,
  referenceAttested:false,controllerPromoted:false,physicalActions:0,
  limitation:'An unverified independently labelled reference can agree with validly signed false evidence.'});
}
async function wag312Audit(){
 const source=wag288Initial(),snapshot=JSON.stringify(source);
 const a=await wag312Evaluate(source),b=await wag312Evaluate(source),get=k=>a.rows.find(r=>r.kind===k);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  sourceUnchanged:JSON.stringify(source)===snapshot,
  nineScenarios:a.rows.length===9&&a.testCases===72,
  accounting:a.rows.every(r=>r.correct+r.wrong+r.abstain===8),
  cleanAgreement:get('clean').correct===8,
  staleRejected:get('stale-reference').abstain===8,
  sharedAncestryRejected:get('shared-ancestry').ancestryRejected===8&&get('shared-ancestry').abstain===8,
  relabelCannotEscape:get('relabel-shared').abstain===8,
  missingAncestryRejected:get('missing-ancestry').abstain===8,
  corruptReferenceWithheld:get('corrupt-reference').abstain===8,
  signedFalseCorrectReferenceWithheld:get('signed-false-correct-reference').abstain===8,
  correlatedFalseCounterexample:get('correlated-false-reference').wrong===8,
  unavailableReferenceWithheld:get('reference-unavailable').abstain===8,
  unsanctionedTruthNeverClaimed:!a.referenceAttested&&!a.controllerPromoted,
  readOnlyAndNoActions:a.physicalActions===0,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  oneFrontalAddress:wag289Groups().frontal.length===1,
  phaseVIHandoff:WAG311.phase==='VI'&&WAG311.turn===8
 };
 return {bound:'WAG-312',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,phaseProgress:1/8};
}
if(typeof module!=='undefined')module.exports={WAG312,wag312Reference,wag312Trace,wag312External,wag312Trial,wag312Evaluate,wag312Audit};
