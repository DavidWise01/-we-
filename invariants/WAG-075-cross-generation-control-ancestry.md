# WAG-075 — Cross-Generation Control Ancestry and Succession Isolation

Date: 2026-11-15. Local synthetic Python reference: **58/58 unit tests passed**.

## Core invariant

New name + new key + new evidence-root label does **not** imply independent control. Before accepting W4 in place of compromised W1, recursively trace the transitive controlling-authority ancestry graph and reject any candidate whose ancestry intersects W1's compromised controlling lineage or either surviving reviewer's controlling lineage.

`ROTATE_OK => DISTINCT_CONTROLLER_ANCESTRY && TWO_REVIEWS && THREE_FRESH_RECEIPTS`

## Test scenario

- Old ring: W1 org-x, W2 org-y, W3 org-z. All have distinct declared evidence roots, keys, operators and failure domains.
- Candidate `shell-w4` has a new key and evidence root but is a descendant of `org-x`. Deny, append a rejection record.
- Candidate W4 `org-w` does not share declared controller ancestry with any active witness. Admit proposal with two distinct surviving reviewer acknowledgements.
- Rotate to W2/W3/W4 in generation 1. Preserve old W1 identifier and all historical audit entries. After three fresh, generation-bound receipt IDs, the local declared succession gate accepts.
- Demo: 9 SHA-256 hash-linked records; all pass local ledger verification.

## Security boundaries and limitations

The two review acknowledgements and receipts in this WAG-075 model are *declared identifiers*, not cryptographically authenticated signatures or external identity proofs. A malicious person can claim a new authority `org-w` even if it is secretly controlled by `org-x`: the gate cannot know otherwise. Transitive ancestry is evaluated only within the supplied declared DAG; omissions or false declarations defeat the independence claim. No live-domain checks, consensus, hardware attestation, or public anchoring are provided. The ledger is memory-resident and hash-linked, not externally immutable. Therefore decision names explicitly include `LOCAL_DECLARED`.

## Local regression coverage

58 tests: old/new controller ancestry, direct/transitive/shared control, cycles, reused names/keys/roots, reviewer authorization and count, generation mismatch, repeat receipts, quorum holds, old identity preservation, hash-chain tampering and failed-transition atomicity. Local demo prints 9 ledger records and three active witnesses.

## Next WAG-076

**Authenticated Control-Ancestry Claims, Registry Cross-Checks and Unknown-Root Holds.** Bind authority lineage claims to signed registry assertions, detect contradictory or missing upstream ancestry, retain confidence/failure provenance, and refuse to mistake unknown ancestry for verified independence. Model multiple evidence origins without triple-counting copied source mirrors.