# Bare Engine Triangulation Audit

Status: `BARE_ENGINE_TRIANGULATION_AUDIT_COMPLETE`

This candidate-only audit compares read-only existing BHSM predictions with the new Tier C spectral-action baseline. It exists because the candidate spectral action preserved hierarchy ordering but did not reproduce the stronger existing BHSM prediction structure.

## Sources

Frozen/existing source: `docs/frozen_predictions.json + theory/bhsm_prediction_ledger.json`
Spectral-action source: `candidate_bare_yukawa_residual_autopsy:A_raw_bare_only`
Reference source: `theory/bhsm_prediction_ledger.json`

## Engine Comparison

| Ratio | Existing bare | Existing dressed | Spectral action | Reference | Closer | Scheme-sensitive |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `mu/tau` | `0.06007447093260976` | `0.06007447093260976` | `0.3747838213299577` | `0.05946353426831603` | `existing_bare` | `False` |
| `e/tau` | `0.00029729106456492414` | `0.00029729106456492414` | `0.03230113011695777` | `0.0002875853753250115` | `existing_bare` | `False` |
| `c/t` | `0.008310500554068288` | `0.004155250277034144` | `0.001458112854293096` | `0.007354218541895883` | `existing_bare` | `True` |
| `u/t` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `7.430054796240815e-06` | `1.2507962244484336e-05` | `existing_bare` | `True` |
| `s/b` | `0.021933971495439474` | `0.021933971495439474` | `0.16529888822158653` | `0.022344497607655504` | `existing_bare` | `True` |
| `d/b` | `0.0011165200546001757` | `0.0011165200546001757` | `0.02466193465732934` | `0.0011172248803827751` | `existing_bare` | `True` |

## Missing-Invariant Diagnostics

Closer counts: `{'existing_bare': 6}`
Strongest spectral-residual correlation: `{'invariant': 'mode_gap_between_nonzero_pair', 'target': 'spectral_action_log_residual', 'pearson': -0.8656860681125852, 'sample_size': 6, 'diagnostic_only': True}`

The spectral action is not the existing BHSM engine. Its largest disagreements point toward missing response-layer structure, branch assignment, nonlinear threshold behavior, or unresolved quark reference schemes rather than a completed universal heat-kernel mass law.

## Answers

1. The new spectral-action baseline does not reproduce the existing BHSM bare prediction pattern.
2. It disagrees most on charged-lepton light mode, down light mode, and charm/top underprediction.
3. Correlations are diagnostic-only because the sample has six rows.
4. Candidate missing ingredients include response-layer effects, branch assignment, orientation/cross terms, nonlinear thresholds, and reference-scheme limitations.
5. No invariant candidate is adopted as a new official formula.
6. Next test: derive or reject a nonlinear threshold/response law before adding any official mass formula.

## Claim Boundaries

- No official predictions are changed.
- No frozen predictions are changed.
- No new official mass formula is introduced.
- `BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived.
- `FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived.
- `RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE` is not upgraded to derived.
