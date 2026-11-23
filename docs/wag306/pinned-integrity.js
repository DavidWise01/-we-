/* WAG-306 · Phase VI 3/8 · pinned provenance reference · .dlw
 * Sources remain private to [1], {1}, (1). Provenance is external only.
 * TEST-ONLY integrity check: deterministic FNV-1a fingerprint compared to
 * a separately held, frozen manifest representing a pinned baseline.
 * FNV is NOT a cryptographic MAC/signature and no real authentication occurs.
 * If the trusted manifest is replaced too, an internally consistent forgery
 * passes the weak integrity gate. Explicit counterexample below.
 */
const WAG306=Object.freeze({phase:'VI',turn:3,of:8,
 scenarios:Object.freeze(['clean','alias-only','parent-tamper','root-substitution',
 'forged-rehash','missing-leaf','registry-compromised','all-corrupt']),
 forms:Object.freeze(['[1]','{1}','(1)']),physicalActions:0});
function wag306Canonical(graph){
 const keys=Object.keys(graph).sort();
 return keys.map(k=>k+':'+JSON.stringify(graph[k].parents.slice().sort())).join('|');
}
function wag306Digest(input){
 // Deliberately lightweight fingerprint, NOT cryptographic authentication.
 let h=2166136261;
 for(let i=0;i<input.length;i++){h^=input.charCodeAt(i);h=Math.imul(h,16777619);}
 return ('00000000'+(h>>>0).toString(16)).slice(-8);
}
function wag306Manifest(graph){
 return Object.freeze({fingerprint:wag306Digest(wag306Canonical(graph)),
  expectedLeaves:Object.freeze(['leaf-A','leaf-B','leaf-C']),
  trustClass:'TEST_FIXTURE_PIN'});
}
const WAG306_BASELINE=wag291DeepFreeze(wag306Manifest(wag305Fixture('independent-clean').nodes));
function wag306Fixture(scenario){
 const clean=wag305Fixture('independent-clean');
 const graph=JSON.parse(JSON.stringify(clean.nodes));
 const leaves=clean.leaves.slice();
 const aliases=clean.claimed.slice();
 if(scenario==='alias-only')aliases.splice(0,3,'renamed-1','renamed-2','renamed-3');
 if(['parent-tamper','forged-rehash','registry-compromised'].includes(scenario)){
   graph['leaf-B'].parents=['root-A'];
 }
 if(scenario==='root-substitution'){graph['leaf-C'].parents=['root-B'];}
 if(scenario==='missing-leaf'){delete graph['leaf-C'];}
 let claimedDigest=wag306Digest(wag306Canonical(graph));
 let trustedManifest=WAG306_BASELINE;
 if(scenario==='registry-compromised')trustedManifest=wag306Manifest(graph);
 return {graph,leaves,aliases,claimedDigest,trustedManifest};
}
function wag306External(records,fixture){
 const recomputed=wag306Digest(wag306Canonical(fixture.graph));
 const selfConsistent=fixture.claimedDigest===recomputed;
 const pinMatches=recomputed===fixture.trustedManifest.fingerprint;
 const leafMatches=records.length===3&&records.every((r,i)=>r.leaf===fixture.trustedManifest.expectedLeaves[i]);
 const integrity=selfConsistent&&pinMatches&&leafMatches;
 const prior=wag305External(records,fixture.graph);
 const accepted=integrity&&prior.candidate!==null;
 return Object.freeze({candidate:accepted?prior.candidate:null,
  verdict:!selfConsistent?'SELF_CHECK_FAILED':!pinMatches?'PIN_MISMATCH':
   !leafMatches?'LEAF_MISMATCH':prior.verdict,
  integrity, selfConsistent,pinMatches,leafMatches,
  traceError:prior.traceError,sharedRootCollision:prior.sharedRootCollision,
  distinctRoots:prior.distinctRoots,rootTraces:prior.rootsTraced,
  verifiedRealWorldOrigin:false,cryptographicallyAuthenticated:false,
  promotionAuthorized:false});
}
function wag306Trial(label,trial,scenario){
 const fixture=wag306Fixture(scenario);
 const records=fixture.leaves.map((leaf,i)=>{
  const corrupted=scenario==='all-corrupt';
  return Object.freeze({form:WAG306.forms[i],leaf,displayName:fixture.aliases[i],
    claim:wag304Isolated(WAG306.forms[i],wag304SourceView(label,trial,corrupted))});
 });
 return Object.freeze({fixture,records:Object.freeze(records),
  result:wag306External(records,fixture)});
}
function wag306Evaluate(authority){
 const snap=JSON.stringify(authority),rows=[];
 for(const scenario of WAG306.scenarios){
  let correct=0,wrong=0,abstain=0,pinRejected=0,forgeryPassed=0;
  for(let label=0;label<8;label++)for(let trial=0;trial<8;trial++){
   const r=wag306Trial(label,trial,scenario).result;
   if(!r.pinMatches)pinRejected++;
   if(scenario==='registry-compromised'&&r.integrity)forgeryPassed++;
   if(r.candidate===null)abstain++;else if(r.candidate===label)correct++;else wrong++;
  }
  rows.push({scenario,correct,wrong,abstain,pinRejected,forgeryPassed,total:64});
 }
 if(JSON.stringify(authority)!==snap)throw Error('WAG306 mutated original state');
 return wag291DeepFreeze({bound:'WAG-306',phase:'VI',turn:3,rows,
  simulatedCases:rows.length*64,pinnedManifest:WAG306_BASELINE,
  physicalActions:0,accepted:false,
  limitation:'Fingerprint only. A compromised trust registry or coordinated false data can still pass.'});
}
function wag306Audit(){
 const s=wag288Initial(),snap=JSON.stringify(s),a=wag306Evaluate(s),b=wag306Evaluate(s);
 const f=k=>a.rows.find(r=>r.scenario===k);
 const forged=wag306Trial(3,0,'forged-rehash'),comp=wag306Trial(3,0,'registry-compromised');
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  readOnly:JSON.stringify(s)===snap,
  exactGeometry:wag289Groups().frontal.length===1&&WAG306.forms.join('|')==='[1]|{1}|(1)',
  eightScenarios:a.rows.length===8&&a.simulatedCases===512,
  completeAccounting:a.rows.every(r=>r.correct+r.wrong+r.abstain===64),
  cleanCorrect:f('clean').correct===64,
  aliasesDoNotMatter:f('alias-only').correct===64,
  parentTamperRejected:f('parent-tamper').pinRejected===64,
  rootSwapRejected:f('root-substitution').pinRejected===64,
  forgedSelfHashFailsPin:forged.result.selfConsistent&&!forged.result.pinMatches,
  missingLeafRejected:f('missing-leaf').pinRejected===64,
  manifestCompromiseVisible:comp.result.integrity&&f('registry-compromised').forgeryPassed===64,
  coordinatedFalseConsensus:f('all-corrupt').wrong===64,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0])&&Object.isFrozen(WAG306_BASELINE),
  noRootInfoInPrivateClaim:comp.records.every(x=>!('leaf' in x.claim)&&!('displayName' in x.claim)),
  noCryptoClaims:comp.result.cryptographicallyAuthenticated===false,
  previousPass:wag305Audit().pass,
  noActuation:a.physicalActions===0
 };
 return {bound:'WAG-306',pass:Object.values(checks).every(Boolean),checks,
  results:a.rows,phaseProgress:3/8};
}
if(typeof module!=='undefined')module.exports={WAG306,WAG306_BASELINE,wag306Canonical,wag306Digest,wag306Manifest,wag306Fixture,wag306External,wag306Trial,wag306Evaluate,wag306Audit};
