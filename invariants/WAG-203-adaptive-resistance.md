# WAG-203 — Adaptive resistance
.dlw
Executed JS test: 64 seeds, three policies, mirrored sign checks for each sample. Noise estimator is integer EWMA of adjacent ternary observation class transitions, denominator 64, scale 1024; use prior estimate >=64 to select robust rather than weighted gate. Missing samples preserve estimate and clear adjacency. Clean phase before reversal deliberately tests recovery of stricter gate. Thresholds designed; class transitions conflate noise with genuine changes. No physical timing or amplitude claims. Results in results.json.
