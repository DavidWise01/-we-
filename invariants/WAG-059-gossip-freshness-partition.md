# WAG-059 — Gossip Freshness, Witness Coverage and Partition Recovery

Status: instantiated and locally tested November 15, 2026. Python unittest result: 24/24 PASS. GitHub HTML visual journal updated for this turn.

## Invariant
CONSISTENT_RECEIVED_VIEWS != COMPLETE_AND_FRESH_NETWORK_KNOWLEDGE.

Operational trust requires authenticated heads, sufficiently recent reports, expected witness coverage, absence of a known partition and compatible histories after reconnection. A local agreeing quorum cannot authorize global trust while known witnesses are unreachable.

## Python reference
- invariants/wag059/wag059.py: Ed25519 signatures on log ID, witnessed ordered-leaf root, tree size and timestamp; per-witness monotonic signed timestamps; a maximum-age window of five logical ticks; distinct declared witness origins and failure domains.
- Every assessment preserves signed reports and a decision in a hash-linked append-only in-memory ledger.
- Known conflicting disclosed prefixes => QUARANTINE_FORK, including when the witness that supplied a conflicting view is now offline.
- Known unreachable witnesses => HOLD_PARTITION, even with 3/5 fresh agreement.
- Missing or stale expected witnesses => HOLD_STALE_OR_MISSING.
- Distinct compatible but lagging fresh heads => HOLD_LAGGING, until all heads are synchronized.
- All five expected fresh reports, matching tree size and root, with no partition => CURRENT.

## Executed synthetic demonstration
Five locally generated Ed25519 witness keys.
W1/W2/W3 report the same tree at logical ticks 11, 12 and 13. At tick 15 W4 and W5 are unreachable, and three fresh reports yield HOLD_PARTITION.
W4 and W5 reconnect with matching histories at tick 16. All five heads are fresh and consistent; CURRENT.
Eight linked audit records verify. 24/24 Python tests passed in 0.024 seconds, including fork detection, stale report hold, exact freshness boundary, rejoin, signed payload tampering, replay, future stamps, ancestry collision and ledger mutation.

## Evidence limits
The reference uses logical timestamps and independently created local keypairs, not authenticated real-world clocks or actual network reachability. The set of expected witnesses is provided by configuration and can omit undiscovered participants. Source independence labels are declared rather than verified. Prefix checks compare fully disclosed leaf lists, not public compact consistency proofs. The SHA-256 ledger is in-memory and not externally anchored or durable. A CURRENT decision is limited to this synthetic policy and does not prove globally complete public knowledge.

## Visual assets
- docs/index.html: WAG-059 responsive embedded SVG, appended to the continuous WAG-044–WAG-059 journal.
- WAG-059-mesh.jpg: generated JPG available in the conversation. Its network statistics, timing and process panels are illustrative; the GitHub HTML visual is a self-contained SVG rather than the JPG binary.

## Next invariant — WAG-060: Partition Rejoin and Monotonic Trust Restoration
Restoration must not merely count matching reports after reconnecting. Require an authenticated witnessed consistency proof spanning the exact pre-partition frozen head and rejoined head, enforce a temporal recovery window, and prevent trust from being restored after a known fork unless an independently authorized remediation establishes a new log identity.
