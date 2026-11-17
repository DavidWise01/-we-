# WAG-128 — Atomic temporal authorization

11 local Python tests passed in 0.072 seconds. Three distinct Ed25519 witness keys sign mesh, nonce, parent root, exact operation and resulting root. SQLite BEGIN IMMEDIATE serializes competing proposals. Head and signed receipt commit in the same transaction. An identical nonce retry returns the durable historical receipt, not a fresh authorization. Conservation: 156 ticks = 26 symbolic units.

Scope: one trusted gate, one host, synthetic keys. No independent custody, expiry, durable witness non-equivocation or integration of WAG-127 live freshness floor. No rollback protection. The gate retains receipt hashes but not complete signed proposal history, so independent full replay is not yet possible. Tests cover two competing threads, not arbitrary distributed schedules. Next WAG-129: durable full proposal certificates and independent audit replay, followed by external anchoring.
