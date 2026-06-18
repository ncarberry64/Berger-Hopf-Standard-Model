# BHSM Colored Lower-Doublet Coframe Bonus

This sprint tests whether the independent down-sector `chi_d` flag can be replaced by the SM-ledger projector `(3B)(1/2-T3)`.
The result is partial: the formula exactly selects colored lower-doublet modes, but the full coframe/action operator remains open.

## Summary

Colored lower projector status: `COLORED_LOWER_PROJECTOR_PARTIAL_DERIVATION`
Down coframe bonus status: `DOWN_COFAME_BONUS_PARTIAL_DERIVATION`
q coefficient status: `Q_COEFFICIENT_3B_MINUS_L_SUPPORTED`
j coefficient status: `J_COEFFICIENT_T3_COLOR_LOWER_PARTIAL`
chi_d follows from B,T3: `True`
Formula reproduces Omega_l,u,d: `True`
Strictly closes down bonus: `False`

## Projector

```text
chi_colored_lower = (3B)(1/2 - T3)
b_f = -4T3 + 2(3B)(1/2 - T3)
Omega_f = (3B-L)q + b_f j
```

## Coefficients

| Sector | a | b | chi colored lower |
| --- | ---: | ---: | ---: |
| `charged_lepton` | `-1` | `2` | `0` |
| `up` | `1` | `-2` | `0` |
| `down` | `1` | `4` | `1` |
| `neutrino` | `-1` | `-2` | `0` |

## Mode Pair Checks

| Sector | Constant | Level |
| --- | --- | ---: |
| `charged_lepton` | `True` | `3` |
| `up` | `True` | `6` |
| `down` | `True` | `12` |

## Missing Assumptions

- derive 3B as the actual coframe/color multiplicity operator inside A_boundary
- derive lower_doublet_projector(T3)=1/2-T3 as a boundary projector, not only SM bookkeeping
- derive the product (3B)(1/2-T3) from the full color/coframe boundary connection
- derive cyclic quotient dimension dim(H)=|Omega| separately
- derive identity/traceless protection before promoting lepton 8/9

## Claim Discipline

- No official frozen outputs are changed.
- No retuning is performed.
- No ordinary superluminal neutrino claim is made.
- No ordinary environmental mass drift claim is made.
- No claim of replacing the Standard Model or proving BHSM is made.
- No claim of a complete first-principles Standard Model derivation is made.
