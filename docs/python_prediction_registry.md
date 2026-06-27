# Python prediction registry

The registry gives every exposed BHSM object a machine-readable status. This
prevents calibration anchors, model outputs, comparison references, frozen
artifacts, theorem blockers, and software gates from being conflated.

The initial registry includes W and electron-neutrino demo mass paths, existing
CKM/PMNS source artifacts, three open interaction-theorem families, the bounded
minimal collider-interface subset, and disabled FeynRules/UFO/MadGraph gates.

W can calibrate the tension-to-GeV scale. In that run its solved value is labeled
`CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION`. Electron-neutrino comparison
uses an `upper_limit` reference by default. CKM/PMNS entries remain
`FROZEN_INTERNAL_PREDICTION`; their external comparison is separate.

`OPEN_THEOREM_REQUIRED` entries cannot be promoted to production vertices.
`DISABLED_UNTIL_RUNTIME_VALIDATED` entries remain disabled until the named live
tool actually passes. Inspect the registry with:

```powershell
python -m bhsm.interface registry
python -m bhsm.interface status W_boson --format json
```

Release status summary: `artifacts/BHSM_v1_2_0_prediction_registry_status.json`.
