# WAG-068 — Recursive Failure-Domain Hypergraphs and Cascade Cuts

Status: November 15, 2026. The Python reference and 34/34 local unittest tests passed.

## Invariant
DISTINCT_WITNESS_ANCESTORS != DISTINCT_FAILURE_PATHS.

A shared upstream infrastructure dependency propagates failure to every downstream component whose required prerequisite fails. This reference implements any-prerequisite failure semantics on a parent-first directed acyclic dependency graph; each dependent node may list multiple parents (a directed hypergraph-like dependency model).

## Synthetic experiment
Three witness ancestors A, B, C are declared distinct. W1 depends on router-a, network-x and power-y; W2 depends on router-b, network-x and power-y; W3 depends on router-c, network-z and power-z. Each router also has a separate host dependency.

Failing power-y disables network-x, router-a, router-b, W1 and W2. W3 survives, but the strict three-witness quorum is held. There are five inclusion-minimal quorum-loss singleton cuts (host-a, host-b, host-c, power-y, power-z), and four inclusion-minimal all-witness cuts: (host-c,power-y), (power-y,power-z), (host-a,host-b,host-c), and (host-a,host-b,power-z). The minimum all-witness cut has size two.

The demonstration produces 15 valid SHA-256 hash-linked records: policy, 13 nodes and one failure event.

## Validation
34/34 local tests passed, covering recursive propagation, common-cause paths, minimal cuts, quorum failure, all-witness loss, declared ancestor preservation, unknown/cyclic parents, duplicate identities, bounded search, tamper detection and rejection atomicity.

## Artifacts
- invariants/wag068/wag068.py: Python reference kernel
- invariants/wag068/test_wag068.py: 34 regression tests
- invariants/wag068/WAG-068-ascii.txt: ASCII topology picture
- docs/index.html: HTML journal embedding ASCII picture

## Limits
The dependency graph and witness provenance are declared synthetic inputs, not authenticated physical infrastructure. The reference models deterministic failures, not probabilities or statistical dependence, and cannot prove Byzantine agreement. Enumerating domain cut combinations is exponential in the worst case and bounded by max_cut_size; no result beyond the search bound is implied. Source hashes in a local memory chain are not externally anchored.

## Next WAG-069 — Repair Order, Recovery Dependency Graph and Fresh Revalidation
Recover prerequisite domains in dependency order, require fresh attestation from any affected witness, preserve the original outage and ensure repaired availability is never confused with restored certification.