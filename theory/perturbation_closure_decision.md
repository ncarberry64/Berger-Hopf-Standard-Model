# BHSM v2.1 Perturbation Closure Decision

H_T dependency status: `HT_THEOREM_CONDITIONAL_ON_COMPLEMENT`
Theorem complete: `False`

| Dependency | Status |
| --- | --- |
| reference self-adjointness | `DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN` |
| graph-norm domain | `GRAPH_NORM_DOMAIN_PROVEN` |
| common domain | `COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL` |
| perturbation symmetry | `PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL` |
| sector coupling | `SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL` |
| Hopf/boundary/chirality | `HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL` |
| lift/projector domain | `LIFT_PROJECTOR_DOMAIN_CONDITIONAL` |
| relative-bound closure | `RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS` |
| Kato-Rellich closure | `KATO_RELLICH_CLOSURE_CONDITIONAL` |
| lower-bound preservation | `LOWER_BOUND_BLOCKED_BY_COMPLEMENT` |

| Bound quantity | Value |
| --- | --- |
| total a | `0.015621013485509948` |
| total b | `1.0` |
| a < 1 | `True` |
| unperturbed lower bound | `6.8171156827281205` |
| degradation estimate | `0.10649025601217732` |
| preserved lower bound | `6.710625426715943` |
| required Dirac lower bound | `0.8038064161349437` |

## Open Obligations

- prove scaffold domain and symmetry assumptions for the complete twisted Dirac/bundle operator
- derive the sector-coupling sparse bound from the complete infinite-basis action
- prove formal complement stability before using the lower bound as a final H_T theorem
- combine with final index and mirror closure before any full theorem claim

## Limitations

- v2.1 strengthens the perturbation bridge from finite-scan evidence to explicit conditional infinite-basis bounds.
- The full H_T theorem remains conditional on complement stability and complete-operator identification.
