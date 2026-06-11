# Frozen Predictions

This file summarizes the frozen no-retuning BHSM prediction/screen package for
release `v1.2.0`.

## Frozen Branches

| Branch | Meaning |
| --- | --- |
| `BHSM_BARE_V1` | Bare alpha-anchored Berger-Hopf overlap model |
| `BHSM_DRESSED_V1_CANDIDATE` | Same frozen model with `Z_virt^{u,2}=1/2` applied only to `c/t` |

## Frozen Constants

| Constant | Value |
| --- | --- |
| `a` | `1.157054135733433` |
| `S` | `0.07957747154594767` |

## Branch Comparison

| Quantity | `BHSM_BARE_V1` | `BHSM_DRESSED_V1_CANDIDATE` | Changed |
| --- | --- | --- | --- |
| `c/t` | `0.008310500554068288` | `0.004155250277034144` | `True` |
| `u/t` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `False` |
| `s/b` | `0.021933971495439474` | `0.021933971495439474` | `False` |
| `d/b` | `0.0011165200546001757` | `0.0011165200546001757` | `False` |
| `sin_theta_13` | `0.0035623676140463315` | `0.0035623676140463315` | `False` |

## Charged Lepton Ratios

| Quantity | BHSM output |
| --- | --- |
| charged leptons heavy/reference | `1.0` |
| charged leptons middle/heavy | `0.06007447093260976` |
| charged leptons light/heavy | `0.00029729106456492414` |

## Up/Down Quark Ratios

| Quantity | BHSM output | Caveat |
| --- | --- | --- |
| `c/t` bare | `0.008310500554068288` | quark mass scheme-sensitive |
| `c/t` dressed candidate | `0.004155250277034144` | candidate dressing only |
| `u/t` | `1.2690463017606151e-05` | quark mass scheme-sensitive |
| `s/b` | `0.021933971495439474` | quark mass scheme-sensitive |
| `d/b` | `0.0011165200546001757` | quark mass scheme-sensitive |

## CKM Screen Values

| Quantity | BHSM output |
| --- | --- |
| `sin_theta_12` | `0.2256184580048353` |
| `sin_theta_23` | `0.04386794299087895` |
| `sin_theta_13` | `0.0035623676140463315` |
| `delta_cp` | `1.1283791670955126` |
| `J_CKM` | `3.1011702945437805e-05` |

## External Validation Caveat

Precision comparison and external validation are separate from release
theorem/package bookkeeping. Quark mass rows are scheme-sensitive unless a
validated common-scale QCD/RG comparison is supplied.
