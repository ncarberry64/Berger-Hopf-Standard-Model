# Python prediction report

`build_prediction_report()` returns a JSON-serializable `PredictionReport` with:

- release and calibration metadata;
- solved interface outputs and formula status;
- one-way reference comparisons;
- registry statuses and source-specific claim boundaries;
- explicit warnings;
- flags for empirical derivation input, runtime mutation, internet, optional
  PDG, and empirical-validation claims.

The deterministic example uses W as the unit anchor and reports the
electron-neutrino demo against an upper limit. With
`include_open_theorem_entries=True`, open interaction families and
runtime-disabled software gates are included as blockers, not outputs.

```powershell
python examples/bhsm_prediction_report.py
```

The generated reference artifact is
`artifacts/BHSM_prediction_report_example_v0_1.json`.
