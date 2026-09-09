# Batched evaluation of the frozen physical mixed derivative

This is an exact regrouping of the existing retained-action derivative graph.
It changes neither the action nor its constants, state, eigenline selection,
weights, output units, or external directions. It is not an all-direction,
neighborhood, or Gate 7 certificate.

## Prescribed mixed path

The existing `Mixed` algebra evaluates derivatives indexed by subsets of
distinct formal variables. Its multiplication uses the subset product rule;
its reciprocal, exponential, and positive-power operations use the same
partition chain rule as the original producer. A supplied derivative with
mask `m` is an actual mixed derivative. Each variable occurs at most once,
so no repeated-variable factorial is present.

For the scalar curvature term, let

    z(x,y) = z0 + x u + y v,
    p(x,y) = p0 + x pu + y pv + xy puv,
    a(x,y) = a0 + x au + y av + xy auv.

Evaluate the unchanged action on

    Z(t1,t2,t3,x,y) = z(x,y) + (t1+t2)p(x,y) + t3 a(x,y).

The coefficients selected by masks 7, 15, 23, and 31 are respectively
`D3 S[p,p,a]` and its x, y, and xy derivatives. Thus one fifth-order mixed
evaluation replaces the original seventeen third-, fourth-, and fifth-order
evaluations, including every derivative of the moving directions and their
mixed derivative. The two columns of `a` are kept separate; y columns are
paired in exactly the original order.

The fixed `D3[output,fixed,u/v]` and `D4[output,fixed,u,v]` evaluations likewise
share one affine four-variable path. The three first-variation contractions
for each outer direction share one column batch. The gradient term remains
the same ordinary third derivative. The full graph therefore uses five
action evaluations instead of twenty-seven. Bordered solves and every
subsequent field/scalar expression remain unchanged.

## Local coordinate lowering

At a quadrature node, a constant global direction matrix L enters the local
integrand only through M L, where M is the existing local map. Multilinearity
permits differentiation in the local coordinate basis followed by multiplication
by M L on that tensor index. Multiple constant indices can be treated this
way, each with its own signed Arb matrix product. No rank estimate, singular
value truncation, numerical zero threshold, or fitted basis is introduced.

An index is lowered only when the supplied path has its singleton derivative
and has no mixed input derivative involving that index. Moving directions
therefore keep their full mixed path. This is essential for the scalar
curvature batch. Exact zero derivatives of the specified polynomial path are
algebraic zeros, not defaults for missing physical input data.

Both bulk and inertia derivative tensors are lifted back to global indices
before summation and before the global reciprocal in `bulk - c/inertia`.
The reciprocal is never moved inside the quadrature sum. Boundary derivatives
use the original boundary maps and the same lifting rule. Temporary local
constructors are restored on success and on failure.

All projections, tensor lifts, action operations, and final derivatives use
Arb. The scalar coefficient `c` retains the exact binary64 value used by the
original source. A pinned parent-function digest prevents silent drift of the
unchanged physical graph. The historical producer and campaign fingerprints
are not modified.

## Validation and remaining scope

Tests compare the moving-direction coefficient with an independent symbolic
degree-five action, compare multiple lowered indices with an exact Hessian,
check column ordering and curved-index exclusion, and compare an affine path
with the original retained action. Full physical pilots additionally compare
original and regrouped Arb balls directly, without replacing them by display
rounding or accepting a numerical tolerance.

Single-slice timing and overlap are implementation evidence. They do not
enclose physical input error over all nodes, prove a neighborhood remainder,
or establish contraction. Those obligations remain on the completion path.
