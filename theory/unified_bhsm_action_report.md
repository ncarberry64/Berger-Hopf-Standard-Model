# BHSM Unified Action Dependency Closure Report

Status: `ACTION_SCAFFOLD_WITH_OPEN_NODES`
Theorem complete: `False`
Hidden circularity detected: `False`
Empirical residual dependency detected: `False`

## Nodes

| Node | Status | Depends on | Open obligations |
| --- | --- | --- | --- |
| `alpha_geometry` | `FROZEN` | `()` | none |
| `overlap_width` | `FROZEN` | `()` | none |
| `omega_f` | `BOUNDARY_FUNCTIONAL_DERIVED` | `()` | derive boundary functional from complete action globally |
| `mode_ledger` | `FROZEN` | `('omega_f',)` | none |
| `ckm_cp` | `FROZEN_SCREEN` | `('mode_ledger', 'alpha_geometry', 'overlap_width')` | derive full flavor matrix from complete action |
| `formal_kernel` | `STRONG_SCAFFOLD` | `('omega_f',)` | prove full topological index theorem |
| `ht_gap` | `STRONG_SCAFFOLD` | `('formal_kernel',)` | prove infinite-basis complement bound<br>prove full operator domain |
| `scalar_topographic` | `STRONG_SCAFFOLD` | `('ht_gap',)` | prove global scalar/topographic action decoupling |
| `virtual_dressing` | `THEOREM_CANDIDATE` | `()` | derive full virtual loop/threshold dressing factor |
| `qcd_rg` | `OPEN` | `()` | supply validated precision-QCD inputs |
| `state_ontology` | `SCAFFOLD` | `()` | connect ontology to complete spectral theorem |

## Gate Statuses

- `ht_gap`: `FORMAL_KERNEL_SCAFFOLD_STRONG`
- `virtual_dressing`: `VIRTUAL_DRESSING_ADOPTION_CANDIDATE`
- `qcd_rg`: `PRECISION_INPUTS_REQUIRED`
- `scalar_topographic`: `SCREENING_SCAFFOLD_PASSES`

## Limitations

- The unified graph is dependency-clean but has open theorem nodes.
- Frozen predictions are not retuned or changed.
