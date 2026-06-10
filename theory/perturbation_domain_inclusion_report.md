# BHSM v2.0 Perturbation Domain Inclusion Report

Status: `PERTURBATION_DOMAIN_INCLUSION_CONDITIONAL`
Theorem complete: `False`
Graph domain status: `GRAPH_NORM_DOMAIN_PROVEN`

| Term | D(A0) included | Open obligations |
| --- | --- | --- |
| `V_Hopf` | `False` | prove q-growth is A0-relative bounded on D(A0) |
| `V_boundary` | `False` | prove Omega_f growth is A0-relative bounded on D(A0) |
| `V_chi` | `True` | none |
| `K_sector` | `False` | upgrade sparse/banded finite-scan evidence to a complete infinite-basis operator bound |
| `P_perp_lift` | `False` | prove formal complement projector preserves D(A0) |
| `PSD_profile` | `True` | none |

## Limitations

- D(A0) is proven, but not every perturbation has proven D(A0) inclusion.

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
