# Derived Yukawa Leading Texture Status

Status matrices:

### cyclic_upper

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE |
| 2 | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE |
| 3 | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE |

### cyclic_lower

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE |
| 2 | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE |
| 3 | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE |

### reference_charged

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE |
| 2 | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE |
| 3 | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE |

### reference_neutral

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE |
| 2 | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE |
| 3 | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | CONDITIONAL_OFF_DIAGONAL_OVERLAP_SOURCE | DERIVED_LEADING_DIAGONAL_OVERLAP_SOURCE |


Compact matrices:

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


Status: `YUKAWA_LEADING_TEXTURE_STATUS_DERIVED_CONDITIONAL`.

Follow-up: [Theorem discharge: Yukawa distance-to-overlap law](theorem_discharge_yukawa_distance_overlap_law.md) preserves the leading/conditional texture status while leaving numerical overlap values open.

Follow-up: [Theorem discharge: legacy geometric-overlap bridge](theorem_discharge_legacy_geometric_overlap_bridge.md) interprets the leading/conditional entries as internal geometric overlap integrals. The strict sharp-peak contribution remains rank-limited, so full rank and numerical values require finite-width moments or additional derived structure.
