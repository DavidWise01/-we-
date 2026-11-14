# WAG-043 — Post-Selection Replication and Effect Stability

Status: instantiated 2026-11-14, local reference implementation with 22/22 tests passing.

## Invariant
A dependency confirmed on a single holdout does not automatically generalize to other environments, generations, or circumstances. Freeze the selected witness subset, null model, statistical allowance and reference checkpoint before acquiring new replication evidence.

REPLICATED_STABLE => FROZEN_SOURCE AND DISTINCT_NEW_CONTEXTS AND VALID_PER_CONTEXT_CONFIRMATION AND EFFECT_STABILITY AND APPEND_ONLY_OBSERVATIONS.

## Executable reference
Local files: wag043.py and test_wag043.py. The Plan names exactly three witnesses, two or more distinct contexts, a preallocated family alpha, minimum per-context sample size and maximum observed effect spread. Trials identify packet, source root, context, generation and three binary bits. Reused packet/root IDs are rejected.

Predeclared confirmatory statistic is the one-sided exact Binomial(n, 1/2) tail for the XOR relation C=A XOR B. Each context is tested at alpha_replication / number_of_contexts (Bonferroni family budget). Do not substitute arbitrary dependence claims for the XOR null. A context with fewer than 16 observations yields HOLD. Observed effect spread above the predeclared bound yields CONTEXT_DIVERGENCE. Successful independent tests in each context with bounded effect spread yield REPLICATED_STABLE.

## Demonstration
Two new contexts Lab A and Lab B, separate generations 0 and 1, 32 synthetic observations each. Every observation follows C=A XOR B, so 32/32 parity matches in each context.
- One-sided exact per-context p = 2^-32 = 2.3283064365386963e-10.
- Family alpha 0.02; allocation 0.01 per context.
- Observed match-rate spread 0.00, below tolerance 0.20.
- Result REPLICATED_STABLE.
- 66 hash-linked in-memory ledger events, verification successful.

## Validation and limits
22/22 Python unittest tests passed locally. Tests cover stable replication, context divergence, underpowered/insufficient observations, unrelated fair parity samples, duplicate packets, reused source-root labels, illegal context/bit/generation, immutable closure, budget validation, exact p-values, atomic rejection and hash-history tampering.

The test assumes conditionally fair independent parity under each null, and independent new trials. Declared distinct roots are not authenticated provenance. The replicated pattern is not necessarily causal. Effect-spread tolerance has no confidence interval or full equivalence-testing guarantee. A memory hash chain is not durable, externally anchored storage.

## Next natural invariant — WAG-044: Replication Failure Localization and Context-Specific Quorum
When a replication passes in one context but fails in another, keep original certification intact, isolate the context difference, and require new context-specific evidence before promoting or revoking operational reliance. Never average away a failed replication by pooling contexts.
