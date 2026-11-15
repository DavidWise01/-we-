# WAG-070 — Epoch-Bound Evidence Freshness and Recovery Snapshot Gate

**Local execution:** 45/45 Python unit tests passed on 2026-11-15. Synthetic demonstration has 13 verified SHA-256 hash-linked audit events, recovering from epoch 0 through a power-y failure (epoch 1) and repair (epoch 2).

## Natural invariant

`PREVIOUSLY_VALID_EVIDENCE != CURRENTLY_VALID_EVIDENCE`

A checkpoint can be locally certified only after all three witnesses are available, the complete infrastructure snapshot has been verified in the current recovery epoch, and three fresh independently labeled receipts have been bound to that **exact `(epoch, snapshot digest)`**. Any change to infrastructure state increments the epoch, invalidates verification and clears current receipts. An old receipt ID is permanently barred from reuse even with a forged new epoch label.

The snapshot includes the current epoch, domain-state flags, and witness dependency mapping. Separate evidence ancestors A/B/C, operators, and failure-domain labels must be distinct. The labels themselves remain *declarations*, not independent attestations.

## Demonstration

1. Epoch 0: power-y and network-x healthy; W1/W2/W3 each attest; local certificate recorded.
2. Epoch 1: power-y fails, disabling W1 and W2; old verification and receipts invalidate, W3 remains available.
3. Epoch 2: power-y repaired, three witnesses available but not trusted until infrastructure reverified.
4. Old epoch-0 receipts are rejected. A new snapshot digest is verified, three newly labeled attestations are accepted, and a new local certificate is appended. The old certificate remains in the historical hash-linked ledger but cannot be used for current trust.

## Test scope

45/45 local tests cover epoch changes, stale hashes, premature certification, missing and duplicate witness receipts, cross-epoch reused receipt IDs, domain outages, failed recovery, declared ancestry collisions, invalid inputs, immutable audit references, and deliberate ledger tampering.

## Important limitations

This is a **local deterministic reference**. It provides no authenticated signatures, secure hardware-backed clocks, durable anchoring, or real Byzantine agreement. Hash-linked Python memory can be rewritten by a privileged actor. Stated evidence and independence are self-declared; cryptographic identity verification is future work. The GitHub files should be executed in CI before calling the repository tested.

## Files

- `invariants/wag070/wag070.py`
- `invariants/wag070/test_wag070.py`
- `invariants/wag070/WAG-070-ascii.txt`
- `docs/index.html`: cumulative journal with ASCII art embedded in `<pre>`

## Next natural invariant — WAG-071

**Signed Recovery Snapshot and Cross-Witness State Agreement:** require independently authenticated witnesses to attest to identical epoch, snapshot digest, dependency ancestry, and repair lineage, preserving contradictory signed observations rather than converting disagreement into a majority statement.