# WAG-099 — Durable Conflict Evidence and Revocation-Aware Witnesses

Date: 2026-11-16. Status: local reference implemented; **18/18 unittest cases passed**.

## Invariants

`HISTORICALLY_VALID_SIGNATURE != CURRENTLY_AUTHORIZED_WITNESS`

`RECOVER_CONFLICT => VERIFY_ALL_THREE_SIGNED_RECEIPTS AND MATCH_EXACT_FULL_INCIDENT`

An authenticated authority signs an effective revocation epoch. Earlier correctly signed observations remain historically verifiable; signed observations at/after the effective epoch are ineligible. A conflicting effective epoch signed by the authority is quarantined. A complete split-view incident contains the original and conflicting snapshots, not only their hashes, and is replicated into three separately named simulated custodian directories. Each signs a SHA-256 digest of the exact incident. Recovery checks all three signatures, distinct custodian identifiers and identical content. Missing, invalid or discrepant evidence fails closed. Files use O_EXCL creation and fsync.

## Executed adversarial tests

18/18 Python unittest tests passed locally: full recovery, restart reconstruction, missing receipt, modified incident, forged signature, cross-custodian replay, duplicate publish, partial publish, complete conflicting content, valid current observation, pre-revocation historical observation, at-revocation rejection, post-revocation rejection, forged revocation authority, forged witness, conflicting revocation epochs, unknown witness and incorrect scoped epoch.

## Limits / evidence honesty

These are **three simulated stores on a single machine**, using generated test keys. They do not prove external physical independence, authenticated real-world revocation chronology, off-host immutability, threshold Byzantine agreement, or immunity to a privileged operator replacing keys and every receipt. Revocation evidence is currently in memory, not a persistent authenticated timeline; a restarted trust registry must reload it from a separately verified source. Partial distributed publication is not atomic and needs retry/reconciliation. Receipt files are create-only under ordinary operation, not immutable under full local administrator control. A previously signed message with a falsely backdated epoch is not automatically legitimate. Historical validity here means signature and claimed epoch pass the reference policy, not proven pre-compromise chronology.

## Files

- Python reference and test suite available as local conversation downloads; the technical checkpoint and ASCII HTML are published in GitHub.
- Interactive narrative in `witness/WAG-099.html`.

## Next natural invariant — WAG-100

An independently witnessed revocation timeline: durably anchor key authorization transitions, prove observation chronology relative to effective revocation, and recover complete conflicts under partition or rollback without trusting caller-provided epochs.

`{{ preserve [signed past -> revoke -> reject new -> archive all conflicts] }}`
