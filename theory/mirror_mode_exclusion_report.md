# BHSM v1.3H Mirror-Mode Exclusion Audit

Mirror exclusion status: `OPEN_MIRROR_RISK`
Theorem complete: `False`
Open mirror risk count: `3`

## Mirror Candidates

| ID | Partner | Sector | k | j | q | chirality | present | boundary residual | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `mirror_lepton` | `zero_mode_lepton` | `lepton` | `0` | `0` | `0` | `1` | `True` | `-3` | `OPEN_MIRROR_RISK` |
| `mirror_up` | `zero_mode_up` | `up` | `0` | `0` | `0` | `1` | `True` | `-6` | `OPEN_MIRROR_RISK` |
| `mirror_down` | `zero_mode_down` | `down` | `0` | `0` | `0` | `1` | `True` | `-12` | `OPEN_MIRROR_RISK` |

## Exclusion Criteria

| ID | Status | Statement |
| --- | --- | --- |
| `M1` | `OPEN` | Boundary conditions exclude opposite-chirality zero modes. |
| `M2` | `OPEN` | Weak/chiral projector lifts opposite-chirality mirror candidates. |
| `M3` | `OPEN` | Higgs-selected U(1) phase lifts or forbids mirror candidates. |
| `M4` | `FALSE_FOR_BASELINE` | Mirror candidates are not present in the finite Level 2 basis. |

## Limitations

- Mirror-mode exclusion remains a proof obligation for the complete twisted Dirac operator.
- The current finite scaffold reports mirror risks rather than hiding them.
- No frozen BHSM predictions are changed.
