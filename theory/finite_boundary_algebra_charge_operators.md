# Finite Boundary Algebra Charge Operators

Candidate charge operators:

```text
P_ell = I - P_C
T3_hat = (1/2) P_w S_sigma
Y_hat = (4/3)P_C - I + (I-P_w)S_sigma
Q_hat = T3_hat + Y_hat/2
```

Electric charge simplification:

```text
Q_hat
= (1/2)P_w S_sigma
  + (1/2)[(4/3)P_C - I + (I-P_w)S_sigma]
= (2/3)P_C - (1/2)I + (1/2)S_sigma
= (1/2)(S_sigma - I) + (2/3)P_C
```

| state | C | sigma | Q |
| --- | --- | --- | --- |
| lepton upper | 0 | +1 | 0 |
| lepton lower | 0 | -1 | -1 |
| quark upper | 1 | +1 | +2/3 |
| quark lower | 1 | -1 | -1/3 |

`w` affects `T3` and `Y`, but not `Q`:

| state | channel block | weak block | orientation | C | ell | w | sigma | T3 | Y | Q |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nu_L | C_ell | M2_active | upper | 0 | 1 | 1 | 1 | 1/2 | -1 | 0 |
| e_L | C_ell | M2_active | lower | 0 | 1 | 1 | -1 | -1/2 | -1 | -1 |
| u_L | M3_C | M2_active | upper | 1 | 0 | 1 | 1 | 1/2 | 1/3 | 2/3 |
| d_L | M3_C | M2_active | lower | 1 | 0 | 1 | -1 | -1/2 | 1/3 | -1/3 |
| e_R | C_ell | C_sigma_minus |  | 0 | 1 | 0 | -1 | 0 | -2 | -1 |
| u_R | M3_C | C_sigma_plus |  | 1 | 0 | 0 | 1 | 0 | 4/3 | 2/3 |
| d_R | M3_C | C_sigma_minus |  | 1 | 0 | 0 | -1 | 0 | -2/3 | -1/3 |
| nu_R | C_ell | C_sigma_plus |  | 0 | 1 | 0 | 1 | 0 | 0 | 0 |

Status: candidate diagnostic. The finite boundary algebra is not yet derived from Berger-Hopf boundary geometry.

## Related Automorphism Closure Gate

- [Boundary automorphism closure origin gate](boundary_automorphism_closure_origin_gate.md)
- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
