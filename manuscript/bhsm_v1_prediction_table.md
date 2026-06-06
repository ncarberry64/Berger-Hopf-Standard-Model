# BHSM v1.0 Frozen Prediction Set

This is a no-retuning frozen prediction package with bare and dressed-candidate branches.

## Tolerance Bands

| Class | Tolerance |
| --- | --- |
| `exact_status` | `pass_fail` |
| `gauge_couplings` | `0.01` |
| `higgs_electroweak_v` | `0.01` |
| `higgs_mass_zeroth_order` | `0.02` |
| `charged_lepton_ratios` | `0.25` |
| `quark_ratios_scheme_aware` | `0.25` |
| `quark_ratios_otherwise` | `SCHEME_SENSITIVE` |
| `ckm_angles` | `0.1` |
| `ckm_cp_jarlskog` | `0.1` |
| `pmns_effective` | `0.05` |
| `ht_gap` | `binary_pass_fail` |
| `scalar_decoupling` | `binary_scaffold_pass_fail` |

## Branch Comparison

| Quantity | BHSM_BARE_V1 | BHSM_DRESSED_V1_CANDIDATE | Changed |
| --- | --- | --- | --- |
| `c/t` | `0.008310500554068288` | `0.004155250277034144` | `True` |
| `u/t` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `False` |
| `s/b` | `0.021933971495439474` | `0.021933971495439474` | `False` |
| `d/b` | `0.0011165200546001757` | `0.0011165200546001757` | `False` |
| `sin_theta_13` | `0.0035623676140463315` | `0.0035623676140463315` | `False` |

## Score Summary

- Bare: `{'PASS': 22}`
- Dressed candidate: `{'PASS': 21, 'SCHEME_SENSITIVE': 1}`

## Freeze Notes

- Canonical geometry, overlap width, mode ledger, and dressing rule are frozen.
- No residual-driven retuning is allowed.
- The dressed branch is a candidate branch, not a proof of the full internal action.
