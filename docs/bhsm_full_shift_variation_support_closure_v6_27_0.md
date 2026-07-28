# BHSM v6.27.0: full shift variation and fold-support closure

## Scope and inherited data

This sprint starts from the frozen covariant P1+GHY action, not from the
reduced scalar-potential equation. It introduces no action term, primitive,
scale, coefficient, boundary axiom, state prescription, or measured input.
The v6.26 closed-dS4 background and normalization are inherited:

\[
 ds_4^2=-du^2+a_4(u)^2d\Omega_3^2,\qquad
 \Box_4q=-\ddot q-3H_4\dot q ,
\]
\[
 W=B+\tau{\pi\chi_1\over16}tq,\qquad
 C_M=-{3\kappa_1X_c\over N_0a_0(t)^2}.
\]

The base is main
`7a5de9fc2d9ad75504ed9db40d42b92aa1bc38e6`; the v6.26 scientific
predecessor is `aa146f05db8d63ef9436b3fc1cf94b79eba4c755`.

## Parent variational provenance

The repository-native exact variation in
`src/bhsm/interface/intrinsic_m4_junction_background.py:241-253` varies the
independent bulk metric before the independent intrinsic metric, matching,
or any perturbative ansatz. Thus the mixed component \(g_{\rho\mu}\), or
equivalently the radial ADM shift \(N_\mu\), is an independent parent metric
component.

The exact stored shift equation in
`src/bhsm/interface/moving_endpoint_shift_domain.py:238-246` is

\[
 D_\nu(K^\nu{}_\mu-\delta^\nu{}_\mu K)
 =\kappa_1^{-1}Z_5(n\sigma)D_\mu\sigma .
\]

That same source records that the shift enters \(K_{\mu\nu}\) through
tangential derivatives only, has no radial derivative, and produces no
independent pole or B1 endpoint term. GHY has already completed the
metric-variation boundary cancellation. The intrinsic B1 action and matcher
depend on the pulled-back tangential metric at fixed embedding, not on an
independent shift trace. The interior shift is freely varied as a constraint
multiplier (`moving_endpoint_shift_domain.py:278-284`). No frozen declaration
excludes a smooth compactly supported, spatially homogeneous
\(\delta N_u(u,\rho)\).

The scalar representation \(\delta N_\mu=D_\mu\lambda\) appears only in the
later scalar-sector analysis
(`seam_slide_symmetry_quotient.py:342`). It is therefore a projection of the
parent tensor system, not the definition of its variational domain.

## Arbitrary full-shift variation

Use

\[
 ds_5^2=N^2d\rho^2+\gamma_{\mu\nu}
 (dx^\mu+N^\mu d\rho)(dx^\nu+N^\nu d\rho),
\]
\[
 K_{\mu\nu}={1\over2N}
 \left(\partial_\rho\gamma_{\mu\nu}
 -D_\mu N_\nu-D_\nu N_\mu\right),\qquad
 Q_{\mu\nu}=K_{\mu\nu}-K\gamma_{\mu\nu}.
\]

At fixed \(N,\gamma_{\mu\nu}\),

\[
 \delta_NK_{\mu\nu}=-{1\over2N}
 (D_\mu\delta N_\nu+D_\nu\delta N_\mu).
\]

The shift part of the completed gravitational variation is therefore

\[
 \delta_NS_{\rm grav}
 =-\kappa_1\int d\rho\,d^4x\sqrt{|\gamma|}
 Q^{\mu\nu}D_\mu\delta N_\nu
\delta_NS_{\partial M_4}.
\]

Tangential integration by parts, including the scalar source, gives

\[
 \delta_NS
 =\int d\rho\,d^4x\sqrt{|\gamma|}\,
 {\cal M}^\mu\delta N_\mu
 -\kappa_1\int_{\partial M_4}\sqrt{|s|}\,
 s_\mu Q^{\mu\nu}\delta N_\nu ,
\]
\[
 {\cal M}_\mu
 =\kappa_1D_\nu Q^\nu{}_\mu
 -Z_5(n\sigma)D_\mu\sigma .
\]

The M4 boundary term vanishes for local compact-support test variations (and
there is no spatial boundary on closed \(S^3\)). There is no radial
integration by parts because \(N_\mu\) has no \(\partial_\rho N_\mu\).
Consequently the regular-pole term and B1 shift endpoint term are both zero.
Each reflected cap supplies its own constraint; the common-normal convention
doubles the junction jump but does not cancel the two local equations.

