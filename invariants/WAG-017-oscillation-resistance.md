# WAG-017 — Oscillation Resistance and Temporal Routing Stability

Status: instantiated reference boundary, 2026-11-13.

## Invariant
A neural route cannot flip due to noise alone. To switch routes, require independent verification, preserved capabilities, hysteresis improvement margin, and a minimum dwell interval.

SWITCH => authentic_independent_evidence AND checkpoint_valid AND capability_safe AND elapsed_ticks >= min_dwell AND measured_loss_improvement >= min_improvement.

Every accepted transition creates a new generation/version of routing state; the predecessor remains reconstructable.

## Reference implementation
Python state machine in local artifact wag017.py, ten tests passed. Its deterministic synthetic trace:
- tick 1: HOLD_DWELL
- tick 5: HOLD_HYSTERESIS
- tick 6: SWITCH_VERIFIED memory → timing
- tick 7: HOLD_DWELL
- tick 12: SWITCH_VERIFIED timing → memory

## Threat and limitations
Sampled metrics might be noisy or adversarial. Unique evidence-root IDs are not proof of independence; external attestations remain necessary. A fixed dwell time alone does not guarantee global stability. Per-task hysteresis should be calibrated on independent data and emergency safety shutdown must supersede normal dwell.

## Next target
WAG-018 — Stability Across Multiple Timescales: fast local plasticity, medium-term route selection, slow generation promotion; keep temporal state and source provenance separate.
