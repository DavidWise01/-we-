# WAG-103 — Persistent mutation holds

A detected graph mutation persists in SQLite across restart. Even a return to the original graph cannot clear the hold. Three pinned Ed25519 reviewers must sign the exact prior state and next graph/epoch; the new graph must have disjoint declared witness ancestry. A fresh matching signed policy anchor is required for local eligibility. The verifier compares the externally supplied anchor to the current state. An older local state mismatches a retained newer anchor.

19 local unit tests passed, including restart, stale proposal, forged approvals, rollback mismatch and audit tamper detection. Test keys and graph ancestry are synthetic. The anchor is supplied by the caller, not fetched from an independently operated monotonic service; replaying both the old anchor and old local state remains possible. Audit hashes are not externally anchored, and audit verification is separate from eligibility. This standalone model does not integrate WAG-102 directly.

Next WAG-104: monotonic anchor retrieval and rollback-resistant audit tails.
