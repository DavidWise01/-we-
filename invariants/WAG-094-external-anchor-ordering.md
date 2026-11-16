# WAG-094 — External Anchor Ordering and Beacon Timing

Date: 2026-11-16

## Natural invariant
An authenticated randomness beacon cannot make a storage sample unpredictable if its value was known before the archive commitment became independently anchored.

`ACCEPT => ARCHIVE_FROZEN < EXTERNAL_ANCHOR_FINAL < BEACON_ROUND_FINAL <= SAMPLE_DERIVED < HOST_RESPONSES`

Here "<" means authenticated causal sequence with independently verifiable evidence, not merely a caller-controlled wall clock. Distinct witness identifiers do not establish independent custodians.

## State machine
`DRAFT -> FROZEN -> ANCHORED -> BEACON_FINAL -> CHALLENGED -> VERIFIED`.
Any signature conflict, invalid anchor inclusion, reused round, rollback, challenge mismatch, or host evidence conflict moves the epoch to `HOLD` or `QUARANTINE`; conflicting records are preserved append-only. An unavailable anchor produces `HOLD_ANCHOR_UNAVAILABLE`, not a synthetic successful timestamp.

## Verifier inputs
- Archive root, chunk count, epoch ID and prior sealed state from WAG-093.
- Independently verified external anchor checkpoint: signed root inclusion or consensus-finality proof, authority identity, and a monotonically ordered sequence.
- Beacon operator identity, authenticated round number, signed output, provider-published schedule and independent publication/availability evidence.
- Deterministic one-time sample derivation, inclusion proofs, and exactly three independently rooted witness responses.

## Fail-closed test matrix
1. Frozen then externally anchored then beacon published: eligible to continue, not automatically certified.
2. Beacon publication before external anchor: HOLD_EARLY_BEACON.
3. Unavailable external anchor: HOLD_ANCHOR_UNAVAILABLE.
4. Reused or regressed beacon round: QUARANTINE_BEACON_REPLAY.
5. Conflicting signed beacons for same operator/round: QUARANTINE_EQUIVOCATION.
6. Self-signed/local anchor falsely labeled independent: HOLD_UNTRUSTED_ANCHOR.
7. Same root at three mirrored endpoints: HOLD_SHARED_ANCESTRY.
8. Unknown timing relationship: HOLD_ORDER_UNPROVEN.

## Proof boundary
This is a protocol/specification and deterministic reference model, **not** a connection to a live TSA, external consensus network, NIST beacon, or off-host witnesses. Local signatures and caller-provided timestamps alone cannot demonstrate external anchoring, unpredictability or physical independence. Verification of time/finality and independent custody must use external trust roots.

## Next boundary — WAG-095
Independently anchor actual transcripts, prevent beacon-provider equivocation with cross-operator gossip, and test how a network partition affects freshness and liveness without silently accepting old checkpoints.
