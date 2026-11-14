# WAG-042 — Selection-Aware Evidence Validation and Global Error Conservation

Status: locally instantiated and tested November 14, 2026. 22/22 Python unit tests passed.

## Invariant
A large discovery search must not count a selected positive result as if it were the only hypothesis examined. Freeze the selected subset and experimental plan, then conduct one separately registered confirmatory test on fresh holdout evidence. Charge the new test to the existing hive-wide alpha budget; do not reset allocations when agents repartition or spawn.

`CONFIRM => FROZEN_SELECTION AND PRIOR_ALPHA_REGISTRATION AND DISJOINT_HOLDOUT AND VALID_PVALUE AND APPEND_ONLY_PROVENANCE`

## Reference implementation
Local Python artifacts:
- wag042.py, SHA-256 01b5ebaef0b5cdd8e3174629a523005746bb0cebce5962d48c65b5ca3a533e4b
- test_wag042.py, SHA-256 f4ecd1b5eba3e97e4271085140d2a543eddcc9cf90af3de12f7dab7d08d0ce0c
- 22/22 unittest tests executed and passed.

The implementation searches bounded 3-witness subsets using discovery-only XOR parity matches, freezes the discovered subset in a content-hashed registration, and charges a Decimal alpha to a family budget. Holdout observations can only be ingested after registration, and packet/root identifiers cannot be reused. The confirmatory statistic is an exact one-sided Binomial(n, 1/2) tail on XOR parity matches in the preregistered triple. Its validity requires independent holdout trials and a fair independent third-bit null conditional on the other two bits. This statistic is not a universal test of joint independence.

## Synthetic demonstration
- Four witnesses A/B/C/D; C=A XOR B; D unrelated.
- 32 discovery observations and a separate 32-observation holdout.
- Frozen selected triple A/B/C.
- Alpha family 0.05; confirmatory allocation 0.02; remaining 0.03.
- 32/32 parity matches on holdout, p=2^-32=2.3283064365386962890625e-10.
- Decision DEPENDENCE_SUPPORTED under the stated null; 67 hash-linked audit events; ledger verifies.

## Limits
Discovery candidate scores are not calibrated p-values. Only a single selected confirmatory test is charged here; additional tests must be registered and budgeted. Unique root labels do not prove independently acquired evidence or independence of trials. The in-memory SHA-256 chain does not provide authenticated, durable storage. No real Jane agent or deployed service was changed.

## Next — WAG-043: Post-Selection Replication and Effect Stability
A dependency supported in one confirmatory holdout should be retested under independently acquired contexts and generations. Freeze the detected relation and its effect size, allocate a new non-recycled confirmatory budget, and check whether the effect remains stable without counting original discovery or holdout records as new evidence.
