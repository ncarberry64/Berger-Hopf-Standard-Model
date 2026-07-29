# BHSM v6.30.5 fixed-h precision ledger

| Quantity/check | Reported value or certified bound |
| --- | --- |
| `mu_c` | `29.4309183529476` |
| `M4` | `21.6901302294121` |
| `C_grav` | `394.705988442955` |
| independent `M4` route discrepancy | `< 2e-7` |
| independent `C_grav` route discrepancy | `< 2e-5` |
| `Phi3_G` 101-node profile discrepancy | `< 2e-7` |
| `Phi3_grav` 101-node profile discrepancy | `< 2e-5` |
| shooting endpoint residual | `< 2e-9` |
| KKT orthogonality residual | `< 2e-8` |

The tolerances are conservative cross-platform certification bounds.
Observed last-bit differences are deliberately not serialized. Exact
projector identities, parity zeros, the Noether formula, and the
reduced-action coefficient identity are symbolic rather than numerical.
