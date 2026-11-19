# WAG-166 — Diodic root succession

Actual local execution: nine tests passed in 0.233s. All 2080 prefix-size pairs through 64 records tested. The WAG-165 fixture root is reproduced exactly; 165 to 166 requires five SHA-256 hashes (160 bytes, excluding roots and sizes). Rewritten prefix, malformed hash, extra or truncated proof, and reverse succession tests reject. Inventory 26 including center six; resource total 540.

Limits: trusted prior root required; consistency does not establish transition validity, freshness, independent custody or protection from equivocation between observers. Nonempty prefix only. Fixture records generated deterministically, not a production archive. Next: three-witness pinned root succession and fork detection.
.dlw
