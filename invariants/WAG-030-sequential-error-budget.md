# WAG-030 — Sequential Error Budget Conservation

Status: instantiated November 14, 2026. Local Python reference: 24/24 tests passing.

## Invariant
Repeatedly inspecting a process must not accumulate unbudgeted false-positive probability.

`SUM(alpha_t, t>=1) <= alpha_total`

## Precommitted schedule
For look t>=1 and alpha_total=0.05:
alpha_t = alpha_total / [t(t+1)].
Its telescoping sum is alpha_total. Cumulative spend through T is alpha_total * T/(T+1), strictly less than alpha_total.

If each per-look p-value is valid under its own null and actual sampling procedure, the union bound controls familywise probability of any false alarm at alpha_total, regardless of dependence *between* the valid per-look tests. This does not excuse optional stopping *within* a test, invalid p-values, or calibration/model violations.

## Synthetic demonstration
Look 1: p=0.20, threshold=0.025, CONTINUE
Look 2: p=0.012, threshold=0.0083333, CONTINUE
Look 3: p=0.003, threshold=0.0041667, ALARM
Look 4: p=0.40, threshold=0.0025, ALREADY_FLAGGED
Cumulative allocated error budget after look 4: 0.04, budget remains 0.01.

## Executable local reference
The Python module `wag030.py` provides Policy, SequentialAuditor and demonstration. Audit records are append-only and SHA-256 linked. 24/24 unittest cases pass in `test_wag030.py`: telescoping error budget, thresholds, alarm latch, record replay, root reuse, tick monotonicity, invalid p-values, atomic rejection and ledger tampering.

## Limits
This is a synthetic single-writer reference implementation. Root labels are not cryptographically authenticated; the 3-root count does not prove true independence. Neither p-value generation nor statistical validity of underlying tests is implemented. A hash-linked memory ledger is not durable authenticated storage. A conservative alpha-spending scheme can have low statistical power at late monitoring looks.

## Next invariant — WAG-031: Evidence-Efficient Sequential Testing
Replace increasingly small fixed-look thresholds with a predeclared anytime-valid e-process or test martingale, under explicit null assumptions, to improve monitoring efficiency while preserving optional-stopping error control. Track evidence accumulation without allowing agents to reset budgets by spawning generations.
