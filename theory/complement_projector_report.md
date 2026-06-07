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

## v1.3H Diagonal/Mirror Update

v1.3H separates the finite diagonal complement lower bound from mirror-mode
exclusion. The finite coordinate-complement diagonal lower bound is `1.4641`,
which clears `d_required = 0.8038064161349437`. The full theorem remains open
because formal/coordinate zero-mode alignment and mirror-mode exclusion are not
proven in the complete operator.

## v1.3J Zero-Mode Alignment Update

v1.3J confirms that the finite coordinate-protected block contains three
coordinates, but they are not identical to the three formal sector-labeled
zero-mode candidates. The lepton formal label aligns with coordinate `0`;
the up and down formal labels match finite basis coordinates `18` and `36`,
which are not in the coordinate-protected block. The complement-projector
status therefore remains a scaffold.

## v1.3K Sector-Labeled Kernel Update

v1.3K builds the formal projector from coordinates `(0,18,36)` and recomputes
the complement gap. The formal projector is idempotent, but the formal up/down
coordinates are not zero-protected by the current Level 2 operator and sector
coupling does not vanish on the formal kernel. The previous coordinate-first
gap does not survive this recomputation.
