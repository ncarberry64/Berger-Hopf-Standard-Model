# BHSM v14.84 full-preimage cap-inertia operator theorem

## Result

The two strata needed by the v14.83 shear calculation are already present as
the reflected domains of the v14.30 full-preimage collar:

\[
\widetilde C_+=\{\rho\geq0\},\qquad
\widetilde C_-=\{\rho\leq0\},\qquad
\widetilde C_+\cap\widetilde C_-=\widetilde\Sigma .
\]

Their round-branch measure is

\[
d\mu_8=d\mu_F\cos^3\rho\,ds\,d\mu_4.
\]

No additional fluid, field, or co-varied copy of the M8 eta sector is needed.
This geometric identification does not yet construct the two cap critical
actions.

## Exact operator identity

Let \(Q\in\mathcal H_2\simeq\mathbb R^9\). After solving the cap bulk
equations, constraints, gauge quotient, and self-adjoint domain, define

\[
\mathsf M_\pm=
\left.\frac{\delta^2\Gamma_\pm^{\rm crit}}
{\delta\dot Q\,\delta\dot Q}\right|_{\Phi_*}.
\]

Assume these operators are positive definite on the same reduced trace space,
and that no cross-cap or seam kinetic block has been discarded. Put

\[
\mathsf M=\mathsf M_++\mathsf M_-,\qquad
\mathsf P=(\mathsf M_+^{-1}+\mathsf M_-^{-1})^{-1},
\]

\[
\overline{\mathsf A}Q=\mathsf M^{-1}
(\mathsf M_+\mathsf A_++\mathsf M_-\mathsf A_-)Q,
\qquad \Delta\mathsf A=\mathsf A_+-\mathsf A_-.
\]

Direct completion of squares gives, without assuming that the inertia
operators commute,

\[
T=\frac12\langle\dot Q+\overline{\mathsf A}Q,
\mathsf M(\dot Q+\overline{\mathsf A}Q)\rangle
+\frac12\langle\Delta\mathsf A Q,
\mathsf P\Delta\mathsf A Q\rangle .
\]

Because the parallel sum of two positive operators is positive,

\[
\Delta\mathsf A^\dagger\mathsf P\Delta\mathsf A\succeq0.
\]

On a stationary common co-moving background, with gyroscopic and
time-dependent-connection terms absent, the linearized stiffness is therefore

\[
\mathsf H_{\rm eff}=\mathsf H_0-
\Delta\mathsf A^\dagger\mathsf P\Delta\mathsf A.
\]

Thus the v14.83 softening sign survives promotion from scalar masses to
noncommuting cap inertia operators.

## Reflection theorem

Let \(\mathsf R\) be the orthogonal pullback identifying the reflected cap
trace spaces. Reflection covariance of the critical actions, background, and
domain implies

\[
\mathsf M_-=\mathsf R\mathsf M_+\mathsf R^\dagger.
\]

The invariant statement is this intertwining relation. Only after pulling the
minus cap back with \(\mathsf R\) may one write
\(\mathsf M_+=\mathsf M_-=\mathsf M_0\). Then

\[
\mathsf M=2\mathsf M_0,\qquad \mathsf P=\tfrac12\mathsf M_0.
\]

On the round SO(4)-symmetric branch, the real nine-dimensional ell=2 scalar
harmonic space is irreducible. An equivariant self-adjoint inertia is therefore
\(\mathsf M_0=m_0I_9\). Canonical normalization cancels \(m_0\) and gives the
relative inertia factor

\[
\nu=\frac14.
\]

This conditionally upgrades the inertia part of the v14.83 equal-mass result.
The value \(\chi_2=2/(3R^2)\) still requires the normalized isotropic
relative-transport covariance used in v14.83; reflection alone does not derive
the magnitude or covariance of \(\Delta\mathsf A\).

## Physical transport boundary

The transport generator cannot be identified with an ADM coordinate shift.
V14.41 proves that the source-free stationary non-Killing coexact shift is
strictly positive in the action and that the relative shift vanishes after
the common rotation quotient. The eligible source must instead be derived
from gauge-reduced conserved momentum: matter/eta/Dirac stress transport, a
quasilocal or canonical cap-boundary momentum, or the conserved exchange
current of v14.81.

## Sequential gates

1. **Cap inertia:** compute \(\mathsf M_\pm\) from the common full-preimage
   critical action, including global constraints and all seam/cross-cap terms.
2. **Reflection:** verify the degree-one background and self-adjoint domain
   admit the reflection intertwiner, then apply the conditional \(\nu=1/4\)
   theorem.
3. **Physical transport:** derive a nonzero conserved, gauge-reduced
   \(\Delta\mathsf A\); the ADM-coordinate-shift route is excluded.
4. **Complete response:** insert the canonically normalized shear operator
   into the complete bulk/GHY/KKT/matter/nonlocal ell=2 Hessian.

## Claim boundary

The operator identity and its positivity theorem are closed. The actual cap
inertias, their positivity after complete gravity/gauge/ghost reduction, the
physical transport, degree-one solution/domain, and complete response remain
open. No Landau coefficients, CKM, PMNS, particle observable, or BHSM
completion follows.

The flavor gates remain:

`PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL`

`ACTION_OWNED_FAMILY_NONCENTRAL_LEFT_HANDED_CURRENT_SOURCE`

The unchanged exact next object is:

`ACTION_OWNED_FULL_PREIMAGE_TWO_STRATUM_KINETIC_REDUCTION_WITH_DERIVED_LAYER_INERTIAS_SHEAR_COVARIANCE_AND_DEGREE_ONE_SELF_ADJOINT_BACKGROUND`
