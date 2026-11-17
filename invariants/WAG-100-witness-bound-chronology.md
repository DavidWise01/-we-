# WAG-100 — Witness-Bound Revocation Chronology

2026-11-16. Local reference: 12/12 unittest cases passed.

CLAIMED_SIGNING_TIME != WITNESSED_OBSERVATION_TIME

Three configured Ed25519 observers sign the exact observation and revocation packet digests, observer identity, pinned checkpoint, observed position, cutoff and head position. All three must agree on observation and cutoff. Eligibility requires observed position strictly before effective revocation. Five distinct public keys (three observers, revocation authority, witness) and distinct declared observer ancestry labels are required.

Run: cd invariants/wag100 && python -m unittest -v

Limits: synthetic keys on one host; logical positions are assertions, not verified timestamps or Merkle inclusion. No durable chronology, monotonic restart protection, nonce freshness, actual remote custody, or successor enrollment. The pin is caller-provided. Signed contradictory views are held but not durably archived. A colluding observer set can backdate. This is historical eligibility only, not final trust. Malformed arbitrary packet structures are not exhaustively tested.

Next WAG-101: authenticated successor enrollment linked to the last certified pin, with durable revocation history and a fresh three-witness challenge, without rewriting old evidence.
