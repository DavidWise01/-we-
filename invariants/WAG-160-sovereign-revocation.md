# WAG-160 — Sovereign revocation

Actual local execution: 10 tests passed in 0.102s. Signed NO and unanimous YES compete under one SQLite immediate transaction. First successful closure advances the parent fingerprint and appends one receipt; a later closure of that parent fails. Withdrawal preserves inventory and reserves. Fresh consent for a new parent remains possible.

Limits: single local registry and synthetic keys. First committed closure wins, not first signed or transmitted decision. A withdrawal invalidates all sibling proposals sharing the same parent. No total-order witness network, independent custody, rollback protection or complete journal replay. Mesh identifier is fixed and independent instances with identical genesis keys share a signing scope. Full address {{y:m:d:h:m:s:d:am:as:ad}} not implemented; sequence is ordering, not elapsed time. Next WAG-161: independent proposal identity, explicit admission, and witnessed closure without sibling invalidation.
.dlw
