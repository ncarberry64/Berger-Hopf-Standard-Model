# BHSM v1.3G Zero-Mode and Complement-Split Note

Branch: `bhsm-v1.3-ht-spectrum`

Status: development audit

Theorem complete: `False`

## Purpose

BHSM v1.3G formalizes the zero-mode/index and complement-projector scaffold
needed for the `H_T` no-extra-light-state theorem. The target decomposition is:

```text
H = ker(D_twist) direct_sum H_perp
```

with target:

```text
dim ker(D_twist) = 3
Index(D_twist) = 3
```

No frozen BHSM v1.0/v1.1 predictions, canonical constants, tolerances, mode
ledger, public release tags, v1.2 action-origin outputs, v1.3 state ontology
outputs, or v1.3 spectral-bound logic are changed.

## Zero-Mode Inventory

| ID | Sector | k | j | q | chirality | status | mirror status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `zero_mode_lepton` | `lepton` | `0` | `0` | `0` | `-1` | `PROTECTED` | `OPEN` |
| `zero_mode_up` | `up` | `0` | `0` | `0` | `-1` | `PROTECTED` | `OPEN` |
| `zero_mode_down` | `down` | `0` | `0` | `0` | `-1` | `PROTECTED` | `OPEN` |

The scaffold identifies exactly three protected zero-mode candidates. The
absence of opposite-chirality mirror zero modes remains an open proof
obligation, not a completed theorem.

## Index Assumptions

The index scaffold records five assumptions:

| ID | Status | Meaning |
| --- | --- | --- |
| `I1` | `OPEN` | Twisted bundle charge/topological number gives total index three. |
| `I2` | `ACTION_LINKED` | Higgs-selected `U(1)` boundary phase selects the protected chiral kernel. |
| `I3` | `OPEN` | No opposite-chirality mirror zero modes survive. |
| `I4` | `REDUCED_FROM_PARENT_ACTION` | The v1.2 sector boundary functional supplies the full kernel boundary condition. |
| `I5` | `OPEN` | Trace `U(1)` is topological/nondynamical and adds no light gauge zero mode. |

Status: `INDEX_SCAFFOLD`, not `INDEX_THEOREM_PROVEN`.

## Complement Projector Audit

The finite Level 2 projector audit checks:

| Diagnostic | Result |
| --- | --- |
| zero-mode count | `3` |
| `P0^2 = P0` | `True` |
| `P_perp^2 = P_perp` | `True` |
| `P0 P_perp = 0` | `True` |
| sector coupling vanishes on protected zero block | `True` |
| heat lift preserves zero modes | `True` |
| complement lower-bound machinery excludes protected zero modes | `True` |
| `P0` commutes with the finite sector block | `True` |

The finite Level 2 implementation protects a three-dimensional coordinate
block by construction. Identifying that finite coordinate block with the full
sector-labeled `ker(D_twist)` remains part of the open index/domain problem.

## Claim Boundary

BHSM v1.3G formalizes the zero-mode/index and complement-projector scaffold
needed for the `H_T` no-extra-light-state theorem. It does not prove the full index theorem unless the topological and mirror-mode assumptions are derived
from the complete operator.

## Remaining Blockers

- Derive `Index(D_twist)=3` from the full twisted bundle topology.
- Exclude mirror opposite-chirality zero modes from the complete operator.
- Prove the infinite-dimensional complement projector is well-defined and
  compatible with the block decomposition.
- Compute or bound the full twisted Dirac / `H_T` spectrum on `H_perp`.
