/* WAG-305 · Phase VI 2/8 · Traceable synthetic source ancestry · .dlw
 * Three mutually unaware private interpreters, external ancestry graph.
 * Claimed names are not roots. Follow producer pointers to fixture roots.
 * Reject alias reuse, overlapping ancestry, absent pointers and cycles.
 * Graph is supplied by a deterministic synthetic test harness; it is NOT
 * independently authenticated, tamper-evident, or proof of real origins.
 * Three distinct false sources can still give the same wrong answer.
*/
const WAG305=Object.freeze({
 phase:'VI',turn:2,of:8,physicalActions:0,
 cases:Object.freeze(['independent-clean','relabel-shared','shared-ancestor',
   'missing-lineage','cycle','one-corrupt','all-corrupt']),
 forms:Object.freeze(['[1]','{1}','(1)'])
});
function wag305Fixture(kind){
 const nodes={
  'root-A':{parents:[]},'root-B':{parents:[]},'root-C':{parents:[]},
  'shared-root':{parents:[]},
  'leaf-A':{parents:['root-A']},'leaf-B':{parents:['root-B']},'leaf-C':{parents:['root-C']}
 };
 let leaves=['leaf-A','leaf-B','leaf-C'];
 let claimed=['alice','bob','carol'];
 if(kind==='relabel-shared'){leaves=['leaf-A','leaf-A','leaf-A'];claimed=['alice','bob','carol'];}
 if(kind==='shared-ancestor'){
  nodes['leaf-A']={parents:['root-A','shared-root']};
  nodes['leaf-B']={parents:['root-B','shared-root']};
  nodes['leaf-C']={parents:['root-C']};
 }
 if(kind==='missing-lineage')nodes['leaf-C']={parents:['unknown-parent']};
 if(kind==='cycle'){nodes['leaf-B']={parents:['root-B','leaf-A']};nodes['leaf-A']={parents:['root-A','leaf-B']};}
 return {nodes,leaves,claimed};
}
function wag305Trace(nodes,leaf){
 const roots=new Set(),visiting=new Set(),visited=new Set();
 function walk(id){
  if(visiting.has(id))throw Error('LINEAGE_CYCLE');
  if(visited.has(id))return;
  if(!Object.prototype.hasOwnProperty.call(nodes,id))throw Error('LINEAGE_MISSING');
  visiting.add(id);
  const parents=nodes[id].parents;
  if(!Array.isArray(parents))throw Error('LINEAGE_INVALID');
  if(!parents.length)roots.add(id);
  for(const p of parents)walk(p);
  visiting.delete(id);visited.add(id);
 }
 walk(leaf);
 return Object.freeze({leaf,roots:Object.freeze([...roots].sort())});
}
function wag305External(records,graph){
 // Provenance is held outside each private interpreter's input and claim.
 let traces,problem=null;
 try{traces=records.map(r=>wag305Trace(graph,r.leaf));}
 catch(e){problem=e.message;traces=[];}
 let collision=false;
 for(let i=0;i<traces.length;i++)for(let j=i+1;j<traces.length;j++){
  if(traces[i].roots.some(root=>traces[j].roots.includes(root)))collision=true;
 }
 const distinct=traces.length===3&&!collision&&!problem;
 const eligible=records.length===3&&records.every(x=>x.claim.channel!==null&&!x.claim.uncertain);
 const unanimous=eligible&&records.every(x=>x.claim.channel===records[0].claim.channel);
 return Object.freeze({
  verdict:problem?'INVALID_LINEAGE':!distinct?'SHARED_ANCESTRY_ABSTAIN':
    !eligible?'LOCAL_ABSTAIN':!unanimous?'CONFLICT_ABSTAIN':'SYNTHETIC_CANDIDATE',
  candidate:distinct&&eligible&&unanimous?records[0].claim.channel:null,
  rootsTraced:Object.freeze(traces),distinctRoots:distinct,
  sharedRootCollision:collision,traceError:problem,
  claimsUnanimous:unanimous,verifiedRealWorldOrigin:false,promotionAuthorized:false
 });
}
function wag305Trial(label,trial,kind){
 const fixture=wag305Fixture(kind),records=[];
 const wrongCount=kind==='one-corrupt'?1:kind==='all-corrupt'?3:0;
 for(let i=0;i<3;i++){
  const view=wag304SourceView(label,trial,i<wrongCount);
  // Observer receives ONLY a view, form selected by private interface.
  const claim=wag304Isolated(WAG305.forms[i],view);
  records.push(Object.freeze({form:WAG305.forms[i],displayName:fixture.claimed[i],
    leaf:fixture.leaves[i],claim}));
 }
 return Object.freeze({records:Object.freeze(records),fixture,result:wag305External(records,fixture.nodes)});
}
function wag305Evaluate(authority){
 const prior=JSON.stringify(authority),rows=[];
 for(const kind of WAG305.cases){
  let correct=0,wrong=0,abstain=0,rejected=0,invalid=0,collisions=0;
  for(let label=0;label<8;label++)for(let trial=0;trial<8;trial++){
   const result=wag305Trial(label,trial,kind).result;
   if(!result.distinctRoots)rejected++;
   if(result.traceError)invalid++;
   if(result.sharedRootCollision)collisions++;
   if(result.candidate===null)abstain++;else if(result.candidate===label)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,rejected,invalid,collisions,total:64});
 }
 if(JSON.stringify(authority)!==prior)throw Error('authoritative silos mutated');
 return wag291DeepFreeze({bound:'WAG-305',phase:'VI',turn:2,rows,total:rows.length*64,
  accepted:false,provenance:'Fixture graph supplies ancestry assertions; no external attestation',
  physicalActions:0});
}
function wag305Audit(){
 const state=wag288Initial(),before=JSON.stringify(state),a=wag305Evaluate(state),
 b=wag305Evaluate(state),get=k=>a.rows.find(r=>r.kind===k);
 const renamed=wag305Trial(2,0,'relabel-shared');
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  readOnly:JSON.stringify(state)===before,
  sevenScenarios:a.rows.length===7&&a.total===448,
  exactAccounts:a.rows.every(r=>r.correct+r.wrong+r.abstain===64),
  independentClean:get('independent-clean').correct===64,
  misleadingAliasesRejected:get('relabel-shared').rejected===64&&get('relabel-shared').abstain===64,
  sameLeafCollision:renamed.result.sharedRootCollision,
  sharedParentRejected:get('shared-ancestor').rejected===64,
  incompleteLineageRejected:get('missing-lineage').invalid===64,
  cycleRejected:get('cycle').invalid===64,
  singleCorruptionAbstains:get('one-corrupt').abstain===64,
  coordinatedWrongRetained:get('all-corrupt').wrong===64,
  blindForms:WAG305.forms.join('|')==='[1]|{1}|(1)',
  ancestryOutsideClaim:renamed.records.every(r=>!('leaf' in r.claim)&&!('displayName' in r.claim)),
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  fixtureNotAuthenticated:wag305Trial(1,0,'independent-clean').result.verifiedRealWorldOrigin===false,
  previousBound:wag304Audit().pass,
  zeroActuation:a.physicalActions===0
 };
 return {bound:'WAG-305',pass:Object.values(checks).every(Boolean),checks,
  rows:a.rows,phaseProgress:.25};
}
if(typeof module!=='undefined')module.exports={WAG305,wag305Fixture,wag305Trace,wag305External,wag305Trial,wag305Evaluate,wag305Audit};
