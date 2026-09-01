# BHSM v2.2 Finite Projector Convergence Report

Status: `FINITE_PROJECTOR_CONVERGENCE_PROVEN`
Theorem complete: `False`
Convergence mode: eventual exact agreement on the three coordinate-free kernel basis vectors; strong convergence on finite-support core
Strong convergence: `True`
Graph-norm convergence: `True`
No coordinate-first artifact: `True`

| k_max | Formal coordinates | Sectors | Coordinate-free agreement | Old coordinate-first used |
| --- | --- | --- | --- | --- |
| `4` | `(0, 30, 60)` | `('lepton', 'up', 'down')` | `True` | `False` |
| `6` | `(0, 56, 112)` | `('lepton', 'up', 'down')` | `True` | `False` |
| `8` | `(0, 90, 180)` | `('lepton', 'up', 'down')` | `True` | `False` |
| `12` | `(0, 182, 364)` | `('lepton', 'up', 'down')` | `True` | `False` |
| `16` | `(0, 306, 612)` | `('lepton', 'up', 'down')` | `True` | `False` |
| `24` | `(0, 650, 1300)` | `('lepton', 'up', 'down')` | `True` | `False` |
| `32` | `(0, 1122, 2244)` | `('lepton', 'up', 'down')` | `True` | `False` |

## Reference Coordinates

- k_max=4 formal coordinates: `(0, 18, 36)`
- rejected old coordinate-first kernel: `(0, 1, 2)`

## Limitations

- Convergence is proven for the nested sector-labeled basis scaffold.
- It does not prove the complete twisted Dirac index theorem.
