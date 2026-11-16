# WAG-083 — Three-Anchor Recovery Quorums and Conflicting-Anchor Quarantine

Date: 2026-11-16.

## Invariant

A locally durable checkpoint is not independently confirmed until three separately signed anchor records agree on the exact epoch, root, and fresh challenge, and each signature verifies under the registered key for its declared host. Three simulated store directories are **not** real off-host failure independence.

`RECOVERY_ELIGIBLE = 3/3 VALID_SIGNATURES ∧ 3/3 MATCHING_HEADS ∧ FRESH_CHALLENGE ∧ LOCAL_HEAD_MATCH`

## Synthetic demonstration

- Start epoch 83 / ROOT A in the local checkpoint and three anchor stores; valid signatures from W1, W2, W3 and three distinct declared ancestry/failure domains -> `LOCAL_RECOVERY_ELIGIBLE`.
- Re-sign anchor W3 at epoch 83 / ROOT B -> `QUARANTINE_CONFLICT`.
- Restore signed W3 anchor at ROOT A -> `LOCAL_RECOVERY_ELIGIBLE`.
- Four hash-linked in-memory audit entries verify.

## Negative decisions

- Missing/invalid signature/invalid identity: `HOLD_ANCHOR_INCOMPLETE`.
- Nonmatching signed heads: `QUARANTINE_CONFLICT`.
- Agreed heads with stale challenge: `HOLD_STALE_CHALLENGE`.
- All anchors ahead of local store: `HOLD_ANCHOR_AHEAD`.
- Local store ahead of all anchors: `HOLD_LOCAL_AHEAD`.
- Same epoch but different all-agreed anchor root: `QUARANTINE_ROOT_FORK`.

## Local test status

36/36 Python unittest tests passed using locally generated Ed25519 keys. Tampered signatures and forged identity attributes are rejected. Host directories are local and only *represent* storage separation; no remote host or GitHub Actions CI run is verified. The engine models a recovery gate, **not** Byzantine agreement, global transparency, or off-host durability. Exact key-independent provenance is outside the model. Anchors are atomic-replaced on a local filesystem but the recovery audit is currently in memory.

## Artifacts

- `invariants/wag083/wag083.py`
- `invariants/wag083/test_wag083.py`
- `invariants/wag083/WAG-083-ascii.txt`
- `docs/index.html` includes the ASCII art.

## Next natural invariant: WAG-084 — Authenticated Off-Host Delivery Receipts

Require actual independent network endpoint acknowledgments, authentic endpoint challenge response, durable write receipt, and independent fault-domain evidence; fail closed on partial acknowledgments, witness aliasing, and replayed delivery receipts. Do not describe logical directory isolation as off-host resilience.