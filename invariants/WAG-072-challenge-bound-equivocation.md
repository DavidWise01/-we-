# WAG-072 — Challenge-Bound Snapshots, Equivocation Certificates and Witness Quarantine

Date: 2026-11-15. Local Python reference tests: **49/49 passed**.

## Rule

Three witnesses W1/W2/W3 present challenge-bound Ed25519-signed snapshot statements. The domain-separated payload includes signer, epoch, round ID, nonce and snapshot hash. Same signer, same epoch+round+challenge, two different authenticated snapshot hashes imply a reproducible equivocation certificate consisting of both full signed statements. Hold the quorum and quarantine the offending signer; do not discard the first observation. Signatures matching a different nonce, epoch or round are rejected in the current gate but are **not**, by themselves, equivocation evidence for the current round.

## Decisions

- REJECT_BAD_SIGNATURE: missing signer or invalid signature; no logged observation.
- REJECT_WRONG_CHALLENGE_OR_ROUND: authenticated but not scoped to the frozen round; no logged observation.
- HOLD_MISSING_WITNESS: fewer than three distinct signed statements.
- HOLD_SNAPSHOT_DISAGREEMENT: three distinct valid witnesses but different snapshot hashes; not automatically malicious behavior.
- LOCAL_SIGNED_AGREEMENT: three signatures over exactly one snapshot, no existing equivocation.
- QUARANTINE_EQUIVOCATION: same signer authenticated two differing hashes in the same round; append proof and quarantine.
- HOLD_EQUIVOCATION: quarantine persists even when three signatures were previously accepted.

## Executed local demonstration

With three in-memory Ed25519 test key pairs, W1/W2/W3 first sign snapshot-A for epoch 2, round recovery-round-7, challenge 0123456789abcdef0123456789abcdef. Gate state initially LOCAL_SIGNED_AGREEMENT. W1 then signs snapshot-B with the same epoch, round, and challenge: proof is verified, W1 quarantined, gate becomes HOLD_EQUIVOCATION. SHA-256 hash-linked in-memory audit has five records (genesis, three observations, equivocation) and verifies. Test suite: 49 passed.

## Limitations

The nonce is supplied by the local synthetic harness, not independently verifiably unpredictable. A real challenge issuer would need CSPRNG challenge generation, signed challenge publication, durable replay registry, key lifecycle/revocation, authenticated ancestry/failure-domain independence, signed externally anchored audit, and bounded storage. Ed25519 key signatures do not establish witness honesty or external source independence. This module is not a Byzantine consensus algorithm. A local acceptance preceding a later-discovered fork is not a finalized distributed commitment.

## Artifacts

- `invariants/wag072/wag072.py` — executable reference.
- `invariants/wag072/test_wag072.py` — 49 local tests.
- `invariants/wag072/WAG-072-ascii.txt` — complete ASCII illustration.
- `docs/index.html` — inline ASCII journal panel.

## Next natural invariant — WAG-073

**Independent equivocation review and witness replacement.** Verify preserved certificates under old-generation keys, check third-party corroboration without re-counting a shared ancestry, revoke/quarantine the culpable signer, and introduce a new independent witness through an authenticated cross-generation handoff. Do not let key rotation erase history or authorize an automatic restored quorum.