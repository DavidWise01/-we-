# WAG-080 — Irrevocable Checkpoint Advancement and Replay Prevention

## Invariant

Previously valid evidence must never authorize a second checkpoint transition. An accepted, exact three-witness Ed25519 certificate advances the frozen root and epoch once, consumes its nonce and receipt identifiers, and derives a distinct next challenge.

`VALID_HISTORICAL_CERTIFICATE != REUSABLE_CERTIFICATION_AUTHORITY`

## Local reference protocol

- Freeze `(old_root, epoch, challenge)` before collecting signatures.
- Verify exact `old_root`, `epoch`, `challenge`, and new Merkle root; require a trusted prefix-verification result (`proof_ok is True`).
- Sign a domain-separated canonical payload containing both roots, the epoch, challenge, and proof digest.
- Require exactly W1/W2/W3, each with an Ed25519 signature, distinct declared ancestry, controller and failure-domain values, and unused receipt IDs.
- After every preflight validation passes, update the checkpoint, consume the nonce and IDs, derive the next nonce from the old challenge and certificate, and append a digest-linked audit record.
- Preserve the historical certificate; reject a replay against the new root or a reused receipt ID against the next epoch.

## Demonstration and tests

Local suite: **50/50 passed**. `demo()` returns `ADVANCED_LOCAL` followed by `OLD_ROOT_MISMATCH` on replay, with epoch 1, one certificate and two validated hash-linked records.

Tests include challenge rotation, historical retention, stale/future epoch, changed old root, bad proof, missing witness, duplicate/reused receipts, tampered signatures, cross-target signatures, second valid checkpoint, duplicate roots/controllers/domains, invalid genesis and audit tampering.

## Boundaries

Witness keys and declared provenance are synthetic. `proof_ok` is a trusted input, not cryptographically verified by this kernel; an independent verifier must validate Merkle proof data against old/new roots before passing True. The state machine is single-writer and in-memory, not crash-durable or consensus replicated. The next step must address atomic proof verification, durable compare-and-swap, and recovery from crashes.

## Next natural invariant — WAG-081

**Atomic Proof Verification and Checkpoint Commit.** Remove the externally supplied boolean; bind the actual WAG-079 proof to the signed transition, preserve source ancestry and precommit evidence, and test concurrent advances and crash replay.