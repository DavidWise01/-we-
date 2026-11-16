# WAG-092 — Verifiable Beacon Binding and Fixed-Sample Recovery

## Objective

Prevent silent sample redrawing when a participant strategically withholds a reveal or fails to answer an unfavorable storage challenge. Each `(checkpoint, round_id)` is bound to one authenticated beacon output and one persistent sample set. Later attempts recover the exact same sample or hold.

## Protocol

1. Verify Ed25519 signature on domain-separated beacon message including checkpoint ID, round ID and output.
2. Derive `k` unique positions in `[0,n)` using SHA-256 counter expansion and 64-bit rejection sampling. This avoids simple modulo reduction bias under the random-oracle/pseudorandom-hash model.
3. Persist checkpoint, round, beacon hash, indices and expected content root within a SQLite `BEGIN IMMEDIATE` transaction.
4. On a missed response, record a terminal `HOLD_ABORT` event. Recovery, if explicitly permitted, transitions that *same stored round and same indices* back to a pending state. A different beacon output cannot be registered under the same round ID.
5. Require three distinct host signatures bound to checkpoint, round, sampled indices, expected content-root declaration and unique receipt IDs. Consume IDs and change the round status atomically. Every transition appends a hash-linked event.

## Local validation

42/42 Python `unittest` cases passed. Tests include signed beacon tampering, same-round redraw, restart persistence, missing or duplicate host, forged host response, wrong round/root/index, abort/restore, replay, duplicate receipt, audit tampering, and atomic failed verification. The unit test suite is local and uses generated keys and SQLite on one host.

## Trust and threat boundaries

- The beacon is signed by a locally generated key. That signature authenticates a key's chosen output; it does **not** prove the operator chose an unpredictable output, could not grind alternatives, or is independent.
- A host signs a content-root *assertion*. This reference intentionally does not reverify WAG-086 Merkle inclusion proofs in the acceptance gate. Real data possession cannot be inferred from the signature alone.
- SQLite can make transitions atomic within one local database; it does not supply distributed Byzantine consensus, physical independence, or off-host anchoring.
- The hash-linked event log is not itself immutable against a database owner replacing both data and hashes. External anchoring is required for stronger evidence.
- Re-enabling the same sample after an abort is an explicit policy decision. Availability can be held indefinitely; no liveness promise is made.
- The sample selection assumes beacon unpredictability until the round is frozen. If the beacon is known to an adversary before archive commitment, selective storage attacks remain possible.

## Next natural invariant — WAG-093

Externally authenticated beacon provenance, immutable pre-beacon archive commitment, and WAG-086 Merkle inclusion evidence included in every host response. Preserve the exact challenge, audited bytes and source ancestry without manufacturing witness independence.

`{{ preserve [freeze → derive once → abort/verify → same-sample recovery] }}`