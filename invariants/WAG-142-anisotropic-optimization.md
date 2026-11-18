# WAG-142 — Anisotropic resistance optimization

10 tests passed locally in 0.039s. Separate declared domain maps for erasure, unavailability and equivocation. Exact minimum set-cover cuts and Pareto frontiers. All 29 quorum configurations for n=3,5,8,13 tested. Example maximin selections q=2,4,6,9 respectively; ties are possible. n=13,q=9 gives (13,5,5) under independent domains. Shared availability collapses the availability axis to 1.

Scope: structural threshold model, not actual deployment or Byzantine consensus. Complete copies, honest non-equivocation, symmetric quorum and complete declared dependencies assumed. Quorum selection objective max min(Ra,Rf) is a design choice, not a universal optimum. No costs or probabilities modeled. Exact enumeration exponential; no physical analogy implied. Next: WAG-143, correlated portfolios and explicit cost-constrained placement.
.dlw
