# WAG-071 — Signed Recovery Snapshots and Three-Witness Agreement

Date: 2026-11-15. Local Python implementation: 42/42 unit tests passed.

## Invariant

Each signed witness report binds a domain-separated protocol identifier, witness identity, recovery epoch, exact SHA-256 snapshot hash and fresh nonce. Accept locally only if exactly three unique declared ancestors/domains/keys are represented, all Ed25519 signatures verify, the current infrastructure snapshot has been marked verified, and all three hashes match the expected recovery snapshot.

`VALID_SIGNATURES != AGREEMENT_ON_SNAPSHOT`

## Executed conflict scenario

A synthetic epoch-2 recovery snapshot A is considered verified; W1 and W2 provide valid signatures for A; W3 provides a valid signature for a different snapshot B. All three signatures are valid, yet the gate returns `QUARANTINE_SNAPSHOT_CONFLICT` and retains the conflicting report. The four-event hash-linked audit verifies. The matching three-signature control case returns `LOCAL_SIGNED_QUORUM_ACCEPTED`.

## Security and evidence boundaries

The locally generated Ed25519 signing keys are deterministic test fixtures, not real-world witness identities or secured private keys. Three distinct declared ancestor and domain labels are not proof of independent evidence origins. The infrastructure-verified Boolean is an asserted input, not a hardware-backed statement. The audit history is an in-memory hash chain, not independent external anchoring. The kernel does not provide a complete Byzantine agreement protocol.

## Tested cases

42 local tests cover matching signatures, valid signed disagreement, incorrect signatures, changed signed fields, stale/future epochs, nonce replay, duplicate witnesses, declared ancestry/domain/key collisions, incomplete quorum, missing infrastructure verification, audit chain tampering and evidence preservation.

## Files

- `invariants/wag071/wag071.py` — signed snapshot gate
- `invariants/wag071/test_wag071.py` — 42 local tests
- `invariants/wag071/WAG-071-ascii.txt` — cumulative story visual
- `docs/index.html` — embedded ASCII chapter

## Next WAG-072 — Challenge-bound snapshot signing and cross-witness equivocation

Require each witness response to bind an unpredictable verifier challenge, signed collection-round ID and exact previous checkpoint; detect a signer producing conflicting snapshots for the same round, preserving both signatures as an equivocation certificate. A challenge raises freshness assurances but does not prove that the signer physically observed the claimed infrastructure.