# UFO Export Runner Guide

Machine-readable artifact:

```text
artifacts/BHSM_ufo_export_runner_contract_v1_4.json
```

The future UFO export path is:

```text
wolframscript -file scripts/feynrules/export_bhsm_minimal_to_ufo.m
```

Current status:

```text
ufo_export_attempted = false
ufo_export_passed = false
ufo_loadability_tested = false
ufo_loadability_passed = false
```

No UFO output directory is generated in Phase Three-L.

Phase Three-M records the live UFO export gate in
`artifacts/BHSM_ufo_export_live_attempt_v1_5.json`. The current gate remains
closed because live FeynRules validation did not pass.

Phase Three-N records the runtime execution outcome in
`artifacts/BHSM_ufo_export_outcome_v1_6.json`. UFO export remains unattempted
because no validated enabled `.fr` file exists.

Phase Three-O adds handoff documentation and setup commands, but UFO export
still requires live FeynRules validation and controlled `.fr` enablement first.
