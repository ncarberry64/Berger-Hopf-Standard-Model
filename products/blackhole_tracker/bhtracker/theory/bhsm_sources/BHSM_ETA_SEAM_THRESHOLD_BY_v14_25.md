# BHSM v14.25 — Seam-Higgs Thresholds and Spherical Interface Charge

## 1. Representation-dependent threshold masses

The two-sided eta construction has exact normal overlap

\[
\zeta_{+-}=1.
\]

Therefore the seam-Higgs mass matrices are

\[
\boxed{
M_f
=
\frac{v_{\rm BH}}{\sqrt2}\mathbb Y_f.
}
\]

For each Yukawa singular value \(y_{f,r}\),

\[
\boxed{
\frac{M_{f,r}}{E_0}
=
\frac{v_{\rm BH}}{E_0}
\frac{|y_{f,r}|}{\sqrt2}.
}
\]

The eta wall supplies localization and chirality. It contributes no additional
representation-dependent overlap factor.

Primary verdict:

`BHSM_TWO_SIDED_ETA_LOCALIZATION_HAS_UNIT_NORMAL_OVERLAP_SO_ALL_REPRESENTATION_AND_FAMILY_THRESHOLD_SPLITTING_RESIDES_IN_THE_ACTION_OWNED_SEAM_HIGGS_YUKAWA_SPECTRA`

Thus the threshold problem is reduced to deriving:

- \(v_{\rm BH}/E_0\);
- \(\mathbb Y_u\);
- \(\mathbb Y_d\);
- \(\mathbb Y_e\);
- the neutral-sector mass operator when applicable.

## 2. Electroweak staging correction

A direct chiral mass such as

\[
\bar Q_Lu_R
\]

is not invariant under the unbroken electroweak group. The gauge-invariant
operator is

\[
\bar Q_L\widetilde H\,\mathbb Y_u u_R.
\]

Therefore ordinary Standard Model fermion masses appear only after the seam
Higgs develops a vacuum.

The RG pipeline must be piecewise.

### Above \(v_{\rm BH}\)

\[
SU(3)_c\times SU(2)_L\times U(1)_Y.
\]

Run

\[
g_1,\quad g_2,\quad g_3
\]

with the chiral matter fields active.

### At \(v_{\rm BH}\)

Diagonalize

\[
M_u=\frac{v_{\rm BH}}{\sqrt2}\mathbb Y_u,
\]

\[
M_d=\frac{v_{\rm BH}}{\sqrt2}\mathbb Y_d,
\]

\[
M_e=\frac{v_{\rm BH}}{\sqrt2}\mathbb Y_e,
\]

and match

\[
\frac1{e^2}
=
\frac1{g_Y^2}
+
\frac1{g_2^2}.
\]

### Below \(v_{\rm BH}\)

The effective gauge group is

\[
SU(3)_c\times U(1)_{\rm em}.
\]

Run

\[
g_3,\quad e
\]

and integrate physical mass eigenstates component by component.

The unbroken \(g_1,g_2,g_3\) whole-multiplet beta vectors cannot simply be
continued through ordinary fermion mass thresholds.

Verdict:

`BHSM_CHIRAL_STANDARD_MODEL_FERMION_MASSES_REQUIRE_PIECEWISE_ELECTROWEAK_MATCHING_AND_CANNOT_BE_USED_AS_WHOLE_MULTIPLET_THRESHOLDS_IN_UNBROKEN_G1_G2_G3_RUNNING`

The v14.24 threshold kernel remains directly applicable to additional heavy
states that:

1. possess a gauge-invariant mass above \(v_{\rm BH}\);
2. form complete representations of the unbroken gauge group.

## 3. Spherical parent geometry

For the round parent \(S^3\), use the areal radius

\[
\rho=R_0\lambda,
\qquad
\lambda=\sin\chi.
\]

The parent radial factor is

\[
\boxed{
F_0(\lambda)=1-\lambda^2.
}
\]

In the time-symmetric spherical constraint reduction, an enclosed relative
source \(\widehat E_{\rm matter}\) changes the radial factor to

\[
\boxed{
F(\lambda)
=
F_0(\lambda)
-
\frac{2\gamma_G\widehat E_{\rm matter}}{\lambda},
}
\]

where

\[
\boxed{
\gamma_G
=
\frac{\ell_P^2}{R_0^2}.
}
\]

## 4. Explicit relative Brown–York charge

The parent-relative Brown–York energy at the interface is

\[
\boxed{
\Delta\widehat E_{\rm BY}
=
\frac{\lambda}{\gamma_G}
\left[
\sqrt{F_0}-\sqrt F
\right].
}
\]

The numerically stable equivalent form is

\[
\boxed{
\Delta\widehat E_{\rm BY}
=
\frac{
2\widehat E_{\rm matter}
}{
\sqrt{F_0}+\sqrt F
}.
}
\]

This is the first explicit evaluation of the gravitational interface charge
in the reduced spherical BHSM sector.

Using the v14.23 reduced source,

\[
\lambda=0.3644325544,
\]

\[
\widehat E_{\rm matter}=9.8689261083,
\]

and the dimensional witness

\[
R_0=10^{-18}\ {\rm m},
\]

gives the weak-gravity value

\[
\boxed{
\Delta\widehat E_{\rm BY}
\approx
10.5970.
}
\]

The difference from the local reduced source is the parent-interface redshift.

This number is not a physical meson prediction. It uses the same unphysical
\(R_0,c_{\rm YM},\widehat\kappa\), zero-threshold, and incomplete-source
witnesses as v14.23.

Charge verdict:

`BHSM_SPHERICAL_S3_COMPOSITE_MINUS_PARENT_GRAVITATIONAL_ENERGY_HAS_AN_EXPLICIT_RELATIVE_BROWN_YORK_INTERFACE_CHARGE_CONDITIONALLY_ON_THE_TIME_SYMMETRIC_EINSTEIN_CONSTRAINT`

## 5. Energy-counting rule

Once the coupled Dirac equation includes the seam-Higgs mass operator, its
fermionic energy must not be added a second time as an independent mass term.

The Higgs field deformation relative to its vacuum remains a separate bosonic
energy.

Once the Einstein constraint is solved, the Brown–York charge is the total
matter-plus-gravity interface energy. A separate gravitational correction
must not be added on top of it.

The nonlinear Wilson-line color functional must likewise enter the equations
and stress tensor exactly once.

## 6. Gate status

Closed:

- exact seam-Higgs threshold mass map;
- localization/mass role separation;
- electroweak piecewise matching structure;
- heavy-multiplet eligibility rule;
- spherical Brown–York interface charge formula;
- energy double-counting ledger.

Invalidated:

- eta overlap as a representation-splitting source;
- ordinary chiral masses as unbroken whole-multiplet thresholds.

Open:

- action-owned complete Yukawa spectra;
- action-derived \(v_{\rm BH}/E_0\);
- component-level broken-phase threshold running;
- coupled spherical Einstein solution and interface metric;
- full nonlinear Wilson-line stress;
- full covariant phase-space charge;
- physical mass prediction.

Exact next object:

`ACTION_OWNED_SEAM_HIGGS_YUKAWA_SPECTRA_WITH_ELECTROWEAK_STAGE_MATCHING_AND_COUPLED_SPHERICAL_EINSTEIN_CONSTRAINT_SOLUTION_FIXING_THE_FULL_COMPOSITE_INTERFACE_METRIC_AND_RELATIVE_CHARGE`

Mark III remains not reached. BHSM physical completion remains false.
