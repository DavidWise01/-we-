# WAG-036 — Semantic Claim Graph and Evidence-Overlap Conservation

Status: instantiated and tested 2026-11-14. 22/22 local Python unittest cases passed.

## Invariant
Shared evidence does not imply equivalent hypotheses. Distinguish reviewer-attested `equivalent`, directed `entails`, `overlaps`, and `disjoint`; leave unspecified relationships `unknown`.

A test's evidence roots must not be counted again as independent confirmation under another claim or family identity. All claim and relation assertions have append-only provenance, and the whole hive remains under its existing alpha budget.

`NEW_LABEL != NEW_INDEPENDENT_EVIDENCE`

## Graph specification
Each claim has an immutable claim ID, human-readable proposition and domain. Each relation records endpoints, relation kind, reviewer and evidence-reference IDs.

Equivalence is symmetric and transitively represented by connected components; implication is directional and supports reachability; overlap and disjoint are symmetric declared relationships. Unknown is not equivalent to disjoint. The reference implementation blocks certain directly contradictory assertions, but is not a complete theorem prover.

Two claims with a shared root have a *union* of one distinct evidence root rather than two independent observations. Confirmation-test registration rejects reuse of any evidence root from an already registered test. Decimal allocations are charged to one family-wide budget.

## Synthetic demonstration
- A and B equivalent.
- A and C overlap.
- A and D disjoint.
- A/B each refer to one shared observation root, counted once.
- Register test A for 0.02 of a 0.05 family allowance.
- Attempt to register test B with recycled confirmatory root; rejected.
- Remaining allocation = 0.03; hash-linked ledger verifies.

## Validation
22 local unittest checks passed: equivalence and transitivity, directed entailment and transitivity, overlap, disjoint, ambiguous/unknown, invalid declared relations, root union deduplication, recycled test evidence, registration, budget exhaustion, immutable-looking ledger integrity and tamper detection.

## Limits
Semantic classifications are explicitly reviewed declarations, not automatic formal semantic inference. The graph does not exhaustively enforce all logical consequences of combinations of relation types. Shared observation ancestry should be authenticated externally; root labels alone are insufficient. In-memory SHA-256 chains do not provide externally anchored durable storage. Distinct properly precommitted confirmatory tests can be valid even when they evaluate one hypothesis again, if their actual evidence roots and error budgets are separately accounted for.

## WAG-037 — Evidence Dependency Graph and Conditional Independence
A pair of distinct roots may share a source upstream. Track transitive observation dependencies and provenance claims in a graph; distinguish evidence source independence from statistical conditional independence. Require a defensible independence argument or independent audit before combining evidence as independent support.
