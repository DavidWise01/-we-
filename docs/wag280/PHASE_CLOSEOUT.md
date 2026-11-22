# WAG-280 — Phase III Final Freeze and Research Release

**Release:** WAG-III-v1.0
**Phase:** WAG-269 through WAG-280, 12/12 complete
**Status:** CLOSED research artifact, not controller promotion
**Canonical geometry:** `---@---@---@---@---{} → {\a{b/}} → one action`
**Reference controller:** WAG-261 (unmodified)
**Experimental candidate:** WAG-276 fixed-weight crystalline cubit controller (unpromoted)
**Exploratory extension:** WAG-277 four-junction lattice-chain terminal (unpromoted)
**Mark:** .dlw

## Findings

The crystalline mesh uses eight opposed rail pairs and three deterministic propagation passes. The chain connects four eight-neuron junctions into the nested crystalline terminal. Signal exchange never creates physical material or energy, and repair execution remains with WAG-244.

In WAG-276's 288-run development comparison (96 conditions), 240-tick full survival was 34/48 crystalline versus 29/48 WAG-261; at 480 ticks both were 23/48. Crystalline structural integrity regressed in 65/96 cases.

WAG-277 then evaluated the precommitted frozen candidate on withheld seeds 6401–6404 at 480 and 720 ticks: 128 matched conditions, 384 policy runs. Full survival was 29/64 for both at 480 ticks and **28/64 crystalline versus 29/64 WAG-261 at 720 ticks**. Integrity regressed in 82/128 matched cases. The extra lattice-chain arm was exploratory, not eligible for promotion.

WAG-278 preserved eight minimum observable failure prefixes: two survival losses and six integrity failures. The common first differing action occurred at tick 55. These prefixes are not independently minimized causal inputs.

WAG-279 changed only tick 55 in those eight cases, substituting the matched reference action for the crystalline action. No lost survival case was rescued, three mean-integrity cases improved, and five worsened. No new rule was promoted.

## Disposition

**DO NOT PROMOTE.** WAG-261 remains the reference. WAG-276 crystalline and WAG-277 lattice-chain controllers remain research prototypes with untrained weights, insufficient calibration, and no independent physical validation.

All experiments, counterfactuals, and replay traces use a single synthetic simulator ancestry; no multiple-witness or Byzantine acceptance gate was introduced.

## Immutable lineage

- WAG-269–271: Pareto baselines and repair timing
- WAG-272–273: two nested cubits and calibration
- WAG-274–275: unfamiliar forcing and regret ledger
- WAG-276: canonical crystalline geometry and candidate freeze
- WAG-277: withheld long-horizon trial and exploratory lattice chain
- WAG-278–279: reduction of observed failures and single-action falsification
- WAG-280: final audit and research release

Release artifacts: [manifest](./release-manifest.json), [receipt](./release-receipt.json), [verifier](./wag280.js), and [closed tracker](../wag269/phase-progress.json).

Future improvements belong to a **new phase** with fresh preregistered trials, independent environment classes, and a new controller candidate. Do not alter these frozen historical receipts.

GitHub Pages source publication is checked, but live Pages serving is not verified.

**One primitive. Opposed crystalline rails. One physical action. Immutable failure evidence. .dlw**
