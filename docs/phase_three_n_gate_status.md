# Phase Three-N Gate Status

Machine-readable artifact:

```text
artifacts/BHSM_phase_three_n_gate_status_v1_6.json
```

Current status:

```text
python_detected = true
wolframscript_detected = false
wolfram_kernel_detected = false
mathematica_detected = false
feynrules_detected = false
madgraph_detected = false
environment_ready_for_feynrules_validation = false
feynrules_validation_attempted = false
feynrules_syntax_validated = false
feynrules_model_load_validated = false
minimal_feynrules_model_enabled = false
production_feynrules_file_exported = false
ufo_export_attempted = false
ufo_export_passed = false
ufo_loadability_tested = false
ufo_loadability_passed = false
madgraph_smoke_test_attempted = false
madgraph_smoke_test_passed = false
lhe_generation_ready = false
hepmc_generation_ready = false
athena_ready = false
cmssw_ready = false
```

Recommended status language:

```text
BHSM Phase Three-N attempted runtime provisioning for live FeynRules validation. The required Wolfram/FeynRules runtime was not detected, so the minimal model remains disabled and no FeynRules/UFO/MadGraph readiness is claimed.
```

