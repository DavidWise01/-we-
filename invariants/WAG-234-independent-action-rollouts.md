# WAG-234 · Independent action-rollout learning

.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

From a cloned simulation state, execute two 12-tick branches under identical future disturbance. The baseline follows graded defense, while the alternative lowers protection at its first tick and resumes baseline control thereafter. Score average 12-tick integrity + 0.08 final energy + 0.006 surviving ticks. The training algorithm alone sees paired future paths. Holdout controller sees only current observations and a frozen nine-cell table (energy band × observed pressure band).

Training seeds: 1001, 1002, 1003, 1004, 1005, 1006. Test seeds: 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108. 5085 paired simulated training comparisons. Nine bins, approved 0; approval requires at least twelve training pairs and positive estimated lower margin (mean - 1.64 standard errors > 0.00015). Correlated branches invalidate formal confidence interpretations; this is merely a heuristic. Holdout consists of 448 policy runs (107520 simulated ticks) across seven familiar scenario families and capacities 5/8/13/21: learned vs graded 0 wins, 0 losses, 224 ties. 0 interventions were applied. These are deterministic synthetic results, not independently established causal effects in the real world.

Negative outcome is preserved: no coarse bin earned permission to intervene, so the frozen policy matched its baseline exactly. Next needed test: richer action candidates and uncertainty-calibrated values, followed by truly new held-out families. GitHub Pages remains separately unverified.
