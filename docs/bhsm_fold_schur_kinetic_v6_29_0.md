# BHSM v6.29.0: projected Schur reduction and fold kinetic norm

## Scope

This phase uses the complete v6.28 operator pencil, radial domain, scalar
projector, and Lyapunov--Schmidt kernel equation. It evaluates the local
two-derivative fold kinetic coefficient without selecting a global
Lorentzian propagator or applying an inverse to the unprojected \(L_0\).

The result is

`BHSM_FOLD_KINETIC_NORM_POSITIVE_CONDITIONALLY`.

This is a kinetic statement in the normalized frozen representative. It is
not a potential-stability theorem and does not define a physical mass.

## Operator-pencil identity

For

\[
L(\lambda)=L_0+\lambda L_1,\qquad
J(\lambda)=J_0+\lambda J_1,\qquad
K(\lambda)=K_0+\lambda K_1,
\]

the derivative of the regular Schur expression is

\[
{d\over d\lambda}
\left[K-\langle J,L^{-1}J\rangle\right]_{\lambda=0}
=K_1
-2\langle J_1,L_0^{-1}J_0\rangle
+\langle J_0,L_0^{-1}L_1L_0^{-1}J_0\rangle.
\]

The scalar symbolic identity has exactly zero residual.

The v6.28 affine convention has \(J_0=L_0v\) on the complementary range.
Consequently \(Y_0=-v\), and the \(L_1v\) term in \(J_1\) cancels the
\(L_1Y_0\) term. This is the explicit singular-pencil version of affine
Schur invariance. Complementary \(J_1\) sources produce a response of
order \(\lambda\), hence contribute first at \(O(\lambda^2)\), not to the
two-derivative kinetic coefficient.

## Metric-modulus Schur term

The one quotient kernel representative is

\[
z_A=\sec^2{\pi t\over4},\qquad z_\psi=1.
\]

After affine cancellation, only the v6.27 threading source pairs with this
mode. Since \(z_{\psi,t}=0\),

\[
j_z=\int_0^1 w J_A^{(B)}z_A\,dt.
\]

Using

\[
B_q=-\tau{\pi\chi_1\over16}t,\qquad
J_A^{(B)}
={6\kappa_1B_q(a_{0,t}/a_0)\over N_0^2a_0^2},
\]

the integral is exact:

\[
j_z=\tau\chi_1\kappa_1
\left({3\over2}\ln2-{6G\over\pi}\right),
\]

where \(G\) is Catalan's constant.

The v6.28 bulk-plus-B1 lifting coefficient is

\[
M_z=\langle z,L_1z\rangle
=12C_\partial+3\kappa_1(6-\pi).
\]

It is positive for the frozen normalized representative
\(\kappa_1=1,\ C_\partial/\kappa_1=1/2\):

\[
M_z=3(8-\pi)=14.575222039230620\ldots .
\]

The kernel amplitude is \(c_z=-j_z/M_z\), and the exact gravitational
constraint contribution is

\[
K_{\rm grav,constraint}^J
=-{j_z^2\over M_z}.
\]

With the repository continuation coefficient
\(\chi_1=5.26830787154212\),

\[
j_z=-3.738626513215215\ldots ,
\]
\[
K_{\rm grav,constraint}^J
=-0.9589787495308423\ldots .
\]

The sign is retained as calculated. The source is sheet odd, but its square
makes this contribution sheet independent. The B1 term is included in
\(M_z\); dropping it would change the answer. The solve is one-dimensional,
so its algebraic condition number is one.

## Scalar normalization

The critical scalar mode satisfies

\[
u_1''+4\cot\rho\,u_1'+\mu_1u_1=0,\qquad
u_1'(0)=0,\qquad u_1(\pi/4)=0,
\]

with

\[
\int_0^{\pi/4}4\sin^4\rho\,u_1^2d\rho=1.
\]

The two-cap scalar kinetic contribution is

\[
K_{\rm scalar}
=2Z_5\int_0^1N_0a_0^2u_1^2dt
=4Z_5\int_0^{\pi/4}\sin^2\rho\,u_1^2d\rho.
\]

It is recomputed by two methods.

Method 1 uses regular-pole shooting, a Brent eigenvalue root, dense
Runge--Kutta output, and adaptive Gauss--Kronrod quadrature. It gives

\[
\mu_1=29.43091835294703\ldots ,
\qquad
K_{\rm scalar}=6.673443432880100\ldots .
\]

Method 2 uses

\[
u_1(\rho)\propto
{}_2F_1(-\nu,\nu+4;5/2;\sin^2(\rho/2)),
\qquad \mu_1=\nu(\nu+4),
\]

with a 60-decimal root and tanh--sinh quadrature. It gives

\[
\mu_1=29.430918352947562\ldots ,
\qquad
K_{\rm scalar}=6.673443432880109\ldots .
\]

The kinetic values differ by \(8.9\times10^{-15}\). The shooting endpoint
residual is below \(2\times10^{-15}\), its integrated eigenvalue residual is
below \(2\times10^{-14}\), and the hypergeometric endpoint residual is below
\(2\times10^{-61}\). Both weighted norms equal one at reported precision.

The next Dirichlet eigenvalue is

\[
\mu_2=93.44565502193322\ldots ,
\]

so the projected scalar gap is

\[
\mu_2-\mu_1=64.01473666898566\ldots>0.
\]

This verifies that the \(P_\perp\) scalar solve has no remaining zero mode.

## Weyl contribution and total

The inherited Einstein-frame Weyl term is counted exactly once:

\[
K_{\rm Weyl}
={3\chi_1^2(4-\pi)^2\over16\pi}
=1.220620174933802\ldots .
\]

Thus

\[
\begin{split}
k_q^E
&=K_{\rm scalar}
+K_{\rm grav,constraint}^J
+K_{\rm Weyl}\\
&=6.673443432880105
-0.9589787495308423
+1.220620174933802\\
&=6.935084858283065.
\end{split}
\]

A conservative numerical uncertainty of \(2\times10^{-12}\) is assigned,
well below the distance from zero. Therefore

\[
k_q^E>0.
\]

The sign is independent of the fold sheet and scalar sign at quadratic
order. The negative-norm audit is not triggered because the complete
coefficient is positive; the negative gravitational Schur contribution is
reported rather than hidden.

## Integrity and handoff

The calculation uses the normalized repository representative

\[
\kappa_1=Z_5=1,\qquad C_\partial/\kappa_1={1\over2},
\]

and the repository-derived continuation/Fredholm coefficient \(\chi_1\).
No measured mass, coupling, mixing value, fitted coefficient, or chat-only
candidate enters.

No global state, generic pseudoinverse, unprojected inverse, new action,
primitive, scale, or physical mass is introduced. Frozen predictions and
official prediction logic are unchanged.

Phase v6.30 is permitted to derive the full off-shell Jordan potential,
frame function through \(F_2\), Einstein-frame stationary point, and
dimensionless mass curvature. A positive kinetic norm alone does not decide
the sign of that curvature.
