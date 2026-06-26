# BHSM Boundary Source Matrices v0.5

Machine-readable artifact:

```text
artifacts/BHSM_boundary_source_matrices_v0_5.json
```

Exported boundary-source matrices:

```text
C_ch_boundary = diag(beta_l*tau, beta_u*tau, beta_d*tau)
K_ch_boundary = diag(kappa_l*tau, kappa_u*tau, kappa_d*tau)
K_nu_boundary =
[[0, 1/3, 0],
 [1/3, 3, 1/6],
 [0, 1/6, 5/3]]
```

Approximate charged diagonals:

```text
C_ch_boundary = [0.000542969379063240, 0.001085938758126480, 0.002171877516252960]
K_ch_boundary = [0.000542969379063240, 0.000542969379063240, 0.000200041350181194]
```

These are boundary-source matrices only, not collider vertices yet.

```text
ufo_ready = false
```
