# WAG-216 — Recoverability after mistaken expiration
.dlw

WAG-215's first 3×192-slot event ledger remains untouched. A fourth 192-slot window tests all expired or released IDs, searching ±3 phase offsets WITHOUT changing the retained period identity. Reactivation needs observed precision ≥0.7. Recovery emits REOPENED followed by REQUALIFIED, with original ID intact; lack of support emits RECHECK_FAILED. Previously qualified components emit CONTINUED if precision ≥0.55 or LOST otherwise. All events are appended. replay216 validates the original WAG-215 sequence and rejects orphan reopenings, double reopenings, missing requalification, invalid continuation/loss, and out-of-order events.

Executed 491520 observation-slot policy evaluations over 640 runs of 768 slots; 4674 ledger events and 640 replay checks. 2 reopenings: both originally mistaken jittered expirations recovered (period 27 in p=23, seeds 215 and 221). 512 expired/released IDs resisted unsupported requalification. Each of stable, jitterB, shiftB, replace, ephemeral, dropA, dropB, bothDrop and mixedTransient has 64/64 expected final period-set matches on the designed fixtures. Harmonic pair remains 64/64 unknown (not a successful identification), and period identity still may miss novel rhythms in a fourth window.

The recovery fixture deliberately supplies further jittered observations: no retroactive evidence of continuous existence between observation windows can be inferred. Every window shares a single generator/source ancestry. Source-level JSON is not cryptographically tamper-proof. No true signed-polarity inversion or runtime performance benchmark.

WAG-217: test an explicit cool-down and multi-window requalification against intermittent reappearances and false revival caused by aliases.
