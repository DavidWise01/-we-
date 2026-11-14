# WAG-018 — Multiscale Temporal Homeostasis

Status: instantiated and locally tested (2026-11-14).
Kernel reference: `wag018.py`; test suite: `test_wag018.py`; 16/16 passing locally.

## Invariant
Fast synaptic proposals cannot directly change routing or generation authority. Medium route changes need dwell time, gain and independent evidence. Slow generation promotion requires its own longer dwell, meaningful improvement, and global capability/resource checks.

`T_synapse < T_route < T_generation`

## Reference policy
- Route minimum dwell: 4 logical ticks
- Generation minimum dwell: 12 logical ticks
- Route improvement threshold: 0.03
- Generation improvement threshold: 0.05
- Maximum protected regression: 0.02
- Maximum synthetic energy: 9.0
- Minimum declared distinct witness roots: 3 (not cryptographically authenticated)
- All proposals, holds, and accepted transitions are hash-linked, append-only records.

## Deterministic example
| Tick | Requested action | Result |
|---|---|---|
| 1 | Synapse proposal | PROPOSE_ONLY |
| 2 | Route to timing | HOLD_ROUTE_DWELL |
| 4 | Route to timing | ROUTE_ACCEPT |
| 6 | Generation promotion | HOLD_GENERATION_DWELL |
| 12 | Generation promotion | GENERATION_ACCEPT |

Final state: route=timing, generation=1. Local tests verify no cross-clock privilege escalation, replay rejection, resource and regression limits, evidence-root filtering and detectable in-memory ledger modification.

## Security and scientific limits
Unique root labels cannot establish actual independent observations. Synthetic metrics and policy thresholds are examples, not measured properties of a deployed neural network. A hash chain alone does not provide durable tamper-proof storage.

## WAG-019 target — Temporal Causality and Cross-clock Commit Barriers
Route or generation promotion must reference a finalized parent clock-state snapshot and must reject stale, reordered or superseded observations. Use parent revision IDs and monotonically increasing event versions. Each higher clock advances only on a completed, independently verified lower-clock evidence window.
