# WAG-161 — Independent sovereign branches

Local Python run: 9 tests passed in 0.126s. A proposal binds mesh, inventory digest, nonce, path and fixed amount one. Admission and closure are journaled atomically. Withdrawal closes one branch without changing inventory version. A sibling can commit using its original signatures. Two competing inventory commitments cannot both succeed against one inventory digest. Fixed singlet six, mobile inventory twenty, resource credits 540.

Limits: single SQLite host, synthetic keys, no independent witnesses or rollback anchor. Journal is append-only by application convention, not hardened against administrator edits. Admission is unauthenticated; amount fixed to one; a mesh identifier must be unique in deployment. Any inventory change stales all old inventory-bound commitments even if spatially disjoint. Full canonical address {{y:m:d:h:m:s:d:am:as:ad}} not implemented. Next: conflict-local read/write footprints and independent witness validation.
.dlw
