# Common-input residual enclosure for the retained Gate-7 local block

This note specifies the mathematical scope of the all-input evaluator. It
does not assert a completed numerical certificate or global Gate-7 closure.
The action, source terms, physical tube, trial/test spaces, and frozen
preconditioner are inherited from the verified retained source records.

## Input and state variables

Let `theta` denote the original product of state balls and the bounded
corrections to the affine predictors for `(psi, lambda, h, b)`. There are
249 original midpoint coordinates or 75 endpoint coordinates, plus 124
base-solve correction coordinates. No physical radius is reduced.

For a fixed complete input map `U`, let `u` range over the **single**
74-dimensional Euclidean unit ball. The saved complete 99-input derivative
inclusions bound each row of the directional solve discrepancy after
composition with `U`. Write each such discrepancy as `rho_i eta_i`, with
`|eta_i| <= 1`. The 124 symbols `eta_i` represent the two 62-component
directional solves. They are shared by every occurrence of the corresponding
unknown. Relaxing their dependence on `(theta,u)` gives a containing domain;
it does not assert independent physical solutions or discard a residual.

The enlarged input domain is the product of the physical Euclidean ball
and this 124-dimensional box. A model has the form

    F(theta,v) = <c + A theta, v> + R(theta,v),
    sup_{theta,v} |R(theta,v)| <= r.

Here `v=(u,eta)`. The polynomial part retains every state-times-input
coefficient, including state-times-directional-correction terms. It is
homogeneous in the common input; the implementation rejects products with
two input legs. The remainder bound scales with the product-ball gauge
when a non-unit input is substituted.

## Enclosure arithmetic

For a scalar state model `g = d + b theta + e`, let `L_F` bound the support
of `A theta` over the state/input product, let `C_F` bound the constant
input functional, and let `L_g` bound `b theta`. The product retains

    c' = d c,       A' = d A + b^T c,

and its remainder is bounded by

    L_F L_g + (C_F + L_F) r_g
                + (|d| + L_g) r_F + r_F r_g.

The matrix support calculation respects every Euclidean group. For two
Euclidean groups it uses the smaller of the Frobenius and induced
one/infinity norm bounds; mixed box/Euclidean groups use the sum of the
corresponding column or row Euclidean norms. All coefficient balls,
products, square roots, and final supports use Arb outward arithmetic.

## Signed residual cancellation and vector reconstruction

The scalar target is the descriptor-pivot output of the fully normalized
rate derivative. Its complete bordered residual is `G`. The first two
adjoint blocks depend linearly on the common physical input; the last two
are input independent. Anchor adjoints are proposals with measured
defects, not uniform certificates. For any such fixed covectors,

    W = Y - beta G = Y

on the inherited implicit solution graph. The uniform producer evaluates
all four residual blocks, including the source terms held constant only
in the separate anchor differentiation. It includes the retained action's
boundary, inverse global inertia, and mixed third/fourth derivatives.

Let `L=(2 dt/3) Q P`, and use the nonzero descriptor pivot `L[73,98]`.
For each of the 74 output rows,

    output_i = (L[i,98]/L[73,98]) W
             + sum_{j<98} (L[i,j]-L[i,98] L[73,j]/L[73,98]) rate_j.

The pivot row is represented directly by `W`. This is descriptor
elimination, not omission of a physical output. Only after the signed
models are assembled are their supports combined into an operator bound.

## Optional local input projection

At a quadrature node the retained action depends on 13 local coordinates.
All input legs supplied by the current producer are constant in `theta`.
Let their local map be `T`, from the common input product to those 13
coordinates. Bound the support of each row by `s_i`, and write `S` for
the diagonal matrix of these scales. A zero row has zero scale and is
handled as exactly zero. Evaluate the local mixed jet with input `S w`,
where `w` ranges over a 13-dimensional unit box. Write `T_scaled` for
`S^{-1} T` on the nonzero rows. Restore a resulting model by

    c -> c T_scaled,       A -> A T_scaled,
    r -> r sup_v ||T_scaled v||_infinity.

