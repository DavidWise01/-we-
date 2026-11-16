# WAG-077 — Signed Registry Transparency, Revocation Lineage, Split-View Detection

Date: 2026-11-15. Local Python reference: **51 / 51 tests passed**.

## Goal

A valid signature over an ancestry claim does not establish current validity or a single coherent global registry history. Keep historical revocations, identify contradictory signed registry states, and require agreement between three named observing witnesses before local ancestry eligibility.

## Model

- Domain-separated Ed25519 signatures bind registry identity, log size, and SHA-256 digest of the selected prefix of an append-only registry history.
- Each event carries sequence, previous-event hash, event kind, subject, controller, epoch, and parent label.
- Three local witness observations must match the registry's complete currently supplied history before a candidate can be marked `LOCAL_DECLARED_ANCESTRY_ACCEPTED`.
- An explicit revocation transitions `ACTIVE` to `REVOKED`, while a historical query to the prior prefix remains `ACTIVE`.
- Two valid signed log heads with the same registry and size but different roots cause `QUARANTINE_SPLIT_VIEW`; a signed head rollback causes `HOLD_ROLLBACK`.
- Invalid signatures, unknown registries, stale observations, missing witnesses, malformed events, log tampering, and invalid prefixes fail closed.

## Tested scenarios

The demo registers `W4` under declared controller `org-w`, receives three matching signed-head observations, and accepts the local declaration. A later revocation is appended, three fresh observations are recorded, and the decision becomes `HOLD_REVOKED`. The demo preserves six verified audit entries. Additional adversarial tests synthesize two signed same-sized heads from a single registry key over mutually incompatible histories, and detect the conflicting witnessed views.

## Important limitations

The hash is a digest of the *entire prefix*, not a Merkle tree; the reference does not implement logarithmic consistency proofs. Matching heads from three named local witnesses do not prove independent external witnesses or global transparency. A signed head by an authorized key may still attest to false data. This is a deterministic cryptographic simulation, not live public registry integration, distributed Byzantine agreement, or anchored immutable storage. The runtime event log is in memory; hash chaining alone does not prevent its owner from rewriting history and recomputing hashes. A signed current head should eventually be externally anchored and cross-checked for actual anti-equivocation guarantees.

## Files

- `invariants/wag077/wag077.py` — executable Ed25519 signed-head and audit reference.
- `invariants/wag077/test_wag077.py` — 51 automated local cases.
- `invariants/wag077/WAG-077-ascii.txt` — pure text image, embedded in `docs/index.html`.

## Next natural bound — WAG-078

**Signed prefix consistency and external observer continuity.** Verify that a newer signed head extends the previously witnessed prefix without silently replacing older claims; use reproducible consistency proofs and independent observers rather than matching current heads alone. Preserve fork proofs as paired signed histories.

`{{ preserve [register -> witness -> compare -> revoke -> verify] }}`