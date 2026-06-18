# BHSM Brownian Cumulant Normalization and Factor-of-Two Audit

This sprint audits whether the BHSM lepton exponent uses a heat-kernel coefficient or a Gaussian phase-cumulant variance convention.
The repo consistently treats `eta` as the exponent coefficient in `Z=exp[-eta N]`, but the completed stochastic path-integral normalization is not yet derived.

## Summary

Brownian factor-two status: `BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT`
Heat-kernel normalization: `HEAT_KERNEL_NORMALIZATION_PARTIAL`
Phase-cumulant status: `PHASE_CUMULANT_HALF_FACTOR_CONDITIONAL`
Ito/generator status: `ITO_GENERATOR_NORMALIZATION_CONVENTION_DEPENDENT`
Eta exponent convention: `ETA_EXPONENT_CONVENTION_REPO_SUPPORTED`
Lepton eta normalization: `LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT`
Preferred eta form: `no_extra_half_repo_exponent_convention`
eta_l=8alpha/(9pi) remains supported: `True`
Factor two resolved: `False`
Official predictions changed: `False`

## Eta Forms

| Form | eta_l | Meaning |
| --- | ---: | --- |
| `no_extra_half` | `0.002064728414019306` | repo heat-kernel/exponent convention |
| `half_factor` | `0.001032364207009653` | Gaussian phase-cumulant if alpha/pi is raw variance |
| `double_factor` | `0.004129456828038612` | sensitivity diagnostic |

## Convention Distinction

```text
Heat kernel:       dK/dt = D Delta K  -> exp[-D lambda t]
Phase cumulant:    E[exp(i theta)] with Var(theta)=sigma^2 -> exp[-sigma^2/2]
Ito:               dtheta=g dW, generator coefficient may be g^2/2
Repo eta:          Z=exp[-eta N]
```

## Hazards

- Gaussian phase cumulant gives exp[-variance/2] if alpha/pi is raw variance
- heat-kernel convention gives exp[-D lambda] if alpha/pi is generator coefficient
- completed stochastic path-integral normalization is still absent

## Blockers Closed

- repo_eta_as_exponent_coefficient_audited
- heat_kernel_no_extra_half_convention_formalized
- phase_cumulant_half_factor_hazard_formalized
- all_three_eta_forms_reported_without_prediction_changes

## Blockers Remaining

- derive from completed stochastic path integral whether alpha/pi is raw variance or generator coefficient
- derive Brownian time/cycle normalization rather than setting tau=1 by convention
- derive primitive cyclic monodromy and full stochastic generator before any full lepton promotion

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No frozen lepton or quark dressing rule is changed.
- No Standard Model replacement claim is made.
