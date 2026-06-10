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
