# WAG-209 — Counterexample-guided frequency qualification
.dlw

Four confirmed WAG-208 wrong locks preserved as deterministic binary sequences. Two are exactly one slot too long at true period 23, another one-slot error at period 17. Original failed lock outputs persist in WAG-208 and WAG-209 counterexamples. WAG-209 adds explicit candidate conflict: return UNKNOWN if early-window dual lock disagrees with full-history median spacing. This is a cross-check on a SINGLE observation ancestry, not independent evidence.

At elasticity ±2, prior dual: 248 correct / 4 wrong / 4 unknown jittered (256 total); WAG-209 cross: 248 correct / 0 wrong / 8 unknown. Exact periodic: 256/256 correct. Shuffled: 256/256 abstained. Full-history pooled on these same fixtures: 256/256 jittered correct, 0 errors but this is the selected same-fixture dataset; not proof of general reliability.

Four inputs minimized by shortest FAILING PREFIX search, not by arbitrary delta debugging, because removing interior events may change inference or disrupt phase ancestry. Their binary strings, precise event positions and seeds are preserved in counterexamples.json.

Test count 2654208 mirrored observation-equivalent checks, across 3 elasticities, 3 patterns, 3 policies, 256 fixtures per cell. No live performance timing, physical resonance, or general error-rate claim.

Next WAG-210: out-of-family harmonic and adversarial drift tests, then conditional commitment.
