# WAG-025 — Controlled Intervention and Causal Verification

Status: instantiated, 2026-11-14. Local Python implementation and 20/20 automated tests passed.

## Invariant
A WAG-024 correlated-error alert is only an observational signal. Causal support requires a frozen intervention plan, a properly controlled comparison, separately acquired reference evidence, predefined decision thresholds, independent replication and append-only evidence preservation.

`SUPPORT(H) => FROZEN_PLAN AND VALID_CONTROLLED_COMPARISON AND SEPARATE_REFERENCE_PROVENANCE AND REPLICATION AND PREDEFINED_STATISTICAL_THRESHOLD`

## Executed synthetic trial
Hypothesis: changing a shared calibration dependency reduces joint failures.
Control: 8 failures / 8 trials.
Intervention: 0 failures / 8 trials.
Risk difference: 1.0; one-sided Fisher exact p=7.77000777000777e-05.
Plan required >=4 per arm, >=2 independently labeled collection batches per arm, risk difference >=0.20, p<=0.05.
Outcome: SUPPORT under the synthetic model assumptions, not demonstrated real-world causation.

## Implementation
Local files: wag025.py and test_wag025.py.
20/20 unittest cases passed. Includes frozen plans, predeclared thresholds, exact binary observations, root-recycling check, separate reference/witness labels, replay rejection, insufficient sample and replication holds, opposite-effect contradiction, unresolved findings, append-only evaluations and hash-chain tamper detection.

## Caveats
This is a deterministic in-memory reference kernel, not a deployed experimental service. Separate root strings do not prove actual independent ancestry; trial allocation is not enforced as randomized. Interference, selection bias, confounding, temporal dependence, multiple hypothesis testing and uncertainty intervals can invalidate naive causal conclusions. A hash chain alone is not durable authenticated storage.

## Next natural invariant — WAG-026: Intervention Transportability and External Replication
An intervention supported in one context must not automatically be trusted in another. Preserve context-specific evidence, test independently across relevant domains, and explicitly separate causal effects observed in one environment from claims of generality.
