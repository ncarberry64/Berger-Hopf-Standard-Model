# BHSM v2.1 Perturbation Domain and Infinite-Bound Note

Status: `HT_THEOREM_CONDITIONAL_ON_COMPLEMENT`
Theorem complete: `False`

BHSM v2.1 addresses the v2.0 perturbation blocker by making the common-domain, symmetry, sector-coupling, Hopf/boundary/chirality, and lift/projector assumptions executable and reportable. The branch does not alter frozen predictions, canonical constants, tolerances, mode ledgers, or the virtual dressing rule.

## Status Table

| Dependency | Status |
| --- | --- |
| Common domain | `COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL` |
| Perturbation symmetry | `PERTURBATION_SYMMETRY_TERMWISE_CONDITIONAL` |
| Sector coupling | `SECTOR_COUPLING_INFINITE_BOUND_CONDITIONAL` |
| Hopf/boundary/chirality | `HOPF_BOUNDARY_CHI_BOUNDS_CONDITIONAL` |
| Lift/projector domain | `LIFT_PROJECTOR_DOMAIN_CONDITIONAL` |
| Relative-bound closure | `RELATIVE_BOUND_CONDITIONAL_WITH_EXPLICIT_ASSUMPTIONS` |
| Kato-Rellich closure | `KATO_RELLICH_CLOSURE_CONDITIONAL` |
| Lower-bound preservation | `LOWER_BOUND_BLOCKED_BY_COMPLEMENT` |
| H_T dependency | `HT_THEOREM_CONDITIONAL_ON_COMPLEMENT` |

## Bound Summary

| Quantity | Value |
| --- | --- |
| total relative a | `0.015621013485509948` |
| total relative b | `1.0` |
| a < 1 | `True` |
| unperturbed lower bound | `6.8171156827281205` |
| degradation estimate | `0.10649025601217732` |
| preserved lower bound | `6.710625426715943` |
| required Dirac lower bound | `0.8038064161349437` |

## Correct Claim

BHSM v2.1 strengthens the perturbation bridge by replacing finite-scan-only sector-coupling evidence with an explicit conditional infinite-basis bound under the formal-kernel scaffold rule. The full H_T theorem remains conditional on formal complement stability and complete-operator identification.

## Limitations

- v2.1 strengthens the perturbation bridge from finite-scan evidence to explicit conditional infinite-basis bounds.
- The full H_T theorem remains conditional on complement stability and complete-operator identification.

## Open Obligations

- prove scaffold domain and symmetry assumptions for the complete twisted Dirac/bundle operator
- derive the sector-coupling sparse bound from the complete infinite-basis action
- prove formal complement stability before using the lower bound as a final H_T theorem
- combine with final index and mirror closure before any full theorem claim
