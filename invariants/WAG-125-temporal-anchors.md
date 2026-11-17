# WAG-125 — Antisotropic temporal anchors

Three SQLite anchor files retain complete signed chains. Replay validates every transition from genesis, conservation of 156 ticks, mesh binding, and three distinct Ed25519 signatures. Inspect requires identical verified chains; missing, invalid, divergent or lagging chains hold. Ten local tests passed in 0.167 seconds, including a counterexample: simultaneous rollback of every anchor to genesis is undetectable without an external freshness witness. Synthetic keys, same host, trusted read channels; no independent custody, non-equivocation or distributed consensus. No automatic repair. Past observes, present deserves, future reserves are symbolic labels, not physical time claims.

Next: WAG-126 independently retained freshness floor, with an explicit replay threat model.
