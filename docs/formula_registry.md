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

The v6.30.5 D0 registry additions are `g3=-Omega3`,
`Gamma4=-2 Z5 g3`, and
`VE4=260.281562752946 G5+3633.0356624841 Z5^2/kappa1`.
They are parameterized action-derived formulas, not numerical physical
predictions. Their unconditional sign remains blocked by unselected `G5`.

Sprint A records `OPEN_EXACT_MISSING_THEOREM` for `X_ch` and the physical
neutrino map, and `OPEN_MISSING_INTERACTION_ATTACHMENT` for standalone CP
`O_int`. Their formula statuses remain `OPEN_THEOREM_REQUIRED`.

The Sprint B focused report is now included in the standalone CP entry's source
artifacts. This adds provenance but does not make its callable available.

Sprint C adds a separate symbolic callable while keeping the production formula
entry `OPEN_THEOREM_REQUIRED`. Its theorem status is
`OPEN_MISSING_ACTION_SOURCE`.
