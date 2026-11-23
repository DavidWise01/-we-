/* WAG-281 · Phase IV crystalline lattice learning, 1/12 · .dlw
  Four learnable J0..J3 inter-lattice/terminal transport coefficients.
  Uses deterministic supervised synthetic signal teacher, NOT physical truth.
  Training only on seeds 6501–6503; withheld 6601–6602.
  WAG-276 and all WAG-III evidence remain untouched.
  Matched pairwise flux conserves abstract activation SUM (not energy).
  No physical action issued by this learning laboratory.
*/
const WAG281_CONFIG=Object.freeze({
 primitive:'---@---@---@---@---{}',
 crystal:'{\\a{b/}}',
 junctions:4,
 baselineWeight:.125,teacherWeight:.22,
 trainSeeds:[6501,6502,6503],holdoutSeeds:[6601,6602],
 patternsPerSeed:6,pulses:72,epochs:6,
 learningRate:.40,finiteDifference:.003,
 minWeight:.025,maxWeight:.245
});
function wag281Hash(seed,index){
 let x=(seed*2654435761+(index+1)*1013904223)>>>0;
 x^=x<<13;x^=x>>>17;x^=x<<5;
 return (x>>>0)/4294967296;
}
function wag281Example(seed,index){
 const state=wag277Initial(4,'pulse');
 for(const row of state.junctionSignals)row.fill(0);
 state.terminalSignals.fill(0);
 for(let k=0;k<8;k++){
  const u=wag281Hash(seed,index*8+k);
  state.junctionSignals[0][k]=(.08+.82*u);
 }
 return state;
}
function wag281InitialWeights(value=WAG281_CONFIG.baselineWeight){
 return Array(4).fill(value);
}
function wag281LearnedStep(state,weights){
 if(!Array.isArray(weights)||weights.length!==4||
   !weights.every(v=>Number.isFinite(v)&&v>=WAG281_CONFIG.minWeight&&v<=WAG281_CONFIG.maxWeight))
   throw Error('Invalid learnable lattice rails');
 const before=wag277Mass(state),n=state.junctionSignals.length;
 const next=state.junctionSignals.map(a=>a.slice()),terminal=state.terminalSignals.slice();
 for(let i=0;i<n-1;i++)for(let k=0;k<8;k++){
  const other=k^7,d=weights[i]*(state.junctionSignals[i][k]-state.junctionSignals[i+1][other]);
  next[i][k]-=d;next[i+1][other]+=d;
 }
 for(let k=0;k<8;k++){
  const d=weights[3]*(state.junctionSignals[n-1][k]-state.terminalSignals[k]);
  next[n-1][k]-=d;terminal[k]+=d;
 }
 for(let k=0;k<8;k++){
  const other=8+(k^7),d=.125*(state.terminalSignals[k]-state.terminalSignals[other]);
  terminal[k]-=d;terminal[other]+=d;
 }
 const output={topology:state.topology,junctionSignals:next,
  terminalSignals:terminal,pulse:state.pulse+1};
 const residual=Math.abs(wag277Mass(output)-before);
 if(residual>1e-10)throw Error('Abstract signal conservation violated');
 if(!next.flat().concat(terminal).every(v=>v>=-1e-12&&v<=1+1e-12))
  throw Error('Neural activation bound violated');
 return {state:output,residual};
}
function wag281RunSignal(source,weights,pulses=WAG281_CONFIG.pulses){
 let state=JSON.parse(JSON.stringify(source)),residual=0;
 const checkpoints=[];
 for(let t=0;t<pulses;t++){
  const z=wag281LearnedStep(state,weights);state=z.state;
  residual=Math.max(residual,z.residual);
  if((t+1)%12===0)checkpoints.push({
   tick:t+1,
   b:state.terminalSignals.slice(8).reduce((a,v)=>a+v,0)/8,
   a:state.terminalSignals.slice(0,8).reduce((a,v)=>a+v,0)/8});
 }
 return {checkpoints,residual,terminalB:checkpoints.at(-1).b,finalMass:wag277Mass(state)};
}
function wag281Examples(seeds){
 return seeds.flatMap(seed=>Array.from({length:WAG281_CONFIG.patternsPerSeed},(_,index)=>({
  seed,index,source:wag281Example(seed,index)})));
}
function wag281Objective(examples,weights){
 const oracle=wag281InitialWeights(WAG281_CONFIG.teacherWeight);
 let loss=0,maxResidual=0;
 for(const item of examples){
  const student=wag281RunSignal(item.source,weights),
   teacher=wag281RunSignal(item.source,oracle);
  for(let j=0;j<student.checkpoints.length;j++){
   const gap=student.checkpoints[j].b-teacher.checkpoints[j].b;
   loss+=gap*gap;
  }
  maxResidual=Math.max(maxResidual,student.residual,teacher.residual);
 }
 return {mse:loss/(examples.length*(WAG281_CONFIG.pulses/12)),maxResidual};
}
function wag281Train(){
 const train=wag281Examples(WAG281_CONFIG.trainSeeds),
  holdout=wag281Examples(WAG281_CONFIG.holdoutSeeds);
 const weights=wag281InitialWeights(),fixed=wag281InitialWeights();
 const history=[{epoch:0,weights:weights.slice(),
  trainMSE:wag281Objective(train,weights).mse,
  heldoutMSE:wag281Objective(holdout,weights).mse}];
 for(let epoch=1;epoch<=WAG281_CONFIG.epochs;epoch++){
  // Gradients obtained on the TRAIN cohort alone. The holdout evaluation
  // is read-only, never used to modify coefficients or choose hyperparameters.
  const gradient=[];
  const eps=WAG281_CONFIG.finiteDifference;
  for(let i=0;i<weights.length;i++){
   const plus=weights.slice(),minus=weights.slice();
   plus[i]+=eps;minus[i]-=eps;
   gradient.push((wag281Objective(train,plus).mse-
    wag281Objective(train,minus).mse)/(2*eps));
  }
  for(let i=0;i<weights.length;i++)
   weights[i]=Math.max(WAG281_CONFIG.minWeight,
    Math.min(WAG281_CONFIG.maxWeight,weights[i]-
     WAG281_CONFIG.learningRate*gradient[i]));
  history.push({epoch,weights:weights.slice(),gradient,
   trainMSE:wag281Objective(train,weights).mse,
   heldoutMSE:wag281Objective(holdout,weights).mse});
 }
 const baseline=wag281Objective(holdout,fixed),
  trained=wag281Objective(holdout,weights);
 const changed=weights.some((v,i)=>Math.abs(v-fixed[i])>1e-12);
 if(!changed)throw Error('No lattice learning observed');
 return {bound:'WAG-281',phase:'WAG-IV',turn:1,
  primitive:WAG281_CONFIG.primitive,config:WAG281_CONFIG,
  fixed,learned:weights,history,
  summary:{trainCases:train.length,holdoutCases:holdout.length,
   holdoutBaselineMSE:baseline.mse,holdoutLearnedMSE:trained.mse,
   holdoutMSEImprovement:baseline.mse-trained.mse,
   updatedWeights:weights.filter((v,i)=>v!==fixed[i]).length,
   maxSignalResidual:Math.max(baseline.maxResidual,trained.maxResidual),
   noPhysicalActions:true},
  limits:['The teacher is an in-model signal transport target, not an optimal repair controller',
   'Each junction learns one shared eight-strand rail weight, not a general neural network',
   'Held-out examples share algorithmic signal-generation ancestry with the training examples',
   'All outcomes are synthetic and signal conservation is not physical energy conservation',
   'Phase III remains closed; WAG261 is the unmodified reference controller']};
}
if(typeof module!=='undefined')module.exports={
 WAG281_CONFIG,wag281Hash,wag281Example,wag281InitialWeights,
 wag281LearnedStep,wag281RunSignal,wag281Examples,wag281Objective,wag281Train};
