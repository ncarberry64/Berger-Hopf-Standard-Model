# Prediction gallery plots

Plots contain registry status/category counts and runtime-gate counts. They use
no live data and omit speculative templates by default.

Plots summarize registry status; they do not validate BHSM empirically.

```powershell
python -m bhsm.interface plot-gallery --dry-run
python scripts/generate_prediction_gallery_plots.py
```
