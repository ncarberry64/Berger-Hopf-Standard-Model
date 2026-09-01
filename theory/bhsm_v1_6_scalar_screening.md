# BHSM v1.6 Scalar/Topographic Screening Proof Scaffold

Status: `SCREENING_SCAFFOLD_PASSES`
Theorem complete: `False`

## Derivative-Screening Conditions

| ID | Coupling operator | Static long-range force absent | Status |
| --- | --- | --- | --- |
| `DS1` | `L_int ~ (1/M_*) partial_mu phi J^mu_topo` | `True` | `DERIVATIVE_SCREENING_DERIVED` |
| `DS2` | `static limit: partial_mu phi J^mu_topo -> 0 for zero momentum transfer` | `True` | `DERIVATIVE_SCREENING_DERIVED` |

## Curvature-Screening Conditions

| ID | Coupling operator | Curvature source | Flat limit suppresses | Status |
| --- | --- | --- | --- | --- |
| `CS1` | `L_int ~ phi R_topo` | `R_topo = K[rho_Phi] or equivalent topographic curvature scalar` | `True` | `CURVATURE_SCREENING_DERIVED` |
| `CS2` | `local flat limit: R_topo -> 0` | `topographic gradients vanish in the local flat comparison patch` | `True` | `CURVATURE_SCREENING_DERIVED` |

## Matter-Coupling Audit

| Mode | Channel | Direct | Derivative only | Curvature only | Virtual | Heavy | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `higgs_projection` | `HIGGS_PROJECTED_LIGHT_MODE` | `True` | `False` | `False` | `False` | `False` | `SM_HIGGS_ALLOWED` |
| `heavy_scalar_complement` | `HOPF_GAP_LIFTED` | `False` | `False` | `False` | `False` | `True` | `FIFTH_FORCE_EXCLUDED_BY_MASS_GAP` |
| `ht_scalar_complement` | `HT_COMPLEMENT_LIFTED` | `False` | `False` | `False` | `False` | `True` | `FIFTH_FORCE_EXCLUDED_BY_MASS_GAP` |
| `derivative_topographic` | `DERIVATIVE_SCREENED` | `False` | `True` | `False` | `False` | `False` | `DERIVATIVE_SCREENED_NOT_STATIC_MEDIATOR` |
| `curvature_topographic` | `CURVATURE_SCREENED` | `False` | `False` | `True` | `False` | `False` | `CURVATURE_SCREENED_FLAT_LIMIT_SUPPRESSED` |
| `virtual_topographic` | `VIRTUAL_ONLY` | `False` | `False` | `False` | `True` | `False` | `VIRTUAL_ONLY_NOT_ON_SHELL_MEDIATOR` |

## Fifth-Force Exclusion

Excluded modes: `6`
Open scalar risks: `0`
Forbidden unscreened modes in current inventory: `0`

The direct light scalar channel is retained as a falsifier and is not present in the current v1.5 scalar inventory.

## Limitations

- This is not FULL_SCREENING_THEOREM_PROVEN.
- Derivative and curvature screening are sufficient action-level scaffold conditions.
- No frozen BHSM predictions, constants, tolerances, mode ledgers, or dressing rules are changed.
