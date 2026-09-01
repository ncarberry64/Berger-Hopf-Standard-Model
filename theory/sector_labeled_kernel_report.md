# BHSM v1.3K Sector-Labeled Kernel Report

Theorem complete: `False`

## Formal Protected Kernel

| ID | Sector | k | j | q | chi | Omega | Target | Coordinate | Present |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `zero_mode_lepton` | `lepton` | `0` | `0` | `0` | `-1` | `0` | `3` | `0` | `True` |
| `zero_mode_up` | `up` | `0` | `0` | `0` | `-1` | `0` | `6` | `18` | `True` |
| `zero_mode_down` | `down` | `0` | `0` | `0` | `-1` | `0` | `12` | `36` | `True` |

## Projector Comparison

| Projector | Coordinates | Rank | Idempotent | Orthogonal to complement | Sector distribution |
| --- | --- | --- | --- | --- | --- |
| `P0_coordinate_first` | `(0, 1, 2)` | `3` | `True` | `True` | `{'lepton': 3}` |
| `P0_formal_sector_labeled` | `(0, 18, 36)` | `3` | `True` | `True` | `{'lepton': 1, 'up': 1, 'down': 1}` |

## v1.3L Corrected Operator Update

v1.3L implements `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`, a corrected Level 2
operator variant that protects the formal sector-labeled coordinates
`(0,18,36)` directly. The corrected variant keeps coordinates `(1,2)` in the
complement and protects exactly one lepton, one up, and one down zero-mode
state.

Corrected status: `FORMAL_KERNEL_GAP_RESTORED`.

The corrected finite-basis variant does not prove the full `H_T` theorem.
