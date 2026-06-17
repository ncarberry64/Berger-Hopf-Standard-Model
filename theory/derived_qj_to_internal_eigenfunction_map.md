# Derived QJ To Internal Eigenfunction Map

```text
E:(q,j)->psi_qj(y)
```

Mode ledger:

| sector | index | q | j | symbolic eigenfunction |
| --- | ---: | ---: | ---: | --- |
| reference_charged | 0 | 0 | 0 | `psi_q0_j0(y)` |
| reference_charged | 1 | 1 | 2 | `psi_q1_j2(y)` |
| reference_charged | 2 | 3 | 3 | `psi_q3_j3(y)` |
| reference_neutral | 0 | 0 | 0 | `psi_q0_j0(y)` |
| reference_neutral | 1 | 3 | 0 | `psi_q3_j0(y)` |
| reference_neutral | 2 | 1 | 1 | `psi_q1_j1(y)` |
| cyclic_upper | 0 | 0 | 0 | `psi_q0_j0(y)` |
| cyclic_upper | 1 | 6 | 0 | `psi_q6_j0(y)` |
| cyclic_upper | 2 | 8 | 1 | `psi_q8_j1(y)` |
| cyclic_lower | 0 | 0 | 0 | `psi_q0_j0(y)` |
| cyclic_lower | 1 | 0 | 3 | `psi_q0_j3(y)` |
| cyclic_lower | 2 | 4 | 2 | `psi_q4_j2(y)` |

This branch defines the symbolic map needed by later theorem layers. It does not derive explicit Berger/BHSM eigenfunction formulas.

Status: `QJ_EIGENFUNCTION_MAP_SCAFFOLD_DERIVED_CONDITIONAL`.
