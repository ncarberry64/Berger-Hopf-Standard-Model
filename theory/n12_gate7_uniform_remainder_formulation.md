# Current-ledger uniform remainder: explicit dependency graph

This derives the missing object; it does not certify global contraction.
The reference ledger is
`artifacts/flagship_integration/gate7_global_checkpoint_20260923/current_history_budget.json`.
No frozen calculation is reopened. Endpoint 19 is the new action-derivative
prototype; endpoint 71 is not refined.

## 1. Domain and exact global formula

Use the ledger's exact rationals

    rL = 4325777291715173/4722366482869645213696,
    rT = 4683284956119277/2417851639229258349412352.

Let E_j be the frozen augmented trial frame, a_j its retained longitudinal
axis, and W the physical-state weighting matrix. The same history parameters
occur in all factors below:

    z_j(theta) = z_j^0 + E_j (rL*a_j*ell_j + rT*t_j),
    |ell_j| <= 1, ||t_j||_2 <= 1, j=1,...,370; z_0 fixed.

The transverse full-coordinate ball is the already-used enclosing domain;
no new independent copies of t_j are introduced in any occurrence of z_j.
For raw action variables x use W^{-1} times the first 98 weighted coordinates;
the last augmented coordinate is descriptor s. The maximum product norm of
the normalized (ell_j,t_j) variables is the history norm. Denote its linear
input map by D_r. All directions u,v below lie in that unit product ball.

Write f for the complete weighted 99-component physical rate. With h_i the
fixed step, the actual midpoint and residual are

    m_i = (z_i+z_(i+1))/2 + h_i*(f(z_i)-f(z_(i+1)))/8,
    r_i = z_(i+1)-z_i-h_i*(f(z_i)+4*f(m_i)+f(z_(i+1)))/6.

Here r_i denotes an HS residual, not either radius. Define

    A_j = Df(z_j), H_j = D2f(z_j), A_m = Df(m_i), H_m = D2f(m_i),
    b_j(u) = (D_r u)_j,
    m_u = (b_i(u)+b_(i+1)(u))/2
          + h_i*(A_i*b_i(u)-A_(i+1)*b_(i+1)(u))/8,
    m_uv = h_i*(H_i[b_i(u),b_i(v)]
                 -H_(i+1)[b_(i+1)(u),b_(i+1)(v)])/8,
    r_i,uv = -h_i/6 * (H_i[b_i(u),b_i(v)]
                   + 4*H_m[m_u,m_v] + 4*A_m*m_uv
                   + H_(i+1)[b_(i+1)(u),b_(i+1)(v)]).

The term 4*A_m*m_uv is mandatory. Endpoint Hessian contributions therefore
have output factors (I+h_i*A_m/2) and (I-h_i*A_m/2), respectively; they
cannot be replaced by two unrelated midpoint noises.

Let B_i = R_i^{-1} T_(i+1) be the frozen right solve/test pullback, and
C_j the exact frozen causal propagation from node j to j+1. Set

    G_(k,i) = C_(k-1) ... C_(i+1),  i+1 < k;
    G_(i+1,i) = I.

Empty products are I. The second derivative of the fixed-frame Newton map is

    D2 N_k(theta)[u,v] = -sum_(i=0)^(k-1) G_(k,i) B_i r_i,uv(theta).

There is no Taylor factor 1/2 in this expression. Existing Q source tensors
include that factor; differentiating their quadratic polynomial supplies 2Q.
The formula refers to the exact frozen operators. Computing with saved binary
centers additionally requires their already-frozen map/arithmetic enclosure;
the stored center matrices alone are not these exact operators.

For an explicitly identified booked vector function F_book, put

    J_beta,k(theta)[u,v] = Pi_beta,k/r_beta *
       (-sum_i G_(k,i) B_i r_i,uv(theta) - D2 F_book,k(theta)[u,v]),
    kappa_beta = max_k sup_(theta,u,v) ||J_beta,k(theta)[u,v]||,

where Pi_L,k=a_k^T and Pi_T,k=I-a_k*a_k^T use their certified projection
norms; exact unit axes are not silently assumed. F_book excludes the constant
and center-linear terms, whose second derivatives vanish. It includes exactly
the selected LL/LT quadratic functions and any genuinely identified booked
nonlinear vector function. Bounds in a ledger do not themselves define those
functions or a signed subtraction. In particular, do NOT subtract a positive
coefficient bound from a different positive coefficient bound.

