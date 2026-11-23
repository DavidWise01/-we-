/* WAG-302 · local error recognition · Phase V 7/8 · .dlw
 Each interpreter receives only its own view, and never sees peer claims.
 The external aggregator receives sealed local claims/statuses only.
 No security sandbox or independent ancestry is implied.
*/
const WAG302=Object.freeze({phase:'V',turn:7,planned:8,
 localMargin:.14,localConsensus:.65,
 kinds:Object.freeze(['clear','frontal-corrupt','cortex-corrupt','both-corrupt','ambiguous','split-cortex']),
 physicalActions:0});
function wag302Box(vector){
 const c=wag301Box(vector);
 const uncertain=c.margin<WAG302.localMargin;
 return Object.freeze({...c,uncertain,channel:uncertain?null:c.channel,reason:uncertain?'LOW_LOCAL_MARGIN':'LOCALLY_DECISIVE'});
}
function wag302Brace(vectors){
 const c=wag301Brace(vectors);
 const votes=Array(8).fill(0);
 for(const v of vectors)votes[wag301Choose(v).channel]++;
 const agreement=Math.max(...votes)/vectors.length;
 const uncertain=c.margin<WAG302.localMargin||agreement<WAG302.localConsensus;
 return Object.freeze({...c,agreement,uncertain,channel:uncertain?null:c.channel,reason:uncertain?'WEAK_OR_SPLIT_LOCAL_EVIDENCE':'LOCALLY_DECISIVE'});
}
function wag302Toroid(vectors){
 const c=wag301Toroid(vectors);
 const votes=Array(8).fill(0);
 for(const v of vectors)votes[wag301Choose(v).channel]++;
 const agreement=Math.max(...votes)/vectors.length;
 const uncertain=c.margin<WAG302.localMargin||agreement<WAG302.localConsensus;
 return Object.freeze({...c,agreement,uncertain,channel:uncertain?null:c.channel,reason:uncertain?'WEAK_OR_SPLIT_LOCAL_EVIDENCE':'LOCALLY_DECISIVE'});
}
function wag302Observe(source,light){
 if(!Number.isFinite(light)||light<0||light>1)throw Error('invalid illumination');
 const g=wag289Groups(),claims=[];
 if(light>=.25)claims.push(wag302Box(source.nodes[62].slice()));
 if(light>=.5)claims.push(wag302Brace(g.cortex.concat(g.frontal).map(i=>source.nodes[i].slice())));
 if(light>=.75)claims.push(wag302Toroid(g.cortex.map(i=>source.nodes[i].slice())));
 const ready=claims.length===3&&claims.every(c=>!c.uncertain);
 const unanimous=ready&&claims.every(c=>c.channel===claims[0].channel);
 const decision=Object.freeze({candidate:unanimous?claims[0].channel:null,
  verdict:claims.length<3?'INCOMPLETE':!ready?'LOCAL_UNCERTAINTY_ABSTAIN':unanimous?'CORRELATED_AGREEMENT':'CONFLICT_ABSTAIN',
  sharedAncestryRoots:claims.length?1:0,promotionAuthorized:false});
 return wag291DeepFreeze({light,claims,decision});
}
function wag302Stimulus(source,label,kind,trial){
 const a=wag301Scenario(source,label,kind==='ambiguous'||kind==='split-cortex'?'clear':kind,trial);
 if(kind==='ambiguous'){
  for(const i of wag289Groups().cortex.concat([62]))a.nodes[i]=Array(8).fill(.48);
 }
 if(kind==='split-cortex'){
  const other=(label+1)%8,ids=wag289Groups().cortex;
  ids.forEach((id,k)=>{const chosen=k<13?label:other;
   for(let ch=0;ch<8;ch++)a.nodes[id][ch]=ch===chosen?.91:.06;
  });
 }
 return a;
}
function wag302Evaluate(source){
 const before=JSON.stringify(source),rows=[];
 for(const kind of WAG302.kinds){
  let correct=0,wrong=0,abstain=0,uncertainty=0,conflict=0;
  for(let label=0;label<8;label++)for(let trial=0;trial<8;trial++){
   const result=wag302Observe(wag302Stimulus(source,label,kind,trial),1);
   if(result.decision.verdict==='LOCAL_UNCERTAINTY_ABSTAIN')uncertainty++;
   if(result.decision.verdict==='CONFLICT_ABSTAIN')conflict++;
   const p=result.decision.candidate;
   if(p===null)abstain++;else if(p===label)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,uncertainty,conflict,total:64});
 }
 if(JSON.stringify(source)!==before)throw Error('authoritative state modified');
 return wag291DeepFreeze({bound:'WAG-302',tick:source.tick,rows,
  caveat:'Coordinated corruption can still fool all local confidence gates; no independent ground truth',
  ancestry:'One underlying 125-node source, not three independent roots',
  physicalActions:0,authority:'READ_ONLY'});
}
function wag302Audit(){
 const s=wag288Initial(),snap=JSON.stringify(s),a=wag302Evaluate(s),b=wag302Evaluate(s);
 const get=k=>a.rows.find(x=>x.kind===k);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  readOnly:JSON.stringify(s)===snap,
  sixCases:a.rows.length===6,
  accounting:a.rows.every(x=>x.correct+x.wrong+x.abstain===64),
  clearWorks:get('clear').correct===64,
  ambiguityAbstains:get('ambiguous').abstain===64,
  frontalConflictWithheld:get('frontal-corrupt').abstain===64,
  cortexConflictWithheld:get('cortex-corrupt').abstain===64,
  coordinatedFalseConsensusExposed:get('both-corrupt').wrong===64,
  darknessAbstains:wag302Observe(s,0).decision.candidate===null,
  threeAlgorithms:new Set([wag302Box.name,wag302Brace.name,wag302Toroid.name]).size===3,
  localNoPeerAccess:[wag302Box,wag302Brace,wag302Toroid].every(f=>!f.toString().includes('wag302Observe(')),
  sharedRootRecorded:wag302Observe(s,1).decision.sharedAncestryRoots===1,
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
  previousPass:wag301Audit().pass,
  noActuation:a.physicalActions===0
 };
 return {bound:'WAG-302',pass:Object.values(checks).every(Boolean),checks,rows:a.rows,phaseProgress:7/8};
}
if(typeof module!=='undefined')module.exports={WAG302,wag302Box,wag302Brace,wag302Toroid,wag302Observe,wag302Stimulus,wag302Evaluate,wag302Audit};
