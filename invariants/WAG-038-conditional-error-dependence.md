# WAG-038 — Conditional Error Dependence and Statistical Independence Auditing

Status: instantiated and locally tested on 2026-11-14. 20/20 Python unittest tests passed.

## Invariant
Separate, transitive evidence ancestry does not imply statistically independent measurement errors. Condition comparisons on event and observation context; test for dependence, preserve unresolved results, and never assert independence solely because a test is nonsignificant.

SOURCE_INDEPENDENCE(A,B) != CONDITIONAL_ERROR_INDEPENDENCE(A,B | CONTEXT)

## Reference kernel
Local reference Python: wag038.py and test_wag038.py. Each paired trial stores packet ID, context, two distinct claimed source roots, binary error indicators, and a separate reference ID. Reused packet IDs or reference IDs fail. Trial and audit records are appended to a SHA-256-linked event history.

For every declared context, compute the binary phi association coefficient. With sufficient observations and nonconstant margins, flag dependence when abs(phi) > tolerance (default 0.2). Otherwise an illustrative Fisher-z approximate upper bound on abs(phi) is compared with the same tolerance. If the bound is not below the tolerance, decision is UNRESOLVED, not independent. Constant margins are unresolved. Perfect positive/negative association is a dependence flag.

## Demonstration
16 synthetic paired observations in calibration=old, with two sensors making matching errors.
Phi = +1.000; decision DEPENDENCE_FLAG. Hash chain verifies.
20/20 tests passed covering correct detection, insufficient data, replay, reused independent reference, root-label collision, invalid binary measurements, constant margins, ambiguous low sample association, multi-context separation, policy checks, and hash-chain tampering.

## Important limits
Distinct root labels and reference IDs do not establish true independence or accurate ground truth. Fisher-z intervals are not generally calibrated confidence intervals for sparse binary phi coefficients, and independent-trial assumptions may fail. The implemented screening classification is a heuristic, not certification of conditional independence or a controlled Type I error procedure. Context must be specified before analysis to avoid selection bias. In-memory hash chains are not durable trusted storage.

## Next invariant — WAG-039: Dependence-Robust Witness Fusion
When witness errors are correlated, avoid treating every agreeing witness as a full independent vote. Develop a dependency-aware aggregation rule with verified provenance and conservative uncertainty. In particular, retain the hard three-independent-witness gate when certification requires it; correlated witnesses may inform but cannot replace genuine independent quorum.
