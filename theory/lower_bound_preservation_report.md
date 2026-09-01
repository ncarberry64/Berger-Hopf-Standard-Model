# BHSM v2.0 Lower-Bound Preservation Report

Status: `LOWER_BOUND_CONDITIONAL`
Theorem complete: `False`
Unperturbed lower bound: `6.8171156827281205`
Perturbation degradation estimate: `0.10649025601217732`
Resulting lower bound: `6.710625426715943`
Required Dirac lower bound: `0.8038064161349437`
Clears threshold: `True`
Applies to formal complement: `False`

## Open Obligations

- prove the relative-bound closure without finite-scan assumptions
- prove formal complement stability before applying the bound to H_perp
- combine with index and mirror exclusion before claiming full H_T theorem

## Limitations

- The numerical lower-bound margin remains favorable, but its theorem use is conditional.

## v2.2 Update

- formal_kernel_projector_status: `FORMAL_KERNEL_PROJECTOR_PROVEN`
- formal_complement_projector_status: `FORMAL_COMPLEMENT_PROJECTOR_PROVEN`
- domain_stability_status: `PROJECTOR_DOMAIN_STABILITY_CONDITIONAL`
- finite_projector_convergence_status: `FINITE_PROJECTOR_CONVERGENCE_PROVEN`
- complement_lower_bound_status: `COMPLEMENT_LOWER_BOUND_CONDITIONAL`
- ht_dependency_status: `HT_THEOREM_CONDITIONAL_ON_INDEX_MIRROR`
- theorem_complete: `False`
- note: `v2.2 closes projector algebra and finite-projector convergence; full H_T remains conditional on index/mirror and complete-operator domain proof.`
