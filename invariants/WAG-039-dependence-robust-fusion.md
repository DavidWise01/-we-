# WAG-039 — Dependence-Robust Witness Fusion

Status: instantiated and tested 2026-11-14. Local Python kernel and 20/20 automated tests passed.

## Invariant
Correlated witness agreement cannot be counted as independent consensus. Exact matching observations, distinct declared roots, separate failure domains, and acceptable dependency screening are necessary but **not sufficient** for authoritative certification.

`FUSION_ELIGIBLE => EXACT_OBSERVATIONS AND DISTINCT_AUTHENTICATED_ROOTS AND DIVERSE_FAILURE_DOMAINS AND DEPENDENCE_SCREEN`

A pairwise low-correlation result does not imply joint conditional independence; any eligible result is still subject to independently verified checkpoint certification.

## Reference kernel
Python reference files: wag039.py and test_wag039.py. Quorum >=3. Witness fields include identity, observation ID, event, scope, method, value, source root and declared failure domains. An externally obtained, nonnegative upper bound for each unordered witness pair's absolute conditional error association is compared to a predeclared threshold.

Decisions:
- HOLD / insufficient quorum
- HOLD / shared root, unverified declared root, mismatch or shared failure domain
- HOLD / unknown pairwise dependence
- HOLD / dependence upper bound exceeds threshold
- ELIGIBLE_FOR_FURTHER_VALIDATION (never automatic certification)

## Executed synthetic reference
Three value=7 witnesses with separate root and failure-domain labels and all pairwise association upper bounds 0.10 against a 0.30 threshold: ELIGIBLE_FOR_FURTHER_VALIDATION. Changing a pair's bound to 0.80 returns HOLD. Missing pair bounds also returns HOLD. 20/20 local unittest tests passed.

## Limits
The reference does not estimate error-correlation bounds; it requires externally validated bounds. Witness-root and domain labels are claims, not source authentication. Pairwise independence does not ensure joint independence. Correlation bounds alone are not proof of a safe fusion rule. A hash-linked in-memory event log is not durable or externally anchored. The example is synthetic and not a deployed Jane system.

## Next natural invariant — WAG-040: Joint Dependence and Higher-Order Witness Interaction
Three witnesses can be pairwise independent yet exhibit a three-way dependency. Examine higher-order interactions using independent validation, prespecified models and adequately powered tests; when joint independence cannot be supported, preserve uncertainty rather than upgrading the quorum.
