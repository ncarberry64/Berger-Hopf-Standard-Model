# v69: a local D5 current map into the Gauss source space

2026-11-03. This stage constructs a sufficient local function-space map for
the dressed diagonal normal-pair current. It derives the required weighted
pole graph estimate, evaluates the saved spatial lower-order operator with
the correct combined eta contact, and retains the native source in its
original weak form. No physical Cauchy columns or event graph are supplied
by these estimates. No new physical regularity postulate is adopted.

The result explains exactly why complete CAR normalization and the prior
unweighted first-order graph estimate alone did not furnish v68's local
source norm. It also avoids turning that particular strong source norm into
a universal prerequisite: the original native weak source has a less
demanding dual-space route.

## 1. Recovered equations and normalization

Use the same material chart and original D5 density
w=C_rho R^3=rho^3 m. Let u be the original geometric right section and v
the independent geometric left Cauchy row, before multiplication by sqrt(w).
The photon insertion derived in v67 gives

    j_phi = rho^3 m v V_phi u.

The exact transported V_phi has norm one on the stated real compact-gauge
chart. Its normal-pair insertion consumes C_ss+C_nn. This local statement
does not assign the physical normal inclusion, CAR Gram, left source or
cap/relative unit conversion. Those must agree on the actual common domain.

The desired local strong source norm is

    N(j)^2 = integral rho^-4 |j|^2 d rho dHaar.

Put z_u=rho^-1/4 u and z_v=rho^-1/4 v, using the reference cone measure
rho^3 d rho dHaar with normalized Haar on unit S3. Holder's inequality gives

    N(j_phi) <= m_plus ||z_v||_4 ||z_u||_4.

For compact regular sections, the ordinary four-dimensional Sobolev
inequality yields

    ||z||_4^2 <= (sqrt(3)/4) ||grad z||_2^2.

