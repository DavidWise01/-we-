/* WAG-258 · hindsight-free episode-level information-value gate · .dlw
 Phase II turn 2/12. Train with paired WAG-256 trajectories, freeze a
 regime-blind policy, evaluate on held-out seeds. No future cost regime,
 privileged counterfactual or evaluation outcome enters action selection.
 This is an EPISODE-START gate only; per-opportunity learned VOI is WAG-259+.
*/
const WAG258_TRAIN=[4501,4502,4503],WAG258_TEST=[4601,4602,4603,4604];
const WAG258_FAMILIES=['scar','combined','phaseflip','famine'];
const WAG258_REGIMES=['stable','surcharge','nonlinear','shock'];
function wag258Features(cap,family,seed,duration,models){
 const x=start244(cap,family,seed,duration);x.modelTable=models.train250.source;
 return {cap,energy:x.s.energy,material:x.material,scar:Math.max(0,1-x.s.ceiling),
   pressure:x.f[x.t].observed,restTicks:duration};
}
function wag258Key(f){return [CAP234.indexOf(f.cap),f.energy<.45?'low':f.energy<.70?'mid':'high',
 f.material<.055?'scarce':'supplied',f.scar>.035?'scarred':'intact'].join(':')}
function wag258Parent(f){return [CAP234.indexOf(f.cap),f.material<.055?'scarce':'supplied'].join(':')}
function wag258Cell(){return {n:0,mean:0,m2:0,wins:0,fees:0,probes:0,actionChanges:0}}
function wag258Add(c,delta,probe,actions){c.n++;const d=delta-c.mean;c.mean+=d/c.n;c.m2+=d*(delta-c.mean);if(delta>0)c.wins++;c.fees+=(probe.fees-c.fees)/c.n;c.probes+=(probe.probeCount-c.probes)/c.n;c.actionChanges+=(actions-c.actionChanges)/c.n}
function wag258Train(models,cadence,cost){
 const fine={},coarse={},all=wag258Cell();let pairs=0;
 for(const cap of CAP234)for(const family of WAG258_FAMILIES)for(const seed of WAG258_TRAIN){
  const features=wag258Features(cap,family,seed,240,models);
  for(const regime of WAG258_REGIMES){
   const no=wag256Run(cap,family,seed,240,regime,'noProbe',models,cadence,cost);
   const probe=wag256Run(cap,family,seed,240,regime,'valueProbe',models,cadence,cost);
   const delta=wag257Utility(probe).utility-wag257Utility(no).utility;
   const changes=wag257ActionDeltas(probe,no).differentTicks;
   wag258Add(fine[wag258Key(features)]??=wag258Cell(),delta,probe,changes);
   wag258Add(coarse[wag258Parent(features)]??=wag258Cell(),delta,probe,changes);
   wag258Add(all,delta,probe,changes);pairs++;
  }
 }
 return {fine,coarse,global:all,pairs,seeds:WAG258_TRAIN,
  minFine:8,minCoarse:12,margin:.00001,
  procedure:'Regime-blind pooled training; no hidden regime in feature key; freeze before test'};
}
function wag258Decision(features,model){
 const f=model.fine[wag258Key(features)],c=model.coarse[wag258Parent(features)];
 const cell=f?.n>=model.minFine?f:c?.n>=model.minCoarse?c:null;
 if(!cell)return {action:'noProbe',reason:'insufficient-training',lower:null,mean:null,n:0};
 const se=cell.n>1?Math.sqrt(cell.m2/(cell.n-1)/cell.n):Infinity;
 const lower=cell.mean-1.64*se;
 const action=lower>model.margin?'valueProbe':'noProbe';
 return {action,reason:action==='valueProbe'?'positive-lower-net-value':'negative-or-uncertain-value',
  lower,mean:cell.mean,n:cell.n,estimatedWins:cell.wins/cell.n};
}
function wag258Pair(cap,family,seed,duration,regime,models,cadence,cost,trained){
 const features=wag258Features(cap,family,seed,duration,models);
 const choice=wag258Decision(features,trained);
 const no=wag256Run(cap,family,seed,duration,regime,'noProbe',models,cadence,cost);
 const always=wag256Run(cap,family,seed,duration,regime,'valueProbe',models,cadence,cost);
 const chosen=choice.action==='valueProbe'?always:no;
 const noU=wag257Utility(no).utility,alwaysU=wag257Utility(always).utility,chosenU=wag257Utility(chosen).utility;
 return {cap,family,seed,duration,regime,features,choice,netLearned:chosenU-noU,
  netAlways:alwaysU-noU,regretToBest:Math.max(noU,alwaysU)-chosenU,
  actionChanges:wag257ActionDeltas(chosen,no).differentTicks,
  runs:{learned:chosen,always,no},source:'post-hoc paired episode evaluation'};
}
function wag258Experiment(){
 const models=wag251Models(),cadence=wag252Train(models),cost=wag254Train(models),
 trained=wag258Train(models,cadence,cost),summary={},examples=[];
 for(const regime of WAG258_REGIMES)for(const family of WAG258_FAMILIES)
 for(const cap of CAP234)for(const seed of WAG258_TEST){
  const p=wag258Pair(cap,family,seed,240,regime,models,cadence,cost,trained);
  const key=regime+':'+family,z=summary[key]??={n:0,learnedNet:0,alwaysNet:0,
   positiveLearned:0,probesChosen:0,meanRegret:0,survivalNonInferior:0};
  z.n++;z.learnedNet+=p.netLearned;z.alwaysNet+=p.netAlways;
  z.positiveLearned+=(p.netLearned>0?1:0);z.probesChosen+=(p.choice.action==='valueProbe'?1:0);
  z.meanRegret+=p.regretToBest;
  z.survivalNonInferior+=(p.runs.learned.aliveTicks>=p.runs.no.aliveTicks&&
    p.runs.learned.reserveTicks>=p.runs.no.reserveTicks?1:0);
  if(cap===13&&seed===4601)examples.push({regime,family,choice:p.choice,
   learned:p.netLearned,always:p.netAlways,regret:p.regretToBest,
   learnedProbes:p.runs.learned.probeCount,baselineProbes:p.runs.no.probeCount});
 }
 for(const z of Object.values(summary))for(const k of ['learnedNet','alwaysNet','meanRegret'])z[k]/=z.n;
 return {bound:'WAG-258',phase:'II',turn:2,trainPairs:trained.pairs,
   trainSeeds:trained.seeds,testSeeds:WAG258_TEST,summary,examples,
   qualification:'Frozen episode gate, not a realtime per-opportunity learner. Held-out evaluation shares one simulator ancestry.'};
}
if(typeof module!=='undefined')module.exports={wag258Train,wag258Decision,wag258Pair,wag258Experiment};
