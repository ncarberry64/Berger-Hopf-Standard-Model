# BHSM Alpha-over-Pi Stochastic Strength Derivation

This sprint audits the proposed rationalized U(1) normalization for the base stochastic strength.
It verifies the algebra `D_U1=(e/(2*pi))^2=alpha/pi` and records the Brownian factor-of-two hazard.

## Summary

alpha/pi strength status: `ALPHA_OVER_PI_STOCHASTIC_STRENGTH_PARTIAL`
U(1) phase normalization status: `U1_PHASE_NORMALIZATION_PARTIAL`
Hopf/contact normalization status: `HOPF_CONTACT_NORMALIZATION_COMPATIBLE`
Brownian factor-two hazard: `BROWNIAN_FACTOR_TWO_HAZARD_RECORDED`
Lepton eta consequence: `LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED`
alpha/pi follows: `True`
eta_l=8alpha/(9pi) follows: `True`
Promotes full lepton 8/9: `False`
Official predictions changed: `False`

## Algebra

```text
alpha = e^2/(4*pi)
g_U1 = e/(2*pi)
D_U1 = g_U1^2 = e^2/(4*pi^2)
e^2 = 4*pi*alpha
D_U1 = alpha/pi
eta_l = D_U1 * 8/9 = 8*alpha/(9*pi)
```

## Mode Norms

| Mode | N=q^2+j^2 | Dressing factor |
| --- | ---: | ---: |
| `tau_reference (0, 0)` | `0` | `1.0` |
| `muon (5, 2)` | `5` | `0.9897294638168652` |
| `electron (9, 3)` | `18` | `0.9635170345177995` |

## Factor-of-Two Hazard

A completed Brownian/cumulant normalization could introduce an extra conventional factor. This sprint records that hazard rather than hiding it.

## Blockers Closed

- exact_rationalized_U1_algebra_D_U1_equals_alpha_over_pi
- Hopf_contact_2pi_normalization_compatibility
- eta_l_equals_D_U1_times_8_over_9

## Blockers Remaining

- derive Brownian/cumulant normalization from a completed stochastic path integral
- derive the boundary U(1) fluctuation measure rather than only phase-cycle normalization
- derive primitive cyclic monodromy and full stochastic generator before promoting full lepton 8/9

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No frozen lepton or quark dressing rule is changed.
- No Standard Model replacement claim is made.
