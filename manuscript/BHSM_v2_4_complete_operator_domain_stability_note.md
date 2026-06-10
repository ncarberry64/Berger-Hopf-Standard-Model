# BHSM v2.4 Complete-Operator Domain-Stability Note

BHSM v2.4 audits the complete-operator domain-stability blocker for the corrected formal-kernel H_T program. It does not change frozen predictions, canonical constants, tolerances, mode ledgers, virtual dressing, scalar/QCD outputs, or prior release tags.

## Status Summary

| Dependency | Status |
| --- | --- |
| complete-operator identification | `COMPLETE_OPERATOR_IDENTIFICATION_CONDITIONAL` |
| perturbation domain stability | `PERTURBATION_DOMAIN_STABILITY_CONDITIONAL` |
| projector graph-domain stability | `PROJECTOR_GRAPH_DOMAIN_STABILITY_CONDITIONAL` |
| commutator control | `PROJECTOR_COMMUTATORS_CONDITIONAL` |
| lower-bound transfer | `HT_LOWER_BOUND_TRANSFER_CONDITIONAL` |
| H_T dependency | `HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG` |

## Termwise Perturbation Domain Audit

| Term | Maps D(A0) to H | Preserves common domain | Status |
| --- | --- | --- | --- |
| `V_Hopf` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |
| `V_boundary` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |
| `V_chi` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |
| `K_sector` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |
| `P_perp_lift` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |
| `PSD_profile` | `True` | `True` | `PERTURBATION_TERM_DOMAIN_CONDITIONAL` |

## Commutator Audit

| Commutator | Vanishes | Bounded | Relatively bounded | Status |
| --- | --- | --- | --- | --- |
| `[P_perp,A0]` | `True` | `True` | `True` | `COMMUTATOR_CONTROLLED` |
| `[P_perp,V_Hopf]` | `False` | `True` | `True` | `COMMUTATOR_CONDITIONAL` |
| `[P_perp,V_boundary]` | `False` | `True` | `True` | `COMMUTATOR_CONDITIONAL` |
| `[P_perp,V_chi]` | `True` | `True` | `True` | `COMMUTATOR_CONTROLLED` |
| `[P_perp,K_sector]` | `False` | `True` | `True` | `COMMUTATOR_CONDITIONAL` |
| `[P_perp,P_lift+PSD]` | `False` | `True` | `True` | `COMMUTATOR_CONDITIONAL` |

## Correct Claim

The v2.4 bridge advances the domain-stability blocker to `HT_DOMAIN_STABILITY_BRIDGE_CONDITIONAL_STRONG`. This is a strong conditional scaffold, not a completed proof of the full H_T theorem.

## Remaining Obstruction

Complete-operator identification, nonzero projector-perturbation commutator control, projector graph-domain stability, and the topological index/mirror channels must be upgraded from conditional scaffold status to complete-operator proofs before `FULL_HT_THEOREM_PROVEN` or a final paper is allowed.
