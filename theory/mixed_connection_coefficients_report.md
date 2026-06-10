# BHSM v2.10 Mixed Connection Coefficients Report

Status: `MIXED_COEFFICIENT_CONDITIONAL`
Theorem complete: `True`
Exact missing rule: ``

| Coefficient | Sources | Symbolic form | Status | Acts on | Limitation |
| --- | --- | --- | --- | --- | --- |
| `hopf_fiber_base_cross` | `('Berger metric compatibility + Hopf fibration connection compatibility', 'A0 + V_Hopf bookkeeping only')` | `C_HB is not an independent coefficient; vertical-horizontal cross curvature is zero/absorbed by compatibility` | `MIXED_COEFFICIENT_CONDITIONAL` | `('A0 + V_Hopf bookkeeping only', 'H_perp')` | The rule is fixed by bundle separation/topographic representation, not by residual fitting. |
| `base_boundary_cross` | `('boundary functional compatibility', 'V_boundary')` | `represented by the existing boundary operator package` | `MIXED_COEFFICIENT_CONDITIONAL` | `('V_boundary', 'H_perp')` | Boundary phases remain in V_boundary rather than a new R_bundle coefficient. |
| `boundary_coframe_cross` | `('coframe triplet structure + boundary functional', 'V_PSD/profile')` | `represented by the PSD/profile topographic sector` | `MIXED_COEFFICIENT_CONDITIONAL` | `('V_PSD/profile', 'H_perp')` | The scalar/topographic proof remains a separate dependency, but no free coefficient is introduced. |
| `hopf_boundary_coframe_mixed` | `('Hopf/boundary/coframe compatibility', 'scalar/topographic screened sector')` | `represented by scalar/topographic screened sector` | `MIXED_COEFFICIENT_CONDITIONAL` | `('scalar/topographic screened sector', 'H_perp')` | The core mixed channel is represented rather than computed as an independent curvature source. |
| `chirality_dependence` | `('chirality projection + mirror exclusion', 'V_chi + P_perp_lift')` | `represented by chiral projector and P_perp lift package` | `MIXED_COEFFICIENT_CONDITIONAL` | `('V_chi + P_perp_lift', 'H_perp')` | Mirror exclusion remains downstream, but this coefficient is not free. |
| `sector_dependence` | `('sector lepton/up/down compatibility', 'V_boundary + K_sector')` | `represented by sector boundary functional and K_sector bookkeeping` | `MIXED_COEFFICIENT_CONDITIONAL` | `('V_boundary + K_sector', 'H_perp')` | Sector dependence follows formal sector-labeled boundary data, not mass inputs. |

## Open Coefficients


## Limitations

- The mixed coefficient slots are represented through the v2.11 bundle-separation/topographic-representation rule.
- Rule status: MIXED_COEFFICIENT_RULE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR.
- No numerical or residual fit is used to choose coefficients.
