# WAG-221 — Independent acquisition and shared-root detection
.dlw

Two 192-slot binary observation streams measure the SAME synthetic target. Acquisition ancestry is separate: a common physical target need not make two acquisition channels the same witness, but a copied feed or common upstream sensor does. Six challenge families × four periods × eight seeds = 192 fixtures (36864 paired slot comparisons). Two channels are treated as corroborating only if acquisition-root sets have EMPTY intersection and observed agreement is >=0.96. Disagreement or shared lineage is never counted as two independent confirming witnesses.

independent_clean: independent 32, shared 0, disagree 0, incorrect 0, self-reported-qualified 32
shared_copy: independent 0, shared 32, disagree 0, incorrect 0, self-reported-qualified 0
shared_corruption: independent 0, shared 32, disagree 0, incorrect 0, self-reported-qualified 0
independent_disagree: independent 0, shared 0, disagree 32, incorrect 0, self-reported-qualified 0
shared_upstream: independent 0, shared 32, disagree 0, incorrect 0, self-reported-qualified 0
forged_distinct: independent 0, shared 32, disagree 0, incorrect 0, self-reported-qualified 32

The forged-distinct claim passes the self-reported root check in 32/32 constructed examples, but the fixture registry catches shared ancestry in all 32. This is **not proof of authentication**: the true root sets are injected by the test harness. A malicious upstream provider could deceive the real lineage store. The two independent-clean channels are deliberately seeded apart but both measure one generated target; they are distinct acquisition streams only by construction. The shared-upstream and shared-corruption fixtures encode a declared shared root. No real sensor, cryptographic signature, physical measurement, runtime benchmark or independent data provenance is demonstrated.

Next WAG-222: lineage challenges with unverifiable roots, aliases, provenance graph traversal, and abstention when authenticated ancestry cannot be established.
