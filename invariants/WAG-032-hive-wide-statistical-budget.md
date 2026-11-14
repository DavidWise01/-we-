# WAG-032 — Hive-Wide Statistical Budget and Agent-Lineage Conservation

Status: instantiated 2026-11-14. Local Python module wag032.py and test_wag032.py: 22/22 unittest cases passed.

## Invariant
Every registered hypothesis test receives a non-recyclable slice of a shared hive familywise error budget. Agent spawning and generation inheritance do not create new budget, alter the underlying null hypothesis, or restart an existing e-process.

FAMILY_ALPHA >= SUM(registered_test_alpha)
AND child(test).e = parent(test).e
AND child(test).allocation = parent(test).allocation

## Concrete allocation
For the i-th distinct test registered by the hive (i=1,2,...), use alpha_i=alpha_family/2^i. The total across infinitely many tests is alpha_family, so allocating more tests cannot exceed the family budget. This is conservative; it is not an optimization of testing power.

A test uses the WAG-031 nonnegative supermartingale e-process: E_t=E_(t-1)*(1+lambda*(X_t-mu0)), default mu0=.5, lambda=1, and [0,1] observations. The test alarms at E_t>=1/alpha_i. The resulting familywise bound relies on per-test anytime validity and union bound, without requiring between-test independence.

## Synthetic demonstration
Total alpha=.05.
Test A, owned by scout-a, allocation .025.
Test B, owned by Jane, allocation .0125.
After 12 observations X=1 in Test A (its descendant continues after tick 3), E_A=129.746337890625, above Test A threshold 40.
Allocated .0375; remaining .0125; 17 hash-linked records; ledger verifies.

## Verified
22/22 local automated tests passed. Cases include allocation total, fixed spending, inherited e-state and agent parentage, unauthorized test updates, duplicated agent/test identifiers, packet replay, root recycling, stale ticks, invalid observations, alarm latch, atomic rejection and ledger mutation detection.

## Limitations
A string root ID is not independently authenticated provenance. E-process validity depends on a correct conditional-mean null; the reference does not generate or empirically validate those measurements. The in-memory hash chain is not durable append-only storage. Summing allocations via floating point entails small rounding; enforce exact rationals/decimals for production. This repository specification does not claim deployment.

## Next — WAG-033: Adaptive Test Allocation Under Shared Budget
Permit Jane to adaptively allocate remaining family budget to promising experiments using only information available *before* those tests are opened. Preserve irrevocable registrations and source lineage. Never retroactively increase alpha after viewing a test's evidence, and never recycle allocation by renaming an agent or hypothesis.
