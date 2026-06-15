# Existing Engine Branch/Threshold Audit

Status: `EXISTING_ENGINE_BRANCH_THRESHOLD_AUDIT_COMPLETE`

This candidate-only audit treats the existing BHSM bare/dressed values as the object to explain. The new spectral-action baseline is demoted to a failed/simple comparator rather than an official mass engine.

## Read-Only Existing Outputs

| Ratio | Sector | q,j | k,j | Existing bare | Existing dressed | Reference | Scheme note |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `mu/tau` | `charged_lepton` | `(1, 2)` | `(5, 2)` | `0.06007447093260976` | `0.06007447093260976` | `0.05946353426831603` | scheme-stable for this audit |
| `e/tau` | `charged_lepton` | `(3, 3)` | `(9, 3)` | `0.00029729106456492414` | `0.00029729106456492414` | `0.0002875853753250115` | scheme-stable for this audit |
| `c/t` | `up` | `(6, 0)` | `(6, 0)` | `0.008310500554068288` | `0.004155250277034144` | `0.007354218541895883` | quark ratios are scheme-sensitive |
| `u/t` | `up` | `(8, 1)` | `(10, 1)` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `1.2507962244484336e-05` | quark ratios are scheme-sensitive |
| `s/b` | `down` | `(0, 3)` | `(6, 3)` | `0.021933971495439474` | `0.021933971495439474` | `0.022344497607655504` | quark ratios are scheme-sensitive |
| `d/b` | `down` | `(4, 2)` | `(8, 2)` | `0.0011165200546001757` | `0.0011165200546001757` | `0.0011172248803827751` | quark ratios are scheme-sensitive |

## Branch Signals

| Sector | Label | Role | Rank | N | Special |
| --- | --- | --- | ---: | ---: | --- |
| `charged_lepton` | `reference` | `reference` | `0` | `0` | `reference` |
| `charged_lepton` | `mu/tau` | `lower_nonzero_action, mixed` | `1` | `5` | `mixed` |
| `charged_lepton` | `e/tau` | `higher_nonzero_action, mixed` | `2` | `18` | `mixed` |
| `up` | `reference` | `reference` | `0` | `0` | `reference` |
| `up` | `c/t` | `lower_nonzero_action, pure_fiber` | `1` | `36` | `pure_fiber` |
| `up` | `u/t` | `higher_nonzero_action, mixed` | `2` | `65` | `mixed` |
| `down` | `reference` | `reference` | `0` | `0` | `reference` |
| `down` | `s/b` | `lower_nonzero_action, pure_base` | `1` | `9` | `pure_base` |
| `down` | `d/b` | `higher_nonzero_action, mixed` | `2` | `20` | `mixed` |

## Threshold Diagnostics

| Family | Policy | RMS to existing bare | Official | Overfit risk |
| --- | --- | ---: | --- | --- |
| `exponential_action_control` | `single_universal_parameter` | `2.714934256444424` | `False` | `False` |
| `bounded_threshold` | `single_universal_parameter` | `2.6026920512069673` | `False` | `False` |
| `logarithmic_threshold` | `single_universal_parameter` | `1.8076741338301048` | `False` | `False` |
| `branch_rank_threshold` | `single_universal_parameter` | `1.4880093492548556` | `False` | `False` |
| `branch_type_weighted_threshold` | `universal_a_b_c_not_sector_specific` | `None` | `False` | `True` |

## Hidden Response Decomposition

The hidden response `R_hidden=existing_bare/spectral_action` is diagnostic only. It identifies what the simple raw action would need to recover the existing engine pattern, not a new formula.

## Answers

1. The existing engine is not closest to a simple raw exponential law.
2. Pure-fiber charm and pure-base strange are special branch types in the ledger.
3. Existing patterns suggest branch assignment before response factors.
4. Missing ingredients include branch assignment, nonlinear threshold behavior, hidden response decomposition, and reference-scheme harmonization.
5. Next target: derive or reject a branch-aware nonlinear threshold/hidden-response law.
6. Forbidden: new official formulas, sector-specific tuning, per-particle response factors, and retrofitting frozen predictions.

## Claim Boundaries

- No official predictions are changed.
- No frozen predictions are changed.
- No new official mass formula is introduced.
- `BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived.
- `FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived.
- `RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE` is not upgraded to derived.
