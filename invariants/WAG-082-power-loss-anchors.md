# WAG-082 — Power-Loss Recovery, Signed Anchors, and Fork-Safe Restoration

Date: 2026-11-16. **30/30 local Python tests passed** (with ResourceWarning treated as an error).

## Invariant

`LOCAL_DURABLE_COMMIT != INDEPENDENTLY_VERIFIED_RECOVERY`

The reference uses two stores, a SQLite checkpoint (WAL, synchronous FULL, local transaction) and a separately fsynced append-only JSONL file of signed anchor records. Three synthetic Ed25519 witnesses sign a domain-separated tuple `(epoch, size, root, previous_anchor_hash)`. Every anchor verifies all signatures, a SHA-256 content digest, and a hash-chain link. The checkpoint and signed-anchor head must agree exactly on epoch, size and root before local recovery reports `RECOVERY_MATCH_LOCAL`.

## Decision states

- `RECOVERY_MATCH_LOCAL`: local and latest signed anchored epoch/size/root agree.
- `HOLD_UNANCHORED_LOCAL_ADVANCE`: local transaction committed but anchor has not caught up; e.g. crash window.
- `HOLD_LOCAL_ROLLBACK`: signed anchor is newer than local checkpoint; do not overwrite local state automatically.
- `QUARANTINE_FORK`: same epoch but different size/root.
- `HOLD_NO_ANCHOR` or `HOLD_NO_LOCAL`: missing evidence.
- `QUARANTINE_*`: corrupted or forged anchor chain or record.

The code is intentionally fail-closed. Two-file writes are **not** a distributed atomic transaction. A crash can leave divergence; exact-match recovery does not silently repair it. Signed anchors are appended in the reference using locally generated keys and same-host file operations; they are NOT independent off-host witnesses or public timestamping. The append-only file is not tamper-proof against deletion, truncation, privileged writes, or concurrent unsynchronized appenders. Anchors are not checked against a Merkle extension proof; end-to-end integration with WAG-079/WAG-081 remains necessary.

## Demonstration

- At epoch 0 both stores agree: `RECOVERY_MATCH_LOCAL`.
- Commit local epoch 1 before signing/persisting anchor epoch 1: `HOLD_UNANCHORED_LOCAL_ADVANCE`.
- Append epoch 1 record with W1/W2/W3 signatures: `RECOVERY_MATCH_LOCAL`.

## Tests

30 passing tests cover missing evidence, forged/missing signatures, bad ancestry declarations, mismatched roots, rollback-like local lag, unanchored local advance, epoch and size monotonicity, a damaged/truncated anchor file, chain continuity, restart and invalid-state atomic rejection. The local code was executed; GitHub CI status should be verified separately.

## Artifacts

- `invariants/wag082/wag082.py` — full Python recovery gate.
- `invariants/wag082/test_wag082.py` — full 30-case regression suite.
- `invariants/wag082/WAG-082-ascii.txt` — ASCII visualization.
- `docs/index.html` — HTML journal inline ASCII visualization.

## Next WAG-083 — Off-Host Anchor Quorum and Restoration

Demand three authenticating external observer systems, separately administered failure domains, authenticated anchor receipts, and a reconciliation protocol that cannot turn any single local loss into a false trusted recovery.