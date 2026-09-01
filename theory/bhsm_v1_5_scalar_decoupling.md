# BHSM v1.5 Scalar/Topographic Decoupling Scaffold

Theorem complete: `False`
Status: `SCALAR_DECOUPLING_SCAFFOLD_PASSES`
Hopf gap: `9720.362165098726`

## Sufficient Conditions

| ID | Status | Statement |
| --- | --- | --- |
| `SD1` | `FINITE_BASIS_VERIFIED` | Exactly one light Higgs projection is allowed. |
| `SD2` | `SCAFFOLD_VERIFIED` | Every orthogonal scalar is heavy, derivative-filtered, curvature-filtered, or screened. |
| `SD3` | `STATE_ONTOLOGY_LINKED` | A screened scalar/topographic mode is not a new on-shell light particle. |
| `SD4` | `FALSIFIER_RULE` | Any unscreened direct-coupled light scalar is a falsifier or open scalar risk. |

## Current Scalar Inventory

| Mode | Category | Status | Light | Allowed | Conditional |
| --- | --- | --- | --- | --- | --- |
| `phi_0` | `SM_HIGGS_PROJECTION` | `light_higgs_projection` | `True` | `True` | `False` |
| `phi_1` | `HEAVY_LIFTED_SCALAR` | `heavy_orthogonal` | `False` | `True` | `False` |
| `phi_2` | `DERIVATIVE_SCREENED_TOPOGRAPHIC_MODE` | `conditional_derivative_filtered` | `True` | `True` | `True` |
| `phi_3` | `CURVATURE_FILTERED_MODE` | `conditional_curvature_filtered` | `True` | `True` | `True` |
| `phi_4` | `SCREENED_TOPOGRAPHIC_MODE` | `conditional_screened` | `True` | `True` | `True` |
| `phi_5` | `HEAVY_LIFTED_SCALAR` | `heavy_orthogonal` | `False` | `True` | `False` |

## Scalar Risk Assessment

Forbidden/open current modes: `0`

A screened scalar/topographic mode is treated as a conditional screened state, not a new on-shell light particle. An unscreened direct-coupled light scalar is a falsifier/open risk.

## Limitations

- Full scalar/topographic decoupling from the action remains open.
- Conditional filtered/screened modes are scaffold-audited, not fully proven safe.
- No frozen BHSM predictions are changed.
