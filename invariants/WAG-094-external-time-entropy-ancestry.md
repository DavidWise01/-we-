# WAG-094 — Signed Ordering and Entropy-Source Ancestry

Status: implemented reference with 43 local Python unit tests passing. No external timestamp or live beacon service is accessed.

## Invariant

`SIGNED_RELEASE_ORDER != PHYSICALLY_PROVEN_PRECOMMITMENT`

Jane freezes a hash of the archive, epoch, and round in a signed commitment statement. Two individually signed beacon release statements must refer to that exact root, epoch, and round and declare integer logical release slots strictly after the signed commitment slot. The clock and beacons must have three distinct declared identity, ancestry, operator, and failure-domain values. The gate derives a sample exactly once from a canonically encoded commitment and both releases, with SHA-256 rejection sampling to eliminate modulo bias.

## Threat tests

- Wrong root, round, epoch, signer, missing signature, malformed output, duplicate release, non-increasing logical slot, shared declared ancestry and repeated sample attempt all fail without approving a round.
- An in-memory append-only SHA-256 hash chain records genesis, signed commitment, each beacon release, and the selected positions. Mutation is detected by verification.
- The order of two beacon identities is fixed and the sample is deterministic from authenticated test messages.

## Explicit unproven properties

Signing a statement that *claims* slot 12 before a statement that *claims* slot 13 is not a trusted external timestamp. These test authorities are created in process and no witness corroborates real delivery times. Signatures do not show that operators lack shared hidden control or that beacon outputs were unpredictable before signing. An actual external system must independently capture, timestamp and persist the archive commitment before the beacon becomes observable; then validate the beacon's actual release schedule, provenance, transparency and unpredictability. The observed graph has only three declared roots, not three verified independent operators. Successful tests are not evidence of physical off-host operation.

## Executed tests

`python -m unittest discover -s /mnt/data/wag094 -p test_wag094.py -q` produced `Ran 43 tests ... OK`.

## Artifact files

- `invariants/wag094/wag094.py` — full Python reference
- `invariants/wag094/test_wag094.py` — 43 unit tests
- `invariants/wag094/WAG-094-ascii.txt` — text illustration
- `docs/index.html` — embedded ASCII journal entry

## Next natural invariant: WAG-095

Capture signed checkpoint commitments in **external** append-only transparency services and independently timestamped receipts, verify their release ordering against a known schedule, and compare independent observers' logs. Hold when the only ordering evidence is self-declared logical slots.