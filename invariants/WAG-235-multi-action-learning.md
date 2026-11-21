# WAG-235 · Multi-action learning

.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

Four options: baseline WAG-230 graded defense, conserve (reduce protection), hold existing protection, boost protection by 0.095 up to capacity ceiling. Offline cloned-state paired 12-tick synthetic rollouts use identical future forcing in both branches; future forcing is unavailable at online decision time. Train seeds 1201–1208, five families chirp/scar/famine/friction/combined, 16781 comparisons. 4 capacity × 9 observable-state bins; approval is >=16 samples and mean -1.96 standard errors >0.00012. This normal margin is a heuristic, not a statistical coverage guarantee because trials are correlated. 15 approved bins (the action selected is boosting protection).

Disjoint test seeds 1301–1308; 5 family-known scenarios and two families withheld from training (phaseflip, bursts). Total 448 policy runs, 107520 ticks. Known family W/L/T 125/35/0; withheld family W/L/T 64/0/0; 13516 applied actions. **Integrity gains can cost energy and reserve/survival ticks**; preserve every tradeoff in results.json. Withheld training families were used in earlier bounds, not novel physical dynamics. Synthetic simulation, not real-world validation. Pages deployment unverified.
