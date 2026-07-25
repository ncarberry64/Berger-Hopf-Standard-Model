# BHSM v6.1.5 Scalar-Wall Junction and Coefficient-Source Audit

## Result

Primary result:
`BHSM_MINIMAL_P1_SCALAR_WALL_JUNCTION_NOT_FOUND`.

This result is deliberately narrower than an exclusion theorem. The frozen
scalar action passes a nontrivial constructive test: on the critical v6.1.4
cap, its odd normal operator has a discrete first instability threshold, and
a regular nonlinear scalar profile exists on the fixed cap metric beyond
that threshold. The sprint does not construct a finite-amplitude solution of
the complete coupled Einstein--scalar equations, B1 junction condition, and
constraint-reduced mixed fluctuation problem.

## Frozen action

The effective five-dimensional action audited here is

\[
 S_5=\int d^5x\sqrt{-g}\left[
 \frac{\kappa_1}{2}R_5-\frac{\kappa_0}{2}
 -\frac{Z_5}{2}(\nabla\sigma)^2-U_5(\sigma)\right]+S_{\rm GHY}+S_{\rm B1},
\]

with

\[
 U_5(\sigma)=\frac{A_5}{2}\sigma^2+\frac{G_5}{4}\sigma^4.
\]

The scalar is the already-declared neutral bulk singlet. It is not the
independent provisional B1 field `sigma_partial`. On the frozen internal
slice, `Z5`, `A5`, and `G5` are the corresponding parent coefficients
multiplied by the internal `S3` volume. No new field, interaction, boundary
vacuum constant, or boundary tension is added.

The metric signature is `(-,+,+,+,+)`. In the Gaussian-normal reduction,

\[
 ds_5^2=N(\rho)^2d\rho^2+a(\rho)^2h_{\mu\nu}dx^\mu dx^\nu,\qquad
 R_{\mu\nu}(h)=3Xh_{\mu\nu}.
\]

The lapse is retained until after variation.

## Scalar vacua and the gravitational constant term

The stationary points are `sigma=0` and, when `-A5/G5>0`,

\[
 \sigma=\pm v,\qquad v^2=-A_5/G_5.
\]

The stable double-well sign domain is `A5<0`, `G5>0`. At its two minima,

\[
 U_5(v)=-\frac{A_5^2}{4G_5},\qquad U_5''(v)=-2A_5>0.
\]

This constant is not discarded. The exact equivalent shifted
parameterization is

\[
 \kappa_{0,\mathrm{eff}}
 =\kappa_0+2U_5(v)
 =\kappa_0-\frac{A_5^2}{2G_5},
\qquad
 q_{5,\mathrm{vac}}=\frac{\kappa_{0,\mathrm{eff}}}{12\kappa_1}.
\]

Thus a positive-curvature vacuum cap requires
`kappa_0>A5^2/(2G5)`. The two signs of `v` are gravitationally degenerate.

## Coupled Gaussian-normal equations

After setting `N=1`, write `H_rho=a'/a`. Direct tensor variation gives

