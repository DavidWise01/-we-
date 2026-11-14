# WAG-035 — Cross-Family Hypothesis Lineage and Budget Conservation

Status: instantiated and locally tested on 2026-11-14. 20/20 unittest checks passed.

## Invariant
A new label, family, or agent identity cannot open a second confirmatory budget allocation for a hypothesis with the same canonical semantic identity.

`NEW_LABEL != NEW_CLAIM != NEW_BUDGET`

Each claim records an ID, human-readable statement, externally curated canonical identity, family, and optional parent claim. A second claim with an already registered identity becomes an alias of the first claim. Registration resolves aliases before spending Decimal budget and rejects a second confirmatory registration for the same canonical claim. Distinct claims can receive separate allocations, subject to the same hive-wide budget cap.

## Synthetic demonstration
Family sensors: claim h1 identity calibration:joint_error.
Family operations: renamed claim h2 with same identity.
Initial budget 0.05. Register h1 for 0.02. Register h2 for 0.02 is rejected as duplicate. Remaining budget 0.03.
Append-only hash-linked ledger checks pass.

## Local artifacts and validation
- wag035.py (122 lines; SHA-256 bbeb776d487371616ccd4a0520d6dfc626030ddc7646c127db5e602c46a50719)
- test_wag035.py (69 lines; SHA-256 57830634a5e2a9f026a5c4e9d7ab744093128fb772d763ae55586af2085075a2)
- 20/20 tests ran successfully: canonical aliasing, no additional budget on renaming, exact budget, invalid values, missing snapshots, duplicate tests, unknown parents, atomic rejection and ledger tamper detection.

## Limitations
Canonical semantic identities are caller-supplied in this reference; no natural-language entailment or equivalence is proven. A true production registry must handle partially overlapping or hierarchically related hypotheses and have human or independently verified semantic review. Reusing one confirmatory-test identity is a conservative policy and is not a ban on properly prespecified new confirmatory studies with freshly budgeted error. A memory-resident hash-linked ledger is not tamper-proof persistence.

## Next — WAG-036: Hypothesis Equivalence and Partial-Overlap Graph
Claims can overlap without being identical. Build a directed relationship graph (equivalent, entails, overlaps, disjoint) with cited evidence, abstain on ambiguity, and prevent double-counting any shared confirmatory test or ancestry without incorrectly merging genuinely distinct questions.
