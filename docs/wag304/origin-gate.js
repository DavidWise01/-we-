/* WAG-304 · Phase VI 1/8 · Origin-aware external evidence gate · .dlw
 Three private form algorithms (box, brace, toroid) receive independent
 synthetic inputs. The external router owns origin records. Interpreters
 neither receive nor know the other forms, root IDs, or any verdict.
 Root IDs are TEST-FIXTURE assertions, not cryptographic authentication.
 Three different labels alone never prove independent real-world sources.
 Research-only: no promotion or physical action.
*/
const WAG304=Object.freeze({phase:'VI',turn:1,of:8,
 forms:Object.freeze(['[1]','{1}','(1)']),
 roots:Object.freeze(['fixture-A','fixture-B','fixture-C']),
 cases:Object.freeze(['three-clean','one-corrupt','two-corrupt','all-corrupt','shared-root','missing-root']),
 minDistinctRoots:3,physicalActions:0});
function wag304SourceView(label,trial,altered){
 const wrong=(label+1+trial%3)%8;
 const channel=altered?wrong:label;
 const row=(site)=>Array.from({length:8},(_,c)=>c===channel?.94:.04+((site*7+c+trial)%4)*.003);
 return Object.freeze({center:Object.freeze(row(62)),cortex:Object.freeze(Array.from({length:26},(_,j)=>Object.freeze(row(j+1))))});
}
function wag304Isolated(form,privateInput){
 // Critically no roots, peers, target or adjudicator are passed here.
 if(form==='[1]')return wag302Box(privateInput.center.slice());
 if(form==='{1}')return wag302Brace(privateInput.cortex.map(x=>x.slice()).concat([privateInput.center.slice()]));
 if(form==='(1)')return wag302Toroid(privateInput.cortex.map(x=>x.slice()));
 throw Error('unknown private form');
}
function wag304External(claimRecords){
 const allPresent=claimRecords.length===3&&claimRecords.every(r=>typeof r.origin==='string'&&r.origin.length>0);
 const uniqueOrigins=new Set(claimRecords.map(r=>r.origin));
 const separate=allPresent&&uniqueOrigins.size>=WAG304.minDistinctRoots;
 const decisive=allPresent&&claimRecords.every(r=>!r.claim.uncertain&&r.claim.channel!==null);
 const unanimous=decisive&&claimRecords.every(r=>r.claim.channel===claimRecords[0].claim.channel);
 const candidate=separate&&unanimous?claimRecords[0].claim.channel:null;
 return Object.freeze({
  candidate,
  decision:candidate===null?'ABSTAIN':'SYNTHETIC_CANDIDATE_ONLY',
  distinctDeclaredOrigins:uniqueOrigins.size,
  sourceOriginGate:separate,localGate:decisive,unanimous,
  promotionAuthorized:false
 });
}
function wag304Trial(label,trial,scenario){
 const roots=scenario==='shared-root'?['fixture-A','fixture-A','fixture-A']:
  scenario==='missing-root'?['fixture-A','fixture-B',null]:WAG304.roots;
 const wrongCount=scenario==='one-corrupt'?1:scenario==='two-corrupt'?2:scenario==='all-corrupt'?3:0;
 const records=[];
 for(let i=0;i<3;i++){
  const view=wag304SourceView(label,trial,i<wrongCount);
  const claim=wag304Isolated(WAG304.forms[i],view);
  records.push(Object.freeze({form:WAG304.forms[i],origin:roots[i],claim}));
 }
 return Object.freeze({records:Object.freeze(records),result:wag304External(records)});
}
function wag304Evaluate(authority){
 const before=JSON.stringify(authority),rows=[];
 for(const scenario of WAG304.cases){
  let correct=0,wrong=0,abstain=0,originRejected=0,conflicted=0;
  for(let label=0;label<8;label++)for(let trial=0;trial<8;trial++){
   const t=wag304Trial(label,trial,scenario),r=t.result;
   if(!r.sourceOriginGate)originRejected++;
   if(r.sourceOriginGate&&!r.unanimous)conflicted++;
   if(r.candidate===null)abstain++;else if(r.candidate===label)correct++;else wrong++;
  }
  rows.push({scenario,correct,wrong,abstain,originRejected,conflicted,total:64});
 }
 if(JSON.stringify(authority)!==before)throw Error('authoritative state mutated');
 return wag291DeepFreeze({bound:'WAG-304',phase:'VI',turn:1,tick:authority.tick,
  rows,simulatedObservations:384,authority:'READ_ONLY',physicalActions:0,
  provenance:'Explicit distinct synthetic generator roots, not externally authenticated origins',
  accepted:false,limitation:'Three correlated false readings with different declared roots can still agree incorrectly'});
}
function wag304Audit(){
 const source=wag288Initial(),snap=JSON.stringify(source),
  a=wag304Evaluate(source),b=wag304Evaluate(source),find=x=>a.rows.find(r=>r.scenario===x);
 const claims=wag304Trial(3,1,'three-clean');
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  readOnly:JSON.stringify(source)===snap,
  threeForms:WAG304.forms.join('|')==='[1]|{1}|(1)',
  threePrivateRoutines:WAG304.forms.every(f=>typeof wag304Isolated(f,wag304SourceView(2,0,false)).channel==='number'),
  privateNoRootInput:!wag304Isolated.toString().includes('privateInput.origin'),
  sixCases:a.rows.length===6,
  accounting:a.rows.every(r=>r.correct+r.wrong+r.abstain===64),
  cleanCorrect:find('three-clean').correct===64,
  singleCorruptionAbstains:find('one-corrupt').abstain===64,
  doubleCorruptionAbstains:find('two-corrupt').abstain===64,
  falseConsensusRetained:find('all-corrupt').wrong===64,
  sharedOriginRejected:find('shared-root').originRejected===64&&find('shared-root').abstain===64,
  missingOriginRejected:find('missing-root').originRejected===64&&find('missing-root').abstain===64,
  noPromotion:claims.result.promotionAuthorized===false&&a.accepted===false,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  oneFrontalAddress:wag289Groups().frontal.length===1,
  previousPhaseClosed:wag303Audit().pass,
  noActions:a.physicalActions===0
 };
 return {bound:'WAG-304',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,
  phaseProgress:1/8};
}
if(typeof module!=='undefined')module.exports={WAG304,wag304SourceView,wag304Isolated,wag304External,wag304Trial,wag304Evaluate,wag304Audit};
