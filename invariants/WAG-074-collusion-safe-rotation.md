# WAG-074 — Independent Review Quorums, Collusion Checks, and Replacement Authorization

Date: 2026-11-15. State: instantiated, 58/58 local Python tests passed.

## Invariant

`VALID_SIGNED_APPROVALS != INDEPENDENT_AUTHORITY`

Following a cryptographically proven same-round equivocation by W1, retain its two conflicting Ed25519-signed statements and their evidence hash. Freeze a proposed W1 -> W4 rotation to the original active set, current epoch/round, certificate hash, candidate public-key fingerprint, nonce, and expiration. Only W2 and W3 may authorize it, and both must sign the *same* rotation proposal. Reject missing/invalid/duplicate/expired reviews, vetoes, reviewers sharing a declared key/ancestry/operator/failure domain, or a replacement colliding with any prior active witness on those dimensions. No approval from the quarantined offender may count.

## Local demonstration

1. Create W1/W2/W3 with unique locally generated Ed25519 keys and independently labeled roots/operators/domains.
2. W1 signs two different snapshot values in the same epoch and round. Validate both signatures; preserve the equivocation certificate and hash.
3. Freeze W1 -> W4 proposal binding candidate to evidence, nonce and expiry.
4. W2 and W3 independently sign the exact same domain-separated proposal hash; reject any sole approval or veto.
5. Retire W1, admit independent labeled W4, advance epoch.
6. Obtain freshly signed equal-snapshot reports from W2, W3, W4 with distinct receipt IDs.
7. Recertify *locally declared* quorum; preserve eight SHA-256 linked events including the old conflicting proof.

**Observed:** `LOCAL_DECLARED_QUORUM_RECERTIFIED`, active `W2,W3,W4`, retired `W1`; 8 hash-linked events; signature and tamper checks pass. 58/58 tests pass locally.

## Boundaries

The review quorum has two distinct *declared* roots, operators, keys, and domains. Actual independence, absence of collusion and authority to approve are not proven by those labels or signatures. Both reviewers may intentionally agree on a bad proposal; the design enforces policy and detectable transcript consistency, **not Byzantine agreement**. The local synthetic keys are test identities, not actual GitHub or infrastructure agents. The in-memory hash-linked event log does not provide externally anchored immutable persistence. GitHub upload and runtime CI verification are distinct operations.

## Deliverables

- `invariants/wag074/wag074.py` — executable Ed25519 authorization kernel.
- `invariants/wag074/test_wag074.py` — 58 local regression cases.
- `invariants/wag074/WAG-074-ascii.txt` — ASCII experiment visual.
- `docs/index.html` — embedded ASCII journal entry.

## Next natural invariant — WAG-075

**Compromise-Resilient Reviewer Succession and Cross-Generation Ancestry.** A replacement's key and labels may be fresh while its true controlling organization is unchanged. Require verifiable historical authorization lineage, cryptographic reviewer succession, independent domain evidence, and bounded recovery from reviewer compromise. Explicitly model holds when reviewer independence is uncertain.

`{{ preserve [prove -> review -> authorize -> rotate -> recertify] }}`