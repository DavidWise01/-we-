# WAG-020 — Causal Fork Reconciliation

Status: instantiated reference, 2026-11-14. Local Python implementation and 16 tests passed.

## Invariant
Merge(A,B) => common immediate parent AND valid branch records AND comparable event/scope AND distinct claimed evidence roots AND exact canonical observation agreement.

## Decisions
- MERGE: compatible observations with distinct roots; create immutable two-parent reconciliation node and update head.
- CONFLICT: valid conflicting observations; preserve both branches and keep current head.
- HOLD: shared roots or incomparable event/scope; preserve without trusting.
- REJECT: missing branch, duplicate branch, replayed packet ID, or different parent.

## Data structure
Each branch records (event, scope, observation, root, packet ID, author) and a single parent hash. A reconciliation node records exactly two sorted branch hashes, common ancestor, decision and reason. Its content is SHA-256 hashed. Every append-only record includes sequence, previous chain hash, node content and new chain hash.

## Tested cases
16/16 local tests passed: valid merge, preserved parents, conflict, no head change on conflict, shared root, event mismatch, scope mismatch, packet replay, unknown parent, duplicate branch, different ancestors, nonbranch reconciliation rejection, ledger integrity, tamper detection, parent order independence, and end-to-end demo.

## Limits
This reference uses a deterministic single-writer in-memory ledger. Unique root IDs do not authenticate independent acquisition; external provenance and signatures are still required. Hash chaining alone does not prevent replacement of an unanchored entire ledger. Two compatible observations do not satisfy any separate three-witness consensus policy.

## WAG-021 — Three-witness Fork Certification
A two-branch merge is a reconciled candidate, not an automatically trusted checkpoint. Require a third independent witness agreeing on exactly the canonical event/scope/observation, authenticate all three roots, and seal a certified checkpoint without rewriting the two-parent merge ancestry.
