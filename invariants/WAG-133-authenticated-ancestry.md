# WAG-133 — Authenticated control ancestry

11 local tests passed in 0.011s. An Ed25519 manifest authority signs a declared control graph, mesh, topology version and witness public keys. The verifier pins the expected version and hash, tests pairwise disjoint declared roots and verifies all three witness signatures over the exact nonce, topology and checkpoint.

Limits: caller supplies trusted topology pin and authority. One manifest authority, synthetic keys, no independent attestation of actual custody, no durable pin or challenge consumption, no expiration or atomic write authorization. The hidden shared root counterexample passes the declared-graph gate. This is a standalone scope-binding prototype, not full WAG-131 integration. Next WAG-134: witnessed topology succession with durable monotonic pin, explicit authority ancestry and old/new membership lifecycle.
