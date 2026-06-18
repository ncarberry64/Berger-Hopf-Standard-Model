# BHSM Sector Projector Derivation From SM Ledger

This sprint tests whether the boundary coefficients can be read from unchanged Standard Model representation data.
The result is partial: `a=3B-L` and the T3 part of `b` are supported, while the down-type coframe bonus remains a structural candidate.

## Summary

Sector projector status: `SECTOR_PROJECTOR_PARTIAL_DERIVATION`
q coefficient status: `Q_COEFFICIENT_3B_MINUS_L_SUPPORTED`
j coefficient status: `J_COEFFICIENT_T3_PARTIAL`
Down coframe bonus status: `DOWN_COFRAME_BONUS_STRUCTURAL_CANDIDATE`
Coefficient origin status: `COEFFICIENT_ORIGIN_PARTIAL`
Formula reproduces Omega_l,u,d: `True`
q follows from 3B-L: `True`
j follows from T3: `True`
Down bonus follows independently: `False`

## Formula

```text
Omega_f = (3B_f - L_f) q + (-4 T3_f + 2 chi_d,f) j
```

## Coefficients

| Sector | a | b | Status |
| --- | ---: | ---: | --- |
| `charged_lepton` | `-1` | `2` | `COEFFICIENT_ORIGIN_PARTIAL` |
| `up` | `1` | `-2` | `COEFFICIENT_ORIGIN_PARTIAL` |
| `down` | `1` | `4` | `COEFFICIENT_ORIGIN_PARTIAL` |
| `neutrino` | `-1` | `-2` | `NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE` |

## Mode Pair Checks

| Sector | Constant | Level |
| --- | --- | ---: |
| `charged_lepton` | `True` | `3` |
| `up` | `True` | `6` |
| `down` | `True` | `12` |

## Missing Assumptions

- derive chi_d from the full color/coframe boundary connection rather than assigning a down indicator
- derive b=-4T3+2chi_d from the connection/action rather than a representation-shaped formula
- derive the sector projector P_f as an operator acting on A_boundary
- derive cyclic quotient dimension dim(H)=|Omega| separately
- derive identity/traceless protection before promoting lepton 8/9

## Neutrino Consequence

The same formula gives the candidate neutral-lepton projector `Omega_nu=-q-2j`.
This is candidate-only: no neutrino mode ledger or numerical PMNS claim is added.

## Claim Discipline

- No official frozen outputs are changed.
- No retuning is performed.
- No ordinary superluminal neutrino claim is made.
- No ordinary environmental mass drift claim is made.
- No claim of replacing the Standard Model or proving BHSM is made.
- No claim of a complete first-principles Standard Model derivation is made.
