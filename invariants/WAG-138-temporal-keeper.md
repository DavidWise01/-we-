# WAG-138 — Sovereign temporal keeper

10 local Python tests passed in 0.103 seconds. A SQLite keeper retains signed WAG-137 bounds, refuses regression and forks through its normal API, and answers single-use random 256-bit challenges with a default five-second deadline. Exact retained history extent is required. 156 ticks = 26 symbolic units.

Limits: the keeper retains checkpoint certificates, not the complete event payloads; it verifies its latest certificate but does not revalidate the entire keeper journal on startup. Direct database deletion can restore an old signed bound, as demonstrated. No independent hardware custody or atomic authorization to mutate, synthetic keys, process-local challenge consumption, declared control roots. Next WAG-139: independently pinned keeper checkpoint receipts and a separate rollback-detection domain; explicitly test common-mode rollback.
