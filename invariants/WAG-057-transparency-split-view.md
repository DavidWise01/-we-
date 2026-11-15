# WAG-057 — Transparency Log Split-View Detection and Cross-Witness Consistency

Status: implemented locally 2026-11-15. Python reference 24/24 tests passed. GitHub HTML journal, kernel and regression tests updated.

## Invariant
VALID_SIGNATURES != CONSISTENT_SHARED_HISTORY.

For the same identified log, independently witnessed signed tree heads must describe an identical history at identical sizes, or an append-only prefix relationship across different sizes. An incompatible signed history triggers QUARANTINE_SPLIT_VIEW; all original signed observations remain preserved.

## Mechanism
- Authenticate each head using Ed25519 public key and domain-separated message binding log ID, logical epoch, tree size and Merkle root.
- Verify each fully disclosed ordered leaf list against its binary Merkle-tree root (domain-separated 0x00 leaf, 0x01 internal node, left-balanced RFC6962-style tree shape).
- Hold if fewer than three declared distinct witness origins and failure domains report.
- Compare every pair of authenticated heads:
  * SAME_SIZE_FORK: two heads disagree in a position at the same tree size;
  * PREFIX_FORK: shorter disclosed history is not a prefix of the longer history.
- If any conflict exists, quarantine operational reliance, append a decision without rewriting the original evidence; otherwise mark CONSISTENT_DISCLOSED_PREFIXES. This is eligibility for further verification, not proof of publicly consistent governance.
- Prevent duplicate witnesses, repeated decisions, unauthenticated signatures, mixed log IDs and forged leaf/root matches.

## Synthetic executed experiment
Three locally generated Ed25519 witness keypairs.
W1: [e1,e2,e3,a] size 4.
W2: [e1,e2,e3,b] size 4.
W3: [e1,e2,e3,a,x] size 5.
W1–W2: SAME_SIZE_FORK.
W2–W3: PREFIX_FORK.
Decision: QUARANTINE_SPLIT_VIEW; five SHA-256 linked in-memory records (policy, three heads, decision) verify.
24/24 Python unittest tests passed locally in 0.019 seconds, including valid append-only extension, conflicting roots, invalid signatures, shared declared witness provenance and tamper detection.

## Artifacts
- docs/index.html: WAG-057 illustrated entry embedded as independent browser-rendered SVG, preserving WAG-044 through WAG-056.
- invariants/wag057/wag057.py: reference implementation
- invariants/wag057/test_wag057.py: 24 passing local tests
- Original WAG-057 JPG remains a conversation artifact; not claimed as GitHub-hosted binary.

## Limitations
Witness origins and failure domains are declared metadata, not authenticated independent operators. Signing keys and views are generated locally; no public transparency service, trusted timestamps or actual network gossip was used. Prefix checking over fully revealed leaves is not an RFC6962 compact consistency proof; the prototype does not verify those proofs or detect private split views it never receives. The signed-head scheme binds a declared log ID, but not a separately authenticated log operator identity, so detection here is specifically conflicting claims about one named log, not proof that a particular operator equivocated. The visual JPG contains illustrative statistics, tree heights, log headers, and test results beyond the executed experiment; these are not empirical findings. In-memory hash chaining is not externally anchored durable storage.

## WAG-058 — Witness Gossip Authenticity and Public Log Consistency
Bind transparency head identity to authenticated log-operator signing keys, verify RFC6962-style compact consistency proofs across tree sizes and independently sourced witness gossip, and distinguish a proven same-size equivocation from a missing proof. Require an externally published evidence packet before asserting misconduct; maintain quarantine while evidence is incomplete.
