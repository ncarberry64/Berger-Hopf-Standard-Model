# BHSM v2.9 Curvature Formula to Operator Map

All contributions classified: `True`
R_bundle classification: `REMAINDER_OPEN`
Theorem complete: `False`

| Contribution | Mapped to | Classification | Limitation |
| --- | --- | --- | --- |
| `diagonal_curvature_contribution` | `A0` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Diagonal curvature is represented by the reference operator package. |
| `hopf_curvature_contribution` | `V_Hopf` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Hopf contribution is represented at the symbolic operator level. |
| `fiber_curvature_contribution` | `V_Hopf + V_boundary` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Trace/topological assumptions remain inherited. |
| `base_curvature_contribution` | `A0 + V_boundary` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Mixed base/fiber terms are not included here. |
| `boundary_curvature_contribution` | `V_boundary` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Uses v1.2/v2 boundary functional scaffold. |
| `chirality_curvature_contribution` | `V_chi` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Mixed chirality curvature is handled by the mixed remainder row. |
| `sector_mixing_curvature_contribution` | `K_sector` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Sector curvature is represented but coefficients remain scaffold-level. |
| `higgs_u1_curvature_contribution` | `V_Hopf + V_boundary` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Mirror-channel curvature action remains conditional. |
| `lift_profile_curvature_contribution` | `P_perp_lift + V_PSD` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Safe only when mapped into lift/profile package. |
| `scalar_topographic_curvature_contribution` | `scalar/topographic screened sector` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Full scalar proof remains separate. |
| `mirror_curvature_contribution` | `V_chi + Higgs-U1 + boundary channels` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Complete mirror curvature remains conditional. |
| `mixed_curvature_remainder` | `new R_bundle` | `REMAINDER_OPEN` | The mixed connection coefficients and Clifford contraction are not defined. |

## R_bundle Rows

- `mixed_curvature_remainder`

## Limitations

- Every curvature contribution is classified.
- The mixed curvature contribution maps to new R_bundle and remains open.
