/* WAG-285 · Bounded crystalline learning economy · Phase IV 5/12 · .dlw
   A hard update, observation, and coefficient-memory ceiling.
   Compared against frozen WAG283 nine-epoch training on same synthetic
   channel-specific teacher and fresh, disjoint 7301..7303 / 7401..7402.
   Budget counted in observable scalar learning operations, not Joules.
   Physical actions: ZERO. No promotion or retroactive WAG284 tuning.
*/
const WAG285_CONFIG=Object.freeze({
 primitive:'---@---@---@---@---{} → {\\a{b/}}',
 trainSeeds:[7301,7302,7303],heldoutSeeds:[7401,7402],
 examplesPerSeed:4,stepsPerExample:48,
 maxEpochs:2,referenceEpochs:9,
 maxTrainPairs:1152,maxCoefficientUpdates:64,
 coefficientMemorySlots:32,gradientAccumulatorSlots:64,
 minWeight:.025,maxWeight:.245,
 learningFraction:.57,actionAuthority:'WAG-261 only'
});
function wag285Dataset(seeds){
 const cases=wag283Dataset(seeds);
 if(cases.some(z=>z.samples.length!==WAG285_CONFIG.stepsPerExample))
  throw Error('unexpected sample length');
 return cases;
}
function wag285TrainBounded(dataset){
 const expectedPairs=dataset.reduce((s,z)=>s+z.samples.length,0);
 const requiredPairs=expectedPairs*WAG285_CONFIG.maxEpochs;
 if(requiredPairs>WAG285_CONFIG.maxTrainPairs)
  throw Error('attempt to exceed observation budget');
 const weights=wag283Weights('channels'),snapshots=[],
  ledger={epochs:0,trainingPairsUsed:0,coefficientUpdates:0,
   memorySlots:32,gradientAccumulatorSlots:64,violations:0};
 const bounded=x=>Math.max(WAG285_CONFIG.minWeight,Math.min(WAG285_CONFIG.maxWeight,x));
 for(let epoch=0;epoch<=WAG285_CONFIG.maxEpochs;epoch++){
  snapshots.push({epoch,trainOneStepMSE:wag283OneStepLoss(dataset,weights).mse,
   weights:weights.map(z=>z.slice())});
  if(epoch===WAG285_CONFIG.maxEpochs)break;
  const grad=Array.from({length:4},()=>Array(8).fill(0)),
   curvature=Array.from({length:4},()=>Array(8).fill(0));
  for(const c of dataset)for(const pair of c.samples){
   if(ledger.trainingPairsUsed>=WAG285_CONFIG.maxTrainPairs)
    throw Error('observation budget exhausted');
   const p=wag283Step(pair.state,weights),
    a=wag283Vector(p.state),b=wag283Vector(pair.next);
   ledger.trainingPairsUsed++;
   for(let edge=0;edge<4;edge++)for(let lane=0;lane<8;lane++){
    const x=p.factors[edge][lane];
    grad[edge][lane]+=2*x.difference*((a[x.right]-b[x.right])-
     (a[x.left]-b[x.left]))/48;
    curvature[edge][lane]+=4*x.difference*x.difference/48;
   }
  }
  for(let edge=0;edge<4;edge++)for(let lane=0;lane<8;lane++){
   if(ledger.coefficientUpdates>=WAG285_CONFIG.maxCoefficientUpdates)
    throw Error('coefficient update budget exhausted');
   weights[edge][lane]=bounded(weights[edge][lane]-
    WAG285_CONFIG.learningFraction*grad[edge][lane]/
    Math.max(1e-7,curvature[edge][lane]));
   ledger.coefficientUpdates++;
  }
  ledger.epochs++;
 }
 if(ledger.epochs>WAG285_CONFIG.maxEpochs||
  ledger.trainingPairsUsed>WAG285_CONFIG.maxTrainPairs||
  ledger.coefficientUpdates>WAG285_CONFIG.maxCoefficientUpdates||
  weights.flat().length>WAG285_CONFIG.coefficientMemorySlots)
  throw Error('budget invariant violated');
 return {weights,ledger,snapshots};
}
function wag285Experiment(){
 const train=wag285Dataset(WAG285_CONFIG.trainSeeds),
  heldout=wag285Dataset(WAG285_CONFIG.heldoutSeeds);
 const budget=wag285TrainBounded(train);
 const reference=wag283TrainModel(train,'channels');
 const starting=wag283Weights('channels');
 const before=wag283Rollout(heldout,starting),
  bounded=wag283Rollout(heldout,budget.weights),
  unconstrained=wag283Rollout(heldout,reference.weights);
 const cases=heldout.map((c,i)=>({seed:c.seed,pattern:c.pattern,
  initialMSE:before.cases[i].mse,budgetedMSE:bounded.cases[i].mse,
  referenceMSE:unconstrained.cases[i].mse,
  budgetBeatsInitial:bounded.cases[i].mse<before.cases[i].mse,
  budgetBeatsReference:bounded.cases[i].mse<unconstrained.cases[i].mse,
  series:{initial:before.cases[i].series,
   budgeted:bounded.cases[i].series,reference:unconstrained.cases[i].series}}));
 const summary={trainingCases:train.length,heldoutCases:heldout.length,
  initialHeldoutMSE:before.mse,budgetHeldoutMSE:bounded.mse,
  referenceHeldoutMSE:unconstrained.mse,
  budgetGainRatio:before.mse?1-bounded.mse/before.mse:0,
  referenceGapRatio:unconstrained.mse?bounded.mse/unconstrained.mse-1:0,
  budgetWinsAgainstInitial:cases.filter(z=>z.budgetBeatsInitial).length,
  budgetWinsAgainstReference:cases.filter(z=>z.budgetBeatsReference).length,
  maxConservationResidual:Math.max(before.maxResidual,bounded.maxResidual,
   unconstrained.maxResidual),budgetWithinLimits:true,physicalActions:0};
 return {bound:'WAG-285',phase:'WAG-IV',turn:5,config:WAG285_CONFIG,
  budgetModel:budget,referenceModel:{weights:reference.weights,
   trainingEpochs:WAG283_CONFIG.epochs,
   trainingObservationPasses:train.length*48*WAG283_CONFIG.epochs,
   coefficientUpdates:32*WAG283_CONFIG.epochs},
  summary,cases,
  limitations:[
   'Computation is accounted as pair-evaluations and coefficient updates, NOT physical energy',
   'This is a synthetic eight-lane transport teacher, not the failed WAG284 repair-value objective',
   'The reference model has a larger training budget and is not a physical control baseline',
   'Heldout examples originate from the same synthetic teacher family; no new physics',
   'No candidate is permitted to change physical repairs and Phase III remains sealed'
  ]};
}
if(typeof module!=='undefined')module.exports={WAG285_CONFIG,wag285Dataset,
 wag285TrainBounded,wag285Experiment};
