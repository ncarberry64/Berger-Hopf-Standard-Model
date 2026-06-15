# Boundary Cycle-Time Normalization

This audit localizes the remaining Brownian factor-of-two issue. It does not alter frozen outputs or create an official prediction update.

## Summary

Stochastic path-integral status: `STOCHASTIC_NORMALIZATION_PARTIAL`
Heat-kernel generator status: `STOCHASTIC_PATH_INTEGRAL_HEAT_KERNEL_PARTIAL`
Phase-cumulant status: `STOCHASTIC_PATH_INTEGRAL_PHASE_CUMULANT_CONDITIONAL`
Ito sqrt(2D) status: `ITO_SQRT_2D_NORMALIZATION_PARTIAL`
Boundary-cycle time status: `BOUNDARY_CYCLE_TIME_NORMALIZATION_CONVENTION_FIXED`
alpha/pi role: `ALPHA_PI_ROLE_GENERATOR_BY_REPO_CONVENTION_RAW_VARIANCE_ALTERNATIVE`
Brownian factor-two status: `BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT_STRENGTHENED`
Lepton eta normalization status: `LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT_STRENGTHENED`
Preferred eta form: `no_extra_half_repo_exponent_convention`
Factor two closed: `False`

## Convention Fork

```text
Raw variance route:
  g_U1^2 = alpha/pi
  D = g_U1^2/2
  Z = exp[-(alpha/pi) N active_fraction / 2]

Heat-kernel route:
  D_U1 = alpha/pi
  Z = exp[-D_U1 N active_fraction]

Ito sqrt(2D) route:
  dtheta = sqrt(2D) dW
  Var(theta)=2D tau
  E[exp(i theta)] = exp[-D tau]
```

## Eta Forms Preserved

| Form | eta_l | Status |
| --- | ---: | --- |
| `no_extra_half` | `0.002064728414019306` | repo-preferred candidate convention |
| `half_factor` | `0.001032364207009653` | raw-variance alternative |
| `double_factor` | `0.004129456828038612` | sensitivity diagnostic |

## Mode Norm Checks

| Mode | N=q^2+j^2 |
| --- | ---: |
| tau `(0,0)` | `0` |
| muon `(5,2)` | `5` |
| electron `(9,3)` | `18` |

## Interpretation

The sprint strengthens the bookkeeping: `alpha/pi` can be treated as the generator coefficient under the existing repo exponent convention, while the raw-variance interpretation remains a valid alternative that would introduce a half factor. The complete stochastic path-integral measure is still not derived, so the factor-of-two issue remains convention-dependent.

## Blockers Closed

- Ito_sqrt_2D_notation_reconciles_half_factor_by_convention
- alpha_pi_generator_vs_variance_roles_are_explicit
- eta_l_8alpha_9pi_remains_supported_as_repo_exponent_convention

## Blockers Remaining

- derive the boundary stochastic measure from the completed BHSM path integral
- derive whether alpha/pi is generator coefficient D or raw variance g^2
- derive tau=1 boundary-cycle time rather than fixing it by convention
- derive full stochastic generator on the physical channel algebra before promoting lepton 8/9

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No frozen lepton or quark dressing rule is changed.
- No Standard Model replacement claim is made.
