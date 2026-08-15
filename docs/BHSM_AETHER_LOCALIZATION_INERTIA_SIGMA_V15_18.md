# BHSM dynamical localization-inertia sigma theorem

## Formation dynamics

The proposed formation equation

\[
 \ddot q-\frac{5m}{6a_c^2}q+\frac{23}{54a_c^2}q^3=0
\]

is exactly Euler--Lagrange equivalent to the v15.9 normalized reduced
potential

\[
 V(q)=-\frac58mq^2+\frac{23}{144}q^4
\]

with collective inertia (M_q=3a_c^2/2). This establishes a consistent
reduced dynamical reading of the static Lyapunov--Schmidt result. The full
constraint-reduced Lorentzian profile norm was not independently
materialized in v15.9, so the normalization remains equation-equivalent
rather than a new physical scale prediction.

## Exact retained inertia test

The retained eta kinetic sector has

\[
 w(\sigma)=1+g\sigma^2,
 \qquad
 \mathbb I_{qq}(\sigma)=M_q(1+g\sigma^2).
\]

Therefore

\[
 \partial_\sigma\mathbb I_{qq}=2gM_q\sigma,
 \qquad
 \partial_\sigma^2\mathbb I_{qq}=2gM_q.
\]

The proposed inertial force is

\[
 J_\sigma^{\rm inertia}
 =\frac12\partial_\sigma\mathbb I_{qq}\dot q^2
 =gM_q\sigma\dot q^2.
\]

Hence

\[
 \boxed{J_\sigma^{\rm inertia}|_{\sigma=0}=0}
\]

for every moving trajectory. Motion does not linearly force sigma in the
retained theory.

This conclusion does not rely on treating eta as a quadratic oscillator. For
the complete one-mode Lorentzian (p=2+p=8) density, let
(X=S-v^2). Direct differentiation gives

\[
 \frac{\partial^2L_\eta}{\partial v^2}
 =(1+g\sigma^2)
 [\kappa_1+X^3-6v^2X^2].
\]

The bracket is the nonlinear Legendre factor whose sign must be checked on
the trajectory. Regardless of its sign, the entire velocity Hessian remains
even in sigma and its first sigma derivative at zero vanishes.

It does produce the first allowed effect. In the Lorentzian (L=T-V)
convention, the tangent equation is

\[
 Z_\sigma\ddot\sigma+
 [K_{\sigma,\rm static}-gM_q\dot q^2]\sigma+O(\sigma^3)=0.
\]

Thus sufficient formation speed can make the symmetric solution
parametrically unstable. Sigma=0 remains an exact solution, but becomes an
unstable one; a nonzero branch would arise spontaneously from perturbations
and retain its two orientation-related signs.

## Why reduction cannot create the missing linear source

The retained action, constraints, and v15.15 material transmission domain
are invariant under (sigma\mapsto-\sigma). A locally unique
reflection-equivariant critical-value or Schur reduction therefore preserves

\[
 \mathbb I_{\rm phys}(-\sigma)=\mathbb I_{\rm phys}(\sigma).
\]

Consequently its first sigma derivative at zero vanishes even after metric,
eta, and constraint response are eliminated. A nonzero linear inertial
source would require a parity-odd retained coupling or a background already
on a nonzero sigma branch. Neither is currently present.

## Coefficient and contact consequences

The velocity-dependent tangent curvature is

\[
 S_{\sigma,\rm dyn}
 =S_{\sigma,\rm static}-\frac{g}{Z_\sigma}M_q\dot q^2
 =S_{\sigma,\rm static}-\frac{rM_q}{\kappa_1}\dot q^2.
\]

This supplies a dynamical way to *measure or reconstruct* (r) if an
action-derived physical tangent propagator is already available. It does not
predict (r). Alpha remains in the static intercept. The quadratic weight
(1+g\sigma^2) has zero fourth sigma derivative, so it generates no bare
quartic; (G_0) remains independent, although eliminating a future response
block could add a conditional order-(g^2) backreaction correction.

The proposed momentum redirection also fails its present provenance gate.
The localization label (ell) and contact separation (d) are not retained
canonical coordinates and have no action-owned momenta. Pure cap repartition
has zero total-action inertia. Therefore (mathbb I_{dq}) and the claimed
(q\)-to-(d) momentum transfer are currently undefined, not nonzero.

## Result

The inertia hypothesis opens a genuine parametric-instability route and
explains why static residuals can remain blind. It does not yet remove the
constitutive obstruction or derive ejection.

The exact next object is:

`ACTION_OWNED_M5_M4_LOCALIZATION_INERTIA_KERNEL_WITH_PARITY_EVEN_SECOND_SIGMA_VARIATION_DERIVING_THE_TANGENT_PROPAGATOR_X_RESPONSE_BACKREACTION_QUARTIC_AND_PHYSICAL_CONTACT_CROSS_INERTIA_ON_THE_DYNAMICAL_V15_9_BRANCH`

`FULL_BHSM_COMPLETE = FALSE`.
