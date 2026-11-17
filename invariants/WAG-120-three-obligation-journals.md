# WAG-120 — Three persistent obligation journals

November 17, 2026. 10/10 local Python unittest cases passed.

Conserve 156 integer ticks (26 symbolic units) across stored and in-flight inventory. H→O→N→H. Three separate SQLite files contain the same hash-linked event history. A partial publication holds further operations. Explicit administrative replay completes a valid common-prefix suffix; conflicting logs are rejected. Repeated receipts cannot credit twice.

Limits: single coordinator and same physical host; no cryptographic witness signatures, independent custody, generation enforcement, or distributed consensus in this standalone journal experiment. The longest-compatible-suffix repair rule is unsafe against an adversary inserting a valid-looking event in one journal; it is only a trusted-writer crash recovery model. The WAG-119 signature and fencing gate must be integrated before deployment. No physical QCD claim.

Next WAG-121: authenticated prepare/commit certificates, witness non-equivocation, and fail-closed recovery of partially published events without trusting the longest suffix.
