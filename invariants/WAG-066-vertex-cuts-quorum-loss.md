# WAG-066 — Vertex Cuts, Quorum Loss, and Declared Failure-Domain Separation

Date: 2026-11-15.

## Invariant
CONNECTED_SURVIVORS != VALID_THREE_WITNESS_QUORUM.

For the complete triangle K3, vertex connectivity κ(K3)=2 (convention for complete graphs), and edge connectivity λ(K3)=2. Removing one vertex leaves a connected K2, but Jane's strict three-witness certification rule fails because only two remain.

## Reference decisions
- Three live connected witnesses with three distinct declared ancestors, operators and failure domains: ELIGIBLE_FOR_FRESH_ATTESTATION.
- Any missing witness: HOLD_QUORUM_LOSS, even when surviving nodes remain mutually reachable.
- After restoration of the failed witness, require a new scoped receipt from each of W1, W2, W3. Existing receipts are not automatically inherited.
- Three distinct declared receipts: LOCAL_DECLARED_QUORUM_ACCEPTED, not real-world authentication.

## Synthetic executed result
Initial K3: three connected, eligible. Fail W1: W2 and W3 connected; certification HOLD_QUORUM_LOSS. Restore W1: three connected and eligible for fresh attestation. Submit distinct new receipts fresh-a/fresh-b/fresh-c: local declared quorum accepted. Four SHA-256 linked event records verified; vertex connectivity computed as 2.
Full local Python reference suite: 26/26 tests passed. Tests include single/double/all vertex failures, ancestor/operator/domain collisions, replayed attestations, restored witness, invalid transitions, tampering and atomic rejection.

## Files
- invariants/wag066/WAG-066-ascii.txt — GitHub ASCII visual, text-based.
- docs/index.html — ASCII diagram embedded as a <pre> panel, preserving earlier journal entries.
- invariants/wag066/wag066.py — GitHub reference kernel.
- invariants/wag066/test_wag066.py — 26-case GitHub reference tests.
- Conversation artifacts include the local Python source, tests and TXT artwork.

## Limits
These failures concern an abstract graph and self-declared provenance, not actual Byzantine consensus or source-authenticated independent quorum. Graph κ(K3)=2 does not mean K3 tolerates two Byzantine processes. A connected survivor pair cannot form Jane's chosen quorum of three, and four or more replicas may be required for Byzantine tolerance under standard assumptions. The hash chain is single-writer and memory-resident, not externally anchored durable storage. The locally tested and GitHub-reference files were created separately; verify executable parity before treating repository tests as CI-validated.

## Next — WAG-067: Common-Cause Failure Domains and Cut Sets
A network may have three nominally separate witnesses yet still lose them simultaneously to one infrastructure failure. Model source ancestry, shared operators, networks and failure domains as a dependency hypergraph. Compute minimal failure-domain hitting sets, preserve counterexamples and require independent attestation before upgrading a declared diversity claim.
