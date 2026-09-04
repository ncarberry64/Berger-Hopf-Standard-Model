# Current-Green full transverse quadratic majorant

## Obligation

The certified mixed Green/transverse causal operator does not control the
quadratic response to two arbitrary directions orthogonal to the current
Green image.  Gate 7 therefore still requires, at every endpoint and every
Hermite--Simpson midpoint, a bound for

\[
  (u,v)\longmapsto D^2F_{(x,s)}[u,v],
  \qquad u,v\in g^\perp\subset\mathbb R^{74},
\]

for the same retained action, selected eigenline, hard-response solve,
independent descriptor coordinate, physical tangent frame, and descriptor
scale used by the accepted current realization.

## Exact center reduction

Let `V` be an orthonormal basis of the 73-dimensional coordinate complement
of the current Green axis and let `E V` be its augmented action-frame lift.
Differentiating the selected symmetric eigenproblem and its bordered hard
response twice gives the complete tensor

\[
  B_{aij}=D^2F_a[E V_i,E V_j],
  \qquad B_{aij}=B_{aji}.
\]

The retained action is evaluated by exact signed broadcast contractions.
Thus one traversal forms each required D3, D4, D5, or D6 contraction with
both transverse column axes retained; no directional polarization and no
sampling of the transverse sphere is used.  The independent descriptor
coordinate is differentiated directly.  It is not identified with the
selected eigenvalue.

For unit coordinate vectors `u` and `v`,

\[
  \|B[u,v]\|_2
  \leq \|B\|_{\rm HS}\,\|u\otimes v\|_2
  =\|B\|_{\rm HS}.
\]

Consequently the tensor Frobenius norm is a valid full-unit-sphere center
majorant.  It is basis invariant under orthogonal changes of `V`.  The same
inequality is retained output by output, producing 99 componentwise
majorants for the later causal two-radius assembly rather than collapsing
the result prematurely to one scalar.

## Compute conservation

The full tensor is contracted and reduced in memory, but only its invariant
norms and solve/normalization residuals are stored in restart-safe shards.
This avoids storing approximately four million tensor entries per node.
One signed broadcast evaluation replaces 73 separate Hessian-direction
evaluations and replaces all polarization grids.  Existing valid shards are
reused by a fingerprint covering the current scientific inputs and the fixed
algorithm revision.

The campaign covers the 370 endpoints with a defined nonzero current Green
axis (nodes 1 through 370) and all 370 midpoints.  Endpoint zero is the fixed
initial boundary and its stored Green image is zero, so it has no normalized
73-dimensional Green complement and is not silently assigned one.  Midpoint
axes are the normalized coordinate
preimages of the already-derived correlated midpoint Green directions.

## Claim boundary

The binary64 tensor stage derives the complete signed center operator and a
deterministic Hilbert--Schmidt center majorant.  It does not by itself supply
an outward neighborhood enclosure.  Promotion of
`CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED` requires a
separate outward-rounding/remainder certificate tied to these centers.
Neither a fitted residue nor an empirical calibration is admissible.  A
failed outward screen records the responsible action/domain term and does
not authorize renormalization.
