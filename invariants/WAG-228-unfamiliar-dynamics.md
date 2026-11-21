# WAG-228 · Homeostasis under unfamiliar environmental dynamics

`.dlw` · `{24/[2]/[4]/(3)/(3)/(1)/(1)}`

This is a synthetic out-of-family evaluation, using new scenario families and disjoint seeds 401–408, with capacities 5/8/13/21 and 240 ticks per run. Four policies: WAG-227-style conditional, WAG-225-style adaptive, fixed-eight memory, plus a new experimental reserve heuristic. **The reserve policy is exploratory, not a previously validated winner.** The WAG-227-style controller preserves the 32-point lag-14 periodicity trigger; no test-time retuning was applied.

New families: `chirp` accelerating oscillations; `scar` permanent damage ceiling reduction (26% of instantaneous damage); `famine` recovery generation curtailed after tick 62 and repair effectiveness reduced; `friction` energy-dependent action-change expense; `combined` all perturbations. Noise comes from seeded LCG; each policy receives the same seed and scenario, and action-independent forcing. Metrics: mean integrity, final energy, reserve-eligible ticks (energy>0.25 and integrity>0.30), alive ticks, action transitions, irreversible damage, recoverable ceiling. Synthetic score only, not empirical biological homeostasis.

**Implementation note:** switching expense is shared across policies and energy-dependent in `friction`/`combined`. Controller proposal rules are intentionally preserved. The new environmental effects are model assumptions; they are not laws of nature. Recorded evidence contains complete example trajectories and all comparison rows. No selection of the controller on the new families was conducted.

Executed local deterministic JS experiment: 640 policy runs × 240 = 153600 simulated ticks. Conditional versus adaptive (unrounded mean integrity, tolerance 1e-6): 43 wins, 16 losses, 101 ties. This outcome is **not** a universal generalization claim. Counterexamples are preserved in `invariants/wag228/results.json`.

The model does not prove physically realistic homeostasis, emergence or resilience outside its equations. GitHub Pages availability requires independent verification.
