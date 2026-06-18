# PO-BH-51: Subsurface Neutral Projection Geometry Localization

This PR localizes the projection geometry required by the PO-BH-50 neutral effective action:

```text
S_eff^(nu) =
S_bulk[Phi] + S_partial^(nu)[Phi]
+ S_subsurface^(nu)[Phi; ellapse_nu, g_sub].
```

## Changes

- Adds `theory/theorem_discharge_subsurface_projection_geometry.md`.
- Adds closure-map objects and entries for:
  - `g_sub`;
  - `ellapse_nu`;
  - `Pi_sub_to_ext`.
- Documents four candidate routes:
  - metric splitting;
  - topographic lapse;
  - stationary neutral channel;
  - causality-preserving exterior-projected apparent FTL interpretation.
- Adds tests in `tests/test_subsurface_projection_geometry.py`.
- Updates status docs and open blockers conservatively.

## Claim Boundary

`g_sub`, `ellapse_nu`, and `Pi_sub_to_ext` are `OPEN_LOCALIZABLE`, not derived.

BHSM does not claim local causality violation. Any FTL-like behavior is exterior-projected apparent behavior arising from a subsurface/internal topographic channel and remains conditional until `g_sub`, `ellapse_nu`, and `Pi_sub_to_ext` are derived.

This PR does not use observed neutrino masses, neutrino mass splittings, PMNS angles, PMNS CP phase, or fitted anomaly/FTL data. It does not change frozen predictions or official outputs.

## Validation

Run:

```text
python -m pytest tests/test_subsurface_projection_geometry.py -q
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

Suggested target branch: `bhsm-s-eff-nu-localization-v1`.
