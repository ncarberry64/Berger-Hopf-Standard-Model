# PO-BH-47/48: Closure Map and Neutral Topographic Suppression Localization

## Summary

This PR packages the PO-BH-47 numerical input closure map together with the
PO-BH-48 neutral topographic suppression localization sprint.

PO-BH-47 records the remaining symbolic numerical inputs and forbidden fit
routes after the current BHSM theorem-discharge chain. PO-BH-48 localizes
`S_nu_topo` as an `OPEN_LOCALIZABLE` neutral numerical-closure object with a
Hessian/barrier candidate formula:

```text
S_nu_topo = 1/2 Delta y_nu^T G_nu_topo Delta y_nu + S_barrier
G_nu_topo = 1/2 E_nu^T H_topo^(nu) E_nu
```

The current public status remains:

```text
structural architecture integrated conditional; numerical closure open
```

## Files Changed

- `data/bhsm_numerical_input_closure_map.json`
- `docs/bhsm_numerical_input_closure_map.md`
- `docs/current_bhsm_status.md`
- `docs/github_claim_summary.md`
- `docs/claim_status_table.md`
- `docs/open_blockers_backlog.md`
- `docs/pr_body_po_bh_47_closure_package.md`
- `docs/pr_body_po_bh_47_48_closure_and_s_nu_topo.md`
- `tests/test_numerical_input_closure_map.py`
- `tests/test_neutral_topographic_suppression_action.py`
- `theory/theorem_discharge_numerical_input_closure_map.md`
- `theory/theorem_discharge_neutral_topographic_suppression_action.md`

## Tests Run

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
- Full test suite passed: `1296 passed`.
- PO-BH-48 focused tests passed: `9 passed`.
- PO-BH-47 focused tests passed: `11 passed`.
- Guardrail audits passed.

## S_nu_topo Status

`S_nu_topo` is `OPEN_LOCALIZABLE`, not derived.

Candidate formula:

```text
S_nu_topo = 1/2 Delta y_nu^T G_nu_topo Delta y_nu + S_barrier
G_nu_topo = 1/2 E_nu^T H_topo^(nu) E_nu
```

## Missing Dependencies

- `Delta y_nu`
- `H_topo^(nu)`
- `E_nu`
- `S_barrier`
- neutral finite-width saddle/path
- scalar/topographic profile solution
- positivity proof for the suppression action

## Open Blockers

- `DELTA_Y_NU_NEUTRAL_SADDLE_DISPLACEMENT_OPEN`
- `H_TOPO_NU_HESSIAN_DERIVATION_OPEN`
- `E_NU_LABEL_TO_DISTANCE_MAP_OPEN`
- `S_BARRIER_NEUTRAL_TOPOGRAPHIC_OPEN`
- `SCALAR_TOPOGRAPHIC_PROFILE_SOLUTION_OPEN`
- `POSITIVITY_PROOF_S_NU_TOPO_OPEN`
- `CKM_1_16_EXPONENT_NOT_DERIVED`
- `SCALAR_TOPOGRAPHIC_DECOUPLING_OPEN`
- `HIGHER_LOOP_THRESHOLDS_OPEN`
- `NUMERICAL_MASS_RATIO_LOCK_OPEN`
- `CKM_NUMERICAL_LOCK_OPEN`
- `PMNS_NUMERICAL_LOCK_OPEN`

## Next Recommended Sprint

`DELTA_Y_NU_NEUTRAL_SADDLE_DISPLACEMENT_OPEN` or
`H_TOPO_NU_HESSIAN_DERIVATION_OPEN`.

## Explicit No-Overclaim Statement

This PR does not claim BHSM is proven, does not claim numerical Standard Model
replacement, does not claim neutrino mass prediction, does not claim CKM or
PMNS numerical prediction, and does not claim `S_nu_topo` is derived. The
neutral topographic suppression action is localized as an open, localizable
blocker with a candidate formula.

