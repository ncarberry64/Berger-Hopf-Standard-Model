# BHSM v1.3G Complement Projector Report

Projector status: `COMPLEMENT_PROJECTOR_SCAFFOLD`
Theorem complete: `False`

## Finite-Basis Diagnostics

| Diagnostic | Value |
| --- | --- |
| Model level | `DIRAC_PROXY_LEVEL_2` |
| Basis size | `54` |
| Zero-mode count | `3` |
| P0 idempotent | `True` |
| P_perp idempotent | `True` |
| P0 P_perp = 0 | `True` |
| Sector coupling vanishes on zero block | `True` |
| Heat lift preserves zero modes | `True` |
| Complement excludes zero modes | `True` |
| P0 commutes with sector block | `True` |

## Assumptions

- The finite Level 2 protected coordinate block represents the three protected zero modes.
- The formal sector-labeled kernel and finite coordinate block must be identified in the complete operator.

## Limitations

- Finite-basis projector identities do not prove the infinite-dimensional complement split.
- The full statement H = ker D_twist plus H_perp remains an index/domain proof obligation.
