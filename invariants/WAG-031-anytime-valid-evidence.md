# WAG-031 — Anytime-Valid Evidence and Cross-Generation Error Conservation

Status: implemented and locally tested, November 14, 2026. Python reference: wag031.py; test_wag031.py. 24/24 tests passed.

## Invariant
An agent can monitor sequential observations at arbitrary stopping times without resetting its evidential accounting after a generation transition. A new generation inherits the existing e-process value, null, threshold and alarm state.

For observations X_t in [0,1], suppose under H0: E[X_t | F_(t-1)] <= mu0, where mu0 = 0.5. For a predeclared constant lambda in [0, 1/mu0], define:
E_0 = 1; E_t = E_(t-1) * (1 + lambda*(X_t - mu0)).
Because each factor is nonnegative with conditional expectation <= 1 under H0, E_t is a nonnegative test supermartingale. By Ville's inequality,
P_H0(sup_t E_t >= 1/alpha) <= alpha.
Default alpha = 0.05, lambda = 1; threshold = 20.

## Synthetic demonstration
Eight X=1 observations yield e-values
1.5, 2.25, 3.375, 5.0625, 7.59375, 11.390625, 17.0859375, 25.62890625.
Generation 1 inherits after tick 3, preserving e=3.375. Alarm fires at tick 8. No reset on inheritance.

## Reference tests
24/24 local unittest cases passed: null-factor expectation, threshold, cumulative updates, inheritance without reset, latched alarms, packet replay, strict tick ordering, 3 distinct declared witness labels per packet, bounded/finite observation validation, invalid policy, zero-lambda case, hash chain verification, tamper detection and demonstration.

## Limitations
The conditional-mean null is a substantive assumption that must be validated for the specific monitored process. A predictable lambda chosen from past data is also valid within nonnegativity constraints, but an arbitrary hindsight-chosen multiplier is not. Distinct root labels are not independent provenance authentication. A hash-linked in-memory ledger lacks independent durable anchoring. Multiple separately launched monitoring families require a shared false-alarm budget; spawning generations does not create fresh alpha.

## Next natural invariant — WAG-032: Across-Agent E-Process Budgeting
When agents launch separate tests, Jane must prevent multiplication of false-alarm opportunities. Precommit a shared familywise budget or use a valid e-value combining rule with explicit assumptions. Enforce cross-agent lineage conservation, immutable test registration, and no budget reset through cloned agents.
