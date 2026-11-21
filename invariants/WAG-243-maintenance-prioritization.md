# WAG-243 · Maintenance Prioritization Under Irrecoverable Deficits

.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

## Bound

Test a one-action-per-tick scheduler choosing **PRESERVE**, **REBUILD**, or **ABSTAIN** from observable loss, energy, trailing energy changes, and material stock. All maintenance operations consume the same explicit energy and material costs as WAG-241/242. The renewable energy and material sources, capacities and transfer losses are unchanged; no future disturbance, scenario label or oracle is used at decision time.

WAG-243 uses a causal EWMA of observed prior recoverable-ceiling loss (factor 0.07). It compares a 12-tick estimated prevented loss (72% prevention efficacy) divided by energy+material expense against reconstructable ceiling deficit divided by its energy+material expense. The higher qualifying score wins a single maintenance slot; otherwise it abstains. A 24-tick trailing energy projection, current-energy reserve floor (0.40 or 0.52 at lower integrity), material floor 0.025, and inferred resource shortage gate are screening constraints. This is a hand-designed prioritization heuristic, **not trained optimization or formally calibrated risk**.

## Reproducible experiment

Fresh seeds 2101–2104, four capacities 5/8/13/21, seven synthetic environment families, and 240/480/960/1920-tick durations. Compare WAG-243 PRIORITY against WAG-242 SELECTIVE, WAG-241 HYBRID and renewable-only BASELINE. 1,792 policy runs, 1,612,800 ticks. External-resource ledger discrepancy 0 at recorded precision.

Observed PRIORITY actions over all runs: **13,131 rebuild, 0 preventive and 390,069 abstentions**. Aggregate priority material used 45.9585 units. The zero prevention count is a substantial counterexample to the intended balanced three-way scheduler: the chosen benefit-per-resource scoring and gates systematically preferred rebuilding or abstaining. It must not be portrayed as a validated preventive policy.

At 1,920 ticks, mean-integrity W/L/T of PRIORITY versus BASELINE: 20/12/80; versus SELECTIVE: 16/16/80; versus HYBRID: 92/16/4 (each out of 112 matched cases). Sixty cases with adverse integrity, survival, reserve or selective-comparison outcomes are preserved in results.json.

Capacity 13 after 1,920 ticks:
- Scar family: PRIORITY mean integrity 0.984625, recoverable ceiling 0.989668, material spent 0.725375; SELECTIVE 0.979837, ceiling 0.98603; HYBRID 0.995036, ceiling 0.996406; BASELINE 0.784497, ceiling 0.641987.
- Combined family: PRIORITY integrity 0.120845, living ticks 246, reserve ticks 138.25; SELECTIVE 0.124212, 249.5, 154.5; HYBRID 0.096746, 206.75, 132.5; BASELINE 0.12359, 250.75, 173.75.

Thus PRIORITY partially reduces unrestricted over-maintenance, but fails to reliably prefer abstention under combined deficit and entirely misses preventive maintenance. Under these synthetic mechanics **repair prioritization still needs calibrated action-value comparisons**, particularly for the prevention-before-damage path.

All physics, energy inputs, material sources and maintenance efficiencies are stipulated synthetic parameters. Ledger conservation is not evidence of physical or biological homeostasis. GitHub Pages deployment remains independently unverified.

## Next bound

WAG-244 · Calibrated Prevent-versus-Rebuild Opportunity Cost. Branch identical observed states into PRESERVE, REBUILD and ABSTAIN with matched future forcing on training seeds only; use a separate holdout to evaluate whether prevention earns approval at all and whether a repair-scheduler can avoid the compound-stress regressions.
