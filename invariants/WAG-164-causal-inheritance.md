# WAG-164 — Recursive causal inheritance

Actual local Python run on 2026-11-19: 8 tests passed in 0.006s. 164 deterministic generations replayed from genesis, first two transferring inventory and remaining 162 empty checkpoints. Inventory 26 including center 6; reserve 536, spent 4. Parent fingerprint and canonical sorted branch fingerprints retained. Stale or overlapping branches rejected; input parent not mutated. Checkpoint tampering rejected by replay.

Limits: isolated in-memory deterministic model; no signed witness certificates, signed admission, persistent ledger, external head anchor or rollback protection. Empty checkpoints demonstrate ancestry depth, not learning or physical time. Full canonical address not implemented. Next: retained ancestry proof and authenticated head anchoring.
.dlw
