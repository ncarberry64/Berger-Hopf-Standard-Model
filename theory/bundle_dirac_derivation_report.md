# BHSM v2.7 Bundle Dirac Derivation Report

Status: `BUNDLE_DIRAC_DERIVATION_BLOCKED_BY_REMAINDER`
Theorem complete: `False`
Unresolved step: `resolve_lichnerowicz_remainder`

| Step | Output | Status | Limitation |
| --- | --- | --- | --- |
| `square_diagonal_berger_core` | `berger_diagonal_kinetic` | `DERIVED_AND_INCLUDED` | none |
| `include_hopf_boundary_chirality` | `hopf/boundary/chirality package` | `DERIVED_AND_INCLUDED` | none |
| `include_sector_and_lift_profile` | `K_sector + P_perp_lift + V_PSD` | `REPRESENTED_BY_EXISTING_TERM` | none |
| `resolve_lichnerowicz_remainder` | `lichnerowicz_bundle_curvature_remainder` | `OPEN` | No proof currently shows this term vanishes, is represented, or is screened/lifted. |

## Limitations

- The derivation remains symbolic until the bundle-curvature remainder is resolved.
