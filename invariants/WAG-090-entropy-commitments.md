# WAG-090 — Entropy Commitments, Unbiased Sample Selection and Selective-Abort Holds

## Status

2026-11-16. Local Python reference and 52 unittest cases: **52 passed**. Three locally simulated witnesses produce one frozen commit/reveal round. The deterministic demonstration returns sample positions **(2, 8, 6)** for 17 chunks and three distinct samples. Nine hash-linked local audit entries verify.

## Rule

`VALID_SAMPLE_PROOF != UNBIASED_SAMPLE_SELECTION`

Binding `RoundID = (epoch, checkpoint_root, challenge, archive_chunks, sample_count)`, participant identity, and secret to a domain-separated SHA-256 commitment prevents changing a committed secret after freeze (subject to the commitment assumptions). All three participants must commit before reveal. Each reveal must match the previously frozen digest. A missing or mismatching reveal ends the round in an explicit hold, without drawing a new sample from the partial seed set.

Combine revealed seeds in **canonical participant order** using length-tagged serialization and SHA-256 domain separation. Sample positions without replacement using counter-based SHA-256 output and **rejection sampling**: reject values outside the largest multiple of the current population size; this avoids modulo reduction bias if the hash stream is indistinguishable from uniform random output. Never reuse the same sampled index in a round.

## Safety boundaries

A last-revealing adversary can see the other seeds and calculate the eventual sample set before choosing whether to reveal. Thus this simple commit/reveal protocol **detects selective abort but does not prevent last-revealer bias**, and cannot by itself guarantee unbiased selection in a system that retries after abort. Repeatedly instantiating a fresh in-memory object with the same challenge is not blocked across independent processes; a durable global challenge registry and abort-aware retry policy must be added. The simulator uses fixed example seeds; production security requires unpredictable high-entropy seeds, authenticated participants and a trusted challenge issuance mechanism. A signed or remotely anchored audit and independent witnesses are not established by locally declared identities.

## Test inventory

52 local tests cover strict three-witness registration; commitment freezing and duplicate/late submissions; missing/incorrect reveals, terminal abort states and audit verification; domain binding to round, challenge, checkpoint, epoch, and witness; order-invariant seed mixing; unique sample indices and sampler input validation; and tamper detection. No cryptographic uniformity statistical certification is claimed; rejection sampling follows its standard bounded-value proof under the hash-as-pseudorandom-stream assumption.

## Artifacts

- `invariants/wag090/wag090.py` — full reference implementation.
- `invariants/wag090/test_wag090.py` — full 52-case regression suite.
- `invariants/wag090/WAG-090-ascii.txt` — text-only experiment illustration.
- `docs/index.html` — cumulative GitHub Pages HTML journal with embedded ASCII panel.

## Next — WAG-091: Selective-Abort Recovery Without Seed Grinding

Precommit one retry policy and immutable attempt identifier, do not silently omit aborted trials, and require a publicly verifiable, unpredictable entropy contribution or equivalent mechanism that prevents a last revealer from choosing between biased attempts. Preserve all aborted attempts with their causal ancestry. Avoid calling this solved before the next implementation and adversarial tests.