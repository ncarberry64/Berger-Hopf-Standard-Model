# BHSM Mass Scheme Audit

This audit structures mass-reference comparisons. It does not run QCD, fetch external data, tune masses, or change BHSM predictions.

## Ratio References

| Scheme Set | Ratio | Reference | Scheme | Scale | Scheme Consistent | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| MIXED_DEFAULT | `charged_leptons.middle` | `0.05946353426831603` | `pole` | `on-shell` | `True` | Charged lepton reference; scheme-stable for this audit.<br>Scheme-consistent comparison. |
| MIXED_DEFAULT | `charged_leptons.light` | `0.0002875853753250115` | `pole` | `on-shell` | `True` | Charged lepton reference; scheme-stable for this audit.<br>Scheme-consistent comparison. |
| MIXED_DEFAULT | `up_quarks.middle` | `0.007354218541895883` | `MSbar_mixed/mixed_top_reference` | `self-scale charm-reference/top mass reference` | `False` | Current repo value; not run to a common top scale.<br>Current repo value; mixed with light-quark references.<br>Scheme-sensitive comparison; common-scale running remains open. |
| MIXED_DEFAULT | `up_quarks.light` | `1.2507962244484336e-05` | `MSbar_mixed/mixed_top_reference` | `2 GeV light-reference/top mass reference` | `False` | Current repo value; not run to a common top scale.<br>Current repo value; mixed with light-quark references.<br>Scheme-sensitive comparison; common-scale running remains open. |
| MIXED_DEFAULT | `down_quarks.middle` | `0.022344497607655504` | `MSbar_mixed` | `2 GeV strange-reference/bottom self-scale reference` | `False` | Current repo value; not run to a common bottom scale.<br>Current repo value; mixed with light-quark references.<br>Scheme-sensitive comparison; common-scale running remains open. |
| MIXED_DEFAULT | `down_quarks.light` | `0.0011172248803827751` | `MSbar_mixed` | `2 GeV light-reference/bottom self-scale reference` | `False` | Current repo value; not run to a common bottom scale.<br>Current repo value; mixed with light-quark references.<br>Scheme-sensitive comparison; common-scale running remains open. |
| COMMON_SCALE_PLACEHOLDER | `charged_leptons.middle` | `0.05946353426831603` | `COMMON_SCALE_PLACEHOLDER` | `OPEN_COMMON_SCALE_RUNNING_NOT_IMPLEMENTED` | `False` | Placeholder only; values are not QCD-run to a common scale.<br>Do not interpret this as a completed common-scale mass scheme.<br>Scheme-sensitive comparison; common-scale running remains open. |
| COMMON_SCALE_PLACEHOLDER | `charged_leptons.light` | `0.0002875853753250115` | `COMMON_SCALE_PLACEHOLDER` | `OPEN_COMMON_SCALE_RUNNING_NOT_IMPLEMENTED` | `False` | Placeholder only; values are not QCD-run to a common scale.<br>Do not interpret this as a completed common-scale mass scheme.<br>Scheme-sensitive comparison; common-scale running remains open. |
| COMMON_SCALE_PLACEHOLDER | `up_quarks.middle` | `0.007354218541895883` | `COMMON_SCALE_PLACEHOLDER` | `OPEN_COMMON_SCALE_RUNNING_NOT_IMPLEMENTED` | `False` | Placeholder only; values are not QCD-run to a common scale.<br>Do not interpret this as a completed common-scale mass scheme.<br>Scheme-sensitive comparison; common-scale running remains open. |
| COMMON_SCALE_PLACEHOLDER | `up_quarks.light` | `1.2507962244484336e-05` | `COMMON_SCALE_PLACEHOLDER` | `OPEN_COMMON_SCALE_RUNNING_NOT_IMPLEMENTED` | `False` | Placeholder only; values are not QCD-run to a common scale.<br>Do not interpret this as a completed common-scale mass scheme.<br>Scheme-sensitive comparison; common-scale running remains open. |
| COMMON_SCALE_PLACEHOLDER | `down_quarks.middle` | `0.022344497607655504` | `COMMON_SCALE_PLACEHOLDER` | `OPEN_COMMON_SCALE_RUNNING_NOT_IMPLEMENTED` | `False` | Placeholder only; values are not QCD-run to a common scale.<br>Do not interpret this as a completed common-scale mass scheme.<br>Scheme-sensitive comparison; common-scale running remains open. |
| COMMON_SCALE_PLACEHOLDER | `down_quarks.light` | `0.0011172248803827751` | `COMMON_SCALE_PLACEHOLDER` | `OPEN_COMMON_SCALE_RUNNING_NOT_IMPLEMENTED` | `False` | Placeholder only; values are not QCD-run to a common scale.<br>Do not interpret this as a completed common-scale mass scheme.<br>Scheme-sensitive comparison; common-scale running remains open. |

## Limitations

- No external mass data are fetched.
- COMMON_SCALE_PLACEHOLDER reuses current values and does not implement QCD running.
- Quark cross-generation comparisons remain scheme-sensitive until common-scale running is supplied.
