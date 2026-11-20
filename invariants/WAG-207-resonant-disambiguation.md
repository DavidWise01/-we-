# WAG-207 — Resonant disambiguation

.dlw — append-only natural invariant.

Deterministic executed experiment: 2304 sequences, 384 samples each, four periods (9,13,17,23), three patterns (perfect/jittered/shuffled), three elasticities (0/1/2). Mirrored transition histories checked each sample; 2304 missing observation resets checked. Five policies: WAG-206 baseline, residual tie-break, lag+median-spacing, direct median spacing, and median spacing confirmed by lag recurrence score >=0.55.

At tolerance ±2, baseline final jitter locks 206/256, exact period 121/256, shuffled locks 0/256. Direct spacing final jitter locks 245/256, exact 230/256, shuffled false locks 4/256. Confirmed spacing final jitter locks 188/256, exact 175/256, shuffled false locks 1/256. At tolerance 0 all policies correctly lock clean periods 256/256, and the new direct spacing method retains clean-period exactness 256/256 at ±1 and ±2. Residual score alone does not solve harmonic ambiguity. These outcomes are synthetic and the 'confirmed' policy has NOT achieved zero false locks.

The computation tests transition-history frequency inference, not physical oscillation or live timing. Next WAG-208: independent residual origins, aliases and abstention to eliminate false locks without discarding jitter robustness.
