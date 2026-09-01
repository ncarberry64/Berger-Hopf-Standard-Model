# BHSM v2.8 Curvature Remainder Formula and Bound Note

Final result: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
Final classification: `REMAINDER_OPEN`
Formula status: `REMAINDER_FORMULA_OPEN`
Basis-action status: `REMAINDER_BASIS_ACTION_OPEN`
Kernel-action status: `REMAINDER_KERNEL_COMPLEMENT_OPEN`
Exact remaining gap: `COMPLETE_BHSM_BUNDLE_CONNECTION_CURVATURE_FORMULA_GAP`
Final paper allowed: `False`

## Objective

BHSM v2.8 formalizes the Lichnerowicz formula for the bundle-curvature remainder and audits whether a safe bound/classification follows.

## Formula

`D_BH^2 = nabla_BH^* nabla_BH + scal_BH/4 + c(F_BH)`

`R_bundle = c(F_BH) - (V_Hopf + V_boundary + V_chi + K_sector + V_PSD represented curvature contractions)`

## Formula Components

| Component | Symbolic term | Represented by | Status |
| --- | --- | --- | --- |
| `hopf_curvature_contraction` | `c(F_Hopf)` | `V_Hopf` | `REPRESENTED_SYMBOLICALLY` |
| `boundary_curvature_contraction` | `c(F_boundary)` | `V_boundary` | `REPRESENTED_SYMBOLICALLY` |
| `chirality_curvature_contraction` | `c(F_chi)` | `V_chi` | `REPRESENTED_SYMBOLICALLY` |
| `sector_curvature_contraction` | `c(F_sector)` | `K_sector` | `REPRESENTED_SYMBOLICALLY` |
| `profile_curvature_contraction` | `c(F_profile)` | `V_PSD` | `CONDITIONAL_PROFILE_REPRESENTATION` |
| `unresolved_mixed_curvature` | `c(F_mixed^BH) - represented contractions` | `not represented` | `OPEN` |

## Action and Bound Status

- sector-action status: `REMAINDER_SECTOR_ACTION_OPEN`
- relative-bound status: `REMAINDER_RELATIVE_BOUND_OPEN`
- lower-bound transfer status: `REMAINDER_LOWER_BOUND_TRANSFER_OPEN`
- nonzero remainder included: `False`
- lower-bound recomputed: `False`

## Complete-Operator Consequence

- complete-operator decision: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
- H_T theorem complete: `False`
- BHSM theorem complete: `False`

## Conclusion

BHSM v2.8 does not close the curvature remainder. It identifies `COMPLETE_BHSM_BUNDLE_CONNECTION_CURVATURE_FORMULA_GAP` as the next exact theorem target.

## Limitations

- This note does not alter frozen branches, constants, modes, tolerances, outputs, or virtual dressing.
- This note does not prepare the final paper.
- This note does not claim zero, representation, PSD control, screening/lifting, or relative-bound safety for the remainder.
