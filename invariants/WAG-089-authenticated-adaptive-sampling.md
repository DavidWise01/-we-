# WAG-089 — Authenticated Adaptive Sampling, Witness Lineage, and Reproducible Failure Evidence

Date: 2026-11-16. Full locally executed Python reference: **44/44 unit tests passed**.

## Natural invariant

A statistical observation counts only when its source witness signed a nonce-, epoch-, round-, root-, and chunk-position-bound observation, and every sampled chunk has a valid Merkle inclusion proof.

`DECLARED_SAMPLE != VERIFIED_OBSERVATION`

Three witnesses checking the same three positions produce three attestations to **three unique positions**, not nine statistically independent chunk inspections.

## Protocol

1. Freeze root, epoch, chunk count, three separate declared witness names/ancestors/failure domains, sample size, missing threshold, and alpha in SQLite.
2. Derive the unique sample positions from the fresh nonce with WAG-086's deterministic challenge selection.
3. Require three Ed25519-signed observations, each including identical positions and full Merkle inclusion paths, using domain-separated protocol label `WAG-089-OBS-v1`.
4. Verify each witness signature and exact binding to the frozen scope, each chunk and each proof.
5. In one SQLite transaction reject replays, consume all three receipt identifiers and the nonce, append one statistical round and a hash-linked audit record.
6. Calculate the **model-based** miss probability under fixed missing count m and independently uniform selection per round: `q = C(N-m,k)/C(N,k)`, `p_t = q^t`. Compare at look t with predeclared alpha spending `alpha_t = alpha/[t(t+1)]`, which sums to alpha.
7. Mark `LOCAL_CONDITIONAL_BOUND_MET` only if p_t <= alpha_t; otherwise `HOLD_INSUFFICIENT_EVIDENCE`.

The spending rule is a conservative multiple-look control **only under the stipulated sampling model and fixed alternative**. It does not demonstrate true randomness, independence, host control separation, hidden missing chunk count, general statistical confidence in integrity, or any real-world reliability level. Absence of detected corruption is not evidence that the assumed minimum missing count is correct.

## Demonstration

Archive 17 chunks, sample 3 per round, assumed at least 3 missing chunks, alpha=1/20. First qualifying look under the conditional calculation is round 14. 14 authenticated rounds, 17 unique positions visited, replay rejected, 14 audit events verified. The synthetic demonstration uses complete honest archives to exercise the success branch; detection claims concern a hypothetical fixed alternative of at least three missing positions.

## Tests

44 tests: valid signatures and inclusion, no missing witnesses, duplicate observer, wrong key, forged signature, bad root/epoch/protocol/count/nonce/index/sample, altered chunk/path, insufficient evidence, exact combinatorial bounds, policy freeze, local replay protection after restart, audit tampering, transactional rollback, ancestry/domain declared collisions, and coverage conservation.

## Implementation limitations

- The local implementation imports the WAG-086 Merkle functions from the sibling `invariants/wag086` directory.
- It reuses WAG-086's SHA-256-based challenge sampler, which is a deterministic mapping. The strong distribution/independence assumptions behind the probability expression are **not** cryptographically established by this implementation.
- Private test keys are created in process. Different ancestor/domain strings are only declarations.
- The SQLite ledger is durable locally but not an externally authenticated public anchor.
- Local code and unit tests passed; GitHub CI should be run separately before production usage.

## Next natural invariant — WAG-090

Challenge entropy provenance, precommitted seeds, verifiable unbiased sampling of positions, withheld reveal and adaptive seed grinding. Preserve failed draws without using them to choose a favorable challenge.