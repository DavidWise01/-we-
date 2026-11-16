# WAG-088 — Adaptive Sampling, Optional Stopping and Global Error Budgets

## Status

2026-11-16. Full reference kernel and tests executed locally. All **56/56 tests pass**. The test uses only simulated responses and a deterministic test secret. No external storage or GitHub CI was tested.

## Exact statistical assumptions

Fix a checkpoint of `N` immutable chunks. The null is `H0: at least m chunks are unavailable`, with the missing set fixed before audit challenges. Each look draws exactly `k` distinct chunk positions uniformly without replacement, with independently generated draws at successive looks and a secret verifier-controlled challenge seed. A valid, independently verified response would determine whether any sampled chunk is missing. The reference's `missing_detected` boolean is **supplied by the test harness, not cryptographically checked**; this kernel is an optional-stopping/statistical decision layer only.

Under H0, the chance of *no detected missing chunk* on a round is at most:

`q = comb(N-m,k) / comb(N,k)`.

The chance of no failures through `t` independent looks is bounded by `p_t=q**t`. Declare a family-wide alpha before testing; assign each audit a fixed allotment `a` (across audits, sum a <= alpha_family). Allocate for look t: `a_t=a/(t(t+1))`. Because `sum_{t>=1} 1/[t(t+1)] = 1`, `sum a_t = a` and by the union bound, the probability of **ever** wrongly certifying H0 using any of the predeclared looks is at most `a` when assumptions hold. No result-dependent budget reallocations are permitted. A halt before threshold gives `HOLD_EARLY_STOP`, not certification. Any detected missing sample gives `HOLD_DETECTED_MISSING`.

Note: Under the fixed missing-set, independent-sampling, one-directional `all rounds pass` event, the bound is conservative. This is not a posterior probability that data is intact, and it is not evidence of cryptographic storage possession.

## Local demo

`N=17, m=3, k=3, a=1/20`, `q=91/170`. At `t=14`, `p=(91/170)^14 <= 1/4200 = a_14`. Unique coverage is 17/17 after 14 rounds in this particular deterministic test schedule. Thus the **local statistical bound** is eligible under the model. Genesis, 14 sampled rounds and certification make **16 verified SHA-256-linked events**.

## Adversarial tests

56 tests cover combinatorial exactness, bad parameters and booleans, predeclared family allocations and attempted overdrafts, fresh sample determinism with an HMAC-derived rejection-sampled Fisher–Yates algorithm, per-round sample uniqueness and domain separation, nonce changes and replay, early-stop and missing-data holds, no premature certification, no double certification, unique coverage accounting, hash-chain tampering, and the executed 14-round example.

## Limits

The demo seed is public and deterministic; never use it for live unpredictability. The kernel must integrate with WAG-086 signed Merkle chunk proofs and WAG-085 authenticated storage reads before observational data can be trusted. Three hosts evaluating identical samples do not constitute three statistically independent samples. Signed witness identities and independent hardware are not authenticated here. The in-memory audit chain is not off-host anchored or tamperproof. Statistics do not substitute for evidence authentication.

## Next invariant — WAG-089: Authenticated Adaptive Sampling

Bind each per-round statistical observation to fresh signed WAG-086 Merkle inclusion and retrieval evidence, an immutable checkpoint root, complete source ancestry, and a durable consumed nonce. Preserve a failing chunk as a reproducible counterexample before any new challenge or hypothesis revision.