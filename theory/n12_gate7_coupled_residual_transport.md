# Interval 13: executable coupled residual transport and its missing action input

This bounded calculation reuses the original paired interval-13 right-column
data. No action derivative, shard, bootstrap, or broader refinement is launched.
It implements common-parameter residual assembly and inverse transport, and
evaluates the normalization part on the saved BHSM predictors. It does **not**
evaluate the complete physical projected residual. The distinction is part of
the output schema, not an implicit qualification of a claimed certificate.

## One parameter vector, including through the solves

For the physical problem use the original two endpoint variations as the
parameters theta, with their fixed two-radius constraints. All selected
eigenvectors, response variables, fields, and the actual HS midpoint are
functions of that same theta. The saved midpoint outer family still covers
249 scaled directions; the endpoint family covers 75. We evaluate predictors
on these full original outer families without asserting their independent
product is the physically attainable joint endpoint/midpoint graph.

Write H for the raw reduced action Hessian, f for the unchanged metric-weighted
response source, p for the selected unit eigenvector, lambda for its eigenvalue,
and (h,b) for the bordered physical response. In this note h is a response
vector; the interval step is denoted dt. The equations are

    (H-lambda I)p = 0,             (p^T p-1)/2 = 0,
    (H-lambda I)h+b p-f = 0,       p^T h = 0.

For a retained physical direction u, let H_u and f_u be their complete
directional action contractions, lambda_u=p^T H_u p, and gamma_u the auxiliary
selected-line border. The first-variation residuals are

    (H-lambda I)p_u + gamma_u p + H_u p-lambda_u p = 0,
    p^T p_u = 0,
    (H-lambda I)h_u+b_u p+H_u h-lambda_u h+b p_u-f_u = 0,
    p^T h_u+p_u^T h = 0.

`coupled_first_variation_residual` implements these eight blocks. Neither the
eigenvalue slope nor either bottom-row term is dropped. Every multiplication
uses the same polynomial parameter IDs. The four additional mixed solves in
the saved seven-solve graph supply derivatives of these predictor variables
along the full neighborhood directions; they are not additional independent
response variables with freely chosen signs.

The original physical normalization can be lifted without dividing variable
intervals. Let

    N=(s c, W(b p+s h)), delta=cpsi*b+s*remainder,
    n^2=N^T N, n>0, n F=(N,delta),
    n n_u=N^T N_u, n F_u+n_u F=(N_u,delta_u).

`lifted_rate_residual` implements the last four polynomial residuals; the
caller must supply the **complete** numerator/action scalar contractions and
their remainders. Positive n, the selected branch, nonzero border, inertia,
and the original domain conditions remain separate binding obligations.

The exact HS relation and the complete right column are

    Z_M=(Z_L+Z_R)/2+dt(F_L-F_R)/8,
    A=DF(Z_R)e, w=e/2-dt*A/8, B=DF(Z_M)w,
    QD=Q[u_14-Pe+dt*P A/6+2dt*P B/3].

`hs_right_column_residual` implements the midpoint relation, the equation for
w, and this column. The identity B=DF(Z_M)w0+DF(Z_M)(w-w0) recovers the previous
center-direction split exactly: its center shift and full chain term are
included. P and Q remain the original frozen maps; Q does not assume that the
stored axis is exactly unit. Boundary/physical quotient identification and
full-history transport are not inferred from these fixed-frame equations.

## Dependency-preserving inverse with a rigorous tail

For one complete preconditioned residual equation, write

    e = r(theta)+E(theta)e.

If a nonlinear G is used, this means r=-R G(theta,Uhat), and E is the **full
stacked secant defect** I-R integral D_U G(theta,Uhat+t e)dt. Its polynomial
representation must retain the same theta and any explicitly bounded common
correction parameters. The correction domain must be invariant and lie in
the domain of the original branch and action bounds. Individual bordered
contractions do not imply this full-stack inclusion or contraction.

`solve_projected_residual` implements the following bound for supplied valid
polynomial r and E on the parameter box (also enclosing the product balls).
For fixed output C, positive weights w, eta>=sup||r||_w and q>=sup||E||_w<1:

    C e = C sum_{k=0}^{m-1} E^k r + C E^m e,
    sup|C e| <= support(C sum E^k r)
                + sup||C E^m||_{w->infinity} eta/(1-q).

All monomials are combined **before** output ranges are taken. For example,
if e1=theta and e2=e1/4+3theta/4, the implementation proves e1-e2=0 after two
terms, including an exactly zero tail. Separate solution boxes allow a
spurious difference of 2. A variable inverse e=theta/(1-theta/4) retains theta
and theta^2 and bounds the remaining tail; its bound encloses 4/3. Uncertain
coefficients are never canceled as if they were exact. No series term is
silently truncated, and a fixed operation cap prevents uncontrolled expansion.

