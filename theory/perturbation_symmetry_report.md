# BHSM v2.0 Perturbation Symmetry Report

Status: `PERTURBATION_SYMMETRY_CONDITIONAL`
Theorem complete: `False`
All symmetric on core: `True`
All extend to D(A0): `False`

| Term | Symmetric on core | Extends to D(A0) | Open obligations |
| --- | --- | --- | --- |
| `V_Hopf` | `True` | `False` | prove q-growth is A0-relative bounded on D(A0) |
| `V_boundary` | `True` | `False` | prove Omega_f growth is A0-relative bounded on D(A0) |
| `V_chi` | `True` | `True` | none |
| `K_sector` | `True` | `False` | upgrade sparse/banded finite-scan evidence to a complete infinite-basis operator bound |
| `P_perp_lift` | `True` | `False` | prove formal complement projector preserves D(A0) |
| `PSD_profile` | `True` | `True` | none |

## Limitations

- Core symmetry is stronger than before, but D(A0)-level extension remains conditional for several terms.

## v2.1 Update

- common_domain_status: `COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL`
- perturbation_symmetry_status: `PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL`
- sector_coupling_status: `SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL`
- hopf_boundary_chi_status: `HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL`
- lift_projector_domain_status: `LIFT_PROJECTOR_DOMAIN_CONDITIONAL`
- relative_bound_status: `RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS`
- kato_rellich_status: `KATO_RELLICH_CLOSURE_CONDITIONAL`
- lower_bound_status: `LOWER_BOUND_BLOCKED_BY_COMPLEMENT`
- ht_dependency_status: `HT_THEOREM_CONDITIONAL_ON_COMPLEMENT`
- theorem_complete: `False`
- note: `v2.1 supersedes the finite-scan perturbation blocker with explicit conditional infinite-basis bounds; formal complement stability remains open.`
