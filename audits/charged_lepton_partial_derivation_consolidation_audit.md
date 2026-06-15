# BHSM Charged-Lepton Partial Derivation Consolidated

This document consolidates the charged-lepton partial derivation chain. It is a status and audit package only: no frozen output is changed and no lepton dressing is promoted to an official prediction.

## Summary

Consolidation status: `CHARGED_LEPTON_PARTIAL_DERIVATION_CONSOLIDATED`
Overall status: `LEPTON_DRESSING_PARTIAL_DERIVATION_CANDIDATE_ONLY`
Omega status: `LEPTON_OMEGA_STRUCTURALLY_DERIVED_FROM_BOUNDARY_PROJECTOR`
Channel dimension status: `DIM_H_EQUALS_ABS_OMEGA_PARTIAL`
Identity/traceless status: `IDENTITY_TRACELESS_STOCHASTIC_CONDITIONAL`
alpha/pi status: `ALPHA_OVER_PI_STOCHASTIC_STRENGTH_PARTIAL`
Factor-two status: `BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT_STRENGTHENED`
Eta status: `LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT_STRENGTHENED`
Dressing status: `LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL`

## Charged-Lepton Arithmetic

```text
q = k - 2j
Omega_l = -q + 2j
N(k,j) = q^2 + j^2
```

| Mode | (k,j) | q | Omega_l | N | Candidate Z under preferred eta |
| --- | --- | ---: | ---: | ---: | ---: |
| `tau_reference` | `(0,0)` | `0` | `0` | `0` | `1.0` |
| `muon` | `(5,2)` | `1` | `3` | `5` | `0.9897294638168652` |
| `electron` | `(9,3)` | `3` | `3` | `18` | `0.9635170345177995` |

## Channel Space

Preferred dimension route: `cyclic_boundary_monodromy`
Geometric quantization plus-one hazard: `True`

| Quantity | Value |
| --- | ---: |
| dim H_l | `3` |
| dim End(H_l) | `9` |
| identity/common count | `1` |
| traceless active count | `8` |
| active fraction | `8/9` |

## Eta Forms

| Form | eta_l | Claim status |
| --- | ---: | --- |
| no_extra_half | `0.002064728414019306` | preferred repo exponent convention |
| half_factor | `0.001032364207009653` | raw-variance alternative |
| double_factor | `0.004129456828038612` | sensitivity diagnostic |

Preferred eta form: `no_extra_half_repo_exponent_convention`
eta_l=8alpha/(9pi) remains supported: `True`
Factor two closes: `False`
Promotes full lepton 8/9: `False`

## Claim-Status Table

| Link | Status | Statement | Limitation |
| --- | --- | --- | --- |
| `hopf_charge` | `DERIVED_LEDGER_FORMULA` | q=k-2j | This is a supplied framework equation, not a new dynamical derivation. |
| `lepton_omega` | `LEPTON_OMEGA_STRUCTURALLY_DERIVED_FROM_BOUNDARY_PROJECTOR` | For B=0, L=1, T3=-1/2, O_q=-1 and O_j=+2, so Omega_l=-q+2j. | Global A_j normalization and full action-level uniqueness remain open. |
| `lepton_level` | `BOUNDARY_LEVEL_LEDGER_RECOVERED` | The nonzero charged-lepton modes (5,2) and (9,3) both satisfy Omega_l=3. | This does not update official frozen predictions. |
| `cyclic_channel_dimension` | `DIM_H_EQUALS_ABS_OMEGA_PARTIAL` | H_l=C[Z_3] and dim(H_l)=3 under cyclic boundary monodromy. | Ordinary S2 geometric quantization is not used for channel dimension; plus-one hazard remains. |
| `physical_channel_space` | `PHYSICAL_CHANNEL_SPACE_PARTIAL` | Orbit residues are interpreted as physical stochastic boundary channels. | Full stochastic dynamics from the completed action remains open. |
| `endomorphism_algebra` | `END_H_STOCHASTIC_ALGEBRA_PARTIAL` | End(H_l) has dimension 9, with one identity/common channel and eight traceless active channels. | Trace-preserving stochastic generator remains partial/conditional. |
| `active_fraction` | `LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED` | F_l=(3^2-1)/3^2=8/9. | Full Brownian/Lindblad rates on su(3) remain open. |
| `alpha_over_pi` | `ALPHA_OVER_PI_STOCHASTIC_STRENGTH_PARTIAL` | g_U1^2=e^2/(4pi^2)=alpha/pi in rationalized units. | The completed stochastic path-integral role of alpha/pi remains convention-dependent. |
| `brownian_exponential` | `BROWNIAN_GENERATOR_TOPOGRAPHIC_PARTIAL` | Z_l(k,j)=exp[-eta_l N(k,j)] with N=q^2+j^2 is the repo-preferred candidate form. | The full stochastic generator is not derived. |
| `eta_preferred` | `LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT_STRENGTHENED` | Under the repo exponent convention, eta_l=(alpha/pi)(8/9)=8alpha/(9pi). | Half and doubled alternatives remain recorded; this is not official prediction adoption. |
| `factor_two` | `BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT_STRENGTHENED` | The factor-of-two hazard remains convention-dependent. | The completed stochastic measure has not selected D versus g^2. |

## Open Blockers

1. derive primitive finite cyclic quotient from the completed boundary action
2. prove C[Z_|Omega_f|] orbit states are physical boundary channel states from full dynamics
3. derive stochastic residue sampling from completed topographic/BHSM dynamics
4. derive full Brownian/Lindblad generator rates D_a on su(d_f)
5. derive from completed stochastic path integral whether alpha/pi is generator coefficient D or raw variance g^2
6. derive Brownian time/cycle normalization beyond repo convention tau=1
7. fix A_j normalization/global bundle coupling without convention dependence
8. decide later whether lepton dressing belongs in an official v2 prediction set

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No frozen lepton or quark dressing rule is changed.
- No claim is made that BHSM replaces the Standard Model.
- The charged-lepton dressing remains candidate-only.
