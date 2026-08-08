# BHSM v14.39 — Static Eta/Metric Mixed Variation and Spin(4) Source Audit

## Primary verdict

`BHSM_STATIC_DEGREE_ONE_PATH_B_BACKGROUND_HAS_ZERO_COEXACT_ADM_MOMENTUM_SOURCE_AND_ZERO_STATIC_ETA_SHIFT_MIXED_BLOCK_SO_THE_SPIN4_L2_L3_BRANCH_DOES_NOT_TURN_ON`

## Secondary verdict

`THE_PATH_B_ETA_SPATIAL_METRIC_MIXED_SECOND_VARIATION_IS_DERIVED_EXACTLY_BUT_THE_NONHOMOGENEOUS_LAMBDA85_SPECTRUM_REMAINS_UNDEFINED_WITHOUT_A_GAUGE_FIXED_PARENT_METRIC_OPERATOR`

## Exact next object

`SELF_CONSISTENT_FERMION_OR_WILSON_SOURCED_COEXACT_L2_L3_ADM_SHIFT_ON_A_COMPACT_CAP_WITH_MATCHED_TETRAD_SPIN_CONNECTION_NORMALIZED_COMMON_DOMAIN_DIRAC_MODES_AND_ACTION_DERIVED_UP_DOWN_RESPONSE`

---

## 1. Question resolved

v14.38 showed that the currently retained homogeneous Lambda85/KKT attachment
branch is orthogonal to every nontrivial flavor channel.  The surviving options
were:

1. nonhomogeneous constraint-reduced metric/incidence modes carrying the same
   angular and Hopf labels as the eta flavor texture;
2. the v12.1 Spin(4) relative-rotation operator.

The two options do not have the same source condition.

The Path-B eta action has an exact mixed second variation with spatial metric
shape modes.  Therefore a nonhomogeneous **spatial** metric route is not ruled
out by the v14.38 homogeneous-character no-go.

However, the Spin(4) mechanism specifically requires a coexact rotational ADM
shift or relative spin connection.  A static degree-one eta background has no
matter momentum density and hence does not source the required `L=2` or `L=3`
rotational shift.  The static shift/phase mixed block also vanishes exactly.

Thus the static Path-B soliton does not spontaneously turn on the Spin(4)
family response.

---

## 2. Exact Path-B eta/metric mixed second variation

Use

\[
S_\eta=\int d\mu_g\,wF(X),
\qquad
F(X)=\frac{\kappa_1}{2}X+\frac18X^4,
\]

\[
X=g^{\mu\nu}A_{\mu\nu},
\qquad
A_{\mu\nu}=\langle D_\mu\eta,D_\nu\eta\rangle.
\]

Let

\[
\delta g^{\mu\nu}=\gamma^{\mu\nu},
\qquad
\delta\eta=V,
\]

and define

\[
\delta A_{\mu\nu}
=
\langle D_\mu V,D_\nu\eta\rangle
+
\langle D_\mu\eta,D_\nu V\rangle,
\]

\[
Y=g^{\mu\nu}\delta A_{\mu\nu}
=2\langle D\eta,DV\rangle.
\]

The exact local mixed bilinear is

\[
\boxed{
B_{g\eta}[\gamma,V]
=
\int d\mu_g\,w\,\gamma^{\mu\nu}
\left[
F''(X)Y A_{\mu\nu}
+F'(X)\delta A_{\mu\nu}
-\frac12F'(X)Yg_{\mu\nu}
\right].
}
\]

For the Path-B density,

\[
F'(X)=\frac12(\kappa_1+X^3)>0,
\qquad
F''(X)=\frac32X^2\ge0.
\]

This identity was checked numerically against a centered mixed finite
difference on deterministic random positive metrics and target gradients.

The formula proves that a nonhomogeneous spatial metric perturbation can couple
to a nontrivial eta shape mode.  It does **not** supply the metric propagator,
its sign, its cap boundary conditions, or its normalized Schur complement.
Those belong to the gauge-fixed parent metric operator, not to Lambda85 itself.

---

## 3. Phase specialization

Let `T` be a constant antisymmetric target-space generator and

\[
V=\phi T\eta.
\]

Define the background Noether current

\[
j_\mu=\langle D_\mu\eta,T\eta\rangle.
\]

Antisymmetry of `T` removes the terms proportional to
\(\phi\langle D_\mu\eta,TD_\nu\eta\rangle\) after symmetrization.  The mixed
bilinear reduces to

\[
\boxed{
B_{g\phi}[\gamma,\phi]
=
\int d\mu_g\,w\,\gamma^{\mu\nu}
\left[
2F''(X)(j\cdot d\phi)A_{\mu\nu}
+2F'(X)j_{(\mu}\partial_{\nu)}\phi
-F'(X)g_{\mu\nu}(j\cdot d\phi)
\right].
}
\]

A spatial metric flavor block can therefore be nonzero only when the actual
full-preimage background carries the relevant target Noether current and the
phase texture has a nonzero gradient.

This is a precise action-owned coupling formula.  It is not yet an instability
calculation because the physical spatial metric Hessian remains undefined.

---

## 4. Static ADM shift block

Now specialize to a static block-diagonal background:

\[
g_{0i}=0,
\qquad
D_0\eta=0,
\qquad
j_0=0.
\]

