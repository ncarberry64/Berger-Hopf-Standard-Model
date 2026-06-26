# MadGraph Smoke Runner Guide

Local script:

```text
scripts/madgraph/import_bhsm_minimal_ufo_smoke.mg5
```

The script is a future local runner and requires a validated, loadable UFO
model. Planned processes remain subject to actual UFO particle naming.

Current status:

```text
smoke_test_attempted = false
smoke_test_passed = false
lhe_generated = false
hepmc_generated = false
```

No event files are generated or committed.

Phase Three-M records the live MadGraph smoke gate in
`artifacts/BHSM_madgraph_live_smoke_attempt_v1_5.json`. The current gate
remains closed because no loadable UFO exists and MadGraph is not detected.

Phase Three-N records the runtime smoke-test outcome in
`artifacts/BHSM_madgraph_smoke_outcome_v1_6.json`. MadGraph remains
unattempted because UFO export/loadability did not pass.