This constant is the normalized-Haar form of the standard whole-space
inequality. The source is [Talenti's original theorem](https://math.jhu.edu/~js/Math646/talenti.sobolev.pdf),
Annali di Matematica Pura ed Applicata 110 (1976), 353-372,
[DOI 10.1007/BF02418013](https://link.springer.com/article/10.1007/BF02418013).
The analytic extremizer integrals in this normalization are 1/12 and 2/3,
giving squared constant 3/16. This auxiliary mathematical normalization is
not a chosen BHSM packet. For vector sections the scalar inequality applies
to their modulus, whose gradient is bounded by the component gradient.

Therefore, with H(u)=||grad(rho^-1/4 u)||_2,

    N(j_phi) <= m_plus (sqrt(3)/4) H(v) H(u).                 (1)

This is a concrete bounded bilinear current map on the displayed local
spaces. It is not a numerical physical current. Independent left data are
kept separate; no analytic left source is obtained by conjugating the right.

## 2. Exact weighted action graph, with every angular degree

The saved full-angular pole result owns

    P0=partial_rho-A/rho,
    spec(A)={n+1,-n-2} for n>=0 and {n,-n-1} for n>=1.

The eta term is included in these exponents. For z=rho^-1/4 u, conjugate
the operator exactly rather than bounding its extra weight by a triangle:

    rho^-1/4 P0 u = Q z,
    Q=partial_rho-(A-1/4)/rho.

The regular compact-core identity is

    ||Qz||^2=||z_rho+z/rho||^2+||(A+3/4)z/rho||^2.

An uncut physical section retains the corresponding boundary term. The
uniform angular gap is now 5/4. On all four branches, polynomial
certificates prove

    n(n+2) <= (48/25)(A+3/4)^2,
    |A+1/2| <= (6/5)|A+3/4|.

They are certificates for every allowed integer n, not a finite-mode scan.
For example the first inequality on A=-n-1 reduces, after multiplication
by 25, to (n-1)(23n-3)>=0. The other three polynomials and their lower
limits are saved in the result receipt.

Integration by parts also gives
||z_rho||^2=||z_rho+z/rho||^2+||z/rho||^2 on the regular compact core.
Since ||z/rho|| <= (4/5)||(A+3/4)z/rho||,

    H(u) <= (8/5)||rho^-1/4 P0u||.                         (2)

If both independent sections possess these graph norms, (1)-(2) give

    N(j_phi) <= m_plus (16 sqrt(3)/25) G(v) G(u),
    G(u)=||rho^-1/4 P0u||,
    16 sqrt(3)/25 = 1.1085125168440815.                     (3)

The functional inequality can be applied separately to the left row as a
vector of components. It does not identify its dynamical adjoint operator
with the right operator. Its actual independent left equation/domain must
supply the required norm. In particular no native left return is replaced
by a physical current adjoint without the owned correspondence.

For the original spatial operator

    P=P0-delta(A+1/2)/rho+V0,  delta=rho C_rho/R-1,

the small relative-remainder sufficient estimate has

    eta=(6/5) delta_sup+(4/5) sup(rho ||V0||),
    H(u) <= 8/[5(1-eta)] ||rho^-1/4 P u||, if eta<1.        (4)

Smallness of V0 is unnecessary if retained as a lower-order source:

    H(u) <= 8/[5(1-eta_ang)]
            [||rho^-1/4 P u||+||V0 rho^-1/4 u||],
    eta_ang=(6/5) delta_sup <1.                            (5)

These are sufficient local estimates, not additional BHSM admission laws.
The material-time forcing, angular terms, source jets and cutoff shell
P(chi u)=chi Pu+chi_rho u remain. An exact Lorentz solution D u=0 does not
set Pu=0. No sharp zero extension through a retained/released edge is used.
Global use needs actual common-domain lifts and continuum coefficient bounds.

## 3. What the old graph norm cannot establish

This issue can be decided without selecting a physical state. On arbitrary
smooth compact annular core test sections, the cone dilation
u_epsilon(rho,Omega)=epsilon^-1 u(rho/epsilon,Omega) has

    ||u_epsilon||_2^2 scaling as epsilon^2,
    ||P0 u_epsilon||_2^2 scaling as epsilon^0,
    N(rho^3 |u_epsilon|^2)^2 scaling as epsilon^-1,
    G(u_epsilon)^2 scaling as epsilon^-1/2.

Thus a uniform current-product bound from just the old L2/first-graph
norms is impossible on that core; the stronger weighted estimate has the
right scaling. These are exact operator homogeneities, not proposed beam
states or proof that the actual dressed Gaussian is singular. The physical
Gaussian may be smoother, but its dressed domain/image must establish that.
No lower bound on a physical current or full observable state dependence is
inferred.

## 4. New saved-coefficient application, retaining the correct eta owner

The 49 original nodes, coframe and eta/profile jets are reused. The combined
contact retained since October19 and checked in v45 is

    Eta_f=-i cot(f)(Gamma0 f0+epsilon Gamma4 f4),
    f0=(f_t-beta f_rho)/N, f4=f_rho/C_rho.

It has no unit-sigma-normal denominator. The known null/timelike sigma
regions in this initializer do not obstruct this causal coefficient. The
earlier unit-normal diagnostic in run_2 is preserved but superseded for
this application. The source-dependent tangential profile term is not
discarded merely because base alignment happened to hold on regular patches.

After multiplying by the inverse radial principal, the newly assembled
lower-order spatial coefficient is

    V0=C_rho h4 I+(i epsilon C_rho Gamma4) Eta_f-I/(2rho)
       +G(A_rho)-epsilon(C_rho/R) sum_a Gamma4 Gamma_a G(A_a).

The full mechanical connection enters A_a once. Both orientation signs,
all 36 lepton normal-pair components, the material-time eta factor, and
independent gauge coefficients are retained. Higgs is the once-owned seam,
not a new D5 bulk mass. Native/relative response is not appended as a second
classical body. This is the saved initializer's coefficient, not the unknown
child parent-minus-reference-plus-child connection or a physical background.

This P is the spatial application. The remaining full D5 term is
`i Gamma0/N (partial_t-beta partial_rho+G(A_t-beta A_rho)+N h0)`;
it supplies the actual material-time forcing when solving for Pu. Any owned
spectral-energy/source term also remains in that forcing. Temporal gauge,
clock and geometric contacts have not been dropped or claimed bounded by
the spatial V0 samples. The auxiliary rho^-1/4 weight changes the estimate,
not the action's physical Riesz density or normalization.

Direct reconstruction agrees with the original D5 spatial expression. A
separate Clifford check retains the eta time term explicitly:

    (i epsilon C_rho Gamma4) Eta_f
      = epsilon C_rho cot(f) Gamma4 Gamma0 f0
        -C_rho cot(f) f4 I.

Numerical results on the saved nodes:

* max sampled angular relative term (6/5)|delta|: 0.6299860375788896;
* max sampled full relative term in (4): 4.142904865160313;
* sampled density ratio m: 0.2157152511002745 to 0.834429917594814.

The full value above one rules out absorbing every lower-order term by (4)
over the whole saved cap. It is not physical instability, inconsistency or
an obstruction to (5). The angular samples below one do not prove a continuum
supremum. No cutoff radius or new resolution is chosen from these samples.
The regular germ guarantees local asymptotic control only under its stated
actual-background hypotheses; it supplies no physical norm values here.

## 5. Native/relative source: keep the original weak formulation

The recovered action differentiates the product on its full domain,
P_zeta=M_zeta U_L R+L M_zeta U_R, with the derivative-of-test vertex
L^a U_R. The completed relative resolvent/heat kernel, matching and product
domain contacts must accompany it. The finite stationary18 coefficient
does not evaluate that full same-domain kernel.

Write the complete local weak source, in its owned density convention, as

    J_native[zeta]=integral [a zeta+b^rho D_rho zeta+b^i D_i zeta]
                   +J_domain/edge[zeta].

A strong density would involve a-div b. Demanding that derivative belong
to weighted L2 is only one route; it is not required by the original weak
equations. On the regular zero-outer-trace electric core, with
k>=kappa_minus rho^6 and angular coefficient e>0, the original Hardy
identity and Cauchy-Schwarz instead give

    ||J_native||_V* <= 2/(5 sqrt(kappa_minus)) ||a||_L2(rho^-4)
        + [integral (|b^rho|^2/k+sum_i |b^i|^2/e)]^(1/2).   (6)

For actual nonzero traces add the true domain/edge functional in the common
trace dual norm and use a bounded lift. This does not multiply a weak flux
by a discontinuous retained indicator. The conormal b.nu, event/endpoint
work, B_R variation, B_L R variation, cutoff motion and relative completion
belong to that same functional. The overlap is subtracted once. All nine
ordered mixed placements persist when it is differentiated.

Equation (6) identifies a weaker constructive target for the native source:
the completed kernel's a and b contractions, rather than unnecessary strong
derivatives of every kernel component. Their actual values/norms and the
physical trace graph are still uninstantiated. The pair bound does not
bound this remainder, and a partial nonzero vertex does not establish
dependence of the complete magnetic observable on an inherited density.

## 6. Exact next obligation and verification

A local bounded current map is now available. To use it for the actual
prescribed Cauchy columns requires their weighted material-time/entering
jets, the independent left data, original density/frame maps, and actual
cutoff/trace lifts. The stationary-past Gaussian condition remains fixed;
no bare packet is substituted for its dressed image. Its full physical
background and source-domain correspondence have not been constructed.

The native calculation can continue in the weaker formulation (6), but
still needs the same-domain first-order return and event-generated
retained/released graph to evaluate a,b and J_domain/edge. Existing local
matching coefficients and newly formed child points do not supply that
solved graph. This is a coupled construction obligation, not a new author
choice or proof of an absent physical law. No broad background/history
solve is launched while its complete residual remains unevaluable.

Eight rational identities, all-degree polynomial certificates, seven
numerical coefficient checks and six focused tests verify this checkpoint.
The maximum numerical defect is 6.59383658785373e-12, below the unchanged
2e-11 method tolerance. Final outputs are run_5/run_6 with portable replay.
The looser run_1 and unit-normal diagnostic run_2, with source snapshots and
amendments, remain preserved. Intermediate run_3/run_4 record the correct
combined body and added weak-form checks; none is physical admission.

Execution uses the same inspected-root, guarded C:\Python314\python.exe
-I -S invocation. No new worker, resolution, quadrature, heat campaign,
history solve, occupation, physical flux value, commit or push is used.
The 2e-10 physical guard and admitted temporal t=2^-9 baseline are unchanged.
Physical reconnection, complete residual, a_mu/g_mu and total uncertainty
remain uncomputed.
