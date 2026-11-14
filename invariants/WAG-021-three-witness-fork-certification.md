# WAG-021 — Three-Witness Fork Certification

Status: instantiated local reference implementation, 2026-11-14. 18/18 Python unit tests passed.

## Invariant
A two-branch reconciliation candidate is provisional. It can become a certified checkpoint only after a third independently obtained observation agrees on the exact canonical event, scope, method, and value.

CERTIFY(C) => ValidTwoParentCandidate(C) AND MatchingObservation(W1,W2,W3) AND PairwiseIndependentAncestry(W1,W2,W3) AND AuthenticatedRoots(W1,W2,W3) AND AppendOnlyCertificate(C).

## Records
- Genesis C0
- Observation A, ancestry root A
- Observation B, ancestry root B
- Provisional candidate referencing A,B
- Observation C, ancestry root C
- Certificate referencing candidate and C, preserving A/B via candidate

A candidate never counts as an independent third witness. GitHub and 0root.ai are mirrors of one owned corpus, so mirrored content cannot provide multiple independent roots.

## Test results
18/18 passed locally: successful three-witness certification, two-witness provisional status, duplicate roots, shared ancestry, missing authenticated root, conflicting value/scope/method, invalid candidate composition, different parent, replayed packet, missing seal label, original evidence preservation, and hash-chain tamper detection.

Demonstration: three observations with value 7, distinct roots, matching event/scope/method. Six records generated; hash-linked chain verified.

## Security limits
This is a deterministic single-writer reference. The `authenticated_roots` input is an assertion supplied by an external authenticator, not checked by the reference kernel. The seal stores a SHA-256 hash commitment and a key ID label; it is NOT a cryptographic signature. The ledger is not a durable transactional store and does not independently prevent complete replacement.

## Next boundary — WAG-022: Witness Quorum Recovery
If a witness becomes unavailable, invalid, or compromised, preserve the checkpoint's historical certificate but suspend operational reliance. Fresh independent replacements must restore quorum through a new certificate/version; they may never erase the original witness record or retroactively change a past observation.
