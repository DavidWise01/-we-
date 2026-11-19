# WAG-167 — Witnessed root sovereignty

Actual local execution: 9 tests passed in 0.152s. Reproduced WAG-166 root, appended one record, 160-byte proof. Three distinct Ed25519 keys and declared roots, separate SQLite pins on one host. Both competing successors have valid prefix proofs. After unanimous signing of A, all original pins reject B. Recreating all databases at the old pin with the same keys permits a second conflicting certificate. This is a reproduced vulnerability, not a resolved rollback defense.

Limits: no independently controlled custody, externally anchored pins, transition validity checking, durable signature receipts or recovery protocol. Split witness advancement can block progress. Certificate checking verifies signatures against the supplied registry only, not proof or external freshness. Next WAG-168: external monotonic anchor and recovery quarantine. .dlw
