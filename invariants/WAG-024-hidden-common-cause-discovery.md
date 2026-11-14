# WAG-024 — Hidden Common-Cause Discovery

Status: instantiated and locally tested 2026-11-14.

## Invariant

Distinct declared witnesses and separately named failure domains do not guarantee independence of errors.

A suspicious pair of witnesses should trigger investigation, **not automatically prove a common cause**.

`ERROR_CORRELATION >= threshold AND joint_errors >= 2 => INVESTIGATE`

## Deterministic prototype
Local Python reference artifacts: `wag024.py` (110 lines, SHA-256 `a62d9a76417311832ad458467308be345cbfdc2bfd818f94f335ff15f75c65f6`) and `test_wag024.py` (59 lines, SHA-256 `cf056c1ff405182dd48a4d23a4bad0d0c9d0a93ca74c1aefd57e23574fe7531e`).

20/20 Python unittest tests passed.

Eight synthetic observation trials, binary error flags:
- Pair A–B: phi = +1.000, four joint errors — INVESTIGATE
- Pair A–C: phi = -0.258199, one joint error — no flag
- Pair B–C: phi = -0.258199, one joint error — no flag

The policy requires 8 independent reference-root labels before evaluation. Replayed packet IDs or reference roots fail. Audit outcomes and trial input records append to a SHA-256 hash-linked ledger. Previous observations remain intact.

## Scientific and security constraints
- Binary error flags must be obtained against independently acquired ground-reference evidence.
- An authenticated root label is not proof of independent measurement.
- Correlation can reflect task difficulty, selection bias, shared input conditions or chance rather than a hidden common cause.
- Constant error vectors have undefined phi, not evidence of zero correlation.
- This prototype does not account for statistical multiple comparisons, confidence intervals, autocorrelation or adaptive threshold selection.
- No automatic revocation is authorized by correlation alone; an independent diagnostic test must establish the failure mechanism.
- In-memory hash chaining is not a durable, independently anchored ledger.

## Next invariant — WAG-025: Causal Discrimination Under Shared Conditions
Once a correlated witness pair is flagged, design a safe controlled experiment that varies a hypothesized common dependency while preserving independent measurement references. Compare intervention and control evidence in a predeclared evaluation, then accept, reject or leave unresolved the causal explanation without rewriting historical observations.

Basic update: WAG-024 adds observational co-failure detection; 20 tests pass; specification committed, executable local artifacts not yet pushed.
