# WAG-065 — Minimum Cuts, Redundant Witness Paths, and Fault-Tolerant Routing

Date: 2026-11-15. Local full Python implementation and 24/24 local unit tests passed.

## Invariant
A three-witness triangle K3 has edge connectivity λ(K3)=2. One removed edge leaves a connected path, but two incident removed edges isolate one witness. Connectivity is not proof of independently authenticated ancestry or Byzantine consensus.

`WITNESS_CONNECTED != BYZANTINE_AGREEMENT`

## Executed synthetic states
1. Initial cycle W1-W2-W3-W1: 3 edges, CONNECTED_REDUNDANT.
2. Cut W1-W2: 2 edges, CONNECTED_DEGRADED.
3. Cut W1-W3: 1 edge, HOLD_DISCONNECTED.
4. Repair W1-W2: 2 edges, CONNECTED_DEGRADED.
5. Repair W1-W3: 3 edges, CONNECTED_REDUNDANT.
All original witness identities and declared distinct ancestry strings A,B,C are preserved. Five append-only SHA256 hash-linked events verified.

## Files
- docs/index.html: ASCII figure embedded in a preformatted text panel and linked TXT art.
- invariants/wag065/WAG-065-ascii.txt: original ASCII illustration.
- invariants/wag065/wag065.py: GitHub reference kernel.
- invariants/wag065/test_wag065.py: 24-case GitHub regression suite.
- Local full files and original TXT are available as conversation artifacts.

## Limitations
Graph edges are abstract communications, not verified secure channels. Distinct root strings are only declared source identities. A connected K3 remains vulnerable to Byzantine misinformation; under common BFT assumptions tolerating f=1 calls for n>=3f+1=4 replicas. The graph reference does not establish Byzantine consensus or physical toroidal mechanics. Hash-linked event records are memory resident, not externally anchored immutable storage.

## Next — WAG-066: Vertex Cuts, Quorum Loss, and Failure-Domain Separation
Calculate κ(K3)=2, but distinguish vertex connectivity from the number of witnesses remaining. A single vertex failure leaves two connected survivors yet violates the strict three-independent-witness quorum. Test overlapping control domains and separate routing availability from authority to certify.
