# BHSM Residual Audit

This is a diagnostic residual audit. No model parameters are tuned in this phase.

| Prediction ID | Sector | Quantity | Predicted | Reference | Relative Error | Log Error | Severity | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `mass_ratio.charged_leptons.heavy` | fermion_mass_ratios | charged_leptons.heavy/reference | `1.0` | `1.0` | 0 | 0 | `EXACT_OR_STATUS` | Computed from internal overlap modes; numerical agreement is a screen, not a final prediction.<br>Mass reference is scheme-stable for this audit.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `mass_ratio.charged_leptons.middle` | fermion_mass_ratios | charged_leptons.middle/heavy | `0.06007447093260976` | `0.05946353426831603` | 0.0102741398037 | 0.00443923640573 | `GOOD` | Computed from internal overlap modes; numerical agreement is a screen, not a final prediction.<br>Mass reference is scheme-stable for this audit.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `mass_ratio.charged_leptons.light` | fermion_mass_ratios | charged_leptons.light/heavy | `0.00029729106456492414` | `0.0002875853753250115` | 0.0337488971021 | 0.0144150592158 | `GOOD` | Computed from internal overlap modes; numerical agreement is a screen, not a final prediction.<br>Mass reference is scheme-stable for this audit.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `mass_ratio.up_quarks.heavy` | fermion_mass_ratios | up_quarks.heavy/reference | `1.0` | `1.0` | 0 | 0 | `EXACT_OR_STATUS` | Computed from internal overlap modes; numerical agreement is a screen, not a final prediction.<br>Mass reference is scheme-stable for this audit.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `mass_ratio.up_quarks.middle` | fermion_mass_ratios | up_quarks.middle/heavy | `0.008310500554068288` | `0.007354218541895883` | 0.130031764317 | 0.0530906513361 | `SCHEME_SENSITIVE` | Computed from internal overlap modes; numerical agreement is a screen, not a final prediction.<br>Quark mass references are scheme-sensitive unless a common-scale running scheme is supplied.<br>Quark mass ratio residual is scheme-sensitive because no consistent quark mass-scheme treatment is implemented.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `mass_ratio.up_quarks.light` | fermion_mass_ratios | up_quarks.light/heavy | `1.2690463017606151e-05` | `1.2507962244484336e-05` | 0.0145907678289 | 0.0062909061785 | `SCHEME_SENSITIVE` | Computed from internal overlap modes; numerical agreement is a screen, not a final prediction.<br>Quark mass references are scheme-sensitive unless a common-scale running scheme is supplied.<br>Quark mass ratio residual is scheme-sensitive because no consistent quark mass-scheme treatment is implemented.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `mass_ratio.down_quarks.heavy` | fermion_mass_ratios | down_quarks.heavy/reference | `1.0` | `1.0` | 0 | 0 | `EXACT_OR_STATUS` | Computed from internal overlap modes; numerical agreement is a screen, not a final prediction.<br>Mass reference is scheme-stable for this audit.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `mass_ratio.down_quarks.middle` | fermion_mass_ratios | down_quarks.middle/heavy | `0.021933971495439474` | `0.022344497607655504` | 0.0183725818957 | -0.00805331971353 | `SCHEME_SENSITIVE` | Computed from internal overlap modes; numerical agreement is a screen, not a final prediction.<br>Quark mass references are scheme-sensitive unless a common-scale running scheme is supplied.<br>Quark mass ratio residual is scheme-sensitive because no consistent quark mass-scheme treatment is implemented.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `mass_ratio.down_quarks.light` | fermion_mass_ratios | down_quarks.light/heavy | `0.0011165200546001757` | `0.0011172248803827751` | 0.000630871899629 | -0.000274070645624 | `SCHEME_SENSITIVE` | Computed from internal overlap modes; numerical agreement is a screen, not a final prediction.<br>Quark mass references are scheme-sensitive unless a common-scale running scheme is supplied.<br>Quark mass ratio residual is scheme-sensitive because no consistent quark mass-scheme treatment is implemented.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `ckm.sin_theta_12` | ckm | sin_theta_12 | `0.2256184580048353` | `0.22497` | 0.0028824198997 | 0.00125001838226 | `EXCELLENT` | Canonical flavor matrix uses internal-rule mass ratios and Hopf phase CP screen; full action derivation of Omega_f remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `ckm.sin_theta_23` | ckm | sin_theta_23 | `0.04386794299087895` | `0.04108` | 0.067866187704 | 0.0285168354803 | `MODERATE` | Canonical flavor matrix uses internal-rule mass ratios and Hopf phase CP screen; full action derivation of Omega_f remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `ckm.sin_theta_13` | ckm | sin_theta_13 | `0.0035623676140463315` | `0.00382` | 0.0674430329722 | -0.030324628999 | `MODERATE` | Canonical flavor matrix uses internal-rule mass ratios and Hopf phase CP screen; full action derivation of Omega_f remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `ckm.matrix_magnitudes` | ckm | |V_CKM| | `[[0.9742095600721029, 0.22561702639894465, 0.0035623676140463315], [0.2254664853946855, 0.9732628072432431, 0.04386766463774175], [0.008977584746899065, 0.04308671994825354, 0.9990309992869156]]` | `None` |  |  | `EXACT_OR_STATUS` | Canonical flavor matrix uses internal-rule mass ratios and Hopf phase CP screen; full action derivation of Omega_f remains open.<br>No numeric reference residual is available for this row. |
| `ckm.delta_cp` | ckm | delta_cp | `1.1283791670955126` | `1.196` | 0.0565391579469 | -0.0252761203355 | `MODERATE` | Canonical flavor matrix uses internal-rule mass ratios and Hopf phase CP screen; full action derivation of Omega_f remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `ckm.jarlskog` | ckm | J_CKM | `3.1011702945437805e-05` | `3e-05` | 0.0337234315146 | 0.0144043605825 | `GOOD` | Canonical flavor matrix uses internal-rule mass ratios and Hopf phase CP screen; full action derivation of Omega_f remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `pmns_effective.sin2_theta_13` | pmns_effective | sin2_theta_13 | `0.021892057707851405` | `0.0222` | 0.0138712744211 | -0.00606639017073 | `GOOD` | PMNS rows use an effective neutrino-sector extension; neutrino masses are not part of the minimal Standard Model ledger.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `pmns_effective.sin2_theta_12` | pmns_effective | sin2_theta_12 | `0.3114412756254819` | `0.307` | 0.0144666958485 | 0.00623779405379 | `GOOD` | PMNS rows use an effective neutrino-sector extension; neutrino masses are not part of the minimal Standard Model ledger.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `pmns_effective.sin2_theta_23` | pmns_effective | sin2_theta_23 | `0.5437841154157028` | `0.558` | 0.0254764956708 | -0.011207681762 | `GOOD` | PMNS rows use an effective neutrino-sector extension; neutrino masses are not part of the minimal Standard Model ledger.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `pmns_effective.delta_m2_21_over_delta_m2_31` | pmns_effective | delta_m2_21_over_delta_m2_31 | `0.029189410277135206` | `0.02947953913388955` | 0.00984170259368 | -0.00429536884245 | `EXCELLENT` | PMNS rows use an effective neutrino-sector extension; neutrino masses are not part of the minimal Standard Model ledger.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `gauge_couplings.alpha_1` | gauge_couplings | alpha_1 | `0.01688686394038963` | `None` |  |  | `EXACT_OR_STATUS` | Geometric couplings are electroweak-scale matching screens; full threshold RG matching remains open.<br>No numeric reference residual is available for this row. |
| `gauge_couplings.alpha_2` | gauge_couplings | alpha_2 | `0.03377372788077926` | `None` |  |  | `EXACT_OR_STATUS` | Geometric couplings are electroweak-scale matching screens; full threshold RG matching remains open.<br>No numeric reference residual is available for this row. |
| `gauge_couplings.alpha_3` | gauge_couplings | alpha_3 | `0.1182080475827274` | `0.1179` | 0.00261278696122 | 0.00113323914726 | `EXCELLENT` | Geometric couplings are electroweak-scale matching screens; full threshold RG matching remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `gauge_couplings.sin2_theta_w` | gauge_couplings | sin2_theta_w | `0.23076923076923078` | `0.23122` | 0.00194952526066 | -0.000847494437623 | `EXCELLENT` | Geometric couplings are electroweak-scale matching screens; full threshold RG matching remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `gauge_couplings.alpha_em_inv_mew` | gauge_couplings | alpha_em_inv_mew | `128.30485721416164` | `127.95` | 0.0027734053471 | 0.0012028074719 | `EXCELLENT` | Geometric couplings are electroweak-scale matching screens; full threshold RG matching remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `higgs_electroweak.v` | higgs_electroweak | v | `246.16986520825228` | `246.21965` | 0.00020219666362 | -8.78217742036e-05 | `EXCELLENT` | Electroweak scale output is a numerical screen, not an independent proof.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `higgs_electroweak.m_H_approx_v_over_2` | higgs_electroweak | m_H_approx_v_over_2 | `123.08493260412614` | `125.1` | 0.0161076530446 | -0.00705241750451 | `GOOD` | Electroweak scale output is a numerical screen, not an independent proof.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `higgs_electroweak.M_lift` | higgs_electroweak | M_lift | `9718.396740299762` | `None` |  |  | `EXACT_OR_STATUS` | Electroweak scale output is a numerical screen, not an independent proof.<br>No numeric reference residual is available for this row. |
| `ht_gap.first_complement_eigenvalue` | ht_gap | first_complement_eigenvalue | `1.4630400252994733` | `None` |  |  | `EXACT_OR_STATUS` | Level 2 finite-basis H_T proxy; full analytic spectrum remains open.<br>No numeric reference residual is available for this row. |
| `ht_gap.first_ht_complement_gap` | ht_gap | first_ht_complement_gap | `19586.72266333732` | `19585.25982625801` | 7.46907159919e-05 | 3.2436554465e-05 | `EXCELLENT` | Level 2 finite-basis H_T proxy; full analytic spectrum remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `ht_gap.margin` | ht_gap | margin | `1.4628370793107024` | `None` |  |  | `EXACT_OR_STATUS` | Level 2 finite-basis H_T proxy; full analytic spectrum remains open.<br>No numeric reference residual is available for this row. |
| `ht_gap.passes` | ht_gap | passes_proxy_gap | `True` | `True` | 0 | 0 | `EXACT_OR_STATUS` | Pass/fail applies only to the current finite-basis proxy audit.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `scalar_decoupling.passes` | scalar_decoupling | passes | `True` | `True` | 0 | 0 | `EXACT_OR_STATUS` | Scalar/topographic decoupling remains a finite-basis scaffold; full action-level proof remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `scalar_decoupling.light_higgs_projection_count` | scalar_decoupling | light_higgs_projection_count | `1` | `1` | 0 | 0 | `EXACT_OR_STATUS` | Scalar/topographic decoupling remains a finite-basis scaffold; full action-level proof remains open.<br>Log-ratio error is reported because small mass ratios can make ordinary relative errors visually harsh. |
| `scalar_decoupling.mode_count` | scalar_decoupling | mode_count | `6` | `None` |  |  | `EXACT_OR_STATUS` | Scalar/topographic decoupling remains a finite-basis scaffold; full action-level proof remains open.<br>No numeric reference residual is available for this row. |

