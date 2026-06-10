# BHSM v2.7 Curvature Remainder Audit

Term: `lichnerowicz_bundle_curvature_remainder`
Final classification: `REMAINDER_OPEN`
Exact remaining gap: `BUNDLE_CURVATURE_REMAINDER_FORMULA_AND_BOUND_GAP`
Theorem complete: `False`

| Disposition | Passes | Evidence | Limitation |
| --- | --- | --- | --- |
| `REMAINDER_ZERO` | `False` | No cancellation/trace/projection proof is implemented. | Cannot claim zero from connection-source inventory alone. |
| `REMAINDER_REPRESENTED_BY_EXISTING_TERM` | `False` | Connection-level sources map to existing terms, but the curvature contraction itself is not mapped. | Representation of the connection is weaker than representation of the Lichnerowicz remainder. |
| `REMAINDER_PSD_PROFILE_CONTROLLED` | `False` | No symmetry and PSD proof for R_bundle is present. | The PSD/profile package cannot absorb an unidentified sign-indefinite curvature contraction. |
| `REMAINDER_SCREENED_OR_LIFTED` | `False` | No proof excludes R_bundle from H_perp or lifts it above threshold. | Screening/lifting remains unavailable without its sector/chirality action. |
| `REMAINDER_RELATIVELY_BOUNDED_SAFE` | `False` | No constants a_R,b_R have been derived for ||R_bundle psi|| <= a_R ||A0 psi|| + b_R ||psi||. | Relative-bound closure requires an explicit operator formula or norm estimate. |
| `REMAINDER_REAL_MISSING_TERM` | `False` | The term is not proven nonzero or uncontrolled; only unresolved. | Failure would require showing the term breaks lower-bound transfer. |
| `REMAINDER_OPEN` | `True` | lichnerowicz_bundle_curvature_remainder has no complete formula/action; 4 connection sources retain curvature-remainder risk. | This is an honest theorem gap, not an H_T theorem failure. |

## Limitations

- The audit classifies the remainder exactly once.
- The classification remains OPEN because the complete curvature contraction formula/action is not derived.