The last norm is bounded by the maximum common-input support of the rows
of `T_scaled`. This keeps the map's anisotropy and includes division
rounding. Thus the nonlinear remainder is enclosed for every original
common input. No coefficient of the
constant or state-linear polynomial is discarded. Restore the common
input coordinates before adding quadrature contributions and before
forming the nonlinear inverse of the global inertia. Evaluate the
boundary through the unchanged full-input path. The local evaluator
checks and rejects state-dependent input legs rather than silently
applying this rule beyond its assumptions.

## Complete right endpoint transport

Reconstruct all 99 endpoint rate coordinates using the same scalar pivot
and the 98 normalized numerator derivatives. Let `A` be that rate applied
to the full right trial basis `E`, and let `A0` be a fixed point anchor.
Let `B` be the full midpoint output for its chosen fixed map `U`, and set
`PM=(2 dt/3) Q P M`, where `M` is the inherited uniform midpoint derivative.
The full local right block is

    Q - QPE + (dt/6) QPA0 + B + PM(E/2-dt A0/8-U)
        + [(dt/6) QP-(dt/8) PM](A-A0).

The signed anchor tail is formed before multiplication by the uniform
`M`. Before bounding the remaining endpoint contribution, eliminate its
descriptor directly against the scalar pivot. This combines the 98
numerator coefficients before their remainders are bounded; reconstructing
the descriptor and then summing independently would count those same
numerator remainders twice. Any difference between a proposed exact endpoint input map and the
original interval trial basis is included through the saved full endpoint
derivative. The original right endpoint state coordinates are shared
between endpoint and midpoint models; their outward coefficient radii
remain present. The two families' implicit correction symbols stay
distinct. The resulting common domain has 497 state coordinates and 322
input coordinates (74 physical, 124 midpoint corrections, 124 endpoint
corrections).

At the final operator support step, restore the known common input in the
constant directional-correction terms. For each family the original full
derivative matrices give `eta = E(theta) u`, where every row of the
normalized error matrix has Euclidean support at most one. Replace

    c_u u + c_eta eta

by the interval coefficient row `(c_u + c_eta E) u`. Leave every
state-times-correction coefficient and the nonlinear remainder unchanged.
The original matrix inclusion contains `E(theta)` for each allowed state,
so this gives a pointwise interval-affine enclosure on the same domain.
It retains the single physical input sphere when combining constant error
contributions. The resulting interval constant coefficients must not be
differentiated; they are used only in the final value/operator norm bound.
For the transported block, apply this substitution after the signed
endpoint and midpoint contributions have been assembled.

The same pointwise substitution can also be applied to every state-affine
coefficient: replace `A_(theta,eta)` by `A_(theta,eta) E` and add it to the
physical-input coefficient block. Include all map coefficient radii. Scale
the original remainder by `max(1,max_row ||E_row||_2)` so that even outward
map rounding or maps larger than the unit error box are covered by input
homogeneity. The constant-only and complete substitutions have identical
constant coefficients. It is therefore valid to select, per output row,
the smaller complete linear-plus-remainder bound and then use the shared
constant matrix in the joint output norm. The selected remainder and
linear bound must stay together. No derivative of these interval
coefficients is asserted.

This construction still covers only interval 13 and the right input block.
Neither its successful evaluation nor a local norm below one establishes
the full-history self-inclusion, contraction, physical force root,
constrained Hessian positivity, or continuum estimates required elsewhere
in the retained completion ledger.

For the two-radius input norm, the same models can also be restricted to
the stored longitudinal axis `a`. Substitute the interval column
`(a, E_mid a, E_end a)` into the complete input-linear model, including
its state-linear coefficients. For every state this column contains the
actual directional corrections. Scale the remainder by the product-domain
gauge of that column; do not assume the stored axis has exact unit norm.
The resulting Taylor coefficients are pointwise interval enclosures and
must not be differentiated. Its transverse output norm is the local
longitudinal-to-transverse bound. The full common-input norm still bounds
the transverse input sphere. Neither bound alone supplies the longitudinal
output, left input block, or full causal two-radius contraction.

