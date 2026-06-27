# Formula registry

The formula registry separates three operational classes:

- `AVAILABLE_ARTIFACT_BACKED`: a local machine-readable source and loader exist;
- `AVAILABLE_INTERFACE_DEFAULT`: a deterministic interface demonstration exists;
- `OPEN_THEOREM_REQUIRED`: the exact production or physical-interpretation
  theorem callable is absent.

The CKM, PMNS, CP phase, boundary-constant, and mass-ratio loaders are
artifact-backed when their named files exist. The hyperspherical metric and
tension remain interface defaults. Charged `X_ch`, physical neutrino
basis/scale, and standalone CP `O_int` remain theorem blockers. Evaluating a
missing theorem callable returns `CALLABLE_NOT_AVAILABLE`.

Inspect the registry offline:

```powershell
python -m bhsm.interface formula-registry --format json
```

Interface default formulas remain interface defaults unless a theorem-backed artifact or callable replaces them.

Theorem blockers remain blockers unless explicit artifact-backed theorem support is present.
