/* WAG-299 · Perception versus inference · Phase V 4/8 · .dlw
   Independent hidden label is used by the GENERATOR and SCORER only.
   The WAG-298 frontal reader receives only synthesized silo arrays.
   [1], {1}, (1) are nested summaries with common ancestry, NOT 3 witnesses.
   No training, actuation, hidden-label leak, or authority state mutation.
*/
const WAG299=Object.freeze({phase:'V',turn:4,steps:8,
  lightLevels:Object.freeze([0,.25,.5,.75,1]),
  conditions:Object.freeze(['clear','center-misleading','cortex-misleading','both-misleading']),
  labels:8,trials:8,physicalActions:0});
function wag299Stimulus(authority,label,trial,condition){
 const nodes=authority.nodes.map(n=>n.slice());
 const cortex=wag289Groups().cortex,center=62,wrong=(label+1+trial%3)%8;
 for(const i of cortex){
  const confuse=condition==='cortex-misleading'||condition==='both-misleading';
  const winning=confuse?wrong:label;
  for(let ch=0;ch<8;ch++)nodes[i][ch]=ch===winning?.91:.06+((i+ch+trial)%4)*.005;
 }
 const misleading=condition==='center-misleading'||condition==='both-misleading';
 for(let ch=0;ch<8;ch++)nodes[center][ch]=ch===(misleading?wrong:label)?.97:.03;
 return {nodes,tick:authority.tick};
}
function wag299Evaluate(source){
 const original=JSON.stringify(source),cases=[];
 for(const condition of WAG299.conditions)for(const light of WAG299.lightLevels){
  let correct=0,wrong=0,abstain=0,marginSum=0,marginCount=0;
  for(let label=0;label<8;label++)for(let trial=0;trial<8;trial++){
   const observed=wag298Read(wag299Stimulus(source,label,trial,condition),light);
   if(observed.abstain)abstain++;
   else if(observed.candidate===label)correct++;
   else wrong++;
   if(observed.margin!==null){marginSum+=observed.margin;marginCount++;}
  }
  cases.push({condition,light,correct,wrong,abstain,total:64,
    coverage:(correct+wrong)/64,accuracy:correct/64,
    selectiveAccuracy:(correct+wrong)?correct/(correct+wrong):null,
    averageMargin:marginCount?marginSum/marginCount:null});
 }
 if(JSON.stringify(source)!==original)throw Error('authoritative silo source mutated');
 return wag291DeepFreeze({bound:'WAG-299',phase:'V',turn:4,tick:source.tick,
  conditions:WAG299.conditions.slice(),lights:WAG299.lightLevels.slice(),cases,
  sampleCount:cases.length*64,authority:'READ_ONLY',
  ancestry:'Three illuminated forms summarize overlapping 27-site source; not independent confirmations.',
  limitation:'Synthetic planted labels score accuracy; high margin is not proof of correctness.',
  physicalActions:0});
}
function wag299Audit(){
 const source=wag288Initial(),before=JSON.stringify(source);
 const a=wag299Evaluate(source),b=wag299Evaluate(source);
 const by=(condition,light)=>a.cases.find(x=>x.condition===condition&&x.light===light);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  readOnly:JSON.stringify(source)===before,
  twentyCases:a.cases.length===20&&a.sampleCount===1280,
  accounting:a.cases.every(x=>x.correct+x.wrong+x.abstain===64),
  allShadowAbstains:WAG299.conditions.every(c=>by(c,0).abstain===64),
  oneVisibleAbstains:WAG299.conditions.every(c=>by(c,.25).abstain===64),
  clearCandidate:by('clear',.75).correct===64,
  misleadingCounterexample:by('both-misleading',1).wrong===64,
  noDarkScores:(()=>{const x=wag298Read(wag299Stimulus(source,1,0,'clear'),0);return x.evidence.length===0&&x.candidate===null&&x.margin===null})(),
  nonindependenceDeclared:a.ancestry.includes('overlapping'),
  threeFormsOneAddress:WAG298.center===62&&wag289Groups().frontal.length===1,
  evidenceFrozen:Object.isFrozen(a)&&Object.isFrozen(a.cases)&&Object.isFrozen(a.cases[0]),
  previousGate:wag298Audit().pass,
  abstentionNotCorrect:a.cases.every(x=>x.accuracy===x.correct/x.total),
  noActuation:a.physicalActions===0
 };
 return {bound:'WAG-299',checks,pass:Object.values(checks).every(Boolean),
  cases:a.cases,phaseProgress:.5};
}
if(typeof module!=='undefined')module.exports={WAG299,wag299Stimulus,wag299Evaluate,wag299Audit};
