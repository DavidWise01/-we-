# WAG-233 · Learning the cost of being wrong

.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

WAG-233 extends the WAG-232 model-estimated decision gate with a running estimate of **matured** 12-tick energy-forecast error (exponential weight 0.04) and observed integrity deterioration (weight 0.08). Forecast errors are learned only after their 12-tick outcomes become observable. The uncertainty margin increases with the matured error and integrity deterioration; no future observations or scenario labels enter controller decisions. This is observational error-based caution, NOT causal learning from the unexecuted action. The fallback remains WAG-230 graded defense.

Evaluation: five inherited synthetic stress families plus two new pressure-only families, `phaseflip` (midstream phase reversal) and `bursts` (short shocks every 57 ticks). New seeds 901–908, capacities 5/8/13/21, four policies (learned WAG-233, fixed-gate WAG-232, graded WAG-230, forecast WAG-231). Same energy and damage equations; new families do not introduce hidden resource depletion. 896 policy runs / 215040 ticks. WAG-233 vs WAG-230 mean-integrity comparison: 6 wins, 44 losses, 174 ties at 1e-6 tolerance. Proposed actions 5312, accepted 2417, rejected 2895. Complete adverse comparisons and representative trajectories are preserved.

No claim of universal improvement, biological homeostasis, field validation, or realized causal effect of rejected actions. Model parameters were not selected by optimization on these seeds, but are explicit design assumptions. GitHub Pages publication requires separate checking.
