# BHSM v2.6 Operator Missing-Term Audit

Status: `OPERATOR_MISSING_TERM_AUDIT_BLOCKED`
Theorem complete: `False`
Hidden missing terms: `False`
Blocking term: `lichnerowicz_bundle_curvature_remainder`
Unique blocking terms: `('lichnerowicz_bundle_curvature_remainder',)`

| Audit | Candidate contribution | Disposition | Blocking | Evidence |
| --- | --- | --- | --- | --- |
| `connection_curvature_terms` | connection curvature terms | `OPEN` | `True` | no repo proof shows this term vanishes, is PSD/profile, or is represented by A0+V |
| `torsion_like_terms` | torsion-like terms if applicable | `OPEN` | `True` | no repo proof shows this term vanishes, is PSD/profile, or is represented by A0+V |
| `bundle_connection_terms` | bundle connection terms | `REPRESENTED_BY_EXISTING_TERM` | `False` | v2.3 Higgs-U1 mirror channel and boundary/Hopf representation |
| `sector_off_diagonal_terms` | sector off-diagonal terms | `REPRESENTED_BY_EXISTING_TERM` | `False` | v1.3-v2.1 sector coupling bound scaffolds represent this block |
| `mirror_channel_terms` | mirror-channel terms | `REPRESENTED_BY_EXISTING_TERM` | `False` | v2.3 mirror-channel reports account for generated mirror candidates |
| `higgs_u1_terms` | Higgs-U1 terms | `REPRESENTED_BY_EXISTING_TERM` | `False` | v2.3 Higgs-U1 mirror channel and boundary/Hopf representation |
| `boundary_functional_terms` | boundary-functional terms | `DERIVED_AND_INCLUDED` | `False` | v1.2/v2.1 boundary functional represented in perturbation package |
| `topographic_scalar_leakage` | topographic/scalar leakage into H_T | `DERIVED_SCREENED_OR_LIFTED` | `False` | scalar/topographic scaffold screens/lifts non-Higgs modes |
| `projection_lift_terms` | projection/lift terms | `DERIVED_AND_INCLUDED` | `False` | v2.2 complement projector and lift/projector domain scaffold |
| `heat_profile_terms` | heat-kernel/profile terms | `DERIVED_AND_INCLUDED` | `False` | v2.1/v2.4 lift term included |

## Limitations

- The audit does not hide the connection-curvature/torsion-like remainder.
- The first blocking item is treated as the single named theorem gap for the next branch.
