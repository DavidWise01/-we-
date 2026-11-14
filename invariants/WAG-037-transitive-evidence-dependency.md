# WAG-037 — Transitive Evidence Dependency and Conditional Independence

Status: instantiated 2026-11-14. Local deterministic Python implementation: 23/23 tests passed.

## Invariant
Different agents or immediate source IDs do not establish independent evidence. Trace all declared upstream dependencies to originating source identities. Pairwise overlap in those source sets disqualifies the observations from being counted as independent roots.

INDEPENDENT_PROVENANCE(A,B) => ANCESTORS(A) ∩ ANCESTORS(B) = ∅
subject to authenticated and sufficiently complete lineage.

This is *source provenance separation*, NOT statistical conditional independence: distinct instruments may still make correlated errors because of shared environment, data-generation process or unmodeled confounders.

## Reference algorithm
Append-only directed graph, with each new node referencing only existing parents. Source nodes require an origin identifier; derived and observation nodes must reference at least one parent and cannot create a new origin by declaration. Traverse all parent links to collect the unique set of origin identities. Quorum is only ELIGIBLE_FOR_FURTHER_VALIDATION if every pair has disjoint source sets; otherwise HOLD. Reject unknown parents, duplicate nodes, duplicate parent links and unsupported node kinds. SHA-256 hash-linked records support local mutation checks.

## Deterministic demonstration
owned-corpus -> github, 0root.ai: SHARED_ANCESTRY.
external-original-1 -> external-reading.
sensor-2 -> device-reading.
Quorum [github, external-reading, device-reading] => ELIGIBLE_FOR_FURTHER_VALIDATION (not certified), three source IDs.
Eight in-memory ledger records verify.

## Local artifacts
wag037.py and test_wag037.py created in working environment.
23/23 Python unittest tests passed. Tests cover transitive origins, mirrored sources, composite ancestors, shared-source aliasing, unknown/duplicate parents, cycles blocked by parent-first insertion, quorum deduplication, tamper detection, and rejected update atomicity.

## Limitations
Origin labels are asserted, not authenticated. Unlisted upstream dependencies may exist. Source-disjoint does not establish conditional statistical independence. Single-writer memory ledger with SHA-256 hash chaining cannot resist wholesale tampering or provide concurrent durability.

## WAG-038 — Conditional Independence Claims and Independent Validation
Jane must distinguish provenance independence from independence of errors conditional on event, time and environment. Register predeclared dependency hypotheses, test them on independent holdouts, preserve uncertainty, and never promote a statistical independence claim solely from a non-significant test result.
