# WAG-220 — Sensor provenance audit and quarantine
.dlw

Audit fixture has four rhythm families (stable, jittered, B disappearance, one-window flash), two base periods (9,23), two seeds (215,221), three masking patterns (visible, burst, event-targeted), and six report states: truthful, falsified coverage, stale window, omitted, false visible label, and plausible-but-false mask label. 288 executed cases.

Audit checks the reported source ID, window number, observed-slot count against actual null markers, observed-slot numerical bounds, and whether a 'visible' claim contradicts any null marker. A failed consistency check emits QUARANTINE, and only the previously *qualified* set is exposed as last-known; previously reopened *probationary* candidates cannot silently become qualified. An accepted report is labeled ACCEPT_UNVERIFIED, NOT trusted/authenticated.

Measured 160 quarantined inconsistent reports, 48 accepted consistent-forgery reports, and 0 probation promotions under quarantine. The false-coverage attack saturates count at 192, leaving its visible-mask cases unchanged. Mask label 'visible' on truly visible data is not falsifiable. Plausible metadata for 'random_half' against an event-correlated mask passes count/time checks; 16/16 event-targeted consistent forgeries produce model mismatches. Quarantine also preserves a wrong old state in a few cases: it cannot retroactively resolve uncertainty.

truthful/visible: accepted 16, quarantined 0, mismatches 0, trust-only mismatches 0
truthful/burst: accepted 16, quarantined 0, mismatches 2, trust-only mismatches 2
truthful/event_targeted: accepted 16, quarantined 0, mismatches 2, trust-only mismatches 2
false_coverage/visible: accepted 16, quarantined 0, mismatches 0, trust-only mismatches 0
false_coverage/burst: accepted 0, quarantined 16, mismatches 2, trust-only mismatches 2
false_coverage/event_targeted: accepted 0, quarantined 16, mismatches 2, trust-only mismatches 2
stale/visible: accepted 0, quarantined 16, mismatches 2, trust-only mismatches 0
stale/burst: accepted 0, quarantined 16, mismatches 2, trust-only mismatches 2
stale/event_targeted: accepted 0, quarantined 16, mismatches 2, trust-only mismatches 2
omitted/visible: accepted 0, quarantined 16, mismatches 2, trust-only mismatches 2
omitted/burst: accepted 0, quarantined 16, mismatches 2, trust-only mismatches 2
omitted/event_targeted: accepted 0, quarantined 16, mismatches 2, trust-only mismatches 2
false_visible/visible: accepted 16, quarantined 0, mismatches 0, trust-only mismatches 0
false_visible/burst: accepted 0, quarantined 16, mismatches 2, trust-only mismatches 2
false_visible/event_targeted: accepted 0, quarantined 16, mismatches 2, trust-only mismatches 2
consistent_forgery/visible: accepted 16, quarantined 0, mismatches 0, trust-only mismatches 0
consistent_forgery/burst: accepted 16, quarantined 0, mismatches 2, trust-only mismatches 2
consistent_forgery/event_targeted: accepted 16, quarantined 0, mismatches 16, trust-only mismatches 16

No independently authenticated sensor, digital signature, trustworthy sensor timestamp hardware or independent evidence ancestry is provided. These checks validate self-consistency, not truthful sensor provenance. Synthetic fixture metadata and observed events arise from one generator; no external corroboration. The fixed case grid is exploratory; no population false-alarm estimate, runtime benchmark or physically observed phenomenon claimed.

Next WAG-221: sensor witness lineage and two-channel agreement where the second channel has independently seeded acquisition and an explicitly tested shared-root failure mode.
