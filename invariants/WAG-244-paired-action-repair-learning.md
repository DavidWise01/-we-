# WAG-244 · Calibrated Prevention-versus-Reconstruction Value

.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

## Purpose and provenance

WAG-243 approved zero preventive actions using a hand-built benefit-per-resource ranking. WAG-244 executes **three independent cloned-state synthetic rollouts** for each eligible observed training state, taking PREVENT, REBUILD or ABSTAIN at the first tick and then abstaining for the remaining 11 ticks. Every branch receives identical future synthetic pressure and external energy flux. The baseline is ABSTAIN and the test reward is mean 12-tick integrity + 0.22 end energy + 0.028 surviving ticks + 0.035 remaining material. Only the offline trainer uses future forcing; deployed controller only uses the frozen state-category action table and current observation.

The simulator keeps WAG-240/241 finite renewable-source, material, transfer-delay, loss and repair-effect assumptions. Training seeds: 2201–2204; training family definitions: chirp, scar, famine, friction, combined; 1,840 states sampled and 1,198 action comparisons eligible. Categorization uses capacity (4), energy band (2), current observed pressure band (3) and structural-ceiling deficit (2), giving 48 bins. Per-action screening: >=10 paired samples and estimated mean minus 1.64 standard errors >0.00008. This is a **heuristic margin, not calibrated coverage** because cloned-trajectory branch scores are correlated; the bound title is an experimental aim rather than a demonstrated uncertainty calibration.

Frozen training approvals: 15 bins REBUILD, 33 ABSTAIN, 0 PREVENT. This is negative evidence against our current prevention mechanism and objective; not a universal claim that prevention never helps. Fully preserve counts and rejected alternatives in results.json.

## Holdout

Disjoint holdout seeds 2301–2304. Seven synthetic scenario families; phaseflip and bursts excluded from WAG-244 training although present in earlier studies. Four capacities, horizons 240/480/960/1920 ticks; arms TRAINED, PRIORITY heuristic, UNRESTRICTED HYBRID and ABSTAIN. 1,792 runs, 1,612,800 simulated ticks. Applied learned interventions: 13,967 REBUILD, 0 PREVENT. Maximum absolute resource reconciliation discrepancy 2.27e-13, including material/energy storage, finite transfer loss, energy source spill and in-flight withdrawals.

At 1,920 ticks and capacity 13, scar family: TRAINED mean integrity 0.994513, ABSTAIN 0.783981, HYBRID 0.993260; train policy material consumed 0.73675 per run on average. Combined disruption: TRAINED mean integrity 0.125372, ABSTAIN 0.126604, HYBRID 0.100871; survival ticks 248.5 vs 254.25 vs 221; reserve ticks 145 vs 206.75 vs 134.5. In the 1,920-tick familiar-family holdout, TRAINED versus ABSTAIN 21 wins / 11 losses / 48 ties in mean integrity; versus unrestricted HYBRID 69 wins / 11 losses. In withheld family tests, TRAINED matched ABSTAIN (32 ties), and beats unrestricted HYBRID in 30 cases (2 ties). Full 58 adverse cases preserved.

## Correct interpretation

The frozen policy demonstrates *conditional local payoff for paid reconstruction* but not long-horizon viability under severe combined stresses. The online scoring criterion undervalues reserve ticks and scarce future survival relative to short-term integrity. Absence of approved PREVENT may reflect a training distribution in which scar prevention requires earlier commitment, poorly estimated value for future damage, or the chosen rollout reward; no causal exclusion of prevention is established. External source flux and mechanical material efficiencies are stipulated synthetic assumptions, not physical or biological validation.

The WAG-244 source reproduces the 12-tick cloned branches. The results archive includes a set of representative sampled trajectories and all counterexamples, not every tick of every run.

## Next natural bound — WAG-245

**Long-Horizon Reserve-Adjusted Action Value.** Compare short-horizon benefit against measured later survival and reserve depletion using nested horizons 12/48/192. Train an abstention-aware policy that denies reconstruction when its deferred reserve cost dominates, while explicitly retaining prevention as a candidate where future damage can be avoided. Cross-check unseen seeds and new, truly withheld generator families.
