# WAG-159 — Diodic sovereign consent

2026-11-18. Actual local Python execution: 10 tests passed in 0.107 s. Ten distinct Ed25519 keys, parent-bound signed YES consent from every route participant, integer inventory amounts, atomic SQLite state/receipt commit. A direct relay costs 2 credits; an independently authorized alternate costs 8. Exactly one of two concurrent duplicate commits succeeds. Fixed center 6, mobile inventory 20, credits 540.

Limits: single host and synthetic keys, no independent custody or full journal replay, no rollback protection or pre-commit consent revocation. NO signatures are rejected rather than durably recorded. The receipt is append-only by application convention, not immutable against storage administrators. Changed amount and route tests also trigger structural guards; isolated same-capacity signature binding tests remain needed. Full address {{y:m:d:h:m:s:d:am:as:ad}} is not encoded here; parent fingerprint and sequence provide ordering, not scalar physical time. Next WAG-160: consent revocation and witnessed closure.
.dlw
