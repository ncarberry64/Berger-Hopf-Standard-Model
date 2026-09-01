# BHSM v2.2 Complement Lower-Bound Bridge Report

Status: `COMPLEMENT_LOWER_BOUND_CONDITIONAL`
Theorem complete: `False`
Applies to H_perp: `True`

| Dependency | Status/Value |
| --- | --- |
| complement projector | `FORMAL_COMPLEMENT_PROJECTOR_PROVEN` |
| domain stability | `PROJECTOR_DOMAIN_STABILITY_CONDITIONAL` |
| finite-projector convergence | `FINITE_PROJECTOR_CONVERGENCE_PROVEN` |
| v2.1 lower-bound status | `LOWER_BOUND_BLOCKED_BY_COMPLEMENT` |
| preserved lower bound | `6.710625426715943` |
| required Dirac lower bound | `0.8038064161349437` |
| clears threshold | `True` |

## Open Obligations

- upgrade perturbation-domain stability from conditional scaffold control to the complete operator
- prove topological index and mirror exclusion before claiming the full H_T theorem

## Limitations

- The lower bound applies to H_perp conditionally under the v2.2 projector/domain scaffold.
- This does not complete the index or mirror-mode portions of the theorem.

## v2.4 Complete-Operator Domain-Stability Update

- Domain-stability decision: `HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG`
- Lower-bound transfer: `HT_LOWER_BOUND_TRANSFER_CONDITIONAL`
- Theorem complete: `False`

The v2.2 lower-bound bridge remains valid only conditionally under the v2.4 complete-operator domain-stability scaffold. It is not a final H_T theorem.
