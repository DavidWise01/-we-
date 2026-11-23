/* WAG-283 · eight lane crystalline signal learning · Phase IV 3/12 · .dlw
 Four directed topological connections, each with eight reciprocal SIGNAL
 lanes. Each pairwise flux is equal/opposite; only WAG244 could enact a
 physical action, and it is never called here.
 Teacher = predefined synthetic channel-dependent transport. Train gradients
 only on seeds 6901..6903. 7001..7002 never enter fitting or selection.
 Matched four-scalar baseline is optimized using identical samples and
 coordinate-scaled update steps. No tuning from holdout.
*/
const WAG283_CONFIG=Object.freeze({
 primitive:'---@---@---@---@---{}',terminal:'{\\a{b/}}',
 laneCount:8,links:4,neurons:48,
 trainSeeds:[6901,6902,6903],holdoutSeeds:[7001,7002],
 patterns:4,steps:48,epochs:9,initialWeight:.125,
 minWeight:.025,maxWeight:.245,learningFraction:.57,
 fixedTerminalInternalWeight:.125
});
function wag283Teacher(){
 return Array.from({length:4},(_,edge)=>
  Array.from({length:8},(_,lane)=>.064+.020*lane+.011*(edge%2)+.003*(edge===3)));
}
function wag283Weights(mode,value=WAG283_CONFIG.initialWeight){
 if(!['scalar','channels'].includes(mode))throw Error('bad parameterization');
 return Array.from({length:4},()=>Array(mode==='scalar'?1:8).fill(value));
}
function wag283GetWeight(weights,edge,lane){
 return weights[edge][weights[edge].length===1?0:lane];
}
function wag283Step(state,weights){
 if(!Array.isArray(weights)||weights.length!==4||
  weights.some(w=>!Array.isArray(w)||![1,8].includes(w.length)||
    w.some(x=>!Number.isFinite(x)||x<WAG283_CONFIG.minWeight-1e-12||
     x>WAG283_CONFIG.maxWeight+1e-12)))throw Error('bad weights');
 const initial=wag277Mass(state),next=state.junctionSignals.map(z=>z.slice()),
   terminal=state.terminalSignals.slice(),inputs=state.junctionSignals,
   factors=[];
 for(let edge=0;edge<4;edge++){
  factors[edge]=[];
  for(let lane=0;lane<8;lane++){
   const left=edge<3?inputs[edge]:inputs[3],li=lane;
   const right=edge<3?inputs[edge+1]:state.terminalSignals,ri=edge<3?(lane^7):lane;
   const difference=left[li]-right[ri],flux=wag283GetWeight(weights,edge,lane)*difference;
   if(edge<3){next[edge][li]-=flux;next[edge+1][ri]+=flux}
   else{next[3][li]-=flux;terminal[ri]+=flux}
   factors[edge].push({left:edge*8+li,right:edge<3?(edge+1)*8+ri:32+ri,difference});
  }
 }
 for(let k=0;k<8;k++){
  const partner=8+(k^7),d=WAG283_CONFIG.fixedTerminalInternalWeight*
    (state.terminalSignals[k]-state.terminalSignals[partner]);
  terminal[k]-=d;terminal[partner]+=d;
 }
 const output={topology:state.topology,junctionSignals:next,
  terminalSignals:terminal,pulse:state.pulse+1};
 const residual=Math.abs(wag277Mass(output)-initial);
 if(residual>1e-10)throw Error('Signal sum drift');
 if(!next.flat().concat(terminal).every(z=>z>=-1e-12&&z<=1+1e-12))
  throw Error('Activation bounds violated');
 return {state:output,factors,residual};
}
function wag283Vector(state){
 return state.junctionSignals.flat().concat(state.terminalSignals);
}
function wag283MSE(x,y){
 const a=wag283Vector(x),b=wag283Vector(y);
 return a.reduce((v,n,i)=>v+(n-b[i])**2,0)/a.length;
}
function wag283Source(seed,pattern){
 const s=wag281Example(seed,pattern);
 for(let lane=0;lane<8;lane++){
  s.junctionSignals[0][lane]=.02+.96*wag281Hash(seed+pattern*31,lane+700);
  s.junctionSignals[1][lane]=.01+.09*wag281Hash(seed,900+lane+pattern);
 }
 return s;
}
function wag283Dataset(seeds){
 const cases=[];
 for(const seed of seeds)for(let pattern=0;pattern<WAG283_CONFIG.patterns;pattern++){
  let state=wag283Source(seed,pattern);const samples=[];
  for(let tick=0;tick<WAG283_CONFIG.steps;tick++){
   const next=wag283Step(state,wag283Teacher()).state;
   samples.push({state,next,tick});
   state=next;
  }
  cases.push({seed,pattern,source:wag283Source(seed,pattern),samples});
 }
 return cases;
}
function wag283OneStepLoss(dataset,weights){
 let loss=0,maxResidual=0,count=0;
 for(const item of dataset)for(const pair of item.samples){
  const prediction=wag283Step(pair.state,weights);
  loss+=wag283MSE(prediction.state,pair.next);
  maxResidual=Math.max(maxResidual,prediction.residual);count++;
 }
 return {mse:loss/count,maxResidual};
}
function wag283Rollout(dataset,weights){
 let loss=0,count=0,maxResidual=0;const cases=[];
 for(const example of dataset){
  let state=JSON.parse(JSON.stringify(example.source)),caseLoss=0;
  const series=[];
  for(const pair of example.samples){
   const prediction=wag283Step(state,weights);
   state=prediction.state;
   const e=wag283MSE(state,pair.next);
   caseLoss+=e;loss+=e;count++;
   maxResidual=Math.max(maxResidual,prediction.residual);
   if((pair.tick+1)%8===0)series.push({tick:pair.tick+1,mse:e,
    terminalPredicted:state.terminalSignals.slice(8).reduce((a,b)=>a+b,0)/8,
    terminalTarget:pair.next.terminalSignals.slice(8).reduce((a,b)=>a+b,0)/8});
  }
  cases.push({seed:example.seed,pattern:example.pattern,
   mse:caseLoss/example.samples.length,series});
 }
 return {mse:loss/count,maxResidual,cases};
}
function wag283TrainModel(dataset,mode){
 const weights=wag283Weights(mode),history=[];
 const bounded=x=>Math.max(WAG283_CONFIG.minWeight,Math.min(WAG283_CONFIG.maxWeight,x));
 for(let epoch=0;epoch<=WAG283_CONFIG.epochs;epoch++){
  const baseline=wag283OneStepLoss(dataset,weights);
  history.push({epoch,oneStepMSE:baseline.mse,
   weights:weights.map(z=>z.slice())});
  if(epoch===WAG283_CONFIG.epochs)break;
  const gradient=weights.map(row=>row.map(()=>0)),
    curvature=weights.map(row=>row.map(()=>0));
  let count=0;
  for(const item of dataset)for(const pair of item.samples){
   const prediction=wag283Step(pair.state,weights),a=wag283Vector(prediction.state),
     b=wag283Vector(pair.next);
   for(let edge=0;edge<4;edge++)for(let lane=0;lane<8;lane++){
    const x=prediction.factors[edge][lane],group=weights[edge].length===1?0:lane;
    gradient[edge][group]+=2*x.difference*((a[x.right]-b[x.right])-
     (a[x.left]-b[x.left]))/48;
    curvature[edge][group]+=4*x.difference*x.difference/48;
   }
   count++;
  }
  for(let i=0;i<4;i++)for(let j=0;j<weights[i].length;j++){
   const delta=WAG283_CONFIG.learningFraction*
    gradient[i][j]/Math.max(1e-7,curvature[i][j]);
   weights[i][j]=bounded(weights[i][j]-delta);
  }
 }
 return {mode,weights,history};
}
function wag283Experiment(){
 const train=wag283Dataset(WAG283_CONFIG.trainSeeds),
  holdout=wag283Dataset(WAG283_CONFIG.holdoutSeeds);
 const scalar=wag283TrainModel(train,'scalar'),
  channels=wag283TrainModel(train,'channels');
 const scalarTrain=wag283OneStepLoss(train,scalar.weights),
  channelTrain=wag283OneStepLoss(train,channels.weights);
 const scalarHeld=wag283OneStepLoss(holdout,scalar.weights),
  channelHeld=wag283OneStepLoss(holdout,channels.weights);
 const scalarRoll=wag283Rollout(holdout,scalar.weights),
  channelRoll=wag283Rollout(holdout,channels.weights);
 const improvement=scalarRoll.mse-channelRoll.mse;
 return {bound:'WAG-283',phase:'WAG-IV',turn:3,config:WAG283_CONFIG,
  target:wag283Teacher(),models:{scalar,channels},
  summary:{trainCases:train.length,heldoutCases:holdout.length,
   scalarParameters:4,multichannelParameters:32,
   trainScalarOneStepMSE:scalarTrain.mse,trainChannelOneStepMSE:channelTrain.mse,
   heldoutScalarOneStepMSE:scalarHeld.mse,heldoutChannelOneStepMSE:channelHeld.mse,
   heldoutScalarRolloutMSE:scalarRoll.mse,heldoutChannelRolloutMSE:channelRoll.mse,
   rolloutRelativeImprovement:scalarRoll.mse?improvement/scalarRoll.mse:0,
   multichannelWins:channelRoll.cases.filter((c,i)=>c.mse<scalarRoll.cases[i].mse).length,
   maxResidual:Math.max(scalarRoll.maxResidual,channelRoll.maxResidual),
   physicalActions:0},
  holdout:{scalar:scalarRoll.cases,channels:channelRoll.cases},
  interpretation:[
   'Teacher channel weights are explicit synthetic ground truth, not discovered physical dynamics',
   'Both controllers fit the same teacher trajectories with the same epoch count and normalized optimizer',
   'Only training samples set coefficients; holdout is read-only',
   'Four-scalar and 32-weight models have different capacity; improvement does not prove biological crystalline learning',
   'No physical actions, material transfer or change to sealed WAG-III']
 };
}
if(typeof module!=='undefined')module.exports={WAG283_CONFIG,wag283Teacher,
 wag283Weights,wag283GetWeight,wag283Step,wag283Vector,wag283MSE,
 wag283Source,wag283Dataset,wag283OneStepLoss,wag283Rollout,
 wag283TrainModel,wag283Experiment};
