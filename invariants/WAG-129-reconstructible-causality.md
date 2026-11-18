# WAG-129 — Reconstructible causality

11 local tests passed in 0.143 seconds. Complete signed proposals, witness signatures, and gate receipts are stored atomically with the state. Public-key replay verifies ancestry, operation, result, nonce uniqueness and receipts. A trusted expected head detects tail truncation; without one, a valid prefix passes.

Limitations: one SQLite gate, synthetic keys, trusted membership and expected head. Standalone replay checks membership count but relies on caller to supply distinct trusted keys. No upgrading existing WAG-128 histories without missing evidence. No independent custody, external freshness or distributed consensus. Next WAG-130: independently retained signed head certificate and prefix completeness gate.