The longitudinal output can be reconstructed without another action
evaluation. Replace the output row map `Q P` by `a^T P` in the same signed
Hermite--Simpson identity. Continue to use the already-certified descriptor
pivot `L_(73,98)` from the transverse construction: for any new coefficient
row `d`, write its contribution as

    (d_98/L_(73,98)) W
      + sum_(j<98) (d_j-d_98 L_(73,j)/L_(73,98)) N'_j.

This is an algebraic row identity; it does not require a nonzero descriptor
coefficient in the longitudinal row. Apply it to both the midpoint term
and the endpoint difference before charging the remainder. The same input
restriction then supplies the longitudinal-to-longitudinal bound.

The four resulting upper bounds form a local matrix `Z_loc` with output
and input order `(longitudinal, transverse)`. Using the full Euclidean
input ball in the transverse-input column is an allowed enlargement.
The strict local weighted test is

    max_i sum_j (Z_loc)_(ij) r_j/r_i < 1,

with the original source-bound radii, not radii selected after evaluation.
A transverse Euclidean bound below one alone does not imply this test.
Even a successful local weighted test does not supply the left input block,
the full causal history, the physical quotient identification, or the two
global self-map inequalities.

## Joint output support

For a common box input `eta`, retain the full output matrix `C` and form
`C^T C` before taking entrywise absolute values. Then

    ||C eta||_2^2 <= sum_ij |(C^T C)_ij|,  |eta_i| <= 1.

This bound retains cancellations between output coordinates. Compare it
with the Euclidean norm of the row-wise box supports and use the smaller
outward upper bound. For a Euclidean input, use a Gershgorin upper bound
on the spectral radius of `C^T C` or `C C^T`, again compared with the
Frobenius and induced-one/infinity bounds. Interval matrix multiplication
encloses every actual Gram matrix; no change of physical norm is made.

## Complete numerator residual cancellation

The descriptor residual does not remove the constant directional-solve
errors in the other 98 rate coordinates. The nonlinear normalization
depends on the 61 unnormalized velocity derivatives

    omega_i = b_u psi_i + b psi_(u,i) + s_u h_i + s h_(u,i).

Use the same four implicit equations `G0, G1, G2, G3` as in the descriptor
construction. At the fixed anchor, let `K+` be the directional bordered
matrix, with `+psi` in its last column and `psi^T` in its bottom row.
For component `i`, choose point covectors by

    K+^T v3 = (s e_i, psi_i),
    K+^T v2 = (b e_i - b v3_top - v3_bottom h, 0).

These remove the derivatives of `omega_i-v2 G2-v3 G3` with respect to
both directional unknowns. Choose the remaining two covectors by solving
the transpose of the complete 124-variable base Jacobian against the
base derivative of that reduced expression. Their coefficients are
linear in the single common physical input. As before, all point
covectors are freely chosen exact dyadic numbers; rounding is retained
in the measured adjoint defect and uniform residual evaluation.

Evaluate

    omega_i - beta0 G0 - beta1 G1 - v2 G2 - v3 G3

on the original common domain, including the complete physical source
terms. It equals `omega_i` on the implicit solution graph. Reconstruct
the normalized 98-component derivative using these corrected velocity
models and the unchanged configuration derivative. This removes the
large constant directional-correction terms before multiplication by
the transport operator, while retaining all state-times-correction and
nonlinear terms. A partially evaluated set of velocity components is
not a complete vector certificate.

