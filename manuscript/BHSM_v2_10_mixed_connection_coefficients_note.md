# BHSM v2.10 Mixed Connection Coefficients Note

Final result: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
Mixed connection classification: `MIXED_CONNECTION_OPEN`
Coefficient status: `MIXED_COEFFICIENT_OPEN`
Curvature status: `MIXED_CURVATURE_OPEN`
Clifford status: `CLIFFORD_CONTRACTION_OPEN`
Exact missing rule: `MIXED_HOPF_BASE_BOUNDARY_COFRAME_COEFFICIENT_RULE`
Exact remaining gap: `MIXED_CONNECTION_COEFFICIENT_RULE_GAP`
Final paper allowed: `False`

## Objective

BHSM v2.10 audits the missing mixed Hopf/base/boundary/coframe connection coefficients that feed the open Lichnerowicz bundle-curvature remainder.

## Mixed Coefficients

| Coefficient | Status | Symbolic form | Acts on |
| --- | --- | --- | --- |
| `hopf_fiber_base_cross` | `MIXED_COEFFICIENT_OPEN` | `C_HB(q,j) [nabla_H,nabla_B]` | `('Hopf/base/fiber modes', 'H_perp')` |
| `base_boundary_cross` | `MIXED_COEFFICIENT_OPEN` | `C_Bbd(j,Omega_f) [nabla_B,nabla_boundary]` | `('lepton', 'up', 'down', 'boundary functional')` |
| `boundary_coframe_cross` | `MIXED_COEFFICIENT_OPEN` | `C_bdC(Omega_f,cof) [nabla_boundary,nabla_cof]` | `('up', 'down', 'coframe channels')` |
| `hopf_boundary_coframe_mixed` | `MIXED_COEFFICIENT_OPEN` | `C_HbdC(q,Omega_f,cof) mixed triple contraction` | `('charged sectors', 'mirror channels', 'formal kernel')` |
| `chirality_dependence` | `MIXED_COEFFICIENT_OPEN` | `C_chi(chi) mixed chirality sign` | `('chirality', 'mirror channels')` |
| `sector_dependence` | `MIXED_COEFFICIENT_OPEN` | `C_sector(f) mixed sector weight` | `('lepton', 'up', 'down')` |

## Curvature and Clifford Contraction

- mixed curvature status: `MIXED_CURVATURE_OPEN`
- Clifford contraction status: `CLIFFORD_CONTRACTION_OPEN`
- contributes to R_bundle: `True`
- represented by existing terms: `False`

## Bound Status

- a_remainder: `None`
- b_remainder: `None`
- lower-bound recomputed: `False`

## Consequence

- complete bundle curvature decision: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
- complete-operator decision: `STILL_BLOCKED_BY_SINGLE_NAMED_THEOREM_GAP`
- H_T theorem complete: `False`
- BHSM theorem complete: `False`

## Conclusion

BHSM v2.10 does not close the mixed connection. It identifies `MIXED_CONNECTION_COEFFICIENT_RULE_GAP` as the next exact theorem target.

## Limitations

- This note does not alter frozen branches, constants, modes, tolerances, outputs, or virtual dressing.
- This note does not prepare the final paper.
- This note does not claim the full H_T theorem is proven.
