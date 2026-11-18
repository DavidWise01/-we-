# WAG-141 — Three-dimensional resistance

10 local Python tests passed in 0.004 seconds. For n witnesses and symmetric q-of-n quorum, thresholds in affected witnesses are n (erase all complete copies), n-q+1 (prevent quorum), max(0,2q-n) (minimum quorum intersection that must equivocate). Enumerate domain combinations to obtain minimum declared domain counts for each threshold and return cut witnesses. Independent one-witness domains reproduce the thresholds. A zero certification threshold means disjoint quorums can conflict with no equivocation.

Scope: structural possibility, not a consensus implementation or probability estimate. Honest signers never sign two conflicting proposals for the same slot; no other validity or locking constraints modeled. Each modeled domain can erase, disable and equivocate the same listed witnesses. Complete copies and observable survivors assumed. Hidden dependencies, distinct failure-mode maps and dynamic membership are excluded. Exhaustive search is exponential.

Next WAG-142: separate failure-mode dependency maps and Pareto analysis under explicit constraints. .dlw
