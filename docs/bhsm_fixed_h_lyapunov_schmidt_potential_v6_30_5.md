# BHSM fixed-h Lyapunov--Schmidt potential v6.30.5

## Executive result

The strict fixed-\(h\), fixed-curvature D0 problem admits a
Lyapunov--Schmidt complement family through fourth order. It does not
generically admit a neighboring exact radial on-shell branch.

With

\[
\gamma=G_5/Z_5,\qquad \zeta=Z_5/\kappa_1,
\]

the third-order reduced-force coefficient is

\[
g_3=130.140781376472814\,\gamma
+2368.235930657732552\,\zeta .
\]

The source convention is \(\Omega_3=-g_3\). Thus \(G_5>0\), \(Z_5>0\),
and \(\kappa_1>0\) certify \(\Omega_3<0\): the exact branch fails its
order-three Fredholm condition, while the complement family and effective
potential remain valid.

After fixed-\(h\) extraction, the \(q=0\) M4 stationarity equation
reproduces the D0 null Hessian. The first nonzero Einstein-frame
interaction is

\[
V_{E,4}=260.281562752946\,G_5
+3633.0356624841\,Z_5^2/\kappa_1.
\]

It is a local quartic minimum in the stable-wall sign domain \(G_5>0\).
The frozen repository does not select \(G_5\)'s sign or magnitude, so the
unconditional classification remains open and v6.31 is not permitted.

## Inherited operator and second order

The KKT vector is
\(\mathbb Y=(A,\psi,\delta\sigma,\eta_{\rm tr})\), with fixed induced
metric, scalar Dirichlet trace, and matcher reaction. The realization is
the symmetric saddle operator derived in v6.30.2, not a Robin operator.
Its scalar complement has certified gap \(64.0147366689857\).

The v6.30.4 tangent and response are

\[
\Phi_1=(0,0,u_1,0),
\]

