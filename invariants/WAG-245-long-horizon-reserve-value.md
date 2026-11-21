# WAG-245 · Long-Horizon Reserve-Adjusted Action Value

.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

## Experiment

WAG-244 favored reconstruction based on 12-tick cloned rollouts but worsened energy reserve and survival under combined synthetic stresses. WAG-245 tests three candidate actions—PREVENT, REBUILD, ABSTAIN—at matched training states using nested 12, 48 and 192 simulated ticks. Each pair shares deterministic disturbance and resource forcing, and applies a candidate maintenance action only on the first branch tick. The subsequent ticks abstain in both branches. This is explicitly a **one-step causal intervention**, not a simulation of repeated maintenance policies. Offline training may inspect known future forcing; online control only uses the learned frozen category table.

Score difference per horizon is average integrity +0.25 reserve-tick fraction +0.50 survival-tick fraction +0.18 final energy +0.04 final material. Approval requires >=8 training samples and a lower-normal-error screening bound >0.00005 at 192 ticks, no large negative screening bound at 48 or 12 ticks, nonnegative reserve/survival estimates within -0.003, and final energy difference >=-0.035. These are conservative heuristic thresholds. Normal-error bounds over related cloned trajectories are **not calibrated probability intervals** and should not be represented as such.

Training seeds 2401–2404; familiar synthetic families chirp/scar/famine/friction/combined. Training sampled just t=24,36,48 from each 240-tick trajectory; 240 sampled states and 324 eligible action-horizon comparisons. The resulting table approved no maintenance actions: 48/48 ABSTAIN, zero PREVENT, zero REBUILD. This *does not establish repair is never worthwhile*. Restrictive early snapshots, coarse bins, comparator weighting and the gate may have excluded useful interventions.

## Holdout

Fresh holdout seeds 2501–2504, seven synthetic families (phaseflip and bursts excluded from WAG-245 training, although known in prior WAG experiments), capacities 5/8/13/21 and 240/480/960/1920-tick horizons. Four policies: WAG-245 frozen long-horizon, WAG-244 frozen twelve-tick, unrestricted hybrid and no maintenance. 1,792 holdout policy runs (1,612,800 ticks). WAG-245 executed 0 PREVENT and 0 REBUILD, exactly matching ABSTAIN in all matched cases. Because no maintenance was applied, there are zero regressions against abstain by construction, not a demonstrated general safety guarantee. All 58? No: the results object has an empty adverse list for the abstention comparison, while against WAG-244 many cases are worse. Keep the complete matched tables and sampled traces as evidence. Maximum ledger discrepancy 2.300486190431883e-13.

At 1,920 ticks and capacity 13, scar: WAG-245 mean integrity 0.785074, final integrity 0.643314, vs WAG-244 mean integrity 0.994467, final integrity 0.995938. Combined disruption: WAG-245 mean integrity 0.138800 and surviving ticks 313.0 vs WAG-244 mean integrity 0.131347 and surviving ticks 286.75; WAG-245 reserve ticks 236.5 vs WAG-244 189.75.

In the 1,920-tick familiar-family holdout, WAG-245 versus WAG-244 mean-integrity results: 15 wins, 17 losses, 48 ties (80 paired cases). On the two withheld-from-training families, all 32 comparisons tied WAG-244 because neither acted.

## Important limits

- The environment and repair effects remain synthetic and stipulated. Energy and material ledgers are numerically consistent; this is not real-world verification.
- The action outcomes do not prove long-horizon safety; learning ABSTAIN everywhere is excessive conservatism.
- The long-horizon train sampled only early-phase states from 240-tick runs, causing severe distribution mismatch with much later recovery choices.
- The rollout's lower-error screening margin does not have validated statistical coverage and is not externally calibrated.
- A simulated intervention's single-tick benefit may not predict the outcome of repeated rehabilitation actions.

**Next natural bound — WAG-246: State-Stratified Recovery Opportunity.** Build a time- and structural-deficit-stratified training sampler covering early, middle and late stress, and add explicit false-abstention cost. Restore permission to reconstruct in demonstrably viable regimes while preserving abstention under persistent deficit. Verify action diversity and holdout survival rather than treating zero interventions as success.

GitHub source results and living lab are linked from the matching docs path. GitHub Pages deployment is unverified.
