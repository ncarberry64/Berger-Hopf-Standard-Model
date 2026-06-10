# BHSM v2.0 Kato-Rellich Perturbation Closure Report

Status: `KATO_RELLICH_CLOSURE_CONDITIONAL`
Theorem complete: `False`
Can apply Kato-Rellich: `False`

| Precondition | Status |
| --- | --- |
| reference self-adjointness | `DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN` |
| graph domain | `GRAPH_NORM_DOMAIN_PROVEN` |
| perturbation symmetry | `PERTURBATION_SYMMETRY_CONDITIONAL` |
| perturbation domain | `PERTURBATION_DOMAIN_INCLUSION_CONDITIONAL` |
| relative bound | `RELATIVE_BOUND_CONDITIONAL` |
| lower bound | `LOWER_BOUND_CONDITIONAL` |

## Open Obligations

- prove q-growth is A0-relative bounded on D(A0)
- prove Omega_f growth is A0-relative bounded on D(A0)
- upgrade sparse/banded finite-scan evidence to a complete infinite-basis operator bound
- prove formal complement projector preserves D(A0)
- prove the relative-bound closure without finite-scan assumptions
- prove formal complement stability before applying the bound to H_perp
- combine with index and mirror exclusion before claiming full H_T theorem
- prove perturbation domain inclusion for the complete operator on D(A0)

## Limitations

- The reference operator is closed, but perturbation symmetry/domain inclusion and full relative-bound closure remain conditional.
- Kato-Rellich closure is therefore not complete.
