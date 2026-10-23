# Point-lens delay/flux invariant: independent derivation and scope

## Verified statement

For a transparent point source lensed by one positive point mass in the geometric-optics, weak-field, single thin-lens approximation, define Delta t>0 as the observed arrival time of the negative-parity faint image minus that of the positive-parity bright image. Let R=|mu_bright|/|mu_faint|>1 be their geometric flux ratio for the same source emission. Then

\[
u(R)=2\sinh\!\left(\tfrac14\ln R\right),
\]

\[
h(u)=\frac{u}{2}\sqrt{u^2+4}
+\ln\frac{\sqrt{u^2+4}+u}{\sqrt{u^2+4}-u},
\]

\[
\boxed{\quad
M_{\rm app}=\frac{c^3\Delta t}
{4G(1+z_l)h[u(R)]}=M.
\quad}
\]

The equality is an established point-lens identity, not a new BHSM prediction. At leading quasistatic order it is unchanged by any source/lens relative trajectory or parallax that only changes the instantaneous source alignment and distances while preserving this model and the image branches. It is therefore a useful control for motion-induced changes in delay. A constant apparent mass does not establish BHSM, and a varying apparent mass is not by itself evidence against ordinary gravity.

## 1. Derivation directly from Fermat stationarity

Write the observer/source/lens angular-diameter distances as D_s,D_l,D_ls. For a mass M,

\[
\theta_E^2=\frac{4GM}{c^2}\frac{D_{ls}}{D_lD_s},
\quad \mathbf x=\boldsymbol\theta/\theta_E,
\quad \mathbf y=\boldsymbol\beta/\theta_E,
\quad u=|\mathbf y|>0.
\]

Ignoring an image-independent arrival-time constant, the dimensionless Fermat potential is

\[
\tau(\mathbf x;\mathbf y)
=\tfrac12|\mathbf x-\mathbf y|^2-\ln|\mathbf x|.
\]

Its stationary equation is

\[
\mathbf0=\nabla_x\tau
=\mathbf x-\mathbf y-\frac{\mathbf x}{|\mathbf x|^2}.
\]

Both images are collinear with the source. Using signed coordinates on that line, let s=sqrt(u²+4). The two solutions are

\[
x_+=\frac{u+s}{2}>1,\qquad
x_-=\frac{u-s}{2}=-\frac1{x_+}<0.
\]

The full two-dimensional lens Jacobian has determinant `1−|x|^(-4)`. Its signed magnifications are

\[
\mu_+=\frac{x_+^4}{x_+^4-1}>0,
\qquad
\mu_-=-\frac1{x_+^4-1}<0.
\]

Thus the positive-parity outer image is the brighter one and

\[
R=-\frac{\mu_+}{\mu_-}=x_+^4,
\qquad \ln R=4\ln x_+=4\operatorname{asinh}(u/2).
\]

Stationarity also gives `x_+−u=1/x_+` and `x_-−u=−x_+`. Therefore

\[
\begin{aligned}
\tau_- -\tau_+
&=\tfrac12(x_+^2-x_+^{-2})+2\ln x_+\\
&=\tfrac12u\sqrt{u^2+4}+2\operatorname{asinh}(u/2)\\
&=h(u)>0.
\end{aligned}
\]

The physical arrival-time factor is

\[
\frac{1+z_l}{c}\frac{D_lD_s}{D_{ls}}\theta_E^2
=\frac{4GM}{c^3}(1+z_l).
\]

This cancels the distance factors and proves the invariant. A change of source direction rotates both images but changes none of the scalar relations. A changed instantaneous source distance also cancels from this factor as long as the same thin-lens point-mass model remains applicable and the relevant redshift factor is used.

The exactly aligned u=0 case is excluded: the two-image point-source description becomes an Einstein ring, R tends to one, and both h and Delta t tend to zero. The displayed estimator is then a limiting 0/0 expression rather than a defined two-image measurement. The bright/faint and parity labels are continued continuously away from this degeneracy.

## 2. Linear residual that removes ordinary alignment motion

The exact derivatives are

\[
h'(u)=\sqrt{u^2+4},\qquad
\frac{d\ln R}{du}=\frac4{\sqrt{u^2+4}}.
\]

Consequently, with redshift fixed,

\[
\boxed{\quad
\delta\ln M_{\rm app}
=\frac{\delta\Delta t}{\Delta t}
-\frac{u^2+4}{4h(u)}\,\delta\ln R.
\quad}
\]

