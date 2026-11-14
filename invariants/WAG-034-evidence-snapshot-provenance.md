# WAG-034 — Evidence Snapshot Provenance and Causal Budget Allocation

Status: instantiated locally 2026-11-14; 22/22 unittest cases passed.

## Invariant

EVIDENCE_SEALED < BUDGET_REGISTERED < TEST_RESULT

Every adaptive test registration records the SHA-256 identifier and sequence number of a previously finalized evidence snapshot. The registered alpha is immutable, and a descendant inherits its ancestor's allocation rather than opening a new statistical family.

## Reference kernel
- Local downloadable artifact: wag034.py (CausalBudget, Snapshot and Registration classes)
- Local test suite: test_wag034.py, 22 checks passed.
- Ledger: genesis, evidence records, immutable snapshot, test registration, subsequent result, agent lineage and inheritance.
- All mutations are appended to a SHA-256 hash-linked chain.
- Decimal arithmetic enforces exact budget conservation.
- Test results that cite evidence collected before registration are rejected.
- Invalid replay, insufficient budget, unknown snapshot and unauthorized inheritance are rejected without appending events.

## Executed demonstration
Total budget: 0.05; registered alpha: 0.03; remaining budget: 0.02.
A scout registers a test against a sealed historical evidence snapshot, submits a new result, and spawns a descendant who inherits the original registration.
9 ledger records; verify() returns true.
22/22 unittest checks passed.

## Security caveats
SHA-256 identifiers provide content commitments but cannot authenticate the real-world provenance of observations without signatures/attestation. The prototype uses in-memory mutable structures and a single-writer model, not independently anchored durable storage. It ensures causality of recorded events, but does not prove that external information was unavailable to the caller at registration time.

## WAG-035 — Cross-Family Allocation and Statistical Ownership
When Jane's hive spans several distinct hypothesis families, prevent agents from laundering an already-tested hypothesis into a new family to obtain another false-alarm budget. Assign stable semantic hypothesis identities with provenance, link related families, and explicitly approve any family-level allocation without double-counting tests.
