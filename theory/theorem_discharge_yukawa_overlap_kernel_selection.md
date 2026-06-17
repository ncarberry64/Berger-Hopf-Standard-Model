# Theorem Discharge: Yukawa Overlap-Kernel Selection

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry. This branch attempts to derive the Yukawa overlap-kernel selection rules and leading texture source from BHSM boundary operator closure, generation mode ledgers, scalar insertion rules, and mode-alignment principles, rather than importing Standard Model Yukawa textures, masses, or mixing values as assumptions. Status labels may be promoted only when the derivation is explicit, deterministic, non-tautological, and does not use known fermion masses or mixing angles as a premise.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers conditionally derived primitive closure, finite boundary algebra, charge/hypercharge operators, anomaly consistency, gauge skeletons, trace normalization, one-loop RG coefficients, the scalar boundary doublet, exactly four renormalizable boundary Yukawa classes, and symbolic 3x3 Yukawa matrix scaffolds.

## 3. Why Overlap-Kernel Selection Is The Next Blocker

The matrix scaffold establishes symbolic entries. This branch classifies which entries are leading self-overlap sources and which require future transport, mixing, or dressing theorem input.

## 4. Four Yukawa Matrix Scaffolds

- `cyclic_upper`
- `cyclic_lower`
- `reference_charged`
- `reference_neutral`

## 5. Mode-Alignment Principle

Generation-aligned pairs `i=j` are leading self-overlap sources. Off-diagonal pairs `i!=j` require additional boundary transport, mixing, or dressing and remain conditional.

## 6. Boundary Kernel Selection Rules

See [Derived Yukawa Overlap Kernel Selection Rules](derived_yukawa_overlap_kernel_selection_rules.md).

## 7. Mode-Distance Scaffold

See [Derived Yukawa Mode Distance Scaffold](derived_yukawa_mode_distance_scaffold.md).

## 8. Leading Diagonal Texture

### cyclic_upper

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | D | O | O |
| 2 | O | D | O |
| 3 | O | O | D |

### cyclic_lower

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | D | O | O |
| 2 | O | D | O |
| 3 | O | O | D |

### reference_charged

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | D | O | O |
| 2 | O | D | O |
| 3 | O | O | D |

### reference_neutral

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | D | O | O |
| 2 | O | D | O |
| 3 | O | O | D |


`D` means `DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE`; `O` means `CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE`.

## 9. Conditional Off-Diagonal Overlap Status

Off-diagonal entries are not set to zero by assumption. They remain conditional symbolic sources for future mixing.

## 10. Forbidden Entries, If Any

No entries are forbidden by the current inherited closure rules once the parent operator class, scalar insertion, and sector ledger are fixed.

## 11. Mass Hierarchy Bridge

```text
m_f,i ~ v/sqrt(2)*N_f*I_f(i,i)
```

This is symbolic only.

## 12. Mixing Source Bridge

```text
V_cyclic=U_cyclic_upper_L^dagger U_cyclic_lower_L
V_reference=U_reference_charged_L^dagger U_reference_neutral_L
```

No CKM or PMNS values are derived.

## 13. What Remains Before Numerical Yukawa Theorem

The numerical boundary overlap kernel theorem remains open.

## 14. Non-Tautology Checks

See [Yukawa Overlap Kernel Non-Tautology Audit](yukawa_overlap_kernel_non_tautology_audit.md).

## 15. Promoted Results, If Any

- `PO_BH_20_YUKAWA_OVERLAP_KERNEL_SELECTION_DERIVED_CONDITIONAL`
- `YUKAWA_MODE_ALIGNMENT_PRINCIPLE_DERIVED_CONDITIONAL`
- `YUKAWA_LEADING_TEXTURE_STATUS_DERIVED_CONDITIONAL`

## 16. Impact On Mass Hierarchy Theorem

The mass hierarchy theorem is narrowed to deriving numerical diagonal kernel values and the sector normalizations.

Follow-up theorem layer: [Theorem discharge: Yukawa distance-to-overlap law](theorem_discharge_yukawa_distance_overlap_law.md) audits candidate maps from mode distance to overlap values. It does not promote a numerical law without a boundary action, Hessian, dressing, or overlap derivation.

Follow-up theorem layer: [Theorem discharge: legacy geometric-overlap bridge](theorem_discharge_legacy_geometric_overlap_bridge.md) conditionally identifies the symbolic overlap kernel with the legacy scalar-topographic internal overlap integral and records the sharp-peak rank guardrail.

## 17. Impact On CKM/PMNS Theorem

Off-diagonal symbolic entries identify where future mixing can enter. No mixing value is derived.

## 18. What This Achieves

This branch conditionally discharges the Yukawa overlap-kernel selection theorem layer. Given the previously derived Yukawa matrix scaffold and generation mode ledgers, diagonal entries are identified as the leading self-overlap sources while off-diagonal entries require an additional boundary transport, mixing, or dressing theorem and remain conditional. The branch derives deterministic mode-distance diagnostics and classifies the texture status of all four Yukawa matrices without assigning numerical Yukawa values or changing frozen predictions. The remaining mass problem is narrowed to deriving the numerical overlap kernel values.

## 19. What Remains Before BHSM Replacement Claim

Replacement readiness remains false until numerical overlap values, mass hierarchy, CKM/PMNS mixing, neutral-sector scales, and the full low-energy Lagrangian theorem are complete.

## Verdict Labels

- `THEOREM_DISCHARGE_YUKAWA_OVERLAP_KERNEL_SELECTION_COMPLETE`
- `PO_BH_20_YUKAWA_OVERLAP_KERNEL_SELECTION_DERIVED_CONDITIONAL`
- `YUKAWA_OVERLAP_KERNEL_SELECTION_RULES_DERIVED_CONDITIONAL`
- `YUKAWA_MODE_ALIGNMENT_PRINCIPLE_DERIVED_CONDITIONAL`
- `YUKAWA_MODE_DISTANCE_SCAFFOLD_DERIVED_CONDITIONAL`
- `YUKAWA_LEADING_TEXTURE_STATUS_DERIVED_CONDITIONAL`
- `YUKAWA_OFF_DIAGONAL_OVERLAP_STATUS_DERIVED_CONDITIONAL`
- `YUKAWA_MASS_HIERARCHY_BRIDGE_DERIVED_CONDITIONAL`
- `YUKAWA_MIXING_SOURCE_BRIDGE_DERIVED_CONDITIONAL`
- `NUMERICAL_OVERLAP_VALUES_REMAIN_OPEN`
- `FERMION_MASS_RATIOS_REMAIN_OPEN`
- `CKM_VALUES_REMAIN_OPEN`
- `PMNS_VALUES_REMAIN_OPEN`
- `DOWNSTREAM_SM_DERIVATION_REMAINS_OPEN`
- `BHSM_REPLACEMENT_CLAIM_NOT_READY`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`
