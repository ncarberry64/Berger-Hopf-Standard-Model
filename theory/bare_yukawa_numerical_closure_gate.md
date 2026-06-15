# Bare Yukawa Numerical Closure Gate

Status: `BARE_YUKAWA_NUMERICAL_CLOSURE_GATE_CANDIDATE`

This candidate-only audit tests whether the bare Yukawa spectral-action mass engine can support the charged-fermion hierarchy with one universal parameter set. It does not create official predictions and does not modify frozen outputs.

## Formula

```text
lambda_hat(q,j) = (1 + epsilon)^(-2) * q^2 + j^2
fiber_fraction(q,j) = q^2/(q^2+j^2), with fiber_fraction(0,0)=0
S_bare(q,j) = tau0 * [lambda_hat + beta_eff * lambda_hat^2] - xi * fiber_fraction
S_bare(0,0)=0
Y_bare(q,j)=exp[-S_bare(q,j)]
```

## Parameter Policy

`NO_SECTOR_SPECIFIC_TUNING_GUARDRAIL`: the main scan uses one shared set `(epsilon,tau0,beta_eff,xi)` across charged leptons, up quarks, and down quarks.

## Response Scenarios

- `bare_only`: `Z_response=1` for all modes.
- `current_candidate_responses`: charged-lepton `eta_l=8 alpha/(9 pi)`, middle-up `1/2`, light-up `1/sqrt(3)`, down-sector `1`.

## Verdict

Verdict: `BARE_YUKAWA_NUMERICAL_GATE_TIER_C_ORDERING_ONLY`
Response scenario: `current_candidate_responses`
Best parameters: `epsilon=0.05`, `tau0=0.2`, `beta_eff=0.0`, `xi=0.0`
RMS log error: `2.7495483280380673`
Max absolute log error: `4.6841726114810145`
Ordering pass: `True`

## Sector Results

| Sector | Row | q,j | predicted | reference | log error | response | scheme-sensitive |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `charged_lepton` | `middle` | `(1,2)` | `0.37093459053213484` | `0.05946353426831603` | `1.830662485990157` | `0.9897294638168652` | `False` |
| `charged_lepton` | `light` | `(3,3)` | `0.03112268910186473` | `0.0002875853753250115` | `4.6841726114810145` | `0.9635170345177995` | `False` |
| `up` | `middle` | `(6,0)` | `0.000729056427146548` | `0.007354218541895883` | `-2.3112782463318258` | `0.5` | `True` |
| `up` | `light` | `(8,1)` | `4.289744136703305e-06` | `1.2507962244484336e-05` | `-1.0701383317144504` | `0.5773502691896258` | `True` |
| `down` | `middle` | `(0,3)` | `0.16529888822158653` | `0.022344497607655504` | `2.001175180284005` | `1.0` | `True` |
| `down` | `light` | `(4,2)` | `0.02466193465732934` | `0.0011172248803827751` | `3.0944131227722367` | `1.0` | `True` |

## Scheme Sensitivity

`QUARK_RATIO_SCHEME_SENSITIVITY_GUARDRAIL`: quark references are the existing repository comparison values and remain scheme-sensitive. This gate reports log-shape and ordering; it does not provide precision QCD closure.

## Failure Modes

- A weak verdict means the universal action orders the hierarchy but does not numerically close it.
- A forbidden sector fit would use separate parameters per sector and is not evidence.
- Candidate response factors remain non-official and are not interchangeable.

## Claim Boundaries

- `BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived.
- `FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived.
- Frozen predictions and official dressed-candidate rules are unchanged.
