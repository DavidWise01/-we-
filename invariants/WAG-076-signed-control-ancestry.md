# WAG-076 — Signed Control-Ancestry Assertions and Unknown-Root Holds

Date: 2026-11-15. Full local implementation: **43/43 tests passed**.

## Invariant
A replacement witness W4 cannot be admitted merely because it claims a new key, root or parent organization. Two separately declared registry operators must provide Ed25519-signed control-parent assertions scoped to the exact witness, recovery epoch, and nonce. The signed canonical JSON is domain-separated by version.

Two matching signed non-excluded parents -> `ELIGIBLE_DECLARED_ANCESTRY`, **not** final witness certification.
One signer -> `HOLD_INSUFFICIENT_REGISTRIES`.
Different signed parents -> `HOLD_REGISTRY_CONFLICT`.
Same registry signing two parents -> `QUARANTINE_EQUIVOCATION`.
Agreement on excluded controller -> `HOLD_COMPROMISED_ANCESTRY`.
Forged, unknown, stale, mismatched or empty ancestry -> reject without appending.

## Recorded synthetic experiment
Both test registries sign W4 -> ORG-W at epoch 2 for the same nonce: eligible declared ancestry. Conflicting signed W4 -> ORG-W versus W4 -> ORG-X: hold and preserve both signed claims. Each scenario produces four verified hash-linked audit records (genesis, two signed claims, freeze). Tests include replay, tampering, equivocation and duplicate declared operator/root/domain/key identities.

## Evidence boundaries
The public keys are locally generated test keys. Registry independence is self-declared, not externally proved. These signatures authenticate test key possession and an assertion; they do not establish the truth of a controlling-organization claim. A colluding pair of registries could agree on a lie. The hash chain is in memory and not anchored to an external ledger. This is not a Byzantine consensus proof.

## Implementation
- `invariants/wag076/wag076.py`: GitHub compact reference model.
- `invariants/wag076/test_wag076.py`: GitHub reference checks.
- `invariants/wag076/WAG-076-ascii.txt`: text visualization.
- `docs/index.html`: inline ASCII journal art.
- The full 43-case locally tested implementation and test suite are included as conversation artifacts.

## Next — WAG-077
Add externally verifiable registry enrollment, signed revocation lineage, independently witnessed append-only checkpoints and unknown-root holds before actual witness replacement.