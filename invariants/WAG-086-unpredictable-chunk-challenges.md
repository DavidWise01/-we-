# WAG-086 — Unpredictable Chunk Challenges and Merkle Inclusion Proofs

Date: 2026-11-16. Local implementation: **40/40 tests passed**.

## Invariant

`SIGNED_HOST_ACK != VERIFIED_SAMPLE != FULL_RETRIEVABILITY`.

For each fresh nonce, derive k unique sample indices in [0,N). Require all three declared, separately keyed host responders to return original chunk bytes, SHA-256 domain-separated Merkle inclusion paths, and signatures over the precise challenge, epoch, root, count, index list and samples. Verify all checks *before* atomically consuming the challenge. Persist nonce consumption and audit event in SQLite, surviving process restart.

## Construction

- `leaf(x) = SHA256(0x00 || x)`, `node(L,R) = SHA256(0x01 || L || R)`.
- Tree uses an odd-node promotion rule. This is a **custom Merkle shape**, not a claim of wire compatibility with RFC6962 consistency proofs.
- Sampling uses SHA256-based domain-separated selection seeded by a nonce, selecting unique indexes. For a cryptographically unpredictable nonce and this idealized hash model, an attacker cannot reliably predict the selected positions before challenge delivery. The seed should be generated securely by the challenger in deployment; local tests use fixed reproducible seed bytes.
- Host keys are locally generated synthetic Ed25519 identities. Unique domain and ancestry labels are asserted, not externally verified.
- Final state is `LOCAL_SAMPLED_STORAGE_ELIGIBLE`, not a global quorum certificate.

## Sampling detection model

For N chunks, m unavailable chunks fixed before sampling, and k unique uniformly sampled positions:

`P(detect >= 1 missing) = 1 - C(N-m,k)/C(N,k)` (with zero success combinations interpreted as zero).

Sampling cannot establish the presence of every archive chunk. Data could disappear after the response, and an adversary might temporarily reconstruct challenged chunks or share one back-end. This test does not prove actual remote host independence or a robust proof-of-retrievability scheme.

## Tests

40 unit tests cover arbitrary-size/odd-count Merkle inclusion, corrupt chunk and path, wrong indices and sample counts, signature forgery, incorrect nonce/epoch/root, replay within a process and across restart, invalid host ancestry declarations, atomic rollback and ledger tampering. Local execution: `python -m unittest discover -s /mnt/data/wag086 -p test_wag086.py -v`.

## Next invariant — WAG-087

Quantify the likelihood of detecting partial loss, rotate sample coverage across epochs, minimize overlapping samples where policy allows, and ensure independence assumptions remain explicit. Do not misstate a bounded check as whole-file retrievability.