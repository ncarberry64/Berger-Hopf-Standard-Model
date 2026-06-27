# BHSM v1.2.0 - Python computational interface and prediction registry

## Summary

This usability/API package adds an offline computational interface, prediction
registry, CLI, and deterministic reviewer report without changing BHSM physics
outputs or claim strength.

## What is included

Hyperspherical geometry records, geometric unit mapping, SciPy root solving,
reference comparisons, optional PDG fallback, registry statuses, CLI commands,
reviewer reports, documentation, artifacts, and tests.

## CLI quickstart

```text
python -m bhsm.interface registry
python -m bhsm.interface report --anchor W_boson --particles W_boson,electron_neutrino --format json
```

## Prediction registry

The registry distinguishes calibration anchors, predictions given calibration,
upper-limit comparisons, frozen artifacts, theorem blockers, and software gates.

## Calibration policy

W is not an independent prediction in a run where it calibrates the unit scale.

## Upper-limit comparison policy

Electron-neutrino output is compared with an upper limit by default, not a
central measured mass.

## What is not claimed

No empirical validation, complete 4D Lagrangian, official CERN integration, or
validated FeynRules/UFO/MadGraph readiness is claimed.

## Tests and audits

The interface, registry, CLI, release tests, full suite, claim audits, frozen
integrity audit, and safety scan must pass before publication.

## Remaining open items

Physics theorem obligations and external runtime gates remain open. The tag
`v1.2.0` is already occupied by an earlier release and cannot be reused.

## Citation

The active `CITATION.cff` remains tied to the currently published package until
a distinct release version is selected. No new DOI is asserted here.
