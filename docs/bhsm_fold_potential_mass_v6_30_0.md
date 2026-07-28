# BHSM v6.30.0 Einstein-frame potential and fold mass

Primary result:
`BHSM_FOLD_EINSTEIN_POTENTIAL_REQUIRES_FIXED_ACTION_OFFSHELL_RADIAL_FAMILY`.

The completed v6.28 quadratic action resolves one part of the historical
v6.12 potential obstruction. It determines the invariant Einstein-frame
Hessian at the critical fold without determining the coefficient functions
\(V_J(q)\) and \(F(q)\) separately. The critical Hessian is exactly null, so
the positive v6.29 kinetic coefficient gives an exactly null dimensionless
mass curvature at \(q_0=0\).

The full off-shell potential is not derived. The stored Puiseux continuation
changes the control \(\mu=-A_5/Z_5\) with \(q\), and therefore moves through
neighboring actions rather than evaluating one fixed action away from its
equations of motion. Phase v6.31 is not permitted.

## Formal Einstein transformation

Write

\[
F(q)=F_0+F_1q+\frac12F_2q^2+\cdots ,
\qquad
V_J(q)=V_0+V_1q+\frac12V_2q^2+\cdots .
\]

For

\[
V_E(q)=\left(\frac{F_0}{F(q)}\right)^2V_J(q),
\]

the value and first two derivatives at the fold are

\[
V_E(0)=V_0,
\]

\[
V_E'(0)=V_1-2\frac{F_1}{F_0}V_0,
\]

\[
V_E''(0)
=V_2-4\frac{F_1}{F_0}V_1
+\left[
6\left(\frac{F_1}{F_0}\right)^2
-2\frac{F_2}{F_0}
\right]V_0.
\]

The critical background obeys the complete frozen Euler--Lagrange and B1
junction equations, so it is stationary:

\[
V_1=2\frac{F_1}{F_0}V_0.
\]

After this substitution,

\[
V_E''(0)
=V_2-2\left[
\left(\frac{F_1}{F_0}\right)^2+\frac{F_2}{F_0}
\right]V_0.
\]

Thus stationarity alone does not determine the Hessian coefficientwise.
The sensitivities are

\[
\frac{\partial V_E''}{\partial V_2}=1,
\qquad
\frac{\partial V_E''}{\partial F_2}=-2\frac{V_0}{F_0}.
\]

No vacuum constant is subtracted. If \(V_0\ne0\), \(F_2\) is indispensable.
Even an unsupported choice \(V_0=0\) would leave \(V_2\) undetermined.

The inherited exact frame coefficients are

\[
F_0=\frac{\pi}{2},
\qquad
F_{1,\tau}=\tau\frac{\chi_1(\pi-4)}4,
\]

and

\[
F_2=4\int_0^1\left[
N_0(a_1^2+a_0a_2)+2N_1a_0a_1+\frac12N_2a_0^2
\right]dt.
\]

The analytic profiles \(a_2(t)\) and \(N_2(t)\) are not stored.

## Invariant critical Hessian

The missing coefficientwise reconstruction does not prevent evaluation of
the complete invariant quadratic form. In the v6.28 affine convention,

\[
Y_{\rm total}=Y+qv,
\]

the zero-derivative metric terms obey

\[
J_0=L_0v,\qquad K_0=\langle v,L_0v\rangle .
\]

On the projected complementary range,

\[
K_0-\langle J_0,L_0^{-1}J_0\rangle=0.
\]

The scalar amplitude is the normalized critical Jacobi mode \(u_1\), so its
zero-derivative quadratic form also vanishes. The metric modulus is handled
by the v6.28 Lyapunov--Schmidt compatibility condition; no inverse on the
unprojected kernel is used.

Therefore

\[
V_{J,\mathrm{red}}''(0)=0.
\]

At a stationary point, a regular field redefinition maps Hessians by
congruence. Since \(F_0=\pi/2>0\), the Jordan-to-Einstein transformation is
regular and preserves the null mode:

\[
\boxed{V_E''(0)=0}.
\]

Equivalently, the complete quadratic action fixes the otherwise unknown
coefficient combination:

\[
V_2
=2\left[
\left(\frac{F_1}{F_0}\right)^2+\frac{F_2}{F_0}
\right]V_0.
\]

This is one invariant relation. It does not reconstruct \(V_2\), \(F_2\), or
the nonlinear functions separately.

## Canonical dimensionless mass

The merged v6.29 result is

\[
k_q^E=6.935084858283065\pm2\times10^{-12}>0.
\]

Consequently,

\[
\boxed{
\mu_q^2=\frac{V_E''(0)}{k_q^E}=0
}.
\]

The exact verdict
`BHSM_FOLD_DIMENSIONLESS_MASS_CURVATURE_DERIVED` is emitted with the scope
"at the critical stationary fold \(q_0=0\)." The classification is
`BHSM_FOLD_CRITICAL_MASS_CURVATURE_NULL`.

This is neither a ghost nor a tachyon. It is also not a positive massive
mode. No eV/GeV mass or stability away from \(q_0\) follows.

## Why the inherited cusp is insufficient

The inherited fixed-control normal form is

\[
\Gamma_{\rm red}-\Gamma_c
=\frac{\delta\mu}{4}q^2-\tau\frac{\nu_1}{6}q^3+\cdots .
\]

Its branch equation is

\[
\delta\mu=\tau\nu_1q+O(q^2),
\]

which gives the stored on-shell cusp

\[
\Gamma_{\rm branch}-\Gamma_c
=\tau\frac{\nu_1}{12}q^3+O(q^4).
\]

But \(\mu=-A_5/Z_5\) is an action control. Substituting
\(\delta\mu(q)\) compares different actions. The Puiseux continuation also
uses an \(X\)-dependent M4 geometry whose common regulated action density was
never supplied. Its cusp cannot be relabeled as the fixed-action
\(V_J(q)\).

The smallest missing object is a fixed-action, fixed-regulator off-shell
constrained radial family \(\mathcal C_{q,\tau}\) that:

- holds \(\kappa_0,\kappa_1,Z_5,A_5,G_5,C_\partial\) fixed;
- keeps the independent M4 metric off shell;
- supplies \(a_2,N_2\) and higher radial responses;
- evaluates P1, GHY, scalar, B1, and matcher terms with one common M4
  density;
- derives \(F(q)\) and \(V_J(q)\) before imposing the M4 metric equation.

This is a class-B missing derivation within the frozen action. It is not a
fatal inconsistency and requires no new action term.

## Campaign stop

The local result
`BHSM_FOLD_EINSTEIN_POTENTIAL_DERIVED_THROUGH_QUADRATIC_ORDER_AT_CRITICALITY`
and the exact null mass curvature are derived. The required full-potential
verdict
`BHSM_FOLD_EINSTEIN_FRAME_POTENTIAL_DERIVED` is deliberately not emitted.

The campaign therefore stops at v6.30 with
`BHSM_FULL_CLOSURE_CAMPAIGN_STOPPED_AT_V6_30_CLASS_B_BLOCKER`.
Phase v6.31 is not permitted.

No measured input, fit, chat-only value, new action, primitive, scale,
vacuum subtraction, frozen prediction change, official prediction-logic
change, physical mass, or global potential-stability claim is introduced.
