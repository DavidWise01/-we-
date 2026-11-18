# WAG-137 — Ancestry-bound temporal reconstruction

10 local Python tests passed in 0.059 seconds. Public-key replay binds declared disjoint root sets to genesis and every signed rotation. A separate Ed25519 keeper signs genesis hash, event count, history hash and state hash. The gate rejects a truncated or changed certified prefix and validates extensions. 156 ticks = 26 symbolic units.

Limits: root sets are declared strings, not independently attested control DAGs; the signed bound is caller-retained and the keeper has no durable monotonic issuance policy. An old authentic bound and its old history still pass. This is an in-memory replay model, not an integration with the atomic SQLite gate or a physically independent custody deployment.

Next WAG-138: monotonic keeper retention with topology-bound live freshness, preserving old evidence and rejecting regression and forks.
