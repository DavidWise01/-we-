# WAG-061 — Independent Checkpoint Re-Certification and Anchored Quorum Trust

Status: instantiated 2026-11-15. Local Python reference executed 24/24 unittest checks successfully. HTML journal updated this turn.

## Invariant
RESTORE_TRUST => MONOTONIC_EXTENSION AND FRESH_INDEPENDENT_QUORUM AND AUTHENTICATED_ANCHOR AND NO_KNOWN_FORK

A reconstructed checkpoint must strictly extend the exact frozen history. It must collect at least three signatures from distinct declared source ancestries, operators and failure domains; each witness signs the same new head, and a separate signed anchor receipt must match that head. Current trust stays held when attestations or the anchor are absent, stale or invalid.

## Reference algorithm
- Freeze an ordered pre-partition history and SHA-256 commitment.
- Reconnect with a proposed full history. Reject shorter rollback, quarantine incompatible prefixes, and hold no-advance heads.
- Bind witness claims (identity, ancestry, operator, failure domain, new head digest, logical tick) into domain-separated Ed25519 signatures.
- Reject duplicate witness IDs, shared declared provenance, invalid signatures and stale attestations.
- Verify a separately signed anchor receipt over the same head digest, logical tick and claimed operator/domain.
- Certify only if at least three witnesses and the matching receipt are present within a predeclared five-tick freshness window.
- Append every accepted state transition to a hash-linked ledger without rewriting the frozen checkpoint or observed history.

## Executed synthetic demonstration
Frozen C0: [a,b,c].
Reconnected C1: [a,b,c,d].
Three locally generated Ed25519 witness keys attest at tick 12 with distinct declared roots and domains. Another local Ed25519 key signs an anchor receipt at tick 12. Certify at tick 13: RECERTIFIED_LOCAL_ANCHOR.
Eight hash-linked audit events verified. 24/24 local unit tests passed, covering good extension, rollback, fork, equal checkpoint, malformed signature, mismatched head, repeated witnesses, ancestry/operator/failure-domain overlap, missing quorum, missing anchor, stale evidence, duplicate anchor and tamper detection.

## Files
- docs/index.html — embedded SVG WAG-061 visual journal entry; all older entries preserved.
- invariants/wag061/wag061.py — executable Python reference kernel.
- invariants/wag061/test_wag061.py — 24 automated tests.
- WAG-061-mesh.jpg — separate conversation visual. Its displayed public TSA, N=40 metrics and certification labels are illustrative artwork rather than measurements or external attestations.

## Limitations
This verifier checks full disclosed history prefixes, not RFC6962 compact consistency proof verification, and is not connected to live WAG-058/059 services. Witness roots and failure domains are unverified labels. The anchor receipt is signed by a locally generated key and is not a genuinely independent timestamp authority or publicly anchored checkpoint. The code lacks durable, externally witnessed storage, authenticated operator identity, and live network observation. Its RECERTIFIED_LOCAL_ANCHOR result must not be promoted as production trust certification.

## Next natural invariant — WAG-062: Quorum Rotation and Revocation-Safe Continuity
When the witnessing set changes between generations, require an overlap or a separately authenticated bridging certificate linking old and new trust roots. Avoid trusting a fresh but unconnected witness cohort; preserve revocation timing and signatures so quorum rotation cannot reset evidence ancestry or launder a known fork.
