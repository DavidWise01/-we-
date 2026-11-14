# WAG-028 — Temporal Boundary Drift and Conditional Trust Recovery

Status: instantiated reference kernel on 2026-11-14. 20/20 local Python tests passed.

## Invariant
Historical validity and operational applicability are separate. A measured drift outside a frozen scope-specific boundary suspends current reliance only in that scope. Historical records remain unchanged. Independent revalidation creates a new scope version.

`CURRENT_TRUST(B,t) => HISTORICAL_VALIDITY(B) AND FRESH_EVIDENCE(B,t) AND WITHIN_BOUNDARY(B,t)`

## Reference implementation
Python local artifacts: `wag028.py`, `test_wag028.py`.
- Maintain immutable frozen baseline values for each context.
- Track a state (CURRENT/SUSPENDED), revision number and monotonic logical tick per scope.
- Every monitoring or recovery window carries a packet ID, a numeric observation and at least three distinct declared witness roots.
- Reject reused packet IDs and root identifiers, unknown scopes, stale ticks, malformed values or insufficient roots.
- Append original observation before the evaluation decision.
- Monitoring outside absolute distance threshold suspends only that scope.
- Monitoring alone cannot restore a suspended scope. A separately labeled recovery observation with new claimed roots and within-threshold value creates a new version and restores operational state.
- A hash-linked append-only event chain makes local record mutation detectable.

## Deterministic demonstration
Frozen baselines: old_calibration=0.30; new_calibration=0.10; allowable deviation=0.20.
1. old_calibration at tick 1 observes 0.80 => SUSPEND_SCOPE.
2. new_calibration at tick 2 observes 0.12 => MONITOR_OK, unaffected.
3. old_calibration at tick 3 independently reports 0.35 in a recovery window => RECERTIFY_SCOPE; version advances to 1.
Ledger validates; baseline remains 0.30; all original observations preserved.

## Validation
20/20 unit tests passed locally, including scoped suspension, unrelated-scope isolation, preserved baseline/history, recovery versus ordinary monitoring, retained hold on persistent drift, versioning, packet replay, witness root reuse, stale ticks, invalid measurements and ledger mutation detection.

## Limits
A three-root window is a synthetic policy demonstration: the identifiers are declared labels, not cryptographically verified independent roots. A single sample and absolute threshold do not constitute statistically reliable change-point detection. Recovery needs suitable sampling, uncertainty estimates, causal checks and actual independent provenance in a deployed system. The memory-resident hash chain lacks durable external anchoring.

## WAG-029 — Evidence-Window Reliability and Change-Point Confirmation
Replace single-sample drift decisions with sequential independently observed windows, explicit uncertainty and precommitted error-rate thresholds. Separate abrupt change, gradual trend and noisy fluctuations. Require independent confirmation before routine scope suspension or recertification, with emergency safety overrides kept separate.
