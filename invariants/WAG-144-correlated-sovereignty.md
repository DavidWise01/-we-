# WAG-144 — Correlated sovereignty

10 local Python tests passed in 0.294s; 3445 feasible symmetry-reduced designs at budget 39. Host groups are disjoint; each either shares signing custody or isolates every key. Synthetic cost = witnesses + 2 per host + 1 per isolated key in a non-singleton group. Score lexicographically maximizes minimum resistance, minimum availability/certification, sum of resistances, lower cost, higher quorum. At budget 29 the selected design is (8,3,3), versus (8,3,5) under the previous assumption. At 39 the selected design is (13,5,5).

Limitations: no actual custody or pricing verification; no overlapping admin/provider dependencies or mixed-mode attack sequences; isolated keys assumed immune to host signing compromise, including unauthorized requests. These are structural domain counts, not probabilities. No live consensus implementation. Next WAG-145: overlapping cross-domain compromise and minimal joint attack sets.
.dlw