If R=N-N(0)-DN(0)D_r*theta-F_book has R(0)=DR(0)=0, the current criterion is

    remainder_value_beta <= r_beta*kappa_beta/2,
    normalized_derivative_remainder_beta <= kappa_beta,
    B_L = 6.163474303009908e-7 + rL*kappa_L/2 < rL,
    B_T = 8.122123169384853e-10 + rT*kappa_T/2 < rT,
    max(0.001267757954549044+kappa_L,
        0.2547585520975398+kappa_T) < 1.

Decimal known terms here are displays; the ledger's exact rationals control
all decisions. Thus kappa_L < 0.6542911248664067 and kappa_T <
0.7452414479024602 remain sufficient targets, not proved values.

### The interval-14 derivative-entry booking

The frozen interval-14 proof bounds one entry of a Jacobian remainder. A
masked Jacobian need not be a Jacobian of a separate vector function (its
mixed partials need not commute). This does NOT invalidate that entry bound
or its booking; it means an integrability identity cannot be assumed when
instantiating the sufficient R-Hessian theorem.

An exact formulation that needs no such extra assumption is available. Let
L_i(theta) be the local Newton derivative after its center derivative and
booked LL/LT derivative have been removed. Let M select only the interval-14
right-block entry (73,14); define B14=M L_14, with the frozen transport.
Use the complement (I-M)L_14 and all other L_i to form E(theta). The
state arguments are common, and E(0)=0. Bound the bilinear operator D E,
where the two arguments mean state variation and Jacobian input variation:

    kappa_beta >= max_k sup_(theta,u,v)
                   || Pi_beta,k * D E_k(theta)[u]v / r_beta ||.

This is the preceding source formula with the corresponding local Jacobian
entry mask applied before transport. It need not be symmetric in u,v.
For the complete Newton map use, exactly,

    N(theta) = N(0) + DN(0)theta + Q_book(theta)
               + integral_0^1 B14(t*theta)theta dt
               + integral_0^1 E(t*theta)theta dt,
    DN(theta) = DN(0) + DQ_book(theta) + B14(theta) + E(theta).

The already-booked uniform value/derivative bounds control B14. Since
||E(t*theta)|| <= t*kappa, the unbooked value is <= r*kappa/2 and the
unbooked derivative-matrix norm is <= kappa. This proves the SAME numerical
inequalities without calling E the derivative of its radial integral.
The mask must act on the right trial column, not the ambient field Hessian.
The input-coordinate L/T combination and descriptor incidence stay intact.
An eventual producer must explicitly attach this identity and matching mask;
the existing checkpoint's flags are not that attachment.

## 2. The physical Hessian's action dependencies

Let S(x) be the retained raw 98-state action, H its reduced 61x61 Hessian,
and (psi,lambda) the oriented index-24 eigenpair. The 62x62 bordered system is

    K = [[H-lambda I, psi], [psi^T,0]],
    K [h;b] = [f_response;0],    psi^T psi = 1,
    lambda_u = psi^T H_u psi,
    K [psi_u;gamma_u] = [-(H_u-lambda_u I)psi;0],
    lambda_uv = psi^T H_uv psi + psi_v^T H_u psi + psi_u^T H_v psi,
    K [psi_uv;gamma_uv] =
       [-H_uv psi-H_u psi_v-H_v psi_u+lambda_uv psi
         +lambda_u psi_v+lambda_v psi_u; -psi_u^T psi_v].

For q=[h;b] and F=[f_response;0],

    q_u  = K^{-1}(F_u-K_u q),
    q_uv = K^{-1}(F_uv-K_uv q-K_u q_v-K_v q_u).

K_u,K_uv contain the SAME psi,lambda derivatives above. The response RHS is
the weighted gradient/configuration-Hessian expression in `_rate_enclosure`;
its first and second derivatives require action orders at most four.
Uniform invertibility (or a verified weighted inverse defect <1) of K is
required over the original domain, not just at its center.

Pad p=(0,psi); put c=W_q*x_configuration,
a=(0,W_reduced*psi/W_state), d=(c,W_reduced*h)/W_state. Then

    C = S'''[p,p,a], J = S'''[p,p,d],
    N = (s*c, W_reduced*(b*psi+s*h)), delta=b*C+s*J,
    U=(N,delta), nu=sqrt(N^T N), f=U/nu.

