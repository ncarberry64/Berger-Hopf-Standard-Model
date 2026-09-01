# BHSM v1.3N Formal-Kernel Action-Origin Note

BHSM v1.3N derives or constrains the corrected formal-kernel projector from
the existing sector, boundary, parent-action, and basis-ordering scaffolds.
It also builds a semi-analytic complement-bound scaffold for
`DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`.

This phase does not prove the full `H_T` theorem.

## Formal Kernel Coordinates

The formal protected kernel is the sector-labeled heavy-mode triplet:

| sector | mode | chirality | coordinate at `k_max=4` |
| --- | --- | --- | --- |
| lepton | `(0,0)` | `-1` | `0` |
| up | `(0,0)` | `-1` | `18` |
| down | `(0,0)` | `-1` | `36` |

The coordinate formula follows from the finite Level 2 sector-major basis:

```text
coordinate = sector_index * 2*M(k_max)
M(k_max)=sum_{k=0}^{k_max}(floor(k/2)+1)
```

For `k_max=4`, `M=9`, giving `(0,18,36)`.

## Derivation Status

| source layer | status |
| --- | --- |
| sector-labeled protected family kernel | `FORMAL_KERNEL_BOUNDARY_DERIVED` |
| chiral projector channel | `FORMAL_KERNEL_BOUNDARY_DERIVED` |
| v1.2 sector boundary functional | `FORMAL_KERNEL_BOUNDARY_DERIVED` |
| Level 2 coordinate placement | `FORMAL_KERNEL_BASIS_DERIVED` |
| Higgs-selected `U(1)` kernel channel | `FORMAL_KERNEL_IMPLEMENTATION_SCAFFOLD` |

The result is boundary/basis-derived inside the scaffold. It is not yet
`FORMAL_KERNEL_ACTION_DERIVED`.

## Semi-Analytic Complement Bound

After removing the formal protected coordinates `(0,18,36)`, the first
diagonal complement mode is coordinate `1`, a lepton-sector
`(k=1,j=0,q=1,chi=-1)` mode. This is one of the old coordinate-first protected
states, but it is not part of the formal sector-labeled protected kernel.

| bound | value |
| --- | --- |
| required Dirac lower bound | `0.8038064161349437` |
| diagonal complement lower bound | `6.833527254265818` |
| Gershgorin lower bound | `6.721838618515489` |
| structured relative lower bound | `6.729508865520464` |
| exact finite lower bound | `6.8171156827281205` |

The semi-analytic scaffold clears the required bound in the corrected Level 2
formal-kernel model.

## Limitations

- This does not prove the full `H_T` theorem.
- The complete twisted Dirac operator, index theorem, and infinite-basis
  complement split remain open.
- The formal-kernel coordinate tuple is a finite-basis representation of a
  sector-labeled subspace.
- Frozen BHSM v1.0/v1.1 predictions are unchanged.
