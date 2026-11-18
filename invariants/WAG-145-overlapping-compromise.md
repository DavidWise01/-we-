# WAG-145 — Overlapping compromise geometry

Actual local Python execution: 10 tests passed in 0.098s. For n=13, q=9, thresholds for erasure, availability and equivocation are (13,5,5). Each declared domain contributes a set of affected witnesses separately per axis. Enumerate combinations by cardinality, returning all minimum sets crossing every requested threshold. Independent domains give joint cut 13; added synthetic backup/provider/admin/recovery dependencies give joint cut 3, uniquely (backup,provider,recovery).

Limits: simultaneous threshold capability, not a demonstrated executable attack or actual infrastructure audit. A disabled signer might be unable to equivocate concurrently; ordering and compatibility of effects are not represented. All evidence copies complete, dependencies declared, domain costs equal, no probability model. Exact enumeration exponential. Next WAG-146: distinguish compatible simultaneous effects from ordered compromise and recovery.
.dlw
