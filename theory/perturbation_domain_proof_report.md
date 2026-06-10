# BHSM v2.1 Perturbation Common-Domain Proof Scaffold

Status: `COMMON_DOMAIN_EQUALS_DA0_CONDITIONAL`
Theorem complete: `False`
Common domain: `D(A0) cap D(V_Hopf) cap D(V_boundary) cap D(V_chi) cap D(K_sector) cap D(P_perp_lift)`
Graph-norm domain status: `GRAPH_NORM_DOMAIN_PROVEN`
Finite core is common core: `True`
Common domain equals D(A0): `True`

| Term | Preserves graph norm | Maps D(A0) to H | Status | Assumptions |
| --- | --- | --- | --- | --- |
| `V_Hopf` | `True` | `True` | `DA0_DOMAIN_CONDITIONAL` | the q-growth comparison holds for the complete Berger twisted diagonal action |
| `V_boundary` | `True` | `True` | `DA0_DOMAIN_CONDITIONAL` | Omega_f growth remains at most linearly controlled by the complete diagonal action. |
| `V_chi` | `True` | `True` | `DA0_DOMAIN_CONDITIONAL` | chirality remains a bounded involutive/projector label in the complete basis |
| `K_sector` | `True` | `True` | `DA0_DOMAIN_CONDITIONAL` | The complete sector-coupling rule has the same fixed-label sparse support as the formal-kernel scaffold.<br>The sector-coupling weights are uniformly bounded by the stated scaffold weight.<br>The diagonal reference action dominates the fixed-label sector-coupling quadratic form. |
| `P_perp_lift` | `True` | `True` | `DA0_DOMAIN_CONDITIONAL` | the formal complement projector has a bounded infinite-basis limit preserving D(A0) |
| `PSD_profile` | `True` | `True` | `DA0_DOMAIN_CONDITIONAL` | the profile contribution is nonnegative on the formal complement |

## Open Obligations

- upgrade scaffold termwise D(A0) preservation to the complete twisted Dirac/bundle operator
- prove the formal complement projector preserves D(A0) in the infinite-basis limit

## Limitations

- The common domain equals D(A0) under explicit v2.1 scaffold assumptions.
- The equality is not marked proven for the complete operator.
