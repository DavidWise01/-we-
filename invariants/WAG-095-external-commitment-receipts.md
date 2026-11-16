# WAG-095 — Signed Commitment Receipts and Beacon Release Ordering

## Invariant

Three distinct **declared** log authorities must sign the same archive root, epoch, round and observation slot. Freeze the signed receipt set before considering a separately signed beacon release tied to its exact digest. A release slot must be greater than the receipt slot.

`THREE_SIGNED_RECEIPTS + FROZEN_SET + SIGNED_LATER_RELEASE -> LOCAL_DECLARED_ORDER_ACCEPTED`

This **does not** establish externally authenticated chronology, independent controllers or unpredictable beacon output. Logical slots are signed claims; a dishonest coalition could backdate receipts. Three witnesses are this application's governance threshold, not a Byzantine consensus guarantee.

## Reference demonstration

- Three test authorities A, B, C each sign `commit-observed` for epoch 95, round 1, root R and logical slot 12.
- The gate freezes the exact signed receipt set, obtaining a deterministic SHA-256 digest.
- A fourth test key signs a `beacon-released` statement for the same root, epoch, round, digest and slot 13.
- Gate returns `LOCAL_DECLARED_ORDER_ACCEPTED`, with six verified SHA-256-linked audit records.
- Rejection tests cover missing and disagreeing receipts, duplicate issuers, colliding declared roots/controllers/domains, malformed statements, forged signatures, replayed release and earlier/equal slots.

## Test statement

42/42 Python `unittest` cases passed locally, with `ResourceWarning` treated as an error. The registered test keys and time slots are synthetic. Events are held in-process in a hash chain and are not backed by an off-host transparency service.

## Next invariant — WAG-096

Externally witnessed inclusion and release ordering: obtain verifiable signed tree heads and inclusion proofs from actual independent logs; preserve the last verified head and require consistency proofs across newer heads. Treat an unavailable registry or conflicting head as HOLD / QUARANTINE, not a license to infer chronology.