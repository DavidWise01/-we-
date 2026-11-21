# WAG-214 — Provisional birth versus verified persistence
.dlw

Three consecutive 192-observation windows: original learning (0–191), candidate model selection (192–383), and strictly later, untouched qualification (384–575). The model is chosen only from the second window by reusing WAG-213 period+phase search; qualification requires at least 0.65 precision for EACH proposed component on the untouched third window. No third-window data enter candidate search. Surviving components are published; unsupported components are withheld. One observation ancestry remains: these are independent temporal partitions, not independent source witnesses.

Executed 737280 observation-slot policy evaluations on ten designed fixture types, 4 base periods × 16 seeded trials × 2 policies × 576 slots. Provisional versus verified rows follow:
stable/provisional: correct 64, wrong 0, unknown 0; candidate births 0
stable/verified: correct 64, wrong 0, unknown 0; candidate births 0
jitterB/provisional: correct 64, wrong 0, unknown 0; candidate births 0
jitterB/verified: correct 62, wrong 2, unknown 0; candidate births 0
shiftB/provisional: correct 64, wrong 0, unknown 0; candidate births 0
shiftB/verified: correct 64, wrong 0, unknown 0; candidate births 0
replace/provisional: correct 64, wrong 0, unknown 0; candidate births 64
replace/verified: correct 64, wrong 0, unknown 0; candidate births 64
ephemeral/provisional: correct 0, wrong 64, unknown 0; candidate births 64
ephemeral/verified: correct 64, wrong 0, unknown 0; candidate births 64
dropA/provisional: correct 64, wrong 0, unknown 0; candidate births 0
dropA/verified: correct 64, wrong 0, unknown 0; candidate births 0
dropB/provisional: correct 64, wrong 0, unknown 0; candidate births 0
dropB/verified: correct 64, wrong 0, unknown 0; candidate births 0
bothDrop/provisional: correct 64, wrong 0, unknown 0; candidate births 0
bothDrop/verified: correct 64, wrong 0, unknown 0; candidate births 0
mixedTransient/provisional: correct 0, wrong 0, unknown 64; candidate births 0
mixedTransient/verified: correct 0, wrong 0, unknown 64; candidate births 0
harmonic/provisional: correct 0, wrong 0, unknown 64; candidate births 0
harmonic/verified: correct 0, wrong 0, unknown 64; candidate births 0

Key comparison: 64/64 genuine replacements retained under both policies. A new period that existed only in window 2 produced 64/64 erroneous provisional commitments, all 64 eliminated by the third-window gate while correctly preserving A. Two jittered pairs were partially withheld under verification. The mixed-transient and harmonic fixtures are unresolved; neither model correctly identifies their expected components and they remain unknown. These are not overall 100% results.

The third window tests future evidence but is the SAME generating stream and source ancestry. No biological timing, physical resonance, actual 200ms execution or out-of-distribution performance is claimed. The 0.65 threshold is selected exploratory parameter. Failure inputs retained append-only in counterexamples.json.

WAG-215 natural boundary: maintain a reversible provisional registry with expiration, confirmation and lineage, rather than immediately presenting every second-window candidate as a current fact.
