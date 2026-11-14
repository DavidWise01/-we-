# WAG-029 — Sequential Evidence-Window Confirmation

Status: instantiated 2026-11-14. Local Python reference kernel + 20/20 automated tests passed.

## Natural invariant

`SINGLE_ANOMALY != CONFIRMED_DRIFT`

Operational scope suspension requires at least two consecutive, nonoverlapping, independently labeled windows whose means violate a predeclared baseline threshold in the **same direction**. A normal window or a change in drift direction resets the pending sequence. Recertification requires two consecutive normal windows in explicit recovery mode and creates a new scope version. Neither suspension nor restoration rewrites earlier observations.

## Deterministic policy

Each window records (scope, packet ID, root ID, first tick, last tick, observations, monitoring/recovery mode). Require at least 3 finite numeric observations per window, strictly increasing nonoverlapping ticks within scope, globally non-replayed packet and root identifiers, and a valid scope. Compute window mean; deviations above +threshold and below -threshold are distinct drift directions.

Decisions: CURRENT, PENDING_DRIFT, CONFIRMED_DRIFT_SUSPEND, PENDING_RECOVERY, RECOVERY_FAILED, RECERTIFIED. Scope states: CURRENT/SUSPENDED.

## Synthetic demonstration

Old calibration baseline 0.30, tolerance 0.20:
- Window 1 mean 0.80: PENDING_DRIFT
- Window 2 (separate scope) mean 0.12: CURRENT
- Window 3 old calibration mean 0.80: CONFIRMED_DRIFT_SUSPEND
- Recovery 1 old calibration mean 0.35: PENDING_RECOVERY
- Recovery 2 old calibration mean 0.33: RECERTIFIED, version 1

Ten append-only records (five windows + five decisions) have a verified hash chain in local test.

## Tested

20 unittest checks passed: ordinary stability, single anomaly hold, consecutive confirmation, resets on normal and opposite-direction observations, scope isolation, two-window recovery, failed recovery, invalid phase transitions, replay and root reuse, overlapping ticks, insufficient samples, nonfinite observations, unknown scope, invalid mode, immutable baseline, hash-chain tampering, end-to-end demonstration.

## Limits

This is a fixed-threshold, uncalibrated reference algorithm. Labels do not cryptographically establish independent witness provenance. A sample mean and consecutive-window heuristic lack controlled false-alarm rates, serial-dependence corrections, uncertainty intervals, and change-point power analysis. It uses in-memory hash linking, not durable transactional or anchored evidence storage. Urgent safety overrides should be a separate explicit mechanism.

## Next natural invariant — WAG-030: Sequential Error Budget Conservation

Repeatedly watching the same process increases the risk of false alerts. The next detector must allocate a precommitted false-alarm budget over indefinite monitoring, control optional stopping and dependence, and distinguish provisional anomalies from statistically supported change points while retaining immutable window lineage.
