# BHSM v1.3C Structured Sector-Coupling Bound Report

Theorem complete: `False`
Baseline classification: `RELATIVE_BOUND_CANDIDATE`

BHSM v1.3C investigates structured relative bounds for the Level 2 sector-coupling block. It does not prove the full H_T theorem unless the zero-mode/complement and infinite-basis limits are also certified.

## Structural Table

| Rule | Value | Evidence |
| --- | --- | --- |
| `sector_pairs` | `True` | Nonzero sector-pair rules: 6. |
| `preserves_mode_labels` | `True` | Every nonzero Dirac-level sector pair has matching k, j, q, and chirality. |
| `sparse_support` | `0.9670781893` | Dirac-level nonzero entries: 96 of 2916. |
| `zero_mode_vanishes` | `True` | First 3 rows and columns vanish in both Dirac-level and squared perturbation blocks. |
| `banded_support` | `mode-block-banded` | Nonzero entries preserve k, j, and chirality while changing sector. |
| `finite_rank_status` | `finite-basis finite-rank; infinite-basis finite-rank not certified` | Fixed basis size: 54. |

## Sector Selection Rules

| Source | Target | Preserves q | Preserves j | Preserves chirality | Nonzero count | Max coupling |
| --- | --- | --- | --- | --- | --- | --- |
| `down` | `lepton` | `True` | `True` | `True` | `15` | `0.010833333333333334` |
| `down` | `up` | `True` | `True` | `True` | `18` | `0.010454545454545454` |
| `lepton` | `down` | `True` | `True` | `True` | `15` | `0.010833333333333334` |
| `lepton` | `up` | `True` | `True` | `True` | `15` | `0.0105` |
| `up` | `down` | `True` | `True` | `True` | `18` | `0.010454545454545454` |
| `up` | `lepton` | `True` | `True` | `True` | `15` | `0.0105` |

## Block-Wise Norm Table

| Source | Target | Nonzero count | Spectral norm | Row-sum norm | Same sector |
| --- | --- | --- | --- | --- | --- |
| `down` | `down` | `18` | `0.00022413888889616373` | `0.00022413888889616373` | `True` |
| `down` | `lepton` | `15` | `0.12257881944444443` | `0.24515763888888886` | `False` |
| `down` | `up` | `18` | `0.11465309027777776` | `0.22930618055555552` | `False` |
| `lepton` | `down` | `15` | `0.12257881944444443` | `0.24515763888888886` | `False` |
| `lepton` | `lepton` | `15` | `0.0002258680555655701` | `0.0002258680555655701` | `True` |
| `lepton` | `up` | `15` | `0.11661847222222221` | `0.23323694444444443` | `False` |
| `up` | `down` | `18` | `0.11465309027777776` | `0.22930618055555552` | `False` |
| `up` | `lepton` | `15` | `0.11661847222222221` | `0.23323694444444443` | `False` |
| `up` | `up` | `18` | `0.00021954752065767025` | `0.00021954752065767025` | `True` |

## Relative-Bound Certificate

| Quantity | Value |
| --- | --- |
| a_K | `0.015621013485509948` |
| b_K | `0.0` |
| Structured lower bound | `1.4412292741558648` |
| Required Dirac lower bound | `0.8038064161349437` |
| Full finite-basis lower bound | `1.463040025299567` |
| Sufficient | `True` |
| Classification | `RELATIVE_BOUND_CANDIDATE` |

## Robustness Summary

- Cases: `84`
- All structured bounds sufficient: `True`
- All finite-basis cases pass: `True`
- Finite-rank certificate: finite rank at fixed k_max; not finite-rank certified in the infinite-basis limit
- Banded-support certificate: banded after mode-block ordering because nonzero Dirac couplings preserve k, j, q, and chirality
- Compactness diagnostic: relative-bound candidate only; no compactness theorem because baseline coupling does not strongly decay with action
- Decay-fit status: `NO_STRONG_DECAY`

## Limitations

- The structured bound is finite-basis unless made uniform in k_max.
- The full zero-mode/complement proof remains open.
- This audit does not prove the full H_T theorem.
