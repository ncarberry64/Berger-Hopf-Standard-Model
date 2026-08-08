# BHSM v14.58 — Exact Round-Collar Spectral Baseline and Symmetry Obstruction

## Primary verdict

`BHSM_V14_58_THE_ROUND_PRODUCT_COLLAR_REPLACES_SYNTHETIC_DTN_MATRICES_WITH_EXACT_SPECTRAL_FORMULAS_AND_PROVES_A_TRACE_CLASS_SEAM_CONTRAST_BUT_THE_CONTRAST_SIGN_DEPENDS_ON_THE_UNDERIVED_INNER_CAP_DOMAIN_AND_ROUND_SYMMETRY_FORBIDS_NONCENTRAL_FLAVOR_MIXING`

v14.58 takes the first non-synthetic step beyond the finite matrices used in
v14.57. It defines an exact reduced product-collar operator on a common round
three-sphere seam, derives its parent and child Dirichlet-to-Neumann spectra,
and proves that their seam difference is trace class.

This is an **analytic reduced spectral laboratory**, not the physical BHSM
cosmological-parent/particle-child solution. It does not emit a neutrino mass,
mass splitting, PMNS matrix, detector response, matter potential, lifetime,
cross section, or absolute scale.

## 1. Exactly specified reduced background

Use the common seam

\[
\Sigma=S^3(R)
\]

and the product operator

\[
P=-\partial_r^2+\slashed D_{S^3(R)}^2+m^2.
\]

The parent is the decaying half-cylinder

\[
[0,\infty)\times S^3(R),
\]

while the child is the finite collar

\[
[-L,0]\times S^3(R).
\]

The induced seam metric and tangential operator are exactly matched. The inner
end of the child still requires a domain choice. v14.58 carries both
Dirichlet and Neumann choices to expose, rather than hide, that fork.

## 2. Exact round-three-sphere spinor spectrum

For the round spin structure,

\[
\operatorname{spec}(\slashed D_{S^3})
=
\left\{\pm\frac{n+3/2}{R}\right\}_{n=0}^{\infty},
\]

with multiplicity \((n+1)(n+2)\) for each sign. Therefore

\[
\kappa_n^2
=
\frac{(n+3/2)^2}{R^2}+m^2,
\qquad
 d_n=2(n+1)(n+2).
\]

There is no spinor zero mode in this round baseline. That does not solve the
zero-mode problem of the full gauge-fixed BHSM bundle, which also contains
gauge, metric, seam, and collective sectors.

## 3. Exact DtN eigenvalues

For a seam value \(u(0)=f\), the decaying parent solution is

\[
u_p(r)=f e^{-\kappa r},
\]

so, using the parent outward normal at the seam,

\[
\mathcal N_p(\kappa)=\kappa.
\]

For a finite child collar with an inner Dirichlet condition,

\[
\mathcal N_c^{D}(\kappa)=\kappa\coth(\kappa L),
\]

and hence

\[
\Delta\mathcal N_D
=
\kappa\bigl(\coth(\kappa L)-1\bigr)
=
\frac{2\kappa}{e^{2\kappa L}-1}>0.
\]

For an inner Neumann condition,

\[
\mathcal N_c^{N}(\kappa)=\kappa\tanh(\kappa L),
\]

and

\[
\Delta\mathcal N_N
=
\kappa\bigl(\tanh(\kappa L)-1\bigr)<0.
\]

Therefore the sign of the reduced parent-child response is not determined by
the common seam geometry alone. The regular core-cap domain must be selected by
the full action and regularity conditions. Choosing the sign because it gives a
preferred neutrino result would violate the no-retuning rule.

## 4. Trace-class seam theorem

For the Dirichlet branch,

\[
\Delta\mathcal N_{D,n}
=
\frac{2\kappa_n}{e^{2\kappa_nL}-1}.
\]

At large \(n\), the multiplicity grows quadratically while \(\kappa_n\) grows
linearly. Thus

\[
 d_n\Delta\mathcal N_{D,n}
=
O\!\left(n^3e^{-2Ln/R}\right).
\]

Consequently

\[
\sum_{n=0}^{\infty}d_n\left|\Delta\mathcal N_{D,n}\right|<\infty.
\]

