# BHSM v1.3N Formal-Kernel Action-Origin Scaffold

Theorem complete: `False`
Projector derivation status: `FORMAL_KERNEL_BASIS_DERIVED`
Parent-action status: `REDUCED_FROM_PARENT_ACTION`

## Action / Boundary / Basis Rules

| Rule | Status | Source | Statement |
| --- | --- | --- | --- |
| `R1_sector_labeled_kernel` | `FORMAL_KERNEL_BOUNDARY_DERIVED` | zero_mode_index.protected_family_zero_modes | The protected kernel consists of one heavy (0,0) label in each charged sector. |
| `R2_chiral_projector` | `FORMAL_KERNEL_BOUNDARY_DERIVED` | weak/chiral projector scaffold | The protected labels carry the BHSM protected chirality chi=-1. |
| `R3_boundary_functional` | `FORMAL_KERNEL_BOUNDARY_DERIVED` | v1.2 boundary functional and parent-action reduction | The v1.2 sector boundary functional supplies the lepton/up/down sector distinction. |
| `R4_basis_ordering` | `FORMAL_KERNEL_BASIS_DERIVED` | twisted_dirac.build_dirac_basis | The finite Level 2 basis is sector-major, then chirality-major, then (k,j)-ordered. |
| `R5_higgs_u1_phase` | `FORMAL_KERNEL_IMPLEMENTATION_SCAFFOLD` | parent internal-action scaffold | The Higgs-selected U(1) boundary phase participates in selecting the protected chiral boundary channel. |

## Projector Derivation

| Quantity | Value |
| --- | --- |
| Formal protected coordinates | `(0, 18, 36)` |
| Old coordinate-first block | `(0, 1, 2)` |
| Protected sectors | `('lepton', 'up', 'down')` |
| Modes per chirality/sector | `9` |
| Basis formula | `coordinate = sector_index * 2*M(k_max), M(k_max)=sum_{k=0}^{k_max}(floor(k/2)+1)` |
| Projector rank | `3` |
| Idempotent | `True` |

## Theorem Scaffold

If the protected sector labels, chiral boundary channel, v1.2 boundary functional, and Level 2 sector-major basis ordering are admitted, the finite formal-kernel coordinates are (0, 18, 36).

Remaining obligations:
- derive the full protected kernel from the complete twisted Dirac operator
- derive the Higgs-selected U(1) kernel channel spectrally
- prove the infinite-basis complement projector
- prove the full H_T lower bound

## Limitations

- The formal kernel is boundary/basis-derived in this scaffold, not fully action-derived.
- Coordinates are finite-basis implementation labels for sector-labeled states.
- No frozen predictions are changed.
