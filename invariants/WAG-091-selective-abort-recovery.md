# WAG-091 — Bounded Selective-Abort Recovery

## Invariant

A frozen, committed sampling attempt that withholds a required reveal is recorded as an aborted attempt. The failure remains in the hash-linked history and cannot itself count as a passing audit. The replacement-round allowance is frozen at genesis.

`ABORT_RECORDED != SUCCESSFUL_AUDIT`

## Reference implementation

`wag091.py` implements an immutable policy, context-bound SHA-256 commitments, three-witness commit/freeze/reveal, an aborted-attempt record, a bounded one-retry pathway, named test beacon input, and SHA-256 rejection sampling without repeated indices. The record chain is append-only in memory.

The local demonstration uses 17 chunks, 3 samples, one permitted retry. W3 withholds on attempt zero; the failure remains recorded. A named beacon value is supplied to the sole recovery attempt. All three witnesses complete attempt one, yielding a bounded three-index sample.

## Validation

46/46 local `unittest` tests passed, including frozen policy, wrong/missing reveals, invalid commitments, duplicate identities, invalid retry attempts, replayed beacon identifiers, exhausted budgets, record tampering, sampling range, and valid finalization.

## Limitations

This is **not proof of non-grindability**. A selective-aborting participant can choose which of a bounded number of attempts survives; one retry still introduces selection opportunity. A caller-supplied beacon is not authenticated, unpredictable, externally anchored, or publicly auditable. The demo uses synthetic secrets, labels, and in-memory audit records; no real distributed process, trusted randomness service, or durable log is involved. The label `anchor` is a declared context token only.

To bound or eliminate grinding in a live system, tie each abort to a fixed penalty/error accounting policy and obtain a non-optional externally verifiable randomness source or a threshold randomness protocol with explicit liveness and bias assumptions.

## Next natural invariant: WAG-092

Threshold entropy, verifiable public randomness, late-reveal resistance, and auditable failure accounting across replacement rounds.