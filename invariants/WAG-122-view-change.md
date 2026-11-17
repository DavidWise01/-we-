# WAG-122 — Unanimous view-change recovery

2026-11-17. Local execution: seven unittest cases passed, including all 27 combinations of empty, A and B locks. Two combinations preserve the old unanimous value; 25 permit a fresh view after unanimous signed closure.

Each honest witness signs its final lock and refuses further votes in the closed view. All three closure signatures bind name, view and lock. Unanimous nonempty locks require recovery of the old vote certificate rather than opening another view. Divergent locks or at least one genuinely empty lock permit advancement. Absent or invalid closure signatures hold.

Scope: standalone single-slot symbolic A/B model with synthetic keys and in-memory state. Assumes honest non-equivocating witnesses, fixed membership, and no rollback. Signatures alone cannot prove honest reporting of prior votes. No durable view state, cross-slot domain binding, inventory integration, or Byzantine liveness. Do not deploy as consensus. The 27 configurations are not all possible network schedules.

Next WAG-123: persist closure and view state atomically and bind each signature to mesh identity, checkpoint slot and prior certified state; integrate WAG-121's journal and test restart.
