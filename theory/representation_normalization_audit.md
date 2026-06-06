# BHSM Representation-Normalization Audit

This audit evaluates candidate factors without tuning or adoption.

Required factor for threshold-aware c/t: `0.5115900067973103`

## Candidate Factors

| Source Rule | Factor | Applies To | c/t | c/t Relative Error | u/t | sin(theta_13) | Status | Adopted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `NONE` | `1.0` | `all_modes` | `0.008310500554068288` | `0.9546902533539826` | `1.2690463017606151e-05` | `0.0035623676140463315` | `DIAGNOSTIC_ONLY` | `False` |
| `WEAK_DOUBLE_PROJECTION` | `0.5` | `pure_fiber_up_nonzero_j0` | `0.004155250277034144` | `0.0226548733230087` | `1.2690463017606151e-05` | `0.0035623676140463315` | `DIAGNOSTIC_ONLY` | `False` |
| `AMPLITUDE_PROJECTION` | `0.7071067811865475` | `pure_fiber_up_nonzero_j0` | `0.005876411296836246` | `0.3821747332658516` | `1.2690463017606151e-05` | `0.0035623676140463315` | `DIAGNOSTIC_ONLY` | `False` |
| `COFRAME_AVERAGE` | `0.3333333333333333` | `all_quark_modes` | `0.002770166851356096` | `0.34843658221533913` | `4.23015433920205e-06` | `0.0020567339009220542` | `DIAGNOSTIC_ONLY` | `False` |
| `COFRAME_AMPLITUDE` | `0.5773502691896258` | `all_quark_modes` | `0.004798069731991861` | `0.12854094395625976` | `7.326842239355902e-06` | `0.002706814038561922` | `DIAGNOSTIC_ONLY` | `False` |
| `ALPHA_SUPPRESSED` | `0.08542454313184122` | `all_nonzero_modes` | `0.0007099207130281969` | `0.833021478142973` | `1.0840770054105326e-06` | `0.0010411901869545892` | `DIAGNOSTIC_ONLY` | `False` |
| `ALPHA_SUPPRESSED` | `0.17084908626368245` | `all_nonzero_modes` | `0.0014198414260563938` | `0.6660429562859461` | `2.168154010821065e-06` | `0.0014724652834009586` | `DIAGNOSTIC_ONLY` | `False` |

## Scope Diagnostics for Factor 1/2

| Scope | c/t | c/t Relative Error | u/t | u/t Relative Error | sin(theta_13) | Adopted |
| --- | --- | --- | --- | --- | --- | --- |
| `middle_up_mode_only` | `0.004155250277034144` | `0.0226548733230087` | `1.2690463017606151e-05` | `0.6129642273365508` | `0.0035623676140463315` | `False` |
| `pure_fiber_up_nonzero_j0` | `0.004155250277034144` | `0.0226548733230087` | `1.2690463017606151e-05` | `0.6129642273365508` | `0.0035623676140463315` | `False` |
| `all_up_sector_modes` | `0.004155250277034144` | `0.0226548733230087` | `6.3452315088030755e-06` | `0.19351788633172462` | `0.0025189742969715027` | `False` |
| `all_quark_modes` | `0.004155250277034144` | `0.0226548733230087` | `6.3452315088030755e-06` | `0.19351788633172462` | `0.0025189742969715027` | `False` |
| `no_modes` | `0.008310500554068288` | `0.9546902533539826` | `1.2690463017606151e-05` | `0.6129642273365508` | `0.0035623676140463315` | `False` |

## Conclusion

The 1/2 factor is numerically suggestive for c/t but remains DIAGNOSTIC_ONLY. No implemented representation rule independently forces adoption.

## Limitations

- No empirical residual is used to select or adopt a factor.
- No canonical ratio, geometry, S, or mode ledger is changed.
- Action-level derivation of any representation normalization remains open.
