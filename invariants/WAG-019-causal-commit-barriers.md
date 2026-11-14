# WAG-019 — Temporal Causality and Immutable Commit Barriers

Status: instantiated reference kernel; 18/18 local tests passing (2026-11-14).

## Invariant

A higher-clock transition must reference an exact, finalized, current lower-clock snapshot. Late, stale, replayed, or reordered evidence cannot rewrite an already committed state.

```
COMMIT(G[n+1]) =>
  CurrentParent(G[n+1])
  AND MonotonicTick
  AND CompareAndSwapRevision
  AND UniqueEvidence
  AND DistinctWitnessIds
  AND AppendOnlyAudit
```

## Three clock types
- synapse: independently evidenced local snapshot
- route: parent must equal current finalized synapse head
- generation: parent must equal current finalized route head

Each immutable Snapshot contains kind, revision, parent hash, logical tick, evidence identifiers, witness identifiers, and SHA-256 content hash. Ledger entries include an incrementing sequence, previous entry hash, and current hash.

A superseded parent may be inspected in history but cannot authorize a new higher-clock commit. New evidence belongs to a later revision.

## Local test results
18/18 tests passed: valid lineage, monotonic clocks, stale revisions, missing/wrong/superseded parents, duplicate witnesses, duplicate or replayed evidence IDs, atomic rejection, ledger tamper detection, and old snapshot preservation.

## Scope and limits
Reference implementation is deterministic single-writer Python; this spec does not claim deployment. Witness IDs are not independent-source authentication. SHA-256 hash chaining does not substitute for durable, externally anchored storage or concurrent transactional semantics.

## Next invariant — WAG-020
Causal fork reconciliation. Concurrent valid proposals from the same finalized parent must become explicit fork records, not silently overwrite one another. Reconciliation must preserve both branches, verify their evidence independence, and produce a new merge checkpoint with a documented decision.