For example C_uv is exactly the sum over all assignments of the distinct
labels {u,v} to four slots A0,A1,A2,A3:

    sum S^(3+|A0|)[(x_w)_(w in A0), p_A1, p_A2, a_A3].

p_empty=p, p_{u,v}=psi_uv padded, and analogously for a or d. There are
16 ordered assignments, including S5[x_u,x_v,p,p,a], the S4 terms with
one moving leg, and S3 terms with two first variations or one second
variation. This formula applies to the affine raw arguments of a rate
Hessian; the non-affine HS midpoint chain is accounted for separately above.
It must not drop the moving-leg terms. Descriptor derivatives obey the same
product rule in delta and N; the action itself is independent of s.

Finally, with all quantities evaluated on the SAME parameters,

    nu_u = N^T N_u/nu,
    nu_uv = (N_u^T N_v+N^T N_uv-nu_u*nu_v)/nu,
    f_uv = U_uv/nu - (U_u*nu_v+U_v*nu_u+U*nu_uv)/nu^2
                     + 2*U*nu_u*nu_v/nu^3.

This is precisely the existing physical Hessian graph. Uniform action
derivatives through order FIVE, the two uniform second implicit variations,
and a uniform positive nu suffice to evaluate it directly. A separate
Lipschitz estimate for f_uv would instead require action derivatives through
order SIX and third implicit variations. That extra order is not necessary
for direct Taylor-model enclosure of the graph above.

## 3. Factor classification (scope matters)

| Factor | Classification | Usable scope |
|---|---|---|
| Current radii, frames, axes, steps, original endpoint domain | CERTIFIED/FROZEN | Fixed original-domain operands |
| Frozen B, causal maps/weights, map arithmetic and covariance receipts | CERTIFIED/FROZEN | Their original certified operator/norm scope |
| Full-history physical DF, incidence, kinematic envelopes | CERTIFIED/FROZEN | Center/formation errors and stated finite-history layers |
| Already-paired point Hessians | CERTIFIED/FROZEN | Stated centers and covered directions only |
| Uncertified floating proposal derivatives at uncovered nodes | NUMERIC CENTER VALUE ONLY | Never substituted for uniform evidence |
| Selected eigenbranch/inertia/value/normalization and local derivative tubes | PARTIAL UNIFORM BOUND | Only their recorded nodes, directions and domains |
| S^(1..5) contracted with the full common-variable moving physical legs | MISSING UNIFORM BOUND | New fifth-action prototype encloses one fixed-leg scalar leaf |
| Coupled psi_uv and q_uv for every required direction pair | MISSING UNIFORM BOUND | Point anchors and isolated columns do not cover the operator |
| Uniform A_m,H_m at the actual midpoint of the same endpoints | MISSING UNIFORM BOUND | Center midpoint/incidence certificates remain reusable |
| Complete transported, masked bilinear source operator D E | MISSING UNIFORM BOUND | Smallest sufficient object for both current kappa bounds |

The all-history domain needs the same selected branch and positive norm at
every rate evaluation. Eight existing eigenbranch records do not establish
that coverage elsewhere. None of these missing factors is inferred from
the magnitude of a fifth-action center contraction or a point Hessian.

## 4. Analytic action structure and the smallest new producer

`factored_local_algebra` expresses each of 96 quadrature summands as a
finite sum of P(z)*exp(l.z), in thirteen affine local coordinates. In these
coordinates the gravitational prefactor has polynomial degree two, the ADM
polynomial degree at most four, the xeta^4 sector degree at most eight in
beta, and inertia's xeta^3 sector degree at most six in beta. Polynomial
derivatives beyond THEIR degrees vanish exactly. The exponentials do not.
The complete action is

    S = sum_q w_q*(gravity_q+algebraic_q) - c/I + B_boundary,
    I = sum_q w_q*inertia_q,
    c = retained binary64 value of 0.25/(2*HOPF_ORBIT_VOLUME^2),
    B_boundary = -C_SM*exp(n)*sqrt(A^2+B^2)/(A*B).

