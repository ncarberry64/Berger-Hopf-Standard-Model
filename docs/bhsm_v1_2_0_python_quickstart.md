# BHSM v1.2.0 Python quickstart

```bash
python -m bhsm.interface registry
python -m bhsm.interface status W_boson
python -m bhsm.interface status electron_neutrino
python -m bhsm.interface predict --particle W_boson --mode calibration
python -m bhsm.interface predict --particle electron_neutrino --anchor W_boson
python -m bhsm.interface report --anchor W_boson --particles W_boson,electron_neutrino --format json
```

W used as an anchor is not an independent prediction. Electron-neutrino
comparison is upper-limit based by default. Open-theorem entries are blockers,
and runtime-disabled software gates require external validation.

These commands run offline without PDG, Wolfram, FeynRules, or MadGraph.
