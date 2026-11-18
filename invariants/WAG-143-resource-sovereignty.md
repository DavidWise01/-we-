# WAG-143 — Resource-constrained sovereignty

10 local tests passed in 0.034s. 507 unlabeled placement/quorum configurations at n=13, capacity=4, budget=39. Cost = n + 2 times domain count. Each domain holds disjoint groups and can erase or disable all its hosted witnesses. Signing control is modeled as independent per witness. Optimize lexicographically: minimum of three resistance axes, minimum of availability/certification, sum of axes, lower cost, higher quorum. At budget 29: groups (2,2,2,2,2,1,1,1), quorum 9, resistance (8,3,5). At budget 39: (13,5,5). 

Limits: illustrative resource units, no real provider prices or actual infrastructure audit. No overlapping providers or common signing dependencies, dynamics, probabilistic failure or consensus implementation. An infrastructure compromise capable of accessing private keys would invalidate the signing independence assumption. Next WAG-144: joint control/storage placement with explicit correlated signing compromise and separate budget axes.
.dlw
