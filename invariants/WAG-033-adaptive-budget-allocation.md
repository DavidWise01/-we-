# WAG-033 — Adaptive Statistical Budget Allocation and Irrevocable Registration

Status: implemented in GitHub on 2026-11-14; tests committed but not executed in this environment (local download blocked by outbound DNS).

## Invariant
An agent may allocate a portion of the remaining hive-wide familywise false-alarm budget using past completed-epoch information, but cannot raise a test's allocation after inspecting its outcome. New generations inherit both the allocation and accumulated e-process; spawning a child does not refund or reset alpha.

REGISTER(test, alpha) => PRIOR_EPOCH_INFO AND alpha <= REMAINING AND IRREVOCABLE

INHERIT(test, child) => SAME_TEST AND SAME_ALPHA AND SAME_EVALUE AND VALID_LINEAGE

## Executable reference
- invariants/wag033/wag033.py — Decimal-based budget ledger, frozen test registrations, agent inheritance, bounded anytime-valid e-process, hash-linked audit sequence.
- invariants/wag033/test_wag033.py — 20 unittest cases covering exact budget sums, overspend rejection, prior-epoch registration, lineage, inheritance, replay, root reuse, invalid observations, threshold alarms, atomic rejection and ledger changes.

## Reference demonstration (not execution-verified)
Initial family budget 0.05. Register high-priority test with 0.03 and low-priority test with 0.005. 0.015 remains. Descendant inherits the first test, not a fresh alpha allocation. Ten X=1 updates at lambda 1 and mu 0.5 yield E=1.5^10=57.6650390625; threshold 1/0.03=33.333..., so the high-priority test is expected to alarm.

## Limits
- evidence_epoch is a claimed tag supplied by the caller; this prototype does not cryptographically prove information was available before registration. A production registry must bind allocation decisions to immutable committed evidence snapshots.
- Priority is caller-assigned and not itself an enforced optimization policy.
- Unique root labels are not independent provenance authentication.
- Decimal arithmetic avoids simple budget rounding but mutable Python objects and in-memory hash links are not durable, externally anchored storage.
- The alpha-spending guarantee requires each constituent e-process to be valid under its conditional null assumptions.
- Unittest results are not claimed until actually executed.

## Next: WAG-034 — Budget Allocation Provenance and No Lookahead
Every adaptive allocation must cite the exact completed evidence snapshot available when the allocation was made. Reject future-looking or retroactively edited priority rankings, distinguish training/selection information from confirmatory test evidence, and preserve registration causality across agent generations.
