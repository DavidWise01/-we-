/* WAG-300 · blind truth sources · .dlw
  Three isolated observers are intentionally unaware of other observers.
  Their inputs are distinct views, not independent evidence ancestry:
  all derive from the SAME authoritative 125-address snapshot.
  Only an external read-only adjudicator compares claims.
  Do not confuse observer ignorance with source independence.
*/
const WAG300=Object.freeze({forms:Object.freeze(['[1]','{1}','(1)']),
 scopes:Object.freeze(['frontal-local','cortex-inclusive','cortex-shell']),
 lightThresholds:Object.freeze([.25,.5,.75]),
 center:62,physicalActions:0,authority:'OBSERVE_ONLY'});
function wag300Claim(form,input){
 // This function cannot access other forms, their outputs or the adjudicator.
 if(!WAG300.forms.includes(form)||!Array.isArray(input)||input.length!==8)throw Error('invalid isolated input');
 const scores=input.slice(),ordered=scores.map((v,i)=>({v,i})).sort((a,b)=>b.v-a.v||a.i-b.i);
 return Object.freeze({form,channel:ordered[0].i,margin:ordered[0].v-ordered[1].v,
  score:ordered[0].v,belief:'LOCAL_TRUTH_CLAIM'});
}
function wag300Views(state,level){
 if(!Number.isFinite(level)||level<0||level>1)throw Error('invalid illumination');
 const cortex=wag289Groups().cortex,frames=[];
 const avg=ids=>Array.from({length:8},(_,j)=>ids.reduce((s,i)=>s+state.nodes[i][j],0)/ids.length);
 for(let i=0;i<3;i++)if(level>=WAG300.lightThresholds[i]){
  // Each call creates an isolated value snapshot. No observer handles another.
  const input=i===0?state.nodes[62].slice():i===1?avg(cortex.concat([62])):avg(cortex);
  frames.push({form:WAG300.forms[i],input});
 }
 return frames;
}
function wag300Adjudicate(claims){
 // External only. Shared root means three agreeing claims cannot be counted
 // as three independent confirmations; disagreement must remain visible.
 const channels=claims.map(c=>c.channel);
 const agreement=channels.length>0&&channels.every(v=>v===channels[0]);
 return Object.freeze({candidate:claims.length===3&&agreement?channels[0]:null,
  unanimous:claims.length===3&&agreement,
  count:claims.length,conflict:channels.length>1&&!agreement,
  independentRoots:claims.length?1:0,
  verdict:claims.length<3?'INCOMPLETE':agreement?'CORRELATED_AGREEMENT':'CONFLICT_ABSTAIN',
  promotionAuthorized:false});
}
function wag300Observe(state,light){
 const frames=wag300Views(state,light);
 const claims=frames.map(v=>wag300Claim(v.form,v.input));
 return Object.freeze({light,claims:Object.freeze(claims),
  adjudication:wag300Adjudicate(claims)});
}
function wag300Audit(){
 const state=wag288Initial(),baseline=JSON.stringify(state),
 dark=wag300Observe(state,0),full=wag300Observe(state,1);
 const claimSrc=wag300Claim.toString();
 const views=wag300Views(state,1);
 const mutated=state.nodes.map(v=>v.slice());mutated[62]=Array(8).fill(0);mutated[62][7]=1;
 const checks={
  threeDistinctForms:new Set(WAG300.forms).size===3,
  centerOneAddress:WAG300.center===62&&wag289Groups().frontal.length===1,
  isolatedFunctionInputs:!claimSrc.includes('state.nodes')&&!claimSrc.includes('wag300Adjudicate('),
  independentSnapshots:views.every((v,i)=>views.every((w,j)=>i===j||v.input!==w.input)),
  noCrossDisclosure:full.claims.every(c=>!('otherClaims' in c)&&!('peerCount' in c)),
  darknessNoClaims:dark.claims.length===0&&dark.adjudication.candidate===null,
  threeAtFull:full.claims.length===3,
  sharedRootCount:full.adjudication.independentRoots===1,
  conflictVeto:wag300Adjudicate([Object.freeze({channel:0}),Object.freeze({channel:1}),Object.freeze({channel:0})]).candidate===null,
  unanimousNotIndependent:wag300Adjudicate([Object.freeze({channel:2}),Object.freeze({channel:2}),Object.freeze({channel:2})]).verdict==='CORRELATED_AGREEMENT',
  sourceImmutable:JSON.stringify(state)===baseline,
  claimImmutable:Object.isFrozen(full.claims[0])&&Object.isFrozen(full.claims),
  priorPass:wag299Audit().pass,
  noActions:WAG300.physicalActions===0
 };
 return {bound:'WAG-300',pass:Object.values(checks).every(Boolean),checks,
  example:{dark:dark.adjudication,full:full.adjudication},
  limitation:'Operator isolation is enforced by inputs and API structure, not a security sandbox; source ancestry remains shared'};
}
if(typeof module!=='undefined')module.exports={WAG300,wag300Claim,wag300Views,wag300Adjudicate,wag300Observe,wag300Audit};
