# WAG-097 — Authenticated Tree-Head Gossip and Split-View Evidence

Date: 2026-11-16. Local reference tests: **44/44 passed**, with ResourceWarning treated as error.

## Invariant

A valid signed head received by one observer does **not** prove a globally consistent history. Require signed log-head authenticity, signed observer gossip, a three-declared-ancestor agreement gate, and preserved conflicting heads.

`SAME_LOG_AND_SIZE_AND_DIFFERENT_SIGNED_ROOTS => QUARANTINE_SPLIT_VIEW`

## Model

- A log signs the tuple `(log_id, epoch, tree_size, Merkle_root)` using Ed25519.
- W1, W2 and W3 independently sign their observation of the exact signed-head fields.
- A SQLite evidence ledger keeps signed observations, a hash-linked audit, and persisted quarantine status. It detects different signed roots at the same log size even if different observers receive them.
- The reference uses RFC6962-style leaf/node hash prefixes. For extensions, **full leaf snapshots** are compared, not compact Merkle consistency proofs. An increased tree size with no supplied continuity evidence is held.
- A detected prefix rewrite or same-size conflict is recorded and held even when the relevant Ed25519 signatures are valid.
- Distinct identity, operator, ancestry, and domain strings are declared by the harness, not independently authenticated facts.

## Executed example

The three observers initially report the tree `[A, B, C]`, producing `LOCAL_AGREEMENT`. The log then signs the contradictory same-size head `[A, X, C]` for W3; the gate returns `QUARANTINE_SPLIT_VIEW`. Five audit events verify. Reopening the SQLite database does not erase the quarantine.

## Limitations

This is **not** a distributed consensus protocol or independent public gossip deployment. Log and observers are locally generated test identities. Same-size forks are authenticated syntactic contradictions, but different-size forks require sound cryptographic consistency proofs plus trusted historical roots. The current reference uses complete original and candidate leaf lists for that check; public online observers and revocation policy are not integrated. Hash-linked local audit is tamper-evident only against unsynchronized mutations, not a durable external anchor.

## Next — WAG-098

Inter-observer *cross-size* compact consistency proofs; require monotonic signed history across observers, preserve minimal cryptographic fork certificates, and distinguish missing consistency evidence from verified inconsistency.