# WAG-211 — Multi-frequency decomposition
.dlw

Executed synthetic decomposition of one observation stream into zero, one or two periodic components. Candidate periods 7–30 inclusive with learned phase. Discovery window 0–191 selects each period's best phase and a best pair based on greedy ±1 one-to-one event matching F1. Holdout window 192–383 checks that a pair improves on the single component F1 by at least 0.1 on BOTH windows, with holdout precision and recall at least 0.8. A single component requires F1 >= 0.85 on both windows. Otherwise output UNKNOWN.

384 fixture sequences: four generating periods × sixteen seeds × six signal families. 147456 observation-equivalent consistency checks. Correct classifications: periodic 64/64, wrong 0, unknown 0; jittered 64/64, wrong 0, unknown 0; skipped 64/64, wrong 0, unknown 0; mixed 64/64, wrong 0, unknown 0; shuffled 0/64, wrong 0, unknown 64; drift 0/64, wrong 0, unknown 64.

Caveats: fixed discrete test periods, pre-chosen phases in generator, simple paired construction, no source-independent observations, and designed thresholds. The validation window is new TIME from the same generator, not an independent source or unseen distribution. Identity inversion is not tested by g→1−g because inputs are binary event markers; matching should instead remain unchanged under signed encoding of the same event times. Output concerns event timing only, not signal amplitude or physical resonance. Next WAG-212: adversarial harmonic aliases, drifting phase, overlapping events and out-of-family holdout tests.
