# WAG-229 · Recovery of recovery capacity

.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

WAG-228 found that integrity can remain relatively high even when energy collapses. WAG-229 adds REST, a low-cost, low-shield action, with a reserve-triggered controller and threat interrupt. The controller observes energy, stress, perceived pressure, and integrity. It does NOT receive the scenario name. REST enters when energy < 0.38, perceived pressure < 0.57, stress < 0.60, integrity > 0.27 and no threat. REST exits at energy > 0.53, observed pressure > 0.78, stress > 0.70, integrity < 0.26, or after 36 consecutive ticks; action-change fees are charged equally. REST upkeep .0015 and shielding .08 are synthetic assumptions. Control policies continue to share WAG-228 forcing and physics, including damaged ceiling and scarcity; we preserve old comparator implementations unchanged.

New disjoint seeds 501–508, five unfamiliar families, four capacities, four policies, 240 ticks each. 640 policy runs (153600 ticks). REST vs WAG-227 conditional mean integrity at 1e-6 tolerance: 60 wins, 27 losses, 73 ties. This is an out-of-family replay, not a physiological claim. Note that no added energy source exists: if available generation is structurally below even REST consumption, recovery cannot happen indefinitely. All failing cases and complete representative traces are retained in results JSON.

Tests and limitations: state and capacity invariants checked on each tick; numeric controller comparisons were executed deterministically in the JS runtime. No proof of homeostatic emergence, optimality, or real biology; GitHub Pages deployment not independently verified.
