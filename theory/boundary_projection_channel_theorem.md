# BHSM Boundary Projection-Channel Theorem Sprint

This sprint tests whether several BHSM candidate correction factors can be organized by protected versus active boundary projection-channel dimensions.
The result is candidate-only: the channel dimensions and algebras are not yet derived from the complete action or spectrum.

## Summary

Theorem status: `BOUNDARY_PROJECTION_CHANNEL_STRUCTURAL_CANDIDATE`
Official outputs modified: `False`
Frozen predictions modified: `False`
PRs opened: `False`
Safe to merge as candidate-only: `True`

## Core Channel Rule

For a candidate sector boundary channel space H_f with dimension d_f:

```text
dim End(H_f) = d_f^2
F_active(d_f) = (d_f^2 - 1) / d_f^2
```

For d=3, `F_active(3)=0.8888888888888888`.

## Component Table

| Blocker | Status | Closed | Structural rule | Computed value |
| --- | --- | --- | --- | --- |
| `lepton_8alpha_9pi` | `LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE` | `False` | eta_l=(alpha/pi)*((Omega_l^2-1)/Omega_l^2), Omega_l=3 | `0.002064728414019306` |
| `pure_fiber_one_half` | `PURE_FIBER_RANK_HALF_STRUCTURAL_CANDIDATE` | `False` | Z_virt^{u,2}=rank(P_phys)/dim(H_fiber)=1/2 for mode (6,0) | `0.5` |
| `ckm_one_sixteenth` | `CKM_1_16_CHANNEL_DILUTION_STRUCTURAL_CANDIDATE` | `False` | Z_mix=Z_mass^(1/dim(End(H_mix))), dim(H_mix)=4 | `0.9576032806985737` |
| `boundary_action` | `BOUNDARY_ACTION_STRUCTURAL_CANDIDATE` | `False` | S_boundary contains lambda_f (Omega_f-Omega_f0)^2 |psi|^2 | `{'lepton_middle': {'sector': 'lepton', 'mode': (5, 2), 'q': 1, 'omega': 3}, 'lepton_light': {'sector': 'lepton', 'mode': (9, 3), 'q': 3, 'omega': 3}, 'up_middle': {'sector': 'up', 'mode': (6, 0), 'q': 6, 'omega': 6}, 'up_light': {'sector': 'up', 'mode': (10, 1), 'q': 8, 'omega': 6}, 'down_middle': {'sector': 'down', 'mode': (6, 3), 'q': 0, 'omega': 12}, 'down_light': {'sector': 'down', 'mode': (8, 2), 'q': 4, 'omega': 12}}` |
| `neutrino_pmns` | `NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE` | `False` | neutral leakage channels may sample broader PMNS mixing spaces than CKM | `{'neutrino_interpretation': 'neutral leakage modes, weakly field-attached and less boundary-pinned', 'boundary_channel_space': 'candidate broad leakage channel space; dimension not derived', 'PMNS_status': 'effective-extension screen only', 'mass_hierarchy_status': 'open', 'ordinary_FTL_claim': False, 'candidate_only': True, 'required_future_inputs': ('neutrino leakage operator', 'neutral mode spectrum', 'PMNS mixing derivation from channel overlap')}` |

## Missing Assumptions

- lepton_8alpha_9pi: derive H_l with dimension Omega_l from the boundary action
- lepton_8alpha_9pi: derive End(H_l) as the stochastic covariance channel algebra
- lepton_8alpha_9pi: derive identity/coherent-channel protection
- lepton_8alpha_9pi: derive Brownian activity only on traceless channels
- pure_fiber_one_half: derive a two-orientation virtual space for nonzero pure-fiber modes
- pure_fiber_one_half: derive rank-one physical mass projection
- pure_fiber_one_half: derive locality to middle-up (6,0) without touching u/t or CKM
- ckm_one_sixteenth: derive dim(H_mix)=4 from internal left-handed overlap channels
- ckm_one_sixteenth: derive End(H_mix) as the correct correlation algebra
- ckm_one_sixteenth: derive that mass dressing dilutes across all 16 channels
- ckm_one_sixteenth: derive Z_mass=1/2 independently before using it in CKM
- boundary_action: derive the boundary penalty term by variation of the complete action
- boundary_action: derive sector signs and base/fiber coefficients rather than inserting them
- boundary_action: derive primitive constant boundary levels as stationary non-heavy modes
- boundary_action: link channel dimension d_f to Omega_f without circular use of selected modes
- neutrino_pmns: derive neutral leakage channel space
- neutrino_pmns: derive PMNS angles or mass splittings from the leakage operator
- neutrino_pmns: derive mass hierarchy rather than using effective screens

## Boundary Operator Values

| Mode label | Sector | Mode | q | Omega |
| --- | --- | --- | ---: | ---: |
| `lepton_middle` | `lepton` | `(5, 2)` | 1 | 3 |
| `lepton_light` | `lepton` | `(9, 3)` | 3 | 3 |
| `up_middle` | `up` | `(6, 0)` | 6 | 6 |
| `up_light` | `up` | `(10, 1)` | 8 | 6 |
| `down_middle` | `down` | `(6, 3)` | 0 | 12 |
| `down_light` | `down` | `(8, 2)` | 4 | 12 |

## Neutrino/PMNS Leakage Ledger

- `neutrino_interpretation`: `neutral leakage modes, weakly field-attached and less boundary-pinned`
- `boundary_channel_space`: `candidate broad leakage channel space; dimension not derived`
- `PMNS_status`: `effective-extension screen only`
- `mass_hierarchy_status`: `open`
- `ordinary_FTL_claim`: `False`
- `candidate_only`: `True`
- `required_future_inputs`: `('neutrino leakage operator', 'neutral mode spectrum', 'PMNS mixing derivation from channel overlap')`

## Claim Discipline

- No official frozen outputs are changed.
- No retuning is performed.
- No ordinary superluminal neutrino claim is made.
- No ordinary environmental mass drift claim is made.
- No claim of replacing the Standard Model or proving BHSM is made.
- All mechanisms remain candidate-only unless the missing assumptions are later derived.
