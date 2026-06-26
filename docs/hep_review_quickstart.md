# BHSM v1.1.0 HEP Review Quickstart

BHSM v1.1.0 packages the internal boundary no-fit release plus a bounded minimal collider-interface handoff layer for HEP-style review. The collider-interface layer includes CKM/PMNS charged-current target structures sourced by BHSM artifacts and excludes unresolved charged-boundary, neutral-kernel, and standalone CP-holonomy sectors. Runtime validation requires external licensed Wolfram/FeynRules tooling and remains gated unless those tools are detected and run successfully.

## 1. Repository Status

BHSM v1.0.1 status-reconciled release: internal boundary no-fit package complete/exported; external empirical comparison layer separate/open.

BHSM v1.1.0 adds release-facing HEP review materials for the Phase Three-C through Phase Three-O collider-interface handoff chain.

## 2. What BHSM v1.1.0 Contains

- Internal boundary no-fit package and frozen prediction integrity checks.
- Minimal bounded collider-interface subset.
- CKM charged-current bounded target.
- PMNS charged-current bounded target.
- BHSM CKM/PMNS source matrices.
- FeynRules-prep JSON/docs.
- Disabled minimal FeynRules draft.
- Runtime validation runner package.
- Institutional HEP handoff package.

## 3. What BHSM v1.1.0 Does Not Contain

- Complete BHSM 4D Lagrangian.
- Production charged-boundary response matrix.
- Production neutral operator kernel.
- Production standalone CP-holonomy attachment.
- Pure no-fit mass-width closure.
- Renormalization closure.
- Enabled validated FeynRules file.
- UFO export/loadability.
- MadGraph validation.
- LHE/HepMC event generation.
- Athena integration.
- CMSSW integration.
- Official CERN software integration.
- Empirical validation.

## 4. Minimal Collider-Interface Subset Scope

The bounded subset is limited to CKM/PMNS charged-current target structures and the supporting field/parameter/vertex handoff artifacts. Excluded vertex families remain documented as excluded.

## 5. Runtime Dependencies

Python is required for repository tests and preflight scripts. Wolfram/WolframScript or a licensed Mathematica runtime, FeynRules, and MadGraph are required for later live validation gates.

## 6. Run Repo Tests

```powershell
python -m pytest -q
```

## 7. Run Environment Preflight

```powershell
python scripts/setup/check_bhsm_hep_environment.py
```

## 8. Map Wolfram/FeynRules

Use environment variables such as `WOLFRAMSCRIPT_PATH`, `WOLFRAM_KERNEL_PATH`, `MATHEMATICA_PATH`, and `FEYNRULES_PATH`, then run:

```powershell
python scripts/setup/map_wolfram_runtime.py
python scripts/setup/install_or_map_feynrules.py
```

## 9. Attempt Live FeynRules Validation

```powershell
python scripts/feynrules/run_live_feynrules_validation.py
```

This gate remains closed unless a legal Wolfram/FeynRules runtime is available and the script records real execution.

## 10. Attempt UFO Export

```powershell
python scripts/feynrules/run_ufo_export_if_validated.py
```

UFO export remains closed unless the FeynRules validation gate has passed.

## 11. Attempt MadGraph Smoke Test

```powershell
python scripts/madgraph/run_minimal_ufo_smoke_if_available.py
```

MadGraph smoke testing remains closed unless UFO loadability exists.

## 12. What Counts As Success

Success is recorded only by machine-readable artifacts showing real runtime detection and execution. Documentation alone does not unlock FeynRules, UFO, MadGraph, event, Athena, or CMSSW gates.

## 13. Claims That Remain Forbidden

Do not claim official CERN software integration, CERN-ready status, Athena-ready status, CMSSW-ready status, validated UFO output, MadGraph validation, validated LHE/HepMC events, complete 4D Lagrangian export, empirical validation, runtime parameters as derivation inputs, or excluded vertices as production-ready.
