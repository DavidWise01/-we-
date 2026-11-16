# WAG-097 — Durable Pin Recovery and Signed Anchor Receipts

Date: 2026-11-16. Status: **15/15 local Python unit tests passed**.

## Invariant

`ACCEPT_NEW => VALID_SIGNED_LOG_HEAD AND MERKLE_INCLUSION AND VALID_SIGNED_ANCHOR_RECEIPT AND PINNED_PREFIX_CONTINUITY AND DISTINCT_DECLARED_ANCESTRY`

Once Jane pins an authenticated log head and the corresponding complete prior leaf prefix, a restart must reload that pin before comparing future evidence. A shorter history yields HOLD_ROLLBACK. A changed frozen prefix yields QUARANTINE_FORK; conflicting observations are appended to evidence, and the trusted pin is not overwritten. All three configured logs must have current, matching checkpoint entries and different anchor identities to become eligible for **further external custody verification**.

## Implemented local model

- Python reference derives from WAG-096's Ed25519 log-head signatures and custom SHA-256 domain-separated Merkle inclusion proofs.
- Independently named synthetic anchor keys sign domain-separated WAG097 receipts bound to log identity, log-head signature, tree size and digest.
- SQLite with `PRAGMA synchronous=FULL` stores one pinned head/prefix/anchor per log and appends evidence in transactions.
- A SHA-256-linked event chain detects tested local record mutation, including across normal restarts.
- Fail-closed states include HOLD_INVALID_HEAD, HOLD_INVALID_INCLUSION, HOLD_INVALID_PREFIX, HOLD_UNKNOWN_ANCHOR, HOLD_INVALID_RECEIPT, HOLD_ROLLBACK, QUARANTINE_FORK, HOLD_MISSING_PIN, HOLD_SHARED_ANCHOR, HOLD_MISSING_ENTRY and QUARANTINE_AUDIT_TAMPER.

## Executed tests

15/15 `unittest` tests passed locally: valid 3-pin checkpoint; restart; rollback after restart; fork after restart; wrong anchor signature; reused anchor; missing pin; audit record edit; forged log head; bad inclusion proof; valid extension; fork evidence preservation; missing entry; unchanged pin on fork; audit verification after restart.

## Scope and unproven properties

The witness and receipt authorities were locally generated. The prototype's 'anchors' are **signed receipts, not external independent log inclusion or trusted timestamps**. Distinct declared names do not prove independent operators. The model uses local SQLite, not Byzantine replicated storage; a privileged owner can replace the complete database, and the chain is not off-host anchored. `synchronous=FULL` improves SQLite durability but does not prove resistance to all hardware failures. The logged fork evidence lacks the complete conflicting submitted prefix, so complete forensic preservation remains future work. This implementation uses complete prefix comparisons rather than compact RFC6962 consistency proofs.

The exact tested Python implementation is available as conversation artifacts; this GitHub checkpoint records the specification and HTML story, **not yet the two Python source files**.

## Next natural invariant: WAG-098

Replicate the pinned commitment across three independently managed off-host ledgers; verify anchored recovery after local database replacement, retain complete conflicting evidence and support key revocation without erasing historical signatures.

`{{ observe -> sign -> pin -> restart -> compare -> preserve }}`