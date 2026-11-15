# WAG-049 — Independent Entropy Provenance and Concealment

Status: instantiated November 14, 2026. Local reference Python code passed 24/24 unittest cases. GitHub copy uploaded; not independently run in the connector.

## Invariant
Reproducible random allocation does not imply independently authenticated entropy, unpredictability or genuine concealment.

REPRODUCIBLE_ALLOCATION != VERIFIED_ENTROPY_SOURCE != VERIFIED_CONCEALMENT

## Reference sequence
1. Register 48 subjects, a fixed 24/24 allocation policy, three claimed entropy source IDs and three witness-root labels.
2. Commit SHA-256 hashes of source-specific 256-bit contributions and protocol hash before the logical enrollment cutoff.
3. Seal a commitment set at cutoff tick 10 with three distinct declared witness-root labels.
4. Reveal source contributions only after the cutoff. Reject mismatched, premature, missing or replayed reveals.
5. Combine contributions in canonical sorted-source order with domain-separated SHA-256 and deterministically rank subjects using HMAC-SHA256.
6. Produce exactly 24 treatment and 24 control assignments, preserve the assignment digest and all ceremony records.

## Executed synthetic results
The local demonstration uses deterministic SHA-256 strings derived from labels prefixed SYNTHETIC-ONLY, not true random entropy.
- 3 commitments
- 1 protocol genesis
- 1 cutoff
- 3 reveals
- 1 allocation
= 9 hash-linked records; ledger verification passed.
- Assignment: control 24; intervention 24.
- Status: REPRODUCED_FROM_REVEALS_NOT_ENTROPY_CERTIFIED.
- 24/24 local unittest tests passed, including invalid parameters, late/duplicate commits, wrong reveals, cutoff ordering, missing witness labels, repeated finalization and hash-chain tamper detection.

## Files and HTML
- docs/index.html: WAG-049 self-contained embedded SVG panel, appended without replacing WAG-044 through WAG-048.
- invariants/wag049/wag049.py: GitHub reference kernel.
- invariants/wag049/test_wag049.py: 24-case GitHub reference test suite.
- Original generated WAG-049 JPG: conversation artifact WAG-049-mesh.jpg. The HTML visual is an embedded SVG drawing; JPG binary is not yet in the GitHub repository.

## Limits
The source IDs, commitment timestamps and witness roots are caller-supplied. A malicious seed contributor can choose contributions strategically, or the claimed contributors can collude. Even a matching precommitment cannot prove that secrets were drawn unpredictably, kept private or came from three truly independent trust domains. This code is deterministic and stores secrets in its event log upon reveal. Real clinical/randomized trials require an independently audited allocation service, access controls, external timestamp/signature attestations, durable append-only records and valid experimental procedures. SHA-256 chaining alone is not tamper-proof archival storage.

## Next invariant — WAG-050: Entropy Contributor Independence and Bias Resistance
Trace causal ancestry and actual control domains for each entropy contributor. Guard against last-contributor manipulation by using immutable commitments and a reveal policy defined before participation, including explicit abort and withholding rules. Verify independence through external attestations and failure-domain audits. Never promote asserted source diversity to proven unbiased assignment.
