# Python interface validation policy

## Separation policy

The computational flow is one-way:

```text
geometry -> unit calibration -> model solve -> external comparison
```

External references may calibrate an explicitly labeled unit mapper or evaluate
a solved output. They may not alter BHSM constants, frozen modes, boundary
operators, frozen predictions, or theorem formulas.

## Calibration anchors

If a particle mass is used to calibrate the geometric-to-physical unit scale, that same particle cannot be counted as an independent prediction in that run.

The W-boson example therefore labels W as
`CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION`. Only non-anchor results can be
labeled `MODEL_PREDICTION_GIVEN_CALIBRATION`, and that label remains conditional
on the supplied geometry and equilibrium equation.

## Electron-neutrino references

The electron-neutrino comparison is treated as an upper-limit comparison unless a vetted central experimental mass reference is explicitly supplied.

The curated fallback uses a KATRIN kinematic upper limit. It is not represented
as a measured central mass, and neutrino outputs remain part of an effective
extension rather than the minimal Standard Model.

## Reference provenance

Every fallback records a source label, URL, reference kind, uncertainty or
limit where available, and loader metadata. The optional `pdg` dependency is
not required and no network call occurs during tests.

## Allowed interpretation

The interface may be described as a computational, calibration-aware review
layer. Numerical outputs may be described as geometric outputs, anchor-based
model predictions, or external comparisons according to their metadata.

It must not be described as empirical validation, official CERN integration,
a completed 4D Lagrangian export, or validated FeynRules/UFO/MadGraph output.

Registry statuses do not override these policies: open-theorem entries remain
blockers and runtime-disabled entries remain gated until live validation.
