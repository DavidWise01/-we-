/* WAG-294 · localized damage & redundant quartz-shell recovery · .dlw
   Synthetic target replicated to six predeclared, independent shell anchors.
   No target access at inference. Absence of sufficient agreement => ABSTAIN.
   This cannot detect coordinated corruption of >=4/6 anchors.
   All experiments operate on copies; no authoritative state updates.
*/
const WAG294=Object.freeze({
 anchors:Object.freeze([wag288Index(0,2,2),wag288Index(4,2,2),wag288Index(2,0,2),
  wag288Index(2,4,2),wag288Index(2,2,0),wag288Index(2,2,4)]),
 scenarios:Object.freeze(['intact','center-damaged','cortex-damaged','both-damaged',
 'both-missing-anchors','both-two-bad-anchors','both-four-bad-anchors','both-five-bad-anchors']),
 minAnchorVotes:5,targets:8,trials:8,physicalActions:0
});
function wag294Stimulus(source,target,scenario,trial){
 const base=wag293Stimulus(source,target,
  scenario.startsWith('both')?'both-damaged':scenario,trial);
 const nodes=base.nodes.map(v=>v.slice()),wrong=(target+1+trial%3)%8;
 for(let k=0;k<6;k++){
  const id=WAG294.anchors[k],arr=nodes[id];
  for(let ch=0;ch<8;ch++)arr[ch]=ch===target?.92:.08;
  if(scenario==='both-missing-anchors')for(let ch=0;ch<8;ch++)arr[ch]=.5;
  if((scenario==='both-two-bad-anchors'&&k<2)||
     (scenario==='both-four-bad-anchors'&&k<4)||
     (scenario==='both-five-bad-anchors'&&k<5)){
    arr[target]=.06;arr[wrong]=.96;
  }
 }
 return {...source,nodes};
}
function wag294Infer(state){
 const shell=wag289Groups().cortex;
 const cortex=Array.from({length:8},(_,ch)=>shell.reduce((acc,i)=>acc+state.nodes[i][ch],0)/26);
 const central=state.nodes[62],localC=wag293Argmax(central),localK=wag293Argmax(cortex);
 const votes=Array(8).fill(0),valid=[];
 for(const id of WAG294.anchors){
  const values=state.nodes[id],top=wag293Argmax(values);
  const sorted=values.slice().sort((a,b)=>b-a);
  if(sorted[0]-sorted[1]>=.4){votes[top]++;valid.push({id,channel:top});}
 }
 const winner=wag293Argmax(votes),agreement=votes[winner],rival=Math.max(...votes.filter((_,i)=>i!==winner));
 const canRecover=agreement>=WAG294.minAnchorVotes&&agreement>rival;
 return {channel:canRecover?winner:null,abstain:!canRecover,
  cortexChannel:localK,frontalChannel:localC,
  localized:{frontalDisagrees:canRecover&&localC!==winner,
    cortexDisagrees:canRecover&&localK!==winner},
  anchorVotes:votes,usableAnchors:valid.length,agreeingAnchors:agreement,
  authority:'OBSERVATION_ONLY'};
}
function wag294Evaluate(source){
 const before=JSON.stringify(source),scenarios=[];
 for(const scenario of WAG294.scenarios){
  let correct=0,incorrect=0,abstained=0,frontalFlag=0,cortexFlag=0;
  for(let target=0;target<8;target++)for(let trial=0;trial<8;trial++){
   const state=wag294Stimulus(source,target,scenario,trial);
   const p=wag294Infer(state);
   if(p.abstain)abstained++;else if(p.channel===target)correct++;else incorrect++;
   if(p.localized.frontalDisagrees)frontalFlag++;
   if(p.localized.cortexDisagrees)cortexFlag++;
  }
  scenarios.push({scenario,correct,incorrect,abstained,total:64,
    coverage:(correct+incorrect)/64,unconditionalAccuracy:correct/64,
    selectiveAccuracy:(correct+incorrect)?correct/(correct+incorrect):null,
    frontalFlag,cortexFlag});
 }
 if(JSON.stringify(source)!==before)throw Error('authoritative memory was altered');
 return wag291DeepFreeze({bound:'WAG-294',tick:source.tick,
  config:{anchorIds:WAG294.anchors.slice(),requiredVotes:WAG294.minAnchorVotes,
    signalChannels:8,scenarioCount:8,trialsPerScenario:64},
  scenarios,limitations:'Injected independent replicas at six trusted, fixed shell addresses; coordinated 5/6 anchor corruption can generate a false consensus',
  authority:'READ_ONLY',physicalActions:0});
}
function wag294LedgerAppend(ledger,receipt){
 if(!Object.isFrozen(receipt)||receipt.bound!=='WAG-294')throw Error('invalid receipt');
 if(ledger.length&&receipt.tick<ledger[ledger.length-1].tick)throw Error('non-monotone tick');
 return Object.freeze([...ledger,receipt]);
}
function wag294Audit(){
 const source=wag288Initial(),snapshot=JSON.stringify(source),a=wag294Evaluate(source),b=wag294Evaluate(source);
 const check={
 deterministic:JSON.stringify(a)===JSON.stringify(b),
 readOnly:JSON.stringify(source)===snapshot,
 sixDistinctOuterAnchors:new Set(WAG294.anchors).size===6&&WAG294.anchors.every(i=>wag289Role(i)==='quartz'),
 eightScenarios:a.scenarios.length===8&&a.scenarios.every(s=>s.total===64),
 intactRecovered:a.scenarios[0].correct===64,
 centerDamageRecovered:a.scenarios[1].correct===64,
 cortexDamageRecovered:a.scenarios[2].correct===64,
 combinedRecovered:a.scenarios[3].correct===64,
 missingAnchorsAbstain:a.scenarios[4].abstained===64,
 twoCorruptAnchorsAbstain:a.scenarios[5].abstained===64,
 fourCorruptAnchorsAbstain:a.scenarios[6].abstained===64,
 fiveCorruptAnchorsFailureExposed:a.scenarios[7].incorrect===64,
 localizeCenter:wag294Infer(wag294Stimulus(source,2,'center-damaged',0)).localized.frontalDisagrees,
 localizeCortex:wag294Infer(wag294Stimulus(source,2,'cortex-damaged',0)).localized.cortexDisagrees,
 immutable:Object.isFrozen(a)&&Object.isFrozen(a.scenarios)&&Object.isFrozen(a.scenarios[0]),
 appendOnly:(()=>{const x=Object.freeze([]),y=wag294LedgerAppend(x,a);return x.length===0&&y.length===1&&Object.isFrozen(y)})(),
 previousPass:wag288Audit().pass&&wag289Audit().pass&&wag290Audit().pass&&wag291Audit().pass&&wag292Audit().pass&&wag293Audit().pass,
 noActuation:a.physicalActions===0
 };
 return {bound:'WAG-294',pass:Object.values(check).every(Boolean),checks:check,example:a.scenarios,
  priorFilesModified:false};
}
if(typeof module!=='undefined')module.exports={WAG294,wag294Stimulus,wag294Infer,wag294Evaluate,wag294LedgerAppend,wag294Audit};
