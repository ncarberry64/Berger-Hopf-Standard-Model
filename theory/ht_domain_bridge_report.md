# BHSM v1.8 H_T Domain Bridge Report

Domain bridge status: `HT_THEOREM_CONDITIONAL_ON_COMPLEMENT`
Theorem complete: `False`
Full H_T theorem status improved: `True`

| Dependency | Status |
| --- | --- |
| Uniform relative bound | `UNIFORM_RELATIVE_BOUND_CONDITIONAL` |
| Self-adjointness | `SELF_ADJOINT_DOMAIN_CONDITIONAL` |
| Formal complement | `FORMAL_COMPLEMENT_CONDITIONAL` |
| Index | `INDEX_THEOREM_OPEN` |
| Diagonal reference | `DIAGONAL_REFERENCE_OPERATOR_PROVEN` |
| Graph-norm domain | `GRAPH_NORM_DOMAIN_PROVEN` |
| Kato-Rellich preconditions | `KATO_RELLICH_PRECONDITIONS_CONDITIONAL` |
| Kato-Rellich closure | `KATO_RELLICH_CLOSURE_CONDITIONAL` |
| Lower-bound preservation | `LOWER_BOUND_BLOCKED_BY_COMPLEMENT` |

## Open Obligations

- prove the q^2/lambda_diag comparison for the complete Berger twisted spectrum
- prove Omega_f growth is relatively bounded by the complete diagonal operator
- prove sparse/banded sector-coupling rule and a_K bound in the complete infinite basis
- prove the complete diagonal Berger/twisted Dirac spectrum and graph-norm closure
- upgrade every finite/scaffold bound to an infinite-basis operator bound
- prove the full operator leaves K_formal and/or H_perp invariant or block-controlled
- prove the diagonal reference operator is essentially self-adjoint on C_fin
- prove perturbations preserve the graph-norm domain
- prove full operator block invariance or controlled off-block coupling
- prove nested finite projectors converge to the coordinate-free formal projector
- derive the topological index of the complete twisted Dirac operator
- prove absence of additional protected kernel states in the complete operator
- prove the formal-kernel/complement split independently of finite truncation
- prove perturbation symmetry on D(A0) for the complete operator
- prove perturbation domain inclusion for Hopf, boundary, sector, lift, and projector terms
- combine the closed reference operator with proven perturbation bounds and complement stability
- prove q-growth is A0-relative bounded on D(A0)
- prove Omega_f growth is A0-relative bounded on D(A0)
- upgrade sparse/banded finite-scan evidence to a complete infinite-basis operator bound
- prove formal complement projector preserves D(A0)
- prove the relative-bound closure without finite-scan assumptions
- prove formal complement stability before applying the bound to H_perp
- combine with index and mirror exclusion before claiming full H_T theorem
- prove perturbation domain inclusion for the complete operator on D(A0)
- prove scaffold domain and symmetry assumptions for the complete twisted Dirac/bundle operator
- derive the sector-coupling sparse bound from the complete infinite-basis action
- prove formal complement stability before using the lower bound as a final H_T theorem
- combine with final index and mirror closure before any full theorem claim

## Limitations

- The H_T theorem is strengthened from a perturbation blocker to a complement-conditional bridge only conditionally.
- Full H_T theorem proof still requires proven self-adjointness, complement stability, index, and mirror closure.

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
