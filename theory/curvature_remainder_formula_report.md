# BHSM v2.8 Curvature Remainder Formula Report

Term: `lichnerowicz_bundle_curvature_remainder`
Status: `REMAINDER_FORMULA_OPEN`
Theorem complete: `False`

Lichnerowicz identity: `D_BH^2 = nabla_BH^* nabla_BH + scal_BH/4 + c(F_BH)`
Remainder formula: `R_bundle = c(F_BH) - (V_Hopf + V_boundary + V_chi + K_sector + V_PSD represented curvature contractions)`
Exact missing input: `COMPLETE_BHSM_BUNDLE_CONNECTION_CURVATURE_FORMULA_GAP`

| Component | Symbolic term | Represented by | Status | Limitation |
| --- | --- | --- | --- | --- |
| `hopf_curvature_contraction` | `c(F_Hopf)` | `V_Hopf` | `REPRESENTED_SYMBOLICALLY` | Coefficient-level contraction in the complete bundle connection is not derived. |
| `boundary_curvature_contraction` | `c(F_boundary)` | `V_boundary` | `REPRESENTED_SYMBOLICALLY` | Boundary functional curvature is action-linked but not fully action-derived. |
| `chirality_curvature_contraction` | `c(F_chi)` | `V_chi` | `REPRESENTED_SYMBOLICALLY` | Chirality action is scaffold-controlled, not a full curvature theorem. |
| `sector_curvature_contraction` | `c(F_sector)` | `K_sector` | `REPRESENTED_SYMBOLICALLY` | Sector off-diagonal curvature coefficients are not derived from the complete connection. |
| `profile_curvature_contraction` | `c(F_profile)` | `V_PSD` | `CONDITIONAL_PROFILE_REPRESENTATION` | Only safe if the curvature contraction is proven PSD/profile-controlled. |
| `unresolved_mixed_curvature` | `c(F_mixed^BH) - represented contractions` | `not represented` | `OPEN` | The complete mixed bundle-curvature formula/action is not specified. |

## Limitations

- The Lichnerowicz structure is formalized but the complete mixed curvature contraction is not derived.
- No harmless classification follows until the missing connection-curvature formula is supplied.
