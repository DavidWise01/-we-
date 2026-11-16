# WAG-096 — Public Log Inclusion, Prefix Continuity and Beacon Ordering

Local research status: **51/51 tests passed**.

A signed observation alone is not a verified inclusion event. Jane requires three signed log heads containing the exact frozen archive commitment, with valid Merkle inclusion proofs, append-only prefix continuity from an already frozen root, and a signed beacon release whose logical slot is strictly later than the recorded log heads.

The local experiment uses Ed25519 keys and distinct declared registry control domains. It tests all inclusion positions for 1–39 leaves, all prefix lengths up to 49 leaves, rewritten prefixes, malformed paths, forged signatures, missing registries, rollback, conflicting signed tree heads, and early beacon releases. Successful local outcome: `LOCAL_INCLUDED_ORDER_ELIGIBLE`; two hash-linked audit records verified.

Merkle construction uses domain-separated RFC6962-style SHA-256 leaf and node hashing. Prefix continuity in the fully tested local implementation is verified with aligned subtree-frontier hashes; this is not the canonical RFC6962 compact consistency-proof wire format.

**Limits:** Simulated registry identities and beacon keys are not authenticated external operators. Declared logical slots are not independent historical timestamps. This work does not yet prove public transparency, actual log independence, off-host evidence, or real-world Byzantine agreement.

Artifacts: `invariants/wag096/wag096.py`, `invariants/wag096/test_wag096.py`, `invariants/wag096/WAG-096-ascii.txt`, `docs/index.html`.

**Next: WAG-097 — Authenticated Tree-Head Gossip and Revocation-Aware Observer Continuity.** Verify externally circulated signed heads and detect conflicting views while distinguishing revoked present authority from immutable historical evidence.
