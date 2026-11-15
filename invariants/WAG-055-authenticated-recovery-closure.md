# WAG-055 — Authenticated Recovery and Durable Closure

Date: 2026-11-15. Local WAG-055 reference implementation passed 24/24 tests.

## Invariant
TRUSTED_CLOSURE => VALID_SIGNATURES AND NONREVOKED_IDENTITIES AND DISJOINT_WITNESS_ROOTS AND DISJOINT_FAILURE_DOMAINS AND VERIFIED_RECOVERY_LINEAGE AND VERIFIED_EXTERNAL_ANCHOR.

Three signatures on the same commitment must come from distinct authenticated identities and source roots. An externally anchored certificate cannot be inferred from an unverified receipt or locally computed hash.

## Reference implementation
- Python Ed25519 signature checking through the cryptography library.
- Canonical JSON bytes sign a domain-separated WAG-055:v1 checkpoint payload.
- Exactly three distinct signers with unique declared source roots and failure-domain labels.
- Reject malformed signatures, unknown or revoked identities, changed checkpoint contents, duplicate attestations, common roots or domains.
- Hold when no externally verifiable anchor receipt or verification function is provided. A matching digest string alone is insufficient.
- Preserve append-only hash-linked historical records and immutable-looking certification details, retaining C0 as the parent of C1.

## Executed local fixture
24/24 Python unittest tests passed. A synthetic three-signer example with freshly generated Ed25519 keys and MOCK-NOT-EXTERNAL anchor receipt returned CERTIFIED under the mock verifier, producing 2 valid hash-linked records. Crucially, this is **not a real externally anchored certificate**. The status means the mock-verifier interface returned true, not that GitHub, 0root.ai, a trusted timestamp authority or an external registry anchored it.

## Artwork and HTML
docs/index.html now includes WAG-055 embedded SVG, preserving WAG-044 through WAG-054. The separately generated WAG-055 JPG illustrates architecture only; its external anchors, identities, registry status and operational metrics are not real attestations or measured results.

## Production limitations
The trust registry and revocation flags are inputs, not verified remotely. This is a memory-resident single-writer reference, not a durable cryptographically witnessed archive. Authenticated timestamps and signed anchor receipts from separate authorities are not integrated. Root/domain diversity is asserted metadata, not proof of independent real-world ownership. A mock anchor must never be promoted as external evidence.

## WAG-056 — Anchor Transparency and Revocation-Aware Trust
Require externally retrievable timestamped anchor receipts and append-only transparency consistency proofs. Query current revocation state independently before operational reliance; preserve prior historical certificates while suspending trust in a compromised signer or anchor. Integrate multiple genuinely independent anchors, not mirrored references.
