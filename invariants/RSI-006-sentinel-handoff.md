# RSI-006 — Sentinel handoff and emergency wake

Three teams of three rotate one sentinel per logical tick. A change of three or more in its observed signal, or an unavailable scheduled sentinel, wakes all available team members. Two quiet ticks restore normal duty. Resting members use a cheap direct sentinel response instead of the three 9-action scoring layers. Counts are modeled score evaluations, not CPU benchmarks. The rest/replay labels do not implement sleep consolidation. Signals at unsensed positions may differ; hidden gradients are explicitly included as a counterexample scenario. Unavailable members are modeled as temporarily frozen, not charged resistance during absence; this is a limitation. No recursive improvement claim.

The normal full-live tick has 3*27+6*1=87 modeled work units versus 243 in the full scoring baseline. Actual runtime and survival comparison are unverified because the local execution environment was unavailable. Eight Python tests are supplied but not run. The original RSI-002 substrate is copied unchanged.

Next RSI-007: bounded spatial blind spots, explicit availability costs, and inter-team handoff acknowledgment.
