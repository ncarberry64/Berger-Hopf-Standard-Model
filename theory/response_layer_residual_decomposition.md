# Response Layer Residual Decomposition

Status: `RESPONSE_LAYER_RESIDUAL_DECOMPOSITION_COMPLETE`

This candidate-only audit follows the Tier C bare-Yukawa numerical gate. It tests whether existing candidate response toggles improve or worsen the fixed raw universal baseline.

## Baseline

Variant: `A_raw`
Parameters: `{'epsilon': 0.05, 'tau0': 0.2, 'beta_eff': 0.0, 'xi': 0.0}`
RMS log error: `2.650470675424182`
Max abs log error: `4.721337722933362`

## Scenario Summary

| Scenario | RMS | Max abs | Improved | Worsened | Delta vs bare | Ordering |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `bare_only` | `2.650470675424182` | `4.721337722933362` | `0` | `0` | `0.0` | `True` |
| `lepton_8_9_only` | `2.638260385865333` | `4.6841726114810145` | `2` | `0` | `-0.012210289558848952` | `True` |
| `up_half_only` | `2.734764700227175` | `4.721337722933362` | `0` | `1` | `0.0842940248029933` | `True` |
| `up_light_amp_only` | `2.677806897733487` | `4.721337722933362` | `0` | `1` | `0.027336222309305214` | `True` |
| `up_half_and_light_amp` | `2.7612665474151807` | `4.721337722933362` | `0` | `2` | `0.11079587199099894` | `True` |
| `current_candidate_responses` | `2.7495483280380673` | `4.6841726114810145` | `2` | `2` | `0.09907765261388546` | `True` |

## Interpretation

- Lepton 8/9 response suppresses overpredicted lepton rows and is directionally helpful.
- Up half response worsens the existing c/t underprediction.
- Up light amplitude response worsens the existing u/t underprediction.
- Down rows are overpredicted in the bare baseline; any missing down response would need suppression, not enhancement.
- Bundled current responses are mixed and do not provide numerical closure.

## Guardrails

- No new official response factor is introduced.
- No down response is treated as official.
- Response factors are not interchangeable.
- CKM interface response is not a mass response.
- `RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE` is not upgraded to derived.
