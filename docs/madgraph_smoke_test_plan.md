# MadGraph Smoke-Test Plan

Machine-readable artifact:

```text
artifacts/BHSM_madgraph_smoke_test_plan_v1_3.json
```

Planned minimal processes:

```text
u d~ > w+
e+ ve > w+
```

These are plans only. The smoke test was not attempted because no loadable UFO
model exists.

```text
smoke_test_attempted = false
smoke_test_passed = false
lhe_generated = false
hepmc_generated = false
```

No event files are generated or committed.

## Phase Three-L Smoke Runner Contract

Phase Three-L adds a MadGraph smoke-runner script at:

```text
scripts/madgraph/import_bhsm_minimal_ufo_smoke.mg5
```

The script remains a runner contract. It is not evidence that MadGraph
imported a UFO, generated amplitudes, or wrote LHE/HepMC output. The current
status remains `smoke_test_attempted=false` and `smoke_test_passed=false`.
