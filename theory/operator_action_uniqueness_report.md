# BHSM v2.13 Operator Action Ingredient Inventory

Status: `OPERATOR_ACTION_INGREDIENTS_CLOSED`
Theorem complete: `True`
All ingredients classified: `True`

| Ingredient | Status | Forced terms | Evidence |
| --- | --- | --- | --- |
| `berger_hopf_geometry` | `ACTION_DERIVED` | `A0, V_Hopf` | Berger diagonal reference operator and Hopf twist are already represented in the complete-operator package. |
| `sector_boundary_functional` | `ACTION_DERIVED` | `V_boundary` | v1.2/v1.2B/v1.2C derive the omega functional from the symbolic parent boundary scaffold under BHSM axioms. |
| `chirality_projection` | `ACTION_DERIVED` | `V_chi` | Chiral projector channel excludes generated mirror candidates in the scaffold chain. |
| `sector_lepton_up_down_structure` | `ACTION_DERIVED` | `K_sector` | Sector-labeled formal kernel and sector-coupling block are the only allowed lepton/up/down mixing package. |
| `formal_kernel_complement_projector` | `ACTION_DERIVED` | `P_perp_lift` | Formal kernel coordinates are sector-labeled and not coordinate-first. |
| `lift_profile_psd_sector` | `REPRESENTED_BY_EXISTING_TERM` | `P_perp_lift, V_PSD` | PSD/profile and lift terms are represented by existing operator package terms. |
| `topographic_representation` | `AXIOM_DERIVED` | `topographic represented sector` | v2.11/v2.12 close mixed coefficient and bundle-curvature formula gaps with BUNDLE_CONNECTION_SEPARATION_WITH_TOPOGRAPHIC_REPRESENTATION. |
| `local_sm_bundle_separation` | `AXIOM_DERIVED` | `forbid independent free mixed operator terms` | Free mixed coefficients are forbidden because they would alter local SM bundle dynamics. |
| `no_mirror_leakage` | `AXIOM_DERIVED` | `forbid mirror-opening perturbations` | Alternative terms that open mirror leakage are theorem-failing rather than allowed deformations. |
| `coordinate_first_kernel_exclusion` | `ZERO_BY_SYMMETRY` | `force sector-labeled formal kernel` | The old coordinate-first protected block is excluded by formal sector-label alignment. |

## Blocking Ingredients


## Limitations

- The inventory closes the action-origin ingredient list under current BHSM axioms.
- It does not by itself prove the full H_T theorem or authorize final paper preparation.
