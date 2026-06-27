# BHSM registry CLI walkthrough

All commands are deterministic and offline-safe:

```bash
python -m bhsm.interface registry
python -m bhsm.interface status W_boson
python -m bhsm.interface predict --particle W_boson --mode calibration
python -m bhsm.interface predict --particle electron_neutrino --anchor W_boson
python -m bhsm.interface report --anchor W_boson --particles W_boson,electron_neutrino --format json
```

Add `--include-open-theorem` to the report command to expose theorem blockers
and runtime-disabled gates. Their presence in a report does not promote them to
predictions or validated software outputs.
