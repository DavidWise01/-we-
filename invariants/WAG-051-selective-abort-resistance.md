# WAG-051 — Last-Revealer Bias and Abort Resistance

Status: instantiated November 14, 2026. The Python kernel was executed locally with 24/24 unittest cases passing. This turn updates docs/index.html with a self-contained embedded SVG visualization.

## Invariant
Valid cryptographic commitments do not guarantee unbiased usable randomness when a last contributor can selectively withhold a reveal.

COMMITMENT_INTEGRITY != ABORT_RESISTANT_RANDOMNESS

Any incomplete ceremony must terminate as ABORTED with explicit event lineage and no silent same-ceremony retry. Recovery creates a new round whose parent is the aborted round, retaining all original commitments and partial reveals.

## Reference algorithm
1. Open a uniquely identified round; optionally designate an aborted predecessor as recovery parent.
2. Collect at least three commitments bound to the round and contributor before the fixed cutoff.
3. Require distinct declared witness roots and failure domains; seal the round at the cutoff tick.
4. Reveal exact committed values only after cutoff.
5. If all reveal, produce a deterministic combined digest and mark COMPLETE.
6. If one or more withhold, mark ABORTED; preserve the list of missing revealers and disallow late reveals or repeated finalize.
7. A new recovery round receives a new identity and commitments; its parent must be a previously aborted round.
8. Preserve all events in a SHA-256 hash-linked in-memory ledger.

## Executed synthetic example
Three ceremony attempts: round 1 COMPLETE, round 2 ABORTED because C withheld, round 3 COMPLETE with parent round-2.
Descriptive observed abort fraction: 1/3 = 0.3333333333. This is NOT statistically calibrated evidence of malicious selective-abort bias. Local ledger: 27 events; verification true. Tests: 24/24 passed.

## Files
- docs/index.html — WAG-051 entry, embedded SVG panel, prior WAG entries preserved.
- invariants/wag051/wag051.py — executable Python reference uploaded.
- invariants/wag051/test_wag051.py — 24 automated tests uploaded.
- Separate locally generated JPG WAG-051-mesh.jpg available as a conversation download, but not GitHub binary. The diagram's decorative numerical claims about significance or a 0.5 abort rate were not produced by the test; use the verified 1/3 descriptive fraction.

## Limits
An abort-and-new-round policy preserves provenance, but does not prevent denial of service or guarantee unbiased outcomes conditional on completion. A malicious last revealer can censor unfavorable runs. True abort resistance requires an analyzed protocol, such as publicly verifiable threshold randomness or other guaranteed-output mechanism, independently authenticated contributors, and trusted timestamping. Witness root and domain strings are unverified declarations. The SHA-256 in-memory log is not durable tamper-resistant storage. The displayed synthetic outcome is not a deployed Jane system.

## WAG-052 — Abort-Censoring Quantification and Conditional Output Bias
Distinguish an honest dropout process from outcome-aware selective aborts. Predeclare a measurable target output statistic and withholding strategy; compare all committed trials, completed outputs, and the censored (aborted) set using an independently audited test and shared family error budget. Preserve the censoring mechanism and do not infer unbiased output merely from successful rounds.
