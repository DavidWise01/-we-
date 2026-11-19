# WAG-165 — Ancestral compression

Actual local Python execution: eight tests passed in 0.040s, all 165 inclusion proofs verified. Domain-separated SHA-256 Merkle tree, largest-power-of-two split, canonical JSON records. 29,033 bytes of canonical records; proof path 96–256 bytes, excluding record/index/tree size/root. Inventory 26 and credits 540 conserved. Root 1e2b2778ad378674705931fcfe3aa85a8a0372a858612a2f539e291f61f08f25.

Limits: generated fixture reconstructs WAG-164 inventory trajectory but changes the checkpoint schema and parent hash domain; not an exact import of WAG-164 checkpoints. Inclusion is not transition validity or proof of append-only growth. No trusted external anchor, consistency proof, signed witnesses, or persistent production archive. Full records reproducible via records(), not independently archived. Verifier intended for byte-hash paths, not hardened against arbitrary malformed inputs. Next: prefix consistency proof and authenticated root succession.
.dlw
