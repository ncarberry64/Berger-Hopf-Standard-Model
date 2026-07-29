# BHSM v6.30.5 fixed-h dependency registry

| Output | Required inputs | Profile order | Domain restriction |
| --- | --- | --- | --- |
| `Omega3`, `g3` | `u1`, `A2`, frozen `G5/Z5`, `Z5/kappa1` | 1, 2 | strict D0 |
| `Phi3` | `Q S3`, exact scalar complement inverse | 1--3 | fixed-h Dirichlet |
| `A4`, `eta4` | exact lapse constraint, `Phi3`, matcher generator | 1--4 | fixed curvature |
| `Gamma4` | projected force, two-cap action pairing | 1--3 | fixed `h`, fixed regulator |
| `F2` | `A2` | 2 | no D2 tangent |
| `F4` | `A2`, `Phi3`, `A4` | 2--4 | no curvature response |
| `VJ2`, `VJ4` | `F2`, `F4`, `Gamma2`, `Gamma4` | 2--4 | extracted before M4 EOM |
| `VE2`, `VE4` | Jordan coefficients, then q=0 M4 stationarity | 2--4 | same D0 family |
| canonical `g4` | `VE4`, D0 `k0` | 1--4 | no D2 kinetic pieces |
| v6.31 permission | unconditional interaction sign and scale source | downstream | fails: `G5` unselected |

The historical curvature-varying D2 values `F1_tau` and
`kE(0)=6.935084858283065` are not dependencies of any D0 output.
