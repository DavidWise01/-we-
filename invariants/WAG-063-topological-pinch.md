# WAG-063 — Topological Pinch and Witness Continuity

Status: implemented 2026-11-15. Full local reference: 24/24 unittest tests passed, 7 audit records verify.

## Invariant

PRESERVE(W1,W2,W3,ANCESTRY) across a separately recorded topology-changing event.

The three witness vertices are at 0, 120 and 240 degrees, preserving their identities and distinct declared source ancestry. Their 3-cycle is the routing primitive, not automatically the surface topology.

A torus has genus 1. Under smooth nonsingular deformation, genus is conserved. Model a shrinking hole with a parameter p in [0,1]; for p < 1 the state remains TORUS, and p = 1 is an explicitly SINGULAR_PINCH stage with no smooth-surface genus. Only a subsequent explicit topology surgery produces a genus-0 spheroid. The changing hole-radius parameter is schematic rather than a physical, fully specified embedding of a torus.

## Executed demonstration

Parameters p = 0, .25, .5, .75, 1. States: TORUS (four stages, genus 1), SINGULAR_PINCH (genus undefined), SPHEROID_AFTER_SURGERY (genus 0). All three witness identity and ancestry strings are preserved exactly. Seven hash-linked in-memory records verify.
Local Python suite: 24/24 passed, testing three-way spacing, immutable witness objects, duplicate ancestry, genus bookkeeping, singularity, explicit surgery, no premature closure, monotonic parameters, invalid radii, audit tampering and atomic rejection.

## Interpretation and limitations

Gravity /\\ and void \\/ are user's conceptual opposing fields. This reference implements a formal pinch parameter, not equations of general relativity, actual gravity, quantum foam, or a continuous physical transformation. Three witness ancestors represent a design criterion, not Byzantine consensus guarantees. A topology-changing singularity or surgery must be specified; smooth deformations alone do not turn a torus into a sphere.

The neon WAG-063 JPG is conceptual artwork and contains illustrative 24/24/Git labels. A separate JPG conversation artifact exists; docs/index.html embeds self-contained SVG artwork rather than the original JPG binary.

## Files
- invariants/wag063/wag063.py — GitHub reference kernel
- invariants/wag063/test_wag063.py — GitHub 24-case regression tests
- docs/index.html — HTML visual journal WAG-044 through WAG-063

## WAG-064 — Pinch Singularity and Witness Path Continuity

At the topological transition, preserve an explicit mapping of each witness path and evidence lineage through the singular pinch. Reject merged or lost identities, prove the routing graph's connectedness separately from the surface's genus, and require a new independent quorum validation after topology surgery before trusting the new surface.
