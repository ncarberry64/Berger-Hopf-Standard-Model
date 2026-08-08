# BHSM v14.70 — Round Second-Shape Jacobi Spectrum and Triplet Selection Gate

## Result

v14.69 proved that the first induced-metric response of a pure normal seam
displacement vanishes at the retained reflection-symmetric round equator:

\[
\delta h_{ab}=2\xi K_{ab}=0.
\]

v14.70 therefore executes the required fallback rather than inserting a
nonround extrinsic curvature by hand. It derives the exact second normal-shape
variation on the round `S^3` seam and asks whether that second-order geometry
selects exactly three nonuniform moving-seam channels.

It does **not**.

The round scalar shape spectrum has multiplicities

\[
1,4,9,16,25,\ldots,
\]

so no scalar eigenspace has dimension three. The first positive shape space is
`ell=2`, dimension nine. That nine-dimensional representation *contains* a
rank-three subrepresentation after a diagonal `SU(2)` is chosen, but the
current global BHSM action does not yet select that polarization or identify
its triplet with the previously declared three shape channels.

Primary verdict:

`BHSM_V14_70_THE_RETAINED_TWO_CAP_REFLECTION_SYMMETRY_KEEPS_THE_ROUND_EQUATOR_FIRST_SHAPE_STATIONARY_AND_THE_EXACT_SECOND_NORMAL_SHAPE_VARIATION_YIELDS_THE_S3_JACOBI_SPECTRUM_J_L_EQUALS_L_MINUS_1_TIMES_L_PLUS_3_OVER_A_SQUARED_WITH_MULTIPLICITIES_L_PLUS_1_SQUARED_SO_ROUND_SCALAR_GEOMETRY_DOES_NOT_SELECT_EXACTLY_THREE_CHANNELS;_THE_FIRST_POSITIVE_L2_SPACE_IS_NINE_DIMENSIONAL_AND_CONTAINS_A_1_PLUS_3_PLUS_5_DIAGONAL_SU2_DECOMPOSITION_BUT_THE_TRIPLET_SELECTION_REQUIRES_AN_ACTION_OWNED_HOPF_OR_POLARIZATION_INTERTWINER_AND_THE_COMPLETE_GLOBAL_SECOND_SHAPE_HESSIAN_REMAINS_OPEN`

Full BHSM completion remains false. Mark III is not reached.

---

## 1. Why the round branch remains first-shape stationary

The retained two-cap geometry is reflection symmetric:

\[
\chi\mapsto\pi-\chi,
\]

with the common seam at

\[
\chi=\frac\pi2.
\]

A normal displacement changes sign under this cap exchange,

\[
\xi\mapsto-\xi.
\]

Therefore any globally assembled action functional that preserves the retained
cap-exchange symmetry satisfies

\[
\Gamma[\xi]=\Gamma[-\xi]
\]

on this symmetric branch, and hence

\[
\boxed{D\Gamma[0]=0.}
\]

This is shape stationarity inside the reflection-symmetric round branch. It is
not a proof that the full parent/child background is stationary under every
bulk field variation, and it does not exclude a separate symmetry-breaking
nonround stationary branch.

No action-selected nonround branch is currently available, so v14.70 takes the
second-shape route.

---

## 2. Exact second induced-metric variation

At fixed time, write the round spatial cap as

\[
ds_4^2=a^2\left(d\chi^2+\sin^2\chi\,d\Omega_3^2\right).
\]

Let a physical normal displacement \(\xi(x)\) define the graph

\[
\chi(x;\epsilon)=\frac\pi2+\epsilon\frac{\xi(x)}a.
\]

The induced spatial seam metric is exactly

\[
h_{ij}(\epsilon)
=a^2\cos^2\!\left(\epsilon\frac\xi a\right)\gamma_{ij}
+\epsilon^2\partial_i\xi\,\partial_j\xi.
\]

Therefore

