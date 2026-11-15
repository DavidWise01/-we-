# WAG-069 — Topological Repair Ordering, Recovery Dependencies, Fresh Quorum Validation

2026-11-15. Local deterministic Python reference: **36/36 unit tests passed**.

## Invariant
`INFRA_REPAIRED != INFRA_VERIFIED != WITNESS_REATTESTED`.

The dependency DAG is power-y -> network-x -> (router-a, router-b), with independent power-z -> router-c. Failing power-y cascades to 4 nodes, disables W1 and W2, and leaves W3 available. Jane holds certification until power-y is repaired and verified, followed by network-x, then both routers. Repair cannot proceed before verifying upstream dependencies. After infrastructure restoration, W1, W2, and W3 must supply three new distinct receipts. A working network alone never certifies.

## Local demo
FAIL(power-y) -> HOLD_UPSTREAM_OR_NODE_FAILURE (1/3 available) -> REPAIR/VERIFY power-y -> REPAIR/VERIFY network-x -> REPAIR/VERIFY router-a -> REPAIR/VERIFY router-b -> HOLD_FRESH_ATTESTATIONS -> attest W1/W2/W3 -> LOCAL_DECLARED_QUORUM_ACCEPTED.
13 hash-linked memory-resident events: genesis 1, failure 1, repair 4, verification 4, attestation 3. All 13 verified; 36 unit tests passed locally.

## Scope and limitations
Node dependencies and unique witness ancestors are self-declared labels, not authenticated source ancestry or observed infrastructure; verification receipts are synthetic strings. This is not Byzantine consensus or an actual operational repair system. In-memory hash chaining does not establish immutable external provenance. The uploaded GitHub reference is not separately CI-tested.

## Deliverables
- docs/index.html: embedded ASCII experiment visual
- invariants/wag069/WAG-069-ascii.txt: text diagram
- invariants/wag069/wag069.py: reference executable kernel
- invariants/wag069/test_wag069.py: regression tests

## Next WAG-070
Bind every verification and attestation to the exact recovery epoch and upstream dependency snapshot. Invalidate all stale receipts after any subsequent failure and reject cross-epoch replay.
