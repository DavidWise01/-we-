# WAG-081 — Integrated Merkle Verification and Atomic Checkpoint Advancement

Date: 2026-11-16. **34/34 local tests passed** for the full local implementation.

**Invariant:** `VERIFY_PREFIX + SIGNED_WITNESSES + SERIALIZED_COMMIT => AT_MOST_ONE_LOCAL_ADVANCEMENT`.

The locally tested kernel imports WAG-079's concrete range-frontier Merkle verifier and does not accept an external `proof_ok` boolean. It verifies a frozen tree size/root and old/new Merkle roots, three scoped Ed25519 witness signatures, distinct declared ancestry/control/failure domains, and fresh receipt IDs inside a SQLite `BEGIN IMMEDIATE` transaction. It consumes all receipt IDs, updates root/size/epoch, rotates the challenge, and appends a hash-linked event before `COMMIT`. Any simulated crash before commit rolls back all changes.

The 34 local tests cover competing proposals (exactly one wins), rewritten history, stale root/epoch/challenge, forged signatures, missing witnesses, reused receipts, restart persistence, pre-commit crash recovery, and audit tampering. The local implementation is in the conversation artifact `wag081.py`; the separately committed reference files should be run by CI before calling them verified in the repository.

**Synthetic test witnesses** do not establish authenticated real-world independence. SQLite local transaction safety is not Byzantine distributed consensus or a power-cut durability guarantee. The proof's Merkle range-frontier format is not the canonical RFC6962 consistency-proof wire format. An in-memory hash-chain and a local SQLite ledger are not external immutable anchors.

## Next: WAG-082
Power-loss recovery, independently anchored checkpoint hashes, partition reconciliation, and fork quarantine. Require external witnesses before asserting cross-machine durability.
