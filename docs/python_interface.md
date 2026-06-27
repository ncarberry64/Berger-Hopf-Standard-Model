# BHSM Python computational interface

The `bhsm.interface` package is a review-oriented interface for constructing
hyperspherical/Berger-Hopf geometry records, evaluating dimensionless geometry,
mapping geometric tension into natural-unit masses, solving replaceable
equilibrium equations, and comparing outputs with provenance-tagged external
references.

It is an interface layer, not a new physics-claim layer. Its four stages are
kept separate:

1. **Geometric output** computes dimensionless metrics and tension.
2. **Unit calibration** defines the conversion from tension to GeV/c^2.
3. **Model prediction** solves an equilibrium equation given that calibration.
4. **Experimental comparison** compares the result without feeding the
   reference back into the geometry or equation.

## Geometry modes

`HypersphericalGeometry` accepts curvature indices, Hopf coefficients, radius,
anisotropy, boundary coupling, sector labels, and metadata. Its built-in metric,
tension, and residual are marked `DEFAULT_INTERFACE_FORMULA` and
`PLACEHOLDER_UNTIL_BHSM_THEOREM_SUPPLIED`. They provide a deterministic API
demonstration, not a claim that these formulas are the completed BHSM theorem.

For theorem-driven work, supply `metric_fn`, `tension_fn`, and/or `residual_fn`
callables. The serialized geometry then reports
`USER_SUPPLIED_BHSM_THEOREM_MODE`.

## Units and calibration

`GeometricUnitMapper` uses the `c=1` natural-unit convention while reporting
masses in GeV/c^2. It converts among GeV, eV, kg, and joules using source-noted
SI constants. `from_anchor()` records the anchor particle, mass, source, scale,
and calibration mode.

If a particle mass is used to calibrate the geometric-to-physical unit scale, that same particle cannot be counted as an independent prediction in that run.

The solver enforces this distinction with
`CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION`; other solved particles receive
`MODEL_PREDICTION_GIVEN_CALIBRATION`.

## Root solving

`ParticleMassSolver` wraps `scipy.optimize.root`. The default residual is the
difference between trial mass and mapped geometric tension. A BHSM theorem
residual can replace it. Failed, nonfinite, or negative roots produce an
explicit failed `SolverResult`; they are never silently returned as masses.

## Validation and PDG fallback

`ExperimentalValue` supports central values, upper/lower limits, and ranges.
`ValidationComparison` computes the metrics appropriate to the reference kind.
External values are comparison-only records with source metadata.

The optional `pdg` package is not required. Until a stable PDG package API is
version-pinned, `load_reference_with_fallback()` uses curated offline records:
the PDG 2024 W-boson listing and the KATRIN kinematic electron-neutrino upper
limit. Package absence or adapter deferral is recorded in metadata.

The electron-neutrino comparison is treated as an upper-limit comparison unless a vetted central experimental mass reference is explicitly supplied.

## Claim boundary

The interface does not modify frozen BHSM predictions, provide empirical
derivation inputs, establish empirical validation, complete the BHSM 4D
Lagrangian, or establish FeynRules/UFO/MadGraph or experiment-software
readiness. Default formulas and example geometries are replaceable interface
demonstrations.

See `docs/python_interface_quickstart.md` and
`docs/python_interface_validation_policy.md`.

The prediction registry and reviewer-report layer are documented in
`docs/python_prediction_registry.md`, `docs/python_cli.md`, and
`docs/python_prediction_report.md`.