At a fixed physical point mass, a displacement du changes the two terms by exactly the same first-order amount. The combination vanishes. For a known varying redshift one additionally subtracts `delta ln(1+z_l)`. No amplitude, angular trajectory or point-lens scale is fitted to force the cancellation.

This is a first variation around a nondegenerate two-image preparation. If used at finite differences, the neglected term is quadratic in the displacements. As u tends to zero, `(u²+4)/(4h)` behaves as `1/(2u)`; flux-ratio errors are strongly amplified. A practical inference would need the joint timing/flux covariance and its model systematics, not just a small numerical residual in this identity check.

## 3. What additional ordinary lens terms do

### Constant isotropic convergence: a cancellation that survives

It would be inaccurate to assert that every macromodel term necessarily biases this invariant. Consider the declared potential

\[
\psi(\mathbf x)=\ln|\mathbf x|+\tfrac12\kappa|\mathbf x|^2,
\qquad a_0=1-\kappa>0,
\]

where the point-mass normalization is fixed. Put `x_tilde=sqrt(a0) x`, `y_tilde=y/sqrt(a0)`. The lens equation becomes the ordinary point-lens equation in tilde coordinates. Its two magnifications have the same common multiplier a0^(-2), which cancels from their ratio. Image-independent terms also cancel from the Fermat difference, leaving exactly h(|y_tilde|), with the same physical point-mass time factor. Thus M_app=M for this ideal isotropic quadratic perturbation too. This does not resolve general mass-sheet/source-distance inference degeneracies; it is the algebra of a specified point mass plus an isotropic quadratic term.

### External shear: a direct conventional-gravity counterexample

An anisotropic tidal term can break the point-lens estimator even when the point mass is constant and ordinary gravity is sufficient. Take

\[
\psi=\ln|\mathbf x|+\tfrac\gamma2(x_1^2-x_2^2),
\qquad \mathbf y=(u,0).
\]

For the on-axis images,

\[
(1-\gamma)x-1/x=u,
\quad
x_\pm=\frac{u\pm\sqrt{u^2+4(1-\gamma)}}{2(1-\gamma)}.
\]

The two-dimensional Jacobian determinant is

\[
\det A=(1-\gamma+x^{-2})(1+\gamma-x^{-2}),
\]

and the Fermat potential includes `−gamma x²/2`. For the choices below, `u>2 gamma/sqrt(1+gamma)`, so off-axis images are absent, both image branches remain noncritical, and the positive-parity image remains the brighter/earlier one.

With gamma=0.05, evaluating the unchanged point-lens estimator gives:

| u | M_app/M |
|---:|---:|
| 0.5 | 1.6955601416 |
| 1.0 | 1.1452309054 |
| 2.0 | 1.0628137062 |

A moving source through this fixed ordinary shear field would produce an apparent-mass change without a changing point mass or BHSM surface response. These are transparent dimensionless counterexamples, not observational results or physically fitted shear values.

## 4. Physical limits and interpretation

The cancellation is exact for the declared instantaneous thin-lens equations. “Slowly moving” here means the leading quasistatic approximation: lens/source changes over the relevant propagation-delay interval, retardation, gravitomagnetic corrections and lens-induced frequency shifts are neglected. A literal moving spacetime is not made static by this algebra.

The flux ratio must refer to the same intrinsic source emission and to geometric magnifications. Differential extinction, independent microlensing, resolved source structure, wave-optics interference and source variability that has not been delay-aligned can all change a measured ratio without changing this ideal lens mass. Near-horizon strong-deflection images and photon rings also lie outside the weak-field two-image thin-lens derivation; ordinary general relativity itself then predicts a different relation.

The invariant is useful as a **kinematic cancellation and null control** inside a justified nuisance family. An independently action-derived screened monopole or multipole response can predict departures, but the ordinary point-lens identity cannot establish that response's physical provenance. General macro/shear and line-of-sight freedoms must be modeled before interpreting a nonzero residual. There is no detection claim here.

## 5. Independent checks

`check_blackhole_point_lens_invariant.py` verifies the point-lens stationarity, parity and full 2D Jacobian relations; symbolically verifies the time-delay and derivative identities; follows synthetic straight, curved and parallax-like alignment trajectories; checks isotropic-convergence cancellation; and reproduces the external-shear counterexample. It writes a receipt and a compact CSV table. The synthetic paths contain no telescope data, and successful checks validate only the stated equations. The checks are internal AI-assisted verification, not external peer review.
