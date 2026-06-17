# Derived Yukawa Matrix Scaffold

### Y_cyclic_upper

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | I_cyclic_upper_11 | I_cyclic_upper_12 | I_cyclic_upper_13 |
| 2 | I_cyclic_upper_21 | I_cyclic_upper_22 | I_cyclic_upper_23 |
| 3 | I_cyclic_upper_31 | I_cyclic_upper_32 | I_cyclic_upper_33 |

- operator class: `cyclic_upper_closure`
- scalar insertion: `H`
- neutral vacuum component: `H_zero`
- diagonal entries: `DERIVED_DIAGONAL_SYMBOLIC_OVERLAP`
- off-diagonal entries: `CONDITIONAL_OFF_DIAGONAL_OVERLAP`
- numerical value status: `NUMERICAL_VALUE_NOT_DERIVED`

### Y_cyclic_lower

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | I_cyclic_lower_11 | I_cyclic_lower_12 | I_cyclic_lower_13 |
| 2 | I_cyclic_lower_21 | I_cyclic_lower_22 | I_cyclic_lower_23 |
| 3 | I_cyclic_lower_31 | I_cyclic_lower_32 | I_cyclic_lower_33 |

- operator class: `cyclic_lower_closure`
- scalar insertion: `H_tilde`
- neutral vacuum component: `H_tilde_zero`
- diagonal entries: `DERIVED_DIAGONAL_SYMBOLIC_OVERLAP`
- off-diagonal entries: `CONDITIONAL_OFF_DIAGONAL_OVERLAP`
- numerical value status: `NUMERICAL_VALUE_NOT_DERIVED`

### Y_reference_charged

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | I_reference_charged_11 | I_reference_charged_12 | I_reference_charged_13 |
| 2 | I_reference_charged_21 | I_reference_charged_22 | I_reference_charged_23 |
| 3 | I_reference_charged_31 | I_reference_charged_32 | I_reference_charged_33 |

- operator class: `reference_charged_closure`
- scalar insertion: `H_tilde`
- neutral vacuum component: `H_tilde_zero`
- diagonal entries: `DERIVED_DIAGONAL_SYMBOLIC_OVERLAP`
- off-diagonal entries: `CONDITIONAL_OFF_DIAGONAL_OVERLAP`
- numerical value status: `NUMERICAL_VALUE_NOT_DERIVED`

### Y_reference_neutral

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | I_reference_neutral_11 | I_reference_neutral_12 | I_reference_neutral_13 |
| 2 | I_reference_neutral_21 | I_reference_neutral_22 | I_reference_neutral_23 |
| 3 | I_reference_neutral_31 | I_reference_neutral_32 | I_reference_neutral_33 |

- operator class: `reference_neutral_closure`
- scalar insertion: `H`
- neutral vacuum component: `H_zero`
- diagonal entries: `DERIVED_DIAGONAL_SYMBOLIC_OVERLAP`
- off-diagonal entries: `CONDITIONAL_OFF_DIAGONAL_OVERLAP`
- numerical value status: `NUMERICAL_VALUE_NOT_DERIVED`

Status: `YUKAWA_MATRIX_SCAFFOLD_DERIVED_CONDITIONAL`.

Follow-up: [Theorem discharge: Yukawa overlap-kernel selection](theorem_discharge_yukawa_overlap_kernel_selection.md) classifies each symbolic matrix entry as leading diagonal or conditional off-diagonal without assigning numerical values.

Follow-up: [Theorem discharge: legacy geometric-overlap bridge](theorem_discharge_legacy_geometric_overlap_bridge.md) identifies these symbolic entries with geometric internal overlap integrals, while preserving the guardrail that strict point-sampling alone is rank-limited and cannot supply a full rank-three matrix.
