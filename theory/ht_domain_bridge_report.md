# BHSM v1.8 H_T Domain Bridge Report

Domain bridge status: `HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR`
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
- prove topological index theorem for the complete twisted Dirac operator
- exclude mirror zero modes in the complete chiral operator
- upgrade conditional perturbation-domain stability to complete-operator proof

## Limitations

- The H_T theorem is strengthened from a perturbation blocker to a complement-conditional bridge only conditionally.
- Full H_T theorem proof still requires proven self-adjointness, complement stability, index, and mirror closure.

## v2.2 Update

- formal_kernel_projector_status: `FORMAL_KERNEL_PROJECTOR_PROVEN`
- formal_complement_projector_status: `FORMAL_COMPLEMENT_PROJECTOR_PROVEN`
- domain_stability_status: `PROJECTOR_DOMAIN_STABILITY_CONDITIONAL`
- finite_projector_convergence_status: `FINITE_PROJECTOR_CONVERGENCE_PROVEN`
- complement_lower_bound_status: `COMPLEMENT_LOWER_BOUND_CONDITIONAL`
- ht_dependency_status: `HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR`
- theorem_complete: `False`
- note: `v2.2 closes projector algebra and finite-projector convergence; full H_T remains conditional on index/mirror and complete-operator domain proof.`
