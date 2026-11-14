# WAG-026 — Intervention Transportability

Status: instantiated deterministic reference, November 14, 2026. Local tests: 20/20 passing.

## Invariant
A causal intervention supported in one context does not automatically apply elsewhere. Transport eligibility requires independent new-context trials, context-specific treatment effects exceeding a declared minimum, and limited observed effect heterogeneity. Historical evidence remains append-only.

`TRANSFER(H) => INDEPENDENT_REPLICATION AND CONTEXT_SPECIFIC_SUPPORT AND EFFECT_STABILITY AND FROZEN_REFERENCE`

## Reference model
The frozen source-context result is a reference, not counted as new independent replication. Each new context requires >=4 observations per arm and >=2 distinct collection-batch labels per arm, with >=2 eligible new contexts. Effect is failure rate(control) minus failure rate(intervention). The minimum effect is 0.20 and the maximum cross-context effect spread is 0.30. Reference effect must be >=0.20.

Synthetic example: Lab B 8/8 control failures versus 0/8 intervention failures, Lab C same: both effects 1.0, spread 0.0, decision `TRANSPORT_ELIGIBLE`.

## Security and statistical limitations
Witness root strings and batch labels are not authenticated provenance. This implementation does not establish random assignment, confidence intervals, external validity, independence of trials, or control for multiple comparisons. Its decision means passing a synthetic configurable policy, not real-world causal proof. A local SHA-256 chain can detect edits to records but is not durable tamper-resistant storage.

## Next invariant — WAG-027: Context Boundary Discovery
When transport fails in one context, find the smallest measured context difference explaining the failure. Do not infer causation solely from subgroup correlations; predeclare hypotheses, run independent interaction tests, and preserve all exceptions rather than averaging them away.
