# WAG-045 — Minimal Context Difference and Independent Holdout

Status: locally instantiated 2026-11-14. 22/22 Python unittest cases passed.

## Invariant
A minimal context feature that predicts local replication success does not establish a causal explanation. Preserve the full original contexts and observations, select a candidate using discovery data only, freeze the selection, and validate it on a separate holdout.

MINIMAL_PREDICTIVE_CONTEXT != VERIFIED_CAUSE

## Synthetic reference demonstration
Frozen three-witness XOR replication pattern. Lab A: 12/12 matches; Lab B: 6/12 matches. Comparison fields: sensor_model=S100 in both, calibration=v1.0 versus v1.1, temperature=22C in both, software=r7.4 in both. The synthetic difference is calibration; this is a predictive candidate, not evidence that calibration caused the divergence.

Reference kernel enumerates bounded subsets of context features from smallest to largest and selects the first feature grouping producing two groups of sufficient size with an observed success-rate gap >= 0.4 in discovery. It freezes the feature indices and discovery packet IDs and evaluates exactly this grouping on separate holdout packets, rejecting discovery additions after freeze. Supports two context groups in its current implementation; ambiguous/multigroup cases remain unresolved.

## Local tests
22/22 Python unittest checks passed, including discovery/holdout separation, repeated registration rejection, packet/root reuse, malformed observations, bounded search, immutable evidence preservation, no causal certification, and detectable ledger modification. Synthetic 48-trial example selects calibration and returns BOUNDARY_SUPPORTED under the configured heuristic.

## HTML picture journal
Self-contained, GitHub Pages compatible HTML with embedded SVG architectural renderings of both WAG-044 and WAG-045: docs/index.html. These are vector recreations of the earlier JPG visual concepts, not the original JPG binary files. Original generated JPG files are available as conversation artifacts; no GitHub JPG upload is claimed.

## Limits
The difference-selection score is a synthetic heuristic, not a statistically calibrated post-selection test; the separate holdout mitigates but does not eliminate selection bias. Root strings do not authenticate independent observation collection. No intervention was conducted and no causal effect is established. In-memory hash chaining cannot guarantee durable or externally anchored provenance.

## Next natural invariant — WAG-046: Minimal Context Intervention
After a predictive feature passes independent holdout, design a controlled and separately budgeted intervention changing that feature while holding feasible confounders fixed. Verify whether changing calibration changes the dependent observation in independent contexts; retain failures and distinguish causal support from predictive stratification.
