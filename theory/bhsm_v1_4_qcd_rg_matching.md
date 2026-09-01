# BHSM v1.4 QCD/RG Matching Scaffold

Theorem complete: `False`
Predictions changed: `False`
Stop condition triggered: `False`

## Reference Sets

| Set | Status | Scheme consistent | Final comparison | Notes |
| --- | --- | --- | --- | --- |
| `MIXED_DEFAULT` | `SCHEME_SENSITIVE_BASELINE` | `False` | `False` | Current repository mass inputs are mixed across schemes/scales for quark ratios.<br>Use for continuity with frozen residual ledgers, not final QCD comparison. |
| `COMMON_SCALE_APPROX` | `APPROXIMATE_RUNNING_SCAFFOLD` | `True` | `False` | Fixed-nf one-loop-inspired common-scale scaffold.<br>Not precision QCD; no final tolerance verdict should be based on this alone. |
| `THRESHOLD_AWARE_APPROX` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` | `True` | `False` | Piecewise-nf approximate scaffold with threshold labels.<br>Still not precision QCD and not a final scheme-consistent reference set. |
| `PRECISION_QCD_PLACEHOLDER` | `PLACEHOLDER_NOT_COMPUTED` | `False` | `False` | Future two-/three-loop threshold-matched reference set.<br>Contains no precision numerical masses in this phase. |

## Comparison Rows

| Branch | Quantity | Predicted | Reference | Relative Error | Scheme Set | Status | Final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `BHSM_BARE_V1` | `c/t` | `0.008310500554068288` | `0.007354218541895883` | `0.13003176431657681` | `MIXED_DEFAULT` | `SCHEME_SENSITIVE_BASELINE` | `False` |
| `BHSM_BARE_V1` | `u/t` | `1.2690463017606151e-05` | `1.2507962244484336e-05` | `0.014590767828891764` | `MIXED_DEFAULT` | `SCHEME_SENSITIVE_BASELINE` | `False` |
| `BHSM_BARE_V1` | `s/b` | `0.021933971495439474` | `0.022344497607655504` | `0.018372581895749498` | `MIXED_DEFAULT` | `SCHEME_SENSITIVE_BASELINE` | `False` |
| `BHSM_BARE_V1` | `d/b` | `0.0011165200546001757` | `0.0011172248803827751` | `0.0006308718996286248` | `MIXED_DEFAULT` | `SCHEME_SENSITIVE_BASELINE` | `False` |
| `BHSM_DRESSED_V1_CANDIDATE` | `c/t` | `0.004155250277034144` | `0.007354218541895883` | `0.4349841178417116` | `MIXED_DEFAULT` | `SCHEME_SENSITIVE_BASELINE` | `False` |
| `BHSM_BARE_V1` | `c/t` | `0.008310500554068288` | `0.004266868071316746` | `0.9476816285776762` | `COMMON_SCALE_APPROX` | `APPROXIMATE_RUNNING_SCAFFOLD` | `False` |
| `BHSM_BARE_V1` | `u/t` | `1.2690463017606151e-05` | `7.876511100850345e-06` | `0.6111782050603717` | `COMMON_SCALE_APPROX` | `APPROXIMATE_RUNNING_SCAFFOLD` | `False` |
| `BHSM_BARE_V1` | `s/b` | `0.021933971495439474` | `0.020007279304305587` | `0.09629955986665618` | `COMMON_SCALE_APPROX` | `APPROXIMATE_RUNNING_SCAFFOLD` | `False` |
| `BHSM_BARE_V1` | `d/b` | `0.0011165200546001757` | `0.0010003639652152794` | `0.11611382799049477` | `COMMON_SCALE_APPROX` | `APPROXIMATE_RUNNING_SCAFFOLD` | `False` |
| `BHSM_DRESSED_V1_CANDIDATE` | `c/t` | `0.004155250277034144` | `0.004266868071316746` | `0.026159185711161905` | `COMMON_SCALE_APPROX` | `APPROXIMATE_RUNNING_SCAFFOLD` | `False` |
| `BHSM_BARE_V1` | `c/t` | `0.008310500554068288` | `0.004251569034944846` | `0.9546902533539826` | `THRESHOLD_AWARE_APPROX` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` | `False` |
| `BHSM_BARE_V1` | `u/t` | `1.2690463017606151e-05` | `7.867789503652917e-06` | `0.6129642273365508` | `THRESHOLD_AWARE_APPROX` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` | `False` |
| `BHSM_BARE_V1` | `s/b` | `0.021933971495439474` | `0.019985125405342665` | `0.09751482918269905` | `THRESHOLD_AWARE_APPROX` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` | `False` |
| `BHSM_BARE_V1` | `d/b` | `0.0011165200546001757` | `0.0009992562702671331` | `0.11735106180689185` | `THRESHOLD_AWARE_APPROX` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` | `False` |
| `BHSM_DRESSED_V1_CANDIDATE` | `c/t` | `0.004155250277034144` | `0.004251569034944846` | `0.0226548733230087` | `THRESHOLD_AWARE_APPROX` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` | `False` |
| `BHSM_BARE_V1` | `c/t` | `0.008310500554068288` | `None` | `None` | `PRECISION_QCD_PLACEHOLDER` | `PLACEHOLDER_NOT_COMPUTED` | `False` |
| `BHSM_BARE_V1` | `u/t` | `1.2690463017606151e-05` | `None` | `None` | `PRECISION_QCD_PLACEHOLDER` | `PLACEHOLDER_NOT_COMPUTED` | `False` |
| `BHSM_BARE_V1` | `s/b` | `0.021933971495439474` | `None` | `None` | `PRECISION_QCD_PLACEHOLDER` | `PLACEHOLDER_NOT_COMPUTED` | `False` |
| `BHSM_BARE_V1` | `d/b` | `0.0011165200546001757` | `None` | `None` | `PRECISION_QCD_PLACEHOLDER` | `PLACEHOLDER_NOT_COMPUTED` | `False` |
| `BHSM_DRESSED_V1_CANDIDATE` | `c/t` | `0.004155250277034144` | `None` | `None` | `PRECISION_QCD_PLACEHOLDER` | `PLACEHOLDER_NOT_COMPUTED` | `False` |

## Stop-Condition Assessment

No final scheme-consistent precision-QCD reference set is available in this scaffold; therefore no Gate 2 structural stop is triggered.

## Limitations

- MIXED_DEFAULT is scheme-sensitive.
- COMMON_SCALE_APPROX and THRESHOLD_AWARE_APPROX are approximate scaffolds, not final precision QCD.
- PLACEHOLDER_PRECISION_QCD is intentionally not computed.
- BHSM frozen predictions are compared but not changed.
