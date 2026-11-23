/* WAG-286 · Quartz lattice growth & bounded learning · Phase IV 6/12
  Canonical four-quartz motif: ---@---@---#---@---@---
  Generalization: N/2 @ --- # --- N/2 @, where N is 2,4,8,16.
  Synthetic reciprocal eight-lane flux; central # is a signal junction only.
  PREDECLARED fixed 64 scalar parameter updates + 768 pair observations
  (2 passes over 384 observations) for every N. No physical action or
  electrical/material simulation. Training 7501-7504; holdout 7601-7602.
 */
const WAG286_CONFIG=Object.freeze({
 bound:'WAG-286',phase:'WAG-IV',crystals:[2,4,8,16],
 quartz:'---@---@---#---@---@---',channels:8,
 trainSeeds:[7501,7502,7503,7504],heldoutSeeds:[7601,7602],
 patterns:2,ticks:48,epochs:2,maxPairs:768,maxUpdates:64,
 minWeight:.025,maxWeight:.245,startWeight:.125,
 learningFraction:.68,benchmarkKind:'synthetic quartz transport',
 physicalActionCalls:0
});
function wag286Layout(crystals){
 if(!WAG286_CONFIG.crystals.includes(crystals))throw Error('invalid growth size');
 const center=crystals/2,labels=Array.from({length:crystals+1},(_,i)=>i===center?'#':'@');
 return {crystals,hubIndex:center,labels,
  glyph:labels.map((x,i)=>(i?'---':'')+x).join('')+'---',
  signalSites:(crystals+1)*8,railParameters:crystals*8,
  topologyLinks:crystals};
}
function wag286Seed(seed,k){
 let v=(Math.imul(seed,2654435761)+Math.imul(k+1,1013904223))>>>0;
 v^=v<<13;v^=v>>>17;v^=v<<5;return (v>>>0)/4294967296;
}
function wag286Teacher(n){
 return Array.from({length:n},(_,e)=>Array.from({length:8},(_,k)=>
  .048+.016*k+.006*(e%3)+.002*((e+1)%5)));
}
function wag286Initial(n,seed,pattern){
 const state=Array.from({length:n+1},()=>Array(8).fill(0));
 for(let k=0;k<8;k++){
  state[0][k]=.08+.74*wag286Seed(seed+pattern*17,k);
  state[n][k]=.07+.46*wag286Seed(seed+pattern*43,100+k);
 }
 return state;
}
function wag286Mass(state){return state.flat().reduce((a,b)=>a+b,0)}
function wag286Step(state,weights){
 const n=state.length-1;
 if(weights.length!==n||weights.some(x=>x.length!==8))throw Error('weight topology mismatch');
 const before=wag286Mass(state),next=state.map(z=>z.slice());
 for(let e=0;e<n;e++)for(let k=0;k<8;k++){
  const w=weights[e][k];if(w<.025||w>.245||!Number.isFinite(w))throw Error('rail bounds');
  const right=k^7,flux=w*(state[e][k]-state[e+1][right]);
  next[e][k]-=flux;next[e+1][right]+=flux;
 }
 const residual=Math.abs(wag286Mass(next)-before);
 if(residual>1e-10||next.flat().some(x=>x< -1e-12||x>1+1e-12))
  throw Error('quartz activation invariant failed');
 return {state:next,residual};
}
function wag286Dataset(n,seeds){
 const teacher=wag286Teacher(n),cases=[];
 for(const seed of seeds)for(let pattern=0;pattern<WAG286_CONFIG.patterns;pattern++){
  let state=wag286Initial(n,seed,pattern);
  const observations=[];
  for(let t=0;t<WAG286_CONFIG.ticks;t++){
   const target=wag286Step(state,teacher).state;
   observations.push({state,target,tick:t});
   state=target;
  }
  cases.push({seed,pattern,source:wag286Initial(n,seed,pattern),observations});
 }
 return cases;
}
function wag286Loss(a,b){
 let sum=0,n=0;
 for(let i=0;i<a.length;i++)for(let k=0;k<8;k++){
  const d=a[i][k]-b[i][k];sum+=d*d;n++;
 }
 return sum/n;
}
function wag286Rollout(cases,weights){
 const rows=[];let total=0,maxResidual=0;
 for(const c of cases){
  let state=c.source.map(z=>z.slice()),loss=0;
  const samples=[];
  for(const p of c.observations){
   const z=wag286Step(state,weights);state=z.state;
   const e=wag286Loss(state,p.target);loss+=e;
   maxResidual=Math.max(maxResidual,z.residual);
   if((p.tick+1)%8===0)samples.push({tick:p.tick+1,mse:e,
    hub:state[Math.floor(weights.length/2)].reduce((a,b)=>a+b,0)/8});
  }
  rows.push({seed:c.seed,pattern:c.pattern,mse:loss/c.observations.length,samples});
  total+=loss;
 }
 return {mse:total/(cases.length*WAG286_CONFIG.ticks),maxResidual,rows};
}
function wag286Train(n,trainCases){
 const weights=Array.from({length:n},()=>Array(8).fill(WAG286_CONFIG.startWeight));
 const budget={pairsUsed:0,updatesUsed:0,maxPairs:WAG286_CONFIG.maxPairs,
  maxUpdates:WAG286_CONFIG.maxUpdates,trainEpochs:0,
  parameterSlots:8*n,gradientSlots:16*n,violations:0};
 const history=[{epoch:0,trainRolloutMSE:wag286Rollout(trainCases,weights).mse,
  updatedRailCount:0}];
 const available=n*8,seen=new Set();
 // Round-robin evenly across N*8 weights: 16 weights get 4 updates,
 // 32 get 2, 64 get 1, 128 get at most 1/2 each. This is by design.
 for(let epoch=0;epoch<WAG286_CONFIG.epochs;epoch++){
  const grad=Array.from({length:n},()=>Array(8).fill(0)),
   curve=Array.from({length:n},()=>Array(8).fill(0));
  for(const c of trainCases)for(const obs of c.observations){
   if(++budget.pairsUsed>budget.maxPairs)throw Error('observation budget exceeded');
   const predicted=wag286Step(obs.state,weights).state;
   const dim=(n+1)*8;
   for(let edge=0;edge<n;edge++)for(let k=0;k<8;k++){
    const j=k^7,diff=obs.state[edge][k]-obs.state[edge+1][j];
    const errorRight=predicted[edge+1][j]-obs.target[edge+1][j],
      errorLeft=predicted[edge][k]-obs.target[edge][k];
    grad[edge][k]+=2*diff*(errorRight-errorLeft)/dim;
    curve[edge][k]+=4*diff*diff/dim;
   }
  }
  // A fixed 32 updates per pass, rotating across all parameter slots.
  for(let u=0;u<32;u++){
   if(++budget.updatesUsed>budget.maxUpdates)throw Error('update budget exceeded');
   const id=epoch*32+u,slot=id%available,edge=Math.floor(slot/8),k=slot%8;
   const delta=WAG286_CONFIG.learningFraction*grad[edge][k]/
    Math.max(1e-7,curve[edge][k]);
   weights[edge][k]=Math.max(.025,Math.min(.245,weights[edge][k]-delta));
   seen.add(slot);
  }
  budget.trainEpochs++;
  history.push({epoch:epoch+1,
   trainRolloutMSE:wag286Rollout(trainCases,weights).mse,
   updatedRailCount:seen.size});
 }
 budget.updatedDistinctParameters=seen.size;
 budget.coverage=seen.size/available;
 if(budget.pairsUsed!==768||budget.updatesUsed!==64||budget.violations)
  throw Error('growth budget audit failed');
 return {weights,budget,history};
}
function wag286Experiment(){
 const cases=[],audits=[];
 for(const n of WAG286_CONFIG.crystals){
  const train=wag286Dataset(n,WAG286_CONFIG.trainSeeds),
    held=wag286Dataset(n,WAG286_CONFIG.heldoutSeeds);
  const model=wag286Train(n,train),baseline=Array.from({length:n},()=>Array(8).fill(.125));
  const initial=wag286Rollout(held,baseline),
    adapted=wag286Rollout(held,model.weights),
    layout=wag286Layout(n);
  const row={crystals:n,layout,budget:model.budget,history:model.history,
   heldoutInitialMSE:initial.mse,heldoutAdaptiveMSE:adapted.mse,
   improvementRatio:initial.mse?1-adapted.mse/initial.mse:0,
   heldoutWins:adapted.rows.filter((c,i)=>c.mse<initial.rows[i].mse).length,
   maxResidual:Math.max(initial.maxResidual,adapted.maxResidual),
   weights:model.weights,
   heldout:{initial:initial.rows,adapted:adapted.rows}};
  cases.push(row);
  audits.push({crystals:n,parameterSlots:8*n,
   weightCoverage:row.budget.coverage,budgetPassed:true,
   maxResidual:row.maxResidual});
 }
 return {bound:'WAG-286',phase:'WAG-IV',turn:6,
  config:WAG286_CONFIG,cases,audits,
  summary:{sizes:cases.length,heldoutCasesPerSize:cases[0].heldout.adapted.length,
   allBudgetChecksPassed:audits.every(z=>z.budgetPassed),
   maxResidual:Math.max(...audits.map(z=>z.maxResidual)),
   casesImproved:cases.map(z=>({quartz:z.crystals,
    relativeImprovement:z.improvementRatio,
    wins:z.heldoutWins,coverage:z.budget.coverage})),
   updateBudgetPerSize:64,trainPairsPerSize:768,physicalActions:0},
  caveats:[
   'Quartz is a geometry/material-style label; this model is synthetic signal transport, not piezoelectric physics',
   'The same total learning operations per size create less coverage at larger parameter counts',
   'Held-out seeds use the same synthetic teacher rule as training seeds',
   'Observations and update counts are proxies for computational cost, not measured wall time or Joules',
   'Zero physical-action decisions; WAG261 and sealed Phase III remain unchanged'
  ]};
}
if(typeof module!=='undefined')module.exports={WAG286_CONFIG,wag286Layout,wag286Seed,
 wag286Teacher,wag286Initial,wag286Mass,wag286Step,wag286Dataset,
 wag286Loss,wag286Rollout,wag286Train,wag286Experiment};
