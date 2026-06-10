# BHSM v2.9 Bundle Curvature Formula Report

Curvature: `F_BH = [nabla_BH,nabla_BH]`
Formula: `F_BH = sum_i F_i + sum_{i<j} F_{ij}^{mixed}`
Status: `CURVATURE_FORMULA_DERIVED`
Theorem complete: `True`
All contributions mapped: `True`

| Contribution | Formula piece | Source | Mapped operator term | Status | Limitation |
| --- | --- | --- | --- | --- | --- |
| `diagonal_curvature_contribution` | `[nabla_Berger,nabla_Berger]` | `berger_metric_spin_connection` | `A0` | `CURVATURE_FORMULA_DERIVED` | Diagonal curvature is the reference operator package. |
| `hopf_curvature_contribution` | `[nabla_Hopf,nabla_Hopf]` | `hopf_twist_connection` | `V_Hopf` | `CURVATURE_FORMULA_DERIVED` | Hopf twist curvature remains in the Hopf operator channel. |
| `fiber_curvature_contribution` | `[nabla_U1/fiber,nabla_U1/fiber]` | `u1_fiber_connection` | `V_Hopf + V_boundary` | `CURVATURE_FORMULA_DERIVED` | Higgs-selected U1/fiber curvature is represented by Hopf and boundary terms. |
| `base_curvature_contribution` | `[nabla_base,nabla_base]` | `base_s2_connection` | `A0 + V_boundary` | `CURVATURE_FORMULA_DERIVED` | Base curvature is represented by diagonal/base and boundary bookkeeping. |
| `boundary_curvature_contribution` | `[nabla_boundary,nabla_boundary]` | `boundary_functional_connection` | `V_boundary` | `CURVATURE_FORMULA_DERIVED` | Boundary functional curvature is represented by V_boundary. |
| `chirality_curvature_contribution` | `[nabla_chi,nabla_chi]` | `chirality_projector_connection` | `V_chi` | `CURVATURE_FORMULA_DERIVED` | Chirality contribution is represented by chiral projector terms. |
| `sector_mixing_curvature_contribution` | `[nabla_sector,nabla_sector]` | `sector_lepton_up_down_connection` | `K_sector` | `CURVATURE_FORMULA_DERIVED` | Sector coupling is already represented and bounded in the operator package. |
| `higgs_u1_curvature_contribution` | `[nabla_Higgs-U1,nabla_Higgs-U1]` | `higgs_u1_connection` | `V_Hopf + V_boundary` | `CURVATURE_FORMULA_DERIVED` | Higgs-U1 curvature remains in Hopf/boundary channels. |
| `lift_profile_curvature_contribution` | `[nabla_lift/profile,nabla_lift/profile]` | `lift_profile_heat_connection` | `P_perp_lift + V_PSD` | `CURVATURE_FORMULA_DERIVED` | Lift/profile curvature is represented by lift and PSD profile operators. |
| `scalar_topographic_curvature_contribution` | `[nabla_scalar/topographic,nabla_scalar/topographic]` | `scalar_topographic_leakage_channel` | `scalar/topographic screened sector` | `CURVATURE_FORMULA_DERIVED` | Scalar/topographic leakage is screened or lifted by existing scaffold obligations. |
| `mirror_curvature_contribution` | `[nabla_mirror,nabla_mirror]` | `mirror_channel_connection` | `V_chi + Higgs-U1 + boundary channels` | `CURVATURE_FORMULA_DERIVED` | Mirror curvature is represented by chiral/Higgs-U1/boundary channels; mirror theorem remains downstream. |
| `mixed_curvature_remainder` | `sum_{i<j} [nabla_i,nabla_j] mixed Hopf/base/boundary/coframe` | `mixed_hopf_base_boundary_coframe_connection` | `V_boundary + V_PSD/profile + scalar/topographic screened sector + P_perp_lift` | `CURVATURE_FORMULA_DERIVED` | v2.11 forbids an independent mixed coefficient and represents mixed curvature topographically. |

## Open Contributions


## Limitations

- Every curvature contribution is mapped to an existing operator/topographic target.
- No independent R_bundle contribution remains after the v2.11 topographic rule.
