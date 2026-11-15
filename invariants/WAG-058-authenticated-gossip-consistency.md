# WAG-058 — Authenticated Gossip and Compact Public Consistency Proofs

Status: locally instantiated 2026-11-15. Full local Python verifier: 24/24 unittest cases passed; all 741 positive tree-size pairs with 1 <= m < n <= 39 were checked. A shorter executable GitHub reference implementation and 24-case suite are committed; GitHub copy was not independently executed here.

## Invariant
TRUSTED_LOG_HISTORY => AUTHENTICATED_LOG_OPERATOR AND VALID_SIGNED_HEADS AND AUTHENTICATED_WITNESS_GOSSIP AND VALID_APPEND_ONLY_CONSISTENCY.

A witness signature on a tree head does not establish that the witnessed history is consistent with earlier tree heads. Different signed roots at identical sizes for the same authenticated log indicate a cryptographic conflict and trigger quarantine. Missing compact consistency proof triggers HOLD, not a misconduct finding.

## Reference algorithm
1. Bind the log's stable identity to a configured Ed25519 public key.
2. Verify Ed25519 signed tree heads over log ID, Merkle root, tree size and logical epoch.
3. Register at least three witness identities with distinct declared roots and failure domains. Verify each witness's signed gossip message binds its name, the received signed-head digest and gossip epoch.
4. Verify RFC6962-style compact consistency paths over domain-separated SHA-256 leaves (0x00 prefix) and internal nodes (0x01 prefix). For small and large tree sizes, recompute both roots using the consistency path without receiving the entire leaf history.
5. Pairwise compare all reports. Same-size incompatible signed roots => QUARANTINE_CONFLICT. Submitted invalid proof for actually received earlier/later signed roots => QUARANTINE_CONFLICT. Absent proof, insufficient reports or incomplete witness quorum => HOLD_INCOMPLETE. Otherwise CONSISTENT_RECEIVED_VIEWS (not verified public-log governance).
6. Append all inputs, proofs and decisions to a hash-linked evidence ledger.

## Synthetic executed local fixture
- One locally generated Ed25519 log-operator key.
- Three locally generated independent *labeled* witness keys.
- W1 observes a signed tree of size 3; W2 and W3 observe a signed tree of size 6.
- A compact consistency proof verifies H3 is an append-only prefix of H6.
- Decision: CONSISTENT_RECEIVED_VIEWS. Nine in-memory events and hash chain verified.
- 24 local unittest cases passed, covering all short/long size pairs up to 39 leaves, signature failures, same-size equivocation, proof failure, missing proofs, source-label overlap, replay, bad epoch and history tampering.
- As a separate negative test, conflicting heads at equal size trigger QUARANTINE_CONFLICT.

## Artifacts
- docs/index.html — updated this turn with an original self-contained SVG illustration of WAG-058, preserving WAG-044 through WAG-057.
- invariants/wag058/wag058.py — executable Python reference committed to GitHub.
- invariants/wag058/test_wag058.py — 24-case GitHub reference test suite.
- Generated JPEG WAG-058-mesh.jpg available in the conversation, not committed as a GitHub binary; HTML has its own embedded SVG.

## Limits and required caution
The Ed25519 checks and compact Merkle verifier are real executable primitives, but the fixture's keys, log, epochs, witness identities and gossip are all local simulations. Distinct witness names and domains are not authenticated real-world independence. There is no independent public transparency operator, external timestamp service, live gossip network, witnessed signed tree-head registry, or durable externally anchored log. A valid proof only establishes consistency between the observed signed roots; it does not prove availability, completeness of gossip, or freedom from all split-view attacks. The illustrative image contains numerous invented measurements and statistics; none should be treated as evidence.

## Next natural invariant — WAG-059: Gossip Freshness, Completeness and Network Partition Resilience
A consistent set of received views may still be stale or selectively delivered. Authenticate gossip timing and expected peer coverage, classify unreachable or delayed witnesses as incomplete rather than independent agreement, detect partition-specific divergence upon reconnection, and preserve all earlier signed heads before resuming operational trust.
