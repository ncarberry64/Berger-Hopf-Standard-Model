# BHSM v1.8 Formal Complement Stability Report

Status: `FORMAL_COMPLEMENT_CONDITIONAL`
Theorem complete: `False`
Old coordinate-first artifact reintroduced: `False`

## Formal Kernel

- `|ell,0,0,q=0,chi=-1>`
- `|u,0,0,q=0,chi=-1>`
- `|d,0,0,q=0,chi=-1>`

## Checks

| Check | Passes | Scope | Open obligations |
| --- | --- | --- | --- |
| `idempotence` | `True` | finite-rank Hilbert-space projection | none |
| `self_adjointness` | `True` | finite-rank orthogonal projection | none |
| `sector_kernel` | `True` | coordinate-free formal label | none |
| `no_coordinate_first` | `True` | explicit rejection | none |
| `operator_invariance` | `False` | conditional complete-operator statement | prove full operator block invariance or controlled off-block coupling |
| `finite_projector_limit` | `False` | conditional nested-basis statement | prove nested finite projectors converge to the coordinate-free formal projector |

## Limitations

- Projection algebra is clean for the finite-rank formal kernel.
- Full operator invariance and finite-projector convergence remain conditional.

## v2.2 Update

- formal_kernel_projector_status: `FORMAL_KERNEL_PROJECTOR_PROVEN`
- formal_complement_projector_status: `FORMAL_COMPLEMENT_PROJECTOR_PROVEN`
- domain_stability_status: `PROJECTOR_DOMAIN_STABILITY_CONDITIONAL`
- finite_projector_convergence_status: `FINITE_PROJECTOR_CONVERGENCE_PROVEN`
- complement_lower_bound_status: `COMPLEMENT_LOWER_BOUND_CONDITIONAL`
- ht_dependency_status: `HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR`
- theorem_complete: `False`
- note: `v2.2 closes projector algebra and finite-projector convergence; full H_T remains conditional on index/mirror and complete-operator domain proof.`