\[
\left.\frac{dh_{ij}}{d\epsilon}\right|_0=0,
\]

and

\[
\boxed{
\left.\frac{d^2h_{ij}}{d\epsilon^2}\right|_0
=2\left(\nabla_i\xi\nabla_j\xi-\frac{\xi^2}{a^2}h_{ij}\right).
}
\]

Polarizing gives the bilinear second differential

\[
\boxed{
D^2h[\xi,\eta]_{ij}
=\nabla_i\xi\nabla_j\eta
+\nabla_i\eta\nabla_j\xi
-\frac{2\xi\eta}{a^2}h_{ij}.
}
\]

The implementation verifies the polarization identity to machine precision and
checks the constant-displacement curvature term against the exact
`cos^2(epsilon xi/a)` metric by finite difference.

This is important structurally: the second shape map is bilinear. It is not a
replacement first-order incidence matrix from `xi` into the metric boundary
space.

---

## 3. Universal round Jacobi form

Taking half the background trace gives

\[
\frac12\operatorname{tr}_h D^2h[\xi,\eta]
=
\langle\nabla\xi,\nabla\eta\rangle
-\frac{3}{a^2}\xi\eta.
\]

Thus the universal minimal-equator area Jacobi form is

\[
Q(\xi,\eta)
=
\int_{S^3_a}
\left(
\langle\nabla\xi,\nabla\eta\rangle
-\frac{3}{a^2}\xi\eta
\right)d\mu.
\]

Equivalently,

\[
\boxed{J_{\rm round}=-\Delta_{S^3}-\frac3{a^2}.}
\]

This is a universal geometric contribution. It is **not yet** the complete
BHSM second shape Hessian, which must also contain the second variations of the
M8/M5 bulk terms, GHY completion, compatibility/KKT reaction, localized matter,
and the relative nonlocal spectral functional.

---

## 4. Exact scalar harmonic spectrum

For scalar harmonics on `S^3_a`,

\[
-\Delta Y_{\ell}
=
\frac{\ell(\ell+2)}{a^2}Y_\ell,
\]

with multiplicity

\[
\boxed{d_\ell=(\ell+1)^2.}
\]

The round Jacobi eigenvalue is therefore

\[
\boxed{
\lambda^{\rm shape}_\ell
=
\frac{\ell(\ell+2)-3}{a^2}
=
\frac{(\ell-1)(\ell+3)}{a^2}.
}
\]

The first sectors are

| `ell` | Jacobi eigenvalue | multiplicity | interpretation |
|---:|---:|---:|---|
| 0 | `-3/a^2` | 1 | homogeneous area instability of an unconstrained equator |
| 1 | `0` | 4 | ambient great-sphere rotation/isometry orbit |
| 2 | `5/a^2` | 9 | first positive scalar round shape space |
| 3 | `12/a^2` | 16 | higher positive shape space |

The homogeneous negative area mode does **not** by itself prove a BHSM global
instability because the complete action supplies additional bulk, constraint,
and nonlocal terms.

The `ell=1` zero modes must likewise be handled as symmetry directions before
any physical interpretation.

The decisive counting result is

\[
\boxed{(\ell+1)^2\neq3\quad\text{for every integer }\ell\ge0.}
\]

So round scalar second-shape geometry cannot directly produce exactly three
physical channels.

---

## 5. Where a triplet nevertheless appears

The first positive space has

\[
\dim\mathcal H_{\ell=2}=9.
\]

As an `SO(4) ~= SU(2)_L x SU(2)_R` representation,

\[
\mathcal H_{\ell=2}\cong(1,1).
\]

After choosing a diagonal subgroup,

\[
SU(2)_{\rm diag}\subset SU(2)_L\times SU(2)_R,
\]

Clebsch-Gordan decomposition gives

\[
\boxed{3\otimes3=1\oplus3\oplus5.}
\]

v14.70 constructs exact orthogonal projectors using the `3 x 3` matrix model:

