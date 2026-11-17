# RSI-003 — Inherited persistence through unfamiliar resistance

ERSE-018, nine branches, same initial energy 100 per branch, 30 logical ticks per condition. Compare inherited state (30 prior ticks plus an energy/position reset frame) to cold state. Both use identical fixed execution rules and observations; no reward maximization or policy evolution.

| Pattern | Odd inherited | Odd cold | Even inherited | Even cold |
|---|---:|---:|---:|---:|
| Step | 44 | 43 | 35 | 35 |
| Reverse | 36 | 35 | 40 | 38 |
| Alternating | 60 | 56 | 52 | 49 |
| Ramp | 53 | 49 | 38 | 38 |

Six local regression tests passed. All survive; inherited state wins six parity-pattern comparisons and ties two. These are deterministic designed patterns, not independent statistical replicates. Within parity branches are identical. Prior experience was not matched in total compute, and history and current state were inherited together. No RSI claim.

Next RSI-004: separate current-state inheritance from deep retrieval and three-second recall with matched ablations.
