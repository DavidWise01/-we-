# WAG-093 — Beacon Provenance, Precommitted Archive Roots and Merkle Observations

Date: November 16, 2026.

## Rule

A signed sampled-storage response only counts when it is bound to: a previously frozen archive root and chunk count; an epoch-bound signed beacon statement; the *single* derived challenge/sample; a named witness key; and valid Merkle inclusion proofs for the requested chunk bytes.

`PERSIST_PRECOMMIT -> VERIFY_SIGNED_BEACON -> FREEZE_SAMPLE_ONCE -> VERIFY_3_MERKLE_RESPONSES -> CERTIFY_LOCALLY`

## Implemented reference

- Archive Merkle root, chunk count, and archive-receipt identifier are frozen in SQLite before the beacon statement is accepted. Root immutability is enforced by an epoch primary key and state transitions.
- An Ed25519 beacon signature is checked against the expected test public key and its epoch/counter/output body.
- A domain-separated SHA-256 challenge binds the frozen root and exact signed beacon output. Sampling selects unique chunk indices without modulo bias using 256-bit rejection sampling.
- Three distinct hosts with distinct *declared* evidence ancestors and failure domains produce Ed25519 responses covering the exact challenge and inclusion paths.
- SQLite transactional gate either verifies all three and certifies once, or rolls back; a restart preserves frozen/challenged/certified state.
- SHA-256 hash-linked audit records detect tested local event-history tampering.

## Local results

45/45 Python unittest tests passed with resource warnings treated as errors. Demo: 17 chunks, sample indices (1, 5, 9), 3 accepted host responses, repeated certification blocked, 3 audit events verified. Adversarial tests include forged beacon and host signatures, modified chunks, altered paths, wrong epoch/challenge, duplicate responses, redraws, malformed samples, and process restart.

## Scope and limitations

The reference accepts a self-reported archive-receipt string and has no trusted external timestamp or anchored prior commitment. Signed beacon output is generated from local keys, not an independently sourced public randomness service. The code confirms cryptographic data consistency, not remote availability, real identity, or noncollusion. No end-to-end statistical detection confidence is certified here; WAG-088/089 separate statistical assumptions from observed authenticated samples. The Merkle tree uses SHA-256 domain separation with odd-node promotion; consumers must match that tree definition exactly. The event chain is not externally anchored.

## Next natural invariant — WAG-094

External timestamp anchoring and beacon unpredictability: bind the archive freeze to an authenticated third-party timestamp or consensus checkpoint, authenticate the beacon provider and timing, enforce monotonically increasing beacon rounds, and preserve conflicting deliveries and unavailable attestations.