/* WAG-280 final seal · Phase III research release verifier.
 No controller decisions changed. Validates aggregate receipts and declared
 one-ancestry policy conclusion; does not imply live Pages verification.
*/
function wag280Verify(manifest, frozen, crystalReceipt, holdoutReceipt, reductionReceipt, falsificationReceipt, progress){
 const assert=(ok,message)=>{if(!ok)throw Error('WAG280 seal failure: '+message)};
 assert(manifest.release==='WAG-III-v1.0'&&manifest.bound==='WAG-280','release');
 assert(manifest.primitive==='---@---@---@---@---{} → {\\a{b/}} → one action','primitive');
 assert(manifest.decision.candidatePromoted===false&&manifest.decision.neuralWeightsTrained===false,'policy promotion');
 assert(manifest.freeze.policyPromotion==='NONE','reference policy');
 assert(frozen.status==='CANDIDATE_FROZEN_FOR_WAG277'&&frozen.promotion===false,'frozen candidate');
 assert(frozen.candidateSourceCommit==='01ece30bc8474d1f53220eded7df980a7154390e','candidate provenance');
 assert(crystalReceipt.summary.policyRuns===288&&crystalReceipt.summary.matchedConditions===96,'crystal cohort');
 assert(crystalReceipt.summary.crystalIntegrityRegressions===65,'crystal regression');
 assert(holdoutReceipt.summary.policyRuns===384&&holdoutReceipt.summary.matchedConditions===128,'withheld cohort');
 assert(holdoutReceipt.aggregate['720'].frozen.fullSurvival===29&&
  holdoutReceipt.aggregate['720'].crystal.fullSurvival===28,'720-tick adverse result');
 assert(holdoutReceipt.summary.crystalIntegrityRegressions===82,'withheld integrity');
 assert(reductionReceipt.summary.selected===8&&reductionReceipt.summary.exactReplayVerified,'counterexamples');
 assert(falsificationReceipt.summary.cases===8&&
  falsificationReceipt.summary.restoredSurvivalAtOriginalFailure===0,'failed surgical rescue');
 assert(progress.phase==='WAG-III'&&progress.completedTurns>=11,'tracker');
 if(progress.status==='CLOSED'){
  assert(progress.completedTurns===12&&progress.progressPercent===100,'closed progress');
  assert(progress.milestones.every(m=>m.accepted),'all milestones');
 }
 return {bound:'WAG-280',release:manifest.release,pass:true,
  checked:['canonical geometry','unpromoted candidate','fixed source ancestry',
   '288-run crystalline receipt','384-run withheld negative result',
   '8 exact minimal observable replays','8 tick-55 interventions',
   'reference policy unchanged','phase acceptance state'],
  phaseStatus:progress.status,candidatePromoted:false,
  livePagesVerified:false};
}
if(typeof module!=='undefined')module.exports={wag280Verify};
