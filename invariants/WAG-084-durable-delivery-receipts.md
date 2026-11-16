# WAG-084 — Authenticated Durable Delivery Receipts

Date: 2026-11-16. Full local Python test suite: 28/28 tests passed.

## Invariant

SIGNED_DELIVERY_ACK != VERIFIED_DURABLE_STORAGE.

A durable-acknowledgment certificate for epoch E, Merkle root R, nonce N is eligible only when three separate declared hosts H1/H2/H3 provide valid Ed25519 signatures over exactly `(domain,epoch,root,nonce,host)` AND the verifier independently reads each persisted checkpoint and matches the signed payload. A missing or altered persistence file invalidates the apparent acknowledgment. A consumed receipt tuple cannot be replayed in the same gate; advancing the epoch requires a new challenge.

## Model

Three local directories simulate three remote hosts. Each node writes a temporary file, flushes and fsyncs the file, atomically renames it, fsyncs the directory, and only then signs an acknowledgment. The verifier checks all three signature contexts and reads back files. An `ack_only` attack models a signer lying about persistence, and is held when storage is absent.

## Results

28/28 Python unittest cases passed. Includes success, signatures, corrupted or missing storage, forged signatures, missing or duplicate hosts, collisions in declared failure domains, epochs/challenges, consumed receipt replay, audit tampering, and restart reads. Simulation consists of one process and one physical computer; it does **not** prove delivery to independent hosts, remote persistence, control independence, Byzantine fault tolerance, or power-loss durability of the physical platform. A hash-linked in-memory decision log is not externally anchored evidence. Receipt replay protection is in-memory and does not itself survive process restart.

## Next: WAG-085 — Remote Challenge, Proof of Storage, and Independence Checks

Have three actual independently controlled hosts respond to fresh verifier-generated challenges, report anchored receipt lineage, and resist simultaneous domain failures. Independent authentication of ownership and physical separation must be established rather than assumed.