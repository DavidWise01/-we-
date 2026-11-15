# WAG-062 — Gravity–Void Geometric Closure and Witness Conservation

Status: 2026-11-15. Local Python geometry kernel and 16/16 unit tests passed.

## Geometric primitive
Three equally spaced points at angles 0°, 120°, 240° establish a minimal closed polygonal witness cycle. The six signed directions ±X, ±Y, ±Z supply a useful spatial routing frame. Conceptual opposing fields / (gravity/compression) and \/ (void/expansion) may deform the embedding.

## Topology boundary
A triangle is a graph cycle, not by itself a toroidal surface. A torus has genus one (a hole), whereas an ellipsoid/spheroid has genus zero. Continuous coordinate deformation does not erase the hole; a pinch or topology-changing operation must be explicitly modeled.

Ellipsoid: x²/a² + y²/b² + z²/c² = 1.
Spheroid if two of a,b,c are equal; sphere if all are equal.
The reference tracks surface axes separately from genus so an apparently spherical embedding cannot silently claim to be topologically a sphere.

## Witness invariant
Throughout deformation keep three distinct witness identities and three distinct declared source ancestors. Equal angular spacing ensures 120° per gap before embedding. No geometric property alone authenticates real-world ancestry, statistical independence, or Byzantine fault tolerance.

## Executed local reference
16/16 Python unittest cases passed: witness count/identity/ancestry/angle validation, surface class, genus distinction, invalid axes, immutable-looking append-only audit, tamper detection, and ancestral preservation.

Local outputs:
- wag062.py (geometry gate)
- test_wag062.py (16 tests)
- WAG-062-mesh.jpg (neon illustration)
The JPG includes illustrative/unverified claims such as 24/24 tests and Git publication status; actual executed verification was 16/16 local tests.

## Next invariant — WAG-063: Topological Transition and Witness Continuity
Specify a controlled pinch/closure operation that changes genus 1 to genus 0, recording the singular transition and tracking exact witness identities, source ancestry, graph links, and quorum eligibility on both sides. The geometry model does not constitute a physical gravity simulation or Byzantine consensus algorithm.
