# WAG-067 — Common-Cause Failure Domains and Cut Sets

Status: instantiated 2026-11-15. 28/28 local Python unittest tests passed.

## Invariant

Three unique witness names and three unique declared evidence roots do not imply independent failure domains.

`INDEPENDENT_SOURCE_ROOTS != INDEPENDENT_INFRASTRUCTURE`

## Dependency graph

W1 (ancestor A) depends on host-a and network-x.
W2 (ancestor B) depends on host-b and network-x.
W3 (ancestor C) depends on host-c and network-x.

Failing network-x disables every witness. In this model, two inclusion-minimal all-three failure sets are {network-x} and {host-a,host-b,host-c}. The minimum-cardinality all-three cut is size one.

## Algorithm and demonstration

The reference enumerates combinations of named domains, maps each domain to dependent witnesses and excludes supersets of previously found minimal sets. The strict quorum policy requires all three witnesses. A domain failure is appended, and repair does not itself recertify the quorum: all three must furnish distinct new receipt identifiers.

Local demo: ELIGIBLE_DECLARED_QUORUM -> FAIL(network-x) -> HOLD_COMMON_CAUSE (0/3 survivors) -> REPAIR -> fresh receipts (W1/W2/W3) -> LOCAL_DECLARED_QUORUM. Four SHA-256-linked events verify.

## Validation

28/28 Python unittest cases passed. Scenarios cover shared and separate infrastructure, inclusion-minimal cuts, single and three-domain all-witness failures, explicit outage and repair, attestation checks, replay rejection, identity validation, bad inputs, mutation detection, and atomic failure. Tested locally; the GitHub version should not be called independently CI-tested until run there.

## Artifacts

- docs/index.html: new inline ASCII preformatted journal illustration.
- invariants/wag067/WAG-067-ascii.txt: ASCII drawing.
- invariants/wag067/wag067.py: Python reference kernel.
- invariants/wag067/test_wag067.py: regression suite.

## Limits

Source roots and dependencies are self-declared labels, not authenticated independent identities or observed live infrastructure. Domain failures are deterministic, not probabilistic. Exhaustively enumerating subsets has exponential worst-case cost; large systems require bounded search. The hash-linked in-memory ledger is not durable external evidence. This is not a Byzantine agreement protocol.

## Next — WAG-068: Dependency Hypergraph and Correlated Failure Propagation

Represent overlapping shared dependencies as hyperedges, track cascades and dependency ancestors, and bound minimal common-cause cut sets without double-counting correlated failures. Require externally verified domain claims before certifying fault tolerance.
