# WAG-135 — Atomic authority graduation

10 local tests passed in 0.082 seconds. Membership and the conserved inventory share a SQLite transaction. Three current witness signatures approve the parent-bound transition; rotation additionally requires three incoming acceptance signatures. Canonical lower-case 32-byte public key encodings prevent textual aliases. Retired key identities remain excluded, pending obligations survive rotation, and competing writes serialize.

Limits: standalone single-host model, synthetic keys; declared control-root graph validation from WAG-134 is not integrated. No independent custody, rollback resistance, full journal replay on restart, or distributed consensus. The two-thread race tests one schedule per run. Sequence increases on every transition; epoch increases only on rotation. Next WAG-136: public-key replay across changing membership, with topology ancestry checks and externally pinned head.
