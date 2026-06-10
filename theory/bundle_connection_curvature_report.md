# BHSM v2.7 Bundle Connection Curvature Report

All sources inventoried: `True`
Theorem complete: `False`

| Component | Source | Represented term | Curvature status | Remainder risk |
| --- | --- | --- | --- | --- |
| `hopf_fiber_connection` | Hopf fiber covariant derivative | `V_Hopf` | `REPRESENTED_AT_CONNECTION_LEVEL` | curvature contraction not independently closed |
| `higgs_u1_connection` | Higgs-selected U1 boundary phase | `V_Hopf + V_boundary` | `REPRESENTED_AT_CONNECTION_LEVEL` | curvature contraction not independently closed |
| `base_connection` | S2 base angular derivative | `A0 + V_boundary` | `REPRESENTED_AT_CONNECTION_LEVEL` | curvature contraction not independently closed |
| `weak_chirality_connection` | weak/chirality projector channel | `V_chi` | `REPRESENTED_AT_CONNECTION_LEVEL` | mirror leakage remains a theorem dependency |
| `coframe_sector_connection` | quark coframe and sector boundary functional | `K_sector + V_boundary` | `REPRESENTED_AT_CONNECTION_LEVEL` | sector-coupling curvature action is not derived |
| `profile_topographic_connection` | PSD/profile and topographic channel | `V_PSD` | `REPRESENTED_AT_PROFILE_LEVEL` | only safe if the remainder maps to PSD/profile term |

## Unresolved Components

- `hopf_fiber_connection`
- `higgs_u1_connection`
- `base_connection`
- `coframe_sector_connection`

## Limitations

- All known connection sources are inventoried.
- Connection-level representation does not automatically close the Lichnerowicz curvature remainder.
