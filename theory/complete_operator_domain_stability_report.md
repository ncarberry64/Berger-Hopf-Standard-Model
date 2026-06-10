# BHSM v2.4 Complete-Operator Domain-Stability Report

Status: `HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG`
Theorem complete: `False`

| Dependency | Status |
| --- | --- |
| complete-operator identification | `COMPLETE_OPERATOR_IDENTIFICATION_PROVEN` |
| perturbation domain stability | `PERTURBATION_DOMAIN_STABILITY_CONDITIONAL` |
| projector graph-domain stability | `PROJECTOR_GRAPH_DOMAIN_STABILITY_PROVEN` |
| commutator control | `PROJECTOR_COMMUTATORS_CONTROLLED` |
| lower-bound transfer | `HT_LOWER_BOUND_TRANSFER_CONDITIONAL` |

## Perturbation Terms

| Term | Maps D(A0) to H | Preserves common domain | Status |
| --- | --- | --- | --- |
| `V_Hopf` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |
| `V_boundary` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |
| `V_chi` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |
| `K_sector` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |
| `P_perp_lift` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |
| `PSD_profile` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |

## Open Obligations

- upgrade topological index and mirror exclusion from conditional to proven before claiming final H_T transfer

## Limitations

- v2.4 strengthens the domain-stability bridge to explicit termwise conditional control.
- It does not mark the bridge proven because commutator/domain and index/mirror proofs remain conditional.
