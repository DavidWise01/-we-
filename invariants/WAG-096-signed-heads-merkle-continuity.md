# WAG-096 — Signed Tree Heads and Merkle Continuity

Date: 2026-11-16

## Invariant

`ELIGIBLE => THREE_VALID_SIGNED_HEADS AND THREE_VALID_INCLUSION_PROOFS AND PINNED_APPEND_ONLY_CONTINUITY AND DISTINCT_DECLARED_ROOTS`

Jane validates Ed25519 log-head signatures, SHA-256 domain-separated Merkle membership proofs, and full-prefix append-only history continuity against local pinned signed heads. A shorter new head is HOLD_ROLLBACK. An authenticated changed prefix is QUARANTINE_FORK. Missing logs or absent checkpoint entries cause HOLD, not fabricated agreement.

## Reference details

- Head signing payload is canonical JSON: `{"tag":"WAG096-head-v1","log":id,"size":n,"digest":root_hex}`.
- Leaf digest `SHA256(0x00 || canonical_json(entry))`; parent digest `SHA256(0x01 || left || right)`.
- Odd orphan nodes are promoted unchanged; this is a custom Merkle profile, not interchangeable with RFC 6962 trees.
- Inclusion proofs are ordered side/hash pairs validated against the signed head.
- Consistency evidence uses **full new leaf prefixes** compared to locally pinned complete prior prefixes. This is deliberately inefficient but auditable; not a compact logarithmic consistency proof.
- Three declared ancestry roots must differ. Declared roots do not establish actual independent ownership.
- The gate returns `ELIGIBLE_FOR_EXTERNAL_TIME_AND_CUSTODY_VERIFICATION`, **never final acceptance**.

## Local test run

17/17 Python `unittest` cases passed on November 16, 2026. Tested: normal three-log path, absent log, absent entry, append-only upgrade, same-size fork, extended fork, rollback, forged signature, missing proof, altered entry, bad prefix, shared ancestry, empty head, preserved fork evidence, odd Merkle nodes, wrong index, same signed head replay.

## Critical limits

Keys are synthetic and generated locally. No actual remote transparency logs, independently witnessed timestamps, off-host storage, log-custody independence, stable durable pins, or live beacon service were verified. The in-memory pinned prefixes and observations can be lost on restart. A hostile local operator can replace local state. A valid signature establishes key authorization only, not event chronology or independence. Full-prefix comparison is not a formal external append-only service proof.

## Next natural invariant — WAG-097

Externalize and durably pin signed heads with independent custodians, verify compact log consistency proofs and independently witnessed checkpoint receipt times, and reject conflicting histories after restart.

`{{ freeze -> sign -> include -> pin -> compare -> preserve }}`
