# BHSM v1.3J Zero-Mode Alignment Note

Branch: `bhsm-v1.3-ht-spectrum`

Status: development audit

Theorem complete: `False`

## Purpose

BHSM v1.3J audits the alignment between:

1. formal protected zero-mode labels from the index scaffold; and
2. the finite Level 2 coordinate-protected block.

This phase does not change the finite Level 2 operator, frozen predictions,
canonical constants, tolerances, mode ledger, public release tags, v1.2
action-origin outputs, or v1.3 state ontology outputs.

## Formal Protected Labels

| Formal label | Sector | (k,j,q) | chirality | Boundary policy |
| --- | --- | --- | --- | --- |
| `zero_mode_lepton` | `lepton` | `(0,0,0)` | `-1` | heavy mode protected separately |
| `zero_mode_up` | `up` | `(0,0,0)` | `-1` | heavy mode protected separately |
| `zero_mode_down` | `down` | `(0,0,0)` | `-1` | heavy mode protected separately |

## Finite Coordinate-Protected Block

The current finite Level 2 scaffold protects coordinate indices `0`, `1`, and
`2` by construction. These are:

| Coordinate index | Sector | (k,j,q) | chirality | Heat preserved | Sector coupling vanishes |
| --- | --- | --- | --- | --- | --- |
| `0` | `lepton` | `(0,0,0)` | `-1` | `True` | `True` |
| `1` | `lepton` | `(1,0,1)` | `-1` | `True` | `True` |
| `2` | `lepton` | `(2,0,2)` | `-1` | `True` | `True` |

## Alignment Result

| Formal label | Matching coordinate | Coordinate protected | Status |
| --- | --- | --- | --- |
| `zero_mode_lepton` | `0` | `True` | `ALIGNED` |
| `zero_mode_up` | `18` | `False` | `OPEN_ALIGNMENT_GAP` |
| `zero_mode_down` | `36` | `False` | `OPEN_ALIGNMENT_GAP` |

The audit therefore finds:

```text
one_to_one_alignment = False
open_alignment_gap_remains = True
```

Mirror exclusion from v1.3I remains intact:

```text
mirror_exclusion_intact = True
```

## Claim Boundary

BHSM v1.3J audits the alignment between formal protected zero-mode labels and
the finite Level 2 coordinate-protected block. It does not prove the full
`H_T` theorem unless the full operator, index theorem, and infinite-basis
complement split are certified.

## Recommended Next Step

v1.3K should either revise the Level 2 coordinate-protection construction to
protect the formal sector-labeled kernel directly, or derive a change-of-basis
/ projection theorem showing why the current coordinate block represents the
formal three-sector kernel.
