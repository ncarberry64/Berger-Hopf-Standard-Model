# BHSM v1.3O Symbolic Formal-Kernel H_T Operator Scaffold

Theorem complete: `False`
Model level: `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`

## Coordinate-Free Operator

`K_formal = span{|ell,0,0,q=0,chi=-1>, |u,0,0,q=0,chi=-1>, |d,0,0,q=0,chi=-1>}`

`H_perp = K_formal^perp`

`D_FK^2 = D_diag^2 + V_Hopf + V_boundary + V_chi + K_sector + P_lift^perp`

## Term Classification

| Term | Expression | Classification | vanishes on K_formal | preserves K_formal | acts only on H_perp | lower-bound method | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `D_diag_squared` | `D_diag^2` | `DIAGONAL_EXACT` | `True` | `True` | `False` | exact diagonal complement minimum after removing K_formal | `SEMI_ANALYTIC_BOUND` |
| `V_Hopf` | `V_Hopf(q)` | `SIGN_INDEFINITE_BOUNDED` | `True` | `True` | `False` | included in semi-analytic diagonal and Gershgorin rows | `SEMI_ANALYTIC_BOUND` |
| `V_boundary` | `V_boundary(Omega_f)` | `SIGN_INDEFINITE_BOUNDED` | `True` | `True` | `False` | included in semi-analytic diagonal and Gershgorin rows | `SEMI_ANALYTIC_BOUND` |
| `V_chi` | `V_chi(chi)` | `SIGN_INDEFINITE_BOUNDED` | `True` | `True` | `False` | included in semi-analytic diagonal and Gershgorin rows | `SEMI_ANALYTIC_BOUND` |
| `K_sector` | `K_sector` | `OFF_DIAGONAL_BOUNDED` | `True` | `True` | `True` | structured relative-bound candidate and finite-basis norm checks | `SEMI_ANALYTIC_BOUND` |
| `P_lift_perp` | `P_lift^perp = mu_H(1-exp(-D_FK^2/Lambda^2)) P_perp` | `PSD_EXACT` | `True` | `True` | `True` | monotone heat-lift lower bound | `SEMI_ANALYTIC_BOUND` |
| `PSD_profile` | `V_profile|H_perp >= 0` | `PSD_EXACT` | `True` | `True` | `True` | PSD nonnegative Weyl contribution | `COORDINATE_FREE_SCAFFOLD` |

## Basis Realization

- Formula: `M(k_max)=sum_{k=0}^{k_max}(floor(k/2)+1); ell=0, u=2M, d=4M`
- Realized coordinates at k_max=4: `(0, 18, 36)`
- Old coordinate-first block: `(0, 1, 2)`
- Matches current corrected operator basis: `True`

## Complement-Bound Statement

| Quantity | Value |
| --- | --- |
| Required Dirac lower bound | `0.8038064161349437` |
| Diagonal complement lower bound | `6.833527254265818` |
| Structured relative lower bound | `6.729508865520464` |
| Exact finite lower bound | `6.8171156827281205` |
| Heat-lift lower bound | `19591.98933512353` |
| Heat gap margin | `6.729508865519165` |
| Clears required Dirac bound | `True` |
| Clears mu_H after heat lift | `True` |

If the coordinate-free K_formal split, semi-analytic complement lower bound, sector-coupling relative bound, and PSD profile condition hold in the full operator, then H_T|H_perp >= mu_H.

## Limitations

- The full operator, index theorem, and infinite-basis complement split remain open.
- Finite-basis evidence is not labeled FULL_OPERATOR_PROVEN.
- Frozen BHSM v1.0/v1.1 predictions are not changed.
- This implication is conditional and scaffold-level.
- The full coordinate-free infinite-basis operator proof remains open.
