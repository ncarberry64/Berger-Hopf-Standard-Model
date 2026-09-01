# BHSM v2.15 Projector Domain-Invariance Report

Status: `PROJECTOR_DOMAIN_INVARIANCE_PROVEN`
Theorem complete: `True`
P_perp D(A0) subset D(A0): `True`
P_perp D(A0+V) subset D(A0+V): `True`

| Term | Classification | Preserves D(A0+V) | Graph-norm bounded | Lower-bound safe |
| --- | --- | --- | --- | --- |
| `D_diag^2` | `DOMAIN_STABLE_EXACTLY` | `True` | `True` | `True` |
| `V_Hopf` | `DOMAIN_STABLE_BY_COMMUTATOR_CONTROL` | `True` | `True` | `True` |
| `V_boundary` | `DOMAIN_STABLE_BY_COMMUTATOR_CONTROL` | `True` | `True` | `True` |
| `V_chi` | `DOMAIN_STABLE_BY_COMMUTATOR_CONTROL` | `True` | `True` | `True` |
| `K_sector` | `DOMAIN_STABLE_BY_RELATIVE_BOUND` | `True` | `True` | `True` |
| `P_perp_lift` | `DOMAIN_STABLE_EXACTLY` | `True` | `True` | `True` |
| `V_PSD` | `DOMAIN_STABLE_BY_GRAPH_NORM_EQUIVALENCE` | `True` | `True` | `True` |
| `topographic_represented_sector` | `DOMAIN_STABLE_BY_LIFT_SCREENING` | `True` | `True` | `True` |
| `complete_operator_curvature_topographic` | `DOMAIN_STABLE_BY_LIFT_SCREENING` | `True` | `True` | `True` |

## Blocking Terms


## Assumptions

- The v2.15 interacting graph-domain equality D(A0+V)=D(A0) holds.
- The v2.14 termwise commutator classifications cover every complete-operator term.

## Limitations

- This closes projector graph-domain invariance only; it does not close lower-bound transfer or index/mirror theorem gates.
