# Gauge and Field Ledger

The working model card records the Standard Model gauge group:

```text
SU(3)_c x SU(2)_L x U(1)_Y
```

The field ledger is:

| Field | Chirality | SU(3) | SU(2) | Y | Generations |
| --- | --- | --- | --- | --- | --- |
| `Q_L` | left | `3` | `2` | `1/6` | 3 |
| `u_R` | right | `3` | `1` | `2/3` | 3 |
| `d_R` | right | `3` | `1` | `-1/3` | 3 |
| `L_L` | left | `1` | `2` | `-1/2` | 3 |
| `e_R` | right | `1` | `1` | `-1` | 3 |
| `H` | scalar | `1` | `2` | `1/2` | profile `Phi(y)` |

The repository test suite verifies anomaly cancellation within this admitted
ledger. The ledger is a conditional BHSM input/output consistency layer; it is
not presented here as a rigorous derivation of the Standard Model from pure
geometry alone.

The symbolic low-energy Lagrangian blocks retained in the model card are the
usual gauge, fermion kinetic, Higgs, Yukawa, effective neutrino, and
topographic/internal sectors. The neutrino sector is treated as an effective
extension rather than as part of the minimal Standard Model.
