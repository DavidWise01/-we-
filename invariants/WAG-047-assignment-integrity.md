# WAG-047 — Assignment Integrity and Causal Evidence Lineage

Status: instantiated locally, November 14 2026. 22/22 Python unittest checks passed.

## Invariant
A statistically significant result does not establish a valid intervention assignment. The immutable test plan must precede outcome collection, and every outcome must be bound to the preregistered subject and assignment. Exposure crossover and unacceptable baseline imbalance trigger an operational HOLD.

SIGNIFICANT_DIFFERENCE != VERIFIED_CAUSAL_ASSIGNMENT

## Reference kernel
Local downloaded files: wag047.py, test_wag047.py. The kernel freezes an external assignment vector by SHA-256 commitment, requires all subjects to be enrolled before allocation, and rejects later changes and repeated identifiers. Each observation carries subject, assigned arm, received arm, outcome, logical tick, packet and root label. Decisions are appended to a hash-linked event log. A one-sided Fisher exact association test is applied only after consistency, crossover and prespecified binary baseline balance checks.

## Executed synthetic demonstration
48 subjects (24 control, 24 intervention); baseline covariate 12/24 in each group. Outcomes: 20/24 successes in control and 12/24 in intervention. Risk difference control-intervention = 0.3333333; one-sided Fisher exact p = 0.015238262362965178. Prespecified alpha=0.02. Decision ASS0CIATION_SUPPORTED_ASSIGNMENT_CHECKS_PASS (in code: ASSOCIATION_SUPPORTED_ASSIGNMENT_CHECKS_PASS). 22/22 unittest tests pass in the local working environment.

## Correctness cautions
The generated WAG-047 illustration shows p=0.0093, a decorative value that is not the executed result. The actual calculation gives p=0.01524. HTML journal and this specification use the tested figure.

The reference accepts a supplied allocation vector and a claimed generation mechanism. It does not independently verify that assignments were truly randomized, concealed, not manipulated, or independent of outcomes. Blocking a baseline gap is a heuristic screening rule, not a proof of randomization. Root identifiers are unverified labels, and a local SHA-256 chain is not durable anchored storage. Association under synthetic assumptions must not be presented as real-world causal certification.

## HTML visual journal
The repository docs/index.html contains an embedded WAG-047 SVG diagram with the tested figures; WAG-044, WAG-045, WAG-046 entries are preserved. JPG conversation artifact: WAG-047-mesh.jpg, not committed as a binary GitHub image.

## WAG-048 — Randomization Mechanism Verification
Independently attest random allocation procedure, allocation concealment and protocol fidelity; preserve random seed provenance without enabling outcome-guided cherry-picking. Prevent the post-hoc assignment repair from changing causal interpretation, and link assignment commitments to three independent witness roots.
