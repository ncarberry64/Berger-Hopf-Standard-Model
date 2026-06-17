# Theorem Discharge: Legacy Geometric Overlap Bridge

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry. This branch bridges the legacy scalar-topographic/Berger-sphere Yukawa overlap integral into the current BHSM theorem stack, identifying the BHSM overlap kernel as a geometric internal-mode integral rather than a fitted distance law. Status labels may be promoted only when the bridge is explicit, non-tautological, and does not use measured fermion masses or mixing angles as input.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived boundary closure, finite algebra, charges, gauge skeletons, scalar representation, Yukawa operator closure, symbolic Yukawa matrices, kernel selection, and distance diagnostics.

## 3. PO-BH-21 Result And Why It Was Partial

PO-BH-21 correctly left direct numerical distance-to-overlap laws open. It did not find a theorem-derived map `D_f(i,j) -> I_f(i,j)` that avoids fitted masses or mixing data.

## 4. Legacy Scalar-Topographic Overlap Integral

```text
Y_ij^f = g_f integral Psi_L_i^*(y) Phi(y) Psi_R_j(y) dV_int
```

## 5. Universal Higgs/Topographic Profile

```text
Phi(y)=Phi0 exp[-sigma d_I(y,y0)^2]
```

## 6. Bridge To Current BHSM Notation

```text
I_f(i,j)=integral_{B^3} Psi_A_f_i^*(y) Phi_H_f(y) Psi_S_f_j(y) dV_gamma
```

## 7. Sharp-Peak Sampling Approximation

```text
I_f(i,j) approx Phi0 Psi_A_f_i^*(y0) Psi_S_f_j(y0)
```

## 8. Rank Guardrail For Strict Point Sampling

```text
rank(I)<=1 for strict point-sampling outer-product approximation
```

Strict point sampling gives an outer product and is therefore only a leading focusing term.

## 9. Internal Harmonic Amplitudes And Hierarchies

Hierarchy information may enter through internal mode amplitudes at `y0`, node suppression, anisotropic focusing, finite-width moments, and transport/dressing terms. No numerical amplitudes are computed here.

## 10. Diagonal Leading Overlaps And Off-Diagonal Mixing

The previous leading/conditional texture status is preserved: diagonal entries are leading self-overlaps, while off-diagonal entries remain conditional mixing/transport/dressing sources.

## 11. Reconciliation With Mode-Distance Diagnostics

Distance enters through `d_I(y,y0)` in the universal profile and through eigenfunction shapes. PO-BH-21 remains valid: no direct numerical `D_f(i,j) -> I_f(i,j)` law is promoted.

## 12. Numerical Value Status

Numerical eigenfunction amplitudes and finite-width overlap moments remain open.

## 13. Non-Tautology Checks

See [Legacy Geometric Overlap Non-Tautology Audit](legacy_geometric_overlap_non_tautology_audit.md).

## 14. Promoted Results

| component | statement | status | guardrail |
| --- | --- | --- | --- |
| legacy_integral | `Y_ij^f = g_f integral Psi_L_i^*(y) Phi(y) Psi_R_j(y) dV_int` | `LEGACY_YUKAWA_OVERLAP_INTEGRAL_BRIDGED_CONDITIONAL` | prompt-provided legacy formula; source ingestion remains incomplete |
| bhsm_kernel | `I_f(i,j)=integral_{B^3} Psi_A_f_i^*(y) Phi_H_f(y) Psi_S_f_j(y) dV_gamma` | `BHSM_GEOMETRIC_OVERLAP_KERNEL_DERIVED_CONDITIONAL` | identifies symbolic kernel only |
| universal_profile | `Phi(y)=Phi0 exp[-sigma d_I(y,y0)^2]` | `UNIVERSAL_HIGGS_TOPOGRAPHIC_PROFILE_DERIVED_CONDITIONAL` | universal profile, no flavor/generation fitted widths |
| sharp_peak | `I_f(i,j) approx Phi0 Psi_A_f_i^*(y0) Psi_S_f_j(y0)` | `SHARP_PEAK_Y0_SAMPLING_APPROXIMATION_DERIVED_CONDITIONAL` | leading focusing approximation only |
| rank_guardrail | `rank(I)<=1 for strict point-sampling outer-product approximation` | `SHARP_PEAK_RANK_GUARDRAIL_DERIVED_CONDITIONAL` | strict point sampling cannot by itself produce rank three |

## 15. What Remains Before Numerical Yukawa Theorem

Compute internal eigenfunction amplitudes at `y0` and finite-width overlap moments over the BHSM internal space, without fitting measured masses.

Follow-up theorem layer: [Theorem discharge: finite-width overlap rank](theorem_discharge_finite_width_overlap_rank.md) derives the symbolic finite-width moment scaffold and the rank-three condition, while leaving internal eigenfunction independence open.

Follow-up theorem layer: [Theorem discharge: QJ eigenfunction map](theorem_discharge_qj_eigenfunction_map.md) refines that independence blocker into the missing explicit map from generation labels `(q,j)` to internal Berger/BHSM eigenfunctions.

## 16. What Remains Before Replacement Claim

Replacement readiness remains false until numerical Yukawa couplings, mass hierarchy, CKM/PMNS mixing, neutral-sector scales, and the full low-energy Lagrangian theorem are complete.

## Conclusion

This branch conditionally discharges the legacy geometric-overlap bridge theorem layer. The current BHSM Yukawa kernel I_f(i,j) is identified with the legacy scalar-topographic internal overlap integral over the Berger/internal space. In the sharp-peak limit of the universal Higgs/topographic profile, the kernel reduces to a product of internal mode amplitudes at the distinguished point y0. Because strict point sampling is an outer-product approximation, it supplies a leading focusing term rather than a full rank-three Yukawa matrix by itself. Numerical Yukawa values, fermion mass ratios, CKM values, and PMNS values remain open until the relevant internal eigenfunction amplitudes and finite-width overlap moments are computed without fitting.

## Verdict Labels

- `THEOREM_DISCHARGE_LEGACY_GEOMETRIC_OVERLAP_BRIDGE_COMPLETE`
- `PO_BH_22_LEGACY_GEOMETRIC_OVERLAP_KERNEL_BRIDGED_CONDITIONAL`
- `LEGACY_YUKAWA_OVERLAP_INTEGRAL_BRIDGED_CONDITIONAL`
- `BHSM_GEOMETRIC_OVERLAP_KERNEL_DERIVED_CONDITIONAL`
- `UNIVERSAL_HIGGS_TOPOGRAPHIC_PROFILE_DERIVED_CONDITIONAL`
- `SHARP_PEAK_Y0_SAMPLING_APPROXIMATION_DERIVED_CONDITIONAL`
- `SHARP_PEAK_RANK_GUARDRAIL_DERIVED_CONDITIONAL`
- `INTERNAL_MODE_AMPLITUDE_HIERARCHY_BRIDGE_DERIVED_CONDITIONAL`
- `DISTANCE_OVERLAP_RECONCILIATION_DERIVED_CONDITIONAL`
- `NUMERICAL_EIGENFUNCTION_AMPLITUDES_REMAIN_OPEN`
- `NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN`
- `FERMION_MASS_RATIOS_REMAIN_OPEN`
- `CKM_VALUES_REMAIN_OPEN`
- `PMNS_VALUES_REMAIN_OPEN`
- `BHSM_REPLACEMENT_CLAIM_NOT_READY`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`
