# BHSM v1.3H Diagonal Complement Lower-Bound Report

Bound status: `FINITE_DIAGONAL_BOUND_PASSES`
Theorem complete: `False`
Formal/coordinate alignment: `OPEN_ALIGNMENT_GAP`

## Bound Summary

| Quantity | Value |
| --- | --- |
| Required Dirac lower bound | `0.8038064161349437` |
| Finite coordinate complement lower bound | `1.4641` |
| Margin | `0.6602935838650562` |
| Passes required bound | `True` |

## First Complement Mode

| basis index | sector | k | j | q | chirality | diagonal D | diagonal D^2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `18` | `up` | `0` | `0` | `0` | `-1` | `-1.21` | `1.4641` |

## First Ten Inventory Rows

| basis index | sector | k | j | q | chi | D^2 | coordinate protected | formal zero candidate | complement included |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0` | `lepton` | `0` | `0` | `0` | `-1` | `0.0` | `True` | `True` | `False` |
| `1` | `lepton` | `1` | `0` | `1` | `-1` | `0.0` | `True` | `False` | `False` |
| `2` | `lepton` | `2` | `0` | `2` | `-1` | `0.0` | `True` | `False` | `False` |
| `18` | `up` | `0` | `0` | `0` | `-1` | `1.4641` | `False` | `True` | `True` |
| `36` | `down` | `0` | `0` | `0` | `-1` | `2.102499999999999` | `False` | `True` | `True` |
| `19` | `up` | `1` | `0` | `1` | `-1` | `7.044255383476838` | `False` | `False` | `True` |
| `45` | `down` | `0` | `0` | `0` | `1` | `7.2360999999999995` | `False` | `False` | `True` |
| `37` | `down` | `1` | `0` | `1` | `-1` | `8.37582415874296` | `False` | `False` | `True` |
| `27` | `up` | `0` | `0` | `0` | `1` | `8.584899999999998` | `False` | `False` | `True` |
| `9` | `lepton` | `0` | `0` | `0` | `1` | `9.302499999999998` | `False` | `False` | `True` |

## Limitations

- The finite diagonal lower bound is not the full infinite-basis bound.
- Formal zero-mode labels are not yet proven identical to the finite coordinate protected block.
- The complete twisted Dirac operator may modify the diagonal spectrum.

## v1.3K Sector-Labeled Kernel Update

The v1.3H diagonal bound used the legacy coordinate-first protected block.
v1.3K recomputes the gap using the formal sector-labeled projector
`(0,18,36)` and finds that the formal projector does not preserve the old
Level 2 gap. The diagonal complement bound must therefore be rebuilt after a
corrected formal-kernel Level 2 operator is implemented.
