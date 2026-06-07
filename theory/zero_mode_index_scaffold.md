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

## v1.3H Diagonal/Mirror Update

v1.3H adds a dedicated diagonal complement lower-bound and mirror-mode audit.
The finite scaffold index remains `3`, but opposite-chirality mirror candidates
are generated explicitly and classified as `OPEN_MIRROR_RISK`. The index status
therefore remains `INDEX_SCAFFOLD`, not `INDEX_THEOREM_PROVEN`.

## v1.3I Mirror-Exclusion Derivation Update

v1.3I audits whether the mirror candidates are excluded by model-internal
structure. The weak chiral projector channel excludes all three generated
opposite-chirality mirror candidates. Higgs-selected `U(1)` phase and
sector-boundary-functional channels remain open rather than forced.

The scaffold index remains `3`, but the full topological index theorem remains
open.

## v1.3J Zero-Mode Alignment Update

v1.3J audits the alignment between the formal protected zero-mode labels and
the finite Level 2 coordinate-protected block. The result is partial:

| Formal label | Matching coordinate | Status |
| --- | --- | --- |
| `zero_mode_lepton` | `0` | `ALIGNED` |
| `zero_mode_up` | `18` | `OPEN_ALIGNMENT_GAP` |
| `zero_mode_down` | `36` | `OPEN_ALIGNMENT_GAP` |

The scaffold index remains `3`, mirror exclusion remains intact, and the
formal/coordinate alignment gap remains open.
