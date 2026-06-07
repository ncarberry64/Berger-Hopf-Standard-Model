# BHSM v1.3G Zero-Mode Index Scaffold

Index status: `INDEX_SCAFFOLD`
Theorem complete: `False`
Target index: `3`
Target kernel dimension: `3`
Mirror zero-mode status: `OPEN`

## Protected Zero-Mode Candidates

| ID | Sector | k | j | q | chirality | boundary condition | contribution | status | mirror status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `zero_mode_lepton` | `lepton` | `0` | `0` | `0` | `-1` | sector boundary functional for lepton | `1` | `PROTECTED` | `OPEN` |
| `zero_mode_up` | `up` | `0` | `0` | `0` | `-1` | sector boundary functional for up | `1` | `PROTECTED` | `OPEN` |
| `zero_mode_down` | `down` | `0` | `0` | `0` | `-1` | sector boundary functional for down | `1` | `PROTECTED` | `OPEN` |

## Index Assumptions

| ID | Status | Statement |
| --- | --- | --- |
| `I1` | `OPEN` | The twisted bundle charge/topological number gives total index three. |
| `I2` | `ACTION_LINKED` | The Higgs-selected U(1) boundary phase selects the protected chiral kernel. |
| `I3` | `OPEN` | No opposite-chirality mirror zero modes survive in the physical kernel. |
| `I4` | `REDUCED_FROM_PARENT_ACTION` | The v1.2 sector boundary functional is the boundary condition for the full kernel problem. |
| `I5` | `OPEN` | The trace U(1) is topological/nondynamical and does not add a light gauge zero mode. |

## Limitations

- Index(D_twist)=3 is scaffolded, not proven.
- Mirror zero-mode exclusion remains open until derived from the complete operator.
- This module does not change frozen BHSM predictions or branch outputs.
