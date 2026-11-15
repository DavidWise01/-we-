# WAG-052 — Selective-Abort Censoring and Conditional Output Bias

Status: instantiated and tested 2026-11-14. 24/24 local Python unittest cases passed. HTML visual journal updated and executable Python files committed.

## Invariant
P(Y | completed) need not equal P(Y) over all committed attempts. Never silently exclude aborted ceremonies from the denominator, and never impute unobserved aborted outcomes as verified facts.

## Reference design
Every attempted ceremony stores a unique attempt ID, claimed root, monotonic tick, completion flag, outcome when known, and a reason if aborted. Completed outcomes must be known; aborted outcomes may be explicitly unknown. Attempts and decisions are appended to a SHA-256 hash-linked in-memory event chain. Repeat IDs, root reuse, stale ticks, invalid binary labels and post-evaluation additions are rejected.

If every aborted outcome is actually available, construct the completed-versus-aborted 2x2 table and calculate the two-sided Fisher exact probability-ordering p-value. A result p<=predeclared alpha is a SELECTION_ASSOCIATION_FLAG, not a demonstrated cause. If outcomes are unknown, report the sharp trivial bounds [known_success/n, (known_success+unknown_abort_count)/n] on the overall success rate and return UNRESOLVED_MISSING_OUTCOMES.

## Executed synthetic example
30 attempts: completed 20 with 16 successes, aborted 10 with 1 success.
- Completed success rate: 0.8
- Aborted success rate: 0.1
- Overall rate: 17/30 = 0.5666666667
- Difference completed minus aborted: 0.7
- Fisher exact two-sided p = 0.00041407867494824016
- Decision: SELECTION_ASSOCIATION_FLAG
- 32 hash-linked records verified; 24/24 Python unit tests passed.

## Evidence provenance and limitations
The demonstration deliberately supplies potential outcomes even for aborted attempts. In real aborts these outcomes may not exist or may be unknowable; selection-bias estimates are then only partially identified. The p-value is valid under the tested fixed-margin contingency null and appropriate independent observation assumptions, which are not authenticated by the reference. A completion-outcome association does not by itself show intentional manipulation. Root strings are not cryptographically authenticated; a memory hash chain is not immutable durable storage.

## GitHub HTML and JPG
docs/index.html now contains WAG-044 through WAG-052 illustrated SVG panels, including the WAG-052 corrected exact p-value. The original WAG-052-mesh.jpg generated art is a conversation artifact, not a binary committed to GitHub. Its decorative p-value is inconsistent with the actual synthetic test; use the HTML and this specification for correct figures.

## Next natural invariant — WAG-053: Censoring-Robust Randomness and Recovery Design
Design protocols that prevent accepted samples being selected by a last revealer. Freeze abort criteria, log all noncompleted attempts, avoid reroll-on-unfavorable-output, and use an externally audited threshold or publicly verifiable recovery source under a predeclared fallback. Separate availability/denial-of-service guarantees from output-unbias guarantees and test them under a stated adversarial model.
