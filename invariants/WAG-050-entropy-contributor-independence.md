# WAG-050 — Entropy Contributor Independence and Bias Resistance

Status: instantiated November 14, 2026. Local reference Python: 24/24 unittest cases passed. HTML illustration appended this turn.

## Invariant
THREE_ENTROPY_SOURCES != THREE_INDEPENDENT_TRUST_DOMAINS

A multi-party entropy ceremony may advance only when each source declares distinct provenance origin, operator, infrastructure, and failure domain; commits before cutoff; and reveals a matching secret afterward. Withheld reveals abort the entire ceremony rather than allowing cherry-picked retries.

## Reference algorithm
- Immutable protocol ID, minimum three contributors, cutoff tick, and ABORT_NO_RETRY policy.
- Contributions contain name, origin, operator, infrastructure, failure domain, and SHA-256 commitment bound to protocol.
- Seal only after at least three commitments at the exact cutoff; compare the four declared domain categories.
- Shared declared domain => HOLD_SHARED_DOMAIN.
- Reveal matching 64-character hexadecimal secret only after cutoff.
- Complete reveals => ELIGIBLE_FOR_EXTERNAL_VERIFICATION; missing reveal => ABORT_WITHHELD_REVEAL.
- Combine complete contributions in canonical source order using domain-separated SHA-256.
- Preserve all events in a hash-linked history.

## Executed synthetic cases
1. Distinct declared domains, all revealed => ELIGIBLE_FOR_EXTERNAL_VERIFICATION; 10 records, verified chain.
2. Shared failure domain => HOLD_SHARED_DOMAIN; 6 records.
3. Withheld reveal => ABORT_WITHHELD_REVEAL; original evidence retained.
24/24 local unittest tests pass, checking shared origin/operator/infrastructure/failure domain, wrong/early/duplicate reveals, cutoff, no-retry and tampering.

## Artifacts
- docs/index.html — WAG-050 embedded SVG illustration, earlier journal entries preserved.
- invariants/wag050/wag050.py — executable reference.
- invariants/wag050/test_wag050.py — 24-case test suite.
- WAG-050-mesh.jpg — generated conversation visual, not GitHub binary; Git HTML has a self-contained SVG drawing.

## Limits
Distinct domain strings are self-declared, not proof of independent control, high-quality entropy or protection from collusion. A hash of arbitrary controlled inputs does not demonstrate adequate min-entropy. The ceremony uses synthetic deterministic secrets, logical ticks rather than trusted time, and an in-memory hash-linked ledger rather than durable externally anchored storage. A last revealer can still selectively abort after observing other contributions: ABORT_NO_RETRY blocks silent acceptance but does not remove denial of service or selective-abort bias. Real security requires authenticated sources, trusted timestamps, independent audit and an analyzed randomness-extraction protocol.

The decorative JPG includes speculative entropy and contributor metrics. They were not measured and are not evidence. The tested code and SVG panel describe the actual reference behavior.

## Next: WAG-051 — Last-Revealer Bias and Abort Resistance
Independently attest the commit/reveal rounds or adopt an analyzed threshold randomness beacon. Explicitly distinguish unbiased output conditional on completion from selective abort bias and denial of service, preserve aborted histories, and verify adaptive-withholding behavior against a stated adversary model.
