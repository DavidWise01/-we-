# WAG-100 — Witness Succession, Revocation Lineage, and Quorum Restoration

## Invariant

A compromised witness's historical evidence stays verifiable even when its key is no longer authorized for current checkpoints. A successor's new key alone does not establish independent control. Rotation requires **two current surviving reviewers** to approve the exact same signed proposal, distinct declared ancestry, control, key, and failure domain, and three fresh matching signatures after the epoch changes.

`HISTORICAL_SIGNATURE_VALID != CURRENT_CERTIFICATION_AUTHORITY`

## Tested reference

SQLite-backed transaction with an append-only hash-linked event chain. The state advances atomically from epoch 99 (`W1,W2,W3`, `root-99`) to epoch 100 (`W2,W3,W4`, `root-100`). Both surviving reviewers sign the proposal bound to the old epoch, old root, next root, and challenge. Reused keys, ancestor/controller/domain collisions, forged approvals, and missing votes are rejected. Following rotation, the three new active signers attest to the same new epoch/root/challenge and consumed receipt IDs are persisted so their replay is rejected after a restart.

The demonstration yields four event records: genesis, revocation, rotation, certification. Historical revocation evidence for W1 remains stored. A rollback or invalid signature cannot partially advance a checkpoint.

## Validation

40/40 local Python unittest cases passed. Tests cover revocation, signature checking, duplicate identities, shared controls, fresh quorum, replay, atomic rollback, restart state, and tamper detection.

## Security scope and limitations

This prototype uses locally generated Ed25519 keys and **declared** source/control ancestry. It does not authenticate real-world controller relationships, prove reviewer independence, incorporate a public revocation registry, implement Byzantine distributed consensus, or solve compromised-surviving-reviewer collusion. SQLite is transactional local persistence; hash-linked history is not externally anchored immutability. The test state is a synthetic model.

## Files

- `invariants/wag100/wag100.py` — full local prototype.
- `invariants/wag100/test_wag100.py` — 40-case unit test suite.
- `invariants/wag100/WAG-100-ascii.txt` — ASCII-only visualization.
- `docs/index.html` — append-only illustrated journal.

## Next natural invariant — WAG-101

**Reviewer-Collusion Resilience and External Succession Witnessing.** Preserve the 3-vertex ring and require evidence of an authorization from an independent external control ancestry when both surviving reviewers could share hidden control. Detect forged or conflicting succession statements and keep rotation on HOLD when independence is unknown.