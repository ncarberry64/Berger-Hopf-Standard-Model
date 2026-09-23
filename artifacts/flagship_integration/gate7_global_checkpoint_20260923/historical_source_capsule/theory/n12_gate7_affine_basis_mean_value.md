# Affine-direction mean-value bounds for a physical derivative column

This is a conditional calculus statement about the existing normalized
physical field. It changes no action, physical branch, frame or trial radius.
Its application requires the same paired physical family throughout the tube;
an interval Hessian at isolated points is insufficient.

Let the weighted augmented tube be

    T = {z0 + E(e*l+t): |l|<=rL, ||t||2<=rT},

with the existing fixed frame E, longitudinal direction e and radii. Every
segment from z0 to a point of T stays in T, since scaling l and t by a number
in [0,1] preserves both bounds. If E or e has certified input uncertainty,
this argument applies to each fixed admissible realization. There is no
additional assumption t perpendicular to e.

Assume F is the same C2 physical field on every such segment. The selected
eigenpair and bordered response must stay on the certified family, their
implicit Jacobians must remain invertible, and the physical normalization
denominator must stay nonzero. Source hashes alone do not prove these
analytic requirements. The paired family certificates and action domain
must justify them before a candidate is consumed as a uniform enclosure.

For one fixed weighted physical input vector v, suppose interval columns
enclose, uniformly for x in T,

    B0 = D2F(x)[v, rL*E*e],
    Bj = D2F(x)[v, rT*E_j], j=1,...,74.

All 75 directions must be present, including the descriptor component of the
augmented frame. The action contractions unweight the first 98 coordinates
and leave the descriptor unchanged. This follows the original physical
graph's coordinate convention.

For each output component i, define

    bi = sup|B0_i| + sqrt(sum_j (sup|Bj_i|)^2).

Write delta=rL*E*e*alpha+rT*E*eta, where |alpha|<=1 and ||eta||2<=1.
The fundamental theorem of calculus and bilinearity give

    DF(z0+delta)v - DF(z0)v
      = integral_0^1 D2F(z0+s*delta)[v,delta] ds.

Triangle and Cauchy–Schwarz inequalities bound its ith component by bi.
Thus DF(z0)v+[-b,b] is a uniform column enclosure under the stated family
assumptions. The point derivative must itself be enclosed with verified
point data; replacing it by an unvalidated floating center is insufficient.

The same argument applies to the mixed selected-line and physical-response
variations. It supplies candidate bounds on their first variations. Once
the assumptions and complete direction coverage are established, intersecting
these with an existing enclosure preserves the true family. A subsequent
Hessian evaluation may use that narrower proven enclosure. No numerical
bootstrap may treat an unproved candidate as an input certificate.

The diagnostic batches the 75 scaled tube directions in the graph's second
input slot while fixing v in the first slot. It retains the original seven
bordered solves and all original fifth-action scalar terms. Point and uniform
arrays have varying solve column counts, stored separately. The two support
tests check attaining directions with opposite signs and reject a missing
direction. The current numerical output remains an unreproduced diagnostic
for one v until a separate consumer establishes the family assumptions and
independent reproduction. All 99 input columns, midpoint and full-path
coverage, nonlinear remainder control and physical quotient identification
remain separate requirements.

## Same-family justification for the retained endpoint implementation

The finite retained local integrand is polynomial in affine state variables
and their exponentials. Its boundary term uses positive A and B, each a
positive constant times an exponential, and r4=A*B/sqrt(A^2+B^2).
Its square root and reciprocal are smooth because A, B and A^2+B^2 are
strictly positive at every finite real state.
The fixed quadrature and linear maps preserve smoothness. The global action
adds an inverse-inertia term; the paired eigenpair certificate supplies a
strict positive inertia lower bound on the entire raw segment hull. Thus
this particular retained action is smooth on a neighborhood of the tube.
This statement does not establish continuum regularity or change the action.

Write the normalized eigenpair equation as

    f(x,p,lambda) = ((H(x)-lambda*I)p, (p^T*p-1)/2) = 0.

The paired certificate bounds its preconditioned Jacobian defect uniformly
in a fixed eigenpair box, with a strictly positive contraction margin in
each of its 62 weighted rows. Strict inclusion gives a unique root for
each x in the tube. The defect bound implies invertibility of R*D_y f,
and hence of D_y f (both are square). The implicit function theorem yields
local smooth roots. Uniqueness in the common box joins these local roots;
the positive overlap with the fixed reference fixes their common sign.
Strict inclusion keeps the roots away from the box boundary. These facts
justify the same smooth eigenpair branch on each radial segment, including
local extensions at its endpoints.

The response matrix K equals D_y f times diag(I,-1). It is therefore
invertible on that same branch. Its right hand side is a smooth expression
in the action derivatives, state and eigenpair, so its unique response is
smooth. The physical value certificate supplies a strictly positive lower
bound on the original physical normalization norm. The resulting field F
is consequently C2 on these segments. The common-border representation
used for the mixed Hessian additionally checks that its border is nonzero;
it is an equivalent representation of this same field.

The consumer must verify the exact source bindings and independent receipts,
all 62 strict rational inclusion/contraction margins, positive inertia,
positive reference overlap, and positive physical norm. It must also
reconstruct the input column and all 75 scaled directions from the same
frozen frame, radii and weights, verify the saved domain, and recompute
the support and point-plus-support columns. A changed action, incomplete
direction matrix, missing receipt or nonpositive margin must fail closed.
Independent reproduction establishes repeatability; the calculus argument
above supplies the mathematical implication. Neither replaces the other.
