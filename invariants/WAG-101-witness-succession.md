# WAG-101 — Revocation-Aware Successor Enrollment

Date: 2026-11-16. Local Python reference: **17/17 unittest cases passed**.

## Invariant
`NEW_QUORUM != NEW_HISTORY`.

Generation 0: W1/W2/W3. Generation 1: W2/W3/W4. Preserve the pinned checkpoint and full history of W1 while preventing W1 from certifying generation 1. Require an Ed25519 authority-signed handoff, distinct signed departing-W1 and incoming-W4 acknowledgements, a derived fresh succession nonce, and signatures of W2, W3 and W4 covering generation, pin, nonce and identity.

The Python reference uses canonical JSON messages and a SQLite transactional generation/state table plus a SHA-256-linked event log. The 17 local tests cover valid succession, membership, preserved history, fresh signature, revoked witness, restart, replay, forgery, missing or swapped quorum, bad acknowledgements, bad pin, atomic rejection, audit tampering, shared declared ancestry, and stale nonce.

## Scope limits
Synthetic generated keys on one host; ancestry identities are **declared**, not verified operationally. No external timestamp, off-host transparency, distributed Byzantine quorum, authenticated custody or independently witnessed revocation. The local audit and database are not secure from complete privileged replacement; recovery needs independent anchors. Only g0 to g1 is modeled, and this normal handoff requires cooperation from departing W1.

The exact executed Python files are available in the conversation's WAG-101 download bundle. This repo checkpoint stores the specification, ASCII record, JSON metadata and HTML panel; it does not yet contain the Python source.

## Next WAG-102
Emergency succession after lost/uncooperative departing witness, with independent authenticated authorization and durable exceptional-action receipts. Preserve all historical evidence.
