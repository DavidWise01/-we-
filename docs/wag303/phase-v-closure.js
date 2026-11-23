/* WAG-303 · Phase V acceptance boundary · .dlw
   Close research phase, NOT controller acceptance.
   Fixed gate declared before evaluation:
   clear accuracy >=95%; all damaged/ambiguous cases false decisions =0;
   every abstention counted as non-success; preserved source unchanged.
   Coordinated corruption remains a blocking counterexample.
*/
const WAG303=Object.freeze({phase:'V',milestone:8,of:8,nextPhase:'VI',
  thresholds:Object.freeze({clearAccuracy:.95,maxWrongAllFaults:0}),
  acceptance:'WITHHELD',physicalActions:0});
function wag303Close(source){
 const snapshot=JSON.stringify(source),results=wag302Evaluate(source);
 const get=kind=>results.rows.find(row=>row.kind===kind);
 const clear=get('clear');
 const faultRows=results.rows.filter(row=>row.kind!=='clear');
 const wrongTotal=faultRows.reduce((s,r)=>s+r.wrong,0);
 const requirements={
  clearAccuracy:clear.correct/clear.total>=WAG303.thresholds.clearAccuracy,
  faultFalseSelections:wrongTotal<=WAG303.thresholds.maxWrongAllFaults,
  ambiguityAbstains:get('ambiguous').abstain===64,
  splitCortexAbstains:get('split-cortex').abstain===64,
  separateForms:WAG301.forms.join('|')==='[1]|{1}|(1)',
  fullEvidenceAccounting:results.rows.every(r=>r.correct+r.wrong+r.abstain===r.total),
  singleCenter:wag289Groups().frontal.length===1&&WAG300.center===62
 };
 const accepted=Object.values(requirements).every(Boolean);
 const receipt=wag291DeepFreeze({
  bound:'WAG-303',phase:'V',phaseStatus:'RESEARCH_SEQUENCE_CLOSED',
  milestone:'8/8',progress:1,acceptance:accepted?'ACCEPTED':'WITHHELD',
  topology:{outer:125,cortex:27,frontal:1,center:62},
  requirements,thresholds:WAG303.thresholds,
  results:results.rows,blockingCounterexample:{
   kind:'both-corrupt',wrong:get('both-corrupt').wrong,
   total:get('both-corrupt').total,detail:'Three confident correlated claims can agree on a false target.'
  },
  provenance:{source:'WAG-302 deterministic generated benchmark',
   ancestry:'three private interpretations from one overlapping 125-site source',
   sourceIndependent:false},
  next:{phase:'VI',name:'Independent Evidence and External Validation',
   scope:'test external independent origin, source-ancestry checks, non-planted observations, and open-world abstention before any action permission'},
  authoritativeMemoryChanged:false,physicalActions:0
 });
 if(JSON.stringify(source)!==snapshot)throw Error('source mutated during closure');
 return receipt;
}
function wag303Audit(){
 const source=wag288Initial(),before=JSON.stringify(source);
 const a=wag303Close(source),b=wag303Close(source);
 const row=k=>a.results.find(r=>r.kind===k);
 const checks={
  deterministic:JSON.stringify(a)===JSON.stringify(b),
  immutable:Object.isFrozen(a)&&Object.isFrozen(a.results)&&Object.isFrozen(a.blockingCounterexample),
  memoryPreserved:JSON.stringify(source)===before,
  geometryPreserved:a.topology.outer===125&&a.topology.cortex===27&&a.topology.frontal===1,
  phaseComplete:a.milestone==='8/8'&&a.progress===1,
  acceptanceWithheld:a.acceptance==='WITHHELD',
  clearCorrect:row('clear').correct===64,
  ambiguityAbstains:row('ambiguous').abstain===64,
  splitAbstains:row('split-cortex').abstain===64,
  counterexamplePreserved:a.blockingCounterexample.wrong===64,
  failGate:a.requirements.faultFalseSelections===false,
  noMiscount:a.results.every(r=>r.correct+r.wrong+r.abstain===r.total),
  oneAncestry:a.provenance.sourceIndependent===false,
  nextPhaseNamed:a.next.phase==='VI',
  priorStages:wag301Audit().pass&&wag302Audit().pass,
  zeroActuation:a.physicalActions===0
 };
 return {bound:'WAG-303',pass:Object.values(checks).every(Boolean),checks,
  closure:a.acceptance,phaseProgress:1,receipt:a};
}
if(typeof module!=='undefined')module.exports={WAG303,wag303Close,wag303Audit};
