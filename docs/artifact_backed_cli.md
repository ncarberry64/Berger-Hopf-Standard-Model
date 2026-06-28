# Artifact-backed CLI

All commands below use local files and work without PDG, internet, Wolfram,
FeynRules, UFO, or MadGraph access:

```powershell
python -m bhsm.interface artifact-sources --format json
python -m bhsm.interface formula-registry --format json
python -m bhsm.interface compute-artifact CKM_matrix_BHSM
python -m bhsm.interface compute-artifact PMNS_matrix_BHSM
python -m bhsm.interface compute-artifact cp_holonomy_phase_attachment
python -m bhsm.interface compute-artifact boundary_constants
python -m bhsm.interface compute-artifact mass_ratios
python -m bhsm.interface artifact-predictions --format json
python -m bhsm.interface artifact-report --anchor W_boson --format json
python -m bhsm.interface artifact-report --anchor W_boson --format markdown
```

JSON output remains structured when an expected artifact or callable is absent.

Missing artifacts are reported as missing, not inferred.

Theorem blockers remain blockers unless explicit artifact-backed theorem support is present.
