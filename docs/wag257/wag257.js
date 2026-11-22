/* WAG-257 · The Value of Knowing · Phase II turn 1/12 · .dlw
   Post-hoc paired accounting. Decision policy remains unchanged from WAG-256.
   The "value" is observable net outcome delta, not estimated information value.
   No oracle future used online. All labels are retrospective diagnostics.
*/
const WAG257_TEST=[4401,4402,4403,4404];
const WAG257_REGIMES=['stable','surcharge','nonlinear','shock'];
const WAG257_FAMILIES=['scar','combined','phaseflip','famine'];
function wag257Utility(r){
 const n=r.duration,trace=r.trace||[];
 const final=trace.at(-1)||{};
 // The inherited simulator may recompute terminal energy from internal cache;
 // therefore external switch fees must be charged in a separate expense ledger.
 // This is an explicit accounting adjustment, not a claim that the physical state
 // persisted the debit. The energy component is left as the simulator reports it.
 const material=Number.isFinite(final.material)?final.material:NaN;
 const energy=r.finalEnergy,integrity=r.meanIntegrity;
 const alive=r.aliveTicks/n,reserve=r.reserveTicks/n;
 const feeExpense=.18*r.fees;
 const utility=integrity+.5*alive+.25*reserve+.18*energy-feeExpense+
  (Number.isFinite(material)?.04*material:0);
 return {utility,integrity,alive,reserve,energy,material,
  materialComponentIncluded:Number.isFinite(material),
  feeExpense,feeAlreadyInternalized:false,feeAccounting:'external charges expensed separately; underlying energy persistence unverified'};
}
function wag257ActionDeltas(a,b){
 const n=Math.min(a.trace.length,b.trace.length);
 let different=0,first=-1,after=0;
 const probeEnd=a.transactions.filter(z=>z.probe).reduce((m,z)=>Math.max(m,z.tick),-1);
 for(let i=0;i<n;i++){
  const left=a.trace[i].maintenance,right=b.trace[i].maintenance;
  if(left!==right){different++;if(first<0)first=i;if(i>probeEnd)after++;}
 }
 return {differentTicks:different,firstDifferentTick:first,
  afterLastProbeDifferentTicks:after,lastProbeTransactionTick:probeEnd,
  caveat:'Action differences may be mechanical consequences of changed cadence; not isolated causal information effects'};
}
function wag257Pair(cap,family,seed,duration,regime,models,cadence,cost){
 const policies={};
 for(const mode of ['valueProbe','periodicProbe','noProbe','frozen'])
  policies[mode]=wag256Run(cap,family,seed,duration,regime,mode,models,cadence,cost);
 const no=policies.noProbe,noValue=wag257Utility(no);
 const comparisons={};
 for(const mode of ['valueProbe','periodicProbe','frozen']){
   const run=policies[mode],value=wag257Utility(run);
   const delta=value.utility-noValue.utility;
   const actions=wag257ActionDeltas(run,no);
   comparisons[mode]={mode,utility:value.utility,deltaUtility:delta,
    informationPaid:run.probeDebits,additionalTotalFee:run.fees-no.fees,
    materialInUtility:value.materialComponentIncluded,
    recoveredCost:delta>0,detectedTick:run.detectedTick,
    changedActions:actions.differentTicks,firstChanged:actions.firstDifferentTick,
    changesAfterProbe:actions.afterLastProbeDifferentTicks,
    probeCount:run.probeCount,probeStage:run.probeStage,
    aliveDelta:run.aliveTicks-no.aliveTicks,reserveDelta:run.reserveTicks-no.reserveTicks,
    integrityDelta:run.meanIntegrity-no.meanIntegrity,
    finalEnergyDelta:run.finalEnergy-no.finalEnergy,
    noProbeLearned: no.detectedTick!==null};
 }
 return {cap,family,seed,duration,regime,baseline:noValue,
  comparisons,policies,
  interpretation:'Paired outcomes identify intervention net effect. Knowledge-specific causal benefit requires isolating probe information from its physical cadence change.'};
}
function wag257Models(){const models=wag251Models(),cadence=wag252Train(models),cost=wag254Train(models);
 return {models,cadence,cost};}
function wag257Experiment(){
 const {models,cadence,cost}=wag257Models(),groups={},examples=[];
 for(const regime of WAG257_REGIMES)for(const duration of [240,480])
 for(const family of WAG257_FAMILIES)for(const cap of CAP234)for(const seed of WAG257_TEST){
  const p=wag257Pair(cap,family,seed,duration,regime,models,cadence,cost);
  const key=regime+':'+duration+':'+family;
  const g=groups[key]??={n:0,positiveNet:0,probed:0,detect:0,meanNet:0,meanExtraFee:0,
   meanActionChanges:0,meanIntegrityDelta:0,nonInferiorSurvival:0};
  const v=p.comparisons.valueProbe;
  g.n++;g.positiveNet+=v.deltaUtility>0?1:0;g.probed+=v.probeCount>0?1:0;
  g.detect+=v.detectedTick!==null?1:0;g.meanNet+=v.deltaUtility;
  g.meanExtraFee+=v.additionalTotalFee;g.meanActionChanges+=v.changedActions;
  g.meanIntegrityDelta+=v.integrityDelta;
  g.nonInferiorSurvival+=v.aliveDelta>=0&&v.reserveDelta>=0?1:0;
  if(cap===13&&seed===4401&&duration===240)examples.push({
   regime,family,seed,baseline:p.baseline,
   comparisons:p.comparisons,
   receipts:p.policies.valueProbe.transactions});
 }
 for(const g of Object.values(groups))for(const k of ['meanNet','meanExtraFee','meanActionChanges','meanIntegrityDelta'])g[k]/=g.n;
 return {bound:'WAG-257',phase:'II',turn:1,plannedTurns:12,
   matchedRuns:Object.values(groups).reduce((n,g)=>n+g.n,0),
   testSeeds:WAG257_TEST,regimes:WAG257_REGIMES,families:WAG257_FAMILIES,groups,examples,
   limitations:['Single synthetic simulator','Utility weights declared, not empirically discovered',
    'Action deltas combine physical probe intervention and receipt-driven policy responses',
    'No claims of positive VOI unless holdout delta is positive']};
}
if(typeof module!=='undefined')module.exports={wag257Utility,wag257Pair,wag257Models,wag257Experiment};
