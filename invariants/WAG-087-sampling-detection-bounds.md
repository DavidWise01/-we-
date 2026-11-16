# WAG-087 — Statistical Detection Bounds and Rotating Sampling Coverage

## Executed result

The locally tested Python kernel completed **51/51 unittest tests** on 2026-11-16. It records exact detection probabilities as reduced integer fractions, keeps per-host and shared sample coverage distinct, rejects repeated challenges, and verifies a SHA256-linked in-memory audit ledger.

## Formal model

For fixed N chunks, m missing chunks and an unpredictable uniform sample of k distinct positions drawn without replacement:

`P(detect at least one missing chunk) = 1 - C(N-m,k)/C(N,k)`.

For independent uniform **rounds** of sizes k_i against a fixed missing set:

`P(detect at least once) = 1 - product_i (C(N-m,k_i)/C(N,k_i))`.

The latter is conditional on independent rounds and stable missing data, and is **not a posterior probability** that all bytes are present after passing. Overlapping sampled positions count once for coverage. Three hosts performing the same challenge provide three reported responses, not three independent selections of positions. A declared distinct source ancestor does not prove distinct controlling infrastructure. Each round's signing and Merkle inclusion proofs are provided by WAG-086; this reference consumes declared audit outcomes rather than re-verifying those signatures.

## Executed example

A 17-chunk archive, three hosts W1/W2/W3, two rounds sampling three positions each per round. The sample sets are identical across hosts within each round. The deterministic fixture generated six unique positions in total and each host was measured at 6/17 coverage. A single round detects three fixed missing chunks with probability 79/170 (about 46.47%) under the uniform randomness model; two independent rounds yield 20619/28900 (about 71.35%). The in-memory ledger has seven verified records: one genesis, six host audit reports.

## Control and limitations

- SHA-256 ranking with supplied seed makes sampling deterministic, **not intrinsically unpredictable**. The seed must be securely chosen and hidden until the host's archive is committed; this code does not implement that cryptographic commitment or secure remote delivery.
- Host ancestors are declarative. No evidence of real independent physical hosts is claimed.
- Population size, missing count, and failed/missing chunk set must be held fixed for the stated formula. Adaptive adversaries and selective response omissions require further modeling.
- `cumulative_detection_bound` multiplies theoretical per-round miss probabilities, not realized evidence independence. Actual repeated, correlated, or adversarially influenced challenges cannot justify this multiplication.
- Hash-linked in-memory records are tamper-evident under a trusted head but not durable, externally anchored records.
- This is a synthetic statistical planning model, not proof of full retrievability.

## Published artifacts

- `invariants/wag087/wag087.py`: Python kernel
- `invariants/wag087/test_wag087.py`: 51 local unit tests
- `invariants/wag087/WAG-087-ascii.txt`: ASCII visual story
- `invariants/WAG-087-sampling-detection-bounds.md`: this specification
- `docs/index.html`: appended ASCII journal entry

## Next — WAG-088

**Adaptive Sampling and Optional-Stopping-Safe Evidence:** fix audit schedules or use anytime-valid error control, hold a global failure budget, record selective host nonresponse, and refuse to upgrade theoretical detection bounds using dependent observations.