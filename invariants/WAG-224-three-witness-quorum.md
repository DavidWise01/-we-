# WAG-224 — Three-channel acquisition quorum and collusion testing
.dlw

This extends WAG-223's SHA-256/HMAC fixture packet checker to three channels, each authenticated under a different (public, demonstration-only) key. A quorum is **2 distinct acquisition roots agreeing on the same binary sequence**, not two signers or two packet signatures. The acquired root aliases 'relay-A' and 'relay-B' are resolved by a fixture-owned mapping. Invalid, missing, stale, or unauthenticated packets cannot contribute. The comparison baseline counts distinct signer IDs and thus double counts copied channels.

Executed 384 constructed cases (12 families × 4 periods × 8 seeds). The tests checked 96 invalid/missing channel packets, avoided 192 signer-count false quorums, and observed 64 false independent quorums accepted by the lineage rule when authorized signers falsely claimed separate acquisition roots. Family results:
three_independent: quorum 32, abstain 0, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 0
copied_pair_dissent: quorum 0, abstain 32, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 0
triple_copy: quorum 0, abstain 32, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 0
independent_dissent: quorum 32, abstain 0, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 0
missing_third: quorum 32, abstain 0, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 0
invalid_third: quorum 32, abstain 0, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 0
alias_pair_dissent: quorum 0, abstain 32, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 0
two_copy_one_agree: quorum 32, abstain 0, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 0
authorized_collusion: quorum 32, abstain 0, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 32
all_disagree: quorum 0, abstain 32, naive quorum 0, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 0
one_shared_bad: quorum 0, abstain 32, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 0
false_distinct_root: quorum 32, abstain 0, naive quorum 32, incorrect versus constructed declared-root rule 0, actually shared acquisitions counted independent 32

The 2-of-3 threshold is a governance policy for this experiment, not a mathematical proof of correctness. Three identical packets from one acquisition count as one, regardless of signer count. If two copied channels agree and a truly distinct channel dissents, the policy abstains. A third missing channel still permits quorum from two independently claimed matching roots, but not from two copies. All three distinct claimed roots can be forged by authorized colluding senders; the attacker wins 64 constructed cases. Thus **observed data and authentic MACs alone cannot prove independent origin**. The actual acquisition ancestry is a test harness oracle. No external sensors, hardware attestation, secrets kept outside source, signed hardware time, or real cryptographic storage is included.

Next WAG-225: add *challenge-response acquisition proofs*, intentionally correlated physical challenges, spoofable witnesses and an explicit independent challenge authority. Treat successful challenge responses as stronger evidence only under a stated trust assumption.
