# WAG-079 — Compact Merkle Consistency Proofs and Signed Prefix Certification

Date: 2026-11-15. Full local reference: **48/48 unit tests passed**.

## Invariant

A new signed root is not proof that a frozen historical prefix survives. To certify an extension, a verifier must validate a compact proof that reconstructs both (a) the trusted frozen root of the first `m` leaves and (b) the claimed root of `n >= m` leaves. The gate then requires three signed, scope-matching witness votes.

`VALID_NEW_SIGNATURE != VERIFIED_PREFIX_CONTINUITY`

## Algorithm

- Domain-separated SHA-256 Merkle tree: leaf `SHA256(0x00 || body)`, internal node `SHA256(0x01 || left || right)`.
- Use RFC6962-style power-of-two recursive tree layout; **the proof format is not the RFC6962 standard wire consistency proof**.
- Split leaf intervals `[0,m)` and `[m,n)` into ordered maximal aligned dyadic blocks. Transmit one subtree hash per block, not event bodies.
- Verify block positions and lengths exactly match the canonical intervals; reconstruct `root(old)` and `root(new)` with aligned equal-sized merges and final right folding; compare both supplied trusted roots.
- Proof size is `O(log n)` subtree hashes (two range frontiers). This is a specialized range-frontier consistency proof, not an optimized RFC6962 proof.
- Bind three Ed25519 observer signatures to old/new sizes, exact old/new roots, recovery epoch and challenge nonce. Enforce unique declared ancestor, operator, failure domain, identity and signing key.
- Record decisions in a SHA-256-linked audit. These records are not externally anchored, immutable storage.

## Demonstration

Frozen history `[A,B,C]` is extended to `[A,B,C,D,E]`. Old frontier contains two subtree digests; appended frontier contains two digests. Three synthetic observers sign a matching scope and the result is `LOCAL_PREFIX_CERTIFIED`. Rewriting `B` to `X` produces `QUARANTINE_PREFIX`, even when the attacker supplies a new valid root. Demo records: 3, hash chain verified.

## Tests

48/48 local Python unittests, including every prefix for trees of 1–79 leaves, singleton/odd/equal-size trees, compact proof bound, malformed/reordered/missing hashes, forged old/new roots, rewritten prefix/suffix, stale epochs and challenges, bad and wrong-key signatures, missing votes, and declared-provenance collisions. Repository files are the same locally tested sources if uploaded verbatim; GitHub CI has not been run.

## Limits

Source ancestry and operational independence are declared, not externally proven. A locally certified proof does not imply Byzantine consensus or global registry transparency. External transparency anchoring, stateful receipt replay prevention, persistent checkpoints and third-party registry verification remain needed.

## Next: WAG-080 — Challenge Rotation and Replay-Safe Certification

One valid quorum may attempt to reuse an old signed proof after an intervening checkpoint or revocation. Assign each certification an irrevocable scope and unique challenge; consume valid vote IDs and require monotonic checkpoint progression without rewriting frozen evidence.