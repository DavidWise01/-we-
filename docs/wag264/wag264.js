/* WAG-264 · precommitted frozen controller selection · Phase II 8/12 · .dlw
   Frozen policy chosen on train-only seeds 5301..5303, then evaluated
   on disjoint 5401..5404 without threshold or policy adjustment.
   No hidden drift schedule available to online action selector; baseline
   WAG-261 and downgrade WAG-263 share same synthetic source genealogy.
*/
const WAG264_TRAIN=[5301,5302,5303],WAG264_HOLDOUT=[5401,5402,5403,5404];
const WAG264_FAMILIES=['scar','combined','phaseflip','famine'];
const WAG264_DRIFTS=['none','drain','pulse','recovery'];
const WAG264_TOLERANCE=0.0001; // fixed before test
function wag264Assess(cap,seeds,models,horizon){
 const summary={cap,n:0,aliveDelta:0,reserveDelta:0,integrityDelta:0,
  integrityRegressions:0,aliveRegressions:0,reserveRegressions:0,suppressed:0};
 for(const family of WAG264_FAMILIES)for(const drift of WAG264_DRIFTS)for(const seed of seeds){
  const adaptive=wag263Run(cap,family,seed,240,drift,'adaptive',models,horizon);
  const baseline=wag263Run(cap,family,seed,240,drift,'baseline',models,horizon);
  const da=adaptive.aliveTicks-baseline.aliveTicks;
  const dr=adaptive.reserveTicks-baseline.reserveTicks;
  const di=adaptive.meanIntegrity-baseline.meanIntegrity;
  summary.n++;summary.aliveDelta+=da;summary.reserveDelta+=dr;summary.integrityDelta+=di;
  summary.integrityRegressions+=di< -1e-10?1:0;
  summary.aliveRegressions+=da<0?1:0;summary.reserveRegressions+=dr<0?1:0;
  summary.suppressed+=adaptive.suppressed;
 }
 for(const key of ['aliveDelta','reserveDelta','integrityDelta'])summary[key]/=summary.n;
 return summary;
}
function wag264Freeze(models,horizon){
 const training=CAP234.map(cap=>wag264Assess(cap,WAG264_TRAIN,models,horizon));
 const policy={};
 for(const z of training){
  // Strict objective: do not accept observed survival or reserve losses,
  // require nonnegative mean survival/reserve advantage and tolerate at most
  // 0.0001 mean integrity loss. Baseline wins deterministic equality.
  const eligible=z.aliveRegressions===0&&z.reserveRegressions===0&&
    z.aliveDelta>=0&&z.reserveDelta>=0&&z.integrityDelta>=-WAG264_TOLERANCE;
  const meaningful=z.aliveDelta>0||z.reserveDelta>0||z.integrityDelta>0;
  policy[z.cap]=eligible&&meaningful?'adaptive':'baseline';
 }
 return {bound:'WAG-264',trainingSeeds:WAG264_TRAIN,holdoutSeeds:WAG264_HOLDOUT,
  policy,training,integrityTolerance:WAG264_TOLERANCE,
  selection:'zero observed survival/reserve regressions plus mean integrity floor; exact ties choose baseline',
  immutable:true};
}
function wag264VerifyFreeze(frozen){
 if(!frozen||frozen.bound!=='WAG-264'||frozen.immutable!==true||
    JSON.stringify(frozen.trainingSeeds)!==JSON.stringify(WAG264_TRAIN)||
    JSON.stringify(frozen.holdoutSeeds)!==JSON.stringify(WAG264_HOLDOUT))
   throw Error('Missing or invalid precommitted policy');
 for(const cap of CAP234)if(!['baseline','adaptive'].includes(frozen.policy[cap]))
   throw Error('Missing frozen action for capacity '+cap);
 return true;
}
function wag264Run(cap,family,seed,duration,drift,frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 const selected=frozen.policy[cap];
 const run=wag263Run(cap,family,seed,duration,drift,selected,models,horizon);
 return {...run,mode:'frozen-'+selected,
  frozenDecision:selected,frozenSource:'docs/wag264/frozen-policy.json',
  trainingSeeds:frozen.trainingSeeds,
  evaluationWasInTraining:frozen.trainingSeeds.includes(seed)};
}
function wag264Experiment(frozen){
 wag264VerifyFreeze(frozen);
 const models=wag251Models(),horizon=wag261Train(models),groups={},examples=[];
 for(const cap of CAP234)for(const family of WAG264_FAMILIES)
 for(const drift of WAG264_DRIFTS)for(const seed of WAG264_HOLDOUT){
  const chosen=wag264Run(cap,family,seed,240,drift,frozen,models,horizon);
  const baseline=wag263Run(cap,family,seed,240,drift,'baseline',models,horizon);
  const adaptive=wag263Run(cap,family,seed,240,drift,'adaptive',models,horizon);
  const key=drift+':'+family,g=groups[key]??={n:0,chosenAdaptive:0,
   integrityDelta:0,aliveDelta:0,reserveDelta:0,integrityRegressions:0,
   aliveRegressions:0,reserveRegressions:0,adaptiveIntegrityDelta:0};
  const di=chosen.meanIntegrity-baseline.meanIntegrity,
   da=chosen.aliveTicks-baseline.aliveTicks,
   dr=chosen.reserveTicks-baseline.reserveTicks;
  g.n++;g.chosenAdaptive+=chosen.frozenDecision==='adaptive'?1:0;
  g.integrityDelta+=di;g.aliveDelta+=da;g.reserveDelta+=dr;
  g.integrityRegressions+=di< -1e-10?1:0;
  g.aliveRegressions+=da<0?1:0;g.reserveRegressions+=dr<0?1:0;
  g.adaptiveIntegrityDelta+=adaptive.meanIntegrity-baseline.meanIntegrity;
  if(cap===13&&seed===5401)examples.push({family,drift,policy:chosen.frozenDecision,
   integrity:chosen.meanIntegrity,reference:baseline.meanIntegrity,
   adaptive:adaptive.meanIntegrity,alive:chosen.aliveTicks,reserve:chosen.reserveTicks});
 }
 for(const g of Object.values(groups))for(const key of ['integrityDelta','aliveDelta','reserveDelta','adaptiveIntegrityDelta'])g[key]/=g.n;
 return {bound:'WAG-264',phase:'II',turn:8,frozenPolicy:frozen.policy,
  holdoutSeeds:WAG264_HOLDOUT,groups,examples,
  limitation:'Same inherited synthetic simulator; selection is trained separately but not independently physically validated'};
}
if(typeof module!=='undefined')module.exports={wag264Freeze,wag264VerifyFreeze,wag264Run,wag264Experiment};
