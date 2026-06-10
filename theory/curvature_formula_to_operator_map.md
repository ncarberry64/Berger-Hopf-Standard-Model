# BHSM v2.9 Curvature Formula to Operator Map

All contributions classified: `True`
R_bundle classification: `REMAINDER_REPRESENTED_BY_TOPOGRAPHIC_SECTOR`
Theorem complete: `True`

| Contribution | Mapped to | Classification | Limitation |
| --- | --- | --- | --- |
| `diagonal_curvature_contribution` | `A0` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Diagonal curvature is the reference operator package. |
| `hopf_curvature_contribution` | `V_Hopf` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Hopf twist curvature remains in the Hopf operator channel. |
| `fiber_curvature_contribution` | `V_Hopf + V_boundary` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Higgs-selected U1/fiber curvature is represented by Hopf and boundary terms. |
| `base_curvature_contribution` | `A0 + V_boundary` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Base curvature is represented by diagonal/base and boundary bookkeeping. |
| `boundary_curvature_contribution` | `V_boundary` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Boundary functional curvature is represented by V_boundary. |
| `chirality_curvature_contribution` | `V_chi` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Chirality contribution is represented by chiral projector terms. |
| `sector_mixing_curvature_contribution` | `K_sector` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Sector coupling is already represented and bounded in the operator package. |
| `higgs_u1_curvature_contribution` | `V_Hopf + V_boundary` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Higgs-U1 curvature remains in Hopf/boundary channels. |
| `lift_profile_curvature_contribution` | `P_perp_lift + V_PSD` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Lift/profile curvature is represented by lift and PSD profile operators. |
| `scalar_topographic_curvature_contribution` | `scalar/topographic screened sector` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Scalar/topographic leakage is screened or lifted by existing scaffold obligations. |
| `mirror_curvature_contribution` | `V_chi + Higgs-U1 + boundary channels` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | Mirror curvature is represented by chiral/Higgs-U1/boundary channels; mirror theorem remains downstream. |
| `mixed_curvature_remainder` | `V_boundary + V_PSD/profile + scalar/topographic screened sector + P_perp_lift` | `MAPPED_TO_EXISTING_OPERATOR_PACKAGE` | v2.11 forbids an independent mixed coefficient and represents mixed curvature topographically. |

## R_bundle Rows


## Limitations

- Every curvature contribution is classified.
- The mixed curvature contribution is represented by existing topographic/operator sectors after v2.11.
