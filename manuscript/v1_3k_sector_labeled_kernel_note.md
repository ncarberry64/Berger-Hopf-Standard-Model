# BHSM v1.3K Sector-Labeled Protected Kernel Note

Branch: `bhsm-v1.3-ht-spectrum`

Status: development audit

Theorem complete: `False`

## Purpose

BHSM v1.3K audits whether the finite Level 2 protected kernel corresponds to
the formal sector-labeled BHSM zero modes:

```text
zero_mode_lepton, zero_mode_up, zero_mode_down
```

This phase does not change `BHSM_BARE_V1`, `BHSM_DRESSED_V1_CANDIDATE`,
canonical constants, frozen predictions, tolerances, the flavor mode ledger,
public release tags, v1.2 action-origin outputs, or v1.3 state ontology
outputs.

## Old vs Formal Projectors

| Projector | Protected coordinates | Sector distribution |
| --- | --- | --- |
| `P0_coordinate_first` | `(0,1,2)` | `{'lepton': 3}` |
| `P0_formal_sector_labeled` | `(0,18,36)` | `{'lepton': 1, 'up': 1, 'down': 1}` |

The legacy Level 2 scaffold protects the first three finite-basis coordinates,
not the formal sector-labeled lepton/up/down zero-mode triplet.

## Formal Kernel Table

| Formal zero mode | Sector | (k,j,q) | chirality | Coordinate | Present |
| --- | --- | --- | --- | --- | --- |
| `zero_mode_lepton` | `lepton` | `(0,0,0)` | `-1` | `0` | `True` |
| `zero_mode_up` | `up` | `(0,0,0)` | `-1` | `18` | `True` |
| `zero_mode_down` | `down` | `(0,0,0)` | `-1` | `36` | `True` |

## Formal-Projector Gap Recompute

| Quantity | Old coordinate-first projector | Formal sector-labeled projector |
| --- | --- | --- |
| first complement eigenvalue | `1.463040025299567` | near `0` |
| `H_T` gap | `19586.72266333732` | near `0` |
| margin vs `mu_H` | positive | negative |
| passes `mu_H` | `True` | `False` |

Classification:

```text
FORMAL_KERNEL_NOT_PROTECTED
```

The formal protected labels are present in the finite basis, but the current
Level 2 matrix does not protect the formal up/down coordinates. The previous
Level 2 gap does not survive the formal-projector recomputation.

## Claim Boundary

BHSM v1.3K audits whether the finite Level 2 protected kernel corresponds to
the formal sector-labeled BHSM zero modes. If the scaffold protected coordinate
positions rather than formal sector labels, the correction must be reported
and the `H_T` gap recomputed.

This audit does not prove the full `H_T` theorem. It exposes a serious Level 2
kernel-protection blocker to be fixed or replaced by a derived basis
transformation/projection theorem.

## Recommended Next Step

v1.3L should implement a corrected Level 2 operator variant whose protected
zero block is built from formal sector-labeled coordinates `(0,18,36)`, then
rerun the sector-coupling, lower-bound, and convergence audits from that
corrected scaffold.