## Sector Summary

```json
{
  "ckm": {
    "best_relative_error": 0.0028824198996990243,
    "count": 6,
    "finite_relative_error_count": 5,
    "severity_counts": {
      "EXACT_OR_STATUS": 1,
      "EXCELLENT": 1,
      "GOOD": 1,
      "MODERATE": 3
    },
    "worst_prediction_id": "ckm.sin_theta_23",
    "worst_relative_error": 0.06786618770396666
  },
  "fermion_mass_ratios": {
    "best_relative_error": 0.0,
    "count": 9,
    "finite_relative_error_count": 9,
    "severity_counts": {
      "EXACT_OR_STATUS": 3,
      "GOOD": 2,
      "SCHEME_SENSITIVE": 4
    },
    "worst_prediction_id": "mass_ratio.up_quarks.middle",
    "worst_relative_error": 0.13003176431657681
  },
  "gauge_couplings": {
    "best_relative_error": 0.0019495252606574985,
    "count": 5,
    "finite_relative_error_count": 3,
    "severity_counts": {
      "EXACT_OR_STATUS": 2,
      "EXCELLENT": 3
    },
    "worst_prediction_id": "gauge_couplings.alpha_em_inv_mew",
    "worst_relative_error": 0.0027734053471015273
  },
  "higgs_electroweak": {
    "best_relative_error": 0.00020219666362016953,
    "count": 3,
    "finite_relative_error_count": 2,
    "severity_counts": {
      "EXACT_OR_STATUS": 1,
      "EXCELLENT": 1,
      "GOOD": 1
    },
    "worst_prediction_id": "higgs_electroweak.m_H_approx_v_over_2",
    "worst_relative_error": 0.01610765304455521
  },
  "ht_gap": {
    "best_relative_error": 0.0,
    "count": 4,
    "finite_relative_error_count": 2,
    "severity_counts": {
      "EXACT_OR_STATUS": 3,
      "EXCELLENT": 1
    },
    "worst_prediction_id": "ht_gap.first_ht_complement_gap",
    "worst_relative_error": 7.469071599190493e-05
  },
  "pmns_effective": {
    "best_relative_error": 0.009841702593675023,
    "count": 4,
    "finite_relative_error_count": 4,
    "severity_counts": {
      "EXCELLENT": 1,
      "GOOD": 3
    },
    "worst_prediction_id": "pmns_effective.sin2_theta_23",
    "worst_relative_error": 0.02547649567078357
  },
  "scalar_decoupling": {
    "best_relative_error": 0.0,
    "count": 3,
    "finite_relative_error_count": 2,
    "severity_counts": {
      "EXACT_OR_STATUS": 3
    },
    "worst_prediction_id": "scalar_decoupling.passes",
    "worst_relative_error": 0.0
  }
}
```

