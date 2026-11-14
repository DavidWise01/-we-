# WAG-027 — Context Boundary Discovery and Conditional Causal Transfer

Instantiated: 2026-11-14. Local Python reference implementation: 16/16 tests passed.

## Invariant
An intervention that works in one context must not be generalized to another without independent evaluation. Discover candidate effect modifiers only on discovery data, freeze the hypothesis, and verify the same context-dependent effect on disjoint holdout evidence. Retain every exception as a first-class observation.

`CONDITIONAL_TRANSFER => FROZEN_CONTEXT_HYPOTHESIS AND INDEPENDENT_HOLDOUT AND REPLICATED_EFFECT_MODIFICATION AND PRESERVED_EXCEPTIONS`

## Reference algorithm
- Record each binary trial with immutable packet ID, claimed unique root ID, phase, environment, context features, treatment and result.
- Use discovery data to select a two-stratum context feature with a declared minimum effect difference.
- Freeze the selected feature and its original effects before any holdout evaluation.
- On holdout, require at least three observations per arm in each stratum, and two independently labeled environments per stratum.
- Compute effect = observed failure rate(control) - observed failure rate(intervention), with an ordered between-strata effect difference.
- Mark BOUNDARY_SUPPORTED when the holdout effect difference meets the 0.4 reference threshold in the preregistered direction. Otherwise HOLD or UNRESOLVED.
- Preserve original trial records and append a hash-linked evaluation; never rewrite historical evidence.

## Executed synthetic example
48 trials total across discovery and holdout. Old calibration: control 33.33% failures, treated 33.33%; effect 0. New calibration: control 100%, treated 0%; effect 1.0. Observed effect modification: 1.0. Decision: BOUNDARY_SUPPORTED under synthetic reference policy. 16/16 unittest checks passed.

## Limitations
Distinct root strings do not establish actual independent provenance. This demonstration lacks causal randomization enforcement, power analysis, uncertainty intervals, blinding, multiple-testing control and representativeness checks. A favorable holdout difference is not proof of a general causal interaction. The SHA-256-linked local ledger is not a durable authenticated database.

## Next target — WAG-028: Boundary Drift and Scope Revocation
A previously validated context boundary may move as sensors, software, or environment conditions change. Monitor prespecified sentinel contexts using fresh independent evidence; suspend operational generalization if calibration drifts, without rewriting the earlier valid conditional findings.
