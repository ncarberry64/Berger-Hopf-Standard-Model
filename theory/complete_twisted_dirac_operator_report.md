# BHSM v2.4 Complete Twisted Dirac Operator Identification Report

Status: `COMPLETE_OPERATOR_IDENTIFICATION_PROVEN`
Theorem complete: `True`
Exact complete operator: `True`
Theorem-candidate model: `True`
Formal kernel coordinates: `(0, 18, 36)`
Old coordinate-first kernel used: `False`

| Component | Role | Source status | Status | Limitations |
| --- | --- | --- | --- | --- |
| `A0` | diagonal reference operator D_diag^2 | `DIAGONAL_REFERENCE_OPERATOR_PROVEN` | `COMPONENT_IDENTIFIED` | does not identify all non-diagonal twisted Dirac/bundle terms |
| `V` | Hopf, boundary, chirality, sector-coupling perturbation package | `RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS` | `COMPONENT_IDENTIFIED` | commutator/domain control remains a downstream H_T dependency |
| `K_formal` | corrected sector-labeled formal kernel | `FORMAL_KERNEL_PROJECTOR_PROVEN` | `COMPONENT_IDENTIFIED` | topological index theorem remains separate from coordinate realization |
| `heat_lift_profile` | heat-lift and PSD profile contribution | `LIFT_PROJECTOR_DOMAIN_CONDITIONAL` | `COMPONENT_IDENTIFIED` | full profile positivity belongs to scalar/topographic action closure |

## Open Obligations


## Limitations

- This audit identifies the complete-operator candidate chain without changing frozen predictions.
- v2.13 upgrades only complete-operator identification; H_T commutator/domain/index/mirror gates remain separate.
