# WAG-073 — Equivocation Review, Revocation-Safe Witness Rotation, and Quorum Reconstitution

Date: 2026-11-15. Status: **52/52 local Python tests passed**.

## Invariant

`REPLACEMENT_IDENTITY != RESTORED_TRUST`

W1 first signs two different recovery snapshots for the same challenge and epoch. Both signatures are cryptographically verified. The gate preserves the complete conflicting signed pair as a hash-linked certificate and quarantines W1. An active, nonquarantined reviewer signs a certificate-bound review declaration. W1 can then be retired, but its certificate remains in the ledger and the retired key is excluded from the new quorum. The replacement W4 must carry a distinct key and distinct declared ancestor, operator and failure domain, including nonreuse of all previously held labels. Rotating advances the epoch and constructs a challenge bound to the old certificate and W4's key. New W2/W3/W4 attestations over that challenge, epoch and exact expected snapshot are required before synthetic recertification.

## Executed synthetic demonstration

1. Quorum `(W1,W2,W3)` of distinct declared roots `A,B,C` starts at epoch 2.
2. W1 signs `snapshot-A` and `snapshot-B` for the same recovery challenge. Both Ed25519 signatures verify.
3. Preserve the equivocation certificate, quarantine W1, decision `HOLD_EQUIVOCATION`.
4. W2 signs a certificate-specific review. Retire W1, register W4 (`root D`, different domain/operator/key).
5. Advance to epoch 3 with a rotated challenge; decision `HOLD_FRESH_REATTESTATION`.
6. W2, W3, W4 sign exactly the scoped target snapshot. Decision `LOCAL_SIGNED_QUORUM_RECONSTITUTED`.

The local audit ledger contains **five hash-linked entries**: genesis, equivocation, review, rotate, certify. The local test suite contains **52 successful tests**, including replay, counterfeit signatures, scope mismatches, rejected reuse of ancestry/operator/domain/key, premature rotation, missing receipts, stale epoch, tamper detection, and retention of historical evidence.

## Implementations

- `invariants/wag073/wag073.py` — executable Python reference (requires `cryptography`)
- `invariants/wag073/test_wag073.py` — 52 unittest cases
- `invariants/wag073/WAG-073-ascii.txt` — text-only research illustration
- `docs/index.html` — append-only visual chapter embedding ASCII art

## Security caveats

This verifies local Ed25519 signatures using generated test keys; it does **not** establish independent external identity, operator independence, a trustworthy issuance system, or Byzantine fault-tolerant consensus. Review in this iteration requires only one surviving witness: that is a deliberately weak local governance policy, not an assurance against colluding reviewers. Declared names and failure domains are not authenticated. A SHA256 in-memory hash chain is not externally anchored immutable storage; it can be replaced wholesale by its operator. In addition, signatures over only a snapshot label do not prove the snapshot accurately represents physical infrastructure. Repository publishing is separate from GitHub Actions CI.

## Next natural invariant — WAG-074

**Independent Rotation Authorization and Collusion-Safe Review.** Require a policy-bound review quorum with authenticated reviewer provenance, disallow shared-control reviewers, bind approval to the replacement's public key and full ancestor record, and test two colluding reviewers and replayed/forged rotation authorizations before admitting W4.

`{{ preserve [equivocation -> review -> revoke -> rotate -> reattest] verify }}`