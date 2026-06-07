# BHSM v1.3J Zero-Mode Alignment Report

Theorem complete: `False`
One-to-one alignment: `False`
Open alignment gap remains: `True`
Mirror exclusion intact: `True`

## Alignment Table

| Formal label | Sector | k | j | q | chi | match index | coordinate protected | heat preserved | sector coupling vanishes | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `zero_mode_lepton` | `lepton` | `0` | `0` | `0` | `-1` | `0` | `True` | `True` | `True` | `ALIGNED` |
| `zero_mode_up` | `up` | `0` | `0` | `0` | `-1` | `18` | `False` | `False` | `False` | `OPEN_ALIGNMENT_GAP` |
| `zero_mode_down` | `down` | `0` | `0` | `0` | `-1` | `36` | `False` | `False` | `False` | `OPEN_ALIGNMENT_GAP` |

## Coordinate-Protected Block

| index | sector | k | j | q | chi | heat preserved | sector coupling vanishes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `0` | `lepton` | `0` | `0` | `0` | `-1` | `True` | `True` |
| `1` | `lepton` | `1` | `0` | `1` | `-1` | `True` | `True` |
| `2` | `lepton` | `2` | `0` | `2` | `-1` | `True` | `True` |

## Criteria

| ID | Passes | Statement |
| --- | --- | --- |
| `A1` | `True` | Exactly three formal protected zero-mode labels are present. |
| `A2` | `True` | Exactly three finite coordinate-protected states are present. |
| `A3` | `True` | Each formal label has a matching sector/chirality coordinate in the finite basis. |
| `A4` | `False` | Each matching coordinate is in the finite protected block and is preserved by heat lift and sector coupling. |

## Limitations

- This audit does not alter the finite Level 2 coordinate ordering or protected block.
- The current scaffold has one exact formal/coordinate alignment and two open alignment gaps.
- The full H_T theorem remains open until the full operator/index/complement split is certified.
