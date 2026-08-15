# BHSM v15.37 — zero-current odd-FR ground state

## Compact constraint resolution

The odd-FR antiperiodic rotor has lowest charged basis states

\[
 \psi_\pm(\theta)=\frac{e^{\pm i\theta/2}}{\sqrt{2\pi}}.
\]

The compact momentum constraint excludes a lone state with nonzero mean
Hopf current. It does not require the FR Casimir to vanish. The real standing
wave

\[
 \boxed{\psi_0(\theta)=\frac{\cos(\theta/2)}{\sqrt\pi}}
\]

belongs to the same self-adjoint antiperiodic ground space and obeys

\[
 \boxed{\langle J\rangle=0,\qquad
 \langle J^2\rangle=\frac14.}
\]

Consequently its semiclassical momentum-constraint source vanishes while its
localized energy remains

\[
 \boxed{E_{\rm FR}(\ell)=\frac{1}{8I_{\rm skin}(\ell)}.}
\]

This is exactly the stabilizing energy evaluated in v15.34. No classical
nonzero charge or compensating kick is inserted.

## Ground-state selection

The lowest antiperiodic eigenspace is spanned by \(\psi_\pm\). The zero-current
condition imposes equal magnitudes of the two coefficients. After quotienting
overall quantum phase, the remaining relative phase is a translation of the
Hopf coordinate origin. Thus

\[
 \left|\mathrm{Sol}_{\rm FR,ground,J=0}/
 (U(1)_{\rm phase}\times U(1)_{\rm Hopf})\right|=1.
\]

The rotor-sector state is unique modulo its exact symmetries.

## Stationary reduced child

Because \(\langle J^2\rangle=1/4\), the v15.34 Routhian and its finite
\(x<0\) minimum are unchanged. The physical state is now interpreted as a
stationary quantum ray times a static enclosure profile. Its only time factor
is the global phase \(e^{-iEt}\), which is quotiented. The enclosure Hessian
and frequency squared remain positive.

Thus a classical internally rotating child is not required for the minimal
compact FR stabilization mechanism.

## Reclassification

- v15.34 localized inertia and its energy: preserved.
- v15.35 lone classical charged rotor: reclassified as an unconstrained
  charged branch.
- v15.36 parent–child counterrotation: retained as a conditional alternative
  if a physical countercurrent mode is independently derived.
- preferred minimal compact sector: the zero-current odd-FR ground state.

At mean-field level no Hopf frame-dragging shift is sourced. Stress
fluctuation backreaction has not yet been computed.

## Claim boundary

Closed:

- the compact mean Hopf-momentum constraint in the minimal FR sector;
- nonzero localized FR energy with zero mean current;
- uniqueness of the rotor ground state modulo exact symmetries;
- a stationary stable reduced child branch.

Open:

- the nonround semiclassical Einstein–eta–sigma constraint BVP sourced by the
  FR expectation stress;
- stress fluctuations and the complete physical Hessian;
- full child persistence, separation, and M4 attachment.

`FULL_BHSM_COMPLETE = FALSE`.

Active dependency:

`SEMICLASSICAL_NONROUND_EINSTEIN_ETA_SIGMA_CONSTRAINT_BVP_WITH_THE_LOCALIZED_FR_GROUND_STATE_EXPECTATION_STRESS_AND_COMPLETE_PHYSICAL_HESSIAN`