The directional-only form `omega_i-v2 G2-v3 G3` is also an exact identity
on the same solution graph. It removes the same constant directional-error
coefficients without the two base adjoints. In exchange, its state-linear
bound can be larger. Both forms include all base correction symbols and
all original source terms. Choosing the directional-only form changes
neither the domain nor the norm nor the required strict contraction
inequality; it is sufficient only if the resulting complete transported
bound meets that unchanged inequality. Its artifacts explicitly record
that the base residuals were not subtracted.

## Cancel base-error and input-error products before input substitution

Let the complete retained base equations have shared state models
`G(theta)=g+J theta+e(theta)`, with component remainder bounds `r_j`.
These equations vanish on the inherited implicit solution graph. For a
constant matrix `B`, chosen freely, an input-linear output has the identity

    f(theta,u) = f(theta,u)-G(theta)^T B u

on that graph. If `c+A theta` is its coefficient polynomial, subtract
`g^T B` from its constant row and `J^T B` from its state coefficient
matrix. A point transpose solve against the coefficients of the base-error
coordinates supplies a useful `B`; retain all coefficient radii and any
remaining solve defect in the resulting polynomial.

The added remainder is bounded by `sum_j r_j |(B u)_j|`. Retain these
individual input-linear factors until the physical common-input map, or a
specific longitudinal direction, has been substituted. In particular,
include the directional-error columns when selecting `B`. Otherwise the
mixed base-error/directional-error products survive the point adjoint
cancellation. For a physical Euclidean input, the box-image norm of the
transpose of the remainder-weighted, input-substituted `B` is a valid bound;
for a specified direction, use the outward sum of the absolute values.

This correction uses the same base equations and original domains. Its
nonlinear remainder must be added explicitly. It provides no certificate
merely by cancelling coefficients: the complete transported, weighted
bound must still be evaluated and independently reproduced.

## Preserve the zero residual through interval transport

For an interval-enclosed transport coefficient `M(theta)`, perform the
endpoint cancellation before multiplying by `M`. On the same implicit
graph, `M f = M (f-G^T B u)`, for the actual shared value of `M`.
The remainder factors become `M B` and must accompany the corrected
polynomial through the entire transport, including longitudinal output.
Bounding the products by interval arithmetic is valid after this identity
has removed the zero residual. Choosing a point adjoint after multiplication
instead leaves the radius of `M` in the nominally cancelled coefficients.
That is a valid but unnecessarily weak enclosure.

## Refine directional errors without reducing the physical domain

The cached directional contractions supply 61 equations `v2_i^T G2=0`
and 61 equations `v3_i^T G3=0`. Include the two directional normalization
equations. One further zero equation follows from the original system:

    psi^T G2 = psi_u^T G0 + psi_u[61] ||psi||^2
               + slope (1-||psi||^2).

Here `slope=psi^T H_u psi` is the unchanged source action derivative.
The base eigenpair equation, its unit normalization, and `G2=0` therefore
give `psi_u[61]=0`. This is a derived constraint on the same implicit
solution, not deletion of a component.

For the fixed original longitudinal physical input `a`, leave the 124
normalized directional errors `eta` symbolic. Form any point row map `P`
from the 125 contracted equations. The implementation selects 124 equations
by floating QR only to propose a well-conditioned point inverse; all
coefficient radii and the entire resulting defect are retained. Thus the
proof relies on `eta=eta-P G`, not on an unverified exact inverse claim.

Cancel the base equations in each input coefficient before taking its
state support. Include the base residual tails in the corresponding
constant or error coefficient. Bound the original directional Taylor
remainders using the known original input gauge. This produces

    |eta| <= f + K |eta|,   f >= 0, K >= 0.

Starting from the previously certified physical enclosure `|eta|<=t0`,
every finite step `t_next=min(t, f+K t)` retains the actual solution.
All arithmetic is outward, and no convergence assumption is needed.
Intersect the resulting symmetric boxes with the original interval input
map when evaluating the longitudinal transport. The state domain, physical
radii, map, and norm are unchanged. The general 74-input bound continues
to use its original input maps. The two-radius test must use these two
valid bounds separately and still satisfy its original strict inequality.
