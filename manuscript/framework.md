# Framework

BHSM = Berger–Hopf Standard Model.

The Berger–Hopf Standard Model is a no-retuning, alpha-anchored geometric
reinterpretation framework for Standard Model flavor, couplings, generations,
and electroweak-scale structure.

## Frozen Constants

The v1.0 freeze fixes:

| Quantity | Frozen Value | Status |
| --- | --- | --- |
| Berger anisotropy | `a = alpha^{-1}/(12*pi^2) = 1.157054135733433` | alpha-anchored canonical geometry |
| Universal overlap width | `S = 1/(4*pi) = 0.07957747154594767` | frozen overlap width |

The alpha-anchored geometry is selected by the theory-side rule recorded in
the model card: the BHSM scale sector contains
`epsilon_alpha = alpha^{-1}/(12*pi^2) - 1`. It is not selected by residual
minimization.

## Fixed Mode Ledger

| Sector | Heavy | Middle | Light |
| --- | --- | --- | --- |
| charged leptons | `(0,0)` | `(5,2)` | `(9,3)` |
| up quarks | `(0,0)` | `(6,0)` | `(10,1)` |
| down quarks | `(0,0)` | `(6,3)` | `(8,2)` |

The Hopf charge is `q = k - 2j`. The mode ledger is frozen and is not modified
in this manuscript.

## Overlap Rule

Charged-sector ratios are generated from the internal overlap form already
implemented in the repository:

```text
m_i/m_3 = exp[-S lambda_{k,j}]
```

where the Berger scalar spectrum proxy used for the overlap ledger is:

```text
lambda_{k,j}(a) = a^2 (k - 2j)^2 + 2((2j + 1)k - 2j^2)
```

The resulting numbers are screens from the frozen internal ledger, not fitted
mass parameters.
