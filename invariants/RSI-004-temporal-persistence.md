# RSI-004 — ERSE temporal persistence
A proposed computational analogy to wake, NREM N1/N2/N3, and REM. The original nine-branch ERSE-018 engine remains unchanged except for a temporal input gate: 12 wake ticks, 3 N1, 4 N2, 5 N3, 4 REM. Wake uses current observations; NREM holds the previous observation; REM replays the three-tick prior frame. All phases continue paying the original resistance cost. Nominal frequency labels are metadata only, not simulated EEG. NREM stages do not yet implement distinct consolidation algorithms.

Matched 100-energy initial budgets and identical 28-tick resistance streams: steady 9/9 survive both groups, sudden steps 0/9 cyclic versus 9/9 awake, alternating extremes 0/9 cyclic versus 9/9 awake. Eight local regression tests passed; passing tests does not mean persistence succeeded. Each parity group has identical branches. This is a designed counterexample, not a biological claim or evidence of recursive improvement.

Neuroscience reading: https://pmc.ncbi.nlm.nih.gov/articles/PMC7611961/ and https://pmc.ncbi.nlm.nih.gov/articles/PMC12576410/ . Brain rhythms coexist and do not correspond one-to-one to software engines.

Next RSI-005: stagger phases across nine branches, retain sentinel perception and test shared alerts under the same resistance and energy accounting.
