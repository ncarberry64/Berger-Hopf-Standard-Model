# BHSM v15.35 — reduced relative-periodic child persistence

## Relative equilibrium

The v15.34 fixed-FR-charge Routhian has a stable child branch at

\[
 x=\ell_*<0,
 \qquad \partial_\ell H_{\rm red}=0,
 \qquad \partial_\ell^2H_{\rm red}>0.
\]

The child is not internally frozen. At fixed \(J=1/2\),

\[
 \dot\theta=\frac{J}{I_{\rm skin}(\ell_*)},
 \qquad
 T=\frac{2\pi I_{\rm skin}(\ell_*)}{|J|}.
\]

For the deterministic v15.34 normalization this gives a relative equilibrium
with \(x\simeq-4.78752\). After one classical Hopf cycle the odd-FR state
returns with sign minus one. This is the antiperiodic self-adjoint sector, not
an inserted half-integer charge.

## Reduced Floquet result

Let \(M_\ell\) be the positive sigma collective kinetic norm and
\(k_\ell=\partial_\ell^2H_{\rm red}\). The physical enclosure frequency is

\[
 \Omega_\ell^2=\frac{k_\ell}{M_\ell}>0.
\]

After removing the exact cyclic and diffeomorphism directions, the reduced
physical Floquet pair is

\[
 \boxed{\mu_\pm=e^{\pm i\Omega_\ell T},\qquad |\mu_\pm|=1.}
\]

Thus the controlled child is persistent as a relative-periodic reduced
solution.

## Full constraint continuation gate

For full coordinates \((\ell,y^I)\), with the lapse, shift, nonround metric,
eta, sigma-complement, and other regular modes in \(y^I\), solve

\[
 \partial_IH(\ell,y_*(\ell))=0.
\]

On a positive invertible physical complement the exact on-shell curvature is

\[
 \boxed{
 k_{\rm child}
 =H_{\ell\ell}-H_{\ell I}H_{II}^{-1}H_{I\ell}.
 }
\]

The direct v15.34 curvature is approximately \(3.1005\) in the deterministic
normalization. The explicit local persistence gate is therefore

\[
 H_{\ell I}H_{II}^{-1}H_{I\ell}<3.1005.
\]

This does not claim that passive auxiliary modes stabilize the skin. The
positive term is the direct localized cyclic Routh energy; the complement is
allowed only its correct subtractive Schur sign.

Independently, \(I_{\rm skin}\to0\) at both material vacua, so the nonzero-FR
Routh energy is endpoint-coercive. Any bounded regular backreaction cannot
restore collapse to either pole, although it can move or split the finite
minima.

## Encapsulation event classification

The seam is a saddle and its physical relative negative mode points toward
one of the two finite fixed-charge wells. The oriented \(x<0\) well is the
child branch. This establishes the nonlinear destination in the controlled
Routhian and reclassifies the negative seam mode as the encapsulation-event
coordinate.

No damping, kick, or capture rule is inserted. Generic formation data may
oscillate or transfer energy into other action-owned modes; capture can only
be decided by integrating the complete coupled formation trajectory.

## Claim boundary

Derived:

- a stable reduced relative equilibrium with an internal Hopf clock;
- the physical reduced Floquet pair after exact symmetry directions are
  removed;
- endpoint coercivity and the explicit full-constraint Hessian gate;
- the negative seam direction as the controlled encapsulation transition.

Open:

- the off-seam nonlinear Einstein–eta–sigma constraint BVP;
- the full physical complement spectrum and mixed Hessian;
- generic formation capture and complete event energy transfer;
- the full child Floquet spectrum and M4 attachment.

`FULL_BHSM_COMPLETE = FALSE`.

Active dependency:

`OFF_SEAM_FULL_EINSTEIN_ETA_SIGMA_CONSTRAINT_BVP_AND_FORMATION_TRAJECTORY_CAPTURE_INTO_THE_RELATIVE_PERIODIC_CHILD`
