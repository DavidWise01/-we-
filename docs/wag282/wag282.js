/* WAG-282 · bounded temporal learning for crystalline @ junctions.
 Independent adaptive rail state per junction with four-slot error-gradient FIFO.
 Every tick: observe current state; predict next state; compare with an
 available synthetic teacher's NEXT state, then update weight for NEXT tick.
 Teacher outcomes are explicitly observed online (not hidden). No future
 target available at decision time, no physical action, no policy promotion.
*/
const WAG282_CONFIG=Object.freeze({
 primitive:'---@---@---@---@---{}',
 trainingSeeds:[6701,6702,6703],holdoutSeeds:[6801,6802],
 patternsPerSeed:4,steps:72,historyLength:4,learningRate:.075,
 finiteDifference:.004,minWeight:.025,maxWeight:.245,
 baseWeight:.125,teacherWeight:.22,transitions:[24,48],
 baseline:'WAG-281 frozen learned four weights'
});
function wag282Source(seed,index){
 const s=wag281Example(seed,index);
 for(let i=0;i<8;i++)s.junctionSignals[0][i]=.05+.85*wag281Hash(seed+index*19,500+i);
 return s;
}
function wag282OracleWeight(t,seed,index){
 // Deterministic, unobserved current target coefficient. An online teacher
 // reveals a state transition AFTER the controller makes its prediction.
 const phase=(seed+index)%3;
 const segment=Math.floor(t/24);
 return Math.max(.035,Math.min(.235,
  WAG282_CONFIG.teacherWeight-(segment%2)*.11+((phase-1)*.015)));
}
function wag282OracleStep(state,t,seed,index){
 return wag281LearnedStep(state,Array(4).fill(wag282OracleWeight(t,seed,index))).state;
}
function wag282StateLoss(a,b){
 let sum=0,count=0;
 for(let i=0;i<4;i++)for(let j=0;j<8;j++){
  const d=a.junctionSignals[i][j]-b.junctionSignals[i][j];
  sum+=d*d;count++;
 }
 for(let j=0;j<16;j++){
  const d=a.terminalSignals[j]-b.terminalSignals[j];sum+=d*d;count++;
 }
 return sum/count;
}
function wag282Clamp(x){return Math.max(WAG282_CONFIG.minWeight,
 Math.min(WAG282_CONFIG.maxWeight,x))}
