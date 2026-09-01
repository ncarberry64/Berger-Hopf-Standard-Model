# BHSM v2.11 Topographic Representation Rule Report

Axiom status: `BUNDLE_SEPARATION_AXIOM_FORMALIZED`
Status: `TOPOGRAPHIC_REPRESENTATION_RULE_FORMALIZED`
All slots represented or zero: `True`
Theorem complete: `True`

| Slot | Representation | Mapped operator term | Free coefficient forbidden | Contributes to R_bundle | Classification | Limitation |
| --- | --- | --- | --- | --- | --- | --- |
| `hopf_fiber_base_cross` | zero/cancelled by vertical-horizontal compatibility | `A0 + V_Hopf bookkeeping only` | `True` | `False` | `ZERO_BY_COMPATIBILITY` | No independent bundle curvature coefficient is introduced. |
| `base_boundary_cross` | represented by boundary functional sector | `V_boundary` | `True` | `False` | `REPRESENTED_BY_V_BOUNDARY` | The boundary action remains the place where base-node phase enters. |
| `boundary_coframe_cross` | represented by profile/coframe topographic sector | `V_PSD/profile` | `True` | `False` | `REPRESENTED_BY_V_PSD_PROFILE` | Full scalar/topographic proof remains separate from this coefficient rule. |
| `hopf_boundary_coframe_mixed` | represented by scalar/topographic screened sector | `scalar/topographic screened sector` | `True` | `False` | `REPRESENTED_BY_SCALAR_TOPOGRAPHIC_SCREENED_SECTOR` | This classifies the mixed channel as represented rather than free. |
| `chirality_dependence` | represented by chiral projector and lift package | `V_chi + P_perp_lift` | `True` | `False` | `REPRESENTED_BY_P_PERP_LIFT` | Mirror exclusion remains a separate dependency in the full theorem chain. |
| `sector_dependence` | represented by sector boundary functional | `V_boundary + K_sector` | `True` | `False` | `REPRESENTED_BY_V_BOUNDARY` | Sector dependence is not a fitted coefficient; it follows the formal sector-labeled boundary functional. |

## Real Missing Terms


## Limitations

- Representation of the mixed coefficient rule does not by itself prove scalar/topographic decoupling or the full H_T theorem.
- The rule forbids independent fitted mixed coefficients.