## COMMON_SCALE_APPROX Residual Section

These rows are separate approximate-running comparisons and do not replace the MIXED_DEFAULT residual audit.

| Target Scale | Ratio | BHSM | Common-Scale Approx Reference | Relative Error | Status |
| --- | --- | --- | --- | --- | --- |
| `91.1876` | `mass_ratio.up_quarks.middle` | `0.008310500554068288` | `0.004266868071316746` | `0.9476816285776762` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `91.1876` | `mass_ratio.up_quarks.light` | `1.2690463017606151e-05` | `7.876511100850345e-06` | `0.6111782050603717` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `91.1876` | `mass_ratio.down_quarks.middle` | `0.021933971495439474` | `0.020007279304305587` | `0.09629955986665618` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `91.1876` | `mass_ratio.down_quarks.light` | `0.0011165200546001757` | `0.0010003639652152794` | `0.11611382799049477` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `172.69` | `mass_ratio.up_quarks.middle` | `0.008310500554068288` | `0.004266868071316747` | `0.9476816285776758` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `172.69` | `mass_ratio.up_quarks.light` | `1.2690463017606151e-05` | `7.876511100850345e-06` | `0.6111782050603717` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `172.69` | `mass_ratio.down_quarks.middle` | `0.021933971495439474` | `0.02000727930430559` | `0.09629955986665599` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `172.69` | `mass_ratio.down_quarks.light` | `0.0011165200546001757` | `0.0010003639652152794` | `0.11611382799049477` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `10.0` | `mass_ratio.up_quarks.middle` | `0.008310500554068288` | `0.004266868071316747` | `0.9476816285776758` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `10.0` | `mass_ratio.up_quarks.light` | `1.2690463017606151e-05` | `7.876511100850345e-06` | `0.6111782050603717` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `10.0` | `mass_ratio.down_quarks.middle` | `0.021933971495439474` | `0.02000727930430559` | `0.09629955986665599` | `APPROXIMATE_RUNNING_SCAFFOLD` |
| `10.0` | `mass_ratio.down_quarks.light` | `0.0011165200546001757` | `0.0010003639652152794` | `0.11611382799049477` | `APPROXIMATE_RUNNING_SCAFFOLD` |

