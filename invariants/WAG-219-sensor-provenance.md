# WAG-219 — MNAR sensor provenance and censored qualification
.dlw

Based on corrected WAG-218. The test distinguishes observed zeros from unavailable slots and adds missing-not-at-random (MNAR) fixture masks: event-targeted disappearance, phase-targeted censoring, and selective absence of non-events. Other masks are random-half and contiguous burst outage. Provenance flags are **provided by the synthetic simulator**; they are not detected by the observer from a missing stream.

The WAG-216 history is reconstructed at window 3, but any previously REOPENED identity is correctly left on WAG-217 PROBATION until a usable fifth window exists. An event-correlated sensor mask immediately suspends qualification; it preserves last **qualified** identity, excludes still-probationary recovered candidates, and records lack of fresh verification. Visible observations still pass through phase-matched precision and minimum opportunity/coverage criteria. Blind policy treats null as zero, coverage policy uses observed portions only.

192 deterministic fixtures across four signal families, six masks, four base periods and two seeds; 184320 observation slots processed (five times 192 per fixture). 216 event-correlated per-component decisions suspended. Results:
stable/visible: blind mismatches 0, coverage mismatches 0, provenance mismatches 0, suspended components 0
stable/random_half: blind mismatches 6, coverage mismatches 0, provenance mismatches 0, suspended components 3
stable/burst: blind mismatches 8, coverage mismatches 0, provenance mismatches 0, suspended components 2
stable/event_targeted: blind mismatches 8, coverage mismatches 8, provenance mismatches 0, suspended components 16
stable/phase_targeted: blind mismatches 8, coverage mismatches 8, provenance mismatches 0, suspended components 16
stable/anti_event: blind mismatches 0, coverage mismatches 0, provenance mismatches 0, suspended components 16
jitterB/visible: blind mismatches 0, coverage mismatches 0, provenance mismatches 0, suspended components 0
jitterB/random_half: blind mismatches 5, coverage mismatches 1, provenance mismatches 1, suspended components 3
jitterB/burst: blind mismatches 8, coverage mismatches 2, provenance mismatches 2, suspended components 2
jitterB/event_targeted: blind mismatches 8, coverage mismatches 8, provenance mismatches 2, suspended components 16
jitterB/phase_targeted: blind mismatches 8, coverage mismatches 8, provenance mismatches 2, suspended components 16
jitterB/anti_event: blind mismatches 0, coverage mismatches 2, provenance mismatches 2, suspended components 16
dropB/visible: blind mismatches 0, coverage mismatches 0, provenance mismatches 0, suspended components 0
dropB/random_half: blind mismatches 6, coverage mismatches 0, provenance mismatches 0, suspended components 4
dropB/burst: blind mismatches 8, coverage mismatches 0, provenance mismatches 0, suspended components 2
dropB/event_targeted: blind mismatches 8, coverage mismatches 8, provenance mismatches 0, suspended components 16
dropB/phase_targeted: blind mismatches 8, coverage mismatches 8, provenance mismatches 0, suspended components 16
dropB/anti_event: blind mismatches 0, coverage mismatches 0, provenance mismatches 0, suspended components 16
flash_return/visible: blind mismatches 0, coverage mismatches 0, provenance mismatches 0, suspended components 0
flash_return/random_half: blind mismatches 6, coverage mismatches 0, provenance mismatches 0, suspended components 5
flash_return/burst: blind mismatches 8, coverage mismatches 0, provenance mismatches 0, suspended components 4
flash_return/event_targeted: blind mismatches 8, coverage mismatches 8, provenance mismatches 0, suspended components 24
flash_return/phase_targeted: blind mismatches 8, coverage mismatches 8, provenance mismatches 0, suspended components 24
flash_return/anti_event: blind mismatches 0, coverage mismatches 0, provenance mismatches 0, suspended components 24

An intact last-known qualified state is not evidence the hidden physical component actually persists. An expired or probationary hypothesis cannot be silently promoted under missingness. The simulated diagnostic provenance is an oracle label; in real settings this would require a trusted sensor health channel or independent instrument. With two seeds per base period, sample diversity is limited; fixed deterministic patterns are repeated. No cryptographic seal, independent witness roots, uncertainty interval, biological signal or runtime benchmark is claimed.

WAG-220 natural bound: sensor provenance audit—distinguish honest diagnostic flags from lying/corrupted metadata, and quarantine a sensor without inventing observations.
