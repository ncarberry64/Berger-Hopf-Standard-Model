# Institutional Validation Protocol

Machine-readable artifact:

```text
artifacts/BHSM_institutional_validation_protocol_v1_7.json
```

The validation chain is:

```text
step_0_repo_integrity
step_1_runtime_preflight
step_2_feynrules_load_validation
step_3_feynman_rules_generation
step_4_ufo_export
step_5_ufo_loadability
step_6_madgraph_import
step_7_minimal_smoke_process
step_8_event_output_optional
step_9_detector_software_boundary_review
```

Each step unlocks only the next gated step. Failure leaves downstream readiness
claims closed.

