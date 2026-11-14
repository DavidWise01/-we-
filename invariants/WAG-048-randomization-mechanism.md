# WAG-048 — Randomization Mechanism Verification

Date: 2026-11-14. Instantiated with executable Python kernel and 24/24 locally passing unittest cases.

## Invariant
A frozen allocation record is not proof that the procedure generating it was random, unpredictable, or concealed.

REPRODUCIBLE_ASSIGNMENT != VERIFIED_RANDOMIZATION

A test may be marked CONSISTENT_WITH_PRECOMMITMENT only when a previously recorded seed hash matches a revealed seed and the declared deterministic allocation algorithm reproduces the frozen assignment exactly. This does not itself prove the seed was sampled without manipulation or kept hidden.

## Reference algorithm
1. Precommit a SHA-256 secret seed digest, fixed cohort and 24/24 arm counts.
2. Require three separately labeled witnesses to report the exact same commitment, plus a declared concealment attestation.
3. Deterministically rank subject IDs by HMAC-SHA256(secret, "WAG048:"+subject_id), assigning 24 to treatment and 24 to control.
4. Freeze the assignment hash before revealing the seed.
5. Reveal seed and verify digest and exact assignment reproduction.
6. Preserve all decisions in an append-only hash-linked log.

## Executed synthetic result
48 registered subjects.
24 control / 24 treatment.
Revealed seed matches precommitment and reproduces the exact assignment.
Verdict: CONSISTENT_WITH_PRECOMMITMENT_NOT_PROOF_OF_RANDOMNESS.
Four local hash-linked ledger records verify.
24/24 local unittest tests passed, including reused roots, duplicate witnesses, wrong seed, changed allocation, repeated reveal, missing concealment attestation, invalid cohort and tampering.

## Files
- invariants/wag048/wag048.py — local-tested Python kernel, committed here
- invariants/wag048/test_wag048.py — 24-test suite committed here
- docs/index.html — updated in this turn with a self-contained WAG-048 SVG illustration, preserving all earlier visual journal entries
- Original generated JPG conversation artifact: WAG-048-mesh.jpg. This JPG binary is not in the repository; the HTML uses an embedded SVG visualization rather than a temporary attachment URL.

## Security and scientific limitations
The demonstrated seed is deterministic and public in reference code. It is NOT a secure private allocation. A chosen seed can encode biased assignments while passing every hash reproduction test. Witness roots are declared labels, not independent-source authentication. The concealment flag is caller-provided, not a verified independent attestation. The process is single-writer and memory-resident; its hash chain does not provide durable anchored storage.

## WAG-049 — Independent Entropy and Allocation Concealment
Move from reproducibility to trustable allocation provenance. Require independently attested entropy generation before outcomes, a verifiable commitment ceremony, controlled secret custody until assignment, and a durable binding between seed reveal, experiment protocol, witness roots and enrollment cutoff. Retrospective reproducibility may not be used to manufacture evidence of unpredictability.
