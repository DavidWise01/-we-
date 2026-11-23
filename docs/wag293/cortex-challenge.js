/* WAG-293 · Cortex Contribution Challenge · .dlw
  Synthetic planted-target test, no biological or real-world validity claim.
  Temporary stimuli do not mutate the WAG-288 authoritative memories.
  Four fixed policies across 8 targets x 4 damage scenarios x 8 trials.
  The source target is injected independently of the candidate readout.
*/
const WAG293=Object.freeze({seed:293,targets:8,trials:8,
 scenarios:Object.freeze(['intact','center-damaged','cortex-damaged','both-damaged']),
 policies:Object.freeze([{name:'frontal-only',weight:1},{name:'cortex-inclusive',weight:0},{name:'balanced',weight:.5},{name:'cortex-shell',weight:null}]),
 authority:'observation only'});
function wag293Argmax(a){let k=0;for(let i=1;i<a.length;i++)if(a[i]>a[k])k=i;return k}
function wag293Stimulus(original,target,scenario,trial){
 const source=JSON.stringify(original);
 const nodes=original.nodes.map(a=>a.slice()),groups=wag289Groups();
 const shell=groups.cortex, center=groups.frontal[0],wrong=(target+1+trial%3)%8;
 for(const i of shell){
  for(let ch=0;ch<8;ch++)nodes[i][ch]=ch===target?.82:.12;
  if(scenario==='cortex-damaged'||scenario==='both-damaged'){
   // 16 of 26 cortical sites carry a conflicting signal.
   if(((i*7+trial*11+WAG293.seed)%26)<16){
    nodes[i][target]=.08;nodes[i][wrong]=.94;
   }
  }
 }
 for(let ch=0;ch<8;ch++)nodes[center][ch]=ch===target?.9:.1;
 if(scenario==='center-damaged'||scenario==='both-damaged'){
  nodes[center][target]=.04;nodes[center][wrong]=.98;
 }
 if(JSON.stringify(original)!==source)throw Error('stimulus mutated authoritative source');
 return {...original,nodes};
}
function wag293Scores(state,policy){
 const group=wag289Groups(),shell=group.cortex;
 const shellMean=Array.from({length:8},(_,ch)=>shell.reduce((s,i)=>s+state.nodes[i][ch],0)/shell.length);
 if(policy.name==='cortex-shell')return shellMean;
 const read=wag290CortexRead(state);
 return read.means.map((mean,ch)=>(1-policy.weight)*mean+policy.weight*read.frontalSnapshot[ch]);
}
function wag293Evaluate(source){
 const sourceBefore=JSON.stringify(source),out=[];
 for(const policy of WAG293.policies){
  const scenarioMetrics=[];
  for(const scenario of WAG293.scenarios){
   let correct=0;
   for(let target=0;target<8;target++)for(let trial=0;trial<WAG293.trials;trial++){
    const temp=wag293Stimulus(source,target,scenario,trial);
    correct+=Number(wag293Argmax(wag293Scores(temp,policy))===target);
   }
   scenarioMetrics.push({scenario,correct,total:64,accuracy:correct/64});
  }
  const aggregate=scenarioMetrics.reduce((a,s)=>a+s.correct,0)/256;
  out.push({name:policy.name,weight:policy.weight,scenarios:scenarioMetrics,accuracy:aggregate});
 }
 const baseline=out[0],sorted=out.slice().sort((a,b)=>b.accuracy-a.accuracy||
   a.name.localeCompare(b.name));
 const winner=sorted[0];
 const centerDamaged=winner.scenarios[1].accuracy,cortexDamaged=winner.scenarios[2].accuracy;
 const frozen=winner.name!=='frontal-only'&&winner.accuracy>=baseline.accuracy+.1&&
   centerDamaged>=.75&&cortexDamaged>=.75;
 const receipt=wag291DeepFreeze({bound:'WAG-293',tick:source.tick,
  protocols:{seed:WAG293.seed,targets:8,scenarios:4,trialsPerTarget:8,
    simulatedObservationsPerPolicy:256,policyCount:4},
  policies:out,selected:winner.name,baselineAccuracy:baseline.accuracy,
  selectedAccuracy:winner.accuracy,verdict:frozen?'FROZEN':'UNFROZEN',
  limitation:'planted-label synthetic benchmark; not physical or biological evidence',
  physicalActions:0});
 if(JSON.stringify(source)!==sourceBefore)throw Error('candidate mutated source');
 return receipt;
}
function wag293LedgerAppend(ledger,r){
 if(!Object.isFrozen(r)||r.bound!=='WAG-293')throw Error('invalid receipt');
 if(ledger.length&&r.tick<ledger[ledger.length-1].tick)throw Error('tick order');
 return Object.freeze([...ledger,r]);
}
function wag293Audit(){
 const state=wag288Initial(),snap=JSON.stringify(state);
 const a=wag293Evaluate(state),b=wag293Evaluate(state);
 const checks={
 deterministic:JSON.stringify(a)===JSON.stringify(b),
 authorityUnchanged:JSON.stringify(state)===snap,
 plantedTargetCounts:a.policies.every(p=>p.scenarios.length===4&&p.scenarios.every(s=>s.total===64)),
 fourPolicies:a.policies.length===4,
 baselinePresent:a.policies[0].name==='frontal-only',
 damageApplied:(()=>{const s=wag293Stimulus(state,3,'both-damaged',2);return s.nodes[62][3]<s.nodes[62][6]||s.nodes[62][3]<s.nodes[62][4]})(),
 separateNodes: new Set(state.nodes).size===125,
 repeatableTieBreak:wag293Argmax([.4,.4,.1])===0,
 immutable:Object.isFrozen(a)&&Object.isFrozen(a.policies)&&Object.isFrozen(a.policies[0].scenarios[0]),
 appendOnly:(()=>{const l=Object.freeze([]),n=wag293LedgerAppend(l,a);return l.length===0&&n.length===1&&Object.isFrozen(n)})(),
 positiveGate:a.verdict!=='FROZEN'||(a.selected!=='frontal-only'&&a.selectedAccuracy>=a.baselineAccuracy+.1),
 baselines:wag288Audit().pass&&wag289Audit().pass&&wag290Audit().pass&&wag291Audit().pass&&wag292Audit().pass,
 noActions:a.physicalActions===0
 };
 return {bound:'WAG-293',pass:Object.values(checks).every(Boolean),checks,
  example:{selected:a.selected,baseline:a.baselineAccuracy,result:a.selectedAccuracy,verdict:a.verdict},
  priorFilesModified:false};
}
if(typeof module!=='undefined')module.exports={WAG293,wag293Argmax,wag293Stimulus,wag293Scores,wag293Evaluate,wag293LedgerAppend,wag293Audit};
