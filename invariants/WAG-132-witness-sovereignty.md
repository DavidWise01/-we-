# WAG-132 — Independent witness sovereignty

10 local Python tests passed in 0.001 seconds. 27 single-root assignments examined: 6 disjoint, 21 shared. Traverse the declared control DAG from each of three distinct witnesses to trusted terminal roots, rejecting cycles, missing nodes and unrecognized roots. Require pairwise disjoint root sets. Compute declared blast radius of any node.

Scope: standalone structural audit, not cryptographic attestation of the control graph. The model assumes every listed control edge is sufficient to exercise potential authority, a conservative simplification of threshold policies. Hidden administrators or shared recovery and hosting dependencies can defeat it. No live compromise, independent custody, or WAG-131 integration tested. Next WAG-133: authenticated, versioned control manifests and topology-bound witness responses; test omitted ancestry, stale manifests and dependency change.