Arbitrariness of \(\delta N_\mu\) gives

\[
 {\cal M}_\mu=0.
\]

This proves
`BHSM_FULL_SHIFT_VARIATION_IMPOSES_COMPLETE_MOMENTUM_CONSTRAINT`.

## Reduction does not commute with variation

In the v6.26 linearized sector the parent equation is

\[
 {\cal M}_\mu=C_MD_\mu W=0.
\]

If \(N_\mu=D_\mu B\) is imposed first, then
\(\delta N_\mu=D_\mu\delta B\), and a second tangential integration by parts
gives

\[
 \delta_BS=-\int\sqrt{|\gamma|}\,\delta B\,D_\mu{\cal M}^\mu
 +\text{M4 boundary}.
\]

It tests only

\[
 D_\mu{\cal M}^\mu=0,\qquad
 -D^\mu{\cal M}_\mu
 ={3\kappa_1X_c\over N_0a_0^2}\Box_4W.
\]

For a homogeneous covector, \(D_\mu{\cal M}^\mu=0\) is
\(\dot{\cal M}_u+3H_4{\cal M}_u=0\), so

\[
 {\cal M}_u={C\over a_4^3},\qquad {\cal M}_i=0
\]

is a nonzero divergence-free kernel. The two routes commute only when this
kernel vanishes in the declared domain or is independently imposed by the
parent equation. Smoothness, local finite action, fixed support, and the B1
shift endpoint audit do not remove it.

For static round-\(S^3\) harmonics the stored scalar operator has eigenvalue
\(-2\ell(\ell+2)/a_S^4\). It is nonzero for \(\ell\ge1\). The \(\ell=0\)
potential is constant, has zero gradient, and is exactly the inherited
\(C_\Sigma\) stabilizer sector. This is why the Lorentzian ambiguity was not
present in v6.18.

The theorem is
`BHSM_SCALAR_REDUCTION_BEFORE_VARIATION_LOSES_C1_MOMENTUM_CONSTRAINT`.
The correction restores an existing parent constraint and is classified
`BHSM_SHIFT_SECTOR_REPAIRABLE_REDUCTION_ERROR`.

## C1 and endpoint closure

The reduced equation permits

\[
 W_h=C_0+C_1\int^u{du'\over a_4(u')^3}.
\]

But the parent time component evaluates to

\[
 {\cal M}_u[W_h]
 =-{3\kappa_1X_c\over N_0a_0^2}{C_1\over a_4^3}.
\]

Arbitrary admissible \(\delta N_u\) therefore forces \(C_1=0\). This is a
local Euler--Lagrange constraint, not retarded, advanced, Feynman, Euclidean,
initial, final, or normalizability data. The constant \(C_0\) is invisible to
the vector constraint and is set to zero only by the inherited v6.18
\(C_\Sigma=0\) scope. Hence

\[
 W=0,\qquad B=-\tau{\pi\chi_1\over16}tq.
\]

The endpoint invariant is uniquely

\[
 {\cal S}_\Sigma=-\tau{\pi\chi_1\over16}q.
\]

Fixed-endpoint gauge, a moving-coordinate representative of the same fixed
support, the full-shift formulation, and the scalar formulation supplemented
by the parent constraint all give this value. The verdict is
`BHSM_ENDPOINT_TRACE_RESPONSE_DERIVED`.

## B1 scalar system

The four retained projections are temporal/Hamiltonian, scalar momentum,
spatial trace, and traceless scalar-longitudinal. For one cap the direct
threading pieces are

\[
 Q_H^{\rm th}=-3{\tau\chi_1\over4}H_4\dot q,\qquad
 Q_M^{\rm th}=0,
\]
\[
 Q_T^{\rm th}={\tau\chi_1\over4}
 (\ddot q+2H_4\dot q),\qquad Q_{TL}^{\rm th}=0.
\]

With \([Q]=2Q_+\), move these direct terms to the source. After algebraic
matcher elimination define

\[
 Y_{B1}=(\Pi_H,\Pi_T,G_H,G_T,T_H,T_T)^T.
\]

