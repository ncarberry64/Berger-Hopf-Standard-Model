# BHSM coupled eta--sigma--metric skin selector theorem

## Coupled normal equations

For a target-geodesic eta profile in Gaussian normal coordinate (n), write

\[
 X=|D_n\eta|^2,\qquad F(X)=\frac{\kappa_1X}{2}+\frac{X^4}{8},
\]

and use the retained static normal density

\[
 \mathcal L_n=(1+g\sigma^2)F(X)
 +\frac{Z_\sigma}{2}\sigma_n^2
 +\frac{A_0}{2}\sigma^2+\frac{G_0}{4}\sigma^4.
\]

If \(\theta=\partial_n\log\sqrt h\), simultaneous variation gives

\[
 D_n\!\left[(1+g\sigma^2)(\kappa_1+X^3)D_n\eta\right]
 +\theta(1+g\sigma^2)(\kappa_1+X^3)D_n\eta=0,
\]

\[
 -Z_\sigma(\sigma_{nn}+\theta\sigma_n)
 +[A_0+2gF(X)]\sigma+G_0\sigma^3=0.
\]

The metric equations supply the Gauss--Codazzi normal Hamiltonian and
momentum constraints sourced by the complete eta--sigma stress. The v15.15
material transmission domain supplies continuous traces and opposite-normal
canonical-flux balance. These equations are coupled; no superposed-wall
approximation was used.

In the flat-normal limit the exact matter first integral is

\[
 \mathcal H_n=(1+g\sigma^2)
 \left(\frac{\kappa_1X}{2}+\frac{7X^4}{8}\right)
 +\frac{Z_\sigma}{2}\sigma_n^2
 -\frac{A_0}{2}\sigma^2-\frac{G_0}{4}\sigma^4.
\]

## Why the coupled BVP does not select its own coefficients

The eta, sigma, and metric variations are field equations at fixed action
law. The retained action contains no variations with respect to
\((\alpha,r,\gamma)\). Regularity and constraints can restrict a field
solution conditional on those coefficients; they do not turn constants that
define the operator into new solution coordinates.

The only established common physical state is the v15.9 eta--metric
formation precursor with \(\sigma=0\). On that state:

- the sigma Euler residual vanishes by the exact \(\mathbb Z_2\) factor;
- the eta equation and metric stress contain no sigma coefficients;
- eta degree, regularity, and normalization are likewise coefficient-blind.

For the six available residual classes, the physical selector Jacobian is
therefore exactly

\[
 J_{\rm sel}=0_{6\times3},\qquad
 \operatorname{rank}J_{\rm sel}=0,\qquad
 \operatorname{nullity}J_{\rm sel}=3.
\]

This is structural rank deficiency, not numerical conditioning.

The requested common parent/child inverse BVP also requires a physical child
asymptotic state specified independently of the trial coefficients. No such
state is currently derived. Using each A/B/C theory's own coefficient-
dependent vacuum creates three different forward problems, not three
solutions of one selector. Selecting the lowest wall tension would additionally
assume an ensemble over action laws that BHSM does not contain.

## The coefficient-promotion no-go

Literal global variation of the static energy with respect to its couplings
would give

\[
 \frac{\partial E}{\partial g}=\int F(X)\sigma^2,
 \quad
 \frac{\partial E}{\partial A_0}=\frac12\int\sigma^2,
 \quad
 \frac{\partial E}{\partial G_0}=\frac14\int\sigma^4.
\]

With positive measure and retained \(F(X)\ge0\), stationarity forces
\(\sigma=0\) almost everywhere. Thus naively promoting the response
coefficients destroys the material wall; it does not derive one. A legitimate
promotion would need a new upstream action-owned degree of freedom and its
own dynamics, which is not present and is not introduced here.

## Scientific completion boundary

The full coupled physical skin BVP is not merely unsolved numerically: it is
not yet uniquely defined by retained BHSM data. The foundational obstruction
is now proved. Aether must supply the three canonical sigma response
observables—the tangent curvature, its eta-(X) derivative, and the
backreaction-unreduced canonical quartic. The v15.10 inverse then uniquely
recovers \((\alpha,r,\gamma)\).

The exact next object is:

`ACTION_OWNED_AETHER_CYCLE_TO_REGULAR_SIGMA_RESPONSE_JET_MAP_PRODUCING_THE_PHYSICAL_SIGMA_TANGENT_PROPAGATOR_X_DERIVATIVE_AND_BACKREACTION_UNREDUCED_CANONICAL_QUARTIC_ON_THE_V15_9_BRANCH`

Until it exists, physical skin tension, contact impulse, ejection, and the
Hopf child are not action-selected. `FULL_BHSM_COMPLETE = FALSE`.
