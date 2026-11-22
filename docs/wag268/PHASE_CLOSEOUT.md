# WAG-II v1.0 — CLOSED (WAG-257–WAG-268)

**Closure date:** 2026-11-22  
**Phase:** Hegemonic Diodic Control  
**Progress:** 12 / 12 = 100% (all planned experiments and release checks accepted)  
**Decision invariant:** one ranked permissible action; survival priority, then resource safety, then structural integrity; no retrospective controller switching  
**Frozen controller:** WAG-264 selected WAG-261 baseline for capacities 5, 8, 13, and 21. This selection remains unchanged.

## What passed

- Executable policy and accounting experiments were committed for WAG-257 through WAG-268.
- Resource-fee persistence was tested with 64 forced transactions over 32 synthetic cases; next-tick continuity held.
- WAG-264 froze training-only policy selections before running the 256 holdouts.
- WAG-265 subjected the unmodified frozen policy to four unfamiliar synthetic stress schedules and preserved all results.
- WAG-266 preserved 43 failing cases and four locally minimized, replayable counterexamples.
- WAG-267 compared 768 policy runs (three controllers × 256 identical scenarios) with a predeclared lexicographic ranking.
- WAG-268 replayed 24 paired controller runs deterministically and revalidated all four minimized failures. All 28 checks passed. This is **sampled replay**, not a universal proof.

## Frozen final ranking (synthetic, 240 ticks)

| Rank | Controller | Full-survival episodes / 256 | Mean integrity |
| ---: | --- | ---: | ---: |
| 1 | No repair (diagnostic) | 218 | 0.912067 |
| 2 | Rejected adaptive | 214 | 0.919914 |
| 3 | Frozen WAG-261 | 213 | 0.920917 |

**Interpretation:** Under the survival-first ranking, no-repair leads, but at the cost of lower structural integrity. WAG-261 remains the integrity leader. This ranking is not permission to change the frozen policy.

## What failed and remains unresolved

1. **43 / 256 frozen-policy cases lost at least one survival tick** under unfamiliar stress. Phase closure does not mean the physical or simulated robustness problem is solved.
2. WAG-263's downgrade policy caused substantial integrity regressions despite occasional survival gains. WAG-264 correctly rejected it on its predeclared integrity tolerance.
3. The uncertainty estimates, policy training, and stress results share a **single synthetic simulator ancestry**; no independent external or physical evidence supports generalization.
4. The 240-tick test horizon does not establish long-term value of no-repair versus structural-recovery controllers.
5. The WAG-266 reductions are greedy/local and cannot claim global minimality.
6. **GitHub Pages live serving was not verified.** Committed HTML/source files exist, but deployment status is separate.

## Canonical frozen release pointers

- [Machine-readable manifest](./release-manifest.json)
- [Deterministic replay receipt](./replay-receipt.json)
- [Frozen policy](../wag264/frozen-policy.json)
- [Unfamiliar-stress receipt](../wag265/receipt-5501-5504.json)
- [Failure archive](../wag266/receipt-5501-5504.json)
- [Predeclared ranking and 768-run receipt](../wag267/receipt-5501-5504.json)
- [Living final lab](./index.html)
- [Original charter](../wag257/PHASE_CHARTER.md)

The original charter is preserved unchanged as an historical open-phase snapshot. The final manifest and this closeout record supersede that status without silently rewriting earlier evidence.

## Next phase (new boundary, no retroactive Phase II alteration)

**Phase III, first candidate WAG-269:** Survival–integrity Pareto frontier at longer horizons, using the WAG-268 freeze as the immutable baseline. Require fresh unseen seeds and sustained famine/shock tests before any conditional repair policy can be promoted.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
