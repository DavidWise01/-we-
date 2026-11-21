# WAG-241 · Material-Backed Recoverability

.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

WAG-241 preserves the WAG-240 renewable energy supply, finite energy-storage limit, transfer losses, and frozen WAG-235 action table. It introduces a **separate, explicitly external bounded material input**: 0.0009 material units per tick, maximum stock 0.50, initial stock 0.20. All four policies receive the same resource opportunities: baseline (never uses material), preventive reinforcement, structural reconstruction, and hybrid.

Preventive reinforcement acts on an observed pressure threshold (>0.55), consumes 0.0015 material and 0.0012 energy, and reduces that tick's incremental scar ceiling loss by 72%. Reconstruction acts while energy >0.35, integrity >0.15 and ceiling <0.995; consumes 0.0035 material and 0.004 energy; can rebuild at most 0.0025 structural ceiling and restore at most 0.0012 integrity in one tick. Reconstruction is *new, costed structure*, not revision or erasure of previously logged damage. Material stock is hard-capped and no stored material is created spontaneously. Historic scar evidence is preserved in the trajectory.

Experiment: four independent seeds (1901–1904), four capacities (5/8/13/21), seven synthetic environment families and horizons 240, 480, 960 and 1,920 ticks. Four policy arms, 1,792 simulation runs, 1,612,800 ticks. Recorded source/material ledgers reconcile at reported precision. Hybrid aggregate material consumed 199.629 units; structural ceiling reconstructed 13.0575; preventive actions 120,899; reconstructive actions 5,223.

At 1,920 ticks, hybrid versus no-maintenance baseline mean-integrity outcomes: 16 wins, 78 losses, 18 ties out of 112 comparisons. Against prevention alone: 20 wins, 12 losses, 80 ties. Against reconstruction alone: 12 wins, 82 losses, 18 ties. At capacity 13, scar scenario hybrid mean integrity 0.995077 versus baseline 0.785158; combined disruption hybrid 0.101270 versus baseline 0.125946 and hybrid surviving ticks 219.25 versus 254.5. **This is not a general improvement.** The cost of unnecessary maintenance can accelerate collapse under severe resource constraints. Preserve all 314 recorded adverse cases.

Scientific limits: energy/material injection and repair efficacy are stipulated simulator assumptions, not experimentally measured biological or physical processes. Mathematically balanced ledgers do not establish thermodynamic viability. Trajectories in results.json are sampled for representative cases; the full source reproduces all ticks deterministically. GitHub Pages deployment remains separately unverified.

Next bound: WAG-242 · Selective Maintenance and Repair Affordability — learn to abstain from costly maintenance when expected structural benefit is lower than the resource opportunity cost.
