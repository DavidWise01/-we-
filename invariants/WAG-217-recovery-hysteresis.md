# WAG-217 — Recovery hysteresis and false-revival resistance
.dlw

Five chronological 192-slot windows: initial component learning, candidate proposal, initial qualification/expiration, proposed reopening, then probation qualification. An expired/released identity that regains support in window 3 gets REOPENED → PROBATION, not immediate restored qualification. A separate window 4 must provide at least 0.70 precision under a ±3 phase search for REQUALIFIED; otherwise PROBATION_FAILED returns it to expired. Original identity and previous EXPIRED events remain in log. Previously qualified identities continue above precision 0.55 or emit LOST. The existing WAG-216 replay validator is reused for the first four windows, with an explicit additional replay validator for probation transitions.

Execution: 552960 observation-slot evaluations, 5634 appended events, 576 ledger replay comparisons; 66 probation entries, 2 requalified, 64 failed. 66 injected premature qualification attempts rejected.

stable: correct 64, wrong 0, unknown 0, probation 0, requalified 0
jitterB: correct 64, wrong 0, unknown 0, probation 2, requalified 2
replace: correct 64, wrong 0, unknown 0, probation 0, requalified 0
ephemeral: correct 64, wrong 0, unknown 0, probation 0, requalified 0
flash_return: correct 64, wrong 0, unknown 0, probation 64, requalified 0
dropA: correct 64, wrong 0, unknown 0, probation 0, requalified 0
dropB: correct 64, wrong 0, unknown 0, probation 0, requalified 0
bothDrop: correct 64, wrong 0, unknown 0, probation 0, requalified 0
harmonic: correct 0, wrong 0, unknown 64, probation 0, requalified 0

The genuine two jittered recoveries remain under their original IDs. The flash_return fixture makes a formerly expired new component reappear in window 3 and vanish in window 4; it yields 64 probation failures and no incorrect revival. In every seeded flash_return instance the deterministic binary pattern is the same; not 64 independent mechanisms. Harmonic cases stay UNKNOWN (not successful decompositions). This is synthetic evidence under a selected rule; no physical resonance, independently sourced witnesses, cryptographic ledger proof or actual runtime-bound validation.

Next WAG-218: asynchronous partial observability, missing windows, and censoring versus true disappearance, while retaining probation ancestry.
