# BHSM v14.87 eta relative-periodic Legendre/current gate

## Primary result

The retained Path-B eta density is

\[
 \mathcal L_\eta=-wF(X),\qquad
 F(X)=\frac{\kappa_1}{2}X+\frac18X^4,
\]

with Lorentzian invariant, in an orthonormal local frame,

\[
 X=|D_i\eta|^2-|D_0\eta|^2.
\]

The physical velocity Legendre map and its Hessian are

\[
 p_\eta=2wF'(X)D_0\eta
 =w(\kappa_1+X^3)D_0\eta,
\]

\[
 \mathsf K_\eta
 =2w\left[F'(X)I-2F''(X)D_0\eta\otimes D_0\eta\right].
\]

On the retained \(X\geq0\), \(\kappa_1>0\), \(w>0\) branch its transverse
and velocity-parallel eigenvalues are

\[
 \lambda_\perp=w(\kappa_1+X^3)>0,
\]

\[
 \boxed{\lambda_\parallel
 =w\left(\kappa_1+X^3-6X^2|D_0\eta|^2\right)}.
\]

Therefore eta kinetic positivity is not automatic on an unknown
relative-periodic solution. The exact pointwise kill screen is

\[
 \boxed{\kappa_1+X^3-6X^2|D_0\eta|^2>0}.
\]

Equality is a singular Legendre map. A negative value is a physical negative
velocity direction before cap reduction and cannot be removed by calling it a
gauge mode or redefining a layer mass.

The canonical full-preimage object remains

`ACTION_OWNED_FULL_PREIMAGE_TWO_STRATUM_KINETIC_REDUCTION_WITH_DERIVED_LAYER_INERTIAS_SHEAR_COVARIANCE_AND_DEGREE_ONE_SELF_ADJOINT_BACKGROUND`.

The sharper executable object is

`ACTION_SELECTED_NONZERO_REFLECTION_ODD_COEXACT_L2_ETA_OR_COLLECTIVE_DIRAC_CHARGE_SECTOR_WITH_POINTWISE_LEGENDRE_POSITIVITY_GLOBAL_CONSTRAINTS_SELF_ADJOINT_FULL_PREIMAGE_DOMAIN_AND_EXPLICIT_MIXED_VARIATION_FROM_THE_SOURCED_MOMENTUM_RESPONSE_INTO_THE_ELL2_SHAPE_TRANSPORT`.

## Zero-momentum theorem

Because \(w(\kappa_1+X^3)>0\) on the retained branch,

\[
 p_\eta=0\quad\Longleftrightarrow\quad D_0\eta=0.
\]

The eta spatial momentum current is

\[
 J_i^\eta
 =w(\kappa_1+X^3)\langle D_0\eta,D_i\eta\rangle.
\]

Thus the retained pointwise zero-momentum stationary branch has

\[
 J_i^\eta=0,
 \qquad
 P_{\mathrm{coex},L=2}J^\eta=0.
\]

This strengthens v14.85. The result is no longer merely the observation that
the chosen static solution has \(D_0\eta=0\): within the positive retained
Legendre branch, zero canonical eta momentum forces it.

The theorem does not prohibit nonzero-charge periodic solutions. It proves
that the source-free zero-momentum branch cannot be used to obtain one and
that a periodic candidate must declare how its charge, exchange current,
amplitude and period are selected.

## Sourced coexact response

If a genuine gauge-reduced reflected current is derived, its round-reference
coexact momentum constraint is

\[
 \mathcal L_{\rm shift}\beta_\perp
 =\kappa_{\rm grav}P_{\rm coex}J.
\]

For \(L=2\), v14.41 gives

\[
 \lambda_2^{\rm shift}=\frac5{R^2},
 \qquad
 \boxed{\beta_{L=2}
 =\frac{\kappa_{\rm grav}R^2}{5}J_{L=2}}.
\]

This is an exact sourced ADM response on the round reference domain. It is
not yet the physical shape transport \(\Delta\mathsf A\). Closure still
requires the canonical mixed variation showing how this sourced momentum
acts on the common full-preimage shape coordinate after all constraints and
seam conditions are reduced.

## Selection audit

The retained action provides equations of motion and conserved currents, but
the current repository contains no theorem selecting:

- a nonzero reflected eta charge sector;
- a relative-periodic orbit amplitude;
- its period;
- a nonaxisymmetric coexact \(L=2\) component; or
- an exchange current that populates that component without a fitted
  coefficient.

The rigid degree-one eta rotor remains an \(L=1\) Killing source. The pure
Path-B phase Hessian is nonnegative by v14.36, so the zero-charge branch does
not spontaneously bifurcate into the requested phase rotation. A nonzero
charge/exchange branch is possible in principle but is not action-selected in
the retained archive.

## Numerical verification

Deterministic tests verify:

- analytic versus finite-difference Legendre Jacobians for random seeded
  velocities;
- positive, near-degenerate and negative branches;
- orthogonal target-basis covariance;
- the zero-momentum/current limit;
- reflected odd-current projection; and
- the \(\kappa_{\rm grav}R^2/5\) round \(L=2\) resolvent.

These tests verify the algebra and kill screen. They do not substitute for the
missing global periodic BVP.

## Hindsight 20/20

### VALIDATED

- Exact eta velocity Legendre spectrum and positivity cone.
- Zero canonical eta momentum forces zero eta current on the retained branch.
- Conditional sourced round \(L=2\) coexact resolvent.

### INVALIDATED

- Unconditional positive eta inertia on an unspecified periodic branch.
- Source-free zero-momentum eta dynamics as a nonzero \(L=2\) driver.
- Identification of a sourced ADM response with physical shape transport
  without its mixed variation.

### RECLASSIFIED

- The periodic eta BVP is a charge/exchange-sector selection problem plus a
  pointwise hyperbolicity/Legendre kill screen, not merely a solver task.

### OPEN

- Action selection of a nonzero reflection-odd coexact \(L=2\) eta or
  collective-Dirac charge sector.
- Global constrained degree-one periodic solution and common self-adjoint
  domain.
- Mixed current-to-shape transport variation and complete Hessian.

## Preserved flavor and completion boundaries

The following gates remain open:

`PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL`

`ACTION_OWNED_FAMILY_NONCENTRAL_LEFT_HANDED_CURRENT_SOURCE`

No CKM, PMNS, mass, coupling or measured flavor datum enters this theorem.

- `FULL_BHSM_COMPLETE = FALSE`
- `MARK_III = NOT_REACHED`
- `PHYSICAL_EXECUTION_BLOCKED = TRUE`
- `USB_SYNCHRONIZATION_ELIGIBLE = FALSE`
