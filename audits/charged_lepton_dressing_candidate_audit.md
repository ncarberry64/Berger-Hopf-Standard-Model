# Charged Lepton Dressing Candidate Audit

```json
{
  "classification": "LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL",
  "eta_classification": "ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
  "candidate_status": "CANDIDATE_NOT_OFFICIAL",
  "official_status": "NOT_OFFICIAL",
  "rule": {
    "name": "charged_lepton_mode_norm_exponential",
    "formula": "Z_l(k,j)=exp[-eta_l*(q^2+j^2)], q=k-2j",
    "q_definition": "q is Hopf charge k-2j, not the coordinate k",
    "fit_parameter": "eta_l",
    "fit_parameter_value": 0.0020443439144236667,
    "fit_input_ratio": "mu/tau",
    "held_out_ratio": "e/tau",
    "derived": false,
    "pre_registered_in_this_sprint": true,
    "per_particle_fitted_factors_used": false
  },
  "formula_integrity_checked": true,
  "eta_derivation_status": "ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED",
  "best_independent_eta_candidate": "fine_structure_alpha_over_pi",
  "reason": "A single mode-dependent charged-lepton dressing candidate improves both rows, but eta_l remains not independently derived and the rule is not official.",
  "baseline_residuals": [
    {
      "rank": "middle",
      "quantity": "mu/tau",
      "mode": [
        5,
        2
      ],
      "q": 1,
      "mode_norm": 5,
      "predicted": 0.06007447093260976,
      "reference": 0.05946353426831603,
      "absolute_error": 0.0006109366642937306,
      "relative_error": 0.010274139803682273
    },
    {
      "rank": "light",
      "quantity": "e/tau",
      "mode": [
        9,
        3
      ],
      "q": 3,
      "mode_norm": 18,
      "predicted": 0.00029729106456492414,
      "reference": 0.0002875853753250115,
      "absolute_error": 9.705689239912637e-06,
      "relative_error": 0.03374889710210006
    }
  ],
  "candidate_rows": [
    {
      "rank": "middle",
      "mode": [
        5,
        2
      ],
      "mode_norm": 5,
      "dressing_factor": 0.9898303446570663,
      "dressed_prediction": 0.05946353426831603,
      "reference": 0.05946353426831603,
      "relative_error": 0.0,
      "baseline_relative_error": 0.010274139803682273,
      "improved": true,
      "fitted_input": true,
      "held_out": false
    },
    {
      "rank": "light",
      "mode": [
        9,
        3
      ],
      "mode_norm": 18,
      "dressing_factor": 0.9638706340121804,
      "dressed_prediction": 0.0002865501268883495,
      "reference": 0.0002875853753250115,
      "relative_error": 0.0035997951408065676,
      "baseline_relative_error": 0.03374889710210006,
      "improved": true,
      "fitted_input": false,
      "held_out": true
    }
  ],
  "official_lepton_predictions_changed": false,
  "closes_lepton_precision_blocker": false,
  "next_action": "derive a mode-structured lepton dressing rule or leave the lepton precision gap open"
}
```
