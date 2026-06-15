# Bare Yukawa Residual Autopsy

Status: `BARE_YUKAWA_RESIDUAL_AUTOPSY_COMPLETE`

This candidate-only audit preserves the previous `BARE_YUKAWA_NUMERICAL_GATE_TIER_C_ORDERING_ONLY` outcome. Tier C is scientifically useful because it shows the raw candidate action preserves hierarchy ordering while failing numerical closure.

## Best Evidence Variant

Variant: `A_raw`
Response scenario: `bare_only`
Verdict: `BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY`
Best parameters: `{'epsilon': 0.05, 'tau0': 0.2, 'beta_eff': 0.0, 'xi': 0.0}`
RMS log error: `2.650470675424182`
Max abs log error: `4.721337722933362`
Ordering pass: `True`

## Previous Raw-Action Residuals

| Ratio | Sector | q,j | predicted | reference | log residual | x-error | sign |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `e/tau` | `charged_lepton` | `(3, 3)` | `0.03112268910186473` | `0.0002875853753250115` | `4.6841726114810145` | `108.22069469524226` | `overpredict` |
| `d/b` | `down` | `(4, 2)` | `0.02466193465732934` | `0.0011172248803827751` | `3.0944131227722367` | `22.074279843177013` | `overpredict` |
| `c/t` | `up` | `(6, 0)` | `0.000729056427146548` | `0.007354218541895883` | `-2.3112782463318258` | `10.087310485252202` | `underpredict` |
| `s/b` | `down` | `(0, 3)` | `0.16529888822158653` | `0.022344497607655504` | `2.001175180284005` | `7.397744676297983` | `overpredict` |
| `mu/tau` | `charged_lepton` | `(1, 2)` | `0.37093459053213484` | `0.05946353426831603` | `1.830662485990157` | `6.238017889390407` | `overpredict` |
| `u/t` | `up` | `(8, 1)` | `4.289744136703305e-06` | `1.2507962244484336e-05` | `-1.0701383317144504` | `2.9157828173166482` | `underpredict` |

## Residual Pattern

Sector RMS: `{'charged_lepton': 3.556177596223263, 'up': 1.8010001639327116, 'down': 2.605771927526443}`
Mode RMS: `{'middle': 2.0573473513048386, 'light': 3.2995990502654755}`
Sign pattern: `{'mu/tau': 'overpredict', 'e/tau': 'overpredict', 'c/t': 'underpredict', 'u/t': 'underpredict', 's/b': 'overpredict', 'd/b': 'overpredict'}`

The raw best fit has `beta_eff=0` and `xi=0`, so the current fourth-order and focusing terms are not numerically favored by this coarse universal scan. The previous epsilon value hit the upper bound, suggesting raw eigenvalue normalization may be incomplete.

## Claim Boundaries

- No official predictions are changed.
- No frozen predictions are changed.
- Quark references remain scheme-sensitive.
- Branch-relative subtraction is a structural control, not primary evidence.
- `BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived.
- `FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived.
