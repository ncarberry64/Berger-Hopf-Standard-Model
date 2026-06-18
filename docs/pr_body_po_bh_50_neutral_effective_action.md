# PO-BH-50: Neutral Effective Action Localization

This PR localizes `S_eff^(nu)` as the action-level source for the neutral saddle displacement used in the neutral topographic suppression scaffold.

## Changes

- Adds `theory/theorem_discharge_neutral_effective_action.md`.
- Adds `S_eff_nu` to `data/bhsm_numerical_input_closure_map.json`.
- Updates the neutral saddle displacement dependency chain so `Delta_y_nu` depends explicitly on `S_eff_nu`.
- Documents four candidate routes:
  - subsurface neutral topographic channel action;
  - boundary scalar/topographic action;
  - neutral operator source from `Omega_nu=-q-2j=-k`;
  - finite-width neutral profile action.
- Adds conservative apparent-FTL / causality guardrails:
  - exterior-projected anomalous propagation is projection-level language only;
  - apparent FTL from exterior-surface viewpoint is not a local causality claim;
  - the candidate remains locally causal in the internal/topographic metric.
- Adds `tests/test_neutral_effective_action.py`.

## Claim Boundary

`S_eff^(nu)` is `OPEN_LOCALIZABLE`, not derived. Numerical neutrino closure remains open.

This PR does not use observed neutrino masses, neutrino mass splittings, PMNS angles, or PMNS CP phase. It does not change frozen predictions or official outputs.

## Validation

Run:

```text
python -m pytest tests/test_neutral_effective_action.py -q
python -m pytest tests/test_neutral_saddle_displacement.py -q
python -m pytest tests/test_neutral_topographic_suppression_action.py -q
python -m pytest tests/test_numerical_input_closure_map.py -q
python -m pytest -q
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
```

## Stacked Target

Suggested target branch: `bhsm-delta-y-nu-localization-v1`.
