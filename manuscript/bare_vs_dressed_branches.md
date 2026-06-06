# Bare vs Dressed Branches

The frozen v1.0 package declares two branches.

## BHSM_BARE_V1

`BHSM_BARE_V1` is the pure alpha-anchored Berger-Hopf overlap model. It uses:

- `a = alpha^{-1}/(12*pi^2)`
- `S = 1/(4*pi)`
- the fixed charged-sector mode ledger
- no virtual-environment dressing factors

## BHSM_DRESSED_V1_CANDIDATE

`BHSM_DRESSED_V1_CANDIDATE` uses the same frozen model, but applies:

```text
Z_virt^{u,2} = 1/2
```

only to the middle up-sector ratio `c/t` for pure-fiber middle up mode `(6,0)`.
It leaves `u/t`, CKM `sin(theta_13)`, down-sector ratios, charged lepton
ratios, gauge outputs, Higgs/electroweak outputs, `H_T`, and scalar outputs
unchanged.

| Quantity | `BHSM_BARE_V1` | `BHSM_DRESSED_V1_CANDIDATE` | Changed |
| --- | --- | --- | --- |
| `c/t` | `0.008310500554068288` | `0.004155250277034144` | `True` |
| `u/t` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `False` |
| `s/b` | `0.021933971495439474` | `0.021933971495439474` | `False` |
| `d/b` | `0.0011165200546001757` | `0.0011165200546001757` | `False` |
| `sin_theta_13` | `0.0035623676140463315` | `0.0035623676140463315` | `False` |

The virtual dressing adoption audit marks the rule as `ADOPTION_CANDIDATE`.
It is not `ADOPTED_CANONICAL_DRESSED`.
