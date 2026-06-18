# PO-BH-49: Neutral Saddle Displacement Localization

## Summary

This PR localizes the neutral saddle displacement `Delta_y_nu` as a required
input for the already-localized `S_nu_topo` Hessian/barrier formula.

Candidate formulas documented:

```text
Delta y_nu = - H_H^{-1} grad_y[delta S_eff^(nu-H)]|_{y_H}
Delta y_nu = <y>_nu - <y>_H
```

Status remains `OPEN_LOCALIZABLE`. Numerical neutrino closure remains open.

## Files Changed

- `data/bhsm_numerical_input_closure_map.json`
- `docs/bhsm_numerical_input_closure_map.md`
- `docs/current_bhsm_status.md`
- `docs/claim_status_table.md`
- `docs/open_blockers_backlog.md`
- `docs/pr_body_po_bh_49_neutral_saddle_displacement.md`
- `tests/test_neutral_saddle_displacement.py`
- `theory/theorem_discharge_neutral_saddle_displacement.md`

## Tests Run

- `python -m pytest tests/test_neutral_saddle_displacement.py -q`
- `python -m pytest tests/test_neutral_topographic_suppression_action.py -q`
- `python -m pytest tests/test_numerical_input_closure_map.py -q`
- `python -m pytest -q`

## Audits Run

- `python tools/audit_forbidden_claims.py`
- `python tools/audit_bhsm_status.py`
- `python tools/audit_frozen_prediction_integrity.py`

## Validation

- Frozen predictions changed: no.
- Official predictions changed: no.
- Full test suite passed: `1305 passed`.
- PO-BH-49 focused tests passed: `9 passed`.
- Guardrail audits passed.

## Delta_y_nu Status

`Delta_y_nu` is `OPEN_LOCALIZABLE`, not derived.

## Candidate Formula(s)

```text
Delta y_nu = - H_H^{-1} grad_y[delta S_eff^(nu-H)]|_{y_H}
Delta y_nu = <y>_nu - <y>_H
```

## Missing Dependencies

- `S_eff^(nu)`
- `S_eff^(H)`
- `H_H`
- `grad_y[delta S_eff^(nu-H)]|_{y_H}`
- `W_nu`
- `W_H`
- coordinate chart or coordinate-invariant centroid convention
- label-to-distance map `E_nu`

## Forbidden Fit Routes

- observed neutrino masses
- observed neutrino mass splittings
- PMNS angles
- PMNS CP phase
- post-comparison `Delta_y_nu` fit
- post-comparison `epsilon_nu_topo` fit

## Current Public Status

```text
structural architecture integrated conditional; numerical closure open
```

## Next Recommended Sprint

`S_EFF_NU_NEUTRAL_ACTION_OPEN` or `H_TOPO_NU_HESSIAN_DERIVATION_OPEN`.

## Explicit No-Overclaim Statement

This PR does not claim `Delta_y_nu` is derived, does not claim `S_nu_topo` is
derived, does not claim neutrino mass prediction, does not claim PMNS numerical
prediction, and does not claim numerical Standard Model replacement.

