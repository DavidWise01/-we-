# WAG-098 — Compact Cross-Size Consistency, Fork Evidence, and Three-Observer Agreement

## Invariant

A tree head of size *n* may legitimately differ from a head of size *m < n*. Accept its history as append-only only if a compact Merkle proof reconstructs **both** independently signed roots and demonstrates that the old tree is exactly the prefix of the new tree.

`SAME_SIZE + TWO_VALID_DIFFERENT_ROOTS => SIGNED_FORK_CERTIFICATE`

`DIFFERENT_SIZES + NO_VALID_CONSISTENCY_PROOF => HOLD`

`THREE_FRESH_MATCHING_OBSERVERS + VERIFIED_EXTENSIONS => LOCAL_CROSS_SIZE_AGREEMENT`

## Reference model

- RFC6962-style domain-separated SHA-256 leaf (`0x00`) and interior (`0x01`) hashing.
- Canonical aligned-dyadic range-frontier proof (compact subtree hashes only), **not** the RFC6962 wire proof format.
- A log Ed25519 key signs exact registry ID, epoch, size and root. Each of three observer keys signs an exact head and shared challenge.
- Verified consistency edges connect frozen smaller heads to larger heads. Three distinct signed observers must report the same newest head for eligibility.
- Two valid log signatures on **different roots at the same size** produce an explicit, retained fork certificate and persistent quarantine.
- Missing or invalid proofs result in HOLD; they do **not** alone prove log equivocation. Failed proof attempts are retained in the local audit.
- SQLite persists views, consistency edges, decisions and a SHA-256-linked event sequence. State persists on restart.

## Executed tests

43/43 local Python tests passed on 2026-11-16. They cover honest cross-size extensions, 80 distinct prefix sizes, altered prefixes, malformed proofs, forged Ed25519 signatures, replayed observer reports, mismatched scope and challenge, same-size log forks, cross-size unproven holds, distinct declared ancestry/operator/domain labels, audit mutation, and post-restart quarantine.

The honest demonstration records four observation events, verifies its audit, and ends in `LOCAL_CROSS_SIZE_AGREEMENT` (three observers at size 5 after size 3 was signed).

## Limitations

The observer identities, distinct control roots and operating domains are synthetic and self-declared. Local signatures do not prove independent operation. The SQLite database and audit chain are not externally anchored. An invalid consistency proof can represent a malformed proof request rather than equivocation. Current implementation requires a supplied old signed head for cross-size proof edges; it is an experimental reference, not production network gossip or generalized Byzantine consensus.

## Next — WAG-099: Pinned Head Freshness and Revocation-Safe Recovery

Bind consistency edges and signature verification to persistent, exact challenges and witness-key revocation epochs, so a revoked observer or replayed old head cannot silently restore trust after a split view.