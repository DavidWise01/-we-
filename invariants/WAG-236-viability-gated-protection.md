# WAG-236 · Viability-gated protection

.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

This bound retains the **frozen WAG-235 trained action table**, learned exclusively on seeds 1201–1208 and families chirp/scar/famine/friction/combined. WAG-236 layers on a conservative viability gate for BOOST; other actions are unchanged. The gate uses only observed energy and the previous eight realized energy changes. A BOOST is blocked when current energy is lower than `0.35 + min(0.2, max(0, -meanRate)*14)`, or projected energy `energy + 12*min(0,meanRate)` falls below 0.28. These are heuristic safety thresholds chosen as engineering assumptions, not learned or statistically calibrated limits; no futures or scenario identifiers enter live decision logic.

Disjoint holdout seeds 1401–1408, five training-family environments plus two family-withheld environments (phaseflip and bursts). 672 policy runs, 161280 simulated ticks. 12271 BOOST executions and 1522 denied boosts. WAG-236 versus WAG-230 and WAG-235, by environment group: {"known":{"graded":{"wins":111,"losses":49,"ties":0},"wag235":{"wins":23,"losses":41,"ties":96}},"withheld":{"graded":{"wins":64,"losses":0,"ties":0},"wag235":{"wins":0,"losses":0,"ties":64}}}. Results measure mean integrity, final energy, surviving ticks, and reserve ticks separately. Preserve regressions and tradeoffs rather than reducing the decision to one scalar.

This is a synthetic controller experiment, not a demonstration of real biological homeostasis. The two withheld families were seen in earlier WAG versions. GitHub Pages deployment remains independently unverified.