- trace part: rank 1;
- antisymmetric part: rank 3;
- symmetric traceless part: rank 5.

The projectors are self-adjoint, idempotent, mutually orthogonal, and sum to
the identity on the nine-dimensional space.

Therefore

\[
\boxed{\text{a mathematical triplet exists inside }\ell=2.}
\]

But

\[
\boxed{\text{the current action does not yet select that triplet physically.}}
\]

Choosing the diagonal `SU(2)` already reduces the round symmetry, and selecting
the rank-three sector over the singlet and quintet requires an action-owned
Hopf/polarization intertwiner. The existing three predeclared moving-seam
channels are **not** identified with this triplet in v14.70.

---

## 6. Hindsight 20/20 ledger

### VALIDATED

- Reflection symmetry keeps the round seam first-shape stationary inside the
  retained symmetric two-cap branch.
- `K_ab=0` remains exact at the round equator.
- The exact static-normal-graph second metric variation is derived.
- The polarized second shape differential is derived.
- Its trace gives the universal round minimal-equator Jacobi form.
- Scalar `S^3` Laplacian eigenvalues and multiplicities are exact.
- The round area Jacobi eigenvalues are `(ell-1)(ell+3)/a^2`.
- `ell=1` contains four symmetry zero modes.
- The first positive round scalar shape space is `ell=2`, dimension 9.
- Under a chosen diagonal `SU(2)`, that space decomposes exactly as `1+3+5`.
- The rank-three projector is explicit and exact.

### INVALIDATED

- First-order round normal motion as the source of the three channels.
- A threefold scalar Jacobi eigenspace on round `S^3`.
- Automatic selection of the `ell=2` triplet by round geometry.
- Promotion of the universal area Jacobi operator to the complete BHSM shape
  Hessian.

### RECLASSIFIED

- The three-channel issue is now a **representation/polarization selection
  problem**, not merely a missing shape eigenvalue problem.
- The `ell=1` modes are symmetry zero modes rather than a three-flavor sector.
- The first positive round shape sector is nine-dimensional and requires an
  action-owned symmetry reduction before a triplet can be physical.
- The round branch is exhausted kinematically through second order; the next
  work is the complete action Hessian and its polarization.

### OPEN

- A globally stationary nonround cap or proof that no such branch exists.
- Full M8/M5 bulk second variation.
- GHY second shape term.
- Compatibility/KKT multiplier Hessian and physical Schur complement.
- Nonlocal relative determinant/heat contribution.
- Action-owned Hopf polarization or diagonal `SU(2)` selection.
- Intertwiner from the selected triplet to the three predeclared shape
  channels.
- Physical `h_C` and `k_D` on the same stationary solution.
- Complete gauge-fixed metric/gauge/spinor/ghost Calderon operators.
- Continuum relative heat supertrace and frozen neutrino execution.

---

## 7. Exact next object

`FULL_GLOBAL_SECOND_SHAPE_HESSIAN_ON_THE_ACTION_STATIONARY_PARENT_CHILD_BACKGROUND_INCLUDING_BULK_GHY_COMPATIBILITY_KKT_AND_NONLOCAL_SPECTRAL_TERMS_WITH_AN_ACTION_OWNED_HOPF_POLARIZATION_OR_DIAGONAL_SU2_INTERTWINER_THAT_SELECTS_OR_REJECTS_THE_L2_TRIPLET_THEN_THREE_NONUNIFORM_SHAPE_DERIVATIVES_COMPLETE_CALDERON_PROJECTORS_RELATIVE_HEAT_SUPERTRACE_AND_FROZEN_NEUTRINO_KILL_SCREEN`

No measured particle datum is used. No nonround `K_ab` is inserted. No
physical mass, CKM/PMNS matrix, neutrino splitting, coupling, or probability is
emitted. Frozen prediction logic is unchanged and USB remains untouched.
