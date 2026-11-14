# WAG-044 — Context-Specific Quorum and Replication Failure Localization

Status: instantiated November 14, 2026. Local Python tests: 22/22 passing.

## Invariant
Replication success in one context must not overwrite or invalidate original evidence or falsely establish generality in another context.

`LOCAL_SUPPORT(A) AND LOCAL_HOLD(B) => PRESERVE(A,B) AND SCOPE_RELIANCE(A) AND SUSPEND_GENERALIZATION(B)`

## Protocol
Freeze the witness relation and original experiment. Collect new context-specific observations with separate packet and claimed origin-root identifiers. Evaluate each context separately and preserve each raw observation before making a scoped decision. Never pool a failed context into a succeeding context to hide local failures.

A local hold can become only a revalidation candidate after a fresh, separately labeled retest, not automatic certification. A contextual difference remains a hypothesis requiring independently designed intervention to identify causality.

## Synthetic reference
Frozen XOR relation C=A XOR B. Lab A has 12/12 parity matches; Lab B has 6/12. Three declared witnesses in each laboratory. The fixed reference gate labels Lab A LOCAL_SUPPORT and Lab B LOCAL_HOLD; 24 observations and 2 evaluations produce 26 hash-linked records. Original observations are preserved.

## Tests and artifacts
Local artifacts wag044.py and test_wag044.py, 22/22 unittest checks passed. Cases cover scoped support/hold, absent contexts, insufficient samples and witness count, fresh retest, replay rejection, root ID reuse, malformed bits, invalid phase, unchanged history, and tamper detection. JPG visualization generated at WAG-044-mesh.jpg.

## Limits
The parity-rate thresholds are an illustrative deterministic screen, not calibrated p-values. Root identifiers and witness labels are not authenticated or proof of genuine independence. An in-memory hash chain is not durable tamper-proof evidence storage. No real-world causal boundary is claimed.

## Next: WAG-045 — Context Difference Minimization
Enumerate candidate context features using discovery data only; freeze a minimal explanatory feature set; validate its predictive separation on independent holdout evidence and then use controlled tests before making causal claims. Preserve exceptions and selection budgets.
