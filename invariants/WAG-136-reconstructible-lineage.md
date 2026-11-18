# WAG-136 — Reconstructible authority lineage

10 local tests passed in 0.182 seconds after correcting ancestry-check ordering. Public-key replay validates parent, approval by current membership, incoming acceptance on rotation, canonical key identity, retirement and conservation. Export reads journal and head in one SQLite snapshot and requires a caller-pinned expected head. Two rotations preserve an in-flight obligation.

Limits: trusted genesis and expected head are supplied externally; no independently retained freshness authority, declared control-root integration or distributed consensus. An old valid head plus its corresponding old prefix still passes. Malformed operation handling is not exhaustive. Next WAG-137: topology-bound replay with independently retained head certificates and explicit control ancestry.
