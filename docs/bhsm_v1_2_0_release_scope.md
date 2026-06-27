# BHSM v1.2.0 Python interface release scope

## Included

- Python computational interface
- `HypersphericalGeometry`
- `GeometricUnitMapper`
- `ParticleMassSolver`
- `ValidationComparison`
- optional PDG fallback interface
- `PredictionRegistry` and prediction status taxonomy
- offline CLI and reviewer prediction report
- deterministic examples and JSON artifacts
- calibration/prediction/validation claim policy

## Excluded

- new physics theorem closure or particle-mass claim set
- empirical validation
- complete BHSM 4D Lagrangian or official CERN integration
- FeynRules validation, UFO export/loadability, or MadGraph validation
- LHE/HepMC generation, Athena readiness, or CMSSW readiness
- live PDG requirement or internet-required tests

This usability/API package does not modify frozen BHSM predictions or existing
physics/model logic.

## Version deployment note

The Git tag `v1.2.0` already identifies an earlier public final-paper package.
That tag must not be moved or overwritten. Publication of this interface package
therefore requires a distinct release version before tagging.
