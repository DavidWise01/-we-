# WAG-054 — Fallback Entropy Independence and Recovery Closure

Status: instantiated 2026-11-14. Local Python implementation passed 24/24 unittest cases; demonstration produced nine valid hash-linked records.

## Natural invariant
ACCEPT_RECOVERY => DISJOINT_ANCESTRY AND DISJOINT_FAILURE_DOMAINS AND VALID_LINEAGE AND TERMINAL_CLOSURE.

## Procedure
- Register immutable source claims: name, upstream ancestry identities, operator, infrastructure, and failure domain.
- Preserve initial C0, with registered source set and an explicit abort reason.
- Permit at most one recovery C1 from an ABORTED initial ceremony, never from a successful ceremony or a recovery descendant.
- Hold a fallback that shares a declared ancestry identity, operator, infrastructure, or failure domain with an original contributor, or reuses one of the original source names.
- Accepted recovery opens C1 with a parent link to C0. Close C1 exactly once with terminal success or failure. History of C0 remains ABORTED.
- Append all decisions to a SHA-256 linked ledger.

## Synthetic reference results
E0/E1/E2 had disjoint declared sources. R had distinct ancestry, operator, infrastructure, failure domain. C0 aborted due to withheld reveal, R passed the declared-domain audit, C1 opened and closed successfully. Nine hash-linked records verified. 24/24 local tests passed, including domain overlaps, shared ancestry, repeated recovery, recursive recovery, failure closure, replay, invalid sources and tampering.

## Limits
Distinct source labels are not authenticated independence, and the fallback's actual entropy, secrecy and selection effects are not tested. A single permitted retry mitigates procedural abuse but does not prove unbiased randomness. The code is synthetic, single-writer and in-memory; a hash-linked ledger is not durable or externally anchored. The WAG-054 generated JPG contains illustrative figures such as 39/40 and p-values that were not produced by the executed implementation.

## HTML journal
docs/index.html is extended with a self-contained embedded SVG WAG-054 panel. Original WAG-054 JPG is a conversation artifact, not a GitHub-hosted binary.

## Next — WAG-055: Authenticated Fallback Attestation and Durable Closure
Bind fallback claims to signed, externally verifiable provenance, independently timestamp both commitment and terminal closure, and ensure that a revoked signer or compromised source cannot silently certify recovery. Preserve old evidence and mark its operational trust separately.
