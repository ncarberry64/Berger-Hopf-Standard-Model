# BHSM v2.11 Boundary/Coframe Compatibility Report

Status: `BOUNDARY_COFRAME_REPRESENTED`
Missing axiom: ``
Theorem complete: `True`

| Sector | Boundary rule | Coframe channel | Coefficient status | Conclusion | Limitation |
| --- | --- | --- | --- | --- | --- |
| `lepton` | `Omega_l=-q+2j=3` | no quark coframe triplet | `BOUNDARY_COFRAME_CONSTRAINED` | lepton sector supplies a control case with no coframe triplet coefficient | Control case does not introduce an independent mixed coefficient. |
| `up` | `Omega_u=q-2j=6` | coframe triplet participates | `BOUNDARY_COFRAME_REPRESENTED` | up-sector boundary/coframe cross coefficient is represented by V_PSD/profile | Full profile positivity remains a separate H_T dependency. |
| `down` | `Omega_d=q+4j=12` | coframe triplet participates | `BOUNDARY_COFRAME_REPRESENTED` | down-sector boundary/coframe cross coefficient is represented by V_PSD/profile | Full profile positivity remains a separate H_T dependency. |

## Limitations

- Boundary/coframe coefficients are represented through existing BHSM topographic/profile sectors.
- No prediction residual is used to choose a boundary/coframe coefficient.