Here \(\Pi_{H,T}\) are the complete non-threading canonical-momentum
projections after the bulk lapse, Weyl, longitudinal, and scalar constraints;
\(G_{H,T}\) are the matched intrinsic Einstein responses; and \(T_{H,T}\)
contain the scalar and other frozen B1 stress responses. The independent
system is

\[
 \begin{pmatrix}
 \kappa_1&0&2C_\partial&0&-1&0\\
 0&\kappa_1&0&2C_\partial&0&-1
 \end{pmatrix}Y_{B1}
 =
 \begin{pmatrix}
 {3\over2}\kappa_1\tau\chi_1H_4\dot q\\
 -{1\over2}\kappa_1\tau\chi_1(\ddot q+2H_4\dot q)
 \end{pmatrix}.
\]

Its rank is two, witnessed by the \((\Pi_H,\Pi_T)\) minor
\(\kappa_1^2\ne0\). The scalar-momentum and traceless-longitudinal rows are
the two Ward-dependent rows. Their zero sources are compatible after the
parent momentum and scalar equations, matcher, and Bianchi identity are
used. The verdict is `BHSM_SCALAR_B1_TWO_EQUATION_SYSTEM_DERIVED`.

## Normal support and support domain

The diagnostic coefficient is

\[
 R_\perp=(\sqrt{|h|})^{-1}
 \delta_{\zeta}^{\rm diag}S_{\rm total}\big|_{\zeta=0}.
\]

There are three equivalent evaluations. Direct differentiation of the
complete fixed-support response reduces it using the bulk Einstein,
momentum, and scalar equations plus matcher, endpoint trace, and the two B1
rows. The Gauss--Codazzi normal projection expresses it as
\(k_HJ_H+k_TJ_T\). The boundary Noether identity gives the same linear
combination of bulk Euler expressions and junction rows. Appending this row
to the rank-two B1 matrix leaves rank two.

Thus through local two-derivative order,

\[
 R_\perp^{(2)}
 =0\,\ddot q+0\,H_4\dot q+0\,\Box_4q.
\]

After \(\Box_4q=-\ddot q-3H_4\dot q\), both independent coefficients remain
zero. This gives
`BHSM_NORMAL_SUPPORT_RESIDUAL_VANISHES_THROUGH_D2Q` and
`BHSM_FOLD_LOCALIZATION_COMPATIBLE_WITH_FIXED_B1_SUPPORT`. No dynamical
embedding, new gluing datum, or embedding Euler--Lagrange equation is needed.

## Operator reopening and bounded continuation

On \(M_5=[0,1]_t\times M_4\), \(B_1=\{t=1\}\), take
\(Y_{\rm red}=(A,\psi,\delta\sigma_\perp)\). Scalar gauge sets \(E=0\);
the parent momentum constraint fixes \(B\); matcher variables are eliminated;
and \(q\) is the external collective source. The reopened structure is

\[
 L(\lambda)=L_0+\lambda L_1+O(\lambda^2),\qquad
 J(\lambda)=J_0+\lambda J_1+O(\lambda^2).
\]

Its inventory contains the lapse/Hamiltonian block, lapse--Weyl mixing,
critical Weyl/radial Einstein block, orthogonal scalar Sturm--Liouville
block, metric--scalar mixing, the two B1 rows, and the unique q source.
Boundary data are pole regularity, fixed B1 support, \(W=0\), the rank-two
junction system, scalar Dirichlet trace, and metric matching.

The fully expanded action-normalized \(L_0,L_1\), adjoint boundary domain,
and reopened kernel/compatibility classification are not yet complete.
Therefore no inverse or Schur number is emitted:
`BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_INCOMPLETE_REOPENED_RADIAL_OPERATOR_AND_ADJOINT_DOMAIN`.
For the identical reason the kinetic sign remains unresolved. No mass or
stability claim follows.

## Hindsight

Validated: the parent arbitrary-shift constraint, its absolute v6.26
normalization, C1 elimination, unique endpoint trace, rank-two B1 system,
Noether-dependent normal residual, and fixed-support compatibility.

Invalidated: treating \(\Box_4W=0\) as the complete shift equation, treating
\(C_1\) as an unstored Lorentzian state, and treating that reduced kernel as
a support-domain obstruction.

Still active: expansion of the complete reopened radial operator and its
adjoint domain before optional Schur and kinetic work.

The repeated loop was caused by premature reduction before variation, not a
physical zero mode and not a missing action domain.