The quadrature, maps and all floating constants remain the retained operands.
The action is NOT a polynomial of degree four. Neither fifth nor sixth action
derivatives vanish in general. The only non-entire denominator conditions
here are I>0 and the positive boundary square-root argument (A,B are positive
exponentials). The physical graph adds bordered inverse K and nu>0. These
conditions must be propagated with their uniform lower bounds.

For one shared domain keep every scalar as c+a.theta+[-rho,rho]. Differentiate
the action in distinct formal directions using the subset jet algebra; this
computes polynomial derivatives exactly, without samples or finite differences.
For a product preserve c*d and c*b+d*a and bound the discarded terms by

    L(a)L(b)+(|c|+L(a))*rho_g+(|d|+L(b))*rho_f+rho_f*rho_g.

For phi=exp, reciprocal or positive power, retain phi(c),phi'(c)*a and bound
the remainder by |phi'(c)|rho+sup|phi''|*(L(a)+rho)^2/2. The support L uses
one scalar interval plus a 74-dimensional Euclidean ball. All 75 signed
coefficients survive quadrature, the inertia reciprocal and boundary assembly
before final support. Only explicitly bounded nonlinear tails are enclosed.

`uniform_action_contraction.contract` implements this construction for any
one-to-six prescribed raw action legs, including Taylor-valued legs on the
same parameter domain. It evaluates D^m S at those pointwise legs; it does
NOT silently supply derivatives of the legs. The 16-term identity above
specifies where those separate moving-leg terms enter.

The endpoint-19 producer consumes the saved raw affine directions and exact
current radii, then evaluates the NEW quantity

    D5 S(x0+rL*dL*theta0+rT*D_T*thetaT)[p0,p0,a0,rL*dL,rL*dL].

p0 and a0 are frozen center legs. The full physical quantity replaces them
with psi(theta) and a(theta), and includes response, moving-leg, normalization,
midpoint, projection and all other directional terms. This probe does not
identify a center leg with a uniform eigenvector or charge a global ledger.

The companion `derive_n12_gate7_uniform_fifth_action_operator_probe.py` adds
two complete independent L/T test-direction balls to the SAME state domain.
Its 225-parameter bound for D5 S(x)[p0,p0,a0,D_r*u,D_r*v] is approximately
1.3109964100037637e-23; the new computation independently reproduced identical
bytes. Thus all input pairs are covered for this fixed-leg action leaf.
Bilinear direction terms enter explicitly bounded nonlinear model tails;
this may lose cancellation and does not claim an optimal operator bound.
Moving physical legs and the rest of the response graph are still missing.

## 5. What must be produced next; feasibility rule

The exact absent operator is D E(theta)[u]v in section 1 on the full stated
product domain. Its new action leaf requires S5[x_u,x_v,p,p,a/d], together
with the lower-order contractions in section 2, sharing the implicit solution
parameters. Point Hessians cannot bound that operator: values at a center
place no restriction on variation away from it without derivative/domain
control. A new sixth derivative is optional, not the smallest requirement.

Next producer stages are explicit:

1. Feed the existing frozen primal/first-variation Taylor models and their
   certified tails into the action-contraction kernel, with the original
   parameter namespace. Use the exact 16-term curvature identity.
2. Enclose the two second implicit solutions by K^-1 applied to the displayed
   signed right sides, retaining their shared coefficients and a certified
   correction residual/inverse defect. Reuse point anchors, never refit them.
3. Form f_uv with the displayed normalization formula. Contract with B and
   projected causal output BEFORE taking support. Include actual m_u,m_uv and
   the interval-14 Jacobian-entry mask; test all required input directions.
4. Only a bound for this complete bilinear source can enter a global screen.
   Use current operator projections and map-error certificates with the frozen
   370 weights. A bound for a raw action scalar has different units and missing
   amplification factors, so multiplying it by the CSV weights is invalid.

For source bounds c_i in the weights' matching quadratic norm, the conditional
screen is sum_i W_i*c_i. Conversion to the two normalized kappa rows additionally
requires the input radius maps, output projections/r_beta and the Taylor-half
convention. These factors are present explicitly in section 1; they must not
be guessed from the historical witness or the small prototype number.

Consequently the scalar prototype alone cannot establish global feasibility,
identify endpoint-71 dominance or justify a 370-interval campaign. The recorded
outcome is B: a specific action-derived uniform contraction producer and an
explicit remaining implicit/operator composition, rather than a claimed
closure path. Gate 7 and the full physical inequalities remain open.
