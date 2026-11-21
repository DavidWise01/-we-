# WAG-213 — Component birth and period replacement
.dlw

The original WAG-212 384-slot source ancestry is preserved. The 0–191 window learns a pair; the 192–383 window can now propose a NEW single or pair model rather than merely test old periods. The new model searches periods 7–46 with phase, matches observations within ±1, and chooses a pair if training F1 exceeds best single by 0.1 with pair F1 >=0.8. Under the guard, pair F1 >=0.88 with gain >=0.1 or single F1 >=0.9 is required; otherwise old elastic persistence remains.

On the eight designed families, retrain and guard both recover all 64 B period replacements (old [p,p+4], new [p,p+6]), preserving the A period. Prior WAG-212 elastic policy recovers 0/64 period replacements. Both policies preserve stable, jittered, phase-shifted, drop-A, drop-B and both-drop scenarios at 64/64 each, and WITHHOLD 64/64 harmonically-related pairs rather than report a known correct decomposition. No new independent holdout is performed after selecting the new second-half period. Therefore high synthetic accuracy does not establish generalization or trustworthy online birth detection; repeat patterns across seeds are not independent.

589824 observation-slot evaluations (same 384-slot fixture replayed under three policies) with no actual polarity mirror or benchmark timing. Results in results.json; prior failure inputs stored in counterexamples.json. Source is append-only, .dlw.

Natural WAG-214 bound: third-window qualification under adversarial replacement and harmonic confusion. Separate candidate birth from verified birth.
