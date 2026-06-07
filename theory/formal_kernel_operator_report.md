# BHSM v1.3L Formal-Kernel Level 2 Operator Variant

Theorem complete: `False`

## Variant Summary

| Quantity | Value |
| --- | --- |
| Old variant | `DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST` |
| New variant | `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL` |
| Old protected coordinates | `(0, 1, 2)` |
| Formal protected coordinates | `(0, 18, 36)` |
| Protected sectors | `('lepton', 'up', 'down')` |
| Projector rank | `3` |
| Projector idempotent | `True` |
| P0 P_perp zero | `True` |
| Matrix symmetric | `True` |
| Heat lift preserves formal kernel | `True` |
| Avoids old lepton-only modes `(1,2)` | `True` |

## Protection Term

`P0_formal_sector_labeled` protects `(0, 18, 36)` with sectors `('lepton', 'up', 'down')`.

## Limitations

- The projection is a corrected Level 2 scaffold term.
- A full action derivation of this projection remains open.
- The corrected finite-basis variant does not prove the full `H_T` theorem.
