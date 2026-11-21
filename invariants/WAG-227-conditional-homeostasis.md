# WAG-227 · Energy-aware conditional homeostasis
.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

This bound returns the experiment to natural self-regulation. We build on WAG-226's simulation and observe (a) local pressure, (b) energy balance, (c) integrity protection, (d) controller state transitions. A conditional controller detects a periodic pressure pattern via a 32-sample window and negative lag-14 covariance (< -0.01) with total pressure span > 0.35. It uses WAG-225 adaptive memory and baseline stress gain, preserving fast response by default. Only while a periodic pattern is detected, and only inside the first eight ticks of an action dwell, it computes a one-step benefit from the difference in estimated environmental damage plus one quarter of the difference in energy cost; if benefit < 0, it defers the proposed switch. An emergency override from WAG-226 remains active.

To make switching explicitly costly and comparisons consistent, a synthetic energy penalty of 0.003 per action change is applied to ALL four replayed policy variants: conditional, adaptive, WAG-226 damped, and fixed eight-sample. These replayed comparator scores are NOT identical to prior WAG-225/WAG-226 published numbers because this new experiment added the shared penalty. The selected conditional policy was picked using only seeds 225-228 from a small parameter sweep (threshold candidates and dwell lengths). Holdout seeds 229-236 are disjoint from tuning but use the SAME synthetic forcing generator.

Held-out execution: 768 simulation runs, 184320 simulated ticks, 192 paired comparisons conditional versus adaptive: 22 wins, 0 regressions, 170 ties at recorded four-decimal average integrity. 8 paired switching reductions and 0 switching increases. 11828 controller ticks met the periodicity detector. Outcomes are synthetic, not independently replicated natural experiments.

5/stable: conditional 0.9978, adaptive 0.9978, damped 0.9978, fixed 0.9978; switches conditional/adaptive 0/0; wins/losses/ties 0/0/8
5/shock: conditional 0.8417, adaptive 0.8417, damped 0.8417, fixed 0.8417; switches conditional/adaptive 0/0; wins/losses/ties 0/0/8
5/oscillating: conditional 0.6199, adaptive 0.6199, damped 0.6199, fixed 0.6199; switches conditional/adaptive 0/0; wins/losses/ties 0/0/8
5/drift: conditional 0.8968, adaptive 0.8968, damped 0.8968, fixed 0.8968; switches conditional/adaptive 0/0; wins/losses/ties 0/0/8
5/recovery: conditional 0.6546, adaptive 0.6546, damped 0.6546, fixed 0.6546; switches conditional/adaptive 0/0; wins/losses/ties 0/0/8
5/default: conditional 0.7966, adaptive 0.7966, damped 0.7966, fixed 0.7966; switches conditional/adaptive 0/0; wins/losses/ties 0/0/8
8/stable: conditional 0.9984, adaptive 0.9984, damped 0.9984, fixed 0.9984; switches conditional/adaptive 0/0; wins/losses/ties 0/0/8
8/shock: conditional 0.9968, adaptive 0.9968, damped 0.9959, fixed 0.9957; switches conditional/adaptive 16/16; wins/losses/ties 0/0/8
8/oscillating: conditional 0.991, adaptive 0.991, damped 0.9905, fixed 0.9905; switches conditional/adaptive 128/128; wins/losses/ties 0/0/8
8/drift: conditional 0.9969, adaptive 0.9969, damped 0.9969, fixed 0.9969; switches conditional/adaptive 8/8; wins/losses/ties 0/0/8
8/recovery: conditional 0.9967, adaptive 0.9967, damped 0.9964, fixed 0.9964; switches conditional/adaptive 16/16; wins/losses/ties 0/0/8
8/default: conditional 0.9964, adaptive 0.9964, damped 0.996, fixed 0.9958; switches conditional/adaptive 32/32; wins/losses/ties 0/0/8
13/stable: conditional 0.9988, adaptive 0.9988, damped 0.9988, fixed 0.9988; switches conditional/adaptive 0/0; wins/losses/ties 0/0/8
13/shock: conditional 0.9982, adaptive 0.9982, damped 0.9978, fixed 0.9978; switches conditional/adaptive 40/40; wins/losses/ties 0/0/8
13/oscillating: conditional 0.7119, adaptive 0.6997, damped 0.6313, fixed 0.6168; switches conditional/adaptive 266/266; wins/losses/ties 7/0/1
13/drift: conditional 0.9847, adaptive 0.9847, damped 0.9847, fixed 0.983; switches conditional/adaptive 24/24; wins/losses/ties 0/0/8
13/recovery: conditional 0.8909, adaptive 0.8909, damped 0.8872, fixed 0.8916; switches conditional/adaptive 40/40; wins/losses/ties 0/0/8
13/default: conditional 0.9597, adaptive 0.9597, damped 0.9546, fixed 0.9581; switches conditional/adaptive 80/80; wins/losses/ties 0/0/8
21/stable: conditional 0.9991, adaptive 0.9991, damped 0.9991, fixed 0.9991; switches conditional/adaptive 0/0; wins/losses/ties 0/0/8
21/shock: conditional 0.9986, adaptive 0.9986, damped 0.9984, fixed 0.9984; switches conditional/adaptive 54/54; wins/losses/ties 0/0/8
21/oscillating: conditional 0.7517, adaptive 0.7365, damped 0.6574, fixed 0.6421; switches conditional/adaptive 270/299; wins/losses/ties 7/0/1
21/drift: conditional 0.9889, adaptive 0.9889, damped 0.9889, fixed 0.985; switches conditional/adaptive 24/24; wins/losses/ties 0/0/8
21/recovery: conditional 0.9154, adaptive 0.9154, damped 0.9102, fixed 0.9161; switches conditional/adaptive 40/40; wins/losses/ties 0/0/8
21/default: conditional 0.9631, adaptive 0.9599, damped 0.9527, fixed 0.9637; switches conditional/adaptive 96/98; wins/losses/ties 8/0/0

The test is not proof of universal optimality, consciousness, biological homeostasis, or spontaneous emergence. Action cost, thresholds, scenario families, and the word "periodic" are model assumptions. We preserve full representative trajectories and nonwinning outcomes. No claims of new physics, 11D geometry, physically measured Planck scales, external sensor data, or independently verified GitHub Pages deploy.

Next natural bound WAG-228: adaptive switching cost, shifting oscillation frequency and irreversible damage. Evaluate generalization across *new scenario families* rather than only unseen seeds.
