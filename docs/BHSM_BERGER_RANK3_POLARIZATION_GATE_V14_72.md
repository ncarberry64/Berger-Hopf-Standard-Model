# BHSM v14.72 — Berger Rank-Three Carrier and Global Polarization Gate

## Executive result

v14.71 proved that the complete second-shape Hessian cannot select three modes
while the physical stationary background retains the full round
\(SU(2)_L\times SU(2)_R\) symmetry.

v14.72 tests the strongest symmetry-breaking structure that BHSM already has:
the twistor/ Berger metric family.

For

\[
g_B
=
L_2^2(\sigma_1^2+\sigma_2^2)
+
L_1^2\sigma_3^2,
\]

the repository Berger scalar spectrum is

\[
\lambda_{J,m}
=
\frac{J(J+1)}{L_2^2}
+
m^2
\left(
\frac1{L_1^2}-\frac1{L_2^2}
\right).
\]

The round \(\ell=2\) shape sector is the \(J=1\) Peter-Weyl sector and has
dimension nine.  Therefore any fixed-axis nonround Berger squashing gives

\[
\boxed{9=3\oplus6.}
\]

The isolated three-dimensional branch is \(m_R=0\).

This is the first exact pre-existing BHSM geometry found in the present
completion chain that is capable of isolating a rank-three shape carrier
without fitting.

It is **not yet a physical selector**.

---

## 1. Fixed-volume shape variables

Separate overall size from squashing with

\[
\rho=(L_2^2L_1)^{1/3},
\qquad
\beta=\frac{L_1}{L_2}.
\]

Then

\[
L_2=\rho\beta^{-1/3},
\qquad
L_1=\rho\beta^{2/3},
\]

so \(L_2^2L_1=\rho^3\) exactly.

For \(J=1\),

\[
\boxed{
\rho^2\lambda_{m=0}
=
2\beta^{2/3}
}
\]

with multiplicity three, while

\[
\boxed{
\rho^2\lambda_{|m|=1}
=
\beta^{2/3}+\beta^{-4/3}
}
\]

has combined multiplicity six.

The gap is

\[
\boxed{
\rho^2\Delta
=
\beta^{-4/3}-\beta^{2/3}.
}
\]

Hence

\[
\Delta=0
\iff
\beta=1.
\]

Every positive \(\beta\neq1\) isolates a rank-three spectral branch.

This selection is dimensionless.  The absolute mass/length scale is not needed
to decide whether the three-dimensional carrier exists.

---

## 2. Infinitesimal departure from the round point

At fixed volume,

\[
\left.
\frac{d\lambda_0}{d\beta}
\right|_{\beta=1}
=
\frac{4}{3\rho^2},
\]

and

\[
\left.
\frac{d\lambda_{\pm1}}{d\beta}
\right|_{\beta=1}
=
-\frac{2}{3\rho^2}.
\]

Therefore

\[
\left.
\frac{d\Delta}{d\beta}
\right|_{\beta=1}
=
-\frac{2}{\rho^2}.
\]

The multiplicity-weighted trace shift vanishes:

\[
3\left(\frac43\right)
+
6\left(-\frac23\right)
=0.
\]

So fixed-volume squashing is a pure first-order anisotropy: it splits the
\(3+6\) sectors without changing their nine-state average at first order.

The deterministic finite-difference check agrees with the analytic derivatives
to better than \(10^{-8}\).

---

## 3. Symmetry reduction

For \(\beta\neq1\), the operator is

\[
H_B
=
\lambda_0 P_{m=0}
+
\lambda_1(I-P_{m=0}).
\]

It commutes with all left \(SU(2)_L\) generators and with the right \(U(1)\)
generator \(J_z\), but not with the other two right \(SU(2)_R\) generators.

Thus

\[
\boxed{
SU(2)_L\times SU(2)_R
\longrightarrow
SU(2)_L\times U(1)_R.
}
\]

This is enough to isolate a rank-three carrier.

A diagonal \(SU(2)\) is therefore **not the only possible route** to a
three-dimensional shape space.

---

## 4. The Berger triplet is not the v14.70 diagonal triplet

The v14.70 triplet was the antisymmetric piece in

\[
3\otimes3=1\oplus3\oplus5
\]

after selecting a diagonal \(SU(2)\).

The Berger carrier instead has product form

\[
V_L\otimes \ell_R,
\]

where \(\ell_R\) is the \(m_R=0\) line selected by the Berger axis.

These are structurally different subspaces.

In an aligned Cartesian representative:

- Berger rank = 3;
- diagonal-triplet rank = 3;
- intersection dimension = 0;
- projector trace overlap = 1;
- Frobenius projector distance = 2;
- principal angles = \(45^\circ,45^\circ,90^\circ\).

The zero intersection also follows abstractly: nonzero vectors in
\(V_L\otimes\ell_R\) are represented by rank-one matrices, whereas nonzero
antisymmetric \(3\times3\) matrices have even rank.

Therefore an action-derived intertwiner is required before either triplet can
be identified with the three physical moving-seam channels.

---

## 5. Why a fiberwise Berger split is not yet a physical selector

The repository already contains a twistor-mediated Berger metric and the exact
\(J,m\) spectrum.  But its own provenance ledger deliberately leaves the
parent action provisional, does not physically select the metric family, and
does not derive the squashing modulus.

