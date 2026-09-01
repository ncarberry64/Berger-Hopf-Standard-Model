# BHSM v1.3K Protected Kernel Audit

Theorem complete: `False`
Classification: `FORMAL_KERNEL_NOT_PROTECTED`
Alignment gap closes: `False`

## Old vs Formal Projectors

| Projector | Coordinates | Rank | Sector distribution |
| --- | --- | --- | --- |
| `P0_coordinate_first` | `(0, 1, 2)` | `3` | `{'lepton': 3}` |
| `P0_formal_sector_labeled` | `(0, 18, 36)` | `3` | `{'lepton': 1, 'up': 1, 'down': 1}` |

## Formal Kernel Table

| ID | Sector | k | j | q | chi | coordinate | present |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `zero_mode_lepton` | `lepton` | `0` | `0` | `0` | `-1` | `0` | `True` |
| `zero_mode_up` | `up` | `0` | `0` | `0` | `-1` | `18` | `True` |
| `zero_mode_down` | `down` | `0` | `0` | `0` | `-1` | `36` | `True` |

## Gap Recompute

| Quantity | Old coordinate-first | Formal sector-labeled |
| --- | --- | --- |
| first complement eigenvalue | `1.463040025299567` | `6.209787055308341e-15` |
| H_T gap | `19586.72266333732` | `1.5286098598742102e-09` |
| margin vs mu_H | `1.4628370793107024` | `-19585.259826256482` |
| passes | `True` | `False` |

## Limitations

- The formal sector-labeled kernel is present in the finite basis but is not protected by the current Level 2 matrix.
- The full H_T theorem remains open.
- No frozen model output is changed.

## v1.3L Corrected Operator Update

v1.3L introduces `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`, a corrected finite
Level 2 variant whose protected block is the formal sector-labeled kernel
`(0,18,36)` rather than the legacy coordinate-first block `(0,1,2)`.

Under the corrected variant:

| Quantity | Value |
| --- | --- |
| status | `FORMAL_KERNEL_GAP_RESTORED` |
| formal kernel protected | `True` |
| sector coupling vanishes on formal kernel | `True` |
| first complement eigenvalue | `6.8171156827281205` |
| H_T gap | `19592.076941940737` |
| margin vs mu_H | `6.81711568272658` |

The v1.3K failure remains an important audit result for the legacy
coordinate-first scaffold. The v1.3L correction supersedes that scaffold for
future Level 2 formal-kernel `H_T` audits, without changing frozen BHSM
predictions.
