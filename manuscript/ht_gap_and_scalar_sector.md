# H_T Gap and Scalar Sector

## H_T Gap

The frozen repository records the `H_T` sector as a finite-basis proxy audit:

| Quantity | Frozen Output |
| --- | --- |
| Status | `PROXY_AUDIT` |
| Model level | `DIRAC_PROXY_LEVEL_2` |
| First complement eigenvalue | `1.4630400252994733` |
| First `H_T` complement gap | `19586.72266333732` |
| Target | `19585.25982625801` |
| Margin | `1.4628370793107024` |
| Passes proxy target | `True` |

The no-extra-light-state theorem remains open until the full analytic twisted
Dirac `H_T` spectrum replaces the finite-basis proxy scaffold.

## Scalar and Topographic Sector

The scalar/topographic audit is recorded as a finite-basis scaffold:

| Quantity | Frozen Output |
| --- | --- |
| Status | `FINITE_BASIS_SCAFFOLD` |
| Passes scaffold | `True` |
| Light Higgs projection count | `1` |
| Mode count | `6` |

The Standard-Model-equivalent low-energy limit requires exactly one light
Higgs projection and no unscreened light direct-coupled scalar. The repository
currently audits that condition in a scaffold, not as a full action-level
proof.
