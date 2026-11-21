# WAG-232 · Decision-calibrated prediction

.dlw · {24/[2]/[4]/(3)/(3)/(1)/(1)}

WAG-231 forecasts energy but does not establish that acting on its forecast improves protection. WAG-232 calculates a modeled one-step paired action comparison using the same available observations: the original WAG-230 protection fraction versus reduced protection. It applies estimated energy savings, modeled extra damage, and a margin from trailing variability. The decision gate falls back to WAG-230 when estimated advantage is too small. No future forcing is supplied to the controller.

IMPORTANT: this is a **model-estimated counterfactual**, not observed proof of a causal effect and not a calibrated uncertainty interval. Margin and horizon multipliers are fixed heuristics. Actual paired policy rollouts on same seeds provide the empirical *synthetic* outcome comparison. Same five WAG-228 families and 5/8/13/21 capacities; eight new seeds 801–808, four modes: WAG-232 decision, WAG-230 graded, WAG-231 forecast, WAG-229 REST. 640 runs, 153600 ticks. On unrounded mean integrity: decision vs graded 7 wins, 49 losses, 104 ties. Proposed interventions 5308, accepted 2970, rejected 2338. Forecast RMSE 0.070246, matured predictions 36480. Full representative trajectories and all adverse comparisons are recorded.

This is deterministic synthetic testing, not biological validation. Commit success does not establish GitHub Pages deployment.
