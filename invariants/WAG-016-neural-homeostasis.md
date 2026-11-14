# WAG-016 — Neural Homeostasis and Global Stability Conservation

Status: instantiated reference boundary (2026-11-13).

## Invariant
A proposed generation may be promoted only when its independently evaluated whole-network metrics satisfy both protected-capability and global resource constraints.

PROMOTE(G[n+1]) => independent_holdout AND protected_capabilities AND meaningful_gain AND energy_budget AND p95_latency_budget AND fanout_budget AND global_strength_budget AND bounded_synaptic_steps.

## Observation / evidence separation
- Original evidence records are immutable.
- Witness-root IDs must be traced to actual independent origins; identifier uniqueness is not proof.
- Development evidence must not leak into holdout evaluation.
- Inherited copies cannot add independent root counts.
- Every promotion/hold result is an append-only decision tied to the baseline and candidate generations.

## Synthetic gate reference
Baseline G15: memory loss 0.10, timing loss 0.18, reasoning loss 0.12.
Candidate G16: memory loss 0.11, timing loss 0.09, reasoning loss 0.12.
Candidate energy 8.2 <= 9.0, p95 latency 11.8 <= 12.0 ms, fanout 3 <= 4, total strength 1.00 <= 1.10.
Memory regression +0.01 <= 0.02; timing improvement 0.09 >= 0.03.
Decision: PROMOTE_ELIGIBLE under synthetic assumptions, not production certification.

## Test coverage
Local reference Python implementation: 14 automated tests passed. Checks include gain, memory regression, total strength, energy, latency, fanout, per-edge step bounds, recycled roots, development leakage, invalid inputs, and hash-chain tamper detection.

## Next invariant: WAG-017 — Oscillation Resistance
A mesh must not repeatedly flip between competing routes due to noisy measurements. Apply hysteresis, minimum dwell time, and independent revalidation before state transitions.

## Limits
A hash-linked in-memory audit is not durable tamper-proof storage. Claimed independent roots require source authentication. Benchmark data and budgets above are illustrative.
