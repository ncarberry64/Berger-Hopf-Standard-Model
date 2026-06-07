# CKM and CP Structure

The CKM angles are computed from the canonical BHSM mass-ratio screens:

```text
sin(theta_12) ~= sqrt(d/s)
sin(theta_23) ~= 2(s/b)
sin(theta_13) ~= sqrt(u/t)
```

The frozen outputs are:

| Quantity | BHSM Output | Residual Severity |
| --- | --- | --- |
| `sin_theta_12` | `0.2256184580048353` | `EXCELLENT` |
| `sin_theta_23` | `0.04386794299087895` | `MODERATE` |
| `sin_theta_13` | `0.0035623676140463315` | `MODERATE` |
| `delta_cp` | `1.1283791670955126` | `MODERATE` |
| `J_CKM` | `3.1011702945437805e-05` | `GOOD` |

The Hopf-phase CP screen is:

```text
delta_CKM = (q_u - q_d) sqrt(S)
```

with `q_u = q(10,1)`, `q_d = q(8,2)`, and `S = 1/(4*pi)`.

The frozen CKM matrix magnitude screen is:

```text
[[0.9742095600721029, 0.22561702639894465, 0.0035623676140463315],
 [0.2254664853946855, 0.9732628072432431, 0.04386766463774175],
 [0.008977584746899065, 0.04308671994825354, 0.9990309992869156]]
```

The CKM sector remains an internal-rule flavor screen. Full action derivation
of the boundary operators `Omega_f` remains open.
