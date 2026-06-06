# BHSM Virtual-Environment Dressing Audit

This audit formalizes a diagnostic dressing layer. Canonical BHSM predictions are not changed.

Formula: `(m_i/m_3)_observed_mu = Z_virt^{f,i}(mu) * (m_i/m_3)_BHSM_bare`

## Candidate Dressing Table

| Source | Factor | Applies To | Status | c/t | u/t | s/b | d/b | sin(theta_13) | Adopted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NONE` | `1.0` | `GLOBAL` | `DIAGNOSTIC_ONLY` | `0.008310500554068288` | `1.2690463017606151e-05` | `0.021933971495439474` | `0.0011165200546001757` | `0.0035623676140463315` | `False` |
| `WEAK_DOUBLE_PROJECTION` | `0.5` | `MIDDLE_UP_ONLY` | `DIAGNOSTIC_ONLY` | `0.004155250277034144` | `1.2690463017606151e-05` | `0.021933971495439474` | `0.0011165200546001757` | `0.0035623676140463315` | `False` |
| `AMPLITUDE_PROJECTION` | `0.7071067811865475` | `MIDDLE_UP_ONLY` | `DIAGNOSTIC_ONLY` | `0.005876411296836246` | `1.2690463017606151e-05` | `0.021933971495439474` | `0.0011165200546001757` | `0.0035623676140463315` | `False` |
| `COFRAME_AVERAGE` | `0.3333333333333333` | `ALL_QUARKS` | `DIAGNOSTIC_ONLY` | `0.002770166851356096` | `4.23015433920205e-06` | `0.007311323831813158` | `0.00037217335153339186` | `0.0020567339009220542` | `False` |
| `COFRAME_AMPLITUDE` | `0.5773502691896258` | `ALL_QUARKS` | `DIAGNOSTIC_ONLY` | `0.004798069731991861` | `7.326842239355902e-06` | `0.01266358434728956` | `0.0006446231540790272` | `0.002706814038561922` | `False` |
| `ALPHA_SUPPRESSED` | `0.08542454313184122` | `GLOBAL` | `DIAGNOSTIC_ONLY` | `0.0007099207130281969` | `1.0840770054105326e-06` | `0.0018736994940647452` | `9.537821556175843e-05` | `0.0010411901869545892` | `False` |
| `ALPHA_SUPPRESSED` | `0.17084908626368245` | `GLOBAL` | `DIAGNOSTIC_ONLY` | `0.0014198414260563938` | `2.168154010821065e-06` | `0.0037473989881294904` | `0.00019075643112351687` | `0.0014724652834009586` | `False` |

## BARE vs VIRTUAL_DRESSED_DIAGNOSTIC

| Variant | c/t | u/t | s/b | d/b | sin(theta_13) |
| --- | --- | --- | --- | --- | --- |
| `BHSM_BARE_CANONICAL` | `0.008310500554068288` | `1.2690463017606151e-05` | `0.021933971495439474` | `0.0011165200546001757` | `0.0035623676140463315` |
| `BHSM_VIRTUAL_DRESSED_DIAGNOSTIC` | `0.004155250277034144` | `1.2690463017606151e-05` | `0.021933971495439474` | `0.0011165200546001757` | `0.0035623676140463315` |

## Linkage Test

```json
{
  "j": 0,
  "mode": [
    6,
    0
  ],
  "omega_u": 6,
  "passes": true,
  "q": 6,
  "uses_empirical_residual": false
}
```

## Limitations

- Virtual dressing is formalized as a diagnostic layer only.
- The 1/2 rule is not adopted canonically in this phase.
- Full loop/threshold derivation of virtual dressing remains open.
