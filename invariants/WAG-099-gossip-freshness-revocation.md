# WAG-099 — Pinned Gossip Freshness and Revocation-Safe Continuity

## Invariant
Historically valid signature != currently authorized certification.

Three witnesses with distinct declared source ancestors and failure-domain labels sign domain-separated observations of the exact pinned epoch, tree size, root and nonce. Duplicate receipts, forged signatures, stale heads and mismatched roots are rejected or held; a valid signed conflicting root triggers persistent quarantine. A current-epoch revocation holds certification even when the revoked witness's historical signature remains cryptographically valid.

## Executed synthetic demo
At epoch 99, W1/W2/W3 sign the same frozen head and the local gate returns LOCAL_CURRENT_AGREEMENT. Revoking W1 effective epoch 99 yields HOLD_REVOKED. Historical Ed25519 signature verification for W1 remains true. An independently exercised signed conflicting head causes QUARANTINE_CONFLICT, persisted across SQLite reopen. A signature is bound to the witness name, epoch, root, tree size, and nonce.

## Verification
37 local Python unittest cases passed with Python warnings treated as errors. Checks include revoked/current split, future-effective revocation, replay, forgery, wrong nonce and epoch, cross-head conflict, conflict durability, SQLite restart and hash-linked event tampering.

## Scope and limitations
This is a standalone synthetic-gossip gate, not integration with the WAG-098 cross-size Merkle prover or a real, trusted log signing authority. W1/W2/W3 are local test keys; independence is declared, not authenticated. SQLite WAL provides local persistence within the tested environment, not physically independent immutable anchoring. The code maintains a fixed pinned checkpoint; it does not implement signing-key rotation or automatically move to a new epoch. Host clock freshness and maximum gossip age are not enforced; 'fresh' means exact nonce and pinned epoch in this model. Fork quarantine is preserved rather than automatically cleared by later agreement.

## Files
- `invariants/wag099/wag099.py`
- `invariants/wag099/test_wag099.py`
- `invariants/wag099/WAG-099-ascii.txt`
- `docs/index.html` (ASCII journal panel)

## Next natural invariant — WAG-100
Revocation-aware successor enrollment: preserve the last certified checkpoint, require separate signed ancestry and authority approval for replacement, bind new witness signatures to a new nonce and epoch, and reconstitute a fresh three-witness quorum without rewriting historical evidence.