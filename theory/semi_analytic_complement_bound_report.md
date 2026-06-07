# BHSM v1.3N Semi-Analytic Complement-Bound Scaffold

Theorem complete: `False`
Status: `SEMI_ANALYTIC_BOUND_SCAFFOLD_PASSES`

## Protected Kernel

- Formal protected coordinates: `(0, 18, 36)`
- Old coordinate-first block: `(0, 1, 2)`

## First Diagonal Complement Mode

| coordinate | sector | k | j | q | chi | diagonal D | diagonal D^2 | old coordinate-first protected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `1` | `lepton` | `1` | `0` | `1` | `-1` | `-2.6141016151377547` | `6.833527254265818` | `True` |

## Lower-Bound Table

| Bound | Value | Clears required bound |
| --- | --- | --- |
| Required Dirac lower bound | `0.8038064161349437` | `target` |
| Diagonal complement lower bound | `6.833527254265818` | `True` |
| Gershgorin lower bound | `6.721838618515489` | `True` |
| Structured relative lower bound | `6.729508865520464` | `True` |
| Exact finite lower bound | `6.8171156827281205` | `True` |

## Why Old Coordinate-First Lepton Modes Are Not Protected

Coordinates `(1,2)` are lepton-sector complement states in the formal-kernel variant. They are not the sector-labeled heavy `(0,0)` protected states for up and down sectors.

## Limitations

- The bound is semi-analytic inside DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL, not the full twisted Dirac operator.
- Gershgorin and structured-relative estimates remain finite-basis scaffold bounds.
- The full H_T theorem remains open.