For an inverse-metric shift perturbation
\(\gamma^{0i}=\beta^i\), the only possible phase term is

\[
B_{\beta\phi}
\propto
2wF'(X)\,\dot\phi\,\beta^ij_i.
\]

Therefore

\[
\boxed{
B_{\beta\phi}^{\rm static}=0
\quad\text{when}\quad
\dot\phi=0.
}
\]

The nonzero-frequency term is gyroscopic or kinetic.  It can modify the
collective dynamics, but it cannot provide the missing negative **static**
Hessian curvature by itself.

---

## 5. Static momentum constraint

The scalar contribution to the ADM momentum density is

\[
J_i^{(\eta)}
=
2wF'(X)\langle D_0\eta,D_i\eta\rangle.
\]

On the static branch,

\[
\boxed{J_i^{(\eta)}=0.}
\]

If the Yang-Mills electric momentum also vanishes,

\[
J_i^{\rm total}=0.
\]

The coexact part of the momentum constraint is therefore homogeneous.  On a
compact self-adjoint domain with no imposed rotating boundary datum, the
non-Killing coexact solution is zero.  In particular, the `L=2` and `L=3`
relative-rotation amplitudes required by the v12.1 family-selection theorem are
not activated by the static eta background.

Killing zero modes may remain as global rotations, but v12.1 already established
that a rigid `L=1` rotation is family diagonal and cannot produce the required
mixing.

---

## 6. Consequence for the Spin(4) route

The v12.1 operator

\[
R_{\rm rel}
=
-i\mathcal L_{\beta_{\rm rel}^{\rm rot}}^K
+i\gamma^iJ_a(\delta\omega_i^a+\gamma_5\chi_i^a)
\]

remains a valid conditional representation mechanism.  Its `L=2\oplus L=3`
content can connect the frozen family slots.

But the static Path-B background supplies neither:

- a coexact momentum source;
- a nonzero rotating boundary condition;
- a matched relative tetrad/spin connection.

Thus the Spin(4) response is not merely unnormalized.  Its amplitude is zero on
the present static branch.

The route can reopen through an action-owned source such as:

1. a time-dependent eta collective rotation;
2. a localized fermion angular-momentum current;
3. a Wilson/hadron momentum source;
4. nonzero rotating cap boundary data selected by a stationary coupled problem.

No one of these is inserted in v14.39.

---

## 7. Status of nonhomogeneous Lambda85

Lambda85 remains an algebraic compatibility multiplier.  Allowing it to depend
on position does not turn it into a propagating tensor field.  Harmonic by
harmonic, its variation imposes the local constraint

\[
\delta C_{\ell p}=0.
\]

The physical nonhomogeneous modes are metric/incidence fluctuations restricted
to the kernel of that constraint.  To evaluate their coupling to eta, BHSM
still needs:

- the gauge-fixed parent Einstein/metric Hessian;
- the cap and seam boundary conditions;
- elimination of Lambda85 on each tensor-harmonic block;
- the compact self-adjoint spectrum;
- the normalized eta/metric mixed matrix from the formula above;
- the Schur-complement zero-crossing test.

The homogeneous v11.3 matrix cannot be copied into these blocks.

---

## 8. Architectural consequence

The v14.35 eta-texture bifurcation and the v12.1 Spin(4) family response are now
separated:

\[
\boxed{
\text{eta texture branch}
\neq
\text{rotational Spin(4) response branch}.
}
\]

A static eta soliton may possess spatial stress and may couple to spatial metric
shape modes.  It does not carry momentum and therefore cannot source the
rotational shift.

For CKM work, the shortest surviving route is now a self-consistent localized
matter or Wilson-sourced coexact shift followed by the already-known Kosmann
and spin-connection projection.  This route does not require the pure eta phase
Hessian to become negative first.

---

## Hindsight 20/20

### Validated

- The exact Path-B eta/spatial-metric mixed second variation is derived.
- Its phase specialization is controlled by the background Noether current.
- A static shift/phase mixed block vanishes exactly.
- A static eta background has zero ADM momentum density.
- The v12.1 `L=2\oplus L=3` representation theorem remains valid conditionally.

### Invalidated

- Static degree-one eta stress as a source for the Spin(4) coexact rotational
  branch.
- Treating nonhomogeneous Lambda85 as a propagating attachment field.
- Using a dynamic gyroscopic shift coupling as a negative static Hessian term.
- Continuing the nonlinear CKM branch before a nonzero source and matched spin
  connection exist.

### Reclassified

- The nonhomogeneous Lambda85 route is a constraint-reduced **metric** problem,
  not a Lambda85 spectrum.
- Spin(4) can bypass the eta phase bifurcation, but only in a sourced rotating or
  time-dependent state.

### Open

- Gauge-fixed compact-cap spatial metric spectrum.
- Full-preimage Noether-current matrix elements.
- Self-consistent fermion/Wilson momentum source.
- Coexact `L=2,L=3` shift solution.
- Matched tetrad and spin connection.
- Normalized common-domain Dirac modes and reduced matrix elements.
- Action-derived up/down response matrices, CKM and CP.

---

## Completion status

BHSM is not complete.  Frozen predictions are unchanged.  No physical CKM,
CP phase, mass, or dimensional scale is emitted.  The USB remains untouched.
