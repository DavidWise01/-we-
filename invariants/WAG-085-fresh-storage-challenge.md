# WAG-085 — Fresh Challenge-Response Storage Verification
## Invariant
A historical delivery receipt cannot establish current storage. A recovery challenge binds epoch, checkpoint SHA-256 hash and nonce. All three hosts must read their checkpoint files, sign domain-separated receipt messages, and furnish distinct, matching signed responses. The verifier atomically consumes the receipts and persists the challenge state. Old proofs must not be reusable after process restart.

`OLD_DELIVERY_RECEIPT != CURRENT_STORAGE_PROOF`

## Synthetic experiment
Three local host directories, three Ed25519 keys, and three declared independent domains simulate the protocol. The host writes, fsyncs, and reopens its file; the returned signature binds a hash of the bytes to the challenge and host identity. SQLite tracks consumed receipts and creates a hash-linked audit trail.

## Executed local result
The full local Python implementation passed **35/35 tests**, including resource warnings checked as errors. Positive quorum accepted; wrong content, missing file, forged signature, stale or duplicated nonce, repeated receipt, incorrect witness or key, altered audit event, and incomplete quorum were rejected. Reopening the persisted gate preserved the used-receipt state. The demo returned LOCAL_FRESH_STORAGE_ELIGIBLE, replay REJECTED, and two verified audit events.

## Limits and source distinction
The GitHub code and regression tests may be a compact reference different from the full 35-test local artifact; do not claim they passed the local test run unless independently run. This is **not** real remote independent storage, a cryptographic proof of retrievability, authenticated actual operator independence, or Byzantine consensus. A malicious host could borrow the requested file bytes during a challenge. The SQLite ledger is not externally anchored.

## Next WAG-086
Use unpredictable authenticated chunk challenges and bounded spot checks, recording exactly what such checks establish. Test stale responses, selective missing blocks, and an explicit remote-host trust boundary.
