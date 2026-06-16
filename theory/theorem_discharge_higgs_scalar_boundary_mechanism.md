# Theorem Discharge: Higgs Scalar Boundary Mechanism

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry. This branch attempts to derive the active scalar orientation doublet from boundary cyclic neutrality, active-orientation breaking, and neutral-vacuum consistency, rather than importing the Standard Model Higgs representation as an assumption. Status labels may be promoted only when the derivation is explicit, exact, non-tautological, and does not use the known Standard Model Higgs doublet as a premise.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the primitive closure spectrum, finite boundary algebra, boundary charge/hypercharge operators, anomaly consistency, boundary gauge algebra/action skeletons, trace normalization, and one-loop RG coefficients.

## 3. Why The Higgs/Scalar Theorem Is The Next Blocker

The one-loop RG layer used the active scalar orientation doublet as a conditional input. This branch derives that representation source from boundary constraints.

## 4. Boundary Scalar Constraints

The scalar must preserve the cyclic channel, be active under orientation breaking, admit a neutral vacuum component, and be minimal in boundary degree.

## 5. Cyclic Neutrality

Boundary cyclic preservation requires `C=0`.

## 6. Active-Orientation Requirement

Breaking the active-orientation factor requires the scalar to transform as a fundamental orientation doublet.

## 7. Neutral Vacuum Requirement

Using `Q=T3+Y/2`, a vacuum component must have `Q=0`.

## 8. Hypercharge Selection (Y=+1) Up To Conjugation

For `T3=sigma/2`, neutral consistency gives `Y=-sigma`. The two possible neutral choices are conjugate scalar conventions. This branch chooses `Y=+1`.

## 9. Scalar Charge Table

| component | sigma | T3 | Y | Q |
| --- | --- | --- | --- | --- |
| H_plus | +1 | 1/2 | 1 | 1 |
| H_zero | -1 | -1/2 | 1 | 0 |

## 10. Derived Conjugate Scalar Doublet

The conjugate `H_tilde=i sigma_2 H*` is derived from the same complex doublet, not added as an independent second scalar multiplet.

| component | sigma | T3 | Y | Q |
| --- | --- | --- | --- | --- |
| H_tilde_zero | +1 | 1/2 | -1 | 0 |
| H_tilde_minus | -1 | -1/2 | -1 | -1 |

## 11. Electroweak-Breaking Generator

With `<H>=(0,v/sqrt(2))^T`, `Q<H>=0`, so:

```text
SU(2)_orient x U(1)_Y -> U(1)_Q
```

## 12. Scalar Covariant Derivative

```text
D_mu H=(partial_mu - i g2 W_mu^a tau^a/2 - i gY B_mu Y/2)H with Y=1
```

## 13. Scalar Kinetic/Gauge-Boson Mass Skeleton

```text
m_W^2 = g2^2 v^2/4
m_Z^2 = (g2^2 + gY^2)v^2/4
m_A^2 = 0
```

This is a mass skeleton, not a measured mass prediction.

## 14. Scalar Potential Skeleton

```text
V(H)=m_H^2 H^dagger H + lambda_H (H^dagger H)^2
m_H^2 < 0
```

The instability sign and scalar potential values remain conditional/open unless derived elsewhere.

## 15. What Remains Conditional

The negative mass-squared sign, Higgs mass, VEV, quartic coupling, and Yukawa/mass/mixing sector remain open.

## 16. Non-Tautology Checks

See [Higgs Scalar Non-Tautology Audit](higgs_scalar_non_tautology_audit.md).

## 17. Promoted Results, If Any

- `PO_BH_16_HIGGS_SCALAR_ACTIVE_ORIENTATION_DOUBLET_DERIVED_CONDITIONAL`
- `BOUNDARY_ACTIVE_SCALAR_DOUBLET_DERIVED_CONDITIONAL`
- `ELECTROWEAK_BREAKING_GENERATOR_DERIVED_CONDITIONAL`
- `SCALAR_BETA_INPUT_NOW_DERIVED_CONDITIONAL`

## 18. Impact On One-Loop RG Theorem

The active scalar input used in the one-loop RG theorem now has a conditional boundary-representation source.

## 19. Impact On Yukawa/Mass Theorem

No Yukawa, mass, or mixing theorem is completed here.

Follow-up theorem layer: [Theorem discharge: Yukawa operator closure](theorem_discharge_yukawa_operator_closure.md) uses the derived scalar and conjugate scalar doublets to conditionally derive the renormalizable boundary Yukawa operator skeleton. Numerical Yukawa values, mass ratios, and CKM/PMNS mixing remain open.

Further follow-up: [Theorem discharge: Yukawa overlap texture source](theorem_discharge_yukawa_overlap_texture_source.md) uses the same scalar insertions to define symbolic boundary-overlap matrix scaffolds without changing official predictions.

## 20. What This Achieves

This branch conditionally discharges the Higgs/scalar boundary-mechanism theorem layer. Boundary cyclic preservation requires C=0, active-orientation breaking requires a fundamental orientation doublet, and neutral-vacuum consistency under Q=T3+Y/2 selects Y=+1 up to conjugation. The resulting scalar has component charges (+1,0), admits a neutral vacuum preserving U(1)_Q, and yields the electroweak-breaking skeleton SU(2)_orient x U(1)_Y -> U(1)_Q. The representation source for the scalar contribution used in the one-loop RG theorem is therefore derived conditionally from BHSM boundary constraints.

## 21. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until scalar potential parameters, Yukawa/mass/mixing, and full low-energy Lagrangian derivations are complete.

## Verdict Labels

- `THEOREM_DISCHARGE_HIGGS_SCALAR_BOUNDARY_MECHANISM_COMPLETE`
- `PO_BH_16_HIGGS_SCALAR_ACTIVE_ORIENTATION_DOUBLET_DERIVED_CONDITIONAL`
- `BOUNDARY_ACTIVE_SCALAR_DOUBLET_DERIVED_CONDITIONAL`
- `SCALAR_CHARGE_TABLE_DERIVED_CONDITIONAL`
- `SCALAR_CONJUGATE_DOUBLET_DERIVED_CONDITIONAL`
- `ELECTROWEAK_BREAKING_GENERATOR_DERIVED_CONDITIONAL`
- `SCALAR_COVARIANT_DERIVATIVE_DERIVED_CONDITIONAL`
- `SCALAR_POTENTIAL_SKELETON_DERIVED_CONDITIONAL`
- `SCALAR_BETA_INPUT_NOW_DERIVED_CONDITIONAL`
- `HIGGS_MASS_REMAINS_OPEN`
- `VEV_REMAINS_OPEN`
- `QUARTIC_REMAINS_OPEN`
- `YUKAWA_MASS_MIXING_REMAINS_OPEN`
- `DOWNSTREAM_SM_DERIVATION_REMAINS_OPEN`
- `BHSM_REPLACEMENT_CLAIM_NOT_READY`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`
