# Phase Three-F Production Basis And Runtime Parameter Status

BHSM Phase Three-F defines a canonical production basis for future
FeynRules/UFO interfaces and separates no-fit derivation mode from runtime
collider-interface comparison mode.

## Result

```text
canonical_production_basis_defined = true
Z_A_prod_status = CANONICAL_PRODUCTION_BASIS_DEFINED
Z_psi_prod_status = CANONICAL_PRODUCTION_BASIS_DEFINED
interface_normalization_gate_cleared = true
runtime_parameter_modes_exported = true
production_coupling_map_exported = true
mass_width_runtime_policy_exported = true
feynrules_ready = false
ufo_ready = false
madgraph_ready = false
```

`Z_A,prod = 1` and `Z_psi,prod = 1` are production-basis definitions for
canonical FeynRules/UFO fields. They are not empirical fits and not nontrivial
BHSM-derived wavefunction-renormalization predictions.

## Runtime Parameter Boundary

`BHSM_PURE_NOFIT` uses only BHSM-derived internal values. `BHSM_COLLIDER_INTERFACE`
may accept external runtime masses, widths, and simulation cards for future
detector/event comparison. Runtime inputs do not modify BHSM constants,
boundary coefficients, mixing matrices, or frozen predictions.

This does not constitute production FeynRules, UFO, MadGraph, LHE/HepMC,
Athena, or CMSSW readiness.

