# WAG-040 — Higher-Order Witness Dependence and Joint Validation

Status: instantiated and executed locally, 2026-11-14. Python reference: 20/20 unittest tests passed.

## Invariant
PAIRWISE_INDEPENDENCE != JOINT_INDEPENDENCE

For three witness error indicators W1,W2,W3, compare the observed joint distribution with the product of the individual marginal distributions, in addition to checking all three pairs. A pairwise pass cannot certify a three-witness quorum.

## Deterministic example
W1, W2 are independent fair binary variables and W3=W1 XOR W2. Across 32 balanced synthetic observations all three pairwise empirical total-variation distances are 0, but joint TV(P123,P1*P2*P3)=0.5. Decision: HOLD_HIGHER_ORDER_DEPENDENCE. Ledger valid; 34 records.

## Reference implementation
Local artifacts:
- wag040.py: immutable Trial records, per-context three-witness screen, empirical total variation, replay prevention and SHA-256-linked audit
- test_wag040.py: 20 automated tests, all passing
Decisions: HOLD_INSUFFICIENT, HOLD_PAIRWISE_DEPENDENCE, HOLD_HIGHER_ORDER_DEPENDENCE, UNRESOLVED_NO_DEPENDENCE_DETECTED. No decision automatically certifies independence.

## Limits
Empirical TV on small samples is noisy; fixed thresholds lack explicit false-positive control and confidence intervals. Independent trial acquisition is assumed, not cryptographically verified. Pairwise roots must also pass WAG-037 ancestry and WAG-023 failure-domain checks. A no-dependence-detected decision is not proof of joint independence, and no causal mechanism is inferred from a dependency pattern. In-memory hash-linking is not durable tamper-proof storage.

## Next invariant — WAG-041: Higher-Order Interaction Locality
Detect which minimal subset of a growing witness cohort carries a higher-order dependency. Use predeclared subgroup search, independent holdouts and statistical multiplicity accounting; preserve counterexamples and do not relabel untested witnesses as independent.
