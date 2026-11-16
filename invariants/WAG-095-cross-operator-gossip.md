# WAG-095 — Cross-Operator Gossip, Partition Holds, and External Evidence

Date: 2026-11-16. Status: reference implementation; no live third-party service connected.

## Invariant
`ACCEPT => authenticated_observations AND anchored_receipts AND independent_roots AND independent_anchors AND current_round AND no_forks`

Jane must not infer a fresh checkpoint from old consistent data when a witness is partitioned. Different authentic digests from the *same operator and round* are retained as evidence of equivocation; different operators disagreeing is a hold, not automatic proof of operator equivocation.

## State distinctions
- `RECORDED`: claim passes caller-supplied authentication/anchor booleans; observation stored.
- `HOLD_PARTITION_OR_MISSING`: fewer than all required configured operators observed at the required round; no new approval.
- `HOLD_SHARED_ANCESTRY`, `HOLD_SHARED_ANCHOR`: duplicated declared trust roots.
- `HOLD_CROSS_OPERATOR_DISAGREEMENT`: operators disagree; preserve evidence, investigate.
- `QUARANTINE_EQUIVOCATION`: same identified operator and round has conflicting authenticated observed digests; preserve both.
- `ELIGIBLE_FOR_EXTERNAL_VERIFICATION`: policy gate only, *not* a final checkpoint certificate.

## Threat model and important limitations
This Python reference is a deterministic decision model; its `authenticated` and `externally_anchored` flags are *supplied by callers*, not independently proven. Operators, roots and anchor names are declared strings. There is no signature verification, Merkle inclusion, externally witnessed time, actual network gossip, durable off-host log, consensus, or real failure-domain analysis in this WAG-095 prototype. A hostile caller can lie about both flags. Application-specific trust validation must precede this policy gate.

The model requires all 3 configured operators for freshness (a deliberate conservative policy, not a generic Byzantine consensus quorum). A local append-only list is inspectable but not immutable against process replacement. A partition may hold indefinitely. This trades liveness for conservative acceptance.

## Test matrix
Fourteen `unittest` cases cover normal agreement, missing operator, partition recovery, operator equivocation, old-round hold, shared ancestry, shared anchors, cross-operator disagreement, unauthenticated message, unavailable external anchor, unconfigured operator, negative round, repeated identical statement, and preserved fork.

Run: `cd invariants/wag095 && python -m unittest -q`

## Next boundary — WAG-096
Connect an actual independently managed transparency log or timestamp receipt verifier; validate signed inclusion, monotonic publication and receipt-operator ancestry before setting either trust flag. Test untrusted anchors and malicious gossip relays.
