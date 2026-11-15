# WAG-064 — Singular Witness Routing, Path Conservation and Post-Surgery Quorum

Status: 2026-11-15. Local Python prototype passed 24/24 unittest checks. GitHub code and 24-case test source have been committed; the uploaded GitHub copies were not independently executed.

## Invariant
WITNESS_IDENTITY_PRESERVED does not imply WITNESS_CONNECTIVITY_PRESERVED.

After a topology-changing singularity, the current witness graph cannot be recertified solely because all three witness names and ancestry labels survived. Preserve the frozen original edges, explicitly register which graph links were cut, restore the same graph, and require fresh consistent attestations from all three separate declared ancestry roots before recertifying.

## State machine
PRE_PINCH -> SINGULAR [HOLD] -> RECONSTRUCTED [HOLD_FRESH_QUORUM] -> RECERTIFIED_DECLARED_WITNESSES.

The ring uses vertices W1 W2 W3 with edges W1-W2, W2-W3, W3-W1 (3 undirected edges). In the executed singular reference, W1-W2 and W1-W3 are removed, so one W2-W3 edge remains and W1 is disconnected. Repair restores the two cut edges; three fresh packets attest to the complete restored edge set. The reference returns RECERTIFIED_DECLARED_WITNESSES, with 7 hash-linked in-memory audit records.

## Test results
24/24 local tests passed. Cases include distinct roots/domains, preserved original edges, singular holds, disconnection, duplicate and invalid cuts, partial repair rejection, missing quorum hold, packet reuse rejection, conflicting witness observations, exact three-witness recertification, replay, and ledger tamper detection.

## Scientific and security limits
This is a three-node graph-routing model, not a physical or numerical simulation of gravity, void, a continuous torus-to-sphere transition, or a production Byzantine consensus system. The surface topology surgery from WAG-063 is represented by a routing interruption, not mechanically derived from a 3D embedding. Source identities, claimed ancestry and attestation packets are neither cryptographically authenticated nor independently verified. SHA-256 in-memory chaining is not durable tamper-proof storage. Three declared witnesses do not guarantee tolerance of a Byzantine faulty participant.

## Images and web
docs/index.html has a self-contained WAG-064 SVG visual. The original generated JPG is available as a separate conversation artifact and is not claimed as a GitHub-hosted JPG binary. The JPG artwork depicts total edge loss E=0 at the pinch, whereas the executed kernel removes two edges and retains E=1; code and this specification are authoritative for test results.

## Next invariant — WAG-065: Edge-Independent Routes and Fault-Cut Capacity
Measure the minimum edge cut of the reconstructed witness cycle and determine how many routes survive one dishonest or unavailable witness. Distinguish basic graph connectivity, multi-path redundancy and Byzantine fault tolerance; preserve identity/ancestry and do not infer one-fault BFT from a triangle.
