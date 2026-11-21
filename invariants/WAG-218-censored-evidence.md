# WAG-218 — Partial observability and censored evidence
.dlw

All observations remain a single source ancestry. The WAG-217 five-window binary event model is extended with explicit null for unobserved fifth-window slots. 'No signal' is encoded 0 only where the sensor was observed, and 'no information' is null. Four coverage patterns: fully visible, wholly missing, first 96 of 192 slots visible, and alternating even/odd observed slots. Six fixture families: stable, jittered, B disappeared, ephemeral, one-window false return, and harmonic ambiguity. Each 4 planted base periods ×16 deterministic seeds.

The WAG-217 blind baseline converts missing slots to zero. The WAG-218 coverage-aware policy filters both forecast and observed positions to only covered slots, calculates precision within ±1 matching with ±3 phase search, and requires at least 50% slot coverage and at least 4 visible predicted events PER component. Below these gates append CENSORED preserving the previous component state, but do not claim fresh validation. Suspended certainty and last-known state must not be confused.

Actual executed: 1474560 slot evaluations, 1536 valid ledger replays, 0 censored component decisions. On fully missing stable streams, baseline incorrectly releases 0 last-known component instances while the coverage-aware policy releases 0. The coverage-aware policy still makes partial-mask mistakes: jittered alternate 50/64 exact set matches, 14/64 wrong; jittered half-visible 62/64 exact, 2/64 wrong. Harmonic alias cases remain unknown; no decomposition claimed. Comparisons against hidden planted ground truth under missingness measure preservation of prior state, NOT proof that the hidden component remains physically present.

stable/visible: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
stable/missing: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
stable/first_half: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
stable/alternate: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
jitterB/visible: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
jitterB/missing: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
jitterB/first_half: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
jitterB/alternate: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
dropB/visible: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
dropB/missing: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
dropB/first_half: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
dropB/alternate: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
ephemeral/visible: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
ephemeral/missing: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
ephemeral/first_half: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
ephemeral/alternate: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
flash_return/visible: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
flash_return/missing: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
flash_return/first_half: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
flash_return/alternate: exact 64, wrong 0, unknown 0, unverified components 0, blind mismatches 0
harmonic/visible: exact 0, wrong 0, unknown 64, unverified components 0, blind mismatches 64
harmonic/missing: exact 0, wrong 0, unknown 64, unverified components 0, blind mismatches 64
harmonic/first_half: exact 0, wrong 0, unknown 64, unverified components 0, blind mismatches 64
harmonic/alternate: exact 0, wrong 0, unknown 64, unverified components 0, blind mismatches 64

The replay test checks chronology and allowed state transitions but is not cryptographic sealing. Missingness mechanisms here are deterministic and may be informative; no unbiased missing-data assumption or confidence interval is justified. No physical resonance, live 200ms benchmark or independent source corroboration.

Next WAG-219: missing-not-at-random masks, sensor outage provenance, and confidence intervals that distinguish observational silence from sensor silence.
