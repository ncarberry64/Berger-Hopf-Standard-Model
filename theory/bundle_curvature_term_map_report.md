# BHSM v2.12 Bundle Curvature Term Map Report

Status: `BUNDLE_CURVATURE_TERM_MAP_CLOSED`
All contributions classified once: `True`
Theorem complete: `True`

| Contribution | Connection piece | Classification | Mapped operator term | R_bundle | New lower-bound term | Limitation |
| --- | --- | --- | --- | --- | --- | --- |
| `diagonal_curvature_contribution` | `[nabla_Berger,nabla_Berger]` | `CURVATURE_REPRESENTED_BY_A0` | `A0` | `False` | `False` | Diagonal curvature is the reference operator package. |
| `hopf_curvature_contribution` | `[nabla_Hopf,nabla_Hopf]` | `CURVATURE_REPRESENTED_BY_V_HOPF` | `V_Hopf` | `False` | `False` | Hopf twist curvature remains in the Hopf operator channel. |
| `fiber_curvature_contribution` | `[nabla_U1/fiber,nabla_U1/fiber]` | `CURVATURE_REPRESENTED_BY_V_HOPF` | `V_Hopf + V_boundary` | `False` | `False` | Higgs-selected U1/fiber curvature is represented by Hopf and boundary terms. |
| `base_curvature_contribution` | `[nabla_base,nabla_base]` | `CURVATURE_REPRESENTED_BY_A0` | `A0 + V_boundary` | `False` | `False` | Base curvature is represented by diagonal/base and boundary bookkeeping. |
| `boundary_curvature_contribution` | `[nabla_boundary,nabla_boundary]` | `CURVATURE_REPRESENTED_BY_V_BOUNDARY` | `V_boundary` | `False` | `False` | Boundary functional curvature is represented by V_boundary. |
| `chirality_curvature_contribution` | `[nabla_chi,nabla_chi]` | `CURVATURE_REPRESENTED_BY_V_CHI` | `V_chi` | `False` | `False` | Chirality contribution is represented by chiral projector terms. |
| `sector_mixing_curvature_contribution` | `[nabla_sector,nabla_sector]` | `CURVATURE_REPRESENTED_BY_K_SECTOR` | `K_sector` | `False` | `False` | Sector coupling is already represented and bounded in the operator package. |
| `higgs_u1_curvature_contribution` | `[nabla_Higgs-U1,nabla_Higgs-U1]` | `CURVATURE_REPRESENTED_BY_V_BOUNDARY` | `V_Hopf + V_boundary` | `False` | `False` | Higgs-U1 curvature remains in Hopf/boundary channels. |
| `lift_profile_curvature_contribution` | `[nabla_lift/profile,nabla_lift/profile]` | `CURVATURE_REPRESENTED_BY_P_PERP_LIFT` | `P_perp_lift + V_PSD` | `False` | `False` | Lift/profile curvature is represented by lift and PSD profile operators. |
| `scalar_topographic_curvature_contribution` | `[nabla_scalar/topographic,nabla_scalar/topographic]` | `CURVATURE_SCREENED_OR_LIFTED` | `scalar/topographic screened sector` | `False` | `False` | Scalar/topographic leakage is screened or lifted by existing scaffold obligations. |
| `mirror_curvature_contribution` | `[nabla_mirror,nabla_mirror]` | `CURVATURE_REPRESENTED_BY_V_CHI` | `V_chi + Higgs-U1 + boundary channels` | `False` | `False` | Mirror curvature is represented by chiral/Higgs-U1/boundary channels; mirror theorem remains downstream. |
| `mixed_curvature_remainder` | `sum_{i<j} [nabla_i,nabla_j] mixed Hopf/base/boundary/coframe` | `CURVATURE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR` | `V_boundary + V_PSD/profile + scalar/topographic screened sector + P_perp_lift` | `False` | `False` | v2.11 forbids an independent mixed coefficient and represents mixed curvature topographically. |

## R_bundle Contributors


## Limitations

- This closes the curvature formula map, not the full H_T theorem.
- Downstream projector, index/mirror, and scalar/topographic theorem dependencies remain separately audited.