The later authoritative bulk-boundary reduction retains the full
quaternionic-Hopf \(S^3\) transport and does not assert a preferred global
\(U(1)\) axis on the physical base.

The full-preimage audit also still lacks the required degree-one stationary
background.

So two things are missing:

1. a **physical polarization** that makes the right \(U(1)\) axis more than a
   coordinate/fiberwise construction;
2. a **stationary nonround value**
   \[
   \beta_\star\neq1
   \]
   selected by the same global action.

---

## 6. Orientation averaging restores the v14.71 no-go

For a Cartesian Berger axis \(\hat n\),

\[
P_B(\hat n)
=
I_3\otimes|\hat n\rangle\langle\hat n|.
\]

If no physical orientation is selected, the gauge/orientation average is

\[
\left\langle
|\hat n\rangle\langle\hat n|
\right\rangle
=
\frac13I_3.
\]

Therefore

\[
\boxed{
\langle P_B\rangle
=
\frac13I_9.
}
\]

The implementation verifies this exactly using the six Cartesian directions,
which form a second-moment spherical design.

Thus an unselected Berger axis collapses back to a central response and cannot
evade the v14.71 theorem.

---

## 7. Minimal action-selection contract

Let the global reduced functional be

\[
\Gamma_{\rm eff}
=
\Gamma_{\rm eff}
[\rho,\beta,\mathcal P,\Phi_I],
\]

where \(\mathcal P\) denotes a physical polarization or equivalent connection
holonomy.

Physical closure requires

\[
\partial_\beta\Gamma_{\rm eff}=0,
\]

the polarization Euler/Gauss equation, all other field equations, and a
positive gauge-reduced Schur curvature

\[
\boxed{
k_\beta^{\rm eff}
=
\Gamma_{\beta\beta}
-
\Gamma_{\beta I}
(\Gamma_{II}^{\rm phys})^{-1}
\Gamma_{I\beta}
>0.
}
\]

The triplet condition is simply

\[
\boxed{\beta_\star\neq1.}
\]

No measured mass or mixing datum may be used to choose \(\mathcal P\) or
\(\beta_\star\).

If the selector is produced by already-owned metric or connection degrees of
freedom, no new elementary field is required.

---

## 8. Important firewall: rank-three carrier is not three-channel dynamics

Pure axisymmetric Berger squashing acts on the selected carrier as

\[
H_B|_{\mathrm{rank}\,3}
=
\lambda_0 I_3.
\]

It therefore does **not** split its three members and does not generate the
noncommuting transverse operators required by the pair-wake/flavor program.

So v14.72 closes only the kinematic question:

> Can existing BHSM geometry contain an exact rank-three carrier after genuine
> symmetry breaking?

Yes.

It does not close:

- three distinct wake phases;
- noncommuting shape-current vertices;
- CKM or PMNS;
- physical neutrino mass splittings;
- the full Calderón/heat execution.

---

## 9. Hindsight 20/20 ledger

### VALIDATED

- Exact Berger \(J=1\) \(3+6\) splitting.
- Scale-free fixed-volume gap.
- Linear nonzero splitting at the round point.
- Multiplicity-traceless first-order deformation.
- \(SU(2)_L\times U(1)_R\) residual symmetry.
- Exact rank-three Berger spectral projector.
- Orientation averaging restores \(I_9/3\).
- Berger and diagonal-SU2 triplets are distinct.
- Existing BHSM geometry already contains the kinematic rank-three mechanism.

### INVALIDATED

- The diagonal-SU2 triplet is the only possible three-dimensional selector.
- A fiberwise Berger axis is automatically physical.
- The old twistor-Berger metric family already supplies an action-selected
  \(\beta_\star\).
- Axisymmetric Berger squashing alone generates the three noncommuting physical
  channels.

### RECLASSIFIED

The highest-upstream three-channel problem is now split into:

1. **rank-three carrier existence:** mathematically available;
2. **global physical polarization:** open;
3. **action-selected nonround \(\beta_\star\):** open;
4. **three transverse/noncommuting dynamics inside the carrier:** open.

### OPEN

The exact next object is

`GLOBAL_ACTION_DERIVATION_OF_A_PHYSICAL_SP1_TO_U1_POLARIZATION_SECTION_OR_EQUIVALENT_ADJOINT_CONNECTION_HOLONOMY_TOGETHER_WITH_A_GAUGE_REDUCED_STATIONARY_BERGER_SQUASHING_BETA_STAR_NOT_EQUAL_ONE_AND_POSITIVE_SCHUR_CURVATURE_THEN_ACTION_OWNED_TRANSPORT_OF_THE_RESULTING_RANK_THREE_SPECTRAL_PROJECTOR_INTO_THE_THREE_TRANSVERSE_CALDERON_SHAPE_DERIVATIVES_FOLLOWED_BY_NONCOMMUTING_WAKE_DYNAMICS_RELATIVE_HEAT_SUPERTRACE_AND_THE_FROZEN_NEUTRINO_KILL_SCREEN`

---

## 10. Completion state

`RANK3_CARRIER_MECHANISM = KINEMATICALLY_DERIVED`

`GLOBAL_PHYSICAL_SELECTOR = OPEN`

`STATIONARY_BETA_STAR = NULL`

`PHYSICAL_TRANSVERSE_TRIPLET_DYNAMICS = OPEN`

`PHYSICAL_EXECUTION = BLOCKED`

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`

No physical particle observable is emitted.
