# WAG-208 — Independent phase windows and harmonic ancestry
.dlw

Executed 2,654,208 observation-equivalent polarity checks over 6,912 policy evaluations, 256 unique sequences per kind/tolerance. For each sequence, a 384-slot observed binary disturbance stream is constructed. Discovery uses rising transition events in slots 0–191; confirmation uses slots 192–383. These temporal partitions are not independent source ancestries. The proposal is the median inter-event interval with 80% within tolerance (±0, ±1, ±2); holdout also requires five interval observations and 80% matching. Candidate integer divisors are checked as possible harmonic aliases. Failure returns unknown rather than a guessed period.

At elasticity ±2: direct spacing correct on 256/256 periodic, 256/256 jittered, and 0/256 shuffled locked. Holdout dual correct on 256/256 periodic, 248/256 jittered, wrong on 4/256 jittered, abstains on 4/256 jittered, with zero shuffled locks. No claim that holdout is universally superior; these fixtures differ from WAG-207 because full 384-slot events are processed instead of only a rolling 128-transition window.

Remaining counterexamples: four incorrect jittered candidate locks; division rules cannot resolve every neighboring frequency. No physical resonance, 200ms timing, or independent-source corroboration is claimed. Next WAG-209: abstention based on agreement across independent temporal estimators, including error cases.
