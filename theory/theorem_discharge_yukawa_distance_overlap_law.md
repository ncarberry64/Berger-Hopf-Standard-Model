# Theorem Discharge: Yukawa Distance-To-Overlap Law

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry. This branch attempts to determine whether the already-derived Yukawa mode-distance scaffold can be promoted into a theorem-level boundary distance-to-overlap law. Status labels may be promoted only when the law follows from BHSM boundary action, Hessian, dressing, or overlap machinery and does not use known fermion masses or mixing angles as input.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived the closure spectrum, finite boundary algebra, charge operators, anomaly consistency, gauge skeletons, trace normalization, one-loop RG coefficients, scalar doublet, Yukawa operator closure, symbolic Yukawa matrix scaffolds, and overlap-kernel selection rules.

## 3. Why Distance-To-Overlap Is The Next Blocker

The kernel-selection layer gives exact mode distances and entry statuses. A numerical mass theorem requires a derived map from those distances to overlap values.

## 4. Current Overlap-Kernel Status

The selection-only status is conditionally derived: diagonal entries are leading and off-diagonal entries remain conditional.

## 5. Mode-Distance Diagnostics

The preserved diagnostics are `D_f(i,j)=|q_i-q_j|+|j_i-j_j|` and `D2_f(i,j)=(q_i-q_j)^2+(j_i-j_j)^2`.

## 6. Candidate Distance-To-Overlap Laws

| candidate_law | formula | required_source | status | reason |
| --- | --- | --- | --- | --- |
| exponential_L1 | `I_f(i,j)=A_f exp[-eta_f D_f(i,j)]` | boundary action or transport Hessian deriving eta_f | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | requires derived eta_f and an action-to-overlap theorem |
| gaussian_D2 | `I_f(i,j)=A_f exp[-eta_f D2_f(i,j)]` | quadratic boundary Hessian overlap theorem | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | requires derived quadratic overlap kernel |
| power_dressing | `I_f(i,j)=A_f Z_f^{D_f(i,j)}` | derived sector dressing law | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | requires non-fitted Z_f and exponent theorem |
| boundary_action_hessian | `I_f(i,j) proportional to exp[-Delta S_f(i,j)]` | explicit BHSM boundary action/Hessian difference | `REMAINS_OPEN` | no theorem-derived action difference was found for Yukawa mode-distance overlaps |
| selection_only | `diagonal leading, off-diagonal conditional` | already derived overlap-kernel selection theorem | `DERIVED_CONDITIONAL` | does not assign numerical values |

## 7. Boundary Action/Hessian Audit

See [Derived Yukawa Boundary Action Overlap Audit](derived_yukawa_boundary_action_overlap_audit.md).

## 8. Guardrails Against Fitting

See [Derived Yukawa Overlap Value Guardrails](derived_yukawa_overlap_value_guardrails.md).

## 9. Candidate Law Status Table

| candidate_law | formula | required_source | status | reason |
| --- | --- | --- | --- | --- |
| exponential_L1 | `I_f(i,j)=A_f exp[-eta_f D_f(i,j)]` | boundary action or transport Hessian deriving eta_f | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | requires derived eta_f and an action-to-overlap theorem |
| gaussian_D2 | `I_f(i,j)=A_f exp[-eta_f D2_f(i,j)]` | quadratic boundary Hessian overlap theorem | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | requires derived quadratic overlap kernel |
| power_dressing | `I_f(i,j)=A_f Z_f^{D_f(i,j)}` | derived sector dressing law | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | requires non-fitted Z_f and exponent theorem |
| boundary_action_hessian | `I_f(i,j) proportional to exp[-Delta S_f(i,j)]` | explicit BHSM boundary action/Hessian difference | `REMAINS_OPEN` | no theorem-derived action difference was found for Yukawa mode-distance overlaps |
| selection_only | `diagonal leading, off-diagonal conditional` | already derived overlap-kernel selection theorem | `DERIVED_CONDITIONAL` | does not assign numerical values |

## 10. Numerical Overlap-Value Status

Numerical overlap values are not derived in this branch.

## 11. Impact On Mass Hierarchy Theorem

The hierarchy theorem remains narrowed to deriving a non-fitted numerical kernel `K_f(mode_i, mode_j, H_f)`.

## 12. Impact On CKM/PMNS Theorem

CKM and PMNS values remain open because no numerical off-diagonal kernel values are derived.

## 13. What This Branch Achieves

This branch derives and audits candidate distance-to-overlap laws for the BHSM Yukawa overlap kernel. The existing mode-distance diagnostics provide a deterministic scaffold for future hierarchy and mixing calculations, but no numerical distance-to-overlap law is promoted unless it is derived from existing BHSM boundary action, Hessian, dressing, or overlap machinery. Therefore numerical overlap values, fermion mass ratios, CKM values, and PMNS values remain open.

## 14. What Remains Before Replacement Claim

Replacement readiness remains false until numerical overlap kernels, mass hierarchy, CKM/PMNS mixing, neutral-sector scales, scalar potential numerics, and the full low-energy Lagrangian theorem are complete.

## Verdict Labels

- `PO_BH_21_YUKAWA_DISTANCE_OVERLAP_LAW_PARTIAL`
- `YUKAWA_DISTANCE_DIAGNOSTICS_DERIVED_CONDITIONAL`
- `YUKAWA_DISTANCE_TO_OVERLAP_LAW_STRUCTURALLY_MOTIVATED_NOT_DERIVED`
- `NUMERICAL_OVERLAP_LAW_REMAINS_OPEN`
- `NUMERICAL_OVERLAP_VALUES_REMAIN_OPEN`
- `FERMION_MASS_RATIOS_REMAIN_OPEN`
- `CKM_VALUES_REMAIN_OPEN`
- `PMNS_VALUES_REMAIN_OPEN`
- `DOWNSTREAM_SM_DERIVATION_REMAINS_OPEN`
- `BHSM_REPLACEMENT_CLAIM_NOT_READY`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`
