# Flavor Residual Diagnostic

This diagnostic does not tune parameters, change modes, or adopt exploratory CKM rules.

## Current Up-Sector Constants

- a = `1.157054135733433`
- S = `0.07957747154594767`
- lambda_(6,0) = `60.1958738286423`
- lambda_(10,1) = `141.68155347314186`

## Current Residuals

- c/t predicted `0.008310500554068288`, reference `0.007354218541895883`
- u/t predicted `1.2690463017606151e-05`, reference `1.2507962244484336e-05`
- sin(theta_13) predicted `0.0035623676140463315`, reference `0.00382`

## First Five Admissible Up Modes

| Mode | q | Omega_u | lambda | suppression | rel error vs u/t |
| --- | --- | --- | --- | --- | --- |
| `(6, 0)` | 6 | 6 | 60.1958738286423 | 0.008310500554068288 | 663.4168243898392 |
| `(10, 1)` | 8 | 6 | 141.68155347314186 | 1.2690463017606151e-05 | 0.014590767828891764 |
| `(14, 2)` | 10 | 6 | 257.87742730178417 | 1.2238874209310043e-09 | 0.9999021513339257 |
| `(18, 3)` | 12 | 6 | 408.7834953145692 | 7.454511563251954e-15 | 0.9999999994040187 |
| `(22, 4)` | 14 | 6 | 594.399757511497 | 2.8675475795726386e-21 | 0.9999999999999998 |

## Next-Mode Assessment

{
  "assessment": "overcorrects",
  "next_mode_after_current_light": [
    14,
    2
  ],
  "note": "Ledger is not changed; this is an admissible-mode sensitivity diagnostic.",
  "reference_u_over_t": 1.2507962244484336e-05,
  "suppression": 1.2238874209310043e-09
}

## Constant Sensitivity Table

```json
[
  {
    "S": 0.07957747154594767,
    "a": 0.573,
    "c_over_t": 0.15023974540099852,
    "relative_error": {
      "c_over_t": 19.429056404171995,
      "sin_theta_13": 11.222184720275772,
      "u_over_t": 173.27610717323776
    },
    "sensitivity_only": true,
    "sin_theta_13": 0.04668874563145345,
    "u_over_t": 0.002179838968638564
  },
  {
    "S": 0.07957747154594767,
    "a": 1.0,
    "c_over_t": 0.021933971495439474,
    "relative_error": {
      "c_over_t": 1.9825019980688525,
      "sin_theta_13": 1.209699566673167,
      "u_over_t": 4.696480633145636
    },
    "sensitivity_only": true,
    "sin_theta_13": 0.008441052344691499,
    "u_over_t": 7.125136468582184e-05
  },
  {
    "S": 0.07957747154594767,
    "a": 1.157054135733433,
    "c_over_t": 0.008310500554068288,
    "relative_error": {
      "c_over_t": 0.13003176431657681,
      "sin_theta_13": 0.06744303297216456,
      "u_over_t": 0.014590767828891764
    },
    "sensitivity_only": true,
    "sin_theta_13": 0.0035623676140463315,
    "u_over_t": 1.2690463017606151e-05
  }
]
```

## CKM Rule Breakdown

Current rule: `sqrt(u/t)` gives `0.0035623676140463315`.

Exploratory alternatives are diagnostics only:

```json
[
  {
    "formula": "sqrt(u/t) * sqrt(d/s)",
    "id": "sqrt_u_over_t_times_sqrt_d_over_s",
    "log_error_vs_sin13": -0.6769500022970298,
    "relative_error_vs_sin13": 0.7895979350975137,
    "status": "EXPLORATORY_ONLY",
    "value": 0.0008037358879274976
  },
  {
    "formula": "sqrt(u/t) * (s/b)",
    "id": "sqrt_u_over_t_times_s_over_b",
    "log_error_vs_sin13": -1.6892073542574602,
    "relative_error_vs_sin13": 0.979545322067338,
    "status": "EXPLORATORY_ONLY",
    "value": 7.813686970276896e-05
  },
  {
    "delta_lambda_lr": 81.48567964449956,
    "formula": "sqrt(u/t) * exp[-S Delta lambda_LR]",
    "id": "sqrt_u_over_t_times_exp_delta_lambda_lr",
    "log_error_vs_sin13": -2.846474343961616,
    "relative_error_vs_sin13": 0.9985759486297027,
    "status": "EXPLORATORY_ONLY",
    "value": 5.43987623453582e-06
  }
]
```

## Likely Root Cause

The localized tension is not caused by a constants mismatch or missing CKM implementation. It traces to the current up-sector overlap ledger and the sqrt(u/t) V_ub screen, with quark mass-scheme sensitivity and possible missing representation/left-right normalization remaining open.

## Limitations

- Diagnostic only; no parameters, modes, or CKM rules are tuned.
- Exploratory CKM alternatives are not adopted.
