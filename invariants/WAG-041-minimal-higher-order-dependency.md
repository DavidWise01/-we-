# WAG-041 — Minimal Higher-Order Dependency and Counterexample Preservation

Status: instantiated and locally tested on 2026-11-14. 22/22 Python unittest tests passed.

## Invariant
Preserve the original failing witness cohort and its observations. Search bounded smaller subsets, freeze the first discovered candidate, and validate it on a disjoint holdout before labeling a dependency pattern replicated. Never silently remove witnesses from the original checkpoint history.

DETECTED_DEPENDENCY => PRESERVE_ORIGINAL AND BOUNDED_MINIMIZATION AND INDEPENDENT_HOLDOUT AND APPEND_ONLY_AUDIT

## Reference algorithm
For each subset of size 3..max_order in deterministic combination order, calculate empirical total-variation distance between the joint binary-error distribution and product of its marginal distributions on discovery data. Stop at first score above predeclared threshold, then evaluate exactly that subset on separate holdout data. Respect maximum tested-subsets budget. Return UNRESOLVED or HOLD if data are insufficient, search budget exhausted, or the pattern does not replicate. Never treat a non-detection as proof of independence.

## Synthetic demonstration
W1=A, W2=B, W3=C=A XOR B; W4=D is an independent balanced bit.
32 discovery and 32 holdout observations, eight equally represented 4-bit patterns in each phase.
Selected minimal detected subset A,B,C.
Empirical joint TV = 0.5 for both phases; all pairs are independent in the complete factorial pattern.
Decision REPLICATED_PATTERN; 66 hash-linked records verify.

## Local artifacts
- wag041.py SHA256 fc783981371f603b026e0603bf8db224d8f68df94f1baf59e603aac4aa83aa8b
- test_wag041.py SHA256 a69c45c271cf21a1299262b10a3313cae2d6a16d627eab6b7817986b6ac999d5
- 22/22 unit tests passed, including replay, malformed input, bound enforcement, subset selection, historical preservation, pairwise XOR example and chain tampering.

## Limitations
The fixed empirical TV threshold is a synthetic heuristic, not a statistically calibrated selective-inference procedure. Disjoint packet/root identifiers do not authenticate independence of real-world data acquisition. A fixed holdout may still be compromised by leakage or shared collection dependencies. Searching many subsets requires explicit multiplicity or valid post-selection control to support calibrated error guarantees. Minimal means smallest detected subset under the chosen bounded search and threshold, not globally unique minimal causal explanation. In-memory hash links are not independently anchored durable storage.

## WAG-042 — Dependency Search Error-Budget Conservation
Every subgroup search creates additional false discovery opportunities. Register discovery and confirmatory budgets with WAG-032/WAG-034 before looking at holdouts; prevent agents from resetting the family budget by repartitioning witness groups. Independent holdout validation must retain full discovery lineage and test registration.
