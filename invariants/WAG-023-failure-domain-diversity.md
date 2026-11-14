# WAG-023 — Failure-Domain Diversity and Common-Mode Resistance

Instantiated 2026-11-14. Local Python reference: 20/20 unit tests passed.

## Invariant

Three distinct witness roots do not suffice if the witnesses share an unacceptable common failure dependency.

TRUST_QUORUM => THREE_EXACT_AGREEMENTS AND AUTHENTICATED_INDEPENDENT_ROOTS AND FAILURE_DOMAIN_DIVERSITY AND VALID_CHECKPOINT.

Model every witness with:
- event, observation scope, method and exact canonical value
- original observation root and witness identity
- hardware, calibration and operator failure domains
- source and collection provenance

## Reference policy
- Quorum size: 3.
- Require exactly one declared hardware, calibration and operator domain per witness.
- Disallow any shared calibration domain or operator domain between witnesses.
- Shared hardware domains are recorded; stricter policies may disallow those as well.
- Evidence with insufficient or ambiguous domains is held.
- Original observations are appended before the decision, whether the decision is HOLD or CERTIFY_ELIGIBLE.
- Packet replay is rejected; hash chain verification detects local mutation.

## Executed synthetic demonstration
W1 root-A calibration=shared
W2 root-B calibration=shared
W3 root-C calibration=independent
Result: HOLD, COMMON_MODE:calibration:shared.

Three replacement witnesses with distinct calibration and operator domains and exactly matching event/scope/method/observation:
Result: CERTIFY_ELIGIBLE under the reference policy.

## Validation
20 local automated tests passed: valid quorum, too few witnesses, duplicate witness/root, missing root attestation, mismatched observation or time, shared calibration/operator, custom hardware policy, missing or ambiguous metadata, duplicate metadata, failed-evidence retention, packet replay, hash-chain integrity and tampering.

## Caveat
This deterministic prototype checks declared dependency labels and externally supplied authenticated-root claims. It does not cryptographically authenticate identities, detect undisclosed common causes, or provide durable tamper-proof storage. Passing the policy is eligibility for certification, not universal truth.

## Next: WAG-024 — Hidden Common-Cause Discovery
An apparently diverse quorum may still exhibit correlated error. Track co-failure patterns across independent holdouts, search for latent shared causes, and open a new audit without rewriting prior certificates.