This is implemented and analytically tested inverse transport, **not** an
instantiation of the missing full BHSM secant-defect polynomial. The stored
row contractions cannot be passed as if they supplied that polynomial.

## Actual saved-data evaluation

The arbitrary exact predictors are

    p_hat = p_center + point_center_3[:61] theta,
    h_hat = point_center_0[:61] + point_center_4[:61] theta,
    p_u_hat = point_center_1[:61] + point_center_5[:61] theta,
    h_u_hat = point_center_2[:61] + point_center_6[:61] theta.

All seven original point solve centers are reused. These predictors need not
be exact solutions or exact tangent jets. Selecting their exact coefficients
does not set anchor error to zero: the complete equation residual measures
their error. In particular, the eigenpair proposal may differ slightly from
the point solver's proposal; neither the constant nor linear residual is
assumed to vanish.

For affine predictors A[1,theta], B[1,theta], the exact polynomial coefficients
of their dot product are A^T B. Equal quadratic monomials are combined before
product-ball support bounds are taken. This retains common parameters across
all response coordinates in the four normalization equations above. The
evaluation is outward Arb arithmetic at 512 bits and preserves all 249/75
directions and the original radii. Approximate upper bounds are:

| Residual | Midpoint, 249 parameters | Right endpoint, 75 parameters |
|---|---:|---:|
| (p_hat^T p_hat-1)/2 | 4.38956e-14 | 2.73257e-15 |
| p_hat^T h_hat | 4.25361e-8 | 6.94740e-10 |
| p_hat^T p_u_hat | 2.50624e-11 | 2.78073e-12 |
| p_hat^T h_u_hat+p_u_hat^T h_hat | 1.65240e-5 | 6.55155e-7 |

Exact bounds and coefficient hashes are in the generated JSON. These are
unprojected equation residuals, with different units/scales from QD. They
must not be subtracted from its norm or treated as its remainder.

The saved same-family bordered contraction upper bounds are approximately
0.1748090848 (midpoint) and 0.5796301701 (endpoint), giving corresponding
inverse amplification bounds about 1.21184078 and 2.37885769. They show that
those individual solves have usable inverse control. They do not include
the off-diagonal response coupling, field normalization, or HS endpoint-to-
midpoint feedback in the proposed stacked residual formulation.

## The precise missing bound and decision against scaling

The newly evaluated constraints do not themselves remove the known bad pair.
Indeed normalization alone cannot bound a tangent response: at p=(1,0),
h=0, p_u=0, h_u=(0,K), all four normalization residuals vanish for every K.
With b=s=1, c=0 and unit weights, the normalized derivative has size |K|.
The lifted field equations also hold with that derivative. This analytic
information-sufficiency example is tested; it is **not** a BHSM state or a
physical noncontraction proof. It identifies why the action rows are essential.

What is still missing is a **signed common-parameter bound for the action
rows above, after the complete output pullback**, together with a valid
stacked correction inclusion. Specifically, H, H_u, f, f_u and the descriptor
contractions need a representation on the same predictor/correction graph
with their full joint remainders. The saved `preconditioned_residual_i` arrays
are already coordinate balls evaluated around fixed centers using boxed
upstream solves. They cannot simply be relabeled as coefficients of this
shared-parameter graph. Neither the full stacked secant defect nor its
projected residual support is supplied by the reviewed saved records.

One suitable next implementation would retain contracted action expressions
as common-parameter Taylor models through G, use an adjoint of the stacked
anchor equations for the chosen output covector, and enclose only the
remaining signed projected action contractions plus the correction tail.
This does not require a new full Hessian inventory. The implementation must
include both endpoints in the midpoint relation, both endpoint and midpoint
response errors, numerator/descriptor terms, normalization, branch/domain
and boundary obligations. A claimed third-derivative shortcut must itself
be justified; no higher-order remainder is assumed small here.

The complete local vector remainder would have to satisfy

    epsilon < 0.9997125743857969,

using the unchanged conservative point/anchor budget from PR #441. For a
scalar covector, success would be an obstruction screen only, followed by
the local vector norm and the global causal operator requirements. No such
epsilon has been proved in this batch. The old coefficient relaxation still
has gain >=48.720352347851 and margin <=-47.720352347851; the full physical
global margin remains unknown. This batch establishes neither a measured
gap reduction nor a no-go theorem for a truly coupled action residual.

Do not scale or launch another broad refinement. The single remaining
mathematical priority is the contracted action residual and its stacked
output/inclusion bound just specified. The independent curvature campaign
continues unchanged and all validated results are preserved.

Gate 7 still requires full physical neighborhood/history certification,
physical quotient identification, the finite-history operator and geometry
jets, signed joint force/KKT/constrained Hessian, and continuum closure.
Full BHSM completion additionally needs action-owned state/scale/observable
maps, no-fit predictions and benchmarks, resulting physical data in existing
Museum engines, and the submission manuscript. No gate or prediction changes.