\[
A_2=-\frac{Z_5}{12\kappa_1}\tan^2\rho
(u_1'^2+\mu_cu_1^2),\qquad \psi_2=\sigma_2=0,
\]

\[
\eta_2=-24\kappa_1A_2(\pi/4),
\]

with \(\int_0^{\pi/4}4\sin^4\rho\,u_1^2d\rho=1\).

## Exact branch versus reduced family

An exact radial branch requires \(\mathcal R(\Phi(q))=0\). The reduced
family solves the complement equations and retains the cokernel component
as the amplitude force. The radial Euler expressions obey

\[
a'E_a+\sigma'E_\sigma-N(E_N)'=0.
\]

Therefore the nonlinear residual representative is not literally the base
pure scalar vector. On the Hamiltonian constraint surface it is

\[
\Xi(\Phi):\quad E_N=0,\quad E_\sigma=\xi_\sigma,\quad
E_a=-(\sigma'/a')\xi_\sigma.
\]

At \(\Phi_0\), \(\sigma'_0=0\), so \(\Xi(\Phi_0)\) is pure scalar. At
order four its metric component is exactly the Noether completion of the
order-three scalar force. No equation is deleted.

## KKT projectors and amplitude coordinate

The exact projector is

\[
PX=\Phi_1\langle\Phi_1^\dagger,X\rangle_{\rm KKT},\qquad Q=I-P,
\]

because \(\mathcal N=1\). The endpoint saddle pairing vanishes on the
kernel. Exact coefficient algebra gives
\(P^2=P\), \(Q^2=Q\), and \(PQ=QP=0\).

The amplitude coordinate is

\[
\langle\Phi_1^\dagger,\Phi(q)-\Phi_0\rangle_{\rm KKT}=q,\qquad
P\Phi_n=0\quad(n\ge2).
\]

This is a coordinate condition, not an amplitude multiplier or new action
term.

## Third-order source and Noether identity

Define

\[
r_3=\gamma u_1^3-\mu_cA_2u_1+\frac12A_2'u_1'.
\]

In the factorial convention,

\[
\mathbb L_D\Phi_3=S_3,\qquad S_{3,\sigma}=-6r_3.
\]

The terms originate respectively in the frozen scalar quartic, quadratic
potential times lapse response, and scalar kinetic lapse/measure response.
Odd Hamiltonian, tangential, matcher-trace, and reaction sources vanish by
reflection. GHY, B1, and matcher projections vanish capwise because the
trace is fixed, \(u_1(\pi/4)=0\), and the adjoint kernel has no reaction
component.

At source order three the Noether coefficient contains no
\(\sigma'E_\sigma\) term because \(\sigma'_0=0\). The reduced scalar force
generates its required tangential completion one order later.

## Third-order projection and exact branch

The independent moments are

\[
M_4=\int4\sin^4\rho\,u_1^4d\rho
=21.6901302294121357,
\]

\[
C_{\rm grav}=394.705988442955425.
\]

Thus

\[
\Omega_3=-6(\gamma M_4+\zeta C_{\rm grav}),\qquad g_3=-\Omega_3.
\]

The sole third-order cancellation locus is

\[
\gamma=-18.1974927890349085\,\zeta.
\]

The exact branch is generically blocked and is rigorously blocked for
\(G_5>0\). The parameterized action admits the displayed algebraic
cancellation, but no repository theorem selects it.

Adaptive regular-pole shooting with Gauss--Kronrod projection and an
independent augmented Dirichlet collocation solve reproduce both moments.
Artifacts contain conservative cross-platform discrepancy bounds, not raw
last-bit differences.

## Complement \(\Phi_3\)

The scalar complement solves

\[
(\partial_\rho^2+4\cot\rho\,\partial_\rho+\mu_c)\sigma_3=6Qr_3,
\]

with

\[
\sigma_3'(0)=0,\quad \sigma_3(\pi/4)=0,\quad
\langle u_1,\sigma_3\rangle=0.
\]

It decomposes as
\(\sigma_3=\gamma\sigma_{3,G}+\zeta\sigma_{3,\rm grav}\). The exact
Dirichlet spectral complement inverse is used; there is no pseudoinverse or
empirical regularization.

## Fourth-order construction

In fixed-h areal gauge,

\[
N^2=\frac{6\kappa_1H_0^2-Z_5\sigma'^2/2}
{6\kappa_1H_0^2-U_5(\sigma)}.
\]

Set

\[
p_2=\frac{Z_5u_1'^2}{12\kappa_1H_0^2},\quad
p_4=\frac{Z_5u_1'\sigma_3'}{36\kappa_1H_0^2},
\]

\[
d_2=\frac{Z_5\mu_cu_1^2}{12\kappa_1H_0^2},\quad
d_4=\frac{Z_5\mu_cu_1\sigma_3}{36\kappa_1H_0^2}
-\frac{G_5u_1^4}{24\kappa_1H_0^2}.
\]

Then

\[
A_4=12(d_2^2-d_4+p_2d_2-p_4-A_2^2/4).
\]

Reflection gives \(\psi_4=\sigma_4=0\), \(P\Phi_4=0\), and
\(\Omega_4=0\). The matcher reaction is

\[
\eta_4=-24\kappa_1A_4(\pi/4)+144\kappa_1A_2(\pi/4)^2.
\]

The tangential residual is the field-dependent Noether completion, not a
failed complement equation.

## Reduced-action identity

For the two identical caps,

\[
\Gamma_{\rm red}'(q)=\mathcal J(q)g(q),
\]

\[
\mathcal J(q)=-2Z_5\int_0^{\pi/4}
\frac{a_0^4}{N}u_1\,\partial_q\sigma\,d\rho.
\]

It is even and \(\mathcal J(0)=-2Z_5\). The minus sign follows from the
repository residual convention and the factor two is cap multiplicity.
Therefore

\[
\Gamma_4=-2Z_5g_3=2Z_5\Omega_3.
\]

Direct action expansion gives the same terms,
\(-12G_5M_4\) and
\(-12Z_5(Z_5/\kappa_1)C_{\rm grav}\). GHY has already canceled the radial
second derivative; fixed B1/matcher trace variations vanish and the
reaction/canonical endpoint pieces cancel in the KKT pairing.

## Jordan coefficients

With \(\Gamma_{\rm red}=F(q)R_c/2-V_J(q)\) and \(R_c=24\),

\[
F_0=\pi/2,\quad F_1=0,\quad
F_2=-6.9387669573380825\,Z_5,
\]

\[
F_4=237.540265238\,Z_5^2/\kappa_1+5.0978230687\,G_5.
\]

No vacuum constant is subtracted:

\[
V_{J,0}\text{ is symbolic},\quad
V_{J,2}=12F_2,\quad V_{J,4}=12F_4+2Z_5g_3.
\]

These are extracted before using the independent M4 metric equation.
\(F_2\) depends on \(\Phi_2\); \(F_4\) depends on \(\Phi_2,\Phi_3,\Phi_4\);
stationarity removes explicit \(\Phi_4\) dependence from \(\Gamma_4\).

## Einstein frame and same-family null Hessian

For \(V_E=(F_0/F)^2V_J\), the raw fixed-\(h\) coefficient is

\[
V_{E,2}=F_2(12-2V_{J,0}/F_0).
\]

Only after extraction, the \(q=0\) stationarity relation
\(V_{J,0}=R_cF_0/4=6F_0\) is applied. It gives

\[
V_{E,1}=V_{E,2}=V_{E,3}=0,
\]

\[
V_{E,4}=-\Gamma_4-36F_2^2/F_0.
\]

This is a D0 derivation and imports no historical D2 \(F_1\).

## Canonical normalization and interaction

Because the D0 first tangent is pure scalar,

\[
k_0=6.673443432880105>0.
\]

The historical \(6.935084858283065\) includes first-order D2
threading/Weyl pieces and is not the D0 norm. With
\(k_E=k_0+k_2q^2/2+\cdots\),

\[
\varphi=\sqrt{k_0}q+\frac{k_2}{12\sqrt{k_0}}q^3+\cdots,
\]

\[
q=\varphi/\sqrt{k_0}
-\frac{k_2}{12k_0^{5/2}}\varphi^3+\cdots.
\]

The unevaluated \(k_2\) cannot affect the first quartic coefficient because
the quadratic and cubic potential terms vanish. Hence

\[
g_4=V_{E,4}/k_0^2
=5.84444718718846\,G_5/Z_5^2
+81.5773688846122/\kappa_1
\]

In the \(Z_5=\kappa_1=1\) representative this is
\(5.84444718718846G_5+81.5773688846122\). The coefficient is dimensionless
in the repository normalization and is not a particle mass.

The exact phase condition removes residual odd amplitude-coordinate
freedom. Independently, the order and sign of the first nonzero canonical
derivative are invariant under admissible odd reparameterizations.

## Local stability and scale permission

The point is a quartic minimum if

\[
G_5/Z_5>-13.95809839182684\,Z_5/\kappa_1,
\]

a maximum below the threshold, and higher-order flat at equality. The
stable-wall domain \(G_5>0\) is strictly in the minimum region. This is only
a local perturbative classification.

The frozen action audit leaves \(G_5\)'s sign and magnitude unselected.
Therefore no unconditional stability, physical scale, or physical mass
follows. The scale verdict is
`BHSM_SCALE_BRIDGE_PHASE_NOT_PERMITTED_WITH_UNSELECTED_G5`.

## Validated, repaired, open, and forbidden

Validated:

- exact projectors and amplitude phase;
- third-order source, projection, complement, and Noether completion;
- fourth-order constraint and matcher response;
- reduced-action/projected-force identity;
- D0 Jordan, Einstein, canonical, and kinetic coefficients.

Repaired:

- nonzero \(\Omega_3\) blocks an exact branch, not the reduced potential;
- the nonlinear cokernel includes its Noether metric component;
- D2 \(F_1\) and kinetic pieces are excluded from D0.

Open:

- frozen selection of \(G_5\);
- unconditional local stability;
- higher interaction at the isolated quartic-cancellation threshold;
- independent dimensionful normalization.

Forbidden:

- an exact-vacuum-family claim away from \(g(q)=0\);
- global stability, physical mass, or scale claims;
- tuning \(G_5\), adding an amplitude multiplier, or importing D2 data.

## Reproducibility

```text
python scripts/materialize_fixed_h_lyapunov_schmidt_potential_v6_30_5.py
python -m pytest -q tests/test_bhsm_fixed_h_lyapunov_schmidt_potential_v6_30_5.py
```

Materialize twice and require byte-identical output, then run the
v6.30.2--v6.30.5 chain and full repository suite.

## Final verdicts

Exact branch in the stable-wall sign domain:

`BHSM_STRICT_FIXED_H_EXACT_ON_SHELL_BRANCH_BLOCKED_AT_THIRD_ORDER_IN_THE_STABLE_WALL_SIGN_DOMAIN`

Reduced family:

`BHSM_FIXED_H_REDUCED_POTENTIAL_FIRST_NONZERO_INTERACTION_DERIVED`

Scale:

`BHSM_SCALE_BRIDGE_PHASE_NOT_PERMITTED_WITH_UNSELECTED_G5`
