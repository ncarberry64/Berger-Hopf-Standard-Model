# BHSM v2.9 Bundle Connection Components Report

All components classified: `True`
Theorem complete: `False`
Exact missing component: `mixed_hopf_base_boundary_coframe_connection`

| Component | Role | Represented by | Status | Curvature contribution | Limitation |
| --- | --- | --- | --- | --- | --- |
| `berger_metric_spin_connection` | Berger metric/spin connection | `A0` | `DERIVED_FROM_EXISTING_BHSM_STRUCTURE` | `diagonal_curvature_contribution` | Does not determine mixed bundle curvature by itself. |
| `hopf_twist_connection` | Hopf twist connection | `V_Hopf` | `REPRESENTED_BY_EXISTING_TERM` | `hopf_curvature_contribution` | Curvature contraction is represented only at the symbolic term level. |
| `u1_fiber_connection` | U1/fiber connection | `V_Hopf + V_boundary` | `REPRESENTED_BY_EXISTING_TERM` | `fiber_curvature_contribution` | Trace/nondynamical assumptions must be retained. |
| `base_s2_connection` | base/S2 connection | `A0 + V_boundary` | `REPRESENTED_BY_EXISTING_TERM` | `base_curvature_contribution` | Complete mixed base/fiber commutators are not derived. |
| `boundary_functional_connection` | boundary functional connection | `V_boundary` | `DERIVED_FROM_EXISTING_BHSM_STRUCTURE` | `boundary_curvature_contribution` | Global derivation from a full action remains a separate limitation. |
| `chirality_projector_connection` | chirality/projector connection | `V_chi` | `REPRESENTED_BY_EXISTING_TERM` | `chirality_curvature_contribution` | Does not prove all mixed curvature contractions preserve chirality. |
| `sector_lepton_up_down_connection` | sector lepton/up/down connection | `K_sector + V_boundary` | `REPRESENTED_BY_EXISTING_TERM` | `sector_mixing_curvature_contribution` | Complete sector curvature coefficients remain symbolic. |
| `higgs_u1_connection` | Higgs-U1 connection | `V_Hopf + V_boundary` | `REPRESENTED_BY_EXISTING_TERM` | `higgs_u1_curvature_contribution` | Standalone curvature action on mirrors remains conditional. |
| `lift_profile_heat_connection` | lift/profile/heat connection | `P_perp_lift + V_PSD` | `SCREENED_OR_LIFTED` | `lift_profile_curvature_contribution` | Only applies once the remainder is mapped into this package. |
| `scalar_topographic_leakage_channel` | scalar/topographic leakage channel | `scalar/topographic screened sector` | `SCREENED_OR_LIFTED` | `scalar_topographic_curvature_contribution` | Full scalar action proof remains separate. |
| `mirror_channel_connection` | mirror channel | `V_chi + Higgs-U1 + boundary channels` | `CONDITIONAL` | `mirror_curvature_contribution` | Complete curvature action on mirror channels is not independently proven. |
| `mixed_hopf_base_boundary_coframe_connection` | mixed Hopf/base/boundary/coframe connection | `not represented` | `MISSING` | `mixed_curvature_remainder` | Single missing connection component blocking the complete curvature formula. |

## Blocking Components

- `mirror_channel_connection`
- `mixed_hopf_base_boundary_coframe_connection`

## Limitations

- Every listed connection component is classified.
- The mixed Hopf/base/boundary/coframe connection remains the first missing geometric input.