## THRESHOLD_AWARE_COMMON_SCALE Residual Section

These rows are diagnostic approximate threshold-aware comparisons and do not replace the MIXED_DEFAULT audit.

| Target Scale | Ratio | BHSM | Threshold-Aware Reference | Relative Error | Status |
| --- | --- | --- | --- | --- | --- |
| `91.1876` | `mass_ratio.up_quarks.middle` | `0.008310500554068288` | `0.004251569034944846` | `0.9546902533539826` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `91.1876` | `mass_ratio.up_quarks.light` | `1.2690463017606151e-05` | `7.867789503652917e-06` | `0.6129642273365508` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `91.1876` | `mass_ratio.down_quarks.middle` | `0.021933971495439474` | `0.019985125405342665` | `0.09751482918269905` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `91.1876` | `mass_ratio.down_quarks.light` | `0.0011165200546001757` | `0.0009992562702671331` | `0.11735106180689185` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `172.69` | `mass_ratio.up_quarks.middle` | `0.008310500554068288` | `0.004251569034944847` | `0.9546902533539822` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `172.69` | `mass_ratio.up_quarks.light` | `1.2690463017606151e-05` | `7.867789503652917e-06` | `0.6129642273365508` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `172.69` | `mass_ratio.down_quarks.middle` | `0.021933971495439474` | `0.019985125405342665` | `0.09751482918269905` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `172.69` | `mass_ratio.down_quarks.light` | `0.0011165200546001757` | `0.0009992562702671333` | `0.11735106180689162` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `10.0` | `mass_ratio.up_quarks.middle` | `0.008310500554068288` | `0.004251569034944847` | `0.9546902533539822` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `10.0` | `mass_ratio.up_quarks.light` | `1.2690463017606151e-05` | `7.867789503652917e-06` | `0.6129642273365508` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `10.0` | `mass_ratio.down_quarks.middle` | `0.021933971495439474` | `0.01998512540534267` | `0.09751482918269885` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
| `10.0` | `mass_ratio.down_quarks.light` | `0.0011165200546001757` | `0.0009992562702671333` | `0.11735106180689162` | `THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD` |
