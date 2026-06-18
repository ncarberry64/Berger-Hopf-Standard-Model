# BHSM Brownian Generator from Topographic Attractor Dynamics

This sprint tests whether topographic attractor fluctuations can support trace-preserving Brownian activity on the finite channel algebra.
The result is partial: exact su(d) channel counts and the quadratic damping scaffold are implemented, while the full stochastic dynamics remains open.

## Summary

Brownian generator topographic status: `BROWNIAN_GENERATOR_TOPOGRAPHIC_PARTIAL`
Attractor Hessian status: `ATTRACTOR_HESSIAN_BROWNIAN_PARTIAL`
Boundary noise projection status: `BOUNDARY_NOISE_PROJECTION_PARTIAL`
Trace-preserving noise status: `TRACE_PRESERVING_NOISE_PARTIAL`
su(d) Brownian generator status: `TRACELESS_BROWNIAN_GENERATOR_PARTIAL`
Exponential dressing status: `EXPONENTIAL_DRESSING_FROM_BROWNIAN_PARTIAL`
Quadratic norm status: `QUADRATIC_NORM_HOPF_BASE_PARTIAL`
alpha/pi strength status: `ALPHA_OVER_PI_STOCHASTIC_STRENGTH_STRUCTURAL_CANDIDATE`
Lepton 8/9 consequence: `LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED`
Quark consequence: `QUARK_BROWNIAN_ACTIVE_FRACTION_CANDIDATE_ONLY`
Neutrino consequence: `NEUTRINO_BROWNIAN_CHANNEL_CANDIDATE_ONLY`

## Brownian Chain

```text
T = T_f^* + delta T
E[T] ~= E[T_f^*] + 1/2 <delta T, H_f delta T>
delta rho_f = Pi_f delta T_boundary Pi_f^dagger
Tr(delta rho_f)=0
delta rho_f in su(d_f)
Z(k,j)=exp[-eta (q^2+j^2)]
```

Topographic dynamics generates noise scaffold: `True`
Boundary projection maps noise to H_f: `True`
Noise acts on End(H): `True`
Trace preservation forces su(d): `True`
Exponential dressing follows as scaffold: `True`
alpha/pi follows: `False`

## Sector Counts

| Sector | d | dim End(H) | su(d) generators | Active fraction | Candidate only |
| --- | ---: | ---: | ---: | ---: | --- |
| `charged_lepton` | `3` | `9` | `8` | `8/9` | `False` |
| `up` | `6` | `36` | `35` | `35/36` | `True` |
| `down` | `12` | `144` | `143` | `143/144` | `True` |

## Lepton Consequence

`eta_l = 0.002064728414019306` from `(alpha/pi)*(8/9)`.
Promotes full lepton 8/9: `False`

## Dimension Warning

probability simplex dimension d-1 is not the lepton 8/9 count; 8/9 uses traceless End(H) dimension d^2-1 over d^2

## Blockers Closed

- trace_preserving_noise_restricts_relative_activity_to_su_d
- Brownian_generator_count_equals_d_squared_minus_one
- exponential_quadratic_dressing_scaffold
- lepton_eta_8alpha_over_9pi_strengthened_as_partial_consequence

## Blockers Remaining

- compute the full topographic attractor Hessian from the completed BHSM action
- derive the boundary projection kernel Pi_f from the full boundary dynamics
- derive Brownian/Lindblad rates D_a on su(d_f)
- derive alpha/pi from a completed stochastic path integral or boundary U(1) normalization
- derive primitive cyclic monodromy rather than using the partial scaffold

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No frozen lepton or quark dressing rule is changed.
- No neutrino speed anomaly claim is made.
- No lab-scale environmental mass-drift claim is made.
- No Standard Model replacement claim is made.
