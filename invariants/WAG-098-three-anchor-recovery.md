# WAG-098 — Three-Anchor Recovery Against Local Database Replacement

Date: 2026-11-16

## Invariant
`RECOVER => VERIFY(3 distinct named Ed25519 receipts) AND MATCH(all committed state digests) AND RESTORE(signed snapshot)`.
`MISSING => HOLD; BAD SIGNATURE => QUARANTINE; DISAGREEMENT => QUARANTINE; REWRITTEN_PREFIX => QUARANTINE`.

## Local reference implementation
- Three **simulated** anchor authorities X, Y, Z use distinct generated Ed25519 keys and separate filesystem directories on one host.
- Each authority publishes a JSON receipt containing the exact frozen snapshot, its SHA-256 digest, epoch, anchor name, and a signature over a domain-separated canonical statement.
- Receipts are created with O_EXCL (no ordinary overwrite) and file fsync.
- Jane's local SQLite state is reloaded, compared with the three verified receipt snapshots, and replaced only when all signed snapshots agree.
- The implementation retains local mismatch incidents in process memory and detects changed historical prefixes before declaring a proposed subsequent epoch eligible for anchoring.
- No claim of live external networked storage, certified timestamps, Byzantine agreement, or independence of custodians.

## Tests
17/17 locally executed Python unittest tests passed. They cover: missing local DB, restart and matching pins, wholesale forged local DB replacement, missing anchor, altered receipt signature, altered signed snapshot, contradictory independently signed receipt, duplicate receipt immutability, valid extension, rewritten-prefix fork, shorter invalid extension, same/earlier epoch rollback, cross-anchor receipt replay, receipt wrong epoch, corrupt local DB fail-closed, frozen digest agreement, and missing-all-anchors fail-closed.

## Critical trust boundaries
The three anchor directories and three private keys were generated on the same machine and have a common physical/control failure domain. Merely using distinct folder names is not independent witness ancestry. A privileged adversary able to replace private keys, public-key trust configuration, and all three receipts could fabricate a new internally consistent history. The complete local-database incident is retained **only in memory** and is not durably exported. Corrupt SQLite input currently raises instead of returning a normalized HOLD state. Filesystem O_EXCL is not robust immutable storage against a privileged owner. There is no compact authenticated cross-size Merkle consistency proof in this iteration.

## Follow-up WAG-099
Persist full conflicting receipts and rejected snapshots in an external append-only incident ledger; verify authenticated revocation at specified effective epochs, preserve historical signatures, and handle missing/corrupt remote storage without losing pinned trust.
