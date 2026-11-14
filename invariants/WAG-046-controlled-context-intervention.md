# WAG-046 — Controlled Context Intervention and Causal Boundary Verification

Status: 2026-11-14. Local Python reference and 22 automated unittest cases executed successfully. New embedded vector illustration added to docs/index.html in this turn.

## Invariant
PREDICTIVE_CONTEXT_DIFFERENCE != CAUSAL_CONTEXT_BOUNDARY

Freeze the proposed intervention and its statistical allowance before collecting confirmatory evidence. Compare control vs intervention with prespecified outcome coding, preserve original observations, and do not grant a causal conclusion from statistical significance alone.

## Synthetic reference
Hypothesis: change calibration v1.0 to v1.1 while other declared factors remain fixed.
Control: 12/12 parity matches; intervention: 6/12 matches.
One-sided Fisher exact p=0.006864988558352402; observed risk difference (control minus intervention) = 0.5.
Policy alpha=0.02, minimum 8 observations per arm. Decision INTERVENTION_SUPPORTED in synthetic model.
Note: this is an exact association test conditional on fixed margins. Causal claims require valid randomized or otherwise identified intervention assignment, consistency, noninterference, and trustworthy witness provenance. No real device was experimentally tested.

## Local verification
22/22 passing unittest cases: preregistration, frozen plan, result direction, p-value, insufficient power hold, null effect unresolved, replay, root reuse, invalid context and binary values, provenance labels, ledger integrity and tampering.

## HTML picture on GitHub each turn
The HTML visual journal docs/index.html has WAG-044, WAG-045, and WAG-046 illustrated diagrams embedded directly as SVG, with links to invariant pages. These are browser-rendered pictures embedded in HTML, not original generated JPG binaries. Original WAG-046 JPG saved as a separate conversation artifact.

## Next invariant — WAG-047: Causal Intervention Identification and Assignment Integrity
An observed treatment difference cannot support a causal conclusion when assignment is confounded, manipulated or influenced by pre-existing outcomes. Jane needs an independently checked assignment log, temporal order, balance diagnostics, exposure fidelity, and scope-specific causal uncertainty. Preserve all exceptions and prohibit post-hoc label changes.