The code supplies a conservative closed-form tail bound based on geometric
moments through cubic order. For its deterministic dimensionless fixture it
reports a certified interval for the full trace.

This proves trace class for the **reduced seam DtN difference**. It does not
prove that the full four-dimensional bulk relative heat evolution is trace
class, nor that the shape derivative of the physical relative determinant is
already controlled.

## 5. Round-symmetry obstruction to flavor mixing

The round homogeneous DtN map is a spectral function of the tangential round
operator. It therefore commutes with the full round isometry action and is
scalar on every irreducible harmonic block:

\[
\Delta\mathcal N\big|_{\mathcal H_n}
=
\delta_n I_{\mathcal H_n}.
\]

By Schur's lemma it cannot generate off-diagonal Peter-Weyl channels inside a
fixed irreducible block. In particular it cannot, by itself, produce the
noncentral three-component wake required by v14.54-v14.57 for flavor mixing or
CP-capable monodromy.

This is a useful negative result. The next physical operator must contain at
least one action-owned symmetry-breaking source, such as:

- Berger anisotropy;
- a nonuniform moving seam;
- a nontrivial core-wall matcher selected by the action;
- a gauge or topographic background that breaks the round block degeneracy.

## 6. Scale covariance

Under

\[
R\mapsto sR,
\qquad
L\mapsto sL,
\qquad
m\mapsto m/s,
\]

one has

\[
\kappa_n\mapsto\kappa_n/s,
\qquad
\Delta\mathcal N_n\mapsto\Delta\mathcal N_n/s.
\]

The dimensionless shape data remain unchanged. The reduced spectrum therefore
does not select the absolute particle scale. A cosmological radius can serve as
an external anchor only after the action selects the nesting ratio between that
parent and the particle child.

## 7. Relationship to the pair-wake neutrino action

v14.58 preserves the fixed-pair interpretation:

\[
\text{fixed pair}\rightarrow\text{elapsed-time cycle}\rightarrow
\text{three perceived wake responses}.
\]

The exact round collar contributes a diagonal baseline response. It does not
supply the noncommuting shape channels. Those must arise from the anisotropic,
moving, action-selected physical seam. Matter kicks remain common-mode pushes
on the intact pair, with phase changes mediated by the explicit
collective-to-wake coupling established in v14.56.

## 8. Hindsight 20/20

### Validated

- Exact round \(S^3\) Dirac-Laplace eigenvalues and multiplicities provide a
  non-synthetic spectral baseline.
- The finite-collar and half-cylinder DtN eigenvalues are analytic.
- The reduced Dirichlet seam contrast is trace class because exponential mode
  decay dominates polynomial degeneracy.
- Global rescaling changes the DtN response by inverse length and does not
  select a scale.
- Round homogeneous response is central on each irreducible block and cannot
  generate flavor mixing.

### Invalidated or reclassified

- A matched seam metric uniquely fixes the sign of the parent-child DtN
  contrast.
- A round homogeneous parent-child response can generate the required
  noncentral wake.
- A trace-class seam DtN difference proves the full bulk relative heat-kernel
  theorem.
- The exact round baseline is already the physical BHSM particle operator.
- A cosmological radius alone fixes the particle radius without an
  action-selected nesting ratio.

### Open

- regular action-selected core-cap domain;
- coupled cosmological-parent and particle-child backgrounds;
- Berger-anisotropic gauge-fixed Dirac-Laplace spectrum;
- complete gauge and geometric zero-mode projector;
- moving-seam off-diagonal shape derivatives;
- full bulk relative heat-kernel small- and large-time control;
- converged periodic BVP and physical monodromy;
- blinded one-shot neutrino kill-screen execution;
- physical neutrino masses, splittings, matter response, CP behavior, and
  widths.

## Exact next object

`ACTION_DERIVED_BERGER_ANISOTROPIC_MOVING_SEAM_DIRAC_LAPLACE_OPERATOR_WITH_A_REGULAR_CORE_CAP_DOMAIN_COMPLETE_GAUGE_ZERO_MODE_PROJECTOR_AND_OFF_DIAGONAL_SHAPE_DERIVATIVES_INSERTED_INTO_THE_NO_RETUNING_NEUTRINO_KILL_SCREEN`

BHSM remains incomplete. Frozen predictions and official prediction logic are
unchanged. USB remains untouched.
