/* WAG-275 · {a{b}} long-horizon regret ledger · Phase III 7/12 · .dlw
 Predeclared: 6201..6203, 240/480 ticks, four WAG274 stress families.
 Counterfactual is a matched policy trajectory, NOT one-action causal effect.
 Regret = area under positive (frozen integrity - mesh integrity).
 Repair omissions are episodes when frozen repaired and mesh abstained,
 with follow-up lag 24 and 48 tick signed integrity difference; observational.
 Conservation verified through original WAG274 engine. No weight changes.
*/
const WAG275_SEEDS=[6201,6202,6203],WAG275_HORIZONS=[240,480],
 WAG275_CAP=[8,13],WAG275_FAMILIES=['scar','combined'],
 WAG275_FORCES=['antiphase','surge-crash','shrinking-cycle','dual-burst'],
 WAG275_LAGS=[24,48];
function wag275Compare(f,m){
 if(f.duration!==m.duration||f.trace.length!==m.trace.length)throw Error('not matched');
 const d=f.duration,series=[],misses=[];
 let positiveLoss=0,negativeLoss=0,materialSavedArea=0,energySavedArea=0,
  pairedAliveGained=0,pairedAliveLost=0;
 for(let t=0;t<d;t++){
  const a=f.trace[t],b=m.trace[t],integrityDelta=a.integrity-b.integrity;
  const materialDelta=b.material-a.material,energyDelta=b.energy-a.energy;
  positiveLoss+=Math.max(0,integrityDelta);
  negativeLoss+=Math.max(0,-integrityDelta);
  materialSavedArea+=materialDelta;energySavedArea+=energyDelta;
  const fa=a.energy>.08&&a.integrity>.15,ma=b.energy>.08&&b.integrity>.15;
  if(ma&&!fa)pairedAliveGained++;
  if(fa&&!ma)pairedAliveLost++;
  if(a.action!=='abstain'&&b.action==='abstain'){
   misses.push({tick:t,expectedAction:a.action,
    beforeIntegrityDelta:integrityDelta,
    beforeMaterialDelta:materialDelta,
    horizons:Object.fromEntries(WAG275_LAGS.map(l=>[l,t+l<d?
     +(f.trace[t+l].integrity-m.trace[t+l].integrity).toFixed(12):null]))});
  }
  series.push({tick:t,integrityDelta,materialDelta,energyDelta,
   cumRegret:positiveLoss/d,cumAdvantage:negativeLoss/d,
   frozenAction:a.action,meshAction:b.action});
 }
 return {positiveIntegrityRegret:positiveLoss/d,
  meshIntegrityAdvantage:negativeLoss/d,
  signedIntegrityDelta:(positiveLoss-negativeLoss)/d,
  materialSavedArea:materialSavedArea/d,
  energySavedArea:energySavedArea/d,
  missedRepairEpisodes:misses.length,
  pairedAliveGained,pairedAliveLost,
  meanAliveDelta:m.aliveTicks-f.aliveTicks,
  meanReserveDelta:m.reserveTicks-f.reserveTicks,
  missedRepairs:misses,series};
}
function wag275Aggregate(rows){
 const n=rows.length;const avg=key=>rows.reduce((s,z)=>s+z[key],0)/n;
 return {n,positiveIntegrityRegret:avg('positiveIntegrityRegret'),
  meshIntegrityAdvantage:avg('meshIntegrityAdvantage'),
  signedIntegrityDelta:avg('signedIntegrityDelta'),
  meanMaterialSaved:avg('materialSavedArea'),
  meanEnergySaved:avg('energySavedArea'),
  meanAliveDelta:avg('meanAliveDelta'),
  meanReserveDelta:avg('meanReserveDelta'),
  missedRepairEpisodes:rows.reduce((s,z)=>s+z.missedRepairEpisodes,0),
  aliveRegressions:rows.filter(z=>z.meanAliveDelta<0).length,
  integrityRegressions:rows.filter(z=>z.signedIntegrityDelta>1e-12).length};
}
function wag275Experiment(frozen,models,horizon){
 wag264VerifyFreeze(frozen);
 const rows=[],episodes=[],cases=[];
 for(const duration of WAG275_HORIZONS)for(const family of WAG275_FAMILIES)
 for(const force of WAG275_FORCES)for(const cap of WAG275_CAP)
 for(const seed of WAG275_SEEDS){
  const a=wag274Run(cap,family,seed,duration,force,'frozen',frozen,models,horizon),
   b=wag274Run(cap,family,seed,duration,force,'mesh',frozen,models,horizon);
  const c=wag275Compare(a,b),id={duration,family,force,cap,seed};
  const row={...id,positiveIntegrityRegret:c.positiveIntegrityRegret,
   meshIntegrityAdvantage:c.meshIntegrityAdvantage,
   signedIntegrityDelta:c.signedIntegrityDelta,
   materialSavedArea:c.materialSavedArea,
   energySavedArea:c.energySavedArea,
   missedRepairEpisodes:c.missedRepairEpisodes,
   pairedAliveGained:c.pairedAliveGained,pairedAliveLost:c.pairedAliveLost,
   meanAliveDelta:c.meanAliveDelta,
   meanReserveDelta:c.meanReserveDelta,
   frozenRepairs:a.repairs,meshRepairs:b.repairs,
   maxResidual:Math.max(a.residual,b.residual),
   maxContinuity:Math.max(a.ledger.continuity,b.ledger.continuity)};
  rows.push(row);cases.push(id);
  const late=c.missedRepairs.map(z=>({...id,...z}));
  episodes.push(...late);
 }
 const byHorizon=Object.fromEntries(WAG275_HORIZONS.map(duration=>
  [duration,wag275Aggregate(rows.filter(z=>z.duration===duration))]));
 const lags=Object.fromEntries(WAG275_LAGS.map(l=>{
  const eligible=episodes.filter(z=>z.horizons[l]!==null);
  return [l,{n:eligible.length,positiveIntegrityGap:eligible.filter(z=>z.horizons[l]>1e-12).length,
   negativeIntegrityGap:eligible.filter(z=>z.horizons[l]< -1e-12).length,
   averageSignedGap:eligible.length?
    eligible.reduce((s,z)=>s+z.horizons[l],0)/eligible.length:null}];
 }));
 return {bound:'WAG-275',phase:'WAG-III',turn:7,primitive:'{a{b}}',
  seeds:WAG275_SEEDS,lags:WAG275_LAGS,byHorizon,lagLedger:lags,
  rows,episodes,
  summary:{policyRuns:rows.length*2,matchedConditions:rows.length,
   missedRepairEpisodes:episodes.length,
   meshIntegrityRegressions:rows.filter(z=>z.signedIntegrityDelta>1e-12).length,
   meshAliveRegressions:rows.filter(z=>z.meanAliveDelta<0).length,
   maxConservationResidual:Math.max(...rows.map(z=>z.maxResidual)),
   maxContinuity:Math.max(...rows.map(z=>z.maxContinuity))},
  caveats:['Matched-policy regret is descriptive, not isolated causal repair effect',
    'Saved material area includes all downstream trajectory differences, not only action cost',
    'Overlapping repair windows and consecutive ticks are dependent',
    'Mesh weights remain fixed and Phase II frozen baseline unchanged',
    'No policy promotion']};
}
if(typeof module!=='undefined')module.exports={wag275Compare,wag275Aggregate,wag275Experiment};
