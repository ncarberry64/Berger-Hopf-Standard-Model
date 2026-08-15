# BHSM dimensional-crossover sigma-response audit

## The repository's actual dimensional convention

The proposed distinction is physically relevant, with an important
qualification. BHSM uses

\[
 M_5=I_t\times S^4,\qquad M_4=I_t\times S^3.
\]

Thus M5 has four spatial dimensions and M4 has three. The ordinary round
bubble controls are therefore

\[
 (A,K)_{M4}=(4\pi R^2,2/R),\qquad
 (A,K)_{M5}=(2\pi^2R^3,3/R).
\]

Their radial Laplacians contain (2/R) and (3/R), respectively.

However, the retained master action does not describe M4 changing into M5
in time. They are simultaneous strata. M8→M5 is an oriented closed-fiber
pushforward, while M5→M4 is an equatorial trace followed by a constrained
critical-value construction.

## Exact crossover geometry

On the round branch,

\[
 ds_5^2=-dt^2+a^2[d\chi^2+\sin^2\chi,ds_{S^3}^2],
 \qquad \chi=\frac\pi2-\rho,
\]

and

\[
 d\mu_5=a\cos^3\rho,d\rho,d\mu_4.
\]

The density is smooth and even under cap reflection. At the seam,

\[
 \partial_\rho\log\cos^3\rho=0,
 \qquad K_{M4}=0.
\]

Consequently the existing round measure and extrinsic curvature provide no
delta-function or orientation-odd sigma source there.

The normal scalar operator is

\[
 L_\chi=-a^{-2}\sin^{-3}\chi\,
 \partial_\chi(\sin^3\chi\,\partial_\chi).
\]

Its selected even Neumann profile is the constant zero mode. Existing BHSM
work explicitly classifies sigma as that bulk singlet restricted to the
equator—not as a derived interface order parameter—and finds no retained
extrinsic sigma coupling.

The stratified action does contain the compatibility term

\[
 \int_{M5}\langle\lambda_\sigma,\sigma_5-P_0\sigma_8\rangle.
\]

Its variation enforces trace matching and the adjoint reaction. The
multiplier has no kinetic term and its normalization is redundant. It cannot
generate sigma mass, eta-(X) response, or quartic data. Likewise, the
M5→M4 constrained critical-value construction is a valid response
architecture, but no globally selected kernel has been evaluated and it
does not eliminate the independent sigma Wilson data.

The physical bubble radius (R) in either endpoint stratum is not the
transverse coordinate (chi). Splicing the two endpoint radial Laplacians
would therefore mix distinct operators.

## Transport rank is not selector rank

Fiber/profile reduction can transport a supplied response jet. For a common
profile measure (I), the critical normalized jet has the form

\[
 S_\sigma=rX_c(\alpha+9/4),\qquad
 \partial_XS_\sigma=6r,\qquad
 \lambda_\sigma=\frac{\gamma r^2X_c^4}{\kappa_1^2 I}.
\]

Its sensitivity to ((\alpha,r,\gamma)) has determinant

\[
 \frac{6r^3X_c^5}{\kappa_1^2I},
\]

which is nonzero for (r\ne0). This means three supplied coefficients are
visible in three reduced observables. It does not determine them. A selector
would require independently action-derived target values for those
observables. The retained crossover supplies none, so the physical selector
rank remains the v15.16 value zero.

## Result

The dimensional-crossover hypothesis identifies a credible upstream home
for the missing law, but that law is not already latent in the retained
trace geometry. There is presently no (E_{\rm dim}), dynamical dimension
field, or M5→M4 localization kernel whose mixed variation produces the
sigma tangent curvature, its eta-(X) derivative, and its canonical
quartic. Consequently no finite skin width or post-crossover traction is
derived from dimension change alone.

The exact next object is:

`ACTION_OWNED_M5_TO_M4_CROSS_STRATUM_LOCALIZATION_CRITICAL_VALUE_KERNEL_PRODUCING_THE_THREE_CANONICAL_SIGMA_RESPONSE_OBSERVABLES_WITHOUT_INDEPENDENT_SIGMA_WILSON_DATA`

This object would implement the author's broader proposed target without a
continuous dimension parameter or an imported wall coefficient.

`FULL_BHSM_COMPLETE = FALSE`.
