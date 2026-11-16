# WAG-078 — Signed Prefix Continuity and Historical Preservation

Date: 2026-11-15.

## Invariant

NEW_SIGNED_HEAD != PROOF_OF_APPEND_ONLY_HISTORY.

Jane freezes an earlier signed head and exact sequence of records. Every candidate head must be Ed25519 signed by its registry, bound to a later epoch, and match the submitted events. Those events must include the original frozen history as their **exact unchanged prefix**, not merely carry a different valid signature.

## Verification and results

The full local Python implementation passed **36/36** Python unittest cases. Honest [A,B,C] -> [A,B,C,D] (epoch 7 -> 8) passes with three independently labelled signed observer votes. A correctly registry-signed [A,X,C,D] (epoch 9) is quarantined for rewriting the prefix. Demo audit: 4 hash-linked events, integrity verified.

No missing or duplicate observers; signer payloads are domain-separated and bind original root, new root, size and epoch. Reject forged signatures, wrong event data, rollback, and old epoch replays. Historical rejection evidence is preserved.

## Visuals and source

- docs/index.html — embedded ASCII text chapter.
- invariants/wag078/WAG-078-ascii.txt — text illustration.
- invariants/wag078/wag078.py — compact GitHub reference kernel.
- invariants/wag078/test_wag078.py — GitHub regression tests.
- Local full source and 36-case tests are delivered as conversation attachments.

## Honesty boundary

The algorithm uses **complete frozen sequence comparison**, not a logarithmic Merkle consistency proof. The signed roots are local test fixtures. The ancestor labels are declared, not externally authenticated. The audit chain is in memory and not externally anchored. The GitHub code is a compact reference authored separately from the 36-case local suite; it is not represented as CI-tested.

## Next: WAG-079 — Compact Merkle Consistency Proof and Observer Freshness

Replace full-snapshot comparison with cryptographic proof of append-only prefix consistency, preserve exact hash context, and establish freshness of all independent observer endorsements before updating a frozen checkpoint.
