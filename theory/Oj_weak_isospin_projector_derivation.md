# O_j Weak-Isospin Projector Derivation

This audit tests whether a symbolic boundary action can support the representation-valued connection `A_rep=A_q tensor O_q + A_j tensor O_j`. The result is partial and candidate-safe.

## Status

Boundary action to A_rep: `BOUNDARY_ACTION_TO_A_REP_PARTIAL`
Boundary source terms: `BOUNDARY_SOURCE_TERMS_STRUCTURAL_CANDIDATE`
O_q status: `O_Q_BOUNDARY_CHARGE_PARTIAL`
O_j status: `O_J_WEAK_ISOSPIN_PROJECTOR_PARTIAL`
Colored lower projector: `COLORED_LOWER_PROJECTOR_DERIVED_LEDGER_ARITHMETIC`
A_q period: `A_Q_PERIOD_NORMALIZATION_SUPPORTED`
A_j period: `A_J_PERIOD_NORMALIZATION_CONVENTION_DEPENDENT`
Sector connection: `SECTOR_CONNECTION_PARTIAL`
Action-to-phase-map: `ACTION_VARIATION_TO_PHASE_MAP_PARTIAL`
Omega-as-degree: `OMEGA_AS_DEGREE_PARTIAL`

## Boundary Source-Term Scaffold

```text
S_boundary[f] = integral_{S1} Psi_f^dagger [d + i A_q O_q + i A_j O_j] Psi_f
A_f = O_q^(f) A_q + O_j^(f) A_j
u_f(s) = exp(i integral A_f)
deg(u_f) = (1/2pi) integral A_f
```

## Sector Operators

| Sector | O_q | O_j | Connection |
| --- | ---: | ---: | --- |
| `charged_lepton` | `-1` | `2` | `A_f = (-1) A_q + (2) A_j` |
| `up` | `1` | `-2` | `A_f = (1) A_q + (-2) A_j` |
| `down` | `1` | `4` | `A_f = (1) A_q + (4) A_j` |

## Mode Checks

| Mode | Omega |
| --- | ---: |
| `lepton_muon` | `3` |
| `lepton_electron` | `3` |
| `up_middle` | `6` |
| `up_light` | `6` |
| `down_middle` | `12` |
| `down_light` | `12` |

## Period-Degree Checks

| Case | Degree |
| --- | ---: |
| `lepton_muon` | `3` |
| `lepton_electron` | `3` |
| `up_middle` | `6` |
| `up_light` | `6` |
| `down_middle` | `12` |
| `down_light` | `12` |

## Claim Boundaries

Promotes full BHSM: `False`
Claims full SM derivation: `False`
Changes official predictions: `False`

## Open Blockers

1. full BHSM boundary action is not yet completed
2. A_rep may remain partial because source terms are scaffolded
3. A_q period normalization is stronger than A_j but still part of an incomplete action derivation
4. A_j normalization/global bundle coupling remains convention-dependent
5. degree theorem remains partial until normalized periods are fully action-derived
6. coherent residue sheets and stochastic response selector remain downstream partial/candidate structures
7. no official predictions change
8. full Standard Model derivation is not claimed

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No frozen lepton, quark, CKM, or down-sector rule is changed.
- No claim is made that BHSM replaces the Standard Model.
- The result remains partial/candidate until the completed boundary action is derived.