\[
 Z_5(\sigma''+4H_\rho\sigma')=A_5\sigma+G_5\sigma^3,
\]

\[
 6\kappa_1\left(H_\rho^2-\frac{X}{a^2}\right)
 +\frac{\kappa_0}{2}
 =\frac{Z_5}{2}\sigma'^2-U_5,
\]

\[
 3\kappa_1\left(\frac{a''}{a}+H_\rho^2-\frac{X}{a^2}\right)
 +\frac{\kappa_0}{2}
 =-\frac{Z_5}{2}\sigma'^2-U_5.
\]

Useful combinations are

\[
 H_\rho'+\frac{X}{a^2}
 =-\frac{Z_5}{3\kappa_1}\sigma'^2
\]

and the nonsingular cap evolution equation

\[
 a''=-\frac{a}{6\kappa_1}
 \left(\frac{\kappa_0}{2}+U_5+\frac{3Z_5}{2}\sigma'^2\right).
\]

The lapse-retaining reduced Lagrangian, after the GHY cancellation, is

\[
 L_{1D}=6\kappa_1\left(\frac{a^2a'^2}{N}+NXa^2\right)
 -Na^4\left(\frac{\kappa_0}{2}+U_5\right)
 -\frac{a^4Z_5\sigma'^2}{2N}.
\]

Its lapse, scalar, and scale-factor variations reproduce the direct tensor
equations. The Bianchi identity propagates the normal constraint.

## Parity and regularity

An even double-cap scalar satisfies `sigma'(0)=0` at the junction. An odd
configuration satisfies `sigma(0)=0`; its two cap values may have opposite
sign. At each regular cap pole, `a=0`, `sigma` is finite, and `sigma'=0` in
the regular radial coordinate.

A finite-width smooth scalar produces no distributional surface stress at
the central M4. Its stress changes the cap equations. Only a controlled
zero-width limit can add an Israel surface term.

The bulk odd scalar has zero pullback at the junction. That fact neither
identifies it with `sigma_partial` nor generates the B1 scalar action.

## Exact integral identity

For the odd Dirichlet junction and a regular cap,

\[
 \int d\rho\,a^4\left[
 Z_5\sigma'^2+A_5\sigma^2+G_5\sigma^4\right]=0.
\]

Consequently, for `Z5>0`, `A5>=0`, and `G5>=0`, the only solution is
`sigma=0`. A stable wall requires the already-open sign choice
`A5<0`, `G5>0`. This is an exact exclusion of the nonnegative-quadratic sign
domain, not a global exclusion of all scalar branches.

## Critical-cap spectral audit

The v6.1.4 critical cap can be normalized by

\[
 q_5=1,\quad X=2,\quad C_{\partial}/\kappa_1=1/2,\quad
 a(\rho)=\sqrt{2}\sin\rho,\quad 0\leq\rho\leq\pi/4.
\]

The regular odd scalar operator is

\[
 {\cal O}_{\rm odd}
 =-a^{-4}\frac{d}{d\rho}\left(a^4\frac{d}{d\rho}\right),
\]

with regular Neumann behavior at the cap pole and Dirichlet data at the
junction. Deterministic shooting and interval bracketing give

\[
 \frac{\mu_1}{q_5}=29.43091835294\ldots .
\]

The linear scalar eigenvalue is

\[
 \lambda_{\rm wall,1}=\mu_1q_5+\frac{A_5}{Z_5}.
\]

At `A5/Z5=-35 q5`, `G5/Z5=q5`, a fixed-background nonlinear shooting
problem has a regular nonzero cap amplitude
`4.0478315253...`. This is a dimensionless probe branch. The calculation
does not include metric backreaction and therefore is not the requested
coupled wall solution.

## Thin-wall diagnostic

In the flat, no-gravity control limit only,

\[
 v=\sqrt{-A_5/G_5},\qquad
 \delta=\sqrt{2Z_5/(-A_5)},\qquad
 T_{\rm excess}
 =\frac{2\sqrt{2Z_5}(-A_5)^{3/2}}{3G_5}.
\]

The tension is defined using stress in excess of the selected vacuum; the
vacuum energy is not included. If a curved family reaches this controlled
limit, its maximally symmetric junction equation would be

\[
 X=q_{5,\rm vac}
 +\left[\frac{T}{6\kappa_1}
 -\frac{C_\partial}{\kappa_1}X\right]^2.
\]

Setting `T=0` recovers the v6.1.4 junction polynomial. No curved BHSM tension
is claimed by this sprint.

## B1 coefficient-source result

Minimal scalar stress can supply a tension-like surface term in a controlled
thin limit. It does not supply an intrinsic `R4` kinetic coefficient, so it
does not derive `C_partial`. The frozen action has no sigma-dependent `F^2`
term, so it does not derive `tau_A`.

A normalizable translation collective coordinate would have a kinetic
normalization related to the wall excess tension. That coordinate is an
embedding/bending mode. It is not `sigma_partial` without an explicit
action, domain, parity, and field map.

Because the parent scalar is a `(J,m)=(0,0)` singlet, its tangential stress is
isotropic and

\[
 p_1-p_2=0.
\]

It cannot source a Berger split, although its quadratic metric dependence
can mix with existing shape perturbations.

## Open gate

The remaining construction problem is a finite-amplitude continuation of
the coupled Einstein--scalar boundary-value system through the B1 junction,
followed by a constraint-reduced spectrum containing the wall fluctuation,
bending/junction displacement, metric scalar, and both Berger shape modes.

Completion gate:
`V6_1_5_COUPLED_FINITE_AMPLITUDE_WALL_AND_MIXED_STABILITY_OPEN`.

`FULL_BHSM_NOT_COMPLETE`.
