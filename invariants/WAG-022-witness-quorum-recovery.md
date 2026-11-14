# WAG-022 — Witness Quorum Recovery

Status: instantiated reference implementation, November 14, 2026.
Local Python: `wag022.py` and `test_wag022.py`; **18/18 tests passed**.

## Governing invariant
When a certified witness is invalidated, retain its historical certificate but suspend current operational reliance. Restore operational trust only with a new three-witness certificate whose remaining and replacement observations agree exactly and have independently evidenced ancestry.

`RECOVER(C2) => PRESERVE(C1) AND SUSPEND_ON_REVOCATION(C1) AND EXACT_THREE(C2) AND INDEPENDENT_ANCESTRY(C2) AND FRESH_REPLACEMENTS(C2) AND APPEND_ONLY_LINEAGE(C1,C2)`

## Reference trace
- C1 certified with three matching observations, roots A/B/C.
- Root C invalidated; operational status becomes SUSPENDED.
- Agent D supplies a new packet with matching event, scope, method and value and a distinct ancestry root.
- New C2 certificate refers to C1 and the selected observation packets A/B/D.
- Historical C1 is untouched and still addressable. Eight-record hash-linked ledger verifies.

## Implemented checks
18/18 local tests pass: initial certification, suspension, successful recovery, old-certificate preservation, conflicting replacement, shared ancestry, missing root authentication, wrong replacement count, no-loss recovery rejection, stale head, packet replay, duplicate revocation, unknown revocation, replacement of two lost witnesses, revoked ancestry reuse, chain verification, tamper detection and demo.

## Limits
Prototype is deterministic single-writer and in-memory. The externally supplied authenticated-root set is not itself cryptographic verification. SHA-256 hash links alone do not provide durable tamper-proof storage. Revocation and recovery records are historical facts, not retroactive edits to the original certificate.

## Next natural invariant — WAG-023: Quorum Diversity and Correlated Failure
Even three distinct ancestry roots may share the same collection infrastructure, timing source, sensor calibration, software dependency or adversarial control domain. Certification should require failure-domain diversity and expose common-mode risk explicitly, not merely count distinct root labels.
