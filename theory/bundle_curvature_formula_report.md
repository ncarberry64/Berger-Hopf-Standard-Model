# BHSM v2.9 Bundle Curvature Formula Report

Curvature: `F_BH = [nabla_BH,nabla_BH]`
Formula: `F_BH = sum_i F_i + sum_{i<j} F_{ij}^{mixed}`
Status: `CURVATURE_FORMULA_CONDITIONAL`
Theorem complete: `False`
All contributions mapped: `True`

| Contribution | Formula piece | Source | Mapped operator term | Status | Limitation |
| --- | --- | --- | --- | --- | --- |
| `diagonal_curvature_contribution` | `[nabla_Berger,nabla_Berger]` | `berger_metric_spin_connection` | `A0` | `CURVATURE_FORMULA_DERIVED` | Diagonal curvature is represented by the reference operator package. |
| `hopf_curvature_contribution` | `[nabla_Hopf,nabla_Hopf]` | `hopf_twist_connection` | `V_Hopf` | `CURVATURE_FORMULA_DERIVED` | Hopf contribution is represented at the symbolic operator level. |
| `fiber_curvature_contribution` | `[nabla_U1/fiber,nabla_U1/fiber]` | `u1_fiber_connection` | `V_Hopf + V_boundary` | `CURVATURE_FORMULA_DERIVED` | Trace/topological assumptions remain inherited. |
| `base_curvature_contribution` | `[nabla_base,nabla_base]` | `base_s2_connection` | `A0 + V_boundary` | `CURVATURE_FORMULA_DERIVED` | Mixed base/fiber terms are not included here. |
| `boundary_curvature_contribution` | `[nabla_boundary,nabla_boundary]` | `boundary_functional_connection` | `V_boundary` | `CURVATURE_FORMULA_DERIVED` | Uses v1.2/v2 boundary functional scaffold. |
| `chirality_curvature_contribution` | `[nabla_chi,nabla_chi]` | `chirality_projector_connection` | `V_chi` | `CURVATURE_FORMULA_DERIVED` | Mixed chirality curvature is handled by the mixed remainder row. |
| `sector_mixing_curvature_contribution` | `[nabla_sector,nabla_sector]` | `sector_lepton_up_down_connection` | `K_sector` | `CURVATURE_FORMULA_CONDITIONAL` | Sector curvature is represented but coefficients remain scaffold-level. |
| `higgs_u1_curvature_contribution` | `[nabla_Higgs-U1,nabla_Higgs-U1]` | `higgs_u1_connection` | `V_Hopf + V_boundary` | `CURVATURE_FORMULA_CONDITIONAL` | Mirror-channel curvature action remains conditional. |
| `lift_profile_curvature_contribution` | `[nabla_lift/profile,nabla_lift/profile]` | `lift_profile_heat_connection` | `P_perp_lift + V_PSD` | `CURVATURE_FORMULA_CONDITIONAL` | Safe only when mapped into lift/profile package. |
| `scalar_topographic_curvature_contribution` | `[nabla_scalar/topographic,nabla_scalar/topographic]` | `scalar_topographic_leakage_channel` | `scalar/topographic screened sector` | `CURVATURE_FORMULA_CONDITIONAL` | Full scalar proof remains separate. |
| `mirror_curvature_contribution` | `[nabla_mirror,nabla_mirror]` | `mirror_channel_connection` | `V_chi + Higgs-U1 + boundary channels` | `CURVATURE_FORMULA_CONDITIONAL` | Complete mirror curvature remains conditional. |
| `mixed_curvature_remainder` | `sum_{i<j} [nabla_i,nabla_j] for mixed Hopf/base/boundary/coframe channels` | `mixed_hopf_base_boundary_coframe_connection` | `V_boundary + V_PSD/profile + scalar/topographic screened sector + P_perp_lift` | `CURVATURE_FORMULA_CONDITIONAL` | v2.11 represents mixed contribution through existing sectors; no independent coefficient remains. |

## Open Contributions


## Limitations

- Every curvature contribution is mapped to an operator target or to new R_bundle.
- The mixed curvature remainder is represented by the v2.11 topographic rule; remaining conditional rows are separate H_T dependencies.