function wag282Step(state,weights,history,teacherNext){
 // Current prediction is scored BEFORE this tick's teacher transition is used.
 const pred=wag281LearnedStep(state,weights),loss=wag282StateLoss(pred.state,teacherNext);
 const eps=WAG282_CONFIG.finiteDifference;
 const nextHistory=history.map(h=>h.slice()),nextWeights=weights.slice();
 const gradients=[];
 for(let i=0;i<4;i++){
  const p=weights.slice(),m=weights.slice();p[i]=wag282Clamp(p[i]+eps);m[i]=wag282Clamp(m[i]-eps);
  const gp=wag282StateLoss(wag281LearnedStep(state,p).state,teacherNext);
  const gm=wag282StateLoss(wag281LearnedStep(state,m).state,teacherNext);
  const grad=(gp-gm)/(p[i]-m[i]);
  nextHistory[i].push(grad);
  if(nextHistory[i].length>WAG282_CONFIG.historyLength)nextHistory[i].shift();
  const rolling=nextHistory[i].reduce((a,b)=>a+b,0)/nextHistory[i].length;
  nextWeights[i]=wag282Clamp(weights[i]-WAG282_CONFIG.learningRate*rolling);
  gradients.push({latest:grad,rolling});
 }
 return {predicted:pred.state,weights:nextWeights,history:nextHistory,
  loss,gradients,residual:pred.residual};
}
function wag282Scenario(seed,index,initialWeights,adaptive){
 const initial=wag282Source(seed,index),snap=JSON.parse(JSON.stringify(initial));
 let student=snap,teacher=JSON.parse(JSON.stringify(initial)),
  weights=initialWeights.slice(),history=Array.from({length:4},()=>[]),
  mseSum=0,maxResidual=0;
 const series=[];
 for(let t=0;t<WAG282_CONFIG.steps;t++){
  // Teacher's transition becomes available at tick t, after state prediction.
  const nextTeacher=wag282OracleStep(teacher,t,seed,index);
  const step=wag282Step(student,weights,history,nextTeacher);
  // Both arms are evaluated on their OWN evolving states; this is
  // trajectory tracking, not an isolated one-step gradient proof.
  mseSum+=step.loss;
  student=step.predicted;teacher=nextTeacher;
  if(adaptive){weights=step.weights;history=step.history}
  maxResidual=Math.max(maxResidual,step.residual);
  if(t%6===0||WAG282_CONFIG.transitions.includes(t+1))
   series.push({tick:t+1,loss:step.loss,weights:weights.slice(),
    memoryGradient:step.gradients.map(z=>z.rolling),
    terminalStudent:student.terminalSignals.slice(8).reduce((a,b)=>a+b,0)/8,
    terminalTeacher:teacher.terminalSignals.slice(8).reduce((a,b)=>a+b,0)/8});
 }
 return {seed,index,adaptive,meanMSE:mseSum/WAG282_CONFIG.steps,
  finalWeights:weights,memoryDepth:history.map(z=>z.length),
  maxResidual,series};
}
function wag282Experiment(baseWeights){
 if(!Array.isArray(baseWeights)||baseWeights.length!==4)
  throw Error('Requires WAG281 frozen learned weights');
 const run=(seeds,adaptive)=>seeds.flatMap(seed=>Array.from(
 {length:WAG282_CONFIG.patternsPerSeed},(_,index)=>
  wag282Scenario(seed,index,baseWeights,adaptive)));
 const trainFixed=run(WAG282_CONFIG.trainingSeeds,false),
  trainAdaptive=run(WAG282_CONFIG.trainingSeeds,true),
  holdoutFixed=run(WAG282_CONFIG.holdoutSeeds,false),
  holdoutAdaptive=run(WAG282_CONFIG.holdoutSeeds,true);
 const avg=x=>x.reduce((a,z)=>a+z.meanMSE,0)/x.length;
 const stats={trainPatterns:trainFixed.length,holdoutPatterns:holdoutFixed.length,
  trainFixedMSE:avg(trainFixed),trainAdaptiveMSE:avg(trainAdaptive),
  holdoutFixedMSE:avg(holdoutFixed),holdoutAdaptiveMSE:avg(holdoutAdaptive),
  holdoutRelativeImprovement:1-avg(holdoutAdaptive)/avg(holdoutFixed),
  holdoutAdaptiveWins:holdoutAdaptive.filter((r,i)=>r.meanMSE<holdoutFixed[i].meanMSE).length,
  maxResidual:Math.max(...trainAdaptive.concat(holdoutAdaptive).map(z=>z.maxResidual)),
  finalMemoryDepthMin:Math.min(...holdoutAdaptive.flatMap(z=>z.memoryDepth)),
  finalMemoryDepthMax:Math.max(...holdoutAdaptive.flatMap(z=>z.memoryDepth))};
 return {bound:'WAG-282',phase:'WAG-IV',turn:2,config:WAG282_CONFIG,
  initialWeights:baseWeights.slice(),summary:stats,
  train:{fixed:trainFixed.map(z=>({seed:z.seed,index:z.index,mse:z.meanMSE})),
   adaptive:trainAdaptive.map(z=>({seed:z.seed,index:z.index,mse:z.meanMSE}))},
  holdout:{fixed:holdoutFixed.map(z=>({seed:z.seed,index:z.index,mse:z.meanMSE})),
   adaptive:holdoutAdaptive},
  caveats:['Online supervision sees the current teacher transition after making each prediction',
   'Holdout seeds are novel, but still use the same synthetic teacher generator',
   'Per-junction bounded memory stores four recent scalar gradients, not actual physical history',
   'Observed improvements cannot establish autonomous or unsupervised regulation',
   'WAG261 and sealed WAG-III remain unchanged, and no repair action executes']};
}
if(typeof module!=='undefined')module.exports={WAG282_CONFIG,wag282Source,wag282OracleWeight,
 wag282OracleStep,wag282StateLoss,wag282Step,wag282Scenario,wag282Experiment};
