# BHSM v1.9 Kato-Rellich Precondition Report

Status: `KATO_RELLICH_PRECONDITIONS_CONDITIONAL`
Theorem complete: `False`
Relative-bound value: `0.015621013485509948`
Relative bound below one: `True`

| ID | Status | Passes | Open obligations |
| --- | --- | --- | --- |
| `reference_self_adjointness` | `DIAGONAL_CORE_ESSENTIALLY_SELF_ADJOINT_PROVEN` | `True` | none |
| `graph_domain` | `GRAPH_NORM_DOMAIN_PROVEN` | `True` | none |
| `perturbation_symmetry` | `CONDITIONAL` | `False` | prove perturbation symmetry on D(A0) for the complete operator |
| `relative_bound` | `UNIFORM_RELATIVE_BOUND_CONDITIONAL` | `True` | prove the q^2/lambda_diag comparison for the complete Berger twisted spectrum<br>prove Omega_f growth is relatively bounded by the complete diagonal operator<br>prove sparse/banded sector-coupling rule and a_K bound in the complete infinite basis |
| `domain_inclusion` | `OPEN` | `False` | prove perturbation domain inclusion for Hopf, boundary, sector, lift, and projector terms |
| `lower_bound_preservation` | `CONDITIONAL` | `False` | combine the closed reference operator with proven perturbation bounds and complement stability |

## Limitations

- The diagonal reference operator and graph-norm domain are closed.
- Kato-Rellich closure remains conditional because perturbation symmetry/domain inclusion and complete infinite-basis bounds are not all proven.
