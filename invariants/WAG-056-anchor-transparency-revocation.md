# WAG-056 — Anchor Transparency and Revocation-Aware Operational Trust

Status: locally instantiated and executed on 2026-11-15. Python reference: 24/24 unittest checks passed. docs/index.html updated with WAG-056 embedded SVG visual.

## Invariant
HISTORICAL_CERTIFICATION != CURRENT_OPERATIONAL_TRUST

CURRENT_TRUST(C,t) => VALID_HISTORICAL_SEAL(C) AND CURRENT_VALID_SIGNER(C,t) AND CURRENT_ANCHOR_QUORUM(C,t)

Never overwrite or delete a historical certificate because its signer or anchor becomes compromised later. Instead, append a time-scoped revocation and suspend operational reliance for affected epochs.

## Reference implementation
- Canonical SHA-256 checkpoint digest with domain-separated Merkle leaf and internal node hashing.
- Explicit Merkle inclusion proof path with left/right sibling hashing, verified against each anchor root.
- Ed25519 anchor receipt signatures over the anchor identifier, certificate digest, Merkle root and logical epoch.
- At least three signed receipts with distinct DECLARED operators and failure domains.
- Issue one historical certificate, then append time-scoped signer/anchor revocations, never retroactively changing its issuance record.
- Current status: CURRENT, HOLD_REVOKED_SIGNER or HOLD_ANCHOR_QUORUM, with SEALED_AT_ISSUANCE preserved.
- SHA-256 linked single-writer in-memory event chain with tamper-detection verification.

## Executed synthetic result
Locally generate three Ed25519 anchor keypairs at logical epoch 10, sign three Merkle inclusion receipts, issue certificate C1, check at epoch 11: CURRENT with three active anchors.
Append synthetic signer S2 revocation at epoch 12; check at epoch 13: HOLD_REVOKED_SIGNER with historical certificate SEALED_AT_ISSUANCE.
Six hash-linked records verified, 24/24 automated tests passed.

## Tests and limitations
Checks include valid signatures, tampering, malformed public keys, bad inclusion roots, Merkle sibling ordering, shared operator/failure domain claims, insufficient anchors, duplicate issuance, unknown/duplicate revocations, revocation predating the anchor, correct historical snapshot behavior and atomic rejection.

IMPORTANT: The anchors and their Ed25519 keys are generated locally in this demonstration. Their identity, independence, timestamps, publication and durable persistence are not externally attested. A locally signed root is not a verified public transparency checkpoint. Declared operators and domains are not authenticated. This reference does not verify consistency across successive public transparency tree heads or detect split-view attacks, and an in-memory hash chain lacks durable external anchoring. The generated WAG-056 JPG includes conceptual trust scores, identities and numerical histories that were not experimentally measured. The HTML has an embedded SVG architectural drawing rather than the original JPG binary.

## Next natural invariant — WAG-057: Transparency Consistency and Split-View Detection
Separate witnesses may obtain individually valid signed transparency roots that disagree about the same log epoch. Verify append-only consistency proofs across tree sizes, independently gossip and compare signed heads, identify equivocation/split views, and quarantine operational trust while preserving every conflicting signed view as evidence.
