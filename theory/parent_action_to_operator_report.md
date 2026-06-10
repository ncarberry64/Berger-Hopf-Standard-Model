# BHSM v2.13 Parent Action to Operator Report

Status: `OPERATOR_DERIVED_FROM_ACTION`
Theorem complete: `True`
Parent action symbol: `S_BHSM -> A0 + V`

| Action input | Reduction | Operator term | Status |
| --- | --- | --- | --- |
| `Berger/Hopf kinetic action` | square/reduce the diagonal internal Dirac core | `A0 = D_diag^2` | `ACTION_REDUCES_TO_OPERATOR_TERM` |
| `Hopf fiber covariant derivative` | fiber phase reduction | `V_Hopf` | `ACTION_REDUCES_TO_OPERATOR_TERM` |
| `sector boundary functional` | boundary variation and omega functional | `V_boundary` | `ACTION_REDUCES_TO_OPERATOR_TERM` |
| `weak chirality projector` | left/right projector reduction | `V_chi` | `ACTION_REDUCES_TO_OPERATOR_TERM` |
| `lepton/up/down sector structure` | sector-preserving plus bounded off-diagonal sector reduction | `K_sector` | `ACTION_REDUCES_TO_OPERATOR_TERM` |
| `formal kernel/complement projector` | protect formal kernel and lift complement | `P_perp_lift` | `ACTION_REDUCES_TO_OPERATOR_TERM` |
| `lift/profile/PSD sector` | positive profile variation | `V_PSD` | `REPRESENTED_BY_EXISTING_OPERATOR_TERM` |
| `topographic representation sector` | mixed curvature representation rather than free coefficient | `topographic represented sector` | `AXIOM_REDUCES_TO_EXISTING_PACKAGE` |

## Missing Operator Terms


## Limitations

- The derivation is symbolic but closes the listed action-to-operator package under BHSM axioms.
- No empirical masses, CKM, PMNS, or residuals are used.
