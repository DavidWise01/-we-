# WAG-150 — Anisotropic counterrotation

Exact rational simulation, 200 sampled iterations plus one final checked update. Five paired channels with coefficients r/20, total 26, center fixed at 6. Each pair starts with total 4. Counterrotating angular addresses advance by opposite unit increments modulo 360. Conservation, nonnegativity, fixed center, nonincreasing squared error and zero net angular address checked on every update. Maximum residual at iteration 200: 7.055079108655332e-10.

Canonical address: {{y:m:d:h:m:s:d:am:as:ad}}. Only local angular coordinates and iteration order are implemented here. Full chronology, cross-pair exchange and physical electromagnetic dynamics are not implemented. Couplings are illustrative; angular coordinates do not yet influence flux. Next: inter-rank conservative coupling and phase-dependent flux, with a counterexample for unequal pair totals.
.dlw
